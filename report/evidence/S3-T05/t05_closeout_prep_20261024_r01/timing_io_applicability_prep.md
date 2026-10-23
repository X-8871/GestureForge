# TIMING-17/36 与 I/O delay：适用报告**准备**（绑定实际部署，2026-10-24）

- 依据：015 r03 §2.4「按实际部署时钟和板级资料核对相关时钟关系、输入输出延迟与例外，**在匹配版本上**给出适用时序/约束报告；
  **DRC 零错误或局部 WNS 为正不替代完整约束签核**」。
- 性质：**准备材料，不是结论**。本轮**未跑 Vivado**（离线报告本身需一个重型 Vivado 时段，属"不需要板卡"的下一步）。
- 绑定版本：见 `g2_material_list.json` 的 `actual_deployment`（SOF bit `7cb33068…`、XSA `1f5b138e…`、ELF `1457cda4…`、XDC `2dae928c…`、补丁 `fd854a62…`）。

## 1. 已知缺口（既有证据，非本轮新结论）

| 缺口 | 已知事实 | 证据 |
|---|---|---|
| **TIMING-17**（未约束内部端点 / I/O delay 缺失） | 方法学 **critical 236** | `report/evidence/S3-CTRL/S3-T05/S3CTRL-20261021-003-handoff-to-dsh-stage3.md:62` |
| **TIMING-36**（critical 1）与 `CRITICAL WARNING [Timing 38-249]` | `rgb2dvi` 的 `SerialClk`（=PIX_CLK×5）与 `axi_dynclk_0_PXL_CLK_O` 之间**未声明 5 倍关系**；DRC 0 error、WNS/WHS 为正 | `report/evidence/S3-T03/t03b_hdmi_build_20261020_r01/bringup_record.md:34`、`t05_v6_board_20261020_r01/README.md:52` |
| 部署版本时序（仅作基线，不是签核） | WNS `1.054525` / TNS `0` / WHS `0.058931` / THS `0`；DRC 0 error / 8 warning / 0 critical；`write_bitstream Complete!` | `t05_sof_fix_20261020_r01/build_report.json` |

纪律（015 §2.4 明示）：**不得加虚假时钟关系或豁免来换通过**；`DRC 0 error`、局部 `WNS>0` 均不替代完整约束签核。

## 2. 时钟关系核对清单（对实际部署）

资料来源优先级：① 实际部署设计（XSA/实现检查点）与 `board/stage3/hardware/an5642_j11_cmos2.xdc`；② 厂商源（`rgb2dvi.vhd`、`alinx_ov5640.v`、驱动 `ov5640.c`）；③ 板级资料（AX7020 V3.0 手册/原理图，页码须记录）。

| # | 需核对对象 | 判定问题 | 期望产出 |
|---|---|---|---|
| C1 | 采集域：传感器 PCLK（设计依据 `84 MHz`，HTS=1892/VTS=740）| 是否 `create_clock` 且频率/波形与驱动寄存器一致 | 时钟名、周期、来源行号 |
| C2 | `cmos_d[9:0]` 输入采样 | 输入端口是否有时钟关联 + 采样边沿说明 | 端口、时钟、边沿 |
| C3 | `rgb2dvi` `SerialClk` 与 `PXL_CLK_O` | **5 倍生成关系**是否已声明（`Timing 38-249` 的根因）| 声明方式或**显式 NOT_APPLICABLE + 资料依据** |
| C4 | 显示域：VDMA MM2S / HDMI 输出时钟 | 时钟交叉是否已按同一设计声明（不引入虚假关系）| 时钟表 + 交叉清单 |
| C5 | PS/AXI：FCLK 与 VDMA/AXI 互连 | 异步/同步关系与已声明例外 | 结论 + 依据 |
| C6 | `set_clock_groups`/`set_false_path` 现存例外 | 每条例外是否有依据、是否覆盖实际路径 | 例外台账（逐条依据）|

## 3. I/O delay 与例外核对清单

| # | 端口组 | 需资料 | 若资料不足时的处理 |
|---|---|---|---|
| I1 | `cmos_d[9:0]`、`pclk`、`vsync/href`（采集输入） | 传感器数据手册建立/保持 + 模块走线延迟 | **NOT_APPLICABLE + 资料缺失理由**（不得编造数值） |
| I2 | I2C（`scl/sda`）| 器件上升/下降与上拉条件 | 同上 |
| I3 | HDMI 输出（TMDS/时钟，经 `rgb2dvi`）| 输出时序要求与板级走线 | 同上 |

每条必须写成三态之一：**APPLICABLE_CLOSED**（有依据且约束齐）/ **APPLICABLE_OPEN**（有依据但未约束）/ **NOT_APPLICABLE**（说明理由与批准范围）。

## 4. 离线执行步骤（下一步，不需要板卡；需一个重型 Vivado 时段）

```bash
# 在 dbdf 内，一次只跑一个重型 Vivado 任务；打开实际部署的实现检查点（勿重新综合）
bash scripts/stage3_t03b/run_xsdb.sh ...          # 仅 JTAG 只读时用；本步不需要
D:/Xilinx/2026.1/Vivado/bin/vivado -mode batch -source <新 run 的 read-only 报告脚本>
#   report_clocks / report_methodology -checks timing / report_timing_summary / report_exceptions
#   输出：新 RunId report/evidence/S3-T05/<run_id>/{clocks.txt,methodology_timing.txt,timing_summary.txt,exceptions.txt}
```
- 输出目录必须是**新 RunId**；命令、工作目录、Vivado 版本、**真实退出码**、原始输出全部留证。
- 结论按 §2/§3 的清单逐项写三态，并**绑定本次部署哈希**；本次 G2 材料已固定这些哈希（见 `g2_material_list.json`）。
- 本步**不改** XDC、不加豁免、不植入调试核。

## 5. 本轮状态

- 本文件为**准备**：清单、判定三态、资料优先级、离线执行命令与留证要求。
- **NOT_RUN**：Vivado 离线报告、I/O delay 数值核对、方法学复核（需重型时段，未启动）。
- 既有 `Timing 38-249` / TIMING-17 critical 236 等**仍为开放**，不得因本轮整理而被视为关闭。