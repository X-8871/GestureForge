#!/usr/bin/env python3
"""S1-T01 官方 Darknet/CUDA 环境探针，不安装依赖、不下载数据、不启动训练。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import re
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


DEFAULT_IDENTITY_MANIFEST = Path(__file__).resolve().parents[1] / "report" / "evidence" / "S1-T01" / "20260914_sha256_manifest.txt"
IDENTITY_KEYS = {
    "darknet": "identity.darknet_executable_sha256",
    "cuda_smoke": "identity.cuda_smoke_executable_sha256",
}


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


def _load_identity_manifest(path: Path | None, report: dict) -> dict[str, str]:
    """读取提交绑定的可执行文件身份清单；缺失或占位条目一律不信任。"""

    if path is None:
        report["identity_manifest"] = None
        report["identity_manifest_error"] = "未提供提交绑定的身份清单"
        return {}
    report["identity_manifest"] = str(path)
    if not path.is_file():
        report["identity_manifest_error"] = "身份清单不存在"
        return {}
    entries: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        report["identity_manifest_error"] = f"身份清单不可读取: {exc}"
        return {}
    for line in lines:
        fields = line.split()
        if len(fields) != 2 or not fields[0].startswith("identity."):
            continue
        if fields[0] in IDENTITY_KEYS.values():
            entries[fields[0]] = fields[1].casefold()
    invalid = [key for key in IDENTITY_KEYS.values() if not re.fullmatch(r"[0-9a-f]{64}", entries.get(key, ""))]
    if invalid:
        report["identity_manifest_error"] = "身份清单缺少真实可执行文件 SHA-256，或仍为不可用占位值"
        return {}
    report["identity_manifest_error"] = None
    return entries


def _check_trusted_identity(
    executable: Path,
    expected_sha256: str | None,
    report: dict,
    check_name: str,
    hash_report_key: str | None = None,
) -> bool:
    """要求运行时文件摘要与冻结清单完全一致。"""

    actual_sha256 = _sha256(executable)
    report[f"{hash_report_key or check_name}_sha256"] = actual_sha256
    if expected_sha256 is None:
        report["checks"][check_name] = "未通过：没有提交绑定的可执行文件 SHA-256"
        return False
    if actual_sha256.casefold() != expected_sha256.casefold():
        report["checks"][check_name] = "未通过：可执行文件 SHA-256 与提交绑定清单不一致"
        return False
    return True


def _is_windows_pe(path: Path) -> bool:
    """检查文件是否具有可执行的基本 Windows PE 结构。"""

    try:
        with path.open("rb") as stream:
            header = stream.read(64)
            if len(header) < 64 or header[:2] != b"MZ":
                return False
            pe_offset = struct.unpack_from("<I", header, 0x3C)[0]
            stream.seek(0, 2)
            file_size = stream.tell()
            if pe_offset < 64 or pe_offset + 4 + 20 > file_size:
                return False
            stream.seek(pe_offset)
            if stream.read(4) != b"PE\0\0":
                return False
            coff = stream.read(20)
            if len(coff) != 20:
                return False
            machine, sections, _, _, _, optional_size, characteristics = struct.unpack("<HHIIIHH", coff)
            if machine not in {0x014C, 0x8664, 0xAA64} or not 1 <= sections <= 96:
                return False
            if optional_size < 2 or optional_size > 4096:
                return False
            optional = stream.read(optional_size)
            if len(optional) != optional_size or struct.unpack_from("<H", optional, 0)[0] not in {0x010B, 0x020B}:
                return False
            if not characteristics & 0x0002:
                return False
            section_table_end = pe_offset + 4 + 20 + optional_size + sections * 40
            return section_table_end <= file_size
    except (OSError, struct.error):
        return False


def _looks_like_darknet(output: str) -> bool:
    """判断版本或帮助输出是否明确属于 Darknet。"""

    normalized = output.casefold()
    has_name = bool(re.search(r"\bdarknet\b", normalized))
    has_version = bool(re.search(r"\b(?:v(?:ersion)?\s*)?\d+\.\d+(?:\.\d+)?\b", normalized))
    has_usage = bool(re.search(r"\busage:\s*darknet\b", normalized))
    return has_name and (has_version or has_usage)


def _probe_darknet(executable: Path | None, report: dict, expected_sha256: str | None = None) -> bool:
    """校验 Darknet 文件格式并执行版本或帮助命令。"""

    if executable is None:
        report["checks"]["darknet"] = "未通过：未提供可执行文件或有效 Darknet 根目录"
        return False
    if not executable.is_file():
        report["checks"]["darknet"] = "未通过：文件不存在"
        return False
    report["darknet_executable"] = str(executable)
    if not _is_windows_pe(executable):
        report["checks"]["darknet"] = "未通过：不是有效 Windows PE 可执行文件"
        return False
    if not _check_trusted_identity(executable, expected_sha256, report, "darknet"):
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


def _probe_cuda_smoke(executable: Path | None, report: dict, expected_sha256: str | None = None) -> bool:
    """执行固定 CUDA 设备冒烟程序并要求明确成功标记。"""

    if executable is None:
        report["checks"]["cuda_device_smoke"] = "未通过：未提供固定 CUDA 设备运算程序"
        return False
    if not executable.is_file():
        report["checks"]["cuda_device_smoke"] = "未通过：设备运算程序不存在"
        return False
    if not _is_windows_pe(executable):
        report["checks"]["cuda_device_smoke"] = "未通过：不是有效 Windows PE 可执行文件"
        return False
    if not _check_trusted_identity(executable, expected_sha256, report, "cuda_device_smoke", "cuda_smoke"):
        return False
    report["cuda_smoke_executable"] = str(executable)
    result = _run_command([str(executable)])
    report["commands"].append(result)
    output = f"{result.get('stdout', '')}\n{result.get('stderr', '')}"
    passed = result["passed"] and "S1_T01_CUDA_SMOKE_PASS" in output
    report["checks"]["cuda_device_smoke"] = "通过：固定设备运算返回成功标记" if passed else "未通过：未返回固定成功标记"
    return passed


def probe_environment(
    darknet_root: Path | None = None,
    darknet_executable: Path | None = None,
    cuda_smoke_executable: Path | None = None,
    identity_manifest: Path | None = DEFAULT_IDENTITY_MANIFEST,
) -> dict:
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
    identity_entries = _load_identity_manifest(identity_manifest, report)
    darknet_ok = _probe_darknet(executable, report, identity_entries.get(IDENTITY_KEYS["darknet"]))
    cuda_smoke_ok = _probe_cuda_smoke(cuda_smoke_executable, report, identity_entries.get(IDENTITY_KEYS["cuda_smoke"]))

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
    parser.add_argument("--identity-manifest", type=Path, default=DEFAULT_IDENTITY_MANIFEST, help="提交绑定的可执行文件 SHA-256 清单")
    parser.add_argument("--report", type=Path, help="输出 JSON 报告路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    """运行探针并按固定框架是否就绪返回退出码。"""

    args = _build_parser().parse_args(argv)
    report = probe_environment(args.darknet_root, args.darknet_executable, args.cuda_smoke_executable, args.identity_manifest)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
