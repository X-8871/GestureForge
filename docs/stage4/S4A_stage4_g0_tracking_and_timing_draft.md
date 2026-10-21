# S4-A 阶段4 G0 草案：结果记录、时间口径与异常记录口径

状态：`DRAFT_NOT_FROZEN`（2026-10-21，UTC+8）。任务编号 `S4-A`。修订 `r04`。
- `r02`：按 rev-spec 第 1 轮独立审查（CHANGES_REQUIRED）修复 F4–F13。
- `r03`：按 dev-ps 实现反馈裁决 `candidate_count` 口径，与 2B 冻结实现及 2A T29 黄金对齐。
- `r04`：按 rev-spec 第 2 轮阻断修复 TIMEOUT 的 `inference_time_ns` 口径与 `state_enum` 混入非状态键；并按建议补齐重复行检测、`frame_id` 回绕与 `stale` 措辞。

机器可读契约（权威字段名）：[`s4a_stage4_g0_fields.json`](s4a_stage4_g0_fields.json)。
本文件是阶段4 的**离线准备草案**，不是阶段4 G0 冻结、不是阶段4 验收，不产生板上、摄像头、HDMI 或 UART 实测结论。

## 1. 范围与边界

- 覆盖：阶段4 一条推理结果的字段与 `frame_id` 语义、推理耗时与端到端延迟的分别定义、丢帧/候选框超限/过期结果的显式记录口径、无手=零框、非结果状态的取值规则、沿用 2A 的解码与阈值常量。
- 不覆盖：真实摄像头联调、上板、烧录、HDMI 显示（阶段5）、交互控制（阶段6）、CNN 重训。
- 不改动：2A 冻结规格与阈值、2B `s2b-physical/1.0.0`／`s2bu/1.1` 接口正文。
- 上游一律只读引用，绑定见第 2 节。

## 2. 上游冻结绑定（真实 SHA-256）

| 绑定 | 路径 | SHA-256 | 状态 |
|---|---|---|---|
| 2A G0 规格 | `docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md` | `7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230` | `G0_FROZEN` |
| tiny416 机器清单 | `report/evidence/S2A-T01/tiny416_model_manifest.json` | `9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a` | `G0_FROZEN` |
| 109 固定样本清单 | `report/evidence/S2A-T01/fixed_test_samples.json` | `ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed` | `G0_FROZEN` |
| 逐层 CPU 黄金索引 | `report/evidence/S2A-T25/cpu_layer_golden_index.json` | `cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d` | `COMPLETE` |
| T25 分片恢复清单 | `report/evidence/S2A-T25/t25_shard_recovery_manifest_20261002.json` | `5352b2ef6edb8f40bb1e635aaa1337556171937db176db841fb044406657d0d9` | `RECOVERY_MANIFEST` |
| 逐样本层流分片 | `report/evidence/S2A-T25/tensors/sample_000..108.zlib`（109 个，390,700,998 B） | 逐片 SHA-256 见分片恢复清单 | 只读引用（未物化到本工作树） |
| CPU D9 解码参考 | `report/evidence/S2A-T29/cpu_decode_nms_reference.json` | `24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231` | `CPU_REFERENCE_GENERATED` |
| D9 解码实现 | `verification/s1_t02_d9_yolo_decode.py` | `94dacdac18968e70871e1c21d24d5f4c3a9941881eaf37ffaab4d5372e28d190` | 2A 冻结语义 |
| D9 依赖指标库 | `verification/s1_t02_d6_detection_metrics.py` | `4dcf0f7d9586b7096be015faf2c5037489b03b04baeec0daea4cadec89be591a` | 2A 冻结语义 |
| 2B UART 运输接口 | `w2b/docs/obsidian-project/02-方案设计/s2b_board_transport.md` | 由 2B 总控维护，本阶段不冻结其哈希 | `s2bu/1.1`，仅接口定义冻结 |
| 2B PS 解码 C 参考 | `w2b/verification/s2a_ps_decode_nms_reference.c` | 由 2B 总控维护 | `candidate_count` 口径的事实来源 |
| 2B PS/PL 物理接口 | `w2b/docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md` | 同上 | `s2b-physical/1.0.0`，仅接口定义冻结 |

