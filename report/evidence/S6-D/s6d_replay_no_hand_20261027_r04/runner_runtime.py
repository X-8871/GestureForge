#!/usr/bin/env python3
"""运行并收尾阶段6单帧预检，记录主进程真实退出码。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层必须是对象：{path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_record(files: list[dict[str, Any]], path: str) -> dict[str, Any]:
    return next(record for record in files if record.get("path") == path)


def update_hash(files: list[dict[str, Any]], path: str, root: Path, role: str,
                reason: str) -> None:
    record = next((item for item in files if item.get("path") == path), None)
    if record is None:
        record = {"path": path, "role": role, "keep_reason": reason}
        files.append(record)
    record["sha256"] = sha256_file(root / path)


def run_tool(command: list[str], cwd: Path) -> dict[str, Any]:
    result = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=False)
    return {"command": subprocess.list2cmdline(command), "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="阶段6单帧回放预检的可复核执行器")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--w4-root", required=True)
    parser.add_argument("--w5-root", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    run_rel = Path(args.run_dir).as_posix()
    expected_run = "report/evidence/S6-D/s6d_replay_no_hand_20261027_r04"
    if run_rel != expected_run:
        print(f"RunId 路径必须精确为 {expected_run}", file=sys.stderr)
        return 2

    preflight = Path('D:\\tmp\\s6d_r04_frozen_blob_39axw8oo\\s6d_replay_preview_preflight_r04.py')
    child_command = [sys.executable, "-B", "-X", "utf8", str(preflight), "--project-root", str(root),
                     "--w4-root", str(Path(args.w4_root).resolve()),
                     "--w5-root", str(Path(args.w5_root).resolve()), "--run-dir", run_rel]
    child = subprocess.run(child_command, cwd=str(root), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", check=False)
    run_dir = root / run_rel
    if not run_dir.is_dir():
        if child.stdout:
            print(child.stdout, end="")
        if child.stderr:
            print(child.stderr, end="", file=sys.stderr)
        return child.returncode

    output_text = child.stdout + child.stderr
    output_path = run_dir / "runner_output.txt"
    exit_path = run_dir / "runner_exit_code.txt"
    output_path.write_text(output_text, encoding="utf-8")
    exit_path.write_text(f"{child.returncode}\n", encoding="utf-8")

    result_path = run_dir / "preflight_result.json"
    result_doc = read_json(result_path)
    result_doc["runner_process"] = {
        "command": subprocess.list2cmdline(child_command),
        "cwd": str(root),
        "exit_code": child.returncode,
        "output_path": f"{run_rel}/runner_output.txt",
        "output_sha256": sha256_file(output_path),
    }
    write_json(result_path, result_doc)

    inputs_path = run_dir / "inputs_manifest.json"
    inputs_doc = read_json(inputs_path)
    preflight_rel = f"{run_rel}/preflight_result.json"
    file_record(inputs_doc["files"], preflight_rel)["sha256"] = sha256_file(result_path)
    write_json(inputs_path, inputs_doc)

    delivery_path = run_dir / "delivery_manifest.json"
    delivery_doc = read_json(delivery_path)
    delivery_files = delivery_doc["files"]
    delivery_doc["checks"].append({
        "name": "主预检 runner 实际进程退出",
        "status": ("BLOCKED" if child.returncode == 2 and result_doc.get("status") == "BLOCKED"
                   else "PASS" if child.returncode == 0 else "FAIL"),
        "command": subprocess.list2cmdline(child_command),
        "exit_code": (None if child.returncode == 2 and result_doc.get("status") == "BLOCKED"
                      else child.returncode),
        **({"reason": "主预检按输入资格门返回 BLOCKED；这不是结构或清单检查失败。"}
           if child.returncode == 2 and result_doc.get("status") == "BLOCKED" else {}),
    })
    update_hash(delivery_files, preflight_rel, root, "result", "绑定主 runner 实际退出码的最终预检结果")
    update_hash(delivery_files, f"{run_rel}/inputs_manifest.json", root, "result", "实际输入清单")
    update_hash(delivery_files, f"{run_rel}/runner_output.txt", root, "log", "主预检 runner 的真实 stdout/stderr")
    update_hash(delivery_files, f"{run_rel}/runner_exit_code.txt", root, "log", "主预检 runner 的真实进程退出码")

    checker = root / "verification/check_stage_delivery.py"
    inputs_command = [sys.executable, "-B", "-X", "utf8", str(checker), "--mode", "inputs",
                      "--manifest", str(inputs_path), "--project-root", str(root)]
    inputs_check = run_tool(inputs_command, root)
    inputs_log = run_dir / "check_inputs_mode_output.txt"
    inputs_log.write_text(inputs_check["stdout"] + inputs_check["stderr"], encoding="utf-8")
    for item in delivery_doc["checks"]:
        if item.get("name") == "阶段交付 inputs 模式":
            item.update({"status": "PASS" if inputs_check["exit_code"] == 0 else "FAIL",
                         "command": inputs_check["command"], "exit_code": inputs_check["exit_code"]})
    update_hash(delivery_files, f"{run_rel}/inputs_manifest.json", root, "result", "实际输入清单")
    update_hash(delivery_files, f"{run_rel}/check_inputs_mode_output.txt", root, "log",
                "最终阶段交付输入清单核验 stdout/stderr")

    evidence_log_rel = f"{run_rel}/check_evidence_mode_output.txt"
    evidence_log = run_dir / "check_evidence_mode_output.txt"
    if not evidence_log.exists():
        evidence_log.write_text("evidence checker 尚未运行。\n", encoding="utf-8")
    update_hash(delivery_files, evidence_log_rel, root, "log", "最终阶段交付 evidence 核验 stdout/stderr")
    evidence_command = [sys.executable, "-B", "-X", "utf8", str(checker), "--mode", "evidence",
                        "--manifest", str(delivery_path), "--project-root", str(root)]
    evidence_exit = 2
    previous_output: str | None = None
    previous_exit: int | None = None
    stable = False
    evidence_check = None
    for _ in range(6):
        write_json(delivery_path, delivery_doc)
        evidence_check = run_tool(evidence_command, root)
        evidence_exit = evidence_check["exit_code"]
        evidence_output = evidence_check["stdout"] + evidence_check["stderr"]
        for item in delivery_doc["checks"]:
            if item.get("name") == "阶段交付 evidence 模式":
                item.update({"status": "PASS" if evidence_exit == 0 else "FAIL",
                             "command": evidence_check["command"], "exit_code": evidence_exit})
                if evidence_exit != 0:
                    item["reason"] = "最终清单 evidence 模式失败"
                else:
                    item.pop("reason", None)
        evidence_log.write_text(evidence_output, encoding="utf-8")
        update_hash(delivery_files, evidence_log_rel, root, "log",
                    "最终阶段交付 evidence 核验 stdout/stderr")
        write_json(delivery_path, delivery_doc)
        if evidence_output == previous_output and evidence_exit == previous_exit:
            stable = True
            break
        previous_output = evidence_output
        previous_exit = evidence_exit
    if not stable:
        for item in delivery_doc["checks"]:
            if item.get("name") == "阶段交付 evidence 模式":
                item.update({"status": "FAIL", "exit_code": evidence_exit,
                             "reason": "evidence checker 输出与清单哈希绑定未稳定"})
        write_json(delivery_path, delivery_doc)

    final_status = "PASS" if evidence_exit == 0 and inputs_check["exit_code"] == 0 else "FAIL"
    print(json.dumps({"runner_exit_code": child.returncode,
                      "runner_status": result_doc.get("status"),
                      "upstream_audit_exit_code": (result_doc.get("independent_upstream_audit") or {}).get("exit_code"),
                      "inputs_check_exit_code": inputs_check["exit_code"],
                      "evidence_check_exit_code": evidence_exit,
                      "evidence_output_stable": stable,
                      "delivery_checker_status": final_status}, ensure_ascii=False))
    if child.stdout:
        print(child.stdout, end="")
    if child.stderr:
        print(child.stderr, end="", file=sys.stderr)
    if final_status != "PASS":
        return 1
    return child.returncode


if __name__ == "__main__":
    raise SystemExit(main())
