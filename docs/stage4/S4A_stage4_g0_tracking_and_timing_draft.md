# S4-A 阶段4 G0 基线与结论口径：结果记录、时间口径与异常记录口径

状态：`G0_ROUND_FROZEN_R06`（2026-10-22，UTC+8）。任务编号 `S4-A`。修订 `r06`。
- `r02`：按 rev-spec 第 1 轮独立审查（CHANGES_REQUIRED）修复 F4–F13。
- `r03`：按 dev-ps 实现反馈裁决 `candidate_count` 口径，与 2B 冻结实现及 2A T29 黄金对齐。
- `r04`：修复 TIMEOUT 的 `inference_time_ns` 口径与 `state_enum` 混入非状态键；补齐重复行检测、`frame_id` 回绕与 `stale` 措辞。
- `r05`：按 rev-spec 第 3 轮修复——新增 `measurement_scope` 定义（N1）、把候选超限改为与 2B 参考实现一致的硬错误语义并取消截断表述（N2），并把推得值/计划要求移出草案阈值节（N5）。
- `r06`：按 CDX-20261022-010 §2 更新并冻结本轮 G0 基线——① 与 2B 正式冻结回执对齐并删除 r05 及更早版本的失效快照语句（§0.1）；② 上游绑定扩展为完整钉扎并全部现场复算（§2）；③ 新增三种范围与各自结论口径（§6）；④ 冻结 UART 方案 B 与结果记录↔旁路日志唯一映射（§8.2）；⑤ 冻结异常行为口径、`stale_age_limit` 降级为 `DRAFT_PENDING_APPROVAL`（§5）；⑥ 冻结候选上限边界测试口径（§9）；⑦ 冻结 4-D 硬件授权与交接条件（§10）。

机器可读契约（权威字段名）：[`s4a_stage4_g0_fields.json`](s4a_stage4_g0_fields.json)。
本文件冻结的是**本轮阶段4 G0 基线与结论口径**，不是阶段4 验收；本轮不执行任何硬件操作，不产生板上、摄像头、HDMI 或 UART 实测结论。

## 0. 本轮冻结要点与上游事实

### 0.1 上游事实对齐（2B 已冻结并释放硬件）

- 2B **已于 2026-10-22 正式冻结并释放硬件**：正式入口为
  `D:\FPGA_Competition\w2b\report\evidence\S2B-T18\stage2b_freeze_receipt_20261022_r01\freeze_receipt.json`
  （SHA-256 `2687e87a9664d6415d17738a6f6ff10b8fe3e372696399eb710fa2d06d2778e1`，本机已复算一致）。
- 冻结事实（对照 CDX-20261022-007 与回执）：代码基线 `16ce2cdf8c00c6214435629d75a5e4b63acb66a9`；最终提交 `07c3d3958578b9cc9d3b8eae3758711fe08724c2`；G4=PASS、G5=PASS（来自独立阶段审查）；1000 次连续任务通过；109 个黄金输出匹配、其中 108 个 ACK 闭环计入（第 109 个最后 ACK 缺证保留）；硬件于 2026-10-22 11:21 释放（cpu0/cpu1 Stopped、CSR SAFE_IDLE_EPOCH1_LEDGER0），18:05 主机只读检查无 `hw_server`/XSDB 作业。
- 本文件 r05 及更早版本中与上述事实不符的旧快照语句已删除；2B 的 G4/G5 通过来自独立阶段审查，不是本文件推导。
- **当前硬件归属以现场会话核验为准**：2B 的释放只证明 2B 在其任务内释放，不代表当前板卡空闲；据只读旁证（`D:\codex-worktrees\w5\.codex\STATE.md`，2026-10-22 18:50）阶段5 S5-T01 上板 bring-up 正在执行并持有 JTAG/`hw_server`。**本任务未核验、未连接、未争用任何硬件会话，本树本轮不执行任何硬件操作。**

### 0.2 本轮冻结项（frozen_items，逐项与人读文档锚点绑定）

| 冻结 ID | 冻结项 | 章节 |
|---|---|---|
| `S4A-FREEZE-UART-B` | UART 方案 B：`s2bu/1.1` 不变、扩展关闭；时间/过期/丢帧/状态只在 PS 侧旁路日志记录；结果记录↔旁路日志唯一映射 | §8.2 |
| `S4A-FREEZE-SCOPES` | 三种范围 `offline_regression` / `board_injection` / `camera` 的允许与禁止结论 | §6 |
| `S4A-FREEZE-ANOMALY` | 超时、队列满、丢帧、非法输入、缓存所有权与恢复的行为口径 | §5.6 |
| `S4A-FREEZE-CANDIDATE-BOUNDARY` | 候选上限边界测试口径：恰好 12675 可行、追加 12676 硬错误 | §9 |
| `S4A-FREEZE-TIMING-REF` | 本轮采用的时间口径引用（端点定义、同一时基、分别测量） | §4 |
| `S4A-FREEZE-HW-AUTH` | 4-D 板测的正式实物授权与硬件会话交接条件 | §10 |

### 0.3 未冻结项（not_frozen_items，禁止写成已批准指标）

| 未冻结 ID | 项 | 状态 |
|---|---|---|
| `S4A-DRAFT-STALE-AGE-LIMIT` | `stale_age_limit = 200 ms` | `DRAFT_PENDING_APPROVAL` |
| `S4A-DRAFT-TIMEBASE` | PS 单调时基常量与 PL 跨域实测门控方法 | `DRAFT_PENDING_APPROVAL` |
| `S4A-DRAFT-OPTION-A-EXTENSION` | 方案 A（扩展帧/TLV 尾块） | `CLOSED_FOR_THIS_ROUND` |

## 1. 范围与边界

- 覆盖：阶段4 一条推理结果的字段与 `frame_id` 语义、推理耗时与端到端延迟的分别定义、丢帧/候选超限/过期结果的显式记录口径、无手=零框、非结果状态的取值规则、运行级测量范围注解、三种证据范围与结论口径、候选上限边界口径、UART 方案 B 与旁路日志映射、4-D 硬件授权条件、沿用 2A 的解码与阈值常量。
- 不覆盖：真实摄像头联调、上板、烧录、HDMI 显示（阶段5）、交互控制（阶段6）、CNN 重训。本轮不执行任何硬件操作。
- 不改动：2A 冻结规格与阈值、2B `s2b-physical/1.0.0`／`s2bu/1.1` 接口正文。
- 上游一律只读引用，完整钉扎见第 2 节。

## 2. 上游完整钉扎（现场复算，路径 / SHA-256 / 字节数 / 状态）

本节全部条目由 `scripts/stage4_s4a/verify_s4a_draft.py` 在每次运行时**现场复算**（1 MiB 流式读取），实际结果与字节数写入证据 JSON。断言失败即整体 FAIL。分组说明：`2A_docs` 为 2A 正式文档与证据；`2A_external` 为 `D:\FPGA_Data`（只读）外部模型/量化资产；`2A_in_tree` 为本工作树内的 2A 冻结参考实现；`2B` 为 w2b（只读）的接口文档、C 参考、软件实现、平台 JSON 与冻结回执。

