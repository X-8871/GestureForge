# P3B 构建报告（rgb2dvi + TMDS + 位流）

| 项 | 值 |
|---|---|
| 阶段 / 任务 | **阶段5（HDMI 显示链）** / **S5-T01**（编号口径 2026-10-30 Wong 决定 A） |
| RunId | **s5_p3b_build_20261030_r01** |
| 日期 | 2026-10-30（UTC+8） |
| 工具 / 器件 | Vivado v2026.1 / `xc7z020clg400-2` |
| 设计 | BD `s4d_p3b`（P3a 全部逻辑 + 新增端口 `pixel_clk_5x`）→ `s4d_p3b_wrapper` → 顶层 **`top_p3b.v`** + 厂商 **`rgb2dvi_v1_3`** |
| 流程 | synth → opt/place/route → **write_bitstream → XSA**（**不上板**） |
| 约束 | `p3b_tmds.xdc`（纯声明式，过 `check_xdc_declarative.py`） |
| 规范 | 遵循同目录 `XDC_GUIDELINES.md` |

---

## 1. 结论（一句话）

**构建成功、位流已出、时序达标、资源在预算内、DRC 无 error。**

- **WNS = +0.544 ns，WHS = +0.022 ns，TNS = THS = 0.000**（52,363 端点，0 失败）→ 门槛通过。
- `write_bitstream completed successfully`（**0 Critical Warnings / 0 Errors**）；**NSTD-1 / UCIO-1 已消失**（P3a 那 28 个无引脚端口在 P3b 全部接了 TMDS/oen 引脚）。
- rgb2dvi 的净成本极低：**+72 LUT / +16 FF / +0 BRAM / +0 DSP / +0 MMCM / +1 BUFG**，另占 **OSERDESE2 ×8**（4 通道 × 主/从）。
- 位流与 XSA 已落地（sha256 见 §7）。

---

## 2. 本阶段相对 P3a 的改动

| 项 | P3a | **P3b** |
|---|---|---|
| 视频输出 | 28 位离散端口、无引脚 | 接厂商 `rgb2dvi`，输出 **TMDS 差分对 + hdmi_oen**，引脚全约束 |
| 5× 串行时钟 | `clk_out2` 未连接（被 trim） | 引出 BD 端口 **`pixel_clk_5x`** → rgb2dvi `SerialClk`（`clocks_route.rpt` 证实存在，2.695 ns） |
| 位流 | 不出（DRC 有意拦下） | **出位流 + XSA** |
| VDMA 帧存数 | IP 默认 3 | **`c_num_fstores = 2`** —— 与 `s5_display_app` 双缓冲（A/B 乒乓）约定一致，且少占地址 |
| 叠加 | 无 | **仍无**（不在 P3b 规格内） |

### 2.1 为什么走"外部 5× 时钟"而不是 rgb2dvi 内部 ClockGen

厂商本板参考 IP 配置（`rgb2dvi_0.xci` MODELPARAM）实测为：
`kGenerateSerialClk=false`、`kClkRange=1`、`kRstActiveHigh=false`。
即厂商在本板已验证的是**外部 5× 串行时钟**路线。本设计跟随：

- `rgb2dvi.vhd:109-129`：`kGenerateSerialClk=false` 时 `PixelClkIO<=PixelClk; SerialClkIO<=SerialClk`，**不引入第二个 MMCM**、无额外 CDC；
- 实测佐证：utilization 里 **MMCM 仍为 1**（若走内部 ClockGen 会变 2）；
- 额外好处：`pixel_clk` 与 `pixel_clk_5x` 出自**同一 clk_wiz MMCM**（CLKOUT0/CLKOUT1），1×/5× 相位确定，
  满足 `OutputSERDES.vhd:110-111`（`CLK => SerialClk, CLKDIV => PixelClk`）对 OSERDESE2 的要求。

### 2.2 rgb2dvi 端口接法依据（逐条对应源码行号）

