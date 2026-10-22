# S5-T01 只读 JTAG 探测：只 connect + 列出目标树，不 halt、不写寄存器、不下载、不烧录。
# 用法（Git Bash）: bash /d/codex-worktrees/dbdf/scripts/stage3_t03b/run_xsdb.sh \
#   "D:\\codex-worktrees\\w5\\scripts\\stage5_t01\\jtag_probe.tcl"

puts "S5T01_PROBE_BEGIN"
connect
puts "S5T01_TARGETS_BEGIN"
targets
puts "S5T01_TARGETS_END"
disconnect
puts "S5T01_PROBE_DONE=1"