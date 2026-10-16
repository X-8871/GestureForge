# 历史运行评估：R05 epoch force 跨时钟失败（FAIL）

本Run绑定源码基线 `2bd977a3d85fc405eaff3bbf3869cf2751d99776` 及本目录 `preflight/source_snapshot/` 内的七份 SystemVerilog 快照、`source_snapshot/` 内的两份监督器快照。原 `result.json` 与 `delivery_manifest.json` 未改写，结果为 `FAIL`。

原生日志在 cycle 3308、directed=130、random=128、integration=0、CASE_ID=1801 终止。最大epoch注入后 `q/d.epoch=ffffffffffffffff` 且状态为IDLE；Fatal文字被XSim损坏。结合当时TB刺激顺序，force 跨过一个手动时钟沿，而TB独立 `phase` 每沿递增；XSim对packed状态成员的force使DUT相位更新受阻，随后固定ERROR监视槽断言失败。该次失败由测试夹具时序触发，未完成公开MAX CSR读回及后续矩阵。

compile、elaborate、simulation原生进程退出码均为0且Job清理记录通过，但驱动从Fatal日志判定整体FAIL；原生退出0不代表矩阵通过。真实WDB和`xsim.jou`已从对应终态tmp目录复制为`failure_waveform.wdb`与`xsim_native.jou`，本评估未解析波形。未执行板卡验证；本Run不代表RTL矩阵通过或阶段验收。
