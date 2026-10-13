"""抽取真实SDK方法的离线审查，不导入SDK或连接设备。"""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).absolute().parents[4]
OUT=ROOT/"report/evidence/S2B-T19/csr_map_review_20261013_r02"
SDK=Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\target.py")
sys.path.insert(0,str(ROOT))
from verification.test_s2b_visibility_probe import CsrDebugMapTests, p

raw=SDK.read_bytes()
tree=ast.parse(raw.decode("utf-8-sig"))
cls=next(row for row in tree.body if isinstance(row,ast.ClassDef) and row.name=="Target")
selected=[row for row in cls.body if isinstance(row,ast.FunctionDef) and row.name in ("loadhw","unloadhw","__clear_memmap")]
methods={}
for row in selected:
    methods[row.name]={"first_line":row.lineno,"last_line":row.end_lineno}
module=ast.fix_missing_locations(ast.Module(body=[ast.ClassDef(name="Target",bases=[],keywords=[],body=selected,decorator_list=[])],type_ignores=[]))
state={"opened":0,"closed":0,"updates":0}
class Design:
    """只计数模拟设计所有权。"""
    def close(self):state["closed"]+=1
design=Design()
def open_design(hw):state["opened"]+=1;return design
env={"argparse":argparse,"os":os,"HwManager":SimpleNamespace(open_hw_design=open_design,current_hw_design=lambda value:None),"check_int":lambda value:int(value),"exec_as_runnable":lambda function,node:SimpleNamespace(getProperties=lambda:{"ParentID":""}),"get_cache_data":lambda *args:None}
exec(compile(module,str(SDK),"exec"),env)
Target=env["Target"]
original_mkdtemp=tempfile.mkdtemp
with patch.object(tempfile,"mkdtemp",side_effect=lambda **kwargs:original_mkdtemp(prefix=kwargs.get("prefix","review_"),dir=Path(__file__).parent)):
    case=CsrDebugMapTests();case.setUp()
case.runtime_patch.stop()
case.directory=OUT/"sdk_fixture_r02"
case.directory.mkdir()
case.log.stream.close()
case.record={"calls":[],"verified_inputs":{"compat_artifacts":{"implemented_xsa":{"path":str(case.binding),"sha256":hashlib.sha256(case.binding.read_bytes()).hexdigest()}}}}
case.log=p.Recorder(case.directory/"calls.jsonl",case.record)
apu=Target();apu.session=case.session;apu._ctx="apu";apu._id=10;apu._name="APU"
apu._Target__get_current_node=lambda:SimpleNamespace()
apu._Target__get_run_ctx=lambda node:None
apu._get_all_children_of_the_node=lambda node:{"cpu0":None,"cpu1":None}
apu._Target__update_mem_map=lambda chan,ctx:state.update(updates=state["updates"]+1)
case.apu=apu;case.controller.targets["apu"]=apu
def select(*,id):case.session._curtarget=apu;return apu
case.session.targets=select
results=[]
def reset():
    case.owner.clear();case.session._designtable.clear();case.session._memmap_ctxs.clear();case.session._memmaptable.clear()
def valid_set(chan,ctx,hw,regs):
    case.session._memmap_ctxs={chan:{ctx:{"infer_S_AXI":{"base":0x43C00000,"high":0x43C0FFFF,"size":0x10000,"type":"REGISTER","flags":3}}}}
    case.session._memmaptable={chan:{ctx:{0x43C00000:[{"Addr":0x43C00000,"Size":0x10000,"Flags":3}]}}}
with patch.object(p,"verify_runtime_sources",return_value={"scope":"INDEPENDENT_AST_ONLY"}):
    apu._Target__set_memmap=valid_set
    case.register();case.clear()
    assert not case.session._designtable and not case.session._memmap_ctxs["owned"]
    results.append({"case":"official_load_unload_success","status":"PASS","closed":state["closed"]})
    reset()
    def fail_set(*args):raise RuntimeError("INDEPENDENT_PRE_MEMMAP_FAILURE")
    apu._Target__set_memmap=fail_set
    try:case.register()
    except RuntimeError as error:assert str(error)=="INDEPENDENT_PRE_MEMMAP_FAILURE"
    else:raise AssertionError("加载异常未返回")
    before=state["closed"]
    try:case.clear()
    except p.VisibilityProbeError as error:
        assert "未清理" in str(error)
        results.append({"case":"official_partial_load_no_memmap","status":"EXPECTED_CLEANUP_FAILURE","error":str(error),"design_retained":bool(case.session._designtable),"close_called":state["closed"]!=before,"cleanup":case.record["debug_memory_map"]["cleanup"]})
    else:raise AssertionError("部分加载被误报清理成功")
case.log.stream.close()
result={"sdk_sha256":hashlib.sha256(raw).hexdigest(),"source_sha256":hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest(),"methods":methods,"results":results,"limitations":["仅抽取官方方法，模拟地址下发与设计解析，无SDK导入、板卡或串口调用。"]}
(OUT/"sdk_cases_result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
