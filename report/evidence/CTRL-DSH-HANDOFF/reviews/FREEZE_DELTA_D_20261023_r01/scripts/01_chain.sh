#!/bin/bash
# 只读链/标签完整性核对；参数：$1 = 仓库路径
set -u
REPO="${1:-/d/codex-worktrees/w6}"
cd "$REPO" || exit 2
F4=6b8e5f2a23ce6f7dec41fc9992141b3423612081
G4=f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d
F5=caa9728af84b0a5b79bed17427eec0091b922923
G5=61caac0d8ce7be6f2ef8dfcd2380f3943cd6029f
G5b=c7ae6b4991bc769bdbd9683036a3c210b153c620
echo "=== repo: $(git rev-parse --show-toplevel) ==="
echo "--- HEAD / branch ---"
git rev-parse HEAD
git rev-parse --abbrev-ref HEAD
echo "--- cat-file -t ---"
for h in "$F4" "$G4" "$F5" "$G5" "$G5b"; do
  printf '%s -> %s\n' "$h" "$(git cat-file -t "$h" 2>&1)"
done
echo "--- tag -> rev-list -n1 ---"
for t in stage6-freeze-20261023 stage6-freeze-20261023-r2 stage6-freeze-20261023-r3 stage6-freeze-20261023-r4 s6a-g0-v1.8-r09 s6b-core-r04; do
  printf '%-32s -> %s\n' "$t" "$(git rev-list -n1 "$t" 2>&1)"
done
echo "--- tag objects (annotated?) ---"
for t in stage6-freeze-20261023 stage6-freeze-20261023-r2 stage6-freeze-20261023-r3 stage6-freeze-20261023-r4; do
  printf '%-32s type=%s deref=%s\n' "$t" "$(git cat-file -t "refs/tags/$t" 2>&1)" "$(git rev-parse "$t^{commit}" 2>&1)"
done
echo "--- ancestry F4->G4->F5->G5->G5b ---"
for pair in "$F4 $G4" "$G4 $F5" "$F5 $G5" "$G5 $G5b"; do
  set -- $pair
  if git merge-base --is-ancestor "$1" "$2"; then echo "OK ancestor: $1 -> $2"; else echo "FAIL not ancestor: $1 -> $2"; fi
done
echo "--- first-parent log F4..G5b ---"
git log --oneline --first-parent "$F4..$G5b"
echo "=== done exit 0 ==="