# 项目状态入口

更新：2026-10-08（UTC+8）。按根目录 `AGENTS.md` 恢复；阶段验收以当前代码、Git 和报告证据为准。

## 当前目标与阶段

- 阶段2A「PL 推理仿真」已完成 G4/G5 独立审查并冻结。用户已批准 8×8 空间 tile、8 路输出通道并行；保持 T01 冻结的 CSR、32-bit 单 word memory 接口、timeout 和握手协议。
- 用户当前明确启动阶段2B，并允许使用手动启动且 ROSS 已连接的 Vivado 2026.1 Tcl 会话。本轮只完成 G0 只读核查，未通过 G0，未改动硬件工程或进行实物操作。
- 阶段2B G0 阻碍：阶段1模型/检测头和后处理规则仍待冻结；PS/PL 地址映射、AXI/DDR传输、DMA与缓存一致性、缓冲所有权等字段未冻结；当前 AX7020 厂商手册/核心板原理图标称 XC7Z020-2，而板卡照片及用户已有 `.xpr` 改动标为 XA7Z020、CLG400、-1I，不能直接沿用厂商旧 PS/DDR 配置。当前工程无 PS Block Design、Vitis 平台或板级 XDC。
- 先前的阶段3方向保持原代码和文档现状；当前请求仅处理阶段2B。阶段2B 后续任务须先冻结上述接口和器件资料；板卡下载、上电、DDR/UART 实测等实物操作须另行明确授权。
- 2026-10-05 核对最新 Vault 阶段计划源 SHA `a94830afe60ae6a339038c1f41656101931a2999529a1bf866ad75d8d1c9f3fd`：2A G4 现要求综合无错误/非预期锁存器、资源可容纳性与时钟风险报告；已将 `docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md` 单文件精确同步到该源。旧准备报告的综合 N/A 字段已过时。

## 当前候选批次（2026-10-08）

- 当前 RTL 候选为 commit `999238284157bed77cdb3a37e3e6eea52daeefc4` / tree `b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67`。原始 RunId `candidate8x8_109_20261006_130252` 的索引 0–24 PASS；恢复 RunId `candidate8x8_109_resume_20261007_023531` 仅运行 25–108，摘要 `PASS_RESUMED_84_RUNNERS`。恢复清单 `PASS_109_RECOVERY_MANIFEST`、109/109 PASS，SHA `eefe285f1c03673143d1fa0563f153626fe90d86be2d245ced59a05d8a7e65a2`；无存活协调器/仿真进程，不重跑。
- 当前候选 D9 报告 `PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9`，最大 score/xyxy 误差均 0，报告 SHA `fcdf60ef68990a13ba634ee6cb2df71ad152d7f9d5a05d6625f5f3af296523ab`。sample000 磁盘 marker 后续被截断；D9 verifier 从 SHA 绑定的 console 原始字节恢复并显式记录，未改写文件、未重跑。109 源快照映射 `PASS_109_CROSS_RUNID_RECOVERY_SOURCE_SNAPSHOT_TO_GIT_TREE`，报告 SHA `61789bb7951dde06160e376761e74b4f2a408002ae81533bbb9cd86906b89ba1`。
- D9 修复及三项关键结果报告提交 `8646a02`。T66 runner 异常处理四项发现已修复并经独立 Reviewer PASS，离线故障回归 35 项 PASS、无残留进程，提交 `671f9cf`；之后当前候选 layer0 完整黑盒仿真亦 PASS（1,384,448 输出字节、2,551,955 请求/响应、6,635,073 stall cycles，记录 SHA `1b7bb9efcf4dc1f5ef0e920a28e5549888005cc2986e42158fc4adfca8e848b3`）。OS 拒绝结束进程时，runner 明确报告进程未退出/输出不完整并返回非零。

## 历史基线批次（非当前候选）

- 历史 RunId `repair109_20261003_194620` 的原始证据为 `report/evidence/S2A-T68/repair109_20261003_194620/`，逐样本审计为 `report/evidence/S2A-T68/acceptance_audit_repair109_20261003_194620.json`。它不是当前 `candidate8x8_109_20261006_130252` 候选的通过记录。
- 该历史批次索引 0–108 均通过当时版本的完整 38 cfg 层 PL golden，无 mismatch；记录每样本 972,865,374 cycles。协调器摘要 `PASS_108_RUNNERS` 只含 1–108；sample000 是同 RunId 独立成功记录。最终审计合并为 109，不能称协调器原始摘要为 `PASS_109`。
- 历史批次的 PL head 对冻结 CPU D9 比较记录最大 score/xyxy 绝对误差为 0：`d9_109_sample_report.json`，`PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9`。该项不替代当前候选独立 D9 证据。
- 该历史批次 109 份编译快照映射到当时冻结的 38 项闭包：源码 commit `fecbf1f8f37fcee8b25e6e2517b9621850912a4e`，tree `094e1492396a6788cc33b3b5866dd304387c02da`。映射报告状态 `PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE`；当前候选映射见上文候选批次段及验收记录。
- 当前候选 T70 tile 算术、选定内存和边界/异常结果，以及 T68 `protocol_directed24` 有各自独立范围，不替代 109 样本整网结果；当前白盒/边界证据经独立 Reviewer PASS。T17/T20 是历史串行 engine/pilot，不能称作新 tile 等价覆盖。详见 `report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`。
- T25 独立干净副本实际恢复 109×38 CPU shards 并完成 109 样本 D9 canonical replay；恢复 2,283.61 秒、D9 12.359 秒。它证明 CPU oracle 可恢复，不证明 PL 在干净副本全量重跑。