| 绑定 ID | 路径 | SHA-256 | 字节数 | 状态 |
|---|---|---|---|---|
| `s2a_t01_spec` | `D:\FPGA_Competition\docs\obsidian-project\04-提交材料\阶段验收\S2A-T01_模型交付规格与G0接口冻结.md` | `7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230` | 21,110 | `G0_FROZEN` |
| `s2a_t01_model_manifest` | `D:\FPGA_Competition\report\evidence\S2A-T01\tiny416_model_manifest.json` | `9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a` | 22,153,976 | `G0_FROZEN` |
| `s2a_t01_fixed_test_samples` | `D:\FPGA_Competition\report\evidence\S2A-T01\fixed_test_samples.json` | `ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed` | 93,708 | `G0_FROZEN` |
| `s2a_t25_layer_golden_index` | `D:\FPGA_Competition\report\evidence\S2A-T25\cpu_layer_golden_index.json` | `cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d` | 3,883,870 | `COMPLETE` |
| `s2a_t25_shard_recovery_manifest` | `D:\FPGA_Competition\report\evidence\S2A-T25\t25_shard_recovery_manifest_20261002.json` | `5352b2ef6edb8f40bb1e635aaa1337556171937db176db841fb044406657d0d9` | 24,428 | `RECOVERY_MANIFEST` |
| `s2a_t25_tensor_shards` | `D:\FPGA_Competition\report\evidence\S2A-T25\tensors`（`sample_000..108.zlib`，109 个） | 逐片 SHA-256 见分片恢复清单（自检逐片校验） | 390,700,998 | `READ_ONLY_REFERENCE` |
| `s2a_t29_cpu_decode_nms_reference` | `D:\FPGA_Competition\report\evidence\S2A-T29\cpu_decode_nms_reference.json` | `24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231` | 265,725 | `CPU_REFERENCE_GENERATED` |
| `s2a_external_cfg` | `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r2\configs\gesture_yolov4_tiny_416_d8_formal.cfg` | `5475dff0daa8ac791ffbfcd10a188aa63d146244e561d62867ac59d627725376` | 3,522 | `G0_FROZEN` |
| `s2a_external_darknet_weights` | `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r2\checkpoints\gesture_yolov4_tiny_416_d8_formal_6000.weights` | `3984affa0a7fdd83ff851646139ea4e734c3df93569bfbaab214774cd92f7d8a` | 23,558,276 | `G0_FROZEN` |
| `s2a_external_gf8` | `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny_416_int8_weights.gf8` | `f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39` | 5,903,100 | `G0_FROZEN`（GFINT8W1 v1） |
| `s2a_external_calibration_list` | `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_calibration_r2\calibration.list` | `d637a2feb671429741c8b6703caaa9cdf995abf49dfa4b72e41f62dfbea1a35c` | 41,408（512 项） | `G0_FROZEN` |
| `s2a_external_hagridv2_manifest_csv` | `D:\FPGA_Data\HaGRIDv2\manifest.csv` | `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74` | 57,672,948 | `G0_FROZEN` |
| `s1_t02_d2_numeric_reference` | `verification/s1_t02_d2_numeric_reference.py` | `6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f` | 18,337 | `IN_TREE_FROZEN_REFERENCE` |
| `s1_t02_d9_decoder` | `verification/s1_t02_d9_yolo_decode.py` | `94dacdac18968e70871e1c21d24d5f4c3a9941881eaf37ffaab4d5372e28d190` | 15,747 | `IN_TREE_FROZEN_REFERENCE` |
| `s1_t02_d6_metrics` | `verification/s1_t02_d6_detection_metrics.py` | `4dcf0f7d9586b7096be015faf2c5037489b03b04baeec0daea4cadec89be591a` | 74,024 | `IN_TREE_FROZEN_REFERENCE` |
| `s2b_physical_interface_candidate` | `D:\FPGA_Competition\w2b\docs\obsidian-project\02-方案设计\s2b_physical_interface_candidate.md` | `c5559f6462b964ee1f7469b006fcd134412702fb074193bf34c1451120f761b0` | 52,200 | `G0_FROZEN_ONLY_DEFINITION`（`s2b-physical/1.0.0`） |
| `s2b_board_transport` | `D:\FPGA_Competition\w2b\docs\obsidian-project\02-方案设计\s2b_board_transport.md` | `b305c84c8b3255ca2c2960b3bce8c08b1c60fc32d0bdc7fa11609c1b609ce6cb` | 13,366 | `G0_FROZEN_ONLY_DEFINITION`（`s2bu/1.1`） |
| `s2a_ps_decode_nms_reference_c` | `D:\FPGA_Competition\w2b\verification\s2a_ps_decode_nms_reference.c` | `cf1904da1b6f9110a957ea788cdb7f9c6b7773d2fd8b7b61779063e5f995d845` | 11,675 | `FROZEN_IMPLEMENTATION_REFERENCE` |
| `s2a_ps_decode_nms_reference_h` | `D:\FPGA_Competition\w2b\verification\s2a_ps_decode_nms_reference.h` | `edd61d7f47e2681ebd3b21f599c9637d41b257f5e0fc7b9b909f7962d758ce47` | 1,135 | `FROZEN_IMPLEMENTATION_REFERENCE` |
| `s2b_board_transport_py` | `D:\FPGA_Competition\w2b\verification\s2b_board_transport.py` | `7dda231e2888c0ed9d95952dcba4d41c9eaf7423e008e4d179b3f7d2c5f0b334` | 30,371 | `FROZEN_IMPLEMENTATION_REFERENCE` |
| `s2b_inference_app_c` | `D:\FPGA_Competition\w2b\vitis\s2b_inference_app.c` | `9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39` | 23,212 | `FROZEN_IMPLEMENTATION_REFERENCE` |
| `s2b_build_inference_py` | `D:\FPGA_Competition\w2b\vitis\build_s2b_inference.py` | `ffa81cbaaaf590ef00eeab8b31c3952becb8a90b29514b310e464f8326c45b9a` | 32,400 | `FROZEN_IMPLEMENTATION_REFERENCE` |
| `s2b_inference_platform_json` | `D:\FPGA_Competition\w2b\board\s2b_inference_platform.json` | `6f69e6ad1d77eb455ab924d41c06e0c93703bfdb89be6743ea301868975ecd97` | 233,528 | `FROZEN_IMPLEMENTATION_REFERENCE` |
| `stage2b_freeze_receipt` | `D:\FPGA_Competition\w2b\report\evidence\S2B-T18\stage2b_freeze_receipt_20261022_r01\freeze_receipt.json` | `2687e87a9664d6415d17738a6f6ff10b8fe3e372696399eb710fa2d06d2778e1` | 6,506 | `STAGE_2B_FROZEN_G4_G5_PASS` |

