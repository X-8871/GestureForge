#!/usr/bin/env bash
# =============================================================================
# 阶段3 S3-T05-PL1「蓝最高位重建变体」启动器
#
# 目的：RGB565 的 B[4]（蓝最高位）实测恒为 0 -> 蓝色动态范围减半、画面偏黄。
#       在 PL 侧用 B[3] 重建 B[4]（近似修复）：B'[4:0] = {B[3:0], B[3]}，
#       即 new_word = {tdata[15:5], tdata[3:0], tdata[3]}。
#
# 流程（沿用 J11+CMOS2 变体）：复制 vendor_src
#   -> git apply 补丁1 alinx_ov5640_sof_hrefgap.patch（SOF 修复）
#   -> git apply 补丁2 alinx_ov5640_blue_msb_rebuild.patch（蓝位重建）
#   -> 覆盖 an5642_j11_cmos2.xdc -> 构建 bitstream + XSA
#
# 已实测：两个补丁互不重叠，A) BLUE 单独对厂商原件可应用、B) SOF->BLUE、C) BLUE->SOF
# 顺序皆 RC=0 且结果字节相同（见证据 patch_apply_order_test.txt）。
#
# 用法: bash run_t04_camera_j11cmos2_bluefix_build.sh <run_name>
#   例: bash run_t04_camera_j11cmos2_bluefix_build.sh t04_bluefix_20261020_r01
#
# 只写本 RunId 目录与 S3-T05 证据目录；不提交 Git、不烧 QSPI、不上板。
# =============================================================================
set -u

RUN_NAME="${1:?需要 run 目录名，例如 t04_bluefix_20261020_r01}"

WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
SRC_COPY="$RUN_DIR/vendor_src"
XDC_IN="$WT/board/stage3/hardware/an5642_j11_cmos2.xdc"
PATCH_SOF="$WT/board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
PATCH_BLUE="$WT/board/stage3/software/sensor/alinx_ov5640_blue_msb_rebuild.patch"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
TCL="$WT/scripts/stage3_t04/build_t04_camera.tcl"
EVID="$WT/report/evidence/S3-T05/t05_bluefix_20261020_r01"
LIC="D:/Xilinx_licenses/basic_only.lic"
RTL_REL="my_ip/ov5640_ip/src/alinx_ov5640.v"

# 确定哈希（补丁生成器给出，作为硬断言）
RTL_SHA_PRISTINE="98260b62f996ec700eb766c6c4e57706b2c1ff3a8224a5105a3641b6475b3e4d"
RTL_SHA_AFTER_SOF="db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6"
RTL_SHA_AFTER_BLUE="91b67c1e0149255112b085b1c737b39f737aec52a4baee97144e8839408b4cec"
PATCH_SOF_SHA="fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5"
PATCH_BLUE_SHA="6609a59da624beb562a5a717e4839567f803bd80e7df0a5ca9ce4e4ff5ec7505"
BASELINE_RUNS="t04_camera_j11cmos2_20261020_r01 t04_sof_fix_20261020_r01"

export XILINXD_LICENSE_FILE="$LIC"

echo "LAUNCHER=gitbash"
echo "RUN_DIR=$RUN_DIR"
echo "PATCH_SOF=$PATCH_SOF"
echo "PATCH_BLUE=$PATCH_BLUE"
echo "XDC_IN=$XDC_IN"
echo "EVID=$EVID"
echo "LICENSE=$XILINXD_LICENSE_FILE"

TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
[ "$TOP" = "$WT" ] || { echo "FAIL=worktree_selfcheck:$TOP"; exit 3; }
[ -e "$RUN_DIR" ] && { echo "FAIL=run_dir_exists"; exit 3; }
[ -d "$VENDOR" ] || { echo "FAIL=vendor_missing"; exit 3; }
[ -f "$PATCH_SOF" ] || { echo "FAIL=patch_sof_missing"; exit 3; }
[ -f "$PATCH_BLUE" ] || { echo "FAIL=patch_blue_missing"; exit 3; }
[ -f "$XDC_IN" ] || { echo "FAIL=xdc_missing"; exit 3; }
[ -f "$TCL" ] || { echo "FAIL=tcl_missing"; exit 3; }
[ -f "$LIC" ] || { echo "FAIL=license_missing"; exit 3; }

