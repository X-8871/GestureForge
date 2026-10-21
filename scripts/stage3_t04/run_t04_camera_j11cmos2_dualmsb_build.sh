#!/usr/bin/env bash
# =============================================================================
# 阶段3 S3-T05-PL3「双位重建 + 水平 3 抽头多数」启动器（明示的近似补偿）
#
# 背景：模块侧 DVP 字节 MSB 线（cmos_d[9]）无信号 ⇒ 16 位字里两个位同时丢失：
#   字 bit15 = B[4]（第一字节 MSB）与 字 bit7 = G[2]（第二字节 MSB），字布局 {B[4:0],G[5:0],R[4:0]}。
#   本变体在 PL 侧做**近似补偿**：B'[4]=B[3]、G'[2]=G[3]，并对这两个重建位做水平 3 抽头多数表决。
#   *** 近似补偿、非真实修复、不得用于颜色验收 ***（真实修复需硬件返修该 DVP 数据线）。
#
# 流程：复制 vendor_src -> git apply SOF 补丁 -> git apply 双位重建补丁
#       -> 覆盖 an5642_j11_cmos2.xdc -> 构建 bitstream+XSA -> 综合网表核对重建位确实接到 FIFO din
#
# 用法: bash run_t04_camera_j11cmos2_dualmsb_build.sh <run_name>
#   例: bash run_t04_camera_j11cmos2_dualmsb_build.sh t04_dualmsb_20261021_r01
#
# 只写本 RunId 目录与 S3-T05 证据目录；不提交 Git、不烧 QSPI、不上板。
# =============================================================================
set -u

RUN_NAME="${1:?需要 run 目录名，例如 t04_dualmsb_20261021_r01}"

WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
SRC_COPY="$RUN_DIR/vendor_src"
XDC_IN="$WT/board/stage3/hardware/an5642_j11_cmos2.xdc"
PATCH_SOF="$WT/board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
PATCH_DUAL="$WT/board/stage3/software/sensor/alinx_ov5640_dual_msb_rebuild.patch"
PATCH_OLD_BLUE="$WT/board/stage3/software/sensor/alinx_ov5640_blue_msb_rebuild.patch"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
TCL="$WT/scripts/stage3_t04/build_t04_camera.tcl"
EVID="$WT/report/evidence/S3-T05/t05_dualmsb_20261021_r01"
TRACE_TCL="$EVID/netlist_din_trace.tcl"
LIC="D:/Xilinx_licenses/basic_only.lic"
RTL_REL="my_ip/ov5640_ip/src/alinx_ov5640.v"

RTL_SHA_PRISTINE="98260b62f996ec700eb766c6c4e57706b2c1ff3a8224a5105a3641b6475b3e4d"
RTL_SHA_AFTER_SOF="db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6"
RTL_SHA_AFTER_BOTH="1d7b86680f27d90dfd79f8aefd6ca0f58f3fa4eb82c1b704f4180329d7f0f8e3"
PATCH_SOF_SHA="fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5"
PATCH_DUAL_SHA="635c886dfdcd0e2517fec86a3ca7239ac805091c54cc907e13510501e6cd2616"
BASELINE_RUNS="t04_camera_j11cmos2_20261020_r01 t04_sof_fix_20261020_r01"

export XILINXD_LICENSE_FILE="$LIC"

echo "LAUNCHER=gitbash"
echo "VARIANT=DUAL_MSB_REBUILD_plus_H3_MAJORITY"
echo "RUN_DIR=$RUN_DIR"
echo "PATCH_SOF=$PATCH_SOF"
echo "PATCH_DUAL=$PATCH_DUAL"
echo "XDC_IN=$XDC_IN"
echo "EVID=$EVID"
echo "LICENSE=$XILINXD_LICENSE_FILE"

TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
[ "$TOP" = "$WT" ] || { echo "FAIL=worktree_selfcheck:$TOP"; exit 3; }
[ -e "$RUN_DIR" ] && { echo "FAIL=run_dir_exists"; exit 3; }
[ -d "$VENDOR" ] || { echo "FAIL=vendor_missing"; exit 3; }
[ -f "$XDC_IN" ] || { echo "FAIL=xdc_missing"; exit 3; }
[ -f "$PATCH_SOF" ] || { echo "FAIL=patch_sof_missing"; exit 3; }
[ -f "$PATCH_DUAL" ] || { echo "FAIL=patch_dual_missing"; exit 3; }
[ -f "$TRACE_TCL" ] || { echo "FAIL=trace_tcl_missing"; exit 3; }
[ -f "$TCL" ] || { echo "FAIL=tcl_missing"; exit 3; }
[ -f "$LIC" ] || { echo "FAIL=license_missing"; exit 3; }

COMMIT="$(git -C "$WT" rev-parse HEAD)"
BRANCH="$(git -C "$WT" rev-parse --abbrev-ref HEAD)"
SOF_SHA_ACTUAL="$(sha256sum "$PATCH_SOF" | awk '{print $1}')"
DUAL_SHA_ACTUAL="$(sha256sum "$PATCH_DUAL" | awk '{print $1}')"
XDC_SHA="$(sha256sum "$XDC_IN" | awk '{print $1}')"
echo "BASELINE_COMMIT=$COMMIT"
echo "BASELINE_BRANCH=$BRANCH"
echo "PATCH_SOF_SHA256=$SOF_SHA_ACTUAL"
echo "PATCH_DUAL_SHA256=$DUAL_SHA_ACTUAL"
echo "XDC_SHA256=$XDC_SHA"
[ "$SOF_SHA_ACTUAL" = "$PATCH_SOF_SHA" ] || { echo "FAIL=sof_patch_sha_mismatch"; exit 4; }
[ "$DUAL_SHA_ACTUAL" = "$PATCH_DUAL_SHA" ] || { echo "FAIL=dual_patch_sha_mismatch"; exit 4; }

RUNNING="$( (tasklist //FI "IMAGENAME eq vivado.exe" //NH 2>/dev/null; tasklist //FI "IMAGENAME eq xsim.exe" //NH 2>/dev/null) | grep -ci 'vivado.exe\|xsim.exe' )"
echo "EXISTING_VIVADO_XSIM_PROCS=$RUNNING"

mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir_run_dir"; exit 3; }
mkdir -p "$EVID" || { echo "FAIL=mkdir_evid"; exit 3; }

# ---- 1) vendor 副本 + 依次应用 SOF 与双位重建补丁 ---------------------------
cp -r "$VENDOR" "$SRC_COPY" || { echo "FAIL=vendor_copy"; exit 3; }
PRISTINE_ACTUAL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
echo "RTL_PRISTINE_SHA256=$PRISTINE_ACTUAL"
[ "$PRISTINE_ACTUAL" = "$RTL_SHA_PRISTINE" ] || { echo "FAIL=pristine_rtl_hash_mismatch:$PRISTINE_ACTUAL"; exit 4; }

REL_SRC="tmp/s3r06/$RUN_NAME/vendor_src"
(
  cd "$WT" || exit 3
  echo "== patch 1/2: SOF =="
  echo "CMD=git apply --check -p1 --directory=$REL_SRC $PATCH_SOF"
  git apply --check -p1 --directory="$REL_SRC" "$PATCH_SOF"; echo "SOF_CHECK_RC=$?"
  echo "CMD=git apply -p1 --directory=$REL_SRC $PATCH_SOF"
  git apply -p1 --directory="$REL_SRC" "$PATCH_SOF"; echo "SOF_APPLY_RC=$?"
  echo "RTL_AFTER_SOF_SHA256=$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
  echo "== patch 2/2: DUAL-MSB REBUILD + H3 MAJORITY =="
  echo "CMD=git apply --check -p1 --directory=$REL_SRC $PATCH_DUAL"
  git apply --check -p1 --directory="$REL_SRC" "$PATCH_DUAL"; echo "DUAL_CHECK_RC=$?"
  echo "CMD=git apply -p1 --directory=$REL_SRC $PATCH_DUAL"
  git apply -p1 --directory="$REL_SRC" "$PATCH_DUAL"; echo "DUAL_APPLY_RC=$?"
  echo "RTL_AFTER_BOTH_SHA256=$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
) > "$EVID/patch_git_apply.log" 2>&1
cat "$EVID/patch_git_apply.log"
get_rc() { grep -m1 "^$1=" "$EVID/patch_git_apply.log" | cut -d= -f2; }
SOF_CHECK_RC="$(get_rc SOF_CHECK_RC)"; SOF_APPLY_RC="$(get_rc SOF_APPLY_RC)"
DUAL_CHECK_RC="$(get_rc DUAL_CHECK_RC)"; DUAL_APPLY_RC="$(get_rc DUAL_APPLY_RC)"
FINAL_RTL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
echo "SOF_CHECK_RC=$SOF_CHECK_RC SOF_APPLY_RC=$SOF_APPLY_RC DUAL_CHECK_RC=$DUAL_CHECK_RC DUAL_APPLY_RC=$DUAL_APPLY_RC"
echo "RTL_FINAL_SHA256=$FINAL_RTL"
if [ "$SOF_CHECK_RC" != "0" ] || [ "$SOF_APPLY_RC" != "0" ] || [ "$DUAL_CHECK_RC" != "0" ] || [ "$DUAL_APPLY_RC" != "0" ]; then
  echo "FAIL=patch_application_rc:$SOF_CHECK_RC/$SOF_APPLY_RC/$DUAL_CHECK_RC/$DUAL_APPLY_RC"; exit 4