注意：2B 仅冻结“接口定义与受控实验规程”，**2B 尚未最终验收**。若上述 2B 正文或 C 参考实现变更，本草案的 UART 映射与 `candidate_count` 口径需做适用回归。带 SHA-256 的绑定共 **8 项**（其余 3 项由对方维护、1 项为目录），另有 T25 分片计数 1 项。

## 3. 阶段4 结果记录

### 3.1 `frame_id`

- `frame_id` 是 `uint32` **不透明值**：PS 在 idle 写 `FRAME_ID`，PL 接受 `start` 时锁存并随 `done` 原样回传；PL 不解释该值（2A 冻结语义）。
- 同一帧的采集侧与结果侧必须使用同一 `frame_id`；结果记录不得重编号、不得把它当序号使用。
- 结果序号由新增的 `result_seq` 承担（PS 本地单调递增，从 1 起）。
- 采集侧连续分配与回绕约定、以及与丢帧判定的依赖关系见 5.1。

### 3.2 结果字段（与 JSON `result_record.fields` 一一对应）

标注含义：`必填` = 该字段在任何结果记录中都必须出现（可以有缺值哨兵，但不得省略字段）；`2A 冻结` = 该字段或其对应量已由 2A 冻结对象定义，阶段4 不得重新定义。边界情况（`geometry`、`detection_count`、`candidate_count`）的判定依据见 JSON `field_annotation_definitions.boundary_cases_of_frozen_by_2a`。

| 字段 | 类型 | 必填 | 2A 冻结 | 语义 |
|---|---|---|---|---|
| `frame_id` | u32 | 是 | 是 | 见 3.1；对 PL 不透明，连续分配与回绕是 PS 侧约定（见 5.1） |
| `result_seq` | u32 | 是 | 否 | PS 结果记录序号，本地单调递增，拒绝回绕到 `0xFFFFFFFF`；与 s2bu 运输 sequence 不同 |
| `geometry` | `{width:u32, height:u32}` | 是 | 是 | 原图尺寸（顺序固定 width,height），是补边逆映射唯一基准 |
| `state` | enum | 是 | 否 | 只能取 3.4 的 5 个状态之一 |
| `detection_count` | u32 | 是 | 否 | 恒等于 `detections` 长度；失败与无手必须为 0；≤15；取值受 2A 第 75 行“检测数必须完全相同”约束 |
| `detections` | array | 是 | 是 | 阈值+稳定排序截断+类别内 NMS 之后的框，顺序即 D9 输出顺序；无结果状态必须为空数组 |
| `candidate_count` | u32 | 是 | 否 | **阈值筛除后、NMS 前**的候选数，与 T29 `raw_candidate_count_before_stable_nms` 及 2B 冻结实现同口径（见 7.2） |
| `candidate_count_pre_threshold` | u32 | 否 | 否 | 可选诊断：阈值筛除前的候选机会数（正面积候选框数 × 5 类）；不进 UART、不参与对拍 |
| `candidate_overflow` | bool | 是 | 否 | 候选数超候选缓冲上限并已截断，必须显式记录；tiny416 固定配置下恒为 false（见 5.2） |
| `capture_time_ns` | u64 | 是 | 否 | 该帧第一个有效像素（或等价帧起始事件）时刻；无观测为 0 哨兵 |
| `result_time_ns` | u64 | 是 | 否 | 解码/NMS 完成、结果可发布（可开始 UART 发送）时刻；无结果为 0 哨兵 |
| `inference_time_ns` | u64 | 是 | 否 | PL 任务窗口耗时，见 4.1；**不得**冒充端到端延迟；超时/错误取 0 哨兵 |
| `end_to_end_latency_ns` | u64 | 是 | 否 | 见 4.2；仅两端均为真实观测时有定义，否则 0 哨兵（不得为负、不得沿用上一帧） |
| `dropped_frames` | u32 | 是 | 否 | 相对上一结果丢失的帧数，见 5.1 |
| `stale` | bool | 是 | 否 | 结果年龄超上限，见 5.3；仅对 `OK`/`NO_HAND` 定义，其余状态恒 false |
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
| `ERROR` | 其他 PL/memory/协议/数值错误（`error_code∉{0,5}`） | 0（框无效） |
| `DROPPED` | 采集侧存在该帧但未产生结果 | 0 |

