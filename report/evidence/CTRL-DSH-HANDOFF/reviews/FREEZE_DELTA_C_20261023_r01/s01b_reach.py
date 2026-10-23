# 检查 3b：可达性（用 rev-parse 展开短哈希）、悬垂提交、STATE 取代关系
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import show, run

NAMES = {
    "F": "0725d9cf", "G": "1e2a66c", "F2": "33b1fee", "G2": "8ecd92cb",
    "F3": "efb9f191", "F4": "6b8e5f2", "G4": "f5b749e",
}
FULL = {}
for k, s in NAMES.items():
    rc, o, e = run(["rev-parse", s])
    FULL[k] = o.strip()
    print(f"{k:3s} {s} -> {o.strip()} (exit {rc})")

rc, out, _ = run(["rev-list", "HEAD"])
reach = set(out.split())
print("\n可达性（自 HEAD）：")
for k, c in FULL.items():
    print(f"  {k:3s} {c[:12]} reachable={c in reach}")

print("\n#### git log --oneline --graph -8")
show(["log", "--oneline", "--graph", "-8"])

print("#### git fsck --unreachable --no-progress（前 60 行）")
rc, out, err = run(["fsck", "--unreachable", "--no-progress"])
print(f"[exit {rc}]")
lines = (out + err).splitlines()
print("\n".join(lines[:60]))
print(f"... 共 {len(lines)} 行")

print("\n#### git fsck --dangling --no-progress（前 20 行）")
rc, out, err = run(["fsck", "--dangling", "--no-progress"])
print(f"[exit {rc}]")
lines = (out + err).splitlines()
print("\n".join(lines[:20]))
print(f"... 共 {len(lines)} 行")

print("\n#### reflog（前 30 行）")
show(["reflog", "--date=iso", "-30"])