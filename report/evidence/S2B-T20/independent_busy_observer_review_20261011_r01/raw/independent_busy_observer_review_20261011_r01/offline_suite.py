"""复跑冻结的68项回归；只调整夹具临时目录，不改准入、硬件或运输方法。"""
import json
import os
from pathlib import Path
import sys
import unittest

run = Path(__file__).resolve().parent
sys.path.insert(0, str(run.parents[3]))
from verification import test_s2b_csr_busy_observer as new
from verification import test_s2b_csr_board_acceptance as old

temporary = run / "suite_cases"
temporary.mkdir()
new.TEST_PARENT = old.TEST_PARENT = temporary
os.environ.pop("S2B_BUSY_FIXTURE_OUTPUT", None)
suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(new), unittest.defaultTestLoader.loadTestsFromModule(old)])
result = unittest.TextTestRunner(verbosity=2).run(suite)
record = {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
          "skipped": len(result.skipped), "success": result.wasSuccessful(), "hardware_execution": "NOT_RUN",
          "scope": "原35个busy与33个已有CSR回归，未变更断言；仅隔离临时路径"}
(run / "suite_result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if result.wasSuccessful() and result.testsRun == 68 else 1)