fi
[ "$FINAL_RTL" = "$RTL_SHA_AFTER_BOTH" ] || { echo "FAIL=final_rtl_hash_mismatch:$FINAL_RTL"; exit 4; }
grep -q "GAP_THRESH" "$SRC_COPY/$RTL_REL" || { echo "FAIL=sof_marker_missing"; exit 4; }
grep -q "s_axis_tdata_dualmsb" "$SRC_COPY/$RTL_REL" || { echo "FAIL=dualmsb_marker_missing"; exit 4; }
if grep -q "s_axis_tdata_bluefix" "$SRC_COPY/$RTL_REL"; then
  echo "FAIL=old_bluefix_marker_present_should_be_superseded"; exit 4
fi
echo "PATCHES_VERIFIED=1 OLD_BLUEFIX_ABSENT=1"
cp -f "$PATCH_SOF" "$EVID/alinx_ov5640_sof_hrefgap.patch"
cp -f "$PATCH_DUAL" "$EVID/alinx_ov5640_dual_msb_rebuild.patch"
[ -f "$PATCH_OLD_BLUE" ] && cp -f "$PATCH_OLD_BLUE" "$EVID/alinx_ov5640_blue_msb_rebuild_superseded.patch" || true

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

# ---- 4) 综合网表核对：重建位确实接到 FIFO din --------------------------------
OOC_DCP="$RUN_DIR/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0.dcp"
TRACE_LOG="$EVID/netlist_din_trace.log"
trace_rc=9
echo "OOC_DCP=$OOC_DCP EXISTS=$([ -f "$OOC_DCP" ] && echo 1 || echo 0)"
if [ -f "$OOC_DCP" ]; then
  TRACE_CMD="$VIVADO -mode batch -source $TRACE_TCL -log $TRACE_LOG -journal $EVID/netlist_din_trace.jou -tclargs $OOC_DCP"
  echo "TRACE_CMD=$TRACE_CMD"
  "$VIVADO" -mode batch -source "$TRACE_TCL" -log "$TRACE_LOG" \
    -journal "$EVID/netlist_din_trace.jou" -tclargs "$OOC_DCP"
  trace_rc=$?
fi
echo "TRACE_EXIT=$trace_rc"

# ---- 5) 证据留存 -------------------------------------------------------------
cp -f "$RUN_DIR/vivado.log" "$EVID/vivado.log" 2>/dev/null || true
cp -f "$RUN_DIR/vivado.jou" "$EVID/vivado.jou" 2>/dev/null || true
for f in "$RUN_DIR"/report_*.rpt; do [ -f "$f" ] && cp -f "$f" "$EVID/$(basename "$f")" || true; done

