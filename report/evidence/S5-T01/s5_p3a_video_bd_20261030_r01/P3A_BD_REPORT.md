# P3A 视频输出通路 BD 报告（阶段6）

| 项 | 值 |
|---|---|
| 任务 | P3a 视频输出通路 BD，迭代至 `validate_bd_design` 0 error |
| 日期 | 2026-10-30（UTC+8） |
| 工具 | Vivado v2026.1（64-bit，SW Build 6511674，IP Build 6504888） |
| 器件 | `xc7z020clg400-2` |
| BD 名 / 工程 | `s4d_p3a` / `s4d_p3a_r01` |
| 基线 | `D:\tmp\lead\p2d_merged_20261029_r01\bd_p2d.tcl`（只读复制改造，P2d 目录未改动） |
| 执行模式 | `-tclargs gen`（BD + validate + `generate_target` + wrapper；**未综合、未实现、未上板**） |
| 证据入口 | `D:\tmp\lead\p3a_video_20261030_r01\validate_console.log`、`out\p3a_bd_facts.txt`、`vivado_p3a.log` |

---

## 1. 结论

**`validate_bd_design` 通过：0 ERROR / 0 CRITICAL WARNING / 14 WARNING。**

后续的 `generate_target all` + `make_wrapper` 同样成功（9 个 IP 与 3 个 SmartConnect 全部生成 BD synth/sim 网表与 wrapper），
说明不仅 BD 拓扑连通，各 IP 的参数组合也通过了 IP 生成期检查（含 clk_wiz 的 MMCM 参数合法性、VDMA/VTC/vid_out 的位宽组合）。

- 未生成 `s4d_p3a_r01.runs` 目录 → 可确认本阶段**没有启动任何综合/实现 run**（与边界一致）。
- 未写 XDC、未碰板卡/JTAG/COM4/hw_server、未 git 提交、未修改 P2d 目录与 `D:\FPGA\AX7Z020` 厂商原件。

计数方式（可复算）：

```powershell
$l = Get-Content 'D:\tmp\lead\p3a_video_20261030_r01\validate_console.log'
($l | Where-Object {$_ -match '^ERROR'}).Count            # 0
($l | Where-Object {$_ -match '^CRITICAL WARNING'}).Count # 0
($l | Where-Object {$_ -match '^WARNING'}).Count          # 14
```

> 说明：脚本内**不再**用 `get_msg` 自报计数。实测 Vivado 2026.1 的 `get_msg` 不返回历史消息
> （同一运行实际打印 14 条 WARNING，`get_msg` 却全返回 0），若用它判据会给出假的"0 error"。
> 因此脚本只打印 `P3A_VALIDATE_DONE`，结论一律以本次 console/log 的文本计数为准。

### 14 条 WARNING 逐条解释（均为已解释项，无隐藏缺陷）

| # | 代码 | 条数 | 解释与处置 |
|---|---|---|---|
| 1 | `IP_Flow 19-5101` | 3 | 三个 module reference（`s4d_preproc_v2_wrap`、`s2b_inference_top`、`s4d_axis8_to_axis64`）的顶层是 SystemVerilog，IP 打包流程不完全支持 SV 顶层。**P2d 既有**，非 P3a 引入；不改 RTL 无法消除，不影响 BD 校验与综合。 |
| 2 | `BD 41-1306` | 4 | `vidout_0` 的 `vid_data/vid_hsync/vid_vsync/vid_active_video` 被逐引脚连成独立网络，而非常规的 `vid_io_out` 接口整体连接。这是 **G0 要求**（引出离散 BD 端口 `vid_hsync`/`vid_vsync`/`vid_de`/`vid_data`），属预期行为；副作用仅是 `write_bd_tcl` 重建时接口聚合关系需按脚本显式网络重放。 |
| 3 | `BD 41-3281` | 4 | `axi_dma_0`、`vdma_0`、`ps7_0`、`s4d_0` 两侧都接 SmartConnect，IPI 不再自动推断其 AXI 协议/位宽，需显式配置——**本设计已显式指定**（HP0/HP1/HP2 全 64-bit，VDMA 32-bit 流）。`s4d_0`/`axi_dma_0` 属 P2d 既有；`vdma_0`/`ps7_0` 因新增 `smc_vid` 而新增。 |
| 4 | `xilinx.com:ip:axi_vdma:6.3-166` | 1 | "ensure AXI Memory Map clock frequency >= AXI Streaming clock frequency"：本设计 VDMA 的 `m_axi_mm2s_aclk`=50 MHz < `m_axis_mm2s_aclk`=74.21875 MHz。这是 **G0 冻结的时钟分配**导致，属性能提示而非功能错误。带宽核算见 §9 第 4 项。 |
| 5 | `BD 41-2925` | 1 | `write_bd_tcl` 导出时提示脚本含 3 个 module reference，重建前需先提供对应 RTL。信息性。 |
| 6 | `IP_Flow 19-4994` | 1 | `generate_target` 覆盖同名 `*_ooc.xdc`。BD 内 IP 实例的 OOC 目标文件重复写，属良性。 |

