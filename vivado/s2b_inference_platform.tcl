# S2B-T13：隔离目录重建全模型 PS/PL 平台；不启动综合、实现或板卡操作。
namespace eval ::s2b_inference_platform {
    variable version 0.1.3
    variable part xc7z020clg400-2
    variable bd_name s2b_inference
    variable rtl_sources {
        src/s2a_network_descriptor_pkg.sv
        src/int8_maxpool_geometry.sv
        src/int8_maxpool_window.sv
        src/s2b_route_query.sv
        src/int8_upsample_query.sv
        src/s2a_conv_tile_engine.sv
        src/s2b_maxpool_engine.sv
        src/s2b_route_engine.sv
        src/s2b_upsample_engine.sv
        src/s2b_network_backend.sv
        src/s2a_memory_master.sv
        src/s2a_runtime_shell.sv
        src/s2b_stage2b_core.sv
        src/s2a_control_csr.sv
        src/s2b_request_guard.sv
        src/s2b_hp0_word_adapter.sv
        src/s2b_control_csr.sv
        src/s2b_inference_top.sv
    }
}

proc ::s2b_inference_platform::literal_absolute {path} {
    # 拒绝工具可能折叠的点组件、重复分隔符和 Windows 非法尾部名称。
    if {[file pathtype $path] ne "absolute" ||
        [regexp {(^|[/\\])\.{1,2}([/\\]|$)} $path] ||
        [regexp {[/\\]{2}} $path] || [regexp {[ .]$} $path]} {
        error "PATH_LITERAL_FAIL:$path"
    }
    return [file split $path]
}

proc ::s2b_inference_platform::exact_existing {path kind} {
    set parts [literal_absolute $path]
    set current [lindex $parts 0]
    set checked [list $current]
    foreach component [lrange $parts 1 end] {
        if {![file isdirectory $current]} {error "PATH_PARENT_TYPE_FAIL:$current"}
        set names [glob -nocomplain -directory $current -tails -- * .*]
        if {[lsearch -exact $names $component] < 0} {error "PATH_EXACT_NAME_FAIL:$path:$component"}
        set current [file join $current $component]
        file lstat $current info
        if {$info(type) eq "link"} {error "PATH_LINK_FAIL:$current"}
        lappend checked $current
    }
    if {($kind eq "directory" && ![file isdirectory $current]) ||
        ($kind eq "file" && ![file isfile $current])} {error "PATH_TARGET_TYPE_FAIL:$path:$kind"}
    return $checked
}

