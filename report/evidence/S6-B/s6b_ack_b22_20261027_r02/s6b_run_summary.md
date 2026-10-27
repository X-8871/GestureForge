# S6-B/C 离线缺口修复回归摘要

RunId：s6b_ack_b22_20261027_r02  
工作树：D:\\codex-worktrees\\w6；分支：stage6-interact-prep  
基线 HEAD：3be42b897003e00680bd554d915939de7dfde08e  
本包的源码、输入、输出哈希见同目录 delivery_manifest.json。

## 本轮处理

- M10：保留当前目标的 IDLE 状态也按 T6-L01/T6-L02 求值；定向测试覆盖单帧选中后在 IDLE 等待至 L02，再 M10→M11 清空旧目标并以新 acquisition_id 重获。
- B28：真实 success/fail ACK 要求非空白字符串 action_id；ID 视为不透明值，不假定 ACT 前缀。重复 success、fail、success+unobserved 均不重复计数/迁移；success/unobserved 保持首个 t_submit 冷却锚点，fail 不设锚点。无 ID 的 S_DEDUP suppression 合法且不进入去重集。新 session 的 B25 全量复位清空去重集。由于契约未定义 ACK ID 格式或重放上限，不设置 FIFO 淘汰；去重集合会随单个长 session 的真实 ACK 数增长。当前 ActionLayer 是同步返回 ACK，接口没有 session_id；未来异步跨 session 迟到回执仍需接口级会话标识。
- B22：指纹为对事件对象规范化 JSON 后的 SHA-256；字典键排序，float 使用 float.hex()，保留列表/元组类型。纳入 kind、state、stale、detections 和其他事件字段；排除 session_id/frame_id（会话作用域和帧键）、t_input_ns（接收时刻）、age_result_ns/age_frame_ns（仅日志字段）、dropped_frames（重复帧分支早于其缺帧统计）。重复帧哈希相同计 duplicate 并幂等丢弃；不同则记 conflict_frames/E_FRAME_CONFLICT，保留前次身份内容，不推进状态机。独立测试分别改变 stale、state、detections、event kind 和 error_code 均得冲突；只改变接收时间、age 和 dropped_frames 仍为 duplicate。
- expected_freeze.json 来源是已冻结的 S6-B r03 case_matrix.json 中的 expected 字段。freeze-only 不调用 run_case、不执行状态机，因此没有使用被测实现生成期望值。

## 验证结果

- 定向回归：21/21 PASS（本轮新增 S6-B/C 回归 11 项；既有 probe 4 项；builder 6 项），exit 0。
- 已有确定性矩阵：26/26 PASS，0 assertion failures，exit 0；每例 JSONL 在 logs/。
- 首次默认沙箱启动定向 unittest 被拒绝访问，exit 1，未启动测试进程；同一命令在审批后重跑通过。原命令、退出码和错误记录见 execution_records.json。
- 当前交付清单核验由 check_stage_delivery.py 在清单生成后单独执行并记录。

## 范围与限制

本包只证明注入输入和虚拟单调时钟下的 S6-B/C 离线行为。未运行相机、板卡、JTAG、串口、HDMI、Vivado或硬件会话；不构成实时性能、G3、G4、独立审查或阶段 G5 结论。T6-A03仍 NOT_RUN；阶段4/5真实接口集成与6-D/6-E实物验收仍 BLOCKED/NOT_RUN。source_commit 是当前基线提交；本轮工作树源码尚未提交，以清单中逐文件 SHA-256 绑定，等待独立 Reviewer。
