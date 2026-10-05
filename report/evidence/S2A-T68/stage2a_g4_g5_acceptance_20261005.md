---
type: acceptance_record
domain: embedded
status: g4-g5-review-pending
created: 2026-10-05
updated: 2026-10-06
---

# 阶段2A PL推理仿真 G4/G5验收与冻结记录

> 本记录是冻结候选，不代表阶段已经通过。Wong 于 2026-10-06 明确选择最新版阶段计划作为 2A G4 控制要求，因此综合、资源可容纳性与时钟风险报告均为必需项；这项决定协调了该计划与 T01 G0 原有“不含综合或资源通过声明”的范围差异，但不改写 T01 冻结文本。109 样本结果、算子证据与归档已核验；所有适用关口由独立 G4/G5 Reviewer 返回 PASS 后，才能记录冻结结论。

## 范围、架构与版本

阶段范围为冻结规格 T01 的 tiny416 PL RTL 推理和 PS 后处理参考比较。网络为 38 个 cfg 层、21 个卷积层、109 个固定输入样本。Wong 已批准 8×8 空间 tile、8 路输出通道并行；CSR 语义、32-bit 单 word memory 接口、timeout 与握手协议沿用 T01 冻结定义。此记录不把仿真结论外推为 DDR/AXI 实现或 FPGA 资源结论。

PL 编译源码的闭包基线为 commit fecbf1f8f37fcee8b25e6e2517b9621850912a4e，Git tree 094e1492396a6788cc33b3b5866dd304387c02da。闭包含 38 项，11 个编译 RTL/TB 源和 3 个编译工具源均按运行快照绑定；源码映射报告同时核验这 14 个当前编译文件与冻结闭包。2A 汇总代码基线为 commit 65dd1c310e7686d50685d2f83b9b2b623e6cf3ad；后续验收文档提交只增加记录，不改变被测 RTL。工作区中其他阶段的未提交改动不属于本冻结版本，未混入本轮提交。

## 验收结果