COMMIT="$(git -C "$WT" rev-parse HEAD)"
BRANCH="$(git -C "$WT" rev-parse --abbrev-ref HEAD)"
SOF_SHA_ACTUAL="$(sha256sum "$PATCH_SOF" | awk '{print $1}')"
BLUE_SHA_ACTUAL="$(sha256sum "$PATCH_BLUE" | awk '{print $1}')"
XDC_SHA="$(sha256sum "$XDC_IN" | awk '{print $1}')"
echo "BASELINE_COMMIT=$COMMIT"
echo "BASELINE_BRANCH=$BRANCH"
echo "PATCH_SOF_SHA256=$SOF_SHA_ACTUAL"
echo "PATCH_BLUE_SHA256=$BLUE_SHA_ACTUAL"
echo "XDC_SHA256=$XDC_SHA"
[ "$SOF_SHA_ACTUAL" = "$PATCH_SOF_SHA" ] || { echo "FAIL=sof_patch_sha_mismatch"; exit 4; }
[ "$BLUE_SHA_ACTUAL" = "$PATCH_BLUE_SHA" ] || { echo "FAIL=blue_patch_sha_mismatch"; exit 4; }

RUNNING="$( (tasklist //FI "IMAGENAME eq vivado.exe" //NH 2>/dev/null; tasklist //FI "IMAGENAME eq xsim.exe" //NH 2>/dev/null) | grep -ci 'vivado.exe\|xsim.exe' )"
echo "EXISTING_VIVADO_XSIM_PROCS=$RUNNING"

mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir_run_dir"; exit 3; }
mkdir -p "$EVID" || { echo "FAIL=mkdir_evid"; exit 3; }

# ---- 1) vendor 副本 + 依次应用两个补丁 -------------------------------------
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
  echo "== patch 2/2: BLUE =="
  echo "CMD=git apply --check -p1 --directory=$REL_SRC $PATCH_BLUE"
  git apply --check -p1 --directory="$REL_SRC" "$PATCH_BLUE"; echo "BLUE_CHECK_RC=$?"
  echo "CMD=git apply -p1 --directory=$REL_SRC $PATCH_BLUE"
  git apply -p1 --directory="$REL_SRC" "$PATCH_BLUE"; echo "BLUE_APPLY_RC=$?"
  echo "RTL_AFTER_BLUE_SHA256=$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
) > "$EVID/patch_git_apply.log" 2>&1
cat "$EVID/patch_git_apply.log"

get_rc() { grep -m1 "^$1=" "$EVID/patch_git_apply.log" | cut -d= -f2; }
SOF_CHECK_RC="$(get_rc SOF_CHECK_RC)"; SOF_APPLY_RC="$(get_rc SOF_APPLY_RC)"
BLUE_CHECK_RC="$(get_rc BLUE_CHECK_RC)"; BLUE_APPLY_RC="$(get_rc BLUE_APPLY_RC)"
echo "SOF_CHECK_RC=$SOF_CHECK_RC SOF_APPLY_RC=$SOF_APPLY_RC BLUE_CHECK_RC=$BLUE_CHECK_RC BLUE_APPLY_RC=$BLUE_APPLY_RC"

AFTER_SOF_ACTUAL="$(sha256sum "$SRC_COPY/$RTL_REL" | awk '{print $1}')"
# 说明：上一步已同时应用两个补丁，故此处只校验最终结果
FINAL_ACTUAL="$AFTER_SOF_ACTUAL"
echo "RTL_FINAL_SHA256=$FINAL_ACTUAL"
if [ "$SOF_CHECK_RC" != "0" ] || [ "$SOF_APPLY_RC" != "0" ] || [ "$BLUE_CHECK_RC" != "0" ] || [ "$BLUE_APPLY_RC" != "0" ]; then
  echo "FAIL=patch_application_rc:$SOF_CHECK_RC/$SOF_APPLY_RC/$BLUE_CHECK_RC/$BLUE_APPLY_RC"; exit 4
