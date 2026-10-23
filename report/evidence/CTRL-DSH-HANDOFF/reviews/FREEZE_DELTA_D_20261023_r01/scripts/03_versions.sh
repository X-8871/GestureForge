#!/bin/bash
# 版本令牌与参数数值核对；$1 = 仓库路径
set -u
REPO="${1:-/d/codex-worktrees/w6}"
cd "$REPO" || exit 2
F4=6b8e5f2a23ce6f7dec41fc9992141b3423612081
F5=caa9728af84b0a5b79bed17427eec0091b922923
J=docs/stage6/s6a_stage6_g0_behavior_v1.json
D=docs/stage6/S6A_stage6_g0_behavior_spec_v1.md
echo "=== artifact_version @F5 ==="
git show "$F5:$J" | grep -n 'artifact_version'
echo "=== artifact_version @F4 ==="
git show "$F4:$J" | grep -n 'artifact_version'
echo "=== v1.9 / v1.8 tokens @F5 json ==="
git show "$F5:$J" | grep -n 'v1\.9\|v1\.8' || echo "(none)"
echo "=== doc line1 @F5 ==="
git show "$F5:$D" | sed -n '1,3p'
echo "=== STATE v1.9/v1.8 @F5 ==="
git show "$F5:.codex/STATE.md" | grep -n 'v1\.9\|v1\.8' | head || echo "(none)"
echo "=== S6-B r06 evidence version mentions ==="
git show "$F5:report/evidence/S6-B/s6b_core_20261023_r06/delivery_manifest.json" | grep -n 'S6A-G0-v1' | head
echo "=== S6-A r11 evidence version mentions ==="
git show "$F5:report/evidence/S6-A/s6a_g0_20261023_r11/delivery_manifest.json" | grep -n 'S6A-G0-v1' | head
echo "=== done ==="