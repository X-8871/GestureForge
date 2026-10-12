"""记录本轮自有 Vivado 的真实身份；不访问板卡或停止进程。"""

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psutil


def main():
    """输入精确路径须存在，读取后再次核对 PID 出生时间。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--allowed", required=True, nargs="+")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if not output.parent.is_dir() or output.exists():
        raise ValueError("输出精确父目录不存在或目标已存在")
    cwd = Path(args.cwd)
    log = Path(args.log)
    allowed = [Path(item) for item in args.allowed]
    if not cwd.is_dir() or not log.is_file() or not all(item.is_dir() for item in allowed):
        raise ValueError("真实工作目录、日志或允许目录类型错误")
    process = psutil.Process(args.pid)
    birth = process.create_time()
    actual = dict(pid=process.pid, create_time=birth, exe=process.exe(),
                  cwd=process.cwd(), cmdline=process.cmdline(), ppid=process.ppid())
    if Path(actual["cwd"]) != cwd or not Path(actual["exe"]).is_file():
        raise ValueError("实际自有进程路径不同")
    if not process.is_running() or psutil.Process(args.pid).create_time() != birth:
        raise ValueError("进程已退出或 PID 发生复用")
    actual.update(source_commit="467463757158aed80d6f75afadff6a8458614a29",
                  run_id="s12_physical_launch_20261012_r01",
                  allowed_run_dirs=[str(item.resolve()) for item in allowed],
                  progress_logs=[str(log.resolve())], no_progress_seconds=900,
                  captured_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat())
    output.write_text(json.dumps(actual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(status="CAPTURED_OWNED_IDENTITY", binding=str(output),
                         binding_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                         identity=actual), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
