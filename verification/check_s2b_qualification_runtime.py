"""通过官方 Vitis -s 入口验证资格运行时绑定导入，不执行硬件操作。"""

from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[1]
VITIS_DIR = ROOT / "vitis"
TZ = timezone(timedelta(hours=8))
if str(VITIS_DIR) not in sys.path:
    sys.path.insert(0, str(VITIS_DIR))


def sha256_file(path):
    """计算文件原始字节的 SHA-256。"""
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    """只读加载绑定配置并调用运行时导入探针。"""
    config_path = Path(os.environ["S2B_QUALIFICATION_RUNTIME_CONFIG"])
    result_path = Path(os.environ["S2B_QUALIFICATION_RUNTIME_RESULT"])
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes.decode("utf-8-sig"))
    probe_path = VITIS_DIR / "run_s2b_visibility_probe.py"
    started = time.perf_counter()
    record = {
        "schema_version": 1,
        "status": "BLOCKED",
        "started_at_utc8": datetime.now(TZ).isoformat(),
        "source_commit": os.environ.get("S2B_QUALIFICATION_RUNTIME_SOURCE_COMMIT"),
        "tool": {
            "vitis_environment_version": os.environ.get("XILINX_VITIS_VERSION"),
            "python_executable": sys.executable,
            "python_version": sys.version,
        },
        "inputs": {
            "config_path": str(config_path),
            "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
            "probe_path": str(probe_path),
            "probe_sha256": sha256_file(probe_path),
        },
        "hardware_operations": {
            "xsdb_session_created": False,
            "xsdb_client_created": False,
            "hw_server_started": False,
            "serial_port_opened": False,
            "ps_initialized": False,
            "ddr_loaded": False,
            "target_programmed": False,
        },
    }
    try:
        probe = importlib.import_module("run_s2b_visibility_probe")
        sdk, serial = probe._runtime(config)
        record["runtime_modules"] = {
            "xsdb": {
                "path": str(Path(sdk.__file__).resolve()),
                "sha256": sha256_file(sdk.__file__),
            },
            "serial": {
                "path": str(Path(serial.__file__).resolve()),
                "sha256": sha256_file(serial.__file__),
                "version": serial.__version__,
            },
        }
        record["status"] = "PASS_RUNTIME_IMPORT_HARDWARE_NOT_RUN"
        record["native_script_exit_code"] = 0
        exit_code = 0
    except Exception as error:
        record["error"] = f"{type(error).__name__}: {error}"
        record["traceback"] = traceback.format_exc()
        record["native_script_exit_code"] = 2
        exit_code = 2
    record["elapsed_seconds"] = time.perf_counter() - started
    record["finished_at_utc8"] = datetime.now(TZ).isoformat()
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with result_path.open("x", encoding="utf-8", newline="\n") as result_file:
        result_file.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
