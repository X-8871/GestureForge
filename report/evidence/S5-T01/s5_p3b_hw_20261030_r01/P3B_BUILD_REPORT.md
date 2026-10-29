# P3B 构建报告（rgb2dvi + TMDS + 位流）

| 项 | 值 |
|---|---|
| 阶段 / 任务 | **阶段5（HDMI 显示链）** / **S5-T01**（编号口径 2026-10-30 Wong 决定 A） |
| RunId | **s5_p3b_build_20261030_r01** |
| 日期 | 2026-10-30（UTC+8） |
| 工具 / 器件 | Vivado v2026.1 / `xc7z020clg400-2` |
| 设计 | BD `s4d_p3b`（= P3a 全部逻辑 + 新增端口 `pixel_clk_5x`）→ `s4d_p3b_wrapper` → 顶层 **`top_p3b.v`** + 厂商 **`rgb2dvi_v1_3`** |
| 流程 | synth → opt/place/route → write_bitstream → XSA（**含位流**，仍不上板） |
| 约束 | `p3b_tmds.xdc`（声明式 + `PROCESSING_ORDER {LATE}`） |
| 规范 | 遵循 `XDC_GUIDELINES.md`（同目录），构建前已过 `check_xdc_declarative.py` |

> **状态：构建进行中／待填**。本文件先固化"设计依据 + 自检计划 + 寄存器表"，
> 构建完成后把 §2/§3/§4 的实测数字补齐即定稿。

---

## 1. 本阶段做了什么（相对 P3a）

| 项 | P3a | **P3b** |
|---|---|---|
| 视频输出 | 28 位离散端口，**无引脚** | 接入厂商 `rgb2dvi`，输出 **TMDS 差分对 + hdmi_oen**，引脚全部约束 |
| 5× 串行时钟 | `clk_out2` 未连接（被 trim） | **引出为 BD 端口 `pixel_clk_5x`**，送 rgb2dvi 的 `SerialClk` |
| 位流 | 不出（DRC NSTD/UCIO 有意拦下） | **出位流 + XSA**（所有顶端口都有引脚约束） |
| 叠加 | 无 | **仍无**（叠加不在 P3b 规格内；G0 D2 的框+文字属后续） |

### 1.1 为什么用"外部 5× 时钟"而不是 rgb2dvi 内部 ClockGen
厂商本板参考工程 `02_hdmi_out_test` 的 IP 配置实测为：
`kGenerateSerialClk=false`、`kClkRange=1`、`kRstActiveHigh=false`（`rgb2dvi_0.xci` 的 MODELPARAM）。
即厂商在本板走的是**外部 5× 串行时钟**路线。本设计跟随该已验证配置：
- `rgb2dvi.vhd:109-129` —— `kGenerateSerialClk=false` 时 `PixelClkIO<=PixelClk; SerialClkIO<=SerialClk`，不引入第二个 MMCM、不产生跨时钟域；
- `rgb2dvi.vhd:125-129` —— 外部模式。
额外好处：`pixel_clk` 与 `pixel_clk_5x` 来自**同一个 clk_wiz MMCM**（CLKOUT1/CLKOUT2），
1×/5× 相位关系确定，满足 `OutputSERDES.vhd:110-111`（`CLK=>SerialClk, CLKDIV=>PixelClk`）对 OSERDESE2 的要求。

### 1.2 rgb2dvi 端口接法依据（逐条对应源码行号）

| rgb2dvi 端口 | 接到 | 依据 |
|---|---|---|
| `TMDS_Clk_p/_n` | 顶层差分端口 → `U13` | `rgb2dvi.vhd:69-70,144-154`（ClockSerializer 输出 10bit 固定码 `"1111100000"`） |
| `TMDS_Data_p/_n(2:0)` | 顶层差分端口 → `W14/Y18/Y16` | `rgb2dvi.vhd:71-72,156-179` |
| `oen` | 顶层 `hdmi_oen` → `V16` | `rgb2dvi.vhd:192` 内部恒为 `'1'`；厂商 `top.v:47` 直连该端口 |
| `aRst` | 常量 `'0'` | `kRstActiveHigh=false`（`rgb2dvi.vhd:101-107`：低有效分支只用 `aRst_n`） |
| `aRst_n` | 顶层像素域 POR（低有效，16 个 pixel_clk 后释放） | `rgb2dvi.vhd:77-78`；内部 `ResetBridge`（`SyncAsyncReset.vhd:63`）负责同步释放 |
| `vid_pData(23:0)` | BD `vid_data[23:0]` | `rgb2dvi.vhd:184-186`：`pDataOut(2)=vid_pData(23:16)` 即 **R 在 [23:16]**，与 BD 的 RGB888 通道顺序一致 |
| `vid_pVDE` / `vid_pHSync` / `vid_pVSync` | BD `vid_de` / `vid_hsync` / `vid_vsync` | `rgb2dvi.vhd:189-191`（HSync/VSync 作为 channel0 的 control 信号，VDE 同时作为三通道 blanking 指示） |
| `PixelClk` | BD `pixel_clk`（74.21875 MHz） | `rgb2dvi.vhd:85` |
| `SerialClk` | BD **`pixel_clk_5x`**（371.09375 MHz = 5×） | `rgb2dvi.vhd:87`；5× 关系由厂商 `rgb2dvi_clocks.xdc:2` 明确（`-multiply_by 5`） |

