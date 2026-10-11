#!/usr/bin/env python3
"""真实捕获新封包器退出，并顺序闭合新r08清单；不重跑原测试。"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[3]
EVIDENCE=ROOT/"report/evidence/S2B-T17/length_guard_20261011_r08"
def digest(path):
    """实际原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):
    """所有产物只创建一次。"""
    if path.exists():raise ValueError("禁止覆盖："+str(path))
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
def execute(label,command,target):
    """子进程returncode为直接捕获，日志在其完成后创建。"""
    env=os.environ.copy();env.update(PYTHONUTF8="1",PYTHONIOENCODING="utf-8")
    started=time.monotonic();stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    p=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout=target/(label+".stdout.log");stderr=target/(label+".stderr.log")
    for path,data in ((stdout,p.stdout),(stderr,p.stderr)):
        if path.exists():raise ValueError("日志禁止覆盖")
        path.write_bytes(data)
    row={"command":command,"cwd":str(ROOT),"started_utc8":stamp,"native_exit_code":p.returncode,"elapsed_seconds":round(time.monotonic()-started,3),
        "stdout":{"path":stdout.relative_to(ROOT).as_posix(),"sha256":digest(stdout)},"stderr":{"path":stderr.relative_to(ROOT).as_posix(),"sha256":digest(stderr)}}
    write(target/(label+".native.json"),row);print(json.dumps(row,ensure_ascii=False),flush=True)
    return row
for name in ("correct_exit_evidence.py","run_correction_package.py"):
    target=EVIDENCE/name
    if target.exists():raise ValueError("新封包器副本禁止覆盖")
    target.write_bytes((WORK/name).read_bytes())
builder=execute("correction_build",[sys.executable,"-B",str(WORK/"correct_exit_evidence.py")],EVIDENCE)
if builder["native_exit_code"]!=0:raise ValueError("新证据封包器失败")
base=json.loads((EVIDENCE/"manifest_base.json").read_text(encoding="utf-8"))
base["checks"].append({"name":"r08_evidence_correction_builder","status":"PASS","command":subprocess.list2cmdline(builder["command"]),"exit_code":builder["native_exit_code"],"reason":"新封包器原生退出直接捕获；不执行原r01或新RTL仿真。"})
def manifest(number,checks):
    """继承旧条目绑定并列新文件；旧模型及源码不复制。"""
    item=json.loads(json.dumps(base));item["checks"].extend(checks)
    inherited=item["files"]
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file():continue
        role="log" if path.suffix==".log" else "diagnostic" if "correction" in path.name else "artifact"
        inherited.append({"path":path.relative_to(ROOT).as_posix(),"sha256":digest(path),"role":role})
    target=EVIDENCE/("delivery_manifest_r"+number+".json");write(target,item);return target
def checks_for(target,label,logdir):
    """标准检查器只验证包装和候选依赖状态。"""
    rows=[]
    for mode in ("evidence","inputs"):
        command=[sys.executable,"-B","verification/check_stage_delivery.py","--mode",mode,"--manifest",target.relative_to(ROOT).as_posix()]
        rows.append(execute(label+"_"+mode,command,logdir))
    if [r["native_exit_code"] for r in rows]!=[0,2]:raise ValueError("实际包装检查结果不符")
    return rows
first=manifest("01",[]);initial=checks_for(first,"initial",EVIDENCE)
extra=[{"name":"r08_initial_"+mode,"status":"PASS" if row["native_exit_code"]==0 else "FAIL","command":subprocess.list2cmdline(row["command"]),"exit_code":row["native_exit_code"],"reason":"evidence0仅绑定通过；inputs实际2，物理候选未冻结及未完成项仍阻断。"} for mode,row in zip(("evidence","inputs"),initial)]
second=manifest("02",extra);closed=checks_for(second,"closure",EVIDENCE)
write(EVIDENCE/"closure_receipt.json",{"checks":closed,"checked_manifest_sha256":digest(second),"interpretation":"只确认修正包可复核；没有新业务验证或G2/G3声明。"})
final=manifest("03",extra);final_checks=checks_for(final,"final",WORK)
write(WORK/"final_receipt.json",{"checks":final_checks,"final_manifest_sha256":digest(final),"source_freeze_sha256":digest(EVIDENCE/"source_freeze.json")})
print(json.dumps({"status":"STOP_CORRECTED_G1_EVIDENCE","final_manifest":final.relative_to(ROOT).as_posix(),"manifest_sha256":digest(final),
    "source_freeze_sha256":digest(EVIDENCE/"source_freeze.json"),"final_receipt_path":(WORK/"final_receipt.json").relative_to(ROOT).as_posix(),"final_receipt_sha256":digest(WORK/"final_receipt.json")},ensure_ascii=False))
