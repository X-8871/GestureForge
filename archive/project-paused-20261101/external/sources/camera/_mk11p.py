# -*- coding: utf-8 -*-
"""生成 bd_p3r_b11p.tcl = build11o + system_ila（AXI 写侧 + AXIS 侧，各 1 slot，深度 8192）。
只加 ILA，不改任何既有逻辑/参数。"""
import io

BASE = r"D:\tmp\lead\p3r_camera_20261031_r01"
s = io.open(BASE + r"\bd_p3r_b11o.tcl", encoding="utf-8").read()
s = s.replace('set out  "D:/tmp/lead/p3r_camera_20261031_r01/out/build11o"',
              'set out  "D:/tmp/lead/p3r_camera_20261031_r01/out/build11p"')

anchor = 'puts "P3R11O_CHECK pc_hp2 READ_WRITE_MODE=[get_property CONFIG.READ_WRITE_MODE [get_bd_cells pc_hp2]] (fixed, was READ_ONLY)"'
assert anchor in s, "b11o 锚点未找到"

ila = anchor + r'''

# ============================================================================
# build11p：system_ila 诊断（AXI 写侧 + AXIS 侧），全部被动监视，不改逻辑
#   SLOT_0_AXI  : axi_vdma_1/M_AXI_S2MM（awvalid/awready/awaddr/wvalid/wready/wlast/bvalid/bresp）
#   SLOT_1_AXIS : axi_vdma_1/S_AXIS_S2MM（tvalid/tready/tlast/tuser）
#   采样时钟 FCLK1(100 MHz)、深度 8192
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:system_ila:1.1 system_ila_cam
set_property -dict [list \
    CONFIG.C_NUM_MONITOR_SLOTS {2} \
    CONFIG.C_SLOT_0_INTF_TYPE {xilinx.com:interface:aximm_rtl:1.0} \
    CONFIG.C_SLOT_1_INTF_TYPE {xilinx.com:interface:axis_rtl:1.0} \
    CONFIG.C_DATA_DEPTH {8192} \
    CONFIG.C_ADV_TRIGGER {false} \
    CONFIG.C_BRAM_CNT {18} \
] [get_bd_cells system_ila_cam]
connect_bd_intf_net [get_bd_intf_pins axi_vdma_1/M_AXI_S2MM] [get_bd_intf_pins system_ila_cam/SLOT_0_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_vdma_1/S_AXIS_S2MM] [get_bd_intf_pins system_ila_cam/SLOT_1_AXIS]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK1] [get_bd_pins system_ila_cam/clk]
connect_bd_net [get_bd_pins rst_100/peripheral_aresetn] [get_bd_pins system_ila_cam/resetn]
puts "P3R11P_CHECK system_ila_cam: SLOT0=axi_vdma_1/M_AXI_S2MM  SLOT1=axi_vdma_1/S_AXIS_S2MM  clk=FCLK1 depth=8192"
'''

s = s.replace(anchor, ila, 1)

head = (
"# ============================================================================\n"
"# bd_p3r_b11p.tcl -- build11p = build11o + system_ila（诊断版，非最终交付位流）\n"
"#   目的：r14 证明 pc_hp2 READ_WRITE 生效但行为不变（SR=0x14810、DDR 全 0、FRMCNT=1）\n"
"#         => 一次 capture 定性：(a) VDMA 的 AXI 写握手是否完成 (b) AXIS 帧边界是否与 VSIZE 一致\n"
"#   加：system_ila_cam（深度 8192，clk=FCLK1）\n"
"#       SLOT_0_AXI  = axi_vdma_1/M_AXI_S2MM  (awvalid/awready/awaddr[31:0]/wvalid/wready/wlast/bvalid/bresp[1:0])\n"
"#       SLOT_1_AXIS = axi_vdma_1/S_AXIS_S2MM (tvalid/tready/tlast/tuser)\n"
"#   其余完全 = build11o（pc_hp2 READ_WRITE、tuser_shaper、全部探针 0x43C8..0x43DB、\n"
"#                      FSYNC=2/SOF_EN=1/FLUSH=1、TDATA=24、VDMA 0x43C60000、CDC XDC）\n"
"#   产物 out/build11p/\n"
"# ============================================================================\n")
io.open(BASE + r"\bd_p3r_b11p.tcl", "w", encoding="utf-8", newline="\n").write(head + s)
print("bd_p3r_b11p.tcl written:", len(head + s), "chars")