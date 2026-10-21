#!/usr/bin/env bash
# =============================================================================
# 阶段3 S3-T05-PL4「PL 端中性灰度（绿通道算亮度）」启动器
#
# 目的：用**完整的绿通道**（G[2] 用 G[3] 重建 + 水平 3 抽头多数）算亮度，三通道同值输出，
#       得到真正无偏色的黑白，并彻底绕开已坏的蓝通道。
#       *** 灰度补偿、非修复 ***：蓝通道被完全弃用；真实修复仍需硬件返修模块侧 DVP 字节 MSB 线。
#
# 流程：复制 vendor_src -> git apply SOF 补丁 -> git apply 灰度补丁
#       -> 覆盖 an5642_j11_cmos2.xdc -> 构建 bitstream+XSA -> 网表核对「三通道位确实来自 G'」
#
# 用法: bash run_t04_camera_j11cmos2_gray_build.sh <run_name>
#   例: bash run_t04_camera_j11cmos2_gray_build.sh t04_gray_20261021_r01
#
# 只写本 RunId 目录与 S3-T05 证据目录；不提交 Git、不烧 QSPI、不上板。
# =============================================================================
set -u

RUN_NAME="${1:?需要 run 目录名，例如 t04_gray_20261021_r01}"

WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
SRC_COPY="$RUN_DIR/vendor_src"
XDC_IN="$WT/board/stage3/hardware/an5642_j11_cmos2.xdc"
PATCH_SOF="$WT/board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
PATCH_GRAY="$WT/board/stage3/software/sensor/alinx_ov5640_gray_luma.patch"
PATCH_DUAL="$WT/board/stage3/software/sensor/alinx_ov5640_dual_msb_rebuild.patch"
PATCH_BLUE="$WT/board/stage3/software/sensor/alinx_ov5640_blue_msb_rebuild.patch"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
TCL="$WT/scripts/stage3_t04/build_t04_camera.tcl"
EVID="$WT/report/evidence/S3-T05/t05_gray_20261021_r01"
TRACE_TCL="$EVID/netlist_din_trace_gray.tcl"
LIC="D:/Xilinx_licenses/basic_only.lic"
RTL_REL="my_ip/ov5640_ip/src/alinx_ov5640.v"

RTL_SHA_PRISTINE="98260b62f996ec700eb766c6c4e57706b2c1ff3a8224a5105a3641b6475b3e4d"
RTL_SHA_AFTER_SOF="db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6"
RTL_SHA_AFTER_BOTH="e9a93f4137829e15631925b9772ed28441e2cc454f18db714b72f6ee15c716b2"
PATCH_SOF_SHA="fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5"
PATCH_GRAY_SHA="136166243e7ef26dc3ba81a983ed17078c8bd3b2d0d1bcf7739d4b2a10045478"
BASELINE_RUNS="t04_camera_j11cmos2_20261020_r01 t04_sof_fix_20261020_r01"
BASELINE_OOC_DCP="$WT/tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0.dcp"

export XILINXD_LICENSE_FILE="$LIC"

echo "LAUNCHER=gitbash"
echo "VARIANT=PL_NEUTRAL_GRAY_FROM_GREEN"
echo "RUN_DIR=$RUN_DIR"
echo "PATCH_SOF=$PATCH_SOF"
echo "PATCH_GRAY=$PATCH_GRAY"
echo "XDC_IN=$XDC_IN"
echo "EVID=$EVID"
echo "LICENSE=$XILINXD_LICENSE_FILE"

TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
[ "$TOP" = "$WT" ] || { echo "FAIL=worktree_selfcheck:$TOP"; exit 3; }
[ -e "$RUN_DIR" ] && { echo "FAIL=run_dir_exists"; exit 3; }
[ -d "$VENDOR" ] || { echo "FAIL=vendor_missing"; exit 3; }
[ -f "$XDC_IN" ] || { echo "FAIL=xdc_missing"; exit 3; }
[ -f "$PATCH_SOF" ] || { echo "FAIL=patch_sof_missing"; exit 3; }
[ -f "$PATCH_GRAY" ] || { echo "FAIL=patch_gray_missing"; exit 3; }
[ -f "$TRACE_TCL" ] || { echo "FAIL=trace_tcl_missing"; exit 3; }
[ -f "$TCL" ] || { echo "FAIL=tcl_missing"; exit 3; }
[ -f "$LIC" ] || { echo "FAIL=license_missing"; exit 3; }

