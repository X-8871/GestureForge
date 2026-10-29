# 项目状态入口

更新：2026-10-26 19:05（UTC+8）。按根目录 AGENTS.md 恢复；本入口仅维护全局状态、阶段归属与证据入口。

## 当前目标与阶段

- 阶段2A「PL 推理仿真」旧XA/-1目标已完成 G4/G5 独立审查并冻结；2026-10-09 新XC/-2限定同源OOC补验也经独立审查PASS并完成技术G4/G5收尾，冻结入口见下文。用户已批准 8×8 空间 tile、8 路输出通道并行；保持 T01 冻结的 CSR、32-bit 单 word memory 接口、timeout 和握手协议。
- 用户已启动独立阶段2B总控；本窗口按其已授权任务补验阶段2A的新器件适用性。2026-10-08 Wong 确认器件输入 `XC7Z020-2CLG400I`；实际 Vivado 目录唯一解析为 `xc7z020clg400-2`。旧 XA/-1 冻结及全部功能证据保留，新器件相关验收须另行补齐；本轮未改硬件工程或进行实物操作。
- 本主目录先前2B只读核查未通过G0，独立2B工作树的后续状态以其自身STATE/证据为准：T01 已冻结 tiny416 模型、两检测头及 D9 解码/NMS，不能继续称这些未冻结；物理 PS/PL 地址映射、AXI/DDR 传输、DMA/cache 和缓冲所有权由2B总控冻结。新器件编号依据本轮用户确认和手册，新实板与 PCB/BOM/DDR 图纸的独立对应仍未知；旧板照片及已有 `.xpr` 的 XA/-1 记录保留历史身份，不能直接沿用其 PS/DDR 配置。当前主工程无 PS Block Design、Vitis 平台或板级 XDC。
- 本轮未改2B/3的独立工作树，仅处理2A器件适用性补验。阶段2B后续任务须先冻结物理接口和适用器件资料；板卡下载、上电、DDR/UART实测等实物操作须另行明确授权。**2026-10-24 02:2x Wong 已拔下板卡 ⇒ 一切板级工作暂停（已核验无残留：`hw_server`/`xsdb`/Vivado 进程 0、3121 无监听、COM4 空闲）**；**转无板卡工作流**（`decisions/board_detached_boardfree_plan_20261024_r01.md`）：**阶段3 回放输入包（task-25）→ 阶段4 离线真实彩色链 + 回放结果包（task-26）→ 阶段5 回放显示路径与离线回归（task-27）→ 阶段6 6-E 回放预演（task-28）**，全部离线且**不得升级为实物/验收结论**；**板卡重连后先重做受连接判据（真彩目视、部署身份核对）再执行板级项**。**2026-10-24 10:29 Wong 已重新插上板卡与摄像头 ⇒ 板级工作可恢复，但"插上"不等于已核验就绪：须先重做受连接判据（部署身份逐字符核对、真彩目视重做、运行期回读 `ADDR_S2MM`/`ADDR_MM2S`）；当前无任何 host 会话（`hw_server`/`xsdb`/Vivado/vitis 进程 0、3121 无监听、COM4 未占用）**。
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
- 上述旧综合实际目标为 `xa7z020clg400-1I`。新补验 r01 的 Python 环境预检查失败、r02 的过期 Enterprise 试用检出失败均保留原证据。Wong 后提供的 Downloads `Xilinx.lic` 同时含有效 BASIC（至2027-08-07）；只复制完整 BASIC 条目到私有临时目录并给本次子进程设置许可路径，未改原件或持久环境。Vivado MCP 只读调用被审批配置拦住后，r03 使用相同安装版本的官方 batch/Tcl，实际 tier=BASIC、part=`xc7z020clg400-2`、14 项历史源精确匹配、进程 exit0/Tcl139秒。新实际报告为 LUT40,550/53,200、FF3,082/106,400、BRAM32/140、DSP186/220、0 errors、0 latch、65 warnings、0 critical；有报告/DCP，峰值为 Vivado 报告2259.402 MB。工业grade仅功耗环境，最差未放置路径97.069ns且无XDC/冻结时钟，不是时序收敛。独立 Reviewer `/root/xc2_supplement_review` 对固定HEAD `b285ca4831be676f2f169c4d57691221ee0b9715`、r03清单SHA `75b3b945b32d32e688b0de5349fb029451ffc7077f6bd082d02c240231622719` 及正式差异返回 `S2A-XC2-R-Final PASS`；补验G3不适用，技术G4/G5通过。证据入口 `report/evidence/S2A-T68/xc7z020_2_ooc_20261008_r03/`，关闭记录 `report/evidence/S2A-T68/xc7z020_2_supplement_acceptance_20261009.json`；提交身份以包含关闭记录的Git提交确定。
- T68、T25 与 tile/协议支持证据已分别归档到 `archive/S2A-T68/repair109_20261003_194620/`、`archive/S2A-T25/clean_restore_20261002_160036/`、`archive/S2A-Support/Stage2A_20261005/`，逐文件 manifest 校验通过。归档和源都在 D 盘同一物理卷，不是异盘备份。
- 在证据归档校验后，仅清理 109 个 PL `build` 与 4 个支持回归 `build/obj_dir` 缓存，释放 33,104,952,077 字节；输入、结果、日志、VCD、T25 shards 和失败记录保留。该 RunId 已完成，绝不重跑。
- T13/T14/T15 当前 helper 源专项已有独立复核通过的新证据；早期 `helper_vectors_current_candidate_20261008_r2` 的 T13/T15 PASS manifest 被 FAIL 日志推翻，失败证据保留，新运行替代其验收地位。验收记录列出各报告、运行日志哈希及确切范围。
- 验收记录：`report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`；用户本地运行说明：`docs/S2A-T68_local_run_guide.md`。限制仍包括无 XDC/时序收敛证明，以及当前候选未在干净副本重跑完整 109 样本 PL；审查确认后者不是 2A 硬性门槛。

## 共享工作区与交接（2026-10-17）

