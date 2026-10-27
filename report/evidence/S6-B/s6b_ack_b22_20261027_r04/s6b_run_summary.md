# S6-B/C ACK 输入验证回归摘要

- RunId：`s6b_ack_b22_20261027_r04`
- 基线提交：`3be42b897003e00680bd554d915939de7dfde08e`；工作树源码为未提交字节，具体 SHA-256 见 `delivery_manifest.json`。
- 范围：修复 S6-B ACK 接收事务性校验；本轮也执行既有 S6-B/C 确定性 26 案例矩阵。未修改上游 S6-A、阶段4/5或硬件相关内容。

## 结果

- 定向与既有回归：`python -B -m unittest test_s6b_core_regressions test_s6b_probe test_s6b_build_evidence -v`，退出码 0，26/26 通过。
- 冻结输入期望：`s6b_run_cases.py --freeze-only`，退出码 0，绑定既有 `s6b_core_20261025_r03/cases/case_matrix.json` 的 26 个 expected 块。此步骤只快照输入中的 expected，不运行状态机、不以被测实现生成期望值。
- 离线矩阵：相同案例矩阵正常运行，退出码 0，26 案例通过、0 assertion failures。
- `execution_records.json` 保留了前置的失败运行（退出码 1）：该轮旧的 session-reset 观测 ACK 夹具缺少现在要求的 `t_effective_ns`；修正夹具后重新执行，最终 26 项全通过。此失败记录未删除或覆盖。

## 本轮判别范围

真实 ACK 必须有非空字符串 `action_id`、`submit_result` 只能是 `success`/`fail`、`t_submit_ns` 必须为非布尔整数；`success+observed` 要求整数 `t_effective_ns >= t_submit_ns`，`success+unobserved` 与 `fail` 要求 `effective_result=unobserved` 且 `t_effective_ns=null`。suppression 依实际 `ActionLayer` 合法输出校验为无 ACK ID、提交/生效结果及时间戳。无效输入在改变状态、计数、冷却锚点或去重集合前拒绝；成功与失败路径均有负测和状态快照断言。

没有将 ACK 时间与 `last_t_ns` 比较：`note_action_ack` 没有回执接收时间字段，接口无法据此证明时序先后；新 ACK 仍须不早于已有成功冷却锚点，合法迟到重复 ACK 按 ID 幂等忽略。

## 限制

- 证据为本机离线测试及虚拟时间，不构成实时、板级 G3、实物或阶段6 G5 结论。
- 本轮未执行 S6-D/S6-E 集成或实物验收，也未声称阶段4/5真实冻结输入已满足。
- 独立复审待总控安排；本轮子任务不提交代码。
