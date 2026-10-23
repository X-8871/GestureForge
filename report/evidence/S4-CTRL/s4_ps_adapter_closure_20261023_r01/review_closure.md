# S4-B-REAL-02B 独立复审闭合摘要

- 最终结论：PASS（G2，仅离线源码、R13 实际 ARM 构建与 one-shot 控制流证据范围）。源基线 `e1e79fcfcedd653681336e45c323de6ba3ed5558`；打包时 HEAD 记录于 `current_real_gate_snapshot.json`。r04 四源冻结及当前运行书逐一绑定 SHA。
- 初审及修复轮 1/2 的阻断记录为 CHANGES_REQUIRED：授权来源不得由 caller 自证或扩权；成功 RUN 后必须真正 one-shot；stop 前后须安全核对完整 CSR；测试 probe 不得污染 preparation；RunId 比较须精确。
- 修复轮 3 后关闭：main OFFER 与 w4 CLAIM 来自受信、可达且当前未撤销的 Git STATE，并交叉绑定 OFFER commit/blob/SHA/source、RunId 与精确 scope；拒绝重复/多余键和 `_r01`/`_r010` 相似串。成功 RUN 的真实 ARM CFG 为 `trace_end_run(1) -> publish(2) -> WFE 自环`；普通成功命令仍回接收循环。测试 22 adapter / 38 tensor 均 exit 0，prepare/validate 均 exit 0。
- “mock execute 成功”只验证 fake 端控制流，不证明授权或实际硬件执行。当前 main 无本任务 OFFER、w4 无 CLAIM，门禁应拒绝真实执行；JTAG/SDK/UART/板测均未运行，G3/G4 未完成。
- 原始 CHANGES/失败记录和 scripts/probes 留在 `history/`，本包作逐字节副本；来源目录不改写。旧 preparation RunId 中 Reviewer 曾写 3 个测试文件，其原 SHA/归属见 `reviewer_prep_contamination.json`；2 个 JSON 副本已收录，28-byte mock ELF 仅记录且未复制。
- R13 文本 manifest、machine result、commands、工具清单、编译/链接/布局文本日志均收录；ELF/map/init/ZIP/XSA/bit、权重/raw/tensor 和工具/缓存不复制，路径/SHA/本机恢复规则见 `storage_policy.json`。真实 SDK 46000-word 能力仍 NOT_RUN。
- 文档输入保留 DRAFT/PENDING_REVIEW，硬件与 RGB/PL 路径保持阻断。包装 `CHECKS_OK` 不代表 G0/G3/G4/G5。
