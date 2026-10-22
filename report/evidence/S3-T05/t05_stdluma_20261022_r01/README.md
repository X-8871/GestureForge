# S3-T05-PL5 标准亮度灰度位流证据（task-13）

更新：2026-10-22 12:05（UTC+8）｜工作树 `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`／基线提交 `eb4599690249a26a311c82222643a64f26c2b74e`
RunId：`tmp/s3r06/t04_stdluma_20261022_r01`｜证据目录：`report/evidence/S3-T05/t05_stdluma_20261022_r01/`

> ## ⚠ 性质声明：**灰度补偿，非修复**
> 本变体只是为了把 PL 直通监视器的观感从「偏黄伪彩」换成**标准亮度黑白**，让画面与 Wong 的训练输入（彩色照片按 0.299R+0.587G+0.114B 转灰度）尽量一致。
> - **没有修复任何故障**：模块侧 DVP 字节 MSB 线 `cmos_d[9]` 仍然无信号（根因见 `t05_msb_line_diagnosis_20261021_r01/`、`t05_v9_board_20261021_r01/`）。
> - **蓝通道仍以「猜位」参与亮度**：B'[4] 直接复制 B'[3]，并按 0.114 权重进入 Y。因此本变体**不构成颜色正确性证据，不得用于颜色验收**。
> - 真实修复仍需**硬件返修/更换模块**（只寄模块，不寄 AX7020 板卡）。
> - 本位流**未上板、未下载、未烧 QSPI**；上板与目视判读由阶段总控另行执行。

---

## 1. 做了什么（只改厂商 IP 的 PL 侧输出字）

新补丁：`board/stage3/software/sensor/alinx_ov5640_stdluma_gray.patch`（只改 `my_ip/ov5640_ip/src/alinx_ov5640.v`，2 个 hunk：FIFO `.din` 前插入灰度块 + 改 `.din`）

位序（已确认）：`word[15:11]=B[4:0]`、`word[10:5]=G[5:0]`、`word[4:0]=R[4:0]`；缺的两位 = `word[15]`(B[4]) 与 `word[7]`(G[2])，同源于 `cmos_d[9]`。

```verilog
R8  = {tdata[4:0], 3'b000}                                    // R[4:0]
G'  = {tdata[10], tdata[9], tdata[8], maj3(tdata[8]), tdata[6], tdata[5]}
G8  = {G'[5:0], 2'b00}
B'  = {tdata[14], tdata[14], tdata[13], tdata[12], tdata[11]}  // B'[4] = B'[3] = B[3]（猜位）
B8  = {B'[4:0], 3'b000}
Y   = (77*R8 + 150*G8 + 29*B8) >> 8                           // 0.3008/0.5859/0.1133 ≈ 0.299/0.587/0.114
new = {Y[7:3], Y[7:2], Y[7:3]}                                // R5=B5=Y>>3, G6=Y>>2
```

- `maj3` = 水平 3 抽头多数 `(c0&c1)|(c0&c2)|(c1&c2)`，**只**用于重建的 `G'[2]`；实现是 2 个像素率延迟寄存器 + 1 个多数门，**无行缓冲、无 BRAM**；窗口因果（当前 + 前 2 像素），数据流不延迟，`tvalid/tlast/tuser` 仍对齐。
- 按卡面确认式，**未**对 `B'[4]` 另加多数滤波（卡面该项为可选项）。
- **未动**：`tlast`/`tuser`/`tkeep`/`tvalid`/`tready`/所有时钟与时序；`DEBUG_OV5640` 仍为 `false`（厂商 ILA 不实例化）。
- **未叠加** dual/blue/gray 旧补丁：最终 RTL 中 `s_axis_tdata_dualmsb`、`s_axis_tdata_bluefix`、`gray_g2_maj` 计数均为 0（启动器断言 + 网表查询双重确认）。

