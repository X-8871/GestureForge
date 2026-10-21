# S3-T05-PL3 双位重建 + 水平 3 抽头多数：证据入口

> ⚠ **近似补偿、非真实修复、不得用于颜色验收。**
> 真实故障是**模块侧 DVP 字节 MSB 线 `cmos_d[9]` 无信号**，导致 16 位字里两个位同时丢失。
> 本变体只是在 PL 侧用相邻位近似重建这两位并做多数平滑；硬件返修后应回到无补偿位流重新验收颜色。

- 任务：task-9（2026-10-21 指派）
- RunId：`tmp/s3r06/t04_dualmsb_20261021_r01`（新建，未复用）
- 基线提交（构建时 HEAD）：`65f2b6b9625a788e99f2808df69ec01962ec4e68`（分支 `codex/stage3-video`）
- **真实退出码：0**（`synth_design Complete!` + `write_bitstream Complete!`，耗时 537 s）；网表核对 `TRACE_EXIT=0`
- 只做构建：未下载、未烧 QSPI、未上板。

## 1. 位序与被丢的两位（本轮经网表分析 + 行样本签名确认）

16 位字布局：`word[15:11] = B[4:0]`，`word[10:5] = G[5:0]`，`word[4:0] = R[4:0]`。

| 丢失位 | 位置 | 来源 |
| --- | --- | --- |
| B[4] | **word[15]** | 第一字节 MSB（DVP `cmos_d[9]`） |
| G[2] | **word[7]** | 第二字节 MSB（同一根 `cmos_d[9]`） |

实测最大值与该位序**完全自洽**：R max 248 = 31<<3（R[4]=1，正常）、G max 236 = 59<<2（59=0b111011，G[2]=0）、
B max 120 = 15<<3（15=0b01111，B[4]=0）。

> ❗ 更正上一轮：task-6 的蓝位补丁按 `word = {R,G,B}` 的**错误位序**重建了 `word[4]`——
> 在实际位序里那是 **R[4]**，所以既没修好蓝位、又改坏了红的最高位（这解释了目视"阴影偏蓝、亮部偏黄、明显伪彩"）。
> task-6 的位流（bit `0819d0da…`）**不要再使用**；本变体的补丁已取代它，且最终 RTL 中不含其标记
> `s_axis_tdata_bluefix`（已在构建脚本里断言）。

## 2. 补偿做了什么

```
重建位表（显式，逐位）：
  B'[4] = B[3] = tdata[14]        G'[2] = G[3] = tdata[8]        其余位原样
新字：
  new = { maj3(B[3]), tdata[14:11], tdata[10:8], maj3(G[3]), tdata[6:5], tdata[4:0] }
→ new[15] = B'[4] 走多数表决，new[7] = G'[2] 走多数表决，其余 14 位与原字逐位相同。
```

**水平 3 抽头多数表决**（独立 `wire`/`always` 块，只作用于这两个重建位）：

```
maj = (c0 & c1) | (c0 & c2) | (c1 & c2)      // c0=当前像素, c1/c2=前 1/2 个像素
```

- 只用**像素率延迟寄存器**（每位 2 个 DFF，共 4 个新寄存器 `dualmsb_b4_d1/d2`、`dualmsb_g2_d1/d2`），
  **不使用行缓冲/BRAM**；
- 窗口是**因果关系**的（当前 + 前 2 个像素）；数据流本身不额外延迟，
  因此 `tvalid/tlast/tuser` 仍与字对齐（未改动 tlast/tuser/tkeep/tvalid/tready 与时钟/时序）；
- 未打开 `DEBUG_OV5640`（保持 `false`）。

## 3. 网表核对：重建位确实接到了 FIFO din（本轮硬证据）

`din = {word, tlast, tuser}`（18 位）⇒ `din[i] = word[i-2]`，故重建位落在 **din[17]**（B'[4]）与 **din[9]**（G'[2]），
参考位 B[3]→din[16]、G[3]→din[10]。用 `netlist_din_trace.tcl` 打开 IP 的 OOC 综合检查点逐位回溯驱动：

