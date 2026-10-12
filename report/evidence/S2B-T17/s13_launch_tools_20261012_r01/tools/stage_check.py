"""复用正式只读检查器；仅给Git追加已批准配置并捕获真实直接子身份/返回。"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import native_capture

W=Path(__file__).absolute().parent; ROOT=W.parents[3]
parser=argparse.ArgumentParser(add_help=False); parser.add_argument("--git-capture-prefix",required=True)
args,rest=parser.parse_known_args(); prefix=Path(args.git_capture_prefix)
assert prefix.parent.is_dir() and prefix.is_absolute() and prefix.is_relative_to(W)
original=subprocess.run
spec=importlib.util.spec_from_file_location("stage_delivery",ROOT/"verification/check_stage_delivery.py"); checker=importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)
count=0
def capture(command,**kwargs):
    global count
    if command[0]!="git": return original(command,**kwargs)
    command=["C:\\Program Files\\Git\\bin\\git.exe","-c","core.longpaths=true","-c","maintenance.auto=false",*command[1:]]
    paths=[prefix.with_name(prefix.name+"_"+str(count)+suffix) for suffix in (".stdout.bin",".stderr.bin",".native.json")]; count+=1
    assert not any(path.exists() for path in paths)
    child=subprocess.Popen(command,cwd=kwargs.get("cwd"),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    identity=None; unknown=None
    try: identity=native_capture.identity(native_capture.psutil.Process(child.pid))
    except (native_capture.psutil.Error,RuntimeError) as error: unknown=repr(error)
    stdout,stderr=child.communicate(timeout=20)
    for path,raw in zip(paths,(stdout,stderr)): path.write_bytes(raw)
    with paths[2].open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(dict(command=command,direct_child_pid=child.pid,direct_child_identity=identity,identity_unknown=unknown,native_exit_code=child.returncode,direct_child_wait_returned=True,whole_tree_terminal="NOT_PROVEN"),stream,ensure_ascii=False,indent=2); stream.write("\n")
    if kwargs.get("text"):
        stdout=stdout.decode(kwargs.get("encoding") or "utf-8",errors=kwargs.get("errors") or "strict"); stderr=stderr.decode(kwargs.get("encoding") or "utf-8",errors=kwargs.get("errors") or "strict")
    return subprocess.CompletedProcess(command,child.returncode,stdout,stderr)
checker.subprocess.run=capture
raise SystemExit(checker.main(rest))
