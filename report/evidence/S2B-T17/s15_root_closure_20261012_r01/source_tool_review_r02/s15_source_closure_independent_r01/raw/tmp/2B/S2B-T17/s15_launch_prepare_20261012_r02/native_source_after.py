"""ROOT明确授权后的轻量source-after包装；直接子身份/返回和未知分列。"""
import argparse
from pathlib import Path
import re
import sys
import compat_pins
import native_capture

parser = argparse.ArgumentParser(); parser.add_argument("--expected-head", required=True); parser.add_argument("--output-dir", required=True, type=Path)
args = parser.parse_args(); compat_pins.require_ready(pnr=True)
if not re.fullmatch(r"[0-9a-f]{40}", args.expected_head) or args.expected_head != compat_pins.SOURCE_COMMIT:
    raise ValueError("CLI必须等于SOURCE")
out = args.output_dir
if not out.is_absolute() or out.parent.parts != compat_pins.PNR_CACHE.parts or out.exists() or not re.fullmatch(r"source_after_check_r[0-9]+", out.name):
    raise ValueError("输出不是本轮PNR cache精确新目录")
compat_pins.exact(out.parent, True)
script = compat_pins.exact(Path(__file__).parent/"source_after_check.py")
sys.argv = [str(Path(__file__)), "s13_"+out.name, sys.executable, "-X", "utf8", "-B", str(script), "--expected-head", args.expected_head, "--output-dir", str(out)]
raise SystemExit(native_capture.main())
