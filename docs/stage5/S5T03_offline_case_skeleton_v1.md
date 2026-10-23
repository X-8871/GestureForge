# S5-T03 离线用例骨架规格（v3，2026-10-24）

> 状态：**离线骨架**，不是阶段5 验收、不是板上结论。冻结参数权威：`docs/stage5/s5t03_offline_skeleton_params_v1.json`
> （`FROZEN_BEFORE_RUN_REVISED_20261024`，种子与样本数先于运行冻结）。实现：`scripts/stage5_t03/**`。
> **v3（复审后修 NB-1..NB-5）**：等价 `frame_id` 改 fail-closed 并新增计数 `duplicate_frame_id_results`（NB-1）；
> 漂移登记改为扫描判据（NB-2）；计数单位改为 JSON↔流水线逐字相等（NB-3）；时间戳按实测（NB-4）；
> 补绑定断言与**实现状态**登记（NB-5，见 §7 第 0 项）。**板卡已被 Wong 拔下 ⇒ 板级工作暂停**。
> 依据：`CDX-20261022-014` §4/§5（≥100 帧、真实动态映射、过期边界、异常计数、30 分钟）、`S5A-G0-v2`、
> **阶段4 r04 共享契约（`7a9507a`）`frame_sequence_rules`**。
> **过去时声明**：既有合成源板上结论（四 FPS、120 帧五元组、31.06 min 长跑）**不重做、不改写、不升级**；
> 本骨架只补齐「真实结果接入前」可离线钉住的部分。
> **本轮修订（v1→v2，B-1/B-2/N-1..N-7）**：输入绑定重绑阶段4 r04；乱序/回退改为按 r04 **拒绝并记 FAIL**；
> 长跑口径改为区间数；计数单位声明；帧级日志落盘 + 独立复算器；时间戳按实际值；`UR-2` 关闭；
> 清单以 `interfaces_not_applicable_reason` 声明 inputs 不适用（首要理由＝无 `role=input` 文件）。
> 明细见 `S5T03_input_contract_binding_colour_v1.md` §9/§10。

## 1. 冻结口径（先冻结再运行）

| 类别 | 来源 | 值 |
|---|---|---|
| 逆映射一致性（vs float64 参考） | `S5A-G0-v2` | ≤1.0 px |
| 绘制保真 / 线宽半像素 | `S5A-G0-v2` | ≤1 px / ±0.5 px |
| 分数文本 | `S5A-G0-v2` | ≤1e-3 |
| 离散字段 | `S5A-G0-v2` | 完全一致（`frame_id`/`detection_count`/`class_id`/`class_name`/`source_order`） |
| 过期阈值 | `S5A-G0-v2`（阶段4 同源） | `STALE_AGE_LIMIT_NS = 200 000 000`，**严格大于**；`stale_effective = stale_flag OR age_frame > limit`，每结果只计一次；**判定不带 state 守卫**（N-1 登记，提请正式 G0 裁定） |
| 顺序规则 | **阶段4 r04** `frame_sequence_rules` | 重复/乱序/回退**一律拒绝并记 FAIL**（拒绝须落日志且记原因，不得只记计数） |
| 布局 | `S5A-G0-v2` | 线宽 2 px（偶数居中，`p` 占 `{p−1,p}`）、安全区 16 px@1080p、≤15 框、类别顺序固定 |
| 画面语义 | Wong 2026-10-21 | `B_latest_result_overlay`（最新候选＝最新**已接受**结果），`displayed_frame_id`/`result_frame_id` 成对如实记录 |
| 种子 | 本骨架（冻结） | `20261024` |
| 帧关联样本 | `CDX-014` §4 + T5-05 | 需求 ≥100 帧；骨架取 **120 帧/模式**；mixed 取 **240 帧** |
| 长跑样本 | `CDX-014` §5 + 板上实测显示周期 | 虚拟 30 分钟：**区间数 106 572**（= 帧数 **106 573** − 1）× 16.89 ms = 1 800 001 080 000 ns，余量 **+1.08 ms**（16.89 ms 取自 `s5t01_board_fps4_20261022_r02`） |
| 计数单位 | 本骨架（N-3） | 见参数 JSON `counter_units` 与 §5，例如 `timeouts` 按**提交帧**计、`stale_cleared` 按**结果键**去重 |
| 坐标手算样例 | 本骨架 | 5 例（`C1..C5`，算式写在参数文件里，独立于实现） |

## 2. 用例分组与判据

