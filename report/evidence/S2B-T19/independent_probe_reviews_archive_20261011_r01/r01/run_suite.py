"""独立单次离线suite，fixture仅重定向到本隔离目录。"""
from pathlib import Path
import ctypes
import json
import os
import sys
import tempfile
import time
import unittest

OUT=Path(__file__).absolute().parent
ROOT=Path(__file__).absolute().parents[4]
sys.path.insert(0,str(ROOT))
original=tempfile.mkdtemp
def isolated(*args,**kwargs):
    """只替换单元测试fixture的临时父目录。"""
    kwargs["dir"]=str(OUT)
    return original(*args,**kwargs)
tempfile.mkdtemp=isolated
class Result(unittest.TextTestResult):
    """保存实际子例结果。"""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.subcases=[]
    def addSubTest(self,test,subtest,err):
        self.subcases.append({"method":test.id(),"case":str(subtest),"status":"PASS" if err is None else "FAIL"})
        super().addSubTest(test,subtest,err)
start=time.monotonic()
result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromName("verification.test_s2b_visibility_probe"))
data={"status":"PASS" if result.wasSuccessful() else "FAIL","methods":result.testsRun,"subcases":result.subcases,"elapsed_seconds":time.monotonic()-start,"native_exit_code":0 if result.wasSuccessful() else 1,"hardware_execution":"NOT_RUN","xsdb_loaded":"xsdb" in sys.modules,"serial_loaded":"serial" in sys.modules,"peak_process_tree_memory_bytes":None}
assert not data["xsdb_loaded"] and not data["serial_loaded"]
with (OUT/"suite_result.json").open("x",encoding="utf-8",newline="\n") as stream:json.dump(data,stream,ensure_ascii=False,indent=2);stream.write("\n")
raise SystemExit(data["native_exit_code"])
