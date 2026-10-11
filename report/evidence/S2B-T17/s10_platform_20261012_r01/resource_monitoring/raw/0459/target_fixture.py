import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# 真实轻量父子夹具：短命helper、持续child或根先自然退出。
parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["race", "orphan", "leaf", "short"])
parser.add_argument("ready")
args = parser.parse_args()
path = Path(args.ready)
children = []
if args.mode in {"race", "orphan"}:
    for mode, name in [("leaf", "long.json")] + ([("short", "short.json")] if args.mode == "race" else []):
        child = subprocess.Popen([sys.executable, "-B", "-X", "utf8", str(Path(__file__).absolute()), mode, str(path.with_name(name))], cwd=Path.cwd())
        children.append(child.pid)
path.write_text(json.dumps({"pid": os.getpid(), "children": children}) + "\n", encoding="utf-8")
time.sleep(1.5 if args.mode == "short" else 2.5 if args.mode == "orphan" else 40)
