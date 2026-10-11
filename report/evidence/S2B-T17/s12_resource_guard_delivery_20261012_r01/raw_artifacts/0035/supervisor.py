"""监督固定守卫自有子进程；终态阻止派发，不停止任何对象。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil

ROOT=Path(__file__).resolve().parents[4]
GUARD=ROOT/"tmp/2B/S2B-T17/s11_resource_guard_20261012_r02/guard.py"
GUARD_SHA="eca5338aeb738b86dbf77a0ae881c8dec5068b89bb4553719e8deba2423cb700"
KEYS=("pid","create_time","exe","cwd","cmdline")

def exact(value,directory=False):
    """逐组件核验精确名称和类型，不接受链接或路径别名。"""
    p=Path(value)
    if not p.is_absolute(): raise ValueError("必须绝对路径")
    current=Path(p.anchor)
    for part in p.parts[1:]:
        if part not in {x.name for x in current.iterdir()}: raise ValueError("精确路径不存在")
        current=current/part
        if current.is_symlink() or current.is_junction(): raise ValueError("拒绝链接")
    if not (current.is_dir() if directory else current.is_file()): raise ValueError("目标类型错误")
    return current

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(value): print(json.dumps(value,ensure_ascii=False,allow_nan=False),flush=True)
def identity(pid):
    """直接重查存活与创建时间，拒绝复用身份。"""
    p=psutil.Process(pid); birth=p.create_time()
    row=dict(pid=pid,create_time=birth,exe=p.exe(),cwd=p.cwd(),cmdline=p.cmdline())
    if not p.is_running() or psutil.Process(pid).create_time()!=birth: raise RuntimeError("身份漂移")
    return row

def supervise(command,binding,out,input_rows,interval=5):
    """替身只能自测导入注入；生产CLI不接受guard路径或阈值替换。"""
    exact(out.parent,True)
    if out.exists(): raise FileExistsError("输出目录已存在")
    out.mkdir(); ready=False; child=None; expected=None; code=None; reason=None; started=time.monotonic()
    def append(stream,row):
        stream.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+"\n"); stream.flush(); os.fsync(stream.fileno())
    with (out/"stdout.log").open("xb") as stdout,(out/"stderr.log").open("xb") as stderr,(out/"supervision.jsonl").open("x",encoding="utf-8",newline="\n") as journal:
        try:
            for row in input_rows:
                if sha(exact(row["path"]))!=row["sha256"]: raise ValueError("启动前输入SHA漂移")
            child=subprocess.Popen(command,cwd=binding["cwd"],stdout=stdout,stderr=stderr)
            next_check=0
            while True:
                code=child.poll()
                if code is not None: reason="GUARD_EXITED"; break
                receipt=out/"guard"/"guard_receipt.json"
                if receipt.exists():
                    reason="GUARD_TERMINAL_RECEIPT"
                    try: code=child.wait(timeout=2)
                    except subprocess.TimeoutExpired: pass
                    break
                if time.monotonic()>=next_check:
                    actual=identity(child.pid)
                    if expected is None:
                        expected=actual
                        if actual["exe"]!=command[0] or actual["cwd"]!=binding["cwd"] or actual["cmdline"]!=command: raise RuntimeError("guard启动身份不符")
                    if any(actual[k]!=expected[k] for k in KEYS): raise RuntimeError("guard身份失效")
                    append(journal,dict(kind="LIVE",elapsed_seconds=time.monotonic()-started,identity=actual)); next_check=time.monotonic()+interval
                sample=out/"guard"/"samples.jsonl"
                if not ready and sample.is_file():
                    with sample.open("rb") as stream: first=stream.readline()
                    if first.endswith(b"\n"):
                        row=json.loads(first); members=row.get("members",[])
                        match=bool(members) and row.get("index")==0 and all(members[0].get(k)==binding[k] for k in ("pid","create_time","exe","cwd"))
                        match=match and all(members[0].get(k)==binding[k] for k in ("cmdline","ppid") if k in binding)
                        if match and not row.get("alerts") and not row.get("uncertain"):
                            live=identity(child.pid)
                            if child.poll() is None and all(live[k]==expected[k] for k in KEYS) and not receipt.exists():
                                ready=True; value=dict(kind="READY",guard_identity=live,root_identity=members[0],first_sample_sha256=hashlib.sha256(first).hexdigest())
                                append(journal,value); emit(value)
                time.sleep(0.05)
        except (OSError,ValueError,KeyError,TypeError,RuntimeError,psutil.Error) as error:
            reason="SUPERVISION_ERROR:"+repr(error)
            if child is not None:
                try: code=child.wait(timeout=2)
                except subprocess.TimeoutExpired: code=child.poll()
        receipt_path=out/"guard"/"guard_receipt.json"
        try: terminal=json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else None
        except (OSError,ValueError) as error: terminal=dict(parse_error=repr(error)); reason="INVALID_TERMINAL_RECEIPT"
        value=dict(kind="TERMINAL",reason=reason,ready=ready,child_native_exit_code=code,guard_identity=expected,child_pid=None if child is None else child.pid,guard_terminal=terminal,command=command,windows_command=subprocess.list2cmdline(command),input_bindings=input_rows,supervisor_sha256=sha(Path(__file__)),elapsed_seconds=time.monotonic()-started,supervisor_exit_code=2,limitations=["终态一律非0阻止后续派发；child原生0仍按原值保存。","ROOT_EXITED只覆盖guard此前已知成员，不证明完整整树安全。","监督器不终止任何对象；身份失效时guard可能仍存活，ROOT须读取原件处置。","ROOT每5秒消费native会话的集成未由本工具执行。"])
        append(journal,value)
    value["logs"]=[dict(path=str(p),sha256=sha(p)) for p in (out/"stdout.log",out/"stderr.log",out/"supervision.jsonl")]
    with (out/"supervisor_receipt.json").open("x",encoding="utf-8",newline="\n") as stream: json.dump(value,stream,ensure_ascii=False,indent=2); stream.write("\n")
    emit(dict(kind="TERMINAL",reason=reason,ready=ready,child_native_exit_code=code,child_pid=value["child_pid"],guard_status=None if terminal is None else terminal.get("status"),receipt_path=str(out/"supervisor_receipt.json"),receipt_sha256=sha(out/"supervisor_receipt.json"),supervisor_exit_code=2)); return 2

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--plan",required=True); parser.add_argument("--binding",required=True); parser.add_argument("--output-dir",required=True); args=parser.parse_args()
    guard=exact(str(GUARD)); plan=exact(args.plan); bound=exact(args.binding); out=Path(args.output_dir)
    if not out.is_absolute() or sha(guard)!=GUARD_SHA: raise ValueError("固定guard路径/SHA或输出路径错误")
    binding=json.loads(bound.read_text(encoding="utf-8")); exact(binding["cwd"],True); json.loads(plan.read_text(encoding="utf-8"))
    if binding.get("fixture_test"): raise ValueError("生产CLI不接受fixture")
    inputs=[dict(path=str(p),sha256=sha(p)) for p in (guard,plan,bound)]
    command=[sys.executable,"-X","utf8","-B",str(guard),"--plan",str(plan),"--binding",str(bound),"--output-dir",str(out/"guard")]
    return supervise(command,binding,out,inputs)

if __name__=="__main__":
    try: raise SystemExit(main())
    except (OSError,ValueError,KeyError,TypeError) as error: emit(dict(kind="TERMINAL",reason=repr(error),ready=False,child_native_exit_code=None)); raise SystemExit(2)
