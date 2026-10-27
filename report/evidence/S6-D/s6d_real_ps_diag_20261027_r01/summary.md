# S6-D 阶段4真实 PS 单帧诊断消费预检

- 判定：**BLOCKED_FOR_S6_CORE**。本次只完成固定提交证据的序号、会话、trace/UART join 与字段资格审计；没有构造或调用阶段6状态机。
- 阶段4输入：提交 `4e0b03dd7090c7dc5615a4cd1e40bd193715faff`，当前 w4 HEAD `83c9284ad2296b9b2c836250cee615e255533615`，固定提交是该 HEAD 的祖先。adapter JSON SHA-256 `688c945eac6a24e1085eed6aa36fd5fc562e5b85a404d0292b9edb4b41541b30`；细化到各输入文件的 Git blob 和 SHA 见 `preflight_result.json`。
- 关联键：PS trace `(session_id=1396845568, frame_id=0, result_seq=1)`；S4-A join `(1396845568, 0, repeat_index=0)`；UART 键 `(frame_id=0, repeat_index=0, sequence=2)`。`OP_WEIGHTS` 使用 sequence 1，`OP_RUN_response` 使用 sequence 2；UART sequence 是请求/响应配对序号，不是 PS 本地 `result_seq`。
- 固定提交中的阶段4 decoder 重解码通过：双读快照字节一致，1 条 trace 记录；CRC、epoch、终态、响应、发送和 ACK 与 UART receipt 一致。检测数=1、框数=1、原始候选数=2，但消费包没有阶段6 `detections[]`/类别/分数/坐标，只有 heads 哈希，不能从数量或哈希推造结果框。
- trace 标记 `capture_time_available=false`、`capture_time_ns=0`；`result_time_ns` 与 `stale` 未提供。原始 PS timer ticks 未换算为 ns，未把未知 stale 当 fresh。
- 范围仅为单帧 `INT8_CHW_416` PS 诊断，不声称完整阶段4/RGB 预处理、实时性能、动作有效或阶段4 G5。T6-A03/P、板级 G3、6-E 实物验收及阶段6 G4/G5 均未执行。
- 本机离线命令与真实退出码：最终审计 `0`、定向单元测试 `0`、inputs/evidence 检查结果见对应输出日志和清单。`attempt_history.json` 保留了修复前退出码不为零的尝试及原因。
