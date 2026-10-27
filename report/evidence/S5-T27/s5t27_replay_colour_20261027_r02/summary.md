# S5-T27 回放/彩色输入路径 · 离线动态显示回归

- RunId：`s5t27_replay_colour_20261027_r02`｜结论范围：**回放/离线**（非实测、非板级、非实时）
- 判定：**REPLAY_OFFLINE_REGRESSION_PASS**（断言 30 项，失败 0 项）
- 回放源：阶段3 固定帧 `stage3_reference_frame_939fce22`（sha256 `939fce22b7e8…`、2764800 B、1280×720、stride 3840、BGR888/BGR），`capture_time_ns=1792776253000000000`（非零）、`clock_domain=replay_documented_wallclock`、`replay_not_live=true`
- 冻结包：`task27_replay_result_package_positive.json`（sha256 `988f2cae79cc…`，`contract_result_key={"session_id": 1396854863, "frame_id": 1, "result_seq": 1}`，检测 1 框）

## 覆盖与结论
- 坐标映射：冻结框 → 像素 [{"x1": 317, "y1": 267, "x2": 445, "y2": 314}]（冻结参考换算，逐值断言）
- 帧关联：240 帧五元组成对、语义唯一 B、每帧恰一次提交事件
- 过期边界：`age==200 ms` 不过期 / `+1 ns` 过期 / 显式 flag 过期（replay-local 逻辑时基）
- 顺序规则：重复键拒绝、`frame_id` 回退拒绝、等价 `frame_id` 未声明拒绝、声明放行、跳帧致过期
- 异常分支：TIMEOUT/ERROR/DROPPED/NO_HAND/零面积框分列且不冒充零框或过期
- 长跑：106573 帧、区间 106572 × 16890000 ns = 1800001080000 ns；每帧恰一次提交、时间戳单调、计数可复算、无重复/乱序叠加
- 相关套件：本卡用例 **14 项全 OK**；另有 **2 项 skip 属上游**（阶段4 契约冻结后被改动：登记 `7228f513…` ≠ 现状 `25bc30d5…`，消费链按设计 fail-closed 而 skip），**不是本卡缺陷**（N5）

## 不得外推（NOT_CLAIMED）
- 回放/离线：冻结包只含 1 帧结果内容，逐帧重复回放；不是新推理、不是真实采集、不是板上运行。
- replay-local 逻辑时基只验证过期与年龄**规则**；capture_time_ns 为阶段3 已文档化的真实抓取时刻（非零）。
- 不主张：板上回放/PL 实跑、UART 实收、摄像头质量与颜色、端到端延迟、G0–G5、T5-10、B1–B10 任一通过。
- 长跑为虚拟逻辑时基（1 800 001 080 000 ns），不是板上耐久。
- 相关套件 2 项 skip 属上游阶段4 契约漂移（登记 7228f513… ≠ 现状 25bc30d5…），非本卡缺陷（N5）。
