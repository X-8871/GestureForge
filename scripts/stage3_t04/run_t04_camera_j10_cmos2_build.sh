#!/usr/bin/env bash
# =============================================================================
# 阶段3 S3-T05-PL2「J10 + 模块 CMOS2 通道」交叉验证变体启动器
#
# 目的：把 AN5642 模块改插 J10（官方 23_ov5640_dual 的 cmos2 映射，FPGA 脚与 J11 完全不同），
#       用于判定「RGB565 B[4] 恒为 0 / 蓝最大恒 120」的根因在板侧 J11 还是在模块 D6 走线。
#
# 只应用 SOF 补丁（alinx_ov5640_sof_hrefgap.patch）——本变体要的是“干净的蓝通道”判定，
# **不应用**蓝位重建补丁。
#
# 流程：复制 vendor_src -> git apply SOF 补丁 -> 覆盖 an5642_j10_cmos2.xdc -> 构建 bitstream+XSA
#
# 用法: bash run_t04_camera_j10_cmos2_build.sh <run_name>
#   例: bash run_t04_camera_j10_cmos2_build.sh t04_j10cmos2_20261020_r01
#
# 只写本 RunId 目录与 S3-T05 证据目录；不提交 Git、不烧 QSPI、不上板。
# =============================================================================
set -u

RUN_NAME="${1:?需要 run 目录名，例如 t04_j10cmos2_20261020_r01}"

WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
SRC_COPY="$RUN_DIR/vendor_src"
XDC_IN="$WT/board/stage3/hardware/an5642_j10_cmos2.xdc"
PATCH_SOF="$WT/board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
TCL="$WT/scripts/stage3_t04/build_t04_camera.tcl"
EVID="$WT/report/evidence/S3-T05/t05_j10_cmos2_20261020_r01"
LIC="D:/Xilinx_licenses/basic_only.lic"
RTL_REL="my_ip/ov5640_ip/src/alinx_ov5640.v"

RTL_SHA_PRISTINE="98260b62f996ec700eb766c6c4e57706b2c1ff3a8224a5105a3641b6475b3e4d"
RTL_SHA_AFTER_SOF="db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6"
PATCH_SOF_SHA="fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5"
# J10 的 16 个 FPGA 落点（官方 23_ov5640_dual cmos2 通道）
J10_PINS="W19 W18 R14 P14 Y17 Y16 W15 V15 Y14 W14 P18 N17 U15 U14 P16 P15"

export XILINXD_LICENSE_FILE="$LIC"

echo "LAUNCHER=gitbash"
echo "VARIANT=J10_CMOS2"
echo "RUN_DIR=$RUN_DIR"
echo "XDC_IN=$XDC_IN"
echo "PATCH_SOF=$PATCH_SOF"
echo "EVID=$EVID"
echo "LICENSE=$XILINXD_LICENSE_FILE"

TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
[ "$TOP" = "$WT" ] || { echo "FAIL=worktree_selfcheck:$TOP"; exit 3; }
[ -e "$RUN_DIR" ] && { echo "FAIL=run_dir_exists"; exit 3; }
[ -d "$VENDOR" ] || { echo "FAIL=vendor_missing"; exit 3; }
[ -f "$XDC_IN" ] || { echo "FAIL=xdc_missing"; exit 3; }
[ -f "$PATCH_SOF" ] || { echo "FAIL=patch_sof_missing"; exit 3; }
[ -f "$TCL" ] || { echo "FAIL=tcl_missing"; exit 3; }
[ -f "$LIC" ] || { echo "FAIL=license_missing"; exit 3; }

COMMIT="$(git -C "$WT" rev-parse HEAD)"
BRANCH="$(git -C "$WT" rev-parse --abbrev-ref HEAD)"
SOF_SHA_ACTUAL="$(sha256sum "$PATCH_SOF" | awk '{print $1}')"
XDC_SHA="$(sha256sum "$XDC_IN" | awk '{print $1}')"
echo "BASELINE_COMMIT=$COMMIT"
echo "BASELINE_BRANCH=$BRANCH"
echo "PATCH_SOF_SHA256=$SOF_SHA_ACTUAL"
echo "XDC_SHA256=$XDC_SHA"
[ "$SOF_SHA_ACTUAL" = "$PATCH_SOF_SHA" ] || { echo "FAIL=sof_patch_sha_mismatch"; exit 4; }