- Wong 决定 Codex 与 DSH 共用本仓库，按任务轮流独占写（方案 A）；共同规则见 `AGENTS.md`「与 Codex 共享同一工作区」。
- 接任务方：先读 `AGENTS.md` 与本文件，核对 `git status --short`、`.git/index.lock` 及 Vivado/xsim 进程，再独占修改；结束时更新本段交接行并只提交本轮相关文件。
- 非接任务方只读复核，不并发写同一文件、不并发提交、不跑重型综合/仿真。
- 交接行格式（11 字段）：`任务 | 负责人 | 工作树/分支 | 起始提交 | 允许修改范围 | 未提交改动归属 | 让出声明 | 心跳(UTC+8) | 证据入口 | 恢复命令 | 状态/下一接手方`；状态机 `IDLE→OFFERED→CLAIMED→IN_PROGRESS→DONE`；当前交接记录见下方「阶段入口与任务归属」。
- 独立信箱（2026-10-19 Wong 授权，主目录单写规则的限定例外）：`report/evidence/CTRL-DSH-HANDOFF/dsh_mailbox/` **仅 DSH 写**、`codex_mailbox/` **仅 Codex 写**，双方只读对方信箱；仅限跨方请求/回执/接收确认/必要核验证据；唯一编号、不覆盖旧记录；不代表工作树写权交接。首条见 `dsh_mailbox/DSH-20261019-001-mailbox-live.md`。
- 环境事实（2026-10-17）：DSH 沙箱在 `D:\FPGA_Competition` 的写入授权已修复（仅给当前用户补完全控制，未删除任何条目，回滚脚本在 `D:\dsh_acl_recovery\20261017\`）；Git Bash 的 `bash.exe`/`sh.exe` 在受限沙箱下报 signal pipe Win32 5，改用 git 直调与 Python。用户级 `TEMP`/`TMP` 已设为 `D:\tmp`（2026-10-17，新进程生效，Vivado/xsim/Verilator 共用；已运行进程需重启后才切换）。

## 阶段入口与任务归属（2026-10-18 核实）

| 阶段 | 工作树 | 分支 | HEAD | 状态入口 |
|---|---|---|---|---|
| 2A（已冻结） | `D:\FPGA_Competition` | `main` | 见下方冻结提交 | 本文件下方 2A 证据段 |
| 2B（进行中，Codex） | `D:\FPGA_Competition\w2b` | `codex/stage2b-dma-g0` | `bca323b1`（2026-10-19 23:40 只读核实；同日由 `75fcc59` 推进至此） | `w2b/.codex/STATE.md`及该树最新证据 |
| 3（**已收尾通过（带记录性局限）；冻结 tag `stage3-close-20261026-r2` → `e287392`**） | `D:\codex-worktrees\dbdf` | `codex/stage3-video` | `2becf99`（收尾冻结基线 `e287392`） | 颜色（新模块实测）、≥30m 耐久 31m15s、参考帧集、地址事实、真彩目视均已完成；**独立复审 `rev-s3` 最终 `PASS`**；视频输入接口经 Wong 2026-10-26 确认 AN5642/J11；**记录性局限（不得改称通过）**：① VDMA 首帧 bit11 根因 `PARTIAL_OPEN` ② task-11 完整 SEC `BLOCKED_NOT_RUN` ③ TIMING-17/I-O delay 未纳入冻结位流、未签核 ④ 无 ILA（BASIC 许可）；**不代表 G0/G4/G5 或实物验收**。证据见该树 STATE 与 `S3-T17/stage3_closeout_20261026_r01/`、`stage3_closeout_erratum_20261026_r01/`。 |
| 4（**离线范围已冻结；真实板级 PS 张量诊断已执行；G5 未主张**） | `D:\codex-worktrees\w4` | `stage4-infer-prep` | `83c9284`（离线冻结文书 14:28；板级执行 `4e0b03d`；会话拆除 `83c9284`） | ① 离线：`OFFLINE_SCOPE_FROZEN`（冻结集 8/8 PASS）；② 板级：run `s4b_ps_tensor_hw_20261027_r01`，`ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED` / `EXECUTED_WITH_EXPLICIT_GATES`，**门禁 8/8**；授权链 main OFFER `84c840f` → w4 CLAIM `3b496fb` → handoff r06；身份四件经 DSH 独立实算一致（bit `555a70c2…`/ELF `bfe88660…`/MAP `4a0f9cf8…`/XSA `ea52da1b…`）；权重 `f6feb6d4…`、输入张量 `da26d385…`（519,168 B INT8_CHW_416）；**回执 frame0/seq2/epoch1/rc0：raw_candidate 2 → 检出 1 框**（head13 5,070 B、head26 20,280 B）；trace `PASS_DECODED_DOUBLE_READ_SNAPSHOT` + `PASS_EXACT_TRACE_UART_JOIN`（session 1396845568）；`run_active_zero`、cpu0 安全点、cpu1 Stopped；会话已拆除（DSH 实测 3121 关、无残留进程）。③ 诚实边界：`complete_stage4_or_RGB_preprocess=NOT_CLAIMED`（不证明 RGB 预处理/raw-PL 新架构/G5）；真摄子项 `DEFERRED_PENDING_MODULE`；真拍回放需 Wong 在场（阶段5 前置）；**待说明**：`jtag_result.json` 底层 `API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING` 且 `cold_lifecycle_proven=false`，与门禁 `cold_basis`（物理断电重启）的层级口径需对齐。④ Wong 已于 2026-10-27 恢复 Hyper-V 端口（`winnat` Running、TCP 排除段已无 3121、3121 空闲）；⑤ **Wong 2026-10-27 裁 D1=A**：允许缩减 `[0x12000000,0x20000000)` 禁区，取 `raw_frame` 12 MiB + `raw_meta` 32 KiB（**109/109**、余量 +1,523,712 B）；**不接受**降覆盖（D2 否，B/E 排除）；D3 META 不强制连续、D4 linker 冻结不作前置（E 排除）——裁决记录 `decisions/stage4_raw_address_d1_optionA_20261027_r01.md`、通报 `dsh_mailbox/DSH-20261027-005`；**仍不授权** `ENABLE=1`/FROZEN/板级访问，须先完成地址图+契约落地并独立复审 PASS（**已达成**：落地 `e39f6de`，独立复审 PASS 0 阻断/4 非阻断——时间戳晚于提交、STATE 11 字段行未同步、证据写21对实为28对、派单4个路径名不符，均已于 `d5a86bf` 更正、`43a9a4c` 增量核对 **DELTA_PASS** 关闭） + **板级四项实测（2026-10-27 晚，5 次窗口共 ~10 min 上板，零副作用）**：**M1=PASS**（`rst -system -stop` 后两核 Suspended；CPU1 PC 两次 2.5 s 不推进）｜**M2=PASS**（DevCfg `0x40000010`、`PCFG_DONE=0` ⇒ PL 未配置 + 两核 Suspended + 唯一调试客户端 ⇒ **构造性排除，非总线测量**）｜**M3=NOT_CLOSED**（`mwr` 在 2026.1 无 `-pattern`、`-bin -file` 缺字数；**仅写 4 字节** `0x12000000` `bfbd8604→00005a5a`，**已按快照精确回填**，16 B 回读与快照逐字节相等、差异 0；**整区恢复后 dump=NOT_CAPTURED**；写入后回读曾误命名 `restored`，经 DSH 逐字节核出、已正名 `m3_readback_after_write.bin` 并补溯源 `e7bf1fb`）｜**M4a=NOT_RUN**｜**M4b=NOT_APPLICABLE→4-D 必测**；证据 `execution_20261027_r01..r05`；**`ENABLE=1` 前置未满足**；**M3/M4-a 并入 4-D bring-up**（Wong 2026-10-27 裁：不再单开测量窗口）；**窗口 A′（22:26）M3 曾 PASS**（整区 dump 与快照逐字节相同、diff=0，证据 `window_a_20261027_r01/`）；**窗口 B r02（22:58）装 PL 后复检：同状态两次只读 dump 互相逐字节一致、但均异于 A′ 参考，`diff_bytes=6`、6 处均为单比特清零（`0x12b09e1b`/`0x12b4805b`/`0x12b4906a`/`0x12b4930e`/`0x12bc8f82`/`0x12bc9f5b`）⇒ 判定 `REGION_CHANGED`（非读不稳）** ⇒ **M3 记 FAIL/未闭合**、**M2"候选区空闲/不相交"论证需重审**；**M4-a/M4-b 本轮 `NOT_RUN`**（按"REGION_CHANGED 即停"未执行）；**根因未定**（候选：`init.elf` 运行时写入 / PL 配置后状态 / DDR 位翻转），**定位法（只读）**：`快照→装PL→快照→装init→快照` 分段 bisect + 对照 `init.elf` 链接映射；证据 `window_b_20261027_r02/read_stability/`；`ENABLE=1` 仍未解锁 |
| 5（**离线范围已冻结（独立复审 PASS）；G5/板级未主张**） | `D:\codex-worktrees\w5` | `stage5-display-prep` | **`26b7439`**（冻结字节身份；tag `stage5-offline-freeze-20261027`）；文书身份 `2797cc3` | **`OFFLINE_SCOPE_FROZEN`**：冻结集 **77 成员（58 file＝49 repo＋9 host；19 file_set 内含 138 repo 文件）＝187 repo 已跟踪文件＋9 host 引用＝196 条目**（14 契约/3 实现/44 回放-显示证据/7 S5-T02/9 宿主只读引用）；校验器 `verify_stage5_frozen_set.py` fail-closed（clean 0 / 改字节 1 / 缺件 2）；独立复审 `rev-s5` **PASS（0 阻断；4 非阻断＋1 文档漂移）**——独立**全量重算 196 文件 0 不符**、**范围洞 0**、F6 两路（`git archive` 导出＋独立检出）exit 0、回归 **142/0/2**（含 106,573 帧）、构建器可复现 `members`、**未 push**；绑定阶段3 帧 `939fce22…` 与 Wong `stale=200 ms` 回执。**未主张**：G0–G5 / 板级 / 实物 / 实时。`task-27` **已交付（离线；独立复审 PASS 0 阻断）**：回放/彩色输入路径在实现层成立（现场重算源帧哈希、逐帧 `frame_integrity` 三要素、10 项 `replay_source_*`、真过阶段4 契约）、离线回归 30/0 可复现、`capture_time_ns` 可核（`2026-10-24T01:24:13+08:00`）；**N1 必须在冻结/交接前修**（清单绑定工作树 LF 字节而目录无 `-text` ⇒ 干净检出 checker exit 2）；未闭合：B1–B10 暂停、18 项历史探测失败（上游漂移，不在冻结集）；下次重冻结需修 F1 路径越界检查、F2 README §6 措辞、F3 `superseded_runs`、F4 失败件 `run_id`、F5 docstring。证据 `S5-T04/s5_freeze_20261027_r05/`、`s5_freeze_f6export_20261027_r01/`；复审记录 `reviews/S5_T04_20261027_r01/`。 |
| 6（Codex 接管；三项门禁修复中） | `D:\codex-worktrees\w6` | `stage6-interact-prep` | `8d232ab` + 本轮修改 | 历史离线内容冻结F6d/G6b保留；task-23/28增量复审CHANGES_REQUIRED：真实claim退出码被合成成功、真实验收允许回放/合成、缺批准状态被接受。Developer修复中；P/T6-A03仍NOT_RUN，回放预演待task-26/27，6-E实物未执行。 |
| 较早 2B | `D:\codex-worktrees\96a3` | `codex/stage2b-t01-board-audit` | `e26feea` | 仅历史参考 |

- 主目录 STATE 只维护全局状态、任务归属与阶段入口；阶段技术事实以对应工作树 STATE/证据为准，不在此复制全文。
- 阶段3（2026-10-20 授权开工 / 11:39 窗口更换）：Wong 的方向是「先完成作品、验证从简，第一版能过即可」；新窗口**工作区 = `D:\FPGA_Competition`（读规则/资料）**，**Git 写入树 = `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`**，由其独占写入，主 STATE 不复制其技术事实。资料：摄像头 `D:\FPGA_Competition\摄像头资料\`（`官方资料` 优先）、板卡 `D:\FPGA\AX7Z020\AX7Z020`（只读）。**若要求阶段3 代码直接写入主工作树，须先由 DSH 让出并声明写入范围，不得默认。**【事故】旧阶段3窗口于 04:36:44 以未闭合 `compaction/start`（`compactionId 58ec4c74-1321-45c6-b788-28661a9a1b58`、turn 5）卡死，构成持久压缩锁、不能自愈；该窗口此前已提交 9 个 dbdf 提交（00:51–04:34，最新 `41ee5ba`：HDMI 已 JTAG 启动、CMOS2 1280×720 可用、仅剩 S2MM 缺 SOF）。【修复】根因是第三方插件 `dsh-batch-tool-calls` 压缩后注入 v3 格式 `{kind:'plugin'}` 被会话格式 v4 拒绝（`lib/index.js:60`/`:231`）；已在 profile `cordis.patch.yml` 覆盖 `reassertAfterCompaction:false`+`reassertEverySteps:0`（备份 `.bak-20261020-batch-fix`），生效 `cordis.yml:1346` 已带新值，只读核验 **6/6 PASS**（`report/evidence/CTRL-HARNESS/session_compaction_lock_20261020_r01/`）。旧会话不修复、不写回；**「新会话不再触发 v4 报错」尚未以实际新会话运行验证**。
- 硬件与 2B 观察（2026-10-21 22:55，DSH）：w2b HEAD=`6e66bfc`（21:09:50）、未提交 169 项；**当前无 `hw_server`、无板测脚本、无 vivado/xsdb/vitis 进程**（21:20 曾见 2B 的 `hw_server` PID 28624 与板测 PID 29364/24176，均已退出）→ 硬件事实空闲，但 **`CDX-20261021-004/005` 的书面占用未由 2B 正式让出**，任何使用前仍须先确认；**阶段3 已由 DSH 阶段三总控 CLAIMED→IN_PROGRESS（心跳 22:05）**，根因收敛为**硬件**（DVP `cmos_d[9]` 单线无信号，配置侧/映射/RTL/FPGA 引脚均已排除），需实物排查；**10-22 12:2x 阶段3 进一步报告：已在无补偿基线上用已知彩条证实「两字节 MSB 同时丢失」的硬件缺位（缺位算术吻合；通道置换无效；板卡已恢复实时灰度视频）——DSH 项目总控**已独立复算通过**（四色数值全部在图中命中；R 未丢位、B 丢 bit4、G 丢 bit2，与「字节 MSB 丢失」自洽；**电气定位未证**），见 `report/evidence/CTRL-DSH-HANDOFF/dsh_mailbox/DSH-20261022-007-colorbar-recheck.md`**；**Wong 2026-10-22 决定：先暂按灰度推进后续工作，等模块到货后再更新——颜色子项一律标 `DEFERRED_PENDING_MODULE`（阶段3 已于同日 12:40 按灰度收尾 `12bd4c9`，交付基线 bit `44e609cc`／XSA `90e1bdee`，颜色不宣称通过）；已发 `DSH-20261022-008`（灰度先行 + 复测要求）与 `DSH-20261022-009`（2B 冻结后的硬件交接口径：请求书面让出/时间窗）**；**Wong 2026-10-22 13:0x 告知：板卡留在 Wong 处、2B 阶段今晚冻结 ⇒ 今晚起 JTAG/COM4 空档开放**；阶段456 走法：① 使能项 = 可加载图像的帧注入源（阶段4 树 `w4`，S4-E，声明为测试夹具而非交付位流）② **阶段5 上板 bring-up 已在进行**（P1：PS 合成图 + 预计算框，13/13 像素检查、2 个 UI 缺陷已修；**无逆映射、display_fps 未验**）（PS 合成图/阶段4 注入源 + 注入结果 → HDMI 叠框/FPS/延迟；**无摄像头时不能用 `0x503D` 图案——那是摄像头内部彩条寄存器**）③ 阶段4 上板注入帧端到端（真摄子项延期）④ 阶段6 另行开树，待阶段5 上板有结果；**注入帧 ≠ 真摄像头，证据须标"适用性仅限注入集"**；`.git` 遗留（43 个 `tmp_obj_*`／约 266 MB 与 10-12 的 `maintenance.lock`）**按 Wong 决定暂不清理**；**Codex `CDX-20261022-006`（10:29）称 2B 已恢复最终验收并独占 JTAG/COM4（`hw_server` PID 4812），且明示「收尾后另发释放通知、本通知不算释放」；DSH 13:0x 现场核验：无 `hw_server`、3121 无监听、无板测进程（该会话已退出），但 2B **未冻结、未发释放** ⇒ 任何上板仍须等其明确释放，之后 w4/w5/w6 才动硬件**；**DSH 2026-10-22 13:4x 经 Wong 授权做极短只读 JTAG 扫描（证据 `report/evidence/CTRL-HW-SCAN/hw_scan_20261022_r01/`）：JTAG 链可见——`Digilent JTAG-HS1 210512180081` / `arm_dap` / `xc7z020`(idcode 23727093)，目标 16 项、两个 A9 核 **Running** ⇒ **板卡已接、已上电、PS 在运行**；扫描后已终止自起 `hw_server`（0 进程、3121 无 LISTENING，仅 TIME_WAIT），未 program/未烧录/未重配/未开 COM4。**判定陷阱：`xsdb` 脚本输出被重定向时裸 `targets` 不打印，须用 `llength [targets]` 或 `jtag targets` 判定，不得据此判"没接上"**（阶段5 窗口曾据此误报未连接）**；**2B 已于 2026-10-22 18:18 冻结（`07c3d39`，G4=PASS／G5=PASS，冻结回执 `w2b/report/evidence/S2B-T18/stage2b_freeze_receipt_20261022_r01/freeze_receipt.json`，独立审查 `S2B-T20/final_acceptance_review_20261022_r01/`；Codex `CDX-20261022-007` 明确「硬件占用结束、旧 PID 4812 失效、本任务不再占板」）⇒ **JTAG/COM4 空档已开放**；**Wong 2026-10-22 18:2x 告知：摄像头改为重新购买，接下来的任务不能用摄像头**（阶段3 颜色项仍 `DEFERRED_PENDING_MODULE`）；阶段5 已上板做 P1（`w5` `d65636c`：PS 合成图 + 叠框上板跑通、显示缓冲已验证、**display_fps 未验证 + 登记 2 个 UI 缺陷**、6 用例 HDMI 照片已归档）；阶段3 按授权清理 41 个可重建构建缓存（1659.7 MB，`f94c25f`）；交外部顾问的现状简报 `report/evidence/CTRL-DSH-HANDOFF/gpt_briefing_20261022_r01/GPT_briefing_20261022.md`**；**Codex 2026-10-22 18:5x 交付阶段3–7 执行文档包（正式集合 `CDX-20261022-015/009/010/014/012/013`，`008`/`011` 已被取代但保留）；DSH 已逐份审阅并出接收回执 `report/evidence/CTRL-DSH-HANDOFF/dsh_mailbox/DSH-20261022-010-execution-index-receipt.md`（6 路径 + SHA-256 + 分派对象 + 冲突澄清）；阶段7 工作树待 Wong 决定是否开 `w7`**；重型任务同时只跑一个；七棵树（main/w2b/dbdf/w4/w5/w6/96a3）均无 index.lock。
- 阶段4 离线准备（2026-10-21 Wong 授权新开窗口 + 分支工作树）：工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`（自 `main` `8ee2530`），由**一个独占写入方**负责；范围仅离线——阶段4 G0 草案（frame_id／框／分数／原图坐标／采集与结果时间／推理耗时 vs 端到端延迟／丢帧与过期口径）、PS 解码/NMS + UART 集成骨架（复用 2A 的 D9 参考实现）、用 2A 冻结数据做离线回放与对拍；**不依赖阶段3 摄像头与板卡、不占 JTAG/COM4、不同时跑重型任务**。阶段5/6 先出规格草案（显示叠框与延迟语义、交互状态机与阈值表），等阶段4 有结果再各自开树；真实验收必须等阶段3 完成且 2B 让出硬件。
- 交接行（11 字段，2026-10-27 15:25）：任务=`HL-T63 main 写权认领（CDX-20261026-001 OFFER）与 S4-B-REAL-02B 硬件 OFFER 落盘` | 负责人=`DSH 项目总控` | 工作树/分支=`D:\FPGA_Competition` / `main`（w4/w5/w6/w2b 不在本次范围） | 起始提交=`bdb7a360916641382a04f018c668774543e45b8e` | 允许修改范围=`main 全局状态与项目总控层；阶段树写权按各自负责人` | 未提交改动归属=`main 424 项为既有 Codex/用户历史改动与未跟踪产物，不属本次交接；DSH 仅对本轮 STATE、认领记录与本信箱负责，不清理不暂存其余` | 让出声明=`Codex 项目总控 2026-10-26 19:05 以 CDX-20261026-001 将 main 与阶段3 OFFERED 给 DSH；阶段3 已由 DSH 阶段三总控 2026-10-26 认领并收尾冻结；**DSH 项目总控 2026-10-27 核验 main（`handoff_check --claim` = `HANDOFF_OK` PASS 9/FAIL 0）后 CLAIMED**` | 心跳(UTC+8)=`2026-10-27 15:33` | 证据入口=`report/evidence/CTRL-DSH-HANDOFF/dsh_claim_20261027_r01/`、`codex_mailbox/CDX-20261026-001-main-stage3-write-offer.md` | 恢复命令=`git --no-optional-locks -C D:/FPGA_Competition rev-parse HEAD; python -B D:/FPGA_Competition/verification/handoff_check.py --worktree D:/FPGA_Competition --record report/evidence/CTRL-DSH-HANDOFF/dsh_claim_20261027_r01/handoff_record.json --json` | 状态/下一接手方=`IN_PROGRESS / DSH 项目总控；阶段3 已收尾冻结（tag `stage3-close-20261026-r2` → `e287392`）；阶段4 硬件 OFFER 见下一行` |
- 交接行（11 字段·硬件会话，2026-10-27T16:48:52+08:00）：任务=`S4-B-REAL-02B::s4b_hardware_session_handoff` | 负责人=`DSH` | 工作树/分支=`D:\FPGA_Competition / main` | 起始提交=`4f44f15141652a1fd36cb78c4b238fb426fa3931` | 允许修改范围=`S4B_PS_TENSOR_DIAGNOSTIC` | 未提交改动归属=`main 工作树另有 428 项未提交改动，不属本次 OFFER；OFFER 提交仅新增本行，无需清理` | 让出声明=`OFFERED` | 心跳(UTC+8)=`2026-10-27T16:48:52+08:00` | 证据入口=`hardware_run_id=s4b_ps_tensor_hw_20261027_r01` | 恢复命令=`git --no-optional-locks -C D:\FPGA_Competition rev-parse HEAD; python -B D:\codex-worktrees\w4/scripts/stage4_s4b/make_claim_line.py --offer-commit <本OFFER提交SHA> --run-id s4b_ps_tensor_hw_20261027_r01` | 状态/下一接手方=`OFFERED Workbuddy 阶段4总控`
- 本轮结束提交：本行同批提交（见 `git log -1 -- .codex/STATE.md`）。此前：`a36a0cd`、`dcf28c1`、`a06e72e`（信箱闭环）、`4885013`、`605a1f8`（阶段3入口）、`f920e24`、`8ee2530`（压缩锁事故与阶段三窗口更换）、`05d2dff`（阶段4 树）、`acd2df6`（阶段4 收尾）。事故证据包 `report/evidence/CTRL-HARNESS/session_compaction_lock_20261020_r01/`（`verify_incident.mjs` 可复跑，6/6 PASS）。
- 交接行格式与状态机见根 `AGENTS.md`「运行逻辑：双 Agent、两级总控（2026-10-19）」；旧 8 字段一行式记录（`51f7130`/`b87dd4f`，无心跳）已作废。
- 环境事实（2026-10-18）：`TEMP/TMP=D:\tmp`（用户级）；Vivado BASIC 许可 `D:\Xilinx_licenses\basic_only.lic`（至 2027-08-07，仅注入 DSH MCP env，用户级 `XILINXD_LICENSE_FILE` 为空）；DSH MCP：`vivado-mcp`(ROSS stdio)、`vivado-py`、`amd-doc-search`(HTTP 8080，服务已停)；ROSS 技能 50 目录 / **49 个 `SKILL.md`**；C 盘 41.2 GB、D 盘 38.0 GB 可用。
- 环境路径索引（2026-10-19 核实）：项目根 `D:\FPGA_Competition`（主工作树 `main`，可写）；2B 工作树 `D:\FPGA_Competition\w2b`；厂商原件 `D:\FPGA\AX7Z020\AX7Z020`（**只读，保持不动**）；Vivado 2026.1 安装 `D:\Xilinx\2026.1`（启动器 `D:\Xilinx\2026.1\Vivado\bin\vivado.bat`）。
- Obsidian 本项目仓库（2026-10-19 核实）：`C:\Users\22061\Documents\Obsidian Vault\02-项目\基于 AX7Z020 的低比特神经网络 FPGA 加速系统，实现摄像头手势识别并驱动板卡进行实时交互`；操作前先读该 Vault 的 `00-AI全局整理规则.md`，不导入其他 Vault 内容，该规则不得由工具/技能扩权。
- 探针证据包 `report/evidence/CTRL-DSH-HANDOFF/handoff_20261018_r01/`：只证明工具链可用（综合/实现/比特流/xsim，原生日志与退出码已封包；xsim 未采集覆盖率；bit 曾因 DRC NSTD-1/UCIO-1 降级后才生成，不作为板级证据）；无 vivado/xsim/hw_server 残留进程。`.xpr` 于 2026-10-18 02:26:41 被 DSH 的 open/close 回写（相对 HEAD 12 增 1 删，前态无快照，不宣称“未动工程”）。
- 主目录小工程（`vivado/AX7Z020_Gesture`）上板前阻碍：无 XDC；`synth_1` ERROR 且增量检查点 part 与 run 不符、BASIC 不含增量；板卡未上电。**仅适用该小工程，与 2B 无关，不得据此改 `w2b`。**
- 交接检查器（2026-10-19 交付，G2 已过）：`verification/handoff_check.py` 只读、纯标准库，参数 `--worktree/--record/--claim/--json/--print-template`，退出码 0=全 PASS、1=有 FAIL、2=输入/环境错误；检查项 a 工作树/分支/HEAD、b index.lock（`git rev-parse --git-path` 解析）、c 未提交改动归属、d 重型进程、e 心跳、f 状态机、g 证据入口、h 范围越界、i 接管让出契约（仅 --claim）。自测 `python -B -m unittest verification.test_handoff_check -v`（38 用例，真实退出码 0）；证据 `report/evidence/CTRL-HANDOFF-CHECK/hl_20261019_r01/manifest.json`；可选加固 OBS-1/2/3 见该清单。
- 运行逻辑（双 Agent、两级总控）：项目总控（每方一个）→ 阶段总控（由项目总控创建与派卡）→ 阶段内 Developer/Reviewer 子 agent；写权、交接信箱/状态机、检查器用法已写入根 `AGENTS.md`「运行逻辑：双 Agent、两级总控（2026-10-19）」，各窗口开工先读该节。

