# 2B 最终验收恢复占用通知

2026-10-22（南京时间）。Codex 2B 总控继续 Wong 已授权的阶段2B验收，工作树 `D:\FPGA_Competition\w2b`。

- 恢复前已核实无 `hw_server`、Vivado/XSDB/板测或重型任务，3121无监听；新建本任务 `hw_server` PID `4812`，创建 FILETIME `134371091860065760`，路径 `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe`，监听3121。
- 已只读核对阶段3 `D:\codex-worktrees\dbdf\.codex\STATE.md`：10月21日23:35记录DONE，冻结为v10_read/gray。未认领或修改阶段3文件写权。其昨晚重载后的板上状态须现场读取，不能复用更早2B状态。
- 当前准备停核、按已绑定XSA安全停稳两个VDMA并恢复R04易失2B配置，然后执行重建PS ELF的DDR/cache及黄金单样本。JTAG与COM4由本任务独占；期间不要连接、结束服务或重配板卡。
- 已完成的1000次连续任务、108个ACK闭合黄金样本及R12超时/恢复子范围保留原证据，当前阶段尚未冻结。收尾后另发明确释放/结果通知，不将本通知当作完成或硬件释放。

本记录仅为追加信箱通知，不授予主目录或阶段3写权；主目录Git暂存/提交仍由DSH串行管理。
