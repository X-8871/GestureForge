#!/usr/bin/env python3
"""S1-T01 官方 Darknet/CUDA 环境探针，不安装依赖、不下载数据、不启动训练。"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _now_iso() -> str:
    """返回东八区当前时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _run_command(command: list[str]) -> dict:
    """执行只读环境命令并保留标准输出、标准错误和退出码。"""

    try:
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        return {
            "command": command,
            "available": True,
            "exit_code": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "passed": completed.returncode == 0,
        }
    except OSError as exc:
        return {
            "command": command,
            "available": False,
            "exit_code": None,
            "stdout": "",
            "stderr": str(exc),
            "passed": False,
        }


def probe_environment(darknet_root: Path | None = None, darknet_executable: Path | None = None) -> dict:
    """检查固定的 official-darknet-cuda 路线并返回 JSON 报告。"""

    report = {
        "schema_version": 1,
        "created_at_utc8": _now_iso(),
        "python": {
            "executable": sys.executable,
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "framework": "official-darknet-cuda",
        "cuda_required": True,
        "checks": {},
        "commands": [],
        "status": "FAIL",
        "notes": [
            "本探针不安装依赖、不下载数据、不切换到其他 YOLO 框架、不启动训练。",
            "未提供 Darknet 路径时，框架就绪检查保持失败。",
        ],
    }

    numpy_available = importlib.util.find_spec("numpy") is not None
    report["checks"]["python"] = "通过"
    report["checks"]["numpy"] = "通过" if numpy_available else "未通过"

    for name, command in (
        ("nvidia_smi", ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,driver_version", "--format=csv,noheader,nounits"]),
        ("nvcc", ["nvcc", "--version"]),
        ("cmake", ["cmake", "--version"]),
    ):
        executable = shutil.which(command[0])
        if executable is None:
            report["checks"][name] = "未通过：命令不可用"
            report["commands"].append({"command": command, "available": False, "exit_code": None, "stdout": "", "stderr": "PATH 中未找到命令", "passed": False})
        else:
            result = _run_command(command)
            result["resolved_executable"] = executable
            report["commands"].append(result)
            report["checks"][name] = "通过" if result["passed"] else f"未通过：退出码 {result['exit_code']}"

    executable = darknet_executable
    if executable is None and darknet_root is not None:
        candidates = (darknet_root / "darknet.exe", darknet_root / "darknet")
        executable = next((candidate for candidate in candidates if candidate.is_file()), None)
    if executable is None:
        report["checks"]["darknet"] = "未通过：未提供可执行文件或有效 Darknet 根目录"
    else:
        report["checks"]["darknet"] = "通过：文件存在" if executable.is_file() else "未通过：文件不存在"
        report["darknet_executable"] = str(executable)

    cuda_ok = report["checks"].get("nvcc", "").startswith("通过")
    gpu_ok = report["checks"].get("nvidia_smi", "").startswith("通过")
    darknet_ok = report["checks"].get("darknet", "").startswith("通过")
    report["status"] = "PASS" if numpy_available and cuda_ok and gpu_ok and darknet_ok else "FAIL"
    return report


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""

    parser = argparse.ArgumentParser(description="探测 S1-T01 official-darknet-cuda 环境")
    parser.add_argument("--darknet-root", type=Path, help="已构建 Darknet 根目录，预期包含 darknet.exe")
    parser.add_argument("--darknet-executable", type=Path, help="Darknet 可执行文件的明确路径")
    parser.add_argument("--report", type=Path, help="输出 JSON 报告路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    """运行探针并按固定框架是否就绪返回退出码。"""

    args = _build_parser().parse_args(argv)
    report = probe_environment(args.darknet_root, args.darknet_executable)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
