# TIMING-17/36 与 I/O delay：适用性报告（固定版本 = 当前部署）

- 被评版本：**实际部署** —— 无补偿 SOF bit `7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710`、
  XSA `1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3`、
  ELF `an5642_j11cmos2_v10_read.elf` `1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073`；
  约束 = `board/stage3/hardware/an5642_j11_cmos2.xdc`（sha256 `2dae928c9458a71ebc9ae741e71f7a274c18afc237676852c53d5e61bbeff5b2`，**仅引脚/IOSTANDARD/PULLUP/CLOCK_DEDICATED_ROUTE**）。
- 依据报告（**已入库、本版实测产物**）：
  `report/evidence/S3-T05/t05_sof_fix_20261020_r01/report_timing_summary_impl.rpt`（`report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose`）、
  `…/report_drc_impl.rpt`、`…/build_report.json`。
- 性质：**离线适用性判定**；本轮**未**重跑 Vivado。判定三态：`APPLICABLE_CLOSED` / `APPLICABLE_OPEN` / `NOT_APPLICABLE(理由)`。

## 1. 版本实测数字（勿与旧轮混用）

| 项 | 值 |
|---|---|
| WNS / TNS / TNS 失败端点 / 总端点 | **1.055 ns / 0.000 / 0 / 21479** |
| WHS / THS / THS 失败端点 / 总端点 | **0.059 ns / 0.000 / 0 / 21344** |
| WPWS / TPWS / 失败 / 总 | 0.529 ns / 0.000 / 0 / 9587 |
| DRC | **0 Error / 8 Warning / 0 Critical**（与基线 run 明细一致） |
| `check_timing -verbose` | **`no_clock (240)`、`unconstrained_internal_endpoints (520)`** |

## 2. 时钟关系（Clock Summary，本版实测）

| 时钟 | 周期/频率 | 来源 |
|---|---|---|
| `clk_fpga_0` | 10.000 ns / 100 MHz | PS FCLK_CLK0（BD `design_1_processing_system7_0_0.xdc`：`create_clock -period 10`） |
| `clk_fpga_1` | 7.000 ns / 142.857 MHz | PS FCLK_CLK1（同上，`-period 7`） |
| `axi_dynclk_0_PXL_CLK_O` | 10.000 ns / 100 MHz | 动态时钟 IP 输出 |
| `design_1_i/rgb2dvi_0/U0/SerialClk` | 2.000 ns / 500 MHz | **IP 自带约束**：`create_generated_clock -source [get_ports PixelClk] -multiply_by 5 [get_ports SerialClk]`（`…/my_ip/rgb2dvi_v1_3/src/rgb2dvi_clocks.xdc`） |
| `mmcm_fbclk_out` | 10.000 ns / 100 MHz | MMCM 反馈 |

**关键事实（与旧记录不同，需更正）**：`SerialClk` 的 **×5 关系是被声明的**（IP XDC + Clock Summary 都成立）。
但本版构建日志**仍然出现** `CRITICAL WARNING [Timing 38-249]`（`build_report.json` 的 `log_messages`）。
⇒ 该告警**不是**"×5 未声明"，更可能是**生成时钟的源对象与 BD 时钟对象不同**（IP 生成时钟源是 **IP 端口 `PixelClk`**，
而 BD 实际驱动它的是 `axi_dynclk_0_PXL_CLK_O` 这一时钟对象）；表现为告警而非时序失败（WNS/WHS 为正、TNS/THS=0）。
**结论：`38-249` 归因 = 假设（有依据但未证实）**，确认方式见 §5。

## 3. 逐项判定

