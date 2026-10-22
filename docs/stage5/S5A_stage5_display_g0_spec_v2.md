# S5-A 阶段5 G0 定稿：HDMI 结果显示（离线准备 v2）

> 状态：`STAGE5_G0_FINALIZED_OFFLINE_NOT_ACCEPTED`。本文是**阶段5 离线准备**的 G0 定稿，把 w4 的 S4-D v1 草案（`73c3dad`，只读）收敛为可执行契约；**阶段5 尚未正式开工、未上板、未接摄像头、未做显示实测**，任何实测项一律 `NOT_RUN`。指标若需变更须交 Wong 决策（`AGENTS.md` 重大验收指标变更条款）。
>
> 机器可读权威：`docs/stage5/s5a_stage5_display_g0_fields.json`（契约身份 `S5A-G0-v2`）；唯一几何/口径来源：`verification/s5_display_geometry_reference.py`。两者与本文冲突时以 JSON + 参考实现为准并回改本文。

## 1. 定位、范围与上游绑定

- 覆盖：画面语义与结果年龄、叠框布局、补边逆映射、坐标误差门槛与测量口径、分数/置信度用词、FPS 与延迟的分别定义与起止事件、显示消费的阶段4 字段、用例集与状态、证据要求。
- 不覆盖：阶段5 成品指标（允许延迟成品值、P99、显示帧率下限——属阶段7/Wong）、阶段4 推理实现、阶段6 状态机（`docs/stage6/`）、阶段7 系统验收。
- 上游绑定（只读，出处与哈希见 `PROVENANCE_s4d_v1_baseline.md`）：阶段计划 L94–L100；S4-D v1 草案（`0b4f537d…`）；S4-A G0 草案（`3524d02a…`，`DRAFT_NOT_FROZEN`）；S4-B 离线链 `20261021_r13` PASS；S4-C 回放对拍 `s4c_replay_20261021_r05` PASS（109/109、mismatch 0、最大误差 0）；阶段3 STATE（颜色受阻、根因=硬件 DVP `cmos_d[9]` 无信号、未验收）。
- **Wong 已定决策**：①（2026-10-21 22:45）超出 `s2bu/1.1` payload 的结果/耗时/丢帧/过期/状态字段按**方案 B 只记 PS 侧**，扩展帧留待与 2B 协商；②画面语义固定为**最新结果叠加**（latest-result overlay，语义 B）。

## 2. 与 v1 草案的收敛点（本阶段的“定稿”动作）

| 编号 | v1 状态 | v2 定稿 | 依据 |
|---|---|---|---|
| C-01 | 语义 A/B/C 三选一，草案默认 B | **固定 B**（Wong 已定）；`display_semantics` 必须是产物清单字段 | Wong 决策；计划 L98 |
| C-02 | `age_result`/`age_frame` 定义 | 保留定义，明确 `age_frame = age_result + (t_result_publish − t_capture(frame_id))`；**两个年龄分别报告**；语义 B 下“端到端延迟”**只**能指 `age_frame` | 计划 L98；禁止伪称同帧 |
| C-03 | 过期门槛“与阶段4 同源” | **同源固定**：单一常量 `STALE_AGE_LIMIT_NS = 200 000 000`（200 ms）；阶段4 `stale` 与阶段5 判定共用同一数值与同一 PS 单调时基；判定为**严格大于**；`stale_effective = stale_flag OR age_frame > limit`，每结果**只计一次**并记录原因 | 计划 L100；S4-A §5.3 |
| C-04 | 布局为“草案建议值” | 固定**布局规则**（线宽 2、偶数线宽居中语义、标签锚点与翻转、安全区 16 px@1080p、多框/零框/过期规则）；颜色表与字号仍待正式 G0 | 计划 L100 |
| C-05 | 取整规则待定 | 固定 `round_half_up_to_nearest_pixel_index`（`floor(v+0.5)`），**只在最终落像素时取整一次**，中间量 float64 | 计划 L96；S5 v1 §3.2 约束 2 |
| C-06 | 逆映射两版写法之争 | 固定**端点对齐**（与 D2 冻结实现同源），v1 的像素中心对齐写法**废弃**（其对 1920 宽源在 `x_r=415` 处给 1915.38 px，偏离 3.62 px，超过门槛） | D2 `[D2 L9]`；已复算：端点对齐给 1919.00 px |
| C-07 | 显示像素层门槛“草案建议” | 保留数值（逆映射一致性 ≤1.0 px、绘制保真 ≤1 px + 线宽端点半像素 ±0.5 px、分数文本 ≤1e-3、离散字段全等）并标为 `G0_FIXED_OFFLINE` | 计划 L96 |
| C-08 | 分数/置信度规则 R1–R5 | 全部保留并机器化：字段名 `score`；禁止用词清单；任何二次变换必须写明变换式 | 计划 L96 |
| C-09 | FPS/延迟“候选事件集” | 固定起止事件（§6）与“分母必须可由帧级事件日志复算”的硬约束 | 计划 L98/L100 |
| C-10 | 显示消费阶段4 字段 | 明确**消费 PS 侧记录**（方案 B），逐字段列白名单，禁止自行反算第二份坐标（除显式兜底） | Wong 决策 A/B；计划 L88 |