| 组 | 用例 | 判据 | 实现位置 |
|---|---|---|---|
| T01 契约完整性 | G0 字节与登记哈希一致（含 N-1 `stale_domain_note`）、几何参考未分叉、阈值与契约逐项一致、绑定 JSON 对齐 r04（两标签均 `camera`、回放 `replay_only`）、**回放 `capture_time_ns` 非零要求与 `carry_fields` 10 字段**、`implementation_status`（尚未实现）、NB-1 规则登记、**漂移登记覆盖扫描**（NB-2）、取代关系与 UR 状态、既有合成源证据未被改写 | 哈希相等；扫描命中集合 == 登记集合（双向相等）；`git diff --name-only 654c72e -- report/evidence/S5-A\|S5-B\|S5-C\|S5-T01` 为空 | `test_s5t03_skeleton.py::T01_*` |
| T02 坐标映射 | `C1..C5` 手算 vs 冻结参考；骨架实际绘制像素 = 手算；1280×720 / 720×1280 / 683×384；683×384 非对称补边 91/92；越界裁剪、裁剪后零面积不绘制、上游非正面积抛错；2 px 偶数线宽居中且钳到画布 | 逐值相等（坐标无容差，取整规则同源）；零面积不产生边框 | `T02_*` |
| T03 帧关联与顺序规则 | 顺序 120 帧五元组可按 `displayed_frame_id` 索引、语义唯一 B；迟到 2 帧如实记录 `displayed != result`；跳帧触发过期；**重复结果键 / `frame_id` 回退 / `result_seq` 回退 / 等价 `frame_id` 未声明（NB-1）一律拒绝并记 FAIL**（不写已接受集合、不更新 latest、不绘制）；等价 `frame_id` 的**显式声明**路径放行；含**判别力对照**（复刻 r02 语义时断言变红）与 `equiv` 流 40 帧覆盖 | 五元组条数 = 帧数；各拒绝计数 ≥1 且每个拒绝事件 `verdict=FAIL` 且有原因；被拒帧框与前一帧逐值相同；`duplicate_frame_id_results` 与 `duplicate_results` 分列 | `T03_*` |
| T04 过期与异常 | `age == limit` 不过期且照常绘制；`age == limit+1` 过期、不绘制、`stale_cleared` 只 +1（同一结果键跨 5 帧）；显式 `stale_flag` 且年龄小时原因 = `stale_flag`；零框 `NO_HAND` 合法（`boxes=0`、非过期）；`TIMEOUT/ERROR/DROPPED` 分列且不冒充零框；无效记录（`NO_HAND` 带框）只计数不绘制；HUD 13 字段齐全且不可用量标 `UNAVAILABLE` | 计数与注入数一致；`counters == 日志复算` | `T04_*` |
| T05 长跑（离线虚拟时间） | 106 573 帧每帧**恰好一条** `overlay_commit` 事件（缺事件即死锁）、提交时间戳单调不减、`virtual_elapsed = 106 572 × 16.89 ms` 且余量 = +1.08 ms、计数完全可由**落盘日志**（独立复算器）复算、重复/乱序不重复叠加 | 全部强断言；**不是板上耐久** | `T05_*` |
| T06 流 schema | 各模式记录通过冻结 `validate_result_record`（除刻意注入的无效记录）；`source_kind=synthetic`、`capture_time_available=false`、`unavailable_fields` 含 `capture_time_ns`；同种子确定、异种子不同 | 无效记录数 = 注入数 | `T06_*` |

## 3. 数据流与单一来源

```
合成动态流(s5t03_dynamic_stream.py, 种子 20261024)
        │  结果记录（阶段4 同 schema；source_kind=synthetic）
        ▼
骨架流水线(s5t03_display_pipeline.py)
  ├─ 校验：verification/s5_display_geometry_reference.py::validate_result_record
  ├─ 帧关联：contract_result_key=(session_id, frame_id, result_seq)
  ├─ 顺序规则（阶段4 r04）：重复结果键 / 乱序回退 / 等价 frame_id 未声明（NB-1）⇒ 拒绝 + verdict=FAIL + 原因；
  │    不写已接受集合、不更新 latest；放行只看 repeat_declared / repeat_index 递增
  ├─ 过期：effective_stale(stale_flag, age_frame)（同源 200 ms，严格大于；无 state 守卫）
  └─ 绘制几何：clip_unit_box → original_norm_to_display_px → border_pixel_sets（**全部导入，不重写**）
        ▼
帧级事件日志（result_submit / overlay_commit）→ 五元组 + HUD13 + 计数
        ├─ 在线复算：pipeline.recompute()
        └─ 落盘复算（N-4）：logs/events_*.jsonl[.gz] → scripts/stage5_t03/recompute_from_log.py（独立解析器）
```

- 骨架**不定义**任何几何公式；`T01` 用 SHA-256 钉住参考实现 `4d9fe369…`（与 S5-A 清单一致）证明未分叉。
- 骨架**不做**解码/NMS/阈值；消费的 `xyxy` 一律按「归一化原图坐标」直接使用。

## 4. 计数单位与时机（N-3）

