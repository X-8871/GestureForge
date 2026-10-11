#!/usr/bin/env python3
"""将旧证据声明为上游输入，保存首轮角色失败后闭合r08新清单。"""
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
    """原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
    """新版本只创建，已有版本完整保留。"""
    if path.exists():raise ValueError("禁止覆盖："+str(path))
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
def execute(mode,manifest,label,logdir):
    """通过subprocess直接捕获标准检查器native退出。"""
    command=[sys.executable,"-B","verification/check_stage_delivery.py","--mode",mode,"--manifest",manifest.relative_to(ROOT).as_posix()]
    started=time.monotonic();p=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    outputs={}
    for suffix,data in (("stdout",p.stdout),("stderr",p.stderr)):
        target=logdir/(label+"."+suffix+".log")
        if target.exists():raise ValueError("日志禁止覆盖")
        target.write_bytes(data);outputs[suffix]={"path":target.relative_to(ROOT).as_posix(),"sha256":digest(target)}
    row={"command":command,"native_exit_code":p.returncode,"elapsed_seconds":round(time.monotonic()-started,3),
        "manifest_sha256":digest(manifest),**outputs}
    write(logdir/(label+".native.json"),row);print(json.dumps(row,ensure_ascii=False),flush=True)
    return row

target=EVIDENCE/Path(__file__).name
if target.exists():raise ValueError("补充封包器副本已存在")
target.write_bytes(Path(__file__).read_bytes())
old=json.loads((EVIDENCE/"manifest_base.json").read_text(encoding="utf-8"))
before=[{"path":row["path"],"sha256":row["sha256"]} for row in old["files"]]
changes=[]
for row in old["files"]:
    if row["role"] not in ("source","input"):
        changes.append({"path":row["path"],"sha256":row["sha256"],"original_role":row["role"],"new_role":"input"})
        row["role"]="input"
if before!=[{"path":row["path"],"sha256":row["sha256"]} for row in old["files"]]:raise ValueError("继承路径或哈希被改变")
write(EVIDENCE/"upstream_role_correction.json",{"reason":"r07目录的原产物是本次证据纠正的上游输入；不复制、不改原字节。检查器禁止artifact/log/diagnostic指向其他evidence_dir。",
    "path_sha_bindings_unchanged":True,"source_roles_unchanged":True,"changes":changes,
    "initial_failure":{"evidence_native_exit":2,"inputs_native_exit":2,
        "evidence_log":{"path":"report/evidence/S2B-T17/length_guard_20261011_r08/initial_evidence.stdout.log","sha256":digest(EVIDENCE/"initial_evidence.stdout.log")},
        "interpretation":"仅包装角色范围错误；r01证据口径及源码未变，初始r01 manifest和真实native2保留"}})
build=json.loads((EVIDENCE/"correction_build.native.json").read_text(encoding="utf-8"))
if build["native_exit_code"]!=0:raise ValueError("纠正封包器native不为0")
old["checks"].append({"name":"r08_correction_build","status":"PASS","command":subprocess.list2cmdline(build["command"]),"exit_code":0,
    "reason":"原生子进程直接捕获；r01运行失败事实与未捕获native/null分别记录"})
old["checks"].append({"name":"r08_initial_packaging_role_failure","status":"FAIL",
    "command":subprocess.list2cmdline(json.loads((EVIDENCE/"initial_evidence.native.json").read_text(encoding="utf-8"))["command"]),"exit_code":2,
    "reason":"直接捕获真实2；旧artifact/log/diagnostic的目录范围不符，新清单把它们作为上游输入绑定"})
def manifest(number,extra):
    """继承原路径和SHA；只新增当前小文件及准确checks。"""
    data=json.loads(json.dumps(old));data["checks"].extend(extra)
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file():continue
        data["files"].append({"path":path.relative_to(ROOT).as_posix(),"sha256":digest(path),
            "role":"log" if path.suffix==".log" else "diagnostic" if "correction" in path.name else "artifact"})
    target=EVIDENCE/("delivery_manifest_r"+number+".json");write(target,data);return target
second=manifest("02",[])
initial=[execute(mode,second,"corrected_"+mode,EVIDENCE) for mode in ("evidence","inputs")]
if [row["native_exit_code"] for row in initial]!=[0,2]:raise ValueError("修正版包装结果不符")
extra=[{"name":"r08_corrected_"+mode,"status":"PASS" if row["native_exit_code"]==0 else "FAIL",
    "command":subprocess.list2cmdline(row["command"]),"exit_code":row["native_exit_code"],
    "reason":"evidence0只说明绑定通过；inputs2为未冻结物理候选及其他明确未完成项，非G2/G3"} for mode,row in zip(("evidence","inputs"),initial)]
write(EVIDENCE/"corrected_closure_receipt.json",{"checks":initial,"scope":"退出码口径修复；未重跑r01或业务测试"})
third=manifest("03",extra)
final=[execute(mode,third,"final_"+mode,WORK) for mode in ("evidence","inputs")]
write(WORK/"final_receipt.json",{"checks":final,"final_manifest_sha256":digest(third),"source_freeze_sha256":digest(EVIDENCE/"source_freeze.json")})
if [row["native_exit_code"] for row in final]!=[0,2]:raise ValueError("最终包装结果不符")
freeze=json.loads((EVIDENCE/"source_freeze.json").read_text(encoding="utf-8"))
for path,sha in freeze["source_sha256"].items():
    if digest(ROOT/path)!=sha:raise ValueError("源码漂移")
print(json.dumps({"status":"STOP_CORRECTED_G1_EVIDENCE","manifest":"report/evidence/S2B-T17/length_guard_20261011_r08/delivery_manifest_r03.json",
    "manifest_sha256":digest(third),"source_freeze_sha256":digest(EVIDENCE/"source_freeze.json"),
    "closure_receipt_sha256":digest(EVIDENCE/"corrected_closure_receipt.json"),"final_receipt_sha256":digest(WORK/"final_receipt.json"),
    "source_binding_count":len(freeze["source_sha256"]),"nine_sources_unchanged":True},ensure_ascii=False))
