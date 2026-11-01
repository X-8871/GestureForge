# R02 增量独立 G2 审查：视频 VDMA map

- 结论：`CHANGES_REQUIRED`
- 审查对象：`D:\FPGA_Competition\w2b\tmp\2B\restore_2b_after_stage3_20261021_r02.py`
- SHA-256：`6602D485133CD12A65A2271A355470F2E14E0A06746965622CE00D2F2059FDA7`
- 仅审查R02新增视频映射/清理及其可达的VDMA停止写入；不重做原R01审查。不运行脚本、不连接硬件。

## 阻断项

1. **CR读改写可能意外置位VDMA RESET。** 第103–104行将完整 CR 读回值仅清除 bit0（RUNSTOP）后写回。本机 AXI VDMA `xaxivdma_hw.h` 第155行定义 bit2（`0x4`）为 RESET。若当前 CR 读回 bit2 为1，此写入会再次写入 RESET=1；这超出脚本声明的“仅停 RUNSTOP”，会触发通道复位。R01 的写入因SDK memory map拦截而未执行，R02加映射后此写入路径已经可达。

   **关闭条件：** 写入前若 `before[0] & 0x4` 非零则拒绝操作并保存失败证据；否则只清 RUNSTOP，并确保写入值的 RESET 位为0。不得将复位当作停止通道的副作用。

2. **视频映射卸载没有实际空表后置条件。** 第115–118行在 `unloadhw()` 返回后直接把 `video_map_attempted` 设为False并记录 `UNLOADED`，没有验证SDK的 `_designtable` 和 `_memmap_ctxs` 已清空；之后第119行就执行 system reset。异常清理第135行也只调用 `unloadhw()`，没有记录实际映射清除结果。SDK实现会依据当前目标上下文清理设计映射，但该调用没有结果值可证明清理完成；若目标/上下文不匹配而未实际清除，脚本仍会继续复位，且绕过finally重试。

   **关闭条件：** 正常卸载后核验本次硬件设计及两个VDMA窗口已从该通道/上下文移除，核验通过后才允许 system reset；finally路径也记录卸载尝试及清理后SDK映射表状态，清理失败影响退出码。

## 已核查的R02映射语义

- 固定阶段3 XSA SHA 与用户提供的 `b9a565...addf17` 一致；本机读取该XSA唯一 HWH，两个MEMRANGE为 `axi_vdma_0: 0x43000000–0x4300FFFF`、`axi_vdma_1: 0x43010000–0x4301FFFF`，均为 REGISTER。
- 本机 Vitis 2026.1 `xsdb/target.py` 文档及实现确认 `loadhw(mem_ranges=...)` 限制映射范围外地址；代码只传这两个64-KiB窗口，随后核对SDK实际范围/type/flags，要求恰好两项且flags=3。该映射边界与权限检查符合目的。
- `unloadhw()` 在SDK源码中按当前 target/channel 上下文移除 `loadhw` 记录的map；R02的正常路径位于CSR-only 2B map登记及system reset之前，顺序合理，但仍须补充上述实际清理后置条件。
- VDMA寄存器地址和CR/SR位定义由本机XSA HWH及官方驱动头文件支持；无其他阶段3外设读写新增路径。

未执行任何硬件操作；本回执仅覆盖SHA所列静态源码，不代表板上恢复结果或验收通过。
