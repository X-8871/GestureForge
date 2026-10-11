"""ROOT逐项准入后仅启动一个既有回归；原生码、来源及资源独立保存。"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import psutil

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
TASKS={
 "feature":("test_s2b_conv_feature_address_rtl.py","0402e00ca5c5bc9e40f2aeb46b1051c01ba9664c3773b45f1a631c4d5ecf36a1","s12_conv_feature_20261012_r",90),
 "output":("test_s2b_conv_output_address_rtl.py","e51f66c2382ae3308c2fdb864e468d8684dc107076d9e75dd7d38625a6326b74","s12_conv_output_20261012_r",90),
 "backend":("test_s2b_backend_coordinates_rtl.py","318f5812dbe37693725c691fbd87ea31862969b41979681c0b8a77156d78fdda","s12_backend_timing_20261012_r",240),
 "route":("test_s2b_route_specialization_rtl.py","4e46cdcc110502acc4b47c9500dca09b42199bae48a6cad944068ad1b1e55f6a","s12_route_generic_20261012_r",60),
}
parser=argparse.ArgumentParser();parser.add_argument("--task",choices=TASKS,required=True);parser.add_argument("--run-id",required=True);parser.add_argument("--admission",type=Path,required=True);args=parser.parse_args()
name,expected,prefix,estimate=TASKS[args.task];assert re.fullmatch(re.escape(prefix)+r"\d+",args.run_id)
runner=(ROOT/"verification"/name).resolve(strict=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert runner.is_file() and sha(runner)==expected
admission=args.admission.resolve(strict=True);assert admission.is_file() and admission.parent==ROOT/"tmp/2B/S2B-T17/s12_root_run_20261012_r01"
assert subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","rev-parse","HEAD"],cwd=ROOT,text=True).strip()=="891f750045ce141a8152c96025da559ff1d3a321"
base=ROOT/"tmp/2B/S2B-T17";assert base.is_dir() and not base.is_symlink()
if args.task in ("feature","output"):
    base=base/"s12_timing_cones_20261012_r01"
    if not base.exists():base.mkdir()
    assert base.is_dir() and not base.is_symlink()
work=base/args.run_id;evidence=ROOT/"report/evidence/S2B-T17"/args.run_id;capture=HERE/(args.run_id+"_capture")
assert evidence.parent.is_dir() and not work.exists() and not evidence.exists() and not capture.exists()
freeze=ROOT/"tmp/2B/S2B-T17/s12_combined_prepare_20261012_r01/source_freeze_prepare.json"
paths=[x["path"] for x in json.loads(freeze.read_text(encoding="utf-8"))["source_files"]];assert len(paths)==43
pre={p:sha(ROOT/p) for p in paths}
assert psutil.virtual_memory().available>=536870912 and shutil.disk_usage("C:\\").free>=8589934592
capture.mkdir();command=[sys.executable,"-X","utf8","-B",str(runner),"--run-id",args.run_id,"--toolchain",r"D:\FPGA_S2A_MSYS2_20261001\env"]
start=time.monotonic();peak=0;min_ram=2**64;min_disk=2**64;stop=None;samples=0;cache_peak=0;report_peak=0
with (capture/"runner.stdout.log").open("xb") as out,(capture/"runner.stderr.log").open("xb") as err,(capture/"samples.jsonl").open("x",encoding="utf-8",newline="\n") as stream:
    child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err);p=psutil.Process(child.pid);birth=p.create_time();identity={"pid":p.pid,"birth":birth,"exe":p.exe(),"cwd":p.cwd(),"cmdline":p.cmdline()}
    print(json.dumps({"identity":identity,"command":subprocess.list2cmdline(command),"cache":str(work),"evidence":str(evidence)},ensure_ascii=False),flush=True)
    while child.poll() is None:
        try:
            root=psutil.Process(child.pid);assert root.create_time()==birth
            rss=sum(p.memory_info().rss for p in [root]+root.children(recursive=True) if p.is_running())
        except psutil.NoSuchProcess:
            if child.poll() is not None:break
            rss=0
        ram=psutil.virtual_memory().available;disk=shutil.disk_usage("C:\\").free
        cache=sum(p.stat().st_size for p in work.rglob("*") if p.is_file()) if work.exists() else 0
        size=sum(p.stat().st_size for p in evidence.rglob("*") if p.is_file()) if evidence.exists() else 0
        peak=max(peak,rss);min_ram=min(min_ram,ram);min_disk=min(min_disk,disk);cache_peak=max(cache_peak,cache);report_peak=max(report_peak,size);samples+=1
        elapsed=time.monotonic()-start
        stream.write(json.dumps({"seconds":elapsed,"tree_rss_bytes":rss,"available_ram_bytes":ram,"C_free_bytes":disk,"cache_bytes":cache,"evidence_bytes":size})+"\n");stream.flush()
        if rss>1073741824 or cache>671088640 or size>104857600 or ram<536870912 or disk<8589934592 or elapsed>600:
            stop="RSS_LIMIT" if rss>1073741824 else "CACHE_LIMIT" if cache>671088640 else "EVIDENCE_LIMIT" if size>104857600 else "LOW_RAM" if ram<536870912 else "LOW_DISK" if disk<8589934592 else "TIMEOUT"
            subprocess.run(["taskkill","/PID",str(child.pid),"/T","/F"],cwd=ROOT,stdout=err,stderr=err,timeout=30);break
        time.sleep(.25)
    code=child.wait(timeout=30)
post={p:sha(ROOT/p) for p in pre}
receipt={"task":args.task,"command":subprocess.list2cmdline(command),"cwd":str(ROOT),"native_returncode":code,"supervisor_stop":stop,"identity":identity,"runner_sha256":sha(runner),"supervisor_sha256":sha(Path(__file__)),"source_pre":pre,"source_post":post,"source_stable":pre==post,"initial_prepare_sha256":sha(freeze),"initial_prepare_scope":"只采用43路径清单；当前哈希真实重新读取，不继承初始旧语义字段/哈希。","admission_sha256":sha(admission),"samples":samples,"sampled_tree_peak_rss_bytes":peak,"sampled_cache_peak_bytes":cache_peak,"sampled_report_peak_bytes":report_peak,"minimum_available_ram_bytes":min_ram,"minimum_C_free_bytes":min_disk,"elapsed_seconds":time.monotonic()-start,"files":[{"path":str(capture/n),"sha256":sha(capture/n),"role":"log"} for n in ("runner.stdout.log","runner.stderr.log","samples.jsonl")],"limits":"250ms采样峰非连续绝对峰；单任务总600s外层更严格限制。feature旧metadata300MiB及backend内simulation1200s保持原件，S12实际外层640MiB/600s；不是STA/G2/G3证明。"}
with (capture/"native_receipt.json").open("x",encoding="utf-8",newline="\n") as stream:stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({key:receipt[key] for key in ("task","native_returncode","supervisor_stop","samples","sampled_tree_peak_rss_bytes","elapsed_seconds","source_stable")},ensure_ascii=False),flush=True)
raise SystemExit(code or (1 if stop or pre!=post else 0))
