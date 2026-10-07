# 项目状态入口

更新：2026-10-07（UTC+8）。按根目录 `AGENTS.md` 恢复；阶段验收以当前代码、Git 和报告证据为准。

## 当前目标与阶段

- 阶段2A「PL 推理仿真」尚未冻结，当前在 G4/G5 独立终审。用户已批准 8×8 空间 tile、8 路输出通道并行；保持 T01 冻结的 CSR、32-bit 单 word memory 接口、timeout 和握手协议。
- 用户选择阶段3并行推进，暂定范围为摄像头到 HDMI 的原始视频链路。先核对 AX7020 PCB/接口、器件、引脚和电平并完成 G0；阶段3不依赖 2A/2B 推理验收。不烧录、不操作实物，除非后续明确授权。
- 本轮不修改阶段3内容。保留共享工作区中其他阶段及用户已有的改动。
- 2026-10-05 核对最新 Vault 阶段计划源 SHA `a94830afe60ae6a339038c1f41656101931a2999529a1bf866ad75d8d1c9f3fd`：2A G4 现要求综合无错误/非预期锁存器、资源可容纳性与时钟风险报告；已将 `docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md` 单文件精确同步到该源。旧准备报告的综合 N/A 字段已过时。

## 当前候选批次（2026-10-06）

- 候选代码提交 `999238284157bed77cdb3a37e3e6eea52daeefc4`，tree `b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67`；包含 8×8 tile/8-lane 引擎、T66 黑盒 testbench 与 runner。T66 layer0 运行记录报告 1,384,448 bytes、mismatch=0；同名并发锁争用记录 PASS。独立静态 runner 复审发现超时/异常清理和 marker 唯一性阻断（见 Git 与下一步），因此这些结果不单独作为阶段签收依据。
- 原始 T68 RunId `candidate8x8_109_20261006_130252` 于 2026-10-06 13:02（UTC+8）启动，证据根 `report/evidence/S2A-T68/candidate8x8_109_20261006_130252/`。原批次异常停止：样本 0–24 有完整 38 层 PASS；sample030 事件失败，sample025–032 只留部分记录；没有批次 summary。旧进度最新完整 marker 是 sample025、layer26、cycle690,000,000（2026-10-06 23:32:18），原协调器和仿真进程已退出。原日志、事件、部分运行目录和 marker 均保留。
- 恢复修复提交 `d767a93`、`81db0f0`、`f21fd2d` 分别处理共享 progress marker 读取、跨 RunId 安全续跑/证据绑定，以及 harness verifier 格式耦合；恢复实现和最后一项修复均已独立审查 PASS。sample033 由现有 fixture-only runner 单独生成；sample034–108 共 75 份由同一 runner 从冻结 T01/T25 输入生成并验证，记录在 `fixture_prep_resume_20261007_022841/fixture_prep_progress.json`。109 份 fixture 通过只读恢复预检。首次 coordinator 尝试在样本启动前被 fail-closed 进程门拦截（观察用 PowerShell 自匹配），没有仿真或样本输出；记录为 `recovery_launch_outcome_20261007_022502.json`，未覆盖。
- 当前恢复 RunId `candidate8x8_109_resume_20261007_023531` 仅运行尚未通过的 25–108，最多 8 workers；旧组 0–24 绑定原 commit/tree `999238284157bed77cdb3a37e3e6eea52daeefc4`/`b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67`，新组绑定 `f21fd2d4237445772f30b901975676455a5766e7`/`25cb9b19282ff110e95448e0edf0c4e1b6976122`。截至 2026-10-07 17:13（UTC+8），协调器 PID17232、当前 8 个 runner 和 8 个仿真器存活；新组 25–80 的 56 个 dispatch 事件均为 `PASS_RUNNER_AND_RECORDS`、runner exit 0，逐项 stdout/stderr 与六类样本记录 SHA-256 复核通过，result summary 均为 `PASS_LAYERWISE_EXACT_GOLDEN` 且 `mismatches=0`。连同原组 0–24，当前 81/109 样本通过；样本 81–88 正在运行，8 个完整 marker 均为 `phase=running`，进度处于 `layer=4–7/cycle=180,000,000–240,000,000`。目前还没有最终 batch summary 或 recovery manifest。启动核验记录为 `recovery_startup_check_20261007_023531.json`；现有 4 小时 heartbeat 监控此恢复 RunId。
- 旧 RunId `repair109_20261003_194620` 属于旧源码基线，已完成并保持不变；恢复批次全部通过后，先验证 recovery manifest 的 109 个跨 RunId 记录，再运行冻结 CPU D9 对比和 `verify_s2a_t68_snapshot_git_binding.py`/相关 Git-tree 核验。禁止只凭进程视为通过。

