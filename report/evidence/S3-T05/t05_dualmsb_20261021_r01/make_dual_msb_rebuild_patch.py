#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3-T05-PL3 双位重建 + 水平 3 抽头多数 补丁生成器（可复现）

只改厂商 IP RTL `my_ip/ov5640_ip/src/alinx_ov5640.v`：

  1) 送入输出 xpm_fifo_async 的 16 位字按**显式位表**重建（字布局 = {B[4:0],G[5:0],R[4:0]}）：
       B'[4:0] = {tdata[14], tdata[14], tdata[13], tdata[12], tdata[11]}   # B'[4] = B[3]
       G'[5:0] = {tdata[10], tdata[9], tdata[8], tdata[8], tdata[6], tdata[5]}  # G'[2] = G[3]
       R'[4:0] = {tdata[4], tdata[3], tdata[2], tdata[1], tdata[0]}        # R 不变
     即 B'[4]=B[3]、G'[2]=G[3]，其余位原样。
  2) 对**这两个被重建的位**（B'[4]、G'[2]）做水平 3 抽头多数表决（当前 + 前 2 个像素，
     仅用像素率延迟寄存器，无行缓冲/BRAM），压掉散斑。

不动 tlast/tuser/tkeep/tvalid/tready 与时序；不开 DEBUG_OV5640。

用法：
    python make_dual_msb_rebuild_patch.py <vendor_v> <out_patch> <scratch_dir> <sof_patched_v>