RUNNING="$( (tasklist //FI "IMAGENAME eq vivado.exe" //NH 2>/dev/null; tasklist //FI "IMAGENAME eq xsim.exe" //NH 2>/dev/null) | grep -ci 'vivado.exe\|xsim.exe' )"
echo "EXISTING_VIVADO_XSIM_PROCS=$RUNNING"

mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir_run_dir"; exit 3; }
mkdir -p "$EVID" || { echo "FAIL=mkdir_evid"; exit 3; }

# ---- 1) vendor 副本 + SOF 补丁（不应用蓝位补丁） ----------------------------
cp -r "$VENDOR" "$SRC_COPY" || { echo "FAIL=vendor_copy"; exit 3; }
PRISTINE_ACTUAL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
echo "RTL_PRISTINE_SHA256=$PRISTINE_ACTUAL"
[ "$PRISTINE_ACTUAL" = "$RTL_SHA_PRISTINE" ] || { echo "FAIL=pristine_rtl_hash_mismatch:$PRISTINE_ACTUAL"; exit 4; }

REL_SRC="tmp/s3r06/$RUN_NAME/vendor_src"
(
  cd "$WT" || exit 3
  echo "CMD=git apply --check -p1 --directory=$REL_SRC $PATCH_SOF"
  git apply --check -p1 --directory="$REL_SRC" "$PATCH_SOF"; echo "SOF_CHECK_RC=$?"
  echo "CMD=git apply -p1 --directory=$REL_SRC $PATCH_SOF"
  git apply -p1 --directory="$REL_SRC" "$PATCH_SOF"; echo "SOF_APPLY_RC=$?"
  echo "RTL_AFTER_SOF_SHA256=$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
) > "$EVID/patch_git_apply.log" 2>&1
cat "$EVID/patch_git_apply.log"
SOF_CHECK_RC="$(grep -m1 '^SOF_CHECK_RC=' "$EVID/patch_git_apply.log" | cut -d= -f2)"
SOF_APPLY_RC="$(grep -m1 '^SOF_APPLY_RC=' "$EVID/patch_git_apply.log" | cut -d= -f2)"
FINAL_RTL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
echo "SOF_CHECK_RC=$SOF_CHECK_RC SOF_APPLY_RC=$SOF_APPLY_RC RTL_FINAL=$FINAL_RTL"
if [ "$SOF_CHECK_RC" != "0" ] || [ "$SOF_APPLY_RC" != "0" ] || [ "$FINAL_RTL" != "$RTL_SHA_AFTER_SOF" ]; then
  echo "FAIL=sof_patch_or_rtl_hash:$SOF_CHECK_RC/$SOF_APPLY_RC/$FINAL_RTL"; exit 4
fi
grep -q "GAP_THRESH" "$SRC_COPY/$RTL_REL" || { echo "FAIL=sof_patch_marker_missing"; exit 4; }
if grep -q "s_axis_tdata_bluefix" "$SRC_COPY/$RTL_REL"; then
  echo "FAIL=blue_patch_unexpectedly_present"; exit 4
fi
echo "SOF_PATCH_APPLIED=1 BLUE_PATCH_ABSENT=1"
cp -f "$PATCH_SOF" "$EVID/alinx_ov5640_sof_hrefgap.patch"

# ---- 2) 覆盖为 J10 约束并逐条核验 16 个落点 --------------------------------
cp "$XDC_IN" "$SRC_COPY/src/constraints/an5642.xdc" || { echo "FAIL=xdc_replace"; exit 3; }
for pin in $J10_PINS; do
  grep -q "PACKAGE_PIN $pin " "$SRC_COPY/src/constraints/an5642.xdc" || { echo "FAIL=j10_pin_not_found:$pin"; exit 3; }
done
echo "J10_16_PINS_PRESENT_IN_XDC=1"

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

# ---- 4) 证据留存（含 io_placed 落点摘要） -----------------------------------
cp -f "$RUN_DIR/vivado.log" "$EVID/vivado.log" 2>/dev/null || true
cp -f "$RUN_DIR/vivado.jou" "$EVID/vivado.jou" 2>/dev/null || true
for f in "$RUN_DIR"/report_*.rpt; do [ -f "$f" ] && cp -f "$f" "$EVID/$(basename "$f")" || true; done
IO_RPT="$RUN_DIR/project/ov5640_single.runs/impl_1/design_1_wrapper_io_placed.rpt"
[ -f "$IO_RPT" ] && cp -f "$IO_RPT" "$EVID/design_1_wrapper_io_placed.rpt" || echo "WARN=io_placed_report_missing"

