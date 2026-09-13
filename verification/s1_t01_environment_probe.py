#!/usr/bin/env python3
"""S1-T01 官方 Darknet/CUDA 环境探针，不安装依赖、不下载数据、不启动训练。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _now_iso() -> str:
    """返回东八区当前时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _run_command(command: list[str], timeout_seconds: float = 10.0) -> dict:
    """执行只读环境命令并保留标准输出、标准错误和退出码。"""

    try:
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=timeout_seconds)
        return {
            "command": command,
            "available": True,
            "exit_code": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "passed": completed.returncode == 0,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "available": True,
            "exit_code": None,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": "命令超时",
            "passed": False,
            "timed_out": True,
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


def _sha256(path: Path) -> str:
    """计算可执行文件 SHA-256。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_windows_pe(path: Path) -> bool:
    """检查文件是否具有基本 Windows PE 标识。"""

    try:
        with path.open("rb") as stream:
            header = stream.read(64)
            if len(header) < 64 or header[:2] != b"MZ":
                return False
            pe_offset = struct.unpack_from("<I", header, 0x3C)[0]
            stream.seek(pe_offset)
            return stream.read(4) == b"PE\0\0"
    except (OSError, struct.error):
        return False


def _looks_like_darknet(output: str) -> bool:
    """判断版本或帮助输出是否明确属于 Darknet。"""

    normalized = output.casefold()
    return any(marker in normalized for marker in ("darknet", "yolo", "usage:"))


def _probe_darknet(executable: Path | None, report: dict) -> bool:
    """校验 Darknet 文件格式并执行版本或帮助命令。"""

    if executable is None:
        report["checks"]["darknet"] = "未通过：未提供可执行文件或有效 Darknet 根目录"
        return False
    if not executable.is_file():
        report["checks"]["darknet"] = "未通过：文件不存在"
        return False
    report["darknet_executable"] = str(executable)
    report["darknet_sha256"] = _sha256(executable)
    if not _is_windows_pe(executable):
        report["checks"]["darknet"] = "未通过：不是有效 Windows PE 可执行文件"
        return False
    attempts: list[dict] = []
    for arguments in (("--version",), tuple()):
        result = _run_command([str(executable), *arguments])
        attempts.append(result)
        output = f"{result.get('stdout', '')}\n{result.get('stderr', '')}"
        if result["passed"] and _looks_like_darknet(output):
            report["darknet_version"] = output.strip()
            report["darknet_version_command"] = result["command"]
            report["commands"].extend(attempts)
            report["checks"]["darknet"] = "通过：PE 校验与版本/帮助命令成功"
            return True
    report["commands"].extend(attempts)
    report["checks"]["darknet"] = "未通过：版本/帮助命令未返回可识别 Darknet 输出"
    return False


def _probe_cuda_smoke(executable: Path | None, report: dict) -> bool:
    """执行固定 CUDA 设备冒烟程序并要求明确成功标记。"""

    if executable is None:
        report["checks"]["cuda_device_smoke"] = "未通过：未提供固定 CUDA 设备运算程序"
        return False
    if not executable.is_file():
        report["checks"]["cuda_device_smoke"] = "未通过：设备运算程序不存在"
        return False
    report["cuda_smoke_executable"] = str(executable)
    report["cuda_smoke_sha256"] = _sha256(executable)
    result = _run_command([str(executable)])
    report["commands"].append(result)
    output = f"{result.get('stdout', '')}\n{result.get('stderr', '')}"
    passed = result["passed"] and "S1_T01_CUDA_SMOKE_PASS" in output
    report["checks"]["cuda_device_smoke"] = "通过：固定设备运算返回成功标记" if passed else "未通过：未返回固定成功标记"
    return passed


def probe_environment(darknet_root: Path | None = None, darknet_executable: Path | None = None, cuda_smoke_executable: Path | None = None) -> dict:
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
            "未提供 Darknet 或固定 CUDA 设备运算程序时，框架就绪检查保持失败。",
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
    darknet_ok = _probe_darknet(executable, report)
    cuda_smoke_ok = _probe_cuda_smoke(cuda_smoke_executable, report)

    cuda_ok = report["checks"].get("nvcc", "").startswith("通过")
    gpu_ok = report["checks"].get("nvidia_smi", "").startswith("通过")
    report["status"] = "PASS" if numpy_available and cuda_ok and gpu_ok and darknet_ok and cuda_smoke_ok else "FAIL"
    return report


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""

    parser = argparse.ArgumentParser(description="探测 S1-T01 official-darknet-cuda 环境")
    parser.add_argument("--darknet-root", type=Path, help="已构建 Darknet 根目录，预期包含 darknet.exe")
    parser.add_argument("--darknet-executable", type=Path, help="Darknet 可执行文件的明确路径")
    parser.add_argument("--cuda-smoke-executable", type=Path, help="固定 CUDA 设备冒烟程序，输出必须包含 S1_T01_CUDA_SMOKE_PASS")
    parser.add_argument("--report", type=Path, help="输出 JSON 报告路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    """运行探针并按固定框架是否就绪返回退出码。"""

    args = _build_parser().parse_args(argv)
    report = probe_environment(args.darknet_root, args.darknet_executable, args.cuda_smoke_executable)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
