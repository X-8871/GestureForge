#!/usr/bin/env python3
"""以已核实的 B/G/R 内存顺序判读本轮实际板测，不把机器判据当作目视验收。"""

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys


def sha256(path):
    """绑定实际输入文件身份。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(rows):
    """每行必须是 1280 个三字节像素；蓝通道只能使用既定近似重建字母表。"""
    alphabet = {value * 8 for value in (0, 2, 4, 6, 8, 10, 12, 14, 17, 19, 21, 23, 25, 27, 29, 31)}
    reports = []
    maximum = 0
    all_alphabet = True
    lower_multiple16 = True
    for name, blob in rows:
        if len(blob) != 3840:
            raise ValueError(f"行长度错误：{name}，实际{len(blob)}，预期3840")
        channels = []
        for offset, color in enumerate(("B", "G", "R")):
            counts = Counter(blob[offset::3])
            channels.append({"channel": color, "byte_offset": offset, "maximum": max(counts),
                             "over127": sum(n for value, n in counts.items() if value > 127),
                             "histogram": dict(sorted(counts.items()))})
        blue = set(blob[0::3])
        maximum = max(maximum, max(blue))
        all_alphabet &= blue.issubset(alphabet)
        lower_multiple16 &= all(value % 16 == 0 for value in blue if value <= 127)
        reports.append({"row": name, "channels": channels})
    checks = {"nonempty_rows": bool(reports), "blue_rebuild_alphabet": all_alphabet,
              "blue_low_values_multiple16": lower_multiple16, "maxB_over127": maximum > 127}
    return {"rows": reports, "maxB": maximum, "checks": checks}


def selftest():
    """用手列量化档检验偏移、低值约束、动态范围及错误输入。"""
    levels = (0, 16, 32, 48, 64, 80, 96, 112, 136, 152, 168, 184, 200, 216, 232, 248)
    good = bytes(v for b in levels * 80 for v in (b, 100, 24))
    assert all(analyze([("positive", good)])["checks"].values())
    old = bytes(v for b in tuple(range(0, 128, 8)) * 80 for v in (b, 100, 24))
    assert not analyze([("old", old)])["checks"]["blue_rebuild_alphabet"]
    assert not analyze([("swapped", bytes(v for i in range(1280) for v in (24, 100, levels[i % 16])))])["checks"]["maxB_over127"]
    assert not analyze([])["checks"]["nonempty_rows"]
    try:
        analyze([("bad_length", b"\x00" * 100)])
    except ValueError:
        pass
    else:
        raise AssertionError("未拒绝长度错误")
    # 同一数值的十六进制补零不能伪装成帧变化。
    assert len({(int(value, 16), int(value, 16)) for value in ("1", "01", "001", "0001", "00001")}) == 1
    print("DISPLAY_CAPTURE_SELFTEST=PASS cases=6")


def main():
    """只读取当前明确给出的构建与新证据目录，拒绝覆盖既有分析结果。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--elf", type=Path)
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    if not all((args.evidence, args.run_dir, args.elf)):
        parser.error("需要 evidence、run-dir、elf")
    evidence = args.evidence.resolve(strict=True)
    run = args.run_dir.resolve(strict=True)
    output = evidence / "board_analysis.json"
    if output.exists():
        parser.error("分析结果已存在，拒绝覆盖")
    root = Path("D:/codex-worktrees/dbdf").resolve(strict=True)
    if not evidence.is_relative_to(root) or not run.is_relative_to(root):
        parser.error("运行与证据必须位于阶段三工作树")
    bit = run / "project/ov5640_single.runs/impl_1/design_1_wrapper.bit"
    xsa = run / "design_1_wrapper.xsa"
    logs = {name: evidence / f"{name}.txt" for name in ("download", "uart", "dump")}
    paths = [bit, xsa, args.elf, *logs.values()]
    row_paths = [evidence / "rows" / f"row_y{y}.bin" for y in (100, 400, 600)]
    for path in paths + row_paths:
        if not path.is_file():
            parser.error(f"缺失输入：{path}")
    uart = logs["uart"].read_text(encoding="utf-8", errors="replace")
    download = logs["download"].read_text(encoding="utf-8", errors="replace")
    dump = logs["dump"].read_text(encoding="utf-8", errors="replace")
    fps = re.findall(r"S3_DIAG6_FP t=(\d+) site=(\d+) sum=0x([0-9A-Fa-f]+) hash=0x([0-9A-Fa-f]+)", uart)
    fp_checks = {str(site): {int(t): (int(s, 16), int(h, 16)) for t, sid, s, h in fps if int(sid) == site} for site in range(3)}
    dump_events = re.findall(r"^CHANNEL_DUMP_(HALT_OK|ROW_OK|RESUME_OK|EXIT)=([^\r\n]*)", dump, re.M)
    expected_types = ["HALT_OK", "ROW_OK", "ROW_OK", "ROW_OK", "RESUME_OK", "EXIT"]
    ordered_dump = [kind for kind, _ in dump_events] == expected_types
    if ordered_dump:
        ordered_dump = dump_events[0][1] == "1" and dump_events[-2][1] == "1" and dump_events[-1][1] == "0"
        for (_, value), y, path in zip(dump_events[1:4], (100, 400, 600), row_paths):
            row, separator, target = value.partition(":")
            ordered_dump &= row == str(y) and bool(separator) and Path(target).resolve() == path.resolve()
    result = analyze([(path.name, path.read_bytes()) for path in row_paths])
    result["checks"].update({
        "download_success": "T03_DL_ALL_DONE=1" in download and "T03_DL_FAIL=" not in download,
        "bit_hash_in_download": sha256(bit) in download,
        "xsa_hash_in_download": sha256(xsa) in download,
        "elf_hash_in_download": sha256(args.elf) in download,
        "sensor_chipid": "S3_DIAG_SENSOR_ID=0x5640" in uart,
        "display_started": "S3_DIAG_DISPLAY_START status=0" in uart,
        "vdma_started": "S3_DIAG_VDMA_WRITE_STARTED" in uart,
        "live_fingerprints": len(fps) == 15 and all(set(values) == {5, 10, 15, 20, 25} and len(set(values.values())) == 5 for values in fp_checks.values()),
        "dump_safe_complete": ordered_dump and not re.search(r"^CHANNEL_DUMP_.*FAIL=", dump, re.M),
    })
    result.update({"time_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
                   "command": [sys.executable, *sys.argv], "fingerprints": fp_checks,
                   "files": [{"path": str(path), "sha256": sha256(path)} for path in paths + row_paths],
                   "machine_status": "PASS" if all(result["checks"].values()) else "FAIL",
                   "visual_status": "PENDING_WONG", "phase_status": "NOT_ACCEPTED",
                   "limitations": ["近似位重建不恢复真实色彩；绿色缺位仍未解决。", "DDR 读取前已暂停 A9，但单次行转储不替代应用侧 cache 正确的实时性诊断。", "本检查不代表目视、长时间运行或完整 I/O 时序签核。"]})
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"machine_status": result["machine_status"], "maxB": result["maxB"], "checks": result["checks"], "visual_status": result["visual_status"]}))
    return 0 if result["machine_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
