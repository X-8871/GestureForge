# S3-T05-PL1 蓝最高位（RGB565 B[4]）重建变体：证据入口

- 任务：task-6（阶段总控 14:0x 指派；Wong 选方案 (a)：PL 侧重建蓝最高位，近似修复）
- RunId：`tmp/s3r06/t04_bluefix_20261020_r01`（新建，未复用）
- 基线提交（构建时 HEAD）：`1b437e399ade0a0498187d4e4d03dc3a01451872`（分支 `codex/stage3-video`）
- **真实退出码：0**（`impl_1 = write_bitstream Complete!`，PROGRESS 100%、`ALL_DONE=1`，耗时 555 s）
- 只做构建：未下载、未烧 QSPI、未上板。

## 1. 丢位判断依据（为什么重建 B[4]）

阶段总控 4 组独立实测（白纸 / 实景 AWB 开 / 实景 AWB 关 / 彩条）统计一致：
**蓝通道最大值恒为 120、从无任何 >127 的蓝像素**，而 R 可达 248、G 可达 236。
⇒ RGB565 的 **B[4]（蓝最高位）恒为 0**，蓝通道动态范围只有一半，画面整体偏黄。
AWB / ISP / 显示器三条路径均已独立排除。

位域依据（厂商 IP 取 `cmos_d[9:2]` 当字节，16 位字由两个字节拼成）：

| 字段 | 位 |
| --- | --- |
| R[4:0] | `tdata[15:11]` |
| G[5:0] | `tdata[10:5]` |
| B[4:0] | `tdata[4:0]` |

第二字节 = {G[2:0], B[4:0]}，缺失位对应 DVP 的 **D[6]** 线；根因（模块侧断线还是映射错）仍在核，
但**重建位与该根因无关**，两种根因下都适用。

## 2. 重建公式

```
B'[4:0] = {B[3:0], B[3]}            // 把 B[3] 复制到最高位
new_word = {tdata[15:5], tdata[3:0], tdata[3]}
```

改动只把 16 位字的 **bit[4] 由常量 0 换成原 bit[3]**，其余 15 位逐位不变；
新老字都取自同一个寄存器，**零新增逻辑**（纯位重排）。
未改动 `tlast`/`tuser`/`tkeep`/时序/时钟，未打开 `DEBUG_OV5640`。

改动位置（`my_ip/ov5640_ip/src/alinx_ov5640.v`，3 处）与补丁顺序分析见
`scripts/stage3_t04/bluefix_bd_note.md`。

## 3. 已知误差（近似修复，不是恢复真实位）

该式等价于把蓝通道低 4 位区间做 2 倍拉伸（以 5 位蓝计，`b(0..15) → b + (b>=8 ? 16 : 0)`）：

- **蓝淡色区（B 小）相对误差最大**，相邻真实值可能被映射到同一台阶或跳变；
- 深蓝区相对准确；
- **AWB 会在此基础上再自适应调整**，可能掩盖也可能加重该误差。

因此本变体只保证"画面不再整体偏黄"，不代表蓝通道被正确还原。

## 4. 补丁与顺序

| 补丁 | SHA-256 | hunks | +/− |
| --- | --- | --- | --- |
| 1/2 `alinx_ov5640_sof_hrefgap.patch`（已有） | `fd854a62…b2c5` | 3 | +24 / −5 |
| 2/2 `alinx_ov5640_blue_msb_rebuild.patch`（本任务） | `6609a59d…7505` | 3 | +5 / −2 |

RTL 哈希：厂商原件 `98260b62…` → 仅 SOF `db4857fe…` → SOF+蓝位 `91b67c1e…`（本构建实际使用）。

**顺序无冲突、可交换**（真实 `git apply` 实测，见 `patch_apply_order_test.txt`）：
A) BLUE 单独对厂商原件 `--check`/`apply` 均 RC=0；
B) SOF→BLUE 四个操作全 RC=0；
C) BLUE→SOF 全 RC=0 且与 B 结果**逐字节相同**。
本构建按卡面要求采用 **SOF → BLUE**。

## 5. 构建结果

| 指标 | 本变体（SOF+蓝位） | SOF 变体 | 基线 04 run |
| --- | --- | --- | --- |
| WNS (ns) | **1.102659** | 1.054525 | 1.141183 |
| TNS (ns) | 0.000000 | 0.000000 | 0.000000 |
| WHS (ns) | **0.040436** | 0.058931 | 0.058332 |
| THS (ns) | 0.000000 | 0.000000 | 0.000000 |
| DRC Error | 0 | 0 | 0 |
| 峰值内存 (MB) | 2566.836 | 2568.176 | 2555.516 |
| IP OOC 寄存器 | 412 | 415 | 401 |

DRC 8 条 Warning 明细与基线一致：PDCN-1569×3、PLCK-12×1、REQP-1839×2、REQP-1840×1、RTSTAT-10×1。

补丁进入设计的旁证：工程 `.gen/.../ipshared/564b/src/alinx_ov5640.v` 哈希 = `91b67c1e…`，
且同时含 `GAP_THRESH` 与 `s_axis_tdata_bluefix`。

诚实记录：首次 `launch_runs synth_1` 的 OOC 子 run 有启动期抖动
（`Could not open 'C' for writing`，2 个子 run 报错），由脚本内置重试在第 1 次恢复，非设计错误。

## 6. 产物（SHA-256）

| 产物 | 路径 | SHA-256 |
| --- | --- | --- |
| bitstream | `tmp/s3r06/t04_bluefix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit` | `0819d0da1508cdc43f72d8ab67e8d4173de3ddc656e3fbfa957a72c061c119d7` |
| XSA | `tmp/s3r06/t04_bluefix_20261020_r01/design_1_wrapper.xsa` | `fed8f652be0a2d567215a7b0e5905355dfe2bbac8c380f0a94df1daf038bbabc` |

## 7. 本目录文件

- `build_report.json`：机器可读产物清单（命令、退出码、两补丁身份与顺序结论、RTL 三方哈希、时序、DRC、内存、资源、产物哈希、限制）
- `alinx_ov5640_blue_msb_rebuild.patch` / `alinx_ov5640_sof_hrefgap.patch`：两个补丁原文
- `patch_git_apply_result.txt`：四个 `git apply` 操作的真实命令/返回码/哈希（`.log` 被 gitignore，故另存 .txt）
- `patch_apply_order_test.txt`：A/B/C 三种顺序的真实实测输出
- `make_blue_msb_rebuild_patch.py`：蓝位补丁生成器（可复现，含锚点断言 + hunk 往返自检 + 位级自检）
- `patch_verification/`：`pristine` / `blue_only` / `combined_sof_then_blue` 三方 RTL，供 byte-level 复核
- `report_*.rpt`、`vivado.log/.jou`（`.log`/`.jou` 被 gitignore）

## 8. 限制与未执行

- 只构建，未下载、未烧 QSPI、未上板；蓝通道直方图与颜色判读由阶段总控执行。
- 蓝位重建是**近似**修复：蓝淡色区误差最大，AWB 会再自适应调整（见 §3）。
- 未做 RTL 功能仿真（无既有 testbench）；正确性靠 + 上板实测验证。
- SOF 既有约束仍适用：复位后第一帧可能无 SOF；`GAP_THRESH=16384` 只对 1280x720(HTS=1892/VTS=740) 成立。
- 根因（DVP D[6] 断线或映射错）未定位、未修复，本变体只是绕过。
- 未提交 Git（由阶段总控统一提交）。