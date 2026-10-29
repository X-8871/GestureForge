#!/usr/bin/env python3
"""串行运行隔离的 S2C 短仿真，并绑定源码、退出码及功能标记。"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path("D:/Xilinx/2026.1/Vivado/bin")


def digest(path: Path) -> str:
    """按磁盘原始字节计算哈希；未提交源不能冒充提交内容。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    """只接受新运行目录；工具正常退出且终止标记齐备才返回成功。"""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--top", required=True)
    parser.add_argument("--source", action="append", required=True)
    parser.add_argument("--marker", action="append", required=True)
    parser.add_argument("--plusarg", action="append", default=[])
    parser.add_argument("--legacy-vectors", type=Path)
    args = parser.parse_args()
    for value in (args.task, args.run_id, args.top):
        if not value or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in value):
            parser.error("标识符只能包含字母、数字、下划线及连字符")
    evidence = ROOT / "report/evidence" / args.task / args.run_id
    work = ROOT / "tmp/S2C" / args.task / args.run_id
    if evidence.exists() or work.exists():
        parser.error("RunId 已存在，不允许覆盖")
    if any(not marker.strip() for marker in args.marker) or not any("PASS" in marker for marker in args.marker):
        parser.error("需要非空且明确包含 PASS 的终止标记")
    sources = []
    for value in args.source:
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            parser.error("源码必须是仓库内的相对路径")
        resolved = (ROOT / path).resolve(strict=True)
        if not resolved.is_relative_to(ROOT.resolve()) or resolved.suffix != ".sv":
            parser.error("源码必须是仓库内的 SystemVerilog 文件")
        sources.append(resolved)
    rtl_sources = list(sources)
    sources.append(Path(__file__).resolve())
    coverage = None
    vectors = None
    if args.legacy_vectors:
        model_path = args.legacy_vectors.resolve(strict=True)
        helper_path = ROOT / "verification/test_s2b_hp0_word_adapter_rtl.py"
        spec = importlib.util.spec_from_file_location("legacy_vectors", helper_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if digest(model_path) != module.MODEL_SHA:
            parser.error("冻结模型 SHA 不一致")
        vectors, coverage = module.build_vectors(json.loads(model_path.read_text(encoding="utf-8")))
        coverage["model_path"] = str(model_path)
        coverage["model_sha256"] = digest(model_path)
        sources.append(helper_path)
    for path in sources:
        if not path.is_file():
            parser.error(f"源码不存在：{path}")
    if len({path.name for path in sources}) != len(sources):
        parser.error("快照文件重名")
    for name in ("xvlog.bat", "xelab.bat", "xsim.bat"):
        if not (TOOLS / name).is_file():
            parser.error("仿真工具不存在：" + name)
    if any(any(c in value for c in '\"&|<>^%!\r\n') for value in args.plusarg):
        parser.error("plusarg 含不支持的批处理解释字符")
    if any(any(c in str(path) for c in '\"&|<>^%!\r\n') for path in sources + [work, evidence, TOOLS]):
        parser.error("路径含不支持的批处理解释字符")
    # 在实际启动前再核对全机资源，查询失败时不冒险占用重型任务槽。
    query = "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[Text.UTF8Encoding]::new($false); $p=@(Get-CimInstance Win32_Process | Where-Object { @('vivado.exe','xsim.exe','xsimk.exe','xelab.exe','xvlog.exe') -contains $_.Name } | Select-Object ProcessId,Name,CommandLine); $o=Get-CimInstance Win32_OperatingSystem; @{processes=$p;available_bytes=([long]$o.FreePhysicalMemory*1024)} | ConvertTo-Json -Depth 4 -Compress"
    try:
        probe = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", query],
                               capture_output=True, text=True, encoding="utf-8", timeout=30, check=True)
        preflight = json.loads(probe.stdout)
    except (subprocess.SubprocessError, ValueError, OSError) as exc:
        parser.error("进程与内存核验失败，未启动仿真：" + str(exc))
    if preflight["processes"] or preflight["available_bytes"] < 2500000000:
        print(json.dumps({"status": "RESOURCE_BUSY_NOT_STARTED", "preflight": preflight}, ensure_ascii=False))
        return 2
    evidence.mkdir(parents=True)
    work.mkdir(parents=True)
    snapshots = evidence / "source_snapshot"
    snapshots.mkdir()
    items = []
    for path in sources:
        target = snapshots / path.name
        if target.exists():
            raise ValueError("快照文件重名")
        target.write_bytes(path.read_bytes())
        items.append({"path": target.relative_to(ROOT).as_posix(), "sha256": digest(target),
                      "source_path": path.relative_to(ROOT).as_posix(), "role": "source_snapshot"})
    plusargs = list(args.plusarg)
    if vectors is not None:
        target = evidence / "vectors.txt"
        target.write_text(vectors, encoding="utf-8")
        items.append({"path": target.relative_to(ROOT).as_posix(), "sha256": digest(target), "role": "vectors"})
        plusargs += ["VECTORS=" + target.as_posix()]
    report = {"task_id": args.task, "run_id": args.run_id, "hash_basis": "worktree_disk",
              "baseline_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "status": "NOT_RUN", "commands": [], "coverage": coverage, "preflight": preflight,
              "limitations": ["短仿真，不代表整帧等价、综合时序或板级结论。", "峰值内存未采集；源码以运行前磁盘快照绑定。"]}
    snapshot = args.top + "_sim"
    commands = [[str(TOOLS / "xvlog.bat"), "-sv"] + [str(snapshots / p.name) for p in rtl_sources],
                [str(TOOLS / "xelab.bat"), args.top, "-s", snapshot],
                [str(TOOLS / "xsim.bat"), snapshot, "-runall"] + sum((["-testplusarg", v] for v in plusargs), [])]
    functional_pass = False
    for name, command in zip(("xvlog", "xelab", "xsim"), commands):
        # Windows 批处理的 CALL 会再次解析等号；每个参数显式加引号保留完整 plusarg。
        if any(any(c in value for c in '\"&|<>^%!\r\n') for value in command):
            raise ValueError("批处理参数含不支持的命令解释字符")
        command_line = " ".join('"' + value + '"' for value in command)
        log = evidence / (name + "_console.log")
        started = time.monotonic()
        timed_out = False
        launch_error = None
        with log.open("wb") as stream:
            try:
                outcome = subprocess.run(command_line, cwd=work, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
                exit_code = outcome.returncode
            except subprocess.TimeoutExpired:
                exit_code = None
                timed_out = True
            except OSError as exc:
                exit_code = None
                launch_error = str(exc)
        record = {"argv": command, "command_line": command_line, "exit_code": exit_code, "timeout": timed_out,
                  "launch_error": launch_error,
                  "elapsed_seconds": round(time.monotonic() - started, 3),
                  "log_path": log.relative_to(ROOT).as_posix(), "log_sha256": digest(log), "hash_basis": "worktree_disk"}
        report["commands"].append(record)
        content = log.read_text(encoding="utf-8", errors="replace")
        print(f"{name}: exit={exit_code}, seconds={record['elapsed_seconds']}", flush=True)
        if timed_out or exit_code != 0:
            report["status"] = "TOOL_FAILURE_OR_TIMEOUT"
            break
        if name == "xsim":
            record["required_markers"] = {marker: marker in content for marker in args.marker}
            record["failure_markers"] = [v for v in ("Fatal:", "FATAL:", "ERROR:", "ERROR: [XSIM", "Simulation engine failed") if v in content]
            functional_pass = all(record["required_markers"].values()) and not record["failure_markers"]
            report["status"] = "PASS_SHORT_SIMULATION" if functional_pass else "FUNCTIONAL_FAIL_OR_INCONCLUSIVE"
            print(content[-2500:], flush=True)
    result = evidence / "result.json"
    result.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    items.append({"path": result.relative_to(ROOT).as_posix(), "sha256": digest(result), "role": "result"})
    manifest = {"task_id": args.task, "run_id": args.run_id, "hash_basis": "worktree_disk", "items": items,
                "limitations": report["limitations"]}
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if functional_pass else 1


if __name__ == "__main__":
    sys.exit(main())
