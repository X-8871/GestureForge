#!/usr/bin/env bash
# =============================================================================
# 阶段3 S3-T05-ILA「BD 内实例化 ILA」路线启动器（总控 2026-10-20 裁决后启用）
#
# 背景：网表插入路线被 BASIC 许可直接否决
#   ERROR: [Vivado 12-29205] 'create_debug_core' tcl command is not supported.
#   Your current selected license is BASIC.
# 本启动器先做便宜的许可预检（precheck，不建 RunId），通过后才做完整 BD 重建。
#
# 用法: bash run_t04_ila_bd_build.sh <run_name>
#   例: bash run_t04_ila_bd_build.sh t04_ila_bd_20261020_r01
#
# 只写本 RunId 目录与 S3-T05 证据目录；不提交 Git、不烧录、不连硬件。
# =============================================================================
set -u

RUN_NAME="${1:?需要 run 目录名，例如 t04_ila_bd_20261020_r01}"

WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VENDOR_ORIG="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
VENDOR_COPY="$RUN_DIR/vendor_src"
XDC_IN="$WT/board/stage3/hardware/an5642_j11_cmos2.xdc"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
TCL="$WT/scripts/stage3_t04/bd_insert_ila.tcl"
EVID="$WT/report/evidence/S3-T05/t05_ila_20261020_r01"
LIC="D:/Xilinx_licenses/basic_only.lic"

export XILINXD_LICENSE_FILE="$LIC"

echo "LAUNCHER=gitbash"
echo "ROUTE=bd_ip_instantiation"
echo "RUN_DIR=$RUN_DIR"
echo "VENDOR_ORIG=$VENDOR_ORIG"
echo "XDC_IN=$XDC_IN"
echo "EVID=$EVID"
echo "LICENSE=$XILINXD_LICENSE_FILE"

TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
if [ "$TOP" != "$WT" ]; then echo "FAIL=worktree_selfcheck:$TOP"; exit 3; fi
if [ -e "$RUN_DIR" ]; then echo "FAIL=run_dir_exists"; exit 3; fi
[ -d "$VENDOR_ORIG" ] || { echo "FAIL=vendor_missing:$VENDOR_ORIG"; exit 3; }
[ -f "$XDC_IN" ]      || { echo "FAIL=xdc_missing:$XDC_IN"; exit 3; }
[ -f "$TCL" ]         || { echo "FAIL=tcl_missing:$TCL"; exit 3; }
[ -f "$LIC" ]         || { echo "FAIL=license_missing:$LIC"; exit 3; }

COMMIT="$(git -C "$WT" rev-parse HEAD)"
BRANCH="$(git -C "$WT" rev-parse --abbrev-ref HEAD)"
XDC_SHA="$(sha256sum "$XDC_IN" | awk '{print $1}')"
echo "BASELINE_COMMIT=$COMMIT"
echo "BASELINE_BRANCH=$BRANCH"
echo "XDC_SHA256=$XDC_SHA"

RUNNING="$( (tasklist //FI "IMAGENAME eq vivado.exe" //NH 2>/dev/null; tasklist //FI "IMAGENAME eq xsim.exe" //NH 2>/dev/null) | grep -ci 'vivado.exe\|xsim.exe' )"
echo "EXISTING_VIVADO_XSIM_PROCS=$RUNNING"

mkdir -p "$EVID" || { echo "FAIL=mkdir_evidence_dir"; exit 3; }

# ---- 阶段 A：许可预检（不建 RunId；在独立 scratch 目录里跑，避免污染工作树根） ----
PRECHECK_LOG="$EVID/ila_ip_precheck.log"
PRECHECK_SCRATCH="$EVID/precheck_scratch"
mkdir -p "$PRECHECK_SCRATCH" || { echo "FAIL=mkdir_precheck_scratch"; exit 3; }
PRECHECK_CMD="$VIVADO -mode batch -source $TCL -log $PRECHECK_LOG -journal $EVID/ila_ip_precheck.jou -tclargs precheck $EVID"
echo "PRECHECK_CMD=$PRECHECK_CMD"
echo "PRECHECK_CWD=$PRECHECK_SCRATCH"
( cd "$PRECHECK_SCRATCH" && "$VIVADO" -mode batch -source "$TCL" -log "$PRECHECK_LOG" \
    -journal "$EVID/ila_ip_precheck.jou" -tclargs precheck "$EVID" )
pre_rc=$?
echo "PRECHECK_EXIT=$pre_rc"
# scratch 清理（仅当路径确为证据目录下的 precheck_scratch）
case "$PRECHECK_SCRATCH" in
  "$EVID"/precheck_scratch) rm -rf "$PRECHECK_SCRATCH" ;;
  *) echo "WARN=skip_precheck_scratch_cleanup:$PRECHECK_SCRATCH" ;;