## 2026-10-26 阶段3–6收尾快照（优先于旧板卡状态摘要）

- 本轮应 Wong 要求停止硬件、编译和开发活动，仅整理状态文档。盘点时 `vivado/xsdb/hw_server/vitis/xsct/xsim` 均无进程、3121 无监听，main/dbdf/w4/w5/w6/w2b/96a3 七棵工作树均无 `index.lock`。Wong 报告已按手册断电重启且 JTAG/A9 恢复；本轮没有重新连接验证，故仍是用户报告，不记为 G3 证据。
- 冻结概况：阶段2A 的 G4/G5 已通过并冻结；阶段2B 的 G4/G5 已通过并冻结（`w2b` HEAD `07c3d39`）。本轮重点阶段：**3 未冻结**（`dbdf` `2ed6609`，VDMA 根因、task-11 完整 SEC、TIMING-17/I/O delay 与部署 G3 重确认开放）；**4 未冻结**（`w4` `33988ed`，RAW G0 未闭合、`ENABLE=0`、推理运行时/P/硬件未完成）；**5 未验收**（`w5` `673d371`，camera/replay 仍未实现，G0/G1/G3/G4/G5 未通过）；**6 未冻结**（`w6` `3be42b8`，离线 F6d/G6b 有效，但阶段 G0/G5 未通过，T6-A03、6-D、6-E 板测未完成）。阶段7本轮未开工作树；阶段0/1未在本次收尾中重新核查。
- 阶段3另有中断前生成的未审 v14 诊断候选：补丁 `dbdf/board/stage3/software/sensor/s3_t04_app_diag_v14_vdma_trace_only.patch`，r04 ELF `dbdf/tmp/s3r06/t05_vdma_start_trace_20261026_r04/app/an5642_j11cmos2_v14_vdma_trace_only.elf`（SHA-256 `5c1e5b2c8183266d35a1ff3b7c40abcf55035d77808effe5275cf5dcb95e8b12`）；仅 make-only，未审、未运行、证据包不完整，**不得部署或视为验证通过**。该应用会复位/重配传感器并配置、启动 VDMA；未进行板上操作。
- 截至 2026-10-26 18:03 的快照记载为 Codex 持有写权、尚无 OFFER；main 当时 408 项，dbdf/w4/w5/w6 当时分别 4/13/0/17 项。该记录仅为交接前快照，由下方 19:05 当前交接行更新；此前改动继续原样保留。

