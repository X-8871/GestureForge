"""固定当前测试与源码哈希，所有新增夹具落在审查隔离目录。"""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).absolute().parents[4]
OUT=ROOT/"report/evidence/S2B-T19/csr_map_review_20261013_r02"
sys.path.insert(0,str(ROOT))
from verification import test_s2b_visibility_probe as test_module

files=[ROOT/"vitis/run_s2b_visibility_probe.py",ROOT/"verification/test_s2b_visibility_probe.py"]
hashes={file.relative_to(ROOT).as_posix():hashlib.sha256(file.read_bytes()).hexdigest() for file in files}
assert hashes["vitis/run_s2b_visibility_probe.py"]=="01e7668a5af91a3f110ae92bcdeecdcf4cb56f12d4dd8f2cc3c45ee6d7ed71ab"
assert hashes["verification/test_s2b_visibility_probe.py"]=="086bfbcdb7e6172a4d51b940e49e0eda3ee0daafc0afc71dfdd2c13e002b161c"
original=tempfile.mkdtemp
start=time.monotonic()
with (OUT/"tests.log").open("x",encoding="utf-8") as log:
    with patch.object(tempfile,"mkdtemp",side_effect=lambda **kwargs:original(prefix=kwargs.get("prefix","review_"),dir=Path(__file__).parent)):
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_module))
status={"command":sys.argv,"python":sys.executable,"source_sha256":hashes,"tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"elapsed_seconds":time.monotonic()-start,"native_exit_code":0 if result.wasSuccessful() else 1,"hardware_calls":0,"note":"运行当前全部28方法；仅mock/AST与静态来源核验，不导入SDK或操作设备。"}
(OUT/"tests_result.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(status,ensure_ascii=False))
sys.exit(status["native_exit_code"])
