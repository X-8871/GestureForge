#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3-T05-PL4 PL 端中性灰度（绿通道算亮度）补丁生成器（可复现）

只改厂商 IP RTL `my_ip/ov5640_ip/src/alinx_ov5640.v`，在送入输出 xpm_fifo_async 的 `.din` 前
构造新的 16 位字：

  G'      = { tdata[10], tdata[9], tdata[8], maj3(tdata[8]), tdata[6], tdata[5] }   # 6 位绿
            （G'[2] 用 G[3]=tdata[8] 重建，并做水平 3 抽头多数压散斑：2 个像素率延迟寄存器 + 1 个多数门）
  新字    = { G'[5:1], G'[5:0], G'[5:1] }    # R'=B'=G'[5:1]、G'=G' ⇒ 三通道同亮度（差 ≤1 LSB）
            = { t10,t9,t8,maj,t6,   t10,t9,t8,maj,t6,t5,   t10,t9,t8,maj,t6 }

**灰度补偿，非修复**：蓝通道被完全弃用；真实修复仍需硬件返修模块侧 DVP 字节 MSB 线。
不动 tlast/tuser/tkeep/tvalid/tready/时钟；不开 DEBUG_OV5640；不叠加 dual/blue 位补丁。

用法：
    python make_gray_luma_patch.py <vendor_v> <out_patch> <scratch_dir> <sof_patched_v>
"""

import difflib
import hashlib
import os
import re
import sys

MODULE_REL = "my_ip/ov5640_ip/src/alinx_ov5640.v"

# 插入锚点：FIFO 前的 wire 声明处（SOF 补丁不触及该区域）
ANCHOR_OLD = b"wire empty;\r\nwire full;\r\n"
GRAY_BLOCK = b"""\
// ---------------------------------------------------------------------------
// S3-T05-PL4 PL-side neutral greyscale (luma taken from the GREEN channel).
// *** GREYSCALE COMPENSATION ONLY -- NOT A REPAIR. ***  The blue channel is
// deliberately discarded entirely (it is the channel whose MSB is dead); the real
// fault -- the module-side dead DVP byte-MSB line cmos_d[9] -- still requires
// hardware repair, and this bitstream must NOT be used for colour acceptance.
// Word layout: word[15:11] = B[4:0],  word[10:5] = G[5:0],  word[4:0] = R[4:0]
//   G'    = { tdata[10], tdata[9], tdata[8], maj3(tdata[8]), tdata[6], tdata[5] }
//           (G'[2] rebuilt from G[3] = tdata[8] and smoothed by a horizontal 3-tap
//            majority vote; only 2 pixel-rate delay registers + 1 majority gate,
//            no line buffer / no BRAM)
//   new   = { G'[5:1], G'[5:0], G'[5:1] }   ->  R = B = G'[5:1],  G = G'
//           (all three channels carry the same luminance, differing by <= 1 LSB)
// tlast / tuser / tkeep / tvalid / tready and all clocks/timing are untouched.
// ---------------------------------------------------------------------------
wire        gray_g2_cand = s_axis_tdata[8];   // G[3]
reg         gray_g2_d1;
reg         gray_g2_d2;
always@(posedge cmos_pclk)
begin
    if(cmos_aresetn == 1'b0)
    begin
        gray_g2_d1 <= 1'b0;
        gray_g2_d2 <= 1'b0;
    end
    else
    begin
        gray_g2_d1 <= gray_g2_cand;
        gray_g2_d2 <= gray_g2_d1;
    end
end
// Majority of (n, n-1, n-2) -- affects ONLY the rebuilt G'[2] bit.
wire gray_g2_maj = (gray_g2_cand & gray_g2_d1) | (gray_g2_cand & gray_g2_d2) | (gray_g2_d1 & gray_g2_d2);
wire[5:0]   gray_g = {s_axis_tdata[10], s_axis_tdata[9], s_axis_tdata[8], gray_g2_maj, s_axis_tdata[6], s_axis_tdata[5]};
wire[15:0]  s_axis_tdata_gray = {gray_g[5:1], gray_g[5:0], gray_g[5:1]};
wire empty;\r\nwire full;\r\n"""

DIN_OLD = b"      .din              ({s_axis_tdata,s_axis_tlast,s_axis_tuser}),\r\n"
DIN_NEW = b"      .din              ({s_axis_tdata_gray,s_axis_tlast,s_axis_tuser}),\r\n"

EDITS = [("gray_block", ANCHOR_OLD, GRAY_BLOCK),
         ("fifo_din", DIN_OLD, DIN_NEW)]

# 期望的位映射：新字每一位的来源（word[i] -> 来源说明）
EXPECTED_BITS = {
    15: "G'[5]=tdata[10]", 14: "G'[4]=tdata[9]", 13: "G'[3]=tdata[8]",
    12: "G'[2]=maj3(tdata[8])", 11: "G'[1]=tdata[6]",
    10: "G'[5]=tdata[10]", 9: "G'[4]=tdata[9]", 8: "G'[3]=tdata[8]",
    7: "G'[2]=maj3(tdata[8])", 6: "G'[1]=tdata[6]", 5: "G'[0]=tdata[5]",
    4: "G'[5]=tdata[10]", 3: "G'[4]=tdata[9]", 2: "G'[3]=tdata[8]",
    1: "G'[2]=maj3(tdata[8])", 0: "G'[1]=tdata[6]",
}


def sha256_bytes(d):
    return hashlib.sha256(d).hexdigest()


def apply_edits(text, label):
    for name, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit("FAIL=%s/%s anchor found %d times (expected 1)" % (label, name, n))
        text = text.replace(old, new, 1)
    return text


def verify_roundtrip(diff, old_lines, new_lines):
    rebuilt, old_idx = [], 0
    for ln in diff:
        if ln.startswith("---") or ln.startswith("+++"):
            continue
        if ln.startswith("@@"):
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", ln)
            if not m:
                raise SystemExit("FAIL=cannot parse hunk header: %r" % ln)
            start = int(m.group(1)) - 1
            while old_idx < start:
                rebuilt.append(old_lines[old_idx]); old_idx += 1
            continue
        if ln.startswith(" "):
            rebuilt.append(ln[1:]); old_idx += 1
        elif ln.startswith("-"):
            old_idx += 1
        elif ln.startswith("+"):
            rebuilt.append(ln[1:])
    while old_idx < len(old_lines):
        rebuilt.append(old_lines[old_idx]); old_idx += 1
    if rebuilt != new_lines:
        for i in range(max(len(rebuilt), len(new_lines))):
            a = rebuilt[i] if i < len(rebuilt) else "<missing>"
            b = new_lines[i] if i < len(new_lines) else "<missing>"
            if a != b:
                print("MISMATCH_AT=%d rebuilt=%r expected=%r" % (i, a, b))
                break
        raise SystemExit("FAIL=in-process round trip mismatch")


def main():
    if len(sys.argv) != 5:
        raise SystemExit("usage: make_gray_luma_patch.py <vendor_v> <out_patch> <scratch> <sof_patched_v>")
    vendor_v, out_patch, scratch, sof_patched_v = sys.argv[1:5]

    pristine = open(vendor_v, "rb").read()
    sof_patched = open(sof_patched_v, "rb").read()
    print("PRISTINE_BYTES=%d SHA256=%s" % (len(pristine), sha256_bytes(pristine)))
    print("SOF_PATCHED_BYTES=%d SHA256=%s" % (len(sof_patched), sha256_bytes(sof_patched)))
    if pristine.count(b"\r\n") != pristine.count(b"\n") or not pristine.endswith(b"\r\n"):
        raise SystemExit("FAIL=expected a pure CRLF file ending with CRLF")
    for tag, blob in (("pristine", pristine), ("sof_patched", sof_patched)):
        if any(b > 127 for b in blob):
            raise SystemExit("FAIL=%s is not pure ASCII" % tag)
        for forbidden in (b"s_axis_tdata_gray", b"s_axis_tdata_dualmsb", b"s_axis_tdata_bluefix"):
            if forbidden in blob:
                raise SystemExit("FAIL=%s already contains %s" % (tag, forbidden.decode()))

    gray_only = apply_edits(pristine, "pristine")
    combined = apply_edits(sof_patched, "sof_patched")

    for tag, blob in (("gray_only", gray_only), ("combined", combined)):
        if blob.count(b"gray_g2_maj") != 2:
            raise SystemExit("FAIL=%s majority wire count unexpected (%d, want decl+1 use)"
                             % (tag, blob.count(b"gray_g2_maj")))
        if blob.count(b"s_axis_tdata_gray") != 2:
            raise SystemExit("FAIL=%s s_axis_tdata_gray count unexpected (want decl+din=2)" % tag)
        if blob.count(b"wire[5:0]   gray_g") != 1:
            raise SystemExit("FAIL=%s gray_g wire missing" % tag)
        for forbidden in (b"s_axis_tdata_dualmsb", b"s_axis_tdata_bluefix"):
            if forbidden in blob:
                raise SystemExit("FAIL=%s still contains %s" % (tag, forbidden.decode()))
        if any(b > 127 for b in blob):
            raise SystemExit("FAIL=%s is not pure ASCII" % tag)
    if b"GAP_THRESH" not in combined:
        raise SystemExit("FAIL=SOF fix content missing in combined result")

    old_lines = pristine.decode("ascii").split("\n")
    new_lines = gray_only.decode("ascii").split("\n")
    diff = list(difflib.unified_diff(old_lines, new_lines,
                                     fromfile="a/" + MODULE_REL, tofile="b/" + MODULE_REL, lineterm=""))
    patch_text = "diff --git a/%s b/%s\n%s\n" % (MODULE_REL, MODULE_REL, "\n".join(diff))
    patch_bytes = patch_text.encode("ascii")

    os.makedirs(scratch, exist_ok=True)
    for name, data in (("pristine", pristine), ("gray_only", gray_only),
                       ("combined_sof_then_gray", combined)):
        p = os.path.join(scratch, name + ".v")
        open(p, "wb").write(data)
        print("%s=%s BYTES=%d SHA256=%s" % (name.upper(), p, len(data), sha256_bytes(data)))
    open(out_patch, "wb").write(patch_bytes)
    print("PATCH=%s BYTES=%d SHA256=%s" % (out_patch, len(patch_bytes), sha256_bytes(patch_bytes)))

    hunks = sum(1 for ln in diff if ln.startswith("@@"))
    added = sum(1 for ln in diff if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff if ln.startswith("-") and not ln.startswith("---"))
    print("PATCH_HUNKS=%d LINES_ADDED=%d LINES_REMOVED=%d" % (hunks, added, removed))

    verify_roundtrip(diff, old_lines, new_lines)
    print("INPROCESS_ROUNDTRIP=OK")
    print("BIT_TABLE=" + "; ".join("word[%d]=%s" % (k, EXPECTED_BITS[k]) for k in sorted(EXPECTED_BITS, reverse=True)))


if __name__ == "__main__":
    main()