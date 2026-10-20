# S3-T05-PL2 J10 + 模块 CMOS2 交叉验证位流：证据入口

- 任务：task-7（Wong 2026-10-20 14:1x 同意把模块改插 J10 做交叉验证）
- RunId：`tmp/s3r06/t04_j10cmos2_20261020_r01`（新建，未复用）
- 基线提交（构建时 HEAD）：`c51b59374b3b068ed317e2cc52c4771d5dde71d6`（分支 `codex/stage3-video`）
- **真实退出码：0**（`synth_design Complete!` + `write_bitstream Complete!` + `ALL_DONE=1`，耗时 488 s）
- 只做构建：未下载、未烧 QSPI、未上板。

## 1. 用途与判读标准（本变体要回答什么）

已确认：模块 CMOS2 通道在 **J11** 上 I2C 通、数据在流，但 4 组独立实测 **RGB565 的 B[4] 恒为 0**
（蓝最大恒 120、从无 >127），R/G 正常到 248/236；我们的 J11 引脚映射已被四路证据确认正确
（D6 → F20 = J11 PIN5 = 模块 pin5）。本变体把模块改插 **J10**，改用官方双目例程 **cmos2 通道**的
FPGA 脚（与 J11 完全不同），以区分「板侧走线」与「模块走线」：

| 上板结果 | 结论 |
| --- | --- |
| J10 下蓝出现 **>127** 的像素 | 故障在**板侧 J11**（该口到 F20 的走线/焊点） |
| J10 下蓝**仍锁 120** | 故障在**模块侧**（模块 pin5/D6 走线或共用路径），因为两次连接共用同一模块引脚 |

注意：两种连接共用**同一个模块 D6 引脚**，因此本交叉验证能区分"板侧 vs 模块侧"，
但若 J10 仍失败，还需后续证据排除两者共有的其他环节。

## 2. 落点依据（两份独立资料一致）

- 官方 `23_ov5640_dual/src/constraints/an5642.xdc` 的 **cmos2 通道** 16 个 `PACKAGE_PIN`；
- AX7020 V3.0 手册 **Table 7.4.1**（J10 针脚表）。

| J10 pin | FPGA | 本设计端口 | 官方 cmos2 信号 |
| --- | --- | --- | --- |
| 3 | W19 | cmos1_d[9] | cmos2_d[9] |
| 4 | W18 | cmos1_i2c_sda_io | cmos2_i2c_sda_io |
| 5 | **R14** | **cmos1_d[6]** | **cmos2_d[6]** ← B[4] 缺失位对应的数据线 |
| 6 | P14 | cmos1_i2c_scl_io | cmos2_i2c_scl_io |
| 7 | Y17 | cmos1_d[7] | cmos2_d[7] |
| 8 | Y16 | cmos1_d[2] | cmos2_d[2] |
| 9 | W15 | cmos1_href | cmos2_href |
| 10 | V15 | cmos1_d[8] | cmos2_d[8] |
| 11 | Y14 | cmos1_d[3] | cmos2_d[3] |
| 12 | W14 | cmos_rstn_tri_o[0] | cmos_rstn_tri_o[1]（本设计为 1 位 GPIO） |
| 13 | P18 | cmos1_d[4] | cmos2_d[4] |
| 14 | N17 | cmos1_d[5] | cmos2_d[5] |
| 15 | U15 | cmos1_d[1] | cmos2_d[1] |
| 16 | U14 | cmos1_d[0] | cmos2_d[0] |
| 17 | P16 | cmos1_vsync | cmos2_vsync |
| 18 | P15 | cmos1_pclk | cmos2_pclk |

数据线映射与 J11 变体**完全同序**（D9..D0 → cmos1_d[9:0]），只换 FPGA 落点：
**J11 组 F/G/H/J/K/L/M → J10 组 W/V/R/P/Y/N/U**。

## 3. 落点证据（16/16 逐条命中）

`impl_1` 的 io_placed 报告逐条核对（`io_placed_check_J10.txt`，脚本 `verify_io_placement.py`）：

```
MATCHED=16/16
RESULT=ALL_16_MATCH_J10_TABLE     (全部 IOSTANDARD=LVCMOS33)
```

