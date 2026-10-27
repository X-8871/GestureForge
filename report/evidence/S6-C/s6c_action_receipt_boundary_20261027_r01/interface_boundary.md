# S6-C 动作回执边界（离线）

## 范围与版本

- RunId：`s6c_action_receipt_boundary_20261027_r01`
- 工作树：`D:\codex-worktrees\w6`；分支：`stage6-interact-prep`
- 起始提交：`2cd8bc9a7fa158a86bde35bb60af8f056d134feb`
- 本包仅新增阶段6内部 ACK 边界与离线回归；不改 S6-A 冻结语义、S6-B 核心、STATE 或既有 RunId。

## 当前已实现的内部边界

`src.stage6.s6_receipts.ActionReceiptBoundary` 接收已经解码的 ACK 字典和调用方显式提供的 `received_at_ns`，然后调用既有 `GestureInteractionCore.note_action_ack()`。该值必须是非负整数纳秒，且同一边界实例观察到的接收时刻不得倒序；代码不读取系统时钟，不推导 Stage 4/5 时间关系。

- 对同一非空 `action_id`，ACK 字典的完整 JSON 业务内容构成指纹；字典键序不影响比较，非 JSON、非有限值、非字符串对象键和循环结构被拒绝。
- 每次传输接收时刻位于 ACK 字典之外，不进入业务指纹。`t_submit_ns`、`t_effective_ns` 仍是核心业务字段，缺失或不合法时由既有核心校验拒绝。
- 同 ID 且相同业务内容时再次交给核心，保留其既有 `duplicate_ack_ignored` 日志与不重复计数行为。
- 同 ID 但任一 ACK 字段不同，边界在调用核心前抛出 `ConflictingActionAckError`；不把新内容静默折叠为重复，也不改核心计数、状态或冷却锚点。
- 无 action ID 的合法抑制 ACK 按既有核心语义逐次交付，不由此边界擅自增加去重语义。
- 边界须在核心处理首个 ACK 前创建，并在 `reset_session()` 后复用同一实例。若已有核心 ACK 历史但没有完整指纹，初始化失败关闭；进程重启后的 ACK 历史持久化尚无正式契约。

## 尚未冻结的真实接口

当前没有已冻结的动作 transport、板级执行器或显示侧观测接口可供 S6-C 消费。故本模块是同一阶段内的输入校验/幂等边界，不负责发送动作，也不生成 `ACTION_SUBMITTED` 或 `ACTION_EFFECTIVE`。离线测试里的 ACK 均为合成字典，只验证核心消费者的既有行为；它们不证明显示状态发生变化。

阶段4结果字段与时间契约、阶段5显示回执字段/观测来源、接收时钟的真实来源、跨进程 action_id 历史恢复均保持 `BLOCKED`，须由对应正式接口冻结后再集成。正式 `ACT-*`、`UNK-*`、`REC-*` 用例及 6-E 实物验收仍 `NOT_RUN`；`T6-A03` 数值仍 `NOT_RUN`。本包不申请窗口、不操作板卡，不代表 G2/G3/G4/G5 通过。
