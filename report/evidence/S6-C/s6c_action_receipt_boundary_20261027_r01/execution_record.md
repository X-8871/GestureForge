# S6-C 动作回执边界离线执行记录

- RunId：`s6c_action_receipt_boundary_20261027_r01`
- 运行日期：2026-10-27（UTC+8）
- 工作树：`D:\codex-worktrees\w6`；分支：`stage6-interact-prep`
- 基线 HEAD：`2cd8bc9a7fa158a86bde35bb60af8f056d134feb`
- 工具版本：Python `3.12.14`（64 位）；Git `2.56.0.windows.2`。
- 本轮文件：`src/stage6/s6_receipts.py`、`verification/test_s6c_receipt_boundary.py`，以及本证据目录。
- 权限核验：开始前 `git status --short` 中的 STATE、S6-A 和旧 S6-B 证据均为既有差异；未改写、暂存或提交。w6 交接状态记 Codex 持有写权。由 `git rev-parse --git-path index.lock` 得 `D:/FPGA_Competition/.git/worktrees/w6/index.lock`，检查时不存在。
- 本轮仅运行离线 Python 单元测试；没有访问摄像头、板卡、JTAG、串口、HDMI 或硬件会话。

## 验证命令与结果

| 命令 | 退出码 | 结果 |
|---|---:|---|
| `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest verification.test_s6c_receipt_boundary verification.test_s6b_core_regressions -v` | 0 | 共运行 4 次，均 41 项通过：S6-C 边界 13 项，S6-B 核心回归 28 项。最后一次在 JSON 快照与 UTF-8 错误路径加固后测得 0.012 s；第 3 次输出见 `unit_test.log`，最终源码版本完整输出见 `unit_test_final.log`。 |

## 覆盖范围

- 同 ID、同业务 ACK 的重放：仅接收时刻不同可去重；核心只计数一次。
- 同 ID 的生效/提交字段冲突：调用核心前拒绝且核心状态/计数不变。
- `success + unobserved` 与 `fail + unobserved`：不晋升为生效；失败不建立冷却锚点；重放不重复计数。
- 缺少显式接收时钟、接收时钟倒序、缺少 `t_submit_ns`、缺少 observed ACK 的 `t_effective_ns`：失败关闭，非法 ACK 不污染 action_id 去重集。
- 非有限值、嵌套非字符串键、循环数据：在核心调用前拒绝。
- 无 ID 抑制 ACK：逐次交给既有核心，不增加新的去重语义。
- session reset 后保持同一边界实例；拒绝晚挂接到既有核心和绕过边界造成的无指纹 ACK。

## 解释边界

上述测试使用合成 ACK，仅验证 S6-B `note_action_ack()` 输入边界。它们不执行外部动作，不观测显示，不是 6-E 真实推理/摄像头试验或板级 G3。真实 transport/执行器、阶段5 `ACTION_EFFECTIVE` 观测字段和冷启动/窗口门禁仍未满足；本轮不声称 S6-C G2、S6-E、G3、G4、G5 通过。独立审查尚待总控安排。