- 当前交接行（11字段，2026-10-26 19:05 UTC+8）：任务=CTRL-DSH-HANDOFF：main 与阶段3写权正式 OFFERED，等待 DSH 项目总控认领阶段3 | 负责人=Codex 项目总控（让出方） | 工作树/分支=D:\FPGA_Competition / main；D:\codex-worktrees\dbdf / codex/stage3-video | 起始提交=main bdb7a360916641382a04f018c668774543e45b8e；dbdf 7e4a0a5699c9034d6b6f3e42b2aa5bee24b5aeb3 | 允许修改范围=main 项目总控与全局状态；阶段3按 dbdf 独立交接行；w4/w5/w6、w2b、96a3 不在本次交接范围；本 OFFER 不授权新的编译、下载、烧录或板级窗口 | 未提交改动归属=main 原有409项及本次新增 Codex mailbox OFFER 记录，共410项；dbdf原有4项及本次 STATE OFFER 行，共5项；全部原样保留，不清理、不回退、不全量暂存 | 让出声明=Wong 明确要求 main 交接行置 OFFERED、由 DSH 项目总控认领阶段3；当前 main/dbdf 无 index.lock、无 Vivado/XSDB/hw_server/Vitis/XSCT/XSim 进程、3121 无监听；dbdf 最新状态对阶段3 G5 的记录与 18:03 快照冲突，须由接手方核对；本轮 Codex 未做技术或硬件操作 | 心跳(UTC+8)=2026-10-26 19:05 | 证据入口=report/evidence/CTRL-DSH-HANDOFF/codex_mailbox/CDX-20261026-001-main-stage3-write-offer.md；report/evidence/CTRL-DSH-HANDOFF/dsh_mailbox/DSH-20261026-001-stage3-and-main-write-handover-clarification.md；dbdf/.codex/STATE.md；report/evidence/S3-T17/t17_takeover_20261026_r01/manifest.json | 恢复命令=git -C D:/FPGA_Competition status --short; git -C D:/codex-worktrees/dbdf status --short; git -C D:/FPGA_Competition rev-parse HEAD; git -C D:/codex-worktrees/dbdf rev-parse HEAD | 状态/下一接手方=OFFERED / DSH 项目总控为下一接手方，须对 main 与阶段3分别完成核验并显式 CLAIMED；在回执到达前不声称 DSH 已接手；w4/w5/w6 等阶段写权不随本 OFFER 转移

