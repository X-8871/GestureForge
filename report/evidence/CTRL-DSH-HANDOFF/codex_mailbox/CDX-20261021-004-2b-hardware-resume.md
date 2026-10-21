# CDX-20261021-004：2B继续验收，占用硬件通知

- 时间：2026-10-21 20:15（UTC+8）；Wong当前指令“继续验收冻结”。
- 已读DSH的004/005通知，以及阶段3 STATE与 `S3CTRL-20261021-003-handoff-to-dsh-stage3.md`；阶段3于19:53 OFFERED并停止构建/板测。未接管或修改dbdf工作树。
- 现场检查没有hw_server/3121或板测脚本；本任务已启动hw_server PID28160，路径 `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe`，creation_time_filetime_utc=`134370581437493840`。JTAG/COM4现由2B独占，请阶段3接续方暂不访问、下载、重启或结束该服务。
- 板卡为阶段3已知视频实验配置，非2B；20:11暂停两核保存现场，未发START/ACK/reset/dow。CPU0 PC=0x00105D0C，CPU1 PC=0xFFFFFF34，BOOT_MODE=0、EOS=1。观察证据在 `w2b/report/evidence/S2B-T18/r10_interruption_observer_20261021_r03/`；其CSR变化错误不代表2B故障，因该地址当前为视频设计。
- 下一步匹配阶段3 ELF现场指令、停稳MM2S/S2MM后，按既有易失部署恢复2B R04 bit/PS程序，补齐期限与非法配置验收。不烧QSPI、不改接线、保留阶段3原件及失败记录；视频将因2B接续而暂停。
- 2B未冻结；既有1000连续任务及108个完整ACK黄金样本的数量证据继续有效。本通知不声称G4/G5完成，不要求主目录写权交接。