COMMIT="$(git -C "$WT" rev-parse HEAD)"
BRANCH="$(git -C "$WT" rev-parse --abbrev-ref HEAD)"
SOF_SHA_ACTUAL="$(sha256sum "$PATCH_SOF" | awk '{print $1}')"
GRAY_SHA_ACTUAL="$(sha256sum "$PATCH_GRAY" | awk '{print $1}')"
XDC_SHA="$(sha256sum "$XDC_IN" | awk '{print $1}')"
echo "BASELINE_COMMIT=$COMMIT"
echo "BASELINE_BRANCH=$BRANCH"
echo "PATCH_SOF_SHA256=$SOF_SHA_ACTUAL"
echo "PATCH_GRAY_SHA256=$GRAY_SHA_ACTUAL"
echo "XDC_SHA256=$XDC_SHA"
[ "$SOF_SHA_ACTUAL" = "$PATCH_SOF_SHA" ] || { echo "FAIL=sof_patch_sha_mismatch"; exit 4; }
[ "$GRAY_SHA_ACTUAL" = "$PATCH_GRAY_SHA" ] || { echo "FAIL=gray_patch_sha_mismatch"; exit 4; }

RUNNING="$( (tasklist //FI "IMAGENAME eq vivado.exe" //NH 2>/dev/null; tasklist //FI "IMAGENAME eq xsim.exe" //NH 2>/dev/null) | grep -ci 'vivado.exe\|xsim.exe' )"
echo "EXISTING_VIVADO_XSIM_PROCS=$RUNNING"

mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir_run_dir"; exit 3; }
mkdir -p "$EVID" || { echo "FAIL=mkdir_evid"; exit 3; }

# ---- 1) vendor 副本 + 依次应用 SOF 与灰度补丁（不叠加 dual/blue） -----------
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
  echo "== patch 2/2: PL NEUTRAL GRAY (luma from green) =="
  echo "CMD=git apply --check -p1 --directory=$REL_SRC $PATCH_GRAY"
  git apply --check -p1 --directory="$REL_SRC" "$PATCH_GRAY"; echo "GRAY_CHECK_RC=$?"
  echo "CMD=git apply -p1 --directory=$REL_SRC $PATCH_GRAY"
  git apply -p1 --directory="$REL_SRC" "$PATCH_GRAY"; echo "GRAY_APPLY_RC=$?"
  echo "RTL_AFTER_BOTH_SHA256=$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
) > "$EVID/patch_git_apply.log" 2>&1
cat "$EVID/patch_git_apply.log"
get_rc() { grep -m1 "^$1=" "$EVID/patch_git_apply.log" | cut -d= -f2; }
SOF_CHECK_RC="$(get_rc SOF_CHECK_RC)"; SOF_APPLY_RC="$(get_rc SOF_APPLY_RC)"
GRAY_CHECK_RC="$(get_rc GRAY_CHECK_RC)"; GRAY_APPLY_RC="$(get_rc GRAY_APPLY_RC)"
FINAL_RTL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
echo "SOF_CHECK_RC=$SOF_CHECK_RC SOF_APPLY_RC=$SOF_APPLY_RC GRAY_CHECK_RC=$GRAY_CHECK_RC GRAY_APPLY_RC=$GRAY_APPLY_RC"
echo "RTL_FINAL_SHA256=$FINAL_RTL"
if [ "$SOF_CHECK_RC" != "0" ] || [ "$SOF_APPLY_RC" != "0" ] || [ "$GRAY_CHECK_RC" != "0" ] || [ "$GRAY_APPLY_RC" != "0" ]; then
  echo "FAIL=patch_application_rc:$SOF_CHECK_RC/$SOF_APPLY_RC/$GRAY_CHECK_RC/$GRAY_APPLY_RC"; exit 4
fi
[ "$FINAL_RTL" = "$RTL_SHA_AFTER_BOTH" ] || { echo "FAIL=final_rtl_hash_mismatch:$FINAL_RTL"; exit 4; }
grep -q "GAP_THRESH" "$SRC_COPY/$RTL_REL" || { echo "FAIL=sof_marker_missing"; exit 4; }
grep -q "s_axis_tdata_gray" "$SRC_COPY/$RTL_REL" || { echo "FAIL=gray_marker_missing"; exit 4; }
for marker in s_axis_tdata_dualmsb s_axis_tdata_bluefix; do
  if grep -q "$marker" "$SRC_COPY/$RTL_REL"; then
    echo "FAIL=residual_patch_marker_present:$marker"; exit 4
  fi
