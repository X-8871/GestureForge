#!/usr/bin/env bash
# =============================================================================
# 阶段3 S3-T05-PL5「标准亮度灰度」启动器
#
# 变体：SOF 补丁 + 标准亮度灰度补丁（alinx_ov5640_stdluma_gray.patch）+ J11/CMOS2 约束
#   Y = (77*R8 + 150*G8 + 29*B8) >> 8   （0.299R + 0.587G + 0.114B 的整数近似）
#   新字 = {Y[7:3], Y[7:2], Y[7:3]}     （R5=B5=Y>>3、G6=Y>>2）
#   *** 灰度补偿、非修复 ***：蓝通道 MSB 仍是「猜」出来的（B'[4]=B[3]）且继续参与亮度，
#   模块侧坏线 cmos_d[9] 未修 ⇒ 本位流不得用于颜色验收，真实修复仍需硬件返修。
#
# 流程：复制 vendor_src -> git apply SOF -> git apply 标准亮度灰度 -> 覆盖
#       an5642_j11_cmos2.xdc -> 构建 bitstream+XSA -> 收集证据
#
# 用法: bash run_t04_camera_j11cmos2_stdluma_build.sh [run_name]
#   默认 run_name = t04_stdluma_20261022_r01  (RunId = tmp/s3r06/<run_name>，已存在则拒绝)
#
# 边界：只写 tmp/s3r06/<run_name>/** 与本证据目录；不上板/不下载/不烧 QSPI/不提交 Git。
# 证据：只做**有界**检查（RTL 标记 + OOC 网表一次过滤查询），不做逐位网表回溯。
# =============================================================================
set -u

RUN_NAME="${1:-t04_stdluma_20261022_r01}"

WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
SRC_COPY="$RUN_DIR/vendor_src"
XDC_IN="$WT/board/stage3/hardware/an5642_j11_cmos2.xdc"
PATCH_SOF="$WT/board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
PATCH_STDLUMA="$WT/board/stage3/software/sensor/alinx_ov5640_stdluma_gray.patch"
PATCH_DUAL="$WT/board/stage3/software/sensor/alinx_ov5640_dual_msb_rebuild.patch"
PATCH_BLUE="$WT/board/stage3/software/sensor/alinx_ov5640_blue_msb_rebuild.patch"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
TCL="$WT/scripts/stage3_t04/build_t04_camera.tcl"
EVID="$WT/report/evidence/S3-T05/t05_stdluma_20261022_r01"
NETS_TCL="$EVID/check_stdluma_ooc_nets.tcl"
LIC="D:/Xilinx_licenses/basic_only.lic"
RTL_REL="my_ip/ov5640_ip/src/alinx_ov5640.v"

# 由 patch_scratch/make_stdluma_patch.sh 干跑预计算（确定性，重复生成同值）
RTL_SHA_PRISTINE="98260b62f996ec700eb766c6c4e57706b2c1ff3a8224a5105a3641b6475b3e4d"
RTL_SHA_AFTER_SOF="db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6"
RTL_SHA_AFTER_BOTH="2a98dcb2eed1fbe698fbb4cfbf986e838a7c1d6635eb019442444bed3e71176d"
PATCH_SOF_SHA="fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5"
PATCH_STDLUMA_SHA="1e667e7f2594f507d48f5d1e0bd70ccfe11dd42e35bf1a9c4e0a788be5c34460"
NETS_TIMEOUT_SECONDS="1500"

export XILINXD_LICENSE_FILE="$LIC"

echo "LAUNCHER=gitbash"
echo "VARIANT=PL_STANDARD_LUMA_GRAY"
echo "RUN_NAME=$RUN_NAME"
echo "RUN_DIR=$RUN_DIR"
echo "EVID=$EVID"
echo "PATCH_SOF=$PATCH_SOF"
echo "PATCH_STDLUMA=$PATCH_STDLUMA"
echo "XDC_IN=$XDC_IN"
echo "LICENSE=$XILINXD_LICENSE_FILE"

TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
[ "$TOP" = "$WT" ] || { echo "FAIL=worktree_selfcheck:$TOP"; exit 3; }
[ -e "$RUN_DIR" ] && { echo "FAIL=run_dir_exists:$RUN_DIR"; exit 3; }
[ -d "$VENDOR" ] || { echo "FAIL=vendor_missing"; exit 3; }
[ -f "$XDC_IN" ] || { echo "FAIL=xdc_missing"; exit 3; }
[ -f "$PATCH_SOF" ] || { echo "FAIL=patch_sof_missing"; exit 3; }
[ -f "$PATCH_STDLUMA" ] || { echo "FAIL=patch_stdluma_missing"; exit 3; }
[ -f "$NETS_TCL" ] || { echo "FAIL=nets_tcl_missing"; exit 3; }
[ -f "$TCL" ] || { echo "FAIL=tcl_missing"; exit 3; }
[ -f "$LIC" ] || { echo "FAIL=license_missing"; exit 3; }

