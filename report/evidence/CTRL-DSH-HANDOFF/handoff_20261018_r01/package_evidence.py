# -*- coding: utf-8 -*-
"""打包 DSH 2026-10-18 交接核实的离线证据（只复制、不移动原件）。"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta

REPO = r"D:\FPGA_Competition"
TASK = "CTRL-DSH-HANDOFF"
RUN = "handoff_20261018_r01"
EVID = os.path.join(REPO, "report", "evidence", TASK, RUN)
RAW = os.path.join(EVID, "raw")
SRC = r"D:\tmp\vivado_test"

CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST).isoformat()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def info(path):
    return {
        "path": path,
        "bytes": os.path.getsize(path),
        "sha256_packaging_time": sha256(path),
        "mtime_utc8": datetime.fromtimestamp(os.path.getmtime(path), CST).isoformat(),
    }


os.makedirs(RAW, exist_ok=True)

# 1) 复制原始探针产物（只读复制，原件保留在 D:\tmp\vivado_test）
copy_list = [
    "license_probe.tcl",
    "run_license_probe.bat",
    "license_probe.txt",
    "probe_out.txt",
    "run_xsim_probe.bat",
    "xsim_probe.log",
    "clockInfo.txt",
]
copied = []
for name in copy_list:
    src = os.path.join(SRC, name)
    if os.path.isfile(src):
        dst = os.path.join(RAW, name)
        shutil.copy2(src, dst)
        copied.append({"name": name, "source": src, "copied": info(dst)})

# 2) Vivado 会话日志/journal（许可与 open/close 证据）
vivado_logs = []
ai_dir = os.path.join(SRC, ".vivado-ai")
for name in sorted(os.listdir(ai_dir)) if os.path.isdir(ai_dir) else []:
    if name.startswith("vivado_61230718") or name.startswith("vivado_proxy_19568"):
        src = os.path.join(ai_dir, name)
        dst = os.path.join(RAW, name)
        shutil.copy2(src, dst)
        vivado_logs.append({"name": name, "source": src, "copied": info(dst)})

# 3) 探针比特流：只记录哈希与大小，不复制构建产物
bit = os.path.join(SRC, "counter_probe.bit")
bit_record = None
if os.path.isfile(bit):
    bit_record = {
        "path": bit,
        **{k: v for k, v in info(bit).items() if k != "path"},
        "committed": False,
        "reason": "一次性探针设计的构建产物；仅登记哈希，不进入 Git",
    }

# 4) .xpr 归因证据：当前文件、HEAD 版本、差异
def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


xpr = os.path.join(REPO, "vivado", "AX7Z020_Gesture", "AX7Z020_Gesture.xpr")
head_xml = git("show", "HEAD:vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr").stdout
head_path = os.path.join(EVID, "xpr_head_committed.xml")
with open(head_path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(head_xml)
diff = git("diff", "--", "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr").stdout
diff_path = os.path.join(EVID, "xpr_worktree_vs_head.diff")
with open(diff_path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(diff)
numstat = git("diff", "--numstat", "--", "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr").stdout.strip()
status = git("status", "--short", "--", "vivado/").stdout.strip()
journal_hits = []
jou = os.path.join(ai_dir, "vivado_61230718_3ce19e70.jou")
if os.path.isfile(jou):
    with open(jou, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "open_project" in line or "close_project" in line or "start_gui" in line:
                journal_hits.append(line.strip()[:200])

xpr_record = {
    "worktree_path": xpr,
    "worktree": info(xpr),
    "head_committed_xml": info(head_path),
    "diff_file": info(diff_path),
    "diff_numstat": numstat,
    "git_status_under_vivado": status,
    "session_journal_commands": journal_hits,
    "attribution": "打开/关闭工程的会话 journal 与 .xpr mtime(2026-10-18 02:26:41) 一致；无 02:26 之前的文件快照或哈希，内容级变化无法归因",
}

# 5) 文档栈日志摘录（原件 2.6 MB，不整体复制）
doc_log = r"D:\tmp\docsearch_configure.log"
doc_record = None
if os.path.isfile(doc_log):
    keys = []
    # PowerShell 重定向默认写 UTF-16LE，需按 BOM 判断编码
    with open(doc_log, "rb") as fh:
        head = fh.read(2)
    enc = "utf-16" if head in (b"\xff\xfe", b"\xfe\xff") else "utf-8"
    with open(doc_log, "r", encoding=enc, errors="replace") as fh:
        for line in fh:
            if any(k in line for k in (
                "importing docs: 725911/725911",
                "weaviate-docs-import-1 exited",
                "Loaded  ghcr.io",
                "Loaded  vivado.amd.com",
                "Loaded  cr.weaviate.io",
                "Loaded  Qwen3-Embedding",
                "Container amd-embedded-doc-search-22061-mcp-1 Started",
            )):
                keys.append(" ".join(line.split())[:200])
    extract = os.path.join(EVID, "docsearch_configure_key_lines.txt")
    with open(extract, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(keys) + "\n")
    doc_record = {
        "original": info(doc_log),
        "extract_file": info(extract),
        "extract_lines": keys,
        "note": "原件 2.6 MB 保留在 D:\\tmp，不整体复制；此处仅摘录导入完成/镜像加载/容器启动关键行",
    }

manifest = {
    "schema_version": 1,
    "task_id": TASK,
    "run_id": RUN,
    "created_utc8": NOW,
    "author": "DSH (deepseek harness team lead)",
    "scope": "2026-10-18 交接核实：Vivado 探针证据保全 + .xpr 变更归因 + 文档栈事实分级",
    "hardware_execution": "NOT_RUN",
    "board_state": "未上电；本轮未访问 JTAG/未下载/未烧写",
    "tool_versions": {
        "vivado": "2026.1（license_probe.txt 记录）",
        "xsim": "v2026.1 (64-bit) SW Build 6511674",
        "license_tier": "BASIC（Vivado_Basic/Synthesis/Implementation/Simulation，有效至 2027-08-07）",
        "license_file": r"D:\Xilinx_licenses\basic_only.lic",
    },
    "runtime_bound_evidence": {
        "license_probe": {
            "command": r"cmd /c D:\tmp\vivado_test\run_license_probe.bat（内部 XILINXD_LICENSE_FILE=D:\Xilinx_licenses\basic_only.lic, TEMP/TMP=D:\tmp）",
            "native_exit_code": 0,
            "result_file_lines": ["VIVADO=2026.1", "XILINXD_LICENSE_FILE=D:\\Xilinx_licenses\\basic_only.lic", "SYNTH_OK cells=8 nets=11", "PART=xc7z020clg400-2"],
            "note": "综合成功只证明该探针 RTL 在当前许可下可综合；不代表真实工程或 2B 平台",
        },
        "xsim_probe": {
            "command": r"cmd /c D:\tmp\vivado_test\run_xsim_probe.bat（xvlog -sv / xelab / xsim）",
            "native_exit_codes": {"xvlog": 0, "xelab": 0, "xsim": 0},
            "testbench": "sim/tb_counter.sv（自检；配套 src/counter.sv）",
            "assertion_result": "无断言失败；测试台打印“计数器测试完成”，$finish @106 ns（tb_counter.sv:91）",
            "coverage": "未采集（未运行覆盖率流程），不得声称覆盖达成",
            "note": "三阶段原生退出码分别记录；总批处理退出码不作为测试通过依据",
        },
    },
    "packaging_time_hashes": {
        "copied_raw": copied,
        "vivado_session_logs": vivado_logs,
        "probe_bitstream": bit_record,
        "xpr": xpr_record,
        "docsearch_log": doc_record,
    },
    "not_runtime_bound": [
        "所有 sha256_packaging_time 均为 2026-10-18 打包时计算，不是运行时绑定；运行时仅原生退出码与日志文本可绑定。",
        "源码（src/counter.sv、sim/tb_counter.sv）哈希未在探针运行时记录，不能声明为运行时绑定基线。",
        "探针设计与真实工程 AX7Z020_Gesture、阶段 2B 平台无关。",
    ],
    "limitations": [
        "counter 探针无时序约束、无 XDC；真实工程 constrs_1 为空。",
        "比特流生成曾因 NSTD-1/UCIO-1 被拒，降级为 Warning 后才生成；该 bit 不得作为板级安全或阶段通过证据。",
        "xsim 只跑单个自检测试台，无随机化/回归/覆盖率。",
        "JTAG 只读枚举到线缆未见器件；本轮未再访问硬件。",
        "D:\\tmp\\vivado_test 原件保持不动；本包为只读复制。",
    ],
}

manifest_path = os.path.join(EVID, "manifest.json")
with open(manifest_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print(json.dumps({
    "evidence_dir": EVID,
    "manifest": manifest_path,
    "manifest_sha256": sha256(manifest_path),
    "files": len(os.listdir(EVID)) + len(os.listdir(RAW)),
}, ensure_ascii=False, indent=2))