## 3. 叠框布局（定稿规则）

- 类别顺序固定 `fist, palm, one, two_up, three`（不得重排）；颜色表按此顺序，具体色值待正式 G0。
- 边框线宽 2 px（1080p 参考），其他分辨率按同一相对规则缩放；**偶数线宽居中**：几何线像素索引 `p` 占 `{p−1, p}`，逐边钳到画布内（由 `border_pixel_sets` 唯一实现）。
- 标签内容 `类别 + 分数`（如 `fist 0.83`，2 位小数）；锚点在框左上外侧，越界翻转到框内左上，仍越界则钳入安全区（16 px@1080p）。
- 多框：按 2A 稳定同分顺序（head → row-major cell → anchor-local → class_id）输出，≤15 框，**不得重排、不得因遮挡丢弃**。
- 零框（`NO_HAND`）：不绘制任何框，HUD `boxes=0` 与当前 `frame_id`；零框是合法结果，**不得**与过期/丢失混淆，不计入过期清除。
- 过期结果：不绘制框，HUD `stale_cleared` 计数 +1。
- 非方形视频：按实际几何显示，不得拉伸；画布尺寸不同时用**整数倍**等比缩放居中（k≥1，`canvas_fit`）并留黑边。
- HUD 13 字段：`capture_fps / inference_fps / display_fps / inference_time_ns / age_result_ns / age_frame_ns / frame_id / boxes / stale_cleared / dropped_frames / timeouts / warmup_state / display_semantics`，逐项命名与 §6 一致，不隐藏任何计数。

## 4. 补边逆映射与坐标误差门槛

- **正向几何**：D2/2A 冻结（整数截断 resize + 左上 floor padding + 端点对齐双线性），实现为 `letterbox_geometry`，并与 `verification/s1_t02_d2_numeric_reference.py::letterbox_geometry` 逐值对拍（S5-A 自检已 PASS）。
- **逆映射**（`network_norm_to_original_norm`）：`x_r = u·dst_w − off_x`；`x_px = x_r · (src_w−1)/(new_w−1)`；`u_orig = x_px/(src_w−1)`。中间量 float64，禁止提前取整。
- **退化几何（同一守卫覆盖正反两向）**：`new_w<=1` / `new_h<=1`（端点对齐映射不适用）或源尺寸 `src_w<=1` / `src_h<=1`（无有效采样点）时，一律抛 `DegenerateGeometryError`，**必须改用阶段4 原图坐标字段**；`original_norm_to_network_norm`（正向，自检用）与 `network_norm_to_original_norm`（逆向）共用同一 `_check_geom` 守卫，任一侧都不得出现 `ZeroDivisionError` 或“静默映射到原点”的行为。
- **奇数总补边**：`(dst_w−new_w)` 或 `(dst_h−new_h)` 为奇数时保留 1 px 非对称补边差（例：683×384 → `new=416×233`、`off_y=91`、下侧 92），禁止对称化/ceil/重新居中。
- **单一来源**：显示层必须与冻结实现同源；禁止在显示代码里重写第二套 resize/逆映射；阶段4 已给出 `xyxy` 时**只允许**使用该字段。
- **门槛**：A 数值链路沿用 2A（score/xyxy 绝对误差 ≤1e-6、相对容限 0、离散字段全等，不得放宽）；B 显示像素层（逆映射 vs float64 参考 ≤1.0 px、绘制保真 ≤1 px + 线宽 ±0.5 px、分数文本 ≤1e-3、零面积不绘制）。门槛只有在证据中声明参考实现版本与哈希后才有意义。

## 5. 分数 vs 置信度（用词规则，机器校验）

