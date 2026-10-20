# S3-T05 在线 A/B 实验：S2MM CR 的 FSYNC_SRC（bit6:5）对 SOF 错误的影响。
#   A: CR=0x00018003（现行为，FSYNC_SRC=00 同通道）
#   B: CR=0x00018043（FSYNC_SRC=10 显式 tuser，对应驱动 XAxiVdma_FsyncSrcSelect(S2MM_TUSER_FSYNC)）
# 只读改写 VDMA 寄存器（易失、可恢复：重下 ELF 即恢复）；不改 PL、不烧 QSPI。
# 用法: xsdb jtag_s2mm_fsync_ab.tcl

proc restart_s2mm {cr} {
    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
    # 1) 停 + 复位 + 清 sticky
    mwr -force 0x43010030 0x00018002
    after 200
    mwr -force 0x43010030 0x00000004
    after 200
    mwr -force 0x43010030 0x00000000
    after 200
    mwr -force 0x43010034 0xFFFFFFFF
    after 200
    # 2) 重编程尺寸/步长/地址
    mwr -force 0x430100A0 0x000002D0
    mwr -force 0x430100A4 0x00000F00
    mwr -force 0x430100A8 0x00000F00
    mwr -force 0x430100AC 0x00110C00
    # 3) 启动
    mwr -force 0x43010030 $cr
}

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "=== CASE A: CR=0x00018003 (FSYNC_SRC=00) ==="
restart_s2mm 0x00018003
after 5000
puts "A_CR=[mrd -force 0x43010030]"
puts "A_SR=[mrd -force 0x43010034]"
after 5000
puts "A_SR2=[mrd -force 0x43010034]"
puts "A_DDR=[mrd -force 0x00110C00 4]"

puts "=== CASE B: CR=0x00018043 (FSYNC_SRC=10 tuser) ==="
restart_s2mm 0x00018043
after 5000
puts "B_CR=[mrd -force 0x43010030]"
puts "B_SR=[mrd -force 0x43010034]"
after 5000
puts "B_SR2=[mrd -force 0x43010034]"
puts "B_DDR=[mrd -force 0x00110C00 4]"

# 还原为现行为（RS=1, FSYNC_SRC=00），清 sticky，然后恢复 CPU
mwr -force 0x43010030 0x00018003
mwr -force 0x43010034 0xFFFFFFFF
if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "FSYNC_AB_DONE=1"