| 计数器 | 单位与时机 | 备注 |
|---|---|---|
| `frames_committed` / `overlay_drawn_frames` / `warmup_frames` | 每**显示帧** 1 | 绘制帧仅当真的画了边框 |
| `boxes_drawn` / `zero_area_dropped` | 每**框** 1（逐帧累加） | 零面积框逐帧、逐框计数 |
| `dropped_frames` / `timeouts` / `error_results` | 每**提交帧** 1 | 该状态结果会被后续无新结果的帧继续复用 ⇒ 计数可高于注入结果数（240 帧 mixed：`timeouts=14` 而注入 TIMEOUT 结果 7 个） |
| `stale_cleared` | 每**结果键** 1（去重） | `(session_id, frame_id, result_seq)` |
| `duplicate_results` / `out_of_order_results` / `invalid_records` | 每次**提交** 1 | 均拒绝、不绘制、不更新 latest；乱序/回退记 FAIL 与原因 |
| `duplicate_frame_id_results`（NB-1） | 每次**提交** 1 | 同 session 等价 frame_id 且未显式声明重复/重放 ⇒ 拒绝并记 FAIL；与 `duplicate_results` 分列 |
| `zero_hand_frames` | 每个 NO_HAND 且非过期的**提交帧** 1 | 合法零框，不算过期 |

> **NB-3 精确表述**：参数 JSON `counter_units` = **14 个计数器条目 + `definition`**（共 15 键）；流水线 `COUNTER_UNITS` = **14 键**；
> 两者 14 条文本**逐字相等**（测试强制）；证据清单 limitations 由参数 JSON 生成**完整 14 条**。

## 5. 运行命令（真实退出码）

```bash
python -B scripts/stage5_t03/test_s5t03_skeleton.py -v              # 用例骨架
python -B scripts/stage5_t03/scan_hash_drift.py                     # NB-2 漂移登记覆盖扫描
python -B scripts/stage5_t03/run_s5t03_evidence.py \
    --run-dir report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r03 \
    --source-commit <交付内容提交>                                   # 证据 + 清单 + 检查器
python -B scripts/stage5_t03/recompute_from_log.py \
    --log report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r03/logs/events_mixed_240.jsonl \
    --expect report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r03/logs/events_mixed_240_expected.json
python -B D:/FPGA_Competition/verification/check_stage_delivery.py \
    --mode evidence --project-root D:/codex-worktrees/w5 \
    --manifest report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r03/delivery_manifest.json
```

- `--mode inputs` 按 `report/README.md` 规定**不适用**：**首要理由是"无 `role=input` 文件"**（本任务无本地输入文件），
  次因是上游接口均未冻结（`S5A-G0-v2` `frozen=false`、阶段4 r04 committed-not-frozen）；清单以
  `interfaces=[]` + `interfaces_not_applicable_reason` 如实声明，不伪造冻结字段、不绕过核验。
- 预期耗时：本机 Python 3.12 实测约 3.5–4 分钟（长跑用例与落盘日志复算占绝大部分），峰值内存远低于 1 GB；
  单次运行即固定证据，不重复跑长跑。

## 6. 与板上任务（S5-T02）的关系

- 本骨架是 S5-T02「板上动态映射」的**离线对拍基线与判据来源**：板上 C 实现必须镜像同一判定
  （取整规则、严格大于过期边界、**重复/乱序/回退拒绝并记 FAIL**、五元组语义、计数单位不隐藏），并接受同一组用例。
- 本骨架**不能**替代板上验证：P1 现有「宿主预计算框」仍只是显示通路基线；板上逆映射/绘制、过期边界、
  HUD 视觉、真实结果注入与 30 分钟联调一律 `NOT_RUN`，见 `S5T03_board_verification_pending_v1.md`。
- **板卡已由 Wong 于 2026-10-24 拔下**（`decisions/board_detached_boardfree_plan_20261024_r01.md`）⇒ 一切板级工作**暂停**；
  恢复后先重做受连接的判据（真彩目视、部署身份核对）再执行板级项。

## 7. 未做项（NOT_RUN，如实）

0. **实现层（NB-5）**：`camera_live_colour` 采集路径与 `camera_capture_replay_colour` 回放路径（逐帧 `frame_integrity` 校验、
   `replay_source_*` 绑定、**非零** `capture_time_ns` 传递、`replay_not_live` 标记）**尚未实现**；
   本骨架的关闭只在**绑定层**，合成流仍硬编码 `source_kind=synthetic`、`capture_time_available=false`。

1. 真实彩色帧（`camera_live_colour`）与回放帧（`camera_capture_replay_colour`）接入：需阶段4 结果契约冻结与其注入路径；
   本骨架的 `camera_capture_replay_colour` 语义已按 r04 对齐（`source_kind=camera` + `timing_claim_scope=replay_only`）。
2. 板上动态映射/绘制、板上过期边界三例、HUD13 视觉确认、跨进程故障注入。
3. 真实集成的 30 分钟联调、T5-10 板上回归、`capture_fps` 由 `UNAVAILABLE` 转实测、显示延迟物理测量。
4. 阶段5 正式 G0 未决项（成品允许延迟上限、颜色表与字号、阶段4 `stale_age_limit` 正式冻结、N-1 stale 判定域裁定）。