export ILA_EVID_DIR="$EVID"
export ILA_RUN_NAME="$RUN_NAME"
export ILA_RUN_DIR="$RUN_DIR"
export ILA_EXIT_CODE="$rc"
export ILA_TRACE_RC="$trace_rc"
export ILA_ELAPSED="$ELAPSED"
export ILA_CMD="$CMD"
export ILA_TRACE_LOG="$TRACE_LOG"
export ILA_COMMIT="$COMMIT"
export ILA_BRANCH="$BRANCH"
export ILA_VENDOR="$VENDOR"
export ILA_PATCH_SOF="$PATCH_SOF"
export ILA_PATCH_SOF_SHA="$SOF_SHA_ACTUAL"
export ILA_PATCH_DUAL="$PATCH_DUAL"
export ILA_PATCH_DUAL_SHA="$DUAL_SHA_ACTUAL"
export ILA_XDC="$XDC_IN"
export ILA_XDC_SHA="$XDC_SHA"
export ILA_LICENSE="$XILINXD_LICENSE_FILE"
export ILA_RTL_PRISTINE_SHA="$RTL_SHA_PRISTINE"
export ILA_RTL_AFTER_SOF_SHA="$RTL_SHA_AFTER_SOF"
export ILA_RTL_AFTER_BOTH_SHA="$RTL_SHA_AFTER_BOTH"
export ILA_SOF_CHECK_RC="$SOF_CHECK_RC"
export ILA_SOF_APPLY_RC="$SOF_APPLY_RC"
export ILA_DUAL_CHECK_RC="$DUAL_CHECK_RC"
export ILA_DUAL_APPLY_RC="$DUAL_APPLY_RC"
export ILA_RTL_REL="$RTL_REL"
export ILA_BASELINE_RUNS="$BASELINE_RUNS"

python -B - <<'PY'
import hashlib, json, os, re, datetime, glob

evid    = os.environ["ILA_EVID_DIR"]
run_dir = os.environ["ILA_RUN_DIR"]
rc      = int(os.environ["ILA_EXIT_CODE"])
trace_rc= int(os.environ["ILA_TRACE_RC"])
log     = os.path.join(run_dir, "vivado.log")
rtl_rel = os.environ["ILA_RTL_REL"]

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

sib = os.path.dirname(run_dir)
regs = {}
for r in os.environ["ILA_BASELINE_RUNS"].split() + [os.environ["ILA_RUN_NAME"]]:
    regs[r] = {
        "design_synth": slice_regs(os.path.join(sib, r, "report_utilization_synth.rpt")),
        "alinx_ip_ooc": slice_regs(os.path.join(
            sib, r, "project", "ov5640_single.runs",
            "design_1_alinx_ov5640_0_0_synth_1",
            "design_1_alinx_ov5640_0_0_utilization_synth.rpt")),
    }

# ---- 综合网表核对解析 --------------------------------------------------------
trace_txt = rt(os.environ["ILA_TRACE_LOG"])
T = {}
for line in trace_txt.splitlines():
    if "ILA_DIN|" not in line: continue
    body = line.split("ILA_DIN|", 1)[1].strip()
    mm = re.match(r"bit=(\d+)\s+net=(\S+)\s+depth1=(\S+)\s+depth2=(\S+)\s+roots=(.*)$", body)
    if mm:
        T[int(mm.group(1))] = {"net": mm.group(2), "depth1": mm.group(3),
                               "depth2": mm.group(4),
                               "roots": [x for x in mm.group(5).split("|") if x]}
def roots(i): return set(T.get(i, {}).get("roots", []))

netlist_check = {
    "trace_log": os.environ["ILA_TRACE_LOG"],
    "trace_vivado_exit_code": trace_rc,
    "din_pins_found": bool(T),
    "bits": {str(k): v for k, v in sorted(T.items())},
    "rule": ("重建位 A[15]/A[7] 落在 din[17]/din[9]（din={word,tlast,tuser}）；"
             "要求 roots(din17) 含 roots(din16)=B[3] 且共 3 个根驱动，roots(din9) 含 roots(din10)=G[3] 且共 3 个根驱动。"),
    "b4_din17_roots": sorted(roots(17)), "b3_din16_roots": sorted(roots(16)),
    "g2_din9_roots": sorted(roots(9)),  "g3_din10_roots": sorted(roots(10)),
    "b4_majority_has_b3_source": bool(roots(16)) and roots(16) <= roots(17),
    "g2_majority_has_g3_source": bool(roots(10)) and roots(10) <= roots(9),
    "b4_is_3tap": len(roots(17)) >= 3,
    "g2_is_3tap": len(roots(9)) >= 3,
}
netlist_check["passed"] = bool(netlist_check["b4_majority_has_b3_source"]
                               and netlist_check["g2_majority_has_g3_source"]
                               and netlist_check["b4_is_3tap"] and netlist_check["g2_is_3tap"])