`state` 只能取以上 5 个值；非 `OK`/`NO_HAND` 状态下其余必填字段的取值规则见 5.5（与 JSON `result_record.absent_value_policy` 一致）。

## 4. 时间口径

### 4.1 推理耗时 `inference_time_ns`

- 起点：CSR 接受有效 `start` 的上升沿（PL `busy=1`、取得 buffer 所有权）。
- 终点（成功）：`operator_result_valid` 单周期脉冲且 `operator_error_code=0`（PL 提交 `done`）。
- **超时没有成功终点**：2A 规格第 65 行规定超时在第 N 个后续上升沿中止任务（`timeout=1` 恰给一个完整执行周期），此时不会出现 `operator_result_valid` 且 `code=0`。因此本合同**不为 `TIMEOUT` 定义 `inference_time_ns` 数值**，取 0 哨兵；实现若按 `STATUS.busy` 门控观测到中止沿耗时，只能作为实现侧诊断值单独记录，不得写入本字段。
- **错误完成事件存在**（2A 规格第 67 行：非零 `operator_error_code` 随单周期 valid 脉冲给出且错误码同沿稳定），但本合同同样不为 `ERROR` 定义该字段的数值口径，缺省 0 哨兵。
- 包含：PL 内部算子计算、PL 对 memory 的 feature/head 读写与停顿周期。
- 不含：PS 预处理/量化、输入与权重装载、PS 解码/NMS、UART 发送、结果排队与显示。
- **本窗口是 2A CSR busy 窗口的近似**：2A 规格第 46 行规定 `busy` 要写完两头与 `FRAME_ID` 才清，而本终点取 `operator_result_valid=0`（第 67 行）。若按 `STATUS.busy` 门控实测，实测窗口可能略宽；本草案**不声称两者逐周期等价**，实测门控方法待 G0 冻结。

### 4.2 端到端延迟 `end_to_end_latency_ns`

- 起点：`capture_time_ns`（该帧第一个有效像素或等价帧起始事件）。
- 终点：`result_time_ns`（该 frame 解码/NMS 完成、结果可发布）。
- 包含：采集 → 缩放/补边/颜色/量化预处理 → 输入搬运 → PL 推理（含 `inference_time`）→ PS 解码/NMS → 结果排队。
- 不含：UART 传输完成之后的显示延迟（属阶段5 口径）。
- 强制规则：两者必须分别测量、分别报告；**不得用推理耗时冒充端到端延迟**；两者必须处于同一 PS 单调时基。
- 定义域：仅当 `capture_time_ns` 与 `result_time_ns` 均为真实观测值（`state ∈ {OK, NO_HAND}`）时有定义；否则取 0 哨兵。

### 4.3 时基与 FPS

- 时基：PS 侧同一单调计数器（建议 CPU 全局定时器，频率与 `COUNTS_PER_SECOND` 需在 G0 冻结）；PL 窗口端点由 PS 侧门控观测，跨域测量方法待 G0 冻结。
- 离线准备期无 PL 硬件时，时间字段取 0 哨兵并必须以 `measurement_scope` 显式标注 `NOT_EXECUTED_OFFLINE`，不得把 0 当作实测耗时。
- FPS 分别定义：采集 FPS、推理 FPS、显示 FPS（阶段5）不得互相替代；预热、丢帧、超时不得隐藏。

## 5. 异常与边界记录口径

### 5.1 丢帧与 `frame_id` 连续分配

