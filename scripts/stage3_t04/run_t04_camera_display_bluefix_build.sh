#!/usr/bin/env bash
# 显示蓝色高五位的近似重建：仅供主控启动全新运行，不恢复真实丢位。
# 用法：bash scripts/stage3_t04/run_t04_camera_display_bluefix_build.sh [t04_display_bluefix_20261021_r01]
# 可用 PYTHON 显式指定解释器；新运行设置同一设计的 OOC 并发为 1。
# 资源默认物理 2048 MiB、提交 8192 MiB；S3_MIN_AVAILABLE_MB/S3_MIN_COMMIT_MB 可显式覆盖。
# 退出码：资源不足为 4，启动器参数或路径错误为 3，检查失败为 2；构建失败保留工具退出码。
set -euo pipefail

fail() { printf 'FAIL=%s\n' "$1" >&2; exit 3; }
[[ $# -le 1 ]] || fail '只接受一个 run_name'
RUN_NAME="${1:-t04_display_bluefix_20261021_r01}"
[[ "$RUN_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$ ]] || fail 'run_name 必须是简单标识符'
[[ "$RUN_NAME" == t04_display_bluefix_20261021_r01 ]] || fail '本任务仅允许指定的新 RunId'

WT='D:/codex-worktrees/dbdf'
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
EVID="$WT/report/evidence/S3-T05/t05_display_bluefix_20261021_r01"
CHECKER="$WT/scripts/stage3_t04/check_display_bluefix.py"
TCL="$WT/scripts/stage3_t04/build_t04_camera.tcl"
VIVADO='D:/Xilinx/2026.1/Vivado/bin/vivado'
LIC='D:/Xilinx_licenses/basic_only.lic'
PYTHON="${PYTHON:-C:/Users/22061/AppData/Local/Programs/Python/Python312/python.exe}"
[[ -f "$PYTHON" && -x "$PYTHON" ]] || fail 'Python 路径不可执行，请显式指定 PYTHON'
[[ -f "$VIVADO" && -x "$VIVADO" ]] || fail 'Vivado 路径不可执行'
[[ -f "$LIC" ]] || fail '基本许可路径不存在'
export PYTHONIOENCODING=utf-8
export S3_BUILD_JOBS=1

# 所有预检只读，拒绝复用已有目录或覆盖旧证据；原子 mkdir 再次拒绝竞争。
"$PYTHON" -X utf8 -I -B "$CHECKER" --preflight --run-name "$RUN_NAME"
mkdir "$RUN_DIR"
mkdir "$EVID"
mkdir "$RUN_DIR/temp"
export TEMP="$RUN_DIR/temp"
export TMP="$RUN_DIR/temp"
export TMPDIR="$RUN_DIR/temp"
export VMCP_AUTOSTART=0
export VMCP_LOGFILE="$RUN_DIR/vmcp.txt"
cd "$RUN_DIR"

# 准备失败立即退出；补丁逐个 --check 和实际应用，输入/副本文件逐一绑定哈希。
"$PYTHON" -X utf8 -I -B "$CHECKER" --prepare --run-name "$RUN_NAME"
sha256sum "$VIVADO" > "$RUN_DIR/vivado_launcher_sha256.txt"
"$PYTHON" -X utf8 -I -B "$CHECKER" --check-heavy | tee "$RUN_DIR/resource_preflight.txt"
printf 'RUN_DIR=%s\nEVIDENCE=%s\n' "$RUN_DIR" "$EVID"

# 许可仅向本次进程及其子进程注入路径，不读取或输出许可文件内容。
# 管道失败保留真实 Vivado 退出码；tee 失败同样禁止报告成功。
if env XILINXD_LICENSE_FILE="$LIC" LM_LICENSE_FILE="$LIC" \
    "$VIVADO" -mode batch -source "$TCL" \
    -log "$RUN_DIR/vivado.log" -journal "$RUN_DIR/vivado.jou" \
    -tclargs "$RUN_DIR" "$RUN_DIR/vendor_src" 2>&1 | tee "$RUN_DIR/console.txt"; then
    pipeline_status=(0 0)
else
    pipeline_status=("${PIPESTATUS[@]}")
fi
rc="${pipeline_status[0]}"
console_rc="${pipeline_status[1]}"
printf 'VIVADO_EXIT=%s\nCONSOLE_EXIT=%s\n' "$rc" "$console_rc"
if "$PYTHON" -X utf8 -I -B "$CHECKER" --finalize --run-name "$RUN_NAME" \
    --exit-code "$rc" --console-exit-code "$console_rc"; then
    exit "$rc"
else
    final_rc=$?
    [[ "$rc" -ne 0 ]] && exit "$rc"
    exit "$final_rc"
fi
