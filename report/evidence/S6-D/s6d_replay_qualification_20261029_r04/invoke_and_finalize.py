#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""捕获真实构建进程并闭合 R04 清单。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

RUN_ID = "s6d_replay_qualification_20261029_r04"
RUN_REL = f"report/evidence/S6-D/{RUN_ID}"
W6_ROOT = Path(r"D:\codex-worktrees\w6")
MAIN_ROOT = Path(r"D:\FPGA_Competition")
RUN_DIR = W6_ROOT / RUN_REL
BUILD_SCRIPT = RUN_DIR / "build_qualification.py"
WRAPPER = RUN_DIR / "invoke_and_finalize.py"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location("s6d_r04_builder", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 R04 构建器")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    command = [sys.executable, "-B", "-X", "utf8", str(BUILD_SCRIPT.resolve())]
    proc = subprocess.run(command, cwd=str(W6_ROOT), capture_output=True, check=False)
    output = proc.stdout + (b"\n[stderr]\n" if proc.stderr else b"") + proc.stderr
    output_path = RUN_DIR / "build_invocation_output.txt"
    output_path.write_bytes(output)
    invocation = {
        "schema_version": 1,
        "run_id": RUN_ID,
        "evidence_dir": RUN_REL,
        "command": command,
        "cwd": str(W6_ROOT),
        "exit_code": proc.returncode,
        "captured_at": datetime.now(timezone.utc).astimezone(
            timezone(timedelta(hours=8))).isoformat(),
        "timezone": "UTC+08:00",
        "scope": "offline_replay_only",
        "constraints": ["未连接或操作板卡", "未调用阶段6核心状态机"],
        "build_script_sha256": sha(BUILD_SCRIPT.read_bytes()),
        "stdout_sha256": sha(proc.stdout),
        "stderr_sha256": sha(proc.stderr),
        "output_path": f"{RUN_REL}/build_invocation_output.txt",
        "output_sha256": sha(output),
    }
    invocation_path = RUN_DIR / "build_invocation.json"
    write_json(invocation_path, invocation)

    builder = load_builder()
    command_path = RUN_DIR / "qualification_commands.json"
    if not command_path.is_file():
        return proc.returncode or 2
    commands = json.loads(command_path.read_text(encoding="utf-8"))
    commands["schema_version"] = 1
    commands["run_id"] = RUN_ID
    commands["evidence_dir"] = RUN_REL
    commands["build_qualification"] = {
        "command": command,
        "cwd": str(W6_ROOT),
        "exit_code": proc.returncode,
        "output": f"{RUN_REL}/build_invocation_output.txt",
        "output_sha256": sha(output),
        "invocation_record": f"{RUN_REL}/build_invocation.json",
        "invocation_sha256": sha(invocation_path.read_bytes()),
    }
    write_json(command_path, commands)

    result_path = RUN_DIR / "preflight_result.json"
    if result_path.is_file():
        result = json.loads(result_path.read_text(encoding="utf-8"))
        result["evidence_dir"] = RUN_REL
        result.setdefault("initial_commands", {})["build_qualification"] = commands["build_qualification"]
        write_json(result_path, result)

    summary_path = RUN_DIR / "summary.md"
    if summary_path.is_file():
        summary = summary_path.read_text(encoding="utf-8")
        summary += (f"\n- RunId：`{RUN_ID}`；证据目录：`{RUN_REL}/`。"
                    f"\n- 构建调用记录：`{RUN_REL}/build_invocation.json`；真实 cwd、退出码和输出哈希均在该记录中。\n")
        summary_path.write_text(summary, encoding="utf-8")

    delivery_path = RUN_DIR / "delivery_manifest.json"
    if not delivery_path.is_file():
        return proc.returncode or 2
    delivery = json.loads(delivery_path.read_text(encoding="utf-8"))
    delivery["run_id"] = RUN_ID
    delivery["evidence_dir"] = RUN_REL
    build_check = next((item for item in delivery.get("checks", [])
                        if item.get("name") == "R04证据构建命令"), None)
    if build_check is None:
        return proc.returncode or 2
    build_check.update({
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "command": subprocess.list2cmdline(command),
        "exit_code": proc.returncode,
    })
    if proc.returncode != 0:
        build_check["reason"] = f"实际构建子进程退出码为 {proc.returncode}。"

    stable = False
    evidence_index = next(i for i, item in enumerate(delivery["checks"])
                          if item.get("name") == "阶段交付evidence模式")
    hash_index = next(i for i, item in enumerate(delivery["checks"])
                      if item.get("name") == "manifest hash_basis strict")
    for _ in range(8):
        before = tuple(builder.file_sha(RUN_DIR / name) for name in (
            "evidence_check.txt", "hash_basis_check.txt", "qualification_commands.json"))
        builder.refresh_delivery(RUN_DIR, delivery)
        evidence_command = [
            sys.executable, "-B", "-X", "utf8",
            str(MAIN_ROOT / "verification/check_stage_delivery.py"),
            "--mode", "evidence", "--manifest", str(delivery_path),
            "--project-root", str(W6_ROOT),
        ]
        evidence = builder.run(evidence_command, MAIN_ROOT, RUN_DIR / "evidence_check.txt")
        commands["evidence_manifest"] = evidence
        delivery["checks"][evidence_index] = builder.check_record("阶段交付evidence模式", evidence)
        write_json(command_path, commands)

        builder.refresh_delivery(RUN_DIR, delivery)
        hash_command = [
            sys.executable, "-B", "-X", "utf8",
            str(MAIN_ROOT / "verification/check_manifest_hash_basis.py"),
            "--repo", str(W6_ROOT), "--paths", f"{RUN_REL}/inputs_manifest.json",
            "--paths", f"{RUN_REL}/delivery_manifest.json", "--mode", "strict", "--json",
            "--commit", builder.W6_HEAD,
        ]
        hash_check = builder.run(hash_command, MAIN_ROOT, RUN_DIR / "hash_basis_check.txt")
        commands["manifest_hash_basis"] = hash_check
        delivery["checks"][hash_index] = builder.check_record("manifest hash_basis strict", hash_check)
        write_json(command_path, commands)
        if evidence["exit_code"] != 0 or hash_check["exit_code"] != 0:
            break
        after = tuple(builder.file_sha(RUN_DIR / name) for name in (
            "evidence_check.txt", "hash_basis_check.txt", "qualification_commands.json"))
        if before == after:
            stable = True
            break

    builder.refresh_delivery(RUN_DIR, delivery)
    return 0 if proc.returncode == 0 and stable and all(
        commands.get(key, {}).get("exit_code") == 0 for key in (
            "stage5_frozen_set", "s6d_eligibility_tests", "inputs_manifest",
            "evidence_manifest", "manifest_hash_basis")) else (proc.returncode or 1)


if __name__ == "__main__":
    raise SystemExit(main())
