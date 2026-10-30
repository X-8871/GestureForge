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