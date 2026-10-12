import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import psutil


# 所有身份使用实际返回值，路径不猜测、不折叠大小写、不替换分隔符。
UTC8 = timezone(timedelta(hours=8))
IDENTITY_KEYS = ("pid", "create_time", "exe", "cwd", "cmdline", "ppid")


def now():
    return datetime.now(UTC8).isoformat()


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encode(value) + "\n")


def checked_path(value, directory):
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError("需要绝对精确路径：" + repr(value))
    path = Path(value)
    if path.is_symlink() or path.is_junction():
        raise ValueError("拒绝链接或目录联接：" + value)
    if not (path.is_dir() if directory else path.is_file()):
        raise ValueError("路径不存在或类型不符：" + value)
    return path


def in_allowed(cwd, directories):
    return any(cwd == root or cwd.startswith(root.rstrip("\\/") + os.sep) for root in directories)


def base_identity(process):
    # 不使用oneshot缓存，在读完关键字段后复查创建时间及存活身份。
    birth = process.create_time()
    value = {"pid": process.pid, "create_time": birth, "exe": process.exe(),
             "cwd": process.cwd(), "cmdline": process.cmdline(), "ppid": process.ppid(),
             "rss_bytes": process.memory_info().rss, "status": process.status()}
    if not process.is_running() or psutil.Process(process.pid).create_time() != birth:
        raise psutil.NoSuchProcess(process.pid, msg="身份读取期间退出或PID复用")
    return value


def identity(process):
    value = base_identity(process)
    if value["ppid"]:
        value["parent"] = base_identity(psutil.Process(value["ppid"]))
    else:
        value["parent"] = None
    if base_identity(process)["ppid"] != value["ppid"]:
        raise RuntimeError("身份读取期间父关系变化")
    return value


def same_identity(left, right):
    return all(left[key] == right[key] for key in IDENTITY_KEYS)


def root_match(actual, binding):
    return all(actual[key] == binding[key] for key in ("pid", "create_time", "exe", "cwd"))


