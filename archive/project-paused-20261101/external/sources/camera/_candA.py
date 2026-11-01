# -*- coding: utf-8 -*-
"""候选 A：tuser 必须与 tvalid&tready 同拍（SOF 只在真被接收时消费 pending）。"""
import io

p = r"D:\tmp\lead\p3r_camera_20261031_r01\rtl\tuser_shaper.v"
t = io.open(p, encoding="utf-8").read()

old1 = "    assign tuser = (TUSER_MODE != 0) ? (sof_pending & tvalid) : sof_pulse;"
assert old1 in t, "tuser 锚点"
new1 = (
    "    // 候选A(build11p2): SOF 必须真正被接收 —— 首拍 tready=0 时不清 pending\n"
    "    assign tuser = (TUSER_MODE != 0) ? (sof_pending & tvalid & tready) : sof_pulse;"
)
t = t.replace(old1, new1, 1)

old2 = "        end else if (sof_pending && tvalid) begin\n            sof_pending <= 1'b0;\n        end"
assert old2 in t, "清除条件锚点"
new2 = "        end else if (sof_pending && tvalid && tready) begin   // 与 tuser 同拍清除\n            sof_pending <= 1'b0;\n        end"
t = t.replace(old2, new2, 1)

old3 = "            if (tuser && !tvalid) c0_misalign_cnt <= c0_misalign_cnt + 32'd1;"
assert old3 in t, "错拍计数锚点"
new3 = "            if (tuser && (!tvalid || !tready)) c0_misalign_cnt <= c0_misalign_cnt + 32'd1;   // tuser 必须与 tvalid&tready 同拍"
t = t.replace(old3, new3, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("tuser_shaper.v -> 候选A (tuser = pending & tvalid & tready)")