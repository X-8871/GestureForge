#!/bin/bash
# 运行 04 参数数值抽验并在文件内记录真实退出码
R=/d/FPGA_Competition/tmp/review/FREEZE_DELTA_D_20261023_r01
cd "$R" || exit 2
python -B "$R/scripts/04_param_values.py" /d/codex-worktrees/w6 "$R/04_param_values.json"
code=$?
echo "REAL_EXIT_CODE=$code"
exit $code