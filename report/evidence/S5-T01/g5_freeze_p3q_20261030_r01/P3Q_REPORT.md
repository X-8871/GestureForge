# P3q 报告 —— 计算集成体（P2d）+ 显示链（P3n/P3p）合并

| 项 | 值 |
|---|---|
| 阶段 / 任务 | **阶段5（HDMI 显示链）** / **S5-T01** |
| RunId | **s5_p3q_build_20261030_r01** |
| 日期 | 2026-10-30（UTC+8） |
| 工具 / 器件 | Vivado v2026.1 / `xc7z020clg400-2` |
| 工程 / BD / 顶层 | `s4d_p3q_r01` / `s4d_p3q` / `top_p3q` |
| 目的 | **阶段5 真正要交付的集成体**：2B 计算通路 + HDMI 显示通路 |

---

## 1. 结论

**位流 + XSA 已出；时序达标（WNS +0.371 / TNS 0 / 失败端点 0）、DRC 0 error、地址与引脚全部按规格落位。**

| 项 | 值 |
|---|---|
| **WNS / TNS** | **+0.371 ns / 0.000** |
| **失败端点 / 总端点** | **0 / 46,096** |
| **WHS / THS** | +0.036 / 0.000 |
| WPWS / TPWS | 1.102 / 0.000 |
| DRC | **444 条、0 error**（详见 §7） |
| 资源 | LUT **24,769 (46.56%)**、FF **12,648 (11.89%)**、BRAM **35.5 (25.36%)**、DSP **158 (71.82%)**、MMCM 1、BUFG 4、OSERDESE2 8、IOB 10 |
| 日志 | **0 ERROR / 0 CRITICAL WARNING / 98 WARNING** |
| **bit** | `out\s4d_p3q_r01.bit` **4,045,762 B** `4d6ea2efd71bc6f9113f3a009278f097443d8a03b244aaedac70ec23f0b9b6e4` |
| **XSA** | `out\s4d_p3q_r01.xsa` **344,843 B** `dfefc883b0fe267cf8bffc3f76b15067b9ab7ed99779670d661f8261907fe96d` |

**构建过程中修了一处**：首轮 `validate_bd_design` 报 `[BD 41-758] /gpio_uf/s_axi_aclk` 未接时钟
⇒ 已把 `gpio_uf/s_axi_aclk` 与 `gpio_uf/s_axi_aresetn` 接到 **FCLK0 / `rst_all`（50 MHz 控制面）**。
这也正是正确选择：RTL 里 underflow 的格雷码 CDC 与"本帧/累计"减法**都在 `clk_50` 域完成**，
GPIO 与它们同域，无跨域问题。`[BD 41-3281]`（P2d 既有双 SmartConnect 结构）**未动**。

---

## 2. 与 P2d 的差异（计算侧：**零改动**）