## 冻结限制与证据保全

- 当前候选全核心 OOC Vivado 综合（`s2a_stage2a_core_ooc`，14 个 RTL）已成功：0 errors、0 latch；LUT 40,550/53,200，FF 3,082/106,400，BRAM 32/140，DSP 186/220。无 XDC/冻结时钟，不能宣称 timing closure。独立 Reviewer 对综合/资源/风险子项 PASS；证据在 `report/evidence/S2A-T68/g4_synthesis_20261005/candidate8x8_core_ooc_run01_20261006/`。T68/OOC、T70 与协议材料归档情况见验收记录。最终 G4/G5 独立 Reviewer 对固定 HEAD `671f9cf494b92ce182b3f1542fefd0cfd4b209f5` 及本轮证据返回 PASS，Stage 2A 已冻结；验收记录为 `report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`。
- T68、T25 与 tile/协议支持证据已分别归档到 `archive/S2A-T68/repair109_20261003_194620/`、`archive/S2A-T25/clean_restore_20261002_160036/`、`archive/S2A-Support/Stage2A_20261005/`，逐文件 manifest 校验通过。归档和源都在 D 盘同一物理卷，不是异盘备份。
- 在证据归档校验后，仅清理 109 个 PL `build` 与 4 个支持回归 `build/obj_dir` 缓存，释放 33,104,952,077 字节；输入、结果、日志、VCD、T25 shards 和失败记录保留。该 RunId 已完成，绝不重跑。
- T13/T14/T15 当前 helper 源专项已有独立复核通过的新证据；早期 `helper_vectors_current_candidate_20261008_r2` 的 T13/T15 PASS manifest 被 FAIL 日志推翻，失败证据保留，新运行替代其验收地位。验收记录列出各报告、运行日志哈希及确切范围。
- 验收记录：`report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`；用户本地运行说明：`docs/S2A-T68_local_run_guide.md`。限制仍包括无 XDC/时序收敛证明，以及当前候选未在干净副本重跑完整 109 样本 PL；审查确认后者不是 2A 硬性门槛。

## Git 与下一步

- 2026-10-08 用户要求改用新建的独立工作树/阶段2B总控窗口，旧2B窗口暂不使用；主目录与阶段3已有未提交改动保持不动。新工作树必须先核对冻结基线，不复制主目录全部未提交内容。
- 新增交付规则见 `AGENTS.md`「产物落点、阶段对接与 ROSS 使用」及 `report/README.md`；只读检查器提交 `9db8d64` 已通过50项回归与独立审查，证据 `report/evidence/CTRL-DELIVERY/validation_20261008_2054/`。它只核对当前声明的输入/证据，不代表阶段 G0/G4/G5 或实物通过。
- 本次 ROSS 2026.9.1 独立 Tcl 冒烟已通过：Vivado 2026.1 `version` 与 Tcl 查询完成码均为0，状态健康且仅本次会话已关闭；证据 `report/evidence/CTRL-ROSS-SMOKE/ross_tcl_20261008_192127/`。未测试 IP、综合/实现或硬件，不能由此关闭上文2B G0阻碍。
- 历史 T68 源映射修复基线为 `65dd1c310e7686d50685d2f83b9b2b623e6cf3ad`。候选实现提交 `999238284157bed77cdb3a37e3e6eea52daeefc4` 包含 tile engine、T66 testbench 与 runner；2026-10-06 G4 acceptance/OOC 综合证据提交为 `a232bc7c815a1e9bb18c675b0e9f31bccd857c62`。均未推送；保持其他阶段改动、运行目录、shards、模型数据、密钥和构建产物不入提交。
- 下一步：Stage 2A 已通过 G4/G5 并冻结。本轮 Reviewer 固定基线为 HEAD `671f9cf494b92ce182b3f1542fefd0cfd4b209f5`，验收记录含审查结论和已知限制；按项目阶段边界，后续阶段由用户开启新的总控任务。