- 独立钉扎条目共 **24 项**（含 1 项目录聚合 `s2a_t25_tensor_shards`，其计数与逐片 SHA 以分片恢复清单为准）；其中带 SHA-256 的**文件**条目 **23 项**，本轮现场复算全部 MATCH（实际字节数见证据 `upstream_sha_recompute.json`）。
- `D:\FPGA_Data` 外部资产按只读访问；不可读时必须在契约中如实标 `NOT_AVAILABLE` 并给出原因，**不得写猜测的哈希**（本轮 5 项全部可读并已复算）。
- 钉扎路径取自 2A manifest 声明的路径；同 SHA 的同内容副本（cfg 3 份、weights 3 份、`calibration.list` 3 份）不改变身份。
- 变更影响：任一 2B 文档/C 参考/软件实现或 2A 外部资产变更，都必须重新推导候选上限与 `candidate_count` 口径，并回归本契约、S4-B 骨架与 S4-C 对拍。

## 3. 阶段4 结果记录

### 3.1 `frame_id`

- `frame_id` 是 `uint32` **不透明值**：PS 在 idle 写 `FRAME_ID`，PL 接受 `start` 时锁存并随 `done` 原样回传；PL 不解释该值（2A 冻结语义；2B 物理接口进一步规定其任意 32-bit 可重复，事务归属由 64-bit epoch 承担）。
- 同一帧的采集侧与结果侧必须使用同一 `frame_id`；结果记录不得重编号、不得把它当序号使用。
- 结果序号由新增的 `result_seq` 承担（PS 本地单调递增，从 1 起）。
- 采集侧连续分配与回绕约定、以及与丢帧判定的依赖关系见 5.1；`frame_id` 同时是 UART 结果记录与 PS 旁路日志的连接键（见 8.2）。

### 3.2 结果字段（与 JSON `result_record.fields` 一一对应）

标注含义：`必填` = 该字段在任何结果记录中都必须出现（可以有缺值哨兵，但不得省略字段）；`2A 冻结` = 该字段或其对应量已由 2A 冻结对象定义，阶段4 不得重新定义。边界情况（`geometry`、`detection_count`、`candidate_count`）的判定依据见 JSON `field_annotation_definitions.boundary_cases_of_frozen_by_2a`。

| 字段 | 类型 | 必填 | 2A 冻结 | 语义 |
|---|---|---|---|---|
| `frame_id` | u32 | 是 | 是 | 见 3.1；对 PL 不透明，连续分配与回绕是 PS 侧约定（见 5.1） |
| `result_seq` | u32 | 是 | 否 | PS 结果记录序号，本地单调递增，拒绝回绕到 `0xFFFFFFFF`；与 s2bu 运输 sequence 不同，且不传输（见 8.2） |
| `geometry` | `{width:u32, height:u32}` | 是 | 是 | 原图尺寸（顺序固定 width,height），是补边逆映射唯一基准 |
| `state` | enum | 是 | 否 | 只能取 3.4 的 5 个状态之一 |
| `detection_count` | u32 | 是 | 否 | 恒等于 `detections` 长度；失败与无手必须为 0；≤15；取值受 2A 第 75 行“检测数必须完全相同”约束 |
| `detections` | array | 是 | 是 | 阈值+稳定排序截断+类别内 NMS 之后的框，顺序即 D9 输出顺序；无结果状态必须为空数组 |
| `candidate_count` | u32 | 是 | 否 | **阈值筛除后、稳定排序截断到 15 之前、NMS 前**的候选数，与 T29 黄金及 2B 冻结实现同口径（见 8.1、9） |
| `candidate_count_pre_threshold` | u32 | 否 | 否 | 可选诊断：阈值筛除前的候选机会数（正面积候选框数 × 5 类）；不进 UART、不参与对拍 |
| `candidate_overflow` | bool | 是 | 否 | 候选数达到候选缓冲上限时为 true，属 ERROR 硬错误路径（`error_code=1`），**不定义截断**；tiny416 固定配置下不可达（恒 false），仍须显式记录（见 5.2、9） |
| `capture_time_ns` | u64 | 是 | 否 | 该帧第一个有效像素（或等价帧起始事件）时刻；无观测为 0 哨兵；注入范围下不可用（见 6.2） |
| `result_time_ns` | u64 | 是 | 否 | 解码/NMS 完成、结果可发布（可开始 UART 发送）时刻；无结果为 0 哨兵 |
| `inference_time_ns` | u64 | 是 | 否 | PL 任务窗口耗时，见 4.1；**不得**冒充端到端延迟；超时/错误取 0 哨兵 |
| `end_to_end_latency_ns` | u64 | 是 | 否 | 见 4.2；仅两端均为真实观测时有定义，否则 0 哨兵（不得为负、不得沿用上一帧） |
| `dropped_frames` | u32 | 是 | 否 | 相对上一结果丢失的帧数，见 5.1 |
| `stale` | bool | 是 | 否 | 结果年龄超上限，见 5.3；仅对 `OK`/`NO_HAND` 定义，其余状态恒 false；上限值仍未批准 |
| `error_code` | u32 | 是 | 是 | 沿用 2A CSR `ERROR_CODE`（0..7）；成功与无手为 0 |

### 3.3 检测框记录 `detection_record`

| 字段 | 类型 | 必填 | 2A 冻结 | 语义 |
|---|---|---|---|---|
| `class_id` | u32 | 是 | 是 | 0..4，严格按 `fist,palm,one,two_up,three` |
| `class_name` | string | 是 | 是 | 由 `class_id` 派生，不得另行映射 |
| `score` | f64 | 是 | 是 | `sigmoid(objectness)*sigmoid(class)`；报告与显示一律称“分数（score）”，**不得**称“置信度” |
| `xyxy` | f64[4] | 是 | 是 | 归一化原图坐标，含补边逆映射，裁剪到 `[0,1]`，正面积 |
| `xyxy_px` | f64[4] | 否 | 否 | 派生显示值 `xyxy * [width,height]`；不作为对拍口径；缺省表示未派生，不等于 0 哨兵 |
| `source_order` | u32 | 是 | 是 | D9 稳定 tie 顺序下的候选序号 |

### 3.4 状态枚举 `state_enum`

| 值 | 条件 | `detection_count` |
|---|---|---|
| `OK` | PL 成功、阈值与 NMS 后 ≥1 框；时间字段均为真实观测值 | ≥1，≤15 |
| `NO_HAND` | PL 成功、阈值与 NMS 后 0 框（无手=零框，合法成功，不计入丢帧） | 0 |
| `TIMEOUT` | PL 期限到期中止（`error_code=5`）；无完成沿，`inference_time_ns` 取 0 哨兵 | 0（框无效） |
| `ERROR` | 其他 PL/memory/协议/数值错误（`error_code∉{0,5}`）；候选达上限属此状态且 `error_code=1` | 0（框无效） |
| `DROPPED` | 采集侧存在该帧但未产生结果 | 0 |