COMMIT="$(git -C "$WT" rev-parse HEAD)"
BRANCH="$(git -C "$WT" rev-parse --abbrev-ref HEAD)"
SOF_SHA_ACTUAL="$(sha256sum "$PATCH_SOF" | awk '{print $1}')"
STDLUMA_SHA_ACTUAL="$(sha256sum "$PATCH_STDLUMA" | awk '{print $1}')"
XDC_SHA="$(sha256sum "$XDC_IN" | awk '{print $1}')"
echo "BASELINE_COMMIT=$COMMIT"
echo "BASELINE_BRANCH=$BRANCH"
echo "PATCH_SOF_SHA256=$SOF_SHA_ACTUAL"
echo "PATCH_STDLUMA_SHA256=$STDLUMA_SHA_ACTUAL"
echo "XDC_SHA256=$XDC_SHA"
[ "$SOF_SHA_ACTUAL" = "$PATCH_SOF_SHA" ] || { echo "FAIL=sof_patch_sha_mismatch"; exit 4; }
[ "$STDLUMA_SHA_ACTUAL" = "$PATCH_STDLUMA_SHA" ] || { echo "FAIL=stdluma_patch_sha_mismatch"; exit 4; }

RUNNING="$( (tasklist //FI "IMAGENAME eq vivado.exe" //NH 2>/dev/null; tasklist //FI "IMAGENAME eq xsim.exe" //NH 2>/dev/null) | grep -ci 'vivado.exe\|xsim.exe' )"
echo "EXISTING_VIVADO_XSIM_PROCS=$RUNNING"
[ "$RUNNING" = "0" ] || { echo "FAIL=heavy_task_already_running:$RUNNING"; exit 3; }

mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir_run_dir"; exit 3; }
mkdir -p "$EVID" || { echo "FAIL=mkdir_evid"; exit 3; }

# ---- 1) vendor 副本 + 依次应用 SOF 与标准亮度灰度补丁（不叠加 dual/blue） --------
cp -r "$VENDOR" "$SRC_COPY" || { echo "FAIL=vendor_copy"; exit 3; }
PRISTINE_ACTUAL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
echo "RTL_PRISTINE_SHA256=$PRISTINE_ACTUAL"
[ "$PRISTINE_ACTUAL" = "$RTL_SHA_PRISTINE" ] || { echo "FAIL=pristine_rtl_hash_mismatch:$PRISTINE_ACTUAL"; exit 4; }

REL_SRC="tmp/s3r06/$RUN_NAME/vendor_src"
(
  cd "$WT" || exit 3
  echo "== patch 1/2: SOF (HREF-gap frame start) =="
  echo "CMD=git apply --check -p1 --directory=$REL_SRC $PATCH_SOF"
  git apply --check -p1 --directory="$REL_SRC" "$PATCH_SOF"; echo "SOF_CHECK_RC=$?"
  echo "CMD=git apply -p1 --directory=$REL_SRC $PATCH_SOF"
  git apply -p1 --directory="$REL_SRC" "$PATCH_SOF"; echo "SOF_APPLY_RC=$?"
  echo "RTL_AFTER_SOF_SHA256=$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
  echo "== patch 2/2: STANDARD-LUMA GRAY =="
  echo "CMD=git apply --check -p1 --directory=$REL_SRC $PATCH_STDLUMA"
  git apply --check -p1 --directory="$REL_SRC" "$PATCH_STDLUMA"; echo "STDLUMA_CHECK_RC=$?"
  echo "CMD=git apply -p1 --directory=$REL_SRC $PATCH_STDLUMA"
  git apply -p1 --directory="$REL_SRC" "$PATCH_STDLUMA"; echo "STDLUMA_APPLY_RC=$?"
  echo "RTL_AFTER_BOTH_SHA256=$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
) > "$EVID/patch_git_apply.log" 2>&1
cat "$EVID/patch_git_apply.log"
get_rc() { grep -m1 "^$1=" "$EVID/patch_git_apply.log" | cut -d= -f2; }
SOF_CHECK_RC="$(get_rc SOF_CHECK_RC)"; SOF_APPLY_RC="$(get_rc SOF_APPLY_RC)"
STDLUMA_CHECK_RC="$(get_rc STDLUMA_CHECK_RC)"; STDLUMA_APPLY_RC="$(get_rc STDLUMA_APPLY_RC)"
FINAL_RTL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
echo "SOF_CHECK_RC=$SOF_CHECK_RC SOF_APPLY_RC=$SOF_APPLY_RC STDLUMA_CHECK_RC=$STDLUMA_CHECK_RC STDLUMA_APPLY_RC=$STDLUMA_APPLY_RC"
echo "RTL_FINAL_SHA256=$FINAL_RTL"
if [ "$SOF_CHECK_RC" != "0" ] || [ "$SOF_APPLY_RC" != "0" ] || [ "$STDLUMA_CHECK_RC" != "0" ] || [ "$STDLUMA_APPLY_RC" != "0" ]; then
  echo "FAIL=patch_application_rc:$SOF_CHECK_RC/$SOF_APPLY_RC/$STDLUMA_CHECK_RC/$STDLUMA_APPLY_RC"; exit 4
