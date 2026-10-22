"""S3-T05 阶段三收尾记录生成（2026-10-22，Wong 决定：以灰度收尾、暂不微调）。

生成 report/evidence/S3-T05/t05_stage3_closeout_20261022_r01/{README.md,manifest.json,hashes.txt}
并 best-effort 运行只读交付核验 verification/check_stage_delivery.py。
不修改任何旧 RunId；只读源码与证据。
"""
import hashlib
import json
import os
import subprocess
import sys

WT = r"D:\codex-worktrees\dbdf"
OUT = os.path.join(WT, "report", "evidence", "S3-T05", "t05_stage3_closeout_20261022_r01")

FROZEN = {
    "bitstream_stdluma_gray": ("tmp/s3r06/t04_stdluma_20261022_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit",
                               "44e609ccc62647c1748cbeecc64b2fdaa0c53b07db6b7bd1c8a230ca65fc4afb"),
    "xsa_stdluma_gray": ("tmp/s3r06/t04_stdluma_20261022_r01/design_1_wrapper.xsa",
                         "90e1bdee1f5baaf9e772edcddc800aab6927d2099b54a45bc020025d82ccb1c4"),
    "bitstream_green_luma_alt": ("tmp/s3r06/t04_gray_20261021_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit",
                                 "2f72aaa42936225eb7215bd8f138f68e52c27c3ab31ab236c8a3c15f7669af4f"),
    "bitstream_dualmsb_colour_alt": ("tmp/s3r06/t04_dualmsb_20261021_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit",
                                     "30db09ba8e4e9df8fca73429ce7e941988391b4475fc88d19ebc86469fff23e4"),
    "bitstream_sof_baseline": ("tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit",
                               "7cb33068" ),
    "elf_v10_read": ("tmp/s3r06/t04_j11cmos2_elf_v10/elf_build/app/an5642_j11cmos2_v10_read.elf",
                     "1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073"),
    "elf_v11_freeze": ("tmp/s3r06/t04_j11cmos2_elf_v11/elf_build/app/an5642_j11cmos2_v11_freeze.elf",
                       "c01133b1bb0204f07a5be215dbeb58ca0dcc627115cd3a06f1c56f9b21ca26c4"),
    "elf_v12_bars": ("tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/app/an5642_j11cmos2_v12_bars_freeze.elf",
                     "527a74fca6ea0774c34625015720a5163fc58557d44c64e29428700fd09845c5"),
}

