# S6-E `command_delivery_review` 严格 JSON 修复轮核验

- RunId：`s6e_command_delivery_20261027_r04`（2026-10-27，UTC+8）
- 基线 HEAD：`b50736e6688a4a384f4f2f484872f9e5e59b690a`
- 保留旧轮：r01/r02/r03 均未改写；原始字节 manifest SHA-256 分别为 `9b7df1dc67e45361d3808715490b781139449436e3729b5072d4ddff25f107a2`、`f45b290bba3e3c38116a9f0976b0035a28f93468bec62f076b564105b0f747cb`、`681b6239b630edbe1de3ac4af612fceccf2328473476b92efc56dfc4b1976c33`，并由本轮 inputs 清单只读绑定。

## 复审整改

`_load_json_strict()` 是计划工具所有文件 JSON 入口的唯一读取函数，使用递归 `object_pairs_hook` 拒绝所有对象层级的重复键，并拒绝非标准 JSON 常量。冻结用例生成入口、计划语义校验入口及 CLI `validate --plan` 文件入口均使用该函数；重复键由 CLI 报为 `BLOCKED`，退出码 2，不继续解释可能被覆盖的键。

新增 CLI 负测分别向顶层 `acceptance_claim` 和用例嵌套的 `samples.min` 注入重复键；另测试冻结用例源文件的重复 `task_id`。三处均按预期拒绝。此前字段白名单、输出目录约束、RunId 检查、独占创建及验收声明拒绝测试也保留在同一测试套件中。

真实 Windows 目录符号链接测试仍受 WinError 1314（缺少创建链接权限）限制，未执行；链接/junction 拒绝分支使用注入检测器覆盖。测试未提权创建真实链接。

## 验收边界

本轮仍只验证离线 dry-run 计划与其输入文件完整性。`command_delivery_review` 仍 **BLOCKED / 未关闭**：正式门禁要求板级执行器和判定脚本独立审查，且硬件命令可复制执行；阶段4真实结果接口及阶段5动作回执契约尚未冻结。本轮不生成硬件命令，不声称 G3、G4 或 G5 通过。T6-A03 仍 `NOT_RUN`，6-E 实物验收未执行。
