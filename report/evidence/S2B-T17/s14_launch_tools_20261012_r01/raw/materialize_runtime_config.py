"""将ROOT已审核真实输入写成唯一新JSON；不改工具源、不生成源码冻结或工程。"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import compat_pins as pins


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--input",required=True); parser.add_argument("--output",required=True); parser.add_argument("--pnr",action="store_true"); args=parser.parse_args()
    source=pins.exact(args.input); out=Path(args.output)
    pins.require(str(out)==args.output and out.parent==pins.WORK and re.fullmatch(r"runtime_pins_(?:synth|pnr)_r[0-9]+\.json",out.name),"输出不是本工具目录精确唯一JSON")
    pins.exact(out.parent,True); pins.require(not out.exists(),"配置输出已存在，禁止覆盖")
    raw=source.read_bytes(); pins.RUNTIME_CONFIG=source; pins._CONFIG_SELECTOR=None; pins.load_runtime_config(); pins.require_ready(args.pnr)
    freeze=json.loads(pins.pinned(pins.SOURCE_FREEZE,pins.SOURCE_FREEZE_SHA).read_text(encoding="utf-8"))
    pins.require(freeze.get("source_commit")==pins.SOURCE_COMMIT and freeze.get("profile")=="s2b-inference-platform/0.1.14","ROOT源码冻结与配置SOURCE/profile不同")
    pins.require(source.read_bytes()==raw,"输入配置核验期间变化")
    with out.open("xb") as stream: stream.write(raw)
    pins.require(out.read_bytes()==raw,"配置写入原字节不同")
    print(json.dumps({"status":"BOUND_CONFIG_NOT_SOURCE_READY","path":str(out),"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"source_commit":pins.SOURCE_COMMIT,"pnr":args.pnr,"tool_source_modified":False,"limitations":["此工具未读取实际HEAD或生产RAW；下一source-before仍强制CLI==SOURCE==actualHEAD并逐源核验。","配置仅数据绑定，不批准资源准入、heavy、硬件或G3-G5。"]},ensure_ascii=False))


if __name__=="__main__":
    try: raise SystemExit(main())
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps({"status":"BLOCKED_CONFIG_INPUTS","error":repr(error)},ensure_ascii=False)); raise SystemExit(2)
