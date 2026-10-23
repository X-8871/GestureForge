# w4 接续认领说明（DSH 项目总控，2026-10-24）

## 1. 依据

- Wong 2026-10-24 决定：**「由DSH接手」**（记录 `report/evidence/CTRL-DSH-HANDOFF/decisions/stage_3_4_direction_20261024_r01.md`）。
- Codex 侧已按 Wong「先完成当前小程序然后结束现阶段的任务」停止写入 `w4`，并提交 `d13610d`「save reviewed frame unit and offer w4 to DSH」。
- 跨方通报：`report/evidence/CTRL-DSH-HANDOFF/dsh_mailbox/DSH-20261024-004-stage3-window-j10-scope-w4-takeover.md`。

## 2. 为什么出「接续记录」而不是直接认领

对 Codex 原让出记录 `report/evidence/CTRL-DSH-HANDOFF/codex_offer_20261024_r01/handoff_record.json` 的只读核验结果为 **`HANDOFF_FAILED`（PASS 7 / FAIL 2 / SKIP 0，退出码 1）**：

- **[FAIL] 检查项 a**：记录声明起始提交 `d4f30e35937efed07c4f3ff62393e2e3a6a2ebdc`，实际 HEAD `d13610dd16655beef3ff73dede02d4c6bcade009`。原因是**记录写在其自身那次提交之前**，故声明值为父提交。
- **[FAIL] 检查项 g**：原证据入口缺 `manifest.json`。

按「历史记录不匹配 HEAD 时应由记录所有者更新，不能伪造通过」的规则，DSH **未**强行认领；依 Wong 的接手决定，以**本接续记录**据实更正 `base_commit` 为承载该让出的提交 `d13610d`，并在 `record_correction` 字段逐项留证（含原值、更正值、原因、原核验结果）。**未改动 Codex 任何文件、未回退任何提交。**

## 3. 认领后的边界

- **12 项未提交改动**归属保持 Codex 文献口径：本轮代码与证据已随 `d13610d` 保存；未跟踪 6 ELF/6 map 为 Codex 本机恢复产物（见原记录 `local_outputs.json` 的声明），**留原位、不入源码 Git、DSH 不删不覆盖**。
- **硬件使用权不随工作树交接**：阶段4 板级工作依 `CDX-20261023-019` 本轮暂缓；恢复时由 DSH 在 main STATE 签发正式硬件 OFFER（格式见 `CDX-20261023-018` §4）。
- DSH 接手后由**单一阶段4 写入方**继续；主目录暂存/提交仍由 DSH 串行执行。