"""仅模拟Process与字段读取；不访问任何实际目标PID或Vivado会话。"""
import ctypes
from ctypes import wintypes
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import guard as new

w = Path(__file__).resolve().parent
oldpath = w.parent / "s11_resource_guard_20261012_r01/guard.py"
spec = importlib.util.spec_from_file_location("race_old_guard",oldpath)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(oldpath)=="9cad1ddf5f1b2d48b99c6d10451756536b25c4abf613f0af8b16e0ffd629f86c"
before, after = oldpath.read_bytes(), (w/"guard.py").read_bytes()
prefix=lambda b:b.split(b"    def readback_member(",1)[0]
suffix=lambda b:b.split(b"    def root_terminal(",1)[1]
assert prefix(before)==prefix(after) and suffix(before)==suffix(after)
patch="".join(difflib.unified_diff(before.decode("utf-8").splitlines(True),after.decode("utf-8").splitlines(True),fromfile=str(oldpath),tofile=str(w/"guard.py")))
(w/"source_diff.patch").write_text(patch,encoding="utf-8",newline="\n")
expected={"pid":700001,"create_time":17.0,"exe":"模拟.exe","cwd":str(w),"cmdline":["模拟"],"ppid":700000}
actual=dict(expected,rss_bytes=8,status="running")
rows=[]
original_process=new.psutil.Process
original_base_new,original_base_old=new.base_identity,old.base_identity
original_identity_new,original_identity_old=new.identity,old.identity

class FakeProcess:
    def __init__(self,pid,birth=17.0):self.pid,self.birth=pid,birth
    def create_time(self):return self.birth

def one(label,base_mode,confirmation,wanted,module=new,initial_birth=17.0,mutated_field=None,minimal=False):
    calls=[]
    def process(pid):
        assert pid==700001
        calls.append(pid)
        if len(calls)==1:return FakeProcess(pid,initial_birth)
        if confirmation=="absent":raise new.psutil.NoSuchProcess(pid,msg="模拟独立新PID读回缺失")
        if confirmation=="denied":raise new.psutil.AccessDenied(pid)
        return FakeProcess(pid,18.0 if confirmation=="reused" else 17.0)
    def base(process):
        if base_mode=="nosuch":raise new.psutil.NoSuchProcess(process.pid,msg="模拟birth成功后字段读取期间退出")
        if base_mode=="denied":raise new.psutil.AccessDenied(process.pid)
        if base_mode=="runtime":raise RuntimeError("模拟身份不稳定")
        value=dict(actual)
        if mutated_field:value[mutated_field]=["漂移"] if mutated_field=="cmdline" else -1 if mutated_field in {"pid","ppid","create_time"} else "漂移"
        return value
    new.psutil.Process=process
    module.base_identity=base
    try:
        result=module.Guard.readback_member(None,{"pid":700001} if minimal else expected)
        assert result["status"]==wanted,(label,result)
        if wanted=="ORIGINAL_PID_REUSED":assert result["new_object_untouched"] is True
        if base_mode in {"denied","runtime"}:assert len(calls)==1
        rows.append({"case":label,"result":result,"simulated_process_ctor_calls":len(calls),"pass":True})
    finally:
        new.psutil.Process=original_process
        new.base_identity=original_base_new
        old.base_identity=original_base_old

one("old_birth_then_exit_reproduces_unknown","nosuch","absent","UNKNOWN",old)
one("fresh_readback_confirms_absent","nosuch","absent","ABSENT")
one("fresh_readback_confirms_reused","nosuch","reused","ORIGINAL_PID_REUSED")
one("fresh_readback_same_birth_stays_unknown","nosuch","same","UNKNOWN")
one("fresh_readback_denied_stays_unknown","nosuch","denied","UNKNOWN")
one("initial_access_denied_stays_unknown","denied","absent","UNKNOWN")
one("runtime_identity_instability_stays_unknown","runtime","absent","UNKNOWN")
one("initial_birth_reused_no_field_reads","ok","same","ORIGINAL_PID_REUSED",initial_birth=18.0)
one("normal_full_identity_alive","ok","same","ALIVE")
one("minimal_expected_uses_first_observed_birth","nosuch","reused","ORIGINAL_PID_REUSED",minimal=True)
for field in new.IDENTITY_KEYS:one("field_drift_"+field,"ok","same","IDENTITY_CHANGED",mutated_field=field)