done
echo "PATCHES_VERIFIED=1 DUAL_AND_BLUE_MARKERS_ABSENT=1"
cp -f "$PATCH_SOF" "$EVID/alinx_ov5640_sof_hrefgap.patch"
cp -f "$PATCH_GRAY" "$EVID/alinx_ov5640_gray_luma.patch"
[ -f "$PATCH_DUAL" ] && cp -f "$PATCH_DUAL" "$EVID/alinx_ov5640_dual_msb_rebuild_not_applied.patch" || true
[ -f "$PATCH_BLUE" ] && cp -f "$PATCH_BLUE" "$EVID/alinx_ov5640_blue_msb_rebuild_not_applied.patch" || true

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

# ---- 4) 网表核对：三通道位确实来自 G'（并把 SOF-only 基线也 trace 一遍做对照） --
OOC_DCP="$RUN_DIR/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0.dcp"
TRACE_LOG="$EVID/netlist_din_trace_gray.log"
BASE_TRACE_LOG="$EVID/netlist_din_trace_gray_baseline.log"
trace_rc=9; base_trace_rc=9
echo "OOC_DCP=$OOC_DCP EXISTS=$([ -f "$OOC_DCP" ] && echo 1 || echo 0)"
if [ -f "$OOC_DCP" ]; then
  "$VIVADO" -mode batch -source "$TRACE_TCL" -log "$TRACE_LOG" \
    -journal "$EVID/netlist_din_trace_gray.jou" -tclargs "$OOC_DCP"
  trace_rc=$?
fi
echo "TRACE_EXIT=$trace_rc"
if [ -f "$BASELINE_OOC_DCP" ]; then
  "$VIVADO" -mode batch -source "$TRACE_TCL" -log "$BASE_TRACE_LOG" \
    -journal "$EVID/netlist_din_trace_gray_baseline.jou" -tclargs "$BASELINE_OOC_DCP"
  base_trace_rc=$?
fi
echo "BASE_TRACE_EXIT=$base_trace_rc"

# ---- 5) 证据留存 -------------------------------------------------------------
cp -f "$RUN_DIR/vivado.log" "$EVID/vivado.log" 2>/dev/null || true
cp -f "$RUN_DIR/vivado.jou" "$EVID/vivado.jou" 2>/dev/null || true
for f in "$RUN_DIR"/report_*.rpt; do [ -f "$f" ] && cp -f "$f" "$EVID/$(basename "$f")" || true; done

export ILA_EVID_DIR="$EVID"
export ILA_RUN_NAME="$RUN_NAME"
export ILA_RUN_DIR="$RUN_DIR"
export ILA_EXIT_CODE="$rc"
export ILA_TRACE_RC="$trace_rc"
export ILA_BASE_TRACE_RC="$base_trace_rc"
export ILA_ELAPSED="$ELAPSED"
export ILA_CMD="$CMD"
export ILA_TRACE_LOG="$TRACE_LOG"
export ILA_BASE_TRACE_LOG="$BASE_TRACE_LOG"
export ILA_COMMIT="$COMMIT"
export ILA_BRANCH="$BRANCH"
export ILA_VENDOR="$VENDOR"
export ILA_PATCH_SOF="$PATCH_SOF"
export ILA_PATCH_SOF_SHA="$SOF_SHA_ACTUAL"
export ILA_PATCH_GRAY="$PATCH_GRAY"
export ILA_PATCH_GRAY_SHA="$GRAY_SHA_ACTUAL"
export ILA_XDC="$XDC_IN"
export ILA_XDC_SHA="$XDC_SHA"
export ILA_LICENSE="$XILINXD_LICENSE_FILE"
export ILA_RTL_PRISTINE_SHA="$RTL_SHA_PRISTINE"
export ILA_RTL_AFTER_SOF_SHA="$RTL_SHA_AFTER_SOF"
export ILA_RTL_AFTER_BOTH_SHA="$RTL_SHA_AFTER_BOTH"
export ILA_RTL_REL="$RTL_REL"
export ILA_BASELINE_RUNS="$BASELINE_RUNS"
export ILA_SOF_CHECK_RC="$SOF_CHECK_RC"
export ILA_SOF_APPLY_RC="$SOF_APPLY_RC"
export ILA_GRAY_CHECK_RC="$GRAY_CHECK_RC"
export ILA_GRAY_APPLY_RC="$GRAY_APPLY_RC"