fi
if [ "$FINAL_ACTUAL" != "$RTL_SHA_AFTER_BLUE" ]; then
  echo "FAIL=final_rtl_hash_mismatch:expected=$RTL_SHA_AFTER_BLUE:actual=$FINAL_ACTUAL"; exit 4
fi
grep -q "GAP_THRESH" "$SRC_COPY/$RTL_REL" || { echo "FAIL=sof_patch_marker_missing"; exit 4; }
grep -q "s_axis_tdata_bluefix" "$SRC_COPY/$RTL_REL" || { echo "FAIL=blue_patch_marker_missing"; exit 4; }
echo "PATCHES_VERIFIED=1"

cp -f "$PATCH_SOF" "$EVID/alinx_ov5640_sof_hrefgap.patch"
cp -f "$PATCH_BLUE" "$EVID/alinx_ov5640_blue_msb_rebuild.patch"

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
export ILA_PATCH_SOF="$PATCH_SOF"
export ILA_PATCH_SOF_SHA="$SOF_SHA_ACTUAL"
export ILA_PATCH_BLUE="$PATCH_BLUE"
export ILA_PATCH_BLUE_SHA="$BLUE_SHA_ACTUAL"
export ILA_XDC="$XDC_IN"
export ILA_XDC_SHA="$XDC_SHA"
export ILA_LICENSE="$XILINXD_LICENSE_FILE"
export ILA_RTL_PRISTINE_SHA="$RTL_SHA_PRISTINE"
export ILA_RTL_AFTER_SOF_SHA="$RTL_SHA_AFTER_SOF"
export ILA_RTL_AFTER_BLUE_SHA="$RTL_SHA_AFTER_BLUE"
export ILA_SOF_CHECK_RC="$SOF_CHECK_RC"
export ILA_SOF_APPLY_RC="$SOF_APPLY_RC"
export ILA_BLUE_CHECK_RC="$BLUE_CHECK_RC"
export ILA_BLUE_APPLY_RC="$BLUE_APPLY_RC"
export ILA_RTL_REL="$RTL_REL"
export ILA_BASELINE_RUNS="$BASELINE_RUNS"

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
drc_detail = {}
drc_rules = {}
for rule, num, sev in re.findall(r"^([A-Za-z0-9_-]+)#(\d+)\s+(Critical Warning|Error|Warning)\s*$", drc_txt, re.M):
    drc_detail[sev] = drc_detail.get(sev, 0) + 1
    drc_rules[rule] = drc_rules.get(rule, 0) + 1

def slice_regs(path):
    txt = rt(path)
    m = re.search(r"^\|\s*Slice Registers\s*\|\s*(\d+)\s*\|", txt, re.M)
    return int(m.group(1)) if m else None

sib = os.path.dirname(run_dir)
base_runs = os.environ["ILA_BASELINE_RUNS"].split()
regs = {}
for r in base_runs + [os.environ["ILA_RUN_NAME"]]:
    regs[r] = {
        "design_synth": slice_regs(os.path.join(sib, r, "report_utilization_synth.rpt")),
        "alinx_ip_ooc": slice_regs(os.path.join(
            sib, r, "project", "ov5640_single.runs",
            "design_1_alinx_ov5640_0_0_synth_1",
            "design_1_alinx_ov5640_0_0_utilization_synth.rpt")),
    }

