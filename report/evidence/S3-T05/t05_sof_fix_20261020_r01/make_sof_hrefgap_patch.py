#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3-T05 SOF 修复补丁生成器（可复现）

把厂商 IP RTL `my_ip/ov5640_ip/src/alinx_ov5640.v` 的帧起始（s_axis_tuser）触发条件
从「cmos_vsync 下降沿」改为「hblank 连续低电平 >= GAP_THRESH 个 pclk 后的第一个有效像素」，
输出可直接 `git apply -p1` / `patch -p1` 的 unified diff。

用法：
    python make_sof_hrefgap_patch.py <vendor_v_path> <out_patch_path> <scratch_dir>

RTL 注释保持纯 ASCII（避免把编码问题带进综合流程）；中文说明留在本报告与任务回传里。

时序依据（厂商驱动 Vitis/auto_create_vitis/src/an5642_single/ov5640.c 的 1280x720 模式）：
    0x3035=0x21, 0x3036=0x69  -> PCLK = 84 MHz
    0x380c/0x380d = 0x0764     -> HTS = 1892
    0x380e/0x380f = 0x02e4     -> VTS = 740
    0x3808/0x3809 = 0x0500     -> 有效宽 1280
    0x380a/0x380b = 0x02d0     -> 有效高 720
  行消隐间隙 = HTS - 1280 = 612 pclk
  场消隐间隙 ≈ (VTS - 720) * HTS + 612 = 20*1892 + 612 = 38452 pclk
  => GAP_THRESH 必须 > 612 且 < 38452；默认 16384（行间隙的 26.8 倍，场间隙的 42.6%）。