### 1.1 必须如实记录的两点偏差（非阻断，但与卡面措辞不一致）

1. **三通道 8 位显示值差不是「≤1 LSB」，而是 ∈ {0,4} LSB（最大 4/255 ≈ 1.6%）**。
   下游 `axis_subset_converter_0` 的厂商 remap 为 `{tdata[4:0],3'b000, tdata[10:5],2'b00, tdata[15:11],3'b000}`（vendor `pl_config.tcl`，本轮 `vivado.log` 内回显），即 B8=Y&0xF8、G8=Y&0xFC、R8=Y&0xF8 ⇒ R/B 丢 `Y[2]`、G 丢 `Y[1:0]`，故差值为 0 或 4。对 65,536 个 16 位字穷举验证过该结论。
2. 亮度用整数权重 `77/150/29 >> 8`（权重和 256），与浮点精确式的差 ≤1 个 8 位码值；`Y` 最大 250（穷举），无溢出。

## 2. 构建与命令

```bash
# 一条命令（启动器内含 SOF + 本补丁 + J11/CMOS2 约束），RunId 已存在则拒绝
bash scripts/stage3_t04/run_t04_camera_j11cmos2_stdluma_build.sh t04_stdluma_20261022_r01
```

- 实际构建命令（真实回显于 `launcher_console.log`）：
  `D:/Xilinx/2026.1/Vivado/bin/vivado -mode batch -source scripts/stage3_t04/build_t04_camera.tcl -log <run>/vivado.log -journal <run>/vivado.jou -tclargs <run> <run>/vendor_src`
- 补丁顺序：`alinx_ov5640_sof_hrefgap.patch` → `alinx_ov5640_stdluma_gray.patch`；XDC 覆盖为 `board/stage3/hardware/an5642_j11_cmos2.xdc`。
- 工具/许可：Vivado 2026.1 BASIC（`D:/Xilinx_licenses/basic_only.lic`，仅注入本进程）；part `xc7z020clg400-2`；`S3_BUILD_JOBS=3`（默认）。
- 耗时 532 秒（约 8.9 分钟）；峰值内存 **2564.582 MB**（Vivado 报告值）。
- **真实退出码：`VIVADO_EXIT=0`、launcher `LAUNCHER_EXIT=0`**（见 `launcher_exit_code.txt`）；`synth_design Complete!`、`write_bitstream Complete!`。

## 3. 关键结果

| 项 | 值 | 来源 |
|---|---|---|
| 时序 WNS / TNS | **1.084451 ns / 0.000000 ns** | `report_timing_summary_impl.rpt`、`T04: TIMING_*` |
| 时序 WHS / THS | **0.043965 ns / 0.000000 ns** | 同上 |
| 时序结论 | `All user specified timing constraints are met.` | `report_timing_summary_impl.rpt` |
| DRC（impl 报告） | **0 Error、0 Critical Warning、8 Warning** | `report_drc_impl.rpt` |
| DRC 规则分布 | PDCN-1569×3、PLCK-12×1、REQP-1839×2、REQP-1840×1、RTSTAT-10×1 | 同上 |
| 全日志 CRITICAL WARNING | 17 条（`Designutils 20-1280`、`Timing 38-249`） | `vivado.log`（48-249 = rgb2dvi `SerialClk`/`PIX_CLK` 未声明 ×5 关系，既有缺口） |
| 全日志 ERROR | **0** | `vivado.log`；OOC 综合 `runme.log` 亦 0 |
| 峰值内存 | **2564.582 MB** | `vivado.log` |
| Slice Registers（impl） | 9,341 | `report_utilization_impl.rpt` |
| bitstream SHA-256 | `44e609ccc62647c1748cbeecc64b2fdaa0c53b07db6b7bd1c8a230ca65fc4afb` | 独立 `sha256sum` 复核一致 |
| XSA SHA-256 | `90e1bdee1f5baaf9e772edcddc800aab6927d2099b54a45bc020025d82ccb1c4` | 独立 `sha256sum` 复核一致 |

