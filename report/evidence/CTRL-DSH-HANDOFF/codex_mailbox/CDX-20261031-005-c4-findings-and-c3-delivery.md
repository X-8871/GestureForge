# C4独立复审、C3交付与M3时间口径

- C4/R-02固定原冻结版复审结论 **CHANGES_REQUIRED**，报告 `w6/legacy_codex_20261031/c4_r02/C4_R02_review_20261031.md`，SHA `3f6efbf4567a92ceea19aeb4f7905080673ef35ad0986412352eb16998a19a43`；未改冻结物。主要问题：旧sidecar重叠（已由新rev3安全14修口径，但不追溯原证据）、奇数锁未先flush/消费者取锁在invalidate之前、跨POR唯一session未证明、真实推理未接入、E2显示读帧proxy不能当相机P、E5原FAIL与严格30min有效跨度矛盾。Stage5按限定DDR fixture显示范围可scoped PASS，freeze tag指针与主STATE存在不一致，详报告逐项位置。
- E5关键数值：有效result_time首末1006368→2804568ms，跨度**29分58.2秒**；host窗口约30分23秒不能替代有效业务跨度；原判FAIL/exit1、vdma_err=3695185等失败记录须保留，不得以包装门禁PASS替代。
- C3方法学与离线采集分析已独立复审 **PASS**，11单测exit0。16673us实为6沿/5间隔、平均5,557,890 GT ticks，复算16,673.669516us；原样本缺逐沿GT，不能复算抖动或严格轮询上界。报告 `c3/方法学.md`；独立复审 `c3/review_new/review_c3_r02_20261031.md` SHA `65ad17cb3fc48507a89c555bcb86ece65d0b9085474e9480c635d3037b2ea3948`。
- R-02②：SEC是sequential equivalence checking，原task-11仍Stage3 BLOCKED_NOT_RUN，不能自动豁免；仅对不含相机wrapper的S5/S6限定交付可论证scope-specific不适用，供Wong裁决。④无ILA替代建议及证据强弱层级在C4_R02报告，不把建议当实测。
- M3：004心跳01:18是预填计划标签；该信实际已在本机时钟约01:16:56写入，**不是硬件开始时间**。唯一开始门禁仍01:20，当前无硬件会话。实际起止以本次Job运行记录与前后快照为准，不使用手填计划时间冒充实际。
- 后续源码/报告请按待提交清单+哈希由DSH串行提交；我方继续遵守不自行git add/commit。C2修复轮独立复审中，板上仍未执行；M3板窗只用于批准保持事件，不夹带C2/C3。
