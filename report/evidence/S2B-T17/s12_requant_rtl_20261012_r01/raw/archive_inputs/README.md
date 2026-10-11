# Report Package

保存设计报告、指标汇总、复现说明和大模型协作记录。中文可出现在报告正文中，但工程目录和文件名保持英文。

建议后续建立：

- `design_report.md`：设计报告初稿。
- `metrics.md`：指标汇总和测量条件。
- `reproduction.md`：从零构建和运行步骤。
- `ai_collaboration.md`：仅在正式竞赛提交需要时整理有价值的协作案例、自我纠错及最终采用结果；不作为逐轮 Agent 消息队列。

当前规则和状态分别在根 `AGENTS.md` 与 `.codex/STATE.md`。开发与审查通过 subagent 消息交接，不新建 handoff、todo 或 review 接力文档。保留 `evidence/` 中可复核的实验、整改和人工观察证据；历史交接文件清理及 Git 取回方式见 [仓库同步说明](../docs/仓库同步说明.md)。

## 新增产物与阶段输入检查

适用于后续新增交付，不要求把旧阶段证据转换成新格式，也不改变正式验收计划。主仓库为 `D:\FPGA_Competition`；独立工作树在自己的工程根执行相同相对命令。

- 正式文档更新现有 `docs/`；源码和测试留在现有模块。
- `report/evidence/<task_id>/<run_id>/` 只保留可复核的输入来源、实际结果、必要原始日志及诊断/冻结产物。
- 可重建缓存、临时工程和批量调试输出在隔离 `tmp/` 或既有忽略目录，不堆入证据包。
- RunId 不覆盖重跑。失败包独立保留；清理缓存必须先核验运行结束、恢复依赖和授权。

检查器仅使用 Python 标准库，只读文件及 Git 对象，结果输出到终端；不执行清单中的命令，不删除、移动、生成位流或操作板卡。两种模式：`inputs` 核对声明的上游冻结接口和输入绑定；`evidence` 核对当前运行目录及文件清单。运行目录枚举超过检查器文件数上限、文件不可读或校验未完成必须报错，不能当作已完成；大文件仅提示体积风险，不以固定字节数替代任务的空间预算和验收标准。

安全示例模板仍为未就绪状态，下面命令预期返回非零，不能把模板用作 2B 冻结记录：

```bash
python -B verification/check_stage_delivery.py --mode inputs --manifest verification/stage_delivery_template.json
```

本次新增证据的清单放在对应运行目录。下面是占位示例，必须用真实任务编号及 RunId 替换，不能直接当作现有证据：

```bash
python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S2B-Txx/RunId/delivery_manifest.json
python -B -m unittest verification.test_stage_delivery -v
```

清单 `schema_version=1`：记录 `stage`、`task_id`、`run_id`、`source_commit`、`evidence_dir`、`interfaces`、`files`、`checks`、`limitations`，证据包另含 `tool_versions`。接口只引用已存在的正式文档及其版本/哈希；文件按角色列出真实路径与 SHA-256，实际源码哈希绑定待审版本，不能只填写历史提交。适用的波形/检查点逐项填写 `keep_reason`；`evidence` 模式列清当前运行目录的全部文件（清单自身除外）。

确无上游接口时，允许 `interfaces=[]`，但必须显式填写非空、非占位的 `interfaces_not_applicable_reason`；有接口的任务不能用此字段绕过冻结核验。不适用声明是否符合任务范围，仍须正式 G0 和独立审查确认。`inputs` 模式仍要求实际输入文件；没有本地输入的独立任务按 G0 说明 `inputs` 不适用，只对交付证据运行 `evidence`，不伪造接口或输入。

`checks` 分别记录 `PASS`、`FAIL`、`BLOCKED`、`NOT_RUN`、`NOT_APPLICABLE`，并绑定命令、真实退出码及适用理由。随机测试还须在已有业务证据中保存种子、样本数和统计口径。模板/清单不重复定义 tensor、地址映射等业务规格。

`CHECKS_OK` 只代表包装或输入绑定的机器检查通过。完整的 `FAIL` 证据包也可能返回 `CHECKS_OK`；它绝不代表测试通过或 G0/G4/G5。接口冻结的批准依据、需求覆盖、独立审查、集成验证及适用的人工/实物验收，仍由正式 G0—G5 判断。

ROSS 按根 `AGENTS.md` 的任务匹配规则使用：复用归属明确的 Tcl 会话，批量操作、精简返回；普通文件/轻量测试使用 Git Bash。耗时与资源记录留在实际运行证据中，不另建插件使用流水账。