export ILA_EVID_DIR="$EVID"
export ILA_RUN_NAME="$RUN_NAME"
export ILA_RUN_DIR="$RUN_DIR"
export ILA_EXIT_CODE="$rc"
export ILA_ELAPSED="$ELAPSED"
export ILA_CMD="$CMD"
export ILA_COMMIT="$COMMIT"
export ILA_BRANCH="$BRANCH"
export ILA_VENDOR="$VENDOR"
export ILA_PATCH_SOF="$PATCH_SOF"
export ILA_PATCH_SOF_SHA="$SOF_SHA_ACTUAL"
export ILA_XDC="$XDC_IN"
export ILA_XDC_SHA="$XDC_SHA"
export ILA_LICENSE="$XILINXD_LICENSE_FILE"
export ILA_RTL_PRISTINE_SHA="$RTL_SHA_PRISTINE"
export ILA_RTL_AFTER_SOF_SHA="$RTL_SHA_AFTER_SOF"
export ILA_SOF_CHECK_RC="$SOF_CHECK_RC"
export ILA_SOF_APPLY_RC="$SOF_APPLY_RC"
export ILA_RTL_REL="$RTL_REL"
export ILA_IO_RPT="$IO_RPT"

python -B - <<'PY'
import hashlib, json, os, re, datetime, glob

evid    = os.environ["ILA_EVID_DIR"]
run_dir = os.environ["ILA_RUN_DIR"]
rc      = int(os.environ["ILA_EXIT_CODE"])
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
base_runs = ["t04_camera_j11cmos2_20261020_r01", "t04_sof_fix_20261020_r01"]
regs = {}
for r in base_runs + [os.environ["ILA_RUN_NAME"]]:
    regs[r] = {
        "design_synth": slice_regs(os.path.join(sib, r, "report_utilization_synth.rpt")),
        "alinx_ip_ooc": slice_regs(os.path.join(
            sib, r, "project", "ov5640_single.runs",
            "design_1_alinx_ov5640_0_0_synth_1",
            "design_1_alinx_ov5640_0_0_utilization_synth.rpt")),
    }

# ---- io_placed 落点摘要：16 个摄像头信号必须逐条落在 J10 表 ------------------
EXPECTED = [
    {"j10_pin": 3,  "fpga": "W19", "port": "cmos1_d[9]"},
    {"j10_pin": 4,  "fpga": "W18", "port": "cmos1_i2c_sda_io"},
    {"j10_pin": 5,  "fpga": "R14", "port": "cmos1_d[6]"},
    {"j10_pin": 6,  "fpga": "P14", "port": "cmos1_i2c_scl_io"},
    {"j10_pin": 7,  "fpga": "Y17", "port": "cmos1_d[7]"},
    {"j10_pin": 8,  "fpga": "Y16", "port": "cmos1_d[2]"},
    {"j10_pin": 9,  "fpga": "W15", "port": "cmos1_href"},
    {"j10_pin": 10, "fpga": "V15", "port": "cmos1_d[8]"},
    {"j10_pin": 11, "fpga": "Y14", "port": "cmos1_d[3]"},
    {"j10_pin": 12, "fpga": "W14", "port": "cmos_rstn_tri_o[0]"},
    {"j10_pin": 13, "fpga": "P18", "port": "cmos1_d[4]"},
    {"j10_pin": 14, "fpga": "N17", "port": "cmos1_d[5]"},
    {"j10_pin": 15, "fpga": "U15", "port": "cmos1_d[1]"},
    {"j10_pin": 16, "fpga": "U14", "port": "cmos1_d[0]"},
    {"j10_pin": 17, "fpga": "P16", "port": "cmos1_vsync"},
    {"j10_pin": 18, "fpga": "P15", "port": "cmos1_pclk"},
]
PLACED = {}
io_txt = rt(os.environ["ILA_IO_RPT"])
for line in io_txt.splitlines():
    if not line.startswith("|"):
        continue
    cols = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cols) < 6:
        continue
    pin, sig, _bank, _pname, use, iostd = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5]
    if not sig or sig == "Signal Name" or pin == "Pin Number" or set(pin) <= set("+- "):
        continue
    PLACED[sig] = {"fpga_pin": pin, "use": use, "iostd": iostd}

landing, mismatches = [], []
for e in EXPECTED:
    got = PLACED.get(e["port"])
    entry = dict(e)
    entry["placed"] = bool(got)
    entry["actual_fpga_pin"] = got["fpga_pin"] if got else None
    entry["use"] = got["use"] if got else None
    entry["iostd"] = got["iostd"] if got else None
    entry["match"] = bool(got) and got["fpga_pin"] == e["fpga"]
    landing.append(entry)
    if not entry["match"]:
        mismatches.append(entry)

