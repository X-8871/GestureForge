#!/bin/bash
# 增量范围核对：只允许列出的类别发生改动；参数：$1 = 仓库路径
set -u
REPO="${1:-/d/codex-worktrees/w6}"
cd "$REPO" || exit 2
F4=6b8e5f2a23ce6f7dec41fc9992141b3423612081
F5=caa9728af84b0a5b79bed17427eec0091b922923
echo "=== 6b8e5f2a..F5 name-status ==="
git diff --name-status "$F4" "$F5"
echo "=== F5..G5b name-status ==="
git diff --name-status "$F5" c7ae6b4991bc769bdbd9683036a3c210b153c620
echo "=== 6b8e5f2a..F5 source/documented diff (code+spec only) ==="
git diff "$F4" "$F5" -- src/stage6/s6_params.py verification/ docs/stage6/
echo "=== behavior json: keys touched ==="
git diff "$F4" "$F5" -- docs/stage6/s6a_stage6_g0_behavior_v1.json | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | sed -E 's/^([+-])\s*/\1 /' | head -80
echo "=== r10/r05 in-place rewrite check (expect empty) ==="
git diff "$F4" "$F5" -- report/evidence/S6-A/s6a_g0_20261023_r10 report/evidence/S6-B/s6b_core_20261023_r05
echo "=== (exit of that diff) $? ==="
echo "=== done ==="