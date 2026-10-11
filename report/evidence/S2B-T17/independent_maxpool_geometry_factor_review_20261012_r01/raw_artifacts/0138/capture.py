"""原字节封存审查stdout/stderr和原生码。"""
import json
from pathlib import Path
import subprocess
import sys
import time
base=Path(__file__).absolute().parent
command=[sys.executable,"-B","-X","utf8",str(base/"review.py")]
stem="review"
if len(sys.argv)>1:
    command.append(sys.argv[1]); stem="review_"+sys.argv[1]
start=time.monotonic()
with (base/(stem+".stdout.log")).open("xb") as so,(base/(stem+".stderr.log")).open("xb") as se: child=subprocess.run(command,stdout=so,stderr=se)
with (base/(stem+".native.json")).open("x",encoding="utf-8") as stream: json.dump({"command":command,"native_exit_code":child.returncode,"elapsed_seconds":time.monotonic()-start},stream,ensure_ascii=False,indent=2)
print(json.dumps({"native_exit_code":child.returncode}))
raise SystemExit(child.returncode)
