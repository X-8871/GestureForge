"""独立重放离线mock suite，所有临时文件限制在审查目录。"""
from pathlib import Path
import sys
import tempfile
import time
import json
import unittest

folder = Path(__file__).parent
root = folder.parents[3]
sys.path.insert(0, str(root))
tempfile.tempdir = str(folder)

class Result(unittest.TextTestResult):
    """分别记录方法与子场景，避免混淆统计口径。"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = []
    def addSubTest(self, test, subtest, err):
        self.cases.append({"method": test.id(), "subcase": str(subtest), "status": "PASS" if err is None else "FAIL"})
        super().addSubTest(test, subtest, err)

started = time.monotonic()
suite = unittest.defaultTestLoader.loadTestsFromName("verification.test_s2b_visibility_probe")
result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
code = 0 if result.wasSuccessful() else 1
record = {"native_exit_code": code, "methods": result.testsRun, "subcases": result.cases,
          "failures": len(result.failures), "errors": len(result.errors), "elapsed_seconds": time.monotonic()-started,
          "hardware_execution": "NOT_RUN", "xsdb_loaded": "xsdb" in sys.modules, "serial_loaded": "serial" in sys.modules}
with (folder / "offline_suite_result.json").open("x", encoding="utf-8") as output:
    json.dump(record, output, ensure_ascii=False, indent=2)
raise SystemExit(code)
