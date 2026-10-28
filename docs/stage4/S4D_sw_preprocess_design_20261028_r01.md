# 4-D SW 预处理设计与逐字节对拍（S4-T34，2026-10-28 r01）

> ## 裁决（2026-10-28，lead 签发，D2 权威）
> **预处理语义以冻结 D2 数值口径为唯一权威**；`vitis/stage4/ps/s4d_geometry.h` 中
> 「最近邻缩放 / `int8(v-128)` / pad=0」的**旧口径作废**（该文件已加 `LEGACY_4B_SUPERSEDED_BY_D2` 标注，
> 历史内容保留作追溯；几何**参数表**仍被 D2 口径复用）。
> **可核事实**：只有 D2 口径能产出与冻结张量 `da26d385…` 逐字节一致的结果（`diff=0`）；
> 按旧口径（最近邻 + `v-128`）**无法复现**该张量 ⇒ 与网络输入语义不符。
> 本文件下述各节即为 D2 口径的完整实现与对拍证据。
>
> 附带裁决：**冻结/交付物以登记 SHA 为准**；`-g3` 调试信息与新增分支导致的"重建 SHA 不同"
> **不作为失败**，但源码快照必须可追溯（见 `app_elf_registration_r5.json.version_mapping_and_rebuild_drift`）。

- 任务：chain-lite-B 的前置 —— 在 PS 侧实现 `RAW 640×480 BGR888 → letterbox → 416×416 INT8 CHW`，
  并与冻结张量 `bridge_input_postquant_int8_chw.bin`（SHA-256 `da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e`）**逐字节对拍**。
- 边界：本轮**离线**（未开窗）；`ENABLE=0`；不主张 G3/G4/G5；M3/M2 未闭合。

## 1. 冻结口径（唯一来源：D2 数值参考）

出处：`report/evidence/S4-B/s4b_pl_preproc_numeric_20261023_r04/source_snapshot/s1_t02_d2_numeric_reference.py`
（本会话所用副本，行号为该文件；该文件为 4-B 阶段冻结的 D2 数值参考快照）

| 环节 | 规则 | 出处行 |
|---|---|---|
| 几何 | Darknet `letterbox_image`：`若 dst_w/src_w < dst_h/src_h` ⇒ `new_w=dst_w, new_h=src_h*dst_w//src_w`，否则 `new_h=dst_h, new_w=src_w*dst_h//src_h`；`offset=(dst-new)//2` | 116–138 |
| 缩放 | Darknet `resize_image` **端点对齐双线性**：`w_scale=(src_w-1)/(new_w-1)`，最后一列/行与 `new==1` 直接取源最后一列/行；**中间结果保持 double，不取整** | 140–181 |
| 归一化 | `v/255`，clamp `[0,1]` | 201–219 |
| pad | `normalized 0.5` ⇒ `int8 64`（`quantize_symmetric(0.5, 1/127)`） | 136–137、349–352 |
| 量化 | 对称、零点为零、`scale = INPUT_SCALE = 1/127`；`q = sat(round_away(v/scale))`，`round_away` = 半数远离零，饱和 `[-127,127]` | 21、32–37、44–52、249–254 |
| 布局 | CHW（plane0=R、plane1=G、plane2=B） | 228–247 |

**640×480 → 416×416 的取值**：`416/640 = 0.65 < 416/480 = 0.8667` ⇒ `new_w=416, new_h=480*416//640=312`，
`offset_x=0, offset_y=(416-312)//2=52` ⇒ 与 `vitis/stage4/ps/s4d_geometry.h` 参数表 **几何完全一致**。

**1440×1920 → 416×416**（T25 源图）：`new_h=416, new_w=1440*416//1920=312`，`offset_x=52, offset_y=0`
⇒ 与 `host_result_test_fist_000.json` 的 `geometry_letterbox`（312×416、pad_left 52、pad_top 0）**一致**。

## 2. 与 `s4d_geometry.h` 的已知规范冲突（需 lead/Wong 裁决后统一文档）

| 项 | `s4d_geometry.h`（4-B 头文件） | 冻结 D2 口径（本实现采用） |
|---|---|---|
| 缩放 | **最近邻**（`src_x=(x*20)/13`、`src_y=((y-52)*20)/13` 整数除法） | **端点对齐双线性** |
| 量化 | `int8(v-128)`（纯偏移，范围 -128..-1..127） | `q = sat(round_away((v/255)/(1/127)))`（对称，范围 0..127） |
| pad | `0`（INT8 零点） | `0.5` 归一化 ⇒ **64** |

