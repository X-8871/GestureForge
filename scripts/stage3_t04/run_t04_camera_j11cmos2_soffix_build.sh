#!/usr/bin/env bash
# =============================================================================
# 阶段3 S3-T05「SOF 修复变体」启动器
#
# 目的：不依赖 cmos_vsync，改用「hblank 连续低 >= GAP_THRESH 个 pclk 后的第一个有效像素」
#       作为帧起始（s_axis_tuser），使 VDMA S2MM 的 TUSER/SOF 能真正出现。
#
# 流程（沿用既有 J11+CMOS2 变体脚本）：
#   复制 vendor_src -> git apply 补丁 -> 覆盖 an5642_j11_cmos2.xdc -> 构建 bitstream + XSA
#
# 用法: bash run_t04_camera_j11cmos2_soffix_build.sh <run_name>
#   例: bash run_t04_camera_j11cmos2_soffix_build.sh t04_sof_fix_20261020_r01
#
# 只写本 RunId 目录与 S3-T05 证据目录；不提交 Git、不烧 QSPI、不上板。
# =============================================================================
set -u

RUN_NAME="${1:?需要 run 目录名，例如 t04_sof_fix_20261020_r01}"

WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
SRC_COPY="$RUN_DIR/vendor_src"
XDC_IN="$WT/board/stage3/hardware/an5642_j11_cmos2.xdc"
PATCH="$WT/board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
TCL="$WT/scripts/stage3_t04/build_t04_camera.tcl"
EVID="$WT/report/evidence/S3-T05/t05_sof_fix_20261020_r01"
LIC="D:/Xilinx_licenses/basic_only.lic"
RTL_REL="my_ip/ov5640_ip/src/alinx_ov5640.v"
# 补丁前后 RTL 的确定哈希（由 make_sof_hrefgap_patch.py 生成，此处作为硬断言）
RTL_SHA_PRISTINE="98260b62f996ec700eb766c6c4e57706b2c1ff3a8224a5105a3641b6475b3e4d"
RTL_SHA_PATCHED="db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6"
BASELINE_RUN_ID="t04_camera_j11cmos2_20261020_r01"

export XILINXD_LICENSE_FILE="$LIC"

echo "LAUNCHER=gitbash"
echo "RUN_DIR=$RUN_DIR"
echo "VENDOR=$VENDOR"
echo "PATCH=$PATCH"
echo "XDC_IN=$XDC_IN"
echo "EVID=$EVID"
echo "LICENSE=$XILINXD_LICENSE_FILE"

TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
[ "$TOP" = "$WT" ] || { echo "FAIL=worktree_selfcheck:$TOP"; exit 3; }
[ -e "$RUN_DIR" ] && { echo "FAIL=run_dir_exists"; exit 3; }
[ -d "$VENDOR" ] || { echo "FAIL=vendor_missing"; exit 3; }
[ -f "$PATCH" ] || { echo "FAIL=patch_missing:$PATCH"; exit 3; }
[ -f "$XDC_IN" ] || { echo "FAIL=xdc_missing"; exit 3; }
[ -f "$TCL" ] || { echo "FAIL=tcl_missing"; exit 3; }
[ -f "$LIC" ] || { echo "FAIL=license_missing"; exit 3; }

COMMIT="$(git -C "$WT" rev-parse HEAD)"
BRANCH="$(git -C "$WT" rev-parse --abbrev-ref HEAD)"
PATCH_SHA="$(sha256sum "$PATCH" | awk '{print $1}')"
XDC_SHA="$(sha256sum "$XDC_IN" | awk '{print $1}')"
echo "BASELINE_COMMIT=$COMMIT"
echo "BASELINE_BRANCH=$BRANCH"
echo "PATCH_SHA256=$PATCH_SHA"
echo "XDC_SHA256=$XDC_SHA"

