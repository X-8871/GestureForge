#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""包装离线官方入口记录；包装通过不代表硬件、业务或阶段验收。"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
MAIN = Path(r"D:\FPGA_Competition")
REL = RUN.relative_to(ROOT).as_posix()
BASE = "b0f4a688aa618f891b673c9b779f6b68f6e7472c"
PYTHON = sys.executable
os.environ["PYTHONIOENCODING"] = "utf-8"


def read(name):
    return json.loads((RUN / name).read_text(encoding="utf-8"))


def write(name, value):
    """只更新本脚本拥有的派生文件，原始输入和执行轨迹不改写。"""
    (RUN / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def member(path, role):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role, "hash_basis": "worktree_disk"}


def verify_inputs():
    """重新消费相同固定blob比对快照，不能改为跟随最新文件。"""
    for item in read("source_bindings.json")["bindings"]:
        snapshot = RUN / item["snapshot"]
        if sha(snapshot) != item["sha256"] or item["hash_basis"] != "commit_blob":
            raise ValueError("输入快照哈希或基座不符: " + item["snapshot"])
        content = subprocess.check_output(["git", "--no-optional-locks", "-c", "core.longpaths=true", "-C", item["repository"],
                                           "cat-file", "blob", f'{item["commit"]}:{item["path"]}'])
        if content != snapshot.read_bytes():
            raise ValueError("输入快照不等于固定blob: " + item["snapshot"])


def execution_check(execution):
    """只使用执行记录的真实命令和返回码；缺少信息即停止封包。"""
    invocation = execution.get("invocation")
    if not isinstance(invocation, dict) or not isinstance(invocation.get("argv"), list) or not invocation["argv"]:
        raise ValueError("execution缺真实invocation.argv，不得推测命令")
    if not isinstance(invocation.get("working_directory"), str) or not invocation["working_directory"]:
        raise ValueError("execution缺真实工作目录")
    status = execution.get("status")
    code = invocation.get("exit_code")
    if status == "NOT_RUN":
        return {"name": "official-xsdb-offline-entry", "status": "NOT_RUN", "command": json.dumps(invocation, ensure_ascii=False),
                "exit_code": None, "reason": execution.get("reason") or "协调器在厂商入口执行前停止，实际原因见execution.json"}
    if not isinstance(code, int) or isinstance(code, bool):
        raise ValueError("execution缺真实wrapper exit_code，不得假设成功")
    passed = status == "PASS_OFFLINE_ENTRY" and code == 0
    return {"name": "official-xsdb-offline-entry", "status": "PASS" if passed else "FAIL",
            "command": json.dumps(invocation, ensure_ascii=False), "exit_code": code,
            "reason": "仅验证离线入口及收尾；没有connect、板卡访问或业务验收" if passed else "实际入口或清理未通过；保留原始execution/log，不在本RunId重试"}


def runtime_observation(execution):
    """把真实子进程原件与总控外层记录逐字段对齐，不重复执行探针。"""
    if execution.get("runtime_directory") != "runtime_offline_01":
        raise ValueError("执行记录不是约定唯一runtime_offline_01")
    runtime = read("runtime_offline_01/execution.json")
    plan = read("runtime_offline_01/launch_plan.json")
    invocation = execution["invocation"]
    if plan["launcher_argv"] != invocation["argv"] or plan["launcher_cwd"] != invocation["working_directory"]:
        raise ValueError("外层argv/cwd与真实launch_plan不一致")
    for name in ["application", "command_line", "cwd"]:
        if runtime[name] != plan[name]:
            raise ValueError("真实子进程计划与结果不一致: " + name)
    after = [sample for sample in runtime["job_samples"] if sample["phase"] == "after_cleanup"]
    stdout = (RUN / "runtime_offline_01/stdout.bin").read_bytes()
    stderr = (RUN / "runtime_offline_01/stderr.bin").read_bytes()
    if execution.get("status") == "PASS_OFFLINE_ENTRY":
        if not (runtime["status"] == "PASS" and runtime["root_exit_code"] == 0 and runtime["cleanup_confirmed"] is True
                and runtime["job_handle_closed"] is True and len(after) == 1 and after[0]["ActiveProcesses"] == 0
                and not after[0]["pids"] and not runtime["errors"] and not runtime["timed_out"]
                and stdout.splitlines() == [b"8.6.13"] and not stderr):
            raise ValueError("总控PASS与runtime/输出/清理真实证据不一致")
    return {"runtime_status": runtime["status"], "child_invocation": {"argv": plan["argv"], "command_line": runtime["command_line"],
             "working_directory": runtime["cwd"], "application": runtime["application"]},
            "root_exit_code": runtime.get("root_exit_code"), "root_exit_code_after_cleanup": runtime.get("root_exit_code_after_cleanup"),
            "elapsed_seconds": runtime["elapsed_seconds"], "cleanup_confirmed": runtime["cleanup_confirmed"],
            "job_samples": runtime["job_samples"], "stdout": stdout.decode("utf-8", "replace"), "stdout_bytes": len(stdout),
            "stderr_bytes": len(stderr), "source": "runtime_offline_01/execution.json、launch_plan.json及原始stdout.bin/stderr.bin",
            "vendor_execution_runs": len(list(RUN.glob("runtime_offline_*/execution.json")))}


