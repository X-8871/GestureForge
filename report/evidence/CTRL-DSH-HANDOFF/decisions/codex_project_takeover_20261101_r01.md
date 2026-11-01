# GestureForge 项目管理权接管决定

生效：2026-11-01（UTC+8）；接管前基线采集：2026-11-01T12:08:46+08:00。

Wong 原话：「现在修改文档，所有项目由你接手，取消DSH最高管理权」。本记录是用户直接指令落实，非 DSH 让出回执，不等待 OFFER 或伪造 CLAIM。

## 当前权限

Wong 保留最终决策与明确审批权。Codex 是 GestureForge 唯一项目最高总控，接管所有阶段（0/1/2A/2B/3/4/5/6/7）、吞吐候选 w2c、主目录及下表全部工作树的管理与写权分派、任务生命周期、独立审查组织、Git 串行提交和资源/板卡窗口协调。

撤销 DSH 的最高管理权、全局否决权、主目录/阶段默认独占写权、唯一硬件调度权和必须由 DSH OFFER/提交的前置权。DSH 未获 Codex 新委派时不再修改、派卡、提交或开硬件窗口。此前相反权限、旧委派和旧租约作为历史保留，不再自动续用；不删除信箱或原始证据。

本次仅修改管理文档，不启动技术开发/构建/板测，不结束 DSH 或其他进程。既有单写者、资源检查、独立审查、冻结证据和明确硬件授权继续有效；管理权切换不是新的板级窗口授权，不授予清理、覆盖既有未提交内容或更改验收判据的权限。未实际核实的阶段技术完成度保持原证据状态。

## 接管前工作树快照

| 工作树 | 分支 | HEAD | Git 报告状态记录数 |
|---|---|---|---|
| `D:\FPGA_Competition` | `main` | `fc66d029d7ee769382fcefb0e50de65f8e6ca219` | 475 |
| `C:\Users\22061\.codex\worktrees\stage7-system-acceptance\FPGA_Competition` | `codex/stage7-system-acceptance` | `615fa46e4c9e8c54685998a5dc041ff24875dae9` | 0 |
| `D:\codex-worktrees\96a3` | `codex/stage2b-t01-board-audit` | `e26feea45b434ba62727c090e08dee33a297102f` | 377 |
| `D:\codex-worktrees\dbdf` | `codex/stage3-video` | `c2cce5d92c1fa27f7124dad204625f5af4846bb2` | 4 |
| `D:\codex-worktrees\w4` | `stage4-infer-prep` | `e22fccf8cc8bbd0ccc8b20c4289c3244b0508c2a` | 212 |
| `D:\codex-worktrees\w5` | `stage5-display-prep` | `2decd0dc2e2204ee60dceead4c30f091d039081d` | 0 |
| `D:\codex-worktrees\w6` | `stage6-interact-prep` | `f0fab846304aec4aa1baeeb012f9ce2888e86812` | 42 |
| `D:\FPGA_Competition\w2b` | `codex/stage2b-dma-g0` | `07c3d3958578b9cc9d3b8eae3758711fe08724c2` | 182 |
| `D:\FPGA_Competition\w2c` | `codex/stage2c-throughput` | `ab5084a027cc6fc520bea5bd20937797f9820557` | 2 |

快照时九树均无 index.lock，暂存区均为空。Get-Process 未返回 Vivado/XSDB/hw_server/Vitis/XSCT/XSim，3121 监听查询无结果；未据此宣称其他聊天已停写或板卡生命周期已复核。w6 status 查询存在既有权限/长路径警告，表中仅为 Git 实际返回数，不当作所有文件完整审计。

原始状态清单和管理文档备份：`C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\governance_takeover_20261101_r01\`；目录 0–8 对应上述表序。机器身份记录见本目录 `codex_project_takeover_20261101_r01_baseline.json`，每个文件哈希明确 `hash_basis=worktree_disk`，不是 commit_blob 冻结身份。

所有现有未提交内容保持原作者/任务归属，不因写权接管而变成本轮修改；特别是 w6 的既有 STATE 差异保留在工作区，本轮各树只提交管理声明。旧技术正文按文本保持，旧冻结标签不移动。

## 执行与恢复

各树 AGENTS/STATE 顶部设置本次优先声明，根 AGENTS 更新现行治理、写权与提交规则。当前治理从根 `D:\FPGA_Competition\AGENTS.md` 和 `.codex/STATE.md` 恢复，不继续把旧 DSH 主控记录当现行权限。

本次提交逐树串行，只纳入此次管理声明及本记录；w6 精确暂存新增声明，保留其原 STATE 修改未暂存。若重读显示 HEAD、索引或管理文件被其他写入改变，停止该树提交并重新核对，不 reset/rebase/clean、不清理他方内容。恢复只读命令：`git --no-optional-locks -C <上述精确工作树> status --short` 与 `git --no-optional-locks -C <上述精确工作树> rev-parse HEAD`；锁路径必须用 `git rev-parse --git-path index.lock` 解析。