rtl_copies = []
for p in glob.glob(os.path.join(run_dir, "project", "**", "alinx_ov5640.v"), recursive=True):
    blob = open(p, "rb").read()
    rtl_copies.append({
        "path": p, "sha256": sha256(p), "size_bytes": os.path.getsize(p),
        "matches_expected": sha256(p) == os.environ["ILA_RTL_AFTER_BOTH_SHA"],
        "contains_gap_thresh": b"GAP_THRESH" in blob,
        "contains_dualmsb": b"s_axis_tdata_dualmsb" in blob,
        "contains_old_bluefix": b"s_axis_tdata_bluefix" in blob,
    })

bit = os.path.join(run_dir, "project", "ov5640_single.runs", "impl_1", "design_1_wrapper.bit")
xsa = os.path.join(run_dir, "design_1_wrapper.xsa")

artifacts = {}
for name, path in (("bit", bit), ("xsa", xsa), ("vivado_log", log),
                   ("report_timing_summary_impl", os.path.join(run_dir, "report_timing_summary_impl.rpt")),
                   ("report_drc_impl", os.path.join(run_dir, "report_drc_impl.rpt")),
                   ("report_utilization_impl", os.path.join(run_dir, "report_utilization_impl.rpt")),
                   ("report_utilization_synth", os.path.join(run_dir, "report_utilization_synth.rpt")),
                   ("patched_rtl", os.path.join(run_dir, "vendor_src", rtl_rel)),
                   ("patch_sof", os.environ["ILA_PATCH_SOF"]),
                   ("patch_dual_msb", os.environ["ILA_PATCH_DUAL"]),
                   ("xdc_j11_cmos2", os.environ["ILA_XDC"]),
                   ("netlist_trace_log", os.environ["ILA_TRACE_LOG"])):
    artifacts[name] = {"path": path, "exists": os.path.isfile(path),
                       "size_bytes": os.path.getsize(path) if os.path.isfile(path) else None,
                       "sha256": sha256(path)}

bit_ok = artifacts["bit"]["exists"] and artifacts["xsa"]["exists"]
status = "ok" if (rc == 0 and bit_ok and netlist_check["passed"]) else "failed"

