#!/bin/bash
# 最终取证：规格文档残留"待批准"与历史修订记录被改写的行号；证据包内 PENDING 语句行号
set -u
cd /d/codex-worktrees/w6 || exit 2
D=docs/stage6/S6A_stage6_g0_behavior_spec_v1.md
echo "=== 规格文档：残留 待批准/不是已批准 行号 ==="
grep -n '待批准\|不是已批准' "$D"
echo "=== 规格文档：APPROVED_20261023 出现的行号（含历史修订记录） ==="
grep -n 'APPROVED_20261023' "$D"
echo "=== 规格文档：历史修订记录中被改成 APPROVED 的行（逐条） ==="
grep -n '^> .*APPROVED_20261023' "$D" | cut -c1-200
echo "=== r11 证据：PENDING 语句（行号） ==="
grep -rn 'PENDING_APPROVAL' report/evidence/S6-A/s6a_g0_20261023_r11/ | grep -v 'approval_regression\|claim_verification\|probe_\|selfcheck_' | cut -c1-220
echo "=== r06 证据：PENDING 语句（行号） ==="
grep -rn 'PENDING_APPROVAL' report/evidence/S6-B/s6b_core_20261023_r06/ | grep -v 'probe/\|cases/' | cut -c1-220
echo "=== r06 params_snapshot 关键布尔 ==="
grep -n 'all_parameters_pending_approval\|thresholds_are_draft_not_approved\|behavior_status\|behavior_artifact_version' report/evidence/S6-B/s6b_core_20261023_r06/params_snapshot.json
echo "=== s6b_run_cases.py 对应字段 ==="
grep -n 'parameters_pending_approval\|all_parameters_pending' verification/s6b_run_cases.py src/stage6/s6_params.py
echo "=== 规格文档 §14 表首行与标题 ==="
sed -n '278,284p' "$D"
echo "=== done ==="