产物路径（未入 Git，缓存）：`tmp/s3r06/t04_stdluma_20261022_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit`、`tmp/s3r06/t04_stdluma_20261022_r01/design_1_wrapper.xsa`。

## 4. 补丁与 RTL 哈希（绑定实际构建输入）

| 对象 | SHA-256 |
|---|---|
| 补丁 `alinx_ov5640_stdluma_gray.patch` | `1e667e7f2594f507d48f5d1e0bd70ccfe11dd42e35bf1a9c4e0a788be5c34460` |
| 补丁 `alinx_ov5640_sof_hrefgap.patch` | `fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5` |
| XDC `an5642_j11_cmos2.xdc` | `2dae928c9458a71ebc9ae741e71f7a274c18afc237676852c53d5e61bbeff5b2` |
| RTL 厂商原件 | `98260b62f996ec700eb766c6c4e57706b2c1ff3a8224a5105a3641b6475b3e4d` |
| RTL（仅 SOF） | `db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6` |
| RTL（SOF + 标准亮度灰度）**最终** | `2a98dcb2eed1fbe698fbb4cfbf986e838a7c1d6635eb019442444bed3e71176d` |

- `git apply --check/apply` 四个退出码全 0（`patch_git_apply.log`）。
- **工程侧 RTL 副本哈希一致**（这是真正被综合的那份）：`project/ov5640_single.gen/sources_1/bd/design_1/ipshared/564b/src/alinx_ov5640.v` = `2a98dcb2…`，含 `GAP_THRESH` 与 `s_axis_tdata_stdluma`，不含旧补丁标记。
- 补丁由 `patch_scratch/make_stdluma_patch.sh` **确定性生成**（重跑得到同一补丁 SHA）；在独立 verify 副本上按 SOF→STDLUMA 应用后与生成基准**逐字节相同**（`patch_scratch/patch_dryrun.log`）。
- 构建前另用 `xvlog` 对该 RTL 做解析检查：`VRFC 10-311 analyzing module alinx_ov5640`，退出码 0，无告警。

## 5. 简要网表佐证（**有界**，刻意不做逐位回溯）

方法：对 IP 的 OOC 检查点做**一次**过滤查询（`check_stdluma_ooc_nets.tcl`），不做逐位 fanout 回溯——上一张卡（task-11）正是在深度网表回溯阶段卡死的。
查询经 `timeout 1500` 包裹，退出码 0、未超时（`stdluma_ooc_nets.txt` / `.log`）：

| 计数 | 值 |
|---|---|
| 含 `stdluma` 的**单元** | **96**（含 `inst/stdluma_g2_d1_reg`、`inst/stdluma_g2_d2_reg`、`inst/stdluma_g8`、`inst/stdluma_luma32`、`inst/stdluma_luma32*_carry*` 等乘法/加法进位链） |
| 含 `stdluma` 的**网络** | **212**（如 `inst/stdluma_g2_cand`、`inst/stdluma_luma320[5..11]`） |
| 旧补丁残留 `dualmsb` / `bluefix` / `gray_g2`（net 与 cell 计数） | **0 / 0 / 0** |
| FIFO 写数据端口 `*xpm_fifo_async_inst/din*` | **18**（18 位 din 通路完整） |

⇒ 新逻辑确实进入了 OOC 网表（2 个多数延迟寄存器与 Y 算术进位链可查），且没有旧补丁残留。**这不是逐位等价性证明**：未做 RTL 仿真、未做逐位 fanout 回溯。

## 6. 本目录文件