| 位 | 基线（仅 SOF 补丁） | 本变体（SOF + 双位重建） |
| --- | --- | --- |
| din[17] = B'[4] | `cmos_d_16bit_d1_reg[15]/Q`（单个 FDRE，1 根） | **LUT3 `xpm_fifo_async_inst_i_3`，3 输入**，根驱动 = {`cmos_d_16bit_d1_reg[14]/Q`, `dualmsb_b4_d1_reg/Q`, `dualmsb_b4_d2_reg/Q`} |
| din[16] = B[3] | `...reg[14]/Q` | `...reg[14]/Q`（∈ din[17] 的根集合） |
| din[9] = G'[2] | `...reg[7]/Q`（单个 FDRE，1 根） | **LUT3 `xpm_fifo_async_inst_i_4`，3 输入**，根驱动 = {`...reg[8]/Q`, `dualmsb_g2_d1_reg/Q`, `dualmsb_g2_d2_reg/Q`} |
| din[10] = G[3] | `...reg[8]/Q` | `...reg[8]/Q`（∈ din[9] 的根集合） |
| din[8]/din[7]/din[2] | 单个 FDRE | 单个 FDRE（未受影响） |

⇒ B'[4] 是 **B[3] 的三抽头多数**、G'[2] 是 **G[3] 的三抽头多数**，且**只有这两位**被改动。
日志：`netlist_din_trace.log`（本变体）、`netlist_din_trace_baseline.log`（基线对照）、脚本 `netlist_din_trace.tcl`。

**核对脚本修正记录（诚实留档）**：首次运行的 `roots_of_pin` 只取组合单元输出管脚、未下钻其输入，
把 LUT3 驱动误判成"1 个根驱动"，于是报告曾写成 `status=failed / NETLIST_CHECK_PASSED=False`。
修正为下钻 LUT 输入后，对**同一份 OOC DCP** 复跑核对即通过；**复跑前后 bit/XSA 哈希完全一致**
（`30db09ba…` / `cf15a02c…`），未重建、未改动产物。构建本身始终是 `VIVADO_EXIT=0`。
详见 `build_report.json` 的 `netlist_check_correction` 与 `update_netlist_confirmation.py`。

## 4. 补丁身份与顺序

| 补丁 | SHA-256 | hunks | +/− |
| --- | --- | --- | --- |
| 1/2 `alinx_ov5640_sof_hrefgap.patch`（已有） | `fd854a62…b2c5` | 3 | +24 / −5 |
| 2/2 `alinx_ov5640_dual_msb_rebuild.patch`（本任务） | `635c886d…2616` | 2 | +51 / −1 |

RTL 哈希：厂商原件 `98260b62…` → 仅 SOF `db4857fe…` → SOF+DUAL `1d7b8668…`（本构建实际使用）。

顺序实测（`patch_apply_order_test.txt`）：A) DUAL 单独对厂商原件 `--check/apply` 均 RC=0；
B) SOF→DUAL 全 RC=0；C) DUAL→SOF 全 RC=0 且与 B **逐字节相同**；
D)（信息性）在 SOF+DUAL 之上再叠旧蓝位补丁 **失败**（同一行 `.din`），故本变体明确不使用它。

## 5. 构建结果

| 指标 | 本变体（SOF+DUAL） | SOF 变体 | 基线 04 run |
| --- | --- | --- | --- |
| WNS (ns) | **1.171408** | 1.054525 | 1.141183 |
| TNS (ns) | 0.000000 | 0.000000 | 0.000000 |
| WHS (ns) | **0.053436** | 0.058931 | 0.058332 |
| THS (ns) | 0.000000 | 0.000000 | 0.000000 |
| DRC Error | 0 | 0 | 0 |
| 峰值内存 (MB) | 2563.582 | 2568.176 | 2555.516 |
| 设计寄存器(synth) | 10544 | 10548 | 10534 |
| IP OOC 寄存器 | 411 | 415 | 401 |

DRC 8 条 Warning 明细与其它变体一致：PDCN-1569×3、PLCK-12×1、REQP-1839×2、REQP-1840×1、RTSTAT-10×1。
日志中 0 条 ERROR（本次无 OOC 启动抖动）。