- 分配约定：同一会话内，PS 采集侧对每个被采集/入队的帧按 `+1` 递增分配 `frame_id`（从 1 起）；离线回放沿用 2A 固定样本的 `frame_id` 0..108。
- 该连续性是 **PS/运输侧约定**（`s2bu/1.1` 第 49 行“响应 frame 为请求 frame+index”），不是 PL 语义；PL 侧仍视之为任意 u32。
- 回绕：与 `result_seq` 同一约定，**拒绝回绕**；`frame_id` 达到 `0xFFFFFFFE` 后不得自然溢出到 0，必须开启新会话或显式复位计数。离线回放固定使用 0..108，不涉及回绕。
- 丢帧判定：同一 `frame_id` 序列中不连续即计为丢帧；`dropped_frames` = 本结果相对上一已发布结果的缺失帧数。
- **互斥规则（避免双计）**：若某缺失帧已单独发布一条 `state=DROPPED` 记录，则该帧**不再计入**后续结果的 `dropped_frames`。`dropped_frames` 只统计既无结果、也无 DROPPED 记录的缺失帧，保证每个缺失帧恰好被计数一次。
- 缺帧不得静默跳过：PS 若知道该帧存在，必须补一条 `state=DROPPED` 记录；仅当完全无采集事实时才只累计 `dropped_frames`。
- 若采集源本身会跳号（非连续分配），必须显式声明实际分配规则，否则丢帧统计无效。

### 5.2 候选框超限

- 候选缓冲上限 `candidate_limit = 12675`，由 2B 冻结候选缓冲上限与 tiny416 几何共同决定：两头 `(13×13 + 26×26) × 3 anchors × 5 classes = 12,675`，即阈值后可产生的候选上界。
- `candidate_count`（或 `candidate_count_pre_threshold`）超过该上限时 `candidate_overflow=true`，并先按分数稳定排序截断到上限，再执行类别内 NMS。
- 因此**在 tiny416 固定配置下 `candidate_overflow` 恒为 false**；此时必须显式记录“未超限”这一事实（字段保留、值为 false），不得因恒假而省略字段或省略记录口径。
- 曾提出的 `candidate_limit = 4096` 属 **弃用的草案值**：它低于理论最大候选数，会引入 2A D9 中不存在的候选截断，破坏与 T29 黄金的逐框等价。
- 区分：`candidate_limit`（12,675）是候选缓冲上限；`max_outputs_per_image=15` 是 NMS 之后的输出上限（2A 冻结）。两者不得混用。

### 5.3 过期结果

- `stale=true` 当结果年龄超过 `stale_age_limit`；结果年龄 = 发布时刻 − `result_time_ns`。
- 发布时刻定义：该结果记录被提交给发布层（开始 UART 发送或交给显示层）的时刻，与其余时间字段同一 PS 单调时基。
- **定义域**：`stale` 与 `state` 独立判定，但仅对 `state ∈ {OK, NO_HAND}` 定义；`TIMEOUT`/`ERROR`/`DROPPED` 恒为 `false`（这些状态无 `result_time_ns`，年龄无定义）。
- stale 结果仍保留原记录与框；显示层必须显式声明结果年龄，不得伪称同帧。
- `stale_age_limit = 200 ms` 为 **DRAFT_PROPOSED**（未冻结）。

### 5.4 无手与其他边界

- 无手 = 零框：`state=NO_HAND`、`detection_count=0`、`error_code=0`；**时间字段仍为真实观测值**；不是错误，不计入丢帧。
- 每图 ≤15 框为 2A 冻结值；放宽即属规格变更，必须回退 G0 决策。

### 5.5 非结果状态的取值与缺值哨兵

- 所有 `required` 字段在每条记录中都必须出现；无结果时用哨兵值填充，**不得省略字段、不得沿用上一帧的值、不得出现负数或时间倒流**。
- `0` 的含义是“未观测/不适用”，不是 1970 时刻、也不是合法耗时；读取方必须先按 `state` 判别。
- 逐状态取值（与 JSON `result_record.absent_value_policy.by_state` 一致）：

| 状态 | capture_time_ns | result_time_ns | inference_time_ns | end_to_end_latency_ns | candidate 字段 | stale | error_code |
|---|---|---|---|---|---|---|---|
| `OK` / `NO_HAND` | 真实值 | 真实值 | 真实实测（大于 0） | `result_time − capture_time`（大于 0） | 真实候选数与溢出标志 | 按 5.3 计算 | 0 |
| `TIMEOUT` | 真实值 | 0 | 0 哨兵（无完成沿，见 4.1） | 0 | 已观测值，未观测为 0 | false | 5 |
| `ERROR` | 真实值 | 0 | 0 哨兵（本合同不定义口径，见 4.1） | 0 | 已观测值，未观测为 0 | false | 非 0 且非 5 |
| `DROPPED` | 已知则真实值，否则 0 | 0 | 0 | 0 | 0 与 false | false | 0 |