## Git 与下一步

- 2026-10-18 工具接入 CTRL-HARNESS：固定上游`17e690cf9a56fc65fe39b2c214276cfdcb5a1891`/Relay0.2.18，仅豁免DSH`0.2.1-rc.2`。独立原生owner Peer补丁独审PASS（16/16）、全回归253/253 PASS、构建/官方安装exit0，源码/安装哈希未变；P05提交`4722cd5`。Wong指定现有空白会话`session-8769e7d0-c6f4-49dc-9667-7ad80ed5dbe1`及`jl-ds/deepseek-v4.1-flash/high`后，授权验收窗口`01a14da3-2112-7f51-9ea9-59618413d762`通过原生start_review/read-only和wait_run取得终态succeeded/精确ACK；run=`925e9e22-a198-4614-8313-7317fb53da0d`，30.988秒。主控核对10次原生调用元数据、实际安装哈希与9项源码、原16项脏文件哈希不变，只读连通验收通过。证据`report/evidence/CTRL-HARNESS/native_ack_20261018_r07/`；首次空scope数组校验失败保留，依正式optional语义省略四字段后成功，未扩大权限。模型内部工具/读取事件未采集，不宣称零读取；工程读写协作/生产稳定性/板卡验收未测。仍为获批精确版本实验兼容，未借browserPeer/读密钥/改native策略、未重启Codex或写2B/硬件；旧失败证据保留。
- 2026-10-19 CTRL-HARNESS 公开合成文件测试发现真实权限投影故障：`PERMISSION_DENIED / permissions session projection is not registered`；失败发生模型提示提交前，分配operation/run标识但无run快照；通过正式`reconcile_permissions`恢复原权限，未删锁。最小候选改为逐操作解析当前权限服务、缺失仍拒绝；独审PASS仅限未上线候选，258/258回归、构建/包检查及实际DSH Cordis4.0.5的5/5生命周期测试通过。证据`report/evidence/CTRL-HARNESS/permission_projection_20261019_r01/`。**候选尚未安装，原生读取/写回测试未通过，不能称插件适配完成**；当前安装bundle仍SHA `2004bc01…`，待Wong从托盘正常退出DSH后按官方CLI替换固定候选包并同范围复测；不强杀、不扩大权限、不重启Codex或2B。真实CSR源码向`jl-ds`处理的另项请求被外传审批拒绝，未重试；合成测试不替代该授权。
- 历史治理记录：2026-10-08 用户要求改用新建的独立工作树/阶段2B总控窗口、旧2B窗口暂不使用，主目录与阶段3已有未提交改动保持不动，新工作树必须先核对冻结基线、不复制主目录全部未提交内容；交付规则见 `AGENTS.md`「产物落点、阶段对接与 ROSS 使用」及 `report/README.md`，只读检查器提交 `9db8d64` 已通过 50 项回归与独立审查（证据 `report/evidence/CTRL-DELIVERY/validation_20261008_2054/`），它只核对当前声明的输入/证据，不代表阶段 G0/G4/G5 或实物通过。
- 历史维护记录：2026-10-11 按 Wong 授权清理可重建缓存（C 盘仅 npm/pip 下载缓存，净释放 6,073,454,592 B；D 盘仅当前候选 109 个成功 RunId 下 218 个精确 PCH 文件，净释放 31,633,760,256 B；失败目录、模型/数据、波形、2B/3 工作树与用户原改动不动；清单见 `report/evidence/CTRL-CLEANUP/cache_cleanup_20261011_r01/cleanup_record.json`）；ROSS 2026.9.1 独立 Tcl 冒烟通过（Vivado 2026.1 退出码 0；证据 `report/evidence/CTRL-ROSS-SMOKE/ross_tcl_20261008_192127/`，未测 IP/综合/实现/硬件）。
- 历史 T68 源映射修复基线为 `65dd1c310e7686d50685d2f83b9b2b623e6cf3ad`。候选实现提交 `999238284157bed77cdb3a37e3e6eea52daeefc4` 包含 tile engine、T66 testbench 与 runner；2026-10-06 G4 acceptance/OOC 综合证据提交为 `a232bc7c815a1e9bb18c675b0e9f31bccd857c62`。均未推送；保持其他阶段改动、运行目录、shards、模型数据、密钥和构建产物不入提交。
- 下一步：发令总控按本次补验关闭记录及其所在Git提交核对交付；r03源码/工具/报告/日志清单核验与独立审查均通过，旧目标成果、109功能证据和r01/r02失败证据保留。r03脚本是已执行快照，不能重复prepare；后续综合须新RunId、路径、namespace及重新绑定哈希，源码可从冻结14项Git blobs恢复。摄像头/HDMI等尚未计入本次核心OOC；阶段7各资源≤85%的初始目标下DSP仅余1、LUT余4,670，完整系统资源/带宽/时序仍须后续评估；不自动越过2B/3阶段边界。

