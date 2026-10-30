# P3g 构建报告（TMDS 引脚勘误：N18 / V20 / T20 / N20）

| 项 | 值 |
|---|---|
| 阶段 / 任务 | **阶段5（HDMI 显示链）** / **S5-T01**（编号口径 2026-10-30 Wong 决定 A） |
| RunId | **s5_p3g_build_20261030_r01** |
| 日期 | 2026-10-30（UTC+8） |
| 工具 / 器件 | Vivado v2026.1 / `xc7z020clg400-2` |
| 工程 / BD / 顶层 | `s4d_p3g_r01` / `s4d_p3g`（= P3b 拓扑） / `top_p3g` |
| 目的 | **引脚勘误版**：修正 TMDS 输出球位，验证"黑屏 = 引脚接错" |
| 流程 | synth → opt/place/route → write_bitstream → XSA |
| 基线 | **P3b**（未采用 P3c 的 100 MHz、未采用 P3f 的协议转换器） |

---

## 1. 结论

**构建成功、位流与 XSA 已出、时序达标、无引脚冲突/DRC error。**
**本版只有 4 行 PACKAGE_PIN 与 P3b 不同**，其余（BD / 顶层 / rgb2dvi / 时钟 / `c_num_fstores=2`）与 P3b 完全一致。

- **WNS = +0.052 ns，WHS = +0.028 ns，TNS = THS = 0.000**（52,248 端点，0 失败）→ 门槛通过
- LUT **25,948（48.77%）**、FF 14,828（13.94%）、BRAM 36.5、DSP 158、MMCM 1、BUFG 5、OSERDESE2 8、Bonded IOB **9**
- DRC **427 条、0 error**；无 `NSTD-1` / `UCIO-1`
- **8 个 TMDS 球位 + `hdmi_oen` 已用 `report_io` 实测**（含工具推断出的 `_n` 球位），全部落在**合法差分对**上
- 位流 `s4d_p3g_r01.bit` 4,045,762 B，sha256 `221e9923…39719b2d`

---

## 2. ★ 勘误说明（本报告最重要的一节）

> **P3a / P3b / P3c / P3d / P3e / P3f 的 `p3b_tmds.xdc` 引脚取自 `course_s1` 工程，
> 与本实板不符（实板为 N18 / V20 / T20 / N20），已由"10-22 亮屏基线"实证。**

| 信号 | 10-22 亮屏设计（实证） | 本版 P3g | 旧（错，P3b 及之前） | 旧引脚实际 SITE |
|---|---|---|---|---|
| `TMDS_clk_p` | **N18** | **N18** | U13 | `IO_L3P_T0_DQS_PUDC_B_34` ← **PUDC_B 专用脚** |
| `TMDS_data_p[0]` | **V20** | **V20** | W14 | `IO_L8P_T1_34` |
| `TMDS_data_p[1]` | **T20** | **T20** | Y18 | `IO_L17P_T2_34` |
| `TMDS_data_p[2]` | **N20** | **N20** | Y16 | `IO_L7P_T1_34` |
| `hdmi_oen` | V16 LVCMOS33 | V16（不变） | V16 | `IO_L18P_T2_34` |

**权威依据（已核对，非转述）**：
`D:\codex-worktrees\dbdf\tmp\3\S3-T05\t05_timing36_project_impl_20261026_r02\vendor_src\src\constraints\hdmi_out.xdc`
（sha256 `71EDC7805065612A21DF7D450B5AE04FAB1E14FCCC68A9BB6F5B90812CF37F0C`；与同目录 `_r01` 副本**逐字节一致**）。
该套设计 2026-10-22 实拍有画面、今日 12:24 板上实测出**灰度条**。

**为什么可以断定不是"电气/Bank 电压"问题**：旧引脚与旧引脚实测**同在 bank 34、同 VCCO 3.3 V（`FP_3.3_50`）**、
IOSTANDARD 同为 `TMDS_33` —— 即"电气合法但**物理连接不对**"。且旧 `U13` 是
`IO_L3P_T0_DQS_PUDC_B_34`（**PUDC_B 配置专用脚**），把 TMDS 时钟放这里本身就强烈提示
那份 `hdmi_out_test.xdc` 属于**另一个工程/板型**（很可能是 HDMI IN 或另一版底板）。

**口径（2026-10-30 Wong/Lead 定稿）**：本板 HDMI 通路已由厂商外部基线证明可用
（10-22 实拍 + 今日 12:4x 复亮）⇒ 硬件/线缆/显示器正常，问题一直在**我们新设计的视频输出实现差异**。
`hdmi_oen`/V16 经图纸（p2/p12/p13）与手册（p35–37）确认**与 HDMI 无实际连接** ⇒ oen 方向（P3d/P3e）已排除、不再作为候选。

