"""只读核查冻结工具；独立夹具仅查询自己的PID，结果写新隔离目录。"""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil

base = Path(__file__).absolute().parent
root = Path.cwd().resolve()
guard_dir = root / "tmp/2B/S2B-T17/s11_resource_guard_20261012_r01"
sup_dir = root / "tmp/2B/S2B-T17/s11_guard_supervisor_20261012_r01"
old_dir = root / "tmp/2B/S2B-T17/s10_resource_guard_20261012_r02"
old_sup_dir = root / "tmp/2B/S2B-T17/s10_guard_supervisor_20261012_r01"
plan_path = root / "tmp/2B/S2B-T17/s11_root_run_20261012_r01/resource_plan.json"
checks = []
inputs = {}
started = time.monotonic()
peak = 0
def sha(data): return hashlib.sha256(data).hexdigest()
def read(path, role="input"):
    assert path.is_file(), str(path)
    data = path.read_bytes()
    inputs[str(path.relative_to(root)).replace(os.sep, "/")] = {"path": str(path.relative_to(root)).replace(os.sep, "/"), "sha256": sha(data), "role": role}
    return data
def load(path, role="input"): return json.loads(read(path, role).decode("utf-8"))
def check(name, condition):
    assert condition, name
    checks.append(name)
def write(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
def block(text, name):
    node = next(x for x in ast.walk(ast.parse(text)) if isinstance(x, ast.FunctionDef) and x.name == name)
    return "".join(text.splitlines(keepends=True)[node.lineno-1:node.end_lineno])

candidate = read(guard_dir / "guard.py", "source")
supervisor = read(sup_dir / "supervisor.py", "source")
old = read(old_dir / "guard.py", "source")
old_sup = read(old_sup_dir / "supervisor.py", "source")
check("候选guard精确SHA", sha(candidate) == "9cad1ddf5f1b2d48b99c6d10451756536b25c4abf613f0af8b16e0ffd629f86c")
check("候选supervisor精确SHA", sha(supervisor) == "b6e8d612551cb5c3df3111075eb680505799b96288253a221df3eb2935a56184")
check("旧guard未变", sha(old) == "be8d51ba18cf331458e1d747578f332c4e5cc4b72604a3fb6d09e15030abb4d4")
check("旧supervisor未变", sha(old_sup) == "d8c6e2e53b4b3012a139a2ab33969d0c308dc2a42e49976cad205b02ba8b578c")
text = candidate.decode("utf-8")
for name in ("stop_one", "verified_chain", "base_identity", "identity"):
    check(name + "完整块与旧版一致", block(text, name) == block(old.decode("utf-8"), name))
check("stop_one冻结块SHA", sha(candidate.split(b"    def stop_one(", 1)[1].split(b"    def progress(", 1)[0]) == "1e4e1108cadb4474a6646fcb62887efa6825b6400d67879314050a82135739d3")
expected_sup = old_sup.decode("utf-8").replace("s10_resource_guard_20261012_r02/guard.py", "s11_resource_guard_20261012_r01/guard.py").replace("be8d51ba18cf331458e1d747578f332c4e5cc4b72604a3fb6d09e15030abb4d4", sha(candidate))
check("supervisor仅固定路径SHA更新", expected_sup.encode("utf-8") == supervisor)
receipt_data = read(guard_dir / "tool_receipt.json", "result")
check("Developer receipt冻结SHA", sha(receipt_data) == "6a2520161bdfbd23092be507bba70186f61f87a174a5f83a04d26eb6c0cc7a9f")
delivery = json.loads(receipt_data)
raw_data = read(guard_dir / "raw_manifest.jsonl")
check("Developer raw冻结SHA", sha(raw_data) == "26ea15b6776743e4bf41e1362b7539ef2f29bfd324f265f2f77f90c83c03fc57")
rows = [json.loads(x) for x in raw_data.decode("utf-8").splitlines()]
check("810原件绑定格式", len(rows) == 810 and all(set(x) == {"path", "sha256", "role"} for x in rows))
for entry in rows:
    p = root / entry["path"]
    assert p.is_file() and sha(p.read_bytes()) == entry["sha256"], entry["path"]
check("810原件逐项SHA只读核验", True)
for name in ("lineage_r01.native.json", "lineage_r02.native.json", "lineage_r03.native.json", "seal_first_failure.json", "lineage_tests_r03/result.json"):
    load(guard_dir / name, "diagnostic" if "failure" in name else "result")
check("旧80MiB超限透明保留", delivery["tool_test_budget"]["original_80MiB_met"] is False and delivery["tool_test_budget"]["root_authorized_revised_bytes"] == 134217728)
plan_data = read(plan_path)
check("ROOT新资源计划SHA", sha(plan_data) == "aec3e818e6e20653fbe55ed89fd4f5a9c3a8e55a41bb8b417eb4bb93fcee6784")
plan = json.loads(plan_data)
check("正式阈值未扩大", [plan[k] for k in ("new_run_tree_rss_limit_bytes", "new_run_available_ram_stop_bytes", "minimum_c_disk_free_before_dispatch_bytes", "resource_sample_interval_seconds")] == [6442450944, 536870912, 8589934592, 1])
check("4.5GiB仅新owned启动准入", plan["minimum_available_ram_before_dispatch_bytes"] == 4831838208 and plan["admission_operation"] == "start_owned_vivado_session" and "不追认S10" in plan["admission_reason"] and "综合启动前另存真实资源" in plan["admission_reason"])
head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True)
(base / "head.stdout.log").write_bytes(head.stdout); (base / "head.stderr.log").write_bytes(head.stderr)
write(base / "head.native.json", {"command": ["git", "rev-parse", "HEAD"], "native_exit_code": head.returncode})
check("固定HEAD", head.returncode == 0 and head.stdout.decode().strip() == "4288795b1e8c75b98cbbeb69ac33709172e97c66")
spec = importlib.util.spec_from_file_location("s11_candidate_guard", guard_dir / "guard.py")
guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
real_process = psutil.Process
owned_pids = {os.getpid()}
def limited_process(pid=None):
    selected = os.getpid() if pid is None else pid
    assert selected in owned_pids, "拒绝查询非本审查owned PID：" + str(selected)
    return real_process(selected)