fi
[ "$FINAL_RTL" = "$RTL_SHA_AFTER_BOTH" ] || { echo "FAIL=final_rtl_hash_mismatch:$FINAL_RTL"; exit 4; }
grep -q "GAP_THRESH" "$SRC_COPY/$RTL_REL" || { echo "FAIL=sof_marker_missing"; exit 4; }
grep -q "s_axis_tdata_stdluma" "$SRC_COPY/$RTL_REL" || { echo "FAIL=stdluma_marker_missing"; exit 4; }
grep -q "stdluma_luma32" "$SRC_COPY/$RTL_REL" || { echo "FAIL=stdluma_luma_marker_missing"; exit 4; }
for marker in s_axis_tdata_dualmsb s_axis_tdata_bluefix gray_g2_maj; do
  if grep -q "$marker" "$SRC_COPY/$RTL_REL"; then
    echo "FAIL=residual_patch_marker_present:$marker"; exit 4
  fi
done
echo "PATCHES_VERIFIED=1 OLD_PATCH_MARKERS_ABSENT=1"
cp -f "$PATCH_SOF" "$EVID/alinx_ov5640_sof_hrefgap.patch"
cp -f "$PATCH_STDLUMA" "$EVID/alinx_ov5640_stdluma_gray.patch"
[ -f "$PATCH_DUAL" ] && cp -f "$PATCH_DUAL" "$EVID/alinx_ov5640_dual_msb_rebuild_not_applied.patch" || true
[ -f "$PATCH_BLUE" ] && cp -f "$PATCH_BLUE" "$EVID/alinx_ov5640_blue_msb_rebuild_not_applied.patch" || true
cp -f "$SRC_COPY/$RTL_REL" "$EVID/alinx_ov5640_stdluma_patched.v"

# ---- 2) J11+CMOS2 约束 -------------------------------------------------------
cp "$XDC_IN" "$SRC_COPY/src/constraints/an5642.xdc" || { echo "FAIL=xdc_replace"; exit 3; }
for pin in F17 F16 F19 L19 K19; do
  grep -q "$pin" "$SRC_COPY/src/constraints/an5642.xdc" || { echo "FAIL=pin_not_found:$pin"; exit 3; }
done
echo "CMOS2_PINS_VERIFIED=1"

# ---- 3) 构建 bitstream + XSA -------------------------------------------------
CMD="$VIVADO -mode batch -source $TCL -log $RUN_DIR/vivado.log -journal $RUN_DIR/vivado.jou -tclargs $RUN_DIR $SRC_COPY"
echo "CMD=$CMD"
START_EPOCH=$(date +%s)
"$VIVADO" -mode batch -source "$TCL" \
  -log "$RUN_DIR/vivado.log" -journal "$RUN_DIR/vivado.jou" \
  -tclargs "$RUN_DIR" "$SRC_COPY"
rc=$?
END_EPOCH=$(date +%s)
ELAPSED=$((END_EPOCH - START_EPOCH))
echo "VIVADO_EXIT=$rc"
echo "ELAPSED_SECONDS=$ELAPSED"

