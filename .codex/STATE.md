# 阶段4 状态（写权：DSH 阶段4 总控 CLAIMED / IN_PROGRESS）

更新：2026-10-24 01:00（UTC+8）。工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`。规则见 `D:\FPGA_Competition\AGENTS.md`。
**写权：DSH 阶段4 总控（stage4-lead，由 DSH 项目总控按 Wong 2026-10-24「由DSH接手」派出）持有并 IN_PROGRESS，执行共享任务 `task-21`（全离线）。**

## 接管核对（task-21 目标 1）

- Codex 按 Wong 指令停止写入并交付 `d13610d`；DSH 项目总控以接续记录 `report/evidence/CTRL-DSH-HANDOFF/dsh_claim_20261024_r01/` 正式认领并提交 `f6fa9f0`（承载该认领）。本轮在该 HEAD 上以新记录 `report/evidence/S4-CTRL/t21_takeover_20261024_r02/` 复核：**`HANDOFF_OK` PASS 9 / FAIL 0 / exit 0**（含 `--claimed-path` 越界核验）。
- 核对事实：无 `index.lock`；无重型引擎进程（6 个命中项均为 MCP server 进程，非 Vivado/xsim 引擎）；3121 无监听；**12 项**未跟踪 = 6 ELF + 6 map（`report/evidence/S4-B/s4b_ps_tensor_20261023_r04|r05|r09|r11|r12|r13/s4b_ps_tensor_diagnostic.*`），归属保持 Codex 交接口径（本机恢复产物），**留原位、不入源码 Git、不删不覆盖**，逐文件 SHA 见该 RunId 的 `untracked_sha256.txt`（r13 `.map` SHA 与 readiness 文档引用值一致）。
- **硬件使用权不随工作树交接**：依 `CDX-20261023-019` 本轮不申请、不保留、不占用硬件窗口。
- **已知结构性现象**：DSH 原认领记录写于其自身提交之前（声明 `base_commit=d13610d`），在新 HEAD 上复跑会在检查项 a 报漂移；该 FAIL 已据实保留在 `t21_takeover_20261024_r02/handoff_check_previous_claim_record_drift.json`，判据是认领时刻的 PASS 9 证据，而非事后复跑。
- **交接约定（DSH 项目总控 2026-10-24 裁决）**：交接记录只声明**它被写出的那个提交**，接管时刻的 `--claim` PASS 9 即为认领证据；之后 HEAD 前进造成的检查项 a 漂移属**设计行为**，在 STATE 写明、复跑用 successor 记录即可；`handoff_check.py` 的祖先/successor 语义改造**登记为待排期改进项**（须连同 38 个单测与既有证据包一起改并重审）。

## 本轮交付（task-21）

- **输入契约改绑真实彩色（r04）**：`docs/stage4/s4b_shared_input_result_contract.json` r03→r04 + 人读镜像。新增 `input_source_profiles`：描述性范围标签 `camera_live_colour`（`real_live`）/`camera_capture_replay_colour`（`replay_only`，结论必须标回放）；绑定阶段3 无补偿 SOF `7cb33068…`、运行 ELF `an5642_j11cmos2_v10_read.elf` `1457cda4…`、1280×720/stride 3840、传感器 RGB565、DDR 转储 B/G/R（**不得与模型 RGB888 混同**）、原图坐标口径、逐帧源帧哈希；采集时钟 `PENDING_MEASUREMENT`（未实测不填造）。显式登记 `cdx_015` r02→r03 绑定取代关系（改绑前自检实测 22 PASS/1 FAIL exit 1）。
- **已批准项应用**：`result_contract.stale_rule.stale_limit_ns` 由草案 `null` → **200000000 ns**，`stale_limit_status=APPROVED_BY_WONG` + `approval_reference`（阶段6 批准记录 SHA `d8edb848…`），与 w5 `STALE_AGE_LIMIT_NS` 同源同值；S4-A r06 内 `DRAFT_PENDING_APPROVAL` 标签登记为历史快照（其取代值以批准记录为准，r06 字节未改写）。**『已批准』≠『实现已同步』**：真实链路 stale 判定仍 `NOT_RUN`。
- **RAW 系统 G0 收口**：`docs/stage4/S4B_raw_system_g0_gap_registry.json` 承接 `d4f30e3` 检查点，逐项登记 G-01..G-19 与 J10 范围外不适用项；只读复算 **9/9 算术、8/8 依据件、状态纪律通过**（需硬件缺口一律保持 `NOT_RUN`/`BLOCKED`）；系统 G0 仍 `CHANGES_REQUIRED_NOT_CLOSED`。
- **帧周期 P 实测方案**：`docs/stage4/S4B_frame_period_P_measurement_plan.md` + 证据模板 + 校验器（6/6 负向对照被拒：禁止填造/回放冒充/样本不足/统计矛盾/门禁缺失/计时器未标定）；**数值仍 `NOT_RUN`**，供阶段6 `T6-A03`。
- **契约自检升 r05**：已批准态必须附批准记录且与阶段5 同源；彩色改绑＋批准态共 **8/8** 负向对照被拒；`upstream_bindings` **12/12** 现场复算一致；契约消费方回归 `verification.test_s4_inject_frame` **10/10 OK**。
- **G-01/G-02 待决提案（规范层面，不改实现）**：`docs/stage4/S4B_raw_address_ownership_proposal_20261024_r01.md` + `.json`；算术证据 `report/evidence/S4-CTRL/t21_raw_address_proposal_20261024_r01/`（`scripts/stage4_s4b/check_raw_address_options.py` **exit 0**）。关键事实：2B 窗口内**最大连续空洞 9,825,540 B < 最大帧 11,059,200 B** ⇒ 全 109 覆盖必须扩出窗口或缩小输入范围。候选 **A**（禁区 12 MiB + 相邻 META，109 帧，余量 +1,523,712 B）／**C**（禁区 11 MiB + 窗口内 META，109 帧，余量 +475,136 B）／**B**（窗口内 9 MiB，107 帧，排除 2 张 1920×1920，属需求层覆盖变更）／**E**（`ps_app_arena` 上部，107 帧，耦合 linker 布局）。**裁决前 G-01/G-02 状态不变、`ENABLE=0`、不访问候选区**；D1–D4 见提案 §5。

## 证据入口（本轮新 RunId，`report/evidence/S4-CTRL/`）

- 接管：`t21_takeover_20261024_r02/`（`t21_takeover_20261024_r01/` 为首次尝试失败输出，保留）。
- 契约改绑：`t21_contract_colour_rebind_20261024_r02/`（`…_r01/` 为改绑前基线 22P/1F exit 1）。
- RAW G0：`t21_raw_g0_gap_registry_20261024_r03/`（`…_r01/` KeyError 失败、`…_r02/` 被 r03 取代，均保留）。
- P 方案：`t21_frame_period_p_plan_20261024_r01/`。
- 通用交付检查器：**evidence 模式 4/4 `CHECKS_OK` exit 0**；inputs 模式按设计被阻断（契约/地址图仍 `DRAFT_PENDING_REVIEW` 未冻结，且含 FAIL/NOT_RUN 检查），原始输出在 `tmp/4/S4-T21/t21_delivery_check_20261024_r02/`。
- 落点更正：本轮 RunId 起初误建为 `S4-CTRL/S4-T21/<run_id>`（多一层），已上移为 `report/evidence/S4-CTRL/<run_id>` 以符合 `report/evidence/<task_id>/<run_id>/` 约定；个别结果 JSON 内记录的 `--evidence-dir` 仍为迁移前路径，仅路径字符串差异，内容未改写。

## 未闭合 / 下一步

- 契约 r04、RAW 缺口登记表与 P 方案**尚无独立复审**（本阶段总控受委派深度限制，不能创建子代理）；须由 DSH 项目总控派 Reviewer。
- RAW 系统 G0 缺口：地址/所有权批准（G-01/G-02 `BLOCKED_PENDING_APPROVAL`）、D2 整帧/padding 数值（G-04）、HP0 串行 owner 与排空（G-05）、平台 BD/XSA（G-07）、PS RAW task 与旧 memcpy 冲突（G-08）、协议项（G-09/G-10/G-11/G-13）、资源与布线后时序（G-14）、mailbox ABI 审查（G-15）。
- 硬件相关**全部 `NOT_RUN`**：八类门禁与正式 OFFER/CLAIM（G-16）、4-D 验收（G-17）、真实彩色回归（G-18）、帧周期 P（G-19）。
- 4-D 与阶段4 G5 未完成；不得把离线/回放结论升级为实物集成结论。
- **G-01/G-02 进展（lead 已裁 D1–D4）**：D1=**有条件批准选项 A**（不选 C）；D2 建议不接受 107 帧子集（决定权报 Wong）；D3 META 不强制与 RAW 相邻；D4 不前置 linker 冻结 ⇒ 选项 E 排除。裁决记录 `report/evidence/CTRL-DSH-HANDOFF/decisions/stage4_raw_address_d1_d4_20261024_r01.md`。
- **条件①交叉核对已取证**：`report/evidence/S4-CTRL/t21_raw_address_crosscheck_20261024_r03/`（`scripts/stage4_s4b/crosscheck_raw_address_owners.py` **exit 0**）。结论：候选 `[0x12000000,0x12C08000)` 与 **2B 全部对象**（含专属窗口——候选自窗口末端 `0x12000000` 起）及 **阶段5 送显三缓冲**（事实取 w5 `S5-T01` 已提交运行清单：`0x00114C00/0x00703800/0x00CF2400`，`ADDR_S2MM==buf0`，720×3840=0x2A3000/帧）**均不相交**；**阶段3 自身未发布静态地址事实**（仅有代码级 `dispCtrl.framePtr[curFrame]` 与每帧 0x2A3000）⇒ 条件①标记 **`INCOMPLETE_PENDING_STAGE3_WRITTEN_FACT`**。**取证未齐，故本轮未落盘任何地址图/契约改动**（`ENABLE=0`、不访问候选区）；已请 lead 向阶段3 索取书面静态事实。
- **005 回执状态**：`dsh_mailbox/DSH-20261024-005-2b-address-confirm-raw-region.md` 已发出；`codex_mailbox/` 截至本轮**无 `CDX-20261024-*` 回执**，2B 书面确认未到。
- **下一轮必修（不为此单独开轮）**：把 RunId 迁移前写入的 `--evidence-dir` 字符串在下一轮以新 RunId 重跑修正——`t21_contract_colour_rebind_20261024_r02/verify_shared_io_contract_result.json`、`t21_raw_g0_gap_registry_20261024_r03/raw_system_g0_gap_audit_result.json`、`t21_frame_period_p_plan_20261024_r01/frame_period_p_validation_result.json`；内容未改写，仅路径字符串差异。
- **待排期改进项**：`handoff_check.py` 祖先/successor 语义（须连同 38 个单测与证据包一起改并重审）——本轮不展开。

## 必须保持的接口与边界（承接）

- 2B 正式冻结 `07c3d3958578b9cc9d3b8eae3758711fe08724c2`：1000 连续任务、108 ACK 闭环样本；109 黄金 ≠ 109 ACK 闭环。
- UART 方案 B：`s2bu/1.1` 正文不变、扩展关闭；时间/丢帧/过期/状态只记 PS 侧（`(session_id, frame_id, result_seq)` 唯一映射）。
- 候选上限 12675 可行、12676 硬错误；4096 禁用；注入须位于被验收预处理前；`capture_time_available=false`、`capture_time_ns=0` 哨兵，`injection_start_ns` 不得冒充采集时间。
- 保护旧已冻结离线链与全部旧 RunId：`s4_ps_decode.*`、`s4_uart_protocol.*`、`s4_offline_host.c`、`run_s4b_offline_chain.py`、`build_s4b_manifest.py`、`test_s4_ps_decode.py`；不得改写 `d4f30e3`/`d13610d` 的历史提交与证据。
- 2B/阶段3/阶段5/阶段6 工作树与厂商原件只读；本树一次只跑一个重型任务；不 push。
- **换行前提（与阶段3 同口径）**：本树**不加 `.gitattributes`**；新产物统一写 LF，复算证据哈希绑定必须用 `-c core.autocrlf=false`，否则换行归一化会造成 SHA 失配。

## 交接行（11 字段）

任务=`task-21 阶段4 接续（DSH 认领 w4）：契约改绑真实彩色 + 应用已批准项 + RAW 系统 G0 收口 + 帧周期 P 方案（全离线）` | 负责人=`DSH 阶段4 总控（stage4-lead）` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`f6fa9f0d84274f1a0d03e6f87263fb550ebc6656` | 允许修改范围=`docs/stage4/、scripts/stage4_s4ctrl/、scripts/stage4_s4b/、verification/、report/evidence/S4-CTRL/、.codex/STATE.md`（主目录与其他树、硬件均无授权） | 未提交改动归属=`12 项未跟踪 6 ELF/6 map 属 Codex 本机恢复产物，留原位不入 Git；本轮新文件随本次提交` | 让出声明=`w4 由 DSH 阶段4 总控持有至本轮收尾；硬件使用权未随交接，阶段4 板级依 CDX-20261023-019 暂缓，恢复须另行申请窗口` | 心跳(UTC+8)=`2026-10-24 01:00` | 证据入口=`report/evidence/S4-CTRL/t21_takeover_20261024_r02/、t21_contract_colour_rebind_20261024_r02/、t21_raw_g0_gap_registry_20261024_r03/、t21_frame_period_p_plan_20261024_r01/` | 恢复命令=`git -C D:/codex-worktrees/w4 log --oneline -3; git -C D:/codex-worktrees/w4 status --short; python -B D:/codex-worktrees/w4/scripts/stage4_s4ctrl/verify_shared_io_contract.py` | 状态/下一接手方=`IN_PROGRESS / 本轮收尾后由 DSH 项目总控指派独立复审与后续（含硬件窗口申请）`