# S5-T03 离线用例骨架规格（v1，2026-10-24）

> 状态：**离线骨架**，不是阶段5 验收、不是板上结论。冻结参数权威：`docs/stage5/s5t03_offline_skeleton_params_v1.json`
> （`FROZEN_BEFORE_RUN`，种子与样本数先于运行冻结）。实现：`scripts/stage5_t03/**`。
> 依据：`CDX-20261022-014` §4/§5（≥100 帧、真实动态映射、过期边界、异常计数、30 分钟）与 `S5A-G0-v2`。
> **过去时声明**：既有合成源板上结论（四 FPS、120 帧五元组、31.06 min 长跑）**不重做、不改写、不升级**；
> 本骨架只补齐「真实结果接入前」可离线钉住的部分。

## 1. 冻结口径（先冻结再运行）

| 类别 | 来源 | 值 |
|---|---|---|
| 逆映射一致性（vs float64 参考） | `S5A-G0-v2` | ≤1.0 px |
| 绘制保真 / 线宽半像素 | `S5A-G0-v2` | ≤1 px / ±0.5 px |
| 分数文本 | `S5A-G0-v2` | ≤1e-3 |
| 离散字段 | `S5A-G0-v2` | 完全一致（`frame_id`/`detection_count`/`class_id`/`class_name`/`source_order`） |
| 过期阈值 | `S5A-G0-v2`（阶段4 同源） | `STALE_AGE_LIMIT_NS = 200 000 000`，**严格大于**；`stale_effective = stale_flag OR age_frame > limit`，每结果只计一次 |
| 布局 | `S5A-G0-v2` | 线宽 2 px（偶数居中，`p` 占 `{p−1,p}`）、安全区 16 px@1080p、≤15 框、类别顺序固定 |
| 画面语义 | Wong 2026-10-21 | `B_latest_result_overlay`（最新结果叠加），`displayed_frame_id`/`result_frame_id` 成对如实记录 |
| 种子 | 本骨架（新冻结） | `20261024` |
| 帧关联样本 | `CDX-014` §4 + T5-05 | 需求 ≥100 帧；骨架取 **120 帧/模式**；mixed 取 **240 帧** |
| 长跑样本 | `CDX-014` §5 + 板上实测显示周期 | 虚拟 30 分钟 = **106 573 帧 × 16.89 ms**（16.89 ms 取自 `s5t01_board_fps4_20261022_r02`） |
| 坐标手算样例 | 本骨架 | 5 例（`C1..C5`，算式写在参数文件里，独立于实现） |

## 2. 用例分组与判据

| 组 | 用例 | 判据 | 实现位置 |
|---|---|---|---|
| T01 契约完整性 | G0 字节未变、几何参考未分叉、阈值与契约逐项一致、绑定 JSON 含两个范围标签、既有合成源证据未被改写 | 哈希相等；`git diff --name-only 654c72e -- report/evidence/S5-A\|S5-B\|S5-C\|S5-T01` 为空 | `test_s5t03_skeleton.py::T01_*` |
| T02 坐标映射 | `C1..C5` 手算 vs 冻结参考；骨架实际绘制像素 = 手算；1280×720 / 720×1280 / 683×384；683×384 非对称补边 91/92；越界裁剪、裁剪后零面积不绘制、上游非正面积抛错；2 px 偶数线宽居中且钳到画布 | 逐值相等（坐标无容差，取整规则同源）；零面积不产生边框 | `T02_*` |
| T03 帧关联 | 顺序 120 帧五元组可按 `displayed_frame_id` 索引、语义唯一 B；迟到 2 帧仍如实记录 `displayed != result`；跳帧导致年龄增长并触发过期；重复结果只计数、**不更新最新结果**（叠加内容与前一帧逐像素相同）；乱序结果计数 | 五元组条数 = 帧数；`age_frame_ns > 0`；重复/乱序计数 ≥1 | `T03_*` |
| T04 过期与异常 | `age == limit` 不过期且照常绘制；`age == limit+1` 过期、不绘制、`stale_cleared` 只 +1（同一结果键跨 5 帧）；显式 `stale_flag` 且年龄小时原因 = `stale_flag`；零框 `NO_HAND` 合法（`boxes=0`、非过期）；`TIMEOUT/ERROR/DROPPED` 分列且不冒充零框；无效记录（`NO_HAND` 带框）只计数不绘制；HUD 13 字段齐全且不可用量标 `UNAVAILABLE` | 计数与注入数一致；`counters == 日志复算` | `T04_*` |
| T05 长跑（离线虚拟时间） | 106 573 帧每帧**恰好一条** `overlay_commit` 事件（缺事件即死锁）、提交时间戳单调不减、虚拟时长 ≥1800 s、计数完全可由事件日志复算、重复结果不重复叠加 | 全部强断言；**不是板上耐久** | `T05_*` |
| T06 流 schema | 各模式记录通过冻结 `validate_result_record`（除刻意注入的无效记录）；`source_kind=synthetic`、`capture_time_available=false`、`unavailable_fields` 含 `capture_time_ns`；同种子确定、异种子不同 | 无效记录数 = 注入数 | `T06_*` |

