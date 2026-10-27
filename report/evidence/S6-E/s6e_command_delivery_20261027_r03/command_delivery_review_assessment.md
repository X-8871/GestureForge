# S6-E `command_delivery_review` 修复轮复核材料

- RunId：`s6e_command_delivery_20261027_r03`（2026-10-27，UTC+8）
- 基线 HEAD：`b50736e6688a4a384f4f2f484872f9e5e59b690a`
- 旧证据保全：r01 原始字节 manifest SHA-256=`9b7df1dc67e45361d3808715490b781139449436e3729b5072d4ddff25f107a2`；r02 原始字节 manifest SHA-256=`f45b290bba3e3c38116a9f0976b0035a28f93468bec62f076b564105b0f747cb`。两者未修改，均作为本轮只读输入绑定。
- 适用范围：输出路径安全与 dry-run 计划的结构/语义完整性；不派发硬件命令。

## Reviewer 的两项整改

1. `plan` 只接受规范 RunId `s6e_command_delivery_YYYYMMDD_rNN`（有效日期、非零序号）；`--out` 仅可省略或逐字匹配 `report/evidence/S6-E/<run_id>/dry_run_plan.json`。拒绝源码目标、既有目录/文件、绝对外部路径及穿越路径。证据根必须是普通目录，检查 symlink/junction，解析后再验证 project-root containment。新目录以 `mkdir(exist_ok=False)` 创建，输出文件以 `O_CREAT | O_EXCL` 独占创建，重跑不覆盖。
2. 对计划顶层、source、每条 case、每条 board gate 执行必需字段与白名单检查。`acceptance_status=PASS`、`real_inference_completed=true` 等未知字段被拒绝；同时固定 `scope_note` / case `reason`，避免借允许的文本字段宣称真实验收通过。严格核对布尔和整数类型。

## 回归覆盖与结果边界

16 项回归覆盖已有源码作为输出目标、外部路径、`..` 穿越、无效 RunId、预存 RunId/输出、相同 RunId 重跑、符号链接/junction 拒绝分支，以及顶层/用例/门禁伪造验收字段。链接分支通过注入检测器在临时项目中触发；运行环境创建真实 Windows 目录链接需要额外权限，本轮未创建真实链接。

正式 `command_delivery_review` 仍为 **BLOCKED / 未关闭**。窗口材料要求执行器和判定脚本经独立审查且命令可复制执行。本轮只有离线 dry-run 计划与计划校验；没有阶段4真实结果命令接口、阶段5动作回执契约或经独审的板级执行器，不生成硬件命令。T6-A03 因缺实测 `P_meas` 仍 `NOT_RUN`；G3、6-E 实物验收、G4/G5 均未通过或未执行。
