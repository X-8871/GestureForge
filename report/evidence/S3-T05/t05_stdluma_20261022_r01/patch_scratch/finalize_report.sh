#!/usr/bin/env bash
# 本轮构建（RunId t04_stdluma_20261022_r01，Vivado 已 exit 0）的**证据清单补生成**脚本。
#
# 背景：启动器本身成功（位流+XSA+时序+DRC+网表查询全部产出），但其内联证据生成器因
# 漏导出 ILA_BRANCH/ILA_VENDOR 抛 KeyError，build_report.json 未写出。启动器已修好该导出；
# 本脚本用**同一份生成器代码**（从修好的启动器里抽取的 make_build_report.py）补齐本次清单，
# 参数从 launcher_console.log / patch_git_apply.log 如实恢复：不重新构建、不重跑 RunId、
# 不改动任何 tmp/ 产物、不上板。
set -u

WT="D:/codex-worktrees/dbdf"
RUN_NAME="t04_stdluma_20261022_r01"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
EVID="$WT/report/evidence/S3-T05/t05_stdluma_20261022_r01"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
RTL_REL="my_ip/ov5640_ip/src/alinx_ov5640.v"
CONSOLE="$EVID/launcher_console.log"
PLOG="$EVID/patch_git_apply.log"
OOC_DCP="$RUN_DIR/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0.dcp"
OOC_RUN_LOG="$RUN_DIR/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/runme.log"
GEN="$EVID/make_build_report.py"

[ -f "$CONSOLE" ] || { echo "FAIL=console_missing"; exit 3; }
[ -f "$PLOG" ] || { echo "FAIL=patch_log_missing"; exit 3; }
[ -f "$GEN" ] || { echo "FAIL=generator_missing"; exit 3; }

c() { grep -m1 "^$1=" "$CONSOLE" | cut -d= -f2- ; }
p() { grep -m1 "^$1=" "$PLOG" | cut -d= -f2- ; }

export EVID RUN_DIR RUN_NAME RTL_REL VENDOR
export ILA_BRANCH="$(c BASELINE_BRANCH)"
export ILA_COMMIT="$(c BASELINE_COMMIT)"
export ILA_VENDOR="$VENDOR"
export ILA_EXIT_CODE="$(c VIVADO_EXIT)"
export ILA_ELAPSED="$(c ELAPSED_SECONDS)"
export ILA_CMD="$(grep -m1 '^CMD=.*vivado' "$CONSOLE" | cut -d= -f2-)"
export ILA_NETS_RC="$(c NETS_QUERY_EXIT | awk '{print $1}')"
export ILA_NETS_TIMEOUT="$(grep -m1 '^NETS_QUERY_EXIT=' "$CONSOLE" | sed 's/.*NETS_QUERY_TIMEOUT=\([0-9]*\).*/\1/')"
export ILA_NETS_OUT="$EVID/stdluma_ooc_nets.txt"
export ILA_NETS_LOG="$EVID/stdluma_ooc_nets.log"
export ILA_NETS_TCL="$EVID/check_stdluma_ooc_nets.tcl"
export ILA_NETS_TIMEOUT_SECONDS="1500"
export ILA_OOC_DCP="$OOC_DCP"
export ILA_OOC_RUN_LOG="$OOC_RUN_LOG"
export ILA_PATCH_SOF="$WT/board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
export ILA_PATCH_STDLUMA="$WT/board/stage3/software/sensor/alinx_ov5640_stdluma_gray.patch"
export ILA_XDC="$WT/board/stage3/hardware/an5642_j11_cmos2.xdc"
export ILA_LICENSE="D:/Xilinx_licenses/basic_only.lic"
export ILA_PATCH_SOF_SHA="$(sha256sum "$ILA_PATCH_SOF" | awk '{print $1}')"
export ILA_PATCH_STDLUMA_SHA="$(sha256sum "$ILA_PATCH_STDLUMA" | awk '{print $1}')"
export ILA_XDC_SHA="$(sha256sum "$ILA_XDC" | awk '{print $1}')"
export ILA_RTL_PRISTINE_SHA="$(sha256sum "$VENDOR/$RTL_REL" | awk '{print $1}')"
export ILA_RTL_AFTER_SOF_SHA="$(p RTL_AFTER_SOF_SHA256)"
export ILA_RTL_AFTER_BOTH_SHA="$(p RTL_AFTER_BOTH_SHA256)"
export ILA_SOF_CHECK_RC="$(p SOF_CHECK_RC)"
export ILA_SOF_APPLY_RC="$(p SOF_APPLY_RC)"
export ILA_STDLUMA_CHECK_RC="$(p STDLUMA_CHECK_RC)"
export ILA_STDLUMA_APPLY_RC="$(p STDLUMA_APPLY_RC)"

echo "RESTORED_FROM_LOGS:"
echo "  ILA_EXIT_CODE=$ILA_EXIT_CODE ILA_ELAPSED=$ILA_ELAPSED"
echo "  ILA_BRANCH=$ILA_BRANCH"
echo "  ILA_NETS_RC=$ILA_NETS_RC ILA_NETS_TIMEOUT=$ILA_NETS_TIMEOUT"
echo "  ILA_PATCH_STDLUMA_SHA=$ILA_PATCH_STDLUMA_SHA"
echo "  ILA_RTL_PRISTINE_SHA=$ILA_RTL_PRISTINE_SHA"
echo "  ILA_RTL_AFTER_SOF_SHA=$ILA_RTL_AFTER_SOF_SHA"
echo "  ILA_RTL_AFTER_BOTH_SHA=$ILA_RTL_AFTER_BOTH_SHA"
echo "  ILA_XDC_SHA=$ILA_XDC_SHA"
echo "  RC sof=$ILA_SOF_CHECK_RC/$ILA_SOF_APPLY_RC stdluma=$ILA_STDLUMA_CHECK_RC/$ILA_STDLUMA_APPLY_RC"
echo "  ILA_CMD=$ILA_CMD"

# 交叉核对：日志里记录的补丁/XDC 哈希必须与磁盘现值一致
for pair in "PATCH_SOF_SHA256:$ILA_PATCH_SOF_SHA" "PATCH_STDLUMA_SHA256:$ILA_PATCH_STDLUMA_SHA" "XDC_SHA256:$ILA_XDC_SHA"; do
  k="${pair%%:*}"; v="${pair##*:}"
  logged="$(c "$k")"
  if [ "$logged" != "$v" ]; then echo "FAIL=sha_mismatch_$k logged=$logged disk=$v"; exit 4; fi
done
echo "CROSS_CHECK_SHAS_MATCH_DISK=1"

python -B "$GEN" || { echo "FAIL=generator_rc"; exit 4; }
echo "FINALIZE_DONE=1"
exit 0