# S5-T03 离线用例骨架摘要（合成动态流，非真实集成）

- RunId：`s5t03_offline_skeleton_20261024_r01`；基线提交：`ba31126490fe8684c774d5e2e7d9fb96324fb623`；输入范围标签：`synthetic_dynamic_reference`
- 用例骨架：24 项，失败 0，错误 0，耗时 193.557 s，退出码 0
- 既有合成源证据未被改写：UNTOUCHED（退出码 0）

## 覆盖（离线）
- 坐标映射：手算 5 例 + 冻结参考实现同源（哈希比对）+ 越界/零面积 + 2 px 偶数线宽钳位
- 帧关联：顺序/迟到/跳帧/重复/乱序；120 帧五元组可按 `displayed_frame_id` 索引、语义唯一 B、`displayed != result` 如实记录
- 异常与过期：`age==limit` 不过期、`limit+1` 过期且每结果只计一次、显式 `stale_flag`、零框 ≠ 过期、`TIMEOUT/ERROR/DROPPED` 分列、无效记录不绘制
- 长跑（离线虚拟时间）：106573 帧 ≈ 30.00 分钟，每帧恰一次提交事件（无死锁）、时间戳单调、计数可复算

## 关键计数（合成流，仅供骨架核对；不得当作板上结论）
- 240 帧 mixed：{"frames_committed": 240, "overlay_drawn_frames": 177, "boxes_drawn": 468, "warmup_frames": 0, "dropped_frames": 7, "timeouts": 14, "error_results": 7, "invalid_records": 7, "stale_cleared": 7, "duplicate_results": 8, "out_of_order_results": 8, "zero_hand_frames": 7, "zero_area_dropped": 89}
- 长跑：commit_events=106573，counters={"frames_committed": 106573, "overlay_drawn_frames": 76603, "boxes_drawn": 196509, "warmup_frames": 0, "dropped_frames": 3330, "timeouts": 6660, "error_results": 3330, "invalid_records": 3330, "stale_cleared": 3330, "duplicate_results": 3331, "out_of_order_results": 3331, "zero_hand_frames": 3330, "zero_area_dropped": 39962}

## 未做项（NOT_RUN，如实）
- 真实彩色采集/回放输入接入（待阶段4 结果契约冻结与注入路径确认）
- 板上动态映射与绘制（待阶段5 板级窗口；见 `docs/stage5/S5T03_board_verification_pending_v1.md`）
- 板上 `age==limit`/`limit+1`/`stale_flag` 边界样例、HUD 13 字段视觉、跨进程故障注入
- 真实集成的 30 分钟联调与 T5-10 板上回归

## 范围声明
本包只是**离线骨架**结论；`check_stage_delivery` 的 `CHECKS_OK` 仅代表清单/文件绑定通过，
不代表测试语义正确、独立审查通过或 G0/G4/G5；亦不得把合成流结论升级为真实集成通过。

