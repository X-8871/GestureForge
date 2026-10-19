#!/usr/bin/env bash
# 阶段3 Git Bash 启动器：调用 Vivado 2026.1 自带的 Tcl 版 xsdb（Vitis 2026.1 的 xsct 已禁用）。
# 用法: bash run_xsdb.sh <tcl脚本绝对路径> [脚本参数...]
set -u

SCRIPT="${1:?需要 tcl 脚本路径}"
shift || true

export XILINXD_LICENSE_FILE="D:/Xilinx_licenses/basic_only.lic"
XSDB='D:\Xilinx\2026.1\Vivado\bin\xsdb.bat'

echo "XSDB_LAUNCHER=$XSDB"
echo "XSDB_SCRIPT=$SCRIPT"

cmd //c "$XSDB" "$SCRIPT" "$@"
rc=$?
echo "XSDB_EXIT=$rc"
exit "$rc"