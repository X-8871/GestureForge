# P3n 报告 —— P3m + VDMA 数据面提速到 100 MHz（候选 A，保 720p60）

| 项 | 值 |
|---|---|
| 阶段 / 任务 | **阶段5（HDMI 显示链）** / **S5-T01** |
| RunId | **s5_p3n_build_20261030_r01** |
| 日期 | 2026-10-30（UTC+8） |
| 工具 / 器件 | Vivado v2026.1 / `xc7z020clg400-2` |
| 工程 / BD / 顶层 | `s4d_p3n_r01` / `s4d_p3n` / `top_p3n` |
| 目的 | 消除 **结构性欠载**（VDMA 每帧只供 52 fps，显示端按 60 Hz 消费） |

---

## 1. 结论

**位流 + XSA 已出；时序清零（WNS +4.252 / TNS 0 / 失败端点 0）、DRC 0 error、TMDS 四对球位与 P3m 完全相同。**
数据面时钟已确认落在 100 MHz（`P3N_FCLK1_ACT=100.000000 MHz`），BD 无 `41-237`。

| 项 | 值 |
|---|---|
| **WNS** | **+4.252 ns** |
| **TNS / 失败端点** | **0.000 / 0** |
| **WHS / THS** | +0.056 / 0.000 |
| 端点总数 | 5,606 |
| DRC | **11 条、0 error**（同 P3m 的 4 类，全 Warning/Advisory） |
| 资源 | LUT **1,637 (3.08%)**、FF 2,503、BRAM 2、DSP 0、OSERDESE2 **8**、MMCM 1、BUFG **4**、IOB 10 |
| 日志 | **0 ERROR / 0 CRITICAL WARNING / 88 WARNING** |
| **bit** | `out\s4d_p3n_r01.bit` **4,045,762 B** `80b88f1750698e15a1961a2b1ee3081fc9d2c8f5744035e9f119ac82fc9cfcb0` |
| **XSA** | `out\s4d_p3n_r01.xsa` **263,571 B** `a9953d04c5d9d89a5f9cc2adbd0693619d7c1cb053156651839b6a891ef45133` |

---

## 2. 与 P3m 的唯一差异（数据面时钟域）

| 信号 | P3m | **P3n** |
|---|---|---|
| `vdma_0/m_axi_mm2s_aclk` | FCLK0 (50 MHz) | **FCLK1 (100 MHz)** |
| `ps7_0/S_AXI_HP2_ACLK` | FCLK0 (50 MHz) | **FCLK1 (100 MHz)** |
| `pc_hp/aclk`（协议转换器） | FCLK0 (50 MHz) | **FCLK1 (100 MHz)** |
| `rst_100`（新增） | — | `proc_sys_reset`，`slowest_sync_clk`=FCLK1，驱动 `pc_hp/aresetn` |
| `vdma_0/s_axi_lite_aclk` | FCLK0 (50) | **FCLK0 (50) 不变** ← 控制面与 `smc_ctrl` 同域，避开 `BD 41-237`（P3c 实测经验） |
| `vdma_0/axi_resetn` | rst_all (50) | **rst_all (50) 不变**（该复位同步于 `s_axi_lite_aclk`） |
| `vdma_0/m_axis_mm2s_aclk` | pixel_clk (74.21875) | **不变**（VDMA 仍 ASYNC 模式，内部 CDC） |
| `axis_to_video` / MMCM / rgb2dvi / TMDS 引脚 / `c_num_fstores=2` | — | **全部不动** |

**改动仅 3 条时钟连线 + 1 个新复位块**；RTL（`axis_to_video.v` / `top_p3n.v`）与引脚约束与 P3m 逐字一致（仅改模块/工程名）。

---

## 3. 为什么这样改（实测依据）

板级实测（P3m）：
- 欠载 **7.27 Mpx/s = 13.1%**，而 `1 − 52/60 = 13.3%` ⇒ **VDMA 每帧只供 52 fps 的数据，显示端按 60 Hz 消费**
- VDMA `CR=0x10003`（RS=1）、`SR=0x11000`（**无 DMA 错误**）⇒ 不是随机故障，是**结构性带宽不足**

带宽账：

| | MM 侧峰值 | 720p60 需求（32bpp） | P3b 实测 |
|---|---|---|---|
| P3m（50 MHz × 64 bit） | 400 MB/s | **221.1 MB/s** | ~190 MB/s（效率 ~47.5%） |
| **P3n（100 MHz × 64 bit）** | **800 MB/s** | 221.1 MB/s | **待测** |

> ⚠️ 已知反例：P3c 同样把数据面提到 100 MHz，但带的是 **SmartConnect** 且三时钟全异步，实测 fps 45（更差）。
> 本版用 **最小 `axi_protocol_converter`**（P3f 已验证）、控制面留在 50 MHz、只有数据面 100 MHz ⇒ 变量更少。
> **能否消除欠载必须上板实测，本报告不声称已解决。**

---

## 4. 时序（交付值 + 原始值口径）

