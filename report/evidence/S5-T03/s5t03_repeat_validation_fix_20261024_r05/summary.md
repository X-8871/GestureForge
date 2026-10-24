# S5-T03 离线用例骨架摘要（合成动态流，非真实集成）

- RunId：`s5t03_repeat_validation_fix_20261024_r05`；基线提交：`30147ab1f958c0dad2795da8e4b1c073ac39adaa`；输入范围标签：`synthetic_dynamic_reference`
- 用例骨架：40 项，失败 1，错误 0，耗时 217.227 s，退出码 1
- 既有合成源证据未被改写：UNTOUCHED（退出码 0）

## 覆盖（离线）
- 坐标映射：手算 5 例 + 冻结参考实现同源（哈希比对）+ 越界/零面积 + 2 px 偶数线宽钳位
- 帧关联：顺序/迟到/跳帧/重复/乱序；120 帧五元组可按 `displayed_frame_id` 索引、语义唯一 B、`displayed != result` 如实记录
- 异常与过期：`age==limit` 不过期、`limit+1` 过期且每结果只计一次、显式 `stale_flag`、零框 ≠ 过期、`TIMEOUT/ERROR/DROPPED` 分列、无效记录不绘制
- 长跑（离线虚拟时间）：106573 帧、区间数 106572 × 16.89 ms = 30.0000 分钟，每帧恰一次提交事件（无死锁）、时间戳单调、计数可复算
- 乱序/回退（B-2）：重复与乱序同构拒绝并记 FAIL；乱序帧框与前一帧逐值相同；不进入已接受集合
- 等价 frame_id（NB-1，fail-closed）：同 session 等价 frame_id 且未显式声明重复/重放 ⇒ 拒绝并记 FAIL；`repeat_declared=true` 或 `repeat_index` 递增才放行（含判别力对照与 `equiv` 流 40 帧覆盖）
- 落盘日志（N-4）：`logs/events_mixed_240.jsonl`、`logs/events_long_run.jsonl.gz`；独立复算器 `scripts/stage5_t03/recompute_from_log.py` 两次 exit 0；拒绝原因与 repeat/declaration 上下文落盘并复核
- task-24 修复：`session_id`/`frame_id`/`result_seq`/`repeat_index` 严格 uint32 校验先于键查找和状态变更；紧凑 JSONL 保存原始键、拒绝原因、重复声明与前序最大编号
- 漂移登记（NB-2）：`scripts/stage5_t03/scan_hash_drift.py` 扫描旧哈希绑定清单 == 登记集合；安静窗口：BUSY；实现层状态 **UNIMPLEMENTED**，板上状态 **SUSPENDED_BOARD_DETACHED**（NB-5）

## 关键计数（合成流，仅供骨架核对；不得当作板上结论）
- 240 帧 mixed：{"frames_committed": 240, "overlay_drawn_frames": 177, "boxes_drawn": 467, "warmup_frames": 0, "dropped_frames": 7, "timeouts": 14, "error_results": 7, "invalid_records": 7, "stale_cleared": 7, "duplicate_results": 8, "duplicate_frame_id_results": 0, "out_of_order_results": 8, "zero_hand_frames": 7, "zero_area_dropped": 89}
- 长跑：commit_events=106573，counters={"frames_committed": 106573, "overlay_drawn_frames": 76603, "boxes_drawn": 196510, "warmup_frames": 0, "dropped_frames": 3330, "timeouts": 6660, "error_results": 3330, "invalid_records": 3330, "stale_cleared": 3330, "duplicate_results": 3331, "duplicate_frame_id_results": 0, "out_of_order_results": 3331, "zero_hand_frames": 3330, "zero_area_dropped": 39962}

## 未做项（NOT_RUN，如实）
- 真实彩色采集/回放输入接入（待阶段4 结果契约冻结与注入路径确认）
- 板上动态映射与绘制（待阶段5 板级窗口；见 `docs/stage5/S5T03_board_verification_pending_v1.md`）
- 板上 `age==limit`/`limit+1`/`stale_flag` 边界样例、HUD 13 字段视觉、跨进程故障注入
- 真实集成的 30 分钟联调与 T5-10 板上回归

## 范围声明
本包只是**离线骨架**结论；G3/G4/G5 未通过；`check_stage_delivery` 的 `CHECKS_OK` 仅代表清单/文件绑定通过，
不代表测试语义正确、独立审查通过或 G0/G4/G5；亦不得把合成流结论升级为真实集成通过。

## 本轮更正（B-1/B-2/N-1..N-7，v1→v2）
- **B-1**：输入绑定重绑到阶段4 **r04**（`7a9507a`，JSON blob `611e6c7c…`）：两个彩色标签都映射 `source_kind=camera`、`capture_time_available=true`，回放用 `timing_claim_scope=replay_only` 区分；v1 曾引用的 `f6fa9f0` 快照记录为 SUPERSEDED。
- **B-2**：乱序/回退采用上游 r04 `frame_sequence_rules` 的**拒绝并记 FAIL**（与重复同构：不写已接受集合、不更新最新结果、不绘制）；新增「`frame_id` 回退」「`result_seq` 回退」两个必拒绝用例与「乱序帧框与前一帧逐值相同」断言。
- **N-1**：只改 S5A-G0-v2 JSON 的 stale 判定域**措辞**（行为不变），登记差异并提请正式 G0 裁定。
- **N-2**：长跑判据改为区间数 106572 × 16.89 ms = 1 800 001 080 000 ns（余量 +1.08 ms）。
- **N-3**：计数单位与时机已声明并机器自检（提交帧 / 结果键 / 提交次数 / 框数）。
- **N-4**：帧级事件日志已随证据落盘（`logs/events_mixed_240.jsonl`、`logs/events_long_run.jsonl.gz`），并有独立复算器实跑（`console/recompute_from_log.txt`，两次 exit 0）。
- **N-5**：时间戳按实际值改正（部署核对 01:07:50；参数首次冻结 00:43:33）。
- **N-6**：`UR-2` 已 RESOLVED（dbdf README 于 01:14 更正为 `v10_read`）。
- **N-7**：清单以 `interfaces=[]` + `interfaces_not_applicable_reason` 声明 inputs 不适用，**首要理由＝无 `role=input` 文件**。

## 取代关系与既有包影响
- 本包取代：`report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r01, report/evidence/S5-T03/s5t03_takeover_20261024_r01, report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r02, report/evidence/S5-T03/s5t03_takeover_20261024_r02`（被取代包清单绑定的源文件在本轮更正后字节已变，其清单对当前字节不再匹配；被取代证据保留、不删除、不就地改写）。
- 旧哈希漂移登记（NB-2 扫描判据）：以 8eac7007… 绑定 S5A-G0-v2 JSON 的清单已全部登记；扫描命中 19 个清单文件、登记 19 个；哈希轨迹 8eac7007… → 10d24a39… → e3347c4e… → af51a4bf…（阈值/几何/语义自 N-1 后未再变）。

