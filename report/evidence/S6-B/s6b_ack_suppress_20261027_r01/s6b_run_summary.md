# S6-B ACK suppression fail-closed 回归摘要

- RunId：`s6b_ack_suppress_20261027_r01`
- 基线提交：`3be42b897003e00680bd554d915939de7dfde08e`；本轮源码字节 SHA-256 见 `delivery_manifest.json`。
- 定向与既有回归：27/27 项 ACK/core/probe/builder 回归全通过，退出码 0。新增测试覆盖 `S_DEDUP` 合法重复正例，以及 truthy/falsey 非字符串、空字符串、未知字符串、核心内部 suppression 名称被拒绝且状态快照不变。
- 既有矩阵：freeze-only 退出码 0，冻结哈希绑定 r03 矩阵的 26 个 expected 块；随后离线矩阵 26/26 通过、0 个断言失败。

## 合法值依据

`src/stage6/s6_actions.py` 的真实提交分支仅将 `SUP_DEDUP="S_DEDUP"` 写入 ACK 的 suppression 字段；真实 ACK 对应 `suppression=None`。S6-A 行为表中的 `S_COOLDOWN` 等是核心状态机抑制事件，不是动作层 ACK suppression。因此 ACK 入口仅接受字段缺失/`None` 或字符串 `S_DEDUP`；其他值在任何状态、计数、冷却锚点或去重集合更新前抛出 `CoreInputError`。

## 限制

本包是本机离线软件回归，不构成实时、板级 G3、阶段4/5真实集成、6-E实物或阶段6 G5 验收。代码未提交，独立定向复审待总控安排。