---

## 2. 时钟实际值

### 2.1 PS7 时钟（实测读回 `PCW_ACT_*`）

| 时钟 | 使能参数 | 设定 | **实际（读回）** | 用途 |
|---|---|---|---|---|
| FCLK0 | `PCW_EN_CLK0_PORT=1`, `PCW_CLK0_FREQ=50000000` | 50 MHz | **50.000000 MHz** | 控制面 + P2d 全部逻辑 + VDMA 的 `s_axi_lite_aclk`/`m_axi_mm2s_aclk` |
| FCLK1 | `PCW_EN_CLK1_PORT=1`, `PCW_CLK1_FREQ=100000000` | 100 MHz | **100.000000 MHz** | `clk_wiz_0/clk_in1` 参考 |

### 2.2 clk_wiz 6.0（100 MHz 参考，厂商已验证 MMCM 原始参数，`OVERRIDE_MMCM=true`）

| 项 | 值 |
|---|---|
| `PRIM_IN_FREQ` / `MMCM_CLKIN1_PERIOD` | 100.000 MHz / 10.000 ns |
| `MMCM_DIVCLK_DIVIDE` | **8** |
| `MMCM_CLKFBOUT_MULT_F` | **59.375** |
| VCO | 100 / 8 × 59.375 = **742.1875 MHz** |
| `MMCM_CLKOUT0_DIVIDE_F`（clk_out1） | **10** → **74.21875 MHz** |
| `MMCM_CLKOUT1_DIVIDE`（clk_out2） | **2** → **371.09375 MHz** |
| 抖动（读回） | clk_out1 337.616 ps / clk_out2 258.703 ps（pk-pk） |
| 像素时序推导 | 74.21875 MHz ÷ 1650 px/行 = 44.981 kHz/行；÷ 750 行 = **59.9747 fps** |
| 串行时钟关系 | 371.09375 = **5 × 74.21875**（正好是 TMDS 10:1 DDR 的 5 倍关系） |

与 G0 目标 74.25 / 371.25 MHz 的偏差均为 **−0.042%**（绝对 −0.031 / −0.156 MHz），在 720p60 容差内（标准要求 ±0.5% 内）。

**备选方案（供 P3b 决策，本阶段未采用）**：若关闭 `OVERRIDE_MMCM` 让 IP 自动求解，clk_wiz 6.0 会给出
`DIVCLK_DIVIDE=5`、`MULT=37.125` → VCO=742.5 MHz → 输出**精确** 74.25 / 371.25 MHz。
当前按 G0 采用"同一板卡参考工程的已验证值"（74.219/371.094），二者只差 0.042%，像素时钟更低更保守。

### 2.3 时钟域划分

| 域 | 时钟 | 成员 |
|---|---|---|
| 控制/数据（50 MHz） | FCLK0 | PS7 GP0/HP0/HP1/HP2 的 ACLK、`s4d_0`、`infer_0`、`pack_0`、`axi_dma_0`、`smc_ctrl`、`smc_data`、`smc_vid`、`vtc_0/s_axi_aclk`、`vdma_0` 的 lite+mm |
| 参考（100 MHz） | FCLK1 | `clk_wiz_0/clk_in1` |
| 像素（74.21875 MHz） | clk_out1 | `vtc_0/clk`、`vidout_0/aclk`、`vdma_0/m_axis_mm2s_aclk`、`rst_pix/slowest_sync_clk`、BD 端口 `pixel_clk` |
| 预留（371.09375 MHz） | clk_out2 | 未使用（P3b TMDS 串行） |

