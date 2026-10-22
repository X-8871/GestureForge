#!/usr/bin/env bash
# S3-T05-PL5 标准亮度灰度补丁「确定性生成 + 干跑校验」脚本（不构建、不下板）
# 目的：从厂商原件 + SOF 补丁的字节级结果出发，确定性生成
#   board/stage3/software/sensor/alinx_ov5640_stdluma_gray.patch
# 并给出三个 RTL 哈希（pristine / after-SOF / after-SOF+stdluma），供启动器硬编码断言。
# 只写本证据目录下的 patch_scratch/**。
set -u

WT="D:/codex-worktrees/dbdf"
EVID="$WT/report/evidence/S3-T05/t05_stdluma_20261022_r01"
SCRATCH="$EVID/patch_scratch"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
PATCH_SOF="$WT/board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
PATCH_OUT="$WT/board/stage3/software/sensor/alinx_ov5640_stdluma_gray.patch"
REL="my_ip/ov5640_ip/src/alinx_ov5640.v"
REL_SCRATCH="report/evidence/S3-T05/t05_stdluma_20261022_r01/patch_scratch"

command -v diff >/dev/null || { echo "FAIL=diff_missing"; exit 3; }
[ -f "$VENDOR/$REL" ] || { echo "FAIL=vendor_missing"; exit 3; }
[ -f "$PATCH_SOF" ] || { echo "FAIL=sof_patch_missing"; exit 3; }

rm -rf "$SCRATCH/orig" "$SCRATCH/new" "$SCRATCH/verify"
mkdir -p "$SCRATCH/orig/$(dirname $REL)" "$SCRATCH/new/$(dirname $REL)" "$SCRATCH/verify/$(dirname $REL)"
cp "$VENDOR/$REL" "$SCRATCH/orig/$REL"
cp "$VENDOR/$REL" "$SCRATCH/new/$REL"
cp "$VENDOR/$REL" "$SCRATCH/verify/$REL"

cd "$WT" || exit 3
# SOF 补丁先作用到三份副本（与启动器顺序一致）
for d in orig new verify; do
  git apply -p1 --directory="$REL_SCRATCH/$d" "$PATCH_SOF" || { echo "FAIL=sof_apply_$d"; exit 4; }
done

echo "RTL_PRISTINE_SHA256=$(sha256sum "$VENDOR/$REL" | awk '{print $1}')"
echo "RTL_AFTER_SOF_SHA256=$(sha256sum "$SCRATCH/orig/$REL" | awk '{print $1}')"

# ---- 确定性变换：插入 std-luma 块 + 改 .din -------------------------------------
export SCRATCH REL
python -B - <<'PY'
import os
base = os.environ["SCRATCH"]
rel  = os.environ["REL"]
p    = os.path.join(base, "new", *rel.split("/"))
raw  = open(p, "rb").read()
nl   = b"\r\n" if b"\r\n" in raw else b"\n"

anchor = b"endgenerate" + nl + nl + b"wire empty;"
assert raw.count(anchor) == 1, "anchor endgenerate/wire empty not unique"
din_old = b".din              ({s_axis_tdata,s_axis_tlast,s_axis_tuser}),"
assert raw.count(din_old) == 1, "din line not unique"

block = b"""// ---------------------------------------------------------------------------
// S3-T05-PL5 standard-luminance greyscale: Y = (77*R8 + 150*G8 + 29*B8) >> 8
// (integer approximation of 0.299R + 0.587G + 0.114B).
// *** GREYSCALE COMPENSATION ONLY -- NOT A TRUE REPAIR. ***  The real fault --
// the module-side dead DVP byte-MSB line cmos_d[9] -- is NOT fixed here. The
// missing blue MSB is still *guessed* (B'[4] = B'[3] = B[3]) and that guessed bit
// still feeds the luma, so this bitstream must NOT be used for colour acceptance
// and cannot replace the hardware repair.
// Word layout: word[15:11] = B[4:0], word[10:5] = G[5:0], word[4:0] = R[4:0]
//   R8  = { tdata[4:0], 3'b000 }
//   G'  = { tdata[10], tdata[9], tdata[8], maj3(tdata[8]), tdata[6], tdata[5] }
//         (dead G[2] = tdata[7] rebuilt from G[3] = tdata[8] and smoothed by a
//          horizontal 3-tap majority vote; 2 pixel-rate delay registers + 1
//          majority gate only -- no line buffer / no BRAM, stream NOT delayed)
//   G8  = { G'[5:0], 2'b00 }
//   B'  = { tdata[14], tdata[14], tdata[13], tdata[12], tdata[11] }   (B'[4]=B'[3])
//   B8  = { B'[4:0], 3'b000 }
//   Y   = (77*R8 + 150*G8 + 29*B8) >> 8
//   new = { Y[7:3], Y[7:2], Y[7:3] }  ->  R5 = B5 = Y>>3, G6 = Y>>2
// tlast / tuser / tkeep / tvalid / tready and all clocks/timing are untouched.
// ---------------------------------------------------------------------------
wire        stdluma_g2_cand = s_axis_tdata[8];   // G[3]
reg         stdluma_g2_d1;
reg         stdluma_g2_d2;
always@(posedge cmos_pclk)
begin
    if(cmos_aresetn == 1'b0)
    begin
        stdluma_g2_d1 <= 1'b0;
        stdluma_g2_d2 <= 1'b0;
    end
    else
    begin
        stdluma_g2_d1 <= stdluma_g2_cand;
        stdluma_g2_d2 <= stdluma_g2_d1;
    end
end
// Majority of (n, n-1, n-2) -- affects ONLY the rebuilt G'[2] bit.
wire        stdluma_g2_maj = (stdluma_g2_cand & stdluma_g2_d1) | (stdluma_g2_cand & stdluma_g2_d2) | (stdluma_g2_d1 & stdluma_g2_d2);
wire[7:0]   stdluma_r8 = {s_axis_tdata[4:0],3'b000};
wire[5:0]   stdluma_g6 = {s_axis_tdata[10],s_axis_tdata[9],s_axis_tdata[8],stdluma_g2_maj,s_axis_tdata[6],s_axis_tdata[5]};
wire[7:0]   stdluma_g8 = {stdluma_g6,2'b00};
wire[4:0]   stdluma_b5 = {s_axis_tdata[14],s_axis_tdata[14],s_axis_tdata[13],s_axis_tdata[12],s_axis_tdata[11]};
wire[7:0]   stdluma_b8 = {stdluma_b5,3'b000};
wire[31:0]  stdluma_luma32 = 77*stdluma_r8 + 150*stdluma_g8 + 29*stdluma_b8;
wire[7:0]   stdluma_y = stdluma_luma32[15:8];
wire[15:0]  s_axis_tdata_stdluma = {stdluma_y[7:3],stdluma_y[7:2],stdluma_y[7:3]};
""".replace(b"\n", nl)

