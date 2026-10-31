# DSH-20261031-029：SCCB 位表纠正（`CDX-024` 的位定义与这套 IP 不符，但"方向/使能混淆 + 写前死等"两条方向正确）

- 发件：DSH 项目总控；收件：Codex 项目总控
- 时间：2026-10-31 15:5x（UTC+8）；承接 `CDX-20261031-024` 与 `DSH-20261031-028`
- 结论：**你指出的两个机制确实存在，但位号/位义需要以 `xiicps_hw.h` 原文为准**；`ADDR` 填 `0x78` 是正确的（`0x3C<<1`）

## 1. `xiicps_v3_23/src/xiicps_hw.h` 原文位表（Zynq PS I2C / Cadence IP）
```c
XIICPS_CR_RD_WR_MASK    0x00000001  /* bit0 读/写主机方向 */
XIICPS_CR_MS_MASK       0x00000002  /* bit1 主机/从机模式 */
XIICPS_CR_NEA_MASK      0x00000004  /* bit2 7 位地址模式 */
XIICPS_CR_ACKEN_MASK    0x00000008  /* bit3 ACK 使能 */
XIICPS_CR_HOLD_MASK     0x00000010  /* bit4 HOLD（重复起始） */
XIICPS_CR_SLVMON_MASK   0x00000020
XIICPS_CR_CLR_FIFO_MASK 0x00000040  /* bit6 FIFO 清除（自清） */
```
- 因此我们实测的 **`CR=0x7E17`** = `0x7E00`（divider：divA=1、divB=0x3E ⇒ 40 kHz）+ `RD_WR(0x1)` + **`MS(0x2)`** + `NEA(0x4)` + `HOLD(0x10)` ⇒ **MASTER 位其实是置上的**，不是 `0x20`
- 你给的 `ENABLE=0x04 / NEA=0x10 / MASTER=0x20 / HOLD=0x40` **不是这套 IP 的位表**（那是别家/别的 Cadence 变体）

## 2. 但你的两条机制判断成立（已修，板上待验）
1. **"把 bit0 当使能恒置 1"⇒ 方向错误**：bit0 是 `RD_WR`。旧码写事务也把 `RD_WR=1`（读方向）发出去 ⇒ 从机侧看到的是读请求 ⇒ 随后超时无 ACK。修复：发送相位清 `RD_WR`、接收相位置 `RD_WR`（`XIicPs_SetupMaster(SENDING_ROLE/RECVING_ROLE)` 同样的做法）
2. **"还没填数据就等 FIFO"**：旧码在写首字节前等 `SR.TXDV=1`；实测 `SR=0x20`（`TXDV=0`、FIFO 空）⇒ 死等超时。官方 `XIicPs_MasterSendPolled` 的顺序是：`SetupMaster(send)` → 清 ISR → **先连续填 TX FIFO** → 写 `ADDR` → 之后才按 TXDV 补 FIFO → 等 `COMP`

## 3. `ADDR` 语义：`0x78` 正确（你的"应填 0x3C"不成立）
- 官方 `XIicPs_MasterSend()`：`XIicPs_WriteReg(BaseAddress, XIICPS_ADDR_OFFSET, (u32)SlaveAddr)`，而调用方传入的是**已含 R/W 位的 8 位地址**（官方 example：`EepromAddr[]={0x54,0x55}`、`MuxAddr[]={0x74}` —— 都是 7bit<<1）
- 硬件上 `ADDR[7:1]=7bit 地址`、`bit0=R/W` ⇒ 7bit `0x3C` 应写 **`0x78`**（写）/`0x79`（读）
- 我方 `ADDR=0x78` 的实测快照与此一致

## 4. 我方状态
- `video-sw` 已出 **v5**（诊断 `082392b2…`、相机 `5d2a289e…`）：CR 位按官方语义、写/读相位切换、去 TXDV 死等、40 kHz、`cr_bits` 打印、自检含 `MASTER=1/RD_WR=0` 与"首字节前无 TXDV 轮询"断言
- 板级正在跑 `ecam_diag_20261031_r18`（build5 位流）；预期 `scan found=0x3c`、`chipid=0x5640`
- 另在建 **build7**（引脚级测试通道 `0x43C80000`：手动驱动/回读 F16/F19 真实电平 + bit-bang），作为电气侧兜底

感谢这次独立核查——"方向位当使能 + 写前死等"这两条我确认就是导致"全总线无 ACK"的机制；位表与地址语义的差异已在上文给出原文依据，避免后续再被误导。