# ---- 4) 有界网表佐证：只对 OOC DCP 做一次过滤查询（不做逐位回溯） --------------
OOC_DCP="$RUN_DIR/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0.dcp"
NETS_OUT="$EVID/stdluma_ooc_nets.txt"
NETS_LOG="$EVID/stdluma_ooc_nets.log"
nets_rc=9; nets_timeout=0
echo "OOC_DCP=$OOC_DCP EXISTS=$([ -f "$OOC_DCP" ] && echo 1 || echo 0)"
if [ -f "$OOC_DCP" ]; then
  if command -v timeout >/dev/null 2>&1; then
    timeout "$NETS_TIMEOUT_SECONDS" "$VIVADO" -mode batch -source "$NETS_TCL" -log "$NETS_LOG" \
      -journal "$EVID/stdluma_ooc_nets.jou" -tclargs "$OOC_DCP" "$NETS_OUT"
    nets_rc=$?
    [ "$nets_rc" = "124" ] && nets_timeout=1
  else
    "$VIVADO" -mode batch -source "$NETS_TCL" -log "$NETS_LOG" \
      -journal "$EVID/stdluma_ooc_nets.jou" -tclargs "$OOC_DCP" "$NETS_OUT"
    nets_rc=$?
  fi
fi
echo "NETS_QUERY_EXIT=$nets_rc NETS_QUERY_TIMEOUT=$nets_timeout"
[ -f "$NETS_OUT" ] && cat "$NETS_OUT" || echo "NETS_OUT_MISSING=1"

# ---- 5) 证据留存 -------------------------------------------------------------
cp -f "$RUN_DIR/vivado.log" "$EVID/vivado.log" 2>/dev/null || true
cp -f "$RUN_DIR/vivado.jou" "$EVID/vivado.jou" 2>/dev/null || true
for f in "$RUN_DIR"/report_*.rpt; do [ -f "$f" ] && cp -f "$f" "$EVID/$(basename "$f")" || true; done
OOC_RUN_LOG="$RUN_DIR/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/runme.log"
[ -f "$OOC_RUN_LOG" ] && cp -f "$OOC_RUN_LOG" "$EVID/alinx_ov5640_ooc_synth_runme.log" || true

export EVID RUN_DIR RUN_NAME COMMIT BRANCH VENDOR RTL_REL
export ILA_BRANCH="$BRANCH" ILA_VENDOR="$VENDOR" ILA_COMMIT="$COMMIT"
export ILA_EXIT_CODE="$rc" ILA_ELAPSED="$ELAPSED" ILA_CMD="$CMD"
export ILA_NETS_RC="$nets_rc" ILA_NETS_TIMEOUT="$nets_timeout" ILA_NETS_OUT="$NETS_OUT"
export ILA_NETS_LOG="$NETS_LOG" ILA_NETS_TCL="$NETS_TCL" ILA_NETS_TIMEOUT_SECONDS="$NETS_TIMEOUT_SECONDS"
export ILA_OOC_DCP="$OOC_DCP" ILA_OOC_RUN_LOG="$OOC_RUN_LOG"
export ILA_PATCH_SOF="$PATCH_SOF" ILA_PATCH_SOF_SHA="$SOF_SHA_ACTUAL"
export ILA_PATCH_STDLUMA="$PATCH_STDLUMA" ILA_PATCH_STDLUMA_SHA="$STDLUMA_SHA_ACTUAL"
export ILA_XDC="$XDC_IN" ILA_XDC_SHA="$XDC_SHA" ILA_LICENSE="$XILINXD_LICENSE_FILE"
export ILA_RTL_PRISTINE_SHA="$RTL_SHA_PRISTINE" ILA_RTL_AFTER_SOF_SHA="$RTL_SHA_AFTER_SOF"
export ILA_RTL_AFTER_BOTH_SHA="$RTL_SHA_AFTER_BOTH"
export ILA_SOF_CHECK_RC="$SOF_CHECK_RC" ILA_SOF_APPLY_RC="$SOF_APPLY_RC"
export ILA_STDLUMA_CHECK_RC="$STDLUMA_CHECK_RC" ILA_STDLUMA_APPLY_RC="$STDLUMA_APPLY_RC"

python -B - <<'PY'
import hashlib, json, os, re, datetime, glob

evid    = os.environ["EVID"]
run_dir = os.environ["RUN_DIR"]
rc      = int(os.environ["ILA_EXIT_CODE"])
rtl_rel = os.environ["RTL_REL"]
log     = os.path.join(run_dir, "vivado.log")

def sha256(p):
    if not os.path.isfile(p): return None
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

def rt(p):
    if not os.path.isfile(p): return ""
    with open(p, encoding="utf-8", errors="replace") as f: return f.read()

logtxt = rt(log)
m = re.search(r"Vivado v\.([0-9.]+)", logtxt)
ver = m.group(1) if m else None
peaks = [float(x) for x in re.findall(r"Memory \(MB\): peak = ([0-9.]+)", logtxt)]
peak_mb = max(peaks) if peaks else None

def t04val(key):
    m = re.search(r"^T04:\s*%s=(.*)$" % re.escape(key), logtxt, re.M)
    return m.group(1).strip() if m else None