| | WNS | TNS | 失败端点 | WHS |
|---|---|---|---|---|
| **P3n 交付（含 CDC 约束）** | **+4.252** | **0.000** | **0** | +0.056 |
| P3m 原始（未加 CDC 约束，同构 CDC） | −5.503 | −173.092 | 32 | +0.050 |
| P3m 交付（含 CDC 约束） | +8.568 | 0.000 | 0 | +0.087 |

**关于"原始数字"**：P3n **没有**单独构建"无 CDC 约束"版本（那需要再跑一轮 ~15 min）。
但 P3n 的 CDC 结构与 P3m **完全相同**（同一 `axis_to_video.v`：32 位格雷码计数器 + 3 级同步器，cell 名一致），
P3m 的原始值 **−5.503 / TNS −173.092 / 32 端点**就是同一结构的"未加约束"表现：
32 个端点 = 计数器 32 位，requirement 仅 0.211 ns（两异步时钟最近边沿），数据路径仅 1.322 ns
⇒ **假性违例**，非功能缺陷、非布线差。

**CDC 约束（与 P3m 相同，cell 过滤避开 12-4739）**：
```tcl
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *uf_pixels_reg[*]}] -to [get_cells -hier -filter {NAME =~ *uf_g_s1_reg[*]}]  13.474
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *uf_g_s1_reg[*]}]    -to [get_cells -hier -filter {NAME =~ *uf_g_s2_reg[*]}]  20.000
```

**四域/六时钟实测**（`out\clocks_route.rpt`）：
`clk_fpga_0` 20.000 ns（50 MHz）· **`clk_fpga_1` 10.000 ns（100 MHz，数据面）** · `sys_clk` 20.000 · `clk_fb` 80.000 ·
`clk_pixel_raw` **13.474 ns（74.21875 MHz）** · `clk_5x_raw` **2.695 ns（371.09375 MHz）**

---

## 5. DRC（11 条、0 error，与 P3m 同类）

| 规则 | 严重度 | 条数 | 说明 |
|---|---|---|---|
| `PDCN-1569` | Warning | 1 | 协议转换器 **IP 内部** LUT |
| `REQP-1839` | Warning | 8 | RAMB36 异步控制（VDMA/PS7 内部 BRAM） |
| `RTSTAT-10` | Warning | 1 | No routable loads |
| `REQP-181` | Advisory | 1 | BRAM writefirst |

无 `NSTD-1` / `UCIO-1`；日志 **0 ERROR / 0 CRITICAL WARNING**。

---

## 6. 引脚复核（`report_io`，与 P3m 完全一致）

| 端口 | 球位 | SITE | IOSTANDARD |
|---|---|---|---|
| `sys_clk` | **U18** | `IO_L12P_T1_MRCC_34` | LVCMOS33 |
| `TMDS_clk_p` | **N18** | `IO_L13P_T2_MRCC_34` | TMDS_33 |
| `TMDS_clk_n` | **P19** | `IO_L13N_T2_MRCC_34` | TMDS_33 |
| `TMDS_data_p[0]` | **V20** | `IO_L16P_T2_34` | TMDS_33 |
| `TMDS_data_n[0]` | **W20** | `IO_L16N_T2_34` | TMDS_33 |
| `TMDS_data_p[1]` | **T20** | `IO_L15P_T2_DQS_34` | TMDS_33 |
| `TMDS_data_n[1]` | **U20** | `IO_L15N_T2_DQS_34` | TMDS_33 |
| `TMDS_data_p[2]` | **N20** | `IO_L14P_T2_SRCC_34` | TMDS_33 |
| `TMDS_data_n[2]` | **P20** | `IO_L14N_T2_SRCC_34` | TMDS_33 |
| `hdmi_oen` | **V16** | `IO_L18P_T2_34` | LVCMOS33（12 mA/SLOW） |

---

## 7. ★ 候选 B（720p50）—— **只准备，未构建**（等 Lead 指令）