`state` 只能取以上 5 个值；非 `OK`/`NO_HAND` 状态下其余必填字段的取值规则见 5.5（与 JSON `result_record.absent_value_policy` 一致）。

## 4. 时间口径

本轮时间口径引用已冻结：`S4A-FREEZE-TIMING-REF`。冻结的是**端点定义、同一 PS 单调时基与分别测量/分别报告**；时基常量与跨域实测门控方法仍是未冻结项 `S4A-DRAFT-TIMEBASE`。

### 4.1 推理耗时 `inference_time_ns`

- 起点：CSR 接受有效 `start` 的上升沿（PL `busy=1`、取得 buffer 所有权）。
- 终点（成功）：`operator_result_valid` 单周期脉冲且 `operator_error_code=0`（PL 提交 `done`）。
- **超时没有成功终点**：2A 规格第 65 行规定超时在第 N 个后续上升沿中止任务（`timeout=1` 恰给一个完整执行周期），此时不会出现 `operator_result_valid` 且 `code=0`。因此本契约**不为 `TIMEOUT` 定义 `inference_time_ns` 数值**，取 0 哨兵；实现若按 `STATUS.busy` 门控观测到中止沿耗时，只能作为实现侧诊断值单独记录，不得写入本字段。
- **错误完成事件存在**（2A 规格第 67 行：非零 `operator_error_code` 随单周期 valid 脉冲给出且错误码同沿稳定），但本契约同样不为 `ERROR` 定义该字段的数值口径，缺省 0 哨兵。
- 包含：PL 内部算子计算、PL 对 memory 的 feature/head 读写与停顿周期。
- 不含：PS 预处理/量化、输入与权重装载、PS 解码/NMS、UART 发送、结果排队与显示。
- **本窗口是 2A CSR busy 窗口的近似**：2A 规格第 46 行规定 `busy` 要写完两头与 `FRAME_ID` 才清，而本终点取 `operator_result_valid=0`（第 67 行）。若按 `STATUS.busy` 门控实测，实测窗口可能略宽；**不声称两者逐周期等价**，实测门控方法待正式 G0 冻结。

### 4.2 端到端延迟 `end_to_end_latency_ns`

- 起点：`capture_time_ns`（该帧第一个有效像素或等价帧起始事件）。
- 终点：`result_time_ns`（该 frame 解码/NMS 完成、结果可发布）。
- 包含：采集 → 缩放/补边/颜色/量化预处理 → 输入搬运 → PL 推理（含 `inference_time`）→ PS 解码/NMS → 结果排队。
- 不含：UART 传输完成之后的显示延迟（属阶段5 口径）。
- 强制规则：两者必须分别测量、分别报告；**不得用推理耗时冒充端到端延迟**；两者必须处于同一 PS 单调时基。
- 定义域：仅当 `capture_time_ns` 与 `result_time_ns` 均为真实观测值（`state ∈ {OK, NO_HAND}`）时有定义；否则取 0 哨兵。
- 注入规则：`board_injection` 范围下 `capture_time_ns` 不可用，本字段无定义（0 哨兵）；注入延迟必须以注入起点 `injection_start_ns` 单独报告（见 6.2）。

### 4.3 时基与 FPS

- 时基：PS 侧同一单调计数器（建议 CPU 全局定时器，频率与 `COUNTS_PER_SECOND` 待正式 G0 冻结）；PL 窗口端点由 PS 侧门控观测，跨域测量方法待正式 G0 冻结（`S4A-DRAFT-TIMEBASE`）。
- FPS 分别定义：采集 FPS、推理 FPS、显示 FPS（阶段5）不得互相替代；预热、丢帧、超时不得隐藏。

### 4.4 运行级注解 `measurement_scope`（证据侧，定义见 JSON `evidence_annotation`）

- 位置：证据清单/结果集合的元数据（例如 S4-B host 结果 JSON 顶层 `measurement_scope`）。它**不是结果记录字段、不进 UART 帧**，此处给出权威键名与取值是为了让 S4-B/S4-C 不再自行发明。
- 键与允许值：

| 键 | 允许值 | 语义 |
|---|---|---|
| `source_kind` | `OFFLINE_REGRESSION` / `BOARD_INJECTION` / `CAMERA` | 本批结果所属证据范围，必须与 §6 的三种范围之一一致，禁止跨范围混用结论 |
| `pl_timing` | `MEASURED` / `NOT_EXECUTED_OFFLINE` | 四个时间字段的测量状态；`NOT_EXECUTED_OFFLINE` 表示取 0 哨兵、不是实测值 |
| `uart_transport` | `MEASURED` / `NOT_EXECUTED_OFFLINE` | UART 真实链路是否参与；离线准备期为 `NOT_EXECUTED_OFFLINE` |
| `board_pl` | `MEASURED` / `NOT_EXECUTED_OFFLINE` | PL/板卡是否参与；离线准备期为 `NOT_EXECUTED_OFFLINE` |
| `capture_time_available` | `true` / `false` | `capture_time_ns` 是否为真实采集时间；离线与注入范围必须为 `false`，仅摄像头范围可为 `true` |
| `injection_start_ns` | u64 或 null | 仅注入范围：注入起点时间（同一 PS 单调时基）；不得写入 `capture_time_ns`、不得解释为采集时间 |
| `clock_domain` | string（如 `PS_MONOTONIC` / `PL_FCLK` / `HOST_WALL`） | 本批时间字段所属时钟域；跨域换算未冻结时必须显式声明，不得跨域直接相减 |
| `unavailable_fields` | `array<string>` | 因未执行或本范围不可用而取 0 哨兵的字段名列表，必须与上述取值自洽 |

- 规则：取值为 `NOT_EXECUTED_OFFLINE` 时相应字段必须是 0 哨兵且不得解释为实测耗时；`source_kind=BOARD_INJECTION` 时 `capture_time_available` 必须为 `false` 且必须给出 `injection_start_ns` 与 `clock_domain`；整个对象缺失表示未声明测量范围，**不得据此推断已实测**。

## 5. 异常与边界记录口径

### 5.1 丢帧与 `frame_id` 连续分配