"""

import difflib
import hashlib
import os
import re
import sys

MODULE_REL = "my_ip/ov5640_ip/src/alinx_ov5640.v"

# 插入锚点：在 FIFO 前的 wire 声明处（该区域不被 SOF 补丁触及：SOF 改参数表、tuser always 块）
ANCHOR_OLD = b"wire empty;\r\nwire full;\r\n"
ANCHOR_NEW_PREFIX = b"""\
// ---------------------------------------------------------------------------
// S3-T05-PL3 dual-MSB approximate compensation.
// *** APPROXIMATE COMPENSATION ONLY -- NOT A TRUE REPAIR -- MUST NOT BE USED FOR
// *** COLOUR ACCEPTANCE.  The real fault (module-side dead DVP byte-MSB line
// *** cmos_d[9]) is not fixed here; this block only approximates the two lost bits.
// Word layout (confirmed by netlist analysis + row-sample signatures):
//   word[15:11] = B[4:0],  word[10:5] = G[5:0],  word[4:0] = R[4:0]
// Lost bits: word[15] = B[4] (first-byte MSB) and word[7] = G[2] (second-byte MSB);
// both come from the same dead DVP line cmos_d[9] (so both are stuck at 0).
// Rebuild table (explicit, bit by bit):
//   B'[4] = B[3] = tdata[14]        G'[2] = G[3] = tdata[8]        all other bits unchanged
// Then a horizontal 3-tap majority vote is applied to THOSE TWO BITS ONLY to suppress
// speckle. It uses pixel-rate delay registers only (no line buffer / no BRAM) and the
// window is causal (current pixel + previous 2 pixels); the data stream itself is NOT
// delayed, so tvalid/tlast/tuser stay aligned with the word.
// ---------------------------------------------------------------------------
wire        dualmsb_b4_cand = s_axis_tdata[14];  // B[3]
wire        dualmsb_g2_cand = s_axis_tdata[8];   // G[3]
reg         dualmsb_b4_d1;
reg         dualmsb_b4_d2;
reg         dualmsb_g2_d1;
reg         dualmsb_g2_d2;
always@(posedge cmos_pclk)
begin
    if(cmos_aresetn == 1'b0)
    begin
        dualmsb_b4_d1 <= 1'b0;
        dualmsb_b4_d2 <= 1'b0;
        dualmsb_g2_d1 <= 1'b0;
        dualmsb_g2_d2 <= 1'b0;
    end
    else
    begin
        dualmsb_b4_d1 <= dualmsb_b4_cand;
        dualmsb_b4_d2 <= dualmsb_b4_d1;
        dualmsb_g2_d1 <= dualmsb_g2_cand;
        dualmsb_g2_d2 <= dualmsb_g2_d1;
    end
end
// Majority of (n, n-1, n-2) -- affects ONLY the two rebuilt bits.
wire dualmsb_b4_maj = (dualmsb_b4_cand & dualmsb_b4_d1) | (dualmsb_b4_cand & dualmsb_b4_d2) | (dualmsb_b4_d1 & dualmsb_b4_d2);
wire dualmsb_g2_maj = (dualmsb_g2_cand & dualmsb_g2_d1) | (dualmsb_g2_cand & dualmsb_g2_d2) | (dualmsb_g2_d1 & dualmsb_g2_d2);
wire[15:0]  s_axis_tdata_dualmsb = {
    dualmsb_b4_maj,                                                                     // [15]    B'[4] = maj3(B[3])
    s_axis_tdata[14], s_axis_tdata[13], s_axis_tdata[12], s_axis_tdata[11],             // [14:11] B[3:0]
    s_axis_tdata[10], s_axis_tdata[9], s_axis_tdata[8],                                 // [10:8]  G[5:3]
    dualmsb_g2_maj,                                                                     // [7]     G'[2] = maj3(G[3])
    s_axis_tdata[6], s_axis_tdata[5],                                                   // [6:5]   G[1:0]
    s_axis_tdata[4], s_axis_tdata[3], s_axis_tdata[2], s_axis_tdata[1], s_axis_tdata[0] // [4:0]   R[4:0]
};
wire empty;\r\nwire full;\r\n"""

DIN_OLD = b"      .din              ({s_axis_tdata,s_axis_tlast,s_axis_tuser}),\r\n"
DIN_NEW = b"      .din              ({s_axis_tdata_dualmsb,s_axis_tlast,s_axis_tuser}),\r\n"

EDITS = [("dualmsb_block", ANCHOR_OLD, ANCHOR_NEW_PREFIX),
         ("fifo_din", DIN_OLD, DIN_NEW)]


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
        raise SystemExit("usage: make_dual_msb_rebuild_patch.py <vendor_v> <out_patch> <scratch> <sof_patched_v>")
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
    if b"s_axis_tdata_dualmsb" in pristine:
        raise SystemExit("FAIL=original already contains the dual-MSB block")
    # 旧（位序错误）的蓝位补丁标记必须不在，避免叠加
    if b"s_axis_tdata_bluefix" in pristine:
        raise SystemExit("FAIL=old bluefix patch unexpectedly present")

    dual_only = apply_edits(pristine, "pristine")
    combined = apply_edits(sof_patched, "sof_patched")

    # 位表自检：逐位核对 new[15] / new[7] 来自 maj，其余来自原字
    for tag, blob in (("dual_only", dual_only), ("combined", combined)):
        if blob.count(b"dualmsb_b4_maj") != 2 or blob.count(b"dualmsb_g2_maj") != 2:
            raise SystemExit("FAIL=%s majority wire count unexpected (want decl+1 use = 2); b4=%d g2=%d"
                             % (tag, blob.count(b"dualmsb_b4_maj"), blob.count(b"dualmsb_g2_maj")))
        if blob.count(b"s_axis_tdata_dualmsb") != 2:
            raise SystemExit("FAIL=%s s_axis_tdata_dualmsb count unexpected (want decl+din=2)" % tag)
        if b"GAP_THRESH" not in combined:
            raise SystemExit("FAIL=SOF fix content missing in combined result")
        if b"s_axis_tdata_bluefix" in blob:
            raise SystemExit("FAIL=%s contains old bluefix marker" % tag)
        if any(b > 127 for b in blob):
            raise SystemExit("FAIL=%s is not pure ASCII" % tag)

    old_lines = pristine.decode("ascii").split("\n")
    new_lines = dual_only.decode("ascii").split("\n")
    diff = list(difflib.unified_diff(old_lines, new_lines,
                                     fromfile="a/" + MODULE_REL, tofile="b/" + MODULE_REL, lineterm=""))
    patch_text = "diff --git a/%s b/%s\n%s\n" % (MODULE_REL, MODULE_REL, "\n".join(diff))
    patch_bytes = patch_text.encode("ascii")

    os.makedirs(scratch, exist_ok=True)
    for name, data in (("pristine", pristine), ("dual_only", dual_only),
                       ("combined_sof_then_dual", combined)):
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

    # 位表机器可读摘要（供报告引用）
    print("BIT_TABLE=B'[4]=B[3](tdata[14]) maj3 ; G'[2]=G[3](tdata[8]) maj3 ; "
          "new={maj_b4,t[14:11],t[10:8],maj_g2,t[6:5],t[4:0]}")


if __name__ == "__main__":
    main()