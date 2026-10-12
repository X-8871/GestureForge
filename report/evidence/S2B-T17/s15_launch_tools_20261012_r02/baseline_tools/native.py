"""轻量collector包装复用真实身份捕获；256MiB/120秒，不执行重型或硬件。"""
import argparse
import re
import sys
from pathlib import Path
import compat_pins
import native_capture

parser = argparse.ArgumentParser(); parser.add_argument("--prefix", required=True); parser.add_argument("arguments", nargs=argparse.REMAINDER)
args = parser.parse_args()
if not re.fullmatch(r"s15_runtime_[A-Za-z0-9_]+", args.prefix):
    raise ValueError("prefix必须为本轮实际包装专用s15_runtime_标识符")
arguments = args.arguments[1:] if args.arguments and args.arguments[0] == "--" else args.arguments
if not arguments or arguments[0] not in ("prepare", "source", "collect", "seal"):
    raise ValueError("只能包装轻量collector模式")
compat_pins.require_ready()
if arguments[0] != "prepare" and native_capture.HERE != compat_pins.SYNTH_CACHE:
    raise ValueError("非prepare原生输出目录必须与已pin CACHE相同")
path = compat_pins.exact(Path(__file__).parent/"collector.py")
sys.argv = [str(Path(__file__)), args.prefix, sys.executable, "-X", "utf8", "-B", str(path), *arguments]
raise SystemExit(native_capture.main(metadata=dict(mode=arguments[0], prefix=args.prefix)))

