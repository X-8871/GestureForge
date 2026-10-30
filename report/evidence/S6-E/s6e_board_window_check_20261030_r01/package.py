#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""固定封包主机与一次枚举记录；包装检查不替代板卡或业务验收。"""
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
BASE = "8d30a9ff693284d5d8fffcd676c6ca94627e6790"
PYTHON = sys.executable
os.environ["PYTHONIOENCODING"] = "utf-8"


def read(name):
    return json.loads((RUN / name).read_text(encoding="utf-8"))


def write(name, value):
    """仅更新本脚本独占的派生封包文件，原始输入和执行记录保持不动。"""
    (RUN / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def member(path, role):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role, "hash_basis": "worktree_disk"}


def base():
    return {"schema_version": 1, "stage": "6", "task_id": "S6-E", "run_id": RUN.name,
            "source_commit": BASE, "evidence_dir": REL, "interfaces": [],
            "interfaces_not_applicable_reason": "仅主机预检与只读拓扑枚举，不读写业务接口；P与业务实物验证不在本次操作范围",
            "hash_basis": "worktree_disk", "hash_basis_note": "包内新文件按磁盘字节保真；固定上游输入权威基座见source_bindings的commit_blob",
            "tool_versions": {"python": sys.version.split()[0], "git": subprocess.check_output(["git", "--version"], text=True).strip(),
                              "powershell": read("host_snapshot_post.json")["host"]["PowerShellVersion"]},
            "limitations": ["包装CHECKS_OK不代表G3/G4/G5或业务验收", "未执行T6-A03帧周期采集、6-E业务实物验收或200ms新鲜度验证", "未交付真实生产推理结果，6-D不预判PASS", "峰值内存未测"]}


def manifests():
    inputs = base()
    inputs["files"] = [member(p, "input") for p in sorted(RUN.glob("input_*")) if p.is_file()]
    inputs["checks"] = [{"name": "fixed_input_snapshot_binding", "status": "PASS", "command": "capture.py inputs; package.py reverify fixed commit blobs", "exit_code": 0}]
    write("inputs_manifest.json", inputs)
    delivery = base()
    delivery["checks"] = [{"name": "host_snapshot_query", "status": "PASS", "command": "capture.py capture --label pre; capture.py capture --label post", "exit_code": 0, "reason": "仅查询成功；post存在后继DSH会话，不声明主机空闲"},
                          {"name": "T6-A03", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "未执行真实帧周期事件采集"},
                          {"name": "S6-E-business-acceptance", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "本次最多只读拓扑枚举，未执行业务实物验收"}]
    execution = read("execution.json")
    result = execution["status"]
    # 检查器的command字段限定字符串，故将真实argv与工作目录编码在同一JSON字符串中。
    invocation = {"argv": [PYTHON, "-X", "utf8", "-B", str(RUN / "enumerate_once.py"), "--execute-once"],
                  "working_directory": str(MAIN)}
    check = {"name": "readonly-topology-once", "command": json.dumps(invocation, ensure_ascii=False)}
    if result == "PASS_READONLY_TOPOLOGY":
        check.update(status="PASS", exit_code=0)
    elif result == "NOT_RUN":
        check.update(status="NOT_RUN", exit_code=None, reason="协调器在启动硬件前停止；实际原因见execution.json")
    else:
        check.update(status="FAIL", exit_code=1, reason="一次枚举或收窗核验未通过；不重试，原始结果见execution.json")
    delivery["checks"].append(check)
    delivery["files"] = []
    for path in sorted(RUN.rglob("*")):
        if not path.is_file() or path.name == "delivery_manifest.json":
            continue
        role = "source" if path.suffix in {".py", ".tcl"} else "input" if path.name.startswith("input_") else "result"
        delivery["files"].append(member(path, role))
    write("delivery_manifest.json", delivery)


def verify_inputs():
    """再次按固定提交校验上游原件和本包快照，不读取其他工作区数据。"""
    for item in read("source_bindings.json")["bindings"]:
        snapshot = RUN / item["snapshot"]
        assert sha(snapshot) == item["sha256"], item["snapshot"]
        if item["hash_basis"] == "commit_blob":
            content = subprocess.check_output(["git", "--no-optional-locks", "-C", item["repository"], "cat-file", "blob", f'{item["commit"]}:{item["path"]}'])
            assert content == snapshot.read_bytes(), item["path"]


def main():
    verify_inputs()
    pre, post = read("host_snapshot_pre.json"), read("host_snapshot_post.json")
    assert pre["host_query_status"] == post["host_query_status"] == "PASS"
    assert pre["identity_check"] == post["identity_check"] == "PASS"
    assert not read("protected_worktree_check.json")["mismatches"]
    assert (RUN / "execution.json").is_file(), "总控执行记录尚未交付"
    assert (RUN / "qualification.json").is_file(), "须由总控确认一次枚举最终状态后填写资格结论"
    write("host_snapshot.json", {"pre": "host_snapshot_pre.json", "post": "host_snapshot_post.json", "host_query_checks": "PASS",
          "post_host_idle": not bool(post["host"]["Listeners"]) and not any(p["Name"].lower() in {"hw_server.exe", "xsdb.exe", "vivado.exe", "xsim.exe", "vitis.exe"} for p in post["host"]["Processes"]),
          "scope": "主机观测不证明P3q位流身份、PS停止状态、实际推理或实物验收", "powershell_version": post["host"]["PowerShellVersion"]})
    commands = {
        "inputs": [PYTHON, "-B", str(RUN / "input_check_stage_delivery.py"), "--mode", "inputs", "--project-root", str(ROOT), "--manifest", str(RUN / "inputs_manifest.json")],
        "evidence": [PYTHON, "-B", str(RUN / "input_check_stage_delivery.py"), "--mode", "evidence", "--project-root", str(ROOT), "--manifest", str(RUN / "delivery_manifest.json")],
        "strict": [PYTHON, "-B", str(RUN / "input_check_manifest_hash_basis.py"), "--repo", str(ROOT), "--paths", REL + "/inputs_manifest.json", "--paths", REL + "/delivery_manifest.json", "--mode", "strict", "--json"]}
    # 先预置日志成员，再运行整批只读检查；仅在输出稳定时宣布固定点。
    for name in commands:
        if not (RUN / f"check_{name}.json").exists():
            write(f"check_{name}.json", {})
    for round_number in range(1, 9):
        manifests()
        results = {}
        for name, command in commands.items():
            proc = subprocess.run(command, cwd=ROOT, capture_output=True)
            results[name] = {"command": command, "exit_code": proc.returncode,
                             "stdout": proc.stdout.decode("utf-8-sig", "replace"), "stderr": proc.stderr.decode("utf-8-sig", "replace")}
        stable = all(read(f"check_{name}.json") == result for name, result in results.items())
        if stable and all(result["exit_code"] == 0 for result in results.values()):
            print(json.dumps({"status": "PACKAGING_FIXED_POINT", "rounds": round_number,
                              "manifest_sha256": sha(RUN / "delivery_manifest.json"), "scope": "仅包装检查通过"}, ensure_ascii=False))
            return 0
        for name, result in results.items():
            # 保留每次真实失败，成功日志只取最后一次；不覆盖原始失败记录。
            if result["exit_code"] != 0:
                failure = RUN / f"packaging_failure_{round_number:02d}_{name}.json"
                if failure.exists():
                    raise RuntimeError("失败轨迹已存在；禁止重跑同一RunId封包")
                write(failure.name, result)
            write(f"check_{name}.json", result)
    raise RuntimeError("八轮内未达固定点，不能声称封包成功")


if __name__ == "__main__":
    raise SystemExit(main())
