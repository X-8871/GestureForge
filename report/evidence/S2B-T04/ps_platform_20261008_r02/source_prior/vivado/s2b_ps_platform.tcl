# S2B-T04：仅创建 PS7 的 UART/DDR 离线候选，不连接 PL AXI，不操作硬件。
# 厂商字段和候选限制见 board/ps_platform_fields.json 与 board/ps_platform.md。

namespace eval ::s2b_ps_platform {
    variable version 1.0.0
    variable cell ps7
    variable bd_name s2b_ps_only
    variable part xc7z020clg400-2
}

proc ::s2b_ps_platform::fresh_dir {path} {
    # 按传入字面路径核验父目录；不修正分隔符，不覆盖任何已有目标。
    if {[file pathtype $path] ne "absolute"} {error "绝对路径必需：$path"}
    if {![file isdirectory [file dirname $path]]} {error "父目录不存在：$path"}
    if {[file exists $path]} {error "拒绝复用已有目录：$path"}
    file mkdir $path
    return $path
}

proc ::s2b_ps_platform::write_new {path text} {
    # EXCL 保证已有报告或导出文件不可被悄悄覆盖。
    set channel [open $path {WRONLY CREAT EXCL}]
    fconfigure $channel -encoding utf-8 -translation lf
    try {puts $channel $text} finally {close $channel}
}

proc ::s2b_ps_platform::prepare {project_dir} {
    variable part
    variable bd_name
    if {[current_project -quiet] ne ""} {error "已有打开项目，停止创建"}
    if {[llength [get_parts $part]] != 1} {error "精确器件不存在：$part"}
    fresh_dir $project_dir
    create_project s2b_ps_candidate $project_dir -part $part
    set_property target_language Verilog [current_project]
    create_bd_design $bd_name
    return "PREPARE:OK"
}

proc ::s2b_ps_platform::requested {} {
    # 新版 V2.2 兼容 MT41J256M16RE-125；0.25ns 延时仅为旧例程候选。
    # 不导入旧工具的封装延时；由当前精确器件在 Vivado 2026.1 派生。
    return [dict create \
        CONFIG.PCW_IMPORT_BOARD_PRESET {None} \
        CONFIG.PCW_CRYSTAL_PERIPHERAL_FREQMHZ {33.333333} \
        CONFIG.PCW_PRESET_BANK0_VOLTAGE {LVCMOS 3.3V} \
        CONFIG.PCW_PRESET_BANK1_VOLTAGE {LVCMOS 1.8V} \
        CONFIG.PCW_UART0_PERIPHERAL_ENABLE {0} \
        CONFIG.PCW_UART1_PERIPHERAL_ENABLE {1} \
        CONFIG.PCW_UART1_UART1_IO {MIO 48 .. 49} \
        CONFIG.PCW_UART1_GRP_FULL_ENABLE {0} \
        CONFIG.PCW_UART_PERIPHERAL_FREQMHZ {100} \
        CONFIG.PCW_MIO_48_IOTYPE {LVCMOS 1.8V} \
        CONFIG.PCW_MIO_49_IOTYPE {LVCMOS 1.8V} \
        CONFIG.PCW_UIPARAM_DDR_ENABLE {1} \
        CONFIG.PCW_UIPARAM_DDR_PARTNO {MT41J256M16 RE-125} \
        CONFIG.PCW_UIPARAM_DDR_MEMORY_TYPE {DDR 3} \
        CONFIG.PCW_UIPARAM_DDR_BUS_WIDTH {32 Bit} \
        CONFIG.PCW_UIPARAM_DDR_DRAM_WIDTH {16 Bits} \
        CONFIG.PCW_UIPARAM_DDR_DEVICE_CAPACITY {4096 MBits} \
        CONFIG.PCW_UIPARAM_DDR_ROW_ADDR_COUNT {15} \
        CONFIG.PCW_UIPARAM_DDR_COL_ADDR_COUNT {10} \
        CONFIG.PCW_UIPARAM_DDR_BANK_ADDR_COUNT {3} \
        CONFIG.PCW_UIPARAM_DDR_FREQ_MHZ {533.333333} \
        CONFIG.PCW_UIPARAM_DDR_ECC {Disabled} \
        CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY0 {0.25} \
        CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY1 {0.25} \
        CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY2 {0.25} \
        CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY3 {0.25} \
        CONFIG.PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_0 {0.0} \
        CONFIG.PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_1 {0.0} \
        CONFIG.PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_2 {0.0} \
        CONFIG.PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_3 {0.0} \
        CONFIG.PCW_UIPARAM_DDR_TRAIN_WRITE_LEVEL {1} \
        CONFIG.PCW_UIPARAM_DDR_TRAIN_READ_GATE {1} \
        CONFIG.PCW_UIPARAM_DDR_TRAIN_DATA_EYE {1} \
        CONFIG.PCW_USE_M_AXI_GP0 {0} \
        CONFIG.PCW_USE_M_AXI_GP1 {0} \
        CONFIG.PCW_USE_S_AXI_GP0 {0} \
        CONFIG.PCW_USE_S_AXI_GP1 {0} \
        CONFIG.PCW_USE_S_AXI_HP0 {0} \
        CONFIG.PCW_USE_S_AXI_HP1 {0} \
        CONFIG.PCW_USE_S_AXI_HP2 {0} \
        CONFIG.PCW_USE_S_AXI_HP3 {0} \
        CONFIG.PCW_USE_S_AXI_ACP {0} \
        CONFIG.PCW_EN_CLK0_PORT {0} \
        CONFIG.PCW_EN_CLK1_PORT {0} \
        CONFIG.PCW_EN_CLK2_PORT {0} \
        CONFIG.PCW_EN_CLK3_PORT {0} \
        CONFIG.PCW_EN_RST0_PORT {0} \
        CONFIG.PCW_EN_RST1_PORT {0} \
        CONFIG.PCW_EN_RST2_PORT {0} \
        CONFIG.PCW_EN_RST3_PORT {0}]
}

