# 阶段3 T03 HDMI 板测：JTAG 下载自建 bitstream + standalone ELF，并初始化 PS（时钟/DDR）。
# 该脚本会复位系统并写 PL/PS 内存；只做易失性下载，不烧 QSPI/非易失。
# 用法: xsdb jtag_download_t03.tcl <bit> <xsa> <elf> <ps7_init.tcl>

set ::bit      [lindex $argv 0]
set ::xsa      [lindex $argv 1]
set ::elf      [lindex $argv 2]
set ::ps7init  [lindex $argv 3]
if {$::bit eq "" || $::xsa eq "" || $::elf eq "" || $::ps7init eq ""} {
    puts "T03_DL_FAIL=USAGE: -tclargs <bit> <xsa> <elf> <ps7_init.tcl>"
    exit 3
}
foreach f [list $::bit $::xsa $::elf $::ps7init] {
    if {![file exists $f]} { puts "T03_DL_FAIL=MISSING:$f"; exit 3 }
    puts "T03_DL_INPUT=$f"
}

proc dl_step {name script} {
    if {[catch {uplevel 1 $script} err]} {
        puts "T03_DL_FAIL=$name:$err"
        exit 2
    }
    puts "T03_DL_OK=$name"
}

proc select_a9_core0 {} {
    if {[catch {targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}} err]} {
        puts "T03_DL_NOTE=A9_FILTER_FALLBACK:$err"
        targets -set 2
    }
    puts "T03_DL_A9_TARGET_LIST:"
    puts [targets]
}

dl_step CONNECT {connect}
puts "T03_DL_TARGETS_BEGIN"
puts [targets]
puts "T03_DL_TARGETS_END"

dl_step PS_RESET {
    targets -set -nocase -filter {name =~ "*APU*"}
    rst -system
}
after 3000

dl_step FPGA_PROGRAM {fpga -file $::bit}

dl_step PS7_INIT_SOURCE [list source $::ps7init]
dl_step PS7_INIT_RUN {ps7_init}
if {[catch {ps7_post_config} err]} { puts "T03_DL_WARN=PS7_POST_CONFIG:$err" } else { puts "T03_DL_OK=PS7_POST_CONFIG" }

dl_step A9_SELECT {select_a9_core0}
dl_step DOW_ELF {dow $::elf}
dl_step RUN {con}
puts "T03_DL_ALL_DONE=1"