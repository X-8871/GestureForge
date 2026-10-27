# S6-E `command_delivery_review` 浮点溢出修复轮核验

- RunId：`s6e_command_delivery_20261027_r05`（2026-10-27，UTC+8）
- 基线 HEAD：`b50736e6688a4a384f4f2f484872f9e5e59b690a`
- 旧 RunId r01–r04 均保留未改写；其 manifest 由本轮 inputs 清单只读绑定。

## 修复

严格 JSON 加载器新增 `parse_float`：解析十进制数后立即检查 `math.isfinite`，拒绝 `1e999` 溢出成 Infinity；原有重复键和非标准常量拒绝逻辑继续生效。计划写出改用 `json.dumps(..., allow_nan=False)`，并在创建 RunId 目录之前完成完整序列化；序列化失败不会留下计划目录或计划文件。

## 定向验证

- CLI `validate` 顶层与 case 嵌套字段中的 `1e999` 均返回 BLOCKED/2。
- CLI `plan` 从冻结用例源读取到嵌套 `1e999` 时返回 BLOCKED/2，且目标 RunId 目录不存在。
- 直接尝试序列化含 `Infinity` 的计划被拒绝，且 RunId 目录未创建。
- 合法有限值 `0.9` 和 `1.25` 可正常解析；正式冻结用例计划生成/校验保持通过。

仍有真实 Windows 目录 symlink 创建权限限制（历史 WinError 1314）：本轮不创建真实链接；链接/junction 检查分支继续使用注入检测器覆盖，限制不被解释为已验证真实文件系统链接。

## 验收边界

本轮仅改严格浮点解析/计划序列化并补定向验证。正式 `command_delivery_review` 仍 BLOCKED；没有板级执行器或可复制硬件命令，没有真实结果接口。本轮无硬件访问，6-E 实物、G3、G4、G5 均未声称通过。
