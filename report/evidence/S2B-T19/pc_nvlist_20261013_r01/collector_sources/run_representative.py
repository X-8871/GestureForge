"""保存现场Info及失败锁止的代表性mock逐调用原件，不调用硬件SDK。"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys
import unittest

root = Path.cwd()
sys.path.insert(0, str(root))
from verification.test_s2b_board_jtag import JtagTests

evidence = root / "report/evidence/S2B-T19/pc_nvlist_20261013_r01/representative_r06"
evidence.mkdir(exist_ok=False)
cache = root / "tmp/2B/S2B-T19/pc_nvlist_20261013_r01"
os.environ.update(TEMP=str(cache), TMP=str(cache))
records = []

class EvidenceTests(JtagTests):
    """在测试清理临时夹具之前保存全部输入与逐调用日志字节。"""
    def tearDown(self):
        self.controller.close()
        destination = evidence / f"fixture_{len(records):02d}"
        destination.mkdir(exist_ok=False)
        mapping = []
        for source in self.directory.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(self.directory)
            copied = destination / relative
            copied.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, copied)
            raw = source.read_bytes()
            if copied.read_bytes() != raw:
                raise AssertionError("mock证据副本不一致")
            mapping.append({"original_path": str(source), "copied_path": str(copied),
                            "sha256": hashlib.sha256(raw).hexdigest()})
        records.append({"test": self._testMethodName, "hardware_execution": "MOCK_ONLY",
                        "mapping": mapping})
        super().tearDown()

names = ["test_pc_nvlist_preserves_actual_async_info_and_raw_stderr",
         "test_pc_nvlist_invalid_structure_locks_and_cleans_owned_breakpoints",
         "test_pc_nvlist_sdk_exception_keeps_raw_output_locks_and_cleans"]
suite = unittest.TestSuite(EvidenceTests(name) for name in names)
with (evidence / "unittest.stderr.log").open("x", encoding="utf-8", newline="\n") as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
(evidence / "fixture_mapping.json").write_text(json.dumps({"actual_hardware_calls": 0,
    "test_methods": result.testsRun, "success": result.wasSuccessful(), "fixtures": records},
    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"methods": result.testsRun, "fixture_count": len(records), "success": result.wasSuccessful()}))
sys.exit(0 if result.wasSuccessful() else 1)
