from __future__ import annotations

import contextlib
import hashlib
import importlib
import json
import os
import platform
import shutil
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RAW_ROOT = ROOT / "raw_runs"
TASKS = [
    {
        "task": "T13",
        "module": "verification.test_s2a_upsample_rtl",
        "report": "report/evidence/S2A-T05/upsample_query_simulation.json",
        "helper": "src/int8_upsample_query.sv",
        "testbench": "sim/tb_s2a_upsample_query.sv",
    },
    {
        "task": "T14",
        "module": "verification.test_s2a_maxpool_geometry_rtl",
        "report": "report/evidence/S2A-T04/maxpool_geometry_simulation.json",
        "helper": "src/int8_maxpool_geometry.sv",
        "testbench": "sim/tb_s2a_maxpool_geometry.sv",
    },
    {
        "task": "T15",
        "module": "verification.test_s2a_route_rtl",
        "report": "report/evidence/S2A-T06/route_query_simulation.json",
        "helper": "src/int8_route_query.sv",
        "testbench": "sim/tb_s2a_route_query.sv",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    RAW_ROOT.mkdir(parents=True, exist_ok=False)
    all_results = []
    overall_status = 0
    for item in TASKS:
        module = importlib.import_module(item["module"])
        original_run_tool = module._run_tool
        log_dir = RAW_ROOT / item["task"]
        log_dir.mkdir(parents=True, exist_ok=False)
        phase_records = []

        def run_tool(tool, arguments, cwd, log_path, deadline):
            started = datetime.now().astimezone().isoformat()
            started_mono = time.monotonic()
            code, output = original_run_tool(tool, arguments, cwd, log_path, deadline)
            saved_log = log_dir / Path(log_path).name
            if Path(log_path).is_file():
                shutil.copyfile(log_path, saved_log)
                log_sha = sha256(saved_log)
                log_bytes = saved_log.stat().st_size
            else:
                log_sha = None
                log_bytes = None
            phase_records.append(
                {
                    "phase": saved_log.stem,
                    "command": [str(tool), *[str(argument) for argument in arguments]],
                    "working_directory": str(cwd),
                    "started_local": started,
                    "duration_seconds": round(time.monotonic() - started_mono, 6),
                    "exit_code": code,
                    "raw_log": str(saved_log.relative_to(ROOT)).replace("\\", "/") if log_sha else None,
                    "raw_log_bytes": log_bytes,
                    "raw_log_sha256": log_sha,
                }
            )
            return code, output

        module._run_tool = run_tool
        console_path = log_dir / "test_console.log"
        with console_path.open("w", encoding="utf-8", newline="\n") as console:
            suite = unittest.defaultTestLoader.loadTestsFromModule(module)
            with contextlib.redirect_stdout(console), contextlib.redirect_stderr(console):
                result = unittest.TextTestRunner(stream=console, verbosity=2).run(suite)
                console.flush()
        report_path = ROOT / item["report"]
        report_bytes = report_path.read_bytes() if report_path.is_file() else b""
        report_value = json.loads(report_bytes.decode("utf-8")) if report_bytes else None
        source_bindings = {
            "model_manifest_sha256": sha256(ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"),
            "helper_sha256": sha256(ROOT / item["helper"]),
            "testbench_sha256": sha256(ROOT / item["testbench"]),
            "runner_sha256": sha256(ROOT / (item["module"].replace(".", "/") + ".py")),
        }
        task_status = 0 if result.wasSuccessful() and report_value and report_value.get("result") == "PASS" else 1
        overall_status = max(overall_status, task_status)
        task_manifest = {
            "task": item["task"],
            "module": item["module"],
            "logical_test_command": f"python -B -m unittest {item['module']} -v",
            "test_exit_code": task_status,
            "report_path": item["report"],
            "report_sha256": hashlib.sha256(report_bytes).hexdigest() if report_bytes else None,
            "report_status": report_value.get("result") if report_value else None,
            "source_bindings": source_bindings,
            "phase_records": phase_records,
            "console_log": str(console_path.relative_to(ROOT)).replace("\\", "/"),
            "console_log_bytes": console_path.stat().st_size,
            "console_log_sha256": sha256(console_path),
        }
        write_json(log_dir / "run_manifest.json", task_manifest)
        all_results.append(task_manifest)
        module._run_tool = original_run_tool

    path_environment = os.environ.get("PATH", "").encode("utf-8")
    manifest = {
        "schema_version": "s2a_helper_vector_raw_runs_v1",
        "status": "PASS" if overall_status == 0 else "FAIL",
        "created_local": datetime.now().astimezone().isoformat(),
        "command": "& 'C:\\Users\\22061\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' -B 'preserve_vivado_logs.py'",
        "working_directory": str(ROOT),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "path_sha256": hashlib.sha256(path_environment).hexdigest(),
        "temp_directory": os.environ.get("TEMP") or os.environ.get("TMP"),
        "vivado_bin": r"D:\Xilinx\2026.1\Vivado\bin",
        "vivado_tool_paths": [
            r"D:\Xilinx\2026.1\Vivado\bin\xvlog.bat",
            r"D:\Xilinx\2026.1\Vivado\bin\xelab.bat",
            r"D:\Xilinx\2026.1\Vivado\bin\xsim.bat",
        ],
        "harness_sha256": sha256(Path(__file__).resolve()),
        "tasks": all_results,
    }
    write_json(RAW_ROOT / "run_manifest.json", manifest)
    return overall_status


if __name__ == "__main__":
    raise SystemExit(main())