proc ::s2b_inference_platform::new_directory {path} {
    literal_absolute $path
    set name [file tail $path]
    if {$name eq "" || [regexp {[<>:"/\\|?*\x00-\x1f]} $name] || [regexp {[ .]$} $name]} {
        error "PATH_NEW_NAME_FAIL:$path"
    }
    set checked [exact_existing [file dirname $path] directory]
    # exists 会同时拒绝 Windows 大小写别名，lstat 也拒绝悬空链接占据名称。
    if {[file exists $path] || ![catch {file lstat $path info}]} {error "PATH_ALREADY_EXISTS:$path"}
    return $checked
}

proc ::s2b_inference_platform::reject_overlap {project_dir evidence_dir} {
    set a [literal_absolute $project_dir]
    set b [literal_absolute $evidence_dir]
    if {$::tcl_platform(platform) eq "windows"} {
        set a [string tolower $a]
        set b [string tolower $b]
    }
    set count [expr {min([llength $a], [llength $b])}]
    if {[lrange $a 0 [expr {$count-1}]] eq [lrange $b 0 [expr {$count-1}]]} {
        error "PATH_OUTPUT_OVERLAP:$project_dir:$evidence_dir"
    }
}

proc ::s2b_inference_platform::reject_reparse {components} {
    if {$::tcl_platform(platform) ne "windows"} {return}
    # Tcl 的 lstat 不能可靠识别所有 junction/reparse 类型；固定只读 .NET 调用补核。
    # 路径仅作为 Base64 UTF-8 数据传入，绝不插入可执行表达式。
    set payload [binary encode base64 -maxlen 0 [encoding convertto utf-8 [join [lsort -unique $components] \n]]]
    set script [string map [list @DATA@ $payload] {
        $ErrorActionPreference = 'Stop'
        $taskPaths = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('@DATA@')).Split([char]10)
        foreach ($taskPath in $taskPaths) {
            $taskAttributes = [IO.File]::GetAttributes($taskPath)
            if (($taskAttributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'PATH_REPARSE_FAIL'
            }
        }
        Write-Output 'PATH_REPARSE:OK'
    }]
    set result [exec powershell.exe -NoLogo -NoProfile -NonInteractive -Command $script]
    if {[string trim $result] ne "PATH_REPARSE:OK"} {error "PATH_REPARSE_CHECK_FAIL:$result"}
}

proc ::s2b_inference_platform::path_preflight {repo_root project_dir evidence_dir helper native_log proof review} {
    set checked [exact_existing $repo_root directory]
    reject_overlap $project_dir $evidence_dir
    set checked [concat $checked [new_directory $project_dir] [new_directory $evidence_dir]]
    set files [list $helper $native_log [file join $repo_root vivado/s2b_ps_platform.tcl] \
        [file join $repo_root verification/check_s2b_inference_platform.py]]
    if {$proof ne "" || $review ne ""} {
        if {$proof eq "" || $review eq ""} {error "可见性证明和独立审查必须成对提供"}
        lappend files $proof $review
    }
    foreach path $files {set checked [concat $checked [exact_existing $path file]]}
    reject_reparse $checked
    return "PATH_PREFLIGHT:OK"
}

proc ::s2b_inference_platform::capture {evidence_dir name script expected} {
    set receipt [ipcfg::capture [file join $evidence_dir ${name}.tcldict] $script $expected]
    puts $receipt
    if {[dict get $receipt status] ne "OK"} {error "PLATFORM_CAPTURE_FAIL:$name"}
}

proc ::s2b_inference_platform::create_ip {evidence_dir name vlnv requested} {
    capture $evidence_dir ${name}_configure [list ipcfg::create_cell_cfg $vlnv $name $requested] {SUCCESS:}
    set stuck [ipcfg::verify_stuck $name $requested]
    if {[llength $stuck]} {error "PLATFORM_CONFIG_READBACK_FAIL:$name:$stuck"}
    ipcfg::write_evidence [file join $evidence_dir ${name}_readback.tcldict] \
        [dict create requested $requested actual [ipcfg::snapshot $name [dict keys $requested]]]
}

proc ::s2b_inference_platform::construct {evidence_dir visibility} {
    # 复用冻结 PS-only DDR/UART 请求，PL 侧只增加当前接口所需的六个配置。
    set ps_request [dict replace [::s2b_ps_platform::requested] \
        CONFIG.PCW_USE_M_AXI_GP0 1 CONFIG.PCW_USE_S_AXI_HP0 1 \
        CONFIG.PCW_S_AXI_HP0_DATA_WIDTH 64 CONFIG.PCW_EN_CLK0_PORT 1 \
        CONFIG.PCW_EN_RST0_PORT 1 CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ 50]
    create_ip $evidence_dir ps7 xilinx.com:ip:processing_system7 $ps_request
    create_ip $evidence_dir axi_gp0_lite xilinx.com:ip:axi_protocol_converter \
        [dict create CONFIG.SI_PROTOCOL AXI3 CONFIG.MI_PROTOCOL AXI4LITE \
            CONFIG.ADDR_WIDTH 32 CONFIG.DATA_WIDTH 32 CONFIG.ID_WIDTH 12 CONFIG.TRANSLATION_MODE 0]
    create_ip $evidence_dir rst_fclk0 xilinx.com:ip:proc_sys_reset \
        [dict create CONFIG.C_EXT_RESET_HIGH 0 CONFIG.C_AUX_RESET_HIGH 1]
    create_ip $evidence_dir const_zero xilinx.com:ip:xlconstant \
        [dict create CONFIG.CONST_WIDTH 1 CONFIG.CONST_VAL 0]
    create_ip $evidence_dir const_one xilinx.com:ip:xlconstant \
        [dict create CONFIG.CONST_WIDTH 1 CONFIG.CONST_VAL 1]
    capture $evidence_dir connect [list ::s2b_inference_platform::connect $visibility] {CONNECT:OK}
    return "CONSTRUCT:OK"
}

proc ::s2b_inference_platform::externalize_unique {pin_path name} {
    # 外口创建命令只保证副作用，返回值可能为空；从真实接口网查询新增端点。
    set pin [get_bd_intf_pins $pin_path]
    if {[llength $pin] != 1} {error "EXTERNAL_SOURCE_PIN_COUNT_FAIL:$pin_path"}
    set before [get_bd_intf_ports]
    make_bd_intf_pins_external $pin
    set nets [get_bd_intf_nets -of_objects $pin]
    if {[llength $nets] != 1} {error "EXTERNAL_INTERFACE_NET_COUNT_FAIL:$pin_path:$nets"}
    set endpoints [get_bd_intf_ports -of_objects $nets]
    set created {}
    foreach port $endpoints {
        if {[lsearch -exact $before $port] < 0} {lappend created $port}
    }
    if {[llength $endpoints] != 1 || [llength $created] != 1} {
        error "EXTERNAL_NEW_ENDPOINT_COUNT_FAIL:$pin_path:$endpoints:$created"
    }
    set_property name $name [lindex $created 0]
    set renamed [get_bd_intf_ports -of_objects $nets]
    if {[llength $renamed] != 1 || [file tail $renamed] ne $name} {
        error "EXTERNAL_ENDPOINT_NAME_READBACK_FAIL:$pin_path:$renamed"
    }
    return $renamed
}

proc ::s2b_inference_platform::connect {visibility} {
    create_bd_cell -type module -reference s2b_inference_top infer
    set_property CONFIG.PROFILE_VISIBILITY_PROVEN $visibility [get_bd_cells infer]
    if {[get_property CONFIG.PROFILE_VISIBILITY_PROVEN [get_bd_cells infer]] != $visibility} {
        error "VISIBILITY_PARAMETER_READBACK_FAIL"
    }
    connect_bd_intf_net [get_bd_intf_pins ps7/M_AXI_GP0] [get_bd_intf_pins axi_gp0_lite/S_AXI]
    connect_bd_intf_net [get_bd_intf_pins axi_gp0_lite/M_AXI] [get_bd_intf_pins infer/S_AXI]
    # HP0 原生 AXI3 直接连接；任何额外 bridge/buffer 都使当前可见性证明失效。
    connect_bd_intf_net [get_bd_intf_pins infer/M_AXI] [get_bd_intf_pins ps7/S_AXI_HP0]
    connect_bd_net [get_bd_pins ps7/FCLK_CLK0] \
        [get_bd_pins ps7/M_AXI_GP0_ACLK] [get_bd_pins ps7/S_AXI_HP0_ACLK] \
        [get_bd_pins axi_gp0_lite/aclk] [get_bd_pins rst_fclk0/slowest_sync_clk] [get_bd_pins infer/clk]
    # FCLK reset 是冷初始化输入，软件不得在运行期单独重置 PL。
    connect_bd_net [get_bd_pins ps7/FCLK_RESET0_N] [get_bd_pins rst_fclk0/ext_reset_in]
    connect_bd_net [get_bd_pins const_zero/dout] [get_bd_pins rst_fclk0/aux_reset_in] [get_bd_pins rst_fclk0/mb_debug_sys_rst]
    # 时钟直接来自 PS FCLK0，无额外 MMCM；此常量不是可见性证明。
    connect_bd_net [get_bd_pins const_one/dout] [get_bd_pins rst_fclk0/dcm_locked]
    connect_bd_net [get_bd_pins rst_fclk0/peripheral_aresetn] \
        [get_bd_pins axi_gp0_lite/aresetn] [get_bd_pins infer/cold_resetn]
    externalize_unique ps7/DDR DDR
    externalize_unique ps7/FIXED_IO FIXED_IO
    set control_segments [get_bd_addr_segs -of_objects [get_bd_intf_pins infer/S_AXI]]
    if {[llength $control_segments] != 1} {error "CONTROL_SEGMENT_COUNT_FAIL:$control_segments"}
    assign_bd_address -offset 0x43C00000 -range 0x00010000 \
        -target_address_space [get_bd_addr_spaces ps7/Data] $control_segments
    # PS 可寻址 1 GiB 不等于 PL 白名单；adapter/guard 限制逐对象物理范围。
    assign_bd_address -offset 0x00000000 -range 0x40000000 \
        -target_address_space [get_bd_addr_spaces infer/M_AXI] [get_bd_addr_segs ps7/S_AXI_HP0/HP0_DDR_LOWOCM]
    return "CONNECT:OK"
}

proc ::s2b_inference_platform::assert_property {object property expected} {
    set actual [get_property $property $object]
    if {$actual ne $expected} {error "PLATFORM_AUDIT_FAIL:$object:$property:expected=$expected:actual=$actual"}
}

proc ::s2b_inference_platform::physical_port_members {} {
    # get_bd_ports 包含接口的合法标量成员；唯一允许集合是两接口成员的并集。
    set externals {}
    set members {}
    set union {}
    foreach port [get_bd_intf_ports] {
        set name [file tail $port]
        lappend externals $name
        set scalar [get_bd_ports -of_objects $port]
        if {![llength $scalar]} {error "PHYSICAL_INTERFACE_MEMBERS_EMPTY:$port"}
        dict set members $name [lsort $scalar]
        set union [concat $union $scalar]
    }
    if {[lsort $externals] ne [lsort [list DDR FIXED_IO]]} {
        error "PHYSICAL_INTERFACE_SET_FAIL:$externals"
    }
    set actual [lsort [get_bd_ports]]
    set expected [lsort -unique $union]
    if {$actual ne $expected} {error "PHYSICAL_SCALAR_MEMBERS_FAIL:actual=$actual:expected=$expected"}
    return [dict create interfaces [lsort $externals] members $members scalar_ports $actual]
}

proc ::s2b_inference_platform::audit {evidence_dir visibility} {
    variable part
    assert_property [current_project] PART $part
    foreach {pin protocol data id} {
        ps7/M_AXI_GP0 AXI3 32 12
        axi_gp0_lite/S_AXI AXI3 32 12
        axi_gp0_lite/M_AXI AXI4LITE 32 0
        infer/S_AXI AXI4LITE 32 0
        infer/M_AXI AXI3 64 6
        ps7/S_AXI_HP0 AXI3 64 6
    } {
        set object [get_bd_intf_pins $pin]
        assert_property $object CONFIG.PROTOCOL $protocol
        assert_property $object CONFIG.ADDR_WIDTH 32
        assert_property $object CONFIG.DATA_WIDTH $data
        if {$protocol eq "AXI3"} {assert_property $object CONFIG.ID_WIDTH $id}
    }
    set hp_net [get_bd_intf_nets -of_objects [get_bd_intf_pins infer/M_AXI]]
    set endpoints [lsort [get_bd_intf_pins -of_objects $hp_net]]
    if {$endpoints ne [lsort [concat [get_bd_intf_pins infer/M_AXI] [get_bd_intf_pins ps7/S_AXI_HP0]]]} {
        error "DIRECT_HP0_AUDIT_FAIL:$endpoints"
    }
    set physical_ports [physical_port_members]
    set expected_cells [lsort [list /ps7 /axi_gp0_lite /rst_fclk0 /const_zero /const_one /infer]]
    if {[lsort [get_bd_cells]] ne $expected_cells} {error "PLATFORM_CELL_CLOSURE_FAIL"}
    assert_property [get_bd_pins ps7/FCLK_CLK0] CONFIG.FREQ_HZ 50000000
    assert_property [get_bd_pins infer/clk] CONFIG.ASSOCIATED_BUSIF S_AXI:M_AXI
    set clock_net [get_bd_nets -of_objects [get_bd_pins ps7/FCLK_CLK0]]
    foreach pin {ps7/M_AXI_GP0_ACLK ps7/S_AXI_HP0_ACLK axi_gp0_lite/aclk rst_fclk0/slowest_sync_clk infer/clk} {
        if {[get_bd_nets -of_objects [get_bd_pins $pin]] ne $clock_net} {error "CLOCK_DOMAIN_AUDIT_FAIL:$pin"}
    }
    set reset_net [get_bd_nets -of_objects [get_bd_pins rst_fclk0/peripheral_aresetn]]
    foreach pin {axi_gp0_lite/aresetn infer/cold_resetn} {
        if {[get_bd_nets -of_objects [get_bd_pins $pin]] ne $reset_net} {error "RESET_DOMAIN_AUDIT_FAIL:$pin"}
    }
    set control_mappings 0
    foreach seg [get_bd_addr_segs -of_objects [get_bd_addr_spaces ps7/Data]] {
        if {[get_property OFFSET $seg] == 0x43C00000 && [get_property RANGE $seg] == 0x00010000} {
            incr control_mappings
        }
    }
    if {$control_mappings != 1} {error "CONTROL_ADDRESS_AUDIT_FAIL:$control_mappings"}
    set data [dict create version [version -short] part $part requested_part_literal XC7Z020-2CLG400I \
        visibility_parameter $visibility physical_ports $physical_ports \
        interfaces {} scalar_pins {} nets {} addresses {} part_properties {}]
    foreach property [list_property [get_parts $part]] {
        if {[regexp -nocase {temp|grade|speed|package} $property]} {
            dict set data part_properties $property [get_property $property [get_parts $part]]
        }
    }
    foreach pin [get_bd_intf_pins -of_objects [get_bd_cells]] {
        foreach property {MODE CONFIG.PROTOCOL CONFIG.ADDR_WIDTH CONFIG.DATA_WIDTH CONFIG.ID_WIDTH} {
            if {[lsearch -exact [list_property $pin] $property] >= 0} {
                dict set data interfaces $pin $property [get_property $property $pin]
            }
        }
    }
    foreach pin {infer/clk infer/cold_resetn ps7/FCLK_CLK0 rst_fclk0/peripheral_aresetn} {
        set object [get_bd_pins $pin]
        foreach property {TYPE DIR CONFIG.FREQ_HZ CONFIG.ASSOCIATED_BUSIF CONFIG.ASSOCIATED_RESET CONFIG.POLARITY} {
            if {[lsearch -exact [list_property $object] $property] >= 0} {
                dict set data scalar_pins $pin $property [get_property $property $object]
            }
        }
    }
    foreach net [get_bd_nets] {dict set data nets $net [get_bd_pins -of_objects $net]}
    foreach seg [get_bd_addr_segs] {
        dict set data addresses $seg [list OFFSET [get_property OFFSET $seg] RANGE [get_property RANGE $seg]]
    }
    ipcfg::write_evidence [file join $evidence_dir platform_readback.tcldict] $data
    return "AUDIT:OK"
}

proc ::s2b_inference_platform::products {evidence_dir} {
    variable bd_name
    set bd_file [get_files */${bd_name}.bd]
    if {[llength $bd_file] != 1} {error "PRODUCTS_BD_OBJECT_COUNT_FAIL:$bd_file"}
    generate_target all $bd_file
    # 返回值只表示创建信息；由官方 import 副作用导入，再查询唯一文件对象。
    make_wrapper -files $bd_file -top -import
    set wrapper [get_files */${bd_name}_wrapper.v]
    if {[llength $wrapper] != 1} {error "PRODUCTS_WRAPPER_OBJECT_COUNT_FAIL:$wrapper"}
    set_property top ${bd_name}_wrapper [current_fileset]
    update_compile_order -fileset sources_1
    write_bd_tcl [file join $evidence_dir s2b_inference_bd.tcl]
    file copy [get_property NAME $bd_file] [file join $evidence_dir s2b_inference.bd]
    write_hw_platform -fixed [file join $evidence_dir s2b_inference_no_bit.xsa]
    return "PRODUCTS:OK"
}

proc ::s2b_inference_platform::run {repo_root project_dir evidence_dir helper native_log {proof ""} {review ""} {review_sha256 ""}} {
    variable part
    variable bd_name
    variable rtl_sources
    # 必须在无项目的归属明确 Tcl 会话调用，不触碰用户已打开的 GUI 项目。
    if {[current_project -quiet] ne ""} {error "已有打开项目，停止创建"}
    puts [path_preflight $repo_root $project_dir $evidence_dir $helper $native_log $proof $review]
    if {($proof ne "" || $review ne "") && ![regexp {^[0-9a-f]{64}$} $review_sha256]} {
        error "独立审查原件固定SHA-256必需"
    }
    if {$proof eq "" && $review eq "" && $review_sha256 ne ""} {error "不能单独提供审查哈希"}
    if {[llength [get_parts $part]] != 1} {error "精确器件不存在：$part"}
    uplevel #0 [list source -notrace [file join $repo_root vivado/s2b_ps_platform.tcl]]
    if {![llength [info commands ::ipcfg::help]]} {uplevel #0 [list source -notrace $helper]}
    set ::ipcfg::native_log_path $native_log
    set python [ipcfg::python_status]
    if {![string match {PYTHON:OK *} $python]} {error $python}
    puts $python
    puts [ipcfg::python_exec -c {import argparse, hashlib, json, pathlib, re, sys; print("PYTHON_IMPORTS:OK")}]
    set checker [file join $repo_root verification/check_s2b_inference_platform.py]
    puts [ipcfg::python_script $checker --root $repo_root]
    set visibility 0
    if {$proof ne "" || $review ne ""} {
        if {$proof eq "" || $review eq ""} {error "可见性证明和独立审查必须成对提供"}
        set result [ipcfg::python_script $checker --root $repo_root --visibility-proof $proof \
            --review $review --review-sha256 $review_sha256]
        if {$result ne "VISIBILITY_PROFILE:BINDINGS_VERIFIED"} {error "VISIBILITY_BINDING_CHECK_FAIL:$result"}
        set visibility 1
    }
    file mkdir $evidence_dir
    file mkdir $project_dir
    create_project s2b_inference_candidate $project_dir -part $part
    set_property target_language Verilog [current_project]
    foreach relative $rtl_sources {add_files [file join $repo_root $relative]}
    update_compile_order -fileset sources_1
    create_bd_design $bd_name
    puts [construct $evidence_dir $visibility]
    capture $evidence_dir validate {validate_bd_design -force; save_bd_design; set status VALIDATE:OK} {VALIDATE:OK}
    capture $evidence_dir audit [list ::s2b_inference_platform::audit $evidence_dir $visibility] {AUDIT:OK}
    capture $evidence_dir products [list ::s2b_inference_platform::products $evidence_dir] {PRODUCTS:OK}
    return "INFERENCE_PLATFORM:BUILD_CANDIDATE_OK"
}