esac

if [ "$pre_rc" -ne 0 ]; then
  echo "PRECHECK_RESULT=BLOCKED_OR_FAILED"
  export ILA_EVID_DIR="$EVID"
  export ILA_RUN_NAME="$RUN_NAME"
  export ILA_PRECHECK_RC="$pre_rc"
  export ILA_PRECHECK_LOG="$PRECHECK_LOG"
  export ILA_COMMIT="$COMMIT"; export ILA_BRANCH="$BRANCH"
  python -B - <<'PY'
import hashlib, json, os
def sha256(p):
    if not os.path.isfile(p): return None
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(1<<20), b''): h.update(c)
    return h.hexdigest()
evid = os.environ["ILA_EVID_DIR"]
log  = os.environ["ILA_PRECHECK_LOG"]
rep = {
  "task_id": "S3-T05-ILA",
  "route": "bd_ip_instantiation",
  "run_id": os.environ["ILA_RUN_NAME"],
  "run_dir": None,
  "status": "failed",
  "failure_stage": "precheck_ip_license",
  "precheck": {"exit_code": int(os.environ["ILA_PRECHECK_RC"]),
               "log": log, "log_sha256": sha256(log)},
  "baseline": {"worktree": "D:/codex-worktrees/dbdf",
               "branch": os.environ["ILA_BRANCH"], "commit": os.environ["ILA_COMMIT"]},
  "conclusion": "未通过许可预检：ILA IP 在当前 BASIC 许可下不可实例化/生成；未创建 RunId、未做实现。",
  "not_executed": ["BD 重建", "synth/impl", "write_bitstream", "write_debug_probes", "上板采集"],
}
with open(os.path.join(evid, "build_report_bd.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=2); f.write("\n")
print("BUILD_REPORT_BD=%s" % os.path.join(evid, "build_report_bd.json"))
PY
  exit "$pre_rc"
fi
echo "PRECHECK_RESULT=PASS"

# ---- 阶段 A2：BD 连接审计（scratch；不建 RunId） ---------------------------
# 目的：显式 connect_bd_net 接 AXI-Stream 接口成员（TUSER/TLAST）会触发
# BD 41-1306 覆盖告警；此处先在 scratch 里只建 BD 并核对连接是否被破坏，
# 通过后才消耗 RunId 做完整综合/实现。
AUDIT_LOG="$EVID/ila_bd_connect_audit.log"
AUDIT_SCRATCH="$EVID/bdaudit_scratch"
mkdir -p "$AUDIT_SCRATCH" || { echo "FAIL=mkdir_audit_scratch"; exit 3; }
AUDIT_CMD="$VIVADO -mode batch -source $TCL -log $AUDIT_LOG -journal $EVID/ila_bd_connect_audit.jou -tclargs bdaudit $AUDIT_SCRATCH $VENDOR_ORIG"
echo "AUDIT_CMD=$AUDIT_CMD"
"$VIVADO" -mode batch -source "$TCL" -log "$AUDIT_LOG" \
  -journal "$EVID/ila_bd_connect_audit.jou" -tclargs bdaudit "$AUDIT_SCRATCH" "$VENDOR_ORIG"
audit_rc=$?
echo "AUDIT_EXIT=$audit_rc"
[ -f "$AUDIT_SCRATCH/_ila_connect_audit.txt" ] && cp -f "$AUDIT_SCRATCH/_ila_connect_audit.txt" "$EVID/ila_bd_connect_audit.txt" || true
case "$AUDIT_SCRATCH" in
  "$EVID"/bdaudit_scratch) rm -rf "$AUDIT_SCRATCH" ;;
  *) echo "WARN=skip_audit_scratch_cleanup:$AUDIT_SCRATCH" ;;
esac
if [ "$audit_rc" -ne 0 ]; then
  echo "AUDIT_RESULT=FAILED"
  export ILA_EVID_DIR="$EVID"
  export ILA_RUN_NAME="$RUN_NAME"
  export ILA_AUDIT_RC="$audit_rc"
  export ILA_AUDIT_LOG="$AUDIT_LOG"
  export ILA_COMMIT="$COMMIT"; export ILA_BRANCH="$BRANCH"
  python -B - <<'PY'
import hashlib, json, os
def sha256(p):
    if not os.path.isfile(p): return None
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(1<<20), b''): h.update(c)
    return h.hexdigest()
