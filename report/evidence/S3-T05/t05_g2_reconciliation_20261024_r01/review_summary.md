# 阶段3 G2 修订包状态

- 上轮独立审查：`CHANGES_REQUIRED`。
- 本轮已补 r02 材料、旧文件勘误、跨树 Git blob 绑定和 VDMA 位拆解。
- 当前状态：`PENDING_REVIEW`；无 Reviewer 对 r02 的独立 PASS/CHANGES_REQUIRED 结论。
- task-11 静态 LUT4：`PASS_STATIC_THRESHOLD_DECODE`（262,144 组、0 差异）；RTL↔网表顺序等价：`NOT_RUN`。
- VDMA：`PARTIAL`；W1C 后 `0x11000` 仍为 count=1 + `FrmCnt_Irq`；根因 OPEN。
- Wong 目视与 31m15s 耐久是已完成证据，不关闭完整 G2。
- 阶段3 G5 未通过、未冻结；TIMING-17/36、C2/I/O delay、ILA 和顺序等价仍按清单保留。
- 仅改本 RunId 与 `.codex/STATE.md`；未碰主仓、业务代码或硬件。本任务不提交。

包装检查若 PASS，只表示清单/哈希/目录一致，不代表独立审查通过。