def base():
    return {"schema_version": 1, "stage": "6", "task_id": "S6-E", "run_id": RUN.name,
            "source_commit": BASE, "evidence_dir": REL, "interfaces": [],
            "interfaces_not_applicable_reason": "只验证官方XSDB离线入口与主机收尾；没有连接板卡，不消费业务接口",
            "hash_basis": "worktree_disk", "hash_basis_note": "新包按磁盘字节保真；固定输入权威基座见source_bindings的commit_blob",
            "tool_versions": {"python": sys.version.split()[0], "git": subprocess.check_output(["git", "--version"], text=True).strip(),
                              "powershell": read("host_snapshot_post.json").get("host", {}).get("PowerShellVersion", "采集失败，详见host_query")},
            "limitations": ["CHECKS_OK只证明包装和文件绑定，不代表G3/G4/G5或业务验收", "本包没有connect、JTAG拓扑枚举、内存寄存器访问、程序控制或板卡状态核验",
                            "T6-A03、真实推理、200ms新鲜度与阶段6业务验收均未执行", "主机查询与所列进程端口空闲观测分别记录，不证明板卡状态或独占租约", "峰值内存未测"]}


def qualification():
    execution = read("execution.json")
    actual = execution_check(execution)
    pre, post = read("host_snapshot_pre.json"), read("host_snapshot_post.json")
    guards = {name: read(name) for name in ["protected_worktree_check.json", "protected_worktree_check_post.json"]}
    receipt = read("review_receipt.json")
    observation = runtime_observation(execution)
    write("qualification.json", {"schema_version": 1, "task_id": "S6-E", "run_id": RUN.name,
          "scope": "官方XSDB入口离线恢复验证；没有板卡操作", "source_commit": BASE,
          "actual_entry_check": actual, "actual_runtime_observation": observation,
          "execution_record": "execution.json", "source_review_receipt": "review_receipt.json",
          "source_review_status": receipt.get("status", "NOT_RUN"),
          "host_queries": {"pre": pre["host_query_status"], "post": post["host_query_status"]},
          "worktree_identity": {"pre": pre["identity_check"], "post": post["identity_check"]},
          "host_observations": {"pre": pre.get("host_observation"), "post": post.get("host_observation")},
          "protection": {name: {"files": guard["file_count"], "mismatches": guard["mismatches"]} for name, guard in guards.items()},
          "hardware_connect_performed": execution.get("hardware_connect_performed", execution.get("hardware_api_called")),
          "hardware_memory_access_performed": execution.get("hardware_memory_access_performed", execution.get("memory_or_register_access")),
          "board_programmed": execution.get("board_programmed"), "serial_opened": execution.get("serial_opened"),
          "hardware_scope_basis": "只复制总控execution的明确观察/声明；缺失项为null，不根据主机查询推断硬件状态",
          "business_statuses": {"JTAG_topology": "NOT_RUN", "P3q_identity": "NOT_VERIFIED", "PS_stop_state": "NOT_VERIFIED",
                                "T6_A03": "NOT_RUN", "real_inference": "NOT_RUN", "S6_E_business_acceptance": "NOT_RUN", "stage6_G3_G4_G5": "NOT_PASSED"},
          "peak_memory_bytes": None, "peak_memory_note": "未测量峰值内存",
          "packaging_scope": "入口执行、独立源码审查与包装检查分开；包内CHECKS_OK不能替代实物验收"})