RUNNING="$( (tasklist //FI "IMAGENAME eq vivado.exe" //NH 2>/dev/null; tasklist //FI "IMAGENAME eq xsim.exe" //NH 2>/dev/null) | grep -ci 'vivado.exe\|xsim.exe' )"
echo "EXISTING_VIVADO_XSIM_PROCS=$RUNNING"

mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir_run_dir"; exit 3; }
mkdir -p "$EVID" || { echo "FAIL=mkdir_evid"; exit 3; }

# ---- 1) 厂商源码副本 + 补丁 -------------------------------------------------
cp -r "$VENDOR" "$SRC_COPY" || { echo "FAIL=vendor_copy"; exit 3; }
PRISTINE_ACTUAL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
echo "RTL_PRISTINE_SHA256=$PRISTINE_ACTUAL"
if [ "$PRISTINE_ACTUAL" != "$RTL_SHA_PRISTINE" ]; then
  echo "FAIL=pristine_rtl_hash_mismatch:expected=$RTL_SHA_PRISTINE:actual=$PRISTINE_ACTUAL"; exit 4
fi

REL_SRC="tmp/s3r06/$RUN_NAME/vendor_src"
(
  cd "$WT" || exit 3
  echo "CMD=git apply --check -p1 --directory=$REL_SRC $PATCH"
  git apply --check -p1 --directory="$REL_SRC" "$PATCH"
  echo "GIT_APPLY_CHECK_RC=$?"
  echo "CMD=git apply -p1 --directory=$REL_SRC $PATCH"
  git apply -p1 --directory="$REL_SRC" "$PATCH"
  echo "GIT_APPLY_RC=$?"
) > "$EVID/patch_git_apply.log" 2>&1
cat "$EVID/patch_git_apply.log"
GIT_CHECK_RC="$(grep -m1 '^GIT_APPLY_CHECK_RC=' "$EVID/patch_git_apply.log" | cut -d= -f2)"
GIT_APPLY_RC="$(grep -m1 '^GIT_APPLY_RC=' "$EVID/patch_git_apply.log" | cut -d= -f2)"
echo "GIT_CHECK_RC=$GIT_CHECK_RC GIT_APPLY_RC=$GIT_APPLY_RC"

PATCHED_ACTUAL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
echo "RTL_PATCHED_SHA256=$PATCHED_ACTUAL"
if [ "$GIT_CHECK_RC" != "0" ] || [ "$GIT_APPLY_RC" != "0" ] || [ "$PATCHED_ACTUAL" != "$RTL_SHA_PATCHED" ]; then
  echo "FAIL=patch_application:$GIT_CHECK_RC/$GIT_APPLY_RC/$PATCHED_ACTUAL"; exit 4
fi
grep -q "GAP_THRESH" "$SRC_COPY/$RTL_REL" || { echo "FAIL=gap_thresh_not_in_patched_rtl"; exit 4; }
echo "PATCH_VERIFIED=1"
cp -f "$PATCH" "$EVID/alinx_ov5640_sof_hrefgap.patch"

# ---- 2) 覆盖 J11+CMOS2 约束 -------------------------------------------------
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

# ---- 4) 证据留存 -------------------------------------------------------------
cp -f "$RUN_DIR/vivado.log" "$EVID/vivado.log" 2>/dev/null || true
cp -f "$RUN_DIR/vivado.jou" "$EVID/vivado.jou" 2>/dev/null || true
for f in "$RUN_DIR"/report_*.rpt; do [ -f "$f" ] && cp -f "$f" "$EVID/$(basename "$f")" || true; done