FILES = {
    "patch_stdluma_gray": "board/stage3/software/sensor/alinx_ov5640_stdluma_gray.patch",
    "patch_gray_luma_alt": "board/stage3/software/sensor/alinx_ov5640_gray_luma.patch",
    "patch_sof_hrefgap": "board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch",
    "runner_stdluma": "scripts/stage3_t04/run_t04_camera_j11cmos2_stdluma_build.sh",
    "runner_gray": "scripts/stage3_t04/run_t04_camera_j11cmos2_gray_build.sh",
    "dump_frame_tcl": "scripts/stage3_t05/jtag_dump_frame.tcl",
    "dump_channels_tcl": "scripts/stage3_t05/jtag_dump_display_channels.tcl",
    "analyze_msb": "scripts/stage3_t05/analyze_missing_msb_signature.py",
    "board_capture_sh": "scripts/stage3_t05/run_t05_board_capture.sh",
    "make_archive": "scripts/stage3_t05/make_archive.py",
    "xdc_j11": "board/stage3/hardware/an5642_j11_cmos2.xdc",
    "xdc_j10": "board/stage3/hardware/an5642_j10_cmos2.xdc",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", WT] + list(a), capture_output=True, text=True).stdout.strip()


def main():
    if os.path.exists(OUT):
        raise SystemExit("REFUSE_OVERWRITE: " + OUT)
    os.makedirs(OUT)

    frozen, missing = {}, []
    for name, (rel, expect) in FROZEN.items():
        p = os.path.join(WT, rel.replace("/", os.sep))
        if os.path.exists(p):
            got = sha256(p)
            frozen[name] = {"path": rel, "sha256": got, "expected_prefix": expect,
                            "matches_expected": got.startswith(expect)}
        else:
            missing.append(rel)

    files = {}
    for name, rel in FILES.items():
        p = os.path.join(WT, rel.replace("/", os.sep))
        files[name] = {"path": rel, "sha256": sha256(p) if os.path.exists(p) else None}

    checker = {"attempted": True, "argv": ["python", "-B", "verification/check_stage_delivery.py", "evidence"],
               "exit_code": None, "output_tail": ""}
    try:
        r = subprocess.run([sys.executable, "-B", os.path.join("verification", "check_stage_delivery.py"), "evidence"],
                           cwd=WT, capture_output=True, text=True, timeout=300)
        checker["exit_code"] = r.returncode
        checker["output_tail"] = (r.stdout + r.stderr).strip().splitlines()[-12:]
    except Exception as exc:  # noqa: BLE001
        checker["error"] = repr(exc)

    manifest = {
        "run_id": "t05_stage3_closeout_20261022_r01",
        "task": "S3-T05",
        "stage": 3,
        "date": "2026-10-22",
        "decision": "Wong 2026-10-22：暂不微调，按灰度收尾阶段三；颜色项待更换模块到货后复测",
        "source_baseline_commit": git("rev-parse", "HEAD"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "deployment_artifacts": frozen,
        "missing_frozen_artifacts": missing,
        "support_files": files,
        "acceptance": {
            "G1_development_delivery": "PASS：RTL/应用/脚本齐备，构建退出码 0，证据含哈希与命令",
            "G2_independent_review": "PARTIAL：Codex 对早期结论的更正 + dev-pl 有界网表核对；stdluma 补丁仅总控人工审阅，未做完整独立 Reviewer 流程",
            "G3_physical_verification": "PASS（灰度口径）：板上实时、|R−B|=0.0、|R−G|≈|G−B|≈2/255、VDMA FRAME0/STRIDE 核对、干净整帧导出；未做 ≥30 min 耐久",
            "G4_task_acceptance": "PASS（按 Wong 修订判据“黑白可接受”）：灰度画面获 Wong 目视接受；颜色项受阻",
            "G5_stage_acceptance": "以灰度收尾；颜色验收明确受阻/待硬件，不宣称完全通过",
        },
        "blocked_or_open": [
            "颜色验收：待更换模块到货，按 t05_freeze_20261021_r01/README.md §5 复测",
            "模型域：灰度输入对彩色训练模型不可靠（第三方实测 tiny320 26%）；Wong 决定暂不微调，作为已知限制随阶段交接",
            "task-11 网表交叉核对未完成（补丁人工审阅）",
            "VDMA 粘滞 0x00015810；方法学 TIMING-17/36 与 I/O delay 缺口；J10 半屏未定性",
            "无 ILA（BASIC 许可禁用 debug core）；未做 ≥30 min 耐久",
        ],
        "colour_msb_root_cause": {
            "conclusion": "模块侧 DVP 字节 MSB 线 cmos_d[9] 无信号；真缺位，非顺序/位拼接错",
            "decisive_evidence": "彩条白条 B5=15(120) 非 31(255)、绿 G6=59(236) 非 63(252)，与两字节 MSB 同时丢失精确吻合",
            "excluded": ["传感器配置（0x301D/0x301E=0x00 正常通路、D 脚输出使能全开）", "RTL/引脚映射（五路核对 + J10/J11 复现）", "FPGA 引脚", "场景/白平衡", "通道顺序（R/B 互换实验）"],
            "action": "硬件返修/更换模块（唯一真修）",
        },
        "next_stage_entry": {
            "stage": 4,
            "input": "冻结的标准亮度灰度视频流（1280×720，RGB565 字内三通道同值 Y）",
            "notes": "PL 预处理与 INT8 主要计算、PS 调度/解码/NMS/显示交互；下游须消费 manifest 中冻结哈希，不使用“最新文件”",
        },
        "recovery": {
            "flash_deployment": ("bash scripts/stage3_t05/run_t05_board_capture.sh "
                                 "D:/codex-worktrees/dbdf/tmp/s3r06/t04_stdluma_20261022_r01 "
                                 "D:/codex-worktrees/dbdf/tmp/s3r06/t04_j11cmos2_elf_v10/elf_build/app/"
                                 "an5642_j11cmos2_v10_read.elf <tag> 60"),
            "frame_grab": "v11 ELF + scripts/stage3_t05/jtag_dump_frame.tcl <empty_dir> <FB from UART>",
            "colour_retest": "t05_freeze_20261021_r01/README.md §5",
        },
        "machine_check": checker,
        "limitations": [
            "灰度补偿非修复：蓝通道被弃用/按重建位参与亮度；不得用于颜色验收",
            "未做电气测量；模块内断点位置（走线/焊点/传感器脚）未区分",
            "未做 RTL 仿真；未做 ≥30 min 耐久",
        ],
    }
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    readme = [
        "# 阶段三收尾记录（灰度，2026-10-22）",
        "",
        "## 1. 决定",
        "Wong 2026-10-22：**暂不微调，按灰度收尾阶段三**；颜色项待**更换模块到货后**复测。",
        "",
        "## 2. 冻结/部署版本（可恢复）",
        "| 角色 | 产物 | SHA-256 |",
        "|---|---|---|",
        "| **部署位流（标准亮度灰度）** | `tmp/s3r06/t04_stdluma_20261022_r01/.../design_1_wrapper.bit` | `44e609cc…` |",
        "| XSA | `tmp/s3r06/t04_stdluma_20261022_r01/design_1_wrapper.xsa` | `90e1bdee…` |",
        "| 应用（只读） | `an5642_j11cmos2_v10_read.elf` | `1457cda4…` |",
        "| 取帧应用 | `an5642_j11cmos2_v11_freeze.elf` | `c01133b1…` |",
        "| 彩条应用（写 0x503D，仅易失） | `an5642_j11cmos2_v12_bars_freeze.elf` | `527a74fc…` |",
        "| 补丁 | `alinx_ov5640_stdluma_gray.patch`（`Y=(77R8+150G8+29B8)>>8`） | 见 manifest |",
        "| 备选（仅留档） | 纯绿灰度 `2f72aaa4…`；补偿彩色 `30db09ba…`（不用） | — |",
        "",
        "## 3. 验收状态",
        "| 关口 | 状态 |",
        "|---|---|",
        "| G1 开发交付 | PASS（构建退出码 0、证据含哈希/命令） |",
        "| G2 独立审查 | PARTIAL（Codex 更正 + dev-pl 有界网表核对；stdluma 补丁仅人工审阅） |",
        "| G3 实物验证 | PASS（灰度口径：实时、`\\|R−B\\|=0.0`、`\\|R−G\\|≈\\|G−B\\|≈2/255`、干净整帧；**未做 ≥30 min 耐久**） |",
        "| G4 任务验收 | PASS（按 Wong 修订判据“黑白可接受”） |",
        "| G5 阶段验收 | **以灰度收尾**；颜色项**明确受阻/待硬件**，不宣称完全通过 |",
        "",
        "## 4. 根因与真修",
        "模块侧 DVP 字节 MSB 线 `cmos_d[9]` 无信号 ⇒ **真缺位**（彩条实验：白条 B5=15/120 非 31/255、绿 G6=59/236 非 63/252）。",
        "配置、RTL/映射、FPGA 引脚、场景、通道顺序均已排除 ⇒ **唯一真修 = 硬件返修/更换模块**。",
        "",
        "## 5. 未关闭项（随阶段交接）",
        "1. 颜色验收（待模块，复测步骤见 `t05_freeze_20261021_r01/README.md §5`）；",
        "2. 模型域：灰度输入对**彩色训练模型**不可靠（第三方实测 tiny320 26%）——Wong 决定暂不微调；",
        "3. task-11 网表交叉核对未完成；VDMA 粘滞 `0x00015810`；方法学 TIMING-17/36 与 I/O 约束缺口；J10 半屏未定性；无 ILA；未做 ≥30 min 耐久。",
        "",
        "## 6. 下一阶段入口",
        "阶段 4：输入 = **冻结的标准亮度灰度视频流**（1280×720，字内三通道同值 `Y`）；后续 PL 预处理/INT8、PS 调度/解码/NMS/显示交互由 Wong 给出阶段目标后开启新总控任务；下游消费须用本 manifest 的冻结哈希。",
        "",
        "## 7. 恢复入口",
        "部署刷写、取帧、颜色复测命令见 `manifest.json` 的 `recovery` 字段；所有板卡操作为易失（JTAG 下载 + 应用侧寄存器读写），未烧 QSPI、未改接线。",
    ]
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(readme) + "\n")

    with open(os.path.join(OUT, "hashes.txt"), "w", encoding="utf-8") as f:
        for n in ("README.md", "manifest.json"):
            f.write("%s *%s\n" % (sha256(os.path.join(OUT, n)), n))
        for name, info in sorted(frozen.items()):
            f.write("%s  %s\n" % (info["sha256"], info["path"]))
        for name, info in sorted(files.items()):
            if info["sha256"]:
                f.write("%s  %s\n" % (info["sha256"], info["path"]))

    print("CLOSEOUT_DIR=%s" % OUT)
    print("FROZEN_OK=%d MISSING=%s" % (sum(1 for v in frozen.values() if v["matches_expected"]), missing))
    print("CHECKER_EXIT=%s" % checker.get("exit_code"))
    print("CHECKER_TAIL=%s" % " | ".join(checker.get("output_tail", [])[-4:]))
    print("HEAD=%s" % git("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    sys.exit(main())