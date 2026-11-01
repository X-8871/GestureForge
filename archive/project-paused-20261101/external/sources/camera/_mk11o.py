# -*- coding: utf-8 -*-
"""生成 bd_p3r_b11o.tcl：build11m + pc_hp2 READ_ONLY -> READ_WRITE（根因修复）。只改 1 处参数。"""
import io

BASE = r"D:\tmp\lead\p3r_camera_20261031_r01"
src = BASE + r"\bd_p3r_b11m.tcl"
dst = BASE + r"\bd_p3r_b11o.tcl"

s = io.open(src, encoding="utf-8").read()
s = s.replace('set out  "D:/tmp/lead/p3r_camera_20261031_r01/out/build11m"',
              'set out  "D:/tmp/lead/p3r_camera_20261031_r01/out/build11o"')

old = "CONFIG.SI_PROTOCOL {AXI4} \\\nCONFIG.MI_PROTOCOL {AXI3} \\\nCONFIG.READ_WRITE_MODE {READ_ONLY} \\"
new = "CONFIG.SI_PROTOCOL {AXI4} \\\nCONFIG.MI_PROTOCOL {AXI3} \\\nCONFIG.READ_WRITE_MODE {READ_WRITE} \\"
assert old in s, "pc_hp2 参数锚点未找到"
s = s.replace(old, new, 1)

anchor = "connect_bd_intf_net [get_bd_intf_pins pc_hp2/M_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP2]"
assert anchor in s, "pc_hp2 连接锚点未找到"
check = anchor + '\nputs "P3R11O_CHECK pc_hp2 READ_WRITE_MODE=[get_property CONFIG.READ_WRITE_MODE [get_bd_cells pc_hp2]] (fixed: was READ_ONLY)"'
s = s.replace(anchor, check, 1)

head = """# ============================================================================
# bd_p3r_b11o.tcl -- build11o = build11m + pc_hp2: READ_ONLY -> READ_WRITE (ROOT CAUSE FIX)
#   现象(r12/r13)：数据流探针全对(921600/1280/720/0、STALL=0、tuser==vsync)
#                  但 CAM_SR=0x14810(bit4 DATAMOVER INTERNAL + bit11 FSZ_MORE)、DDR 不落
#   根因：pc_hp2 (AXI4->AXI3，通往 S_AXI_HP2) 的 CONFIG.READ_WRITE_MODE = READ_ONLY
#         (build2 时代只有显示 MM2S 读 DDR 时留下) => 相机 S2MM 的写事务在 HP2 入口被丢弃
#         => 写响应错误 => datamover INTERNAL ERROR + FSZ_MORE + DDR 全 0
#         同源证据：smartconnect 报 S01_AXI(WRITE_ONLY) -> M00_AXI(READ_ONLY)
#   修复：pc_hp2 CONFIG.READ_WRITE_MODE {READ_WRITE}（1 行）
#   其余完全 = build11m（保留 smc_vis、b11j base、tuser_shaper 同拍、全部探针、
#                        FSYNC=2/SOF_EN=1/FLUSH=1、TDATA=24、VDMA 0x43C60000、CDC XDC）
#   产物 out/build11o/
# ============================================================================
"""
io.open(dst, "w", encoding="utf-8", newline="\n").write(head + s)
print("bd_p3r_b11o.tcl written:", len(head + s), "chars")