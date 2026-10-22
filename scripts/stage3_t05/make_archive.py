"""S3-T05 彩色缺位证据留档（2026-10-22）。

生成两个 RunId：
  A: report/evidence/S3-T05/t05_color_msb_missing_20261022_r01/
  B: report/evidence/S3-T14/v12_bars_freeze_tool_20261022_r01/

只做复制 + 哈希 + manifest/表格/复算脚本生成；不修改任何源目录，不覆盖旧 RunId。
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

WT = r"D:\codex-worktrees\dbdf"
TMP = os.path.join(WT, "tmp", "3", "S3-T05")
A = os.path.join(WT, "report", "evidence", "S3-T05", "t05_color_msb_missing_20261022_r01")
B = os.path.join(WT, "report", "evidence", "S3-T14", "v12_bars_freeze_tool_20261022_r01")

FRAMES = {
    "bars_raw": os.path.join(TMP, "bars_20261022_r01"),
    "pose1": os.path.join(TMP, "pose1_20261022_r01"),
    "pose2": os.path.join(TMP, "pose2_20261022_r01"),
    "colpose1": os.path.join(TMP, "colpose1_20261022_r01"),
}

V12_BARS_LINE = ("S3_DIAG12_BARS=503D before=0x00 after=0x80 readback=0x80 write_status=0")
# 后续 v10_read 运行（恢复实时）中 S3_DIAG5_SENS 行实测 503D=0x00 ⇒ 彩条已复位。
RESTORED_EVIDENCE = ("S3_DIAG5_SENS=4202=0x00 3008=0x02 4740=0x20 3035=0x21 3034=0x1A 4300=0x60 "
                     "501F=0x01 3824=0x04 503D=0x00（v10_read 运行，init 表已把 0x503D 写回 0x00）")

BARS_X = (80, 240, 400, 560, 720, 880, 1040, 1200)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", WT] + list(args), capture_output=True, text=True).stdout.strip()


def bar_table(bin_path):
    """按 3 行 x 8 段输出原序与 R/B 互换两套数值。"""
    data = open(bin_path, "rb").read()
    lines = []
    for y in (200, 360, 500):
        row = data[y * 1280 * 3:(y + 1) * 1280 * 3]
        for x in BARS_X:
            i = x * 3
            b, g, r = row[i], row[i + 1], row[i + 2]
            lines.append("y=%d x=%4d  asis(R,G,B)=%3d,%3d,%3d   rb_swap(R,G,B)=%3d,%3d,%3d"
                         % (y, x, r, g, b, b, g, r))
    return lines


RECOMPUTE = '''"""复算脚本：彩条帧的 8 段数值 + “两字节 MSB 同时丢失”签名检查。

