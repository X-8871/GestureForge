# 历史运行评估：R06 首个 AXI 响应元数据失败（FAIL）

本Run绑定源码基线 `2bd977a3d85fc405eaff3bbf3869cf2751d99776` 及本目录 `preflight/source_snapshot/` 内的七份 SystemVerilog 快照、`source_snapshot/` 内的两份监督器快照。原 `result.json` 与 `delivery_manifest.json` 未改写，结果为 `FAIL`。

CASE_ID=1801的无时钟沿epoch注入通过。运行随后在 cycle 5877、stage=`late_exokay_r_after_first_error`、directed=140、random=128、integration=25 失败：状态为6、epoch为1，CSR `0x074` 期望`0x11`而实际`0x10`。对应测试先观察到CORE错误，再接收匹配的EXOKAY R响应；旧RTL只在首个整体故障分支写入低三位，因此晚到EXOKAY置协议bit4但没有记录首个AXI响应`01`。这是真实RTL语义缺陷，测试期望符合本Run所绑定的接口字段定义。

compile、elaborate、simulation原生进程退出码均为0且Job清理记录通过，但驱动从CSR断言失败判定整体FAIL；原生退出0不代表矩阵通过。真实WDB和`xsim.jou`已从对应终态tmp目录复制为`failure_waveform.wdb`与`xsim_native.jou`，本评估未解析波形。未执行板卡验证；本Run不代表RTL矩阵通过或阶段验收。