python -B - <<'PY'
import hashlib, json, os, re, datetime, glob

evid    = os.environ["ILA_EVID_DIR"]
run_dir = os.environ["ILA_RUN_DIR"]
rc      = int(os.environ["ILA_EXIT_CODE"])
trace_rc= int(os.environ["ILA_TRACE_RC"])
base_trace_rc = int(os.environ["ILA_BASE_TRACE_RC"])
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

# ---- 网表核对：逐位比对期望映射 ----------------------------------------------
LINE_RE = re.compile(r"bit=(\d+)\s+net=(\S+)\s+depth1=(\S+)\s+lut_inputs=(\S*)\s+roots=(.*)$")

def parse_trace(path):
    T = {}
    for line in rt(path).splitlines():
        if "ILA_GRAY|" not in line: continue
        body = line.split("ILA_GRAY|", 1)[1].strip()
        mm = LINE_RE.match(body)
        if mm:
            T[int(mm.group(1))] = {"net": mm.group(2), "depth1": mm.group(3),
                                   "lut_inputs": [x for x in mm.group(4).split("|") if x],
                                   "roots": [x for x in mm.group(5).split("|") if x]}
    return T

def base_reg(n):
    return "inst/cmos_d_16bit_d1_reg[%d]/Q" % n

# din[i] = word[i-2]；期望来源（word 位 -> (说明, 种类, 寄存器号)）
EXPECT_WORD = {
    15: ("G'[5]=tdata[10]", "reg", 10), 14: ("G'[4]=tdata[9]", "reg", 9),
    13: ("G'[3]=tdata[8]", "reg", 8),   12: ("G'[2]=maj3(tdata[8])", "maj", 8),
    11: ("G'[1]=tdata[6]", "reg", 6),
    10: ("G'[5]=tdata[10]", "reg", 10), 9: ("G'[4]=tdata[9]", "reg", 9),
    8: ("G'[3]=tdata[8]", "reg", 8),    7: ("G'[2]=maj3(tdata[8])", "maj", 8),
    6: ("G'[1]=tdata[6]", "reg", 6),    5: ("G'[0]=tdata[5]", "reg", 5),
    4: ("G'[5]=tdata[10]", "reg", 10),  3: ("G'[4]=tdata[9]", "reg", 9),
    2: ("G'[3]=tdata[8]", "reg", 8),    1: ("G'[2]=maj3(tdata[8])", "maj", 8),
    0: ("G'[1]=tdata[6]", "reg", 6),
}
# 允许出现的根驱动（只允许绿通道相关寄存器 + 2 个多数延迟寄存器）
ALLOWED_REGS = {5, 6, 8, 9, 10}
FORBIDDEN_REGS = {0, 1, 2, 3, 4, 7, 11, 12, 13, 14, 15}

T = parse_trace(os.environ["ILA_TRACE_LOG"])
Tbase = parse_trace(os.environ["ILA_BASE_TRACE_LOG"])

per_bit, problems = [], []
for wbit in sorted(EXPECT_WORD, reverse=True):
    db = wbit + 2
    desc, kind, regn = EXPECT_WORD[wbit]
    got = T.get(db)
    entry = {"din_bit": db, "word_bit": wbit, "expected_source": desc,
             "expected_kind": kind, "actual_roots": got["roots"] if got else None,
             "actual_driver": got["depth1"] if got else None, "ok": False}
    if not got:
        entry["problem"] = "din bit not found in trace"
        problems.append(entry); per_bit.append(entry); continue
    roots = got["roots"]
    ref = got["depth1"].split("(")[-1].rstrip(")") if got else ""
    if kind == "reg":
        entry["ok"] = (roots == [base_reg(regn)])
        if not entry["ok"]:
            entry["problem"] = "expected single root %s" % base_reg(regn)
    else:
        others = [r for r in roots if r != base_reg(regn)]
        entry["ok"] = (re.match(r"^(LUT|MUXF)", ref or "") is not None
                       and len(roots) == 3 and base_reg(regn) in roots
                       and len(others) == 2
                       and all(o.endswith("/Q") for o in others))
        entry["majority_extra_roots"] = others
        if not entry["ok"]:
            entry["problem"] = "expected LUT3 majority with roots {reg8/Q, d1, d2}"
    if not entry["ok"]:
        problems.append(entry)
    per_bit.append(entry)

