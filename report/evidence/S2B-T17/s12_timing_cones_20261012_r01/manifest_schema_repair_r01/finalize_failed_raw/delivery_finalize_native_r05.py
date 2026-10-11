"""仅监督一次已批准封存及两个只读包装检查，保留每个实际原生码。"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
SCRIPT=HERE/"delivery_collect_r05.py";OUT=HERE/"delivery_finalize_capture_r05"
MAIN=ROOT/"report/evidence/S2B-T17/s12_timing_cones_20261012_r01"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert SCRIPT.is_file() and sha(SCRIPT)=="3617c3ac23fde1482677c35b150c3d14be2075183319f53d16e48f9dec86e32f"
assert HERE.is_dir() and MAIN.parent.is_dir() and not MAIN.exists() and not OUT.exists()
ast.parse(SCRIPT.read_text(encoding="utf-8"))
original=ROOT/"tmp/2B/S2B-T17/s12_combined_prepare_20261012_r01/production_stop_receipt.json"
expected=json.loads(original.read_text(encoding="utf-8"))["changed_source_sha256"]
expected["verification/test_s2b_conv_validation_rtl.py"]="cdf680a67d7bf08407ee3a3993d62032ff33b1aa468d483600861fa217965c2d"
assert len(expected)==16 and {p:sha(ROOT/p) for p in expected}==expected
OUT.mkdir();runs=[];began=time.monotonic();peak=0
steps=(("finalize",[str(SCRIPT),"--mode","finalize"],0),
       ("evidence",[str(ROOT/"verification/check_stage_delivery.py"),"--mode","evidence","--manifest",str(MAIN/"delivery_manifest.json")],0),
       ("inputs",[str(ROOT/"verification/check_stage_delivery.py"),"--mode","inputs","--manifest",str(MAIN/"delivery_manifest.json")],2))
for name,arguments,wanted in steps:
    command=[sys.executable,"-X","utf8","-B",*arguments];start=time.monotonic();failure=None;local_peak=0;samples=0
    with (OUT/(name+".stdout.log")).open("xb") as out,(OUT/(name+".stderr.log")).open("xb") as err:
        child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err)
        process=psutil.Process(child.pid);identity={"pid":process.pid,"birth":process.create_time(),"exe":process.exe(),"cwd":process.cwd(),"cmdline":process.cmdline()}
        while child.poll() is None:
            try:
                root=psutil.Process(child.pid);assert root.create_time()==identity["birth"]
                rss=sum(p.memory_info().rss for p in [root]+root.children(recursive=True) if p.is_running())
                local_peak=max(local_peak,rss);peak=max(peak,rss);samples+=1
            except psutil.NoSuchProcess:
                if child.poll() is not None:break
            if local_peak>134217728 or time.monotonic()-start>60:
                failure="RSS_LIMIT" if local_peak>134217728 else "LIGHT_TOOL_TIMEOUT"
                subprocess.run(["taskkill","/PID",str(child.pid),"/T","/F"],stdout=err,stderr=err,timeout=30);break
            time.sleep(.02)
        native=child.wait(timeout=30)
    record={"name":name,"command":subprocess.list2cmdline(command),"cwd":str(ROOT),"identity":identity,"native_returncode":native,"expected_returncode":wanted,"seconds":time.monotonic()-start,"sampled_tree_peak_rss_bytes":local_peak,"samples":samples,"failure":failure}
    runs.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
    if failure or native!=wanted:break
post={p:sha(ROOT/p) for p in expected};stable=post==expected
receipt={"status":"FINALIZED_AND_WRAPPERS_EXPECTED" if len(runs)==3 and all(r["native_returncode"]==r["expected_returncode"] and r["failure"] is None for r in runs) and stable else "FAILED_OR_BLOCKED_PARTIAL_PRESERVED","runs":runs,"seconds":time.monotonic()-began,"sampled_tree_peak_rss_bytes":peak,"script_sha256":sha(SCRIPT),"wrapper_sha256":sha(Path(__file__)),"actual16_source_pre":expected,"actual16_source_post":post,"actual16_stable":stable,"source_commit_role":"实际precommit Git baseline；本轮候选RAW未提交，不是Git891 tree。","actual_observed_head":"891f750045ce141a8152c96025da559ff1d3a321","limits":"只轻量一次finalize；128MiB/每命令60秒；20ms采样非连续绝对峰。evidence0只包装检查，inputs2明确候选未冻结；整体G2/STA/G3/G5未执行，子代理不提交。","files":[{"path":str(p),"sha256":sha(p),"role":"log"} for p in sorted(OUT.glob("*.log"))]}
if (MAIN/"delivery_manifest.json").is_file():
    receipt["main_sha256"]={name:sha(MAIN/name) for name in ("delivery_manifest.json","source_freeze.json","g1_summary.json","source_diff.patch")}
with (OUT/"native_receipt.json").open("x",encoding="utf-8",newline="\n") as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write("\n")
print(json.dumps({"status":receipt["status"],"receipt_sha256":sha(OUT/"native_receipt.json"),"main_sha256":receipt.get("main_sha256")},ensure_ascii=False),flush=True)
raise SystemExit(0 if receipt["status"]=="FINALIZED_AND_WRAPPERS_EXPECTED" else 1)
