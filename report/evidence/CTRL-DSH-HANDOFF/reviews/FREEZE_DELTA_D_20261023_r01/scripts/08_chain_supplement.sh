#!/bin/bash
# 链完整性补充：旧哈希可达性、reflog amend 轨迹、r10_selfproof 变更内容、工作区洁净
set -u
W6=/d/codex-worktrees/w6
CLONE=/d/FPGA_Competition/tmp/review/FREEZE_DELTA_D_20261023_r01/clone/w6_transport
cd "$W6" || exit 2
echo "=== 工作区状态（w6） ==="
git status --short; echo "[status 输出结束]"
echo "=== 旧引用提交在传输克隆中的可达性 ==="
cd "$CLONE" || exit 2
for h in 33b1fee30af1974560fa0b94bf6c6662d3e5d1e0 \
         efb9f191c67fff307366f9552059ba7a5720b477 \
         1e2a66c904b15ed7e8a01206c3c2fe4a43dc760e \
         8ecd92cb35a34c29fc9570d5fcbed955f2063fd8 \
         1839766883436f521383f5432446eb67a01ada56 ; do
  printf '%s -> %s\n' "${h:0:8}" "$(git cat-file -t "$h" 2>&1)"
done
echo "=== 被 amend 取代的中间提交是否仍存在（历史，不影响引用） ==="
for h in 66f45dd aabce4c 05126fd 43f7995; do
  printf '%s -> %s\n' "$h" "$(git cat-file -t "$h" 2>&1)"
done
echo "=== reflog：F4/G4/F5/G5/G5b 是否出现 amend ==="
cd "$W6" || exit 2
git reflog --date=iso -n 30 | grep -E '6b8e5f2a|f5b749ed|caa9728a|61caac0d|c7ae6b49'
echo "=== reflog 中全部 amend 条目（历史，供对照） ==="
git reflog --date=iso -n 40 | grep -n 'amend' || echo "(无)"
echo "=== F4..F5 对 r10_selfproof / r05_selfproof 的实际改动（+/- 行） ==="
git diff 6b8e5f2a caa9728a -- report/evidence/S6-A/s6a_g0_20261023_r10_selfproof/export_selfproof.json | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | cut -c1-160
echo "=== F4..F5 r05_selfproof 改动（+/- 行） ==="
git diff 6b8e5f2a caa9728a -- report/evidence/S6-B/s6b_core_20261023_r05_selfproof/ | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | cut -c1-160
echo "=== done ==="