| # | 项 | 判定 | 依据 |
|---|---|---|---|
| C1 | PS FCLK 与显示域内时钟已声明 | **APPLICABLE_CLOSED** | Clock Summary 出现 `clk_fpga_0/1`、`axi_dynclk_0_PXL_CLK_O`、`SerialClk`；组内 WNS/WHS 为正 |
| C2 | **采集域 `cmos1_pclk` 是否有 `create_clock`** | **APPLICABLE_OPEN** | Clock Summary **无 `cmos1_pclk`**；用户 XDC 无 `create_clock`；`no_clock (240)` |
| C3 | `rgb2dvi` SerialClk ×5 关系 | **APPLICABLE_CLOSED（声明在 IP XDC）** + 告警归因待证 | §2；`38-249` 仍在日志中 ⇒ 归因假设见 §5 |
| I1 | 采集输入 `cmos1_d[9:0]` / `pclk` / `href` / `vsync` 的 I/O delay | **APPLICABLE_OPEN** | 用户 XDC 无任何 `set_input_delay`；`unconstrained_internal_endpoints (520)`、Unconstrained Path Table 的 `(none) → clk_*` 行 |
| I2 | I2C（`cmos1_i2c_scl_io`/`sda_io`）I/O delay | **APPLICABLE_OPEN** | 同上（仅有 PULLUP/IOSTANDARD） |
| I3 | HDMI 输出（经 `rgb2dvi`）的 output delay | **APPLICABLE_OPEN（用户约束侧）** | 用户 XDC 无 `set_output_delay`；IP 内置输出路径约束未在本轮逐条核对（见 §5） |
| C4 | `CLOCK_DEDICATED_ROUTE FALSE [get_nets cmos1_pclk_IBUF]` | **有意识例外，需登记** | 用户 XDC 显式放宽（PCLK 未走专用时钟引脚）；**属"已知例外"，不得当作隐藏缺省** |
| E1 | 现存 false path / multicycle / clock groups | **无**（用户 XDC 未定义） | ⇒ 不存在"用虚假例外换通过"的情况；但也意味着 **C2/I1–I3 的跨域路径未被约束** |

## 4. 与验收口径的关系（015 §2.4）

- **DRC 0 error / 局部 WNS>0 不能替代完整约束签核** ⇒ 上表 **C2/I1/I2/I3 四项 OPEN** 即"约束缺口"未关闭。
- 上述 OPEN 项**不阻断**当前实时彩色功能的**已实现事实**（本版时序为正、DRC 干净、板上 31 min 稳定），
  但**阻断**"完整时序/约束签核"这一验收维度。
- 未新增任何豁免或虚假时钟关系。

## 5. 关闭所需的离线动作（不需要板卡；需一个重型 Vivado 时段）

1. 在实际部署的实现检查点（`tmp/s3r06/t04_sof_fix_20261020_r01/project/…/impl_1/*_routed.dcp`）上跑只读：
   `report_clocks`、`report_exceptions`、`report_methodology -checks timing`、`report_timing_summary -report_unconstrained`，
   输出到**新 RunId**，逐项替换本报告 §1/§2 的"本版实测"数字（本报告已用本版既有报告，等价）。
2. 归因 `38-249`：读 `rgb2dvi_clocks.xdc` 的生成时钟源对象 + BD 中 `PixelClk` 的实际连接，
   判定是"源对象不同"还是"IP 约束未生效"；据实登记（不得删告警凑通过）。
3. I/O delay：需要**板级资料**（传感器数据手册建立/保持 + 模块走线；HDMI 输出时序要求）。
   资料不足 ⇒ 按 §6 记 `NOT_APPLICABLE + 理由`，**不得编造数值**。

## 6. 资料可得性（本轮回查）

- 盘上**无 PG020/AXI VDMA 官方手册**（详见 `vdma_fsz_more_analysis.md` §4）；
- OV5640/AN5642 板级 I/O 时序资料**未在本树入库**；AX7020 V3.0 手册/原理图的引用目前在既有证据中为**引脚层面**（Table 7.5.1），未见数据建立/保持章节。
⇒ 因此 **I1/I2/I3 当前无法给数值约束**，只能记 **OPEN**（有缺口、无依据），并把"取得资料或明确批准范围排除"列为关闭条件。

## 7. 本轮状态

- **已完成**：基于本版既有报告的适用性判定（三态）、时钟表复算、`38-249` 归因假设与确认路径、资料可得性回查。
- **NOT_RUN**：Vivado 离线报告重跑、I/O delay 数值、`38-249` 归因确认。
- **仍开放**：C2、I1、I2、I3（约束缺口）、`38-249` 归因。**本报告不等于时序签核通过。**