| rgb2dvi 端口 | 接到 | 依据 |
|---|---|---|
| `TMDS_Clk_p/_n` | 顶层差分端口 → **U13**（N 端 V13） | `rgb2dvi.vhd:69-70,144-154`（ClockSerializer 发固定码 `"1111100000"`） |
| `TMDS_Data_p/_n(2:0)` | → **W14/Y18/Y16**（N 端 Y14/Y19/Y17） | `rgb2dvi.vhd:71-72,156-179` |
| `oen` | 顶层 `hdmi_oen` → **V16** | `rgb2dvi.vhd:192` 内部恒 `'1'`；厂商 `top.v:47` 直连该端口 |
| `aRst` | 常量 `'0'` | `kRstActiveHigh=false`（`rgb2dvi.vhd:101-107`：低有效分支只用 `aRst_n`） |
| `aRst_n` | 顶层像素域 POR（低有效，16 个 pixel_clk 后释放） | `rgb2dvi.vhd:77-78`；内部 `ResetBridge`（`SyncAsyncReset.vhd:63`）同步释放 |
| `vid_pData(23:0)` | BD `vid_data[23:0]` | `rgb2dvi.vhd:184-186`：`pDataOut(2)=vid_pData(23:16)` → **R 在 [23:16]**，与 BD 的 RGB888 通道顺序一致 |
| `vid_pVDE/pHSync/pVSync` | BD `vid_de/vid_hsync/vid_vsync` | `rgb2dvi.vhd:189-191`（HSync/VSync 走 channel0 control，VDE 作为三通道 blanking 指示） |
| `PixelClk` | BD `pixel_clk`（74.21875 MHz） | `rgb2dvi.vhd:85` |
| `SerialClk` | BD **`pixel_clk_5x`**（371.09375 MHz = 5×） | `rgb2dvi.vhd:87`；5× 关系见 `rgb2dvi_clocks.xdc:2`（`-multiply_by 5`） |

**generic 固定值**：由自有薄封装 `rtl/rgb2dvi_wrap.vhd` 固定（**Verilog 实例化 VHDL entity 不能覆盖 generic**，这是必须加这层的原因）：

```
kGenerateSerialClk => false, kClkPrimitive => "MMCM",
kClkRange => 1,              kRstActiveHigh => false
```

厂商 7 个 VHDL 文件**逐字节原样复制**（含 BSD 3-clause 许可头，未改内容），哈希在 §7。

### 2.3 TMDS 引脚依据与实际落点

依据：`...\02_hdmi_out_test\hdmi_out_test.srcs\constrs_1\new\hdmi_out_test.xdc` **第 4-17 行**（未臆造）。
实际布线结果（`out\io_route.rpt` 实测，全部 FIXED）：

| 信号 | PACKAGE_PIN | 实际 SITE | IOSTANDARD | 厂商行号 |
|---|---|---|---|---|
| `TMDS_clk_p` | **U13** | `IO_L3P_T0_DQS_PUDC_B_34` | TMDS_33 | L5-L6 |
| `TMDS_clk_n` | 由 P 推出 | `IO_L3N_T0_DQS_34` (V13) | TMDS_33 | L4 |
| `TMDS_data_p[0]` | **W14** | `IO_L8P_T1_34` | TMDS_33 | L8-L9 |
| `TMDS_data_n[0]` | 由 P 推出 | `IO_L8N_T1_34` (Y14) | TMDS_33 | L7 |
| `TMDS_data_p[1]` | **Y18** | `IO_L17P_T2_34` | TMDS_33 | L11-L12 |
| `TMDS_data_n[1]` | 由 P 推出 | `IO_L17N_T2_34` (Y19) | TMDS_33 | L10 |
| `TMDS_data_p[2]` | **Y16** | `IO_L7P_T1_34` | TMDS_33 | L14-L15 |
| `TMDS_data_n[2]` | 由 P 推出 | `IO_L7N_T1_34` (Y17) | TMDS_33 | L13 |
| `hdmi_oen` | **V16** | `IO_L18P_T2_34`（LVCMOS33, SLOW, 12 mA） | LVCMOS33 | L16-L17 |

差分对由 `OutputSERDES.vhd:83` 的 **OBUFDS** 内部生成 → 顶层只声明 `_p/_n` 两个端口、只给 `_p` 设 `PACKAGE_PIN`（与厂商 XDC 完全一致）。Bonded IOB 实测 = **9**（4 对 + oen）。

> ⚠️ **hdmi_oen 极性与 Lead 提示不一致，须上板确认**：Lead 提示"低有效、驱动 0 使能"，
> 但厂商源码 `rgb2dvi.vhd:192` 为 `oen <= '1'`、厂商 `top.v:47` 把该端口**直连** `hdmi_oen`，
> 即厂商参考实际驱动 **1**。本设计以厂商源码/参考工程为准（无依据不反相）。
> 若上板"有信号但屏不亮"，第一处置点 = 顶层把 `hdmi_oen` 反相（1 行）。