din_new = b".din              ({s_axis_tdata_stdluma,s_axis_tlast,s_axis_tuser}),"
out = raw.replace(anchor, b"endgenerate" + nl + nl + block + b"wire empty;").replace(din_old, din_new)
assert out != raw and out.count(b"s_axis_tdata_stdluma") == 2, "transform failed"
open(p, "wb").write(out)
print("TRANSFORM=ok newline=%s bytes=%d" % ("CRLF" if nl == b"\r\n" else "LF", len(out)))
PY
[ $? -eq 0 ] || { echo "FAIL=transform"; exit 4; }

# ---- 生成 unified diff ----------------------------------------------------------
diff -u --label "a/$REL" --label "b/$REL" "$SCRATCH/orig/$REL" "$SCRATCH/new/$REL" > "$SCRATCH/stdluma.body.diff"
BODY_RC=$?
[ "$BODY_RC" -le 1 ] || { echo "FAIL=diff_rc_$BODY_RC"; exit 4; }
{
  echo "diff --git a/$REL b/$REL"
  cat "$SCRATCH/stdluma.body.diff"
} > "$PATCH_OUT"
echo "PATCH_WRITTEN=$PATCH_OUT"
echo "PATCH_SHA256=$(sha256sum "$PATCH_OUT" | awk '{print $1}')"
echo "PATCH_HUNKS=$(grep -c '^@@' "$PATCH_OUT")"
echo "PATCH_LINES_ADDED=$(grep -c '^+' "$PATCH_OUT")"
echo "PATCH_LINES_REMOVED=$(grep -c '^-' "$PATCH_OUT")"

# ---- 干跑：在 verify 副本上按启动器顺序应用并逐字节比对 --------------------------
# 注意：verify 副本在上面的 for 循环里已经应用过 SOF 补丁，这里只应用 STDLUMA 补丁。
{
  echo "VERIFY_HAS_SOF_SHA256=$(sha256sum "$SCRATCH/verify/$REL" | awk '{print $1}')"
  echo "== git apply --check STDLUMA (on SOF-applied verify copy) =="
  git apply --check -p1 --directory="$REL_SCRATCH/verify" "$PATCH_OUT"; echo "STDLUMA_CHECK_RC=$?"
  git apply -p1 --directory="$REL_SCRATCH/verify" "$PATCH_OUT"; echo "STDLUMA_APPLY_RC=$?"
  echo "VERIFY_AFTER_STDLUMA_SHA256=$(sha256sum "$SCRATCH/verify/$REL" | awk '{print $1}')"
} > "$SCRATCH/patch_dryrun.log" 2>&1
cat "$SCRATCH/patch_dryrun.log"

cmp -s "$SCRATCH/verify/$REL" "$SCRATCH/new/$REL" || { echo "FAIL=dryrun_bytes_differ"; exit 4; }
echo "DRYRUN_BYTES_IDENTICAL=1"
echo "RTL_AFTER_BOTH_SHA256=$(sha256sum "$SCRATCH/new/$REL" | awk '{print $1}')"
echo "PATCH_SHA256=$(sha256sum "$PATCH_OUT" | awk '{print $1}')"

# 标记断言
F="$SCRATCH/new/$REL"
grep -q "s_axis_tdata_stdluma" "$F" && echo "MARKER_STDLUMA=1" || { echo "FAIL=marker_missing"; exit 4; }
grep -q "GAP_THRESH" "$F" && echo "MARKER_GAP_THRESH=1" || { echo "FAIL=sof_marker_missing"; exit 4; }
grep -q "stdluma_luma32" "$F" || { echo "FAIL=luma_marker_missing"; exit 4; }
for m in s_axis_tdata_dualmsb s_axis_tdata_bluefix gray_g2_maj; do
  if grep -q "$m" "$F"; then echo "FAIL=residual_marker:$m"; exit 4; fi
done
echo "RESIDUAL_MARKERS_ABSENT=1"
echo "GENERATE_DONE=1"
exit 0