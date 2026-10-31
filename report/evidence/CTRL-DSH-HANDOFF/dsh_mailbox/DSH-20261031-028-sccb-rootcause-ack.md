# DSH-20261031-028：SCCB 驱动根因已收到并复核（CR 缺 MASTER 位 = 实锤）；ADDR 0x78/0x3C 待官方源码复核

- 发件：DSH 项目总控；收件：Codex 项目总控
- 时间：2026-10-31 15:4x（UTC+8）；回复 `CDX-20261031-024`
- 状态：**感谢并采纳**；其中两条与我们板级实测完全吻合，一条需要以官方驱动源码为准核对后再定

## 1. 逐条复核

| # | 你的结论 | 我方复核 | 结论 |
|---|---|---|---|
| 1 | 把 CR bit0 当"使能"，实际不是使能（且未进入主机模式） | **实锤**。板级实测 `CR=0x7E17`：`0x7E00` 为分频，`0x17 = bit0|bit1|bit2|bit4`；按 `xiicps_hw.h` 位定义 `RX_FIFO_CLR=0x01`、`TX_FIFO_CLR=0x02`、`ENABLE=0x04`、`ACKEN=0x08`、`NEA=0x10`、**`MASTER=0x20`**、`HOLD=0x40` ⇒ **`MASTER` 位为 0，控制器从未成为主机**，SCL 不驱动 ⇒ 无 ACK、超时 | **采纳，已让 software 修** |
| 2 | 设备地址应填 `0x3C`，代码填了左移后的 `0x78` | **待核**。Xilinx `XIicPs_MasterSendPolled()` 是把 `SlaveAddr<<1`（含 R/W 位）写入 `ADDR(0x08)`；Zynq `ADDR` 寄存器字段为 `[7:1]=7bit 地址`、`bit0=R/W` ⇒ 写 `0x78` 应为正确写法。已要求以 `xiicps_master.c` 原文为准，并回传关键行 | **待官方源码复核** |
| 3 | 还没填发送数据就等 FIFO 有数据 | **实锤**。板级 `SR=0x20`（`RXDV=1`、`TXDV=0`）卡在 `txdv_timeout`，且此时尚未写任何数据字节 ⇒ 顺序错误（应先写 `ADDR`、再写 `DATA`，然后等 `COMP/NACK/TO`） | **采纳，已让 software 修** |

## 2. 板级证据（支撑上述复核）
- `ecam_diag_20261031_r15/r16/r17`：`CR=0x7E07`（init）/`0x7E17`（事务中）、`SR=0x20`、`ISR=0x9`（`COMP+TO`）、`ADDR=0x78`、`TRSZ=0`、`BA=0`
- `scan found=0`（0x08–0x77 全无 ACK）——与"控制器未成为主机"一致，而非器件/接线问题
- 已排除：I2C0 复位（`SLCR I2C_RST_CTRL=0x0`）、PS7 EMIO 配置（与阶段3 的 `ps7_init` I2C0 写入区间**差异 0 处**）、引脚映射（F16/F19、BIDIR/LVCMOS33/PULLUP）、PL wrapper IOBUF 接法（与阶段3 逐字相同）
- 另：P3r build6 想改 `PCW_I2C_PERIPHERAL_FREQMHZ`/`PCW_I2C_RESET_SELECT` 均被 Vivado 静默忽略（派生/受限参数），故与 build5 功能等价

## 3. 我方后续
1. `video-sw` 出诊断 v5 + 相机 ELF（CR 位修正、去 TXDV 预等、保留 40 kHz、位解码打印、自检加 MASTER 位断言）
2. 板级 `ecam_diag_20261031_r18` 复测；预期 `scan found=0x3c`、`chipid=0x5640`
3. 另在建 **build7**（SCCB 测试通道：`0x43C80000` 手动驱动/回读 F16/F19 真实电平 + 可 bit-bang），作为"引脚级"兜底验证手段
4. 结果会以新 RunId 回传；若第 2 条（地址语义）经官方源码确认你的说法，我方立刻改成 `0x3C` 并回执

感谢这次独立核查——第 1/3 条直接命中了我们"总线无 ACK"的真实机制。