errs  = re.findall(r"^ERROR: \[([^\]]+)\]", logtxt, re.M)
crits = re.findall(r"^CRITICAL WARNING: \[([^\]]+)\]", logtxt, re.M)
warns = re.findall(r"^WARNING: \[([^\]]+)\]", logtxt, re.M)

drc_txt = rt(os.path.join(run_dir, "report_drc_impl.rpt"))
drc_detail, drc_rules = {}, {}
for rule, num, sev in re.findall(r"^([A-Za-z0-9_-]+)#(\d+)\s+(Critical Warning|Error|Warning)\s*$", drc_txt, re.M):
    drc_detail[sev] = drc_detail.get(sev, 0) + 1
    drc_rules[rule] = drc_rules.get(rule, 0) + 1

def slice_regs(path):
    txt = rt(path)
    m = re.search(r"^\|\s*Slice Registers\s*\|\s*(\d+)\s*\|", txt, re.M)
    return int(m.group(1)) if m else None

# ---- 有界网表佐证解析（一次过滤查询的结果） -----------------------------------
nets_txt = rt(os.environ["ILA_NETS_OUT"])
def nets_val(key):
    m = re.search(r"^%s=(.*)$" % re.escape(key), nets_txt, re.M)
    return m.group(1).strip() if m else None
nets_counts = {}
for k in ("STDLUMA_CELL_COUNT", "STDLUMA_NET_COUNT", "RESIDUAL_DUALMSB_COUNT",
          "RESIDUAL_BLUEFIX_COUNT", "RESIDUAL_GRAYG2_COUNT"):
    v = nets_val(k)
    nets_counts[k] = int(v) if (v or "").lstrip("-").isdigit() else None
nets_cells = [x for x in re.findall(r"^STDLUMA_CELL=(.*)$", nets_txt, re.M)]
nets_sample = nets_val("STDLUMA_NET_SAMPLE") or ""

nets_rc = int(os.environ["ILA_NETS_RC"])
nets_timeout = os.environ["ILA_NETS_TIMEOUT"] == "1"
if not os.path.isfile(os.environ["ILA_OOC_DCP"]):
    nets_status, nets_reason = "not_done", "OOC DCP 不存在（构建未产生 IP OOC 检查点）"
elif nets_timeout:
    nets_status, nets_reason = "not_done", "OOC 网表查询超时（%s s）后终止，未重试" % os.environ["ILA_NETS_TIMEOUT_SECONDS"]
elif nets_rc != 0 or not nets_txt:
    nets_status, nets_reason = "not_done", "OOC 网表查询退出码 %d 或无输出，未重试" % nets_rc
else:
    nets_status, nets_reason = "done", ""

# ---- RTL 副本（工程内若存在局部副本，一并绑定哈希） ---------------------------
rtl_copies = []
for p in glob.glob(os.path.join(run_dir, "project", "**", "alinx_ov5640.v"), recursive=True):
    blob = open(p, "rb").read()
    rtl_copies.append({
        "path": p, "sha256": sha256(p), "size_bytes": os.path.getsize(p),
        "matches_expected": sha256(p) == os.environ["ILA_RTL_AFTER_BOTH_SHA"],
        "contains_gap_thresh": b"GAP_THRESH" in blob,
        "contains_stdluma_marker": b"s_axis_tdata_stdluma" in blob,
        "contains_dualmsb_marker": b"s_axis_tdata_dualmsb" in blob,
        "contains_bluefix_marker": b"s_axis_tdata_bluefix" in blob,
        "contains_gray_g2_marker": b"gray_g2_maj" in blob,
    })

bit = os.path.join(run_dir, "project", "ov5640_single.runs", "impl_1", "design_1_wrapper.bit")
xsa = os.path.join(run_dir, "design_1_wrapper.xsa")

artifacts = {}
for name, path in (("bit", bit), ("xsa", xsa), ("vivado_log", log),
                   ("report_timing_summary_impl", os.path.join(run_dir, "report_timing_summary_impl.rpt")),
                   ("report_drc_impl", os.path.join(run_dir, "report_drc_impl.rpt")),
                   ("report_utilization_impl", os.path.join(run_dir, "report_utilization_impl.rpt")),
                   ("report_utilization_synth", os.path.join(run_dir, "report_utilization_synth.rpt")),
                   ("patched_rtl_in_run", os.path.join(run_dir, "vendor_src", rtl_rel)),
                   ("patched_rtl_in_evidence", os.path.join(evid, "alinx_ov5640_stdluma_patched.v")),
                   ("patch_sof", os.environ["ILA_PATCH_SOF"]),
                   ("patch_stdluma", os.environ["ILA_PATCH_STDLUMA"]),
                   ("xdc_j11_cmos2", os.environ["ILA_XDC"]),
                   ("ooc_dcp", os.environ["ILA_OOC_DCP"]),
                   ("ooc_synth_runme_log", os.environ["ILA_OOC_RUN_LOG"]),
                   ("stdluma_ooc_nets_txt", os.environ["ILA_NETS_OUT"]),
                   ("stdluma_ooc_nets_log", os.environ["ILA_NETS_LOG"])):
    artifacts[name] = {"path": path, "exists": os.path.isfile(path),
                       "size_bytes": os.path.getsize(path) if os.path.isfile(path) else None,
                       "sha256": sha256(path)}