复位：`rst_all`（同步到 FCLK0）+ 独立的 `rst_pix`（同步到 74.21875 MHz），两者 `ext_reset_in` 同源取 `ps7_0/FCLK_RESET0_N`，
实现"异步断言 / 各域同步释放"；`clk_wiz_0/reset`（高有效）由 `rst_all/peripheral_reset` 驱动。

---

## 3. 地址段表（GP0 控制面 + 三个 HP 数据端）

### 3.1 AXI-Lite 控制面（`ps7_0/Data`，经 `smc_ctrl` 1S/**5M**）

| 基址 | 范围 | 目标 | 从端 | 相对 P2d |
|---|---|---|---|---|
| `0x43C00000` | 64 KB | `smc_ctrl/M01` → `infer_0/S_AXI`（2B 推理核 CSR） | GP0 | 不变 |
| `0x43C10000` | 128 B | `smc_ctrl/M00` → `s4d_0/S_AXI`（preproc CSR） | GP0 | 不变 |
| `0x43C20000` | 64 KB | `smc_ctrl/M02` → `axi_dma_0/S_AXI_LITE` | GP0 | 不变 |
| **`0x43C30000`** | **64 KB** | `smc_ctrl/M03` → `vtc_0/ctrl`（VTC） | GP0 | **新增** |
| **`0x43C40000`** | **64 KB** | `smc_ctrl/M04` → `vdma_0/S_AXI_LITE`（VDMA） | GP0 | **新增** |

**重叠结论：无重叠。** 5 段均在 `0x43C0_0000`–`0x43C4_FFFF` 内连续排布，基址间距 = 各自范围，
`assign_bd_address` 显式指定；validate 对地址段重叠会直接报 ERROR，本次 0 ERROR 即为无重叠的机器证据。

### 3.2 主端 DDR 段

| 主端 | 目标从端 | 基址 | 范围 | 相对 P2d |
|---|---|---|---|---|
| `infer_0/M_AXI` | `ps7_0/S_AXI_HP0`（`HP0_DDR_LOWOCM`，64-bit） | `0x00000000` | 1 GB | 不变（P2d 直连 HP0） |
| `s4d_0/M_AXI_RD` | `ps7_0/S_AXI_HP1`（`HP1_DDR_LOWOCM`，64-bit） | `0x00000000` | 1 GB | 不变（经 `smc_data`） |
| `axi_dma_0/M_AXI_S2MM` | `ps7_0/S_AXI_HP1`（同上） | `0x00000000` | 1 GB | 不变（经 `smc_data`） |
| **`vdma_0/M_AXI_MM2S`** | **`ps7_0/S_AXI_HP2`（`HP2_DDR_LOWOCM`，64-bit）** | **`0x00000000`** | **1 GB** | **新增（经 `smc_vid`）** |

基址相同不构成冲突：四段分属**不同主端地址空间**，且 HP0/HP1/HP2 是 PS 侧三个独立物理端口。

**VDMA 是否落在 HP2：是。** 三重证据：
1. `bd_p3a.tcl` 中 `connect_bd_intf_net vdma_0/M_AXI_MM2S → smc_vid/S00_AXI`、`smc_vid/M00_AXI → ps7_0/S_AXI_HP2`；
2. 地址分配 `-target_address_space [get_bd_addr_spaces -of_objects [get_bd_intf_pins vdma_0/M_AXI_MM2S]]` → `SEG_ps7_0_HP2_DDR_LOWOCM`；
3. `out\p3a_bd_facts.txt` 的地址段读回中出现 `SEG_ps7_0_HP2_DDR_LOWOCM offset=0x00000000 range=0x40000000`，而 HP0/HP1 未被 VDMA 占用。

---

## 4. BD 端口清单（wrapper 实测，共 26 个端口）

### 4.1 视频输出端口（本阶段新增，**不接 TMDS**）

| 端口 | 方向 | 位宽 | 来源 | 说明 |
|---|---|---|---|---|
| `pixel_clk` | out | 1 | `clk_wiz_0/clk_out1` | 74.21875 MHz 像素时钟 |
| `vid_hsync` | out | 1 | `vidout_0/vid_hsync` | 行同步（720p 正极性） |
| `vid_vsync` | out | 1 | `vidout_0/vid_vsync` | 场同步（720p 正极性） |
| `vid_de` | out | 1 | `vidout_0/vid_active_video` | 数据有效 |
| `vid_data` | out | **24** `[23:0]` | `vid_slice/Dout`（`vidout_0/vid_data` 32b 取 `[23:0]`） | RGB888，R=[23:16]、G=[15:8]、B=[7:0] |

