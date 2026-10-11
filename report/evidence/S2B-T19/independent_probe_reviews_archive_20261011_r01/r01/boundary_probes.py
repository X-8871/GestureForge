"""独立边界与SDK连接逻辑AST模拟；不导入真实xsdb/serial或创建会话。"""
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import json
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

OUT=Path(__file__).absolute().parent
ROOT=Path(__file__).absolute().parents[4]
sys.path.insert(0,str(ROOT))
from verification import test_s2b_visibility_probe as tests
from verification import check_stage_delivery as delivery
p=tests.p
original=tempfile.mkdtemp
def isolated(*args,**kwargs):
    """边界fixture仅写本目录。"""
    kwargs["dir"]=str(OUT);return original(*args,**kwargs)
tempfile.mkdtemp=isolated
checks=[]

sdk_session=Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\session.py")
source=sdk_session.read_text(encoding="utf-8")
tree=ast.parse(source)
sdk_class=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=="Session")
connect=next(node for node in sdk_class.body if isinstance(node,ast.FunctionDef) and node.name=="connect")
connect.decorator_list=[]
# 仅复用官方connect方法；初始化、TCF与launch全部是阻止外部行为的mock。
mock_class=ast.parse('class Session:\n def __init__(self):\n  self.__channel_map={}\n  self.launches=[]\n def __launch_server(self,server,url):\n  self.launches.append((server,url))\n  raise RuntimeError("MOCK_AUTOSTART_REACHED")\n').body[0]
mock_class.body.append(connect)
module=ast.fix_missing_locations(ast.Module(body=[mock_class],type_ignores=[]))
scope={"argparse":argparse,"check_int":int,"tcf":SimpleNamespace(connect=lambda url:(_ for _ in ()).throw(RuntimeError("MOCK_ROOT_SERVER_DISAPPEARED")))}
exec(compile(module,str(sdk_session),"exec"),scope)
for host in ("127.0.0.1","localhost"):
    session=scope["Session"]()
    try:session.connect(host=host,port=3121,server="hw_server")
    except Exception as error:
        checks.append({"name":"官方connect连接失败分支AST_MOCK","host":host,"error":repr(error),"launches":session.launches,"sdk_source":tests.bind(sdk_session)})
    else:raise AssertionError("连接失败竟成功")
assert checks[0]["launches"]==[("hw_server","TCP:127.0.0.1:3121")]
assert not checks[1]["launches"]

fixture=tests.PreflightTests();fixture.setUp()
try:
    duplicate=fixture.directory/"duplicate_status_compat.json"
    raw=json.dumps(fixture.receipt).replace('"status": "PASS"','"status": "FAIL", "status": "PASS"',1)
    duplicate.write_text(raw,encoding="utf-8")
    fixture.cfg["compat_review"]=tests.bind(duplicate)
    fixture.check()
    checks.append({"name":"重复compat状态键被消费为PASS","status":"CONFIRMED_BLOCKER","receipt":tests.bind(duplicate),"runtime_called":False})
    fixture.cfg["compat_review"]=tests.bind(fixture.receipt_path)
    fixture.cfg["schema_version"]=True
    fixture.check()
    checks.append({"name":"bool schema_version被视为整数1","status":"ACCEPTED","runtime_called":False})
finally:fixture.tearDown()

fixture=tests.PreflightTests();fixture.setUp()
try:
    sdk_init=p.SDK_INIT
    clone=fixture.directory/"sdk_source_fixture";clone.mkdir()
    for name in ("__init__.py","target.py","xsdb_debug_session.py","session.py"):
        (clone/name).write_bytes((sdk_init.parent/name).read_bytes())
    fixture.cfg["bindings"]["sdk_init"]=tests.bind(clone/"__init__.py")
    fixture.cfg["bindings"]["sdk_target"]=tests.bind(clone/"target.py")
    before=tests.bind(clone/"session.py")
    with patch.object(p,"SDK_INIT",clone/"__init__.py"):
        fixture.check()
        (clone/"session.py").write_bytes((clone/"session.py").read_bytes()+"\n# SDK会话漂移，仅测试fixture\n".encode("utf-8"))
        fixture.check()
    after=tests.bind(clone/"session.py")
    assert before["sha256"]!=after["sha256"]
    checks.append({"name":"SDK未声明session实现漂移不触发门禁","status":"CONFIRMED_CLOSURE_GAP","before":before,"after":after,"sdk_init_target_bound":True,"runtime_called":False})
finally:fixture.tearDown()

fixture=tests.LifecycleTests();fixture.setUp()
try:
    fixture.session.objects[12].state=lambda:"UNKNOWN_INDEPENDENT"
    path=fixture.directory/"unknown_state_config.json";tests.write(path,fixture.config)
    with patch.object(p,"ROOT",fixture.directory),patch.object(p,"_preflight",return_value=(tests.j,tests.j.transport,fixture.build,fixture.expected)),patch.object(p,"_runtime",side_effect=fixture.runtime),patch.object(p,"_identity_snapshot",return_value=fixture.actual):
        try:p.run(path)
        except p.VisibilityProbeError:pass
        else:raise AssertionError("未知CPU状态未拒绝")
    assert not any(op[0]=="stop" for op in fixture.session.operations)
    checks.append({"name":"CPU1未知状态在双核确认前拒绝","status":"PASS_NO_STOP","result":tests.bind(Path(fixture.config["run_dir"])/"visibility_probe_result.json")})
finally:pass

fixture=tests.LifecycleTests();fixture.setUp()
def close_and_raise(port):
    """故障注入仅关闭mock资源再抛清理异常。"""
    port.is_open=False;raise RuntimeError("INDEPENDENT_SERIAL_CLEANUP_FAILURE")
with patch.object(tests.Port,"close",close_and_raise):
    result=fixture.execute("cache")
assert result["native_exit_code"]==2 and "CRC" in result["error"]
assert any("INDEPENDENT_SERIAL_CLEANUP_FAILURE" in row["error"] for row in result["cleanup_errors"])
assert not fixture.session.objects[11].running and not fixture.ports[0].is_open
checks.append({"name":"cache原失败+serial清理失败保留primary","status":"PASS","primary":result["error"],"cleanup":result["cleanup_errors"],"result":tests.bind(Path(fixture.config["run_dir"])/"visibility_probe_result.json")})

manifest=ROOT/"report/evidence/S2B-T19/offline_probe_entry_20261011_r01/delivery_manifest_r03.json"
checks.append({"name":"包装evidence","result":delivery.check_manifest("evidence",str(manifest),str(ROOT))})
assert "xsdb" not in sys.modules and "serial" not in sys.modules
record={"schema_version":1,"status":"CHANGES_REQUIRED","hardware_execution":"NOT_RUN","checks":checks,
    "source_bindings":[tests.bind(ROOT/"vitis/run_s2b_visibility_probe.py"),tests.bind(ROOT/"verification/test_s2b_visibility_probe.py")],
    "sdk_readonly_dependencies":[tests.bind(p.SDK_INIT.parent/name) for name in ("__init__.py","target.py","xsdb_debug_session.py","session.py")],
    "limitations":["compat与runtime均为明确mock fixture，不能证明实际独审/冷恢复/位流批准。","AST仅模拟官方connect失败分支，TCF与launch均不执行真实行为。"]}
with (OUT/"boundary_result.json").open("x",encoding="utf-8",newline="\n") as stream:json.dump(record,stream,ensure_ascii=False,indent=2);stream.write("\n")
print(json.dumps({"status":record["status"],"checks":len(checks)},ensure_ascii=False))