| 项 | P2d | **P3q** |
|---|---|---|
| 2B 推理核 `infer_0/M_AXI` | **直连 `S_AXI_HP0`** | **完全不变** |
| preproc 读 + AXI DMA 写 | `smc_data`(2S/1M) → `S_AXI_HP1` | **完全不变** |
| 地址 | 2B CSR `0x43C00000`、preproc `0x43C10000`(0x80)、AXI DMA `0x43C20000` | **完全不变**（实测见 §3） |
| PS7 | FCLK0=50 MHz、HP0/HP1 64b | **追加** FCLK1=100 MHz、**HP2 64b**（仅供显示） |
| `smc_ctrl` | 1S/**3M** | 1S/**5M**（M00~M02 原样，新增 M03=VDMA Lite、M04=GPIO） |
| 打包器 / DMA 23-bit 长度 / SRC_BASE | — | **完全不变**（`P3Q_SRC_BASE_BD=0x12000000`） |

**P2d 计算侧的行、连线、参数逐字保留**；P3q 只是在 BD 里**追加**显示段与 HP2/FCLK1。

---

## 3. 地址映射（构建日志实测打印）

| 从设备 | 基址 | 范围 | 归属 |
|---|---|---|---|
| 2B 推理核 CSR | **0x43C00000** | 64 KB | P2d（不变） |
| preproc CSR | **0x43C10000** | 0x80 | P2d（不变） |
| AXI DMA（S2MM） | **0x43C20000** | 64 KB | P2d（不变） |
| **VDMA（MM2S）AXI-Lite** | **0x43C40000** | 64 KB | **P3q 新增** |
| **underflow GPIO** | **0x43C50000** | 4 KB | **P3q 新增** |
| 2B 主端 → HP0 DDR | 0x00000000 | 1 GB | P2d（不变） |
| preproc/DMA 主端 → HP1 DDR | 0x00000000 | 1 GB | P2d（不变） |
| **VDMA 主端 → HP2 DDR** | 0x00000000 | 1 GB | **P3q 新增** |

**GPIO 双通道**（`axi_gpio`，只读）：`0x43C50000 +0x00` = **本帧欠载像素数**（每 vsync 归零）、`+0x08` = **累计欠载像素数**（注：lead 原话写 `+0x04`，但 Xilinx AXI GPIO 双通道的通道 2 数据寄存器偏移是 **+0x08**；`+0x04` 是通道 1 的三态寄存器。请软件按 **+0x08** 读，或用驱动 `XGpio_DiscreteRead(&g, 2)`）。

---

## 4. 与 P3n 显示侧的差异

| 项 | P3n | **P3q** |
|---|---|---|
| 计算集成体 | 无（只有显示） | **P2d 全部** |
| VDMA AXI-Lite | 0x43C00000 | **0x43C40000**（避让 P2d） |
| underflow GPIO | 0x43C10000 单通道（累计） | **0x43C50000 双通道（本帧 + 累计）** |
| fsync 能力 | 无 | **有**（`c_use_fsync=1`/`c_use_mm2s_fsync=1`，`mm2s_fsync ← axis_to_video.vs`；软件不置 `SYNC_EN` 时等价于 P3n 自由跑） |
| 其余显示结构 | MMCM 原语 74.21875/371.09375 + `locked`、`axis_to_video` 自产 720p60、rgb2dvi、TMDS N18/V20/T20/N20 | **完全一致** |
| VTC / `v_axi4s_vid_out` | 已删除 | **仍无**（P3g/P3h 已证明它们不出时序） |

---

## 5. 时钟域

| 域 | 时钟 | 承载 |
|---|---|---|
| 50 MHz | `clk_fpga_0`（PS7 FCLK0） | 2B 核 / preproc / 打包器 / AXI DMA / `smc_ctrl` / `smc_data` / VDMA Lite / **underflow GPIO** / `rst_all` |
| 100 MHz | `clk_fpga_1`（PS7 FCLK1） | VDMA MM 侧 / 协议转换器 / `S_AXI_HP2` / `rst_100` |
| 74.21875 MHz | `clk_pixel_raw`（RTL MMCM CLKOUT0） | VDMA 流侧 / `axis_to_video` / rgb2dvi 像素侧 |
| 371.09375 MHz | `clk_5x_raw`（MMCM CLKOUT1） | rgb2dvi OSERDESE2 CLK |
| 50 MHz 输入 | `sys_clk`（U18） | MMCM 参考 |

实测六时钟：`clk_fpga_0` 20.000 / `clk_fpga_1` **10.000** / `sys_clk` 20.000 / `clk_fb` 80.000 /
`clk_pixel_raw` **13.474** / `clk_5x_raw` **2.695** ns ✓

---

## 6. 时序（交付值 + 原始口径）

| | WNS | TNS | 失败端点 | WHS |
|---|---|---|---|---|
| **P3q 交付（含 CDC 约束）** | **+0.371** | **0.000** | **0** | +0.036 |
| P2d 基线（无显示链） | +0.128 | 0 | 0 | +0.036 |
| 参考：P3m 原始（同构 CDC、未加约束） | −5.503 | −173.092 | 32 | +0.050 |

**原始口径说明**：P3q 未单独构建"无 CDC 约束"版本；其 CDC 结构与 P3m 同源（32 位格雷码 + 3 级同步 +
vsync 2 级同步），P3m 的未约束原始值 **−5.503 / TNS −173.092 / 32 端点**（32=位宽、requirement 仅 0.211 ns、
数据路径 1.322 ns）⇒ 假性违例。加 `set_max_delay -datapath_only` 后本版 **TNS=0、失败端点=0**。

时序报告里跨时钟行实测：`clk_pixel_raw → clk_fpga_0` **WNS 11.329 ns、0 失败 / 33 端点** ⇒ CDC 通路健康。

**关键对比**：P3q 的 WNS **+0.371 优于 P2d 的 +0.128** —— 说明加入显示链后，关键路径没有变差
（时序由 P2d 的 2B/计算侧主导）。

---

## 7. DRC（444 条、**0 error**）

| 规则 | 严重度 | 条数 | 说明 |
|---|---|---|---|
| `DPIP-1` | Warning | 135 | DSP48 输入流水线建议（2B 推理核固有） |
| `DPOP-1` | Warning | 146 | DSP48 PREG 输出流水线建议 |
| `DPOP-2` | Warning | 148 | DSP48 MREG 输出流水线建议 |
| `DPREG-4` | Warning | 2 | DSP48 PregDynOpmodeZmuxP |
| `PDCN-1569` | Warning | 1 | 协议转换器 IP 内部 LUT |
| `REQP-1839` | Warning | 8 | RAMB36 异步控制（VDMA/PS7 内部 BRAM） |
| `RTSTAT-10` | Warning | 1 | No routable loads |
| `REQP-165` / `REQP-181` | Advisory | 1 / 2 | BRAM writefirst |

无 `NSTD-1` / `UCIO-1`；日志无 ERROR、无 CRITICAL WARNING。

---

## 8. 资源对比

| 资源 | P2d（计算） | P3n（显示） | **P3q（合并）** | P3q−P2d | 上限 |
|---|---|---|---|---|---|
| LUT | 23,451 (44.08%) | 1,637 | **24,769 (46.56%)** | **+1,318** | 53,200 |
| FF | 10,414 (9.79%) | 2,503 | **12,648 (11.89%)** | **+2,234** | 106,400 |
| BRAM | 33.5 (23.93%) | 2 | **35.5 (25.36%)** | **+2** | 140 |
| DSP | 158 (71.82%) | 0 | **158 (71.82%)** | **0** | 220 |
| MMCM | 0 | 1 | **1** | +1 | 4 |
| BUFG | 1 | 4 | **4** | +3 | 32 |
| OSERDESE2 | 0 | 8 | **8** | +8 | 125 |
| Bonded IOB | 0 | 10 | **10** | +10 | 125 |

增量 = 显示链（少于一"P3n 独立版"的 1,637/2,503，因为部分逻辑与 BD 共享/优化）。
**远低于 G0 §4 预算**（LUT 46.56% < 55–61%，DSP 与预算完全一致）。

---

## 9. 引脚（`report_io` 实测）

| 端口 | 球位 | 说明 |
|---|---|---|
| `sys_clk` | **U18** | 50 MHz 输入（LVCMOS33） |
| `TMDS_clk_p` / `_n` | **N18 / P19** | TMDS_33 |
| `TMDS_data_p[0]` / `_n[0]` | **V20 / W20** | TMDS_33 |
| `TMDS_data_p[1]` / `_n[1]` | **T20 / U20** | TMDS_33 |
| `TMDS_data_p[2]` / `_n[2]` | **N20 / P20** | TMDS_33 |
| `hdmi_oen` | **V16** | LVCMOS33（12 mA / SLOW） |

**2B / preproc 侧无新增芯片引脚**（它们只走 PS7 的 DDR/MIO，由 PS7 IP 自带约束）；
`Bonded IOB = 10` 正好是 `sys_clk` + 8 个 TMDS + `hdmi_oen`，与规格一致。

---

## 10. 软件最小改动清单（给 video-sw）

显示链地址与本版语义：

| 项 | 值 |
|---|---|
| VDMA AXI-Lite | **0x43C40000** |
| underflow GPIO | **0x43C50000**（ch1 `+0x00` 本帧 / ch2 `+0x08` 累计） |
| VDMA 模式 | MM2S-only、非 SG、`c_num_fstores=2`、MM 64-bit、流 32-bit、**具备 fsync 能力** |
| 帧存 ABI | 1280×720、32bpp（`0xAARRGGBB`）、stride **5120 B/行**、帧 **3,686,400 B** |

1. **启动 VDMA**：帧地址 + HSIZE/VSIZE/STRIDE 写法同前，`CR.RS=1`。
2. **若要消除撕裂**（推荐）：启用 fsync —— `CR.SYNC_EN(bit3)=1` + `FSYNC_SRC(bits[6:5])=0`（本通道外部引脚），
   即 `CR=0x00000009`；或驱动里 `DmaSetup.EnableSync=1` / `GenLock=XAXIVDMA_SLAVE` + `XAxiVdma_FsyncSrcSelect(...,XAXIVDMA_CHAN_FSYNC, XAXIVDMA_MM2S)`。
   不启用时行为同 P3n（自由跑，可能撕裂）。
3. **欠载判定**：读 `0x43C50000`（本帧）连续为 0 ⇒ 欠载消除；仍 ~13% ⇒ 数据面不足 ⇒ 候选 B（720p50，只改 `H_FP 110→440`）。
4. **计算侧完全不变**：2B CSR `0x43C00000`、preproc `0x43C10000`、DMA `0x43C20000` 的现有代码一行不用改。

---

## 11. 未验证项 / 风险（**如实记录，不优化掩盖**）

1. **⚠️ DDR 带宽并发风险（最高优先）**：P2d 的 2B 推理 47,287 ms 是在**无显示**时测的。
   本版 P2d 数据面（HP0/HP1 @50 MHz）与显示（HP2 @100 MHz）**并发读同一颗 DDR**
   ⇒ 必须复测 2B 单帧耗时与 `fps_dis`；**若 2B 变慢，如实记录，不作为优化掩盖**。
   预期影响方向未知：2B 核是延迟暴露型单 outstanding 主端，且 DDR 总量（~1.6 GB/s 理论）远大于
   显示需求（221 MB/s）+ 2B 需求，但 PS7 的 DDR 仲裁与 HP 端口配置会影响实际分配。
2. **⚠️ 上屏 / 欠载 / 撕裂：均未验证**（需板测；判据见 §10）。
3. **fsync 在"供数慢于显示"方向的行为**未实测（`GenLockRepeat` 重复帧 vs 停顿）。
4. **非 SG 每帧重装**：重装不及时会短暂无数据（本帧欠载计数会体现）。SG 留待 C 档。
5. 未做叠加（G0 D2 框+文字属后续）。
6. `tlast_misalign` 计数仍在 RTL 内部（未占 GPIO 通道），需要时加第二个 GPIO（0x43C60000）。

---

## 12. 产物与哈希（SHA-256）

| 文件 | 字节 | SHA-256 |
|---|---|---|
| `out\s4d_p3q_r01.bit` | **4,045,762** | `4d6ea2efd71bc6f9113f3a009278f097443d8a03b244aaedac70ec23f0b9b6e4` |
| `out\s4d_p3q_r01.xsa` | **344,843** | `dfefc883b0fe267cf8bffc3f76b15067b9ab7ed99779670d661f8261907fe96d` |

**中间记录留痕**：首轮 `validate_bd_design` 失败（`BD 41-758 /gpio_uf/s_axi_aclk`）已修，
修复内容 = 补 `gpio_uf/s_axi_aclk`(FCLK0) 与 `gpio_uf/s_axi_aresetn`(rst_all)。

边界：未上板、未 git；未改动 P2d/P3a/P3b/P3c/P3d/P3e/P3f/P3g/P3h/P3k/P3m/P3n/P3p 目录。