rtl_copies = []
for p in glob.glob(os.path.join(run_dir, "project", "**", "alinx_ov5640.v"), recursive=True):
    blob = open(p, "rb").read()
    rtl_copies.append({
        "path": p, "sha256": sha256(p), "size_bytes": os.path.getsize(p),
        "matches_expected": sha256(p) == os.environ["ILA_RTL_AFTER_SOF_SHA"],
        "contains_gap_thresh": b"GAP_THRESH" in blob,
        "contains_bluefix": b"s_axis_tdata_bluefix" in blob,
    })

bit = os.path.join(run_dir, "project", "ov5640_single.runs", "impl_1", "design_1_wrapper.bit")
xsa = os.path.join(run_dir, "design_1_wrapper.xsa")

artifacts = {}
for name, path in (("bit", bit), ("xsa", xsa), ("vivado_log", log),
                   ("io_placed_report", os.environ["ILA_IO_RPT"]),
                   ("report_timing_summary_impl", os.path.join(run_dir, "report_timing_summary_impl.rpt")),
                   ("report_drc_impl", os.path.join(run_dir, "report_drc_impl.rpt")),
                   ("report_utilization_impl", os.path.join(run_dir, "report_utilization_impl.rpt")),
                   ("report_utilization_synth", os.path.join(run_dir, "report_utilization_synth.rpt")),
                   ("patched_rtl", os.path.join(run_dir, "vendor_src", rtl_rel)),
                   ("patch_sof", os.environ["ILA_PATCH_SOF"]),
                   ("xdc_j10_cmos2", os.environ["ILA_XDC"])):
    artifacts[name] = {"path": path, "exists": os.path.isfile(path),
                       "size_bytes": os.path.getsize(path) if os.path.isfile(path) else None,
                       "sha256": sha256(path)}

bit_ok = artifacts["bit"]["exists"] and artifacts["xsa"]["exists"]
status = "ok" if (rc == 0 and bit_ok and not mismatches) else "failed"

