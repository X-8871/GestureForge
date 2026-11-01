# -*- coding: utf-8 -*-
import io
BASE = r"D:\tmp\lead\p3r_camera_20261031_r01"
s = io.open(BASE + r"\bd_p3r_b11m.tcl", encoding="utf-8").read()
s = s.replace('set out  "D:/tmp/lead/p3r_camera_20261031_r01/out/build11m"',
              'set out  "D:/tmp/lead/p3r_camera_20261031_r01/out/build11o"')
old = "    CONFIG.READ_WRITE_MODE {READ_ONLY} \\"
assert old in s, "READ_ONLY 行锚点"
s = s.replace(old, "    CONFIG.READ_WRITE_MODE {READ_WRITE} \\", 1)
anchor = "connect_bd_intf_net [get_bd_intf_pins pc_hp2/M_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP2]"
assert anchor in s, "pc_hp2 连接锚点"
s = s.replace(anchor, anchor + '\nputs "P3R11O_CHECK pc_hp2 READ_WRITE_MODE=[get_property CONFIG.READ_WRITE_MODE [get_bd_cells pc_hp2]] (fixed, was READ_ONLY)"', 1)
head = (
"# ============================================================================\n"
"# bd_p3r_b11o.tcl -- build11o = build11m + pc_hp2: READ_ONLY -> READ_WRITE (ROOT CAUSE FIX)\n"
"#   r12/r13: 数据流探针全对(921600/1280/720/0、STALL=0、tuser==vsync)\n"
"#            但 CAM_SR=0x14810(bit4 DATAMOVER INTERNAL + bit11 FSZ_MORE)、DDR 不落\n"
"#   根因: pc_hp2 (AXI4->AXI3, 通往 S_AXI_HP2) 的 READ_WRITE_MODE = READ_ONLY\n"
"#         (build2 时代只有显示 MM2S 读 DDR 时留下) => 相机 S2MM 写事务在 HP2 入口被丢弃\n"
"#         => 写响应错误 => datamover INTERNAL ERROR + FSZ_MORE + DDR 全 0\n"
"#         同源证据: smartconnect 报 S01_AXI(WRITE_ONLY) -> M00_AXI(READ_ONLY)\n"
"#   修复: pc_hp2 READ_WRITE_MODE {READ_WRITE} (1 行)\n"
"#   其余 = build11m (保留 smc_vis、b11j base、tuser_shaper、全部探针、\n"
"#                   FSYNC=2/SOF_EN=1/FLUSH=1、TDATA=24、VDMA 0x43C60000、CDC XDC)\n"
"#   产物 out/build11o/\n"
"# ============================================================================\n")
io.open(BASE + r"\bd_p3r_b11o.tcl", "w", encoding="utf-8", newline="\n").write(head + s)
print("b11o written", len(head+s), "chars")
