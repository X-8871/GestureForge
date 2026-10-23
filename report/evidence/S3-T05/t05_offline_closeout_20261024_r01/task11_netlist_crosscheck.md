# task-11：网表交叉核对（离线有界版，2026-10-24）

- 背景：既有 STATE 长期记「task-11 网表交叉核对未完成（补丁已人工审阅）」。本轮用**已入库产物**做**有界**核对，不需要板卡。
- 对象：SOF 修复补丁 `board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch`
  （sha256 `fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5`，目标 `my_ip/ov5640_ip/src/alinx_ov5640.v`）
  是否真实进入**部署版（`t04_sof_fix_20261020_r01`）** 的综合结果。

## 1. 证据链（逐环节哈希）

| 环节 | 证据 | 值 |
|---|---|---|
| 补丁 | `t05_sof_fix_20261020_r01/build_report.json` → `patch` | sha256 `fd854a62…`；`change_summary` = tuser 触发改「hblank 连续低 ≥ `GAP_THRESH=16384` pclk 后首个有效像素」+ 新增饱和计数器 |
| 部署 XSA | 实测 | `1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3` |
| **OOC 综合后网表**（本设计内被综合的厂商 IP） | `tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0_sim_netlist.v` | 227,006 B，sha256 **`7b8f457c1cd5377367b3032369ba72fc5d00ac465629ecd970d6fb7e479b852a`** |
| OOC 利用率报告 | 同目录 `…_utilization_synth.rpt` | 8,440 B（存在） |

## 2. 网表核对结果（本版实测）

在 `design_1_alinx_ov5640_0_0_sim_netlist.v` 中（大小写不敏感计数）：

| 目标构造 | 命中 |
|---|---|
| `cmos_hblank_low_cnt`（补丁新增的饱和计数器） | **160 处** |
| `cmos_hblank*`（含 `cmos_hblank`、`cmos_hblank_d0/d1`、`cmos_hblank_low_cnt[*]` 等） | **192 处**（其中 160 处含 `cmos_hblank_low_cnt`）；另 `hblank`（不分前后缀，含注释）198 处 |
| 字面量 `16384` / `0x4000` / `16383` | **0 处** |

**判读**：补丁引入的**计数器与其 hblank 采样链在部署版的综合后网表中确实存在** ⇒ 补丁不是"只改了源码、未进综合"。
`GAP_THRESH` 的**数值**在综合后已折入 LUT 常量（`INIT`），**不能**从网表按字面量读出 ⇒ 本轮**不声称**已核对阈值数值。

## 3. 判定与边界

- **有界核对结论**：`补丁 → 部署 XSA → 该 IP 的 OOC 综合后网表` 三环节**存在性一致**（`APPLICABLE_CLOSED`，限于"补丁构造已进综合"）。
- **未做（NOT_RUN）**：
  1. 阈值数值的网表级核对（需在 OOC DCP 上做 `report_property`/等效性检查，或读综合日志中的参数展开）；
  2. RTL↔网表**等价性**核对（需 Vivado 或形式化工具，离线但重型；本设计**未做 RTL 仿真**，属既有缺口）；
  3. 时序路径级核对（并入 `timing_io_applicability_report.md` 的约束缺口项）。
- 因此本文件**不能**替代完整网表核对；它把该项从"完全未做"推进到"**补丁进入综合已有网表证据、阈值数值与等价性仍未核**"，并给出可复跑的哈希与命令。

## 4. 复跑命令（只读）

```bash
nl=tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0_sim_netlist.v
sha256sum "$nl"
grep -c cmos_hblank_low_cnt "$nl"      # 160（本窗口实测）
grep -c cmos_hblank "$nl"              # 198
```
