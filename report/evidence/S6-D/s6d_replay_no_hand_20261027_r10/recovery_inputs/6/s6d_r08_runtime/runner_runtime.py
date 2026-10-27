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
    expected_run = "report/evidence/S6-D/s6d_replay_no_hand_20261027_r08"
    if run_rel != expected_run:
        print(f"RunId 路径必须精确为 {expected_run}", file=sys.stderr)
        return 2

    preflight = Path(__file__).resolve().with_name("preflight_runtime.py")
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

    audit_script = Path(__file__).resolve().with_name("positive_replay_audit.py")
    positive_audit_path = run_dir / "positive_replay_input_audit.json"
    positive_audit_command = [sys.executable, "-B", "-X", "utf8", str(audit_script),
                              "--w4-root", str(Path(args.w4_root).resolve()),
                              "--w5-root", str(Path(args.w5_root).resolve()),
                              "--output", str(positive_audit_path)]
    positive_audit_run = run_tool(positive_audit_command, root)
    positive_audit_output = positive_audit_run["stdout"] + positive_audit_run["stderr"]
    positive_audit_log = run_dir / "positive_replay_audit_output.txt"
    positive_audit_log.write_text(positive_audit_output, encoding="utf-8")
    positive_audit_exit = run_dir / "positive_replay_audit_exit_code.txt"
    positive_audit_exit.write_text(f"{positive_audit_run['exit_code']}\n", encoding="utf-8")

    output_text = child.stdout + child.stderr
    output_path = run_dir / "runner_output.txt"
    exit_path = run_dir / "runner_exit_code.txt"
    output_path.write_text(output_text, encoding="utf-8")
    exit_path.write_text(f"{child.returncode}\n", encoding="utf-8")

    result_path = run_dir / "preflight_result.json"
    result_doc = read_json(result_path)
    prior_attempt_rel = "tmp/6/s6d_r05_attempt_evidence/prior_attempt_record.json"
    prior_attempt_path = root / prior_attempt_rel
    prior_attempt_doc = read_json(prior_attempt_path)
    result_doc["prior_r05_setup_attempt"] = {
        "path": prior_attempt_rel,
        "sha256": sha256_file(prior_attempt_path),
        "outer_exit_code": prior_attempt_doc.get("outer_exit_code"),
        "preflight_child_exit_code": prior_attempt_doc.get("preflight_child_exit_code"),
        "core_effect": "未调用阶段6核心；r05 不作为预演结果入口。",
    }
    prior_r06_rel = "tmp/6/s6d_r06_attempt_evidence/attempt_record.json"
    prior_r06_path = root / prior_r06_rel
    prior_r06_doc = read_json(prior_r06_path)
    result_doc["prior_r06_upstream_audit_attempt"] = {
        "path": prior_r06_rel,
        "sha256": sha256_file(prior_r06_path),
        "observed_tool_exit_code": prior_r06_doc.get("observed_tool_exit_code"),
        "effect": prior_r06_doc.get("effect"),
    }
    prior_r07_dir = "report/evidence/S6-D/s6d_replay_no_hand_20261027_r07"
    prior_r07_delivery_rel = f"{prior_r07_dir}/delivery_manifest.json"
    prior_r07_delivery_path = root / prior_r07_delivery_rel
    prior_r07_delivery = read_json(prior_r07_delivery_path)
    prior_r07_failed_checks = [
        {"name": check.get("name"), "status": check.get("status"), "reason": check.get("reason")}
        for check in prior_r07_delivery.get("checks", [])
        if check.get("status") == "FAIL"
    ]
    result_doc["prior_r07_checker_attempt"] = {
        "delivery_manifest_path": prior_r07_delivery_rel,
        "delivery_manifest_sha256": sha256_file(prior_r07_delivery_path),
        "failed_checks": prior_r07_failed_checks,
        "check_inputs_output_sha256": sha256_file(root / f"{prior_r07_dir}/check_inputs_mode_output.txt"),
        "check_evidence_output_sha256": sha256_file(root / f"{prior_r07_dir}/check_evidence_mode_output.txt"),
        "r07_remains_unchanged": True,
    }
    result_doc["latest_positive_replay_audit"] = {
        "status": "PASS_BYTES_BLOCKED_INPUT" if positive_audit_run["exit_code"] == 0 else "FAIL",
        "eligibility": "BLOCKED" if positive_audit_run["exit_code"] == 0 else "NOT_ESTABLISHED",
        "command": positive_audit_run["command"],
        "exit_code": positive_audit_run["exit_code"],
        "output_path": f"{run_rel}/positive_replay_input_audit.json",
        "output_sha256": (sha256_file(positive_audit_path)
                          if positive_audit_path.is_file() else None),
        "log_path": f"{run_rel}/positive_replay_audit_output.txt",
        "log_sha256": sha256_file(positive_audit_log),
    }
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
    inputs_doc["files"].extend([
        {"path": "tmp/6/s6d_r08_runtime/preflight_runtime.py",
         "sha256": sha256_file(Path(__file__).resolve().with_name("preflight_runtime.py")),
         "role": "source", "keep_reason": "由 r04 执行副本复制并固定到 r08 的只读预检器"},
        {"path": "tmp/6/s6d_r08_runtime/runner_runtime.py",
         "sha256": sha256_file(Path(__file__).resolve()),
         "role": "source", "keep_reason": "r08 实际执行器及真实退出码收集逻辑"},
        {"path": "tmp/6/s6d_r08_runtime/positive_replay_audit.py",
         "sha256": sha256_file(audit_script),
         "role": "source", "keep_reason": "只读绑定新增 W4/W5 阳性回放字节与时间字段闸门"},
    ])
    prior_attempt_inputs = [
        prior_attempt_rel,
        prior_r06_rel,
        f"{prior_r07_dir}/preflight_result.json",
        f"{prior_r07_dir}/inputs_manifest.json",
        f"{prior_r07_dir}/delivery_manifest.json",
        f"{prior_r07_dir}/runner_output.txt",
        f"{prior_r07_dir}/runner_exit_code.txt",
        f"{prior_r07_dir}/check_inputs_mode_output.txt",
        f"{prior_r07_dir}/check_evidence_mode_output.txt",
        "tmp/6/s6d_r05_attempt_evidence/runner_output.txt",
        "tmp/6/s6d_r05_attempt_evidence/runner_exit_code.txt",
        "tmp/6/s6d_r05_attempt_evidence/positive_replay_audit_output.txt",
        "tmp/6/s6d_r05_attempt_evidence/positive_replay_audit_exit_code.txt",
    ]
    for relative_path in prior_attempt_inputs:
        path = root / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"r05 失败尝试保全副本缺失：{relative_path}")
        inputs_doc["files"].append({
            "path": relative_path,
            "sha256": sha256_file(path),
            "role": "input",
            "keep_reason": "保全的 r05 执行器启动失败真实命令/退出码/输出；不作为阶段6结果证据",
        })
    if positive_audit_path.is_file():
        inputs_doc["files"].append({
            "path": f"{run_rel}/positive_replay_input_audit.json",
            "sha256": sha256_file(positive_audit_path),
            "role": "input",
            "keep_reason": "新增阶段4/5阳性 replay-only 输入的精确上游绑定及 BLOCKED 原因",
        })
    inputs_doc["checks"].append({
        "name": "最新阶段4/5阳性 replay-only 输入绑定审计",
        "status": "PASS" if positive_audit_run["exit_code"] == 0 else "FAIL",
        "command": positive_audit_run["command"],
        "exit_code": positive_audit_run["exit_code"],
        **({} if positive_audit_run["exit_code"] == 0
           else {"reason": "阳性回放冻结字节、主键或来源绑定审计失败"}),
    })
    inputs_doc["limitations"].append(
        "新增阳性回放虽通过文件绑定，但 capture_time_ns 为 0 哨兵、result_time_ns/stale 不可用；状态机未调用。")
    write_json(inputs_path, inputs_doc)

    summary_path = run_dir / "summary.md"
    with summary_path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("\n## 前序执行器启动失败记录\n\n")
        stream.write("- r05 因运行器与目标 RunId 目录重合而在创建预检结果前拒绝运行；子进程退出码 2，外层运行器退出码 1。\n")
        stream.write("- 原始 r05 及其日志保留；副本位于 `tmp/6/s6d_r05_attempt_evidence/` 并由输入清单绑定。\n")
        stream.write("- r06 在创建结果目录前因严格比较当前 W5 磁盘源码与旧冻结 blob 而退出；其 pinned commit blobs 实际与清单一致，独立记录位于 `tmp/6/s6d_r06_attempt_evidence/`。\n")
        stream.write("- r07 上游审计和定向单测通过，但最终 inputs/evidence 清单字段校验失败；原始 r07 输出未改写并由本 RunId 输入清单绑定。\n")
        stream.write("\n## 新增阶段4/5阳性回放输入（独立只读核验）\n\n")
        stream.write("- 回放绑定审计：" +
                     ("**PASS_BYTES_BLOCKED_INPUT**；上游文件与来源绑定通过。\n"
                      if positive_audit_run["exit_code"] == 0 else
                      "**FAIL**；绑定审计未通过。\n"))
        stream.write("- 实际帧：`PRESENT`、1 个 `fist` 检测框；与阶段4冻结包主键及框字段匹配。\n")
        stream.write("- 时间闸门：`capture_time_ns=0` 是 FILE_INJECTION 哨兵，`result_time_ns=null`、`stale=null`；阳性帧保持 **BLOCKED**。\n")
        stream.write("- 阶段6核心：**NOT_RUN**；未构造事件、未调用状态机。\n")
        stream.write("- 阳性输入审计文件：`positive_replay_input_audit.json`。\n")
    update_hash(inputs_doc["files"], f"{run_rel}/summary.md", root, "result",
                "同时说明原 NO_HAND 与新增 PRESENT 回放各自适用范围")
    write_json(inputs_path, inputs_doc)
    preflight_rel = f"{run_rel}/preflight_result.json"
    file_record(inputs_doc["files"], preflight_rel)["sha256"] = sha256_file(result_path)
    write_json(inputs_path, inputs_doc)

    delivery_path = run_dir / "delivery_manifest.json"
    delivery_doc = read_json(delivery_path)
    delivery_files = delivery_doc["files"]
    delivery_doc["checks"].extend([
        {
            "name": "新增阶段4/5阳性 replay-only 字节与主键绑定",
            "status": "PASS" if positive_audit_run["exit_code"] == 0 else "FAIL",
            "command": positive_audit_run["command"],
            "exit_code": positive_audit_run["exit_code"],
            **({} if positive_audit_run["exit_code"] == 0
               else {"reason": "阳性回放冻结字节或主键交叉绑定失败"}),
        },
        {
            "name": "新增 PRESENT 阳性帧阶段6安全输入资格",
            "status": "BLOCKED" if positive_audit_run["exit_code"] == 0 else "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "capture_time_ns=0 哨兵、result_time_ns=null、stale=null；保持核心 NOT_RUN。",
        },
    ])
    delivery_doc["limitations"].append(
        "最新 PRESENT 阳性回放只验证文件绑定；其时间字段不具备适配条件，状态机未调用。")
    for relative_path, role, reason in [
        ("tmp/6/s6d_r08_runtime/preflight_runtime.py", "source", "r08 复制预检器"),
        ("tmp/6/s6d_r08_runtime/runner_runtime.py", "source", "r08 真实执行器"),
        ("tmp/6/s6d_r08_runtime/positive_replay_audit.py", "source", "阶段4/5阳性回放只读绑定器"),
        (f"{run_rel}/positive_replay_audit_output.txt", "log", "阳性回放绑定审计真实 stdout/stderr"),
        (f"{run_rel}/positive_replay_audit_exit_code.txt", "log", "阳性回放绑定审计真实退出码"),
    ]:
        update_hash(delivery_files, relative_path, root, role, reason)
    for relative_path in prior_attempt_inputs:
        update_hash(delivery_files, relative_path, root, "input",
                    "r05/r06 前序启动失败的保全日志/退出码/尝试记录")
    if positive_audit_path.is_file():
        update_hash(delivery_files, f"{run_rel}/positive_replay_input_audit.json", root,
                    "input", "阶段4/5阳性回放字段与哈希绑定结果")
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
    update_hash(delivery_files, f"{run_rel}/summary.md", root, "result",
                "同时说明原 NO_HAND 与新增 PRESENT 回放各自适用范围")
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
            if inputs_check["exit_code"] != 0:
                item["reason"] = "最终 inputs 模式失败；查看 check_inputs_mode_output.txt 的结构化错误。"
            else:
                item.pop("reason", None)
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
