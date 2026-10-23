# w4让出给DSH

Wong要求直接结束并交DSH。Codex仅完成本次保存提交，此后停止写入。状态OFFERED，下一接手方DSH 项目总控；尚未代替DSH执行CLAIMED。4D及阶段4未完成，未占用硬件。

当前小程序r08仿真和修复1局部G2独审PASS，完整416帧/系统集成/板测未执行。系统G0五项阻断、地址契约草案和OOC保持时序违例详见STATE，不能当作已闭合。最新停止指令下未运行新整帧包装检查。

交接record与内容一起提交，因此base_commit为保存前基线，不能直接当最终HEAD。DSH接管时：

1. 只读核对实际分支/HEAD、git rev-parse --git-path index.lock、重型进程、未跟踪12产物及local_outputs.json。
2. 在内存读取handoff_record.json，把base_commit替换为git rev-parse HEAD返回值（不改原record）。
3. 将该JSON作为--record参数调用主树verification/handoff_check.py --worktree D:\codex-worktrees\w4 --claim --json。只有核验通过后DSH才能CLAIMED并继续；未替换时a项因提交落后一条失败属绑定设计，不是授权通过。
4. 正式认领后由DSH更新本树STATE。主STATE、其他树及硬件另按各自归属办理。

真实源码/仿真证据入口：report/evidence/S4-B/s4b_pl_frame_g2_20261023_r02/、s4b_pl_frame_20261023_r08/；独审报告与日志：report/evidence/S4-CTRL/s4_pl_frame_closure_20261023_r01/。原失败证据、tmp恢复依赖及12份ELF/map均保留，不删除或覆盖。