# 候选模块与psutil共享；只允许本审查创建的成员和审查自身。
psutil.Process = limited_process
def wait(path):
    deadline = time.monotonic() + 4
    while not path.exists():
        assert time.monotonic() < deadline
        time.sleep(0.02)
    return json.loads(path.read_text(encoding="utf-8"))
def leave(work, role, item):
    (work / (role + "_exit")).touch()
    deadline = time.monotonic() + 4
    while True:
        try: limited_process(item["pid"]).create_time()
        except psutil.NoSuchProcess: return
        assert time.monotonic() < deadline, "自有自然退出超时"
        time.sleep(0.02)
def sample_peak(items):
    global peak
    total = limited_process().memory_info().rss
    for item in items:
        try: total += limited_process(item["pid"]).memory_info().rss
        except psutil.NoSuchProcess: pass
    peak = max(peak, total)
    assert total <= 134217728, "独立夹具超128MiB即停止派发"

fixture_rows = []
for case in ("A_known", "B_unknown"):
    work = base / case; work.mkdir()
    with (work / "fixture.stdout.log").open("xb") as so, (work / "fixture.stderr.log").open("xb") as se:
        child = subprocess.Popen([sys.executable, "-S", "-B", str(base / "fixture.py"), "root"], cwd=work, stdout=so, stderr=se)
        identities = []
        try:
            ids = [wait(work / (role + "_ready.json"))["pid"] for role in ("root", "helper", "leaf")]
            owned_pids.update(ids)
            identities = [guard.identity(limited_process(pid)) for pid in ids]
            root_id, helper, leaf = identities
            write(work / "owned.json", identities)
            binding = {k: root_id[k] for k in ("pid", "create_time", "exe", "cwd")}
            binding.update(allowed_run_dirs=[str(work)], source_commit="4288795b1e8c75b98cbbeb69ac33709172e97c66", run_id=case, fixture_test=True)
            monitor = guard.Guard(plan, binding, work, {"tree_rss_bytes": 134217728, "available_ram_bytes": 0, "c_disk_free_bytes": 0})
            monitor.initial_root = root_id
            monitor.event_file = (work / "events.jsonl").open("x", encoding="utf-8")
            monitor.samples = (work / "samples.jsonl").open("x", encoding="utf-8")
            records = []
            if case == "A_known":
                members, unknown, exited = monitor.collect(root_id)
                check("A 首次完整实时六字段链登记", not unknown and len(members) == 3 and len(monitor.known_lineage) == 2)
                monitor.last_members.update({(x["pid"], x["create_time"]): x for x in members})
                leave(work, "helper", helper)
                for index in (1, 2):
                    monitor.sample_count = index
                    members, unknown, exited = monitor.collect(root_id)
                    historical = [x for x in members if x["pid"] == leaf["pid"]]
                    check("A 祖先真实缺失持续采样" + str(index), not unknown and len(historical) == 1 and historical[0]["lineage_mode"] == "HISTORICAL_CHAIN" and historical[0]["stoppable"] is False and historical[0]["rss_bytes"] > 0)
                    record = {"index": index, "members": members, "uncertain": unknown, "confirmed_exits": exited}
                    records.append(record); monitor.samples.write(json.dumps(record, ensure_ascii=False) + "\n"); monitor.samples.flush()
                    monitor.last_members.update({(x["pid"], x["create_time"]): x for x in members})
                    sample_peak(identities); time.sleep(1)
                outcome = monitor.stop_one(historical[0], root_id, "INDEPENDENT_STOP_GATE")
                check("A 历史身份绝不授予停止权", outcome["status"] == "BLOCKED" and guard.base_identity(limited_process(leaf["pid"]))["create_time"] == leaf["create_time"])
                status, stopped, retained = monitor.stop_tree(root_id, members, [], "INDEPENDENT_STOP_GATE")
                check("A stop闭合保留历史孤儿与root", status == "BLOCKED" and not stopped and retained and limited_process(root_id["pid"]).is_running())
                changed = dict(leaf, ppid=-1)
                try: monitor.historical_member(changed, root_id)
                except RuntimeError: check("C 注入ppid漂移拒绝历史监控", True)
                else: raise AssertionError("ppid漂移漏拒绝")
                unknown = {"expected": leaf, "status": "UNKNOWN", "error": "独立注入AccessDenied"}
                original_readback = monitor.readback_member
                monitor.readback_member = lambda expected: unknown if expected["pid"] == leaf["pid"] else original_readback(expected)
                _, uncertain, _ = monitor.collect(root_id)
                check("D 注入真实读回UNKNOWN语义阻断", bool(uncertain))
                monitor.readback_member = original_readback
                # 复用只作身份规则注入；不声称OS真的复用PID。
                reused_expected = dict(leaf, create_time=leaf["create_time"] - 1)
                reused = monitor.readback_member(reused_expected)
                check("C 注入出生身份不符拒绝并保留新对象", reused["status"] == "ORIGINAL_PID_REUSED" and reused["new_object_untouched"] and limited_process(leaf["pid"]).is_running())
                leave(work, "root", root_id)
                code = monitor.root_terminal("ROOT_MISSING", None)
                terminal = load(work / "guard_receipt.json", "result")
                check("D ROOT真实退出活孤儿明确非零保留", code == 3 and terminal["status"] == "ROOT_EXITED_WITH_REMAINING" and terminal["retained"] and limited_process(leaf["pid"]).is_running())
            else:
                leave(work, "helper", helper)
                # OS root枚举不会发现未知孤儿；显式注入该own候选验证安全拒绝。
                real_children = real_process.children
                real_process.children = lambda process, recursive=False: [limited_process(leaf["pid"])] if process.pid == root_id["pid"] else real_children(process, recursive=recursive)
                try: members, unknown, exited = monitor.collect(root_id)
                finally: real_process.children = real_children
                check("B 未登记孤儿候选阻断且不收编", bool(unknown) and all(x["pid"] != leaf["pid"] for x in members) and not monitor.known_lineage)
                check("B 未知对象实际仍活未停止", limited_process(leaf["pid"]).is_running())
            write(work / "independent_result.json", {"case": case, "status": "PASS", "injection_limits": "B候选枚举/C身份差异/DUNKNOWN均显式注入；祖先/root退出及RSS为真实自有夹具"})
            fixture_rows.append({"case": case, "status": "PASS"})
        finally:
            cleanup = []
            for item in reversed(identities):
                try: actual = guard.base_identity(limited_process(item["pid"]))
                except psutil.NoSuchProcess:
                    cleanup.append({"expected": item, "status": "ABSENT"}); continue
                assert guard.same_identity(item, actual), "清理身份不符必须保留"
                process = limited_process(item["pid"]); process.terminate(); native = process.wait(timeout=3)
                cleanup.append({"identity": actual, "status": "STOPPED_OWN_FIXTURE_ONLY", "native_process_exit_code": native})
            child.wait(timeout=3)
            if "monitor" in locals():
                monitor.event_file.close(); monitor.samples.close()
            write(work / "cleanup.json", cleanup)
            owned_pids.difference_update(ids)
