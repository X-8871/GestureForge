"""独立离线suite重放，强制既有fixture写入本审查目录。"""
from pathlib import Path
import sys
import tempfile
import time
import json
import unittest
from unittest.mock import patch

folder = Path(__file__).parent
root = folder.parents[3]
sys.path.insert(0, str(root))
original = tempfile.mkdtemp
def isolated(*args, **kwargs):
    """覆盖调用显式指定的dir，避免写出审查边界。"""
    kwargs["dir"] = folder
    return original(*args, **kwargs)
class Result(unittest.TextTestResult):
    """分开统计方法与子场景。"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = []
    def addSubTest(self, test, subtest, err):
        self.cases.append({"method": test.id(), "case": str(subtest), "status": "PASS" if err is None else "FAIL"})
        super().addSubTest(test, subtest, err)
started = time.monotonic()
with patch.object(tempfile, "mkdtemp", side_effect=isolated):
    suite = unittest.defaultTestLoader.loadTestsFromName("verification.test_s2b_visibility_probe")
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
code = 0 if result.wasSuccessful() else 1
record = {"native_exit_code": code, "methods": result.testsRun, "subcases": result.cases,
          "failures": len(result.failures), "errors": len(result.errors), "elapsed_seconds": time.monotonic()-started,
          "hardware_execution": "NOT_RUN", "xsdb_loaded": "xsdb" in sys.modules, "serial_loaded": "serial" in sys.modules}
with (folder/"offline_suite_result.json").open("x", encoding="utf-8") as output:
    json.dump(record, output, ensure_ascii=False, indent=2)
raise SystemExit(code)
