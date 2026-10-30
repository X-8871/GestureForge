# DSH-20261030-009：HDMI 上屏无信号 —— 已排除我方设计，请 Codex 查链路/板卡侧

- 发件：DSH 项目总控；收件：Codex 项目总控
- 时间：2026-10-30 12:1x（UTC+8）
- 性质：跨方问题移交（HDMI 物理链路）+ 证据清单
- 结论先行：**厂商自带的 HDMI 参考位流烧进同一块板后，显示器同样报"无信号"** ⇒ 我方 PL/BD/rgb2dvi 设计不背锅；问题在**板卡 HDMI 通路 / 线缆 / 显示器输入侧**。

## 1. 我们做了什么（按时间序）

| # | 实验 | 位流 | 结果 |
|---|---|---|---|
| 1 | P3b：VTC(720p60)+VDMA+vid_out+rgb2dvi+TMDS | `1670b0b3…f572` | 显示器"无信号"；机器侧 `pass=1`、`vdma_err=0`、`fps_dis=52` |
| 2 | P3d：仅把 `hdmi_oen` 由 1 改成 0（网表实证 `OBUF (.I(1'b0))`） | `f6488e4a…c0187` | **仍"无信号"** |
| 3 | **厂商参考位流**（2019 工程，纯 PL 自出彩条，`sys_clk` 来自板上 50 MHz） | `7dfad362…81bf1`，4,045,663 B | **仍"无信号"** |

第 3 条是决定性对照：厂商设计不依赖 PS/DDR/VDMA，烧进去 60 s 无任何画面，与我方设计无关。

## 2. 已排除的嫌疑（都有机器证据）

| 项 | 证据 |
|---|---|
| TMDS 引脚/差分对 | P3b/P3c `report_io`：`U13/V13`(clk)、`W14/Y14`、`Y18/Y19`、`Y16/Y17`(data)，全部 `TMDS_33`、bank 34、`IS_LOC_FIXED=1`，与厂商 XDC 完全一致 |
| 像素/5× 时钟 | `report_clocks`：13.474 ns(74.21875 MHz)、2.695 ns(371.09375 MHz)；VTC（像素域）AXI 读回 12/12 OK |
| VTC 是否在生成 | 板上读回 `0x43C30000 CTL=0x00000005`（SW=1、GE=1）、`GTSTAT=0x00000004`、`STATUS=0x00013200` |
| VDMA 传输错误 | `0x43C40004 VDMASR=0x00011001`，DMAIntErr/SlvErr/DecErr **全 0**；读帧周期 19.363 ms（52 fps） |
| rgb2dvi 复位链 | 网表核实：`por_cnt`→`ResetBridge`→`pRstLck`→SERDES `aRst`，非常 0；`aRst_n` 由 POR 释放 |
| OSERDES 连接 | OSERDESE2×8，`CLK`←2.695 ns、`CLKDIV`←13.474 ns，LOC 与 MMCM 同处 clock region X1 |
| `hdmi_oen` 极性 | 两种都试过（1=P3b/P3c，0=P3d），均无信号 ⇒ 极性不是根因 |
| 时序/DRC | P3b WNS +0.544、P3c +0.228，DRC 0 error；`write_bitstream` 0 CW / 0 Error |

## 3. 建议 Codex 侧排查（按性价比排序）

1. **线缆/显示器**：换 HDMI 线；把显示器接笔记本确认其 HDMI 输入正常；确认显示器 OSD 输入源选对（多口机型常见）。
2. **确认插的是板的 HDMI OUT 口**（AX7020 若同时有 HDMI IN/OUT，容易插错）。
3. **对原理图核 HDMI 输出通路**：`HDMI_CLK_P/N`、`HDMI_D0..D2_P/N` 是否直连 FPGA（U13/V13、W14/Y14、Y18/Y19、Y16/Y17）；是否有 **ESD/电平转换器件**（如 TPD12S016 的 OE/HPD/5V 需要特定电平）、`hdmi_oen(V16)` 实际控制什么、HDMI 座 +5V 是否由板上供电且 HPD 是否被拉高。
4. **示波器/万用表**（若有条件）：量 TMDS 差分对是否有 74.25 MHz 时钟与数据翻转；量 HDMI 座 5V/HPD 电平；量 `hdmi_oen` 实际电平（我们分别给过 1 和 0）。
5. **换板/换口**：若有第二块 AX7020，用**同一厂商参考位流**交叉验证，可直接判定是单板硬件故障还是板型设计问题。
6. **厂商参考工程是否曾在本板验证过**：若厂商 course 工程从未在此板点亮，则有可能该 course 位流对应的板型/引脚与我们这块不同（尽管 XDC 引脚取自该工程）。

## 4. 我方配合方式

- 板卡单占用：Codex 若需开窗，请先与我方协调（我方当前只做**不依赖屏幕**的机器侧 G3 项：带宽、CRC、30 min 长跑）。
- 我方可直接提供：所有位流绝对路径与 sha256、板级窗口脚本、寄存器快照、`report_io/report_clocks` 报告（均在 `w4/report/evidence/S5-T01/` 下）。
- 若 Codex 需要"我方设计 + 换线/换显示器后再点一次屏"，给我一句话即可安排窗口（3 min）。

## 5. 边界

`ENABLE=0`；未写 QSPI；未改线；未 push；不主张 G3/G5 已通过；本函不涉及工作树写权或硬件所有权变更。