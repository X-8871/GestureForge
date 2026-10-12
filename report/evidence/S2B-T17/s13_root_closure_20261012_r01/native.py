"""轻量collector包装复用真实身份捕获；256MiB/120秒，不执行重型或硬件。"""
import argparse
import re
import sys
from pathlib import Path
import compat_pins
import native_capture

parser = argparse.ArgumentParser(); parser.add_argument("--prefix", required=True); parser.add_argument("arguments", nargs=argparse.REMAINDER)
args = parser.parse_args(); compat_pins.require_ready()
if not re.fullmatch(r"s13_[A-Za-z0-9_]+", args.prefix):
    raise ValueError("prefix必须为精确安全s13_标识符")
arguments = args.arguments[1:] if args.arguments and args.arguments[0] == "--" else args.arguments
if not arguments or arguments[0] not in ("prepare", "source", "collect", "seal"):
    raise ValueError("只能包装轻量collector模式")
path = compat_pins.exact(Path(__file__).parent/"collector.py")
sys.argv = [str(Path(__file__)), args.prefix, sys.executable, "-X", "utf8", "-B", str(path), *arguments]
raise SystemExit(native_capture.main())

