# ERRATUM：r01 位流的 AXI DMA LENGTH 只有 14 bit ⇒ **功能不可用**（不要上板当 P2c 用）

- RunId：`pl_v2_p2c_dma_bitstream_20261029_r01`（本目录）
- 记录：2026-10-29 16:1x（UTC+8），独立复审 rev-s5 发现，lead 复核确认
- 性质：**本目录的位流 `s4d_p2c.bit`（sha256 `0c8ec476…e8352f`）在功能上不可用于目标用途**。
  构建、DRC、时序全部通过，但 DMA 传输长度被硬件截断，`tensor_crc32` 目标不可达。

## 事实

- 本构建的 AXI DMA 实例使用默认 `c_sg_length_width = 14`：
  - XCI：`out/proj/s4d_p2c.srcs/sources_1/bd/s4d_p2c/ip/s4d_p2c_axi_dma_0_0/s4d_p2c_axi_dma_0_0.xci`
    → `"c_sg_length_width": [ { "value": "14" } ]`
  - 生成 VHDL：`C_SG_LENGTH_WIDTH => 14`；`sim_netlist.v`：`wire [13:0] s2mm_length`
- 后果：应用写 `S2MM_LENGTH = 0x7EC00 (519,168)` 实际生效 `0x2C00 (11,264)` ⇒ S2MM 提前结束、
  置 `DMAIntErr` 并 halt，剩余 507,904 B 不写 DDR ⇒ `tensor_crc32=0x5B183B50` 不可达。
- 因此 r01 的"补齐 AXIS→DMA 消费者"在**结构上**成立（连接、地址、位宽转换、时序均已验证），
  但**功能上**不能完成一帧完整传输。

## 处置

1. 本目录保留不动（失败证据不删），**不得**作为 P2c 位流引用；`README.md` 的"BUILD_ONLY"不等于"可用"。
2. 修复版：`bd_p2c.tcl` 增加 `CONFIG.c_sg_length_width {23}`，重建为 **r02**
   （`D:\tmp\lead\p2c_20261029_r02\`，证据另立 RunId `pl_v2_p2c_dma_bitstream_20261029_r02`）。
3. 应用侧必须加自检：写 `S2MM_LENGTH` 后**回读**，必须等于 519168，否则停止（已转达 stage4-lead）。
4. 新增教训：AXI DMA 在非 SG 模式下的**有效长度位宽来自 `c_sg_length_width`，不是 32 bit**；
   凡 "长度 > 16 KiB" 的 DMA 用法，必须在 XCI/生成物里核对 `s2mm_length` 位宽，不能只看 validate 通过。

## 边界

未上板；未写 QSPI；`ENABLE=0`；不主张 G3/G4/G5。r02 的位流身份、时序、资源以 r02 证据目录为准。