| 文件 | 内容 |
|---|---|
| `build_report.json` | 机器可读清单：基线/工具/命令/退出码/哈希/时序/DRC/内存/网表查询/限制 |
| `alinx_ov5640_stdluma_gray.patch` | 本卡新补丁原文 |
| `alinx_ov5640_sof_hrefgap.patch` | 前置 SOF 补丁原文 |
| `alinx_ov5640_dual_msb_rebuild_not_applied.patch`、`alinx_ov5640_blue_msb_rebuild_not_applied.patch` | **未应用**的旧补丁（留档对照） |
| `alinx_ov5640_stdluma_patched.v` | 构建实际使用的补丁后 RTL（哈希 `2a98dcb2…`） |
| `patch_git_apply.log`、`patch_scratch/` | 补丁应用日志、确定性生成脚本、干跑校验日志与哈希 |
| `check_stdluma_ooc_nets.tcl`、`stdluma_ooc_nets.txt`/`.log`/`.jou` | 有界网表查询脚本、输出、日志 |
| `report_timing_summary_impl.rpt`、`report_drc_impl.rpt`、`report_clock_interaction_impl.rpt`、`report_clocks_impl.rpt`、`report_utilization_impl.rpt`、`report_utilization_synth.rpt` | 本轮报告 |
| `vivado.log`、`vivado.jou`、`alinx_ov5640_ooc_synth_runme.log`、`launcher_console.log`、`launcher_exit_code.txt` | 原始日志、OOC 综合日志、启动器控制台与退出码 |
| `make_build_report.py` | 清单生成器（从启动器抽出，供复现/补生成） |

### 6.1 过程如实记录（本轮的一个小事故）

启动器本体**成功**（位流+XSA+时序+DRC+网表查询全部产出，退出码 0），但其内联证据生成器漏导出 `ILA_BRANCH`/`ILA_VENDOR`/`ILA_COMMIT`，抛 `KeyError` 导致 `build_report.json` 未写出。
处理：启动器已补上这三个导出（供后续新 RunId 使用）；本轮**未重建、未重跑 RunId**，而是用同一份生成器代码（抽取为 `make_build_report.py`）由 `patch_scratch/finalize_report.sh` 从本轮日志/产物**补生成**清单，并在脚本内交叉核对补丁与 XDC 哈希与磁盘现值一致（`CROSS_CHECK_SHAS_MATCH_DISK=1`）。

## 7. 未做 / 未验证（明确记录，不重试）

- **未上板、未下载、未烧 QSPI**（本卡边界）；因此**没有画面/目视结论**，也没有"三通道是否真等值"的实测。
- **未做 RTL 功能仿真**；灰度算式只做了离线穷举算术验证（65,536 字，脚本口径见 §1.1）。
- **未做逐位网表回溯与等价性证明**（刻意避免上一卡的卡死点）。
- 未做 ≥30 min 耐久；未做色卡/仪器测量。
- 既有未关闭项（与本卡无关，仍成立）：VDMA 粘滞 `0x00015810`、方法学 TIMING-17/36 与 I/O delay 缺口、`Timing 38-249` CRITICAL WARNING、J10 半屏未定性、无 ILA（BASIC 许可不支持 `create_debug_core`）。
- 颜色验收在硬件修复前**保持 FAIL/受阻**；`build_report.json` 的 `status=ok` 仅表示"位流+XSA 产出且网表查询通过"，**不代表**接口语义、板上功能、颜色或 G3/G4/G5 通过。

## 8. 复现入口

```bash
# 只读复核
python -B -c "import json;d=json.load(open(r'D:/codex-worktrees/dbdf/report/evidence/S3-T05/t05_stdluma_20261022_r01/build_report.json',encoding='utf-8'));print(d['status'],d['implementation']['timing'],d['artifacts']['bit']['sha256'])"
sha256sum D:/codex-worktrees/dbdf/tmp/s3r06/t04_stdluma_20261022_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit
# 重新生成补丁（确定性，应得到同一 SHA）
bash report/evidence/S3-T05/t05_stdluma_20261022_r01/patch_scratch/make_stdluma_patch.sh
```