evid = os.environ["ILA_EVID_DIR"]
log  = os.environ["ILA_AUDIT_LOG"]
rep = {
  "task_id": "S3-T05-ILA", "route": "bd_ip_instantiation",
  "run_id": os.environ["ILA_RUN_NAME"], "run_dir": None, "status": "failed",
  "failure_stage": "bd_connect_audit",
  "bd_connect_audit": {"exit_code": int(os.environ["ILA_AUDIT_RC"]),
                       "log": log, "log_sha256": sha256(log)},
  "baseline": {"worktree": "D:/codex-worktrees/dbdf",
               "branch": os.environ["ILA_BRANCH"], "commit": os.environ["ILA_COMMIT"]},
  "conclusion": "BD 级连接审计未通过：ILA 显式接入破坏了 AXI-Stream 接口成员网，或对象解析为空；未创建 RunId、未综合/实现。",
  "not_executed": ["synth", "impl", "write_bitstream", "write_debug_probes", "上板采集"],
}
with open(os.path.join(evid, "build_report_bd.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=2); f.write("\n")
print("BUILD_REPORT_BD=%s" % os.path.join(evid, "build_report_bd.json"))
PY
  exit "$audit_rc"
fi
echo "AUDIT_RESULT=PASS"

# ---- 阶段 B：完整 BD 重建 --------------------------------------------------
mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir_run_dir"; exit 3; }
cp -r "$VENDOR_ORIG" "$VENDOR_COPY" || { echo "FAIL=vendor_copy"; exit 3; }
cp "$XDC_IN" "$VENDOR_COPY/src/constraints/an5642.xdc" || { echo "FAIL=xdc_replace"; exit 3; }
for pin in F17 F16 F19 L19 K19; do
  grep -q "$pin" "$VENDOR_COPY/src/constraints/an5642.xdc" || { echo "FAIL=pin_not_found:$pin"; exit 3; }
done
echo "CMOS2_PINS_VERIFIED=1"

BUILD_CMD="$VIVADO -mode batch -source $TCL -log $RUN_DIR/vivado_ila_bd.log -journal $RUN_DIR/vivado_ila_bd.jou -tclargs build $RUN_DIR $VENDOR_COPY $XDC_IN"
echo "BUILD_CMD=$BUILD_CMD"
START_EPOCH=$(date +%s)
"$VIVADO" -mode batch -source "$TCL" \
  -log "$RUN_DIR/vivado_ila_bd.log" -journal "$RUN_DIR/vivado_ila_bd.jou" \
  -tclargs build "$RUN_DIR" "$VENDOR_COPY" "$XDC_IN"
rc=$?
END_EPOCH=$(date +%s)
ELAPSED=$((END_EPOCH - START_EPOCH))
echo "VIVADO_EXIT=$rc"
echo "ELAPSED_SECONDS=$ELAPSED"

cp -f "$RUN_DIR/vivado_ila_bd.log" "$EVID/vivado_ila_bd.log" 2>/dev/null || true
cp -f "$RUN_DIR/vivado_ila_bd.jou" "$EVID/vivado_ila_bd.jou" 2>/dev/null || true
[ -f "$RUN_DIR/ila_bd_netmap.txt" ] && cp -f "$RUN_DIR/ila_bd_netmap.txt" "$EVID/ila_bd_netmap.txt" || true
[ -f "$RUN_DIR/ila_bd_status.txt" ] && cp -f "$RUN_DIR/ila_bd_status.txt" "$EVID/ila_bd_status.txt" || true
if [ -d "$RUN_DIR/impl_ila" ]; then
  for f in "$RUN_DIR"/impl_ila/*.rpt; do [ -f "$f" ] && cp -f "$f" "$EVID/" || true; done
fi
cp -f "$PRECHECK_LOG" "$EVID/ila_ip_precheck.log" 2>/dev/null || true

export ILA_EVID_DIR="$EVID"
export ILA_RUN_NAME="$RUN_NAME"
export ILA_RUN_DIR="$RUN_DIR"
export ILA_EXIT_CODE="$rc"
export ILA_ELAPSED="$ELAPSED"
export ILA_BUILD_CMD="$BUILD_CMD"
export ILA_PRECHECK_CMD="$PRECHECK_CMD"
export ILA_COMMIT="$COMMIT"; export ILA_BRANCH="$BRANCH"
export ILA_XDC="$XDC_IN"; export ILA_XDC_SHA="$XDC_SHA"
export ILA_LICENSE="$XILINXD_LICENSE_FILE"
export ILA_SCRIPT="scripts/stage3_t04/bd_insert_ila.tcl"

python -B - <<'PY'
import hashlib, json, os, re, datetime

evid    = os.environ["ILA_EVID_DIR"]
run_dir = os.environ["ILA_RUN_DIR"]
rc      = int(os.environ["ILA_EXIT_CODE"])
log     = os.path.join(run_dir, "vivado_ila_bd.log")
netmap  = os.path.join(run_dir, "ila_bd_netmap.txt")
statusf = os.path.join(run_dir, "ila_bd_status.txt")
out_dir = os.path.join(run_dir, "impl_ila")
bit     = os.path.join(out_dir, "design_1_wrapper.bit")
ltx     = os.path.join(out_dir, "design_1_wrapper.ltx")

def sha256(p):
    if not os.path.isfile(p): return None
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(1<<20), b''): h.update(c)
    return h.hexdigest()

def rt(p):
    if not os.path.isfile(p): return ""
    with open(p, encoding="utf-8", errors="replace") as f: return f.read()

logtxt = rt(log)
peaks = [float(x) for x in re.findall(r"Memory \(MB\): peak = ([0-9.]+)", logtxt)]
peak_mb = max(peaks) if peaks else None
m = re.search(r"Vivado v\.([0-9.]+)", logtxt)
ver = m.group(1) if m else None
errs  = re.findall(r"^ERROR: \[([^\]]+)\]", logtxt, re.M)
crits = re.findall(r"^CRITICAL WARNING: \[([^\]]+)\]", logtxt, re.M)
warns = re.findall(r"^WARNING: \[([^\]]+)\]", logtxt, re.M)
lic_msgs = [l.strip() for l in logtxt.splitlines()
            if re.search(r"16-620|12-29205|[Cc]hip[Ss]cope|license|License", l)
            and re.search(r"ERROR|CRITICAL WARNING|WARNING", l)]
t05 = [l.split("ILA_BD|",1)[1].strip() for l in logtxt.splitlines() if "ILA_BD|" in l]
fails = [x for x in t05 if x.startswith("FAIL=")]

lmap = {}
for ln in rt(netmap).splitlines():
    ln = ln.strip()
    if ln and not ln.startswith("#") and "=" in ln:
        k,v = ln.split("=",1); lmap[k]=v

probes = {}
intended = [
 "cmos1_pclk 顶层 DVP 输入（外部端口 cmos1_pclk / alinx_ov5640_0/cmos_pclk，同一 BD 网络）",
 "cmos1_vsync 顶层 DVP 输入（外部端口 cmos1_vsync / alinx_ov5640_0/cmos_vsync）",
 "cmos1_href 顶层 DVP 输入（外部端口 cmos1_href / alinx_ov5640_0/cmos_href）",
 "alinx_ov5640_0 m_axis_video TUSER（S2MM 帧起始）",
 "alinx_ov5640_0 m_axis_video TLAST（行结束）",
]
for i in range(5):
    probes["probe%d"%i] = {
        "intended_signal": intended[i],
        "target_bd_pin": lmap.get("probe%d_target_pin"%i),
        "bd_net": lmap.get("probe%d_bd_net"%i),
        "bd_net_pins": lmap.get("probe%d_net_pins"%i),
        "bd_net_ports": lmap.get("probe%d_net_ports"%i),
    }

stat = {}
for ln in rt(statusf).splitlines():
    if "=" in ln:
        k,v = ln.split("=",1); stat[k]=v

drc_txt = rt(os.path.join(out_dir, "report_drc_routed.rpt"))
drc_detail = {}
for rule, num, sev in re.findall(r"^([A-Za-z0-9_-]+)#(\d+)\s+(Critical Warning|Error|Warning)\s*$", drc_txt, re.M):
    drc_detail[sev] = drc_detail.get(sev, 0) + 1

artifacts = {}
for name, path in (("bit", bit), ("ltx", ltx),
                   ("vivado_bd_log", log), ("ila_bd_netmap", netmap),
                   ("ila_ip_precheck_log", os.path.join(evid, "ila_ip_precheck.log")),
                   ("xdc_j11_cmos2", os.environ["ILA_XDC"])):
    artifacts[name] = {"path": path, "exists": os.path.isfile(path),
                       "size_bytes": os.path.getsize(path) if os.path.isfile(path) else None,
                       "sha256": sha256(path)}

ok = (rc == 0 and artifacts["bit"]["exists"] and artifacts["ltx"]["exists"])
rep = {
  "task_id": "S3-T05-ILA",
  "task_board_id": "task-2",
  "route": "bd_ip_instantiation",
  "title": "BD 内实例化 xilinx.com:ip:ila（5 探针）-> 比特流 + .ltx",
  "run_id": os.environ["ILA_RUN_NAME"],
  "run_dir": run_dir,
  "evidence_dir": evid,
  "generated_at_utc8": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
  "status": "ok" if ok else "failed",
  "tool": {"name": "Vivado", "version": ver, "mode": "batch_tcl",
           "license_file": os.environ["ILA_LICENSE"]},
  "baseline": {"worktree": "D:/codex-worktrees/dbdf", "branch": os.environ["ILA_BRANCH"],
               "commit": os.environ["ILA_COMMIT"], "part": "xc7z020clg400-2",
               "vendor_source": "tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project",
               "xdc": os.environ["ILA_XDC"], "xdc_sha256": os.environ["ILA_XDC_SHA"]},
  "commands": {"precheck": os.environ["ILA_PRECHECK_CMD"],
               "build": os.environ["ILA_BUILD_CMD"],
               "tcl_script": os.environ["ILA_SCRIPT"],
               "vivado_exit_code": rc, "elapsed_seconds": int(os.environ["ILA_ELAPSED"])},
  "ila_configuration": {"cell": "ila_cam",
                        "ip": "xilinx.com:ip:ila (BD 内实例化，未用 create_debug_core)",
                        "num_probes": 5, "data_depth": 4096, "c_en_strg_qual": 1,
                        "vendor_debug_ov5640": "false (厂商内嵌 6 探针 ila_0 保持关闭)",
                        "clock_input": "axi_vdma_1/s_axis_s2mm_aclk 所在 BD 网 (processing_system7_0_FCLK_CLK1，150MHz)"},
  "probe_map": probes,
  "ila_clock": {"bd_pin": lmap.get("ila_clock_pin"), "bd_net": lmap.get("ila_clock_net")},
  "implementation": {
      "timing": {"wns_ns": stat.get("wns_ns"), "tns_ns": stat.get("tns_ns"),
                 "whs_ns": stat.get("whs_ns"), "ths_ns": stat.get("ths_ns")},
      "drc_error_count": drc_detail.get("Error", 0),
      "drc_critical_warning_count": drc_detail.get("Critical Warning", 0),
      "drc_warning_count": drc_detail.get("Warning", 0),
      "ila_cells_in_impl": stat.get("impl_ila_cells"),
      "dbg_hub_cells_in_impl": stat.get("impl_dbg_hub_cells"),
      "peak_memory_mb": peak_mb},
  "log_messages": {"error_count": len(errs), "critical_warning_count": len(crits),
                   "warning_count": len(warns),
                   "error_codes": sorted(set(errs))[:40],
                   "critical_warning_codes": sorted(set(crits))[:40],
                   "license_or_chipscope_messages": lic_msgs[:20],
                   "ila_bd_fail_marks": fails},
  "artifacts": artifacts,
  "route_history": [{
      "route": "netlist_insertion_create_debug_core",
      "run_id": "t04_ila_20261020_r01",
      "result": "blocked_by_basic_license",
      "error": "ERROR: [Vivado 12-29205] 'create_debug_core' tcl command is not supported. Your current selected license is BASIC.",
      "evidence": "report/evidence/S3-T05/t05_ila_20261020_r01/vivado_ila.log"}],
  "limitations": [
      "只产出调试位流与 .ltx，未下载、未上板、未做 ILA 采集（采集由阶段总控在独立运行中执行）。",
      "ILA 采样时钟 150MHz + C_DATA_DEPTH=4096 ≈ 27.3us 采集窗口（约 1.2 行 1280x720@74.25MHz），短于一个视频帧；需靠触发条件命中 VSYNC 下降沿/TUSER 脉冲。",
      "probe0..2 接在摄像头 IP 的 DVP 输入管脚上（与外部端口 cmos1_pclk/vsync/href 同一个 BD 网络），等价于探外部引脚信号；已用 BD 网络成员核验。",
      "未做上板功能验证；未验证位流与基线功能一致性。",
  ],
  "not_executed": ["program_device / hw_server 连接", "ILA arm/trigger/capture/read_ila_data",
                   "上板图像或帧数据验证", "Git 提交（由阶段总控统一提交）"],
}
with open(os.path.join(evid, "build_report_bd.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=2); f.write("\n")
print("BUILD_REPORT_BD=%s" % os.path.join(evid, "build_report_bd.json"))
print("STATUS=%s" % rep["status"])
print("PEAK_MEM_MB=%s" % peak_mb)
print("BIT_SHA256=%s" % artifacts["bit"]["sha256"])
print("LTX_SHA256=%s" % artifacts["ltx"]["sha256"])
PY

exit "$rc"