#!/usr/bin/env python3
"""复核旧蓝位补丁的真实落点，保存有哈希绑定的历史证据。"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def sha256(path: Path) -> str:
    """流式计算文件身份。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def invoke(args: list[str], root: Path) -> dict:
    """保留真实命令、退出码及输出，不把后续命令的成功当作前序成功。"""
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(args, cwd=root, env=child_env, capture_output=True, encoding="utf-8", errors="replace")
    return {"command": args, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def main() -> int:
    """只读取声明的旧运行，输出必须是工作树内的新目录。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    options = parser.parse_args()
    root = options.worktree.resolve(strict=True)
    output = options.output.absolute()
    if not output.parent.is_dir() or output.exists():
        parser.error("输出父目录必须存在，输出目录本身必须不存在")
    if not output.resolve().is_relative_to(root):
        parser.error("输出必须位于接管工作树内")
    run = root / "tmp/s3r06/t04_bluefix_20261020_r01"
    generated = run / "project/ov5640_single.gen/sources_1/bd/design_1"
    ooc = run / "project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1"
    source_paths = [
        root / "report/evidence/S3-CTRL/S3-T05/S3CTRL-20261021-002-handoff-to-codex-stage3.md",
        root / "board/stage3/software/sensor/alinx_ov5640_blue_msb_rebuild.patch",
        run / "vendor_src/my_ip/ov5640_ip/src/alinx_ov5640.v",
        generated / "ipshared/564b/src/alinx_ov5640.v",
        ooc / "design_1_alinx_ov5640_0_0.tcl",
        ooc / "runme.log",
        ooc / "design_1_alinx_ov5640_0_0_sim_netlist.v",
        generated / "ip/design_1_axis_subset_converter_0_0/design_1_axis_subset_converter_0_0_sim_netlist.v",
        run / "vendor_src/my_ip/rgb2dvi_v1_3/src/rgb2dvi.vhd",
        run / "t05_bluefix/download_bluefix.log",
        run / "project/ov5640_single.runs/impl_1/design_1_wrapper.bit",
        run / "design_1_wrapper.xsa",
    ]
    sample_paths = [
        root / "report/evidence/S3-T05/t05_j10_board_20261020_r01/row_y100.bin",
        root / "tmp/3/S3-CTRL/t05_live_r01/row_y100.bin",
        root / "tmp/3/S3-CTRL/t05_live_r01/row_y400.bin",
        root / "tmp/3/S3-CTRL/t05_live_r01/row_y600.bin",
    ]
    for path in source_paths + sample_paths:
        if not path.is_file():
            parser.error(f"缺失输入：{path}")
    commands = [
        invoke(["git", "--no-optional-locks", "rev-parse", "--show-toplevel"], root),
        invoke(["git", "--no-optional-locks", "branch", "--show-current"], root),
        invoke(["git", "--no-optional-locks", "rev-parse", "HEAD"], root),
        invoke(["git", "--no-optional-locks", "status", "--short"], root),
        invoke(["git", "--no-optional-locks", "rev-parse", "--git-path", "index.lock"], root),
    ]
    if any(item["exit_code"] for item in commands):
        print(json.dumps(commands, ensure_ascii=False, indent=2))
        return 2
    if commands[1]["stdout"].strip() != "codex/stage3-video":
        parser.error("分支与交接不符")
    output.mkdir()
    samples_output = output / "samples"
    samples_output.mkdir()
    mapping = {0: "display_blue", 1: "display_green", 2: "display_red"}
    expected_values = {((2 * value + value // 8) * 8) for value in range(16)}
    samples = []
    for index, path in enumerate(sample_paths):
        blob = path.read_bytes()
        if not blob or len(blob) % 3:
            raise ValueError(f"无效的三字节像素行：{path}")
        copy_path = samples_output / f"{index:02d}_{path.name}"
        shutil.copyfile(path, copy_path)
        channels = []
        for offset in range(3):
            counts = Counter(blob[offset::3])
            channels.append({
                "byte_offset": offset,
                "display_channel": mapping[offset],
                "pixels": sum(counts.values()),
                "minimum": min(counts),
                "maximum": max(counts),
                "over_127": sum(n for value, n in counts.items() if value > 127),
                "bit4_set": sum(n for value, n in counts.items() if value & 16),
                "histogram": dict(sorted(counts.items())),
                "fits_rebuild_alphabet": set(counts).issubset(expected_values),
            })
        samples.append({"source": str(path.relative_to(root)), "copy": str(copy_path.relative_to(output)),
                        "sha256": sha256(path), "channels": channels})
    converter = source_paths[7].read_text(encoding="utf-8")
    hdmi = source_paths[8].read_text(encoding="utf-8")
    netlist = source_paths[6].read_text(encoding="utf-8")
    semantic_checks = {
        "bit_identity": sha256(source_paths[10]) == "0819d0da1508cdc43f72d8ab67e8d4173de3ddc656e3fbfa957a72c061c119d7",
        "xsa_identity": sha256(source_paths[11]) == "fed8f652be0a2d567215a7b0e5905355dfe2bbac8c380f0a94df1daf038bbabc",
        "generated_rtl_identity": sha256(source_paths[3]) == "91b67c1e0149255112b085b1c737b39f737aec52a4baee97144e8839408b4cec",
        "converter_blue": "assign m_axis_tdata[7:3] = s_axis_tdata[15:11];" in converter,
        "converter_red": "assign m_axis_tdata[23:19] = s_axis_tdata[4:0];" in converter,
        "hdmi_blue": "pDataOut(0) <= vid_pData(7 downto 0)" in hdmi,
        "hdmi_red": "pDataOut(2) <= vid_pData(23 downto 16)" in hdmi,
        "ooc_ram_rebuild": "dina[15:3],dina[6],dina[1:0]" in netlist,
        "old_control_not_rebuilt": not samples[0]["channels"][2]["fits_rebuild_alphabet"],
        "patched_red_rebuilt": all(s["channels"][2]["fits_rebuild_alphabet"] and s["channels"][2]["over_127"] > 0 for s in samples[1:]),
        "patched_blue_still_missing": all(s["channels"][0]["maximum"] == 120 and not s["channels"][0]["fits_rebuild_alphabet"] for s in samples[1:]),
        "green_bit4_missing": all(s["channels"][1]["bit4_set"] == 0 for s in samples),
    }
    excerpts = []
    anchors = ("s_axis_tdata_bluefix", ".din", "DIADI", "assign m_axis_tdata", "pDataOut(2) <=", "pDataOut(1) <=", "pDataOut(0) <=", "synthesizing module 'alinx_ov5640'")
    for path in source_paths:
        if path.suffix not in {".v", ".vhd", ".log"}:
            continue
        hits = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if any(anchor in line for anchor in anchors):
                hits.append({"line": line_number, "text": line.strip()})
        if hits:
            excerpts.append({"source": str(path.relative_to(root)), "matches": hits})
    heartbeat = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    record = {
        "task": "S3-T05 display blue rebuild diagnosis", "owner": "Codex stage3 lead",
        "worktree": str(root), "branch": "codex/stage3-video", "base_commit": commands[2]["stdout"].strip(),
        "allowed_paths": ["board/stage3/**", "scripts/stage3_t03b/**", "scripts/stage3_t04/**", "scripts/stage3_t05/**", "report/evidence/S3-T05/**", "report/evidence/S3-CTRL/**", ".codex/STATE.md"],
        "dirty_owner": "NA/ and clockInfo.txt: existing user files; scoped changes: Codex; tmp: not committed",
        "yield_statement": "DSH OFFERED on 2026-10-21 15:05 UTC+8; user explicitly assigned takeover; Codex CLAIMED then IN_PROGRESS",
        "heartbeat_utc8": heartbeat, "evidence_dir": str(output),
        "recovery_command": "Inspect OOC source, FIFO RAM netlist and display channel mapping before rebuilding",
        "status": "IN_PROGRESS", "next_owner": "Codex stage3 lead",
    }
    record_path = output / "takeover_record.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": 1, "task_id": "S3-T05", "run_id": output.name,
        "source_commit": commands[2]["stdout"].strip(),
        "source_branch": commands[1]["stdout"].strip(), "created_utc8": heartbeat,
        "command": [sys.executable, *sys.argv],
        "inputs": [{"path": str(path.relative_to(root)), "sha256": sha256(path)} for path in source_paths],
        "historical_samples": samples,
        "scope": "历史样本与网表的只读复核；未重新下载/上板；不代表阶段验收",
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    check = invoke([sys.executable, "-B", "D:/FPGA_Competition/verification/handoff_check.py", "--worktree", str(root), "--record", str(record_path), "--json"], root)
    (output / "handoff_check.json").write_text(json.dumps(check, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {
        "schema_version": 1, "task": "S3-T05", "created_utc8": heartbeat,
        "command": [sys.executable, *sys.argv], "commands": commands, "handoff_checker_exit": check["exit_code"],
        "inputs": [{"path": str(path.relative_to(root)), "sha256": sha256(path)} for path in source_paths],
        "excerpts": excerpts, "historical_ddr_samples": samples, "semantic_checks": semantic_checks,
        "findings": [
            "旧补丁进入 OOC 综合并在 RAM 写端保留重建连接；不是未打补丁的源或缓存复用。",
            "转换器输出低字节来自 tdata[15:11]，高字节来自 tdata[4:0]；HDMI 高字节为红，低字节为蓝。",
            "旧补丁修改低5位，实际改变显示红通道；补丁后样本的 offset2 呈现独有重建字母表。",
            "显示蓝低字节仍缺 bit7；绿色样本也未出现 bit4。若追溯到 DVP，这两个位都对应字节 MSB/cmos_d[9]，不是 cmos_d[6]。",
            "数据位缺失发生在何处仍需定位；仅凭两个扩展口同现象不能排除共有 RTL/配置问题，不能宣称已证明模块硬件故障。",
        ],
        "limitations": ["本报告仅复核既有文件，没有重新下载或采样；旧采样时间绑定仍依赖历史日志。", "位重建是近似拉伸，不恢复真实丢失最高位。", "绿色缺位的根因尚未排除，不在本次蓝通道最小修复中更改。"],
    }
    (output / "channel_mapping_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["outputs"] = [{"path": path.name, "sha256": sha256(path)} for path in (record_path, output / "handoff_check.json", output / "channel_mapping_report.json")]
    final_rc = check["exit_code"] or (0 if all(semantic_checks.values()) else 1)
    manifest["exit_code"] = final_rc
    manifest["semantic_checks"] = semantic_checks
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "samples": len(samples), "handoff_checker_exit": check["exit_code"], "semantic_checks": semantic_checks, "exit_code": final_rc, "report_sha256": sha256(output / "channel_mapping_report.json")}, ensure_ascii=False))
    return final_rc


if __name__ == "__main__":
    raise SystemExit(main())