**阴性对照**（`io_placed_check_J11_negative_control.txt`）：把 **J11 变体**的 io_placed 报告按同一张
J10 期望表比对 = **MATCHED=0/16**，实际落点为 J11 的
`F17/F16/F20/F19/G20/G19/H18/J18/L20/L19/M20/M19/K18/K17/J19/K19`。
⇒ 该比对确实按 FPGA 脚逐条判定（而非解析失败后假通过），且本变体确实换到了**完全不同的 FPGA 脚**。

## 4. 构建结果

| 指标 | 本变体（J10+CMOS2，仅 SOF 补丁） | J11 SOF 变体 | J11 基线 04 run |
| --- | --- | --- | --- |
| WNS (ns) | **1.162281** | 1.054525 | 1.141183 |
| TNS (ns) | 0.000000 | 0.000000 | 0.000000 |
| WHS (ns) | **0.058777** | 0.058931 | 0.058332 |
| THS (ns) | 0.000000 | 0.000000 | 0.000000 |
| DRC Error | 0 | 0 | 0 |
| 峰值内存 (MB) | 2560.598 | 2568.176 | 2555.516 |
| 设计寄存器(synth) | 10548 | 10548 | 10534 |
| IP OOC 寄存器 | 415 | 415 | 401 |

DRC 8 条 Warning 明细与其它变体一致：PDCN-1569×3、PLCK-12×1、REQP-1839×2、REQP-1840×1、RTSTAT-10×1。
资源与 J11 SOF 变体完全相同（只改引脚落点，逻辑无变化），符合预期。

变体边界：**只应用 `alinx_ov5640_sof_hrefgap.patch`**（`fd854a62…`，`git apply` check/apply 均 RC=0），
**未应用**蓝位重建补丁（`s_axis_tdata_bluefix` 在最终 RTL 中不存在，保持"干净蓝通道"）；
`DEBUG_OV5640` 保持 `false`。RTL 哈希 = `db4857fe…`（仅 SOF 后）。

## 5. 产物（SHA-256）

| 产物 | 路径 | SHA-256 |
| --- | --- | --- |
| bitstream | `tmp/s3r06/t04_j10cmos2_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit` | `d4ce330b5dc706392530668166e2f8806bf09bd3a615c81455d3c26e195b9474` |
| XSA | `tmp/s3r06/t04_j10cmos2_20261020_r01/design_1_wrapper.xsa` | `7afe4174a732811ea19a6f7b782f8b2465210ebed194ef95cba11c95fe375c2e` |
| J10 约束 | `board/stage3/hardware/an5642_j10_cmos2.xdc` | `07fe96adf4d9ee752c2574616322f6844904995e08b77cf9aff9377ad9210de8` |

## 6. 本目录文件

- `build_report.json`：机器可读清单（命令/退出码/时序/DRC/内存/资源/bit+XSA 哈希/16 条落点明细/限制）
- `io_placed_check_J10.txt`：正向核验 16/16（含 iostandard）
- `io_placed_check_J11_negative_control.txt`：阴性对照 0/16
- `verify_io_placement.py`：独立落点比对脚本（可对任意 io_placed 报告重跑）
- `design_1_wrapper_io_placed.rpt`：io_placed 报告副本
- `alinx_ov5640_sof_hrefgap.patch`、`patch_git_apply.log`：所用补丁与其应用记录
- `report_*.rpt`、`vivado.log/.jou`（`.log`/`.jou` 被 gitignore）

## 7. 限制与未执行

- 只构建，未下载、未烧 QSPI、未上板；**插拔 J10 与蓝通道判读由阶段总控执行**。
- 仅构建本身不能定根因；必须配合上板蓝通道直方图（是否出现 >127 的蓝像素）。
- 若 J10 仍锁 120，仍不能排除两种连接共有的其他环节（模块内部共用走线、IP 内部该位处理）。
- SOF 修复的既有约束仍成立：复位后第一帧可能无 SOF；`GAP_THRESH=16384` 只对 1280x720(HTS=1892/VTS=740) 成立。
- 未做 RTL 功能仿真；未验证位流与基线功能一致性（仅时序/DRC/资源/落点对比）。
- 未提交 Git（由阶段总控统一提交）。