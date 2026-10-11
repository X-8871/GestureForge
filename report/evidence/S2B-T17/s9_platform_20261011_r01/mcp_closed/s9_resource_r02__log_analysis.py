#!/usr/bin/env python3
"""只读绑定实际启动与runme日志，区分确证事实和历史未采字段。"""
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[3]
RUNS=ROOT/"tmp/2B/S2B-T17/s9p1/s2b_inference_candidate.runs"
OWNER=ROOT/"tmp/2B/S2B-T17/s9_root_run_20261011_r01/.vivado-ai/vivado_31868414_af802b43.log"
started=time.monotonic()
raw=WORK/"log_raw";assert not raw.exists();raw.mkdir()
sources={"owner_session.log":OWNER}
for run in ("s2b_inference_ps7_0_synth_1","s2b_inference_infer_0_synth_1","s2b_inference_rst_fclk0_0_synth_1","s2b_inference_axi_gp0_lite_0_synth_1","synth_1"):
    sources[run+"_runme.log"]=RUNS/run/"runme.log"
sources["infer_runme.bat"]=RUNS/"s2b_inference_infer_0_synth_1/runme.bat"
sources["infer_rundef.js"]=RUNS/"s2b_inference_infer_0_synth_1/rundef.js"
bindings=[];extracts=[];intervals=[]
pattern=re.compile(r"Start of session at:|Process ID\s*:|Exiting Vivado at|Launching helper|maximum of 1 processes|launch_runs synth_1 -jobs 1|Command: synth_design|Launched .*synth_1|wait_on_runs:|synth_design completed successfully")
for name,path in sources.items():
    assert path.is_file()
    data=path.read_bytes();target=raw/name
    with target.open("xb") as f:f.write(data)
    bindings.append({"source":str(path),"snapshot":str(target),"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)})
    text=data.decode("utf-8")
    entries=[{"line":i+1,"text":line} for i,line in enumerate(text.splitlines()) if pattern.search(line)]
    extracts.append({"file":name,"entries":entries})
    if name.endswith("_runme.log"):
        begin=re.search(r"^# Start of session at: (.+)$",text,re.M)
        end=re.search(r"Exiting Vivado at (.+?)\.\.\.",text)
        pid=re.search(r"^# Process ID\s*: (\d+)",text,re.M)
        assert begin and end and pid
        intervals.append({"file":name,"pid":int(pid[1]),"start":begin[1].strip(),"end":end[1].strip(),"synthesis_completed":bool(re.search("synth_design completed successfully",text))})
    if name=="owner_session.log":
        assert "launch_runs synth_1 -jobs 1" in text
        assert "# Process ID         : 33940" in text
history=json.loads((WORK.parent/"s9_resource_watch_20261011_r01/samples.jsonl").read_text(encoding="utf-8").splitlines()[0])
assert {28052,6940}.issubset({p["pid"] for p in history["processes"]})
child={p["pid"]:p for p in history["processes"] if p["pid"] in (28052,6940)}
zone=datetime.timezone(datetime.timedelta(hours=8))
for p in child.values():p["creation_time_utc8"]=datetime.datetime.fromtimestamp(p["create_time"],zone).isoformat()
report={"status":"STOP_READONLY_RESOURCE_R02","at":time.strftime("%Y-%m-%d %H:%M:%S +08:00",time.localtime()),"bindings":bindings,"log_extracts":extracts,"official_run_intervals":intervals,"r01_observed_children":list(child.values()),"find_initial_native_exit_code":1,"find_initial_reason":"有限枚举父目录时两个无关s7_cheap目录Permission denied；r02精确父/新名称已核验并创建，无旧目录写入。","conclusions":["owner日志实际launch_runs synth_1 -jobs 1，runme PID28052精确对应infer_0综合；infer日志明确maximum of 1 processes并启动spawning children Vivado helper。","r01实际23:23:04同一owned递归树同时含28052、6940，是两进程时间重叠的直接观测；infer runme显示28052从23:21:12至23:24:09，覆盖该样本。","r01未采每个子进程的命令/父PID/工作目录；现在两PID缺失，无法追溯读取这些历史字段。6940具体helper子进程命令及runme归属未测，只能说明同一owned树内的推断，不冒充完整父链证明。","jobs=1不等于仅一个Vivado OS进程；本轮树RSS4,900,474,880B确实超过原4GiB预算，未提高预算或抹除警报。","r02 snapshot显示树RSS1,130,930,176B及可用RAM3,983,429,632B已回落；资源警报与真实综合/设计STA结果分别判断，本任务不作STA判定。"],"elapsed_seconds":time.monotonic()-started}
with (WORK/"analysis_receipt.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
print(json.dumps({"status":report["status"],"intervals":intervals,"analysis_receipt_sha256":hashlib.sha256((WORK/"analysis_receipt.json").read_bytes()).hexdigest(),"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"elapsed_seconds":time.monotonic()-started},ensure_ascii=False))
