# P3r 报告 —— P3q 冻结集成体 + AN5642 相机采集→DDR raw（R-07）

| 项 | 值 |
|---|---|
| 阶段 / 任务 | **阶段5（HDMI 显示链）** / **S5-T01** / 关联 **R-07 真实相机接入** |
| RunId | **s5_p3r_build_20261031_r01** |
| 日期 | 2026-10-31（UTC+8） |
| 工具 / 器件 | Vivado v2026.1 / `xc7z020clg400-2` |
| 工程 / BD / 顶层 | `s4d_p3r_r01` / `s4d_p3r` / `top_p3r` |
| 性质 | **离线构建，未上板、未烧 QSPI、未 push** |

---

## 1. 结论

**位流 + XSA 已出，时序清零（TNS=0、失败端点=0），DRC 0 error，相机 16 个 J11 引脚与 TMDS 均按阶段3 冻结引脚落位。**

**两版并存，推荐交付 build3**（设计与约束完全相同，仅实现策略不同）：

| | **build2（`out/`）** | **build3（`out/build3/`，推荐）** | P3q 基线 |
|---|---|---|---|
| impl 策略 | `Vivado Implementation Defaults` | **`Performance_ExplorePostRoutePhysOpt`** | 默认 |
| **WNS** | +0.019 | **+0.342** | +0.371 |
| **TNS / 失败端点** | 0.000 / 0 | **0.000 / 0** | 0 / 0 |
| **WHS / THS** | +0.061 / 0 | +0.053 / 0 | +0.036 / 0 |
| 端点总数 | 58,726 | 58,492 | 46,096 |
| DRC | 436 条 / 0 error | **430 条 / 0 error** | 11 条 / 0 error |
| LUT | 27,558 (51.80%) | **27,536 (51.76%)** | 24,769 |
| BRAM / DSP / IOB / BUFG | 43.5 / 158 / 24 / 5 | 43.5 / 158 / 24 / 5 | 35.5 / 158 / 10 / 4 |
| **bit** | `6202872e…`（4,045,762 B，`out\`） | **`648f3156…`（4,045,762 B，`out\build3\`）** | — |
| **XSA** | `7b26a487…`（418,944 B） | **`1284f637…`（418,950 B）** | — |

> **build3 把 WNS 余量从 +0.019 提到 +0.342**（+0.323 ns，基本恢复到 P3q 的 +0.371 水平），
> 0 失败端点、DRC 0 error 保持不变；**设计/RTL/BD/XDC 与 build2 完全一致，唯一差异是实现策略**。
> 详见 §6.3。

---

## 2. 与 P3q 的差异清单（计算/显示基线**未动**）

| 项 | P3q（冻结集成体） | **P3r** |
|---|---|---|
| 2B 直连 HP0 / preproc+DMA→HP1 / 地址 43C0/1/2 | — | **完全不变** |
| 显示链（MMCM/axis_to_video/rgb2dvi/TMDS/VDMA MM2S） | — | **完全不变**（VDMA 仍 0x43C40000，underflow GPIO 仍 0x43C50000） |
| 采集通路 | 无 | **新增**：DVP → `alinx_ov5640` → AXIS16 → `axis_subset_converter`(24b) → VDMA S2MM → HP2 |
| HP2 连接 | 显示 MM2S → `pc_hp2` → HP2 | **两路合并**：显示 MM2S + 采集 S2MM → **`smc_vis`(2S/1M)** → `pc_hp2` → HP2 |
| PS7 | FCLK0=50、FCLK1=100、HP0/1/2 | **追加 I2C0 via EMIO**（SCCB） |
| `smc_ctrl` | 1S/**5M** | 1S/**8M**（M05=采集VDMA Lite、M06=相机 GPIO、M07=相机复位；M00~M04 原样） |
| 新地址 | — | 采集 VDMA **0x43C60000**、相机 GPIO **0x43C70000**、相机复位 **0x41200000**（沿用阶段3） |
| 新引脚 | — | J11/CMOS2 共 **16** 脚（见 §9） |

**唯一触及既有显示通路的地方**：在 `pc_hp2` 前插入 `smc_vis`（显示 MM2S 语义不变，仅多一级仲裁）。

---

## 3. 采集通路（与阶段3 冻结证据逐项对齐）

```
DVP(J11) cmos1_d[9:0]/href/vsync/pclk
   └─> alinx_ov5640:5.4（厂商打包 IP，ip_repo 只读引用；DEBUG_OV5640=false）
         · 内部取 cmos_d[9:2]（8b）→ cmos_8_16bit 组装为 16b RGB565
         · **PCLK→AXIS 时钟域的 CDC 在 IP 内部**（fifo_ready 同步器，BUFFER_DEPTH=4096）
   └─> axis_subset_converter:1.1  S=2B → M=3B（24b RGB888）
         TDATA_REMAP = {tdata[4:0],3'b000, tdata[10:5],2'b00, tdata[15:11],3'b000}
   └─> axi_vdma_1（S2MM，非 SG）→ smc_vis → pc_hp2(AXI4→AXI3) → S_AXI_HP2 → DDR
```

**VDMA S2MM 参数（逐项照抄阶段3 冻结 XSA）**：
`c_include_sg=0`、`c_include_s2mm=1`、`c_include_mm2s=0`、`c_include_s2mm_dre=1`、
`c_m_axi_s2mm_data_width=64`、`c_num_fstores=1`、`c_use_s2mm_fsync=2`、
`c_s2mm_linebuffer_depth=4096`、`c_s2mm_max_burst_length=128`；
**流宽 24 bit 由所连 AXIS 接口自动派生**（`C_S_AXIS_S2MM_TDATA_WIDTH` 是只读派生量，不可硬设 —— 与阶段3 相同）。

### 3.1 跨组不一致的裁定（本报告结论）
| 问题 | 结论 | 证据 |
|---|---|---|
| 阶段3 采集 VDMA 流宽 | **24 bit** | 冻结 XSA `1f5b138e…` 内 `.hwh`：`C_S_AXIS_S2MM_TDATA_WIDTH=24` |
| `c_include_sg` | **0（非 SG）** | 同上：`C_INCLUDE_SG=0` |
| 是否插 565→888 展开 | **是**，库 IP `axis_subset_converter:1.1`，`S=2B→M=3B` + 固定 TDATA_REMAP | 同上 `.hwh` |
| 写 DDR 每像素字节数 / 内存序 | **3 B/px，B,G,R**（AXIS `tdata[23:16]=R`,`[15:8]=G`,`[7:0]=B`；S2MM 把 `tdata[7:0]` 写最低地址） | 同上 + `video-sw` 的 `HSIZE=STRIDE=0xF00=3840=1280×3` 吻合 |

**位扩展规则（与阶段3 完全一致，左对齐补零）**：`R8={R5,3'b000}`、`G8={G6,2'b00}`、`B8={B5,3'b000}`。
（注意：不是 `×255/31` 的满量程缩放，低位为 0。）

---

## 4. 地址映射（validate 后实测打印，无冲突）

| 从设备 | 基址 | 范围 | 状态 |
|---|---|---|---|
| 2B 推理核 CSR | 0x43C00000 | 64 KB | 既有，未动 |
| preproc CSR | 0x43C10000 | 0x80 | 既有，未动 |
| AXI DMA（S2MM） | 0x43C20000 | 64 KB | 既有，未动 |
| 显示 VDMA AXI-Lite | 0x43C40000 | 64 KB | 既有，未动 |
| underflow GPIO | 0x43C50000 | 4 KB | 既有，未动 |
| **采集 VDMA AXI-Lite** | **0x43C60000** | 64 KB | **新增** |
| **相机状态/帧计数 GPIO** | **0x43C70000** | 4 KB | **新增** |
| **相机复位 GPIO** | **0x41200000** | 64 KB | **新增**（沿用阶段3 同址，便于软件复用） |
| HP0 / HP1 / HP2 DDR | 0x00000000 | 1 GB | 2B / preproc+DMA / 显示+采集 |

**相机 GPIO（双通道，只读）**：`+0x00` = **采集帧计数**（RTL 在 100 MHz 域数 `tuser`=SOF，每个 SOF 脉冲 +1）；`+0x08` = **采集 VDMA S2MM 当前帧指针**（`s2mm_frame_ptr_out[4:0]` 零扩展到 32 bit）。
**相机复位**：`0x41200000` bit0 → `cmos_rstn`（L19）。

---

## 5. 时钟域

| 域 | 时钟 | 承载 |
|---|---|---|
| 50 MHz | `clk_fpga_0` | 2B / preproc / 打包器 / AXI DMA / 两个 SmartConnect / **所有 AXI-Lite（含采集 VDMA Lite、相机 GPIO、相机复位）** / `rst_all` |
| 100 MHz | `clk_fpga_1` | 显示 VDMA MM/流侧、采集 VDMA MM/流侧、`alinx_ov5640` 的 AXIS 侧、subset converter、`smc_vis`、`pc_hp2`、HP2、`rst_100` |
| **cam_pclk（输入）** | K19，约束 **10.417 ns（96 MHz，OV5640 DVP 上限）** | 仅 `alinx_ov5640` 的 DVP 输入侧；**PCLK→100 MHz 的跨域由 IP 内部 FIFO 完成** |
| 74.21875 MHz | `clk_pixel_raw` | 显示 `axis_to_video` / rgb2dvi |
| 371.09375 MHz | `clk_5x_raw` | rgb2dvi OSERDESE2 |
| 50 MHz 输入 | `sys_clk`（U18） | MMCM 参考 |

实测七时钟：`clk_fpga_0` 20.000 / `clk_fpga_1` 10.000 / **`cam_pclk` 10.417** / `sys_clk` 20.000 / `clk_fb` 80.000 / `clk_pixel_raw` 13.474 / `clk_5x_raw` 2.695 ns。

---

## 6. 时序（**两轮如实记录**）

### 6.1 第一轮（无 IP 内部 CDC 约束）：不达标
- **WNS = −5.493 / TNS = −5.493 / 失败端点 = 1**（58,493 端点）→ `CRITICAL WARNING [Timing 38-282]`
- 各时钟域自身全达标（cam_pclk +3.516 / clk_fpga_0 +0.368 / clk_fpga_1 +2.471 / clk_pixel_raw +5.283），
  唯一违例是 **`cam_pclk → clk_fpga_1`** 的单条跨域路径：
```
Source:      u_bd/s4d_p3r_i/alinx_ov5640_0/inst/fifo_ready_reg_replica/C   (cam_pclk 10.417ns)
Destination: u_bd/s4d_p3r_i/alinx_ov5640_0/inst/fifo_ready_maxis_reg/D     (clk_fpga_1 10.000ns)
Requirement: 0.097 ns      数据路径: 1.411 ns (logic 0.379 / route 1.032)
```
**根因**：厂商 IP **内部**的 `fifo_ready → fifo_ready_maxis` 单比特同步器（厂商源码该寄存器已标 `(* ASYNC_REG="true" *)`），
属异步跨域被当同步分析的**假性违例**（与 P3m/P3p 同类）。

### 6.2 第二轮（加 cell 过滤 CDC 约束）：交付值
`p3r_cdc.xdc` 追加（**cell 过滤避开 12-4739**，`-datapath_only` 只限物理绕线）：
```tcl
set_max_delay -datapath_only \
  -from [get_cells -hier -filter {NAME =~ *alinx_ov5640_0*fifo_ready_reg*}] \
  -to   [get_cells -hier -filter {NAME =~ *alinx_ov5640_0*fifo_ready_maxis_reg*}] 10.417
```
| | WNS | TNS | 失败端点 | WHS |
|---|---|---|---|---|
| 第一轮（无该约束） | −5.493 | −5.493 | 1 | +0.053 |
| **第二轮（交付）** | **+0.019** | **0.000** | **0** | +0.061 |
| P3q 基线（无相机） | +0.371 | 0 | 0 | +0.036 |

**各时钟（第二轮）**：`cam_pclk` **+3.520** / `clk_fpga_0` **+0.019（限制项）** / `clk_fpga_1` **+3.089** / `clk_pixel_raw` **+4.528**。
**跨时钟（第二轮）**：`clk_fpga_1 → cam_pclk` +8.850、`cam_pclk → clk_fpga_1` **+9.180（修复前 −5.493）**、`clk_pixel_raw → clk_fpga_0` +11.518，全部 0 失败端点。

### 6.3 第三轮（build3：仅换实现策略）→ **推荐交付**
build2 的 WNS 余量只有 +0.019 ns（由 `clk_fpga_0` 域单端点决定），硅上余量过薄。
**build3 保持 synth/RTL/BD/XDC 与 build2 完全相同**，仅把 `impl_1` 策略从默认换为
**`Performance_ExplorePostRoutePhysOpt`**（多轮 post-route 物理优化探索）：

```tcl
set_property strategy Performance_ExplorePostRoutePhysOpt [get_runs impl_1]
```

| | build2 | **build3** | 目标 |
|---|---|---|---|
| `clk_fpga_0` WNS | +0.019 | **+0.342** | ≥ +0.15 ✅ |
| 总 WNS / TNS / 失败端点 | +0.019 / 0 / 0 | **+0.342 / 0.000 / 0** | ✅ |
| `cam_pclk` | +3.520 | **+4.589** | — |
| `clk_fpga_1` | +3.089 | **+2.629** | — |
| `clk_pixel_raw` | +4.528 | **+4.404** | — |
| LUT | 27,558 | **27,536** | 基本不变 |
| DRC | 436 / 0 error | **430 / 0 error** | 0 error ✅ |

**结论：build3 达标（+0.342，为 P3q 的 92%），推荐交付 build3**；不需要再做 §"区域约束"那一级措施。

**过程中遇到并已规避的环境问题（留痕）**：build3 第一次启动（`-jobs 2`）失败于
`[Vivado 12-13638] Failed runs: s4d_p3r_smc_vis_0_synth_1` + `[Common 17-354] Could not open 'C' for writing`
+ `tclapp::load_apps failed` —— 这是本机已知隐患：`Vivado_init.tcl` 会把 MCP 插件注入**每个** Vivado 进程，
并行 OOC IP 综合抢占同一本地端口。按既定策略**降为 `-jobs 1` 重跑即通过**（代价是综合+实现耗时翻倍）。
日志：`s5_p3r_build3_console.log`（失败留痕）／`s5_p3r_build3b_console.log`（成功）。

---

## 7. DRC 与告警

**DRC 436 条、0 error**：

| 规则 | 严重度 | 条数 | 说明 |
|---|---|---|---|
| `DPIP-1` / `DPOP-1` / `DPOP-2` / `DPREG-4` | Warning | 133 / 147 / 148 / 2 | DSP48 流水线建议（2B 推理核固有，阶段3/4 同） |
| `PDCN-1569` | Warning | 1 | 协议转换器 IP 内部 LUT |
| `PLCK-12` | Warning | 1 | 时钟布局检查 —— 由 `cmos1_pclk` 走**非专用时钟路由**引起（阶段3 同样用 `CLOCK_DEDICATED_ROUTE FALSE`，属预期） |
| `RTSTAT-10` | Warning | 1 | No routable loads |
| `REQP-165` / `REQP-181` | Advisory | 1 / 2 | BRAM writefirst |

**唯一 CRITICAL WARNING（无害）**：
`[Designutils 20-1280] Could not find module 'ila_0'` —— 厂商 IP 自带 `ila_0.xci`；我们按阶段3 做法把
`DEBUG_OV5640=false` 关掉内嵌 ILA（否则 >5 probe 触发许可限制），其残留 XDC 因无实例被跳过。**不影响功能**。

---

## 8. 资源对比

| 资源 | P3q（冻结集成体） | **P3r** | 增量 | 上限 |
|---|---|---|---|---|
| LUT | 24,769 (46.56%) | **27,558 (51.80%)** | **+2,789** | 53,200 |
| FF | 12,648 (11.89%) | **17,028 (16.00%)** | **+4,380** | 106,400 |
| BRAM | 35.5 (25.36%) | **43.5 (31.07%)** | **+8** | 140 |
| DSP | 158 (71.82%) | **158 (71.82%)** | 0 | 220 |
| MMCM | 1 | 1 | 0 | 4 |
| BUFG | 4 | **5** | +1 | 32 |
| OSERDESE2 | 8 | 8 | 0 | 125 |
| Bonded IOB | 10 | **24** | **+14** | 125 |

增量主体 = `alinx_ov5640`（含内部 FIFO）+ `axis_subset_converter` + 采集 VDMA + 2 个 GPIO + `smc_vis`。
LUT 51.80% 仍低于 G0 §4 的 55–61% 预算上限，DSP 与预算一致。

---

## 9. `report_io` 引脚复核

### 9.1 显示侧（与 P3q 完全一致）
| 端口 | 球位 | SITE | IOSTANDARD |
|---|---|---|---|
| `sys_clk` | U18 | IO_L12P_T1_MRCC_34 | LVCMOS33 |
| `TMDS_clk_p/n` | **N18/P19** | IO_L13P/N_T2_MRCC_34 | TMDS_33 |
| `TMDS_data_p/n[0]` | **V20/W20** | IO_L16P/N_T2_34 | TMDS_33 |
| `TMDS_data_p/n[1]` | **T20/U20** | IO_L15P/N_T2_DQS_34 | TMDS_33 |
| `TMDS_data_p/n[2]` | **N20/P20** | IO_L14P/N_T2_SRCC_34 | TMDS_33 |
| `hdmi_oen` | V16 | IO_L18P_T2_34 | LVCMOS33 |

### 9.2 相机侧（J11 / CMOS2 连接器，**全部 bank 35、LVCMOS33、FIXED**）
| 信号 | 球位 | SITE | 备注 |
|---|---|---|---|
| `cmos1_d[0]` | K17 | IO_L12P_T1_MRCC_35 | |
| `cmos1_d[1]` | K18 | IO_L12N_T1_MRCC_35 | |
| `cmos1_d[2]` | G19 | IO_L18P_T2_AD13P_35 | |
| `cmos1_d[3]` | L20 | IO_L9N_T1_DQS_AD3N_35 | |
| `cmos1_d[4]` | M20 | IO_L7N_T1_AD2N_35 | |
| `cmos1_d[5]` | M19 | IO_L7P_T1_AD2P_35 | |
| `cmos1_d[6]` | F20 | IO_L15N_T2_DQS_AD12N_35 | |
| `cmos1_d[7]` | G20 | IO_L18N_T2_AD13N_35 | |
| `cmos1_d[8]` | J18 | IO_L14P_T2_AD4P_SRCC_35 | |
| `cmos1_d[9]` | F17 | IO_L6N_T0_VREF_35 | |
| `cmos1_href` | H18 | IO_L14N_T2_AD4N_SRCC_35 | |
| `cmos1_vsync` | J19 | IO_L10N_T1_AD11N_35 | |
| `cmos1_pclk` | **K19** | IO_L10P_T1_AD11P_35 | **输入时钟**（CLOCK_DEDICATED_ROUTE FALSE，同阶段3） |
| `cmos1_i2c_sda_io` | **F16** | IO_L6P_T0_35 | **BIDIR + PULLUP** |
| `cmos1_i2c_scl_io` | **F19** | IO_L15P_T2_DQS_AD12P_35 | **BIDIR + PULLUP** |
| `cmos_rstn` | L19 | IO_L9P_T1_DQS_AD3P_35 | OUTPUT |

**引脚来源**：阶段3 冻结约束 `an5642_j11_cmos2.xdc`
（`D:\codex-worktrees\dbdf\board\stage3\hardware\an5642_j11_cmos2.xdc`，其依据为官方 `23_ov5640_dual` 的 `an5642.xdc` + AX7020 V3.0 手册 Table 7.5.1 J11 针脚表）。
**SCCB 两脚（F16/F19）属 J11/CMOS2 连接器**，经 **PS7 `I2C0` EMIO** 驱动（`PCW_EN_I2C0=1`、`PCW_EN_EMIO_I2C0=1`、`PCW_I2C0_I2C0_IO=EMIO`），沿用阶段3 的 PS I2C 软件路径。

---

## 10. HP2 带宽评估

| 项 | 速率 | 依据 |
|---|---|---|
| **相机写**（640×480 @ 24bpp @ 30 fps） | **27.6 MB/s** | 640×480×3×30 = 27,648,000 B/s |
| **显示读**（1280×720 @ 32bpp @ 60 fps） | **221.1 MB/s** | 1280×720×4×59.97 |
| **合计（HP2）** | **≈248.7 MB/s** | |
| HP2 峰值（100 MHz × 64 bit） | 800 MB/s | PS7 HP 端口 |
| 实测有效效率约 47.5%（P3b/P3m 实测 ~190 MB/s@50 MHz 折算） | ≈380 MB/s | |
| **占用率** | **≈65%** | 248.7 / 380 |

**结论：可行，但余量不宽（约 35%）**。且 HP2 与 **HP0（2B 直连）/ HP1（preproc+DMA）共用同一颗 DDR**，
实际退化**必须板测**——尤其 P2d 基线的 **2B 单帧 47,287 ms** 是否因显示+采集并发变慢，须如实记录，不做优化掩盖。

---

## 11. I/O delay 约束（相机 DVP 输入侧）

`p3r.xdc` 中已加（R-02-3 §2.2 草案的落地，**声明式**）：
```tcl
create_clock -period 10.417 -name cam_pclk [get_ports cmos1_pclk]   # OV5640 DVP PCLK 上限 96 MHz 的保守值
set_input_delay -clock cam_pclk -max 2.500 [get_ports {cmos1_d[*]}]
set_input_delay -clock cam_pclk -max 2.500 [get_ports cmos1_href]
set_input_delay -clock cam_pclk -max 2.500 [get_ports cmos1_vsync]
set_input_delay -clock cam_pclk -min 1.500 [get_ports {cmos1_d[*]}]
set_input_delay -clock cam_pclk -min 1.500 [get_ports cmos1_href]
set_input_delay -clock cam_pclk -min 1.500 [get_ports cmos1_vsync]
```
**⚠️ 数值性质**：**保守占位值**，假定"数据在 PCLK 上升沿后 ≤2.5 ns 稳定、保持 ≥1.5 ns"。
**本地仓库没有 OV5640/AN5642 数据手册**（`R-02-3 §2.2` 本身也把 tSU/tH 留空写"待按模组手册页码核对后填入"），
因此**不编造页码**；按 R-02-3 的 V4 条款，须以**手册 AC 特性表页码 + 板级走线延迟（约 6 ps/mm）**核对后正式签核。
本版**不声称 I/O 时序已签核**。

### 11.1 `cam_pclk` 实际频率（与 video-sw 覆盖表核对）
- **设计意图：84 MHz**（阶段3 实机测得 1280×720 时 PCLK ≈ 84 MHz，见 `R-07` 方案 §1 与 `R-02` 记录）；
- video-sw 的 640×480 覆盖表沿用**同一组 PLL 分频** `0x3035=0x21 / 0x3036=0x69`（与阶段3 720p 相同），
  即 PLL/VCO 不变，故预期 640×480 模式下 PCLK **仍在 84 MHz 量级**；
- **但本地没有任何 640×480 模式的实测 PCLK 记录**（仓库内只有寄存器清单，无测量值），
  因此**不声称 84 MHz 已确认**；
- **约束按 96 MHz 保守**（`create_clock -period 10.417`，OV5640 DVP PCLK 上限），
  即"**按 84 MHz 设计意图、按 96 MHz 保守约束**"——两种情形下都满足，无需改约束；
- 待板窗用 SDC/计数器或示波器实测 `K19` 后，若确认 84 MHz，可把周期放宽到 11.905 ns 换取更多 I/O 时序余量（**非必须**）。

### 11.2 拿到手册后如何替换占位值（一行模板）
```tcl
# tCO_max / tCO_min：OV5640 数据手册 AC Characteristics（DVP timing）表给出的 PCLK→DATA 输出延迟（ns）
# skew：板级走线延迟差（约 6 ps/mm × 走线长度差），四对数据/同步相对 PCLK 的最大差值
set_input_delay -clock cam_pclk -max [expr {<tCO_max> + <skew>}] [get_ports {cmos1_d[*] cmos1_href cmos1_vsync}]
set_input_delay -clock cam_pclk -min [expr {<tCO_min> - <skew>}] [get_ports {cmos1_d[*] cmos1_href cmos1_vsync}]
```
替换时**必须在报告里写明手册版本与页码/节号**（R-02-3 §2.2 的 V4 签核要求）。

---

## 12. 软件接口（给 `video-sw`）

| 项 | 值 |
|---|---|
| **采集 VDMA AXI-Lite** | **0x43C60000** |
| 写几何（raw ABI） | **640×480、BGR888（3 B/px）、stride 1920、帧 921,600 B** |
| **目标地址** | **0x12000000** |
| VDMA 模式 | S2MM-only、**非 SG**、`c_num_fstores=1`、MM 64-bit、流 24-bit（派生）、fsync=2 |
| 相机 GPIO | **0x43C70000**：`+0x00` 采集帧计数、`+0x08` 采集 VDMA 当前帧指针 |
| 相机复位 | **0x41200000** bit0 → `cmos_rstn`（阶段3 同址） |
| SCCB | **PS7 I2C0（EMIO）**，沿用阶段3 的 PS I2C 驱动与器件地址；勿用 PL AXI IIC |
| 显示链 | **完全不变**（帧存 A/B 0x20000000/0x20384000、1280×720/32bpp/stride 5120、VDMA 0x43C40000） |
| 2B/preproc/DMA | **完全不变**（0x43C00000 / 0x43C10000 / 0x43C20000） |

**数据通路（Lead 2026-10-31 澄清）**：相机只负责填 raw 区；CPU 读 raw → 缩放渲染到帧存 → 显示 VDMA 读帧存 → TMDS。**不存在显示几何不匹配**。

---

## 13. 未验证项 / 风险（如实记录）

1. **⚠️ 全部功能未上板验证**：相机出图、SCCB 初始化、VDMA 写入、采集帧计数、显示、2B 推理均未在硬件上跑过。
2. **⚠️ DDR 并发带宽未测**：HP0/HP1/HP2 并发时 2B 单帧耗时与显示/采集速率须实测；预期影响方向未知。
3. **WNS 余量**：build2 仅 +0.019 ns（过薄）；**build3 已改善到 +0.342 ns**（推荐交付），仍比 P3q 的 +0.371 略低但同量级。
4. **⚠️ I/O delay 为保守占位**：未按手册 AC 表签核（本地无手册），V4 必做。
5. **`cam_pclk` 实际频率未知**：约束按 96 MHz 上限；实际由软件配置的 OV5640 PLL 决定（640×480 时通常更低）。若软件把 PCLK 配到 >96 MHz，需更新约束。
6. **`cmos_d[9:0]` 中 IP 只用 `[9:2]`**：D[1:0] 未使用（阶段3 同），引脚仍按 10 bit 全部约束。
7. **采集 VDMA fsync=2**：沿用阶段3；若采集侧帧节奏与相机不同步的策略有差异，需软件确认语义。
8. `tlast_misalign`（显示链诊断）仍未引出 GPIO（P3q 遗留），需要时加第二个 GPIO。
9. 未做 ILA 观测；未做叠加。

---

## 14. 产物与哈希（SHA-256）

| 文件 | 字节 | SHA-256 |
|---|---|---|
| **`out\build3\s4d_p3r_r01.bit`（推荐交付）** | **4,045,762** | **`648f31567e0a20916020b3dd33b649cd4de9ac1b5cd2534b6552d8427dcb9f4e`** |
| **`out\build3\s4d_p3r_r01.xsa`（推荐交付）** | **418,950** | **`1284f637438af3485ba7508b2443bb44b78f5d4a99d440d28c94bf3beabf3f81`** |
| `out\s4d_p3r_r01.bit`（build2，保留） | 4,045,762 | `6202872e5958ee388e3df2825cb309dd420aaa4824e655317a3d09d6607dfb8c` |
| `out\s4d_p3r_r01.xsa`（build2，保留） | 418,944 | `7b26a487abe00c70daa47dc64ea1766f075423dc5e22692ffcee4db89daaa3d6` |
| `bd_p3r_b3.tcl`（build3 脚本） | — | 见目录 |
| `bd_p3r.tcl` | — | `f40bcda05f73f27c9a31852583b5d5821a91ea68327275f933879179695131b3` |
| `p3r.xdc` | — | `fce251d18155a81dcc260a5ba231c9fb148132116a70841f2a28ed392d93eade` |
| `p3r_cdc.xdc` | — | `b685b3eabe0907bebc4b6a49835e2087fcab0f763d7de849b817d4af03310a8d` |
| `rtl\top_p3r.v` | — | `bb7a6804afd24c004eb2b3b797248e3927f1ebdcc8dc2d15f8f2de83f760d8c8` |
| `rtl\axis_to_video.v` | — | `52d09b89edc0d01952cb6891c289123210ce23be22177cc8542aea7ad97e1867` |
| `s5_p3r_build2_20261031_r01_console.log` | — | `28ede381b4f8df8c79f09c5c0efc14ed3811c90c1867cee8d1a68601bd398fe6` |

**两轮留痕**：第一轮（时序不达标 −5.493）日志 `s5_p3r_build_20261031_r01_console.log` 已保留；
第二轮（交付 +0.019）日志 `s5_p3r_build2_20261031_r01_console.log`。

**边界**：未上板、未烧 QSPI、未 push；未改动 P2d/P3a~P3q 各目录；厂商 IP 仅通过 `ip_repo_paths` **只读引用**，未复制、未修改。

---

## 15. ★ build4：修 PS7 UART 时钟缺失 + `cmos_rst` 默认值（2026-10-31 追加）

### 15.1 缺陷（板级从 `ps7_init.c` 反查，Lead 发现，**确认成立**）
build3（及 P3q/P2d 继承）的 `ps7_init.c` 里：
```
EMIT_MASKWRITE(0XF800012C, 0x01FFCCCDU ,0x014C000DU),      ← build3 / P3q
```
字段表（`ps7_init.c` 自带注释逐位给出）：
`bit18 I2C0_CPU_1XCLKACT=1`、`bit19 I2C1=1`、**`bit20 UART0_CPU_1XCLKACT=0`**、**`bit21 UART1_CPU_1XCLKACT=0`**、`bit22 GPIO=1`、`bit24 SMC=1`
⇒ **两路 UART 的外设时钟都没开**，应用用 P3r 自己的 `ps7_init` 时会在 UART 初始化处卡死、无串口输出。

### 15.2 改动（仅 BD 参数，无 RTL / 无引脚改动）
| 项 | build3 | **build4** |
|---|---|---|
| `PCW_EN_UART1` / `PCW_UART1_UART1_IO` | 0 / — | **1 / `MIO 48 .. 49`** |
| `PCW_UART1_BAUD_RATE` | — | **115200** |
| `PCW_EN_UART0` / `PCW_UART0_UART0_IO` | 0 / — | **1 / `MIO 46 .. 47`** |
| `PCW_UART0_BAUD_RATE` | — | **115200** |
| `cmos_rst` `C_DOUT_DEFAULT` | 0x0 | **0x1**（复位后默认释放） |
| `PCW_I2C_RESET_ENABLE` | 0 | **1**（与阶段3 对齐） |
| `PCW_EN_EMIO_I2C0` / `PCW_I2C0_I2C0_IO` | 1 / EMIO | **保持 1 / EMIO**（未动） |

### 15.3 自检（新 XSA `ps7_init.c` 原文）
```
EMIT_MASKWRITE(0XF800012C, 0x01FFCCCDU ,0x017C000DU),      ← build4（3 处一致）
```
| bit | 字段 | 值 | 判定 |
|---|---|---|---|
| 18 | I2C0_CPU_1XCLKACT | 1 | PASS |
| **20** | **UART0_CPU_1XCLKACT** | **1** | **PASS** |
| **21** | **UART1_CPU_1XCLKACT** | **1** | **PASS** |
| 22 | GPIO_CPU_1XCLKACT | 1 | PASS |
| 24 | SMC_CPU_1XCLKACT | 1 | PASS |

另自检：新 XSA `.hwh` 中 `cmos_rst: C_DOUT_DEFAULT=0x00000001`、`C_ALL_OUTPUTS=1`；
`PCW_EN_EMIO_I2C0=1`、`PCW_I2C0_I2C0_IO=EMIO` 保持正确；
`PCW_EN_UART0=1 / UART0_IO=MIO 46 .. 47 / 115200`、`PCW_EN_UART1=1 / UART1_IO=MIO 48 .. 49 / 115200`。

### 15.4 ⚠️ 重要口径：板载串口是 **UART1**，不是 UART0
证据：阶段3 的 PS7 配置**只使能 UART1**（`PCW_EN_UART1=1`、`PCW_UART1_UART1_IO {MIO 48 .. 49}`、`PCW_EN_UART0=0`），
而阶段3 实机 **COM4/115200 抓到 105 B / 4 行诊断输出**
（`report/evidence/S3-T04/t04_camera_build_20261020_r03/board_pretest_record.md` 第 25/30 行；
`report/evidence/S3-CTRL/S3-T05/t05_hw_20261020_r01/S3CTRL-20261020-001-stage3-jtag-com4-usage.md`）。
⇒ **板的 USB-UART 物理接在 MIO48/49 = UART1 功能**。

因此：
- **真正能出日志的是 UART1**（base `0xE0001000`，`XPAR_XUARTPS_1`）；
- UART0 被同时使能，是为了满足"APER_CLK bit20=1"的自检，并让"应用若按 UART0 设备号运行"至少不会因时钟关闭而卡死；
  但 **UART0 的 MIO46/47 在板上原属 USB0-RST / SD0-CD**（阶段3 的 MIO 分配表），
  本版 PS7 未使能 USB0/SD0，故无功能冲突；**若将来要开 USB0/SD0，必须先撤掉 UART0**；
- **软件提醒**：若 BSP 是从本 XSA 重新生成，Xilinx BSP 的 stdout 默认会选**第一个可用 UART（UART0）**，
  那样 `xil_printf` 会走到 MIO46/47（板上非串口）⇒ **必须显式把 stdout 设为 `ps7_uart_1`**，
  或应用直接用 `XPAR_XUARTPS_1`。**这是本次最容易被忽略的坑。**

### 15.5 build4 交付数据
| 项 | 值 |
|---|---|
| **WNS / TNS** | **+0.342 ns / 0.000** |
| **失败端点 / 总端点** | **0 / 58,492** |
| **WHS / THS** | +0.053 / 0.000 |
| DRC | **430 条、0 error**（与 build3 完全一致） |
| 资源 | LUT **27,536 (51.76%)**、BRAM **43.5 (31.07%)**、DSP **158**、IOB **24**、BUFG **5**、MMCM 1 |
| 日志 | 0 ERROR / 1 CRITICAL WARNING（仍是无害的 `ila_0`） |
| impl 策略 | `Performance_ExplorePostRoutePhysOpt`，`-jobs 1`（避开 MCP 插件端口冲突） |
| **bit** | `out\build4\s4d_p3r_r01.bit` **4,045,762 B** `e86efef68a55389ca515e2b15d2e57b203055dfd017f5a85e4156d282628a460` |
| **XSA** | `out\build4\s4d_p3r_r01.xsa` **436,460 B** `d2d2447c38aad621656780239112d995ff9eab113c11e65d6058e610a1a7a1b2` |

> **推荐交付：build4**（build2/build3 全部保留，产物分别在 `out/`、`out/build3/`、`out/build4/`）。
> 时序与 build3 完全相同（+0.342 / 0 失败端点），差异只在 PS7 UART 与 GPIO 默认值。

---

## 16. ★ build5：PS7 DDR 512 MiB → 1 GiB（**真根因修复**，2026-10-31 追加）

### 16.1 根因（Lead + video-sw 联合定位，确认成立）
P2a 首次建 PS7 时 DDR 器件选错，之后 P2d → P3q → P3r 一路继承：
`MT41J128M8 JP-125` / 8 bit / 1024 MBit / `PCW_DDR_RAM_HIGHADDR=0x1FFFFFFF` ⇒ **DDR 窗口只有 512 MiB**。
而我们的帧存 A/B（`0x20000000` / `0x20384000`）、结果块（`0x20800000`）都在 512 MiB 之上
⇒ **AXI 解码错误 ⇒ 数据中止**（CPSR=0x1D7 的 ABT 模式、PC 落低地址、UART 无任何打印），
与 r05/r06/r09/r10/r13 的全部现象吻合。**这一条与相机/中断都无关。**

### 16.2 改动（只有 PS7 DDR 参数；RTL/BD 结构与引脚均未变）
逐项照抄阶段3 冻结 XSA（`1f5b138e…`），不估算：

| 参数 | build4 | **build5** |
|---|---|---|
| `PCW_UIPARAM_DDR_PARTNO` | MT41J128M8 JP-125 | **MT41J256M16 RE-125** |
| `PCW_DDR_RAM_HIGHADDR` | 0x1FFFFFFF | **0x3FFFFFFF（1 GiB）** |
| `PCW_DDR_RAM_BASEADDR` | 0x00100000 | 0x00100000 |
| `PCW_UIPARAM_DDR_BUS_WIDTH` | 32 Bit | 32 Bit |
| 派生 `DEVICE_CAPACITY` | 1024 MBits | **4096 MBits** |
| 派生 `DRAM_WIDTH` | 8 Bits | **16 Bits** |
| 派生 `ROW_ADDR_COUNT` | 14 | **15** |
| 派生 `T_FAW` / `T_RC` | 30.0 / 48.75 | **40.0 / 48.91** |
| 板级/封装延迟（`PCW_PACKAGE_DDR_*`、`*_PACKAGE_LENGTH`、`BOARD_DELAY*`） | 另一套 | **阶段3 值** |

### 16.3 自检（必查项，全部 PASS）
**① `.hwh` 参数**
```
PCW_UIPARAM_DDR_PARTNO          = MT41J256M16 RE-125
PCW_DDR_RAM_BASEADDR            = 0x00100000
PCW_DDR_RAM_HIGHADDR            = 0x3FFFFFFF      ← 1 GiB ✅
PCW_UIPARAM_DDR_BUS_WIDTH       = 32 Bit
PCW_UIPARAM_DDR_DEVICE_CAPACITY = 4096 MBits   PCW_UIPARAM_DDR_DRAM_WIDTH = 16 Bits
PCW_UIPARAM_DDR_ROW_ADDR_COUNT  = 15           PCW_UIPARAM_DDR_T_FAW = 40.0  PCW_UIPARAM_DDR_T_RC = 48.91
```
**② `ps7_init.c` 与阶段3 逐位比对（DDR 相关）**
- **DDR 控制器 + DDR PHY 区（`0xF8006000`–`0xF80060FF`）：两版各 40 条写入，逐地址 100% 一致（差异 0）** ✅
- 全量 `EMIT_MASKWRITE` 比对：仅 1 处 DDR 邻域地址不同 —— `0xF8000B00`（阶段3 写 `VREF_EN=1`，属 **OCM REMAPPING** 段，与 DDR 无关，是阶段3 有 QSPI/OCM 配置所致）⇒ **DDR 相关差异 = 0**
- 其余非 DDR 差异全部可解释：`0xE00000xx`=UART0 寄存器（build5 额外启用 UART0）、`0xE000A2xx`=PS GPIO（阶段3 启用我们不用）、`0xF8000110/118/140/14C/150/154/168/170/180`=PLL/分频（FCLK0/1 配置不同）、`0xF8000700/704`=MIO0/1（阶段3 的 QSPI）
- **`0xF800012C`**（APER_CLK_CTRL）：build5 = `0x017C000D` ⇒ bit18(I2C0)=1、**bit20(UART0)=1**、**bit21(UART1)=1**、bit22(GPIO)=1、bit24(SMC)=1 ✅

### 16.4 build5 交付数据
| 项 | 值 |
|---|---|
| **WNS / TNS** | **+0.342 ns / 0.000** |
| **失败端点 / 总端点** | **0 / 58,492** |
| **WHS / THS** | +0.053 / 0.000 |
| DRC | **430 条、0 error** |
| 资源 | LUT **27536**、FF **16900**、BRAM **43.5 (31.07%)**、DSP **158**、IOB **24**、BUFG **5**、MMCM **1** |
| impl 策略 | `Performance_ExplorePostRoutePhysOpt`、`-jobs 1` |
| **bit** | `out\build5\s4d_p3r_r01.bit` **4,045,762 B** `da89789ba9f57db6d44d1212717fb812987d1f115274f05ccdc396d98eb645bc` |
| **XSA** | `out\build5\s4d_p3r_r01.xsa` **436,525 B** `3e8d56e2de327c985957aea65db50473952cb03eac9e1d86471b6dd5639cced1` |

> **推荐交付：build5**（build2/3/4 全部保留）。相机与显示路径未改，仅修 DDR 窗口。

### 16.5 ★ 遗留 R-16：全部历史 XSA 的 DDR 参数都是错的（交付面）
只读扫描 `D:\tmp\lead\*\out\*.xsa`（15 份）：**从 P2a、P2b、P2c_r01/r02、P2d、P3b、P3c、P3f、P3g、P3h、P3m、P3n、P3p、P3q（冻结 `dfefc883…`）到 P3r build2，全部为 `MT41J128M8 JP-125` / `HIGHADDR=0x1FFFFFFF`（512 MiB，错）**。
对照真值（1 GiB）：阶段3 冻结 XSA `1f5b138e…` 与 2B `s2b_inference.hwh` 均为 `MT41J256M16 RE-125` / `0x3FFFFFFF`（对）。

**影响与处理**：
- 全部板上流程用的是 **stage-4 `init.elf`（1 GiB）**，因此**已交付的板上证据不受影响**；
- 但下游若用这些 XSA 自带的 `ps7_init`（512 MiB）自行 bring-up，就会踩同一坑（写 `0x20000000+` 数据中止）；
- **交付说明必须写明**："P2a→P3r build4 的 XSA `ps7_init` 为 512 MiB，必须配 1 GiB 的 `init.elf`；修正件为 **P3r build5** 与（计划中的）**`s4d_p3q_ddrfix`**"；
- **P3q 修正件另行立 RunId `s4d_p3q_ddrfix_20261031_r01`，不替换已冻结的 stage5-freeze 记录**（冻结件保持原样，以勘误说明指向修正件）。

---

## 17. ★ SCCB 通道选择（build7/build8）与 PS I2C0 已知限制（R-17）· 2026-10-31

### 17.1 背景：PS7 I2C0（EMIO）→ 引脚路径实测不可用
| 证据 | 结论 |
|---|---|
| build5（`out/build5`）实机 | PS7 I2C0 能发出 SCL，但**收不到任何 ACK**（`scan found=0`、`ISR=0x9`=COMP+TO、`SR=0x20`=RXDV、无 NACK/无 ARB_LOST） |
| build7（`out/build7`）实机 | 该路径**无时钟输出**（`BA=0` 总线空闲、`TO=1`） |
| 结构核查（本报告 §15、§16 及本轮） | wrapper IOBUF 端口映射（`I/O/T`）与 BD `port_maps`、`interface_net` 与阶段3 冻结件**逐字一致**；`ps7_init.c` 的 **I2C0 寄存器写入与阶段3 差异 = 0 处**；27 项 I2C 参数仅 2 项派生差异（`I2C_PERIPHERAL_FREQMHZ`、`I2C_RESET_SELECT`，且 Vivado 拒绝写入，不影响 `ps7_init`） |
| 尝试过的修复 | build6 对齐那 2 项 → **参数不可设**，`ps7_init` I2C 写入仍与阶段3 零差异 |

⇒ **判定：这是 PS7 EMIO I2C0 控制器路径本身的已知限制**（非接线笔误、非可 5 分钟修复的 T/I 极性错误），登记 **R-17**，**不再为它重建位流**。

### 17.2 最终方案：`gpio_sccb` 手动 SCCB 主控（已实测可读 CHIPID）
在 PL 侧新增 `axi_gpio`（`gpio_sccb`）与顶层 `IOBUF + mux`，**软件可直接读引脚真实电平并 bit-bang**：

| 地址 | 读/写 | 位定义 |
|---|---|---|
| **`0x43C80000`** | 写（ch1，3 bit 输出） | `bit0`=mode（**1=手动**，0=PS7 直通）· `bit1`=SCL 拉低 · `bit2`=SDA 拉低 |
| **`0x43C80008`** | 读（ch2，8 bit 输入） | build7：`bit0`=SCL 电平 · `bit1`=SDA 电平；**build8 扩展**：`bit2`=PS7_SCL_O `bit3`=PS7_SCL_T `bit4`=PS7_SDA_O `bit5`=PS7_SDA_T `bit6`=回传PS7 的 SCL_I `bit7`=回传PS7 的 SDA_I |

**mux 语义**：`mode=0` 时 `SCL/SDA` 的 `O/T` 完全由 PS7 的 EMIO I2C0 驱动（与 build5/stage-3 同路径，直通、不改行为）；
`mode=1` 时改为 open-drain 手动：拉低 = `I=0,T=0`（驱动 0），释放 = `T=1`（高阻，靠上拉）。
**build8 默认值 = `0x1`（mode=1、两线均释放）** ⇒ 复位后引脚为高阻、由上拉拉高，**软件即使不写也处于可 bit-bang 的安全状态**。

**板级实测（build7）**：手动模式 9 脉冲恢复 → bit-bang 读 CHIPID = **`0x5640`** ✅
⇒ 模组、排线、引脚、上拉**全部正常**，问题确属 PS7 I2C0 路径。

### 17.3 build7（测试通道版，已验证）
| 项 | 值 |
|---|---|
| WNS/TNS/失败端点 | **+0.186 / 0.000 / 0**（58,967 端点），WHS +0.055 |
| DRC | 438 条、0 error |
| 资源 | LUT 27,564 / FF 17,155 / BRAM 43.5 / DSP 158 / IOB 24 / BUFG 5 |
| **bit** | `out\build7\s4d_p3r_r01.bit` **4,045,771 B** `3ae13e42f19f9d08ce3cd463b30f3a5a33893c85f47ed1dda111b228ac8a26a9` |
| **XSA** | `out\build7\s4d_p3r_r01.xsa` **438,619 B** `55194a75689b398c217a018499b0adf48b54f3784aac5145ed3268843b92ea18` |

### 17.4 **build8（正式交付件）** = build7 + 3 点正式化
1. `gpio_sccb` **默认值 0x1**（复位即手动、两线释放、靠上拉为高）；
2. `sccb_level` 由 2 bit 加宽到 **8 bit**（向后兼容，bit0/1 语义不变）；
3. `ps_i2c_*` 6 个信号整理为内部网（**不接任何引脚**，仅服务 mode=0 直通路径，报告标注为 R-17 限制）。

| 项 | 值 |
|---|---|
| **WNS / TNS** | **+0.042 ns / 0.000** |
| **失败端点 / 总端点** | **0 / 59,038** |
| **WHS / THS** | +0.053 / 0.000 |
| DRC | **439 条、0 error** |
| 资源 | LUT **27,632 (51.94%)** / FF 17,207 / BRAM 43.5 / DSP 158 / IOB 24 / BUFG 5 |
| 自检 | `gpio_sccb` 在 **0x43C80000**（validate 打印 `SEG_gpio_sccb_Reg offset=0x43C80000`）；DDR `MT41J256M16 RE-125` / `HIGHADDR=0x3FFFFFFF`；APER=`0x017C000D` |
| **bit** | `out\build8\s4d_p3r_r01.bit` **4,045,765 B** `7acea72617024db9cf2540e22fb422f1f6f8fe302cc8afa1a99c4f3372922a2d` |
| **XSA** | `out\build8\s4d_p3r_r01.xsa` **438,635 B** `07728bd2cf900891371e168371d718fa09d0bfec0c1caf149d59b97c503eac75` |

> ⚠️ **WNS 余量说明**：build8 只有 **+0.042 ns**（build7 为 +0.186），差异来自布局/时序种子；**0 失败端点、DRC 0 error 均满足**。若需要更厚余量，可再换实现种子重跑一版（约 30–35 min），不影响功能。

### 17.5 软件接口（给 `video-sw`，已单独给伪代码）
- 写 `0x43C80000 = 0x1` 进入手动（build8 复位默认已是 0x1）；
- 拉低 SCL：`0x3`（base|0x2）；拉低 SDA：`0x5`（base|0x4）；都拉低：`0x7`；释放回 `0x1`；
- 读 `0x43C80008`：`bit0`=SCL 真实电平、`bit1`=SDA 真实电平；
- 半周期建议 ≥ **5 µs**（≈100 kHz），释放 SDA 后采样前**多等一拍**（上拉弱、上升慢）；
- SCCB 16-bit 读序列：9 脉冲恢复 → START → `0x78` → 寄存器高/低字节 → repeated START → `0x79` → 读 2 字节 → NACK → STOP；
  CHIPID 期望 `0x300A/0x300B = 0x56/0x40`。

---

## 18. ★★ R-07 根因：S2MM `tuser`(SOF) 未接到 VDMA（build10b2 修复）· 2026-10-31

### 18.1 根因（BD 网表实证，build2~build9 一直存在）
```
build9  : [net] axis_subset_converter_0_m_axis_tuser : [converter/m_axis_tuser, cam_sof]
          axi_vdma_1/s_axis_s2mm_tuser = 悬空（不在任何 net 中）
阶段3   : 无独立 tuser 网 —— tuser 由 AXIS 接口自动接入 VDMA ✅
```
- `axi_vdma_1` 的 `C_USE_S2MM_FSYNC=2`（**用 tuser 作帧同步/SOF**）⇒ tuser 恒 0 时 VDMA
  永远等不到帧首 ⇒ `SR = 0x14810`（`ERR_INTERNAL 0x10` + `ERR_FSZ_MORE 0x800`）、
  `frmcnt=1`、`raw` 全 0，且**与几何（VSIZE/HSIZE/STRIDE）无关**。
- 来源：P3q 起为观测 SOF 计数，把 `axis_subset_converter_0/m_axis_tuser` 单独接到 `cam_sof` 计数器；
  IPI 因此把该 pin 从 AXIS 接口网里摘出（日志长期有 `[BD 41-1271] ... m_axis_tuser has been
  overridden by the user. This pin will not be connected as a part of the interface connection`），
  VDMA 端随之悬空。**阶段3 没有这个计数器，所以没有该缺陷。**

### 18.2 修复方式（build10b2）
- **tdata 保持走 AXIS 接口**（关键：`c_s_axis_s2mm_tdata_width` 是不可写派生量，若把 tdata 也拆成
  标量，VDMA 流宽会退化成 32 并触发 `[BD 41-2383]` 宽度不匹配 —— build10 实测踩到过，已废弃）；
- 仅对 4 个 1-bit 信号做"**converter 端 + VDMA 端显式同网 + 观测端口**"：
```
axis_subset_converter_0_m_axis_tuser  : [converter/m_axis_tuser, conv_tuser, axi_vdma_1/s_axis_s2mm_tuser]
axis_subset_converter_0_m_axis_tlast  : [converter/m_axis_tlast, conv_tlast, axi_vdma_1/s_axis_s2mm_tlast]
axis_subset_converter_0_m_axis_tvalid : [converter/m_axis_tvalid, conv_tvalid, axi_vdma_1/s_axis_s2mm_tvalid]
axi_vdma_1_s_axis_s2mm_tready         : [axi_vdma_1/...tready, conv_tready, converter/m_axis_tready]
```
- 顶层 `assign cam_sof = conv_tuser;` ⇒ **SOF 计数器（`0x43C70000+0x00`）与 VDMA 同时得到 tuser**。

### 18.3 ★ 另一项 IP 级关键事实：厂商 IP 内部有 3.6 s 就绪等待
`my_ip/ov5640_ip/src/alinx_ov5640.v`（只读）：
```verilog
if (reset_cnt < 32'd200_000_000) begin reset_cnt <= reset_cnt+1; cmos_aresetn <= 1'b0; end
else cmos_aresetn <= 1'b1;                                     // 200M PCLK 后释放内部复位
else if (fifo_ready_cnt < 32'd100_000_000) ... fifo_ready <= 1'b0;  // 再 100M PCLK
wr_en = s_axis_tvalid & fifo_ready;                            // 期间一个数都不写
```
⇒ **PCLK 连续跑满 300,000,000 周期（84 MHz 下≈3.6 s）之前，FIFO 不写、AXIS 无数据**；
`reset_cnt` 无复位输入 ⇒ **每次重下位流都重新计时**。
**板级必须"启动 sensor 流后等 ≥6 s（建议 8–10 s）再判 VDMA"。**
另：`m_axis_video_aresetn` 在该 IP 内部**完全未被使用**（仅端口声明），故它不可能是复位卡死点；
build10b2 仍把它引出到 `0x43CD0000` 供确认 rst_100 已释放。

### 18.4 IP 极性/信号生成（用于软件寄存器核对）
```verilog
s_axis_tlast  <= cmos_hblank_d0 & ~cmos_hblank;                  // hblank<=href ⇒ href 下降沿 = 行尾
s_axis_tuser  <= 1 on (cmos_vsync_d1==1 && cmos_vsync_d0==0);    // vsync 下降沿 = 帧首
s_axis_tvalid =  cmos_href_16bit_d1 & cmos_hblank_d1 & s_axis_tready;
```
⇒ 要求 **href 高有效、vsync 高有效（下降沿=帧首）、PCLK 上升沿采样**；与阶段3 的 `0x4740=0x20` 默认极性一致。
IP **自带** `m_axis_video_tuser/tlast` 输出 ⇒ **无需外部 tlast/tuser 生成 RTL**（阶段3 也没有）。

### 18.5 build10b2 交付与自检
| 项 | 值 |
|---|---|
| **WNS / TNS / 失败端点** | **+0.313 ns / 0.000 / 0**（63,345 端点），WHS +0.050 |
| DRC | 437 条、0 error |
| 资源 | LUT 28,693 (53.93%) / FF 20,134 / BRAM 43.5 / DSP 158 / IOB 24 / BUFG 5 |
| VDMA | `C_S_AXIS_S2MM_TDATA_WIDTH=24`（无宽度告警）、`C_USE_S2MM_FSYNC=2`、`C_INCLUDE_S2MM_DRE=1`、`C_INCLUDE_SG=0` |
| DDR | `MT41J256M16 RE-125` / `HIGHADDR=0x3FFFFFFF`（1 GiB） |
| APER | `0x017C000D`（bit18/20/21=1） |
| **bit** | `out\build10b2\s4d_p3r_r01.bit` **4,045,767 B** `44bc86ed4657d914baab3144837bd40c47f0ec350822218e78a5060ce1270233` |
| **XSA** | `out\build10b2\s4d_p3r_r01.xsa` **448,740 B** `314289913d5ec6067258eca204738e160512411bca6add8e2e7b5f53037611d3` |

### 18.6 观测寄存器总表（build10b2）
| 地址 | 含义 |
|---|---|
| `0x43C80000+0x00` | SCCB 手动控制（bit0 mode / bit1 SCL 拉低 / bit2 SDA 拉低） |
| `0x43C80000+0x08` | SCCB 电平：[0]SCL [1]SDA [2]PS7_SCL_O [3]PS7_SCL_T [4]PS7_SDA_O [5]PS7_SDA_T [6]SCL_I [7]SDA_I |
| `0x43C90000+0x00 / +0x08` | PCLK 上升沿计数 / HREF 期间 PCLK 计数（cam_pclk 域） |
| `0x43CA0000+0x00` | VSYNC 边沿：[15:0]=上升、[31:16]=下降 |
| **`0x43CB0000+0x00 / +0x08`** | **S2MM tlast 脉冲数 / S2MM tuser(SOF) 脉冲数** |
| **`0x43CC0000+0x00 / +0x08`** | **`tvalid&&tready` 有效拍数 / `tvalid&&!tready` 反压拍数** |
| **`0x43CD0000+0x00`** | **IP `m_axis_video_aresetn` 电平（bit0，应=1）** |
| `0x43C70000+0x00 / +0x08` | SOF 计数（=tuser 计数）/ VDMA S2MM 当前帧指针 |
所有计数器均为 `clk_100`(S2MM aclk) 或 `cam_pclk` 域采集，经格雷码两级同步到读出域（`clk_50`/`clk_100`）。

---

## 19. S2MM 帧同步语义与 build11a（FSYNC=0 free-run）· 2026-10-31

### 19.1 r37 定量（warmup 8.26 s 窗，build10b2）
| 观测 | 实测 | 理论期望 | 判读 |
|---|---|---|---|
| `tlast` 计数 | +5,579 ⇒ **675/s** | 行数×fps：960 行 ⇒ 14,400/s；480 行 ⇒ 7,200/s | **量级不符** |
| 有效传输拍（`tvalid&&tready`） | +7,582,466 ⇒ **918k/s** | 1280×960×15fps ⇒ 18.4M/s（24bpp 一拍≈1 px） | **仅 1/20** |
| `SR`（冷启动） | `0x10000` | — | 干净 |
| `SR`（热运行） | `0x14810` = ERR_INTERNAL(0x10)+ERR_FSZ_MORE(0x800)+Err_Irq(0x4000)+…  | 无错误位 | **帧边界不成立** |
| 四种几何（480/960 行 × 2560/3840 行宽） | 错误完全相同 | 若几何是主因则应不同 | **几何非主因** |

### 19.2 `C_USE_S2MM_FSYNC` 语义
| 值 | 语义 |
|---|---|
| 0 | **free-run**：VDMA 收到 `RS=1` 即按 `HSIZE/VSIZE` 连续收数据，用 **tlast** 作行结束、按行数凑满 VSIZE 即完成一帧；**不使用 tuser** |
| 1 | 使用 `s2mm_fsync` 输入（外部帧同步信号） |
| 2 | **使用 `tuser` 作帧首同步（SOF）**：每个帧必须在正确位置看到 tuser，否则帧起点错位、判 `FSZ_MORE`/内错 |

build10b2 为 `=2`。r37 已证明 tuser 能到 VDMA（`tuser` 计数增长、`cam_sof` 大增），但帧起点仍错位 ⇒ **tuser 的时序/极性/位置与 VDMA 期望不一致**（IP 的 tuser 只在 vsync 下降沿置 1 并保持到首个有效拍）。改用 free-run 可**完全绕开 tuser 语义**，这是 AXIS Video 通路最常用的稳定配置。

### 19.3 build11a 改动（唯一功能改动）
`axi_vdma_1`：`c_use_s2mm_fsync` **2 → 0**（其余与 build10b2 逐字相同；tuser 引脚做条件连接，仍引出供计数器）。

### 19.4 build11a 交付
| 项 | 值 |
|---|---|
| **WNS / TNS / 失败端点** | **+0.140 ns / 0.000 / 0**（63,167 端点），WHS +0.056 |
| DRC | 436 条、0 error |
| 资源 | LUT 28,657 (53.87%) / FF 20,034 / BRAM 43.5 / DSP 158 / IOB 24 / BUFG 5 |
| VDMA | **`C_USE_S2MM_FSYNC=0`**、`C_S_AXIS_S2MM_TDATA_WIDTH=24`、`C_INCLUDE_S2MM_DRE=1`、`C_INCLUDE_SG=0`、`C_S2MM_SOF_ENABLE=1`、`C_FLUSH_ON_FSYNC=1` |
| DDR / APER | `MT41J256M16 RE-125` / `HIGHADDR=0x3FFFFFFF`；`0x017C000D` |
| **bit** | `out\build11a\s4d_p3r_r01.bit` **4,045,767 B** `378521254047ef4af656e9c98379dc1f5cb4d7677d329f87f5748aed1cbb11cb` |
| **XSA** | `out\build11a\s4d_p3r_r01.xsa` **448,736 B** `8e72c826a50479cc1eba77823a4381b00de04dfbacb018fdf429a50c58490e4c` |

### 19.5 用计数器反推正确几何（r38 若仍 FSZ_MORE 时直接套用）
设 `R_tl` = `0x43CB0000+0x00` 的 tlast 速率（/s）、`R_tv` = `0x43CC0000+0x00` 的有效拍速率（/s）、`fps` = `0x43CA0000+0x00` 高 16 位（VSYNC 下降沿）之速率：
```
每帧行数 VSIZE = round(R_tl / fps)
每行像素     = HPSIZE / 3  ← 其中 HSIZE(字节) = round(R_tv / R_tl * 3)
```
（24bpp 下一拍 = 1 像素 = 3 字节；若传感器实际输出 1280×960，则应得 VSIZE≈960、HSIZE=3840。）

### 19.6 过程记录：一次脚本事故
首次 build11a 启动时生成脚本用大写 `C_USE_S2MM_FSYNC` 作替换锚点，而 build10b 脚本里实际是小写 `c_use_s2mm_fsync`，断言失败 ⇒ tcl 未生成 ⇒ Vivado 19:28:27 秒退（`couldn't read file ... bd_p3r_b11a.tcl`）。修正锚点后 19:33 重跑成功即本次交付；两次日志均在 `s5_p3r_build11a_console.log`（前 1 KB 为秒退记录）。

---

## 20. build11b：IP 输出侧计数器（定位"零拍"根因）· 2026-10-31

### 20.1 build11a（FSYNC=0）实测结果与关键反常
- **成功**：`FSZ_MORE(0x800)/ERR_INTERNAL(0x10)` 全部消失，cold/hot `S2MM_SR` 均为 `0x10000`、四组几何 `err=0x0`
  （注：`0x10000` 是 **bit16，不在错误位段**——`XAXIVDMA_SR_ERR_ALL_MASK=0x00000FF0`，见 `axivdma_v6_17/src/xaxivdma_hw.h`），
  说明"帧同步语义"这条已修好；
- **反常**：所有 AXIS 计数器归零（`TL_TLAST=0`、`TL_TUSER=0`、`TAP_VALID` 冻结在 0x55、`TAP_BP=0`），
  而 sensor 侧完全正常（15.0 fps、每帧 1,228,800 px、PCLK 84 MHz、`IP_RST=1`）。

### 20.2 网表核查：build11a 的连线没有被拆（否定"条件连接拆网"的假设）
build11a 与 build10b2 的 1-bit 网表**逐字相同**：
```
axis_subset_converter_0_m_axis_tlast  : [converter/m_axis_tlast, conv_tlast, axi_vdma_1/s_axis_s2mm_tlast]
axis_subset_converter_0_m_axis_tuser  : [converter/m_axis_tuser, conv_tuser, axi_vdma_1/s_axis_s2mm_tuser]
axis_subset_converter_0_m_axis_tvalid : [converter/m_axis_tvalid, conv_tvalid, axi_vdma_1/s_axis_s2mm_tvalid]
axi_vdma_1_s_axis_s2mm_tready         : [axi_vdma_1/...tready, conv_tready, converter/m_axis_tready]
[intf] axis_subset_converter_0_M_AXIS : [converter/M_AXIS, axi_vdma_1/S_AXIS_S2MM]
```
且 FSYNC=0 时 VDMA **仍保留 tuser 引脚**（构建脚本打印 `P3R11A_CHECK VDMA 仍有 tuser 引脚，已连接`）。

### 20.3 厂商 IP 的关键门控关系（解释"零拍"）
`my_ip/ov5640_ip/src/alinx_ov5640.v`：
```verilog
assign m_axis_video_tvalid = ~empty & m_axis_video_tready;   // tvalid 被 tready 门控！
assign s_axis_tvalid = cmos_href_16bit_d1 & cmos_hblank_d1 & s_axis_tready;
wr_en = s_axis_tvalid & fifo_ready;                          // 写 FIFO 也依赖 tready
```
⇒ **只要下游不拉高 tready，IP 连 FIFO 都不写**，整条链零拍。
r38 的 `TAP_VALID=0x55`（几十拍后冻结）与"linebuffer 填满 → tready 落下"一致。

### 20.4 build11b 改动与交付
新增 IP 输出侧 4 个 1-bit 信号（**IP 端 + converter 端显式同网 + 观测口**，tdata 仍走 AXIS 接口）：

| 地址 | 内容 |
|---|---|
| `0x43CE0000 +0x00` | IP `m_axis_video_tvalid` 拍数 |
| `0x43CE0000 +0x08` | IP `m_axis_video_tlast` 拍数 |
| `0x43CF0000 +0x00` | IP `m_axis_video_tuser` 拍数 |
| `0x43CF0000 +0x08` | **IP `m_axis_video_tready` 高电平拍数**（VDMA 是否在收，最关键） |

（axi_gpio 单实例仅 2 通道，故拆 0x43CE0000/0x43CF0000 两块；`0x43CB/CC/CD` 语义不变。）

| 项 | 值 |
|---|---|
| **WNS / TNS / 失败端点** | **+0.133 ns / 0.000 / 0**（65,361 端点），WHS +0.052 |
| DRC | 436 条、0 error |
| 资源 | LUT 29,162 (54.82%) / FF 21,546 / BRAM 43.5 / DSP 158 / IOB 24 / BUFG 5 |
| VDMA / DDR | `C_USE_S2MM_FSYNC=0`、`C_S_AXIS_S2MM_TDATA_WIDTH=24`、DRE=1；DDR `MT41J256M16 RE-125`/1 GiB |
| **bit** | `out\build11b\s4d_p3r_r01.bit` **4,045,767 B** `ba0f7009a29c651f152389f0de30ed03ec7702bf9ff9684c676753964ab460db` |
| **XSA** | `out\build11b\s4d_p3r_r01.xsa` **452,785 B** `c3866d954afa6055c7b7a1f48b9571d303058ba3bc393abec5b6633bfab2e1b8` |

### 20.5 r39 判读表
| IP `tready` 高拍数 | IP `tvalid` 拍数 | 结论 |
|---|---|---|
| ≈0 | ≈0 | **VDMA 从不拉 tready** ⇒ 问题在 VDMA 启动/S2MM 配置（非 IP、非 converter） |
| 增长 | ≈0 | IP 内部 FIFO 空/未写 ⇒ IP 的 `fifo_ready`/内部复位/溢出 |
| 增长 | 增长 | IP 正常出数 ⇒ 查 converter 侧 `0x43CC0000+0x00` 与 `frmcnt/raw` |

---

## 21. S2MM 通道"永远在复位"→ VDMA 复位域修正（build11c/d/e）· 2026-10-31 夜

### 21.1 r48 的硬证据
软件写入 `S2MM_CR`（`0x43C60030`）后读回恒为 `0x10004`（含 **bit2 = XAXIVDMA_CR_RESET_MASK = 0x4**），写 `0/1/8` 都不改变 bit2
⇒ **S2MM 通道被硬件按在复位里**，`RS(bit0)` 无法维持。这与"IP 侧 tready 一直高但 beat 不落 DDR、CR 清不掉"完全一致。

### 21.2 逐个排除的假设（都有实测/网表证据）
| 假设 | 结论 | 证据 |
|---|---|---|
| 厂商 IP 的 `s_axis_*` 输入端口悬空 | **否定** | IP 只有 12 个端口，`s_axis_*` 全是内部信号（`src/alinx_ov5640.v` 端口列表） |
| VDMA `*_prmry_resetn` 未连接被 tie 0 | **否定** | `axi_vdma_1` 只有 `axi_resetn` 一个复位端口（hwh 实测），且已连 `rst_all/peripheral_aresetn` |
| `C_PRMY_IS_ACLK_ASYNC` 未置位 | **否定** | 该参数在该 IP 上**不存在**（`get_property` 读回空） |
| `rst_all/peripheral_aresetn` 未释放 | **否定** | 同域 `gpio_sccb`/`smc_ctrl`/`gpio_cam*` 均正常工作 |
| `c_s2mm_sof_enable=1` 与 `c_use_s2mm_fsync=0` 冲突 | **已尝试**（build11c） | 仍 `SR=0x10000`、`CR` 复位位不变，非根因 |
| **时钟/复位域错配** | **唯一剩余结构差异，build11e 修** | 见 21.3 |

### 21.3 结构差异（阶段3 vs 本工程）
| | 阶段3（实测能写 DDR） | build11c |
|---|---|---|
| VDMA `s_axi_lite_aclk` | FCLK1（150 MHz） | **FCLK0（50 MHz）** |
| VDMA `s_axis/m_axi_s2mm_aclk` | FCLK1（150 MHz） | FCLK1（100 MHz） |
| VDMA `axi_resetn` 来源 | `rst_…_150M`（**与数据面同域**） | `rst_all`（**50 MHz 域**） |

⇒ 阶段3 是"三个时钟同域 + 同域复位"；本工程 50/100 混用且复位在 50 MHz 域。
`axi_resetn` 为"异步置位/同步释放"，其同步释放所依赖的时钟与数据面时钟不同源时，
VDMA 内部 datamover 复位同步器可能**永不释放** ⇒ 正好呈现 `CR.RESET` 恒 1、寄存器写不进。

### 21.4 build11c / build11e 交付
| | build11c | **build11e** |
|---|---|---|
| 改动 | `c_s2mm_sof_enable=0`、`c_flush_on_fsync=0` | 同 build11c + **`axi_vdma_1/axi_resetn` 由 `rst_all` 改接 `rst_100`（100 MHz 域）** |
| WNS/TNS/失败端点 | +0.133 / 0 / 0 | **+0.237 / 0 / 0**（65,343） |
| DRC | 436、0 error | **437、0 error** |
| 资源 | LUT 29,162 / FF 21,546 | LUT 29,126 / FF 21,533 / BRAM 43.5 / DSP 158 |
| **bit** | `out\build11c\s4d_p3r_r01.bit` 4,045,767 B `50e974144dbfc48ba03a6492d6aed8dd1cce6c6574006583d8b2337e2635589c` | `out\build11e\s4d_p3r_r01.bit` 4,045,767 B `c74a1fd44a71e4a8a8780067054d3134600a115f411783d471ecff2f4e3d598b` |
| **XSA** | 452,789 B `59a59ffe36df…` | **452,787 B** `a03ec9769aac5ebec51fd4f50f18b604c5ec3d12cde56516ff41a57936fd9a14` |

build11e BD 网表实测：`axi_vdma_1/axi_resetn` 所在 net 成员 = `{rst_100/peripheral_aresetn, cam_aresetn_ip, alinx_ov5640_0/m_axis_video_aresetn, smc_vis/aresetn, axi_vdma_1/axi_resetn, pc_hp2/aresetn}`（**100 MHz 域** ✅）。

### 21.5 r49 判据
- **`0x43C60030` 写 1 后读回应为 `0x00000001`**（bit2 自清零）= 通道脱离复位；
- 若仍含 bit2 ⇒ 上 **build11f（结构性对齐）**：在 `smc_ctrl`(50 MHz) 与 `axi_vdma_1/S_AXI_LITE` 间插入 `axi_clock_converter`，使 VDMA 三个时钟全部为 FCLK1(100 MHz)、复位全部 `rst_100`（= 阶段3 同域结构）。

### 21.6 build11d（IP 内部探针）已废弃但保留产物
`out/build11d`（未完成，r48 找到更直接根因后主动停止）；其 RTL 副本 `rtl/p3r_ov5640_dbg.v`、`rtl/p3r_cmos_8_16bit.v` 保留备用（厂商源码副本，仅加只读探针，未改功能）。

---

## 22. build11f：时钟/复位电平观测（判断"复位未释放"）· 2026-10-31 深夜

### 22.1 背景
r49a：`clear_reset` 后 `S2MM_CR` 仍 `0x10004`（bit2=RESET 恒 1）、`start` 后仍 `0x10004`；`S2MM_SR` 已变干净（`0x10000`）。
而 build11e 已把 `axi_vdma_1/axi_resetn` 从 `rst_all`(50 MHz 域) 改到 `rst_100`(100 MHz 域)，仍未解决
⇒ 需要直接观测两个复位的电平与两路 FCLK 是否在动。

### 22.2 已提前确认（build11e/11f 的 XSA `.hwh`）
```
PCW_FPGA0_PERIPHERAL_FREQMHZ = 50      PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ = 50.000000
PCW_FPGA1_PERIPHERAL_FREQMHZ = 100     PCW_ACT_FPGA1_PERIPHERAL_FREQMHZ = 100.000000
PCW_EN_CLK0_PORT = 1  PCW_EN_CLK1_PORT = 1  PCW_FPGA_FCLK0_ENABLE = 1  PCW_FPGA_FCLK1_ENABLE = 1
PCW_FCLK1_PERIPHERAL_CLKSRC = IO PLL  DIVISOR0 = 6  DIVISOR1 = 3  PCW_FCLK_CLK1_BUF = TRUE
```
⇒ **FCLK1 已使能且为 100 MHz**（"FCLK1 未使能"假设排除）。
另外显示链路的 `smc_vis`/`pc_hp2` 同样挂在 `rst_100` 上且工作正常（fps=60）⇒ `rst_100` 大概率已释放。

### 22.3 build11f 新增观测（全只读、不接任何引脚）
| 地址 | 内容 |
|---|---|
| `0x43D40000+0x00` | `bit0`=`rst_100/peripheral_aresetn`、`bit1`=`rst_all/peripheral_aresetn` 电平 |
| `0x43D40000+0x08` | FCLK0（50 MHz）上升沿计数（clk_50 域自由运行） |
| `0x43D50000+0x00` | FCLK1（100 MHz）上升沿计数（clk_100 域自由运行） |

构建时网表断言实测：
```
P3R11F_LEN rst_100/peripheral_aresetn pin 数=1 ; rst_all/... pin 数=1
P3R11F_LEN gpio_obs_a/gpio_io_i / gpio2_io_i / gpio_obs_b/gpio_io_i 均=1
P3R11F_NET rst_100/peripheral_aresetn -> /Net
P3R11F_NET rst_all/peripheral_aresetn -> /rst_all_peripheral_aresetn
SEG_gpio_obs_a_Reg offset=0x43D40000 ; SEG_gpio_obs_b_Reg offset=0x43D50000
```

### 22.4 build11f 交付
| 项 | 值 |
|---|---|
| **WNS / TNS / 失败端点** | **+0.300 ns / 0.000 / 0**（67,803 端点），WHS +0.056 |
| DRC | 439 条、0 error |
| 资源 | LUT 29,833 (56.08%) / FF 23,165 / BRAM 43.5 / DSP 158 / IOB 24 / BUFG 5 |
| VDMA / DDR | `C_USE_S2MM_FSYNC=0`、`C_S2MM_SOF_ENABLE=0`、`C_FLUSH_ON_FSYNC=0`、24 bit；DDR 1 GiB |
| **bit** | `out\build11f\s4d_p3r_r01.bit` **4,045,767 B** `4ae379a9aa2dd4ca69e12032eff8f4606104411c595bb3adfb55cf1f924e6313` |
| **XSA** | `out\build11f\s4d_p3r_r01.xsa` **497,794 B** `46dfdf7e7a719a3672f4a0397612222ac6257b3ef0a18974bc746cb7ab8898a0` |

### 22.5 r50 判读与后续预案
1. `0x43D40000+0x00` 的 `bit0`（rst_100）：**若=1 ⇒ 复位已释放，CR bit2 恒 1 与复位无关**，问题回到 VDMA 寄存器/软件层；
2. `0x43D40000+0x08` 与 `0x43D50000+0x00` 两次读差应 >0（FCLK0/1 均在动）；
3. 若 1、2 都正常，后续二选一：
   - **软件侧最小验证**：对 `0x43C60030` 做最原始 `Xil_Out32` 写入后立即读 `0x43C60034`(SR) / 再读 `0x43C60030`，并读 `0x43C60038`(CURDESC)，排除寄存器映射/写保护问题；
   - **build11g（已备好脚本骨架）**：用全新实例名 `axi_vdma_cam` 重新生成 VDMA（同参数 S2MM-only / FSYNC=0 / DRE / 24 bit，地址仍 `0x43C60000`），排除旧 XCI/缓存异常。

### 22.6 过程记录（三次脚本返工，均为生成脚本的引用顺序问题，非设计问题）
1. `rst_100`/`rst_all` 的引脚在脚本前段尚不存在 ⇒ `[BD 41-701] connect_bd_net requires at least two pins/ports`；
2. 改到末尾块后，`M16/M17_AXI` 仍在前段连接（此时 `gpio_obs_*` 未创建）⇒ `[BD 5-106] Arguments to connect_bd_intf_net cannot be empty`；
3. 将 `M16/M17` 一并移入末尾块后一次通过（v3）。

---

> **今晚结论交接文档**：见 `NIGHT_HANDOFF_20261031.md`（R-07 状态、已排除假设 15 条、build2→build11g 与 sha、板级窗口 r37→r52、build11g 判据、明早两条备选路径、未完成事项）。

---

## 23. build11g（重建实例+三路同域，**中断**）与 build11h（参考设计逐字回归）· 2026-11-01 凌晨

### 23.1 关键新证据：拿到厂商参考设计的**逐字参数**
参考源：`D:\codex-worktrees\dbdf\tmp\3\S3-T05\t05_timing36_project_impl_20261026_r01\vendor_src\pl_config.tcl`
（厂商 `22_ov5640_single` 的 BD 生成脚本，171 行，板上验证可用；对应 BD `...\ov5640_single.srcs\sources_1\bd\design_1\design_1.bd`）

```tcl
# L89-L100  axi_vdma_1（S2MM-only）
CONFIG.c_include_mm2s {0}  CONFIG.c_include_s2mm_dre {1}  CONFIG.c_m_axi_s2mm_data_width {64}
CONFIG.c_num_fstores {1}   CONFIG.c_s2mm_genlock_mode {0}
CONFIG.c_s2mm_linebuffer_depth {4096}  CONFIG.c_s2mm_max_burst_length {128}
CONFIG.c_use_s2mm_fsync {2}        ;# ★未设 C_S2MM_SOF_ENABLE / C_FLUSH_ON_FSYNC ⇒ 默认 1
# L187  rst_100M/peripheral_aresetn (AXI-Lite 时钟域) -> axi_vdma_1/axi_resetn
# L182  FCLK0(100M) -> axi_vdma_*/s_axi_lite_aclk ；L183 FCLK1(150M) -> 数据面 aclk
# L157/L154  axi_vdma_1/M_AXI_S2MM -> axi_mem_intercon/S01 -> M00 -> S_AXI_HP0
# L197  axi_vdma_1 地址 = 0x43010000
```
**结论**：参考设计与本工程用的是**同一个 IP 版本 `axi_vdma:6.3`**（此前说的"阶段3 v6.17"是**驱动** `axivdma_v6_17`）；而 build11a/11c/11e 把 `c_use_s2mm_fsync`、`C_S2MM_SOF_ENABLE`、`C_FLUSH_ON_FSYNC`、`axi_resetn` 域**4 项全部改离了参考值**。

### 23.2 build11g（中断，现场保留）
- 设计：全新实例 `axi_vdma_cam` + `axi_clock_converter`（AXI-Lite 50→100 MHz）+ 三路 aclk 全 FCLK1 + `axi_resetn=rst_100`
- 构建前两轮失败（脚本层，已修）：`[BD 5-106]`（`gpio_obs_c` 创建顺序）、`[BD 41-237]`（时钟转换器 `PROTOCOL` 需 `AXI4LITE` 而非 `AXI4`）
- 第三轮 BD validate 通过、网表断言正确（三路 aclk 全 `ps7_0_FCLK_CLK1`），但在 OOC 综合阶段按 lead 决策**中断**（因参数仍是 FSYNC=0/SOF=0/FLUSH=0，与"零 beat"的 11e/11f 同类，命中率低）；`out/build11g/` 现场保留
- 附带收获：Vivado 自动打印 `All clocks connected to AXI VDMA are not identical, therefore configuring AXI-VDMA in ASYNC mode`（`vdma_0` 同样如此却工作正常）⇒ **异步/同步模式是 IP 自动派生的**，故 `CONFIG.C_PRMY_IS_ACLK_ASYNC` 读不到值；"时钟域混用导致复位不释放"的解释进一步被削弱

### 23.3 build11h（交付）：参考设计 4 项全部回归
改动 = build11f + 3 处（全部回归参考值）：
1. `CONFIG.c_use_s2mm_fsync {2}`
2. 删除 `C_S2MM_SOF_ENABLE=0` / `C_FLUSH_ON_FSYNC=0` 覆盖 ⇒ 恢复默认 **1**
3. `axi_vdma_1/axi_resetn` 改回 `rst_all/peripheral_aresetn`（= 本工程 AXI-Lite 时钟域）

| 项 | 值 |
|---|---|
| **WNS / TNS / 失败端点** | **+0.191 ns / 0.000 / 0**（67,550 端点），WHS +0.059 |
| DRC | **431 条、0 error** |
| 资源 | LUT 29,854 (56.12%) / FF 23,026 / BRAM 43.5 / DSP 158 / IOB 24 / BUFG 5 |
| `.hwh` 实测参数 | `C_USE_S2MM_FSYNC=2`、`C_S2MM_SOF_ENABLE=1`、`C_FLUSH_ON_FSYNC=1`、`C_S_AXIS_S2MM_TDATA_WIDTH=**24**`、`C_INCLUDE_SG=0`、`C_INCLUDE_S2MM_DRE=1`、地址 `0x43C60000`、DDR `0x3FFFFFFF` |
| **bit** | `out\build11h\s4d_p3r_r01.bit` **4,045,767 B** `2ca55cf3903464f57916fa856394b4c891fcb041eac967b37f42a5e4fbdf9407` |
| **XSA** | `out\build11h\s4d_p3r_r01.xsa` **497,798 B** `e1d7bf7c8901c7ca823dd56e085fbe3c50f7dda1632c5c31afabe10142714411` |

**诚实说明等价关系**：build11h 的参数集 **≈ build10b2**（即"唯一真正收到 beat 的一版"：27.6M beat/s、tlast 正常），差别是多了 0x43C8..0x43D6 全套观测寄存器、且基线更干净。故 r52 应重点看 **`CfgInitialize`/`CR`/`SR(FSZ_MORE)`/`frmcnt`/`raw`**，而不是 beat 数（beat 预期恢复）。

### 23.4 r52 判读与下一步
1. `CfgInitialize` 是否 **0**；`CR` 写 1 读回是否 **`0x00000001`**；
2. `SR`（`0x43C60034`）是否仍有 `FSZ_MORE(0x800)`/`INTERNAL(0x10)`；
3. `frmcnt`/`cam_frmptr32` 是否递增、`raw` 是否非零。
- 若"**beat 恢复但 DDR 仍不写、SR 仍 FSZ_MORE**" ⇒ 问题转向 **S2MM 帧几何语义**（HSIZE/VSIZE/STRIDE/FRMPTR 与 `tlast`/`tuser` 的对齐），下一个 build 应加 **tlast 周期计数 + VSIZE/HSIZE 回读观测**（`0x43D7`），而不是继续替换 IP。
- 备选：`PLAN_STAGE3_CAPTURE_PORT.md` §4 的 **build11i**（用 `axi_interconnect:2.1` 替代 `smc_vis` 做相机 S2MM→HP2 通道）。

---

## 24. build11i（tuser 整形+测量）与 build11k（tuser 与首拍 tvalid 同拍）· 2026-11-01 凌晨

### 24.1 build11i：SOF 整形 + 行/帧结构测量
- 新增 `tuser_gen`：`cmos_vsync` 下降沿 → PCLK 域翻转 → clk_100 两级同步 + 边沿检测 → **每帧单拍脉冲**，直接驱动 `axi_vdma_1/s_axis_s2mm_tuser`（converter 的 tuser 仍进 `conv_tuser` 计数口）
- 新增测量：`0x43D70000+0x00`（两次 tlast 间 beat 数 = 实际行像素）、`+0x08`（两次 tuser 间 tlast 数 = 实际每帧行数）；`0x43D80000+0x00`（整形 tuser 计数）、`+0x08`（vsync 下降沿计数）
- 交付：bit `e3400600…`（4,045,767 B）/ XSA 501,853 B；资源 LUT 30,395 / FF 24,563
- **问题**：WNS **−5.284**。逐条核对：全设计仅 11 条违规，且 100% 在新增两个 2 级同步器上（10 条 → `vsf_g1_reg`、1 条 → `sof_t1_reg/D`）——既有的 `p3r_cdc_b9.xdc` 用 `*vf_g1_reg` 匹配，**匹配不到新加的 `vsf_g1_reg`**（多一个 s）。功能不受影响（`r05` 测量全部正确）。
- 修复：新增 `p3r_cdc_b11i.xdc`（`-datapath_only 10.000`，覆盖 `*vsf_r_reg[*]→*vsf_g1_reg[*]→*vsf_g2_reg[*]`、`*sof_tgl_reg→*sof_t1_reg→*sof_t2_reg`），并挂进 `read_xdc` 序列。

### 24.2 r05/r09 的关键测量结论（流侧完全正确）
`1280 px/行`、`720 行/帧`、`30 fps`、`tuser 与 vsync 1:1`，但 `S2MM_SR` 的 `FSZ_MORE` 每帧复现、DDR 仍不落 ⇒ 唯一嫌疑转向"注入的 tuser 落在消隐期，VDMA 采样不到 SOF"（AXIS：tuser 仅在 tvalid 有效时被采样）。

### 24.3 build11k：tuser 与帧首拍 tvalid 同拍
```verilog
parameter TUSER_MODE = 1;              // 1=同拍(默认) / 0=直连脉冲(11i/11j 行为，一行可切回)
reg sof_pending;
assign s2mm_tuser_gen = (TUSER_MODE != 0) ? (sof_pending & conv_tvalid) : sof_pulse;
assign tuser_ev       = (TUSER_MODE != 0) ? (s2mm_tuser_gen & hs_beat)   : sof_pulse;
// clk_100：sof_pulse -> sof_pending=1；sof_pending & conv_tvalid -> 该拍 tuser=1 且同拍清 pending
```
新增探针：`0x43DA0000+0x00`（tuser→首 tlast beat，应≈1280）、`+0x08`（末 tlast→下一 tuser beat，应=0）；`0x43DB0000+0x00`（每帧总 beat，应=921,600）、`+0x08`（pending 卡住帧数）。

### 24.4 build11k 交付
| 项 | 值 |
|---|---|
| **WNS / TNS / 失败端点** | **+0.379 ns / 0.000 / 0**（72,400 端点），WHS +0.052 |
| DRC | **432 条、0 error** |
| 资源 | LUT 30,746 (57.79%) / FF 26,283 / BRAM 43.5 / DSP 158 / IOB 24 |
| `.hwh` | `FSYNC=2`、`SOF_ENABLE=1`、`FLUSH_ON_FSYNC=1`、`TDATA=24` |
| **bit** | `out\\build11k\\s4d_p3r_r01.bit` **4,045,767 B** `f1c9b5738f70bb9e1cc758eb3659807e4407dedf65040ead2ade98260cc6876c` |
| **XSA** | `out\\build11k\\s4d_p3r_r01.xsa` **507,705 B** `8cc340f7302da4a7e25fc4f2c9fac248e3290a658c530c286dc6a5f3afc8e940` |
| **ps7_init** | `p3r_build11k_ps7_init.tcl` **27,602 B** `0c07e86f807a27405aca9e8d11ef91a74cb051f641dc49ca44fcdc7888ea00f2`（与 build11i 相同 ⇒ PS7 配置未变） |

### 24.5 工程教训（已落实为流程）
1. **改 RTL 前先 `xvlog.bat rtl/<top>.v` 过一遍**（<10 s）。build11k 首次构建失败就是 RTL 层问题，白等 35 min。
2. 失败类型与修法（本次共 4 类）：
   - 补丁残留导致**同一组 reg/wire 声明两份** → 从"已验证 top"重新生成，而非继续打补丁；
   - 名字先出现在 wrapper 端口连接里 → 被**隐式声明成 1 bit**，之后显式声明 32 bit 冲突 → 在端口列表后**统一提前声明**，后续一律 `assign`；
   - 遗留 `cam_sof` / `clk_100` / `clk_50` 声明位置在使用之后 → 提前声明 + 删除后置声明。
3. 构建脚本引用顺序（`rst_100`/`gpio_obs_*`/`Mxx_AXI` 必须在创建之后连接）——见 §22.6/§23.2。

---

## 25. build11k 退化与 build11l（tuser_shaper 模块，仿真驱动）· 2026-11-01 清晨

### 25.1 build11k 退化（板级实测）
`TUSER_SHAPED` 120 s 仅 **1**（b11i ≈4880）、`VSYNC_NEG` 也变成 **1**（b11i ≈4880）、`CAM: frm=0`。
⇒ 从 b11i **重新生成** RTL 时把 PCLK 域的 vsync 计数/整形链打断了（不是"同拍条件难满足"）。
根因：为避免重复/隐式声明冲突，对声明做了批量重排，连带影响了 PCLK 域计数链。

### 25.2 流程改进（已执行）
**先仿真、后构建**。整形逻辑抽成独立模块 `rtl/tuser_shaper.v` + `rtl/tb_tuser_shaper.v`，用 `xvlog/xelab/xsim` 验证：
```
xvlog exit=0   xelab exit=0   xsim exit=0
frame_cnt=3  tuser_xfer=3  a0=8  a1=0  b0=32  b1=0   TB_RESULT: PASS
```
仿真抓到并修掉 2 个真问题：
1. TB 在时钟沿之后采样（把已清零的 pending 当成结果）→ 改为 **negedge 驱动/采样**；
2. DUT `a0`（tuser→首 tlast 的 beat 数）**少 1**：tlast 那一拍未计入 → latch 时 `+1`。

### 25.3 build11l 设计（对 b11i 的最小增量）
- **base = `top_p3r_b11j.v`**（b11i + SOF 相位），**b11i 的 PCLK 通路 `cmos1_vsync→vsync_d2→vsf_r→格雷码→vsf_g1/g2→VSYNC_NEG` 一行未动**
- **唯一功能改动**：`s2mm_tuser_gen` 由 `sof_pulse` 改为 `tuser_shaper.tuser`
- `tuser_shaper`：全 clk_100(FCLK1) 域；`sof_pending` 由 `sof_pulse` 置位、由 `conv_tvalid` 消费、`tuser = sof_pending & conv_tvalid`（与帧首拍同拍）；`TUSER_MODE=0` 一行回退
- 探针：`0x43DA/0x43DB` 四根由**模块寄存器输出**驱动

### 25.4 build11l 交付
| 项 | 值 |
|---|---|
| 仿真 | `xvlog/xelab/xsim` 均 exit 0，`TB_RESULT: PASS` |
| **WNS / TNS / 失败端点** | **+0.211 ns / 0.000 / 0**（73,522 端点），WHS +0.059 |
| DRC | **437 条、0 error** |
| 资源 | LUT 30,897 (58.08%) / FF 26,818 / BRAM 43.5 / DSP 158 / IOB 24 |
| `.hwh` | `FSYNC=2`、`SOF_ENABLE=1`、`FLUSH_ON_FSYNC=1`、`TDATA=24`、VDMA 地址 `0x43C60000` |
| **bit** | `out\\build11l\\s4d_p3r_r01.bit` **4,045,767 B** `bebd435e0f3d3bf5604c73aa2c8cc242b3a6390f46640942cb0a5b99db5cee53` |
| **XSA** | `out\\build11l\\s4d_p3r_r01.xsa` **507,701 B** `fa157c69d3bdded46eee16160e44b23fb45fbe7a8783f5b601741e335bb4e868` |
| **ps7_init** | `p3r_build11l_ps7_init.tcl` **27,602 B** `0c07e86f…`（与 11i/11k 一致 ⇒ PS7 未变） |

### 25.5 r12 判据（先验 b11k 退化是否已恢复）
1. `0x43D80000+0x08`（`mes_vsync_cnt`）应回到 ≈**4880**/120 s（b11i 水平）；
2. `0x43D80000+0x00`（`mes_tuser_cnt`）≈ 同上；
3. `0x43DA0000+0x00` ≈1280、`+0x08`=0、`0x43DB0000+0x00`=921600、`+0x08`=0；
4. `CAM: sr_after_1s` 干净、`0x12000000` 非零 ⇒ 相机通。

---

## 26. ★★ R-07 真正根因：`pc_hp2` 被配成 READ_ONLY（build11o 修复）· 2026-11-01 清晨

### 26.1 现象（r12/r13，build11l/11m）
- AXIS 侧**完全正确**：`TUSER2TLAST=1280`、`TLAST2TUSER=0`、`FRAME_BEATS=921600`、`VSYNC=TUSER=5142/120s`、`STALL=0`、几何 720 行/1280 px/30 fps
- 但 `CAM_SR=0x14810` = `bit4`(**DATAMOVER INTERNAL ERROR**) + `bit11`(**FSZ_MORE**) + `bit14`(Err_Irq)，`0x12000000` 全 0
- 从 build11g 起每次构建都有一条告警：
  `WARNING [smartconnect-1.0-1] smc_vis: S01_AXI is WRITE_ONLY connects to endpoint(s) on M00_AXI which are READ_ONLY`

### 26.2 根因
`bd_p3r_*.tcl` 中：
```tcl
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_protocol_converter pc_hp2
set_property -dict [list \
  CONFIG.SI_PROTOCOL {AXI4} CONFIG.MI_PROTOCOL {AXI3} \
  CONFIG.READ_WRITE_MODE {READ_ONLY}          ;# ← 根因
  CONFIG.DATA_WIDTH {64} CONFIG.ADDR_WIDTH {32} ] [get_bd_cells pc_hp2]
```
`pc_hp2` 是通往 `S_AXI_HP2` 的唯一通路，**READ_ONLY** 是 build2 时代"只做显示 MM2S 读 DDR"时的遗留配置。
相机 S2MM 接入同一通路后，**写事务在 HP2 入口被协议转换器丢弃** ⇒ AXI 写响应错误 ⇒ datamover INTERNAL ERROR + FSZ_MORE + DDR 全 0；AXIS 侧无任何异常，因此长期被误判为"SOF 相位/复位/时钟"问题。

### 26.3 修复（build11o，1 行）
```diff
- CONFIG.READ_WRITE_MODE {READ_ONLY}
+ CONFIG.READ_WRITE_MODE {READ_WRITE}
```
其余 = build11m（保留 smartconnect；b11j base 的 PCLK 通路、`tuser_shaper` 同拍、全部探针、FSYNC=2/SOF_EN=1/FLUSH=1、TDATA=24、VDMA `0x43C60000`、CDC XDC）。

### 26.4 验证证据
- **第一判据**：`S01_AXI is WRITE_ONLY` 告警由"每次必现" → **0 条**；
- `.hwh`：`pc_hp2 READ_WRITE_MODE = READ_WRITE`；
- 网表：`axi_vdma_1/M_AXI_S2MM → smc_vis/S01_AXI → smc_vis/M00_AXI → pc_hp2/S_AXI → pc_hp2/M_AXI → ps7_0/S_AXI_HP2`（链路完整）。

### 26.5 build11o 交付
| 项 | 值 |
|---|---|
| **WNS / TNS / 失败端点** | **+0.104 ns / 0.000 / 0**（80,933 端点），WHS +0.053 |
| DRC | **433 条、0 error** |
| 资源 | LUT 32,001 (60.15%) / FF 28,492 / BRAM 44.5 / DSP 158 / IOB 24 |
| `.hwh` | `FSYNC=2`、`SOF_ENABLE=1`、`FLUSH_ON_FSYNC=1`、`TDATA=24`、`pc_hp2=READ_WRITE` |
| **bit** | `out\\build11o\\s4d_p3r_r01.bit` **4,045,767 B** `7c46a8a9c8304432342d9a5d7a6383648715da6a8c6d17df8b923a12ab8b9b1e` |
| **XSA** | `out\\build11o\\s4d_p3r_r01.xsa` **513,893 B** `aa3fb4c8bbd036f326f8220a4b173ef67eabf2a97e9632d75189b958d0e31075` |
| **ps7_init** | `p3r_build11o_ps7_init.tcl` **27,602 B** `0c07e86f…`（与 11i/11k/11l 一致） |

### 26.6 教训（写进交接）
1. **"数据流正确但 SR 报错"** 优先怀疑 **AXI 写侧**（协议转换器读写模式、互连端口权限、地址译码、HP 口写使能），而不是 AXIS 相位；
2. **构建告警必须逐条清零**：`smartconnect ... WRITE_ONLY ↔ READ_ONLY` 这条从 build11g 就在，被当作"无害告警"忽略了 7 个小时；
3. 派生自早期阶段的 BD 参数（如"只读协议转换器"）在后续功能扩展时**必须重新审视**。
