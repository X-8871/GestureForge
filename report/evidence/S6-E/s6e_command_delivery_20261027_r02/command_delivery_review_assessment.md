# S6-E `command_delivery_review` 修复轮核验

- RunId：`s6e_command_delivery_20261027_r02`（2026-10-27，UTC+8）
- 基线 HEAD：`b50736e6688a4a384f4f2f484872f9e5e59b690a`
- 前轮保全：r01 `delivery_manifest.json` 原始字节 SHA-256 为 `9b7df1dc67e45361d3808715490b781139449436e3729b5072d4ddff25f107a2`；r02 `inputs_manifest.json` 按交付检查器的文本换行规范化口径记录为 `b5a04bc38f6fc68c2d448e35be582f54c4247399826847714f273e5005f85c8d`。两者分别按原始字节/规范化文本计算，r01 目录未修改。
- 适用范围：计划文件输出安全、dry-run 计划字段完整性与拒绝路径；不派发硬件命令。

## 修复内容

1. `plan` 只接受规范 RunId `s6e_command_delivery_YYYYMMDD_rNN`（日期有效，序号非零），且 `--out` 若提供必须逐字匹配 `report/evidence/S6-E/<run_id>/dry_run_plan.json`。不得写入源码、证据根外路径、绝对路径或穿越路径。
2. 要求 `report/evidence/S6-E` 为普通目录，检查其祖先中的符号链接/junction；解析后的输出必须留在 project-root 内。RunId 目录以 `mkdir(exist_ok=False)` 创建，计划文件以 `O_CREAT | O_EXCL` 原子独占创建，拒绝既有 RunId 或目标文件；重复调用不会覆盖既有字节。
3. 计划顶层、来源对象、每条用例和每条门禁都有严格字段白名单与必需字段检查。诸如 `acceptance_status=PASS`、`real_inference_completed=true` 等未知字段拒绝；布尔字段同时要求真实布尔类型，不能用整数伪装。

## 复核判断

本轮修复回应 Reviewer 对 r01 的两项 `CHANGES_REQUIRED`。16 项离线回归覆盖源码目标、外部路径、穿越路径、非法 RunId、预存 RunId/输出、同一 RunId 重跑、链接/junction 拒绝分支、顶层及用例伪造验收声明。链接/junction 分支用注入检测器在临时项目内确定性触发；本运行环境创建真实 Windows 目录链接需额外权限，因此没有创建真实链接。

正式 `command_delivery_review` 仍为 **BLOCKED / 未关闭**：窗口材料要求执行器与判定脚本经独立审查且命令可复制执行。本轮交付仍只是无命令 dry-run 与防覆盖校验，未实现/审查板级执行器，没有获得真实结果记录接口，也不将离线自测、回放或包装检查升级为实物验收。阶段4真实结果接口、阶段5动作回执接口、`P_meas`、实物授权与窗口等缺项保持原状态；T6-A03、G3、6-E 实物、G4/G5 均未通过。