"""

import difflib
import hashlib
import os
import re
import sys

MODULE_REL = "my_ip/ov5640_ip/src/alinx_ov5640.v"

PARAM_OLD = b"   parameter DEBUG_OV5640 = 1\r\n)"
PARAM_NEW = (
    b"   parameter DEBUG_OV5640 = 1,\r\n"
    b"   // S3-T05 SOF fix: the first valid pixel after hblank (active window; cmos_8_16bit\r\n"
    b"   // drives hblank <= de_i) has stayed low for >= GAP_THRESH pclk is the frame start.\r\n"
    b"   // PCLK=84MHz, HTS=1892, VTS=740, 720 active lines -> line gap 612 pclk,\r\n"
    b"   // field gap ~38452 pclk, so the threshold must sit strictly between them.\r\n"
    b"   parameter GAP_THRESH = 16'd16384\r\n)"
)

DECL_OLD = b"reg           s_axis_tuser;\r\n"
DECL_NEW = (
    b"reg           s_axis_tuser;\r\n"
    b"reg[15:0]     cmos_hblank_low_cnt; // S3-T05 SOF fix: hblank low run length (saturating)\r\n"
)

BLOCK_OLD = (
    b"always@(posedge cmos_pclk)\r\n"
    b"begin\r\n"
    b"    if(cmos_aresetn == 1'b0)\r\n"
    b"        s_axis_tuser <= 1'b0;\r\n"
    b"\telse if(cmos_vsync_d1 == 1'b1 && cmos_vsync_d0 == 1'b0)\r\n"
    b"\t\ts_axis_tuser <= 1'b1;\r\n"
    b"\telse if(s_axis_tuser == 1'b1 && s_axis_tvalid == 1'b1)\r\n"
    b"\t\ts_axis_tuser <= 1'b0;\r\n"
    b"end\r\n"
)

BLOCK_NEW = (
    b"// S3-T05 SOF fix: frame start no longer comes from the cmos_vsync falling edge (that\r\n"
    b"// vsync never reaches this IP); it is the first valid pixel after hblank stayed low for\r\n"
    b"// >= GAP_THRESH pclk, i.e. the first valid pixel of the first active line of a frame.\r\n"
    b"always@(posedge cmos_pclk)\r\n"
    b"begin\r\n"
    b"    if(cmos_aresetn == 1'b0)\r\n"
    b"        cmos_hblank_low_cnt <= 16'd0;\r\n"
    b"    else if(cmos_hblank == 1'b1)\r\n"
    b"        cmos_hblank_low_cnt <= 16'd0;\r\n"
    b"    else if(cmos_hblank_low_cnt < 16'hFFFF)\r\n"
    b"        cmos_hblank_low_cnt <= cmos_hblank_low_cnt + 16'd1;\r\n"
    b"end\r\n"
    b"\r\n"
    b"always@(posedge cmos_pclk)\r\n"
    b"begin\r\n"
    b"    if(cmos_aresetn == 1'b0)\r\n"
    b"        s_axis_tuser <= 1'b0;\r\n"
    b"    else if(cmos_hblank_d0 == 1'b0 && cmos_hblank == 1'b1 && cmos_hblank_low_cnt >= GAP_THRESH)\r\n"
    b"        s_axis_tuser <= 1'b1;\r\n"
    b"    else if(s_axis_tuser == 1'b1 && s_axis_tvalid == 1'b1)\r\n"
    b"        s_axis_tuser <= 1'b0;\r\n"
    b"end\r\n"
)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def must_replace(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit("FAIL=%s anchor found %d times (expected 1)" % (label, n))
    return text.replace(old, new, 1)


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: make_sof_hrefgap_patch.py <vendor_v> <out_patch> <scratch_dir>")
    vendor_v, out_patch, scratch = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(vendor_v, "rb") as fh:
        pristine = fh.read()

    print("PRISTINE_BYTES=%d SHA256=%s" % (len(pristine), sha256_bytes(pristine)))
    if pristine.count(b"\r\n") != pristine.count(b"\n") or pristine.count(b"\n") == 0:
        raise SystemExit("FAIL=expected a pure CRLF file")
    if not pristine.endswith(b"\r\n"):
        raise SystemExit("FAIL=file does not end with CRLF")
    if b"GAP_THRESH" in pristine:
        raise SystemExit("FAIL=original already contains GAP_THRESH (already patched)")
    if any(b > 127 for b in pristine):
        raise SystemExit("FAIL=original file is not pure ASCII")

    expected = must_replace(pristine, PARAM_OLD, PARAM_NEW, "param")
    expected = must_replace(expected, DECL_OLD, DECL_NEW, "decl")
    expected = must_replace(expected, BLOCK_OLD, BLOCK_NEW, "tuser_block")
    if b"cmos_vsync_d1 == 1'b1" in expected:
        raise SystemExit("FAIL=old vsync falling-edge trigger still present")
    if b"GAP_THRESH = 16'd16384" not in expected:
        raise SystemExit("FAIL=GAP_THRESH parameter missing")
    if b"cmos_hblank_low_cnt" not in expected:
        raise SystemExit("FAIL=hblank low counter missing")
    if not expected.rstrip(b"\r\n").endswith(b"endmodule"):
        raise SystemExit("FAIL=patched file does not end with endmodule")
    if any(b > 127 for b in expected):
        raise SystemExit("FAIL=patched file is not pure ASCII")

    # git 风格 unified diff：内容行保留 CR（与文件一致），结构行只含 LF
    old_lines = pristine.decode("ascii").split("\n")
    new_lines = expected.decode("ascii").split("\n")
    diff = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile="a/" + MODULE_REL, tofile="b/" + MODULE_REL, lineterm=""))
    patch_text = "diff --git a/%s b/%s\n%s\n" % (MODULE_REL, MODULE_REL, "\n".join(diff))
    patch_bytes = patch_text.encode("ascii")

    os.makedirs(scratch, exist_ok=True)
    for name, data in (("pristine", pristine), ("expected", expected)):
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

    # 进程内自检：按 hunk 头声明的行号把补丁应用到 pristine 行，必须得到 expected 行
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
        print("LEN rebuilt=%d expected=%d" % (len(rebuilt), len(new_lines)))
        raise SystemExit("FAIL=in-process patch round trip mismatch")
    print("INPROCESS_ROUNDTRIP=OK")


if __name__ == "__main__":
    main()