export ILA_EVID_DIR="$EVID"
export ILA_RUN_NAME="$RUN_NAME"
export ILA_RUN_DIR="$RUN_DIR"
export ILA_EXIT_CODE="$rc"
export ILA_ELAPSED="$ELAPSED"
export ILA_CMD="$CMD"
export ILA_COMMIT="$COMMIT"
export ILA_BRANCH="$BRANCH"
export ILA_VENDOR="$VENDOR"
export ILA_PATCH="$PATCH"
export ILA_PATCH_SHA="$PATCH_SHA"
export ILA_XDC="$XDC_IN"
export ILA_XDC_SHA="$XDC_SHA"
export ILA_LICENSE="$XILINXD_LICENSE_FILE"
export ILA_RTL_PRISTINE_SHA="$RTL_SHA_PRISTINE"
export ILA_RTL_PATCHED_SHA="$RTL_SHA_PATCHED"
export ILA_GIT_CHECK_RC="$GIT_CHECK_RC"
export ILA_GIT_APPLY_RC="$GIT_APPLY_RC"
export ILA_RTL_REL="$RTL_REL"
export ILA_BASELINE_RUN_ID="$BASELINE_RUN_ID"

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
ver = None
m = re.search(r"Vivado v\.([0-9.]+)", logtxt)
if m: ver = m.group(1)
peaks = [float(x) for x in re.findall(r"Memory \(MB\): peak = ([0-9.]+)", logtxt)]
peak_mb = max(peaks) if peaks else None

def t04val(key):
    m = re.search(r"^T04:\s*%s=(.*)$" % re.escape(key), logtxt, re.M)
    return m.group(1).strip() if m else None

errs  = re.findall(r"^ERROR: \[([^\]]+)\]", logtxt, re.M)
crits = re.findall(r"^CRITICAL WARNING: \[([^\]]+)\]", logtxt, re.M)
warns = re.findall(r"^WARNING: \[([^\]]+)\]", logtxt, re.M)

# DRC（routed）
drc_txt = rt(os.path.join(run_dir, "report_drc_impl.rpt"))
drc_detail = {}
for rule, num, sev in re.findall(r"^([A-Za-z0-9_-]+)#(\d+)\s+(Critical Warning|Error|Warning)\s*$", drc_txt, re.M):
    drc_detail[sev] = drc_detail.get(sev, 0) + 1

# 综合利用率（用于与基线对比 FF 增量，作为补丁进入设计的旁证）
def slice_regs(p):
    txt = rt(p)
    m = re.search(r"^\|\s*Slice Registers\s*\|\s*(\d+)\s*\|", txt, re.M)
    return int(m.group(1)) if m else None

regs_new = slice_regs(os.path.join(run_dir, "report_utilization_synth.rpt"))
base_run = os.environ["ILA_BASELINE_RUN_ID"]
regs_base = slice_regs(os.path.join(os.path.dirname(run_dir), base_run, "report_utilization_synth.rpt"))

# 工程内 IP RTL 副本（证明打过补丁的 RTL 被 IP 生成采用）
rtl_copies = []
for p in glob.glob(os.path.join(run_dir, "project", "**", "alinx_ov5640.v"), recursive=True):
    h = sha256(p)
    rtl_copies.append({
        "path": p,
        "sha256": h,
        "size_bytes": os.path.getsize(p),
        "matches_patched": h == os.environ["ILA_RTL_PATCHED_SHA"],
        "contains_gap_thresh": b"GAP_THRESH" in open(p, "rb").read(),
    })

bit = os.path.join(run_dir, "project", "ov5640_single.runs", "impl_1", "design_1_wrapper.bit")
xsa = os.path.join(run_dir, "design_1_wrapper.xsa")

artifacts = {}
for name, path in (("bit", bit), ("xsa", xsa),
                   ("vivado_log", log),
                   ("report_timing_summary_impl", os.path.join(run_dir, "report_timing_summary_impl.rpt")),
                   ("report_drc_impl", os.path.join(run_dir, "report_drc_impl.rpt")),
                   ("report_utilization_impl", os.path.join(run_dir, "report_utilization_impl.rpt")),
                   ("report_utilization_synth", os.path.join(run_dir, "report_utilization_synth.rpt")),
                   ("patched_rtl", os.path.join(run_dir, "vendor_src", rtl_rel)),
                   ("patch", os.environ["ILA_PATCH"]),
                   ("xdc_j11_cmos2", os.environ["ILA_XDC"])):
    artifacts[name] = {"path": path, "exists": os.path.isfile(path),
                       "size_bytes": os.path.getsize(path) if os.path.isfile(path) else None,
                       "sha256": sha256(path)}

