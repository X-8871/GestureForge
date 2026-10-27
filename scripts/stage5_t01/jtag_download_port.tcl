# S5-T01 端口可覆盖的 JTAG 下载（忠实复制 dbdf/jtag_download_t03.tcl 的步骤顺序）。
# 用途：本机 3121 出现 `Socket bind error`（疑似保留端口/占用）时，改用自起 hw_server 的端口。
# 用法: xsdb jtag_download_port.tcl <port> <bit> <xsa> <elf> <ps7_init.tcl>
# 只做易失性下载：PS_RESET → FPGA_PROGRAM → PS7_INIT → DOW → RUN；不烧 QSPI。

set ::port     [lindex $argv 0]
set ::bit      [lindex $argv 1]
set ::xsa      [lindex $argv 2]
set ::elf      [lindex $argv 3]
set ::ps7init  [lindex $argv 4]
if {$::port eq "" || $::bit eq "" || $::elf eq "" || $::ps7init eq ""} {
    puts "S5DL_FAIL=USAGE: -tclargs <port> <bit> <xsa> <elf> <ps7_init.tcl>"
    exit 3
}
foreach f [list $::bit $::elf $::ps7init] {
    if {![file exists $f]} { puts "S5DL_FAIL=MISSING:$f"; exit 3 }
}
puts "S5DL_PORT=$::port"

proc dl_step {name script} {
    if {[catch {uplevel 1 $script} err]} {
        puts "S5DL_FAIL=$name:$err"
        exit 2
    }
    puts "S5DL_OK=$name"
}

dl_step CONNECT [list connect -url tcp:localhost:$::port]
dl_step PS_RESET {
    targets -set -nocase -filter {name =~ "*APU*"}
    rst -system
}
after 3000
dl_step FPGA_PROGRAM [list fpga -file $::bit]
dl_step PS7_INIT_SOURCE [list source $::ps7init]
dl_step PS7_INIT_RUN {ps7_init}
if {[catch {ps7_post_config} err]} { puts "S5DL_WARN=PS7_POST_CONFIG:$err" } else { puts "S5DL_OK=PS7_POST_CONFIG" }
dl_step A9_SELECT {
    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
}
dl_step DOW_ELF [list dow $::elf]
dl_step RUN {con}
puts "S5DL_ALL_DONE=1"