## 冻结声明（2026-10-28，Wong 指令「冻结阶段45」）

- **阶段5 离线冻结**：tag stage5-offline-freeze-20261027-r3 -> 679b8a1；frozen_set 4461bbbc...（tag 与 HEAD 同字节）；93 成员/93 唯一 id；三路 93/93 exit 0；自测 4/4；旧 tag r1/r2 未动。
- **阶段4 离线冻结**：tag stage4-offline-freeze-20261028-r5 -> a0ecc71（tree 5b6fc279）；冻结包 6 个输入类文件（tag 树内 _verification/ 计数=0）；115 成员（17/5/8/85）+ 11 项真实产物身份；真 git archive 导出 4359 文件 -> --disk 115/115 exit 0；五项退出码全 0；验证包为 post-freeze 提交 3ddb0af（不在 tag 内）。
- **未主张**：G3/G4/G5、阶段4/5 验收通过、板级 B1-B10、ENABLE=1（仍 0）；阶段4 未闭合项与阶段5 板级项见 decisions/freeze_declaration_stage4_r5_stage5_r3_20261028_r01.md。
- 迭代中被拦下的真缺陷（r1 假哈希 / r2 导出不可复现 / r3 gitignore 日志入清单 / r4 tag 树含旧验证包）均已记录在该决策文件中。
- **阶段4 冻结勘误（2026-10-28）**：r5 包的 `not_frozen_count` 记录 35、实为 32（`not_frozen` 32 条 = `git status` 32 项）；errata RunId = `stage4_freeze_20261028_r05_errata_20261028_r01`（`ERRATA.md` sha256 `dc7f1b94ebac25c0…32cf3`）；**tag r5 `a0ecc71` 与冻结包 6 文件字节未动**；生成器改为由 `len(frozen_set.not_frozen)` 计数并加 exit 8/9 断言（统计不符/磁盘与 blob 不一致即拒）。

## 阶段5 W-E 板级窗口（2026-10-28）

- 窗口 r02：11:06:35 -> 11:07:55（80 s）；证据 report/evidence/S5-WE/window_20261028_r02/（w5 提交 2decd0d）；w5 工作树干净、未 push。
- 身份四项全等：重建 ELF 6a521a60...、XSA 90e1bdee...、XSA 内 bit 44e609cc...（1,572,373 B）、ps7_init.tcl 4fc10193...；ELF 载入区间 [0x100000,0x130ad40) 与阶段4 候选区无重叠。
- **B1=PASS**（装载 exit 0、S5DL_ALL_DONE=1；读回 xc7z020 / DAP 4ba00477 / A9 两核 Running / DevCfg 0x40000F30）；**B9=PASS**（connect 16 -> disconnect -> reconnect 16，exit 0）。
- **B2/B7=NOT_RUN**（Wong 未确认在场，未用截图替代）；**B3/B4/B5/B6/B8/B10=BLOCKED_BY_DEPLOYMENT**（摄像头->PL->结果显示的合并部署未构建）。
- 前一轮空窗口：执行体失败、无任何证据，只读探测显示两核仍 Running（未复位/未装载），已记 report/evidence/S5-WE/window_20261028_r01/FAILED_ATTEMPT_NOTE.md，进程已清理（4bd9fb8）。
- **未主张**：G5、B1-B10 全部完成、任何超出逐项判定的板级/实时/实物结论。
- **难题移交门槛（2026-10-28 Wong 修订）**：≥3 次尝试仍未解决才单独列出放入 Codex 信箱（原 2 次作废）；移交须附现象/尝试清单/证据路径/请求分析；回执不覆盖旧记录；见 dsh_mailbox/DSH-20261028-013。
- **PL v2 冻结提交 `91fde517…` 窄复审 PASS（2026-10-29 01:35，rev-s5，独立复跑）**：3 项 MAJOR 关闭（4KB 拆分 `ars=2073=1443+630`、`4k_viol=0`；量化除法消除且穷举 0 反例；冻结 manifest 147 条 0 不符、V1–V4 PASS）；6 个 TB 全部自行复跑且 RESULT 与冻结日志逐字相同；BD validate 0/0；**可作为 v2 综合基线**；余 4 项非阻断 MINOR（文档措辞/生成器路径/CRLF/冗余段）。`timing.status=NOT_BUILT`，未主张时序/板上/G3–G5。
- **产品吞吐目标裁决（2026-10-29，Wong 批准）**：目标改为 **30 fps 视频预览/叠加 + 5-10 fps 检测**。依据：2B 引擎仅 1 个 MAC 单元（每拍 1 乘加）导致实测 11.8 s/帧；XC7Z020 DSP=220、100 MHz 理论 22 GMAC/s，YOLOv4-tiny 416 INT8 约 3 GMACs/帧，故 30 fps 检测物理不可达（需约 890 MAC/cycle）。路线：L0 逐层剖析(先做) -> L2 模型缩小(416->208) + L1 引擎并行化(16-32x，待定) -> 组合目标 5-10 fps。4-D 位流工作不受影响；不降低既有判据、不主张已实现。裁决记录 decisions/product_throughput_target_20261029_r01.md。