- `DROPPED` 记录本身的 `dropped_frames` 按 5.1 的互斥规则处理（该帧不被重复计入后续结果）。

## 6. 沿用 2A 的冻结常量

以下常量由上游 `tiny416_model_manifest.json` 的 `detection_postprocess` / `address_map.heads` 与 2A 规格决定；自检脚本必须从上游文件读取并比对，不得只与本契约的副本比对。

| 项 | 值 |
|---|---|
| 模型/输入 | tiny416，RGB 416×416 CHW INT8 |
| 类别顺序 | `fist=0, palm=1, one=2, two_up=3, three=4` |
| `score_threshold` | `0.25`，判定为 `score >= 0.25`（含等号） |
| NMS | 类别内 greedy `IoU=0.45`，跨类别不抑制 |
| 每图输出上限 | 15（NMS 之后） |
| 候选理论上界 | 12,675（`(13×13+26×26) × 3 anchors × 5 classes`） |
| 分数定义 | `sigmoid(objectness)*sigmoid(class)` |
| 坐标策略 | D2 整数截断 resize + 左上 floor padding；裁剪到 `[0,1]`；零面积丢弃 |
| 稳定 tie 顺序 | head 顺序 → row-major cell → anchor-local → class_id |
| 检测头 | `[1,30,13,13]` length_bytes 5,070 scale `0.24267549589862975`；`[1,30,26,26]` length_bytes 20,280 scale `0.30223452951025775` |
| 对拍容限 | 离散字段必须完全相同；`score` 与 `xyxy` 各分量绝对误差 ≤`1e-6`；相对容限 0（规格第 75 行） |

## 7. 与 `s2bu/1.1` 的映射与未决接口决策

### 7.1 字段覆盖

| 阶段4 字段 | `s2bu/1.1` |
|---|---|
| `frame_id`、`geometry` | 40 B 头 `<4sHH8I>` 的 frame_id / width / height |
| `detection_count` | 响应元数据 `box_count` |
| `detections` | 每框 48 B `<ii5d>`（class_id、source_order、score、x1..y2） |
| `candidate_count` | 响应元数据 `raw_candidate_count`（同口径，见 7.2） |
| `candidate_count_pre_threshold` | 无（诊断字段，不进 UART） |
| `error_code` | 响应元数据 `ERROR_CODE` |
| `result_seq` | 无对应字段（运输 `sequence` 是请求/响应配对序号，不是结果序号） |

### 7.2 未定义语义与缺失字段

- `raw_candidate_count` 语义：`s2bu/1.1` **正文未写明统计口径**；但 2B G0 冻结实现（`w2b/verification/s2a_ps_decode_nms_reference.c`）与 2A T29 黄金（`samples[i].raw_candidate_count_before_stable_nms`）实际都是**阈值筛除后、NMS 前**的计数。阶段4 的 `candidate_count` 采用完全相同口径，以保证可与 T29 黄金逐样本比对，并因此与 UART 字段可直接对齐。**若 2B 后续把该字段正式冻结为其他口径（阈值前或 NMS 后），必须回归本契约、S4-B 骨架与 S4-C 对拍口径**。
- 缺失字段：`s2bu/1.1` 现有 payload 没有 `candidate_overflow`、`capture_time`、`result_time`、`inference_time`、`end_to_end_latency`、`dropped_frames`、`stale` 与显式 `state`；而该接口正文只能由 2B 总控修改。因此：
  - 选项 A：阶段4 G0 决定后新增扩展（新 op 或 TLV 尾块），不改 `s2bu/1.1` 既有字段语义 —— 属重大接口语义变化，需 Wong/项目总控决策并协调 2B。
  - 选项 B（**离线准备期临时默认**）：UART 只传 `s2bu/1.1` 既有字段；时间/丢帧/过期/状态字段在 PS 侧记录，不改任何接口正文。