rtl_copies = []
for p in glob.glob(os.path.join(run_dir, "project", "**", "alinx_ov5640.v"), recursive=True):
    blob = open(p, "rb").read()
    rtl_copies.append({
        "path": p,
        "sha256": sha256(p),
        "size_bytes": os.path.getsize(p),
        "matches_final": sha256(p) == os.environ["ILA_RTL_AFTER_BLUE_SHA"],
        "contains_gap_thresh": b"GAP_THRESH" in blob,
        "contains_bluefix": b"s_axis_tdata_bluefix" in blob,
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
                   ("patch_sof", os.environ["ILA_PATCH_SOF"]),
                   ("patch_blue", os.environ["ILA_PATCH_BLUE"]),
                   ("xdc_j11_cmos2", os.environ["ILA_XDC"])):
    artifacts[name] = {"path": path, "exists": os.path.isfile(path),
                       "size_bytes": os.path.getsize(path) if os.path.isfile(path) else None,
                       "sha256": sha256(path)}

bit_ok = artifacts["bit"]["exists"] and artifacts["xsa"]["exists"]
status = "ok" if (rc == 0 and bit_ok) else "failed"

report = {
    "task_id": "S3-T05-PL1",
    "task_board_id": "task-6",
    "title": "蓝最高位（RGB565 B[4]）重建变体：B'[4:0]={B[3:0],B[3]} 于厂商 IP 内，构建到比特流+XSA",
    "run_id": os.environ["ILA_RUN_NAME"],
    "run_dir": run_dir,
    "evidence_dir": evid,
    "generated_at_utc8": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "status": status,
    "tool": {"name": "Vivado", "version": ver, "mode": "batch_tcl",
             "license_file": os.environ["ILA_LICENSE"],
             "flow": "vendor BD auto_create_project (build_t04_camera.tcl)"},
    "baseline": {"worktree": "D:/codex-worktrees/dbdf", "branch": os.environ["ILA_BRANCH"],
                 "commit_at_build": os.environ["ILA_COMMIT"], "part": "xc7z020clg400-2",
                 "vendor_source": os.environ["ILA_VENDOR"],
                 "compare_runs": base_runs,
                 "xdc": os.environ["ILA_XDC"], "xdc_sha256": os.environ["ILA_XDC_SHA"]},
    "patches": {
        "applied_order": ["alinx_ov5640_sof_hrefgap.patch", "alinx_ov5640_blue_msb_rebuild.patch"],
        "target_module": "my_ip/ov5640_ip/src/alinx_ov5640.v",
        "items": [
            {"name": "SOF fix (task-2)", "file": os.environ["ILA_PATCH_SOF"],
             "sha256": os.environ["ILA_PATCH_SOF_SHA"], "hunks": 3, "lines_added": 24, "lines_removed": 5,
             "change_summary": "s_axis_tuser 触发改为 hblank 长低电平后的第一个有效像素（GAP_THRESH=16384，16 位饱和计数器）",
             "git_apply_check_rc": int(os.environ["ILA_SOF_CHECK_RC"]),
             "git_apply_rc": int(os.environ["ILA_SOF_APPLY_RC"])},
            {"name": "BLUE MSB rebuild (this task)", "file": os.environ["ILA_PATCH_BLUE"],
             "sha256": os.environ["ILA_PATCH_BLUE_SHA"], "hunks": 3, "lines_added": 5, "lines_removed": 2,
             "change_summary": ("新增 wire s_axis_tdata_bluefix = {s_axis_tdata[15:5], s_axis_tdata[3:0], s_axis_tdata[3]}；"
                                "FIFO .din(...) 与（关闭的）ILA 探针 .probe0 改用它；仅 bit[4] 改变，"
                                "tlast/tuser/tkeep/时序不动"),
             "git_apply_check_rc": int(os.environ["ILA_BLUE_CHECK_RC"]),
             "git_apply_rc": int(os.environ["ILA_BLUE_APPLY_RC"])},
        ],
        "order_conflict_analysis": ("两个补丁修改区域互不重叠（SOF 改参数表/tuser always 块；BLUE 改 s_axis_tdata 声明后、"
                                    "ILA probe0、FIFO din），实测 A) BLUE 单独对厂商原件 --check/apply RC=0；"
                                    "B) SOF->BLUE 四个操作全 RC=0；C) BLUE->SOF 亦全 RC=0 且最终字节相同（幂等/可交换）。"
                                    "本构建按卡面要求采用 SOF->BLUE 顺序。"),
        "order_test_evidence": "report/evidence/S3-T05/t05_bluefix_20261020_r01/patch_apply_order_test.txt",
        "git_apply_log": "report/evidence/S3-T05/t05_bluefix_20261020_r01/patch_git_apply.log",
        "git_apply_note": "git apply 必须从工作树根执行并配 --directory=<相对路径>；补丁内容行保留 CRLF，GNU patch 不适用。",
    },
    "rtl_hashes": {
        "pristine_vendor": os.environ["ILA_RTL_PRISTINE_SHA"],
        "after_sof_patch": os.environ["ILA_RTL_AFTER_SOF_SHA"],
        "after_sof_then_blue": os.environ["ILA_RTL_AFTER_BLUE_SHA"],
        "final_actual": artifacts["patched_rtl"]["sha256"],
    },
    "blue_fix": {
        "problem_evidence": ("阶段总控 4 组独立实测（白纸 / 实景 AWB 开 / 实景 AWB 关 / 彩条）统计一致："
                             "蓝通道最大值恒为 120、从无 >127 的蓝像素，而 R 可达 248、G 可达 236 "
                             "=> RGB565 的 B[4] 恒为 0，蓝色动态范围减半，画面偏黄；AWB/ISP/显示器均已排除。"
                             "依据厂商 IP 取 cmos_d[9:2] 当字节，RGB565 第二字节 = {G[2:0],B[4:0]}，"
                             "缺失位对应 DVP 的 D[6] 线（断线或映射错仍在核，与重建位无关）。"),
        "field_layout": "R=tdata[15:11](5b), G=tdata[10:5](6b), B=tdata[4:0](5b)",
        "rebuild_formula": "B'[4:0] = {B[3:0], B[3]}  <=>  new_word = {tdata[15:5], tdata[3:0], tdata[3]}",
        "equivalence_note": "该式只把 bit[4] 由常量 0 换成原 bit[3]，其余 15 位逐位不变，故只恢复一半量化台阶。",
        "known_error": ("把 B[3] 复制到 B[4] 等价于把蓝通道的低 4 位区间做 2 倍拉伸，蓝值 b(0..15) 映射为 "
                        "b' = b + (b>=8 ? 16 : 0)（以 5 位蓝计），在蓝淡色区（B 小）误差相对最大、"
                        "深蓝区相对准确；AWB 会在此基础上再自适应调整，可能掩盖或加重该误差。"
                        "因此这是近似修复，不是恢复真实位。"),
        "not_changed": ["tlast", "tuser", "tkeep", "时序/时钟", "DEBUG_OV5640（保持 false，未打开厂商内嵌 6 探针 ILA）"],
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
        "drc_counts_by_severity": dict(drc_detail),
        "drc_rule_breakdown": dict(drc_rules),
        "peak_memory_mb": peak_mb,
        "utilization_by_run": regs,
        "xsa_exists": t04val("XSA_EXISTS"),
    },
    "rtl_evidence": {
        "project_rtl_copies": rtl_copies,
        "meaning": ("工程 .gen 下 IP RTL 副本哈希等于两补丁叠加后的 RTL 哈希，且同时含 GAP_THRESH 与 "
                    "s_axis_tdata_bluefix，证明两个补丁都被本次 IP 生成/综合采用。"),
    },
    "log_messages": {"error_count": len(errs), "critical_warning_count": len(crits),
                     "warning_count": len(warns), "error_codes": sorted(set(errs))[:40],
                     "critical_warning_codes": sorted(set(crits))[:40]},
    "artifacts": artifacts,
    "limitations": [
        "只产出 bitstream + XSA；未下载、未烧 QSPI、未上板（上板与判读由阶段总控执行）。",
        "蓝位重建是近似修复：B'[4:0]={B[3:0],B[3]} 把 B[3] 复制到 B[4]，蓝淡色区误差相对最大，且 AWB 会再自适应调整。",
        "未做 RTL 功能仿真（无既有 testbench）；SOF 与蓝位两处改动的正确性靠时序核算 + 上板实测验证。",
        "SOF 修复的既有约束仍成立：复位后第一帧可能无 SOF；GAP_THRESH=16384 只对 1280x720(HTS=1892/VTS=740) 成立。",
        "根因（DVP D[6] 断线或映射错）未在本任务定位与修复，本变体只是绕过。",
        "未验证位流与基线功能一致性（仅时序/DRC/资源对比）。",
    ],
    "not_executed": ["program_device / QSPI 烧写", "上板颜色/蓝通道直方图判读", "RTL 仿真",
                     "根因定位（D[6] 线断/映射）", "Git 提交（由阶段总控统一提交）"],
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
print("RTL_COPY_MATCHES_FINAL=%s" % any(c["matches_final"] for c in rtl_copies))
print("UTIL=%s" % json.dumps(regs))
PY

echo "EVIDENCE_JSON=$EVID/build_report.json"
exit "$rc"