## 3. 数据流与单一来源

```
合成动态流(s5t03_dynamic_stream.py, 种子 20261024)
        │  结果记录（阶段4 同 schema；source_kind=synthetic）
        ▼
骨架流水线(s5t03_display_pipeline.py)
  ├─ 校验：verification/s5_display_geometry_reference.py::validate_result_record
  ├─ 帧关联：contract_result_key=(session_id, frame_id, result_seq)
  ├─ 过期：effective_stale(stale_flag, age_frame)（同源 200 ms，严格大于）
  └─ 绘制几何：clip_unit_box → original_norm_to_display_px → border_pixel_sets（**全部导入，不重写**）
        ▼
帧级事件日志（result_submit / overlay_commit）→ 五元组 + HUD13 + 计数（必须可复算）
```

- 骨架**不定义**任何几何公式；`T01` 用 SHA-256 钉住参考实现 `4d9fe369…`（与 S5-A 清单一致）证明未分叉。
- 骨架**不做**解码/NMS/阈值；消费的 `xyxy` 一律按「归一化原图坐标」直接使用。

## 4. 运行命令（真实退出码）

```bash
python -B scripts/stage5_t03/test_s5t03_skeleton.py -v              # 用例骨架
python -B scripts/stage5_t03/run_s5t03_evidence.py \
    --run-dir report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r01 \
    --source-commit <交付内容提交>                                   # 证据 + 清单 + 检查器
python -B D:/FPGA_Competition/verification/check_stage_delivery.py \
    --mode evidence --project-root D:/codex-worktrees/w5 \
    --manifest report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r01/delivery_manifest.json
```

- `--mode inputs` 按 `report/README.md` 规定**不适用**（上游接口均未冻结：`S5A-G0-v2` `frozen=false`、阶段4 结果为草案），已在清单 `checks` 记 `NOT_APPLICABLE`，不伪造冻结字段。
- 预期耗时：本机 Python 3.12 实测约 3.5 分钟（长跑用例占绝大部分），峰值内存远低于 1 GB；单次运行即固定证据，不重复跑长跑。

## 5. 与板上任务（S5-T02）的关系

- 本骨架是 S5-T02「板上动态映射」的**离线对拍基线与判据来源**：板上 C 实现必须镜像同一判定
  （取整规则、严格大于过期边界、五元组语义、计数不隐藏），并接受同一组用例。
- 本骨架**不能**替代板上验证：P1 现有「宿主预计算框」仍只是显示通路基线；板上逆映射/绘制、过期边界、
  HUD 视觉、真实结果注入与 30 分钟联调一律 `NOT_RUN`，见 `S5T03_board_verification_pending_v1.md`。

## 6. 未做项（NOT_RUN，如实）

1. 真实彩色帧（`camera_live_colour`）与回放帧（`camera_capture_replay_colour`）接入：需阶段4 结果契约冻结与
   注入路径确认（`UR-1`）。
2. 板上动态映射/绘制、板上过期边界三例、HUD13 视觉确认、跨进程故障注入。
3. 真实集成的 30 分钟联调、T5-10 板上回归、`capture_fps` 由 `UNAVAILABLE` 转实测、显示延迟物理测量。
4. 阶段5 正式 G0 未决项（成品允许延迟上限、颜色表与字号、阶段4 `stale_age_limit` 正式冻结）。