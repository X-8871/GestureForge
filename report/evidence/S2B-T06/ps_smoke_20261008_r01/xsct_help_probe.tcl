# 只读取本机帮助；不加载用户ini、不连接目标、不枚举或改变板卡。
puts [version]
foreach command {connect targets stop rst dow con disconnect mrd} {
    puts [format {=== HELP %s ===} $command]
    puts [help $command]
}
puts {XSCT_HELP_ONLY_OK hardware_execution=NOT_RUN}
exit
