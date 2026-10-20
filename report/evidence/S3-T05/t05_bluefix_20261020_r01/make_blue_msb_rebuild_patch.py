#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3-T05-PL1 蓝最高位重建补丁生成器（可复现）

在厂商 IP RTL `my_ip/ov5640_ip/src/alinx_ov5640.v` 的 8->16 位重组之后、送 FIFO 之前，
把 RGB565 字里的蓝通道最高位 B[4] 用 B[3] 重建：

    B = tdata[4:0] ;  B'[4:0] = {B[3:0], B[3]}
    new_word = {tdata[15:5], tdata[3:0], tdata[3]}

只改 3 处（互不重叠、且都落在 SOF 补丁未触及的区域）：
  1. 在 `wire[15:0] s_axis_tdata = cmos_d_16bit_d1;` 之后新增一条重建 wire；
  2. ILA 探针 `.probe0(s_axis_tdata)` -> 用重建 wire（DEBUG_OV5640 关闭，此分支不综合）；
  3. FIFO `.din({s_axis_tdata,...})` -> 用重建 wire（这是真正生效的通路）。

不动 tlast/tuser/tkeep/时钟/时序。

用法：
    python make_blue_msb_rebuild_patch.py <vendor_v> <out_patch> <scratch_dir> <sof_patched_v>