bit_ok = artifacts["bit"]["exists"] and artifacts["xsa"]["exists"]

# 结论状态：位流/XSA 是否产出与网表查询解耦（网表查询不可得时不算失败，见 limitations）
if rc == 0 and bit_ok:
    status = "ok"
elif rc != 0:
    status = "failed"
else:
    status = "incomplete_missing_artifacts"

report = {
    "task_id": "S3-T05-PL5",
    "task_board_id": "task-13",
    "title": "PL 端标准亮度灰度 Y=(77*R8+150*G8+29*B8)>>8 -> bitstream+XSA",
    "run_id": os.environ["RUN_NAME"],
    "run_dir": run_dir,
    "evidence_dir": evid,
    "generated_at_utc8": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "status": status,
    "disclaimer": ("*** 灰度补偿、非修复 ***。蓝通道 MSB 仍是猜出来的（B'[4] = B'[3] = tdata[14]）"
                   "且继续按 0.114 权重参与亮度；模块侧坏线 cmos_d[9] 未修，本变体不构成颜色正确性证据，"
                   "不得用于颜色验收；真实修复仍需硬件返修/更换模块。"),
    "tool": {"name": "Vivado", "version": ver, "mode": "batch_tcl",
             "license_file": os.environ["ILA_LICENSE"],
             "flow": "vendor BD auto_create_project (build_t04_camera.tcl)"},
    "baseline": {"worktree": "D:/codex-worktrees/dbdf", "branch": os.environ["ILA_BRANCH"],
                 "commit_at_build": os.environ["ILA_COMMIT"], "part": "xc7z020clg400-2",
                 "vendor_source": os.environ["ILA_VENDOR"], "xdc": os.environ["ILA_XDC"],
                 "xdc_sha256": os.environ["ILA_XDC_SHA"]},
    "bit_layout": {
        "word_layout": "word[15:11]=B[4:0], word[10:5]=G[5:0], word[4:0]=R[4:0]",
        "lost_bits": ["word[15] = B[4] (第一字节 MSB, cmos_d[9])",
                      "word[7] = G[2] (第二字节 MSB, 同一根 cmos_d[9])"],
    },
    "grayscale": {
        "formula": "R8={tdata[4:0],3'b000}; G'={tdata[10],tdata[9],tdata[8],maj3(tdata[8]),tdata[6],tdata[5]}; "
                   "G8={G'[5:0],2'b00}; B'={tdata[14],tdata[14],tdata[13],tdata[12],tdata[11]}（B'[4]=B'[3]）; "
                   "B8={B'[4:0],3'b000}; Y=(77*R8+150*G8+29*B8)>>8; new={Y[7:3],Y[7:2],Y[7:3]}",
        "weights": {"r": 77, "g": 150, "b": 29, "shift": 8, "sum_of_weights": 256,
                    "approx": "0.3008 / 0.5859 / 0.1133（对照 0.299 / 0.587 / 0.114）"},
        "channel_mapping": "new[15:11]=Y[7:3](B5), new[10:5]=Y[7:2](G6), new[4:0]=Y[7:3](R5)",
        "channel_reconstruction_at_display": ("B8={word[15:11],3'b000}=Y&0xF8, G8={word[10:5],2'b00}=Y&0xFC, "
                                              "R8={word[4:0],3'b000}=Y&0xF8 ⇒ 三通道差 ∈ {0,4} LSB，"
                                              "即最大 4/255（约 1.6%）；卡面写的「差 ≤1 LSB」按此公式并不精确成立，"
                                              "已在该项如实记录（不阻断，属显示级量化残差）"),
        "max_y": 250,
        "majority": ("水平 3 抽头多数 maj=(c0&c1)|(c0&c2)|(c1&c2)，只用于重建的 G'[2]；"
                     "2 个像素率延迟寄存器 + 1 个多数门，无行缓冲/BRAM；窗口因果（当前+前 2 像素），"
                     "数据流不额外延迟，tvalid/tlast/tuser 仍对齐。"),
        "b4_note": "B'[4] 按卡面确认式直接复制 B'[3]（未对 B'[4] 加多数滤波，卡面该项为可选项）。",
        "not_changed": ["tlast", "tuser", "tkeep", "tvalid/tready", "时钟/时序", "DEBUG_OV5640（保持 false）"],
    },
    "patches": {
        "applied_order": ["alinx_ov5640_sof_hrefgap.patch", "alinx_ov5640_stdluma_gray.patch"],
        "items": [
            {"name": "SOF fix (task-2)", "file": os.environ["ILA_PATCH_SOF"],
             "sha256": os.environ["ILA_PATCH_SOF_SHA"], "hunks": 3,
             "git_apply_check_rc": int(os.environ["ILA_SOF_CHECK_RC"]),
             "git_apply_rc": int(os.environ["ILA_SOF_APPLY_RC"])},
            {"name": "PL standard-luma gray (this task, S3-T05-PL5)", "file": os.environ["ILA_PATCH_STDLUMA"],
             "sha256": os.environ["ILA_PATCH_STDLUMA_SHA"], "hunks": 2, "lines_added": 49, "lines_removed": 2,
             "git_apply_check_rc": int(os.environ["ILA_STDLUMA_CHECK_RC"]),
             "git_apply_rc": int(os.environ["ILA_STDLUMA_APPLY_RC"])},
        ],
        "not_applied": ["alinx_ov5640_dual_msb_rebuild.patch（task-9，双位重建）",
                        "alinx_ov5640_blue_msb_rebuild.patch（task-6）",
                        "alinx_ov5640_gray_luma.patch（task-11，绿通道灰度，被本卡取代）"],
        "residual_marker_assertion": "启动器断言最终 RTL 不含 s_axis_tdata_dualmsb / s_axis_tdata_bluefix / gray_g2_maj（PATCHES_VERIFIED=1）。",
        "patch_dryrun": "patch_scratch/make_stdluma_patch.sh 确定性生成补丁；verify 副本上 SOF->STDLUMA 结果与本补丁生成基准逐字节相同（patch_scratch/patch_dryrun.log）。",
    },
    "rtl_hashes": {
        "pristine_vendor": os.environ["ILA_RTL_PRISTINE_SHA"],
        "after_sof_patch": os.environ["ILA_RTL_AFTER_SOF_SHA"],
        "after_sof_then_stdluma": os.environ["ILA_RTL_AFTER_BOTH_SHA"],
        "run_copy_actual": artifacts["patched_rtl_in_run"]["sha256"],
        "evidence_copy_actual": artifacts["patched_rtl_in_evidence"]["sha256"],
    },
    "netlist_confirmation": {
        "method": "一次有界过滤查询（不做逐位回溯）：open_checkpoint(OOC DCP) -> get_cells/get_nets -hier -filter {NAME =~ \"*stdluma*\"}",
        "status": nets_status,
        "reason_if_not_done": nets_reason or None,
        "query_exit_code": nets_rc,
        "timed_out": nets_timeout,
        "timeout_seconds": int(os.environ["ILA_NETS_TIMEOUT_SECONDS"]),
        "counts": nets_counts,
        "cells_found": nets_cells[:40],
        "net_name_sample": nets_sample,
        "expectation": ("IP OOC 网表里应能查到本补丁引入的 stdluma_g2_d1/d2 寄存器；"
                        "旧补丁标记 dualmsb/bluefix/gray_g2 的计数应为 0。"),
        "passed": (nets_status == "done"
                   and (nets_counts.get("STDLUMA_CELL_COUNT") or 0) >= 2
                   and (nets_counts.get("STDLUMA_NET_COUNT") or 0) >= 1
                   and (nets_counts.get("RESIDUAL_DUALMSB_COUNT") or 0) == 0
                   and (nets_counts.get("RESIDUAL_BLUEFIX_COUNT") or 0) == 0
                   and (nets_counts.get("RESIDUAL_GRAYG2_COUNT") or 0) == 0),
    },
    "rtl_evidence": {
        "run_rtl_copy": {"path": os.path.join(run_dir, "vendor_src", rtl_rel),
                         "sha256": artifacts["patched_rtl_in_run"]["sha256"],
                         "contains_gap_thresh": True, "contains_stdluma_marker": True,
                         "old_patch_markers_absent": True},
        "project_local_copies": rtl_copies,
        "meaning": "构建输入 RTL 哈希 = SOF+标准亮度灰度叠加后的字节，含 GAP_THRESH 与 s_axis_tdata_stdluma，不含 dual/blue/gray 旧补丁标记。",
    },
    "commands": {"build": os.environ["ILA_CMD"], "tcl_script": "scripts/stage3_t04/build_t04_camera.tcl",
                 "launcher": "scripts/stage3_t04/run_t04_camera_j11cmos2_stdluma_build.sh",
                 "netlist_query_tcl": os.environ["ILA_NETS_TCL"],
                 "vivado_exit_code": rc, "netlist_query_exit_code": nets_rc,
                 "elapsed_seconds": int(os.environ["ILA_ELAPSED"])},
    "implementation": {
        "synth_status": t04val("SYNTH_STATUS"), "impl_status": t04val("IMPL_STATUS"),
        "timing": {"wns_ns": t04val("TIMING_WNS"), "tns_ns": t04val("TIMING_TNS"),
                   "whs_ns": t04val("TIMING_WHS"), "ths_ns": t04val("TIMING_THS")},
        "timing_reference_runs": {
            "t04_camera_j11cmos2_20261020_r01_baseline": {"wns_ns": "1.141183", "whs_ns": "0.058332"},
            "t04_sof_fix_20261020_r01_sof_only": {"wns_ns": "1.054525", "whs_ns": "0.058931"},
            "t04_dualmsb_20261021_r01_dual_rebuild": {"wns_ns": "1.171408", "whs_ns": "0.053436"},
            "t04_gray_20261021_r01_green_luma": {"note": "task-11 产物，其网表证据未完成"},
        },
        "drc_error_count": drc_detail.get("Error", 0),
        "drc_critical_warning_count": drc_detail.get("Critical Warning", 0),
        "drc_warning_count": drc_detail.get("Warning", 0),
        "drc_counts_by_severity": dict(drc_detail),
        "drc_rule_breakdown": dict(drc_rules),
        "peak_memory_mb": peak_mb,
        "slice_registers_design": slice_regs(os.path.join(run_dir, "report_utilization_impl.rpt")),
        "xsa_exists": t04val("XSA_EXISTS"),
    },
    "log_messages": {"error_count": len(errs), "critical_warning_count": len(crits),
                     "warning_count": len(warns), "error_codes": sorted(set(errs))[:40],
                     "critical_warning_codes": sorted(set(crits))[:40]},
    "artifacts": artifacts,
    "limitations": [
        "只产出 bitstream + XSA；未下载、未烧 QSPI、未上板（上板与目视判读由阶段总控执行）。",
        "*** 灰度补偿、非修复 ***：蓝 MSB 仍为猜位且参与亮度；真实修复仍需硬件返修模块侧 DVP 字节 MSB 线。",
        "三通道 8 位显示值差 ∈ {0,4} LSB（非卡面所述 ≤1 LSB）；R/B 丢弃 Y[2] 而 G 丢弃 Y[1:0]。",
        "亮度权重用整数近似 77/150/29>>8（误差 ≤1 个 8 位码值），非浮点精确公式。",
        "G'[2] 与 B'[4] 均为重建/猜位，暗部与高饱和区仍有残差；整帧无颜色信息。",
        "SOF 修复的既有约束仍成立：复位后第一帧可能无 SOF；GAP_THRESH=16384 只对 1280x720(HTS=1892/VTS=740) 成立。",
        "未做 RTL 功能仿真；未做逐位网表回溯（上一卡失败点，本卡刻意避免）。",
    ],
    "not_executed": ["program_device / QSPI 烧写", "上板目视判读", "RTL 功能仿真",
                     "逐位网表回溯", "硬件返修", "Git 提交（由阶段总控统一提交）"],
}

os.makedirs(evid, exist_ok=True)
rpt = os.path.join(evid, "build_report.json")
with open(rpt, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2); f.write("\n")
print("BUILD_REPORT=%s" % rpt)
print("STATUS=%s" % status)
print("PEAK_MEM_MB=%s" % peak_mb)
print("BIT_SHA256=%s" % artifacts["bit"]["sha256"])
print("XSA_SHA256=%s" % artifacts["xsa"]["sha256"])
print("TIMING=%s" % json.dumps(report["implementation"]["timing"]))
print("DRC_ERRORS=%s" % report["implementation"]["drc_error_count"])
print("NETLIST_QUERY_STATUS=%s" % nets_status)
print("NETLIST_QUERY_PASSED=%s" % report["netlist_confirmation"]["passed"])
print("NETLIST_COUNTS=%s" % json.dumps(nets_counts))
PY

echo "LAUNCHER_DONE=1 VIVADO_EXIT=$rc"
if [ "$rc" -ne 0 ]; then exit "$rc"; fi
exit 0