def manifests():
    inputs = base()
    inputs["files"] = [member(p, "input") for p in sorted(RUN.glob("input_*")) if p.is_file()]
    inputs["checks"] = [{"name": "fixed_input_snapshot_binding", "status": "PASS", "command": "package.py verify_inputs: git cat-file blob at exact source_bindings commits", "exit_code": 0}]
    write("inputs_manifest.json", inputs)
    delivery = base()
    delivery["checks"] = []
    for label in ["pre", "post"]:
        snapshot = read(f"host_snapshot_{label}.json")
        query = snapshot["host_query"]
        delivery["checks"].append({"name": f"host-query-{label}", "status": snapshot["host_query_status"],
            "command": json.dumps({"argv": query["argv"], "working_directory": query["working_directory"]}, ensure_ascii=False),
            "exit_code": query["exit_code"], "reason": "只表示CIM/设备/监听查询是否成功，空闲观测另见host_observation"})
    delivery["checks"].append(execution_check(read("execution.json")))
    for name in ["JTAG-topology", "T6-A03", "S6-E-business-acceptance"]:
        delivery["checks"].append({"name": name, "status": "NOT_RUN", "command": None, "exit_code": None,
                                   "reason": "离线入口验证范围不包含板卡或业务实物操作"})
    delivery["files"] = []
    for path in sorted(RUN.rglob("*")):
        if not path.is_file() or path.name == "delivery_manifest.json":
            continue
        role = "input" if path.name.startswith("input_") else "source" if path.suffix in {".py", ".tcl"} else "log" if path.suffix == ".log" else "result"
        delivery["files"].append(member(path, role))
    write("delivery_manifest.json", delivery)


def main():
    if ROOT != Path(r"D:\codex-worktrees\w6") or RUN.name != "s6e_xsdb_offline_entry_20261030_r01":
        raise ValueError("精确RunId或ROOT不符")
    for name in ["execution.json", "host_snapshot_pre.json", "host_snapshot_post.json", "protected_worktree_check.json", "protected_worktree_check_post.json", "review_receipt.json"]:
        if not (RUN / name).is_file():
            raise ValueError("依赖未交付，禁止提前封包: " + name)
    verify_inputs()
    for name in ["protected_worktree_check.json", "protected_worktree_check_post.json"]:
        if read(name)["file_count"] != 297 or read(name)["mismatches"]:
            raise ValueError("297项保护未通过: " + name)
    qualification()
    commands = {
        "inputs": [PYTHON, "-X", "utf8", "-B", str(RUN / "input_check_stage_delivery.py"), "--mode", "inputs", "--project-root", str(ROOT), "--manifest", str(RUN / "inputs_manifest.json")],
        "evidence": [PYTHON, "-X", "utf8", "-B", str(RUN / "input_check_stage_delivery.py"), "--mode", "evidence", "--project-root", str(ROOT), "--manifest", str(RUN / "delivery_manifest.json")],
        "strict": [PYTHON, "-X", "utf8", "-B", str(RUN / "input_check_manifest_hash_basis.py"), "--repo", str(ROOT), "--paths", REL + "/inputs_manifest.json", "--paths", REL + "/delivery_manifest.json", "--mode", "strict", "--json"]}
    for name in commands:
        if not (RUN / f"check_{name}.json").exists():
            write(f"check_{name}.json", {})
    # 先将真实日志纳入清单，再复跑达到逐字节固定点；保留所有失败原始输出。
    for round_number in range(1, 9):
        manifests()
        results = {}
        for name, command in commands.items():
            proc = subprocess.run(command, cwd=ROOT, capture_output=True)
            results[name] = {"argv": command, "working_directory": str(ROOT), "exit_code": proc.returncode,
                             "stdout": proc.stdout.decode("utf-8-sig", "replace"), "stderr": proc.stderr.decode("utf-8-sig", "replace")}
        stable = all(read(f"check_{name}.json") == result for name, result in results.items())
        if stable and all(result["exit_code"] == 0 for result in results.values()):
            print(json.dumps({"status": "PACKAGING_FIXED_POINT", "rounds": round_number, "manifest_sha256": sha(RUN / "delivery_manifest.json"),
                              "scope": "仅包装检查通过"}, ensure_ascii=False))
            return 0
        for name, result in results.items():
            if result["exit_code"] != 0:
                target = RUN / f"packaging_failure_{round_number:02d}_{name}.json"
                if target.exists():
                    raise ValueError("失败记录已存在，禁止覆盖同RunId轨迹")
                with target.open("x", encoding="utf-8", newline="\n") as stream:
                    json.dump(result, stream, ensure_ascii=False, indent=2)
                    stream.write("\n")
            write(f"check_{name}.json", result)
    raise ValueError("八轮内未达固定点，不能声称包装成功")


if __name__ == "__main__":
    raise SystemExit(main())
