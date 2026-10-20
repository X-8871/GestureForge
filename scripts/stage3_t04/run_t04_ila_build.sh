#!/usr/bin/env bash
# =============================================================================
# 阶段3 S3-T05-ILA 启动器：在 J11+CMOS2 综合检查点上插入 1 个 5 探针 ILA，
# 实现到比特流并导出 .ltx。只写本任务 RunId 目录与证据目录，不提交 Git，不上板。
#
# 用法: bash run_t04_ila_build.sh <run_name>
#   例: bash run_t04_ila_build.sh t04_ila_20261020_r01
#
# 说明：
#   * RunId 目录必须不存在才创建（禁止覆盖/复用既有 RunId）。
#   * BASIC 许可（basic_only.lic）按进程注入 XILINXD_LICENSE_FILE。
#   * 本机 16GB：同一时刻只跑这一个重型任务。
# =============================================================================
set -u

RUN_NAME="${1:?需要 run 目录名，例如 t04_ila_20261020_r01}"

WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
SYNTH_DCP="$WT/tmp/s3r06/t04_camera_j11cmos2_20261020_r01/project/ov5640_single.runs/synth_1/design_1_wrapper.dcp"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
TCL="$WT/scripts/stage3_t04/netlist_insert_ila.tcl"
EVID="$WT/report/evidence/S3-T05/t05_ila_20261020_r01"
LIC="D:/Xilinx_licenses/basic_only.lic"

export XILINXD_LICENSE_FILE="$LIC"

echo "LAUNCHER=gitbash"
echo "RUN_DIR=$RUN_DIR"
echo "SYNTH_DCP=$SYNTH_DCP"
echo "EVID=$EVID"
echo "LICENSE=$XILINXD_LICENSE_FILE"

# ---- 前置自检 --------------------------------------------------------------
TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
if [ "$TOP" != "$WT" ]; then echo "FAIL=worktree_selfcheck:$TOP"; exit 3; fi
if [ -e "$RUN_DIR" ]; then echo "FAIL=run_dir_exists"; exit 3; fi
[ -f "$SYNTH_DCP" ] || { echo "FAIL=synth_dcp_missing:$SYNTH_DCP"; exit 3; }
[ -f "$TCL" ]       || { echo "FAIL=tcl_missing:$TCL"; exit 3; }
[ -f "$LIC" ]       || { echo "FAIL=license_missing:$LIC"; exit 3; }

COMMIT="$(git -C "$WT" rev-parse HEAD)"
BRANCH="$(git -C "$WT" rev-parse --abbrev-ref HEAD)"
DCP_SHA="$(sha256sum "$SYNTH_DCP" | awk '{print $1}')"
echo "BASELINE_COMMIT=$COMMIT"
echo "BASELINE_BRANCH=$BRANCH"
echo "SYNTH_DCP_SHA256=$DCP_SHA"

# 重型任务唯一性：确认没有其他 vivado/xsim 在跑
RUNNING="$( (tasklist //FI "IMAGENAME eq vivado.exe" //NH 2>/dev/null; tasklist //FI "IMAGENAME eq xsim.exe" //NH 2>/dev/null) | grep -ci 'vivado.exe\|xsim.exe' )"
echo "EXISTING_VIVADO_XSIM_PROCS=$RUNNING"

mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir_run_dir"; exit 3; }
mkdir -p "$EVID"    || { echo "FAIL=mkdir_evidence_dir"; exit 3; }

CMD="$VIVADO -mode batch -source $TCL -log $RUN_DIR/vivado_ila.log -journal $RUN_DIR/vivado_ila.jou -tclargs $RUN_DIR $SYNTH_DCP"
echo "CMD=$CMD"

START_EPOCH=$(date +%s)
# 注意：不使用 set -e，退出码需要在 vivado 之后原样捕获
"$VIVADO" -mode batch \
  -source "$TCL" \
  -log "$RUN_DIR/vivado_ila.log" \
  -journal "$RUN_DIR/vivado_ila.jou" \
  -tclargs "$RUN_DIR" "$SYNTH_DCP"
rc=$?
END_EPOCH=$(date +%s)
ELAPSED=$((END_EPOCH - START_EPOCH))
echo "VIVADO_EXIT=$rc"
echo "ELAPSED_SECONDS=$ELAPSED"