- `score = sigmoid(objectness)·sigmoid(class)`（PS 在 float64 上计算，输入为 PL 的 INT8 原始 logits）。
- 一律称**分数（score）**；禁止「置信度 / confidence / probability / 可信度 / 准确率」作为 score 的称谓，除非同处写出 sigmoid 转换式依据并声明“未做概率校准，不表示可靠概率”。
- D6 评估产物字段 `confidence ≡ score`；复用时必须显式声明等价并绑定公式，**禁止各自统计**。
- 阈值与常量：`score ≥ 0.25`（含等号）、NMS IoU 0.45、≤15 框、类别顺序如上；显示层不得引入第二套阈值。
- 显示层对 score 的任何二次变换（百分号、截位、颜色分档）必须在 HUD 或文档写明变换式，否则只显示原始分数。

## 6. FPS 与延迟：分别定义、起止事件（计划 L98/L100）

| 量 | 起事件 | 止事件 | 口径要求 |
|---|---|---|---|
| 采集 FPS | 采集侧该帧首个有效像素写入帧缓冲 | 下一帧同一事件 | `(N−1)/(t_last−t_first)`；声明整段平均或滑动窗口；区分接收帧数与有效帧数 |
| PL 推理耗时 `t_pl` | CSR 接受有效 `start` 上升沿 | PL 完成（`operator_result_valid` 且 `error_code=0`） | 不含 PS 预处理/解码/NMS/UART/排队/显示 |
| PS 结果耗时 `t_result` | 同一次 `start` 接受时刻 | 结果记录发布（字段集齐） | 含解码/NMS |
| 推理 FPS | — | — | “已完成并发布结果的帧数 / 观测时长”；**必须声明**是否剔除超时/丢帧；建议同时给“全部接收帧”“有效完成帧”两版分母 |
| 显示 FPS | 输出帧起始 | 下一输出帧起始 | 与采集/推理/叠加更新率分列 |
| `age_result_ns` | `t_result_publish` | `t_overlay_commit` | 待显示结果的陈旧度 |
| `age_frame_ns` | `t_capture(frame_id)` | `t_overlay_commit` | 语义 B 下唯一可称“端到端延迟”的量，且必须说明它不是同帧往返 |

- 所有时间同一 PS 单调时钟；事件必须写**帧级事件日志**（`frame_id`、事件类型、时间戳），任何统计量可由日志复算，否则不得进入报告；分位数必须给样本数。
- 预热、采集丢帧、推理丢帧/跳过、过期清除、超时**均不得隐藏**：分别计数 + 清单；超时不计入有效完成帧、不重试覆盖。
- 阶段7 才冻结吞吐下限与端到端 P99；本文不承诺任何 FPS/延迟数值。

## 7. 显示消费的阶段4 记录（方案 B）

- 必需字段：`frame_id`、`geometry`、`state`、`detection_count`、`detections[]`（`class_id`/`class_name`/`score`/`xyxy`/`source_order`）、`stale`、`dropped_frames`、`capture_time_ns`、`result_time_ns`、`inference_time_ns`、`end_to_end_latency_ns`、`error_code`；消费前用 `validate_result_record` 校验。
- `xyxy` 语义：**归一化原图坐标**（含补边逆映射、裁剪到 [0,1]、正面积）。显示层只允许使用该字段，不得自行反算第二份坐标；§4 逆式仅是阶段4 缺失该字段时的兜底（是否启用待阶段4 G0）。
- `capture_time_ns / result_time_ns / inference_time_ns / end_to_end_latency_ns / stale / dropped_frames` 属**只记 PS 侧**字段（方案 B）：不进 UART；显示层消费 PS 侧记录，**不得**声称这些来自 UART，也不得据此宣称满足计划第 88 行的“每条结果包含…采集与结果时间、推理耗时和状态”。
- 结果—帧号对应：每条结果与每张显示帧都携带 `frame_id`，形成五元组 `(displayed_frame_id, result_frame_id, age_result_ns, age_frame_ns, display_semantics)`；语义 B 下不要求相等，但必须如实记录，禁止改写 `frame_id`、禁止伪称同帧。

## 8. 用例集与状态（本轮离线 vs 未执行）