- 分配约定：同一会话内，PS 采集侧对每个被采集/入队的帧按 `+1` 递增分配 `frame_id`（从 1 起）；离线回放沿用 2A 固定样本的 `frame_id` 0..108。
- 该连续性是 **PS/运输侧约定**（`s2bu/1.1` 第 49 行“响应 frame 为请求 frame+index”），不是 PL 语义；PL 侧仍视之为任意 u32。
- 回绕：与 `result_seq` 同一约定，**拒绝回绕**；`frame_id` 达到 `0xFFFFFFFE` 后不得自然溢出到 0，必须开启新会话或显式复位计数。离线回放固定使用 0..108，不涉及回绕。
- 会话：同一 `session_id` 内禁止复用 `frame_id`；PS 重启、复位 `frame_id` 计数或以相同请求 frame 重开 RUN 时必须分配新 `session_id`（见 8.2）。
- 丢帧判定：同一 `frame_id` 序列中不连续即计为丢帧；`dropped_frames` = 本结果相对上一已发布结果的缺失帧数。
- **互斥规则（避免双计）**：若某缺失帧已单独发布一条 `state=DROPPED` 记录，则该帧**不再计入**后续结果的 `dropped_frames`。`dropped_frames` 只统计既无结果、也无 DROPPED 记录的缺失帧，保证每个缺失帧恰好被计数一次。
- 缺帧不得静默跳过：PS 若知道该帧存在，必须补一条 `state=DROPPED` 记录；仅当完全无采集事实时才只累计 `dropped_frames`。
- 若采集源本身会跳号（非连续分配），必须显式声明实际分配规则，否则丢帧统计无效。

### 5.2 候选超限（与 2B 参考实现一致的硬错误语义）

- 候选缓冲上限 `candidate_limit = 12675`，由 2B 冻结实现 `w2b/verification/s2a_ps_decode_nms_reference.h` 的 `S2A_T62_MAX_CANDIDATES = 12675u` 与 tiny416 几何共同决定：两头 `(13×13 + 26×26) × 3 anchors × 5 classes = 12,675`，即阈值后可产生的候选上界。
- **该上限以硬错误方式强制**：参考实现在候选数达到上限时返回 `S2A_T62_INVALID_ARGUMENT` 并中止（该文件 `.c` 第 178–179 行），**没有“截断到上限”的行为**；该实现只有 NMS 之前对 **15** 的截断（第 263 行）。本契约因此**不定义候选截断语义**。
- 对应到阶段4 记录：`candidate_overflow=true` ⇒ `state=ERROR`、`error_code=BAD_ARGUMENT(1)`、`detections=[]`。
- **在 tiny416 固定配置下不可达**：`candidate_count` 的上界恰等于该上限，故 `candidate_overflow` 恒为 false；此时必须**显式记录“未超限”这一事实**（字段保留、值为 false），不得因恒假而省略字段或省略记录口径。
- 边界测试口径见 §9（恰好 12675 可行、尝试追加 12676 必须硬错误）。
- 曾提出的 `candidate_limit = 4096` 属 **弃用的草案值**：它低于理论最大候选数，会引入 2A D9 与 2B 参考实现中都不存在的候选截断，破坏与 T29 黄金的逐框等价；**禁止启用**。
- 区分：`candidate_limit`（12,675）是候选缓冲上限（硬错误路径）；`max_outputs_per_image=15` 是 NMS 之前的截断与 NMS 之后的输出上限（2A 冻结）。两者不得混用，也不得用 NMS 后 ≤15 框推断候选容量。

### 5.3 过期结果

- `stale=true` 当结果年龄超过 `stale_age_limit`；结果年龄 = 发布时刻 − `result_time_ns`。
- 发布时刻定义：该结果记录被提交给发布层（开始 UART 发送或交给显示层）的时刻，与其余时间字段同一 PS 单调时基。
- **定义域**：`stale` 与 `state` 独立判定，但仅对 `state ∈ {OK, NO_HAND}` 定义；`TIMEOUT`/`ERROR`/`DROPPED` 恒为 `false`（这些状态无 `result_time_ns`，年龄无定义）。
- stale 结果仍保留原记录与框；显示层必须显式声明结果年龄，不得伪称同帧。
- `S4A-DRAFT-STALE-AGE-LIMIT`：`stale_age_limit = 200 ms` 仍是草案（`DRAFT_PENDING_APPROVAL`，取代此前的 `DRAFT_PROPOSED` 措辞），无批准依据；由阶段4 正式 G0（或 Wong）批准后才供阶段5 消费，批准前阶段5/6 不得把它当作已批准门槛。

### 5.4 无手与其他边界

- 无手 = 零框：`state=NO_HAND`、`detection_count=0`、`error_code=0`；**时间字段仍为真实观测值**；不是错误，不计入丢帧。
- 每图 ≤15 框为 2A 冻结值；放宽即属规格变更，必须回退 G0 决策。

### 5.5 非结果状态的取值与缺值哨兵

- 所有 `required` 字段在每条记录中都必须出现；无结果时用哨兵值填充，**不得省略字段、不得沿用上一帧的值、不得出现负数或时间倒流**。
- `0` 的含义是“未观测/不适用”，不是 1970 时刻、也不是合法耗时；读取方必须先按 `state` 判别，并按 4.4 的 `measurement_scope` 确认测量范围。
- 逐状态取值（与 JSON `result_record.absent_value_policy.by_state` 一致）：

| 状态 | capture_time_ns | result_time_ns | inference_time_ns | end_to_end_latency_ns | candidate 字段 | stale | error_code |
|---|---|---|---|---|---|---|---|
| `OK` / `NO_HAND` | 真实值 | 真实值 | 真实实测（大于 0） | `result_time − capture_time`（大于 0） | 真实候选数；overflow=false | 按 5.3 计算 | 0 |
| `TIMEOUT` | 真实值 | 0 | 0 哨兵（无完成沿，见 4.1） | 0 | 已观测值，未观测为 0；overflow=false | false | 5 |
| `ERROR` | 真实值 | 0 | 0 哨兵（本契约不定义口径，见 4.1） | 0 | 已观测值；若达候选上限则 overflow=true | false | 非 0 且非 5；候选超限为 1 |
| `DROPPED` | 已知则真实值，否则 0 | 0 | 0 | 0 | 0 与 false | false | 0 |

- `DROPPED` 记录本身的 `dropped_frames` 按 5.1 的互斥规则处理（该帧不被重复计入后续结果）。

### 5.6 异常行为冻结（`S4A-FREEZE-ANOMALY`）

本轮冻结以下行为口径（与 JSON `anomaly_behaviour_freeze` 一致）：

- **超时**：PL 期限中止（`error_code=5`），无成功完成沿，`inference_time_ns` 取 0 哨兵；不得把超时记作零框成功，也不得用后续帧结果顶替。
- **队列满**：不得覆盖仍被推理或显示读取的帧；新帧按丢帧路径显式记录（`state=DROPPED` 或累计 `dropped_frames`），队列满事件必须计数并可在旁路日志按 `session_id`/`result_seq` 定位。
- **丢帧**：见 5.1；`dropped_frames` 与 `DROPPED` 行互斥，每个缺失帧恰好计数一次。
- **非法输入**：非法长度/格式/地址/几何/CRC 必须在进入需验收的预处理之前拒绝，返回非零失败并保留原始字节；禁止静默截断、补齐或改写为合法输入，禁止用部分消费的输入发布结果。
- **缓存所有权与恢复**：帧缓冲所有权显式移交（写入完成 → 发布所有权 → 消费者读取完成 → 读取结果/invalidate → 释放）；DMA 完成顺序与 cache 维护方向必须与地址图一致；禁止生产者覆盖仍被读取的帧。恢复只由当前硬件持有者执行，恢复前先保全原始日志与终态；禁止自动复位 PL、清空串口、复用旧 epoch/结果或改写失败记录。
- 一律禁止：静默截断候选、复用旧结果、把超时记作零框成功、静默跳过缺失帧、用图像发送次数代替有效推理完成次数。