report = {
    "task_id": "S3-T05-PL3",
    "task_board_id": "task-9",
    "title": "双位重建（B'[4]=B[3]、G'[2]=G[3]）+ 水平 3 抽头多数表决 —— 明示的近似补偿",
    "run_id": os.environ["ILA_RUN_NAME"],
    "run_dir": run_dir,
    "evidence_dir": evid,
    "generated_at_utc8": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "status": status,
    "disclaimer": ("*** 近似补偿、非真实修复、不得用于颜色验收 ***。真实故障是模块侧 DVP 字节 MSB 线 "
                   "cmos_d[9] 无信号（两个字节的 MSB 都丢），本变体只是用相邻位近似重建这两个位并做多数平滑；"
                   "硬件返修后应回到无补偿位流重新验收颜色。"),
    "tool": {"name": "Vivado", "version": ver, "mode": "batch_tcl",
             "license_file": os.environ["ILA_LICENSE"],
             "flow": "vendor BD auto_create_project (build_t04_camera.tcl)"},
    "baseline": {"worktree": "D:/codex-worktrees/dbdf", "branch": os.environ["ILA_BRANCH"],
                 "commit_at_build": os.environ["ILA_COMMIT"], "part": "xc7z020clg400-2",
                 "vendor_source": os.environ["ILA_VENDOR"], "compare_runs": os.environ["ILA_BASELINE_RUNS"].split(),
                 "xdc": os.environ["ILA_XDC"], "xdc_sha256": os.environ["ILA_XDC_SHA"]},
    "bit_layout": {
        "word_layout": "word[15:11]=B[4:0], word[10:5]=G[5:0], word[4:0]=R[4:0]",
        "lost_bits": ["word[15] = B[4] (第一字节 MSB, cmos_d[9])",
                      "word[7] = G[2] (第二字节 MSB, 同一根 cmos_d[9])"],
        "measured_maxima_support": "R max 248(31<<3)、G max 236(59<<2, G[2]=0)、B max 120(15<<3, B[4]=0) 与该位序完全自洽",
        "note": "旧一轮（task-6）按 word={R,G,B} 的位序重建了 word[4]，实际是 R[4]，因此没有修好蓝位并引入伪彩；本轮按正确位序重建 word[15]。",
    },
    "compensation": {
        "rebuild_table": "B'[4]=B[3]=tdata[14]；G'[2]=G[3]=tdata[8]；其余位原样",
        "new_word": "new = { maj3(B[3]), tdata[14:11], tdata[10:8], maj3(G[3]), tdata[6:5], tdata[4:0] }",
        "majority": ("水平 3 抽头多数（当前 + 前 2 个像素）：maj=(c0&c1)|(c0&c2)|(c1&c2)，"
                     "只用像素率延迟寄存器（2 个 DFF/位，共 4 个），无行缓冲/BRAM；"
                     "只作用于 B'[4] 与 G'[2] 两位；数据流本身不额外延迟，故 tvalid/tlast/tuser 仍对齐。"),
        "not_changed": ["tlast", "tuser", "tkeep", "tvalid/tready", "时钟/时序", "DEBUG_OV5640（保持 false）"],
        "known_errors": [
            "低蓝/暗部残差：B'[4]=B[3] 把蓝低 4 位区间做 2 倍拉伸，暗部/低饱和蓝的量化误差被放大（G'[2]=G[3] 同理影响绿的次高位）。",
            "亮部可能过冲：真实 B[4]=0 而 B[3]=1 的亮色会被判成 B[4]=1，蓝偏高；多数表决只能压掉孤立过冲。",
            "整帧仍非真实颜色：这是近似补偿，不构成颜色正确性证据，也不能用于颜色验收/标定。",
        ],
    },
    "patches": {
        "applied_order": ["alinx_ov5640_sof_hrefgap.patch", "alinx_ov5640_dual_msb_rebuild.patch"],
        "items": [
            {"name": "SOF fix (task-2)", "file": os.environ["ILA_PATCH_SOF"],
             "sha256": os.environ["ILA_PATCH_SOF_SHA"], "hunks": 3, "lines_added": 24, "lines_removed": 5,
             "git_apply_check_rc": int(os.environ["ILA_SOF_CHECK_RC"]),
             "git_apply_rc": int(os.environ["ILA_SOF_APPLY_RC"])},
            {"name": "dual-MSB rebuild + H3 majority (this task)", "file": os.environ["ILA_PATCH_DUAL"],
             "sha256": os.environ["ILA_PATCH_DUAL_SHA"], "hunks": 2, "lines_added": 51, "lines_removed": 1,
             "git_apply_check_rc": int(os.environ["ILA_DUAL_CHECK_RC"]),
             "git_apply_rc": int(os.environ["ILA_DUAL_APPLY_RC"])},
        ],
        "supersedes": ("旧 task-6 的 alinx_ov5640_blue_msb_rebuild.patch 基于错误位序（改到了 R[4]），"
                       "本变体**不使用**它；已断言最终 RTL 中不含其标记 s_axis_tdata_bluefix。"),
        "order_note": ("两补丁修改区域不重叠（SOF 改参数表/tuser always 块；DUAL 在 FIFO 前插入新块并改 .din），"
                       "实测 dual 单独对厂商原件 --check/apply RC=0，SOF->DUAL 与 DUAL->SOF 均 RC=0 且结果字节相同。"),
        "git_apply_log": os.path.join(evid, "patch_git_apply.log"),
        "order_test_evidence": os.path.join(evid, "patch_apply_order_test.txt"),
    },
    "rtl_hashes": {
        "pristine_vendor": os.environ["ILA_RTL_PRISTINE_SHA"],
        "after_sof_patch": os.environ["ILA_RTL_AFTER_SOF_SHA"],
        "after_sof_then_dual": os.environ["ILA_RTL_AFTER_BOTH_SHA"],
        "final_actual": artifacts["patched_rtl"]["sha256"],
    },
    "netlist_confirmation": netlist_check,
    "commands": {"build": os.environ["ILA_CMD"], "tcl_script": "scripts/stage3_t04/build_t04_camera.tcl",
                 "netlist_trace_tcl": "report/evidence/S3-T05/t05_dualmsb_20261021_r01/netlist_din_trace.tcl",
                 "vivado_exit_code": rc, "trace_exit_code": trace_rc,
                 "elapsed_seconds": int(os.environ["ILA_ELAPSED"])},
    "implementation": {
        "synth_status": t04val("SYNTH_STATUS"), "impl_status": t04val("IMPL_STATUS"),
        "timing": {"wns_ns": t04val("TIMING_WNS"), "tns_ns": t04val("TIMING_TNS"),
                   "whs_ns": t04val("TIMING_WHS"), "ths_ns": t04val("TIMING_THS")},
        "timing_reference_runs": {
            "t04_camera_j11cmos2_20261020_r01_baseline": {"wns_ns": "1.141183", "tns_ns": "0.000000", "whs_ns": "0.058332", "ths_ns": "0.000000"},
            "t04_sof_fix_20261020_r01_sof_only": {"wns_ns": "1.054525", "tns_ns": "0.000000", "whs_ns": "0.058931", "ths_ns": "0.000000"},
        },
        "drc_error_count": drc_detail.get("Error", 0),
        "drc_critical_warning_count": drc_detail.get("Critical Warning", 0),
        "drc_warning_count": drc_detail.get("Warning", 0),
        "drc_counts_by_severity": dict(drc_detail),
        "drc_rule_breakdown": dict(drc_rules),
        "peak_memory_mb": peak_mb,
        "utilization_by_run": regs,
        "xsa_exists": t04val("XSA_EXISTS"),
    },
    "rtl_evidence": {
        "project_rtl_copies": rtl_copies,
        "meaning": "工程 .gen 下 IP RTL 副本哈希 = SOF+DUAL 叠加后的哈希，且含 GAP_THRESH 与 s_axis_tdata_dualmsb、不含旧 bluefix 标记。",
    },
    "log_messages": {"error_count": len(errs), "critical_warning_count": len(crits),
                     "warning_count": len(warns), "error_codes": sorted(set(errs))[:40],
                     "critical_warning_codes": sorted(set(crits))[:40]},
    "artifacts": artifacts,
    "limitations": [
        "只产出 bitstream + XSA；未下载、未烧 QSPI、未上板（上板与目视判读由阶段总控执行）。",
        "*** 近似补偿、非真实修复、不用于颜色验收 ***；真实修复需硬件返修模块侧 DVP 字节 MSB 线。",
        "已知误差：低蓝/暗部残差被放大；亮部蓝可能过冲；多数表决只压孤立散斑，不改变系统性偏差。",
        "SOF 修复的既有约束仍成立：复位后第一帧可能无 SOF；GAP_THRESH=16384 只对 1280x720(HTS=1892/VTS=740) 成立。",
        "未做 RTL 功能仿真；未验证位流与基线功能一致性（仅时序/DRC/资源/网表连通性对比）。",
    ],
    "not_executed": ["program_device / QSPI 烧写", "上板目视/直方图判读", "RTL 仿真",
                     "硬件返修", "Git 提交（由阶段总控统一提交）"],
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
print("NETLIST_CHECK_PASSED=%s" % netlist_check["passed"])
print("NETLIST_DETAIL=%s" % json.dumps({k: netlist_check[k] for k in
      ("b4_din17_roots", "b3_din16_roots", "g2_din9_roots", "g3_din10_roots",
       "b4_majority_has_b3_source", "g2_majority_has_g3_source", "b4_is_3tap", "g2_is_3tap")}))
PY

if [ "$rc" -ne 0 ]; then exit "$rc"; fi
python -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); sys.exit(0 if d['status']=='ok' else 21)" "$EVID/build_report.json" || exit 21
echo "EVIDENCE_JSON=$EVID/build_report.json"
exit 0