---

## 3. 时序结果

| 指标 | **P3b 实测** | P3a+ r02 | 变化 | 说明 |
|---|---|---|---|---|
| **WNS** | **+0.544 ns** | +0.041 ns | **+0.503** | P3a 的无引脚输出端口被移除后关键路径大幅改善 |
| **WHS** | **+0.022 ns** | +0.043 ns | −0.021 | 仍为正；最紧的 hold 来自 TMDS/OSERDES 附近 |
| **TNS / THS** | **0.000 / 0.000** | 0.000 / 0.000 | 不变 | 0 个失败端点 |
| WPWS / TPWS | 1.102 / 0.000 | 3.000 / 0.000 | — | 无脉冲宽度违例 |
| 端点总数 | 52,363 | 52,443 | −80 | |

**四域异步组的补充验证**：构建时 XDC 里的 `set_clock_groups` 仍因读取顺序失效（见 §6），
因此我在**已路由 DCP** 上用 Tcl 补加同样的三组异步关系后重算（`out\post_clkgrp.log`、`out\timing_post_clkgrp.rpt`）：

```
P3B_POST_CLOCKS: g0={clk_fpga_0} | g1={clk_fpga_1} | gp={clk_out1_...  clk_out2_...}
P3B_POST_CLKGRP=APPLIED
P3B_POST_WNS=0.544    P3B_POST_WHS=0.022     ← 与构建时完全相同
```

→ **结论：关键路径不跨时钟域，异步组缺失对时序数字没有任何影响**。
故 §3 的数字即最终数字，不存在"放宽后才达标"的问题。

---

## 4. 资源占用与 P3a+ 增量

| 资源 | P2d | P3a+ | **P3b 实测** | **P3b−P3a+（rgb2dvi）** | 上限 | G0 §4 预算 | 判断 |
|---|---|---|---|---|---|---|---|
| LUT | 23,451 (44.08%) | 25,895 (48.67%) | **25,967 (48.81%)** | **+72** | 53,200 | 29.5k–32.5k (55–61%) | **低于预算** |
| FF | 10,414 (9.79%) | 14,876 (13.98%) | **14,892 (14.00%)** | **+16** | 106,400 | 16k–18k (15–17%) | **低于预算** |
| BRAM | 33.5 | 36.5 (26.07%) | **36.5 (26.07%)** | **+0** | 140 | 42–54 (30–39%) | **低于预算** |
| DSP | 158 (71.82%) | 158 (71.82%) | **158 (71.82%)** | **+0** | 220 | 158 | **完全一致 ✔** |
| MMCM | 0 | 1 | **1** | **+0** | 4 | 1–2 | 预算内（未因 rgb2dvi 增加，证明走外部 5× 路线） |
| BUFG/BUFGCTRL | 1 | 4 | **5** | **+1** | 32 | — | 5× 时钟一个 BUFG |
| OSERDESE2 | 0 | 0 | **8** | **+8** | 125 组 | — | 4 通道 × 主/从 = 10:1 DDR 串行化 |
| Bonded IOB | 0 | 28（无引脚） | **9** | −19 | 125 | — | 4 差分对 + oen |

**判读**：
1. rgb2dvi 主要吃**专用原语**（OSERDESE2 ×8、1 个 BUFG），织物逻辑只 +72 LUT / +16 FF —— 几乎"免费"。
2. DSP 仍 **158（71.82%）、+0**，MMCM 仍 1 → 与 G0 §4 预期完全吻合。
3. LUT 48.81%，距 60% 预警线与 85% 门槛都有余量 → **后续叠加（G0 D2 框+文字）仍可行**。
4. 降级选项**未触发**（LUT<61%、WNS>0、WHS>0），故不实施；备用方案见 P3A_BUILD_REPORT §4。

---

## 5. DRC / 位流

### 5.1 DRC（`out\drc_route.rpt`，429 条，**0 error**）

| 规则 | 严重度 | 条数 | 解释 |
|---|---|---|---|
| `DPIP-1` | Warning | 129 | DSP48 输入流水线建议（2B 推理核固有，与 P2d 同类） |
| `DPOP-1` | Warning | 147 | DSP48 PREG 输出流水线建议 |
| `DPOP-2` | Warning | 148 | DSP48 MREG 输出流水线建议 |
| `DPREG-4` | Warning | 2 | DSP48 PregDynOpmodeZmuxP 用法提示 |
| `REQP-165` / `REQP-181` | Advisory | 1 / 2 | BRAM `writefirst` 模式建议 |

