# P3C 构建报告（VDMA 数据面提速到 100 MHz）

| 项 | 值 |
|---|---|
| 阶段 / 任务 | **阶段5（HDMI 显示链）** / **S5-T01**（编号口径 2026-10-30 Wong 决定 A） |
| RunId | **s5_p3c_build_20261030_r01** |
| 日期 | 2026-10-30（UTC+8） |
| 工具 / 器件 | Vivado v2026.1 / `xc7z020clg400-2` |
| 工程 / BD / 顶层 | `s4d_p3c_r01` / `s4d_p3c` / `top_p3c` |
| 流程 | synth → opt/place/route → **write_bitstream → XSA**（**不上板**） |
| 约束 | `p3c_tmds.xdc`（纯声明式，过 `check_xdc_declarative.py`） |
| 基线 | P3b（`D:\tmp\lead\p3b_video_20261030_r01\`），**只改时钟域**，未改 P3b/P2d 目录 |

---

## 1. 结论（一句话）

**构建成功、位流已出、时序达标、资源几乎不变；VDMA 数据面已从 50 MHz 提到 100 MHz。**
**但"带宽是否达标"必须上板实测，本报告不声称已解决。**

- **WNS = +0.228 ns，WHS = +0.036 ns，TNS = THS = 0.000**（52,582 端点，0 失败）
- `write_bitstream` 成功；**NSTD-1 / UCIO-1 不出现**（引脚全部约束）
- 资源相对 P3b 几乎不变：LUT **+54**、FF **+129**、BRAM +0、DSP +0、MMCM +0、BUFG +0、OSERDES +0
- DRC 435 条、**0 error**（全是 DSP 流水线建议与 BRAM writefirst，与 P3b 同类）

---

## 2. 与 P3b 的**唯一差异**（时钟域）

| 信号 | P3b | **P3c** | 依据 |
|---|---|---|---|
| `vdma_0/m_axi_mm2s_aclk` | FCLK0 (50 MHz) | **FCLK1 (100 MHz)** | 数据面提速（本改动核心） |
| `ps7_0/S_AXI_HP2_ACLK` | FCLK0 (50 MHz) | **FCLK1 (100 MHz)** | 与 VDMA MM 侧同域，否则跨域回 50 MHz |
| `smc_vid/aclk` | FCLK0 (50 MHz) | **FCLK1 (100 MHz)** | AXI4→AXI3 转换桥必须与两侧同域（MM 侧 100 MHz） |
| `rst_100`（新增） | — | `proc_sys_reset`，`slowest_sync_clk`=FCLK1，`ext_reset_in`=FCLK_RESET0_N | 100 MHz 域复位 |
| `smc_vid/aresetn` | rst_all (50) | **rst_100 (100)** | 与自身 aclk 同域 |
| `vdma_0/s_axi_lite_aclk` | FCLK0 (50 MHz) | **FCLK0 (50 MHz) 不变** | 见 §3（第一轮失败教训） |
| `vdma_0/axi_resetn` | rst_all (50) | **rst_all (50) 不变** | 该复位同步于 `s_axi_lite_aclk`(=50 MHz) |
| `vdma_0/m_axis_mm2s_aclk` | 74.21875 | **74.21875 不变** | 像素域不动 |
| 像素域（VTC/vid_out/pixel_clk/5x）、2B@HP0、preproc+DMA@HP1、地址、`c_num_fstores=2`、rgb2dvi/TMDS/顶层/XDC 引脚 | — | **全部不变** | — |

**顶层 RTL 差异 = 4 行**（仅模块名/instance 名/文件头，逻辑 0 行改动）：
`top_p3c.v` vs `top_p3b.v` 的 `Compare-Object` 结果只有 `module top_p3c`、`s4d_p3c_wrapper u_bd`、两行注释。
厂商 7 个 VHDL 与 `rgb2dvi_wrap.vhd` **逐字节复制、未改**。

---

## 3. 第一轮失败与修正（BD 41-237，重要教训）

第一轮把 VDMA 的 **AXI-Lite 也提到 100 MHz**，BD 直接不通过：

```
ERROR: [BD 41-237] Bus Interface property FREQ_HZ does not match between
       /vdma_0/S_AXI_LITE(100000000) and /smc_ctrl/M04_AXI(50000000)