report = {
    "task_id": "S3-T05-PL2",
    "task_board_id": "task-7",
    "title": "J10 + 模块 CMOS2 交叉验证变体（官方 23_ov5640_dual cmos2 映射，SOF 补丁、无蓝位重建）",
    "run_id": os.environ["ILA_RUN_NAME"],
    "run_dir": run_dir,
    "evidence_dir": evid,
    "generated_at_utc8": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "status": status,
    "purpose": ("判定「RGB565 B[4] 恒 0 / 蓝最大恒 120」的根因在板侧 J11 走线还是在模块 D6 走线："
                "把模块改插 J10、用官方双目例程 cmos2 通道的 FPGA 脚（与 J11 完全不同）。"
                "若 J10 下蓝出现 >127 像素 => 板侧 J11 故障；若仍锁 120 => 模块 D6 故障。"),
    "tool": {"name": "Vivado", "version": ver, "mode": "batch_tcl",
             "license_file": os.environ["ILA_LICENSE"],
             "flow": "vendor BD auto_create_project (build_t04_camera.tcl)"},
    "baseline": {"worktree": "D:/codex-worktrees/dbdf", "branch": os.environ["ILA_BRANCH"],
                 "commit_at_build": os.environ["ILA_COMMIT"], "part": "xc7z020clg400-2",
                 "vendor_source": os.environ["ILA_VENDOR"], "compare_runs": base_runs,
                 "xdc": os.environ["ILA_XDC"], "xdc_sha256": os.environ["ILA_XDC_SHA"],
                 "xdc_basis": ["官方 23_ov5640_dual src/constraints/an5642.xdc（cmos2 通道 16 个 PACKAGE_PIN）",
                               "AX7020 V3.0 手册 Table 7.4.1（J10 针脚表）"]},
    "variant_scope": {
        "pin_group_replaced": "J11 (F/G/H/J/K/L/M) -> J10 (W/V/R/P/Y/N/U)",
        "blue_patch_applied": False,
        "blue_patch_note": "本变体故意不应用 alinx_ov5640_blue_msb_rebuild.patch，保持蓝通道原始行为以便判定。",
        "sof_patch_applied": True,
        "debug_ov5640": False,
    },
    "patches": {
        "items": [{"name": "SOF fix", "file": os.environ["ILA_PATCH_SOF"],
                   "sha256": os.environ["ILA_PATCH_SOF_SHA"], "hunks": 3,
                   "lines_added": 24, "lines_removed": 5,
                   "git_apply_check_rc": int(os.environ["ILA_SOF_CHECK_RC"]),
                   "git_apply_rc": int(os.environ["ILA_SOF_APPLY_RC"])}],
        "applied_order": ["alinx_ov5640_sof_hrefgap.patch"],
        "git_apply_note": "从工作树根执行 git apply -p1 --directory=<run>/vendor_src；GNU patch 对该 CRLF 文件不适用。",
    },
    "rtl_hashes": {
        "pristine_vendor": os.environ["ILA_RTL_PRISTINE_SHA"],
        "after_sof_patch": os.environ["ILA_RTL_AFTER_SOF_SHA"],
        "final_actual": artifacts["patched_rtl"]["sha256"],
        "bluefix_marker_absent": True,
    },
    "commands": {"build": os.environ["ILA_CMD"], "tcl_script": "scripts/stage3_t04/build_t04_camera.tcl",
                 "vivado_exit_code": rc, "elapsed_seconds": int(os.environ["ILA_ELAPSED"])},
    "implementation": {
        "synth_status": t04val("SYNTH_STATUS"), "impl_status": t04val("IMPL_STATUS"),
        "timing": {"wns_ns": t04val("TIMING_WNS"), "tns_ns": t04val("TIMING_TNS"),
                   "whs_ns": t04val("TIMING_WHS"), "ths_ns": t04val("TIMING_THS")},
        "timing_reference_runs": {
            "t04_camera_j11cmos2_20261020_r01_baseline": {"wns_ns": "1.141183", "tns_ns": "0.000000", "whs_ns": "0.058332", "ths_ns": "0.000000"},
            "t04_sof_fix_20261020_r01_sof_only_J11": {"wns_ns": "1.054525", "tns_ns": "0.000000", "whs_ns": "0.058931", "ths_ns": "0.000000"},
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
    "io_placement": {
        "source_report": os.environ["ILA_IO_RPT"],
        "device_package_pins_checked": 16,
        "all_16_match_j10_table": not mismatches,
        "mismatches": mismatches,
        "expected_and_actual": landing,
        "meaning": ("通过 io_placed 报告逐条核对：16 个摄像头信号（cmos1_d[9:0]、cmos1_href、cmos1_vsync、"
                    "cmos1_pclk、cmos1_i2c_sda_io、cmos1_i2c_scl_io、cmos_rstn_tri_o[0]）落点等于官方 "
                    "23_ov5640_dual cmos2 通道的 J10 FPGA 脚，即本变体确实换到了与 J11 完全不同的 FPGA 脚。"),
    },
    "rtl_evidence": {
        "project_rtl_copies": rtl_copies,
        "meaning": "工程 .gen 下 IP RTL 副本哈希 = 仅 SOF 补丁后的哈希，且不含蓝位重建标记，证明本变体是“干净蓝通道”。",
    },
    "log_messages": {"error_count": len(errs), "critical_warning_count": len(crits),
                     "warning_count": len(warns), "error_codes": sorted(set(errs))[:40],
                     "critical_warning_codes": sorted(set(crits))[:40]},
    "artifacts": artifacts,
    "limitations": [
        "只产出 bitstream + XSA；未下载、未烧 QSPI、未上板（上板、插拔 J10 与判读由阶段总控执行）。",
        "本变体的结论必须配上板蓝通道直方图才能定根因；仅构建本身不能判定。",
        "若 J10 下蓝仍锁 120，还不能完全排除「两种连接共用的模块侧 D6 走线」以外的其他共性因素（如 IP 内部该位处理），需结合后续证据。",
        "SOF 修复的既有约束仍成立：复位后第一帧可能无 SOF；GAP_THRESH=16384 只对 1280x720(HTS=1892/VTS=740) 成立。",
        "未做 RTL 功能仿真；未验证位流与基线功能一致性（仅时序/DRC/资源与落点对比）。",
    ],
    "not_executed": ["program_device / QSPI 烧写", "上板插拔 J10 与蓝通道判读", "RTL 仿真",
                     "根因定位（J11 板侧 vs 模块 D6）", "Git 提交（由阶段总控统一提交）"],
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
print("IO_ALL16_MATCH=%s" % (not mismatches))
print("IO_MISMATCHES=%s" % json.dumps(mismatches))
PY

echo "EVIDENCE_JSON=$EVID/build_report.json"
exit "$rc"