## 6. 三种证据范围与结论口径（`S4A-FREEZE-SCOPES`）

每个范围给出**允许**与**禁止**的结论；范围字段 `source_kind` 必须与 4.4 的 `measurement_scope.source_kind` 一致，禁止跨范围混用结论。**注入子项通过 ≠ 摄像头 G5 通过**；完整阶段4 判 G3/G4/G5 仍受摄像头验收约束。

### 6.1 `offline_regression`（离线回归）

- 允许：字段/契约/文档一致性结论；离线回放对拍（冻结 109 彩色样本的 PS 解码/NMS 数值等价、逐框差异与最大误差）；候选上限边界的离线判定；异常记录口径与缺值哨兵的自洽性。
- 禁止：声称板上 PL 实测、真实 UART 运输、真实采集或摄像头结论；用离线 0 哨兵冒充实测耗时（必须声明 `measurement_scope` 的 `NOT_EXECUTED_OFFLINE`）；把注入/离线子项通过写成阶段4 G5 或摄像头验收通过；把灰度（诊断用）输入与冻结彩色输入的 golden 逐框比对并据此报告颜色质量或总体准确率。

### 6.2 `board_injection`（板上注入）

- 允许：注入帧经预处理→PL→PS 解码/NMS 的整链结论（注入点必须在需验收的预处理之前）；两头 INT8 原始字节（head13 5,070 B / head26 20,280 B）与独立 PC 参考的逐值比对；逐框数量/类别/坐标/分数差异与分层判错；注入起点到结果的延迟（单独报告，与 PL 耗时分开）；故障序列的可观测性与恢复统计。
- **注入不得伪造 `capture_time`**：必须声明注入起点时间 `injection_start_ns`、时钟域 `clock_domain` 与 `measurement_scope`；注入下 `capture_time_ns` 不可用（`capture_time_available=false`），**不得用注入起点冒充采集时间**，也不得写入 `end_to_end_latency_ns`。
- 其他禁止：把注入子项通过写成摄像头范围结论或阶段4 G5 通过；用注入输入对冻结彩色 golden 直接比对（输入不同必须由冻结独立参考另生成预期并绑定）；用 UART 传输完成时刻或主机接收时刻冒充 `result_time_ns`；跳过上游 SHA 校验或临时放宽容限取得正式 PASS。

### 6.3 `camera`（真实摄像头）

- 允许：真实 RGB565 展开、颜色、缩放/补边/量化与独立参考一致的结论；真实采集条件下 ≥30 分钟且 ≥1000 次有效推理的稳定性、丢帧与过期统计；≥50 次预定义交互观察（每类 ≥10 次）的记录与成功率（门槛须由有效 G0 确认）；独立保留测试集上的 mAP/各类召回与精确率/无手误检（阈值须经批准）。
- 禁止：用注入/离线/灰度结果替代真实摄像头结论，或据此判完整 G3/G4/G5；把灰度或旧坏模块的帧作为真彩质量或总体准确率依据；把单框 0.90 分数写成 90% 准确率，或用图像发送次数代替有效推理完成次数；在未冻结样本/阈值前宣称独立测试集指标。

## 7. 沿用 2A 的冻结常量

以下常量由上游 `tiny416_model_manifest.json` 的 `detection_postprocess` / `address_map.heads` 与 2A 规格决定；自检脚本必须从上游文件读取并比对，不得只与本契约的副本比对。候选理论上界同时与 2B 参考实现头文件的宏比对。

| 项 | 值 |
|---|---|
| 模型/输入 | tiny416，RGB 416×416 CHW INT8 |
| 类别顺序 | `fist=0, palm=1, one=2, two_up=3, three=4` |
| `score_threshold` | `0.25`，判定为 `score >= 0.25`（含等号） |
| NMS | 类别内 greedy `IoU=0.45`，跨类别不抑制 |
| 每图输出上限 | 15（NMS 之前截断与 NMS 之后输出） |
| 候选缓冲上限 | 12,675（2B 参考实现 `S2A_T62_MAX_CANDIDATES`；等于理论最大候选数 `(13×13+26×26) × 3 anchors × 5 classes`） |
| 分数定义 | `sigmoid(objectness)*sigmoid(class)` |
| 坐标策略 | D2 整数截断 resize + 左上 floor padding；裁剪到 `[0,1]`；零面积丢弃 |
| 稳定 tie 顺序 | head 顺序 → row-major cell → anchor-local → class_id |
| 检测头 | `[1,30,13,13]` length_bytes 5,070 scale `0.24267549589862975`；`[1,30,26,26]` length_bytes 20,280 scale `0.30223452951025775` |
| 对拍容限 | 离散字段必须完全相同；`score` 与 `xyxy` 各分量绝对误差 ≤`1e-6`；相对容限 0（规格第 75 行） |

## 8. 与 `s2bu/1.1` 的映射与 UART 方案 B 冻结

### 8.1 字段覆盖

| 阶段4 字段 | `s2bu/1.1` |
|---|---|
| `frame_id`、`geometry` | 40 B 头 `<4sHH8I>` 的 frame_id / width / height |
| `detection_count` | 响应元数据 `box_count` |
| `detections` | 每框 48 B `<ii5d>`（class_id、source_order、score、x1..y2） |
| `candidate_count` | 响应元数据 `raw_candidate_count`（同口径，见下） |
| `candidate_count_pre_threshold` | 无（诊断字段，不进 UART） |
| `error_code` | 响应元数据 `ERROR_CODE` |
| `result_seq` | 无对应字段（不传输；运输 `sequence` 是请求/响应配对序号，不是结果序号） |
| `session_id` | 无对应字段（不传输；仅存在于 PS 旁路日志） |

- `raw_candidate_count` 语义：`s2bu/1.1` **正文未写明统计口径**；但 2B 冻结实现（`s2a_ps_decode_nms_reference.c`）与 2A T29 黄金（`samples[i].raw_candidate_count_before_stable_nms`）实际都是**阈值筛除后、15 框截断前、NMS 前**的计数。阶段4 的 `candidate_count` 采用完全相同口径，以保证可与 T29 黄金逐样本比对，并因此与 UART 字段可直接对齐。**若 2B 后续把该字段正式冻结为其他口径，必须回归本契约、S4-B 骨架与 S4-C 对拍口径**。