**generic 固定值**（自有薄封装 `rtl/rgb2dvi_wrap.vhd`，因为 **Verilog 实例化 VHDL entity 不能覆盖 generic**）：

```
kGenerateSerialClk => false,  kClkPrimitive => "MMCM",
kClkRange => 1,               kRstActiveHigh => false
```

### 1.3 TMDS 引脚依据（厂商 XDC 原文，未臆造）

来源：`D:\FPGA\AX7Z020\AX7Z020\course_s1\course_s1\02_hdmi_out_test\hdmi_out_test.srcs\constrs_1\new\hdmi_out_test.xdc` **第 4-17 行**

| 信号 | PACKAGE_PIN | IOSTANDARD | 厂商行号 |
|---|---|---|---|
| `TMDS_clk_p` | **U13** | TMDS_33 | L5-L6 |
| `TMDS_clk_n` | （由 P 推出） | TMDS_33 | L4 |
| `TMDS_data_p[0]` | **W14** | TMDS_33 | L8-L9 |
| `TMDS_data_n[0]` | （由 P 推出） | TMDS_33 | L7 |
| `TMDS_data_p[1]` | **Y18** | TMDS_33 | L11-L12 |
| `TMDS_data_n[1]` | （由 P 推出） | TMDS_33 | L10 |
| `TMDS_data_p[2]` | **Y16** | TMDS_33 | L14-L15 |
| `TMDS_data_n[2]` | （由 P 推出） | TMDS_33 | L13 |
| `hdmi_oen` | **V16** | LVCMOS33 | L16-L17 |

差分对由 `OutputSERDES.vhd:83` 的 `OBUFDS` 内部生成，故顶层只声明 `_p/_n` 两个端口、只给 `_p` 设 `PACKAGE_PIN`（与厂商 XDC 一致）。

> ⚠️ **极性与 Lead 提示不一致，需上板确认**：Lead 曾提示"hdmi_oen 低有效，驱动 0 使能"，
> 但厂商源码为 `rgb2dvi.vhd:192` `oen <= '1'`、厂商 `top.v:47` 把该端口**直连** `hdmi_oen`，
> 即厂商参考实际驱动 **1**。本设计**以厂商源码/参考工程为准**（不在无依据时反相）。
> 若上板出现"有信号但屏幕不亮"，第一处置点是把 `hdmi_oen` 反相（顶层 1 行改动）。

---

## 2. 时序结果（待构建后填）

| 指标 | **P3b 实测** | P3a+（r02，保守下界） | 说明 |
|---|---|---|---|
| WNS | `待填` ns | +0.041 ns | 现含 TMDS 输出与 5× 时钟域 |
| WHS | `待填` ns | +0.043 ns | |
| TNS / THS | `待填` | 0.000 / 0.000 | |
| WPWS | `待填` | 3.000 | |
| 失败端点 | `待填` | 0 / 52,443 | |

---

## 3. 资源占用（待构建后填）+ 与 P3a+ 的增量

| 资源 | P2d | P3a+ | **P3b 实测** | **P3b−P3a+ 增量（rgb2dvi）** | 上限 | 预算判断 |
|---|---|---|---|---|---|---|
| LUT | 23,451 (44.08%) | 25,895 (48.67%) | `待填` | `待填` | 53,200 | |
| FF | 10,414 (9.79%) | 14,876 (13.98%) | `待填` | `待填` | 106,400 | |
| BRAM | 33.5 | 36.5 (26.07%) | `待填` | `待填`（rgb2dvi 不用 BRAM，预期 +0） | 140 | |
| DSP | 158 (71.82%) | 158 (71.82%) | `待填` | `待填`（预期 **+0**） | 220 | |
| MMCM | 0 | 1 | `待填`（预期 1） | +0（外部 5× 路线不加 MMCM） | 4 | |
| BUFG/BUFIO/BUFR | 1 | 4 | `待填` | `待填`（5× 时钟路由会增加） | 32 | |

G0 §4 预算（含叠加的估算）：LUT 29.5k–32.5k（55–61%）、FF 16k–18k（15–17%）、BRAM 42–54（30–39%）、DSP 158。

---

## 4. DRC / 位流（待构建后填）