### 4.2 PS7 外部端口（沿用 P2d）

- `DDR_0_*`：15 个 inout（`addr[14:0]`、`ba[2:0]`、`cas_n`、`ck_n`、`ck_p`、`cke`、`cs_n`、`dm[3:0]`、`dq[31:0]`、`dqs_n[3:0]`、`dqs_p[3:0]`、`odt`、`ras_n`、`reset_n`、`we_n`）
- `FIXED_IO_0_*`：6 个 inout（`ddr_vrn`、`ddr_vrp`、`mio[53:0]`、`ps_clk`、`ps_porb`、`ps_srstb`）

---

## 5. 视频通路 IP 关键参数（`out\p3a_bd_facts.txt` 实测读回）

### 5.1 `v_tc` 6.2（`vtc_0`，generation-only）

| 参数 | 值 | 对应 720p60 要求 | 核对 |
|---|---|---|---|
| `VIDEO_MODE` | `720p` | — | IP 预设 |
| `GEN_HACTIVE_SIZE` | 1280 | 行有效 1280 | ✔ |
| `GEN_HFRAME_SIZE` | 1650 | 行总 1650 | ✔ |
| `GEN_HSYNC_START` / `GEN_HSYNC_END` | 1390 / 1430 | 前肩 110（1280→1390）、同步 40（1390→1430）、后肩 220（1430→1650） | ✔ |
| `GEN_VACTIVE_SIZE` | 720 | 场有效 720 | ✔ |
| `GEN_F0_VFRAME_SIZE` | 750 | 场总 750 | ✔ |
| `GEN_F0_VSYNC_VSTART` / `VEND` | 724 / 729 | 空行共 30 = 前肩 5 + 同步 5 + 后肩 20 | ✔（取 IP 720p 预设寄存器值，未自造偏移） |
| 极性 | H/V Sync、ActiveVideo、H/V Blank 全 `High` | 720p 正极性 | ✔ |
| `HAS_AXI4_LITE` / `enable_generation` / `enable_detection` | true / true / **false** | 使能 AXI4-Lite 与 generation | ✔ |
| `HAS_INTC_IF` | false | 本阶段不用 VTC 中断 | — |
| `max_clocks_per_line` / `max_lines_per_frame` | 4096 / 4096 | 覆盖 1650×750 | ✔ |
| `VID_PPC` | 4（**IP 强制**） | — | 非 arbitrary-res 模式下该 GUI 参数被 IP 置 4 且禁用；标准 `vtiming_out` 仍为 1 pixel/clk（实测连线与生成均正常）。作为 IP 版本差异记录。 |

### 5.2 `axi_vdma` 6.3（`vdma_0`，只开 MM2S、非 SG）

| 参数 | 值 |
|---|---|
| `c_include_mm2s` / `c_include_s2mm` / `c_include_sg` | **1 / 0 / 0** |
| `c_m_axi_mm2s_data_width` | **64**（→ `S_AXI_HP2`） |
| `c_m_axis_mm2s_tdata_width` | **32**（RGB888 存 32-bit/RGBA） |
| `c_addr_width` | **32** |
| `c_use_fsync` / `c_single_interface` | 0 / 0（自由运行，由 `M_AXIS_MM2S` 的 TREADY 反压） |
| `c_sg_length_width` | **不存在**：非 SG 模式 IP 不暴露该参数（设置会触发 `CRITICAL WARNING [BD 41-1276]`），故未设置；简单模式下长度由 LENGTH 寄存器给出 |
| 时钟模式 | IP 自动判为 **ASYNC**（`6.3-16`：MM 侧 50 MHz ≠ 流侧 74.21875 MHz） |
| 中断 | `mm2s_introut` → `ps7_0/IRQ_F2P[0]`（`PCW_USE_FABRIC_INTERRUPT=1`、`PCW_IRQ_F2P_INTR=1`） |

**AXIS 位宽实测**（`TDATA_NUM_BYTES`）：`vdma_0/M_AXIS_MM2S` = **4 字节（32-bit）**，
`vidout_0/video_in` = **4 字节（32-bit）** → 两侧一致，连接合法（不是靠位宽不匹配"侥幸通过"）。

### 5.3 `v_axi4s_vid_out` 4.0（`vidout_0`）与 `xlslice`