| 验收项 | 实际结果 | 证据与结论 |
|---|---|---|
| 冻结输入与规格 | 使用 T01 tiny416 清单和固定输入清单，109 个样本索引 0–108；样本输入与权重由逐样本 fixture manifest、输入文件 SHA 和 common GF8 权重 SHA 绑定。 | T01 G0 文件、T68 运行夹具及其归档清单；通过。 |
| cfg 算子与共享 MAC 专项 | 21 个卷积层各 1,000 随机输出查询 + 16 定向查询；11 个 route 层各 1,000 随机空间用例 + 16 定向用例，全部输出通道逐元素检查；maxpool layer9/17/25 各 1,000+16；upsample layer33 1,000 随机 + 16 定向用例；两 YOLO head 各 1,000 随机 + 16 定向用例。共享 MAC 另有 1,000 随机点积 + 16 定向向量和 INT64/INT32 溢出审计。 | 新 tile 卷积数值详见下一行。历史算子记录：T02 `mac_unit_simulation.json` SHA-256 a7b909b4d4dbf87d381a89e8b1ed3f80952a0d5ff54c699eee134b945ddcc282；T08 `yolo_view_query_simulation.json` SHA-256 14e8fe5f22061e8a8d1f74c8a5bc725e2ff5f7b0975e499440dff085799f7198；T13 `upsample_simulation.json` SHA-256 ee9c1c0cdd4500eac6398ef0eb0a893021aee3b66d4845e50930f7cfac15d04e；T14 `maxpool_simulation.json` SHA-256 2e681fb5db9037f6858c7516b4620053374d571e66d27c15ded6dfbffb8927e3；T15 `route_simulation.json` SHA-256 6011c3272c05b8e428128410b0d7a25a689873a12404631f23dc707f1fa9f124；均 PASS。它们的被测范围和限制依原报告；串行 T17/T20 不替代新 tile 回归。 |
| 新 tile 算术 | T70 对 21 个卷积层各执行 1,000 个随机与 16 个定向输出查询，共 21,336 次查询、169,790 个 lane 检查，零差异。 | report/evidence/S2A-T70/whitebox_diagnostic03/summary.json，SHA-256 d1d50e5a8b4a77635d4681131b19917d4e11a7702a60a1bc116c3b8034c50e4b；PASS_WHITEBOX_ARITHMETIC_ONLY。它只证明算术查询，不代替 memory 或完整网络。 |
| 新 tile 内存 | T70 覆盖 21 层 × 每层 16 个定向情形，共 336 项、147,896 输出字节、56,740,684 cycles，零差异。 | report/evidence/S2A-T70/memory_full01/summary.json，SHA-256 bb20447a555e70fee8b44d6372ca5a3e6f526bfd0240c53b76ffdeed0fdf0bd1；PASS_SELECTED_TILE_MEMORY_ONLY。 |
| 边界与异常 | T70 对实际 layer29/36 完整生产输出遍历及 8 类异常情形运行 12 次仿真，编译和仿真退出码均为 0。 | report/evidence/S2A-T70/boundary_full01/boundary_report.json，SHA-256 6464f04bdbac98cfdb8cc36f8d1d1c62129603e3885113396bdd5234e724ec63；PASS_FOUR_HEAD_BLACKBOX_AND_EIGHT_EXCEPTION_CASES。 |
| 109 样本完整 PL 网络 | 109/109 个索引各有独立 compile、simulation、source snapshot、result summary、head13/head26 与 fixture manifest。每份结果覆盖 cfg 层 0–37（36 个 materialized tensors + 2 个 alias rows），PASS_LAYERWISE_EXACT_GOLDEN，feature_write_bytes=11,382,150，mismatches=0；compile 与 simulation/runner 退出码均为 0，head 导出及进度标记有效，无 watchdog failure。每样本 cycles 均为 972,865,374；head13/head26 分别为 5,070/20,280 字节。 | report/evidence/S2A-T68/acceptance_audit_repair109_20261003_194620.json，SHA-256 17cd8778ca8c83e0d7efd14f664bd7167cc102894b85c1d564d8b7872eee5939；PASS_109_SAMPLE_ARTIFACT_AUDIT。 |
| 批次与失败处理 | batch_summary 的 `status=PASS_108_RUNNERS`、`stage2a_pass=false` 只涉及 coordinator 调度的索引 1–108；sample000 是同一 RunId 下单独成功的记录。逐样本 final audit 明确核对并合并两者，未把 coordinator 摘要误称为 109 样本 PASS。初始 unattended 状态 STOP_BATCH_FAILED、首次 recovery 状态 COORDINATOR_ERROR 均保留；recovery2 在不重跑 PL 样本的情况下完成 D9。更早 RunId repair109_20261003_124125 未计入通过数。 | batch_summary：report/evidence/S2A-T68/repair109_20261003_194620/batch_dispatch/batch_summary.json，SHA-256 93cb51989c98fdb074c5c5857acd9842ee7902c8a27d09c655ae555c41ac2e38。初始/恢复/恢复2 记录依次为 `unattended_continuation_repair109_20261003_194620.json`（SHA-256 8eec0d708ecec9c63de9d187e4ff31348c48bb9d08a6d2998617e86158666b93）、`unattended_continuation_repair109_20261003_194620_recovery.json`（SHA-256 4c187dda223209d2a4308dd7fbe210f34ff5be06bb2cce624229cc477e664cda）、`unattended_continuation_repair109_20261003_194620_recovery2.json`（SHA-256 7d40d458af3cc15f1df3fb2da89b15bbe507f9d235c2ddd488bd4e8a0b9a13b7）；均在运行证据目录且由归档清单覆盖。 |
| 实际 PL heads 对 CPU D9 | 109 样本全部比较通过；检测项精确输出 PASS，最大 score 绝对误差为 0，最大 xyxy 坐标绝对误差为 0。 | report/evidence/S2A-T68/repair109_20261003_194620/d9_109_sample_report.json，SHA-256 6e8d3d6366928bec78990f0de4cce3403e167331736f86ebb8c57b8ea48486ce；PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9。 |
| 源码版本映射 | 109/109 编译快照映射到固定的 38 项源码闭包和冻结 Git tree。 | report/evidence/S2A-T68/repair109_20261003_194620/source_snapshot_git_binding_repair109_20261003_194620.json，SHA-256 c4f2d66fd5354fb721151d70b7aff9236a78094c6a74c5ee76a9a2107621c681；PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE。闭包报告 report/evidence/S2A-T68/static_source_closure_20261003_worker_crlf.json，SHA-256 9920c8f782677de1fb38053ae5357f517b8f24526ccb9edab816a56b72830244。 |
| 控制与协议回归 | T68 protocol_directed05/06 均 exit 0，覆盖真实 backend memory error 6/7 映射、pending write 的 reset/timeout 取消、无迟到副作用及恢复；protocol_directed06 保留 backend_fault_recovery.vcd。 | 两份 simulation_execution_record SHA-256 分别为 a8bc5d01d0207f686fe60f0770f94ef371be48c7a11aa2bedb62d5059f1ab299、af485300153aa67a397d557f30ca3d101867b19a4e282fe764a43d6ff1710b26；VCD SHA-256 e08b209e00c467b9571e96f723025fe59930db0721463404a18fe6459b4b1c5f。既有 T02/T08/T10–T21 结果按原始范围复用；T17/T20 是历史串行 engine/pilot，不作为新 tile 的同等证据，新 tile 以 T70 和 109 网络结果验收。 |
| 干净副本恢复 | T25 在干净 Git 副本实际恢复 109×38 CPU shard，恢复 exit 0、耗时 2,283.61 秒；CPU D9 canonical replay 109/109、exit 0、耗时 12.359 秒。固定环境 Python 3.12.10、NumPy 2.4.6、OpenCV 4.13.0。 | report/evidence/S2A-T25/clean_restore_20261002_160036/recovery_execution_record.json，SHA-256 021a11d5318ea599216aabe8cb0d065e75d735573e29a5b4a4a0fb9ad97806a7；final_evidence_integrity.json，SHA-256 af57636d75872df1c604e1e06496b600b2ccd2a3644be4ae7b99abd7d19e406a。该项证明 CPU oracle 的真实恢复与重验，不声称在干净副本再次执行了完整 109 样本 PL 仿真。 |
| 冻结 PL 源闭包干净副本编译 | 从 commit fecbf1f8f37fcee8b25e6e2517b9621850912a4e / tree 094e1492396a6788cc33b3b5866dd304387c02da 重建 38 项源闭包并逐项验证 Git blob；T68 现有 runner 对固定 sample000 重新生成夹具并完成编译，exit 0、65 warnings、0 errors，source/tooling 未变化，simulator_started=false。 | report/evidence/S2A-T68/g4_synthesis_20261005/clean_restore_fecbf_20261006/clean_restore_execution_record.json，SHA-256 b8b7e9dea7e6d321080ebd8276728ad7093dfdd286fe8a68a906e02a1fcd05af；编译记录 SHA-256 731abc855e9ca01eb960e38d6d1ae198f4be66890d522a1206bb934b85d8496b；Verilator 5.050。此项证明冻结源副本可恢复并编译，不替代综合或完整 109 样本仿真。 |
| 证据归档与复现 | T68 归档复制 2,416 个非构建文件、1,323,413,060 字节；T25 归档 126 文件、417,152,290 字节；tile/协议支持归档 41 文件、214,836,577 字节，所有纳入文件逐项 SHA-256 匹配。准确 archive 路径与完整文件清单在三份 archive manifest 中。 | T68 manifest SHA-256 9b4d90c7d0aad70dc89bf0e78af6f74c9d0cacd6a002f46aa18afec6ed266bdf；T25 manifest SHA-256 9249b07f004de4fba196212a8617b987088b1e85d54e761b033ef03be84a9631；support manifest SHA-256 bd32ea5f8949bb63239f6120325fa41480916704572e287ee6ad3e789cab4900。所有归档都在 D 盘同一物理卷，不是异盘备份。 |

