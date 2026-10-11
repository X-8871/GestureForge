"""封存最小竞态修正与纯自有验证，不访问真实进程或Git。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

w=Path(__file__).resolve().parent
root=w.parents[3]
sup=w.parent/"s11_guard_supervisor_20261012_r02"
old=w.parent/"s11_resource_guard_20261012_r01/guard.py"
old_sup=w.parent/"s11_guard_supervisor_20261012_r01/supervisor.py"
actual=w.parent/"s11_guard_actual_20261012_r01/guard"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding="utf-8"))
assert sha(old)=="9cad1ddf5f1b2d48b99c6d10451756536b25c4abf613f0af8b16e0ffd629f86c"
assert sha(w/"guard.py")=="eca5338aeb738b86dbf77a0ae881c8dec5068b89bb4553719e8deba2423cb700"
a,b=old.read_bytes(),(w/"guard.py").read_bytes()
assert a.split(b"    def readback_member(",1)[0]==b.split(b"    def readback_member(",1)[0]
assert a.split(b"    def root_terminal(",1)[1]==b.split(b"    def root_terminal(",1)[1]
assert (sup/"supervisor.py").read_bytes()==old_sup.read_bytes().replace(b's11_resource_guard_20261012_r01/guard.py',b's11_resource_guard_20261012_r02/guard.py').replace(sha(old).encode(),sha(w/"guard.py").encode())
for p in list(w.glob("*.py"))+list(sup.glob("*.py")):ast.parse(p.read_text(encoding="utf-8"))
with (w/"supervisor_diff.patch").open("x",encoding="utf-8",newline="\n") as f:
    f.write("".join(difflib.unified_diff(old_sup.read_text(encoding="utf-8").splitlines(True),(sup/"supervisor.py").read_text(encoding="utf-8").splitlines(True),fromfile=str(old_sup),tofile=str(sup/"supervisor.py"))))
native=read(w/"selftest.native.json");test=read(w/"selftest_result.json");supnative=read(sup/"native_receipt.json")
assert native["native_exit_code"]==supnative["native_exit_code"]==0
assert len(test["cases"])==16 and len(test["collect_race"])==2 and len(read(sup/"selftest_result.json")["cases"])==8
rawreceipt=read(actual/"guard_receipt.json")
assert sha(actual/"guard_receipt.json")=="bdf128df3c4776c3d72b8907b6978a395cf84413ff2684327a929e629f60dcc6"
assert all(sha(actual/x["path"])==x["sha256"] for x in rawreceipt["files"])
inputs=[old,old_sup,actual/"guard_receipt.json",actual/"samples.jsonl",actual/"events.jsonl"]
receipt={"schema_version":1,"task":"S11-G-RACE2","status":"PASS_G1_SIMULATED_TOOL_ONLY","developer_stop":True,
    "at_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"task_baseline":"a710ec431474841a81912a6055f861e811a151e3",
    "git_read_or_written":False,"sources":{"guard.py":sha(w/"guard.py"),"supervisor.py":sha(sup/"supervisor.py")},
    "source_diff_sha256":sha(w/"source_diff.patch"),"supervisor_diff_sha256":sha(w/"supervisor_diff.patch"),
    "only_readback_member_changed":True,"all_other_guard_bytes_unchanged":True,"supervisor_only_fixed_path_and_sha_changed":True,
    "checks":{"guard_native":native,"supervisor_native":supnative},"readback_case_count":16,"collect_case_count":2,"supervisor_fixture_case_count":8,
    "seed":20261012,"own_test_os_peak_working_set_bytes":test["own_os_peak_working_set_bytes"],"test_budget_bytes":134217728,
    "actual_failure_diagnosis":{"path":str((w/"actual_failure_diagnosis.json").relative_to(root)),"sha256":sha(w/"actual_failure_diagnosis.json")},
    "input_bindings":[{"path":str(p.relative_to(root)).replace("\\","/"),"sha256":sha(p)} for p in inputs],
    "limitations":["等ROOT另安排独立review；工具G1不审批实际运行预算、综合/STA或硬件。","除自有supervisor假guard进程外，Process与读取竞态均内存模拟，不访问实际4256/36612或任何其它窗口对象。","自测内存31,592,448B为自身OS峰，不伪称进程树/整机峰；supervisor另记录自有替身离散树采样峰。","首birth成功后base_identity NoSuch必须独立新Process读回；仅ABSENT或birth变化才确认原对象消失，同birth/确认AccessDenied保留UNKNOWN，身份字段变化仍IDENTITY_CHANGED。","实际旧150样本BLOCKED/缺测原件保持，只绑定其HASH；不补测、不重新分类为预算PASS。","STOP_ONE/verified_chain/root_terminal及所有其它方法/生产阈值原字节不变；新增确认不产生停止权限。","不读写Git/STATE/生产源、不调用ROSS/UART/JTAG/Vivado或重型任务，不复制旧810文件。"],
    "raw_manifest_path":"raw_manifest.jsonl"}
with (w/"tool_receipt.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write("\n")
files=list(w.rglob("*"))+list(sup.rglob("*"))
rows=[{"path":str(p.relative_to(root)).replace("\\","/"),"sha256":sha(p),"role":"source" if p.suffix==".py" else "log" if p.suffix==".log" or p.name=="journal.jsonl" else "diagnostic" if p.suffix==".patch" else "result"} for p in files if p.is_file() and p.name!="raw_manifest.jsonl"]
rows += [{"path":str(p.relative_to(root)).replace("\\","/"),"sha256":sha(p),"role":"input"} for p in inputs]
assert len(rows)==len({r["path"] for r in rows})
with (w/"raw_manifest.jsonl").open("x",encoding="utf-8",newline="\n") as f:
    for r in sorted(rows,key=lambda x:x["path"]):f.write(json.dumps(r,ensure_ascii=False)+"\n")
print(json.dumps({"developer_stop":True,"guard_sha256":sha(w/"guard.py"),"supervisor_sha256":sha(sup/"supervisor.py"),"tool_receipt_sha256":sha(w/"tool_receipt.json"),"raw_manifest_sha256":sha(w/"raw_manifest.jsonl"),"source_diff_sha256":sha(w/"source_diff.patch"),"supervisor_diff_sha256":sha(w/"supervisor_diff.patch"),"bindings":len(rows)},ensure_ascii=False))
