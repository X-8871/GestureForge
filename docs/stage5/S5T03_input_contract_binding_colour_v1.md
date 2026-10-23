# S5-T03 输入契约改绑：真实彩色（v1，2026-10-24）

> 状态：`BINDING_PROPOSED_PENDING_STAGE4_G0`。本文是**外围绑定与范围标签**，**不改** `S5A-G0-v2` 的任何阈值/几何/语义，也不把既有合成源结论升级为真实集成结论。
> 机器可读权威：`docs/stage5/s5t03_input_contract_binding_v1.json`；冻结参数：`docs/stage5/s5t03_offline_skeleton_params_v1.json`。
> 依据：`CDX-20261022-015`（r03）§2.2、`CDX-20261022-014`（r02）§4/§5、`decisions/stage_3_4_direction_20261024_r01.md`。

## 1. 要解决的问题

015 r03 §2.2 要求各阶段单一写入方把自己的输入/结果契约显式标 `camera_live_colour` 或 `camera_capture_replay_colour`，并分别绑定：阶段3 部署（bit/XSA/ELF）、实际格式/字节序、宽高/stride、原图坐标口径、采集时钟与源帧哈希；同时明确「回放结论必须标回放」。原 `S5A-G0-v2`（2026-10-21）写的是「阶段3 颜色受阻 ⇒ 真实采集路径不可用」，该前提已由阶段3 新模块实测撤销，故必须补一份绑定把标签与上游身份写清，但**不得顺手改显示契约的指标**。

## 2. 输入范围标签（互斥，三选一）

| 标签 | 含义 | 阶段4 `source_kind` | `capture_time_ns` | 状态 |
|---|---|---|---|---|
| `camera_live_colour` | 实时真实彩色采集（新模块 + 无补偿基线） | `camera` | 非零真值，不得标 unavailable | `ALIGNED_WITH_STAGE4_DRAFT` |
| `camera_capture_replay_colour` | 抓取到的**真实彩色帧**在回放/注入路径重放 | `file_injection`（经板级注入）或 `synthetic`（纯离线重放） | 按 015/阶段4 口径：非 camera 时 `0` 哨兵 + `unavailable_fields`；另**单独携带** `source_capture_time_ns` | **`PROPOSED_PENDING_STAGE4_G0_CONFIRMATION`** |
| `synthetic_dynamic_reference` | 与阶段4 同 schema 的合成动态流（既有 120 帧/31.06 min 均属此列） | `synthetic` | `0` 哨兵 + unavailable | `ALIGNED_WITH_STAGE4_DRAFT` |

- **不新造枚举值**：阶段4 S4-B r03 现有 `file_injection/camera/synthetic`；本树不自行加第四个枚举，也不改 w4 文件。`camera_capture_replay_colour` 的映射作为**请求**提交给阶段4 G0（`UR-1`）。
- **回放标签必须携带**：`source_frame_sha256`、`source_capture_time_ns`、`source_frame_id`、`source_bit_sha256`、`source_elf_sha256`、`replay_not_live=true`；并且**不得**报告采集 FPS 为实测、不得把注入起点当采集起点。
- **互斥**：一个证据包只能属于一种标签；五元组与产物清单必须携带该标签。

## 3. 阶段3 部署身份（本轮独立只读重算，2026-10-24 00:55）

| 产物 | 路径（dbdf，只读） | SHA-256（本树重算） | 与 015 r03 前缀 |
|---|---|---|---|
| 无补偿 SOF/bit | `dbdf\tmp\s3r06\t04_sof_fix_20261020_r01\project\ov5640_single.runs\impl_1\design_1_wrapper.bit` | `7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710` | ✅ 一致 |
| XSA | `dbdf\tmp\s3r06\t04_sof_fix_20261020_r01\design_1_wrapper.xsa` | `1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3` | ✅ 一致 |
| 实时彩色应用 ELF | `dbdf\tmp\s3r06\t04_j11cmos2_elf_v10\elf_build\app\an5642_j11cmos2_v10_read.elf` | `1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073` | ✅ 一致 |

- 次要（只读登记、本轮不部署）：`v11_freeze` ELF `c01133b1bb0204f07a5be215dbeb58ca0dcc627115cd3a06f1c56f9b21ca26c4`。
- 历史回退专用（**不得**当当前部署身份）：灰度 `44e609cc…`、纯绿 `2f72aaa4…`、补偿彩色 `30db09ba…`。
- **已登记的口径不一致**：dbdf `S3-T05/t05_new_module_reverify_20261023_r01/README.md` 标题行写 `v9_read`、同文「处置」段写 `v10_read`；015 r03 与 dbdf `window_open_prestate.json`（2026-10-24 00:35）均为 v10。本树按**独立重算**绑定 v10 并请求阶段3 更正（`UR-2`）。
- **范围外**：J10 半屏黑（Wong 2026-10-24 移出范围，当前 J11/CMOS2；不得写成已修复）；`v12`/`0x503D` 仅既定彩条用例，本轮不动硬件。
- 命令与真实退出码：`report/evidence/S5-T03/s5t03_takeover_20261024_r01/console/deploy_hash_verify.txt`。

