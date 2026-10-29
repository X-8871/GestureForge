# P2a：把 M_AXIS 输出流改为内部悬空（不引出顶层 IO），用于"仅 CSR/PL 通路"验证位流
# 原因：外引 13 个 AXIS 端口无板上引脚约束 ⇒ bitgen DRC NSTD-1/UCIO-1 失败；
#       P2a 的目标是验证 PS↔PL 通路与 CSR（长跑根因），不验证输出流（那是合并部署的事）。
import io

p = r"D:\tmp\lead\p2a_20261029_r01\src\bd_preproc_v2.tcl"
t = io.open(p, encoding="utf-8", newline="").read()

old = '''# ---------------- 输出流与状态外引 ----------------
# 输出改为 AXI4-Stream 接口（tuser=帧首、tlast=帧尾），其余状态仍外引为单端信号
make_bd_intf_pins_external [get_bd_intf_pins s4d_0/M_AXIS]
# M_AXIS 需要"随流时钟"：FCLK0 已连内部网络，不能用 make_bd_pins_external 外引，
# 正确做法是新建一个输出时钟端口，接同一条 FCLK0 网络，并把 M_AXIS 关联到它。
create_bd_port -dir O -type clk m_axis_aclk
set_property CONFIG.FREQ_HZ 100000000 [get_bd_ports m_axis_aclk]
set_property CONFIG.ASSOCIATED_BUSIF {M_AXIS_0} [get_bd_ports m_axis_aclk]
connect_bd_net [get_bd_ports m_axis_aclk] [get_bd_pins ps7_0/FCLK_CLK0]
puts "==== FORWARDED CLOCK: /m_axis_aclk <- FCLK0, ASSOCIATED_BUSIF=M_AXIS_0 ===="'''

new = '''# ---------------- 输出流（P2a：内部悬空） ----------------
# P2a 目标 = 验证 PS<->PL 通路与 CSR（长跑根因），不验证输出流。
# 若外引 M_AXIS + 随流时钟，会产生 13 个无引脚约束的顶层端口 -> bitgen DRC NSTD-1/UCIO-1 失败。
# 故本版将 M_AXIS 保持内部悬空；输出流的消费（VDMA/显示）属合并部署（P2b/W-C）。
puts "==== P2A: M_AXIS left internal (output stream not routed to top in this build) ===="'''

assert t.count(old) == 1, ("axis block", t.count(old))
t = t.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("P2A_BD_PATCHED (M_AXIS internal)")