## 2026-10-29 板级窗口（长跑停住定位 A 项）与 DAP 粘连

- **板卡当前不可用：DAP 粘连**（只读探测 `DAP (APB AP transaction error, DAP status 0x30000021)`，A9 目标消失）。按硬规则 2 只能由 Wong **整机断电（12V+USB ≥10 s）**清除；未用 `-force`。断电重启前任何一方不得再连 JTAG。收窗后进程已清零（hw_server/xsdb/vivado 0、3121 仅 TIME_WAIT）。
- 触发窗口 RunId `bringup_longrun_probe_20261029_r02`（w4 提交 `f0a4178`）= **INVALID_RUN 自伤**：预载真实 RAW+权重后板上 `tensor_crc32=0x5B183B50` 复现，但执行器未置位 `_PL_STATE` → `load_elf_ddr` 走 `rst -system -stop` 清掉刚编程的 PL → 应用首次 `0x43C00000` 读挂死 → 停核失败 → DAP 粘连。作废说明 `w4/report/evidence/S4-T34/bringup_longrun_probe_20261029_r02/ERRATA_INVALID_RUN.md`；**不得引用本次现象作为产品根因证据**。
- 该窗口另两件事实：① W0 打开时候选区与 M3 快照差异 11,850,821 B（已按快照重写、diff 0）；② **W4 收尾恢复未完成** ⇒ 下个窗口第一步必须做 W0 式 dump 对比。
- 已备好、**未执行**的修正执行器：`D:\tmp\lead\probe_long_20261029_r03\run_probe_longrun_r03.py`（sha256 `f525ac03…7d7aeb`）、`D:\tmp\lead\p2b_board_20261029_r01\run_p2b_4d.py`（sha256 `9be5e855…d7fb95`）。已发 `dsh_mailbox/DSH-20261029-005`（回 CDX-20261029-001）。

### 2026-10-29 17:24 断电重启后的第一次板级窗口（A 项重跑）与二次粘连

- **DAP 已恢复**（上电后只读探测：A9 两核 Running、无 AP 错误）→ 开窗 `bringup_longrun_probe_20261029_r03`
  （预载真实 fixture `tensor_crc32=0x5B183B50`、探针五步打印、SW 预处理）。**结果：41 轮全部 `done=1`/`status=0x00000E04`，未停住**；
  窗口在脚本 1950 s 采集上限处切断（第 42 轮在 `wait_done_pre`），应用自身 30 min 口径未达 ⇒ 记 `DIAG_NOT_REPRODUCED_LIMITED`，**不构成稳定性通过**。
  历史停住点 r01=40/r04=23/r05=24 轮 ⇒ 本轮刚超过最长者 1 轮。
- **重要发现：应用自报时间与主机实测差约 4 倍**（两条独立证据：r03 的 41 轮/1950 s vs 11.82 s/轮；14:38 带主机时间戳日志 32.38 s vs 8,096 ms）。
  ⇒ "30 min 长跑"判据实际≈2 h 真实时间；历史"11.8 s/帧"按主机时间≈47 s/帧；2B BD 的 FCLK0 设计值是 50 MHz（非 100）。原因未定，需专门实验。
- **本轮两次窗口自伤并再次粘连板卡**：18:10 的迭代计时窗口在 `program_pl` 之后仍用 `rst -system -stop` 装载（清 PL → 首次 CSR 读挂死，与 15:01 同类），
  随后 `rst -system` 救场使 DAP 再次 `0x30000021`；该窗口与随后的 r02 均标 `INVALID_RUN_ORDERING_BUG`。教训已写进 w4 STATE（执行器硬门禁）。
- **板卡现状：DAP 粘连，需再次整机断电（12V+USB ≥10 s）**；主机侧零残留。下一步顺序：断电 → 5 min 计时三方对照（修正版，先静态自检禁止 `rst -system`）
- **A 项（长跑停住定位）按真实口径通过（2026-10-29 20:20）**：40 轮 / 真实 30.7 min / failures=0 / `exit=0 within_judgement=1` /
  每轮 47,287 ms 恒定 / tensor CRC 恒定；时间基座修复后 host/app=1.000。判据常量 140→38 勘误（140 是旧 4× 口径值）。
- **阶段5 收口文档已出（23:5x）**：P2d README/地址表/证据索引；位流身份只认 bit `58c66cdb…` / XSA `4ebc631e…`。
- **已发信箱 DSH-20261029-007**：更正对 2B 的两条怀疑（超时常量/宿主预置，非 RTL），通报 P2d 方向 A 与"M_AXI 不得并入通用 SMC"约束，请求 M3 工具入口。
- **P2d 上板四窗全绿（23:4x）**：2B 恢复 **47,287 ms**（P2b 85,899 超时→修复成立）、chain-lite A **PASS**、
  preproc→DMA(HP1) **CRC 0x5B183B50**、M4-b 收口 **pass=1**（尾字 lane 正确）。⇒ 阶段5 合并计算体板上可用，剩文档收口。
- **阶段5 方向 A 合并位流 P2d 已构建（23:12）**：2B 直连 HP0、preproc+DMA→HP1；bit `58c66cdb…`、WNS +0.128/WHS +0.036、DSP 158(71.82%)；
  上板三窗口冒烟（M4-b/chainA/P2c-CRC）在跑。
- **B 项（4-D 链路）在 2B 基线位流上全部 PASS（22:5x）**：M3 逐字节相同、M4-a 对拍通过、
  **M4-b pass=1**（尾字 lane 验证）、**chain-lite A pass=1**（检测框与 r13 参考 ≤1e-9）、**chain-lite B pass=1**（CRC 0x5B183B50，8 字段一致），均 47,287 ms。
  P2b 位流上 M4-b/chain 超时属 P2b 慢 2× 的连带（同 ELF A/B 已证），非链路缺陷；阶段5 修 BD 方向 A 即可。
- **M4-b 收口 PASS（22:3x）**：2B 基线上 `pass=1 / diff13=0 / diff26=0 / stale=1 / error=0 / 47,287 ms`；尾字探针 `before=0x5A5A5A5A after=0x5A5A0506`、
  `lane01_ok=1 lane23_ok=1` ⇒ PL 尾字 lane 正确且未越界。关闭方式=参考预置补齐 1268 字 + 输出区投毒。
- **同 ELF A/B（22:4x）**：2B 基线 47,287 ms 完成 vs P2b 85,899 ms 超时 ⇒ **P2b ≥1.82× 慢**（SmartConnect 串行化）；修复方向 A 只改 BD、不需 Codex。
- **head13 尾字已定案（22:2x）**：差异来自**参考预置漏写尾 2 字节**（`run_window_b_driver.py:355` 用 1267 字=5068 B，
  而 head13=5070 B），非 PL 尾字缺陷；补齐 5072 B/1268 字 + 强制 `stale=1` 后即可 PASS（收口窗口已排）。
- **P2b 慢 2× 归因（22:2x）**：主因是 P2b 把 2B 核 `M_AXI` 改经 SmartConnect，而该主端单 outstanding/单 beat ⇒ 串行化，实测 ≥1.817×；
  修复方向 A（只改 BD，infer 直连 HP0、preproc 走 HP1）不需 Codex，方向 B/C 需 Codex。
- **阶段5 范围已定稿**：视频链归阶段6、吞吐归 Codex；P2c r02 即合并体；阶段5 只剩冒烟+收口。
- **M4-b `error=5` 已定因并验证（21:5x）**：旧 ELF 的 `core_timeout=0x40000000`（50 MHz 下 21.47 s）< 单帧 47.3 s ⇒ 必然超时；
  重建 ELF（0xFFFFFFFF）后 2B 基线位流上 **引擎 DONE_SAFE、error=0、47,287 ms**。M4-b 只剩 head13 末尾 2 字节（尾字 lane）差异 ⇒ 一个窄修复即可 PASS。
