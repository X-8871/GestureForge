"""仅监督器隔离自测替身，不采样或停止任何目标对象。"""
import argparse
import json
import os
from pathlib import Path
import time

p=argparse.ArgumentParser(); p.add_argument("--binding"); p.add_argument("--output-dir"); p.add_argument("--case"); a=p.parse_args()
binding=json.loads(Path(a.binding).read_text(encoding="utf-8")); out=Path(a.output_dir); out.mkdir()
os.write(1,"替身原始stdout\n".encode("utf-8")); os.write(2,"替身原始stderr\n".encode("utf-8"))
codes={"valid":0,"missing":7,"mismatch":9,"alert":2,"invalid":11,"empty":4,"identity_loss":6,"bad_terminal":8}
if a.case!="missing":
    row=dict(index=0,members=[dict(binding)],alerts=[],uncertain=[])
    if a.case=="mismatch": row["members"][0]["pid"]+=1
    if a.case=="alert": row["alerts"]=["FIXTURE_ALERT"]
    text="{bad}\n" if a.case=="invalid" else "" if a.case=="empty" else json.dumps(row)+"\n"
    with (out/"samples.jsonl").open("x",encoding="utf-8") as f: f.write(text); f.flush(); os.fsync(f.fileno())
time.sleep(0.3)
if a.case in ("valid","bad_terminal"):
    with (out/"guard_receipt.json").open("x",encoding="utf-8") as f:
        f.write(json.dumps(dict(status="ROOT_EXITED",known_members_count=1,fixture=True)) if a.case=="valid" else "{bad}"); f.flush(); os.fsync(f.fileno())
raise SystemExit(codes[a.case])
