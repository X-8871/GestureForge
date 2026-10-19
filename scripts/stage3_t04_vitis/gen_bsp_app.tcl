# 阶段3 T04：用 Vitis 2026.1 内置 sdtgen/HSI 从 XSA 生成 standalone BSP 与应用骨架
# 用法（由 run_stage3_vitis_elf.cmd 调用，或直接：sdtgen.bat gen_bsp_app.tcl）
# 环境变量：
#   S3_XSA          必填，输入 XSA（Vivado 导出的 design_1_wrapper.xsa）
#   S3_OUT          必填，输出根目录（脚本会创建，含 bsp/ 与 app/）
#   S3_PROC         选填，处理器实例，默认 ps7_cortexa9_0
#   S3_APP_TEMPLATE 选填，应用模板名，默认 empty_application（2026.1 已无 "Empty Application" 名称）
#   S3_DO_BSP       选填，1=附带生成独立 BSP 目录（默认 1）
# 退出：全部关键步骤成功打印 S3_RESULT=PASS；否则 S3_RESULT=FAIL 并给出失败步骤与错误原文。
# 说明：Vitis 2026.1 已禁用 xsct，classic createhw/createbsp/createapp 不可用；
#       但 sdtgen 仍加载完整 HSI（hsi::generate_bsp / hsi::generate_app），本脚本走该入口。

set xsa  $::env(S3_XSA)
set out  $::env(S3_OUT)
set proc "ps7_cortexa9_0"
set tmpl "empty_application"
set do_bsp 1
if {[info exists ::env(S3_PROC)]}          { set proc  $::env(S3_PROC) }
if {[info exists ::env(S3_APP_TEMPLATE)]}  { set tmpl  $::env(S3_APP_TEMPLATE) }
if {[info exists ::env(S3_DO_BSP)]}        { set do_bsp $::env(S3_DO_BSP) }

set bspdir "$out/bsp"
set appdir "$out/app"
set failures {}

puts "S3_STAGE3_VITIS_XSA=$xsa"
puts "S3_STAGE3_VITIS_OUT=$out"
puts "S3_STAGE3_VITIS_PROC=$proc"
puts "S3_STAGE3_VITIS_TEMPLATE=$tmpl"

file mkdir $out

if {[catch { hsi::open_hw_design $xsa } err]} {
    puts "S3_FAIL:OPEN_HW_DESIGN:$err"
    puts "S3_ERRORINFO=$::errorInfo"
    puts "S3_RESULT=FAIL"
    return
}
puts "S3_STEP_OK:OPEN_HW_DESIGN=[hsi::current_hw_design]"
puts "S3_PROCESSORS=[hsi::get_cells -filter {IP_TYPE == PROCESSOR} -hierarchical]"

# 1) BSP：create_sw_design + generate_bsp + write_mss（等价于 classic createbsp）
if {$do_bsp} {
    if {[catch {
        hsi::create_sw_design bsp0 -proc $proc -os standalone
        file mkdir $bspdir
        hsi::generate_bsp -dir $bspdir
        hsi::write_mss -name system -dir $bspdir
        hsi::close_sw_design [hsi::current_sw_design]
    } err]} {
        puts "S3_FAIL:CREATE_BSP:$err"
        lappend failures "BSP"
    } else {
        puts "S3_STEP_OK:CREATE_BSP:$bspdir"
    }
}

# 2) 应用骨架：create_sw_design + generate_app（等价于 classic createapp -app "Empty Application"）
if {[catch {
    hsi::create_sw_design app0 -proc $proc -os standalone
    file mkdir $appdir
    hsi::generate_app -app $tmpl -dir $appdir
} err]} {
    puts "S3_FAIL:GENERATE_APP:$err"
    lappend failures "APP"
} else {
    puts "S3_STEP_OK:GENERATE_APP:$appdir"
}

if {[llength $failures] > 0} {
    puts "S3_FAILED_STEPS=$failures"
    puts "S3_RESULT=FAIL"
} else {
    puts "S3_RESULT=PASS"
}
puts "S3_SCRIPT_END"