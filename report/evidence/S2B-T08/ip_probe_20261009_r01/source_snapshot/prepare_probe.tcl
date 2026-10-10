# 只创建隔离配置探测工程，不生成位流或连接实物。
set probe_root {C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition}
set probe_run [file join $probe_root tmp 2B S2B-T08 ip_probe_20261009_r01]
set probe_evidence [file join $probe_root report evidence S2B-T08 ip_probe_20261009_r01]
set probe_helper {C:\Users\22061\.codex\plugins\cache\amd-ross-agentic-ai-assistant\amd-ross-agentic-ai-assistant\2026.9.1\skills\vivado-ip-configurator\lib\ipcfg.tcl}
set probe_log [file join $probe_run .vivado-ai vivado_61503851_b6e150b9.log]
foreach probe_path [list $probe_run $probe_evidence] {
    if {![file isdirectory $probe_path]} {error "已核验目录缺失：$probe_path"}
}
if {![file isfile $probe_helper] || ![file isfile $probe_log]} {error "helper或本次启动日志不存在"}
source -notrace [file join $probe_root vivado s2b_ps_platform.tcl]
puts [::s2b_ps_platform::prepare [file join $probe_run project]]
source -notrace $probe_helper
set ::ipcfg::native_log_path $probe_log
set probe_python [ipcfg::python_status]
puts $probe_python
if {![string match {PYTHON:OK *} $probe_python]} {error $probe_python}
puts [ipcfg::python_exec -c {import argparse, base64, hashlib, json, pathlib, re, sys, typing; print("PYTHON_IMPORTS:OK")}]
puts [ipcfg::write_evidence [file join $probe_evidence startup_preflight.tcldict] [dict create part [get_property PART [current_project]] version [version -short] python $probe_python native_log $probe_log helper $probe_helper]]
puts "PREPARE_PROBE:OK"
