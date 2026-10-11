import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

# 自测夹具仅睡眠，不分配大内存；子进程由夹具显式启动。
parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["child", "normal", "tree", "mixed"], required=True)
parser.add_argument("--ready", required=True)
parser.add_argument("--unknown-cwd")
args = parser.parse_args()
children = []
if args.mode in {"tree", "mixed"}:
    cwd = str(Path.cwd())
    child = subprocess.Popen([sys.executable, "-S", "-B", "-X", "utf8", str(Path(__file__).absolute()), "--mode", "child", "--ready", str(Path(args.ready).with_name("child_ready.json"))], cwd=cwd)
    children.append(child.pid)
    if args.mode == "mixed":
        child = subprocess.Popen([sys.executable, "-S", "-B", "-X", "utf8", str(Path(__file__).absolute()), "--mode", "child", "--ready", str(Path(args.ready).with_name("unknown_ready.json"))], cwd=args.unknown_cwd)
        children.append(child.pid)
Path(args.ready).write_text(json.dumps({"pid": __import__("os").getpid(), "children": children}) + "\n", encoding="utf-8")
time.sleep(1.5 if args.mode == "normal" else 45)