**为何按 D2**：冻结张量 `da26d385…` 由 D2 参考产生（见 `layer_divergence_probe.py:249-266`），且链路上网络
（2B 位流）的输入语义以该张量为准；若按 `s4d_geometry.h` 的 NN + `v-128` 生成，**不可能**与该张量逐字节一致
（本轮对拍已实测：D2 路径 diff=0）。故 **SW/PL 预处理文档需以 D2 口径为准并修订 `s4d_geometry.h`**，
此项属规范冲突，**未擅自修改头文件**，等 lead/Wong 裁决。

## 3. 实现（PS 侧 C，无平台依赖）

- `vitis/stage4/ps/s4d_sw_preproc.h` / `s4d_sw_preproc.c`
- API：`s4d_sw_preproc_bgr888_to_chw_int8(const uint8_t *bgr, int src_w, int src_h, int8_t *out)`（PS 入口，RAW 为 BGR888）
  与 `s4d_sw_preproc_rgb888_to_chw_int8(...)`（主机对拍入口）；`s4d_sw_letterbox_geometry(...)` 供核对。
- 内存：单个 `416*416` double 缓冲（≈1.38 MB）复用 3 次；不做按源图尺寸的分配；中间量全 `double`，**仅在最后一步量化**（与冻结参考一致）。
- 输出 519,168 B = 3×416×416（CHW）。

## 4. 逐字节对拍（本会话实测）

- 工具：`tmp/4/S4-T34/pair_sw_preproc.py`，用 `d:\mingw64\bin\gcc.exe -O2 -std=c99` 编译**与 PS 同一份**
  `s4d_sw_preproc.c` + 主机 Harness（`sw_preproc_hosttest.c`），输入 T25 源图解码后的 RGB888/BGR888 raw。
- 源图：`D:\FPGA_Data\HaGRIDv2\dataset\fist\fist\c39c0301-d0ed-4d34-97a0-84c93dd0f515.jpg`
  SHA-256 `6dbd72693bc6ad2af6121ffe95e2ee5e9c14597a4c4d16a6db8cdf07d8e43b0e` ✓（与 T25 绑定一致），1440×1920。
- 结果（`report/evidence/S4-T34/sw_preproc_pairing_20261028_r01/pairing_result.json`）：
  - `rgb_entry`：519,168 B、**SHA-256 = `da26d385…`（与冻结张量完全相同）**、`byte_equal=true`、`diff_count=0`；
  - `bgr_entry`：同样 diff=0，且与 `rgb_entry` 逐字节相同（BGR→RGB 通道映射正确）；
  - 主机编译 `exit=0`、`-Wall -Wextra` 无错误。
- 结论：**BYTE_EXACT_MATCH**。

## 5. chain-lite-B 计划（待 lead 签发窗口，不在本轮执行）

1. 主机把一帧 **640×480 BGR888** RAW 预置到 `0x12000000`（同样落盘并记 SHA-256）；
2. 板上应用走 `CHAINB` 分支：`SW 预处理 → arena 0x10000000 → START → DONE_SAFE → invalidate → 解码 → 框 JSON → ACK`；
   预处理后**打印张量 CRC-32**（`s4d_crc32`，= zlib crc32），与离线同输入算得的 CRC 比对 ⇒ 板上预处理实现自证；
3. 框 JSON 与**离线参考**比较（同一 RAW → 同一预处理 → 同一网络/解码参考），容差 1e-9；
4. 判据与停止规则沿用 chain-lite-A 的写法，**不新增宽松项**。

## 6. 当前产物

| 产物 | 路径/身份 |
|---|---|
| C 实现 | `vitis/stage4/ps/s4d_sw_preproc.{h,c}` |
| 对拍脚本 | `tmp/4/S4-T34/pair_sw_preproc.py`、`sw_preproc_hosttest.c`（tmp，不提交） |
| 对拍证据 | `report/evidence/S4-T34/sw_preproc_pairing_20261028_r01/`（`pairing_result.json`、两侧 raw、两份输出张量） |

## 7. 限制

- 未上板验证 chain-lite-B；本轮只证明**离线 C 实现与冻结张量逐字节一致**。
- 未修改 `s4d_geometry.h`（规范冲突待裁决）；未改 2B 位流、未碰 `ENABLE`、未写 QSPI、未改线、未 push。
- 结论仅覆盖 **2B 平台位流适用性**；不主张 G3/G4/G5；M3/M2 未闭合。