# R02 最终增量复审：VDMA停止与map清理

- 结论：`PASS`（仅静态复核两处修复；未运行脚本或操作硬件）
- 审查对象：`D:\FPGA_Competition\w2b\tmp\2B\restore_2b_after_stage3_20261021_r02.py`
- SHA-256：`12F18E2B3FAB82A7437F25746BD2F5260EBF0FE3689A4D1342F7BFA7DEF3919B`

## 已关闭项

- 第113行在每个VDMA控制寄存器写回前要求 RESET bit2 为0；满足时写入 `before[0] & ~1`，RUNSTOP清零且RESET仍为0。若观察到RESET仍置位，脚本拒绝写回，不会以读改写重置通道。
- `clear_video_map()` 统一用于主路径和异常清理。它调用SDK `unloadhw()` 后核验 `_designtable` 为空、所有 `_memmap_ctxs` 均为空；仅核验通过后才清除 `video_map_attempted` 并记录 `UNLOADED_AND_SDK_MAP_EMPTY`。失败会留下attempted状态并抛错，顶层finally纳入 `cleanup_errors`，退出码将为2。
- finally现先执行视频map清理，再关闭 `controller`，然后清理CSR map、断开本次session及dispose XSDB。因此异常路径的 `controller.call` 仍可写日志并执行卸载，不再先关闭控制器日志而阻断清理。
- 本机SDK `__clear_memmap` 按已加载的target context移除map上下文；SDK `unloadhw` 在最后一个target移除后关闭设计并移除设计表项，与新增空表断言一致。

R02其余视频XSA哈希绑定、HWH窗口限定、SDK实际map范围/flags核验沿用上一份增量回执中的审查结论。此PASS仅针对静态审查SHA，不证明恢复运行成功、板上验收或G3/G4通过。