用法: python recompute_color_msb.py <frame_full.bin>
内存序为 B,G,R（每像素 3 字节，1280x720）。第三方独立复算脚本可并列引用本文件。
"""
import sys

X = (80, 240, 400, 560, 720, 880, 1040, 1200)
BIN = sys.argv[1]
d = open(BIN, "rb").read()
for y in (200, 360, 500):
    row = d[y * 1280 * 3:(y + 1) * 1280 * 3]
    for x in X:
        i = x * 3
        b, g, r = row[i], row[i + 1], row[i + 2]
        print("y=%d x=%4d asis(R,G,B)=%3d,%3d,%3d rb_swap=%3d,%3d,%3d" % (y, x, r, g, b, b, g, r))

# 缺位签名：白条 5 位蓝应=15（120），绿 6 位应=59（236）；真值应为 31（255）与 63（252）。
row = d[360 * 1280 * 3:361 * 1280 * 3]
b, g, r = row[80 * 3], row[80 * 3 + 1], row[80 * 3 + 2]
print("VERDICT_B5=%d (expect 15 if blue MSB lost, 31 if intact)" % (b >> 3))
print("VERDICT_G6=%d (expect 59 if green bit2 lost, 63 if intact)" % (g >> 2))
'''


def ensure_empty(path):
    if os.path.exists(path):
        raise SystemExit("REFUSE_OVERWRITE: " + path)
    os.makedirs(path)


def copy(src, dst):
    shutil.copy2(src, dst)
    return sha256(dst)


def main():
    for p in (A, B):
        ensure_empty(p)

    artifacts = {}
    raw_total = 0

    # ---- A: 彩条 + 三张手势帧（asis/rbswap） ----
    pairs = [
        ("bars_raw.png", os.path.join(FRAMES["bars_raw"], "bars_raw.png"), "bars_raw.png"),
        ("bars_raw.bin", os.path.join(FRAMES["bars_raw"], "frame_full.bin"), "bars_raw_frame_full.bin"),
    ]
    for tag in ("pose1", "pose2", "colpose1"):
        for suf in ("asis", "rbswap"):
            pairs.append(("%s_%s.png" % (tag, suf), os.path.join(FRAMES[tag], "%s_%s.png" % (tag, suf)),
                          "%s_%s.png" % (tag, suf)))
        pairs.append(("%s.bin" % tag, os.path.join(FRAMES[tag], "frame_full.bin"),
                      "%s_frame_full.bin" % tag))

    for key, src, name in pairs:
        if not os.path.exists(src):
            raise SystemExit("MISSING_SOURCE: " + src)
        artifacts[key] = {"file": name, "sha256": copy(src, os.path.join(A, name)),
                          "source": os.path.relpath(src, WT).replace("\\", "/")}
        if name.endswith(".bin"):
            raw_total += os.path.getsize(os.path.join(A, name))

    table = bar_table(os.path.join(A, "bars_raw_frame_full.bin"))
    with open(os.path.join(A, "bars_values.txt"), "w", encoding="utf-8") as f:
        f.write("传感器内置彩条（无补偿原始基线，0x503D=0x80）8 段数值，3 行 x 8 段 x 2 变体\n")
        f.write("内存序 B,G,R；asis 按 R,G,B 渲染；rb_swap 强制 R/B 互换\n")
        f.write("判定：白条蓝 5 位=15(120) 而非 31(255)、绿 6 位=59(236) 而非 63(252)\n")
        f.write("      ⇒ 两个字节 MSB 同时丢失（真缺位），通道置换无法修复\n\n")
        f.write("\n".join(table) + "\n")

    with open(os.path.join(A, "recompute_color_msb.py"), "w", encoding="utf-8") as f:
        f.write(RECOMPUTE)

    script_hashes = {}
    for name in ("recompute_color_msb.py", "make_archive.py"):
        p = os.path.join(A, name)
        if os.path.exists(p):
            script_hashes[name] = sha256(p)
    for name in ("jtag_dump_frame.tcl",):
        p = os.path.join(WT, "scripts", "stage3_t05", name)
        script_hashes[name] = sha256(p)

    manifest_a = {
        "run_id": "t05_color_msb_missing_20261022_r01",
        "task": "S3-T05",
        "date": "2026-10-22",
        "purpose": "第三方要求的两个便宜实验：已知颜色测试图案 + R/B 互换，判定“真缺位 vs 顺序错”",
        "source_baseline_commit": git("rev-parse", "HEAD"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "v12_register_condition": V12_BARS_LINE,
        "v12_register_restored_evidence": RESTORED_EVIDENCE,
        "capture_command": (
            "bash scripts/stage3_t05/run_t05_board_capture.sh "
            "D:/codex-worktrees/dbdf/tmp/s3r06/t04_sof_fix_20261020_r01 "
            "D:/codex-worktrees/dbdf/tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/app/"
            "an5642_j11cmos2_v12_bars_freeze.elf bars1 55"),
        "dump_command": (
            "bash scripts/stage3_t03b/run_xsdb.sh scripts/stage3_t05/jtag_dump_frame.tcl "
            "<empty_dir> 0x00114C00   # 基址取自 UART 的 FB=（禁止写死）"),
        "hardware": {
            "board": "AX7020", "connector": "J11 (CMOS2)", "sensor": "OV5640 (AN5642 module)",
            "bitstream": "SOF fix baseline (no compensation)", "app": "v12 bars+freeze",
            "fb": "0x00114C00", "fb_bytes": "0x2A3000", "stride": "0x0F00",
        },
        "artifacts": artifacts,
        "script_sha256": script_hashes,
        "bars_values_file": "bars_values.txt",
        "recompute_script": {
            "file": "recompute_color_msb.py",
            "note": "第三方自有复算脚本可并列引用；本文件只读 .bin 输出同口径数值与签名判读",
        },
        "third_party_model_measurements": {
            "note": "由 Wong 转述的第三方实测，原始日志待补附",
            "gray_two_orders": "逐项一致（灰度帧 R≈G≈B，R/B 互换渲染像素级相同）",
            "compensated_color_two_orders": "tiny320 仅 26%，其余为 0",
            "verdict": "该帧不能用于模型识别（对彩色训练模型属强域外），也不满足颜色验收",
        },
        "volume_policy": {
            "raw_bin_total_bytes": raw_total,
            "limit_bytes": 15 * 1024 * 1024,
            "included_all_raw": raw_total <= 15 * 1024 * 1024,
            "note": "未搬入 tmp/** 整目录；未覆盖任何旧 RunId",
        },
        "limitations": [
            "彩条为合成图案，只证明链路缺位与色相顺序，不覆盖真实场景噪声/白平衡",
            "未做电气测量；模块侧断点位置（走线/焊点/传感器脚）仍未区分",
            "灰色帧与补偿彩色帧的模型输出为第三方转述，原始日志未附",
        ],
        "not_executed": ["RTL 仿真", "≥30 分钟耐久", "ILA 波形（BASIC 许可禁用 debug core）"],
    }
    with open(os.path.join(A, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_a, f, ensure_ascii=False, indent=2)

    with open(os.path.join(A, "README.md"), "w", encoding="utf-8") as f:
        f.write("# S3-T05 彩色缺位证据（2026-10-22）\n\n")
        f.write("## 结论\n\n传感器内置彩条经**无补偿原始链路**转储后：白条蓝 5 位 = 15（120）而非 31（255）、"
                "绿 6 位 = 59（236）而非 63（252）⇒ **两个字节 MSB 同时丢失（真缺位）**；"
                "色相顺序本身正确，**任何通道置换都无法修复**。\n\n")
        f.write("## 组件\n\n- `bars_raw.png` / `bars_raw_frame_full.bin`：彩条帧（决定性证据）\n")
        f.write("- `pose1/pose2_asis|rbswap.png`：灰度帧两种渲染（逐项一致）\n")
        f.write("- `colpose1_asis|rbswap.png`：补偿彩色帧两种渲染\n")
        f.write("- `bars_values.txt`：3 行 x 8 段 x 2 变体完整数值\n")
        f.write("- `recompute_color_msb.py`：复算/签名判读脚本\n")
        f.write("- `manifest.json`：基线 commit、寄存器条件、命令、哈希、限制\n\n")
        f.write("## 边界\n\n>%s\n" % RESTORED_EVIDENCE)
        f.write("\n彩条寄存器写入为**易失**且已复位；本 RunId 不覆盖任何旧证据。\n")

    # ---- B: v12 工具留档 ----
    src_v12 = os.path.join(WT, "report", "evidence", "S3-T05", "t05_sw_v12_20261022_r01")
    b_artifacts = {}
    for name in ("build_report.json", "README.md", "elf_build_evidence.txt"):
        p = os.path.join(src_v12, name)
        if os.path.exists(p):
            b_artifacts[name] = {"sha256": copy(p, os.path.join(B, name)),
                                 "source": os.path.relpath(p, WT).replace("\\", "/")}
    for rel, name in (("board/stage3/software/sensor/s3_t04_app_diag_v12.patch", "s3_t04_app_diag_v12.patch"),
                      ("board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch", "alinx_ov5640_sof_hrefgap.patch")):
        p = os.path.join(WT, rel)
        if os.path.exists(p):
            b_artifacts[name] = {"sha256": copy(p, os.path.join(B, name)), "source": rel}

    manifest_b = {
        "run_id": "v12_bars_freeze_tool_20261022_r01",
        "task": "S3-T14",
        "date": "2026-10-22",
        "tool": "an5642_j11cmos2_v12_bars_freeze.elf",
        "tool_sha256": "527a74fca6ea0774c34625015720a5163fc58557d44c64e29428700fd09845c5",
        "source_baseline_commit": git("rev-parse", "HEAD"),
        "writes_board_register": {
            "register": "0x503D (OV5640 test pattern / color bar enable, sensor side)",
            "value_written": "0x80",
            "observed": V12_BARS_LINE,
            "volatile_only": True,
            "restored_on_board": True,
            "restored_evidence": RESTORED_EVIDENCE,
            "halt_behaviour": "v12 自身会在 t≈20 s 停 S2MM 并保持 240 s（取帧设计）；当前板卡已回到非 HALT 的实时灰度应用，无 HALT",
        },
        "preconditions_for_future_use": [
            "使用前必须确认硬件占用：CDX-20261021-004/005 所载 2B 的书面占用尚未让出，未获让出不得占用板卡/会话",
            "不得把本工具当作通用“重置工具”反复使用；每次使用须登记 RunId、FB= 与恢复步骤",
            "写入前必须回读原值、写入后回读校验；读失败一律跳过写入",
        ],
        "artifacts": b_artifacts,
        "limitations": [
            "该工具会写板卡传感器寄存器 0x503D（易失）；本次已在板上恢复为 0x00",
            "未做 ≥30 分钟耐久；未做 RTL 仿真；无 ILA（BASIC 许可禁用 debug core）",
        ],
        "not_executed": ["长期占用测试", "非易失写入（禁止）"],
    }
    with open(os.path.join(B, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_b, f, ensure_ascii=False, indent=2)

    with open(os.path.join(B, "README.md"), "w", encoding="utf-8") as f:
        f.write("# S3-T14 v12 工具留档（2026-10-22）\n\n")
        f.write("工具：`an5642_j11cmos2_v12_bars_freeze.elf`（SHA-256 `527a74fc…9845c5`）\n\n")
        f.write("## 必须知道的写入行为\n\n")
        f.write("- 该工具会**写板卡传感器寄存器 `0x503D` = `0x80`**（彩条测试图案）；**仅易失**。\n")
        f.write("- 本次写入与回读：`%s`\n" % V12_BARS_LINE)
        f.write("- **已在板上恢复**：后续 v10_read 运行的 init 表把 `0x503D` 写回 `0x00`，实测 `%s`\n" % RESTORED_EVIDENCE)
        f.write("- v12 自身在 t≈20 s 停 S2MM 并保持 240 s（取帧设计）；**当前板卡已回到非 HALT 的实时灰度应用，无 HALT**。\n\n")
        f.write("## 使用前置条件\n\n")
        f.write("1. **使用前必须确认硬件占用**：`CDX-20261021-004/005` 所载 2B 的书面占用**尚未让出**，未获让出不得占用板卡与会话。\n")
        f.write("2. **不得当通用“重置工具”反复使用**；每次使用须登记 RunId、`FB=` 与恢复步骤。\n")
        f.write("3. 写入前回读原值、写入后回读校验；读失败一律跳过写入。\n")

    print("ARCHIVE_A=%s" % A)
    print("ARCHIVE_B=%s" % B)
    print("RAW_BIN_TOTAL_BYTES=%d (limit %d) included_all=%s" % (raw_total, 15 * 1024 * 1024, raw_total <= 15 * 1024 * 1024))
    print("ARTIFACTS_A=%d ARTIFACTS_B=%d" % (len(artifacts), len(b_artifacts)))
    print("HEAD=%s" % git("rev-parse", "--short", "HEAD"))
    print("A_SHA256_RECOMPUTE=%s" % script_hashes.get("recompute_color_msb.py"))
    print("A_SHA256_BARS_BIN=%s" % artifacts["bars_raw.bin"]["sha256"])
    print("A_SHA256_BARS_PNG=%s" % artifacts["bars_raw.png"]["sha256"])


if __name__ == "__main__":
    sys.exit(main())