### 8.2 UART 方案 B 冻结（`S4A-FREEZE-UART-B`）

- **冻结内容**：Wong 已定方案 B（CDX-20261022-007/015 §6、CDX-20261022-010 §2.3）。本轮冻结为：`s2bu/1.1` 正文与既有字段语义**不变**、**扩展关闭**（方案 A 的新 op / TLV 尾块 `S4A-DRAFT-OPTION-A-EXTENSION` 不实现、不预埋）；时间、过期、丢帧、状态契字段只在 **PS 侧旁路日志**记录。**不单方修改上游协议正文**；若需扩展须由 Wong 决策并协调 2B。
- **本地方案（因现有字段不足以唯一关联）**：`s2bu/1.1` 既不携带 `session_id` 也不携带 `result_seq`；运输 `sequence` 是请求/响应配对序号，`epoch` 是 PL 事务 epoch，都**不足以**在同一 PS 会话内把「结果记录」与「PS 旁路日志」唯一关联。因此本契约给出本地映射方案：

| 项 | 定义 |
|---|---|
| 仅本地字段 | `session_id`（u32，PS 本地分配，不传输）、`result_seq`（u32，PS 结果记录本地单调递增，从 1 起，不传输） |
| 连接键 | `(session_id, frame_id, repeat_index)` |
| PS 日志主键 | `(session_id, result_seq)` |
| UART 可观测键 | `(frame_id, repeat_index, sequence)` |
| `session_id` 规则 | 每次 PS 启动、每次复位 `frame_id` 计数、或每次以相同请求 `frame_id` 重开 RUN 时重新分配；同一 `session_id` 内禁止复用 `frame_id` |

- **唯一性论证**：`s2bu/1.1` 第 49 行规定响应 frame 为请求 frame+index，故同一 RUN 内每个结果的 `frame_id` 互不相同，`(session_id, frame_id, repeat_index)` 在同一 `session_id` 内唯一；`result_seq` 单调递增且拒绝回绕，构成 PS 日志主键。主机侧只用 UART 可观测键连接，**不依赖时钟接近度**。
- **冲突处理（必须显式记录，禁止猜测归属）**：
  - PS 日志出现重复 `(session_id, frame_id, repeat_index)` ⇒ 判为日志损坏 `LOG_DUPLICATE_KEY`，禁止发布该结果，保留原始两行；
  - UART 收到但日志无对应行 ⇒ `uart_orphan`，逐条计数；
  - 日志有行但 UART 无对应记录 ⇒ `log_orphan`（运输丢弃或主机漏收），逐条计数；
  - 一条 UART 记录匹配到多于一条日志行 ⇒ `AMBIGUOUS`，不归属、停止自动对账、保留原始证据；
  - 不得按时间邻近、序号邻近或「最新一条」猜测归属。
- `sequence` 只作配对与一致性核对（连续递增、拒绝回绕），不作唯一键；冲突时以 PS 日志主键为准。
- **后果（必须显式承认）**：方案 B 下 `capture_time_ns`/`result_time_ns`/`inference_time_ns`/`end_to_end_latency_ns`/`stale`/`dropped_frames` 不出现在 UART 记录中，主机侧拿不到 PS 侧真实采集/结果/推理耗时。因此阶段计划第 88 行的相关要求只能由 **PS 侧旁路日志方案**满足（日志落点与采集方式须在正式 G0 声明），**不得据方案 B 直接宣称已满足**。

## 9. 候选上限边界测试口径（`S4A-FREEZE-CANDIDATE-BOUNDARY`）

- 上限 `candidate_limit = 12675`，依据 2B 冻结实现：`s2a_ps_decode_nms_reference.h` 的 `S2A_T62_MAX_CANDIDATES = 12675u`，`.c` 第 178–179 行在候选数达到上限时返回 `S2A_T62_INVALID_ARGUMENT`。
- **恰好 12675**：必须**可行**——不报错、不截断，按稳定 tie 顺序继续到 NMS 之前对 15 的截断与类别内 NMS。
- **尝试追加 12676**：必须**硬错误**——返回 `S2A_T62_INVALID_ARGUMENT`，映射到 CSR `BAD_ARGUMENT(1)`；对应结果记录 `state=ERROR`、`candidate_overflow=true`、`detections=[]`、`detection_count=0`。
- **禁止启用已废弃的 4096**：`candidate_limit=4096` 会引入 2A D9 与 2B 参考实现中都不存在的候选截断，破坏与 T29 黄金的逐框等价；本轮明确 `enabled=false`。
- **不得混同**：候选容量（12,675，硬错误路径）与 NMS 后 ≤15 框（2A 冻结输出上限）是两个不同量；不得用「NMS 后 ≤15 框」推断候选容量，也不得把候选上限写成输出上限。
- 测试须绑定：被测实现的 `S2A_T62_MAX_CANDIDATES` 值、调用返回值、CSR/记录映射，以及恰好/超出两例的原始输出；测试在离线范围（`offline_regression`）执行即有效，**不需要也不得为此操作硬件**。

## 10. 4-D 板测：正式实物授权与硬件会话交接条件（`S4A-FREEZE-HW-AUTH`）

以下条件**全部具备**时，才可执行 4-D 的注入子任务（CDX-20261022-010 §5）；**本轮不执行任何硬件操作**（`NOT_RUN`）：

| 条件 ID | 条件 | 本轮状态 |
|---|---|---|
| `operator_authorization` | 正式实物授权：由 Wong 或阶段总控给出、含授权时间与范围的上板/注入授权记录（阶段5 的 13:25 授权不覆盖阶段4） | `NOT_MET_BY_THIS_TASK` |
| `hardware_session_handoff` | 当前硬件持有方明确让出，并有真实 11 字段交接行（状态 `OFFERED`→`CLAIMED`）；没有 `OFFERED` 不得接管 | `NOT_MET_BY_THIS_TASK` |
| `exclusive_session` | 独占 `hw_server`/JTAG/串口会话；已核对现场会话与板上程序，不使用旧 PID、不结束他人进程 | `NOT_MET_BY_THIS_TASK` |
| `artifact_binding` | 绑定本次 bit/XSA/ELF、地址图、时钟与恢复入口；PL 未从源重建等限制如实记录 | `NOT_MET_BY_THIS_TASK` |
| `injection_command_delivery` | 4-B 交付实际构建/装载/启动/导出/停止/恢复命令，含参数校验与非零失败退出，并通过独立审查（注入点必须在需验收的预处理之前） | `BLOCKED_PENDING_S4B` |
| `timing_and_threshold_freeze` | 本轮时间口径引用与候选上限边界已冻结；时基常量、跨域门控方法与 `stale_age_limit` 仍待正式 G0 批准 | `PARTIAL` |

