#!/usr/bin/env python3
"""只读采样ROOT自有综合进程树；不停止、控制或修改真实任务。"""
import hashlib
import json
import os
from pathlib import Path
import psutil
import subprocess
import time

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[3]
OWNED_PID=33940
CREATED=1791731869.1464615
EXPECTED=ROOT/"tmp/2B/S2B-T17/s9_root_run_20261011_r01"
SID="vivado-20261011-231748-2cdeefaf"
INTERVAL=20
MAX_SECONDS=420
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def stamp():
    """使用南京UTC+8当地时间标注样本。"""
    return time.strftime("%Y-%m-%d %H:%M:%S +08:00",time.localtime())


def write(path,value):
    """只创建新的原始结果。"""
    with path.open("x",encoding="utf-8",newline="\n") as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write("\n")


def main():
    """核验实际工作目录同一对象、PID创建时间后进行有限周期采样。"""
    assert EXPECTED.is_dir()
    started=time.monotonic()
    samples=[]
    stop="MAX_DURATION"
    try:
        p=psutil.Process(OWNED_PID)
        identity={"pid":p.pid,"ppid":p.ppid(),"name":p.name(),"exe":p.exe(),"cwd":p.cwd(),"create_time":p.create_time(),"cmdline":p.cmdline(),"captured_at":stamp()}
        assert identity["create_time"]==CREATED and identity["name"].lower()=="vivado.exe"
        assert os.path.samefile(identity["cwd"],str(EXPECTED))
        identity["cwd_samefile_expected"]=True
    except psutil.NoSuchProcess:
        identity={"pid":OWNED_PID,"status":"MISSING_AT_START","captured_at":stamp()}
        stop="OWNED_PID_MISSING"
    write(WORK/"identity.json",identity)
    head_argv=["git","rev-parse","HEAD"]
    head=subprocess.run(head_argv,cwd=ROOT,capture_output=True)
    assert head.returncode==0 and head.stdout.decode().strip()=="38c5bc02f42920d4203aa6752530d09c80fc4c57"
    write(WORK/"source_head_native.json",{"command":subprocess.list2cmdline(head_argv),"native_exit_code":head.returncode,"stdout":head.stdout.decode("utf-8"),"stderr":head.stderr.decode("utf-8")})
    with (WORK/"samples.jsonl").open("x",encoding="utf-8",newline="\n") as raw:
        while "status" not in identity and time.monotonic()-started<=MAX_SECONDS:
            if (WORK/"STOP_REQUEST").exists():stop="ROOT_NOTIFICATION";break
            try:
                owned=psutil.Process(OWNED_PID)
                if owned.create_time()!=CREATED:stop="OWNED_PID_REUSED";break
                tree=[owned,*owned.children(recursive=True)]
                processes=[];unavailable=[]
                for child in tree:
                    try:processes.append({"pid":child.pid,"name":child.name(),"rss_bytes":child.memory_info().rss,"create_time":child.create_time()})
                    except (psutil.NoSuchProcess,psutil.AccessDenied) as exc:unavailable.append({"pid":child.pid,"exception":type(exc).__name__})
            except psutil.NoSuchProcess:stop="OWNED_PID_MISSING";break
            memory=psutil.virtual_memory()
            rss=sum(item["rss_bytes"] for item in processes)
            sample={"sample_index":len(samples),"at":stamp(),"elapsed_seconds":round(time.monotonic()-started,3),"owned_tree_rss_bytes":rss,"system_available_ram_bytes":memory.available,"system_free_ram_bytes":memory.free,"c_disk_free_bytes":psutil.disk_usage("C:\\").free,"processes":processes,"unavailable_processes":unavailable,"alerts":[]}
            if memory.available<512*1024*1024:sample["alerts"].append("AVAILABLE_RAM_LT_512MiB")
            if rss>4*1024*1024*1024:sample["alerts"].append("OWNED_TREE_RSS_GT_4GiB")
            samples.append(sample);raw.write(json.dumps(sample,ensure_ascii=False)+"\n");raw.flush()
            print(json.dumps(sample,ensure_ascii=False),flush=True)
            if sample["alerts"]:stop="RESOURCE_ALERT_SAMPLER_STOP";break
            deadline=min(started+MAX_SECONDS,time.monotonic()+INTERVAL)
            while time.monotonic()<deadline:
                if (WORK/"STOP_REQUEST").exists():break
                time.sleep(min(1,deadline-time.monotonic()))
    result={"status":"STOP","sid":SID,"owned_pid":OWNED_PID,"identity_sha256":sha(WORK/"identity.json"),"stop_reason":stop,"samples":len(samples),"sampling_interval_seconds":INTERVAL,"maximum_seconds":MAX_SECONDS,"elapsed_seconds":round(time.monotonic()-started,3),"sampled_peak_tree_rss_bytes":max((s["owned_tree_rss_bytes"] for s in samples),default=None),"sampled_min_available_ram_bytes":min((s["system_available_ram_bytes"] for s in samples),default=None),"sampled_min_c_disk_free_bytes":min((s["c_disk_free_bytes"] for s in samples),default=None),"raw":{"path":str(WORK/"samples.jsonl"),"sha256":sha(WORK/"samples.jsonl")},"alerts":[{"at":s["at"],"alerts":s["alerts"]} for s in samples if s["alerts"]],"limitations":"20秒离散采样所得峰与最小值，仅监测上述身份核验的PID树；非真实连续绝对峰。未执行ROSS/Tcl/任务终止/硬件操作，不证明设计G2/STA/G3。"}
    write(WORK/"sampler_receipt.json",result)
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=="__main__":main()