---

## 3. 与 P3b 的唯一差异

`p3g_tmds.xdc` 中 4 行 `PACKAGE_PIN`：

```
set_property PACKAGE_PIN N18 [get_ports TMDS_clk_p]        # 原 U13
set_property PACKAGE_PIN V20 [get_ports {TMDS_data_p[0]}]  # 原 W14
set_property PACKAGE_PIN T20 [get_ports {TMDS_data_p[1]}]  # 原 Y18
set_property PACKAGE_PIN N20 [get_ports {TMDS_data_p[2]}]  # 原 Y16
```

保持不变：`_n` 端只给 `IOSTANDARD TMDS_33`（球位由 P 端推断）、`hdmi_oen=V16/LVCMOS33`、
时钟组约束、全部 BD/顶层/rgb2dvi/时钟配置。`top_p3g.v` 与 `top_p3b.v` 仅差模块名与 wrapper 实例名（逻辑 0 改动）。

---

## 4. `report_io` 实测：8 个 TMDS 球位（`out\io_route.rpt`）

| 端口 | PACKAGE_PIN | 实际 SITE | IOSTANDARD | Bank / VCCO | 差分对合法 |
|---|---|---|---|---|---|
| `TMDS_clk_p` | **N18** | `IO_L13P_T2_MRCC_34` | TMDS_33 | 34 / FP_3.3_50 | ✔ |
| `TMDS_clk_n`（推断） | **P19** | `IO_L13N_T2_MRCC_34` | TMDS_33 | 34 / 3.3 V | ✔ 与 L13P 配对 |
| `TMDS_data_p[0]` | **V20** | `IO_L16P_T2_34` | TMDS_33 | 34 / 3.3 V | ✔ |
| `TMDS_data_n[0]`（推断） | **W20** | `IO_L16N_T2_34` | TMDS_33 | 34 | ✔ 与 L16P 配对 |
| `TMDS_data_p[1]` | **T20** | `IO_L15P_T2_DQS_34` | TMDS_33 | 34 | ✔ |
| `TMDS_data_n[1]`（推断） | **U20** | `IO_L15N_T2_DQS_34` | TMDS_33 | 34 | ✔ 与 L15P 配对 |
| `TMDS_data_p[2]` | **N20** | `IO_L14P_T2_SRCC_34` | TMDS_33 | 34 | ✔ |
| `TMDS_data_n[2]`（推断） | **P20** | `IO_L14N_T2_SRCC_34` | TMDS_33 | 34 | ✔ 与 L14P 配对 |
| `hdmi_oen` | **V16** | `IO_L18P_T2_34` | LVCMOS33（12 mA / SLOW） | 34 | — |

全部 `FIXED`（已按 XDC 落定），**P/N 均为同一 IOB 的合法差分对**（L13/L14/L15/L16）。
时钟输出落在 **MRCC**（`IO_L13P_T2_MRCC_34`）——与 TMDS 时钟用途相符。

---

## 5. 时序

| 指标 | **P3g** | P3b | 说明 |
|---|---|---|---|
| **WNS** | **+0.052 ns** | +0.544 ns | 引脚位置改变后 OSERDES/时钟资源布局随变（时钟输出到 MRCC L13P，数据在 L14/L15/L16），关键路径随之变化；**仍为正但余量仅 52 ps** |
| **WHS** | **+0.028 ns** | +0.022 ns | 略好 |
| TNS / THS | 0.000 / 0.000 | 0 / 0 | 0 失败端点 |
| WPWS / TPWS | 1.102 / 0.000 | 1.102 / 0.000 | 无脉冲宽度违例 |
| 端点总数 | 52,248 | 52,363 | −115 |

四域时钟（`out\clocks_route.rpt`）：`clk_fpga_0` 20.000 / `clk_fpga_1` 10.000 /
`clk_out1_s4d_p3g_clk_wiz_0_0` **13.474 ns（74.21875 MHz）** / `clk_out2_s4d_p3g_clk_wiz_0_0` **2.695 ns（371.09375 MHz = 5×）**。

> ⚠️ WNS 只剩 **+52 ps**：这不是错误，但余量很薄。若后续要在此引脚方案上叠加逻辑，
> 需要先看这 52 ps 的路径（大概率在 OSERDES/OBUF 与像素域之间）。**P3g 本身不需要改**。

---

## 6. 资源