**`NSTD-1` / `UCIO-1` 已完全不出现** ✔（P3a 的 28 个无引脚端口已全部接真实引脚）。
`write_bitstream` 步骤自报 **"0 Critical Warnings and 0 Errors"**。

### 5.2 位流 / XSA

| 文件 | 字节数 | SHA-256 |
|---|---|---|
| `out\s4d_p3b_r01.bit` | **4,045,762** | `1670b0b38e4fef7ffe8021a99e4c9a1c0a92724e84f13d3fe5a8ca77a7b6f572` |
| `out\s4d_p3b_r01.xsa` | **376,153** | `2171583fbac75c00519d7633ff351b2f81feabbe1bc9b96953fdac1fff33719d` |

（原始位流亦保留在 `out\proj\s4d_p3b_r01.runs\impl_1\top_p3b.bit`）

---

## 6. 约束自证（`report_clocks` / `report_io`）

### 6.1 时钟（`out\clocks_route.rpt`）

| 时钟 | 周期 | 属性 | 来源 | 判定 |
|---|---|---|---|---|
| `clk_fpga_0` | 20.000 ns（50 MHz） | P | PS7 FCLKCLK[0] | ✔ |
| `clk_fpga_1` | 10.000 ns（100 MHz） | P | PS7 FCLKCLK[1] | ✔ |
| **`clk_out1_s4d_p3b_clk_wiz_0_0`** | **13.474 ns（74.21875 MHz）** | P,G,A | MMCM CLKOUT0 | ✔ 像素域 |
| **`clk_out2_s4d_p3b_clk_wiz_0_0`** | **2.695 ns（371.09375 MHz = 5×）** | P,G,A | MMCM CLKOUT1 | ✔ 串行域（**P3a 时不存在，P3b 已出现**） |
| `clkfbout_s4d_p3b_clk_wiz_0_0` | 80.000 ns | — | MMCM 反馈 | 忽略 |

### 6.2 仍存在的约束问题（诚实记录）
- `[Vivado 12-4739] set_clock_groups: No valid object(s)...` ×6（`p3b_tmds.xdc:34`）：
  **`PROCESSING_ORDER {LATE}` 实测并未解决**该读取顺序问题。构建因此少了异步组；
  已用 §3 的路由后补加证明**对数字零影响**。
  → `XDC_GUIDELINES.md` 已更正：LATE 不可靠，**必须用路由后补加或 impl `STEPS.OPT_DESIGN.TCL.PRE` 钩子**。
- `[Vivado 12-627] No clocks matched 'clk_fpga_0/1'` ×3：同源问题（synth 阶段）。
- 0 条 `[Designutils 20-1307]` ✔ （声明式 XDC 生效）。
- 其余 117 条 WARNING 全部良性：`Synth 8-7071/7023`（IP 可选端口未连接）59+19+10、
  `BD 41-1306` 4（vid_io_out 逐引脚连接，G0 要求离散端口）、`BD 41-3281` 4（双侧 SmartConnect）、
  `IP_Flow 19-5101` 3（SV 顶层 module reference）、`XPM_CDC_SINGLE TCL-1000` 4、`Vivado 12-627` 3 等。

---

## 7. 产物与哈希（SHA-256）

| 文件 | 字节 | SHA-256 |
|---|---|---|
| `bd_p3b.tcl` | — | `fc4da51e9a1831dea3d1be0b17265393e707bd9694717f8876c340b14f84717f` |
| `p3b_tmds.xdc` | — | `65178374e0fe4891e6ed100e8f61c7cb7a4ba69281a8dd267eec07e2acdf1e99` |
| `check_xdc_declarative.py` | — | （见 `out\xdc_static_check.log`） |
| `s5_p3b_build_20261030_r01_console.log` | — | `be4ee8f96ae34570ddc1bd907c91849979194fabd1f1b5adec7260f9a993dca3` |
| `s4d_p3b_r01.bit` | 4,045,762 | `1670b0b38e4fef7ffe8021a99e4c9a1c0a92724e84f13d3fe5a8ca77a7b6f572` |
| `s4d_p3b_r01.xsa` | 376,153 | `2171583fbac75c00519d7633ff351b2f81feabbe1bc9b96953fdac1fff33719d` |
| `out\timing_route.rpt` | 422,765 | `a862fad24b6f17f9a809383f0229b8bc77b816bb216545df78fb66e05bb55770` |
| `out\util_route.rpt` | 12,631 | `18aa1a2cacca9fe0a008d1360a6c9d0bd2c6fc9b08d148236864f931c3c04e68` |
| `out\drc_route.rpt` | 268,718 | `5c7579e9451a0f0474a3a4c2fa20540a15750deb26cf18095f036550a1ffff1a` |
| `out\clocks_route.rpt` | 3,468 | `a5c8ddc43b7af4965e9b50d530c37468881ddc3578576146f7cce43bcb8929d0` |
| `out\io_route.rpt` | 125,459 | `9a398ccc6d91310b979ca2e67522ec22c3eda97fb878270951b190d9cb5a6551` |
| `out\timing_post_clkgrp.rpt` | 422,771 | `55aa9b02742ca79950d8c8528eded18be44443784585b3b404f1595ed10e9bbe` |