## 4. 采集几何与字节序

| 项 | 值 | 依据 |
|---|---|---|
| 源分辨率 | 1280×720 | 阶段3 部署 |
| 每像素字节 | 3 | 行文件 3840 B / 1280 px |
| `row_stride_bytes` | 3840 | `row_y100/400/600.bin` 各 3840 B |
| 帧字节 | 2764800 | `bars_frame_full.bin` 实测大小 |
| DDR 转储通道序 | `B,G,R` | 015 §2.1/§2.2（本树未独立改判，仅登记） |
| 传感器格式 | RGB565 | 同上 |

**不得混同**：传感器 RGB565 展开、DDR 转储 B/G/R 三字节序、模型 RGB888 语义是三种东西；转换/量化/补边必须与冻结 D2 对齐；`stride` 之外的行尾填充未定义、不得被消费。

## 5. 原图坐标口径（沿用，未改）

- `detections[].xyxy` = **归一化原图坐标**（含补边逆映射、裁剪到 [0,1]、正面积），原图 = 1280×720 采集帧。
- 显示层**只允许**使用该字段，不得自行反算第二份坐标；缺失时才启用冻结逆式（启用待阶段4 G0）。
- 映射链（全部来自冻结参考实现 `verification/s5_display_geometry_reference.py`，哈希 `4d9fe369…` 与 S5-A 清单一致）：
  `clip_unit_box` → `original_norm_to_display_px`（`round_half_up(v*(span-1))`，只在最后取整一次）→ `border_pixel_sets`（2 px 偶数线宽居中、逐边钳到画布内）→ 标签锚点（框外左上→框内左上→安全区）、分数文本 ≤1e-3。
- 门槛全部沿用：逆映射 ≤1.0 px、绘制保真 ≤1 px、线宽 ±0.5 px、离散字段完全一致。

## 6. 帧关联键（对齐阶段4 草案，不自造）

| 键 | 字段 | 用途 |
|---|---|---|
| 共享契约结果键 | `(session_id, frame_id, result_seq)` | 唯一标识一条结果 |
| S4-A join key | `(session_id, frame_id, repeat_index)` | 结果与同一请求重复项连接 |
| PS 日志主键 | `(session_id, result_seq)` | 旁路结果日志 |
| UART 可观测键 | `(frame_id, repeat_index, sequence)` | 请求/响应配对（`sequence` 非唯一键） |
| **显示侧成对** | `displayed_frame_id` / `result_frame_id` | 语义 B 下不要求相等，禁止改写 `frame_id` 掩盖错配 |

- 五元组：`(displayed_frame_id, result_frame_id, age_result_ns, age_frame_ns, display_semantics)`。
- 时间：同一 PS 单调时钟；`capture_time_ns` 在 `camera` 下必须非零，在非 camera 下为 `0` 哨兵 + `unavailable_fields`。
- 唯一性：重复结果**只计数**、不当作新结果叠加；无法唯一关联或顺序矛盾的结果不得用于跨阶段证据。

## 7. 既有合成源结论的处置（**不重做、不升级**）

| 既有结论 | 证据 | 范围标签 |
|---|---|---|
| 四 FPS（display 59.206 / video_refresh 59.175；`inference_fps=NA`） | `report/evidence/S5-T01/s5t01_board_fps4_20261022_r02/` | `synthetic_dynamic_reference`（显示侧） |
| 120 帧五元组 + 故障计数 + HUD 13 字段 | `report/evidence/S5-T01/s5t01_board_5t_20261022_r02/` | 同上 |
| 30 分钟长跑（r03：31.06 min、124 完整轮） | `report/evidence/S5-T01/s5t01_board_soak_20261022_r03/` | 同上（**仅显示/叠加路径**） |

- 这些 RunId 与产物**本轮不重跑、不改写**；已用 `git diff --name-only 654c72e -- report/evidence/S5-A|S5-B|S5-C|S5-T01`（空）核验，真实退出码在骨架证据包。
- 它们**不是**真实采集/真实推理集成结论；本轮离线骨架 PASS 同样只是骨架结论。

## 8. 未决与请求

| 编号 | 对象 | 请求 | 影响 |
|---|---|---|---|
| `UR-1` | 阶段4 写入方（DSH/w4） | 在 S4-B G0 确认 `camera_capture_replay_colour` 的 `source_kind` 与 `carry_fields` | 真实彩色回放/实时集成的分类与结论范围 |
| `UR-2` | 阶段3 写入方（DSH/dbdf） | 核对并更正 README 的 ELF 名称口径 | 部署身份单一书面口径 |
| `UR-3` | Wong / 阶段5 正式 G0 | 成品延迟上限、颜色表与字号、阶段4 `stale_age_limit` 正式冻结 | 阶段5 正式验收（不影响本轮骨架） |
| `UR-4` | DSH 项目总控 | 阶段5 板级窗口申请（阶段4 结果冻结后） | 见 `S5T03_board_verification_pending_v1.md` |