### 7.1 具体改法（1 处参数，其余全不动）
1. 从 **P3n** 复制出新目录（建议 `D:\tmp\lead\p3o_video_20261030_r01\`，工程名 `s4d_p3o_r01`）；
2. 只改 `rtl/top_p3o.v` 里 `axis_to_video` 实例的**一个参数**：
   ```verilog
   .H_FP (110)   ->   .H_FP (440)      // 720p50 标准前肩
   ```
   （`H_ACTIVE=1280`、`H_SYNC=40`、`H_BP=220` 保持不变 ⇒ `H_TOTAL = 1280+440+40+220 = 1980`）
3. `V_*` 全部不变（`720/5/5/20` ⇒ `V_TOTAL = 750`）；
4. **BD / 时钟 / XDC / 引脚 / rgb2dvi / MMCM 全部不动**（引脚仍 N18/V20/T20/N20）；
5. 构建流程与 P3n 完全相同。

### 7.2 预期数值（已核算）
| 量 | 值 |
|---|---|
| H_TOTAL × V_TOTAL | **1980 × 750** |
| 帧率 | 74.21875e6 / 1,485,000 = **49.979 Hz** |
| 像素率 | 46.06 Mpx/s |
| **带宽需求（32bpp）** | **184.2 MB/s** |
| 对比：实测供数能力 | ~190 MB/s（P3b/P3m 实测） |
| 对比：720p60 需求 | 221.1 MB/s |
| ⇒ 判定 | **184.2 < 190 ⇒ 理论上不再欠载**（余量仅 ~3%，属"刚好够"） |

### 7.3 风险与注意
1. **显示器是否接受 720p50**：720p50 是 CEA-861 标准格式（H total 1980 就是标准值），绝大多数显示器支持；
   但若显示器/线缆只吃 60 Hz，可能无信号——**上板前先确认 Wong 的屏支持 50 Hz**。
2. 余量只有 ~3%（184 vs 190），若 VDMA 效率有波动仍可能偶发欠载；真到那步可再考虑
   `H_TOTAL` 更大（如 2200 → 45 Hz）或改 SG/提高突发效率。
3. 画面帧率变 50 Hz，功能上无影响（棋盘/视频显示；截图类任务无差别）。
4. 若 A（P3n）已消除欠载，则 **B 不必构建**。

---

## 8. 未验证项 / 风险

1. **⚠️ 欠载是否消除：未验证，必须上板实测**（读 GPIO `0x43C10000` 的 underflow 计数，或看屏上是否还有黑块/撕裂）。
2. **带宽仍是 100 MHz 数据面的首次实测**：P3c 曾在 100 MHz 下变差（但带 SmartConnect），本版变量更少，结论待测。
3. 非 SG 模式每帧需软件重装，重装不及时仍会短暂黑屏（与 P3m 相同，未改）。
4. 未做 ILA 观测；如需看 AXIS 时序可下一版加。
5. 未做叠加（G0 D2 框+文字属后续）。

---

## 9. 软件接口（与 P3m 相同，仅数据面时钟变了）

| 项 | 值 |
|---|---|
| VDMA AXI-Lite 基址 | **0x43C00000** |
| underflow 计数（GPIO 只读） | **0x43C10000**（单位=欠载像素数，0=从未欠载） |
| VDMA 模式 | MM2S-only、非 SG、`c_num_fstores=2`、MM 64-bit、流 32-bit |
| 帧存 ABI | 1280×720、32bpp（`0xAARRGGBB`）、stride **5120 B/行**、帧 **3,686,400 B** |
| 时钟 | 控制面 50 MHz、**数据面 100 MHz**、流侧 74.21875 MHz（ASYNC） |

---

## 10. 产物与哈希（SHA-256）

| 文件 | 字节 | SHA-256 |
|---|---|---|
| `out\s4d_p3n_r01.bit` | **4,045,762** | `80b88f1750698e15a1961a2b1ee3081fc9d2c8f5744035e9f119ac82fc9cfcb0` |
| `out\s4d_p3n_r01.xsa` | **263,571** | `a9953d04c5d9d89a5f9cc2adbd0693619d7c1cb053156651839b6a891ef45133` |
| `bd_p3n.tcl` | — | `957705369f0394dc0e9cf47e03b2fe10729d7c83db4bedb65447790a63aa7a0f` |
| `p3n.xdc` | — | `5bed5bc641e58260aa6debc9ab1bc9afd4c1001f22643217755df19b9fd7f385` |
| `p3n_cdc.xdc` | — | `4334592e84db7fec8837fbbacad7d4324b1b9cd520d4685a46d3d1552016d44c` |
| `rtl\top_p3n.v` | — | `fe9b053912fceceaa00d066d1e526e9e211b069fffe847075123c834daf6b179` |
| `rtl\axis_to_video.v` | — | `a7b36d7f90cc1619eeb6133ddd5f1c4ff2ad31953fe47fac10b5228456de665a` |
| `s5_p3n_build_20261030_r01_console.log` | — | `4fd5eb59bd180356a480643d10a9c6a89375e22525255a7672f0b7375addcd1a` |
| `out\timing_route.rpt` | 517,606 | `687488bcde62512e9040d68e91bc82f51dfda80c7a281024bab439f86d6cd863` |
| `out\util_route.rpt` | 11,944 | `d016c59957623ef05fec5834a60474d7d191a9ee7d6a5189152ff56e3a75157d` |
| `out\drc_route.rpt` | 16,717 | `70564fccee6174128e15ae4dbd006b22fd7d927331a808e13c7b27b7ab921d27` |
| `out\io_route.rpt` | 125,459 | `248ba003e52249a6f2495ac3fa25753556bba8c6cd4b93602fa670fc39948041` |
| `out\clocks_route.rpt` | 2,668 | `cf39034aab395d46a6d9f6b641037b80408fe81ce020fe74471ce3c199d894c2` |

边界：未上板、未 git；未改动 P2d/P3a/P3b/P3c/P3d/P3e/P3f/P3g/P3h/P3k/P3m 目录。