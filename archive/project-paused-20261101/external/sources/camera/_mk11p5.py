# -*- coding: utf-8 -*-
"""生成 bd_p3r_b11p.tcl（v5）= build11o + **5 探针原生 ILA**（BASIC 许可上限，已实测合规）。

探针规划（全部 ≤5 probe，符合 [Chipscope 16-620] BASIC 限制）：
  probe0 = {s2mm_awready, s2mm_awvalid}                    (2b)  写地址握手
  probe1 = {s2mm_bresp[1:0], s2mm_bvalid}                  (3b)  写响应/错误码
  probe2 = {s2mm_wlast, s2mm_wready, s2mm_wvalid}          (3b)  写数据握手
  probe3 = {s2mm_tuser, s2mm_tlast, s2mm_tready, s2mm_tvalid} (4b) AXIS 侧
  probe4 = s2mm_awaddr[31:0]                               (32b) 写地址
采样时钟 FCLK1(100MHz)，深度 8192。
"""
import io

BASE = r"D:\tmp\lead\p3r_camera_20261031_r01"
s = io.open(BASE + r"\bd_p3r_b11o.tcl", encoding="utf-8").read()
s = s.replace('set out  "D:/tmp/lead/p3r_camera_20261031_r01/out/build11o"',
              'set out  "D:/tmp/lead/p3r_camera_20261031_r01/out/build11p"')

anchor = "assign_bd_address -offset 0x43DB0000 -range 0x00001000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins gpio_mes_e/S_AXI]]"
assert anchor in s, "0x43DB0000 地址锚点"

ila = anchor + r'''

# ============================================================================
# build11p（v5）：5 探针原生 ILA —— BASIC 许可上限（[Chipscope 16-620] 只允许 <=5 probe）
#   已实测：AXI 子信号可作为 BD 引脚访问（axi_vdma_1/m_axi_s2mm_awvalid 等，
#           注意是**小写** s2mm_ 前缀；接口本身仍保留在 S01_AXI 网上，不打断接口）
#   探针：
#     probe0 = {awready, awvalid}                      (2b)
#     probe1 = {bresp[1:0], bvalid}                    (3b)   ← bresp 是否非 0 = HP2 是否拒绝写
#     probe2 = {wlast, wready, wvalid}                 (3b)
#     probe3 = {tuser, tlast, tready, tvalid}          (4b)   ← AXIS 帧边界
#     probe4 = awaddr[31:0]                            (32b)
#   时钟 FCLK1(100 MHz)，深度 8192
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:ila:6.2 ila_cam
set_property -dict [list \
    CONFIG.C_NUM_OF_PROBES {5} \
    CONFIG.C_DATA_DEPTH {8192} \
    CONFIG.C_TRIGIN_EN {false} \
    CONFIG.C_EN_STRG_QUAL {false} \
    CONFIG.C_INPUT_PIPE_STAGES {0} \
    CONFIG.C_ADV_TRIGGER {false} \
] [get_bd_cells ila_cam]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK1] [get_bd_pins ila_cam/clk]

# --- probe0 = {awready, awvalid} ---
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 cc_aw
set_property -dict [list CONFIG.NUM_PORTS {2}] [get_bd_cells cc_aw]
connect_bd_net [get_bd_pins axi_vdma_1/m_axi_s2mm_awready] [get_bd_pins cc_aw/In0]
connect_bd_net [get_bd_pins axi_vdma_1/m_axi_s2mm_awvalid] [get_bd_pins cc_aw/In1]
connect_bd_net [get_bd_pins cc_aw/dout] [get_bd_pins ila_cam/probe0]

# --- probe1 = {bresp[1:0], bvalid} ---
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 cc_b
set_property -dict [list CONFIG.NUM_PORTS {2}] [get_bd_cells cc_b]
connect_bd_net [get_bd_pins axi_vdma_1/m_axi_s2mm_bresp]  [get_bd_pins cc_b/In0]
connect_bd_net [get_bd_pins axi_vdma_1/m_axi_s2mm_bvalid] [get_bd_pins cc_b/In1]
connect_bd_net [get_bd_pins cc_b/dout] [get_bd_pins ila_cam/probe1]

# --- probe2 = {wlast, wready, wvalid} ---
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 cc_w
set_property -dict [list CONFIG.NUM_PORTS {3}] [get_bd_cells cc_w]
connect_bd_net [get_bd_pins axi_vdma_1/m_axi_s2mm_wlast]  [get_bd_pins cc_w/In0]
connect_bd_net [get_bd_pins axi_vdma_1/m_axi_s2mm_wready] [get_bd_pins cc_w/In1]
connect_bd_net [get_bd_pins axi_vdma_1/m_axi_s2mm_wvalid] [get_bd_pins cc_w/In2]
connect_bd_net [get_bd_pins cc_w/dout] [get_bd_pins ila_cam/probe2]

# --- probe3 = {tuser, tlast, tready, tvalid}（AXIS 侧）---
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 cc_ax
set_property -dict [list CONFIG.NUM_PORTS {4}] [get_bd_cells cc_ax]
connect_bd_net [get_bd_pins axi_vdma_1/s_axis_s2mm_tuser]  [get_bd_pins cc_ax/In0]
connect_bd_net [get_bd_pins axi_vdma_1/s_axis_s2mm_tlast]  [get_bd_pins cc_ax/In1]
connect_bd_net [get_bd_pins axi_vdma_1/s_axis_s2mm_tready] [get_bd_pins cc_ax/In2]
connect_bd_net [get_bd_pins axi_vdma_1/s_axis_s2mm_tvalid] [get_bd_pins cc_ax/In3]
connect_bd_net [get_bd_pins cc_ax/dout] [get_bd_pins ila_cam/probe3]

# --- probe4 = awaddr[31:0] ---
connect_bd_net [get_bd_pins axi_vdma_1/m_axi_s2mm_awaddr] [get_bd_pins ila_cam/probe4]

puts "P3R11P_CHECK ila_cam: 5 probes (aw{ready,valid} | b{resp,valid} | w{last,ready,valid} | ax{tuser,tlast,tready,tvalid} | awaddr[31:0]) clk=FCLK1 depth=8192"
puts "P3R11P_CHECK BASIC 许可合规：C_NUM_OF_PROBES=[get_property CONFIG.C_NUM_OF_PROBES [get_bd_cells ila_cam]] (<=5)"
'''

s = s.replace(anchor, ila, 1)

head = (
"# ============================================================================\n"
"# bd_p3r_b11p.tcl -- build11p = build11o + 5 探针原生 ILA（诊断版；BASIC 许可合规）\n"
"#   r14：pc_hp2 READ_WRITE 生效但行为不变(SR=0x14810/DDR 全 0/FRMCNT=1)\n"
"#   => 一次 capture 定性 AXI 写握手 vs AXIS 帧边界\n"
"#   ILA：C_NUM_OF_PROBES=5（BASIC 许可 [Chipscope 16-620] 上限），深度 8192，clk=FCLK1\n"
"#        probe0={awready,awvalid} probe1={bresp,bvalid} probe2={wlast,wready,wvalid}\n"
"#        probe3={tuser,tlast,tready,tvalid} probe4=awaddr[31:0]\n"
"#   AXI 子信号以 BD 引脚访问（小写 s2mm_ 前缀），接口网不改动\n"
"#   其余完全 = build11o\n"
"#   产物 out/build11p/\n"
"# ============================================================================\n")
io.open(BASE + r"\bd_p3r_b11p.tcl", "w", encoding="utf-8", newline="\n").write(head + s)
print("bd_p3r_b11p.tcl v5 written")