def collect_race(module):
    count=[0]; enumerate_count=[0]; events=[]
    leaf=FakeProcess(700001)
    class RootProcess(FakeProcess):
        def children(self,recursive=False):
            enumerate_count[0]+=1
            return [leaf] if enumerate_count[0]==1 else []
    def process(pid):
        if pid==700000:return RootProcess(pid,11.0)
        assert pid==700001
        count[0]+=1
        if count[0]==1:return leaf
        raise new.psutil.NoSuchProcess(pid,msg="模拟第二次及后续候选确已缺失")
    def nosuch(process):raise new.psutil.NoSuchProcess(process.pid,msg="模拟读取竞态")
    root=dict(actual,pid=700000,create_time=11.0,ppid=0)
    monitor=module.Guard.__new__(module.Guard)
    monitor.binding={"allowed_run_dirs":[str(w)]}
    monitor.last_members={(700001,17.0):dict(actual)}
    monitor.known_lineage={};monitor.retired_members=set();monitor.confirmed_sample_exits=[];monitor.sample_count=0
    monitor.event=lambda kind,**values:events.append({"kind":kind,**values})
    new.psutil.Process=process;module.base_identity=nosuch;module.identity=nosuch
    try:
        members,uncertain,exited=monitor.collect(root)
        if module is old:
            assert len(uncertain)==1 and len(exited)==1
        else:
            assert not uncertain and len(exited)==1
            later=monitor.collect(root)
            assert not later[1] and not later[2] and len(later[0])==1
        return {"old_version":module is old,"uncertain":uncertain,"confirmed_exits":exited,"events":events,"simulated_scope":True}
    finally:
        new.psutil.Process=original_process
        new.base_identity=original_base_new;old.base_identity=original_base_old
        new.identity=original_identity_new;old.identity=original_identity_old

integration=[collect_race(old),collect_race(new)]
actual_dir=w.parent/"s11_guard_actual_20261012_r01/guard"
receipt=json.loads((actual_dir/"guard_receipt.json").read_text(encoding="utf-8"))
terminal=json.loads((actual_dir/"samples.jsonl").read_text(encoding="utf-8").splitlines()[-1])
assert receipt["status"]=="BLOCKED" and receipt["samples"]==150 and not terminal["alerts"]
assert any(x["pid"]==36612 and x["reason"]=="KNOWN_MEMBER_READBACK_UNKNOWN" for x in terminal["uncertain"])
assert any(x["expected"]["pid"]==36612 and x["status"]=="ABSENT" for x in terminal["confirmed_exits"])
diagnosis={"receipt_status":receipt["status"],"receipt_reason":receipt["reason"],"terminal_sample_index":terminal["index"],
    "at_utc8":terminal["at_utc8"],"same_sample_known_pid":36612,"same_sample_unknown_and_absent":True,
    "budget_alerts":terminal["alerts"],"tree_rss_bytes":terminal["tree_rss_bytes"],"original_failure_not_reclassified":True,
    "raw_inputs":[{"path":str(actual_dir/name),"sha256":sha(actual_dir/name)} for name in ("guard_receipt.json","samples.jsonl","events.jsonl")]}
(w/"actual_failure_diagnosis.json").write_text(json.dumps(diagnosis,ensure_ascii=False,indent=2),encoding="utf-8")

class Counters(ctypes.Structure):
    _fields_=[("cb",wintypes.DWORD),("PageFaultCount",wintypes.DWORD)]+[(x,ctypes.c_size_t) for x in ("PeakWorkingSetSize","WorkingSetSize","QuotaPeakPagedPoolUsage","QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage","QuotaNonPagedPoolUsage","PagefileUsage","PeakPagefileUsage")]
kernel=ctypes.WinDLL("kernel32",use_last_error=True);api=ctypes.WinDLL("psapi",use_last_error=True)
kernel.GetCurrentProcess.restype=wintypes.HANDLE
api.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
mem=Counters();mem.cb=ctypes.sizeof(mem)
assert api.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(mem),mem.cb)
assert mem.PeakWorkingSetSize<=128*1024*1024
result={"status":"PASS_SIMULATED_G1_ONLY","cases":rows,"collect_race":integration,"seed":20261012,
    "own_os_peak_working_set_bytes":mem.PeakWorkingSetSize,"guard_sha256":sha(w/"guard.py"),"outside_readback_member_raw_unchanged":True,
    "actual_targets_accessed_or_stopped":False,"heavy_ross_hardware_executed":False,
    "limitations":["Process/字段读取全为内存模拟，700000/700001没有真实OS查询；内存只读自身GetCurrentProcess。","新旧collect对照复现同样本UNKNOWN与ABSENT冲突，新版确认缺失后下一轮不重复缺测；未运行真实guard绑定。","只修复readback_member出生时间成功后的NoSuch路径，其它方法与预算原字节不变。","实际S11旧BLOCKED/缺测原件只绑定，不补预算PASS或继承STA批准。"]}
(w/"selftest_result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"status":result["status"],"readback_cases":len(rows),"collect_cases":len(integration),"own_os_peak_working_set_bytes":mem.PeakWorkingSetSize,"guard_sha256":result["guard_sha256"]},ensure_ascii=False))
