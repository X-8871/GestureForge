#!/usr/bin/env python3
"""S3-T17：DVP 位完整性 / 真彩（机器可判部分）判定器（只读、可离线自测）。

背景（必须与证据一致，不凭记忆）
- 显示管道为 DVP 两字节拼接 RGB565：**第一字节 = {b[4:0], g[5:3]}（MSB = B[4]）、
  第二字节 = {g[2:0], r[4:0]}（MSB = G[2]）**；16 位字字段布局 R=word[4:0]、G=word[10:5]、
  B=word[15:11]（由归档 subset-converter 网表复算：`m_axis_tdata[15:10]=s_axis_tdata[10:5]`、
  `m_axis_tdata[7:3]=s_axis_tdata[15:11]`、`m_axis_tdata[23:19]=s_axis_tdata[4:0]`）。
  两个字节各自的 MSB 在厂商 IP 里走同一条 `cmos_d[9]`（本设计 J11/CMOS2 变体落 FPGA 引脚 F17）。
- 该线无信号时必然同时造成：显示蓝 bit7（B[4] 丢失）恒 0、显示绿 bit4（G[2] 丢失）恒 0。
  上次实测：蓝 bit7 置位率 0.000%、绿 bit4 置位率 0.000%，白条蓝 5 位 = 15(120) 而非 31(248)、
  绿 6 位 = 59(236) 而非 63(252) ⇒ 真缺位（通道置换无法修复）。
- **命名限制（评审 N-1）**：「蓝 bit7 / 绿 bit4」是**帧缓冲通道名**（offset0/offset1），其与 DVP 字节的
  对应来自归档网表（offset0=B、offset1=G、offset2=R）；本轮盘上**没有**厂商 `cmos_8_16bit.v` 拼接源码
  （已被缓存清理），故「哪个 DVP 字节承载哪个通道」属**推断**。阶段B 报告请以**数值判据**陈述
  （offset0 bit7、offset1 bit4、offset2 完整），不单独依赖通道命名。
- 帧缓冲内存序为 B,G,R；1280×720 时每行 3840 字节。
- **前提（评审 N-4）**：本仓库 `core.autocrlf=true`；工作区口径复核须用
  `git -c core.autocrlf=false clone` 或 `git cat-file blob <rev>:<path>`，见 `scripts/stage3_t17/README.md`。

判定口径见 `report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/t17_judgement_table.json`。

退出码（**与旧脚本 `scripts/stage3_t05/analyze_missing_msb_signature.py` 语义不同，不得混用**：
旧脚本 0=符合缺位签名、1=不符合签名；本脚本 0=位完整性通过）：
    0 = BIT_INTEGRITY_PASS        全部判定项通过（位完整性机器判定通过）
    1 = DEFECT_REPRODUCED         复现「两字节 MSB 同时丢失」旧缺位签名（判板侧/连接侧方向）
    2 = USAGE_OR_INPUT_ERROR      用法/输入错误（缺文件、长度非法、彩条段不足）
    3 = INCONCLUSIVE_ATYPICAL     非典型/证据不足，需人工判读（不得当通过）

用法：
    python -B analyze_t17_bit_integrity.py --rows <row_y200.bin> <row_y360.bin> <row_y500.bin> [--json-out f.json]
    python -B analyze_t17_bit_integrity.py --frame <frame_full.bin> [--json-out f.json]
    python -B analyze_t17_bit_integrity.py --selftest [--fixture-dir <tmp目录>] [--json-out f.json]

限制：本判定器只处理数值产物的位完整性；「真彩帧在 HDMI 上正确显色」必须由 Wong 目视确认，
      脚本只能给出可判定的中性度与满量程证据，并始终输出 requires_human_visual=true。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

UTC8 = timezone(timedelta(hours=8))
WIDTH = 1280
ROW_BYTES = WIDTH * 3
BAR_X = (80, 240, 400, 560, 720, 880, 1040, 1200)
FRAME_ROWS = (200, 360, 500)
ROW_RE = re.compile(r"row_y(\d+)", re.IGNORECASE)

# 判定阈值（RGB565→8 位为移位扩展，故白条满量程期望 R=248、G=252、B=248；容差为文档化的余量）
TOL_R_FULL = 240
TOL_G_FULL = 248
TOL_B_FULL = 240
TOL_NEUTRAL = 8
TOL_BLACK = 8

# C7 字段位计数（评审 B-1）：每个显示字节 8 位 = 字段位 + 结构性恒 0 低位
#   R：字段 5 位（field4..0 → 显示 bit7..3）+ 结构性低位 3（显示 bit2..0）
#   G：字段 6 位（field5..0 → 显示 bit7..2）+ 结构性低位 2（显示 bit1..0）
#   B：字段 5 位（field4..0 → 显示 bit7..3）+ 结构性低位 3（显示 bit2..0）
#   ⇒ 字段位合计 5+6+5 = 16；结构性恒 0 低位合计 3+2+3 = 8（16+8 = 3 字节 × 8 = 24）
FIELD_BITS = {"R": 5, "G": 6, "B": 5}
STRUCTURAL_ZERO_BITS = {"R": 3, "G": 2, "B": 3}
# 黑条字段容差（与 C5 的 TOL_BLACK=8 一致）：字段值 <= 该值视为「容差内 0」，不判不可辨（评审 B-2）
FIELD_TOLERANCE = {ch: TOL_BLACK >> (3 if ch in ("R", "B") else 2) for ch in ("R", "G", "B")}  # R/B:1, G:2

EXIT_PASS = 0
EXIT_DEFECT = 1
EXIT_USAGE = 2
EXIT_ATYPICAL = 3

DEFAULT_FIXTURE_DIR = "tmp/3/S3-T17/t17_analyzer_selftest_r01"
ARCHIVED_DEFECT_FRAME = (
    "report/evidence/S3-T05/t05_color_msb_missing_20261022_r01/bars_raw_frame_full.bin"
)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_rows_by_name(paths) -> tuple[dict[int, str], list[str]]:
    rows: dict[int, str] = {}
    problems: list[str] = []
    for path in paths:
        if not os.path.isfile(path):
            problems.append(f"文件不存在：{path}")
            continue
        m = ROW_RE.search(os.path.basename(path))
        if m is None:
            problems.append(f"文件名不含 row_y<行号>，无法确定行位置：{path}")
            continue
        rows[int(m.group(1))] = path
    return rows, problems


def extract_rows_from_frame(path: str) -> tuple[dict[int, str], list[str], bytes]:
    if not os.path.isfile(path):
        return {}, [f"文件不存在：{path}"], b""
    data = open(path, "rb").read()
    per_row = ROW_BYTES
    need = max(FRAME_ROWS) * per_row + per_row
    if len(data) < need:
        return {}, [f"整帧长度不足：{len(data)} < {need}（1280×720×3）"], data
    return {y: data for y in FRAME_ROWS}, [], data


def row_bytes(source, y: int) -> bytes | None:
    """取某行的 1280 像素 × 3 字节。source 为 bytes 时按整帧切片，为路径时按行文件读。"""
    if isinstance(source, bytes):
        start = y * ROW_BYTES
        chunk = source[start:start + ROW_BYTES]
        return chunk if len(chunk) == ROW_BYTES else None
    data = open(source, "rb").read()
    if len(data) < ROW_BYTES:
        return None
    return data[:ROW_BYTES]


def stats_for_row(chunk: bytes) -> dict:
    n = len(chunk) // 3
    blue = chunk[0::3]
    green = chunk[1::3]
    red = chunk[2::3]
    return {
        "pixels": n,
        "maxB": max(blue),
        "maxG": max(green),
        "maxR": max(red),
        "minB": min(blue),
        "minG": min(green),
        "minR": min(red),
        "blue_bit7_set": sum(1 for v in blue if v & 0x80),
        "green_bit4_set": sum(1 for v in green if v & 0x10),
    }


def bar_table(chunk: bytes) -> list[dict]:
    out = []
    for x in BAR_X:
        i = x * 3
        if i + 2 >= len(chunk):
            continue
        b, g, r = chunk[i], chunk[i + 1], chunk[i + 2]
        out.append({
            "x": x,
            "r": r, "g": g, "b": b,
            "r_field5": r >> 3, "g_field6": g >> 2, "b_field5": b >> 3,
        })
    return out


def per_bit_table(white: dict, black: dict, strict_black_bits: bool = False) -> list[dict]:
    """按 RGB565 有效字段逐位列出可辨性（C7）。

    对齐口径（默认，与 C5 一致，评审 B-2 关闭）：黑条字段值落在 `FIELD_TOLERANCE` 内视为
    「容差内 0」，不因传感器黑条自身的 1 LSB 残差（G=4 ⇒ G6=1）判不可辨 ⇒ 修好时可达 16/16。
    严格口径（`strict_black_bits=True`，仅供对照/自证）：黑条字段位必须为 0 ⇒ 黑条残差会多判
    G6 bit0 不可辨（修好时最多 15/16，与 C5 冲突），**已弃用为默认**。
    """
    rows = []
    for channel, bits, key in (("R", 5, "r_field5"), ("G", 6, "g_field6"), ("B", 5, "b_field5")):
        w_val, b_val = white[key], black[key]
        tol = FIELD_TOLERANCE[channel]
        for k in range(bits - 1, -1, -1):
            w_bit = (w_val >> k) & 1
            b_bit = (b_val >> k) & 1
            row = {
                "channel": channel,
                "field_bit": k,
                "display_byte_bit": k + (3 if channel in ("R", "B") else 2),
                "white_expected": 1,
                "black_expected": 0,
                "white_observed": w_bit,
                "black_observed": b_bit,
                "black_field_value": b_val,
                "black_within_tolerance": b_val <= tol,
            }
            if w_bit != 1:
                row["status"] = "NOT_DISCRIMINATED"
                row["reason"] = "WHITE_BIT_NOT_SET（白条字段位为 0 ⇒ 缺位）"
            elif strict_black_bits:
                if b_bit == 0:
                    row["status"] = "OBSERVABLE_BOTH"
                else:
                    row["status"] = "NOT_DISCRIMINATED"
                    row["reason"] = "BLACK_BIT_SET_STRICT（严格口径：黑条该位为 1）"
            elif b_val <= tol:
                row["status"] = "OBSERVABLE_BOTH"
                row["reason"] = "BLACK_WITHIN_TOLERANCE（黑条字段值在 C5 容差内，不计不可辨）"
            elif b_bit:
                row["status"] = "NOT_DISCRIMINATED"
                row["reason"] = "BLACK_FIELD_EXCEEDS_TOLERANCE（黑条字段值超容差且该位为 1）"
            else:
                row["status"] = "OBSERVABLE_BOTH"
            rows.append(row)
    for channel, low_bits, shift in (("R", 3, 3), ("B", 3, 3), ("G", 2, 2)):
        for k in range(low_bits - 1, -1, -1):
            rows.append({
                "channel": channel,
                "field_bit": f"display_bit{k}",
                "display_byte_bit": k,
                "status": "NOT_APPLICABLE_STRUCTURAL_ZERO",
                "reason": "RGB565 5/6/5 移位扩展：该低位在 8 位显示字节中恒 0，不是缺位",
            })
    return rows


def evaluate(rows: dict[int, str], frame_bytes: bytes | None,
             strict_black_bits: bool = False) -> dict:
    """按判定表评估；返回 dict（含 exit_code 与结论）。

    `strict_black_bits=True` 用于复现修复前的严格口径（仅供对照/自证），默认用与 C5 对齐的口径。
    """
    result: dict = {
        "inputs": [],
        "rows": {},
        "signature": {},
        "bar_segments": [],
        "criteria": {},
        "per_bit": [],
        "verdict": None,
        "exit_code": None,
        "requires_human_visual": True,
    }
    usable: dict[int, bytes] = {}
    for y, src in sorted(rows.items()):
        chunk = row_bytes(frame_bytes if frame_bytes is not None else src, y)
        if chunk is None or len(chunk) % 3 != 0:
            result["inputs"].append({"row_y": y, "source": src if not isinstance(src, bytes) else "<frame>",
                                     "status": "SKIPPED_INVALID_LENGTH"})
            continue
        result["inputs"].append({"row_y": y, "source": src if not isinstance(src, bytes) else "<frame>",
                                 "status": "SCANNED", "bytes": len(chunk)})
        usable[y] = chunk
    result["scanned_rows"] = sorted(usable)
    if not usable:
        result["verdict"] = "USAGE_OR_INPUT_ERROR"
        result["exit_code"] = EXIT_USAGE
        result["reason"] = "没有可用行样本（缺失或长度非 3 的倍数）"
        return result

    total_px = 0
    blue_set = green_set = 0
    for y, chunk in usable.items():
        st = stats_for_row(chunk)
        result["rows"][str(y)] = st
        total_px += st["pixels"]
        blue_set += st["blue_bit7_set"]
        green_set += st["green_bit4_set"]
    blue_rate = blue_set / total_px if total_px else 0.0
    green_rate = green_set / total_px if total_px else 0.0
    signature_present = (blue_rate == 0.0 and green_rate == 0.0)
    result["signature"] = {
        "pixels_scanned": total_px,
        "blue_bit7_set_rate": blue_rate,
        "green_bit4_set_rate": green_rate,
        "old_defect_signature_present": signature_present,
        "note": "旧签名 = 蓝 bit7 与绿 bit4 置位率同时为 0（两字节 MSB 同源同断）",
    }

    judge_y = 360 if 360 in usable else sorted(usable)[len(usable) // 2]
    segs = bar_table(usable[judge_y])
    result["bar_judge_row_y"] = judge_y
    result["bar_segments"] = segs
    if len(segs) < 8:
        result["verdict"] = "USAGE_OR_INPUT_ERROR"
        result["exit_code"] = EXIT_USAGE
        result["reason"] = f"彩条段不足 8 段（实得 {len(segs)}）"
        return result

    white = max(segs, key=lambda s: s["r"] + s["g"] + s["b"])
    black = min(segs, key=lambda s: s["r"] + s["g"] + s["b"])
    result["white_segment"] = white
    result["black_segment"] = black

    c1 = white["r"] >= TOL_R_FULL
    c2 = white["g"] >= TOL_G_FULL
    c3 = white["b"] >= TOL_B_FULL
    c4 = (abs(white["r"] - white["g"]) <= TOL_NEUTRAL
          and abs(white["g"] - white["b"]) <= TOL_NEUTRAL
          and abs(white["r"] - white["b"]) <= TOL_NEUTRAL)
    c5 = (black["r"] == 0 and black["g"] <= TOL_BLACK and black["b"] <= TOL_BLACK)
    c6 = not signature_present
    aligned_bits = per_bit_table(white, black)
    strict_bits = per_bit_table(white, black, strict_black_bits=True)
    bits = strict_bits if strict_black_bits else aligned_bits
    result["per_bit"] = bits
    result["per_bit_aligned"] = aligned_bits
    result["per_bit_strict_variant"] = strict_bits
    result["per_bit_mode"] = "STRICT_BLACK_BITS" if strict_black_bits else "TOLERANCE_ALIGNED_WITH_C5"
    c7 = all(item["status"] != "NOT_DISCRIMINATED" for item in bits)
    field_total = sum(FIELD_BITS.values())                     # 5+6+5 = 16
    structural_total = sum(STRUCTURAL_ZERO_BITS.values())      # 3+2+3 = 8
    disc = sum(1 for i in bits if i["status"] == "OBSERVABLE_BOTH")
    disc_aligned = sum(1 for i in aligned_bits if i["status"] == "OBSERVABLE_BOTH")
    disc_strict = sum(1 for i in strict_bits if i["status"] == "OBSERVABLE_BOTH")
    result["per_bit_count"] = {
        "field_bits_total": field_total,
        "structural_zero_bits_total": structural_total,
        "total_display_bits": field_total + structural_total,
        "basis": "R 字段 5 + G 字段 6 + B 字段 5 = 16；R/B 结构性低位各 3、G 结构性低位 2 ⇒ 8；16+8 = 24 = 3 字节 × 8 位",
        "verdict_mode": result["per_bit_mode"],
        "discriminated_used_for_c7": disc,
        "discriminated_aligned": disc_aligned,
        "discriminated_strict_variant": disc_strict,
        "not_discriminated": [f"{i['channel']} field_bit {i['field_bit']}（{i.get('reason')}）"
                              for i in bits if i["status"] == "NOT_DISCRIMINATED"],
        "field_tolerance": FIELD_TOLERANCE,
        "note": "C7 默认采用对齐口径（黑条字段值 <= FIELD_TOLERANCE 不计不可辨）；严格口径仅作对照（评审 B-2）。",
    }
    result["criteria"] = {
        "C1_white_R_full_scale": {"pass": c1, "observed": white["r"], "threshold": f">={TOL_R_FULL} (期望 248=31<<3)"},
        "C2_white_G_full_scale": {"pass": c2, "observed": white["g"], "threshold": f">={TOL_G_FULL} (期望 252=63<<2)"},
        "C3_white_B_full_scale": {"pass": c3, "observed": white["b"], "threshold": f">={TOL_B_FULL} (期望 248=31<<3)"},
        "C4_white_neutral": {"pass": c4, "observed": [white["r"], white["g"], white["b"]], "threshold": f"三通道差 <={TOL_NEUTRAL}"},
        "C5_black_zero": {"pass": c5, "observed": [black["r"], black["g"], black["b"]], "threshold": f"R=0 且 G,B<={TOL_BLACK}"},
        "C6_old_defect_signature_absent": {"pass": c6, "observed": signature_present},
        "C7_per_bit_discriminable": {
            "pass": c7,
            "discriminated_used_for_verdict": f"{disc}/{field_total}",
            "discriminated_aligned": f"{disc_aligned}/{field_total}",
            "discriminated_strict_variant": f"{disc_strict}/{field_total}",
            "structural_na": structural_total,
            "verdict_mode": result["per_bit_mode"],
            "tolerance_aligned_with_C5": not strict_black_bits,
        },
    }
    failed = [k for k, v in result["criteria"].items() if not v["pass"]]
    if not failed:
        result["verdict"] = "BIT_INTEGRITY_PASS"
        result["exit_code"] = EXIT_PASS
    elif signature_present and not (c2 and c3):
        result["verdict"] = "DEFECT_REPRODUCED"
        result["exit_code"] = EXIT_DEFECT
        result["reason"] = "复现旧缺位签名，且白条绿/蓝未达满量程 ⇒ 判板侧/连接侧方向（仍非电气定位）"
    else:
        result["verdict"] = "INCONCLUSIVE_ATYPICAL"
        result["exit_code"] = EXIT_ATYPICAL
        result["reason"] = "非典型组合，需人工判读：失败项=" + ",".join(failed)
    result["failed_criteria"] = failed
    result["note"] = ("机器判定只覆盖位完整性与彩条数值；真彩显示必须由 Wong 目视确认"
                      "（不偏黄、不偏青），脚本不代替目视验收。")
    return result


def build_synthetic_criterion_frame() -> bytes:
    """合成「判定表满足」夹具（非传感器数据）：白条满量程 + 黑条 0 + 各字段位可辨。"""
    segs = [
        (248, 252, 248), (248, 252, 128), (128, 252, 128), (64, 252, 64),
        (192, 0, 128), (168, 0, 32), (0, 4, 24), (0, 0, 0),
    ]
    row = bytearray()
    for x in range(WIDTH):
        idx = min(range(len(BAR_X)), key=lambda i: abs(BAR_X[i] - x))
        r, g, b = segs[idx]
        row += bytes((b, g, r))
    assert len(row) == ROW_BYTES
    frame = bytearray()
    for y in range(720):
        frame += row
    return bytes(frame)


def restore_missing_bits(frame: bytes, fix_blue: bool, fix_green: bool) -> bytes:
    """按「缺位模型」的逆操作恢复：蓝 |= 0x80、绿 |= 0x10（仅用于夹具，非真实数据）。"""
    out = bytearray(frame)
    for i in range(0, len(out) - 2, 3):
        if fix_blue:
            out[i] |= 0x80
        if fix_green:
            out[i + 1] |= 0x10
    return bytes(out)


def segment_index_for_x(x: int) -> int:
    """按最近彩条中心确定像素所属段序号（与 bar_table 的取样位置一致）。"""
    return min(range(len(BAR_X)), key=lambda i: abs(BAR_X[i] - x))


def set_segments(frame: bytes, overrides: dict) -> bytes:
    """把指定彩条段整体替换为给定 (r,g,b)（内存序 B,G,R）；其余像素逐字节保持不变。"""
    out = bytearray(frame)
    for y in range(len(out) // ROW_BYTES):
        base = y * ROW_BYTES
        for x in range(WIDTH):
            idx = segment_index_for_x(x)
            if idx in overrides:
                r, g, b = overrides[idx]
                i = base + x * 3
                out[i], out[i + 1], out[i + 2] = b, g, r
    return bytes(out)


def segment_indices_of(frame: bytes) -> tuple[int, int]:
    """用 y=360 行判定白条/黑条所在段序号。"""
    row = frame[360 * ROW_BYTES:(360 + 1) * ROW_BYTES]
    segs = bar_table(row)
    white_idx = max(range(len(segs)), key=lambda i: segs[i]["r"] + segs[i]["g"] + segs[i]["b"])
    black_idx = min(range(len(segs)), key=lambda i: segs[i]["r"] + segs[i]["g"] + segs[i]["b"])
    return white_idx, black_idx


def run_selftest(fixture_dir: str, repo_root: str) -> dict:
    os.makedirs(fixture_dir, exist_ok=True)
    archived = os.path.join(repo_root, ARCHIVED_DEFECT_FRAME)
    report: dict = {"fixtures": [], "results": [], "conclusion": None}
    if not os.path.isfile(archived):
        report["conclusion"] = "USAGE_OR_INPUT_ERROR"
        report["reason"] = f"缺归档缺陷帧：{archived}"
        report["exit_code"] = EXIT_USAGE
        return report
    real = open(archived, "rb").read()
    report["fixtures"].append({"name": "A_real_archived_defect", "source": ARCHIVED_DEFECT_FRAME,
                               "sha256": sha256_file(archived), "bytes": len(real),
                               "kind": "真实归档缺陷帧"})
    fixture_b_path = os.path.join(fixture_dir, "fixture_B_criterion.bin")
    fixture_b = build_synthetic_criterion_frame()
    open(fixture_b_path, "wb").write(fixture_b)
    report["fixtures"].append({"name": "B_synthetic_criterion", "path": fixture_b_path,
                               "sha256": hashlib.sha256(fixture_b).hexdigest(), "bytes": len(fixture_b),
                               "kind": "合成判定表夹具（非传感器数据）"})
    fixture_c_path = os.path.join(fixture_dir, "fixture_C_blue_only.bin")
    fixture_c = restore_missing_bits(real, fix_blue=True, fix_green=False)
    open(fixture_c_path, "wb").write(fixture_c)
    report["fixtures"].append({"name": "C_blue_only_restored", "path": fixture_c_path,
                               "sha256": hashlib.sha256(fixture_c).hexdigest(), "bytes": len(fixture_c),
                               "kind": "真实缺陷帧只恢复蓝 MSB（绿仍缺）——非典型夹具"})

    white_idx, black_idx = segment_indices_of(real)
    fixture_d = restore_missing_bits(real, fix_blue=True, fix_green=True)
    fixture_e = set_segments(fixture_d, {black_idx: (0, 0, 0)})
    fixture_f = set_segments(real, {white_idx: (248, 252, 248), black_idx: (0, 4, 0)})
    extra = (
        ("D_both_bits_restored_black_also_set", fixture_d,
         "真实缺陷帧两处缺位均 OR 恢复（黑条随之被置位）⇒ 应判非典型，不得当通过"),
        ("E_D_plus_black_cleared", fixture_e, "D 再把黑条清零 ⇒ 应通过（证明 exit 0 可达）"),
        ("F_table_if_fixed_white_full_black_residual", fixture_f,
         "判定表自声明 if_fixed（白 248/252/248、黑 0,4,0）⇒ 对齐口径必须 exit 0（评审 B-2 关闭）"),
    )
    for name, data, kind in extra:
        path = os.path.join(fixture_dir, f"fixture_{name[0]}.bin")
        open(path, "wb").write(data)
        report["fixtures"].append({"name": name, "path": path,
                                   "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                                   "kind": kind, "white_segment_index": white_idx,
                                   "black_segment_index": black_idx})

    expectations = (
        ("A_real_archived_defect", real, False, "DEFECT_REPRODUCED", EXIT_DEFECT),
        ("B_synthetic_criterion", fixture_b, False, "BIT_INTEGRITY_PASS", EXIT_PASS),
        ("C_blue_only_restored", fixture_c, False, "INCONCLUSIVE_ATYPICAL", EXIT_ATYPICAL),
        ("D_both_bits_restored_black_also_set", fixture_d, False, "INCONCLUSIVE_ATYPICAL", EXIT_ATYPICAL),
        ("E_D_plus_black_cleared", fixture_e, False, "BIT_INTEGRITY_PASS", EXIT_PASS),
        ("F_table_if_fixed_white_full_black_residual", fixture_f, False, "BIT_INTEGRITY_PASS", EXIT_PASS),
        ("F_probe_strict_black_bits", fixture_f, True, "INCONCLUSIVE_ATYPICAL", EXIT_ATYPICAL),
    )
    ok = True
    for name, data, strict, want_verdict, want_code in expectations:
        rows = {y: data for y in FRAME_ROWS}
        res = evaluate(rows, data, strict_black_bits=strict)
        matched = (res["verdict"] == want_verdict and res["exit_code"] == want_code)
        ok = ok and matched
        report["results"].append({
            "fixture": name,
            "strict_black_bits": strict,
            "expected_verdict": want_verdict,
            "expected_exit_code": want_code,
            "actual_verdict": res["verdict"],
            "actual_exit_code": res["exit_code"],
            "matched": matched,
            "white_segment": res.get("white_segment"),
            "black_segment": res.get("black_segment"),
            "blue_bit7_set_rate": res["signature"].get("blue_bit7_set_rate"),
            "green_bit4_set_rate": res["signature"].get("green_bit4_set_rate"),
            "per_bit_mode": res.get("per_bit_mode"),
            "discriminated_used_for_c7": res.get("per_bit_count", {}).get("discriminated_used_for_c7"),
            "discriminated_aligned": res.get("per_bit_count", {}).get("discriminated_aligned"),
            "discriminated_strict_variant": res.get("per_bit_count", {}).get("discriminated_strict_variant"),
            "field_bits_total": res.get("per_bit_count", {}).get("field_bits_total"),
            "not_discriminated": res.get("per_bit_count", {}).get("not_discriminated"),
            "failed_criteria": res.get("failed_criteria"),
        })
    report["conclusion"] = "SELFTEST_PASS" if ok else "SELFTEST_FAIL"
    report["exit_code"] = EXIT_PASS if ok else EXIT_ATYPICAL
    report["note"] = ("自测证明判定器能区分「旧缺位」「满足判定表」「非典型（只修蓝 / 缺位恢复但黑条被置位）」；"
                      "夹具 F（判定表自声明 if_fixed）在对齐口径下 exit 0，其严格口径探针 exit 3 —— "
                      "证明「修好即通过」可达且修复可见（评审 B-2/B-1）。"
                      "夹具 B/F 为合成或改写数据，只校准判定表，不代表传感器行为。")
    return report


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="S3-T17 DVP 位完整性判定器", allow_abbrev=False)
    ap.add_argument("--rows", nargs="*", default=[], help="行样本文件（文件名须含 row_y<行号>）")
    ap.add_argument("--frame", default=None, help="整帧文件（1280×720×3，内存序 B,G,R）")
    ap.add_argument("--selftest", action="store_true", help="离线自测：真实缺陷帧 + 合成夹具")
    ap.add_argument("--fixture-dir", default=DEFAULT_FIXTURE_DIR, help="自测夹具输出目录（缓存，不入库）")
    ap.add_argument("--repo-root", default=os.getcwd(), help="仓库根（解析归档缺陷帧）")
    ap.add_argument("--strict-black-bits", action="store_true",
                    help="复现修复前的严格口径（黑条字段位必须为 0）；仅供对照/自证，不建议用于验收")
    ap.add_argument("--json-out", default=None, help="把完整结果写入该 JSON 文件")
    args = ap.parse_args(argv)

    stamp = datetime.now(UTC8).strftime("%Y-%m-%dT%H:%M:%S+08:00")
    if args.selftest:
        out = run_selftest(args.fixture_dir, args.repo_root)
        out["created_utc8"] = stamp
        code = out["exit_code"]
        print(f"SELFTEST 结论={out['conclusion']} 退出码={code}")
        for item in out.get("results", []):
            print("  %-26s 期望=%s(%d) 实际=%s(%d) 匹配=%s" % (
                item["fixture"], item["expected_verdict"], item["expected_exit_code"],
                item["actual_verdict"], item["actual_exit_code"], item["matched"]))
    else:
        problems: list[str] = []
        frame_bytes = None
        if args.frame:
            rows, problems, frame_bytes = extract_rows_from_frame(args.frame)
        else:
            rows, problems = parse_rows_by_name(args.rows)
        if problems:
            out = {"created_utc8": stamp, "verdict": "USAGE_OR_INPUT_ERROR", "exit_code": EXIT_USAGE,
                   "problems": problems}
            code = EXIT_USAGE
            print("输入问题：" + "；".join(problems))
        else:
            out = evaluate(rows, frame_bytes, strict_black_bits=args.strict_black_bits)
            out["created_utc8"] = stamp
            code = out["exit_code"]
            print("判定=%s 退出码=%d" % (out["verdict"], code))
            print("扫描行=%s 像素=%d 蓝bit7置位率=%.4f%% 绿bit4置位率=%.4f%%" % (
                out["scanned_rows"], out["signature"]["pixels_scanned"],
                100 * out["signature"]["blue_bit7_set_rate"],
                100 * out["signature"]["green_bit4_set_rate"]))
            if out.get("white_segment"):
                w, b = out["white_segment"], out["black_segment"]
                print("白条(R,G,B)=%d,%d,%d  黑条=%d,%d,%d" % (w["r"], w["g"], w["b"], b["r"], b["g"], b["b"]))
            cnt = out.get("per_bit_count", {})
            print("字段位计数：字段位 %s / 结构性恒 0 %s（共 %s）；口径=%s；可辨 %s（对齐口径 %s、严格口径 %s）" % (
                cnt.get("field_bits_total"), cnt.get("structural_zero_bits_total"),
                cnt.get("total_display_bits"), cnt.get("verdict_mode"),
                cnt.get("discriminated_used_for_c7"), cnt.get("discriminated_aligned"),
                cnt.get("discriminated_strict_variant")))
            if cnt.get("not_discriminated"):
                print("不可辨位：" + "；".join(cnt["not_discriminated"]))
            for k, v in out["criteria"].items():
                print("  [%s] %s" % ("PASS" if v["pass"] else "FAIL", k))
            if out.get("failed_criteria"):
                print("失败项：" + ",".join(out["failed_criteria"]))
            print("注意：真彩显示仍须 Wong 目视确认（requires_human_visual=true）")
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        print(f"JSON_OUT={args.json_out}")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))