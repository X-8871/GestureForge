# 检查 3：tag / 可达性 / 父链
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import show, run

TAGS = ["s6a-g0-v1.8-r09", "s6b-core-r04", "stage6-freeze-20261023",
        "stage6-freeze-20261023-r2", "stage6-freeze-20261023-r3"]
COMMITS = {
    "F": "0725d9cf48aeed21d3ea445ef01575c16b68d950",
    "G": "1e2a66c904b15ed7e8a01206c3c2fe4a43dc760e",
    "F2": "33b1fee",
    "G2": "8ecd92cb35a34c29fc9570d5fcbed955f2063fd8",
    "F3": "efb9f191",
    "F4": "6b8e5f2a23ce6f7dec41fc9992141b3423612081",
    "G4": "f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d",
}

print("#### 1. tag -> commit (peel) & tag 对象类型")
for t in TAGS:
    rc1, o1, _ = run(["rev-parse", t + "^{commit}"])
    rc2, o2, _ = run(["cat-file", "-t", t])
    rc3, o3, _ = run(["rev-list", "-n", "1", t])
    print(f"{t:34s} type={o2.strip():9s} rev-parse^{{commit}}={o1.strip()[:12]} rev-list-n1={o3.strip()[:12]}")

print()
print("#### 2. 关键提交对象类型（当前仓库）")
for k, c in COMMITS.items():
    rc, o, e = run(["cat-file", "-t", c])
    rc2, subj, _ = run(["log", "-1", "--format=%H %P | %s", c])
    print(f"{k:4s} {c[:12]} type={o.strip() or 'MISSING'}  {subj.strip()}")

print()
print("#### 3. 全量 rev-list HEAD（判断可达性）")
rc, out, _ = run(["rev-list", "HEAD"])
reach = set(out.split())
for k, c in COMMITS.items():
    print(f"{k:4s} full={c}  reachable_from_HEAD={c in reach}")
print("HEAD 可达提交总数 =", len(reach))

print()
print("#### 4. F4 / G4 的父链")
for k in ["F4", "G4"]:
    show(["log", "--format=%H%n  parents=%P%n  author=%an%n  date=%ad%n  subject=%s", "-1", COMMITS[k]], k)

print()
print("#### 5. 各提交是否含 'F2 不可达' 相关记录（grep STATE）")
show(["show", "G4:.codex/STATE.md"])