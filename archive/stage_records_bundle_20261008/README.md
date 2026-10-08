# GestureForge 阶段资料包

整理快照：2026-10-08（UTC+8）。本目录收集阶段一的正式记录与完整 T01/T02 证据，以及阶段 2A 的冻结验收核心材料。它们是原件副本；仓库原始路径仍是权威来源，没有移动或删除原件。

## 阶段一

- 正式记录：`stage1/docs/`，含《阶段1_实施步骤与决策_最终产物_20260922》《阶段1_PC范围冻结补充_20260922》及 S1-T02 D2、D3、D6 文档。
- 原始证据：`stage1/evidence/S1-T01/`（6 个文件）和 `stage1/evidence/S1-T02/`（29 个文件）；完整复制，未只挑摘要。
- 最新总控盘点指出：PC 范围冻结记录存在，但硬件侧完整算子/张量清单和系统级 PS/PL 接口资料仍缺。此资料包不构成阶段 G5 验收结论；历史收尾记录仅供追溯。

## 阶段 2A

- `stage2A/stage2a_g4_g5_acceptance_20261005.md`：阶段冻结验收记录。
- `stage2A/acceptance_audit_repair109_20261003_194620.json`：机器可读审计证据。
- `stage2A/batch_summary.json`：109 样本恢复批次摘要。
- `stage2A/` 内另含 S2A-T01 模型交付规格与 G0 接口冻结文档。
- 完整历史证据不重复复制：原件仍在 `archive/S2A-T68/`、`archive/S2A-T25/`、`archive/S2A-Support/`；本次只复制冻结结论与关键审计摘要。验收记录中的限制（包括时序约束和完整网络重跑范围）应以冻结报告原文为准。

## 阶段 3（进行中，未冻结）

- 独立工作树：`C:/Users/22061/.codex/worktrees/dbdf/FPGA_Competition`；分支 `codex/stage3-video`；核验时 HEAD 为 `896e6c7a6bae9571303cd65e08c6176c6baebd12`。
- 核验时有 5 个已修改跟踪文件：`.codex/STATE.md`、`board/stage3/README.md`、`board/stage3/hardware_photo_evidence.md`、`board/stage3/prepower_check.md`、`scripts/s3_implement_hdmi_only_diag.tcl`；另有 4 个未跟踪项：`NA/`、`clockInfo.txt`、`docs/adr/ADR-0002-stage3-gitbash-runner.md`、`scripts/stage3_t03/`。
- `tmp/s3r04/` 含 `.Xil`、Vivado 工程/运行目录、DCP 检查点、报告、lease 状态文件和 T03 构建/测试目录。均属于活动诊断或可恢复性材料，暂不清理、不打入冻结包。
- 以上状态是 2026-10-08 的快照；阶段 3 总控仍需按其正式计划完成 T03、审查和验证后再决定归档范围。

## 根目录日志整理与保护项

- 13 个 2026-09-26 至 2026-09-30 的 Vivado/XSim `.jou`、`.log` 和 `.str` 文件已从工程根目录移入 `archive/root_tool_logs_20260926_20260930/`。日志含历史仿真 PASS 哨兵，因此采取可恢复归档而非删除；整理时未发现 Vivado/XSim 活动进程。
- 主工作树仍有用户/阶段任务未提交的跟踪文件修改；另有大量未跟踪证据/归档内容。两个 S2A-T68 Vivado 子目录拒绝读取。除上述 13 个根目录日志外，没有清理、覆盖、暂存或提交这些现存改动。
- 阶段 1、2A、3 的最新总控窗口均已取得信息，不需要为本次整理恢复旧归档窗口。只有在某项正式证据确实只存在于旧窗口、且仓库/归档中缺失时，才按具体缺项调阅。