| 资源 | P3b | **P3g** | 变化 |
|---|---|---|---|
| LUT | 25,967 (48.81%) | **25,948 (48.77%)** | −19 |
| FF | 14,892 (14.00%) | **14,828 (13.94%)** | −64 |
| BRAM | 36.5 (26.07%) | **36.5 (26.07%)** | 0 |
| DSP | 158 (71.82%) | **158 (71.82%)** | 0 |
| MMCM / BUFG / OSERDESE2 / Bonded IOB | 1 / 5 / 8 / 9 | **1 / 5 / 8 / 9** | 0 |

（LUT/FF 微降属布线/优化噪声级别，不是功能改动）

---

## 7. DRC / 日志

`out\drc_route.rpt`：**427 条、0 error**
→ `DPIP-1` 128、`DPOP-1` 146、`DPOP-2` 148、`DPREG-4` 2（DSP 流水线建议）、`REQP-165` 1 / `REQP-181` 2（BRAM writefirst）。
**无 `NSTD-1` / `UCIO-1`**（9 个端口全部有真实引脚约束）。

构建日志：**0 ERROR / 6 CRITICAL WARNING（全部为已知的 `Vivado 12-4739` 时钟组读取顺序）/ 117 WARNING**（IP 可选端口未连接等良性）。
`write_bitstream completed successfully`，无 Critical Warning / 无 Error。

---

## 8. 位流 / XSA

| 文件 | 字节数 | SHA-256 |
|---|---|---|
| `out\s4d_p3g_r01.bit` | **4,045,762** | `221e99235ef87286daee7fdfd0fffdb3a2a55506735660c8f5e81faa39719b2d` |
| `out\s4d_p3g_r01.xsa` | **376,152** | `2e4605b84a385eecdb2996e1d3516053aac92d5f5b250d4eb0695bbced2e72bb` |

（XSA 与 P3b 的 376,153 B 仅差 1 B —— 结构完全相同，只有引脚不同）

---

## 9. 未验证项

1. **⚠️ 上屏效果未验证**：本报告只到"位流 + 引脚实测"。是否有画面须上板确认（Wong 在场点屏）。
2. **带宽未测**：本版沿用 P3b 的 50 MHz 数据面（190 MB/s / 52 fps 基线）；带宽优化另属 P3f/P3c 线。
3. **TMDS 输出无 `output_delay` 约束**：ALINX demo 同样没有，且无板级 Tco/Tsu 数据，不编造（以实际上屏为准）。
4. **`hdmi_oen` 极性/连接**：按图纸与手册确认与 HDMI 无连接，故保持 V16/LVCMOS33、极性沿用厂商（1），不再作为变量。
5. 异步时钟组仍未在 XDC 中生效（`12-4739`；P3b 已证明对时序数字零影响），本版未复算。
6. 若上屏仍不亮，下一批候选变量（**不在本版范围**）：`rgb2dvi` 的 `kRgbToDvi`/通道映射与 ALINX demo 的实现差异、
   `pixel_clk_5x` 相位关系、以及 VTC 极性与 demo 的差异。

---

## 10. 产物与哈希（SHA-256）

| 文件 | 字节 | SHA-256 |
|---|---|---|
| `bd_p3g.tcl` | — | `6f851b204ce46e5ca256ea9f46e30784a75cc75fa8b38bfcbe6739f336b00ddf` |
| `p3g_tmds.xdc` | — | `87798da4e16179f0d9df86773dd7df0a63b49c24474a65663d669ce176ca6c80` |
| `rtl\top_p3g.v` | — | `25bb5d537b216973d6d61fd932a0e13a0d31c9aeaaff97c26494166a53f9ab68` |
| `s5_p3g_build_20261030_r01_console.log` | — | `9c26c33c4c8ee96f139b09b033f3908a58bb08c0ee9f26a8724ebbc5152a7e76` |
| `out\timing_route.rpt` | 456,836 | `d760423ad58f227fe8bf085b18a68f8b909d0cb50d7fcf6ba1a28edceb059679` |
| `out\util_route.rpt` | 12,631 | `f448002829e4dc3c6cd60a7f5820003db869b599ca08e1431a0e1302f23f8146` |
| `out\drc_route.rpt` | 267,712 | `1c3fef7f9d4acac94f58d957e39ba113b518c1be91663edb3700feb0305dcc0d` |
| `out\clocks_route.rpt` | 3,468 | `47a531cacd3706b617b1e9683123202b06c453290307a5ad15fb36663088e042` |
| `out\io_route.rpt` | 125,459 | `115e9c433d1df78d46b02ebe1dd008d0a091392dd442810fe823091ebf706886` |

边界：未上板、未 git；未改动 P2d / P3a / P3b / P3c / P3d / P3e / P3f 目录，未改厂商原件。