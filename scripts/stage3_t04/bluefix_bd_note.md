# S3-T05-PL1 蓝最高位（RGB565 B[4]）重建：改动位置与补丁关系说明

本文件配合 task-6（蓝位重建变体）与证据目录
`report/evidence/S3-T05/t05_bluefix_20261020_r01/` 使用，供独立复核改动边界与顺序安全。

## 1. 问题与依据

阶段总控 4 组独立实测（白纸 / 实景 AWB 开 / 实景 AWB 关 / 彩条）统计一致：**蓝通道最大值恒为 120、
从无 >127 的蓝像素**，而 R 可达 248、G 可达 236 ⇒ RGB565 的 **B[4]（蓝最高位）恒为 0**，
蓝色动态范围只有一半，画面整体偏黄。AWB / ISP / 显示器均已独立排除。

厂商 IP 取 `cmos_d[9:2]` 当字节 → 16 位字 = {byte0, byte1}，RGB565 布局：

| 字段 | 位 |
| --- | --- |
| R[4:0] | `tdata[15:11]` |
| G[5:0] | `tdata[10:5]` |
| B[4:0] | `tdata[4:0]` |

第二字节 = {G[2:0], B[4:0]}，缺失位对应 DVP 的 D[6] 线（断线还是映射错仍在核，
但**重建位与该根因无关**，两种根因下都适用）。

## 2. 改动位置（只改 `my_ip/ov5640_ip/src/alinx_ov5640.v`，3 处）

| # | 原内容 | 新内容 | 是否在综合路径 |
| --- | --- | --- | --- |
| 1 | `wire[15:0] s_axis_tdata = cmos_d_16bit_d1;`（其后无重建 wire） | 其后新增 2 行注释 + `wire[15:0] s_axis_tdata_bluefix = {s_axis_tdata[15:5], s_axis_tdata[3:0], s_axis_tdata[3]};` | 是（组合逻辑） |
| 2 | `.probe0(s_axis_tdata),`（ILA 实例内） | `.probe0(s_axis_tdata_bluefix),` | **否**（`DEBUG_OV5640=false`，该 generate 分支不综合；改动只为两条路径语义一致） |
| 3 | `.din              ({s_axis_tdata,s_axis_tlast,s_axis_tuser}),` | `.din              ({s_axis_tdata_bluefix,s_axis_tlast,s_axis_tuser}),` | **是**（真正生效：重建字写入异步 FIFO，再出现在 `m_axis_video_tdata`） |

未改动：`tlast`、`tuser`、`tkeep`、时钟/时序、`DEBUG_OV5640`（保持 `false`，未打开厂商内嵌 6 探针 `ila_0`）。

## 3. 与 SOF 补丁的关系：区域不重叠，顺序可交换（已实测）

- SOF 补丁（`alinx_ov5640_sof_hrefgap.patch`）改动：参数表（加 `GAP_THRESH`）、
  `reg s_axis_tuser;` 之后的声明区、`s_axis_tuser` 的 always 块（原 136–144 行）。
- 蓝位补丁改动：`s_axis_tdata` 声明之后（原 42 行后）、ILA `probe0`（原 150 行）、FIFO `din`（原 189 行）。
- 三处蓝位锚点在**厂商原件**与**已打 SOF 补丁的 RTL**中都各出现且仅出现 1 次 ⇒ 上下文互不重叠。

实测（真实 `git apply`，原文见 `patch_apply_order_test.txt`）：

| 场景 | 结果 |
| --- | --- |
| A) 厂商原件 + BLUE（`--check` / `apply`） | RC=0 / RC=0，结果 = `e1cc558e…` |
| B) 厂商原件 → SOF → BLUE | 四个操作全 RC=0，结果 = `91b67c1e…` |
| C) 厂商原件 → BLUE → SOF | 四个操作全 RC=0，结果 = `91b67c1e…`（与 B 逐字节相同） |

⇒ **两个补丁无冲突、可交换**。本变体按卡面要求采用 **SOF → BLUE** 顺序；
蓝位补丁同时满足「对厂商原件单独 `git apply --check` 通过」。

注：`git apply` 须从工作树根执行并带 `--directory=<相对路径>`；补丁内容行保留 CRLF，
GNU `patch` 对该文件报 `different line endings` 而失败，故不使用。

## 4. 重建公式与已知误差

```
B'[4:0] = {B[3:0], B[3]}          // 即把 B[3] 复制到最高位
new_word = {tdata[15:5], tdata[3:0], tdata[3]}
```

该式**只把 bit[4] 由常量 0 换成原 bit[3]**，其余 15 位逐位不变 ⇒ 只恢复一半量化台阶。

误差性质：等价于把蓝通道低 4 位区间做 2 倍拉伸（以 5 位蓝计，b(0..15) → b + (b≥8 ? 16 : 0)）。

- **蓝淡色区（B 小）相对误差最大**（相邻真实值会被映射到同一台阶或跳变）；
- 深蓝区相对准确；
- AWB 会在此基础上再自适应调整，可能掩盖也可能加重该误差。

⇒ 这是**近似修复**（画面不再整体偏黄），不是恢复真实丢位；根因（D[6] 断线/映射）未在本变体修复。

## 5. 复现

```bash
# 生成蓝位补丁（可复现，含锚点断言与 hunk 往返自检）
python -B report/evidence/S3-T05/t05_bluefix_20261020_r01/make_blue_msb_rebuild_patch.py \
  <厂商原件>/my_ip/ov5640_ip/src/alinx_ov5640.v \
  <out>/alinx_ov5640_blue_msb_rebuild.patch <scratch> \
  report/evidence/S3-T05/t05_sof_fix_20261020_r01/patch_verification/expected_patched_alinx_ov5640.v
# 期望：PATCH_HUNKS=3 LINES_ADDED=5 LINES_REMOVED=2
#       PATCH SHA256=6609a59da624beb562a5a717e4839567f803bd80e7df0a5ca9ce4e4ff5ec7505
#       INPROCESS_ROUNDTRIP=OK / BIT_CHECK=OK

# 构建
bash scripts/stage3_t04/run_t04_camera_j11cmos2_bluefix_build.sh t04_bluefix_20261020_r01
```