# 只读查询实际器件目录；不据此选择实板引脚或时钟约束。
set resolution_dir {D:\FPGA_Competition\report\evidence\S2A-T68\xc7z020_2_ooc_20261008_r01}
set resolution_file [open [file join $resolution_dir target_resolution.txt] {WRONLY CREAT EXCL}]
fconfigure $resolution_file -encoding utf-8 -translation lf
puts $resolution_file "USER_CONFIRMED_DEVICE=XC7Z020-2CLG400I"
puts $resolution_file "VIVADO_VERSION=[version]"
set resolution_candidates [get_parts -quiet xc7z020clg400*]
puts $resolution_file "CANDIDATE_COUNT=[llength $resolution_candidates]"
foreach resolution_part $resolution_candidates {
    puts $resolution_file "BEGIN_PART=[get_property NAME $resolution_part]"
    foreach resolution_property [lsort [list_property $resolution_part]] {
        puts $resolution_file "$resolution_property=[get_property $resolution_property $resolution_part]"
    }
    puts $resolution_file "END_PART"
}
close $resolution_file
puts "TARGET_CATALOG_CANDIDATES=$resolution_candidates"
puts "TARGET_RESOLUTION_PATH=[file join $resolution_dir target_resolution.txt]"