proc ::s2b_ps_platform::configure {evidence_dir} {
    variable cell
    if {![file isdirectory $evidence_dir]} {error "证据目录不存在"}
    foreach name {baseline.tcldict intent.tcldict} {
        if {[file exists [file join $evidence_dir $name]]} {error "拒绝覆盖配置证据：$name"}
    }
    if {![ipcfg::vlnv_ok xilinx.com:ip:processing_system7]} {error "PS7 不支持当前器件"}
    set requested [requested]
    # 独立默认单元提供真实默认值；读取后删除，不遗留在交付 BD。
    set default_result [ipcfg::create_cell xilinx.com:ip:processing_system7 defaults]
    if {![string match {SUCCESS:*} $default_result]} {error $default_result}
    set baseline [ipcfg::snapshot defaults [dict keys $requested]]
    ipcfg::write_evidence [file join $evidence_dir baseline.tcldict] $baseline
    puts [ipcfg::cleanup defaults]
    set result [ipcfg::create_cell_cfg xilinx.com:ip:processing_system7 $cell $requested]
    if {![string match {SUCCESS:*} $result]} {error $result}
    set stuck [ipcfg::verify_stuck $cell $requested]
    if {[llength $stuck]} {error "STUCK_FAIL:$stuck"}
    set reqmap {}
    dict for {key want} $requested {lappend reqmap $key $want [dict get $baseline $key]}
    set intent [ipcfg::verify_intent $cell $reqmap 0]
    if {[llength $intent]} {error "INTENT_FAIL:$intent"}
    ipcfg::write_evidence [file join $evidence_dir intent.tcldict] [dict create baseline $baseline requested $requested audit [ipcfg::audit_intent $cell $reqmap]]
    return "CONFIG:OK"
}

proc ::s2b_ps_platform::validate {} {
    variable cell
    make_bd_intf_pins_external [get_bd_intf_pins $cell/DDR]
    make_bd_intf_pins_external [get_bd_intf_pins $cell/FIXED_IO]
    validate_bd_design -force
    save_bd_design
    return "VALIDATE:OK"
}

proc ::s2b_ps_platform::products {} {
    variable bd_name
    set bd_file [get_files */${bd_name}.bd]
    generate_target all $bd_file
    set wrapper [make_wrapper -files $bd_file -top]
    if {![llength [get_files -quiet $wrapper]]} {add_files $wrapper}
    set_property top ${bd_name}_wrapper [current_fileset]
    update_compile_order -fileset sources_1
    return "PRODUCTS:OK"
}

