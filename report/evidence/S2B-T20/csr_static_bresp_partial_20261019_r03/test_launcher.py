"""在官方Vitis入口运行CSR静止矩阵BRESP部分证据离线回归。"""
import contextlib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT = Path(r"D:\FPGA_Competition\w2b")
RUN = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
modules = (
    "verification.test_s2b_model_acceptance_runner",
    "verification.test_s2b_csr_board_acceptance",
    "verification.test_s2b_csr_busy_observer",
    "verification.test_s2b_csr_deadline_flow",
    "verification.test_s2b_csr_acceptance_flow",
)
sources = (
    "vitis/run_s2b_model_acceptance.py",
    "verification/s2b_csr_board_acceptance.py",
    "verification/s2b_csr_busy_observer.py",
    "verification/s2b_csr_deadline_flow.py",
    "verification/s2b_csr_acceptance_flow.py",
    *(module.replace(".", "/") + ".py" for module in modules),
)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
bindings = {relative: sha(ROOT / relative) for relative in sources}
started = time.monotonic()
with (RUN / "unittest.log").open("x", encoding="utf-8", newline="\n") as stream:
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(module) for module in modules)
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
native = 0 if result.wasSuccessful() else 1
record = {"schema_version": 1, "status": "PASS" if native == 0 else "FAIL",
          "scope": "OFFLINE_CSR_STATIC_BRESP_PARTIAL_REGRESSION_ONLY", "source_commit": baseline,
          "source_sha256": bindings, "tool": "Vitis 2026.1", "python": sys.version,
          "command": r"D:\Xilinx\2026.1\Vitis\bin\vitis.bat -s " + str(Path(__file__).resolve()),
          "tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
          "skipped": len(result.skipped), "native_exit_code": native,
          "elapsed_seconds": time.monotonic() - started,
          "log_sha256": sha(RUN / "unittest.log"),
          "limitations": ["本运行未接触硬件、JTAG、XSDB或串口，不代表CSR实板或阶段2B验收通过。",
                          "只验证限定AHB AP签名的BRESP未解析部分路径及原有离线回归。"]}
with (RUN / "regression_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({key: record[key] for key in ("status", "tests", "native_exit_code", "elapsed_seconds")}, ensure_ascii=False))
raise SystemExit(native)
