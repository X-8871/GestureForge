# Report Package

保存设计报告、指标汇总、复现说明和大模型协作记录。中文可出现在报告正文中，但工程目录和文件名保持英文。

建议后续建立：

- `design_report.md`：设计报告初稿。
- `metrics.md`：指标汇总和测量条件。
- `reproduction.md`：从零构建和运行步骤。
- `ai_collaboration.md`：仅在正式竞赛提交需要时整理有价值的协作案例、自我纠错及最终采用结果；不作为逐轮 Agent 消息队列。

当前规则和状态分别在根 `AGENTS.md` 与 `.codex/STATE.md`。开发与审查通过 subagent 消息交接，不新建 handoff、todo 或 review 接力文档。保留 `evidence/` 中可复核的实验、整改和人工观察证据；历史交接文件清理及 Git 取回方式见 [仓库同步说明](../docs/仓库同步说明.md)。