proc ::s2b_ps_platform::export {evidence_dir} {
    variable cell
    variable bd_name
    set ps [get_bd_cells $cell]
    set bd_file [get_files */${bd_name}.bd]
    foreach name {s2b_ps_only.xsa s2b_ps_only.bd readback.tcldict readback.tsv interfaces.tcldict} {
        if {[file exists [file join $evidence_dir $name]]} {error "拒绝覆盖导出证据：$name"}
    }
    # 导出硬件描述但不请求位流；不存在任何综合、实现或器件操作。
    set xsa [file join $evidence_dir s2b_ps_only.xsa]
    if {[file exists $xsa]} {error "拒绝覆盖 XSA：$xsa"}
    write_hw_platform -fixed $xsa
    set bd_copy [file join $evidence_dir s2b_ps_only.bd]
    if {[file exists $bd_copy]} {error "拒绝覆盖 BD：$bd_copy"}
    file copy $bd_file $bd_copy
    set keys [concat [dict keys [requested]] {
        CONFIG.PCW_EN_DDR CONFIG.PCW_EN_UART1
        CONFIG.PCW_UART1_BASEADDR CONFIG.PCW_UART1_HIGHADDR
        CONFIG.PCW_MIO_48_DIRECTION CONFIG.PCW_MIO_49_DIRECTION
        CONFIG.PCW_UIPARAM_DDR_CL CONFIG.PCW_UIPARAM_DDR_CWL
        CONFIG.PCW_UIPARAM_DDR_SPEED_BIN CONFIG.PCW_UIPARAM_ACT_DDR_FREQ_MHZ
        CONFIG.PCW_UIPARAM_DDR_T_FAW CONFIG.PCW_UIPARAM_DDR_T_RAS_MIN
        CONFIG.PCW_UIPARAM_DDR_T_RC CONFIG.PCW_UIPARAM_DDR_T_RCD CONFIG.PCW_UIPARAM_DDR_T_RP
        CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY0 CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY1
        CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY2 CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY3
        CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_0 CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_1
        CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_2 CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_3
    }]
    set readback [ipcfg::snapshot $cell $keys]
    ipcfg::write_evidence [file join $evidence_dir readback.tcldict] $readback
    set lines [list "parameter\tactual"]
    dict for {key value} $readback {lappend lines "$key\t$value"}
    write_new [file join $evidence_dir readback.tsv] [join $lines \n]
    ipcfg::write_evidence [file join $evidence_dir interfaces.tcldict] [dict create cells [get_bd_cells] interfaces [get_bd_intf_pins -of_objects $ps] external_interfaces [get_bd_intf_ports] scalar_pins [get_bd_pins -of_objects $ps] part [get_property PART [current_project]]]
    return "EXPORT:OK"
}

proc ::s2b_ps_platform::run {project_dir evidence_dir helper native_log} {
    # 从新目录重建的入口；依赖已安装 ROSS library 及本次 Vivado 原生日志路径。
    if {![file isfile $helper] || ![file isfile $native_log]} {error "helper 或原生日志不存在"}
    if {[current_project -quiet] ne ""} {error "已有打开项目，停止创建"}
    foreach path [list $project_dir $evidence_dir] {
        if {[file pathtype $path] ne "absolute" || ![file isdirectory [file dirname $path]] || [file exists $path]} {
            error "新目录精确路径或父目录不满足要求：$path"
        }
    }
    fresh_dir $evidence_dir
    prepare $project_dir
    if {![llength [info commands ::ipcfg::help]]} {source -notrace $helper}
    set ::ipcfg::native_log_path $native_log
    set python [ipcfg::python_status]
    if {![string match {PYTHON:OK*} $python]} {error $python}
    puts $python
    puts [ipcfg::python_exec -c {import argparse, base64, hashlib, json, pathlib, re, sys, typing; print("PYTHON_IMPORTS:OK")}]
    set configure_receipt [ipcfg::capture [file join $evidence_dir configure.tcldict] [list ::s2b_ps_platform::configure $evidence_dir] {CONFIG:OK}]
    puts $configure_receipt
    if {[dict get $configure_receipt status] ne "OK"} {error "配置 capture 未通过"}
    set validate_receipt [ipcfg::capture [file join $evidence_dir validate.tcldict] [list ::s2b_ps_platform::validate] {VALIDATE:OK}]
    puts $validate_receipt
    if {[dict get $validate_receipt status] ne "OK"} {error "验证 capture 未通过"}
    set products_receipt [ipcfg::capture [file join $evidence_dir products.tcldict] [list ::s2b_ps_platform::products] {PRODUCTS:OK}]
    puts $products_receipt
    # Vivado 2026.1 生成输出时会重排普通警告历史，ROSS 严格计数可误报。
    # 只在本次 Tcl 成功且没有错误/关键警告、原因精确为 WARNING 计数变化时重验一次。
    # 失败原证据保留；第二次仍需严格 OK，绝不放行真实配置或生成失败。
    if {[dict get $products_receipt status] ne "OK" &&
        [dict get $products_receipt code] == 0 &&
        [dict get $products_receipt error_count] == 0 &&
        [dict get $products_receipt critical_count] == 0 &&
        [dict exists $products_receipt capture_error] &&
        [string match {CAPTURE_FAIL:native message export incomplete or counters changed: WARNING emitted=*} [dict get $products_receipt capture_error]]} {
        set products_receipt [ipcfg::capture [file join $evidence_dir products_recheck.tcldict] [list ::s2b_ps_platform::products] {PRODUCTS:OK}]
        puts $products_receipt
    }
    if {[dict get $products_receipt status] ne "OK"} {error "输出生成 capture 未通过"}
    set export_receipt [ipcfg::capture [file join $evidence_dir export.tcldict] [list ::s2b_ps_platform::export $evidence_dir] {EXPORT:OK}]
    puts $export_receipt
    if {[dict get $export_receipt status] ne "OK"} {error "导出 capture 未通过"}
    return "PS_PLATFORM:OFFLINE_CANDIDATE_OK"
}