bit_ok = artifacts["bit"]["exists"] and artifacts["xsa"]["exists"]
status = "ok" if (rc == 0 and bit_ok) else "failed"

report = {
    "task_id": "S3-T05-SOF-FIX",
    "task_board_id": "task-2",
    "title": "SOF 修复变体：帧起始改为 hblank 长低电平后的第一个有效像素（不依赖 cmos_vsync）",
    "run_id": os.environ["ILA_RUN_NAME"],
    "run_dir": run_dir,
    "evidence_dir": evid,
    "generated_at_utc8": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "status": status,
    "tool": {"name": "Vivado", "version": ver, "mode": "batch_tcl",
             "license_file": os.environ["ILA_LICENSE"], "flow": "vendor BD auto_create_project (build_t04_camera.tcl)"},
    "baseline": {"worktree": "D:/codex-worktrees/dbdf", "branch": os.environ["ILA_BRANCH"],
                 "commit": os.environ["ILA_COMMIT"], "part": "xc7z020clg400-2",
                 "vendor_source": os.environ["ILA_VENDOR"],
                 "reference_run_id": base_run,
                 "xdc": os.environ["ILA_XDC"], "xdc_sha256": os.environ["ILA_XDC_SHA"]},
    "patch": {
        "file": os.environ["ILA_PATCH"], "sha256": os.environ["ILA_PATCH_SHA"],
        "target_module": "my_ip/ov5640_ip/src/alinx_ov5640.v",
        "change_summary": ("s_axis_tuser 触发由 cmos_vsync 下降沿改为：hblank(=有效像素窗, "
                           "cmos_8_16bit hblank<=de_i) 连续低 >= GAP_THRESH 个 pclk 后的第一个有效像素；"
                           "保留「置起 -> 首个 tvalid 清除」结构；新增 16 位饱和计数器 cmos_hblank_low_cnt；"
                           "新增参数 GAP_THRESH 默认 16'd16384；不 OR 原 vsync 触发；DEBUG_OV5640 仍为 false"),
        "hunks": 3, "lines_added": 24, "lines_removed": 5,
        "pristine_rtl_sha256": os.environ["ILA_RTL_PRISTINE_SHA"],
        "patched_rtl_sha256": os.environ["ILA_RTL_PATCHED_SHA"],
        "git_apply_check_rc": int(os.environ["ILA_GIT_CHECK_RC"]),
        "git_apply_rc": int(os.environ["ILA_GIT_APPLY_RC"]),
        "git_apply_command": "git apply -p1 --directory=<run>/vendor_src <patch>（从工作树根执行）",
        "gnu_patch_note": "GNU patch -p1 对该 CRLF 文件报 'different line endings' 而失败；本流程统一用 git apply。",
        "patch_application_log": os.path.join(evid, "patch_git_apply.log"),
    },
    "timing_design_basis": {
        "source": "厂商驱动 Vitis/auto_create_vitis/src/an5642_single/ov5640.c（1280x720 模式寄存器表）",
        "pclk_hz": 84000000, "hts": 1892, "vts": 740, "active_w": 1280, "active_h": 720,
        "line_blank_pclk": 612, "field_blank_pclk": 38452,
        "gap_thresh_default": 16384,
        "check": "612 < 16384 < 38452（阈值必须严格位于行消隐与场消隐之间）",
        "note": ("与阶段总控给出的估算（行周期约 3784 pclk、HBLANK 约 2.5k）不一致："
                 "驱动寄存器 0x380c/0x380d=0x0764 -> HTS=1892，0x380e/0x380f=0x02e4 -> VTS=740，"
                 "故行周期 1892 pclk、行消隐 612 pclk、场消隐 ≈38452 pclk；PCLK=84MHz（0x3035=0x21,0x3036=0x69）"
                 "与此一致（1892*740/84e6 = 16.67ms = 60fps）。默认阈值 16384 仍同时满足两侧约束。"),
    },
    "commands": {"build": os.environ["ILA_CMD"], "tcl_script": "scripts/stage3_t04/build_t04_camera.tcl",
                 "vivado_exit_code": rc, "elapsed_seconds": int(os.environ["ILA_ELAPSED"])},
    "implementation": {
        "synth_status": t04val("SYNTH_STATUS"), "impl_status": t04val("IMPL_STATUS"),
        "timing": {"wns_ns": t04val("TIMING_WNS"), "tns_ns": t04val("TIMING_TNS"),
                   "whs_ns": t04val("TIMING_WHS"), "ths_ns": t04val("TIMING_THS")},
        "drc_error_count": drc_detail.get("Error", 0),
        "drc_critical_warning_count": drc_detail.get("Critical Warning", 0),
        "drc_warning_count": drc_detail.get("Warning", 0),
        "peak_memory_mb": peak_mb,
        "slice_registers_synth": regs_new,
        "slice_registers_synth_baseline": regs_base,
        "slice_registers_delta_vs_baseline": (regs_new - regs_base) if (regs_new is not None and regs_base is not None) else None,
        "xsa_exists": t04val("XSA_EXISTS"),
    },
    "rtl_evidence": {
        "project_rtl_copies": rtl_copies,
        "any_copy_matches_patched": any(c["matches_patched"] for c in rtl_copies),
        "any_copy_contains_gap_thresh": any(c["contains_gap_thresh"] for c in rtl_copies),
        "meaning": "工程 .gen 下的 IP RTL 副本哈希等于补丁后 RTL 哈希，证明打过补丁的 RTL 被本次 IP 生成/综合采用。",
    },
    "log_messages": {"error_count": len(errs), "critical_warning_count": len(crits),
                     "warning_count": len(warns), "error_codes": sorted(set(errs))[:40],
                     "critical_warning_codes": sorted(set(crits))[:40]},
    "artifacts": artifacts,
    "limitations": [
        "只产出 bitstream + XSA，未下载、未烧 QSPI、未连接硬件（下载与上板验收由阶段总控执行）。",
        "未做 RTL 功能仿真（本任务未要求；无既有 testbench），SOF 修复的正确性靠时序核算 + 上板实测验证。",
        "复位后第一帧可能没有 SOF（cmos_aresetn 由 200M 个 pclk 计数器保持低约 2.4s，复位释放后若正处于行消隐，"
        "计数器尚未达到阈值）；从第二个场消隐起每个场消隐都必然超过 GAP_THRESH。",
        "GAP_THRESH=16384 的适用前提是 1280x720（HTS=1892/VTS=740）：若换成垂直消隐更短的模式，"
        "需重新核算阈值（阈值必须 < 场消隐 pclk 数）。",
        "帧起始改为「hblank 长低后的第一个有效像素」，等价于该帧第一行第一个有效像素；"
        "若传感器在行消隐期间出现 >=16384 pclk 的异常停顿，会误产生一次 SOF（本模式下行消隐仅 612 pclk）。",
        "未验证位流与基线功能一致性（除时序/DRC/资源对比外）。",
    ],
    "not_executed": ["program_device / QSPI 烧写", "上板图像与 VDMA S2MM SR 验证",
                     "RTL 仿真", "ILA 采集（见 t05_ila_20261020_r01 证据）", "Git 提交（由阶段总控统一提交）"],
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
print("RTL_COPY_MATCHES_PATCHED=%s" % report["rtl_evidence"]["any_copy_matches_patched"])
print("SLICE_REGS new=%s base=%s delta=%s" % (regs_new, regs_base, report["implementation"]["slice_registers_delta_vs_baseline"]))
PY

echo "EVIDENCE_JSON=$EVID/build_report.json"
exit "$rc"