厂商 VHDL（逐字节原样复制，与 `repo\ip\rgb2dvi_v1_3\src\` 哈希一致）：
`rgb2dvi.vhd 9EF5CEB9…`、`TMDS_Encoder.vhd B047A257…`、`OutputSERDES.vhd 6205D584…`、
`ClockGen.vhd 5DF9265E…`、`SyncAsync.vhd 5561AC80…`、`SyncAsyncReset.vhd 3CE7ADE3…`、`DVI_Constants.vhd D8DBBBC3…`

---

## 8. VTC AXI-Lite 寄存器表（软件侧对接，值必须一致）

**基址 `0x43C30000`**（64 KB）。偏移来自厂商驱动头文件
`D:\Xilinx\2026.1\Vivado\data\embeddedsw\XilinxProcessorIPLib\drivers\vtc_v8_5\src\xvtc_hw.h`（行号见下）。

### 8.1 本设计固化的 720p60 时序（与 Lead 给的软件约定逐项对齐）

| 时序量 | 值 | 核对 |
|---|---|---|
| H total / Hactive | 1650 / 1280 | ✔ H 1650 / HACT 1280 |
| HSync start / end | 1390 / 1430 | → HSW = **40** ✔；HBP = 1650−1430 = **220** ✔；HFP = 110 |
| V total / Vactive | 750 / 720 | ✔ V 750 / VACT 720 |
| VSync start / end | 724 / 729 | → VSW = **5** ✔；VBP = 750−730 = **20** ✔（v_tc 预设寄存器惯例） |
| 极性 | H/V Sync、H/V Blank、ActiveVideo 全 **High** | 720p 正极性 |

### 8.2 寄存器偏移与值

| 偏移 | 名称（xvtc_hw.h） | 值（720p60） | 说明 |
|---|---|---|---|
| `0x000` | `XVTC_CTL`（L150） | **`0x00000005`**（常规）；运行时重下时序则 `0x03FDEF05` + `RU` → **`0x03FDEF07`** | bit0 `SW` 核心使能 + bit2 `GE` 生成器使能；bit1 `RU` 寄存器更新 |
| `0x004` | `XVTC_ISR`（L151） | 只读 | 状态/中断状态 |
| `0x008` | `XVTC_ERROR`（L153） | 只读 | 错误状态 |
| `0x00C` | `XVTC_IER`（L154） | `0x00000000` | 本设计未用 VTC 中断（`HAS_INTC_IF=false`） |
| `0x010` | `XVTC_VER`（L156） | 只读 | 版本 |
| `0x060` | `XVTC_GASIZE`（L186） | **`0x02D00500`** | V(29:16)=720=0x2D0，H(13:0)=1280=0x500 |
| `0x068` | `XVTC_GFENC`（L188） | **`0x00000000`** | 逐行（progressive） |
| `0x06C` | `XVTC_GPOL`（L189） | **`0x0000003F`** | VBP/HBP/VSP/HSP/AVP/ACP 全高；FIP=0（fieldid 关闭） |
| `0x070` | `XVTC_GHSIZE`（L190） | **`0x00000672`** | H total 1650 = 0x672 |
| `0x074` | `XVTC_GVSIZE`（L192） | **`0x02EE02EE`** | F1(29:16)=750，F0(13:0)=750 |
| `0x078` | `XVTC_GHSYNC`（L194） | **`0x0596056E`** | end=1430=0x596，start=1390=0x56E |
| `0x07C` | `XVTC_GVBHOFF`（L197） | **`0x056E056E`** | 垂直 blank 的水平起止 = 1390/1390 |
| `0x080` | `XVTC_GVSYNC`（L199） | **`0x02D902D4`** | end=729=0x2D9，start=724=0x2D4 |
| `0x084` | `XVTC_GVSHOFF`（L201） | **`0x056E056E`** | 垂直 sync 的水平起止 = 1390/1390 |

### 8.3 软件侧两条可选路径（都合法，**值必须与 8.2 一致**）

1. **用 IP 固化时序（推荐，最少写寄存器）**：只写 `0x000 = 0x00000005`。
   依据 `XVTC_CTL_ALLSS_MASK = 0x03FDEF00`（xvtc_hw.h L301）是"源选择"位掩码：位为 0 的参数取自
   **IP 构建期默认值**（本设计即 720p60），置 1 才改用 AXI 寄存器值。
2. **`XVtc_GenerateTiming()` 运行时下发**：先置 `0x03FDEF00`，再按 8.2 写全部参数，最后置 `RU` → `0x03FDEF07`。

> `VID_PPC` 在非 arbitrary-res 模式被 v_tc 6.2 强制为 4（GUI 参数禁用），但标准 `vtiming_out` 仍是 1 pixel/clk，不影响上述寄存器语义（实测 720p 生成正常）。

---

## 9. VDMA 关键参数（软件侧对接）

| 参数 | 值 | 说明 |
|---|---|---|
| `c_include_mm2s/s2mm/sg` | 1 / 0 / 0 | 只读通道、非 SG 简单模式（写 DA/LENGTH 启动） |
| `c_m_axi_mm2s_data_width` | 64 | AXI-MM 侧（经 smc_vid → PS7 `S_AXI_HP2`） |
| `c_m_axis_mm2s_tdata_width` | 32 | 流侧 32 b（RGBA 承载 RGB888；`vid_data[23:0]` 由 xlslice 裁出） |
| `c_addr_width` | 32 | |
| **`c_num_fstores`** | **2** | **与 `s5_display_app` 双缓冲（A/B 乒乓）约定一致**；IP 默认 3 会与软件假设不符且多占地址 |
| `c_use_fsync` | 0 | 自由运行，由 `M_AXIS_MM2S` 的 TREADY 反压 |
| 基址 / 中断 | `0x43C40000` / `mm2s_introut → ps7_0/IRQ_F2P[0]` | |

帧存约定（供软件）：1280×720、RGB888 存 32-bit 字（`0xAARRGGBB`，alpha 忽略），
stride = 1280×4 = **5120 B/行**；2 个 frame store → 每帧 3,686,400 B（0x384000）。

---

## 10. 未尽事项 / 风险

1. **未上板（本报告不构成 G3/G4/G5）**：S6-A（上屏 ≥5 min）、S6-C（VDMA 读帧 CRC）、S6-D（叠加）、S6-E（P2d 7 项回归）、S6-F（30 min 稳定）全未做。
   本轮板级窗口因**板卡疑似未上电（JTAG TAP 全 0）**被阻断，非设计问题。
2. **`hdmi_oen` 极性待上板确认**（§2.3 ⚠️）：本设计遵厂商源码驱动 `1`；若屏不亮，第一处置点是反相（1 行）。
3. **TMDS 输出无 output_delay**：厂商参考同样没有、无板级 Tco 数据，不编造；以 S6-A 上屏为最终判据。
4. **四域异步组未在 XDC 生效**（§6.2）：`PROCESSING_ORDER {LATE}` 实测无效。已证明对时序数字零影响，
   但**下一步应改用"路由后补加"或 impl `TCL.PRE` 钩子**，把异步关系正式固化（`XDC_GUIDELINES.md` §2 已更正）。
5. **WHS 余量仅 +0.022 ns**：属"通过但偏紧"。若后续加叠加逻辑/换策略导致 hold 变差，需要关注（先看 TMDS 附近的 hold 路径）。
6. **OSERDESE2 ×8 走 BUFG 驱动**（与厂商参考一致），本次未触发任何 `CLOCK_DEDICATED_ROUTE` 类 DRC。
7. **叠加未实现**（G0 D2 框+文字属后续）：P3b 只保证"能出稳定 720p60 TMDS"。
8. **软件侧尚未对接**：VTC 寄存器（§8）与 VDMA 双缓冲（§9）的值已给出，但未在任何驱动/应用里验证过。