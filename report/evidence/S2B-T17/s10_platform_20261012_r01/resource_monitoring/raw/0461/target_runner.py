import argparse
import json
import time
from pathlib import Path

import psutil
import guard

# 只替换调度或单次父NoSuch；身份、RSS、实际停止和进程全部真实。
parser = argparse.ArgumentParser()
parser.add_argument("case", choices=["race", "parent_nosuch", "orphan"])
parser.add_argument("binding")
parser.add_argument("plan")
parser.add_argument("output")
parser.add_argument("--short-pid", type=int)
args = parser.parse_args()
b = json.loads(Path(args.binding).read_text(encoding="utf-8"))
p = json.loads(Path(args.plan).read_text(encoding="utf-8"))
monitor = guard.Guard(p, b, Path(args.output))
if args.case == "race":
    stale = psutil.Process(args.short_pid)
    saved_birth = stale.create_time()
    original_children = psutil.Process.children
    original_limits = monitor.limits
    while psutil.pid_exists(args.short_pid):
        time.sleep(0.02)
    calls = [0]

    def scheduled_children(process, recursive=False):
        calls[0] += 1
        actual = original_children(process, recursive=recursive)
        return [stale] + actual if calls[0] == 1 else actual

    def scheduled_limits():
        limits = original_limits()
        if monitor.sample_count >= 1:
            limits["tree_rss_bytes"] = 1
        return limits

    psutil.Process.children = scheduled_children
    monitor.limits = scheduled_limits
    monitor.event_fixture_identity = {"pid": args.short_pid, "birth": saved_birth}
elif args.case == "parent_nosuch":
    original_identity = guard.identity
    calls = [0]

    def inject_parent_nosuch(process):
        if process.pid != b["pid"] and calls[0] == 0:
            calls[0] += 1
            # 候选实际活着，模拟身份读取中仅父/祖先NoSuch的异常出口。
            actual = guard.base_identity(process)
            raise psutil.NoSuchProcess(actual["ppid"], msg="SELFTEST_PARENT_ONLY_NOSUCH")
        return original_identity(process)

    guard.identity = inject_parent_nosuch
raise SystemExit(monitor.run())
