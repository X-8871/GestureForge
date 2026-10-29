# P2c 上板结果（2026-10-29 18:36–18:41）：PL 预处理 → packer → AXI DMA → **张量 CRC 与离线一致**

- RunId：`s4d_p2c_board_20261029_r01`；窗口 18:36:53 → 18:41:30（UTC+8，4.6 min）
- 位流：P2c r02 `022f48fb…d52ca4`（前缀 `022F48FB`）；应用 ELF：`56c6967b…ac93100`；fixture RAW `ce37aa77…`
- **结论：`P2C_TENSOR_CRC_MATCH`** —— 板上 PL 预处理产出的 519,168 B INT8 CHW 张量，CRC-32 = `0x5B183B50`，
  与离线 C 预处理同 fixture 的 golden 完全一致。这是 C 项（PL 预处理上板）**数据面**的第一次正证。

## 1. 板上关键读数（原始 UART，全文见 `W2_uart.log` / `W2_uart_output.txt`）

| 项 | 值 |
|---|---|
| 身份 | `dma_base=0x43C20000`、`preproc_base=0x43C10000`、`da=0x10000000`、`len=519168`、`crc_expect=0x5B183B50` |
| SLCR 前置闸 | `lvl_shftr=0x0F`、`fpga_rst_ctrl=0x00`、`fpga0_clk=0x00600600` |
| DMA 预检 | `dmasr=0x00000001`（halted=1、无错误、SGIncld=0）——与 IP 名义值一致 |
| arm | `da_rb=0x10000000`、`cr=0x00010002→0x10010003`（RS 置位并回读） |
| **长度**（B1 关闭验证） | 写 `519168`，回读 `len_reg=0x0007EC00` ⇒ **23 bit 生效、无 14-bit 截断** |
| preproc 身份 | `id=0x53344450`、`bytes=519168`、`geom=0x013801A0`、`geom2=0x00340000` |
| DMA 完成 | `dmasr=0x00001002`（IOC=1、Idle=1）、`length_reg=519168`、`pre_status=0x2`、`pre_done_ms=11` |
| **CRC** | **`PCB DMA tensor_crc32=0x5B183B50 expected=0x5B183B50 pass=1`** |
| 汇总 | `P2CDMA RESULT exit=0, preproc_rc=0, dma_rc=0, halt_rc=0, crc_pass=1` |

## 2. 字节级交叉验证（不只依赖 CRC）

| 位置 | 板上（本次重读） | 离线 golden（`D:\wb-out-r3\p0_rerun\golden\golden_416x416_int8_chw.bin`，sha256 `6c03f2af…`） |
|---|---|---|
| 首 16 B | `40404040…4040` | `40404040…4040` ✅ |
| 末 8 B（`0x1007EBF8`） | `4040404040404040` | `4040404040404040` ✅ |

> 更正一处记录：首次抽样脚本把"末 8 B"读在 `0x1007EFF8`（张量末尾之后 0x3F8），得到 `fffffffbffffffff`，
> 那是**张量之外的区域**，不构成不符。已用正确地址 `0x1007EBF8` 重读并比对（`W6_tensor_*`）。

## 3. 本结果证明 / 不证明什么

**证明（本窗口范围内）**：
- P2c 位流的 preproc `M_AXIS → packer(8b→64b) → AXI DMA S2MM → HP0 → 0x10000000` 通路可用；
- `SRC_BASE=0x12000000` 生效（预处理读的是预载的 fixture RAW）；
- AXI DMA 的 23-bit 长度足够（519,168 B 一帧完整搬完，无截断、无 DMA 错误）；
- PL 预处理结果与离线 C 实现在**字节级**一致（CRC + 首尾抽样）。

**不证明**：
- 不是摄像头实拍链（fixture 为生成样本）；不是合并部署（无 VDMA/HDMI/叠加）；
- 不是 G3/G4/G5；位流与应用 ELF 均为**候选/未冻结**；`ENABLE=0` 未变；
- 单帧一次成功 ≠ 长时间稳定性（A 项另论）；
- 计时口径：`pre_done_ms=11` 是应用自报值，按已定因的 `XTime_GetTime` 1/4 缺陷，真实耗时约 **44 ms/帧**
  （仍远快于 2B 推理的 ~47 s/帧）。

## 4. 窗口收尾

- 候选区恢复：`W5_final_restore` PASS（`W4_dump`/`W4_restored` 已落盘，diff 见该 JSON）；记录区清零 PASS。
- 收窗：`P4_teardown` PASS（3121 释放、无残留进程）。
- 未写 QSPI、未改线、未 push、未用 `-force`。