| 参数 | 值 | 说明 |
|---|---|---|
| `C_S_AXIS_VIDEO_FORMAT` | **6 = RGBA**（4 分量） | 这是"32-bit AXIS + RGB888"的关键：RGB(2) 只有 3 分量、1ppc/8b 时 AXIS 仅 24-bit，无法接 32-bit 流 |
| `C_PIXELS_PER_CLOCK` | 1 | 1 pixel/clk @ 74.21875 MHz |
| `C_S_AXIS_VIDEO_DATA_WIDTH` / `C_NATIVE_COMPONENT_WIDTH` | 8 / 8 | 分量 8-bit |
| 推导结果 | AXIS TDATA = 1×4×8 = **32-bit**；native `vid_data` = **32-bit** | 与 VDMA 32-bit 流对齐 |
| `C_ADDR_WIDTH` / `C_HYSTERESIS_LEVEL` | 10（FIFO 1024 word）/ 12 | 默认值 |
| `C_HAS_ASYNC_CLK` | 0 | 流与视频输出同域（均 74.21875 MHz） |
| `C_VTG_MASTER_SLAVE` | **0 = Slave** | 由 `vidout_0/vtg_ce` 驱动 `vtc_0/gen_clken`，视频时序跟随外部 VTC |
| 时序接口 | `vtc_0/vtiming_out` → `vidout_0/vtiming_in` | 接口级连接 |
| `xlslice`（`vid_slice`） | `DIN_WIDTH=32`、`DIN_FROM=23`、`DIN_TO=0`、`DOUT_WIDTH=24` | 砍掉 alpha 字节 → `vid_data[23:0]` |

像素字约定：32-bit 小端 `0xAARRGGBB` → AXIS 字节序 B/G/R/A → `vid_data[23:0] = {R,G,B}`（R 在 [23:16]），
与常规 RGB888 通道顺序一致，**alpha 被丢弃**。若 P3b 更换像素格式需同步调整该 slice 与 rgb2dvi 映射。

### 5.4 SmartConnect / 其它