# 全局：任何 word 位的根驱动都不得落在被禁寄存器上（R 字段 / B 字段 / 死的 G[2]）
def classify_root(r):
    """返回 (是否允许, 说明)"""
    m = re.match(r"^inst/cmos_d_16bit_d1_reg\[(\d+)\]/Q$", r)
    if m:
        n = int(m.group(1))
        if n in ALLOWED_REGS:
            return True, "green-source reg[%d]" % n
        return False, "forbidden reg[%d]%s" % (n, " (dead G[2] line)" if n == 7 else "")
    if re.search(r"gray_g2_d\d", r) and r.endswith("/Q"):
        return True, "gray majority delay register"
    return False, "unrecognised root"

leak, unexpected = [], []
for wbit in EXPECT_WORD:
    for r in (T.get(wbit + 2, {}) or {}).get("roots", []) or []:
        ok, why = classify_root(r)
        if not ok:
            rec = {"din_bit": wbit + 2, "word_bit": wbit, "root": r, "why": why}
            if "forbidden reg" in why:
                leak.append(rec)
            else:
                unexpected.append(rec)

base_cmp = {}
for wbit in (15, 12, 11, 7, 1):
    ab = Tbase.get(wbit + 2, {})
    base_cmp["din[%d_search]" % (wbit + 2)] = {
        "word_bit": wbit, "baseline_roots": ab.get("roots"), "gray_roots": (T.get(wbit + 2) or {}).get("roots")}

netlist_check = {
    "trace_log": os.environ["ILA_TRACE_LOG"],
    "trace_vivado_exit_code": trace_rc,
    "baseline_trace_log": os.environ["ILA_BASE_TRACE_LOG"],
    "baseline_trace_exit_code": base_trace_rc,
    "din_pins_found": bool(T),
    "rule": ("din={word,tlast,tuser} => word[i]=din[i+2]；新字三个通道都取自 G'[5:1]/G'，"
             "故每一位的根驱动都必须落在 {reg[5],reg[6],reg[8],reg[9],reg[10]} 与 2 个多数延迟寄存器内；"
             "G'[2] 的三处（word[12],[7],[1]）必须由 3 输入多数门驱动。"),
    "expected_map": {str(w): EXPECT_WORD[w][0] for w in EXPECT_WORD},
    "per_bit": per_bit,
    "problems": problems,
    "leaked_forbidden_register_roots": leak,
    "unexpected_root_names": unexpected,
    "baseline_vs_gray": base_cmp,
    "baseline_meaning": ("基线(仅 SOF)里 word[15]/word[12]/word[11] 来自 B 字段寄存器(reg[15]/[12]/[11])、"
                         "word[7] 来自已死的 reg[7]；本变体里对应位改由绿通道 reg[10]/[9]/[8]/[6] 与多数门驱动。"),
    "passed": bool(T) and not problems and not leak and not unexpected,
}
print("GRAY_NETLIST_MAP:")
for e in per_bit:
    print("  din[%d] word[%d] %-24s -> %s" % (e["din_bit"], e["word_bit"], e["expected_source"], e["actual_roots"]))