| 编号 | 用例 | 本轮状态 |
|---|---|---|
| T5-01 | 非方形视频（1280×720 / 720×1280 / 683×384） | 离线渲染 + 几何逐值断言（S5-B） |
| T5-02 | 边缘框/四角/部分越界/裁剪后零面积 | 离线渲染 + 断言（S5-B） |
| T5-03 | 多框（15）与零框（NO_HAND） | 离线渲染 + 断言（S5-B） |
| T5-04 | 过期清除（==limit 不过期 / limit+1 过期 / stale 标志） | 离线渲染 + 断言（S5-B） |
| T5-05 | 结果—帧号对应（≥100 帧） | 五元组日志断言（S5-B 合成序列；S5-C 109 样本） |
| T5-06 | 分数/置信度用词 | 产物文本扫描（S5-B）+ 字段名检查（S5-C） |
| T5-07 | 奇数补边半像素（683×384） | 几何断言（S5-A 自检 + S5-B） |
| T5-08 | FPS/延迟口径 | 仅口径与可复算性（离线事件日志）；真实统计 `NOT_RUN` |
| T5-09 | 连续 30 分钟无死锁 | `NOT_RUN`（需阶段3 完成 + 阶段4 跑通 + 硬件） |
| T5-10 | 回归阶段4 数值链路 | 109 样本离线勾连（S5-C） |
| T5-11 | 预热/丢帧/超时不隐藏 | HUD/日志字段与计数口径断言；真实注入 `NOT_RUN` |
| T5-12 | 显示语义一致性 | 单包内 `display_semantics` 唯一性断言（S5-B/C） |

## 9. 证据要求

- 目录 `report/evidence/<task_id>/<run_id>/`；机器可读清单必须绑定：源码基线（本树 HEAD）、实际源码文件哈希、上游只读输入路径 + SHA256、适用接口版本（`S5A-G0-v2`）、命令与**真实退出码**、统计（样本数/种子/最大误差）、限制、未执行项。
- 必须保留：PNG 渲染结果、逐用例/逐样本 JSON、帧级事件日志、逆映射参考实现绑定、逐值比较结果、过期清除与丢帧清单、失败与反例证据（不因失败而删除）。
- 每项测试分别标 `PASS/FAIL/BLOCKED/NOT_RUN/NOT_APPLICABLE`；不适用须写理由；禁止用“平均”“看起来对齐”替代逐值比较。
- 阶段5 证据不得以阶段4/阶段6 证据替代；显示层证据必须含显示侧原始产物。

## 10. 未决项与风险

- 待正式 G0/Wong：成品允许延迟上限、颜色表与字号、阶段4 `stale_age_limit` 的正式冻结（本契约已按同源常量 200 ms 使用，**阶段4 侧仍是 DRAFT_PROPOSED**）。
- 接口扩展（选项 A 新增扩展帧）仍需与 2B 协商；本树不得改 2B 正文，也不得改 `s2bu/1.1`。
- 显示实测依赖：阶段3 颜色验收通过（当前受阻，根因=硬件）、阶段4 正式联调跑通、2B 让出 JTAG/COM4 与 `hw_server`。
- 风险：S5 v1 的像素中心对齐写法若被误用会引入 3.62 px 偏差（已废弃并用自检钉住）；阶段4 契约未冻结，其字段名若变更将影响 S5-B/S5-C，需回归。

## 11. 覆盖矩阵（计划条目 → 本文 ↔ 机器可读）

| 计划条目 | 要求 | 位置 |
|---|---|---|
| L96 | 原始画面＋框/类别/分数/FPS/延迟 | §3、§6 |
| L96 | 逆映射、非方形、边缘框、多框、零框、过期清除 | §4、§8（T5-01…04/07） |
| L96 | 坐标误差门槛在阶段1/G0 冻结 | §4（门槛 A/B） |
| L96 | logits/整数分数显示为「分数」；概率转换明确后才称置信度；不把数值大等同可靠概率 | §5 |
| L98 | 结果关联帧号；延迟/最新结果叠加须明确语义与年龄；不能伪称同帧 | §2、§7 |
| L98 | FPS 分别说明采集/推理/显示；预热/丢帧/超时不隐藏 | §6 |
| L100 | G0 确定布局、测量起止事件、允许延迟 | §3、§6、§10 |
| L100 | ≥100 帧结果对应；30 分钟无死锁；回归阶段4 数值链路；截图/视频与原始统计留证 | §8（T5-05/09/10）、§9 |

- 机器可读版本：`docs/stage5/s5a_stage5_display_g0_fields.json`（含 test_cases/unfrozen_and_unexecuted/reference_implementation）；自检与对拍见 `report/evidence/S5-A/`。