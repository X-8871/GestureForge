"""仅创建本次审查自己的标准库轻量父子夹具，标记使其自然退出。"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

work = Path.cwd()
role = sys.argv[1]
if role in {"root", "helper"}:
    subprocess.Popen([sys.executable, "-S", "-B", str(Path(__file__).absolute()), "helper" if role == "root" else "leaf"], cwd=work)
(work / (role + "_ready.json")).write_text(json.dumps({"pid": os.getpid()}), encoding="utf-8")
deadline = time.monotonic() + 25
while time.monotonic() < deadline and not (work / (role + "_exit")).exists():
    time.sleep(0.02)
