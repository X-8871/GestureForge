# 遗留任务离线交付就绪：精确清单，请DSH串行提交并回传SHA

遵守DSH-020，不自行git add/commit主目录或w6。w6 HEAD仍 `892d944f6a1c04a8956fce200f9edc416edce8c6`，本轮新源码/证据与既有历史差异分开。

## 待提交范围

- 清单：`D:\codex-worktrees\w6\report\evidence\CTRL-LEGACY\residuals_20261031_r01\submission_inventory.json`。
- 清单文件SHA：`6e761828ff2c1b38e24f48ed44c41e3ba0fa3031e749451c78a0f1e604a2fa8e`。
- 清单列出**85文件、540434B**，三个限定前缀为 `legacy_codex_20261031/`、`report/evidence/R03-M3/`、`report/evidence/CTRL-LEGACY/`；请逐项核对SHA后仅提交这些85项和清单本身（共86文件）。本清单是提交前工作区身份快照，**尚非commit_blob交付manifest**。
- 不包含：STATE历史增量、两份S6-A旧规格差异、14旧RunId、其他工作树/main业务文件、ARM临时编译目录。R-08新STATE段如要提交请按差异精确分离，不整文件混入历史改动。
- 稍后新增的根因独立复审报告将单列补充，不自动扩大当前清单。此处列项的实现/证据已停写。

## 当前结论与验证

| 任务 | 结论 | 证据及数字 |
|---|---|---|
| R-08 | PASS | OFFER11字段、19项归属；DSH020 CLAIM关闭；C1归位892d944 |
| R-03工具 | PASS | 源码独立审查、43 mock测试exit0、官方bat与Job收尾绑定 |
| R-03真实M3 | BLOCKED | 01:20:08.792615–01:21:08.245793，59.453秒；CPU0 Running前置失败，capture NOT_RUN；两核stop收尾/零残留，006/007已交还板卡 |
| R-03不自洽根因 | 离线诊断完成，独立复核中 | 精确失败ELF ada4b30d实际写400周期（8µs@50MHz）；done=2跳过比较，diff初值0不表示相等；3份历史有效样本有HEADS行/47287ms/尾word5A5A0506。见R03-M3/m4b_rootcause_20261031_r02 |
| R-05/C2 | PASS离线，板上BLOCKED | safe14@+100，PS5.1/7回归exit0、r02独立复审PASS；新增GCC13.4 Cortex-A9编译exit0且锁字单次STR，仅代码生成结论 |
| R-09/C3 | PASS | 11单测exit0、r02独立复审PASS；P=16673.669516µs为VDMA显示读帧代理，不是相机P |
| R-09/C4 | FAIL / CHANGES_REQUIRED | 复审报告已交，旧S6证据阻断详005与C4_R02_review_20261031.md；未改冻结物 |
| R-02②/④ | 论证与建议已交 | 原Stage3 SEC仍BLOCKED；仅当前S5/S6限定scope可论证N/A；无ILA替代分层取证在报告内 |

验证汇总SHA `081300c21e01d1c08e7dc43c38650585b5836a617e99938ad2689c35d0a27831`；ARM记录SHA `94d1b43bf3e621692bc8fff6cf3fd757eac485c35ddf5e95980e2986f0f8967d`。

请DSH按交接约定核验并串行提交w6这86文件，回传完整提交SHA。我方随后只在新目录生成权威 `hash_basis=commit_blob` manifest，逐项用 `git cat-file blob <commit>:<path>` 计算，并运行统一strict门禁；再将新manifest与检查结果精确交DSH提交。**提交和strict尚未完成，当前不声称全部交付已完成。**

仍未收到新M3 OFFER，不重新开硬件会话；R-01未处理，ENABLE=0、不push、不写QSPI、不改阶段5/6冻结物。
