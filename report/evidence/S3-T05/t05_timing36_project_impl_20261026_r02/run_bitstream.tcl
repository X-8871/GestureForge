set project_file {D:\codex-worktrees\dbdf\tmp\3\S3-T05\t05_timing36_project_impl_20261026_r02\project\ov5640_single.xpr}
set bit_file {D:\codex-worktrees\dbdf\tmp\3\S3-T05\t05_timing36_project_impl_20261026_r02\project\ov5640_single.runs\impl_1\design_1_wrapper.bit}

if {![file isfile $project_file]} {error "PROJECT_FILE_MISSING=$project_file"}
open_project $project_file
set impl_run [get_runs impl_1]
set prior_status [get_property STATUS $impl_run]
puts "IMPLEMENTATION_STATUS_BEFORE_BITGEN=$prior_status"
if {[string first "route_design Complete" $prior_status] < 0} {
    error "ROUTED_IMPLEMENTATION_NOT_READY_FOR_BITGEN"
}
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
set final_status [get_property STATUS $impl_run]
set final_progress [get_property PROGRESS $impl_run]
puts "IMPLEMENTATION_STATUS_AFTER_BITGEN=$final_status"
puts "IMPLEMENTATION_PROGRESS_AFTER_BITGEN=$final_progress"
puts "BITSTREAM_PATH=$bit_file"
if {$final_progress ne "100%" || [string first "write_bitstream Complete" $final_status] < 0} {
    error "BITSTREAM_GENERATION_NOT_COMPLETE"
}
if {![file isfile $bit_file] || [file size $bit_file] < 1} {
    error "BITSTREAM_FILE_MISSING_OR_EMPTY"
}
puts "BITSTREAM_SIZE_BYTES=[file size $bit_file]"
puts "BITSTREAM_GENERATION_RESULT=PASS_NOT_PROGRAMMED"
close_project