- DRC 计数：`待填`（**预期 NSTD-1 / UCIO-1 消失**：P3b 所有顶端口都有引脚约束）
- 位流：`out\s4d_p3b_r01.bit`（`待填` 大小/哈希）
- XSA：`out\s4d_p3b_r01.xsa`（`待填`）

---

## 5. 构建后自检计划（按 `XDC_GUIDELINES.md` §3，构建中执行）

```tcl
report_clocks            -file $out/clocks_route.rpt
report_clock_interaction -delay_type min_max -file $out/clk_interaction_route.rpt
report_clock_utilization -file $out/clk_util_route.rpt
report_io                -file $out/io_route.rpt        ;# 核对 TMDS/oen 引脚
report_drc               -file $out/drc_route.rpt
```

| 自检项 | 预期 | 判据 |
|---|---|---|
| `clk_out1_*` 像素时钟 | **13.474 ns**（74.21875 MHz） | `clocks_route.rpt` |
| **`clk_out2_*` 5× 时钟** | **2.6945 ns**（371.09375 MHz） | **P3b 必须出现**（P3a 因未连接被 trim）；属性含 G |
| 时钟组是否生效 | `grep '12-4739'` **为空** | 验证 `PROCESSING_ORDER {LATE}` 起作用 |
| 控制流陷阱 | `grep '20-1307'` **为空** | 声明式 XDC |
| TMDS 引脚 | U13/W14/Y18/Y16 TMDS_33，V16 LVCMOS33 | `io_route.rpt` |
| DRC | **0 error**；NSTD-1/UCIO-1 不出现 | `drc_route.rpt` |

骨架命令：

```powershell
$c = Get-Content D:\tmp\lead\p3b_video_20261030_r01\s5_p3b_build_20261030_r01_console.log
($c | Where-Object {$_ -match '^(ERROR|CRITICAL WARNING)'}) | Measure-Object   # 期望 0
($c | Select-String '12-4739|20-1307')                                        # 期望空
```

---

## 6. VTC AXI-Lite 寄存器表（软件侧对接，**值必须一致**）

**基址：`0x43C30000`**（64 KB）。寄存器偏移来自厂商驱动头文件
`D:\Xilinx\2026.1\Vivado\data\embeddedsw\XilinxProcessorIPLib\drivers\vtc_v8_5\src\xvtc_hw.h`
（行号见下表）；数值按该文件的位域掩码 + 本设计的 IP 配置（`GEN_*`）算出。

### 6.1 本设计固化的 720p60 时序（与 Lead 给的软件约定逐项对齐）

| 时序量 | 值 | 与约定核对 |
|---|---|---|
| H total / Hactive | 1650 / 1280 | ✔ H 1650 / HACT 1280 |
| HSync start / end | 1390 / 1430 | → HSW = **40** ✔；HBP = 1650−1430 = **220** ✔；HFP = 1390−1280 = 110 |
| V total / Vactive | 750 / 720 | ✔ V 750 / VACT 720 |
| VSync start / end | 724 / 729 | → VSW = **5** ✔；VBP = 750−730 = **20** ✔（v_tc 预设寄存器惯例） |
| 极性 | H/V Sync、H/V Blank、ActiveVideo 全 **High** | 720p 正极性 |

### 6.2 寄存器偏移与值

| 偏移 | 名称（xvtc_hw.h） | 值（720p60） | 说明 |
|---|---|---|---|
| `0x000` | `XVTC_CTL`（L150） | **`0x00000005`** 常规；若运行时重下时序再 `\|0x03FDEF00` → `0x03FDEF07` | bit0 `SW`(核心使能) + bit2 `GE`(生成器使能)；（可选 bit1 `RU` 寄存器更新） |
| `0x004` | `XVTC_ISR`（L151） | 只读 | 状态/中断状态 |
| `0x008` | `XVTC_ERROR`（L153） | 只读 | 错误状态 |
| `0x00C` | `XVTC_IER`（L154） | `0x00000000` | 本设计未用 VTC 中断（`HAS_INTC_IF=false`） |
| `0x010` | `XVTC_VER`（L156） | 只读 | 版本 |
| `0x060` | `XVTC_GASIZE`（L186） | **`0x02D00500`** | V(29:16)=720=0x2D0，H(13:0)=1280=0x500 |
| `0x068` | `XVTC_GFENC`（L188） | **`0x00000000`** | 逐行（progressive），非隔行 |
| `0x06C` | `XVTC_GPOL`（L189） | **`0x0000003F`** | VBP/HBP/VSP/HSP/AVP/ACP 全高；FIP 因 fieldid 关闭为 0 |
| `0x070` | `XVTC_GHSIZE`（L190） | **`0x00000672`** | H total = 1650 = 0x672 |
| `0x074` | `XVTC_GVSIZE`（L192） | **`0x02EE02EE`** | F1(29:16)=750，F0(13:0)=750 |
| `0x078` | `XVTC_GHSYNC`（L194） | **`0x0596056E`** | end=1430=0x596，start=1390=0x56E |
| `0x07C` | `XVTC_GVBHOFF`（L197） | **`0x056E056E`** | 垂直 blank 的水平起始/结束 = 1390/1390 |
| `0x080` | `XVTC_GVSYNC`（L199） | **`0x02D902D4`** | end=729=0x2D9，start=724=0x2D4 |
| `0x084` | `XVTC_GVSHOFF`（L201） | **`0x056E056E`** | 垂直 sync 的水平起始/结束 = 1390/1390 |

