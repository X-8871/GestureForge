"""单次原生启动后台消费器并保存真实移交；ROOT随后可调用长MCP操作。"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import runtime_consumer as consumer


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--config",required=True); parser.add_argument("--output-dir",required=True); args=parser.parse_args()
    path=consumer.exact(args.config); raw=path.read_bytes(); config=json.loads(raw)
    out=Path(args.output_dir); consumer.exact(out.parent,True)
    if str(out)!=args.output_dir or out.exists() or out.parent!=Path(config["output_dir"]).parent:
        raise ValueError("移交输出必须为consumer同父目录精确新目录")
    out.mkdir(); child,handoff=consumer.launch(str(path),str(out/"stdout.bin"),str(out/"stderr.bin"))
    handoff.update(config_path=str(path),config_sha256=hashlib.sha256(raw).hexdigest(),heavy_terminal="NOT_PROVEN",whole_tree_terminal="UNKNOWN",startup_first_consumption=None)
    deadline=time.monotonic()+2
    first=Path(config["output_dir"])/"consumption.jsonl"
    while child.poll() is None and time.monotonic()<deadline:
        if first.is_file():
            rows,binding=consumer.complete(str(first)); handoff["startup_first_consumption"]=dict(row=rows[0],binding=binding); break
        time.sleep(.05)
    current=None; error=None
    try: current=consumer.identity(child.pid)
    except consumer.psutil.Error as failure: error=repr(failure)
    ready=handoff["startup_first_consumption"] is not None and handoff["startup_first_consumption"]["row"]["status"]=="CONSUMED_LIVE_READY" and child.poll() is None and consumer.same(current,handoff["identity"]) and path.read_bytes()==raw
    handoff.update(status="READY_NATIVE_BACKGROUND_RUNNING" if ready else "BLOCKED_BACKGROUND_STARTUP",native_launcher_exit_code=0 if ready else 2,direct_child_poll=child.poll(),fresh_identity_readback=current,identity_error=error,
                   limitation="launcher退出不表示consumer或heavy退出；ROOT须保留此身份、原流和最终实际读回。")
    with (out/"handoff_receipt.json").open("x",encoding="utf-8",newline="\n") as stream: json.dump(handoff,stream,ensure_ascii=False,indent=2); stream.write("\n")
    print(json.dumps(handoff,ensure_ascii=False)); return 0 if ready else 2


if __name__=="__main__":
    try: raise SystemExit(main())
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,consumer.psutil.Error) as error:
        print(json.dumps({"status":"BLOCKED_BACKGROUND_STARTUP","error":repr(error),"heavy_terminal":"UNKNOWN"},ensure_ascii=False)); raise SystemExit(2)