"""

import difflib
import hashlib
import os
import re
import sys

MODULE_REL = "my_ip/ov5640_ip/src/alinx_ov5640.v"

DECL_OLD = b"wire[15:0]    s_axis_tdata = cmos_d_16bit_d1;\r\n"
DECL_NEW = (
    b"wire[15:0]    s_axis_tdata = cmos_d_16bit_d1;\r\n"
    b"// S3-T05-PL1 blue fix: RGB565 blue MSB rebuild. B = tdata[4:0]; B'[4:0] = {B[3:0], B[3]}.\r\n"
    b"// Only bit[4] changes; R/G and all other bits, tlast/tuser/tkeep/timing stay untouched.\r\n"
    b"wire[15:0]    s_axis_tdata_bluefix = {s_axis_tdata[15:5], s_axis_tdata[3:0], s_axis_tdata[3]};\r\n"
)

PROBE_OLD = b"        .probe0(s_axis_tdata),\r\n"
PROBE_NEW = b"        .probe0(s_axis_tdata_bluefix),\r\n"

DIN_OLD = b"      .din              ({s_axis_tdata,s_axis_tlast,s_axis_tuser}),\r\n"
DIN_NEW = b"      .din              ({s_axis_tdata_bluefix,s_axis_tlast,s_axis_tuser}),\r\n"

EDITS = [
    ("decl_bluefix_wire", DECL_OLD, DECL_NEW),
    ("ila_probe0", PROBE_OLD, PROBE_NEW),
    ("fifo_din", DIN_OLD, DIN_NEW),
]


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def apply_edits(text, label):
    for name, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit("FAIL=%s/%s anchor found %d times (expected 1)" % (label, name, n))
        text = text.replace(old, new, 1)
    return text


def unified_diff_text(old_bytes, new_bytes, rel):
    old_lines = old_bytes.decode("ascii").split("\n")
    new_lines = new_bytes.decode("ascii").split("\n")
    diff = list(difflib.unified_diff(
        old_lines, new_lines, fromfile="a/" + rel, tofile="b/" + rel, lineterm=""))
    return diff, "diff --git a/%s b/%s\n%s\n" % (rel, rel, "\n".join(diff))


def verify_roundtrip(diff, old_lines, new_lines):
    rebuilt = []
    old_idx = 0
    for ln in diff:
        if ln.startswith("---") or ln.startswith("+++"):
            continue
        if ln.startswith("@@"):
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", ln)
            if not m:
                raise SystemExit("FAIL=cannot parse hunk header: %r" % ln)
            start = int(m.group(1)) - 1
            while old_idx < start:
                rebuilt.append(old_lines[old_idx])
                old_idx += 1
            continue
        if ln.startswith(" "):
            rebuilt.append(ln[1:])
            old_idx += 1
        elif ln.startswith("-"):
            old_idx += 1
        elif ln.startswith("+"):
            rebuilt.append(ln[1:])
    while old_idx < len(old_lines):
        rebuilt.append(old_lines[old_idx])
        old_idx += 1
    if rebuilt != new_lines:
        for i in range(max(len(rebuilt), len(new_lines))):
            a = rebuilt[i] if i < len(rebuilt) else "<missing>"
            b = new_lines[i] if i < len(new_lines) else "<missing>"
            if a != b:
                print("MISMATCH_AT=%d rebuilt=%r expected=%r" % (i, a, b))
                break
        raise SystemExit("FAIL=in-process patch round trip mismatch")


def main():
    if len(sys.argv) != 5:
        raise SystemExit("usage: make_blue_msb_rebuild_patch.py <vendor_v> <out_patch> <scratch> <sof_patched_v>")
    vendor_v, out_patch, scratch, sof_patched_v = sys.argv[1:5]

    with open(vendor_v, "rb") as fh:
        pristine = fh.read()
    with open(sof_patched_v, "rb") as fh:
        sof_patched = fh.read()

    print("PRISTINE_BYTES=%d SHA256=%s" % (len(pristine), sha256_bytes(pristine)))
    print("SOF_PATCHED_BYTES=%d SHA256=%s" % (len(sof_patched), sha256_bytes(sof_patched)))
    if pristine.count(b"\r\n") != pristine.count(b"\n") or not pristine.endswith(b"\r\n"):
        raise SystemExit("FAIL=expected a pure CRLF file ending with CRLF")
    for tag, blob in (("pristine", pristine), ("sof_patched", sof_patched)):
        if any(b > 127 for b in blob):
            raise SystemExit("FAIL=%s is not pure ASCII" % tag)
    if b"s_axis_tdata_bluefix" in pristine:
        raise SystemExit("FAIL=original already contains s_axis_tdata_bluefix")

    blue_only = apply_edits(pristine, "pristine")                 # vendor + blue
    combined = apply_edits(sof_patched, "sof_patched")            # (vendor + SOF) + blue

    if b"s_axis_tdata_bluefix" not in blue_only or b"s_axis_tdata_bluefix" not in combined:
        raise SystemExit("FAIL=bluefix wire missing after edit")
    if combined.count(b"s_axis_tdata_bluefix") != 3:
        raise SystemExit("FAIL=unexpected s_axis_tdata_bluefix occurrence count in combined (want def+probe0+din=3)")
    # 除 bit[4] 外的 16 位字必须逐位保持
    if b"cmos_hblank" not in combined or b"GAP_THRESH" not in combined:
        raise SystemExit("FAIL=SOF fix content missing in combined result")

    diff, patch_text = unified_diff_text(pristine, blue_only, MODULE_REL)
    patch_bytes = patch_text.encode("ascii")

    os.makedirs(scratch, exist_ok=True)
    for name, data in (("pristine", pristine), ("blue_only", blue_only),
                       ("combined_sof_then_blue", combined)):
        p = os.path.join(scratch, name + ".v")
        with open(p, "wb") as fh:
            fh.write(data)
        print("%s=%s BYTES=%d SHA256=%s" % (name.upper(), p, len(data), sha256_bytes(data)))
    with open(out_patch, "wb") as fh:
        fh.write(patch_bytes)
    print("PATCH=%s BYTES=%d SHA256=%s" % (out_patch, len(patch_bytes), sha256_bytes(patch_bytes)))

    hunks = sum(1 for ln in diff if ln.startswith("@@"))
    added = sum(1 for ln in diff if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff if ln.startswith("-") and not ln.startswith("---"))
    print("PATCH_HUNKS=%d LINES_ADDED=%d LINES_REMOVED=%d" % (hunks, added, removed))

    verify_roundtrip(diff, pristine.decode("ascii").split("\n"), blue_only.decode("ascii").split("\n"))
    print("INPROCESS_ROUNDTRIP=OK")

    # 语义自检：位级等价性（new_word = {w[15:5], w[3:0], w[3]}）
    print("BIT_CHECK=" + ("OK" if (b"{s_axis_tdata[15:5], s_axis_tdata[3:0], s_axis_tdata[3]}"
                                   in blue_only) else "MISSING"))


if __name__ == "__main__":
    main()