ERROR: [BD 41-237] Bus Interface property CLK_DOMAIN does not match between
       /vdma_0/S_AXI_LITE(s4d_p3c_ps7_0_0_FCLK_CLK1) and /smc_ctrl/M04_AXI(s4d_p3c_ps7_0_0_FCLK_CLK0)
```

**根因**：VDMA 的 AXI-Lite 是**控制面**，挂在 `smc_ctrl/M04`（50 MHz 域）上；只有**数据面** MM 侧需要提速。
**修正**：`s_axi_lite_aclk` 回退 50 MHz（与 `smc_ctrl` 同域），只把 `m_axi_mm2s_aclk`/HP2/`smc_vid` 提到 100 MHz；
同时把 `vdma_0/axi_resetn` 也放回 50 MHz 域——因为 **VDMA 只有一个 `axi_resetn`，它同步于 `s_axi_lite_aclk`**，
若跟随数据面放 100 MHz 域会变成跨域异步复位。

> 这条经验值得复用到任何"给 IP 局部提速"的场景：**控制口跟着控制面走，数据口才提速；单复位引脚跟主时钟走。**

---

## 4. 时钟域自证（BD 接口级，`out\post_checks.log`）

直接读 BD 接口的 `FREQ_HZ` / `CLK_DOMAIN`（比看连线更硬的证据）：

| BD 接口 | FREQ_HZ | CLK_DOMAIN | 判定 |
|---|---|---|---|
| `vdma_0/S_AXI_LITE` | **50,000,000** | `...FCLK_CLK0` | ✔ 控制面 50 MHz |
| `smc_ctrl/M04_AXI` | 50,000,000 | `...FCLK_CLK0` | ✔ 与上一行**同域**（BD 41-237 已消除） |
| `vdma_0/M_AXI_MM2S` | **100,000,000** | `...FCLK_CLK1` | ✔ **数据面 100 MHz** |
| `smc_vid/S00_AXI` | 100,000,000 | `...FCLK_CLK1` | ✔ |
| `smc_vid/M00_AXI` | 100,000,000 | `...FCLK_CLK1` | ✔ |
| `ps7_0/S_AXI_HP2` | **100,000,000** | `...FCLK_CLK1` | ✔ **HP2 100 MHz** |
| `vdma_0/M_AXIS_MM2S` | **74,218,750** | `/clk_wiz_0_clk_out1` | ✔ 流侧像素域不动 |
| `vidout_0/video_in` | 74,218,750 | `/clk_wiz_0_clk_out1` | ✔ |
| `vtc_0/ctrl` | 50,000,000 | `...FCLK_CLK0` | ✔ 不动 |
| `ps7_0/M_AXI_GP0` | 50,000,000 | `...FCLK_CLK0` | ✔ 不动 |

VDMA 参数（`out\post_checks.log`）：`c_prmry_is_aclk_async = 1`（ASYNC 模式）、`c_num_fstores = 2`、
`c_m_axi_mm2s_data_width = 64`、`c_m_axis_mm2s_tdata_width = 32` —— 与 P3b 一致。

四域时钟对象（`out\clocks_route.rpt`）：

| 时钟 | 周期 | 属性 | 归属 |
|---|---|---|---|
| `clk_fpga_0` | 20.000 ns | P | 50 MHz 控制面 |
| `clk_fpga_1` | 10.000 ns | P | **100 MHz 数据面** + clk_wiz 参考 |
| `clk_out1_s4d_p3c_clk_wiz_0_0` | **13.474 ns** | P,G,A | 74.21875 MHz 像素域 |
| `clk_out2_s4d_p3c_clk_wiz_0_0` | **2.695 ns** | P,G,A | 371.09375 MHz 串行域 |

### 4.1 异步时钟组（与 P3b 同一已知问题）
构建日志仍有 **6 条 `[Vivado 12-4739] set_clock_groups: No valid object(s)`**（`p3c_tmds.xdc:...`）：
用户 XDC 早于 IP/BD 时钟约束被读取，`get_clocks` 取空 → 组未建立（`PROCESSING_ORDER {LATE}` 在 P3b 已实测修不好）。

**已用"路由后补加"验证**（`out\post_clkgrp.log`）：

```
P3C_POST_CLOCKS: g0={clk_fpga_0} | g1={clk_fpga_1} | gp={clk_out1_... clk_out2_...}
P3C_POST_CLKGRP=APPLIED
P3C_POST_WNS=0.228   P3C_POST_WHS=0.036     ← 与构建时完全相同
```

→ **关键路径不跨时钟域，异步组缺失只影响"跨域路径是否被分析"，对报告数字零影响**；
故 §5 的数字即最终数字（且是保守下界）。18 条 `[Vivado 12-627] No clocks matched` 同源。

---

## 5. 时序结果

| 指标 | **P3c** | P3b | 变化 | 说明 |
|---|---|---|---|---|
| **WNS** | **+0.228 ns** | +0.544 ns | −0.316 | 100 MHz 数据面域新引入（10 ns 周期），关键路径转移 |
| **WHS** | **+0.036 ns** | +0.022 ns | **+0.014（更好）** | |
| **TNS / THS** | **0.000 / 0.000** | 0 / 0 | 不变 | 0 失败端点 |
| WPWS / TPWS | 1.102 / 0.000 | 1.102 / 0.000 | 不变 | |
| 端点总数 | 52,582 | 52,363 | +219 | 新增 rst_100 与 100 MHz 域逻辑 |

门槛（WNS/WHS ≥ 0、TNS/THS = 0）→ **通过**。

---

## 6. 资源占用与 P3b 对比

| 资源 | P2d | P3a+ | P3b | **P3c** | **P3c−P3b** | 上限 |
|---|---|---|---|---|---|---|
| LUT | 23,451 (44.08%) | 25,895 (48.67%) | 25,967 (48.81%) | **26,021 (48.91%)** | **+54** | 53,200 |
| FF | 10,414 (9.79%) | 14,876 (13.98%) | 14,892 (14.00%) | **15,021 (14.12%)** | **+129** | 106,400 |
| BRAM | 33.5 | 36.5 | 36.5 (26.07%) | **36.5 (26.07%)** | **+0** | 140 |
| DSP | 158 (71.82%) | 158 | 158 (71.82%) | **158 (71.82%)** | **+0** | 220 |
| MMCM | 0 | 1 | 1 | **1** | **+0** | 4 |
| BUFG/BUFGCTRL | 1 | 4 | 5 | **5** | **+0** | 32 |
| OSERDESE2 | 0 | 0 | 8 | **8** | **+0** | 125 |
| Bonded IOB | 0 | 28 | 9 | **9** | **+0** | 125 |

**判读**：只改时钟域几乎不产生资源变化（+54 LUT / +129 FF 来自 `rst_100` 与其复位同步逻辑）。
全部仍在 G0 §4 预算内（LUT 48.91% < 55–61% 预算下限；DSP 158 与预算完全一致）。

---

## 7. DRC（`out\drc_route.rpt`，435 条，**0 error**）

| 规则 | 严重度 | 条数 | 解释 |
|---|---|---|---|
| `DPIP-1` | Warning | 135 | DSP48 输入流水线建议（2B 推理核固有） |
| `DPOP-1` | Warning | 147 | DSP48 PREG 输出流水线建议 |
| `DPOP-2` | Warning | 148 | DSP48 MREG 输出流水线建议 |
| `DPREG-4` | Warning | 2 | DSP48 PregDynOpmodeZmuxP 提示 |
| `REQP-165` / `REQP-181` | Advisory | 1 / 2 | BRAM writefirst 模式建议 |

**`NSTD-1` / `UCIO-1` 不出现**（引脚全部约束）。`write_bitstream` 步骤无 Critical Warning / 无 Error。

`report_clocks`：四域齐全（§4）。日志 6 条 CRITICAL WARNING **全部是 `Vivado 12-4739`**（时钟组读取顺序，见 §4.1），
无其它 Critical Warning。

---

## 8. 位流 / XSA

| 文件 | 字节数 | SHA-256 |
|---|---|---|
| `out\s4d_p3c_r01.bit` | **4,045,762** | `f55a93706e2bbdb64f32d60947c4139ab0f2acba32861e14ac76ed0efcd31485` |
| `out\s4d_p3c_r01.xsa` | **376,383** | `1af694a08bcb2482e31ced3bf0dec5596f7fcc6d4c42a183b81e4c0c963c6d84` |

与 P3b 对比：位流大小相同（4,045,762 B，同器件同配置）、sha 不同（时钟/复位改动）；
XSA 增大 230 B（多了 `rst_100` 的地址/参数信息）。

---

## 9. 产物与哈希（SHA-256）

| 文件 | 字节 | SHA-256 |
|---|---|---|
| `bd_p3c.tcl` | — | `bce7144cd584dbec4c7087fd525f0d5c6a4c1a9e5c827194d693cbbc173a0ad3` |
| `p3c_tmds.xdc` | — | `025abbe529c1670dd108e67e8113660433dd1294cc8cd43ad7370c3f3a21fca7` |
| `s5_p3c_build_20261030_r01_console.log` | — | `91b892fef9bcb0fda194255ded8b289ef2a152a7d42cf48ad3cee4fbfb628b9f` |
| `out\timing_route.rpt` | 612,799 | `1d87a67dfdbed3e5ac6ecae0aa3ee3028fd4d8385ead6004c6e91e11bde61721` |
| `out\util_route.rpt` | 12,662 | `4083cbb51b2db6c8e5b811349b25c670d0a7964005f3250f6f2fb48eee237d24` |
| `out\drc_route.rpt` | 270,794 | `eb9ad3067fc41affdb12678318e6745712a986be3f679bf138bca36d1425664a` |
| `out\clocks_route.rpt` | 3,468 | `f630924b2568bd5d70ddfe6c8e4e71c4bfa60030b5340b3e7d5b95ae2404c167` |
| `out\io_route.rpt` | 125,459 | `42d65dd1a01235e1e934aebf5f2df8511ce917417be4da024383142563ccb2ea` |
| `out\clk_util_route.rpt` | 34,684 | `a8ddac9f72b59846cfe7e1c3da8f0cd95c5dea2adb131f2ed1efaea59204d556` |
| `out\timing_post_clkgrp.rpt` | 612,805 | `a0d541e6600ccef5b438598427b5eee1f777b7d267873c14b2d1e5a15a535164` |

同时生成：`out\post_checks.log`（BD 接口时钟域自证）、`out\post_clkgrp.log`（路由后异步组复算）、
`out\clk_interaction_route.rpt`、`out\check_timing_route.rpt`、`out\cdc_route.rpt`、`out\p3c_bd_facts.txt`。

---

## 10. 未验证项 / 风险（**带宽不在本报告结论内**）

1. **⚠️ 带宽是否达标：未验证，必须上板实测。** 本构建只能证明"设计合法、时序达标、数据面时钟已到 100 MHz"。
   理论上限从 50 MHz×64 bit = 400 MB/s 提到 **100 MHz×64 bit = 800 MB/s**；需求（720p60、32 bpp）**221 MB/s**。
   板级此前在 50 MHz 下实测 190 MB/s（效率约 47.5%）；若效率相当，100 MHz 下约 ~380 MB/s，相对 221 MB/s 约 1.7× 余量
   —— **这是估算，不是实测结论**。需 board-runner 用同一口径（同样帧数/同样分辨率）复测后填这里。
2. **未上板**：S6-A（上屏）、S6-C（读帧 CRC）、S6-D（叠加）、S6-E（P2d 7 项回归）、S6-F（30 min 稳定）全未做 → 不构成 G3/G4/G5。
3. **四域异步组在 XDC 中仍未生效**（§4.1，`12-4739`）：已证明对数字零影响，但应在下一版改用 impl `STEPS.OPT_DESIGN.TCL.PRE` 钩子正式固化
   （`D:\tmp\lead\p3b_video_20261030_r01\XDC_GUIDELINES.md` 已给出做法）。
4. **WNS 从 +0.544 降到 +0.228**：100 MHz 数据面域成为新的约束来源，仍为正但余量减小。
   若后续加叠加逻辑，需重新评估（尤其 10 ns 域）。
5. **`hdmi_oen` 极性仍待上板确认**（P3b 已记录：厂商源码 `rgb2dvi.vhd:192` 驱动 `'1'`，与"低有效"提示相反）。
6. **VDMA 三时钟（50/100/74.21875）**：已确认 `c_prmry_is_aclk_async = 1`、IP 自报 ASYNC 模式；
   但**三时钟组合下的行缓存欠载/溢出行为需上板观察**（`mm2s_introut` 错误计数）。
7. **软件侧未对接**：VTC 寄存器表（P3B 报告 §8）与 VDMA 双缓冲（`num_fstores=2`）未在驱动中验证。