class Guard:
    def __init__(self, plan, binding, output, overrides=None):
        self.plan = plan
        self.binding = binding
        self.output = Path(output)
        self.overrides = overrides or {}
        self.started = time.monotonic()
        self.sample_count = 0
        self.sample_peak = None
        self.minimum_ram = None
        self.minimum_disk = None
        self.initial_root = None
        self.events = []
        self.samples = None
        self.event_file = None
        self.no_progress_signature = None
        self.no_progress_since = self.started
        self.last_members = {}
        self.known_lineage = {}
        self.retired_members = set()
        self.input_bindings = []
        self.confirmed_sample_exits = []
        self.collection_observation = {}

    def readback_member(self, expected):
        # NoSuch可能来自父节点；只以全新候选PID读回认定候选缺失或复用。
        try:
            process = psutil.Process(expected["pid"])
            birth = process.create_time()
        except psutil.NoSuchProcess:
            return {"expected": expected, "status": "ABSENT"}
        except psutil.Error as error:
            return {"expected": expected, "status": "UNKNOWN", "error": repr(error)}
        if expected.get("create_time") is not None and birth != expected["create_time"]:
            return {"expected": expected, "status": "ORIGINAL_PID_REUSED", "actual_create_time": birth, "new_object_untouched": True}
        try:
            current = base_identity(process)
            known_keys = [k for k in IDENTITY_KEYS if k in expected]
            state = "ALIVE" if all(current[k] == expected[k] for k in known_keys) else "IDENTITY_CHANGED"
            return {"expected": expected, "status": state, "actual": current}
        except psutil.NoSuchProcess as error:
            # 初次birth成功后读取字段仍可能自然退出；只凭独立新PID读回确认。
            try:
                confirmed_birth = psutil.Process(expected["pid"]).create_time()
            except psutil.NoSuchProcess as confirmation_error:
                return {"expected": expected, "status": "ABSENT", "first_read_create_time": birth,
                        "error": repr(error), "confirmation_error": repr(confirmation_error),
                        "confirmation": "FRESH_PID_READBACK_ABSENT"}
            except psutil.Error as confirmation_error:
                return {"expected": expected, "status": "UNKNOWN", "actual_create_time": birth,
                        "error": repr(error), "confirmation_error": repr(confirmation_error)}
            if confirmed_birth != birth:
                return {"expected": expected, "status": "ORIGINAL_PID_REUSED",
                        "first_read_create_time": birth, "actual_create_time": confirmed_birth,
                        "error": repr(error), "new_object_untouched": True,
                        "confirmation": "FRESH_PID_READBACK_REUSED"}
            return {"expected": expected, "status": "UNKNOWN", "actual_create_time": confirmed_birth,
                    "error": repr(error), "confirmation": "FRESH_PID_STILL_SAME_BIRTH"}
        except (psutil.Error, RuntimeError) as error:
            return {"expected": expected, "status": "UNKNOWN", "actual_create_time": birth, "error": repr(error)}

    def root_terminal(self, state, actual):
        # 根退出后仅只读已知成员；没有当前真实父链的孤儿绝不追杀。
        readback = [self.readback_member(x) for x in self.last_members.values()]
        retained = [x for x in readback if x["status"] not in {"ABSENT", "ORIGINAL_PID_REUSED"}]
        self.event("KNOWN_MEMBERS_READBACK", root_state=state, actual_root=actual, members=readback,
                   coverage="仅此前已核采样成员，未采到的新生对象未知，不证明完整整树闭合")
        status = "ROOT_EXITED_WITH_REMAINING" if state == "ROOT_MISSING" and retained else "ROOT_EXITED" if state == "ROOT_MISSING" else "BLOCKED"
        return self.finish(status, state, retained=retained)

    def event(self, kind, **values):
        event = {"at_utc8": now(), "elapsed_seconds": time.monotonic() - self.started,
                 "kind": kind, **values}
        self.events.append(event)
        self.event_file.write(encode(event) + "\n")
        self.event_file.flush()
        os.fsync(self.event_file.fileno())

    def limits(self):
        return {"tree_rss_bytes": self.overrides.get("tree_rss_bytes", self.plan["new_run_tree_rss_limit_bytes"]),
                "available_ram_bytes": self.overrides.get("available_ram_bytes", self.plan["new_run_available_ram_stop_bytes"]),
                "c_disk_free_bytes": self.overrides.get("c_disk_free_bytes", self.plan["minimum_c_disk_free_before_dispatch_bytes"])}

    def validate(self):
        b = self.binding
        if type(b["pid"]) is not int or b["pid"] <= 0 or type(b["create_time"]) not in (int, float):
            raise ValueError("PID或创建时间类型不符")
        if not re.fullmatch(r"[0-9a-f]{40}", b["source_commit"]):
            raise ValueError("源码提交必须为完整40位SHA")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", b["run_id"]):
            raise ValueError("RunId必须是单一英文数字名称")
        checked_path(b["exe"], False)
        checked_path(b["cwd"], True)
        if not isinstance(b["allowed_run_dirs"], list) or not b["allowed_run_dirs"]:
            raise ValueError("允许目录为空")
        for root in b["allowed_run_dirs"]:
            checked_path(root, True)
            if Path(root).parent == Path(root):
                raise ValueError("允许目录不能是盘符根")
        if not in_allowed(b["cwd"], b["allowed_run_dirs"]):
            raise ValueError("父进程cwd不在允许的RunId目录")
        if self.plan["resource_sample_interval_seconds"] != 1:
            raise ValueError("必须使用1秒资源采样周期")
        if any(type(v) is not int or v < 0 for v in self.limits().values()):
            raise ValueError("资源阈值必须为非负整数字节")
        if self.overrides and not b.get("fixture_test", False):
            raise ValueError("本工具仅允许显式fixture降低自测阈值，生产阈值来自计划")
        if self.overrides and (self.overrides.get("tree_rss_bytes", 0) > self.plan["new_run_tree_rss_limit_bytes"] or self.overrides.get("available_ram_bytes", 0) > self.plan["new_run_available_ram_stop_bytes"] or self.overrides.get("c_disk_free_bytes", 0) > self.plan["minimum_c_disk_free_before_dispatch_bytes"]):
            raise ValueError("fixture不得扩大生产预算")
        if b["pid"] in {p.pid for p in psutil.Process().parents()} | {os.getpid()}:
            raise ValueError("拒绝监控或停止守卫自身及祖先")
        logs = b.get("progress_logs", [])
        if b.get("no_progress_seconds") is not None:
            if b["no_progress_seconds"] != 900 or not logs:
                raise ValueError("日志无变化停止必须显式900秒并提供实际日志路径")
            for path in logs:
                checked_path(path, False)
                if not in_allowed(str(Path(path).parent), b["allowed_run_dirs"]):
                    raise ValueError("进度日志不在本轮允许目录")

    def get_root(self):
        try:
            process = psutil.Process(self.binding["pid"])
            birth = process.create_time()
        except psutil.NoSuchProcess:
            return "ROOT_MISSING", None
        except psutil.Error as error:
            return "IDENTITY_UNAVAILABLE", {"error": repr(error)}
        if birth != self.binding["create_time"]:
            try:
                actual = identity(process)
            except (psutil.Error, RuntimeError) as error:
                actual = {"pid": process.pid, "create_time": birth, "error": repr(error)}
            return "PID_REUSED", actual
        try:
            current = identity(process)
        except psutil.NoSuchProcess as error:
            # 父节点退出不能误写成本轮根已经退出；单独读回根的真实状态。
            try:
                actual_birth = psutil.Process(self.binding["pid"]).create_time()
            except psutil.NoSuchProcess:
                return "ROOT_MISSING", None
            return ("PID_REUSED" if actual_birth != self.binding["create_time"] else "IDENTITY_UNAVAILABLE"), {"error": repr(error), "create_time": actual_birth}
        except (psutil.Error, RuntimeError) as error:
            return "IDENTITY_UNAVAILABLE", {"error": repr(error)}
        if current["create_time"] != self.binding["create_time"]:
            return "PID_REUSED", current
        if not root_match(current, self.binding):
            return "IDENTITY_MISMATCH", current
        if self.initial_root is not None and not same_identity(current, self.initial_root):
            return "IDENTITY_CHANGED", current
        return "MATCH", current

    def verified_chain(self, candidate, root):
        # 每次停止之前重新建立实际祖先链，任何中间节点也必须在允许cwd范围。
        chain = []
        process = psutil.Process(candidate["pid"])
        current = identity(process)
        if not same_identity(current, candidate):
            raise RuntimeError("PID复用或身份变化")
        if candidate["pid"] != root["pid"] and candidate.get("parent") is not None:
            if current["parent"] is None or not same_identity(current["parent"], candidate["parent"]):
                raise RuntimeError("候选已保存的直接父身份变化")
        proof = self.known_lineage.get((candidate["pid"], candidate["create_time"]))
        expected_chain = None if proof is None else proof["ancestor_chain"]
        leaf = current
        visited = set()
        while True:
            if current["pid"] in visited:
                raise RuntimeError("父链循环")
            visited.add(current["pid"])
            if not in_allowed(current["cwd"], self.binding["allowed_run_dirs"]):
                raise RuntimeError("对象cwd超出本轮范围")
            # 动作前逐级比较本次首次完整链；禁止旧child沿复用父PID获得停止权。
            if expected_chain is not None:
                if len(chain) >= len(expected_chain) or not same_identity(current, expected_chain[len(chain)]):
                    raise RuntimeError("本次已保存祖先链身份变化")
            chain.append(current)
            if current["pid"] == root["pid"]:
                status, actual_root = self.get_root()
                if status != "MATCH" or not same_identity(current, actual_root):
                    raise RuntimeError("父进程身份失效：" + status)
                if expected_chain is not None and len(chain) != len(expected_chain):
                    raise RuntimeError("本次已保存祖先链长度变化")
                return process, leaf, chain
            if not current["ppid"]:
                raise RuntimeError("无法到达本轮根PID")
            parent = identity(psutil.Process(current["ppid"]))
            if current["parent"] is None or not same_identity(parent, current["parent"]):
                raise RuntimeError("祖先身份变化")
            if parent["create_time"] > current["create_time"]:
                raise RuntimeError("父出生时间晚于子对象，拒绝复用父PID链")
            current = parent

    def collect(self, root):
        # 最多三轮独立枚举及读回；两次连续活身份集合一致才声明离散集合闭合。
        started = time.monotonic()
        started_at = now()
        previous = None
        all_exited = []
        observed = dict(self.last_members)
        members, uncertain = [], []
        closed = False
        for scan in range(1, 4):
            members, uncertain, exited = self.collect_round(root, observed)
            all_exited.extend(exited)
            observed.update({(x["pid"], x["create_time"]): x for x in members})
            current = {(x["pid"], x["create_time"]) for x in members}
            if uncertain:
                break
            if previous == current and not exited:
                closed = True
                break
            previous = current
        if not closed and not uncertain:
            uncertain.append({"reason": "TREE_RESCAN_NOT_CLOSED", "maximum_scans": 3})
        self.collection_observation = {"started_at_utc8": started_at, "ended_at_utc8": now(),
                                       "elapsed_seconds": time.monotonic() - started,
                                       "scans": scan, "maximum_scans": 3, "closed": closed}
        return members, uncertain, all_exited

    def round_identity(self, process, table):
        # 表只在这一轮存在；读取所有六字段，不使用跨轮或psutil缓存。
        if process.pid not in table:
            table[process.pid] = base_identity(process)
        item = table[process.pid]
        if "parent" not in item:
            parent_pid = item["ppid"]
            if parent_pid and parent_pid not in table:
                table[parent_pid] = base_identity(psutil.Process(parent_pid))
            item["parent"] = None if not parent_pid else table[parent_pid]
            if base_identity(process)["ppid"] != parent_pid:
                raise RuntimeError("当前轮直接父PID变化")
        return item

    def round_chain(self, candidate, root, table):
        # 当前轮祖先证明复用新鲜表；停止动作仍使用原verified_chain完整重查。
        leaf = candidate
        current = candidate
        chain, visited = [], set()
        proof = self.known_lineage.get((candidate["pid"], candidate["create_time"]))
        expected = None if proof is None else proof["ancestor_chain"]
        while True:
            if current["pid"] in visited:
                raise RuntimeError("父链循环")
            visited.add(current["pid"])
            if not in_allowed(current["cwd"], self.binding["allowed_run_dirs"]):
                raise RuntimeError("对象cwd超出本轮范围")
            if expected is not None and (len(chain) >= len(expected) or not same_identity(current, expected[len(chain)])):
                raise RuntimeError("本次已保存祖先链身份变化")
            chain.append(current)
            if current["pid"] == root["pid"]:
                if not same_identity(current, root) or (expected is not None and len(chain) != len(expected)):
                    raise RuntimeError("当前轮ROOT身份或祖先链长度变化")
                return None, leaf, chain
            if not current["ppid"]:
                raise RuntimeError("无法到达本轮根PID")
            parent = self.round_identity(psutil.Process(current["ppid"]), table)
            if current["parent"] is None or not same_identity(parent, current["parent"]):
                raise RuntimeError("祖先身份变化")
            if parent["create_time"] > current["create_time"]:
                raise RuntimeError("父出生时间晚于子对象，拒绝复用父PID链")
            current = parent

    def round_ancestor_readback(self, key, table):
        # 已有祖先若不在当前表仍用原独立读回，保留缺失与复用判定。
        proof = self.known_lineage.get(key)
        if proof is None:
            return
        for ancestor in proof["ancestor_chain"][1:-1]:
            current = table.get(ancestor["pid"])
            if current is not None:
                if not same_identity(current, ancestor):
                    raise RuntimeError("历史祖先复用或六字段漂移")
            else:
                result = self.readback_member(ancestor)
                if result["status"] not in {"ALIVE", "ABSENT"}:
                    raise RuntimeError("历史祖先复用、漂移或未知：" + result["status"])
                if result["status"] == "ALIVE":
                    table[ancestor["pid"]] = result["actual"]

    def collect_round(self, root, observed):
        # 历史证明只由本次执行的完整现时父链建立，绝不导入旧日志。
        members = {}
        uncertain = []
        exited = []
        visited = set()
        queue = []
        table = {}
        try:
            state, current_root = self.get_root()
            if state != "MATCH" or not same_identity(root, current_root):
                raise RuntimeError("重扫ROOT完整身份失效：" + state)
            members[(root["pid"], root["create_time"])] = dict(current_root, monitorable=True,
                    stoppable=True, lineage_mode="CURRENT_CHAIN")
            table[root["pid"]] = current_root
            queue.extend((p, None) for p in psutil.Process(root["pid"]).children(recursive=True))
        except (psutil.Error, RuntimeError) as error:
            return list(members.values()), [{"reason": "TREE_ENUMERATION_FAILED", "error": repr(error)}], exited
        # ROOT枚举可能已看不到孤儿；每轮仍逐个读回曾完整证明的成员。
        for known in observed.values():
            if known["pid"] == root["pid"] or (known["pid"], known["create_time"]) in self.retired_members:
                continue
            result = self.readback_member(known)
            if result["status"] == "ALIVE":
                try:
                    queue.append((psutil.Process(known["pid"]), known))
                    continue
                except psutil.NoSuchProcess:
                    # 构造句柄期间退出仍须新的候选PID读回，不推断RSS零。
                    pass
                result = self.readback_member(known)
            if result["status"] in {"ABSENT", "ORIGINAL_PID_REUSED"}:
                self.record_sample_exit(result, exited)
            else:
                uncertain.append({"pid": known["pid"], "reason": "KNOWN_MEMBER_READBACK_UNKNOWN", "readback": result})
        cursor = 0
        while cursor < len(queue):
            process, queued_expected = queue[cursor]
            cursor += 1
            item = None
            candidate_birth = None
            try:
                candidate_birth = process.create_time()
                if queued_expected is not None and candidate_birth != queued_expected["create_time"]:
                    result = self.readback_member(queued_expected)
                    if result["status"] in {"ABSENT", "ORIGINAL_PID_REUSED"}:
                        self.record_sample_exit(result, exited)
                    else:
                        uncertain.append({"pid": process.pid, "reason": "KNOWN_HANDLE_CHANGED", "readback": result})
                    continue
                key = (process.pid, candidate_birth)
                if key in visited:
                    continue
                visited.add(key)
                item = self.round_identity(process, table)
                expected = observed.get(key)
                if expected is not None and not same_identity(item, expected):
                    raise RuntimeError("已核成员六字段变化")
                # 旧成员不能沿已经复用的父PID重新获得当前停止权限。
                self.round_ancestor_readback(key, table)
                _, current, chain = self.round_chain(item, root, table)
                if key not in self.known_lineage:
                    proof = {"first_verified_sample": self.sample_count,
                             "ancestor_chain": [{k: x[k] for k in IDENTITY_KEYS} for x in chain]}
                    self.known_lineage[key] = proof
                    self.event("LINEAGE_FIRST_VERIFIED", **proof)
                members[key] = dict(current, monitorable=True, stoppable=True, lineage_mode="CURRENT_CHAIN")
            except psutil.NoSuchProcess as error:
                expected = observed.get((process.pid, candidate_birth)) or item or {"pid": process.pid, "create_time": candidate_birth}
                result = self.readback_member(expected)
                result["original_error"] = repr(error)
                if result["status"] in {"ABSENT", "ORIGINAL_PID_REUSED"}:
                    self.record_sample_exit(result, exited)
                else:
                    try:
                        if result["status"] != "ALIVE":
                            raise RuntimeError("候选读回没有完整确认存活身份")
                        current = self.historical_member(result["actual"], root)
                        self.reject_reused_ancestor((current["pid"], current["create_time"]))
                        members[(current["pid"], current["create_time"])] = current
                        # 新孤儿子对象仍需现时完整ROOT链；历史链不能用于收编新成员。
                        queue.extend((p, None) for p in psutil.Process(current["pid"]).children(recursive=True))
                    except (psutil.Error, RuntimeError) as fallback_error:
                        retry = self.readback_member(expected)
                        if retry["status"] in {"ABSENT", "ORIGINAL_PID_REUSED"}:
                            self.record_sample_exit(retry, exited)
                        else:
                            uncertain.append({"pid": process.pid, "reason": "CANDIDATE_ALIVE_OR_UNKNOWN_PARENT_CHAIN", "readback": retry, "historical_rejection": repr(fallback_error)})
            except (psutil.Error, RuntimeError) as error:
                uncertain.append({"pid": process.pid, "reason": "UNVERIFIED_MEMBER", "identity": item, "error": repr(error)})
        # 发布前每个表项均重新完整读回；任何漂移或未知不能形成闭合集合。
        for previous in list(table.values()):
            result = self.readback_member(previous)
            key = (previous["pid"], previous["create_time"])
            if result["status"] == "ALIVE":
                current = result["actual"]
                current["parent"] = None
                if previous.get("parent") is not None:
                    parent_result = self.readback_member(previous["parent"])
                    if parent_result["status"] != "ALIVE":
                        uncertain.append({"pid": previous["pid"], "reason": "ROUND_PARENT_READBACK_CHANGED", "readback": parent_result})
                    else:
                        current["parent"] = parent_result["actual"]
                if key in members:
                    members[key] = dict(current, monitorable=members[key]["monitorable"], stoppable=members[key]["stoppable"], lineage_mode=members[key]["lineage_mode"])
            elif result["status"] in {"ABSENT", "ORIGINAL_PID_REUSED"} and previous["pid"] != root["pid"]:
                self.record_sample_exit(result, exited)
                members.pop(key, None)
            else:
                uncertain.append({"pid": previous["pid"], "reason": "ROUND_FINAL_READBACK_UNKNOWN", "readback": result})
        return list(members.values()), uncertain, exited

    def reject_reused_ancestor(self, key):
        # 历史祖先的复用与未知都阻断；不读取新对象字段或枚举其子树。
        proof = self.known_lineage.get(key)
        if proof is None:
            return
        for ancestor in proof["ancestor_chain"][1:-1]:
            result = self.readback_member(ancestor)
            if result["status"] not in {"ALIVE", "ABSENT"}:
                raise RuntimeError("历史祖先复用、漂移或未知：" + result["status"])

    def record_sample_exit(self, result, exited):
        key = (result["expected"]["pid"], result["expected"].get("create_time"))
        if key in self.retired_members:
            return
        self.retired_members.add(key)
        exited.append(result)
        self.confirmed_sample_exits.append(result)
        self.event("HELPER_EXIT_CONFIRMED_CONTINUE", readback=result, limitation="短命对象RSS/峰值缺测，不伪造零；继续后续采样")

    def historical_member(self, current, root):
        key = (current["pid"], current["create_time"])
        proof = self.known_lineage.get(key)
        if proof is None or not same_identity(current, proof["ancestor_chain"][0]):
            raise RuntimeError("没有本次完整历史证明或成员六字段已变化")
        if not in_allowed(current["cwd"], self.binding["allowed_run_dirs"]):
            raise RuntimeError("已知成员cwd超出允许目录")
        if not same_identity(root, proof["ancestor_chain"][-1]):
            raise RuntimeError("本次ROOT完整身份已失效")
        missing = []
        for ancestor in proof["ancestor_chain"][1:-1]:
            result = self.readback_member(ancestor)
            if result["status"] in {"ABSENT", "ORIGINAL_PID_REUSED"}:
                missing.append(result)
            elif result["status"] != "ALIVE":
                raise RuntimeError("历史祖先读回未知或身份变化")
        if not missing:
            raise RuntimeError("未确认旧祖先缺失，不能使用历史链例外")
        reread = self.readback_member(proof["ancestor_chain"][0])
        if reread["status"] != "ALIVE":
            raise RuntimeError("历史核验期间候选退出或身份未知/变化")
        current = reread["actual"]
        self.event("KNOWN_LINEAGE_MONITOR_ONLY", identity=current, missing_ancestors=missing,
                   first_verified_sample=proof["first_verified_sample"], limitation="仅本次已核归属的真实RSS；没有当前停止权限")
        return dict(current, monitorable=True, stoppable=False, lineage_mode="HISTORICAL_CHAIN")

    def stop_tree(self, root, initial_members, initial_uncertain, reason):
        stopped = []
        retained = list(initial_uncertain)
        # 后出现的子对象仍需采集并核身份；若有不确定对象，保留根以免丢失祖先关系。
        members, uncertain, exited = self.collect(root)
        retained.extend(uncertain)
        self.last_members.update({(x["pid"], x["create_time"]): x for x in initial_members + members})
        # 现时ROOT枚举之外的历史孤儿也必须出现在闭合读回中，不能漏掉。
        for known in self.last_members.values():
            if known["pid"] == root["pid"]:
                continue
            result = self.readback_member(known)
            if result["status"] not in {"ABSENT", "ORIGINAL_PID_REUSED"} and not any(same_identity(known, x) for x in members):
                retained.append({"pid": known["pid"], "reason": "KNOWN_MEMBER_NOT_IN_CURRENT_COLLECTION", "readback": result})
        candidates = []
        for item in members:
            if item["pid"] == root["pid"]:
                continue
            try:
                _, current, chain = self.verified_chain(item, root)
                candidates.append((len(chain), current))
            except (psutil.Error, RuntimeError) as error:
                retained.append({"pid": item["pid"], "reason": "PRE_STOP_IDENTITY_REJECTED", "error": repr(error)})
        for _, item in sorted(candidates, key=lambda x: x[0], reverse=True):
            outcome = self.stop_one(item, root, reason)
            (stopped if outcome["status"] in {"STOPPED", "ALREADY_EXITED"} else retained).append(outcome)
        # 再枚举一次；不追杀已失去可证实时父链的残留或新生对象。
        state, actual_root = self.get_root()
        if state == "MATCH":
            remaining, unknown, exited = self.collect(actual_root)
            retained.extend(unknown)
            retained.extend({"pid": x["pid"], "reason": "STILL_PRESENT_OR_NEW_CHILD", "identity": x} for x in remaining if x["pid"] != root["pid"])
            if not retained:
                outcome = self.stop_one(actual_root, actual_root, reason)
                (stopped if outcome["status"] in {"STOPPED", "ALREADY_EXITED"} else retained).append(outcome)
            else:
                retained.append({"pid": root["pid"], "reason": "ROOT_RETAINED_FOR_UNCERTAIN_DESCENDANTS", "identity": actual_root})
        elif state not in {"ROOT_MISSING", "PID_REUSED"}:
            retained.append({"pid": root["pid"], "reason": state, "identity": actual_root})
        else:
            readback = [self.readback_member(x) for x in self.last_members.values()]
            retained.extend(x for x in readback if x["status"] not in {"ABSENT", "ORIGINAL_PID_REUSED"})
            self.event("ROOT_LOST_DURING_STOP_READBACK", root_state=state, members=readback,
                       coverage="仅已知成员；活/未知孤儿不追杀，未采新生对象未知")
        self.event("STOP_TREE_RESULT", reason=reason, stopped=stopped, retained=retained)
        return ("STOP_PARTIAL" if stopped else "BLOCKED") if retained else "STOPPED", stopped, retained

    def stop_one(self, expected, root, reason):
        try:
            process, current, chain = self.verified_chain(expected, root)
            self.event("PRE_STOP_VERIFIED", reason=reason, identity=current, ancestor_chain=chain)
            # 原始事件fsync之后再查一次，且psutil自身也执行PID复用保护。
            process, current, chain = self.verified_chain(expected, root)
            if not process.is_running():
                return {"pid": expected["pid"], "status": "ALREADY_EXITED"}
            process.terminate()
            self.event("TERMINATE_SENT", identity=current, ancestor_chain=chain)
            try:
                exit_code = process.wait(timeout=3)
            except psutil.TimeoutExpired:
                process, current, chain = self.verified_chain(expected, root)
                self.event("PRE_KILL_VERIFIED", identity=current, ancestor_chain=chain)
                process, current, chain = self.verified_chain(expected, root)
                process.kill()
                exit_code = process.wait(timeout=3)
            try:
                after = base_identity(psutil.Process(expected["pid"]))
                absent = after["create_time"] != expected["create_time"]
            except psutil.NoSuchProcess:
                after, absent = None, True
            outcome = {"pid": expected["pid"], "status": "STOPPED" if absent else "STILL_PRESENT", "native_process_exit_code": exit_code, "before": current, "after": after}
            self.event("POST_STOP_READBACK", **outcome)
            return outcome
        except psutil.NoSuchProcess:
            result = self.readback_member(expected)
            if result["status"] in {"ABSENT", "ORIGINAL_PID_REUSED"}:
                return {"pid": expected["pid"], "status": "ALREADY_EXITED", "readback": result}
            outcome = {"pid": expected["pid"], "status": "BLOCKED", "reason": "CANDIDATE_ALIVE_OR_UNKNOWN_PARENT_CHAIN", "readback": result}
            self.event("STOP_REJECTED", **outcome)
            return outcome
        except (psutil.Error, RuntimeError) as error:
            outcome = {"pid": expected["pid"], "status": "BLOCKED", "reason": repr(error), "expected": expected}
            self.event("STOP_REJECTED", **outcome)
            return outcome

    def progress(self):
        if self.binding.get("no_progress_seconds") is None:
            return False
        signature = [(str(path), Path(path).stat().st_size, Path(path).stat().st_mtime_ns) for path in self.binding["progress_logs"]]
        if signature != self.no_progress_signature:
            self.no_progress_signature = signature
            self.no_progress_since = time.monotonic()
        return time.monotonic() - self.no_progress_since >= 900

    def finish(self, status, reason, stopped=None, retained=None):
        receipt = {"schema_version": 1, "status": status, "reason": reason, "at_utc8": now(),
                   "guard_stop": "STOP_NO_RESTART", "elapsed_seconds": time.monotonic() - self.started,
                   "source_commit": self.binding.get("source_commit"), "run_id": self.binding.get("run_id"),
                   "binding": self.binding, "limits": self.limits(), "sample_interval_seconds": 1,
                   "samples": self.sample_count, "sampled_peak_tree_rss_bytes": self.sample_peak,
                   "monitoring_semantics": "规定节拍离散监测执行；仅闭合活身份集合的非原子实测RSS合计",
                   "minimum_sampled_available_ram_bytes": self.minimum_ram, "minimum_sampled_c_disk_free_bytes": self.minimum_disk,
                   "initial_root_identity": self.initial_root, "stopped": stopped or [], "retained": retained or [],
                   "input_bindings": self.input_bindings,
                   "guard_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   "known_members_count": len(self.last_members), "confirmed_sample_exits": self.confirmed_sample_exits,
                   "known_lineage_count": len(self.known_lineage),
                   "historical_lineage_limitations": ["历史完整链只支持本次执行已核成员的真实RSS，缺失当前祖先链不授予停止权限", "已知孤儿仍逐项读回并枚举其新子对象；未曾完整核验的新对象、真实UNKNOWN或字段变化继续阻断", "PID复用的新对象不动，不沿复用父PID连接新祖先；缺测不补零或旧RSS"],
                   "absolute_peak_memory_bytes": None, "guard_peak_memory_bytes": None,
                   "limitations": ["1秒离散采样不是连续绝对峰，短命helper已确认退出仅记录缺测，不伪造RSS零并继续监控", "根退出/复用时只读此前已核成员；新生未采对象未知，不能证明整树闭合；活/未知孤儿保留并非零", "创建时间及实际祖先链每次动作前重查；OS没有跨整树原子身份/停止事务", "不确定对象不动；保留根并STOP_PARTIAL/BLOCKED，ROOT需读原件后处置", "ROOT缺失/复用终态，不重启或扫描其它窗口", "900秒进度可选口径仅指定日志size/mtime变化，不证明设计进展或收敛", "使用前ROOT必须首个样本/守卫PID确认后才派发heavy，并在MCP长wait中每5秒并行消费guard进程与终态；异常阻止后续派发，闭合读回所有owned身份；此集成未由本工具执行", "新6GiB计划不修改旧S9预算，也不批准功能/时序/实板"]}
        self.event("GUARD_TERMINAL", status=status, reason=reason)
        for name in ("samples.jsonl", "events.jsonl"):
            receipt.setdefault("files", []).append({"path": name, "sha256": hashlib.sha256((self.output / name).read_bytes()).hexdigest()})
        write_new(self.output / "guard_receipt.json", receipt)
        return 0 if status == "ROOT_EXITED" else 2 if status == "STOPPED" else 3

    def run(self):
        # 输出目录必须首次创建，STOP_REQUEST只在此目录读取，不覆盖或恢复旧RunId。
        checked_path(str(self.output.parent), True)
        if self.output.exists() or self.output.is_symlink():
            raise FileExistsError("输出目录已存在，拒绝覆盖：" + str(self.output))
        self.output.mkdir()
        with (self.output / "samples.jsonl").open("x", encoding="utf-8", newline="\n") as self.samples, (self.output / "events.jsonl").open("x", encoding="utf-8", newline="\n") as self.event_file:
            self.event("START", binding=self.binding, plan=self.plan, thresholds_override=self.overrides, native_command=[sys.executable] + sys.argv, python=sys.version, psutil_version=psutil.__version__)
            try:
                self.validate()
                state, root = self.get_root()
                if state != "MATCH":
                    self.event("ROOT_REJECTED", state=state, actual=root)
                    return self.root_terminal(state, root)
                self.initial_root = root
                self.last_members[(root["pid"], root["create_time"])] = root
                self.event("ROOT_BOUND", identity=root)
                next_sample = time.monotonic()
                previous_sample_start = None
                while True:
                    sample_start = time.monotonic()
                    sample_started_at = now()
                    state, root = self.get_root()
                    if state != "MATCH":
                        self.event("ROOT_TERMINAL_IDENTITY", state=state, actual=root)
                        return self.root_terminal(state, root)
                    members, uncertain, exited = self.collect(root)
                    self.last_members.update({(x["pid"], x["create_time"]): x for x in members})
                    rss = sum(x["rss_bytes"] for x in members)
                    ram = psutil.virtual_memory().available
                    disk = psutil.disk_usage("C:\\").free
                    limits = self.limits()
                    alerts = []
                    if rss > limits["tree_rss_bytes"]:
                        alerts.append("OWNED_TREE_RSS_GT_LIMIT")
                    if ram < limits["available_ram_bytes"]:
                        alerts.append("AVAILABLE_RAM_LT_LIMIT")
                    if disk < limits["c_disk_free_bytes"]:
                        alerts.append("C_DISK_FREE_LT_LIMIT")
                    if self.progress():
                        alerts.append("SPECIFIED_LOGS_UNCHANGED_900_SECONDS")
                    stop_request = self.output / "STOP_REQUEST"
                    if stop_request.exists():
                        if not stop_request.is_file() or stop_request.is_symlink():
                            return self.finish("BLOCKED", "INVALID_STOP_REQUEST_TYPE")
                        alerts.append("STOP_REQUEST")
                    sample = {"index": self.sample_count, "at_utc8": now(), "elapsed_seconds": time.monotonic() - self.started,
                              "tree_rss_bytes": rss if not uncertain else None, "verified_subset_rss_bytes": rss,
                              "live_measured_rss_sum": rss if not uncertain else None,
                              "sample_started_at_utc8": sample_started_at, "sample_ended_at_utc8": now(),
                              "sample_elapsed_seconds": time.monotonic() - sample_start,
                              "actual_start_gap_seconds": None if previous_sample_start is None else sample_start - previous_sample_start,
                              "schedule_delay_seconds": max(0, sample_start - next_sample),
                              "collection_observation": self.collection_observation,
                              "available_ram_bytes": ram, "c_disk_free_bytes": disk, "members": members,
                              "uncertain": uncertain, "confirmed_exits": exited, "limits": limits, "alerts": alerts}
                    sample["current_chain_rss_bytes"] = sum(x["rss_bytes"] for x in members if x.get("stoppable", True))
                    sample["historical_chain_rss_bytes"] = sum(x["rss_bytes"] for x in members if not x.get("stoppable", True))
                    sample["coverage"] = "有界重扫闭合活身份集合的非原子实测合计；退出单列，短命未采对象未知；不是连续绝对峰"
                    self.samples.write(encode(sample) + "\n")
                    self.samples.flush()
                    os.fsync(self.samples.fileno())
                    self.sample_count += 1
                    previous_sample_start = sample_start
                    if not uncertain:
                        self.sample_peak = max(self.sample_peak or 0, rss)
                    self.minimum_ram = min(ram, self.minimum_ram if self.minimum_ram is not None else ram)
                    self.minimum_disk = min(disk, self.minimum_disk if self.minimum_disk is not None else disk)
                    if alerts:
                        self.event("ALERT", alerts=alerts, sample_index=sample["index"])
                        status, stopped, retained = self.stop_tree(root, members, uncertain, alerts)
                        return self.finish(status, alerts, stopped, retained)
                    if uncertain:
                        self.event("TREE_UNCERTAIN", uncertain=uncertain)
                        return self.finish("BLOCKED", "INCOMPLETE_TREE_IDENTITY", retained=uncertain)
                    max_seconds = self.binding.get("max_seconds")
                    if max_seconds is not None and time.monotonic() - self.started >= max_seconds:
                        return self.finish("BLOCKED", "GUARD_OBSERVATION_LIMIT_NO_TASK_STOP")
                    next_sample += 1
                    time.sleep(max(0, next_sample - time.monotonic()))
            except (psutil.Error, OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
                self.event("GUARD_ERROR_NO_UNVERIFIED_STOP", error=repr(error))
                return self.finish("BLOCKED", repr(error))


def main():
    parser = argparse.ArgumentParser(description="仅本轮已核身份进程树的资源守卫")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fixture-tree-limit-bytes", type=int)
    args = parser.parse_args()
    plan_path = checked_path(args.plan, False)
    binding_path = checked_path(args.binding, False)
    output = Path(args.output_dir)
    if not output.is_absolute():
        raise ValueError("输出路径必须绝对")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    overrides = {} if args.fixture_tree_limit_bytes is None else {"tree_rss_bytes": args.fixture_tree_limit_bytes}
    monitor = Guard(plan, binding, output, overrides)
    monitor.input_bindings = [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in (plan_path, binding_path)]
    return monitor.run()


if __name__ == "__main__":
    raise SystemExit(main())
