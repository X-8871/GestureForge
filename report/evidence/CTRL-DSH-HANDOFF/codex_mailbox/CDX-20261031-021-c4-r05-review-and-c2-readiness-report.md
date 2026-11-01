# C4 r05 增量 CHANGES_REQUIRED / C2 准备度 BLOCKED：补充清单

承接 CDX-019，以下两份报告已停写；没有操作硬件、修改被审冻结物或 Git index。

## C4 独立复审

- 报告：`D:\codex-worktrees\w6\legacy_codex_20261031\c4_r02\C4_r05_incremental_20261031.md`；SHA `4e8f62af6388bfe126645456325e53ded5ad7bb9edb8b033f045ab94a4a6a101`。
- 固定 main `35c45778d2473faea41f16da014ba33e8e031bda`、w4 `e22fccf8cc8bbd0ccc8b20c4289c3244b0508c2a`；核查命令 exit 0，审查结论 **CHANGES_REQUIRED**。保留两份旧报告。
- r05 已补 s1/s2 字段和 POR 满足运行标记；这些局部缺口关闭。
- 未关闭：实际 rev5 ELF/源/构建记录未在 r05 commit_blob manifest 绑定；临时目录源码之后已变化，不能从当前临时文件重建该次 ELF 身份。相同偶锁正样本不证明写奇锁 flush/DSB、读 s1 前 invalidate 或所有交错下无撕裂。
- r05 `delta_vs_inf_ms=26.234`，不是文档/026 所述17.7；`result_time` 采于最终 flush/偶锁发布前，与“最终发布可见”语义尚不一致。
- E5 仍 FAIL。G4/G5 增补虽披露 FAIL，同文仍保留旧“E5 链路 PASS/全绿”并称 G5 冻结，需明确替代旧结论并按验收标准处理。E6 是真实板上模拟框 producer，不能称真实模型结果。

## C2 准备度

- 报告：`D:\codex-worktrees\w6\legacy_codex_20261031\c2_integration\C2_REAL_APP_READINESS_20261031.md`；SHA `0dd279191cb2e235d044be5c2a9ef91538b499022ccbfa0f6b1fbf69a277d84c`。
- 包含固定 Chain-B/renderer/ABI/G0 的完整 commit_blob 身份、接入点、可信 previous SID/cap GT/匹配部署包缺口及 infer_done 事件冲突。未改已审 C2 库或旧计划；报告明确旧 decoder-return 接入建议在冻结事件对齐前不得执行。
- 整体板验 BLOCKED，不能承诺≤1天；按019建议由DSH做最小组合兜底。只读核查，不是新实现或板上通过报告。

## 可串行提交的精确范围

清单 `D:\codex-worktrees\w6\report\evidence\CTRL-LEGACY\review_followup_20261031_r01\submission_inventory.json`，SHA `94d4c5c928e8df7c66c28f01f97863a287373f191bd6300d5bb6f98cec9839c5`；**内列2文件 + 清单自身 =3文件**。这是提交前 worktree_disk 附注，尚不具交付权威性；请 DSH 核验后串行提交并回 SHA，再建 commit_blob/strict。

015 的11文件清单仍有效；017已由020暂停，等待M3顺序门禁修复与复审后的新清单。没有有效 M3 OFFER，不开窗。
