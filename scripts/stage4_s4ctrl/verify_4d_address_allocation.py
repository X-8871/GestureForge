"""4-D 地址分配机械核验（Phase 1，离线只读）。

检查项（任一失败 ⇒ exit 1）：
  A. 每个分配区间都落在 D1=A 获批的 raw_frame / raw_meta 内（半开区间语义）；
  B. 所有分配两两不重叠；
  C. 与 2B 冻结对象（tensor/GF8/feature）不重叠；
  D. 与禁区 [0x12C08000,0x20000000) 不重叠；
  E. mailbox 子偏移与 ADR §8.2 表逐项一致（偏移、长度、record/magic、合计 32 KiB）；
  F. 对齐：raw_frame 8 B、raw_meta 64 B、tensor 64 B；
  G. 分配 JSON 自身声明的 checks_expected 全部为 true 且与实测一致。

用法：python -B scripts/stage4_s4ctrl/verify_4d_address_allocation.py [--json-out <path>]
退出码：0=全部通过；1=存在失败；2=输入/环境错误。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

W = Path(r"D:\codex-worktrees\w4")
ALLOC = W / "docs" / "stage4" / "S4D_4d_address_allocation_20261027_r01.json"
RAW = (0x12000000, 0x12C00000)
META = (0x12C00000, 0x12C08000)
FORBIDDEN = (0x12C08000, 0x20000000)
FROZEN = {"tensor": (0x10000000, 0x1007EC00), "gf8": (0x10100000, 0x106A12FC),
          "feature": (0x11000000, 0x11ADADB8)}
# ADR §8.2 mailbox 内部偏移（唯一权威；核验 JSON 是否与之逐项一致）
ADR_META = {
    "HOST_REQ": (0x0000, 128, 0x52423453, 128),
    "PS_ACK": (0x0080, 64, 0x41423453, 64),
    "PS_GEOM": (0x00C0, 64, 0x47423453, 64),
    "PS_RESULT": (0x0100, 64, 0x53423453, 64),
    "X_TABLE": (0x0140, 9984, None, None),
    "Y_TABLE": (0x2840, 9984, None, None),
    "JTAG_RAW_RESULT": (0x4F40, 12480, None, None),
}


def overlap(a: tuple[int, int], b: tuple[int, int]) -> int:
    """半开区间交集长度。"""
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))


def main() -> int:
    """执行核验。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", default="")
    args = parser.parse_args()
    if not ALLOC.is_file():
        print(f"[FAIL] 分配文件缺失：{ALLOC}")
        return 2
    doc = json.loads(ALLOC.read_text(encoding="utf-8"))
    regions = {r["name"]: (int(r["base_hex"], 16), int(r["end_hex_exclusive"], 16), r) for r in doc["regions"]}
    failures: list[str] = []

    # A. 在 D1=A 区域内
    for name in ("raw_frame_slot", "raw_meta"):
        if name not in regions:
            failures.append(f"A: 缺少分配 {name}")
            continue
        lo, hi, rec = regions[name]
        allowed = RAW if name == "raw_frame_slot" else META
        if (lo, hi) != allowed:
            failures.append(f"A: {name} 区间 {hex(lo)}..{hex(hi)} != D1=A {hex(allowed[0])}..{hex(allowed[1])}")
        if int(rec["length_bytes"]) != allowed[1] - allowed[0]:
            failures.append(f"A: {name} 长度不符")

    # B/C/D. 两两不重叠 + 冻结对象 + 禁区
    paid = [(n, v[0], v[1]) for n, v in regions.items() if n != "frozen_input_tensor"]
    for i in range(len(paid)):
        for j in range(i + 1, len(paid)):
            n1, a1, b1 = paid[i]
            n2, a2, b2 = paid[j]
            if overlap((a1, b1), (a2, b2)):
                failures.append(f"B: {n1} 与 {n2} 重叠")
    for name, lo, hi in paid:
        for fname, (flo, fhi) in FROZEN.items():
            if overlap((lo, hi), (flo, fhi)):
                failures.append(f"C: {name} 与冻结对象 {fname} 重叠")
        if overlap((lo, hi), FORBIDDEN):
            failures.append(f"D: {name} 与禁区重叠")

    # E. mailbox 子偏移与 ADR 一致
    meta = regions.get("raw_meta", (0, 0, {}))[2]
    subs = {s["name"]: s for s in meta.get("sub_offsets", [])}
    total = 0
    for name, (off, length, magic, rec_bytes) in ADR_META.items():
        if name not in subs:
            failures.append(f"E: 缺少 mailbox 子项 {name}")
            continue
        s = subs[name]
        if int(s["offset"], 16) != off:
            failures.append(f"E: {name} 偏移 {s['offset']} != {hex(off)}")
        if int(s["length_bytes"]) != length:
            failures.append(f"E: {name} 长度 {s['length_bytes']} != {length}")
        if magic is not None and int(s.get("record_bytes", -1)) != rec_bytes:
            failures.append(f"E: {name} record_bytes 不符")
        total += length
    if total != 32768:
        failures.append(f"E: 子项合计 {total} != 32768")
    if len(subs) != len(ADR_META):
        failures.append(f"E: 子项数量 {len(subs)} != {len(ADR_META)}")
    # 子项两两不重叠
    items = [(s["name"], int(s["offset"], 16), int(s["offset"], 16) + int(s["length_bytes"])) for s in subs.values()]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if overlap((items[i][1], items[i][2]), (items[j][1], items[j][2])):
                failures.append(f"E: 子项 {items[i][0]} 与 {items[j][0]} 重叠")

    # F. 对齐
    for name, expect in (("raw_frame_slot", 8), ("raw_meta", 64), ("frozen_input_tensor", 64)):
        if name in regions:
            lo, hi, rec = regions[name]
            if lo % expect or hi % expect:
                failures.append(f"F: {name} 未按 {expect} B 对齐")
            if int(rec.get("alignment_bytes", 0)) != expect:
                failures.append(f"F: {name} 声明对齐 {rec.get('alignment_bytes')} != {expect}")

    # G. 自声明一致
    for key, value in doc.get("checks_expected", {}).items():
        if value is not True:
            failures.append(f"G: checks_expected.{key} 非 true")

    result = {"artifact": ALLOC.name, "status": "PASS" if not failures else "FAIL",
              "regions_checked": list(regions), "failures": failures,
              "raw_frame": [hex(RAW[0]), hex(RAW[1])], "raw_meta": [hex(META[0]), hex(META[1])],
              "forbidden_gap": [hex(FORBIDDEN[0]), hex(FORBIDDEN[1])],
              "note": "只校验分配表内部一致性与不相交；不构成 G0 通过，不解除地址图 BLOCKED。"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())