> FF 计数说明：本变体新增 4 个延迟寄存器（网表中确实可见 `dualmsb_*_d1/d2_reg/Q`），但 IP OOC 寄存器
> 从 SOF 的 415 变成本次的 411，属**综合优化差异**（小改动下该计数不稳定），**不作为资源增量的依据**；
> 重建位是否落地以第 3 节的 din 连通性核对为准。

## 6. 产物（SHA-256）

| 产物 | 路径 | SHA-256 |
| --- | --- | --- |
| bitstream | `tmp/s3r06/t04_dualmsb_20261021_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit` | `30db09ba8e4e9df8fca73429ce7e941988391b4475fc88d19ebc86469fff23e4` |
| XSA | `tmp/s3r06/t04_dualmsb_20261021_r01/design_1_wrapper.xsa` | `cf15a02c36b4ba33ed4a5430e70ccc5d4a5960932266b25ade2c1cc177a3ce36` |
| 双位重建补丁 | `board/stage3/software/sensor/alinx_ov5640_dual_msb_rebuild.patch` | `635c886dfdcd0e2517fec86a3ca7239ac805091c54cc907e13510501e6cd2616` |
| J11+CMOS2 约束 | `board/stage3/hardware/an5642_j11_cmos2.xdc` | `2dae928c9458a71ebc9ae741e71f7a274c18afc237676852c53d5e61bbeff5b2` |

## 7. 已知误差（必须随波一起说明）

1. **低蓝/暗部残差**：`B'[4]=B[3]` 等价于把蓝的低 4 位区间做 2 倍拉伸，暗部/低饱和蓝的量化误差被放大；
   绿 `G'[2]=G[3]` 同理影响绿的次高位。
2. **亮部可能过冲**：真实 `B[4]=0` 而 `B[3]=1` 的亮色会被判成 `B[4]=1`，蓝偏高；多数表决只能压掉孤立过冲。
3. **整帧仍非真实颜色**：本变体不构成任何颜色正确性证据，**不能用于颜色验收/标定**；
   这是硬件返修期间的明示近似补偿。
4. 三抽头多数是因果窗口（当前 + 前 2 像素），不是居中窗口——为保持数据流与 tvalid/tlast/tuser 对齐而未延迟数据。

## 8. 本目录文件

- `build_report.json`：机器可读清单（命令/退出码/补丁身份+RTL 哈希/网表核对/时序/DRC/内存/资源/产物哈希/限制）
- `alinx_ov5640_dual_msb_rebuild.patch`、`alinx_ov5640_sof_hrefgap.patch`、`alinx_ov5640_blue_msb_rebuild_superseded.patch`
- `patch_apply_order_test.txt`、`patch_git_apply.log`
- `netlist_din_trace.tcl` + `netlist_din_trace.log` + `netlist_din_trace_baseline.log`
  （另有一批 `netlist_din_trace*_<pid>.backup.log/.jou`：Vivado 同名日志轮转产生的原始历史，
  含最初那次核对脚本有 bug 的运行；全部被 `.gitignore` 的 `*.log`/`*.jou` 规则忽略，仅为本地原始留档）
- `update_netlist_confirmation.py`（核对脚本修正后更新报告，不改产物）
- `make_dual_msb_rebuild_patch.py`（补丁生成器，含锚点断言 + hunk 往返自检 + 位表自检）
- `patch_verification/`：`pristine` / `dual_only` / `combined_sof_then_dual` 三方 RTL + 补丁，供 byte-level 复核
- `report_*.rpt`、`vivado.log/.jou`（`.log`/`.jou` 被 gitignore）

## 9. 限制与未执行

- 只构建，未下载、未烧 QSPI、未上板；上板与目视/直方图判读由阶段总控执行。
- **近似补偿**：真实修复需要硬件返修模块侧 DVP 字节 MSB 线；返修后必须回到无补偿位流重新验收颜色。
- 未做 RTL 功能仿真；未验证位流与基线功能一致性（仅时序/DRC/资源/网表连通性对比）。
- SOF 既有约束仍成立：复位后第一帧可能无 SOF；`GAP_THRESH=16384` 只对 1280x720(HTS=1892/VTS=740) 成立。
- 未提交 Git（由阶段总控统一提交）。