rtl_copies = []
for p in glob.glob(os.path.join(run_dir, "project", "**", "alinx_ov5640.v"), recursive=True):
    blob = open(p, "rb").read()
    rtl_copies.append({
        "path": p, "sha256": sha256(p), "size_bytes": os.path.getsize(p),
        "matches_expected": sha256(p) == os.environ["ILA_RTL_AFTER_BOTH_SHA"],
        "contains_gap_thresh": b"GAP_THRESH" in blob,
        "contains_gray_marker": b"s_axis_tdata_gray" in blob,
        "contains_dualmsb_marker": b"s_axis_tdata_dualmsb" in blob,
        "contains_bluefix_marker": b"s_axis_tdata_bluefix" in blob,
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
                   ("patch_gray_luma", os.environ["ILA_PATCH_GRAY"]),
                   ("xdc_j11_cmos2", os.environ["ILA_XDC"]),
                   ("netlist_trace_log", os.environ["ILA_TRACE_LOG"]),
                   ("netlist_trace_baseline_log", os.environ["ILA_BASE_TRACE_LOG"])):
    artifacts[name] = {"path": path, "exists": os.path.isfile(path),
                       "size_bytes": os.path.getsize(path) if os.path.isfile(path) else None,
                       "sha256": sha256(path)}

bit_ok = artifacts["bit"]["exists"] and artifacts["xsa"]["exists"]
status = "ok" if (rc == 0 and bit_ok and netlist_check["passed"]) else "failed"

report = {
    "task_id": "S3-T05-PL4",
    "task_board_id": "task-11",
    "title": "PL 端中性灰度（用完整绿通道算亮度，三通道同值输出）",
    "run_id": os.environ["ILA_RUN_NAME"],
    "run_dir": run_dir,
    "evidence_dir": evid,
    "generated_at_utc8": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "status": status,
    "disclaimer": ("*** 灰度补偿，非修复 ***。蓝通道已被完全弃用（它的最高位就是坏的那根 DVP 线）；"
                   "真实修复仍需硬件返修模块侧 DVP 字节 MSB 线 cmos_d[9]。本变体只保证黑白画面无偏色，"
                   "不构成颜色正确性证据，不得用于颜色验收。"),
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
    },
    "grayscale": {
        "formula": "G' = { tdata[10], tdata[9], tdata[8], maj3(tdata[8]), tdata[6], tdata[5] }；"
                   "new = { G'[5:1], G'[5:0], G'[5:1] }",
        "expansion": "new = { t10,t9,t8,maj,t6,  t10,t9,t8,maj,t6,t5,  t10,t9,t8,maj,t6 }",
        "luma_source": "完整绿通道（6 位），G'[2] 用 G[3]=tdata[8] 重建",
        "majority": ("水平 3 抽头多数 maj=(c0&c1)|(c0&c2)|(c1&c2)，只用于 G'[2]；"
                     "2 个像素率延迟寄存器 + 1 个多数门，无行缓冲/BRAM；窗口因果（当前+前 2 像素），"
                     "数据流不额外延迟，tvalid/tlast/tuser 仍对齐。"),
        "channel_equality": "R=B=G'[5:1]、G=G' ⇒ 三通道亮度基本相等（丢 G'[0]，差 ≤1 LSB）",
        "card_expansion_note": ("卡面括注写作 `{t10,t9,t8,t8,t6, ...}`，与本卡主公式 `{G'[5:1], G', G'[5:1]}` 的第四位"
                                "（应为 maj3(tdata[8])）不一致；本实现按**主公式**执行（R=B=G'[5:1]），"
                                "这样三通道才真正只差 1 LSB。"),
        "not_changed": ["tlast", "tuser", "tkeep", "tvalid/tready", "时钟/时序", "DEBUG_OV5640（保持 false）"],
        "known_errors": [
            "灰度亮度取自绿通道：偏绿的场景亮度偏亮、偏蓝/偏红的场景亮度偏低（非标准亮度权重，未做 0.299R+0.587G+0.114B）。",
            "G'[2] 是近似重建位，暗部/低饱和区仍有量化残差；多数表决只压孤立散斑。",
            "整帧只有亮度信息，颜色不可恢复；不得用于颜色验收。",
        ],
    },
    "patches": {
        "applied_order": ["alinx_ov5640_sof_hrefgap.patch", "alinx_ov5640_gray_luma.patch"],
        "items": [
            {"name": "SOF fix (task-2)", "file": os.environ["ILA_PATCH_SOF"],
             "sha256": os.environ["ILA_PATCH_SOF_SHA"], "hunks": 3, "lines_added": 24, "lines_removed": 5,
             "git_apply_check_rc": int(os.environ["ILA_SOF_CHECK_RC"]),
             "git_apply_rc": int(os.environ["ILA_SOF_APPLY_RC"])},
            {"name": "PL neutral gray luma (this task)", "file": os.environ["ILA_PATCH_GRAY"],
             "sha256": os.environ["ILA_PATCH_GRAY_SHA"], "hunks": 2, "lines_added": 36, "lines_removed": 1,
             "git_apply_check_rc": int(os.environ["ILA_GRAY_CHECK_RC"]),
             "git_apply_rc": int(os.environ["ILA_GRAY_APPLY_RC"])},
        ],
        "not_applied": ["alinx_ov5640_dual_msb_rebuild.patch（task-9，双位重建）",
                        "alinx_ov5640_blue_msb_rebuild.patch（task-6，已被 task-9 取代）"],
        "residual_marker_assertion": "构建脚本断言最终 RTL 不含 s_axis_tdata_dualmsb / s_axis_tdata_bluefix（PATCHES_VERIFIED=1）。",
        "order_note": ("两补丁区域不重叠（SOF 改参数表/tuser always 块；GRAY 在 FIFO 前插入新块并改 .din）；"
                       "实测 gray 单独对厂商原件 --check/apply RC=0，SOF->GRAY 与 GRAY->SOF 均 RC=0 且结果字节相同。"),
        "git_apply_log": os.path.join(evid, "patch_git_apply.log"),
        "order_test_evidence": os.path.join(evid, "patch_apply_order_test.txt"),
    },
    "rtl_hashes": {
        "pristine_vendor": os.environ["ILA_RTL_PRISTINE_SHA"],
        "after_sof_patch": os.environ["ILA_RTL_AFTER_SOF_SHA"],
        "after_sof_then_gray": os.environ["ILA_RTL_AFTER_BOTH_SHA"],
        "final_actual": artifacts["patched_rtl"]["sha256"],
    },
    "netlist_confirmation": netlist_check,
    "commands": {"build": os.environ["ILA_CMD"], "tcl_script": "scripts/stage3_t04/build_t04_camera.tcl",
                 "netlist_trace_tcl": "report/evidence/S3-T05/t05_gray_20261021_r01/netlist_din_trace_gray.tcl",
                 "vivado_exit_code": rc, "trace_exit_code": trace_rc, "baseline_trace_exit_code": base_trace_rc,
                 "elapsed_seconds": int(os.environ["ILA_ELAPSED"])},
    "implementation": {
        "synth_status": t04val("SYNTH_STATUS"), "impl_status": t04val("IMPL_STATUS"),
        "timing": {"wns_ns": t04val("TIMING_WNS"), "tns_ns": t04val("TIMING_TNS"),
                   "whs_ns": t04val("TIMING_WHS"), "ths_ns": t04val("TIMING_THS")},
        "timing_reference_runs": {
            "t04_camera_j11cmos2_20261020_r01_baseline": {"wns_ns": "1.141183", "tns_ns": "0.000000", "whs_ns": "0.058332", "ths_ns": "0.000000"},
            "t04_sof_fix_20261020_r01_sof_only": {"wns_ns": "1.054525", "tns_ns": "0.000000", "whs_ns": "0.058931", "ths_ns": "0.000000"},
            "t04_dualmsb_20261021_r01_dual_rebuild": {"wns_ns": "1.171408", "tns_ns": "0.000000", "whs_ns": "0.053436", "ths_ns": "0.000000"},
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
        "meaning": "工程 .gen 下 IP RTL 副本哈希 = SOF+GRAY 叠加后的哈希，含 GAP_THRESH 与 s_axis_tdata_gray，且不含 dual/blue 标记。",
    },
    "log_messages": {"error_count": len(errs), "critical_warning_count": len(crits),
                     "warning_count": len(warns), "error_codes": sorted(set(errs))[:40],
                     "critical_warning_codes": sorted(set(crits))[:40]},
    "artifacts": artifacts,
    "limitations": [
        "只产出 bitstream + XSA；未下载、未烧 QSPI、未上板（上板与目视判读由阶段总控执行）。",
        "*** 灰度补偿，非修复 ***：蓝通道已被完全弃用；真实修复仍需硬件返修模块侧 DVP 字节 MSB 线。",
        "亮度取自绿通道而非标准亮度权重，场景偏色会带来亮度偏差；G'[2] 为近似重建位，暗部仍有残差。",
        "SOF 修复的既有约束仍成立：复位后第一帧可能无 SOF；GAP_THRESH=16384 只对 1280x720(HTS=1892/VTS=740) 成立。",
        "未做 RTL 功能仿真；未验证位流与基线功能一致性（仅时序/DRC/资源/网表连通性对比）。",
    ],
    "not_executed": ["program_device / QSPI 烧写", "上板目视判读", "RTL 仿真",
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
print("NETLIST_PROBLEMS=%s" % json.dumps(problems, ensure_ascii=False)[:800])
print("NETLIST_LEAK=%s" % json.dumps(leak))
PY

if [ "$rc" -ne 0 ]; then exit "$rc"; fi
python -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); sys.exit(0 if d['status']=='ok' else 21)" "$EVID/build_report.json" || exit 21
echo "EVIDENCE_JSON=$EVID/build_report.json"
exit 0