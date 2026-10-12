"""捕获S15 runner直接子进程wait码，原始流不覆盖，内层记录资源峰值。"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

root=Path.cwd()
sys.path.insert(0,str(root/'verification'))
import test_s2b_conv_tile_origin_rtl as support

parser=argparse.ArgumentParser()
parser.add_argument('--mode',required=True)
parser.add_argument('--attempt',required=True)
args=parser.parse_args()
parent=support.exact_directory(root/'report/evidence/S2B-T17')
base=parent/'s15_arithmetic_fix_20261012_r01'
if not base.exists():base.mkdir()
base=support.exact_directory(base)
capture=base/('native_'+args.mode+'_'+args.attempt)
capture.mkdir()
command=[sys.executable,'-B','verification/test_s2b_s15_arithmetic_rtl.py','--mode',args.mode,'--attempt',args.attempt]
started=time.monotonic()
with (capture/'stdout.bin').open('xb') as stdout,(capture/'stderr.bin').open('xb') as stderr:
    child=subprocess.Popen(command,cwd=root,stdout=stdout,stderr=stderr)
    code=child.wait()
record=dict(command=command,cwd=str(root),native_exit_code=code,direct_wait_exit_code=code,pid=child.pid,elapsed_seconds=time.monotonic()-started,created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),peak_rss='外层未测；内层每个compile/simulation实际监测')
record['streams']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in capture.iterdir()}
support.save(capture/'native.json',record)
print(json.dumps(record,ensure_ascii=False),flush=True)
raise SystemExit(code)