## 关口判定

- G0：T01 模型、数据与接口冻结有效。
- G1/G2：候选实现有当前 tile 专项算术/内存/边界证据，完整 109 样本零整数差异，并绑定固定源码版本；最终独立审查待签。
- G3：不适用。2A 不含上板或实物操作；T01 未授权烧录或板卡操作。
- 综合、资源与时钟风险：按 Wong 2026-10-06 的范围决定，综合无错误及非预期锁存器、资源可容纳性和时钟风险报告均为 2A G4 必需项；当前仍未验证。7 次启动诊断汇总见 report/evidence/S2A-T68/g4_synthesis_20261005/vivado_bootstrap_attempts_20261005.json（SHA-256 5eadd3296ef16752d34e24675761ae09993c2add058a82b7ccd1286fe9443028）：5 次有效许可的 batch 综合启动和 1 次 -init 启动探针均在 load_features / Tcl Store 功能加载阶段失败，项目综合 Tcl 未执行，未生成 utilization、timing/clocks、锁存器清单或 DCP。尝试包含默认用户环境、空隔离 APPDATA、复制的完整 287 文件 Tcl Store 缓存，以及只在隔离副本移除 .tcl_store_lock；错误一致。无效许可的第 2 次尝试不用于判断 Tcl Store。原始用户 Tcl Store 和全局设置均未改动；被测 RTL 输入已从冻结 commit fecbf1f8f37fcee8b25e6e2517b9621850912a4e 精确复核 10/10，但这不能替代综合结果。AMD xsetup.bat -b ConfigGen 探针因当前 shell 缺少管理员权限退出（未生成配置、未修改安装），详见 report/evidence/S2A-T68/g4_synthesis_20261005/installer_configgen_probe_20261006.json。不得把资源、锁存器或时钟风险记为通过。
- G4/G5：仍待 Vivado G4 证据和独立 Reviewer 对本记录、运行报告、历史适用性与归档恢复入口返回 PASS 后，才可记录冻结结论。独立 Reviewer 未找到要求重跑完整 109 样本 PL 批次的明确硬门；原批次保持不动。本次已在冻结 commit 的干净副本恢复 38 项源码闭包并完成 sample000 编译，但未在副本重新运行 full network，也未重启原批次。

## 本地恢复入口与限制

T68 运行证据归档目录：D:\FPGA_Competition\archive\S2A-T68\repair109_20261003_194620。CPU oracle 与恢复记录归档目录：D:\FPGA_Competition\archive\S2A-T25\clean_restore_20261002_160036。当前 tile/协议回归归档目录：D:\FPGA_Competition\archive\S2A-Support\Stage2A_20261005。三个目录及源均在 D 盘同一卷，目录之间逐文件校验通过；发生整盘故障仍需从原始输入、冻结 Git commits 和已归档输入重新恢复。

109 个大编译 build 缓存以及 4 个 T68/T70 可重建 obj_dir/build 缓存已从源目录清除，合计释放 33,104,952,077 字节；归档保留了结果、日志、波形、输入、快照和重建所需材料。工具记录为 Verilator 5.050（2026-07-01 rev vUNKNOWN-built20260702）。不清理失败批次、T70 结果输入、T25 shard 或其他阶段文件。

最终结论字段：待独立 G4/G5 Reviewer 签收后补记。