| 实例 | 配置 | 作用 |
|---|---|---|
| `smc_ctrl` | 1S/**5M** | GP0 → 5 个 AXI-Lite 从端（P2d 为 1S/3M） |
| `smc_data` | 2S/1M | preproc 读 + DMA 写 → HP1（P2d 既有，未改） |
| **`smc_vid`** | **1S/1M，新建** | **VDMA `M_AXI_MM2S`(AXI4) → PS7 `S_AXI_HP2`(AXI3) 的协议转换** |
| `rst_all` / `rst_pix` | proc_sys_reset ×2 | 50 MHz 域 / 74.21875 MHz 像素域各一个 |
| `const_1` / `const_0` | xlconstant ×2 | `clken`/`aclken`/`vid_io_out_ce` 拉高；`fsync_in`/`sof_state`/`fid` 拉低 |

---

## 6. 与 P2d 的差异（只增不改）

| 项 | P2d | P3a | 性质 |
|---|---|---|---|
| PS7 FCLK1 | 未启用 | **100 MHz 启用**（`EN_CLK1_PORT` + `CLK1_FREQ`） | 新增 |
| PS7 HP 端口 | HP0、HP1 | HP0、HP1 + **HP2** | 新增 |
| PS7 中断 | 无 | **`IRQ_F2P[0]`**（VDMA MM2S） | 新增 |
| 视频 IP | 无 | **clk_wiz / v_tc / axi_vdma / v_axi4s_vid_out / xlslice** | 新增 |
| `smc_ctrl` | 1S/3M | **1S/5M**（+VTC +VDMA） | 扩展 |
| 数据面 | HP0（2B）、HP1（preproc+DMA） | 原样保留 + **HP2（VDMA）经 smc_vid** | 新增 |
| 视频输出端口 | 无 | **pixel_clk / vid_hsync / vid_vsync / vid_de / vid_data[23:0]** | 新增 |
| 地址 `0x43C00000`/`0x43C10000`/`0x43C20000` | 有 | **完全不变** | 不变 |
| `s4d_0`/`infer_0`/`pack_0`/`axi_dma_0` 连接与参数 | — | **完全不变** | 不变 |
| 顶层 RTL / SRC_BASE / PROFILE_VISIBILITY_PROVEN | — | 不变 | 不变 |

---

## 7. 遇到并解决的主要报错（4 项 + 1 项设计性改造）

1. **[BD 5-235] `No pins matched 'get_bd_pins ps7_0/FCLK_CLK1'`** → FCLK1 引脚根本没生成。
   根因不是频率参数，而是**端口使能**：2026.1 的 PS7 里 `FCLK_CLK1` 的门控是
   `PCW_EN_CLK1_PORT==1 && PCW_USE_CR_FABRIC==1`，频率由 `PCW_CLK1_FREQ`（单位 **Hz**）决定；
   只写 G0 里的 `PCW_FPGA1_PERIPHERAL_FREQMHZ {100}` 时 `PCW_ACT_FPGA1_PERIPHERAL_FREQMHZ` 仍是 10 MHz、引脚不出现。
   解决：补设 `PCW_EN_CLK1_PORT {1}`、`PCW_CLK1_FREQ {100000000}`、`PCW_USE_CR_FABRIC {1}`，并加断言脚本内校验 ACT=100 MHz。
2. **[BD 41-1285] `protocols of '/vdma_0/M_AXI_MM2S'(AXI4) and '/ps7_0/S_AXI_HP2'(AXI3) are incompatible`**。
   VDMA 的 MM 接口是 AXI4，而 Zynq PS7 的 HP 口是 AXI3。HP0/HP1 之所以能直连/经 smc，是因为中间有 SmartConnect 做转换。
   解决：新增 `smc_vid`（1S/1M，High-performance 模式）承接协议转换，`vdma_0 → smc_vid → HP2`。
3. **[BD 41-1276] `Cannot set the parameter c_sg_length_width on /vdma_0. Parameter does not exist`**。
   `c_include_sg=0` 时该参数在 6.3 中不暴露（G0 列了它，但 IP 版本不允许）。
   解决：删除该设置并在报告中记录；非 SG 模式传输长度由 LENGTH 寄存器直接给出，语义上不需要 SG 长度位宽。
4. **[BD 5-700] `No address spaces matched 'get_bd_addr_spaces axi_dma_0/M_AXI_S2MM'`（×2）**。
   对"既有 AXI-Lite 从端又有 AXI 主端"的 IP，主端地址空间名不等于 `<cell>/<pin>`。
   解决：改用 `get_bd_addr_spaces -of_objects [get_bd_intf_pins <master>]`（对 `infer_0`/`s4d_0`/`axi_dma_0`/`vdma_0` 全部统一），
   警告消失，且四段 DDR 地址分配全部落实（见 §3.2 与 facts 文件）。
5. **（设计改造）32-bit 流 vs 24-bit `vid_data`**：G0 要求 VDMA 流 32-bit、`vid_data[23:0]`，而 RGB(格式 2) 在 1ppc/8b 下 AXIS 只有 24-bit。
   若强行连接会位宽不匹配。解决：`C_S_AXIS_VIDEO_FORMAT=6`（**RGBA**，4 分量 → 32-bit AXIS / 32-bit native），
   再用 `xlslice` 取 `[23:0]`，语义上正好是"32-bit 承载 RGB888 + 丢弃 alpha"，同时满足两条 G0 约束。

---

## 8. 复现命令

```powershell
# 只建 BD + validate + save（约 2–3 分钟）
& 'D:\Xilinx\2026.1\Vivado\bin\vivado.bat' -mode batch -notrace `
  -log D:\tmp\lead\p3a_video_20261030_r01\vivado_p3a.log `
  -source D:\tmp\lead\p3a_video_20261030_r01\bd_p3a.tcl -tclargs validate

# 本次实际执行：validate + generate_target + make_wrapper（仍不综合，约 4 分钟）
& 'D:\Xilinx\2026.1\Vivado\bin\vivado.bat' -mode batch -notrace `
  -log D:\tmp\lead\p3a_video_20261030_r01\vivado_p3a.log `
  -source D:\tmp\lead\p3a_video_20261030_r01\bd_p3a.tcl -tclargs gen
```

`-tclargs build`（synth + impl + bitstream + XSA）已实现但**本任务未执行**。

---

## 9. 未尽事项 / 风险（P3b 与后续阶段入口）

1. **TMDS 输出未做**（G0 明确本阶段不含）：`vid_*` 只是普通单端信号，尚未接 `rgb2dvi`/TMDS 编码器，也没有引脚约束。
   板卡引脚已记录（**本阶段未写入 XDC**）：`TMDS_clk_p=U13`、`TMDS_data_p={W14, Y18, Y16}`、`hdmi_oen=V16`。
2. **时序约束（XDC）未写**：像素域需要 `create_clock -period 13.4737 [get_ports pixel_clk]`（74.21875 MHz），
   并需 `set_clock_groups -asynchronous` 隔离 50 / 74.21875 / 100 / 371.09375 MHz 四个域，
   以及 VDMA/`v_axi4s_vid_out` 的跨域 false path。**综合前必须补齐**，否则 WNS 无意义。validate 阶段不需要 XDC。
3. **未综合/未实现**：资源占用、时序、MMCM 实际锁定、DRC 均未验证。本次只证明"BD 拓扑 + IP 参数组合"合法（含 IP 生成期检查）。
4. **VDMA 时钟性能风险**（`axi_vdma 6.3-166`）：MM 侧 50 MHz 低于流侧 74.21875 MHz。
   带宽核算：读需求 = 74.21875 Mpx/s × 4 B = **296.9 MB/s**（283.1 MiB/s）；HP2 峰值 = 64 bit × 50 MHz = **400 MB/s**（381.5 MiB/s），
   理论占用 **74.2%**，余量偏小。若 P3b 出现 `underflow`/掉帧，需要 G0 变更（如把 FCLK0 提到 100 MHz，会牵动 P2d 全部逻辑；
   或改 VDMA 时钟方案），本阶段不做擅自变更。
5. **`clk_out2`=371.09375 MHz 已生成但悬空未用**（留给 P3b TMDS 串行）。悬空输出不产生 ERROR；
   若 P3b 不用，建议回头 `CLKOUT2_USED=false` 以省一个 BUFG。
6. **`VID_PPC` 被 v_tc 6.2 强制为 4**（非 arbitrary-res 模式参数禁用，与 G0 字面值不同但实测不影响 720p 生成与连线）。
   若后续要用 arbitrary resolution 才需要显式 PPC。
7. **像素格式假设未与软件侧对齐**：`vid_data[23:0]={R,G,B}` 基于 framebuffer 为小端 `0xAARRGGBB`、alpha 丢弃。
   VDMA 帧缓存 stride（1280×4 = 5120 B/行）、帧数、基址等 ABI **尚未在 PS 侧固化**，需 P3b/P4 驱动阶段一起定。
8. **叠加通路未接入**（G0 明确本阶段不含 OSD/bbox 叠加），后续在 `vidout_0/video_in` 前插入 mixer 时需重新评估 32-bit RGBA 语义。
9. **未做 P2d 功能回归**：P2d 的连接/参数/地址/时钟均未改动（脚本逐条保留），但本阶段未重跑 P2d 的既有证据去证明"加通路后原功能不变"。
10. **验证范围**：本报告只覆盖 BD 设计与 `validate_bd_design`。不构成 G3（实物）/G4（任务验收）/G5（阶段验收）结论。

---

## 10. 产物与哈希（SHA-256）

| 文件 | 大小 | SHA-256 |
|---|---|---|
| `bd_p3a.tcl` | 24,969 B | `778a423136f9769c13971ca3341ba82df22729074ddc8665c135bec82772c3b3` |
| `bd_p3a.bd` | 84,461 B | `289344d987f86f4290b88d8556ad1f2e26c30f8fba414690c9546f9f476b6c79` |
| `validate_console.log` | 32,580 B | `9ce72b9cb03266c0ba452aa73401dc7348b61e00feb287dbf5d6aae92d219617` |
| `out\p3a_bd_facts.txt` | 3,183 B | `b24b114393ac34fcdcac490ef229e04c0f528cf24feee987e1d0a5bb57a8bb76` |

附加产物：
- `vivado_p3a.log` / `vivado_p3a.jou`：Vivado 完整运行日志与命令记录
- `out\bd_p3a_generated.tcl`：由 `write_bd_tcl` 导出的可重建 BD 脚本（注意需先提供 3 个 SV module reference 的 RTL）
- `out\proj\`：完整 Vivado 工程（含 `s4d_p3a_wrapper`、BD synth/sim 网表、IP 生成产物、`s4d_p3a.hwh`）
- `probe\`、`probe2\`、`probe3\`：参数探测证据（IP 可用版本 / 视频链路位宽可行性 / PS7 FCLK 门控），保留作为方法留痕