- 完整阶段4 仍受摄像头验收约束（CDX-20261022-010 §6）：**注入子项通过 ≠ 摄像头 G5 通过**。
- 本轮证据只覆盖离线范围，硬件相关检查一律记 `NOT_RUN` 并说明原因，不得以离线结果替代。

## 11. 未冻结项与下一步

- **`DRAFT_PENDING_APPROVAL`（未冻结）**：`stale_age_limit`（`S4A-DRAFT-STALE-AGE-LIMIT`）、时基常量与跨域测量方法（`S4A-DRAFT-TIMEBASE`）。由阶段4 正式 G0 或 Wong 批准后才生效，不得写成已批准指标。
- **`CLOSED_FOR_THIS_ROUND`**：方案 A 的 UART 扩展（`S4A-DRAFT-OPTION-A-EXTENSION`）；重新开启须 Wong 决策并协调 2B。
- **由上游推导（不属草案值）**：`candidate_limit = 12675`（2B 参考实现 `.c`/`.h` 已完整钉扎并现场复算 + tiny416 几何）；弃用值 4,096 已记录理由且禁止启用。
- **计划要求（未实测）**：阶段4 至少 1000 次有效推理形成基线；至少 50 次预定义交互观察、每类至少 10 次、基线成功率建议 ≥80%（阶段计划第 92 行）。不得写成已达成。
- 下一步：S4-B（PS 解码/NMS + UART 骨架 + 最小注入通路）按本契约实现并交付命令；S4-C（离线回放对拍）按 §6.1 范围执行；S4-D 板测按 §10 条件具备后执行。

## 12. 验收与自检

```bash
cd D:/codex-worktrees/w4
python -B scripts/stage4_s4a/verify_s4a_draft.py --evidence-dir report/evidence/S4-A/<run_id>
python -B scripts/stage4_s4a/mutate_verify_s4a_draft.py --evidence-dir report/evidence/S4-A/<run_id>
python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S4-A/<run_id>/delivery_manifest.json
```

自检退出码 0 表示：
1. 契约 JSON 可解析、必需键齐全（含 `g0_round_freeze`、`scope_freeze`、`candidate_limit_boundary_test`、`uart_plan_b_freeze`、`hardware_authorization_conditions`）；
2. §2 的全部带 SHA-256 上游绑定在本机现场复算一致（本轮 23 项），T25 分片计数与分片恢复清单一致（109 个 / 390,700,998 B）并逐片校验 SHA-256；声明 `NOT_AVAILABLE` 的条目必须真不可读（可读却标不可读判 FAIL）；
3. §3.2 与 §3.3 表格与 JSON 的字段集合**双向相等**、**无重复行**，且逐字段 `必填`/`2A 冻结` 标注一致；
4. §3.4 状态表的状态集合与 JSON `state_enum` 的**键集合严格相等**且恰为 5 个状态；
5. §4.4 的 `measurement_scope` 键集合与 JSON 严格相等；
6. 2A 冻结常量与**上游文件**一致（manifest `detection_postprocess`、`address_map.heads`、T29 `head_tensors`），且候选理论上界与 manifest 两头几何乘积及 2B 参考实现头文件宏 `S2A_T62_MAX_CANDIDATES` 一致；
7. `g0_round_freeze` 与人读文档一致：6 个冻结项 ID 齐备且锚点存在、2 个未冻结项为 `DRAFT_PENDING_APPROVAL` 且文档出现 `DRAFT_PENDING_APPROVAL`、方案 A 为 `CLOSED_FOR_THIS_ROUND`；
8. `scope_freeze` 恰含三种范围、各自允许/禁止结论非空且锚点存在；`candidate_limit_boundary_test` 的 12675/12676/`BAD_ARGUMENT`/禁用 4096 口径齐备；
9. 2B 事实对齐：文档必须出现回执 SHA、代码基线、最终提交、G4/G5、1000/108 与「正式冻结并释放硬件」「现场会话核验为准」；**不得**再出现旧快照语句；
10. 未批准值显式标注 `DRAFT_PENDING_APPROVAL`（**已知限制**：本项为结构/字符串检查，不能机器判定“某数值被写成了验收门槛”；该判定由 Reviewer 人工覆盖）。

**变异自证**（`scripts/stage4_s4a/mutate_verify_s4a_draft.py`）：在隔离沙箱副本上做定点变异，必须全部被检出（exit 1），未变异的阳性对照必须通过（exit 0）。至少覆盖：改动某条钉扎 SHA、删掉某个冻结项、把 `stale_age_limit` 写成已批准、删除候选边界 12676 锚点。

**不代表**阶段4 G0 的未决项批准、阶段4 验收或任何实物验收；也不代表 S4-B/S4-C 的实现正确。

## 13. 限制

- 本轮冻结的是阶段4 G0 基线与结论口径，不是阶段4 验收；无板上、无摄像头、无 HDMI、无 UART 实测，**本轮未执行任何硬件操作**。
- 上游资产只读；T25 分片未物化到本工作树（按只读绝对路径与分片恢复清单逐片复算）。
- 2A manifest（2026-09-23 快照）记录的 D2/D9/D6 SHA 与本工作树当前版本不同（`ea48281f`/`0be8e2dc`/`5ff91ffb` 对应 `6a3453d5`/`94dacdac`/`4dcf0f7d`）；本契约钉扎并现场复算当前树内版本，差异属上游文档快照滞后，若 2A 正式重新冻结须回归。
- 外部资产钉扎路径取自 2A manifest 声明路径；同 SHA 的同内容副本（cfg 3 份、weights 3 份、`calibration.list` 3 份）不改变身份。
- 2B 的释放只证明 2B 在其任务内释放；当前硬件归属以现场会话核验为准，本任务未核验、未连接、未争用任何硬件会话。
- 时间口径的时基常量（`COUNTS_PER_SECOND`）与跨域实测门控方法仍为 `DRAFT_PENDING_APPROVAL`；本轮只冻结端点定义。
- `inference_time` 窗口是 2A busy 窗口的近似，不声称与 `STATUS.busy` 门控逐周期等价；`TIMEOUT`/`ERROR` 下该字段取 0 哨兵。
- 候选缓冲上限 12,675 的推导依赖 2B 参考实现（`.c`/`.h` 已钉扎并复算）；若该实现变更必须重新推导并回归。
- 会引入候选截断的上限（如曾提出的 4,096）与 2A D9 及 2B 参考实现都不一致，已弃用并禁止启用。
- `stale_age_limit` 为 `DRAFT_PENDING_APPROVAL`，不构成验收指标，阶段5/6 不得当作已批准门槛。
- 方案 B 下阶段计划第 88 行的部分字段不由 UART 记录满足，只能由 PS 侧旁路日志方案满足（见 8.2）。
- 自检第 10 项为结构/字符串检查，不覆盖“数值是否被误写为门槛”的语义判定。
- 不声称与 Darknet C 后处理逐值相同（2A D9 已声明奇数补边半像素差异）。