- **选项 B 的后果（必须显式承认）**：选项 B 下 `capture_time_ns`/`result_time_ns`/`inference_time_ns`/`end_to_end_latency_ns`/`stale`/`dropped_frames` 不会出现在 UART 记录中；主机侧只能自行记录接收时刻并推导部分状态，**拿不到 PS 侧的真实采集/结果/推理耗时**。因此**不得据选项 B 宣称满足阶段计划第 88 行**“每条结果包含…采集与结果时间、推理耗时和状态”；该满足只能来自选项 A 的 G0 决策，或一个明确的 PS 侧日志证据方案（其证据落点与采集方式需在 G0 声明）。
- 状态：`OPEN_AWAITING_DECISION`。准备阶段按选项 B 推进，不因此停滞。

## 8. 未冻结项与下一步

- 未冻结：`stale_age_limit`、时基/跨域测量方法、选项 A/B 的帧格式扩展。
- 已由上游推导（不再属未冻结草案）：`candidate_limit = 12675`（2B 冻结候选缓冲上限 + tiny416 几何）；弃用值 4,096 已记录理由。
- 计划要求（尚未实测）：阶段4 至少 1000 次有效推理形成基线；至少 50 次预定义交互观察、每类至少 10 次、基线成功率建议 ≥80%（阶段计划第 92 行）。不得写成已达成。
- 下一步：S4-B（PS 解码/NMS + UART 骨架）、S4-C（离线回放对拍）按本契约实现；S4-D 细化阶段5/6 口径。

## 9. 验收与自检

```bash
cd D:/codex-worktrees/w4
python -B scripts/stage4_s4a/verify_s4a_draft.py --evidence-dir report/evidence/S4-A/<run_id>
```

自检退出码 0 表示：
1. 契约 JSON 可解析、必需键齐全；
2. 上游带 SHA 的绑定（当前 8 项）在本机复算一致，且 T25 分片计数与分片恢复清单一致（109 个 / 390,700,998 B）并逐片校验 SHA-256；
3. §3.2 与 §3.3 表格与 JSON 的字段集合**双向相等**、**无重复行**，且逐字段 `必填`/`2A 冻结` 标注一致；
4. §3.4 状态表的状态集合与 JSON `state_enum` 的**键集合严格相等**且恰为 5 个状态（枚举中混入非状态键会被判 FAIL）；
5. 2A 冻结常量与**上游文件**（manifest `detection_postprocess`、`address_map.heads`、T29 `head_tensors`）一致；
6. 草案未冻结值显式标注 `DRAFT_PROPOSED`（**已知限制**：本项为子串存在性检查，不能机器判定“某数值被写成了验收门槛”；该判定由 Reviewer 人工覆盖）。

**不代表**阶段4 G0 冻结或任何实物验收；也不代表 S4-B/S4-C 的实现正确。

## 10. 限制

- 草案未冻结、未验收；无板上、无摄像头、无 HDMI、无 UART 实测。
- 上游资产只读；T25 分片未物化到本工作树（只读绝对路径引用）。
- 时间口径的时基与跨域测量方法待 G0 冻结；本草案只给端点定义。
- `inference_time` 窗口是 2A busy 窗口的近似，不声称与 `STATUS.busy` 门控逐周期等价；`TIMEOUT`/`ERROR` 下该字段取 0 哨兵，超时/错误窗口的诊断值不由本合同定义。
- 会引入截断的候选上限（如曾提出的 4,096）会破坏与 2A D9 的逐框等价，已弃用；当前 `candidate_limit=12675` 使 `candidate_overflow` 在 tiny416 固定配置下恒为 false。
- `stale_age_limit` 为 DRAFT_PROPOSED，不构成验收指标。
- 选项 B 下阶段计划第 88 行的部分字段不由 UART 记录满足（见 7.2）。
- 自检第 6 项为子串检查，不覆盖“数值是否被误写为门槛”的语义判定。
- 不声称与 Darknet C 后处理逐值相同（2A D9 已声明奇数补边半像素差异）。