# S6-D 单帧回放输入预检

- 状态：**BLOCKED**
- 适用范围：阶段4/5 固定字节下的离线 replay-only 输入资格检查。
- 状态机：**未调用**；没有构造事件或动作。
- 真实回放帧：1 帧 `NO_HAND`、0 检测框。
- 阻断原因：stale 不是布尔值；阶段6不能把未知状态静默当作 fresh
- 阳性门禁几何投影明确 `display_eligible=false`，未读作回放检测框。
- `capture_time_ns` 是文档化回放墙钟，不是单调发布计时；`result_time_ns`、年龄和 `stale` 均不可用。
- T6-A03/P、实时延迟、板级 G3、6-E 实物验收及阶段 G4/G5 未执行。
