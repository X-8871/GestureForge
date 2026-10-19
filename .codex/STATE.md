# 项目状态入口

更新：2026-10-19（UTC+8）。按根目录 `AGENTS.md` 恢复；阶段验收以当前代码、Git 和报告证据为准。主目录只维护全局状态、任务归属与阶段入口。

## 当前目标与阶段

- 阶段2A「PL 推理仿真」旧XA/-1目标已完成 G4/G5 独立审查并冻结；2026-10-09 新XC/-2限定同源OOC补验也经独立审查PASS并完成技术G4/G5收尾，冻结入口见下文。用户已批准 8×8 空间 tile、8 路输出通道并行；保持 T01 冻结的 CSR、32-bit 单 word memory 接口、timeout 和握手协议。
- 用户已启动独立阶段2B总控；本窗口按其已授权任务补验阶段2A的新器件适用性。2026-10-08 Wong 确认器件输入 `XC7Z020-2CLG400I`；实际 Vivado 目录唯一解析为 `xc7z020clg400-2`。旧 XA/-1 冻结及全部功能证据保留，新器件相关验收须另行补齐；本轮未改硬件工程或进行实物操作。
- 本主目录先前2B只读核查未通过G0，独立2B工作树的后续状态以其自身STATE/证据为准：T01 已冻结 tiny416 模型、两检测头及 D9 解码/NMS，不能继续称这些未冻结；物理 PS/PL 地址映射、AXI/DDR 传输、DMA/cache 和缓冲所有权由2B总控冻结。新器件编号依据本轮用户确认和手册，新实板与 PCB/BOM/DDR 图纸的独立对应仍未知；旧板照片及已有 `.xpr` 的 XA/-1 记录保留历史身份，不能直接沿用其 PS/DDR 配置。当前主工程无 PS Block Design、Vitis 平台或板级 XDC。
- 本轮未改2B/3的独立工作树，仅处理2A器件适用性补验。阶段2B后续任务须先冻结物理接口和适用器件资料；板卡下载、上电、DDR/UART实测等实物操作须另行明确授权。
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
- 交接行格式：`任务 | 负责人 | 工作树/分支 | 起始提交 | 允许修改范围 | 未提交改动归属 | 状态 | 下一接手方`；当前交接记录见下方「阶段入口与任务归属」。
- 环境事实（2026-10-17）：DSH 沙箱在 `D:\FPGA_Competition` 的写入授权已修复（仅给当前用户补完全控制，未删除任何条目，回滚脚本在 `D:\dsh_acl_recovery\20261017\`）；Git Bash 的 `bash.exe`/`sh.exe` 在受限沙箱下报 signal pipe Win32 5，改用 git 直调与 Python。用户级 `TEMP`/`TMP` 已设为 `D:\tmp`（2026-10-17，新进程生效，Vivado/xsim/Verilator 共用；已运行进程需重启后才切换）。

## 阶段入口与任务归属（2026-10-18 核实）

| 阶段 | 工作树 | 分支 | HEAD | 状态入口 |
|---|---|---|---|---|
| 2A（已冻结） | `D:\FPGA_Competition` | `main` | 见下方冻结提交 | 本文件下方 2A 证据段 |
| 2B（进行中，Codex） | `D:\FPGA_Competition\w2b` | `codex/stage2b-dma-g0` | `5e26eddb`（2026-10-19 只读核实） | `w2b/.codex/STATE.md`及该树最新证据 |
| 3（未启动） | `D:\codex-worktrees\dbdf` | `codex/stage3-video` | `896e6c7` | 该工作树自身 |
| 较早 2B | `D:\codex-worktrees\96a3` | `codex/stage2b-t01-board-audit` | `e26feea` | 仅历史参考 |

- 主目录 STATE 只维护全局状态、任务归属与阶段入口；阶段技术事实以对应工作树 STATE/证据为准，不在此复制全文。
- 2B 当前恢复观察（2026-10-19）：R14 是历史失败，不能继续称当前阻断。正式 R02 `formal_stress1000_then109_20261018_r02` 已运行；07:49 只读观察为 574 个连续 stress 结果、109 尚未执行，独审仅 `PASS_PREFIX_ONLY`，不是1000/109或G4/G5通过。入口为 `w2b/report/evidence/S2B-T18/resume_observation_20261019_r01/`及实际运行目录；恢复先核实进程完整身份与新日志，不因旧PID/HEAD或本行快照重启任务。用户现优先完成DSH插件适配，2B健康硬件后台保持独占、不干预。
- 交接记录（一行式）：任务=`交接核实与统一入口补齐` | 负责人=DSH | 工作树/分支=`D:\FPGA_Competition`/`main` | 起始提交=`51f7130` | 结束提交=`b87dd4f`（主提交 `7d56a24`） | 允许修改范围=`.codex/STATE.md`、`.codex/DSH_HANDOFF_20261018.md`、`report/evidence/CTRL-DSH-HANDOFF/**` | 未提交改动归属=主目录原有 403 项属 Codex/用户、DSH 未动；`w2b` 104 项属 Codex | 状态=本轮已提交、待 Codex 只读复核 | 下一接手方=Codex
- 环境事实（2026-10-18）：`TEMP/TMP=D:\tmp`（用户级）；Vivado BASIC 许可 `D:\Xilinx_licenses\basic_only.lic`（至 2027-08-07，仅注入 DSH MCP env，用户级 `XILINXD_LICENSE_FILE` 为空）；DSH MCP：`vivado-mcp`(ROSS stdio)、`vivado-py`、`amd-doc-search`(HTTP 8080，服务已停)；ROSS 技能 50 目录 / **49 个 `SKILL.md`**；C 盘 41.2 GB、D 盘 38.0 GB 可用。
- 环境路径索引（2026-10-19 核实）：项目根 `D:\FPGA_Competition`（主工作树 `main`，可写）；2B 工作树 `D:\FPGA_Competition\w2b`；厂商原件 `D:\FPGA\AX7Z020\AX7Z020`（**只读，保持不动**）；Vivado 2026.1 安装 `D:\Xilinx\2026.1`（启动器 `D:\Xilinx\2026.1\Vivado\bin\vivado.bat`）。
- Obsidian 本项目仓库（2026-10-19 核实）：`C:\Users\22061\Documents\Obsidian Vault\02-项目\基于 AX7Z020 的低比特神经网络 FPGA 加速系统，实现摄像头手势识别并驱动板卡进行实时交互`；操作前先读该 Vault 的 `00-AI全局整理规则.md`，不导入其他 Vault 内容，该规则不得由工具/技能扩权。
- 探针证据包 `report/evidence/CTRL-DSH-HANDOFF/handoff_20261018_r01/`：只证明工具链可用（综合/实现/比特流/xsim，原生日志与退出码已封包；xsim 未采集覆盖率；bit 曾因 DRC NSTD-1/UCIO-1 降级后才生成，不作为板级证据）；无 vivado/xsim/hw_server 残留进程。`.xpr` 于 2026-10-18 02:26:41 被 DSH 的 open/close 回写（相对 HEAD 12 增 1 删，前态无快照，不宣称“未动工程”）。
- 主目录小工程（`vivado/AX7Z020_Gesture`）上板前阻碍：无 XDC；`synth_1` ERROR 且增量检查点 part 与 run 不符、BASIC 不含增量；板卡未上电。**仅适用该小工程，与 2B 无关，不得据此改 `w2b`。**
- 交接检查器（2026-10-19 交付，G2 已过）：`verification/handoff_check.py` 只读、纯标准库，参数 `--worktree/--record/--claim/--json/--print-template`，退出码 0=全 PASS、1=有 FAIL、2=输入/环境错误；检查项 a 工作树/分支/HEAD、b index.lock（`git rev-parse --git-path` 解析）、c 未提交改动归属、d 重型进程、e 心跳、f 状态机、g 证据入口、h 范围越界、i 接管让出契约（仅 --claim）。自测 `python -B -m unittest verification.test_handoff_check -v`（38 用例，真实退出码 0）；证据 `report/evidence/CTRL-HANDOFF-CHECK/hl_20261019_r01/manifest.json`；可选加固 OBS-1/2/3 见该清单。

## Git 与下一步

- 2026-10-18 工具接入 CTRL-HARNESS：固定上游`17e690cf9a56fc65fe39b2c214276cfdcb5a1891`/Relay0.2.18，仅豁免DSH`0.2.1-rc.2`。独立原生owner Peer补丁独审PASS（16/16）、全回归253/253 PASS、构建/官方安装exit0，源码/安装哈希未变；P05提交`4722cd5`。Wong指定现有空白会话`session-8769e7d0-c6f4-49dc-9667-7ad80ed5dbe1`及`jl-ds/deepseek-v4.1-flash/high`后，授权验收窗口`01a14da3-2112-7f51-9ea9-59618413d762`通过原生start_review/read-only和wait_run取得终态succeeded/精确ACK；run=`925e9e22-a198-4614-8313-7317fb53da0d`，30.988秒。主控核对10次原生调用元数据、实际安装哈希与9项源码、原16项脏文件哈希不变，只读连通验收通过。证据`report/evidence/CTRL-HARNESS/native_ack_20261018_r07/`；首次空scope数组校验失败保留，依正式optional语义省略四字段后成功，未扩大权限。模型内部工具/读取事件未采集，不宣称零读取；工程读写协作/生产稳定性/板卡验收未测。仍为获批精确版本实验兼容，未借browserPeer/读密钥/改native策略、未重启Codex或写2B/硬件；旧失败证据保留。
- 2026-10-19 CTRL-HARNESS 公开合成文件测试发现真实权限投影故障：`PERMISSION_DENIED / permissions session projection is not registered`；失败发生模型提示提交前，分配operation/run标识但无run快照；通过正式`reconcile_permissions`恢复原权限，未删锁。最小候选改为逐操作解析当前权限服务、缺失仍拒绝；独审PASS仅限未上线候选，258/258回归、构建/包检查及实际DSH Cordis4.0.5的5/5生命周期测试通过。证据`report/evidence/CTRL-HARNESS/permission_projection_20261019_r01/`。**候选尚未安装，原生读取/写回测试未通过，不能称插件适配完成**；当前安装bundle仍SHA `2004bc01…`，待Wong从托盘正常退出DSH后按官方CLI替换固定候选包并同范围复测；不强杀、不扩大权限、不重启Codex或2B。真实CSR源码向`jl-ds`处理的另项请求被外传审批拒绝，未重试；合成测试不替代该授权。
- 2026-10-08 用户要求改用新建的独立工作树/阶段2B总控窗口，旧2B窗口暂不使用；主目录与阶段3已有未提交改动保持不动。新工作树必须先核对冻结基线，不复制主目录全部未提交内容。
- 新增交付规则见 `AGENTS.md`「产物落点、阶段对接与 ROSS 使用」及 `report/README.md`；只读检查器提交 `9db8d64` 已通过50项回归与独立审查，证据 `report/evidence/CTRL-DELIVERY/validation_20261008_2054/`。它只核对当前声明的输入/证据，不代表阶段 G0/G4/G5 或实物通过。
- 2026-10-11 按 Wong 授权清理已结束任务的可重建缓存：C盘仅npm/pip下载缓存，操作时净释放6,073,454,592 B；D盘仅当前候选109个成功RunId下218个精确PCH文件，净释放31,633,760,256 B。其余8,434个候选文件前后SHA一致，109个可执行文件保留；全部失败目录、模型/数据、波形、2B/3工作树及用户原16项修改不动。范围经独立Reviewer PASS；精确清单、命令和空间口径见 `report/evidence/CTRL-CLEANUP/cache_cleanup_20261011_r01/cleanup_record.json`，不是全库清空，下载/PCH缓存后续可重建。
- 本次 ROSS 2026.9.1 独立 Tcl 冒烟已通过：Vivado 2026.1 `version` 与 Tcl 查询完成码均为0，状态健康且仅本次会话已关闭；证据 `report/evidence/CTRL-ROSS-SMOKE/ross_tcl_20261008_192127/`。未测试 IP、综合/实现或硬件，不能由此关闭上文2B G0阻碍。
- 历史 T68 源映射修复基线为 `65dd1c310e7686d50685d2f83b9b2b623e6cf3ad`。候选实现提交 `999238284157bed77cdb3a37e3e6eea52daeefc4` 包含 tile engine、T66 testbench 与 runner；2026-10-06 G4 acceptance/OOC 综合证据提交为 `a232bc7c815a1e9bb18c675b0e9f31bccd857c62`。均未推送；保持其他阶段改动、运行目录、shards、模型数据、密钥和构建产物不入提交。
- 下一步：发令总控按本次补验关闭记录及其所在Git提交核对交付；r03源码/工具/报告/日志清单核验与独立审查均通过，旧目标成果、109功能证据和r01/r02失败证据保留。r03脚本是已执行快照，不能重复prepare；后续综合须新RunId、路径、namespace及重新绑定哈希，源码可从冻结14项Git blobs恢复。摄像头/HDMI等尚未计入本次核心OOC；阶段7各资源≤85%的初始目标下DSP仅余1、LUT余4,670，完整系统资源/带宽/时序仍须后续评估；不自动越过2B/3阶段边界。
