# S6-D 单帧回放输入预检

- 状态：**BLOCKED**
- 适用范围：阶段4/5 固定字节下的离线 replay-only 输入资格检查。
- 状态机：**未调用**；没有构造事件或动作。
- 真实回放帧：1 帧 `NO_HAND`、0 检测框。
- 阻断原因：stale 不是布尔值；阶段6不能把未知状态静默当作 fresh
- 阳性门禁几何投影明确 `display_eligible=false`，未读作回放检测框。
- `capture_time_ns` 是文档化回放墙钟，不是单调发布计时；`result_time_ns`、年龄和 `stale` 均不可用。
- T6-A03/P、实时延迟、板级 G3、6-E 实物验收及阶段 G4/G5 未执行。

## 前序执行器启动失败记录

- r05 因运行器与目标 RunId 目录重合而在创建预检结果前拒绝运行；子进程退出码 2，外层运行器退出码 1。
- 原始 r05 及其日志保留；副本位于 `tmp/6/s6d_r05_attempt_evidence/` 并由输入清单绑定。
- r06 在创建结果目录前因严格比较当前 W5 磁盘源码与旧冻结 blob 而退出；其 pinned commit blobs 实际与清单一致，独立记录位于 `tmp/6/s6d_r06_attempt_evidence/`。

## 新增阶段4/5阳性回放输入（独立只读核验）

- 回放绑定审计：**PASS_BYTES_BLOCKED_INPUT**；上游文件与来源绑定通过。
- 实际帧：`PRESENT`、1 个 `fist` 检测框；与阶段4冻结包主键及框字段匹配。
- 时间闸门：`capture_time_ns=0` 是 FILE_INJECTION 哨兵，`result_time_ns=null`、`stale=null`；阳性帧保持 **BLOCKED**。
- 阶段6核心：**NOT_RUN**；未构造事件、未调用状态机。
- 阳性输入审计文件：`positive_replay_input_audit.json`。
