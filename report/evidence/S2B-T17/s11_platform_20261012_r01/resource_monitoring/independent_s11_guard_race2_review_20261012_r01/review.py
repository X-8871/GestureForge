"""独立只读二次确认竞态审查；Process及资源读回完全模拟。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import types
import psutil

script_base=Path(__file__).absolute().parent
base=script_base/sys.argv[1] if len(sys.argv)>1 else script_base
if base!=script_base:base.mkdir()
root=Path.cwd().resolve()
new=root/"tmp/2B/S2B-T17/s11_resource_guard_20261012_r02"
old=root/"tmp/2B/S2B-T17/s11_resource_guard_20261012_r01"
sup=root/"tmp/2B/S2B-T17/s11_guard_supervisor_20261012_r02"
old_sup=root/"tmp/2B/S2B-T17/s11_guard_supervisor_20261012_r01"
actual=root/"tmp/2B/S2B-T17/s11_guard_actual_20261012_r01/guard"
started=time.monotonic(); checks=[]; inputs={}; cases=[]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bind(path,role="input"):
    assert path.is_file(),str(path)
    relative=path.relative_to(root).as_posix()
    inputs[relative]={"path":relative,"sha256":sha(path),"role":role}
    return path
def load(path,role="input"):return json.loads(bind(path,role).read_text(encoding="utf-8"))
def check(name,value):
    assert value,name
    checks.append(name)
def write(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")
for path,value in ((new/"guard.py","eca5338aeb738b86dbf77a0ae881c8dec5068b89bb4553719e8deba2423cb700"),(sup/"supervisor.py","bbe74e023603ee686a746b92d7dc5c2cb8066b3554eb5e65176bb1f6af88b9f9"),(new/"tool_receipt.json","a30653e5d91a046838ffef080bbad8bbd4f0907b2790207c2c7598f3960a4634"),(new/"raw_manifest.jsonl","30bfd70dca1236c52645f3365858d8445cc016eaca1db85a79e0962dcb316ada"),(actual/"guard_receipt.json","bdf128df3c4776c3d72b8907b6978a395cf84413ff2684327a929e629f60dcc6")):
    check("精确SHA "+path.name,sha(bind(path,"source" if path.suffix==".py" else "input"))==value)
delivery=load(new/"tool_receipt.json","result")
rows=[json.loads(x) for x in (new/"raw_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
check("75绑定三字段",len(rows)==75 and all(set(x)=={"path","sha256","role"} for x in rows))
check("75原件逐项SHA",all((root/x["path"]).is_file() and sha(root/x["path"])==x["sha256"] for x in rows))
text=bind(new/"guard.py","source").read_text(encoding="utf-8")
old_text=bind(old/"guard.py","source").read_text(encoding="utf-8")
before,changed,after=text.split("    def readback_member(",1)[0],text.split("    def readback_member(",1)[1].split("    def root_terminal(",1)[0],text.split("    def root_terminal(",1)[1]
old_before=old_text.split("    def readback_member(",1)[0];old_changed=old_text.split("    def readback_member(",1)[1].split("    def root_terminal(",1)[0];old_after=old_text.split("    def root_terminal(",1)[1]
check("除readback_member其余全部原字节一致",before==old_before and after==old_after)
check("readback最小仅新增NoSuch确认分支",changed.replace(changed.split("        except psutil.NoSuchProcess as error:\n",1)[1].split("        except (psutil.Error, RuntimeError) as error:",1)[0],"",1).replace("        except psutil.NoSuchProcess as error:\n", "",1)==old_changed)
sup_text=bind(sup/"supervisor.py","source").read_text(encoding="utf-8")
old_sup_text=bind(old_sup/"supervisor.py","source").read_text(encoding="utf-8")
check("supervisor仅path/SHA两个字段",sup_text==old_sup_text.replace("s11_resource_guard_20261012_r01/guard.py","s11_resource_guard_20261012_r02/guard.py").replace(sha(old/"guard.py"),sha(new/"guard.py")))
old_receipt=load(actual/"guard_receipt.json","result")
samples=[json.loads(x) for x in bind(actual/"samples.jsonl","log").read_text(encoding="utf-8").splitlines()]
bind(actual/"events.jsonl","log")
check("旧真实运行150samples仍BLOCKED",old_receipt["status"]=="BLOCKED" and len(samples)==150)
def walk(value):
    if isinstance(value,dict):
        yield value
        for x in value.values():yield from walk(x)
    elif isinstance(value,list):
        for x in value:yield from walk(x)
last=list(walk(samples[-1]))
states={x.get("status") for x in last if x.get("expected",{}).get("pid")==36612}
check("36612同原样本ABSENT及UNKNOWN原件保留",{"ABSENT","UNKNOWN"}<=states and samples[-1]["tree_rss_bytes"] is None)
head=subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True)
(base/"head.stdout.log").write_bytes(head.stdout);(base/"head.stderr.log").write_bytes(head.stderr)
write(base/"head.native.json",{"command":["git","rev-parse","HEAD"],"native_exit_code":head.returncode})
check("固定基线",head.returncode==0 and head.stdout.decode().strip()=="a710ec431474841a81912a6055f861e811a151e3")
spec=importlib.util.spec_from_file_location("independent_guard",new/"guard.py")
guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
real_psutil=psutil
fake_psutil=types.SimpleNamespace(**{name:getattr(psutil,name) for name in dir(psutil) if not name.startswith("__")})
fake_psutil.__version__=psutil.__version__
guard.psutil=fake_psutil
expected={"pid":90000001,"create_time":12.5,"exe":"fixture.exe","cwd":str(base),"cmdline":["fixture.exe"],"ppid":90000002}
class Handle:
    def __init__(self,birth):self.pid=expected["pid"];self.birth=birth
    def create_time(self):
        if isinstance(self.birth,Exception):raise self.birth
        return self.birth
def exercise(name,steps,base_value,status,confirmation=None):
    calls=[];pending=list(steps)
    def factory(pid):
        assert pid==expected["pid"];calls.append(pid)
        item=pending.pop(0)
        if isinstance(item,Exception):raise item
        if isinstance(item,tuple):return Handle(item[1])
        return Handle(item)
    fake_psutil.Process=factory
    def read(_process):
        if isinstance(base_value,Exception):raise base_value
        return dict(base_value)
    guard.base_identity=read
    monitor=guard.Guard({}, {},base)
    result=monitor.readback_member(expected)
    check(name,result["status"]==status and (confirmation is None or result.get("confirmation")==confirmation))
    if status=="ORIGINAL_PID_REUSED":check(name+"新对象不动",result["new_object_untouched"])
    cases.append({"name":name,"result":result,"fresh_process_call_count":len(calls)})
    return result
nsp=lambda:psutil.NoSuchProcess(expected["pid"],msg="独立模拟NoSuch")
denied=lambda:psutil.AccessDenied(expected["pid"],msg="独立模拟AccessDenied")
exercise("初始PID缺失",[nsp()],None,"ABSENT")
exercise("初始birth缺失",[("birth_error",nsp())],None,"ABSENT")
exercise("初始AccessDenied",[denied()],None,"UNKNOWN")
exercise("初次birth不符",[13.5],None,"ORIGINAL_PID_REUSED")
exercise("首次birth成功后确认构造缺失",[12.5,nsp()],nsp(),"ABSENT","FRESH_PID_READBACK_ABSENT")
exercise("首次birth成功后确认birth缺失",[12.5,("birth_error",nsp())],nsp(),"ABSENT","FRESH_PID_READBACK_ABSENT")
exercise("首次birth成功后确认复用",[12.5,14.5],nsp(),"ORIGINAL_PID_REUSED","FRESH_PID_READBACK_REUSED")
exercise("同birth不推断消失",[12.5,12.5],nsp(),"UNKNOWN","FRESH_PID_STILL_SAME_BIRTH")
exercise("确认AccessDenied仍UNKNOWN",[12.5,denied()],nsp(),"UNKNOWN")
exercise("确认birth AccessDenied仍UNKNOWN",[12.5,("birth_error",denied())],nsp(),"UNKNOWN")
exercise("普通base AccessDenied仍UNKNOWN",[12.5],denied(),"UNKNOWN")
exercise("普通base RuntimeError仍UNKNOWN",[12.5],RuntimeError("模拟字段变化"),"UNKNOWN")
exercise("完整六字段一致ALIVE",[12.5],dict(expected,rss_bytes=321,status="running"),"ALIVE")
for key in guard.IDENTITY_KEYS:
    changed=dict(expected);changed[key]=["变化"] if key=="cmdline" else "变化" if key in {"exe","cwd"} else expected[key]+1
    exercise("字段漂移 "+key,[12.5],changed,"IDENTITY_CHANGED")
write(base/"independent_readback_cases.json",cases)

# 运行真实Guard.run控制流，但所有进程、时钟、RAM和磁盘完全mock。
root_identity={"pid":90000002,"create_time":11.0,"exe":"root_fixture.exe","cwd":str(base),"cmdline":["root_fixture.exe"],"ppid":0,"parent":None,"rss_bytes":100,"status":"running"}
enumerations=[0];lookups=[0]
class Leaf:
    pid=expected["pid"]
    def create_time(self):return expected["create_time"]
class Root:
    pid=root_identity["pid"]
    def children(self,recursive=False):
        enumerations[0]+=1
        return [Leaf()] if enumerations[0]==1 else []
def process(pid):
    if pid==root_identity["pid"]:return Root()
    assert pid==expected["pid"]
    lookups[0]+=1
    if lookups[0]==1:return Leaf()
    raise nsp()
fake_psutil.Process=process
fake_psutil.virtual_memory=lambda:types.SimpleNamespace(available=2**30)
fake_psutil.disk_usage=lambda _path:types.SimpleNamespace(free=2**34)
guard.identity=lambda _process:(_ for _ in ()).throw(nsp())
guard.base_identity=lambda _process:(_ for _ in ()).throw(nsp())
clock=[0.0]
guard.time=types.SimpleNamespace(monotonic=lambda:clock[0],sleep=lambda seconds:clock.__setitem__(0,clock[0]+seconds))
plan={"new_run_tree_rss_limit_bytes":6442450944,"new_run_available_ram_stop_bytes":536870912,"minimum_c_disk_free_before_dispatch_bytes":8589934592,"resource_sample_interval_seconds":1}
binding={"source_commit":"a710ec431474841a81912a6055f861e811a151e3","run_id":"independent_mock_race","allowed_run_dirs":[str(base)],"max_seconds":1}
class MockGuard(guard.Guard):
    def validate(self):pass
    def get_root(self):return "MATCH",dict(root_identity)
monitor=MockGuard(plan,binding,base/"mock_monitor")
code=monitor.run()
mock_samples=[json.loads(x) for x in (base/"mock_monitor/samples.jsonl").read_text(encoding="utf-8").splitlines()]
check("collect确认缺失不补RSS",code==3 and len(mock_samples)==2 and mock_samples[0]["tree_rss_bytes"] is None and mock_samples[0]["confirmed_exits"] and not mock_samples[0]["uncertain"])
check("collect下一样本继续实际监控语义",mock_samples[1]["tree_rss_bytes"]==100 and not mock_samples[1]["uncertain"] and not mock_samples[1]["confirmed_exits"] and monitor.sample_peak==100)
check("collect无停止调用",not monitor.events or all(x["kind"] not in {"TERMINATE_SENT","PRE_KILL_VERIFIED"} for x in monitor.events))
write(base/"mock_controlflow_result.json",{"component_return_code":code,"factory_calls":lookups[0],"samples":2,"scope":"所有PID与RSS值为独立mock，非OS真实退出/复用或真实资源达标；Guard.run返回3为观察限时BLOCKED预期"})
rss=real_psutil.Process().memory_info().rss
check("自身轻量RSS≤128MiB",rss<=134217728)
check("候选收尾SHA未变",sha(new/"guard.py")==delivery["sources"]["guard.py"] and sha(sup/"supervisor.py")==delivery["sources"]["supervisor.py"])
write(base/"review_inputs.json",list(inputs.values()))
write(base/"review_result.json",{"status":"PASS","scope":"S11-G-RACE2二次确认最小工具修复及可恢复性；不批准旧运行覆盖/预算、STA、产品或G3","source_commit":"a710ec431474841a81912a6055f861e811a151e3","reviewed_source_hashes":delivery["sources"],"reviewed_manifest_hash":sha(new/"raw_manifest.jsonl"),"reviewer_stop":"STOP_READONLY_RACE2_REVIEW","checks":checks,"findings":[],"elapsed_seconds":time.monotonic()-started,"own_sampled_rss_bytes":rss,"absolute_peak_bytes":None,"independent_readback_cases":len(cases),"mock_controlflow_component_return_code":code,"limitations":["本审查所有进程/竞态为独立mock，不访问4256、36612或任意实际任务PID；自身RSS为实际单点读回而非峰","旧150样本ABSENT+UNKNOWN/BLOCKED/缺测保持原字节，不用新工具追填或改判全程PASS","仅guard二次确认及supervisor固定绑定准备G2；生产ROOT首样本/5秒监督/真实关闭仍需实际执行","阈值、stop_one、verified_chain、root_terminal及fsync完全原字节；不增加停止权限","只核75原件SHA，不复制重复包；未执行Vivado/ROSS/硬件/生产改动/Git写入"]})
print(json.dumps({"status":"PASS","checks":len(checks),"cases":len(cases),"rss_bytes":rss},ensure_ascii=False))
