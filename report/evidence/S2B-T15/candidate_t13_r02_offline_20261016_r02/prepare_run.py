"""沿用已审候选构建入口，仅更换隔离工作目录。"""
import hashlib
from pathlib import Path
import shutil

RUN = Path(__file__).resolve().parent
OLD = RUN.parent / "candidate_t13_r02_offline_20261016_r01"
source = OLD / "launch_build.py"
assert hashlib.sha256(source.read_bytes()).hexdigest() == "debed8e17b41049731866ce078a21bc974a950f93388592113ad523f9479b1b9"
text = source.read_text(encoding="utf-8")
before = 'WORK = ROOT / "tmp/2B/S2B-T15/c16r1"'
assert text.count(before) == 1
text = text.replace(before, 'WORK = ROOT / "tmp/2B/S2B-T15/c16r2"')
with (RUN / "launch_build.py").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(text)
shutil.copy2(OLD / "check_launcher_preflight.py", RUN / "check_launcher_preflight.py")
print(hashlib.sha256((RUN / "launch_build.py").read_bytes()).hexdigest())