# 证据留存：日志、命令流水、网表映射、状态、报告、产物
cp -f "$RUN_DIR/vivado_ila.log" "$EVID/vivado_ila.log" 2>/dev/null || true
cp -f "$RUN_DIR/vivado_ila.jou" "$EVID/vivado_ila.jou" 2>/dev/null || true
[ -f "$RUN_DIR/ila_netmap.txt" ] && cp -f "$RUN_DIR/ila_netmap.txt" "$EVID/ila_netmap.txt" || true
[ -f "$RUN_DIR/ila_status.txt" ] && cp -f "$RUN_DIR/ila_status.txt" "$EVID/ila_status.txt" || true
if [ -d "$RUN_DIR/impl_ila" ]; then
  for f in "$RUN_DIR"/impl_ila/*.rpt; do
    [ -f "$f" ] && cp -f "$f" "$EVID/" || true
  done
fi

export ILA_RUN_NAME="$RUN_NAME"
export ILA_RUN_DIR="$RUN_DIR"
export ILA_EVID_DIR="$EVID"
export ILA_EXIT_CODE="$rc"
export ILA_ELAPSED="$ELAPSED"
export ILA_CMD="$CMD"
export ILA_COMMIT="$COMMIT"
export ILA_BRANCH="$BRANCH"
export ILA_DCP="$SYNTH_DCP"
export ILA_DCP_SHA="$DCP_SHA"
export ILA_LICENSE="$XILINXD_LICENSE_FILE"
export ILA_SCRIPT="scripts/stage3_t04/netlist_insert_ila.tcl"

python -B - <<'PY'
import hashlib, json, os, re, sys, datetime

run_dir  = os.environ["ILA_RUN_DIR"]
evid     = os.environ["ILA_EVID_DIR"]
rc       = int(os.environ["ILA_EXIT_CODE"])
elapsed  = int(os.environ["ILA_ELAPSED"])
log      = os.path.join(run_dir, "vivado_ila.log")
netmap   = os.path.join(run_dir, "ila_netmap.txt")
statusf  = os.path.join(run_dir, "ila_status.txt")
out_dir  = os.path.join(run_dir, "impl_ila")
bit      = os.path.join(out_dir, "design_1_wrapper.bit")
ltx      = os.path.join(out_dir, "design_1_wrapper.ltx")


def sha256(path):
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


# ---- vivado.log 解析：峰值内存 / 版本 / 关键消息 / 失败标记 -------------------
logtxt = read_text(log)
peaks = [float(x) for x in re.findall(r"Memory \(MB\): peak = ([0-9.]+)", logtxt)]
peak_mb = max(peaks) if peaks else None
ver = None
m = re.search(r"Vivado v\.([0-9.]+ \(win64\) Build \d+)", logtxt)
if m:
    ver = m.group(1)
else:
    m = re.search(r"Vivado v\.([0-9.]+)", logtxt)
    ver = m.group(1) if m else None

errs = re.findall(r"^ERROR: \[([^\]]+)\]", logtxt, re.M)
crits = re.findall(r"^CRITICAL WARNING: \[([^\]]+)\]", logtxt, re.M)
warns = re.findall(r"^WARNING: \[([^\]]+)\]", logtxt, re.M)
# 与许可/调试核相关的消息（BASIC 许可 >5 探针、Chipscope 16-620 等）
license_msgs = [ln.strip() for ln in logtxt.splitlines()
                if re.search(r"16-620|ChipScope|Chipscope|chipscope|license|License", ln)
                and re.search(r"ERROR|CRITICAL WARNING|WARNING", ln)]
ila_t05 = [ln.split("ILA_T05|", 1)[1].strip() for ln in logtxt.splitlines() if "ILA_T05|" in ln]
fail_marks = [x for x in ila_t05 if x.startswith("FAIL=")]

# ---- 探针网名映射 -----------------------------------------------------------
probes = {}
clk = {}
lmap = {}
for ln in read_text(netmap).splitlines():
    ln = ln.strip()
    if not ln or ln.startswith("#") or "=" not in ln:
        continue
    k, v = ln.split("=", 1)
    lmap[k] = v
for i in range(5):
    probes["probe%d" % i] = {
        "net": lmap.get("probe%d" % i),
        "width": lmap.get("probe%d_width" % i),
        "driver_pin": lmap.get("probe%d_driver" % i),
        "driver_ref": lmap.get("probe%d_driver_ref" % i),
        "sink_count": lmap.get("probe%d_sink_count" % i),
        "intended_signal": [
            "cmos1_pclk (顶层 DVP 输入网 / IBUF 输出)",
            "cmos1_vsync (顶层 DVP 输入网 / IBUF 输出)",
            "cmos1_href (顶层 DVP 输入网 / IBUF 输出)",
            "alinx_ov5640_0/m_axis_video_tuser (S2MM 帧起始 TUSER)",
            "alinx_ov5640_0/m_axis_video_tlast (S2MM 行结束 TLAST)",
        ][i],
    }
clk["net"] = lmap.get("ila_clock")
for x in ila_t05:
    if x.startswith("RESULT ila_clock_obj="):
        body = x[len("RESULT ila_clock_obj="):]
        clk["clock_object"] = body.split(" period_ns=")[0]
        clk["period_ns"] = body.split(" period_ns=")[1] if " period_ns=" in body else None

# ---- 状态文件 / 时序 --------------------------------------------------------
stat = {}
for ln in read_text(statusf).splitlines():
    if "=" in ln:
        k, v = ln.split("=", 1)
        stat[k] = v

# ---- DRC 报告：错误/严重警告/警告计数（两路交叉核对） ----------------------
drc_rpt = os.path.join(out_dir, "report_drc_routed.rpt")
drc_txt = read_text(drc_rpt)
drc_detail = {}
for rule, num, sev in re.findall(r"^([A-Za-z0-9_-]+)#(\d+)\s+(Critical Warning|Error|Warning)\s*$", drc_txt, re.M):
    drc_detail[sev] = drc_detail.get(sev, 0) + 1
drc_table = {}
for rule, sev, n in re.findall(r"^\|\s*([A-Za-z0-9_-]+)\s*\|\s*(Critical Warning|Error|Warning)\s*\|[^|]*\|\s*(\d+)\s*\|", drc_txt, re.M):
    drc_table[sev] = drc_table.get(sev, 0) + int(n)

# ---- 产物哈希 --------------------------------------------------------------
artifacts = {}
for name, path in (("bit", bit), ("ltx", ltx),
                   ("synth_dcp", os.environ["ILA_DCP"]),
                   ("vivado_log", log),
                   ("ila_netmap", netmap)):
    artifacts[name] = {
        "path": path,
        "exists": os.path.isfile(path),
        "size_bytes": os.path.getsize(path) if os.path.isfile(path) else None,
        "sha256": sha256(path),
    }

status = "ok" if (rc == 0 and artifacts["bit"]["exists"] and artifacts["ltx"]["exists"]) else "failed"

report = {
    "task_id": "S3-T05-ILA",
    "task_board_id": "task-2",
    "title": "在 J11+CMOS2 综合检查点上以网表插入法加 1 个 5 探针 ILA 并实现到调试位流",
    "run_id": os.environ["ILA_RUN_NAME"],
    "run_dir": run_dir,
    "evidence_dir": evid,
    "generated_at_utc8": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "status": status,
    "tool": {
        "name": "Vivado",
        "version": ver,
        "mode": "batch_tcl",
        "license_file": os.environ["ILA_LICENSE"],
    },
    "baseline": {
        "worktree": "D:/codex-worktrees/dbdf",
        "branch": os.environ["ILA_BRANCH"],
        "commit": os.environ["ILA_COMMIT"],
        "part": "xc7z020clg400-2",
        "synth_checkpoint": os.environ["ILA_DCP"],
        "synth_checkpoint_sha256": os.environ["ILA_DCP_SHA"],
        "design": "design_1_wrapper (BD design_1, alinx_ov5640 + axi_vdma_1 S2MM + HDMI 直通)",
    },
    "commands": {
        "launcher": "bash scripts/stage3_t04/run_t04_ila_build.sh %s" % os.environ["ILA_RUN_NAME"],
        "vivado": os.environ["ILA_CMD"],
        "addressing_dcp": os.environ["ILA_DCP"],
        "tcl_script": os.environ["ILA_SCRIPT"],
        "vivado_exit_code": rc,
        "elapsed_seconds": elapsed,
    },
    "ila_configuration": {
        "core": "u_ila_0",
        "type": "ila",
        "num_probes": 5,
        "data_depth": 4096,
        "clock_input": "axi_vdma_1 S2MM 流时钟 (BD 网 processing_system7_0_FCLK_CLK1)",
        "single_core_no_vendor_debug": True,
        "note": "BASIC 许可上限 5 探针；未打开厂商 IP 内嵌 DEBUG_OV5640 ila_0(6 探针)",
    },
    "probe_map": probes,
    "ila_clock": clk,
    "implementation": {
        "flow": ["opt_design", "place_design", "phys_opt_design", "route_design",
                 "report_timing_summary", "report_drc", "write_bitstream", "write_debug_probes"],
        "timing": {
            "wns_ns": stat.get("wns_ns"),
            "tns_ns": stat.get("tns_ns"),
            "whs_ns": stat.get("whs_ns"),
            "ths_ns": stat.get("ths_ns"),
            "wns_from_get_timing_paths_ns": stat.get("wns_from_path_ns"),
            "whs_from_get_timing_paths_ns": stat.get("whs_from_path_ns"),
        },
        "drc_error_count": drc_detail.get("Error", 0),
        "drc_critical_warning_count": drc_detail.get("Critical Warning", 0),
        "drc_warning_count": drc_detail.get("Warning", 0),
        "drc_error_count_from_summary_table": drc_table.get("Error", 0),
        "drc_violation_counts_by_severity": drc_detail,
        "debug_core_cells_after_opt": stat.get("ila_cells"),
        "dbg_hub_cells_after_opt": stat.get("dbg_hub_cells"),
        "peak_memory_mb": peak_mb,
    },
    "log_messages": {
        "error_count": len(errs),
        "critical_warning_count": len(crits),
        "warning_count": len(warns),
        "error_codes": sorted(set(errs))[:40],
        "critical_warning_codes": sorted(set(crits))[:40],
        "license_or_chipscope_messages": license_msgs[:20],
        "ila_t05_fail_marks": fail_marks,
    },
    "artifacts": artifacts,
    "limitations": [
        "本任务只产出调试位流与 .ltx，未下载到实物、未做 ILA 采集（下载与采集由阶段总控在独立运行中执行）。",
        "ILA 采样时钟为 S2MM 流时钟 (FCLK_CLK1, 150MHz)，C_DATA_DEPTH=4096 对应约 27.3us 窗口（约 1.2 行 1280x720 PCLK@74.25MHz），单次采集窗口短于一个视频帧；能否看到 VSYNC 下降沿/TUSER 脉冲取决于触发条件，需在采集阶段设置触发。",
        "probe0 取 cmos1_pclk_IBUF（IBUF 输出、BUFG 之前的原始引脚活动网）；该网为时钟网，ILA 作为数据负载接入可能引入 PLCK 类 DRC 警告（见 report_drc_routed.rpt）。",
        "未做上板功能验证，位流是否与基线功能一致未在本任务内验证。",
        "未执行：JTAG 下载、ILA 触发采集、波形导出、帧数据比对。",
    ],
    "not_executed": [
        "program_device / hw_server 连接",
        "ILA arm/trigger/capture/read_ila_data",
        "上板图像或帧数据验证",
        "Git 提交（由阶段总控统一提交）",
    ],
}

os.makedirs(evid, exist_ok=True)
rpt_path = os.path.join(evid, "build_report.json")
with open(rpt_path, "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print("BUILD_REPORT=%s" % rpt_path)
print("STATUS=%s" % status)
print("PEAK_MEM_MB=%s" % peak_mb)
print("DRC_ERRORS=%s" % report["implementation"]["drc_error_count"])
print("BIT_SHA256=%s" % artifacts["bit"]["sha256"])
print("LTX_SHA256=%s" % artifacts["ltx"]["sha256"])
PY

echo "EVIDENCE_JSON=$EVID/build_report.json"
exit "$rc"