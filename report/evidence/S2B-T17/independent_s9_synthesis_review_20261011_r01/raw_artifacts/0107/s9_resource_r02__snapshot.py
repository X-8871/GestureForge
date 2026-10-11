#!/usr/bin/env python3
"""只读核验综合结束后的自有进程树及历史子进程身份。"""
import hashlib
import json
import os
from pathlib import Path
import psutil
import sys
import time

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[3]
EXPECTED=ROOT/"tmp/2B/S2B-T17/s9_root_run_20261011_r01"


def inspect(pid):
    """读取真实存活进程，缺失或权限问题按事实保存。"""
    try:
        p=psutil.Process(pid)
        return {"pid":pid,"ppid":p.ppid(),"name":p.name(),"exe":p.exe(),"cwd":p.cwd(),"creation_time":p.create_time(),"rss_bytes":p.memory_info().rss,"cmdline":p.cmdline()}
    except (psutil.NoSuchProcess,psutil.AccessDenied) as exc:return {"pid":pid,"status":type(exc).__name__}


started=time.monotonic()
owned=inspect(33940)
assert owned.get("creation_time")==1791731869.1464615 and owned["name"].lower()=="vivado.exe"
assert os.path.samefile(owned["cwd"],str(EXPECTED))
owned["same_work_directory"]=True
tree=[owned,*[inspect(p.pid) for p in psutil.Process(33940).children(recursive=True)]]
report={"at":time.strftime("%Y-%m-%d %H:%M:%S +08:00",time.localtime()),"owned":owned,"tree":tree,"owned_tree_rss_bytes":sum(p.get("rss_bytes",0) for p in tree),"r01_children":[inspect(28052),inspect(6940)],"available_ram_bytes":psutil.virtual_memory().available,"free_ram_bytes":psutil.virtual_memory().free,"c_disk_free_bytes":psutil.disk_usage("C:\\").free,"elapsed_seconds":time.monotonic()-started,"limits":{"tree_rss_bytes":4294967296,"available_ram_bytes":536870912},"scope":"单次结束后只读样本，不是连续峰；未控制任何任务。"}
report["resource_alerts"]=( ["TREE_RSS_GT_4GiB"] if report["owned_tree_rss_bytes"]>4294967296 else [] )+( ["AVAILABLE_RAM_LT_512MiB"] if report["available_ram_bytes"]<536870912 else [] )
with (WORK/"snapshot.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
print(json.dumps(report,ensure_ascii=False))
record={"command":sys.executable+" -X utf8 -B "+str(Path(__file__)),"native_exit_code":0,"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"snapshot_sha256":hashlib.sha256((WORK/"snapshot.json").read_bytes()).hexdigest(),"elapsed_seconds":time.monotonic()-started,"scope":"实际脚本成功完成后记录；退出异常不会生成此native0原件。"}
with (WORK/"native_capture.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write("\n")
print(json.dumps(record,ensure_ascii=False))