## 阶段2A 已验证事实

- 主批次 RunId：`repair109_20261003_194620`；原始运行证据 `report/evidence/S2A-T68/repair109_20261003_194620/`，逐样本审计 `report/evidence/S2A-T68/acceptance_audit_repair109_20261003_194620.json`。
- 109 个索引 0–108 均通过完整 38 cfg 层 PL golden，无 mismatch；每样本 972,865,374 cycles。协调器摘要状态 `PASS_108_RUNNERS` 只含 1–108；sample000 是同 RunId 独立成功记录。最终审计合并为 109，不能称协调器原始摘要为 `PASS_109`。
- 109 个真实 PL head 对冻结 CPU D9 比较通过，最大 score/xyxy 绝对误差为 0：`d9_109_sample_report.json`，`PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9`。
- 109 份编译快照映射到冻结 38 项闭包：源码 commit `fecbf1f8f37fcee8b25e6e2517b9621850912a4e`，tree `094e1492396a6788cc33b3b5866dd304387c02da`。映射报告状态 `PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE`。
- T70 tile 算术、选定内存和边界/异常结果，以及 T68 `protocol_directed05/06` 有各自独立范围，不替代 109 样本整网结果；T17/T20 是历史串行 engine/pilot，不能称作新 tile 等价覆盖。详见 `report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`。
- T25 独立干净副本实际恢复 109×38 CPU shards 并完成 109 样本 D9 canonical replay；恢复 2,283.61 秒、D9 12.359 秒。它证明 CPU oracle 可恢复，不证明 PL 在干净副本全量重跑。

## 冻结前的限制与证据保全

- 当前候选全核心 OOC Vivado 综合（`s2a_stage2a_core_ooc`，14 个 RTL，candidate commit/tree）已成功，launcher exit 0、0 errors、0 latch；LUT 40,550/53,200，FF 3,082/106,400，BRAM 32/140，DSP 186/220。无 XDC/冻结时钟，风险报告不代表 timing closure。独立 Reviewer 已对该 G4 子项 PASS；详细证据在 `report/evidence/S2A-T68/g4_synthesis_20261005/candidate8x8_core_ooc_run01_20261006/`。早期 Tcl Store 启动失败和安装器权限探针保留为历史记录。当前整网109/D9/快照映射仍待完成；整体G4/G5未通过。T66 runner 独立审查发现4项证据完整性/异常清理问题，须修复复审后才可把其作为稳定的复现入口。
- T68、T25 与 tile/协议支持证据已分别归档到 `archive/S2A-T68/repair109_20261003_194620/`、`archive/S2A-T25/clean_restore_20261002_160036/`、`archive/S2A-Support/Stage2A_20261005/`，逐文件 manifest 校验通过。归档和源都在 D 盘同一物理卷，不是异盘备份。
- 在证据归档校验后，仅清理 109 个 PL `build` 与 4 个支持回归 `build/obj_dir` 缓存，释放 33,104,952,077 字节；输入、结果、日志、VCD、T25 shards 和失败记录保留。该 RunId 已完成，绝不重跑。
- 验收候选：`report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`；用户本地运行说明：`docs/S2A-T68_local_run_guide.md`。候选仍是 review-pending，不能当成通过报告。

## Git 与下一步

- 历史 T68 源映射修复基线为 `65dd1c310e7686d50685d2f83b9b2b623e6cf3ad`。候选实现提交 `999238284157bed77cdb3a37e3e6eea52daeefc4` 包含 tile engine、T66 testbench 与 runner；2026-10-06 G4 acceptance/OOC 综合证据提交为 `a232bc7c815a1e9bb18c675b0e9f31bccd857c62`。均未推送；保持其他阶段改动、运行目录、shards、模型数据、密钥和构建产物不入提交。
- 下一步：保持当前 25–108 恢复批次运行且不另启进程；按四小时 heartbeat 核对进度、事件与 summary。完成后检查 recovery manifest、109 份 PL 结果、D9 报告和新旧源码快照映射。T66 独立候选 runner 的遗留复审问题继续单独保留；整体 G4/G5 仍未通过，全部适用关口 PASS 后再冻结阶段，不降低门槛。