### 6.3 软件侧两条可选路径（**都合法，值必须与上表一致**）

1. **用 IP 固化的时序（推荐、最少写寄存器）**：只写 `0x000 = 0x00000005`（SW+GE）。
   依据：`XVTC_CTL_ALLSS_MASK = 0x03FDEF00`（xvtc_hw.h L301）是"源选择"位掩码——
   某位为 0 时该参数取自 **IP 构建期配置的硬件默认值**（本设计即 720p60），
   置 1 才改用 AXI 寄存器里的值。故不写参数寄存器也能出正确 720p60。
2. **用 `XVtc_GenerateTiming()` 运行时下发**：先置 `0x03FDEF00` 源选择位，再按 §6.2 写全部参数寄存器，
   最后置 `RU`(bit1) 生效 → `0x000 = 0x03FDEF07`。
   **两边数值必须逐项一致**，否则屏幕上会出现错位/不同步。

> 备注：`VID_PPC` 在非 arbitrary-res 模式下被 v_tc 6.2 强制为 4（GUI 参数禁用），
> 但标准 `vtiming_out` 仍是 1 pixel/clk，不影响上述寄存器语义（已实测 720p 生成正常）。

---

## 7. VDMA 关键参数（软件侧对接）

| 参数 | 值 | 说明 |
|---|---|---|
| `c_include_mm2s` / `c_include_s2mm` / `c_include_sg` | 1 / 0 / 0 | 只读通道、非 SG（简单模式，写 DA/LENGTH 启动） |
| `c_m_axi_mm2s_data_width` | 64 | AXI-MM 侧（经 smc_vid → PS7 `S_AXI_HP2`） |
| `c_m_axis_mm2s_tdata_width` | 32 | 流侧 32 b（RGBA 承载 RGB888；`vid_data[23:0]` 由 xlslice 裁出） |
| `c_addr_width` | 32 | |
| **`c_num_fstores`** | **2** | **与 `s5_display_app` 双缓冲（A/B 乒乓）约定一致**；IP 默认 3 会与软件假设不符且多占帧存地址 |
| `c_use_fsync` | 0 | 自由运行，由 `M_AXIS_MM2S` 的 TREADY 反压 |
| 基址 / 中断 | `0x43C40000` / `mm2s_introut → ps7_0/IRQ_F2P[0]` | |

帧存约定（供软件）：1280×720、RGB888 存 32-bit 字（`0xAARRGGBB`，alpha 忽略），stride = 1280×4 = **5120 B/行**；2 个 frame store → 每帧 3,686,400 B（0x384000）。

---

## 8. 未尽事项 / 风险

1. **未上板**：S6-A（上屏 ≥5 min）、S6-C（VDMA 读帧 CRC）、S6-D（叠加）、S6-E（P2d 7 项回归）、S6-F（30 min 稳定）全部未做 → 本报告**不构成 G3/G4/G5 结论**。
2. **`hdmi_oen` 极性待上板确认**（见 §1.3 的 ⚠️）：本设计遵厂商源码驱动 `1`；若屏不亮，第一处置点是反相。
3. **TMDS 输出无 output_delay**：厂商参考同样没有，且无板级 Tco 数据；不编造。上板以 S6-A 上屏为最终判据。
4. **371.09 MHz 5× 时钟经 BUFG 驱动 OSERDESE2**（与厂商参考一致）：若出现 `CLOCK_DEDICATED_ROUTE` 类 DRC 或布线告警，按厂商做法处理（必要时 `set_property CLOCK_DEDICATED_ROUTE FALSE`），并在报告中记录处置。
5. **叠加未实现**（G0 D2 的框+文字属后续阶段）：P3b 只保证"能出 720p60 稳定 TMDS 信号"。
6. **`PROCESSING_ORDER {LATE}` 的有效性需用 `grep '12-4739'` 实测确认**（P3a 未验证到此步）；若仍失效，改用 impl PRE 钩子（`XDC_GUIDELINES.md` §2 做法 B）。
7. **JSON/哈希**：构建完成后补 `bit`/`xsa`/报表的 SHA-256 与时间戳。