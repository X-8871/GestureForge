#!/usr/bin/env python3
"""S3-T17：DVP 位完整性 / 真彩（机器可判部分）判定器（只读、可离线自测）。

背景（必须与证据一致，不凭记忆）
- 显示管道为 DVP 两字节拼接 RGB565：第一字节 = {g[2:0], b[4:0]}，第二字节 = {r[4:0], g[5:3]}；
  两个字节各自的 MSB 在厂商 IP 里走同一条 `cmos_d[9]`（本设计 J11/CMOS2 变体落 FPGA 引脚 F17）。
- 该线无信号时必然同时造成：显示蓝 bit7（B[4] 丢失）恒 0、显示绿 bit4（G[2] 丢失）恒 0。
  上次实测：蓝 bit7 置位率 0.000%、绿 bit4 置位率 0.000%，白条蓝 5 位 = 15(120) 而非 31(248)、
  绿 6 位 = 59(236) 而非 63(252) ⇒ 真缺位（通道置换无法修复）。
- 帧缓冲内存序为 B,G,R；1280×720 时每行 3840 字节。

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


def per_bit_table(white: dict, black: dict) -> list[dict]:
    """按 RGB565 有效字段逐位列出「白条应为 1 / 黑条应为 0」的可辨性。"""
    rows = []
    for channel, bits, white_key, black_key in (
        ("R", 5, "r_field5", "r_field5"),
        ("G", 6, "g_field6", "g_field6"),
        ("B", 5, "b_field5", "b_field5"),
    ):
        for k in range(bits - 1, -1, -1):
            exp_w = (white[white_key] >> k) & 1
            exp_b = (black[black_key] >> k) & 1
            ok = (exp_w == 1 and exp_b == 0)
            rows.append({
                "channel": channel,
                "field_bit": k,
                "display_byte_bit": k + (3 if channel in ("R", "B") else 2),
                "white_expected": 1,
                "black_expected": 0,
                "white_observed": exp_w,
                "black_observed": exp_b,
                "status": "OBSERVABLE_BOTH" if ok else "NOT_DISCRIMINATED",
            })
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


def evaluate(rows: dict[int, str], frame_bytes: bytes | None) -> dict:
    """按判定表评估；返回 dict（含 exit_code 与结论）。"""
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
    bits = per_bit_table(white, black)
    result["per_bit"] = bits
    c7 = all(item["status"] != "NOT_DISCRIMINATED" for item in bits)
    result["criteria"] = {
        "C1_white_R_full_scale": {"pass": c1, "observed": white["r"], "threshold": f">={TOL_R_FULL} (期望 248=31<<3)"},
        "C2_white_G_full_scale": {"pass": c2, "observed": white["g"], "threshold": f">={TOL_G_FULL} (期望 252=63<<2)"},
        "C3_white_B_full_scale": {"pass": c3, "observed": white["b"], "threshold": f">={TOL_B_FULL} (期望 248=31<<3)"},
        "C4_white_neutral": {"pass": c4, "observed": [white["r"], white["g"], white["b"]], "threshold": f"三通道差 <={TOL_NEUTRAL}"},
        "C5_black_zero": {"pass": c5, "observed": [black["r"], black["g"], black["b"]], "threshold": f"R=0 且 G,B<={TOL_BLACK}"},
        "C6_old_defect_signature_absent": {"pass": c6, "observed": signature_present},
        "C7_per_bit_discriminable": {"pass": c7, "discriminated": sum(1 for i in bits if i["status"] == "OBSERVABLE_BOTH"),
                                     "structural_na": sum(1 for i in bits if i["status"] == "NOT_APPLICABLE_STRUCTURAL_ZERO")},
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

    expectations = (
        ("A_real_archived_defect", real, "DEFECT_REPRODUCED", EXIT_DEFECT),
        ("B_synthetic_criterion", fixture_b, "BIT_INTEGRITY_PASS", EXIT_PASS),
        ("C_blue_only_restored", fixture_c, "INCONCLUSIVE_ATYPICAL", EXIT_ATYPICAL),
    )
    ok = True
    for name, data, want_verdict, want_code in expectations:
        rows = {y: data for y in FRAME_ROWS}
        res = evaluate(rows, data)
        matched = (res["verdict"] == want_verdict and res["exit_code"] == want_code)
        ok = ok and matched
        report["results"].append({
            "fixture": name,
            "expected_verdict": want_verdict,
            "expected_exit_code": want_code,
            "actual_verdict": res["verdict"],
            "actual_exit_code": res["exit_code"],
            "matched": matched,
            "white_segment": res.get("white_segment"),
            "black_segment": res.get("black_segment"),
            "blue_bit7_set_rate": res["signature"].get("blue_bit7_set_rate"),
            "green_bit4_set_rate": res["signature"].get("green_bit4_set_rate"),
        })
    report["conclusion"] = "SELFTEST_PASS" if ok else "SELFTEST_FAIL"
    report["exit_code"] = EXIT_PASS if ok else EXIT_ATYPICAL
    report["note"] = ("自测证明判定器能区分「旧缺位」「满足判定表」「非典型（只修蓝）」三类；"
                      "夹具B为合成数据，只校准判定表，不代表传感器行为。")
    return report


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="S3-T17 DVP 位完整性判定器", allow_abbrev=False)
    ap.add_argument("--rows", nargs="*", default=[], help="行样本文件（文件名须含 row_y<行号>）")
    ap.add_argument("--frame", default=None, help="整帧文件（1280×720×3，内存序 B,G,R）")
    ap.add_argument("--selftest", action="store_true", help="离线自测：真实缺陷帧 + 合成夹具")
    ap.add_argument("--fixture-dir", default=DEFAULT_FIXTURE_DIR, help="自测夹具输出目录（缓存，不入库）")
    ap.add_argument("--repo-root", default=os.getcwd(), help="仓库根（解析归档缺陷帧）")
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
            out = evaluate(rows, frame_bytes)
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