#!/usr/bin/env python3
"""S9原生执行包装；已有runner只替换缓存父目录，oracle、刺激和判据不动。"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import types

import psutil

ROOT=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parent
BASELINE="5ea54b441bd885e10eac4794cbad5ad48c510a49"
PYTHON=Path(r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe")
RUNS={"direct":("verification/test_s2b_conv_output_address_rtl.py","conv_output_address_20261011_r01",[]),
      "direct_r02":("verification/test_s2b_conv_output_address_rtl.py","conv_output_address_20261011_r02",[]),
      "direct_r03":("verification/test_s2b_conv_output_address_rtl.py","conv_output_address_20261011_r03",[]),
      "boundary":("verification/test_s2b_conv_validation_rtl.py","conv_output_address_boundary_20261011_r01",["--mode","boundary"]),
      "layer0":("verification/test_s2b_conv_validation_rtl.py","conv_output_address_layer0_20261011_r01",["--mode","layer0"]),
      "backend":("verification/test_s2b_backend_coordinates_rtl.py","conv_output_address_trace_20261011_r01",[]),
      "geometry":("verification/test_s2b_geometry_specialization_rtl.py","conv_output_address_geometry_20261011_r01",[])}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def resources():
    """读取实际RAM、磁盘和已存在重型进程，不查询或操作硬件。"""
    processes=[]
    for p in psutil.process_iter(["name","cmdline","memory_info"]):
        try:
            if p.info["name"] and re.fullmatch(r"(?:vivado|vitis|verilator_bin|g\+\+|cc1plus|xsim|Vtb_.*)\.exe",p.info["name"],re.I):
                processes.append({"pid":p.pid,"name":p.info["name"],"cmdline":p.info["cmdline"],"rss":p.info["memory_info"].rss})
        except psutil.Error:
            pass
    return {"epoch":time.time(),"available_ram_bytes":psutil.virtual_memory().available,
            "total_ram_bytes":psutil.virtual_memory().total,"disk_free_bytes":shutil.disk_usage(WORK).free,"existing_tools":processes}


def child(stage):
    """只有经限定的缓存父目录替换允许进入现有runner。"""
    if stage=="preflight":
        data=resources()
        assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==BASELINE
        for path in [ROOT/p for p in {r[0] for r in RUNS.values()}|{"verification/check_s2b_inference_platform.py"}]:
            ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
        assert data["available_ram_bytes"]>2*1024**3 and data["disk_free_bytes"]>1024**3
        assert not any(re.fullmatch(r"(?:vivado|verilator_bin|cc1plus|xsim|Vtb_.*)\.exe",i["name"],re.I) for i in data["existing_tools"])
        (WORK/"resource_preflight.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        command=[str(PYTHON),"-X","utf8","-B",str(ROOT/"verification/check_s2b_inference_platform.py"),"--root",str(ROOT)]
        done=subprocess.run(command,cwd=ROOT,capture_output=True)
        record={"command":subprocess.list2cmdline(command),"argv":command,"native_exit_code":done.returncode,
                "stdout":done.stdout.decode("utf-8"),"stderr":done.stderr.decode("utf-8")}
        (WORK/"static_native.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"resource":data,"static":record},ensure_ascii=False))
        return done.returncode
    relative,runid,extra=RUNS[stage]
    source=ROOT/relative
    sys.path.insert(0,str(source.parent))
    raw=source.read_bytes();text=raw.decode("utf-8")
    substitutions=[]
    if stage in ("boundary","layer0","backend"):
        before='work=ROOT/"tmp/2B/S2B-T17"/args.run_id;evidence=ROOT/"report/evidence/S2B-T17"/args.run_id' if stage in ("boundary","layer0") else 'work=ROOT/"tmp/2B/S2B-T17"/args.run_id; evidence=ROOT/"report/evidence/S2B-T17"/args.run_id'
        after=before.replace('ROOT/"tmp/2B/S2B-T17"','ROOT/"tmp/2B/S2B-T17/s9_conv_g1_20261011_r01"')
        assert text.count(before)==1
        text=text.replace(before,after);substitutions.append({"before":before,"after":after})
    elif stage=="geometry":
        before='work = ROOT / "tmp/2B/S2B-T17" / args.run_id'
        after='work = ROOT / "tmp/2B/S2B-T17/s9_conv_g1_20261011_r01" / args.run_id'
        assert text.count(before)==1
        text=text.replace(before,after);substitutions.append({"before":before,"after":after})
    capture={"stage":stage,"source":relative,"source_sha256":sha(source),"transformed_sha256":hashlib.sha256(text.encode()).hexdigest(),
             "unique_substitutions":substitutions,"run_id":runid,"extra":extra,"wrapper_sha256":sha(Path(__file__))}
    (WORK/(stage+"_adapter.json")).write_text(json.dumps(capture,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (WORK/(stage+"_runtime.py")).write_text(text,encoding="utf-8",newline="\n")
    module=types.ModuleType("s9_"+stage);module.__file__=str(source)
    exec(compile(text,str(source),"exec"),module.__dict__)
    sys.argv=[str(source),"--run-id",runid,*extra]
    return module.main()


def main():
    """逐阶段单并发运行，90秒无日志进度先告知，240秒无进度停止。"""
    parser=argparse.ArgumentParser();parser.add_argument("stage",choices=("preflight",*RUNS));parser.add_argument("--child",action="store_true")
    args=parser.parse_args()
    assert PYTHON.is_file() and Path.cwd().resolve()==ROOT
    if args.child:return child(args.stage)
    stage=args.stage
    prefix=WORK/stage
    capture_path=Path(str(prefix)+"_native.json")
    assert not capture_path.exists()
    before=resources()
    argv=[str(PYTHON),"-X","utf8","-B",str(Path(__file__)),stage,"--child"]
    started=time.monotonic();progress=started;peak=0;lastsize=-1;stop=None
    outpath=Path(str(prefix)+"_stdout.log");errpath=Path(str(prefix)+"_stderr.log")
    env=os.environ.copy()
    for key in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):env[key]="1"
    with outpath.open("xb") as out,errpath.open("xb") as err:
        process=subprocess.Popen(argv,cwd=ROOT,stdout=out,stderr=err,env=env)
        while process.poll() is None:
            now=time.monotonic()
            try:
                owner=psutil.Process(process.pid)
                peak=max(peak,sum(p.memory_info().rss for p in [owner]+owner.children(recursive=True) if p.is_running()))
            except psutil.Error:pass
            size=outpath.stat().st_size+errpath.stat().st_size
            if size!=lastsize:lastsize=size;progress=now
            if peak>1610612736 or now-started>1500 or now-progress>240 or shutil.disk_usage(WORK).free<512*1024**2:
                stop="RSS_1.5G_OR_1500S_OR_NO_PROGRESS_240S_OR_DISK_512M"
                subprocess.run(["taskkill","/PID",str(process.pid),"/T","/F"],stdout=err,stderr=err,timeout=30)
                break
            time.sleep(0.2)
        code=process.wait(timeout=30)
    record={"stage":stage,"command":subprocess.list2cmdline(argv),"argv":argv,"cwd":str(ROOT),"native_exit_code":code,
            "host_shell_exit_code":None,"elapsed_seconds":round(time.monotonic()-started,3),"peak_tree_rss_bytes":peak,
            "stop_reason":stop,"resource_before":before,"resource_after":resources(),"wrapper_sha256":sha(Path(__file__)),
            "stdout":{"path":outpath.relative_to(ROOT).as_posix(),"sha256":sha(outpath),"bytes":outpath.stat().st_size},
            "stderr":{"path":errpath.relative_to(ROOT).as_posix(),"sha256":sha(errpath),"bytes":errpath.stat().st_size}}
    capture_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record,ensure_ascii=False))
    return code


if __name__=="__main__":raise SystemExit(main())