psutil.Process = real_process
write(base / "review_inputs.json", list(inputs.values()))
write(base / "review_result.json", {"status": "PASS", "checks": checks, "findings": [], "scope": "S11资源guard本次历史链只监控语义、未知/身份漂移/根退出与停止闭合门禁；supervisor固定绑定与新资源计划只读审查", "source_commit": "4288795b1e8c75b98cbbeb69ac33709172e97c66", "reviewed_source_hashes": {"guard": sha(candidate), "supervisor": sha(supervisor), "resource_plan": sha(plan_data)}, "reviewer_stop": "STOP_READONLY_REVIEW", "elapsed_seconds": time.monotonic()-started, "sampled_owned_fixture_rss_peak_bytes": peak, "absolute_peak_bytes": None, "fixture_results": fixture_rows, "limitations": ["仅工具G2语义，不批准真实预算达标/STA/产品/实板；S10缺测与4.5GiB未达仍原状", "代表性自有夹具A/B串行；未重跑Developer13全套。C出生与ppid差异/DUNKNOWN/B孤儿候选均显式注入，不声称OS真实复用", "测试直接调用候选collect/stop_one/stop_tree/root_terminal，未启动生产guard CLI/supervisor/ROOT集成；未查询或停止其它任务PID", "所有RSS是离散读回，仅自有轻量测试；128MiB本轮工具预算，正式6GiB/512MiB/8GiB/1秒不变", "810原件只核SHA不复制；实际资源计划PREPARED_NOT_EXECUTED；ROOT启动首样本/身份与5秒监督集成仍须实际执行"]})
print(json.dumps({"status": "PASS", "checks": len(checks), "fixture_peak": peak}, ensure_ascii=False))
