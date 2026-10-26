if {[llength $argv] != 2} {
    puts stderr "用法：probe_clocks.tcl <routed.dcp> <output_dir>"
    exit 2
}

set dcp [file normalize [lindex $argv 0]]
set out [file normalize [lindex $argv 1]]
if {![file isfile $dcp]} {
    puts stderr "DCP 文件不存在：$dcp"
    exit 2
}
file mkdir $out

proc safe_property {object property} {
    if {[catch {get_property $property $object} value]} {
        return "UNAVAILABLE"
    }
    return $value
}

puts "DCP=$dcp"
puts "DCP_SHA256_EXPECTED=17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728"
open_checkpoint $dcp

set clocks [get_clocks -quiet *]
puts "CLOCK_COUNT=[llength $clocks]"
foreach clock $clocks {
    puts "CLOCK=$clock"
    foreach property {IS_GENERATED PERIOD WAVEFORM SOURCE_PINS MASTER_CLOCK} {
        puts "  $property=[safe_property $clock $property]"
    }
}

set report_path [file join $out clocks.rpt]
report_clocks -file $report_path
puts "REPORT_CLOCKS=$report_path"

foreach pattern [list {*axi_dynclk_0*PXL_CLK_O*} {*rgb2dvi_0*PixelClk*} {*rgb2dvi_0*SerialClk*}] {
    set pins [get_pins -hier -quiet -filter "NAME =~ $pattern"]
    puts "PIN_PATTERN=$pattern COUNT=[llength $pins]"
    foreach pin $pins {
        set nets [get_nets -quiet -of_objects $pin]
        set pin_clocks [get_clocks -quiet -of_objects $pin]
        puts "PIN=$pin CLOCKS=$pin_clocks NETS=$nets"
        foreach net $nets {
            set connected [get_pins -quiet -of_objects $net]
            puts "  NET=$net CONNECTED_PINS=$connected"
        }
    }
}

set ports [get_ports -quiet *axi_dynclk_0_PXL_CLK_O*]
puts "PXL_CLK_PORTS=$ports"
foreach port $ports {
    set nets [get_nets -quiet -of_objects $port]
    puts "PORT=$port NETS=$nets CLOCKS=[get_clocks -quiet -of_objects $port]"
}

close_design
puts "PROBE_RESULT=COMPLETE_READ_ONLY"