- **P2b 集成事实（阶段5）**：同一重建 ELF 在 P2b 上 >85.9 s 才超时 ⇒ P2b 的 2B 核比 2B 基线慢约 2×（疑与 preproc 共用数据 smartconnect/HP0），
  这是阶段5 合并体的关键性能事实，需专项测量。
- **M4-b 根因（离线，21:3x）**：`error=5` = 2B 内核 **TIMEOUT**（`s2a_control_csr.sv:59`）；但 timeout 已设 0xFFFFFFFF（85.9 s @50 MHz）、
  实测 47.3 s/帧且 heads 与参考 0 差异 ⇒ 证据不自洽，判 **BLOCKED**，需 2B 侧 ILA/回读（2B 归 Codex）。已发信箱 `DSH-20261029-006`。
- **阶段5 范围收缩（Wong 指示）**：帧率/吞吐任务移交 Codex（不追 5 fps）；视频链移阶段6；
  **P2c r02 已是"2B+preproc+打包+DMA"合并计算体**（DSP 158/220、WNS +0.039、preproc→DMA CRC 已上板验证）⇒ 阶段5 无需新建 BD，
  只剩合并体冒烟（受 error 5 阻塞）+ 文档收口；E 四项已按默认定稿，不再待裁。
- **B 项（P2b 4-D 复验）部分通过**：M3 只读复检逐字节相同（sha `41907f53…`）、M4-a PASS；
  **M4-b FAIL** 且**在 2B 平台位流上复现完全相同**（`status=0x0C05 error=5`，heads 与参考 0 差异）⇒ 非 P2b 特有回归，
  卡在 2B 引擎错误码 5 的语义（现有文档只定义 1/2/6），需查 2B RTL 错误码表后判定。
  另修掉同类驱动缺陷第三例：`run_window_b_driver.load_elf()` 硬编码 `rst -system`（PL 编程后系统复位清 PL）。
- **C 项数据面首次正证（2026-10-29 18:36–18:41）**：P2c r02 位流在板上跑通 `preproc → packer → AXI DMA → HP0`，
  **张量 CRC `0x5B183B50` 与离线 golden 一致**（首尾字节亦逐字节相同；`len_reg=519168` 证明 23-bit 长度生效、无 14-bit 截断）。
  ⇒ PL 预处理上板的**数据面**目标达成（候选位流/单帧 fixture/非合并部署；未冻结、不主张 G3/G4/G5）。
  证据 `w4/report/evidence/S4-T34/s4d_p2c_board_20261029_r01/`（门禁 63 条 0 不符）。计时口径：`pre_done_ms=11`（应用口径）⇒ 真实约 44 ms/帧。
- **18:24 第二次断电后**：DAP 恢复（A9 两核正常枚举）；跑 `s4d_time_basis_20261029_r01` 计时三方对照 → **定因**：
  同一段 DONE 等待**主机 32.18 s / 应用 8.096 s = 3.975**；全局定时器 ≈333 MHz 与 BSP 常量一致 ⇒ **`XTime_GetTime` 时基只有全局定时器的 1/4（≈83 MHz）**。
  ⇒ ① A 项"30 min"判据实际≈2 h；按真实时间 ≈47.4 s/轮，真实 30 min ≈38 轮（历史停住 23/24/40 轮 ≈18/19/32 min 真实）；
  ② 历史"11.8 s/帧"按真实时间 ≈47 s/帧；③ 2B BD FCLK0 设计值 **50 MHz**（非 L0 剖析的 100 MHz）⇒ 产品吞吐/L0 需重算。
  修复：应用改直接读全局定时器（PS-only，已委派 stage4-lead）；修后同窗口复核 host/app≈1.00，再按**真实** 30 min 重跑 A，判据同步勘误。
  证据 `w4/report/evidence/S4-T34/s4d_time_basis_20261029_r01/`（门禁 37 条 0 不符）。**板卡当前空闲可用**。
- 未主张 G3/G4/G5；`ENABLE=0`；未写 QSPI；未改线；未 push。

- 边界：未主张 G3/G4/G5，未写 QSPI、未改线、`ENABLE=0`、未 push。

### 待 Wong 裁决（2026-10-29；板卡恢复后执行）

1. **R0 断电重启（唯一板级前置）**：板卡 DAP 粘连，需 12V + USB 同时断电 ≥10 s 再上电；未断电前不再连 JTAG。
2. **E（阶段5 总闸）合并部署硬冲突**（离线设计包 `D:\tmp\stage5\merged_deploy_20261029_r01\`）：
   - 地址：2B CSR `0x43C00000` 撞阶段3 冻结 `v_tc_0`；preproc CSR `0x43C10000` 撞 `axi_dynclk_0`。建议 `v_tc_0→0x43C20000`、`axi_dynclk_0→0x43C30000`（代价：阶段5 冻结集需修订并重做 F6 导出）。
   - 时钟：第三方表写单域 100 MHz，但 2B/preproc 元数据写死 50 MHz（P2b 实测 FCLK0=50 MHz）。建议仅 FCLK0=50 + FCLK1=150，全程无 CDC。
   - 地址空间：现应用 ELF 跨度 18.04 MiB，第三方给的 `0x02000000–0x03000000` 仅 16 MiB ⇒ 需扩到 ≥20 MiB。
   - 数据通路：preproc `M_AXIS`（519,168 B/帧 INT8 CHW）在任何冻结位流里**无消费者** ⇒ 必须先裁决 DMA（AXIS→MM2S/S2MM→HP0）与 S2MM 中断归属。
   - 资源仅"相加看起来装得下"（≈LUT 50%/BRAM 33%/DSP 66.8%，DSP 余 73），**未实构建**。
3. **C（PL 预处理上板）已有可用候选位流，但未上板**：P2a/P2b 的 `M_AXIS` 无消费者 + 引擎源图基址固定 DDR `0x0` ⇒ 冻结位流上 `tensor_crc32=0x5B183B50` 不可达。已离线构建 **P2c r02**（`w4/report/evidence/S4-T34/pl_v2_p2c_dma_bitstream_20261029_r02/`，bit `022f48fb…d52ca4`、XSA `8051dd48…61bf4c`；preproc `M_AXIS`→64b 打包→AXI DMA S2MM→HP0，DMA 长 23 bit；50 MHz WNS +0.039/WHS +0.042，DSP 71.82%），配套应用变体（含 LENGTH 回读自检、IOC 完成判据、每帧重武装、IRQ_CLR 顺序）。独立复审 rev-s5：初审 CHANGES_REQUIRED（其中 AXI DMA 长度 14 bit 会截断 519,168 B —— 构建/DRC/时序全绿也发现不了）→ 修复后**增量复审 PASS**；manifest 过统一门禁（strict，26 条 0 不符）。**仍未上板**；板卡恢复且 Wong 批准后，可做"真彩/注入 RAW 预载 + P2c 位流 + 张量 CRC 对拍"。r01 位流已作废（ERRATUM）。
4. **第三方地址表纠正**：真表是 `D:\wb-out\task3\address_table.json`（`wc_merged_address_table_v1`）；`D:\wb-out-r2\task3` 是 AXI-Lite 超时守卫 IP，非地址表。
- **B25 已裁决并重申（2026-10-29）**：口径 1 = 与阶段4 冻结契约一致（同会话严格递增、任何回退状态改变前拒绝、仅 0xFFFFFFFF->0 允许、0xFFFFFFFE 无特殊性、复位必须换 session_id）；裁决 decisions/b25_frame_session_semantics_20261029_r01.md（提交 6bb80cb）；回执 dsh_mailbox/DSH-20261029-004、DSH-20261029-005（重申+6-C 收口要求）。阶段6 不得自定义阈值。
