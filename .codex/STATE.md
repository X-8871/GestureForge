# 阶段4 状态（写权：Codex 项目总控 / IN_PROGRESS；上次 OFFER 已撤回）

## 当前任务（S4-T26-GOLDEN-CONTROL，2026-10-26 20:44 UTC+8）

- Wong 明确撤回 `d2262bc` 的 w4 OFFER，由 Codex 继续 task-26；**DSH 不 claim**。仅修改 w4；不操作板卡、JTAG、COM4 或 Vivado，不改写 main/dbdf/w2b/w5/w6。
- 起始提交 `d2262bca4c562cf2ff9037e6ed098e37f3d62596`；原有 STATE 差异及 12 个 ELF/MAP 已逐项核验、保持原位。初始归属与 SHA：`report/evidence/S4-CTRL/s4t26_golden_control_20261026_r01/initial_snapshot.json`；原始 STATE 临时恢复快照在该清单声明的 tmp 目录，不纳入提交。
- 执行顺序：修正固定提交/祖先绑定并独立复审 → 当前 Darknet/hook 对 T29 `test_fist_000` 导出 layer 29/36、按冻结 scale 量化并逐字节控制对拍 → **仅完全一致后**生成指定校准样本新黄金和 producer 记录，再推进真实推理/回放。任何控制差异立即停止，结果保持 BLOCKED。
- `ENABLE=0`、RAW 系统 G0 未闭合、P/4-D/G3/G5 NOT_RUN 继续有效；本任务不自动解除这些关口。

## 当前交接行（11字段，2026-10-26 20:44 UTC+8）
任务=`S4-T26-GOLDEN-CONTROL：撤回 OFFER、修正基线绑定并执行独立黄金控制` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`d2262bca4c562cf2ff9037e6ed098e37f3d62596` | 允许修改范围=`仅 w4 内 task-26 相关代码、文档、新 RunId 证据和 STATE` | 未提交改动归属=`原有 STATE 用户差异及12个ELF/MAP保留、不混入提交；本轮新证据和状态增量归当前Codex` | 让出声明=`Wong 已撤回上次 OFFER；Codex 继续 task-26，DSH 不 claim；硬件与其他工作树无操作授权` | 心跳(UTC+8)=`2026-10-26 20:44` | 证据入口=`report/evidence/S4-CTRL/s4t26_golden_control_20261026_r01/initial_snapshot.json` | 恢复命令=`git -C D:/codex-worktrees/w4 rev-parse HEAD; git -C D:/codex-worktrees/w4 status --short` | 状态/下一接手方=`IN_PROGRESS / Codex 项目总控；DSH 不 claim`

## task-26 G0 接续结果（2026-10-26 19:32 UTC+8；r10 为最终固定输入预检）

- 修复两轮 Reviewer 意见后，权威直接命令运行 `s4t26_g0_inputs_20261026_r10` 返回 **BLOCKED / exit 2**，无 FAIL。既有 Python 3.12.10 可导入 `cv2 4.13.0`；校准清单 SHA `d637a2fe…a1a35c`、D8 cfg `5475dff0…725376`、weights `3984affa…f7d8a`、GF8 `f6feb6d4…93cc39`、S4-A r06 与 activation report SHA 均匹配冻结绑定。缺失必需文件/绑定和 task-25 字段分类为 BLOCKED；task-25 状态核验使用 `--no-optional-locks` 并记录 dbdf index 前后 SHA 不变；RunId 必须显式提供且已存在目录拒绝覆盖。
- 缺失输入故障注入 `r08`（S4-A 路径不存在）与 `r09`（task-25 包目录不存在）均完整生成 preflight 与 delivery manifest、返回 BLOCKED/2、无 FAIL；正式输入未被改动。Reviewer 对 r07 的 CHANGES_REQUIRED 为“缺输入时 delivery manifest 仍无条件计算 SHA/解引用”；当前检查器用可空 SHA 与空输入记录关闭该项，r08/r09 已覆盖两条缺失路径。
- task-25 包从明确提交 `584b07664e88a18bf786ba9565a138861e136d76` 消费，清单 SHA `616da71d…067b6e`；源帧提交 `0ad2000cbc4af7b29f299c2277465bba608a8129`，SHA `939fce22…6752f0`，1280×720 BGR888 输入字段完整。其 `capture_time_ns` 是秒级 `replay_documented_wallclock`，仅作 `replay_only`；不把 `injection_start_ns` 当采集时间。
- 阻断：冻结校准样本 `D:\FPGA_Data\HaGRIDv2\dataset\fist\fist\98529267-1eda-43a6-8e38-245947ecb312.jpg`（SHA `c116ba1d…35ee70b`）的历史记录只有 metrics/integer_stats，无同 SHA 的独立 raw head13/head26 黄金；activation report 引用的 Darknet EXE SHA `f025f5ab…229948`、hook 源 SHA `0487e694…7ef7d65` 与固定路径当前字节不符；旧桥接入口固定 w4/dbdf HEAD 与本任务指定基线/精确 task-25 来源不符，未执行该入口。
- 实际网络推理、raw head 对拍、D9/NMS、负向对照、PNG `IMREAD_UNCHANGED` 检查和硬件运行均 `NOT_RUN`；未生成 task-27/28 冻结推理结果。继续保持 `ENABLE=0`、RAW 系统 G0 未闭合、P/4-D/G3/G5 `NOT_RUN`；s4-shared-io r06 仍 `DRAFT_PENDING_REVIEW`。
- 验收证据：权威目录 `report/evidence/S4-CTRL/s4t26_g0_inputs_20261026_r10/`（预检 JSON SHA `72f87a8b…65233a`；检查器 SHA `c31d09e4…62025d`）。dbdf task-25 输入与显式提交核验通过，状态检查 index SHA 前后相同；r03-r09 作为前置诊断/故障注入尝试原样保留。既有 12 个 ELF/MAP 哈希复核未变、既有 STATE 差异保留。

## 历史交接行（11字段，2026-10-26 19:40 UTC+8；OFFER 已由当前任务撤回）
任务=`S4-CODEX-T26-OFFLINE G0 阻断收尾并交还 w4 写权` | 负责人=`Codex 项目总控（当前让出方）` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`33988ed7e8a97a9d5395b8cfd136a327c37d7dc9` | 允许修改范围=`docs/stage4/；scripts/stage4_s4ctrl/；scripts/stage4_s4b/；verification/；report/evidence/S4-CTRL/；.codex/STATE.md` | 未提交改动归属=`task-26 检查器和 r03-r10 证据已提交于 29b7c231；原有 .codex/STATE.md 用户差异及 12 个 ELF/MAP 未提交、未改动` | 让出声明=`独立 Reviewer PASS；task-26 G0 BLOCKED/exit 2；Codex 已停止 w4 写入并 OFFERED 给 DSH 项目总控；未启动硬件、Vivado、JTAG、COM4 或板测；阶段3与硬件仍归 DSH` | 心跳(UTC+8)=`2026-10-26 19:40` | 证据入口=`report/evidence/S4-CTRL/s4t26_g0_inputs_20261026_r10/manifest.json` | 恢复命令=`git -C D:/codex-worktrees/w4 rev-parse HEAD; git -C D:/codex-worktrees/w4 status --short` | 状态/下一接手方=`OFFERED / DSH 项目总控（待 DSH claim）`


更新：2026-10-25 05:31（UTC+8）。工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`。规则见 `D:\FPGA_Competition\AGENTS.md`。
**写权：依 `DSH-20261024-006` 正式 OFFER 与 Wong 授权，由 Codex 项目总控接续。task-26 桥接脚本及 r07 包已提交于当前基线 `06c9ab8`；其独立只读复审 PASS（仅代码/证据一致性），真实推理仍 BLOCKED/exit 2。task-21 registry 修复经 R4-03 独立复审 PASS，现已完成总控复核并提交；无硬件/Vivado操作。**

## 当前增量（BGR888 契约 r06，2026-10-25 22:55 UTC+8）

- 当前基线 `2c1dcd6e81efdfd9d4ed6f70b5d1af9016b985de`；契约升为 `s4-shared-io/1.2.0 r06`，**`DRAFT_PENDING_REVIEW`**。共享 `pixel_format` 为名称字符串，支持规格值 `BGR888`；像素通道序 `[B,G,R]` 与平台 `byte_order=little` 分开。D2 离线 Python 参考只做一次逐像素 BGR→RGB，再 resize/归一化/量化。
- **真实 C/PL 运行期仍 `NOT_IMPLEMENTED`**：缺 mailbox PS driver；`s4b_preproc_frame` 未接入实际 RTL top，且当前独立模块未实现 BGR 通道重排。C enum 的 `1=RGB565` 与候选 wire `mailbox_pixel_format_code=1` 仅属不同命名空间，候选映射未冻结，禁止直接 cast。RAW 系统 G0 保持 `CHANGES_REQUIRED_NOT_CLOSED`，地址区非冻结、`ENABLE=0`。
- 唯一证据包 `report/evidence/S4-CTRL/s4_bgr888_contract_20261025_r01/` 绑定 16 个源码路径。定向结果：契约 27/27、upstream 17/17、r06 负例 10/10、G0 依据 17/17 + 离线复算 13/13 + gap 状态 3/3、registry 10/10、地址/词汇 11/11、BGR 映射 2/2；整组注入 11/12，唯一 integration case 因沙箱拒绝创建固定工作树临时目录而未执行成功，不算通过。JSON/占位扫描/CRLF-aware diff check 均通过。
- 当前增量已完成独立复审 PASS：首轮发现历史清单版本误标后，生成器已改为既有清单不可覆盖；r02 清单固定 SHA 核验通过，构建器重跑 exit 0 并保留四份旧清单字节。复审结果及重跑摘要见 `report/evidence/S4-CTRL/s4_t21_manifest_immutability_20261025_r01/`。本轮源码/STATE 及两个新证据 RunId 待精确核对后提交；旧 12 项 ELF/MAP 未跟踪产物未动。仍未闭合：校准样本独立 heads 与 `cv2` 运行环境、RAW G0、真实 PS/PL 集成、帧周期 P、板级窗口和 G5。

## 当前离线修复（task-21，2026-10-25）

- 新 RunId `report/evidence/S4-CTRL/t21_address_binding_fix_20261025_r01/` 修复阶段3重复来源哈希及阶段5两个帧缓冲区的十进制/十六进制矛盾；权威值分别为 `d5ba4b6b…`、`0x00114C00=1133568`、`0x00F95400=16339968`。
- 主入口回归 8/8、registry 12/12 + 11/11依据、delivery evidence `CHECKS_OK`；独立审查 R4-03 `PASS` 仅关闭这两项重复事实缺陷。
- 旧 `bound_trees.json` 当前仍 `FAIL_STABLE_DRIFT`、1/5 匹配；未重绑。RAW系统G0、区域冻结、P实测、板级4-D与G5仍未完成；`ENABLE=0`、未 FROZEN。

## 当前接续增量（task-26，2026-10-24）

- 基线提交 `1046cdc9eedefd903e6b96e0190f4897c6a371db`，分支 `stage4-infer-prep`；主输入契约、地址图和 RAW G0 状态不变，仍 `ENABLE=0`、未 FROZEN，未访问板卡。
- 回放桥 `scripts/stage4_s4ctrl/replay_forward_bridge.py` 增加 heads 捕获、D9 解码入口、量化输入字节扰动检查及两 PNG `IMREAD_UNCHANGED` 像素比较；代码和 r07 证据经独立复审 PASS。该结论不代表真实推理验证通过。
- 当前证据 `report/evidence/S4-CTRL/s4t26_forward_bridge_20261024_r07/`：清单/源码快照哈希一致；状态 `BLOCKED`、退出码 2；冻结校准样本推理、raw heads 对拍、D9/NMS、负向对照及 PNG 像素检查均 `NOT_RUN`。
- 阻塞输入：可导入 `cv2` 的既有解释器；绑定到指定冻结校准样本路径与 SHA 的独立 raw head13/head26 黄金及对应冻结参数来源 SHA。不得安装依赖或以合成烟测冒充网络推理。r01–r06 历史 RunId 全部保留。
- 阶段4仍未冻结：RAW 系统 G0、P 实测、硬件集成及 G5 均未完成；板级窗口按 `CDX-20261023-019` 暂缓，需另行正式 OFFER。

## 当前接续增量（2026-10-24）

- 基线 `ced5bdef5c6f2d623237908ddb74baa4d6fa2bdb`，无 `index.lock`；原有 13 项未跟踪（12 ELF/map + 未完成 `replay_forward_bridge.py`）均保留原位、未修改、不入本轮提交。以下 task-21 内容为历史事实，当前接续以本节为准。
- B-r03-1：`verify_shared_io_contract.py` r07 按 `byte_basis` 单次取得 raw bytes，同一字节同时用于 SHA 与 S4-A/阶段5 JSON 语义解析；固定 blob 不可读、缺修订、未知口径或 SHA 不符均不得回退磁盘。
- 新证据 `report/evidence/S4-CTRL/s4_codex_binding_fix_20261024_r01/`：定向回归 9/9、真实契约自检 26 PASS/0 FAIL（15/15 绑定）、消费方回归 10/10，exit 均0；初始测试夹具错误保留摘要。固定100/磁盘200/契约200现被拒绝，固定200/磁盘100按固定200通过。
- 旧 `bound_trees.json` 的审查有效窗口已失效：w4/main 的 MOVING 与 dbdf/w5 的 STABLE 均已出现 HEAD 漂移。本轮只证明工具字节绑定修复与当前声明文件哈希；未重发跨树有效窗口、未把当前哈希复核升级为系统 G0。旧完整 T 标签报告未找到，不补造映射。
- 接口、地址与109/109覆盖不变；`ENABLE=0`、未 FROZEN、RAW系统G0未闭合；硬件、P实测、4-D/G5仍未完成。以上为 task-21 收尾时的计划快照；task-26 当前状态见本文件上方。

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

- 契约 r04、RAW 缺口登记表与 P 方案已经在**被审提交 `7a9507a`** 上通过独立复审 **`PASS`**（阻断 0／非阻断 4）：契约 r04 可作为阶段4 **当前基线**（冻结时必须显式引用 `r04` + 被审 SHA）；G-01 被独立确认为**设计级阻断**（窗口内最大连续可用区 9,825,540 B < 最大帧 11,059,200 B，缺口 **1,233,660 B** ⇒ 批准不足以解决，须 Wong 决定）。
- **流程纠正（下一轮起严格执行）**：① 交审前先声明**固定基线**并**停写被审对象**；审查期间只允许改**审查范围之外**的文件且必须**先报 lead**；② 冻结/引用基线必须写明**提交号 + 被审 SHA**，不得写“最新”；③ 若须在审查期间改动同范围 ⇒ **对新基线另行复审**，不得沿用旧结论。（本次成因是排程重叠，已在 lead 侧记录。）
- RAW 系统 G0 当前缺口：G-01/G-02 均为 `PARTIALLY_CLOSED_OFFLINE`（D1=A 已批准并登记；仍待固定版本独立 G0 复审，region 非 FROZEN、`ENABLE=0` 且不得访问候选区）；D2 整帧/padding 数值（G-04）、HP0 串行 owner 与排空（G-05）、平台 BD/XSA（G-07）、PS RAW task 与旧 memcpy 冲突（G-08）、协议项（G-09/G-10/G-11/G-13）、资源与布线后时序（G-14）、mailbox ABI 审查（G-15）。
- 硬件相关**全部 `NOT_RUN`**：八类门禁与正式 OFFER/CLAIM（G-16）、4-D 验收（G-17）、真实彩色回归（G-18）、帧周期 P（G-19）。
- 4-D 与阶段4 G5 未完成；不得把离线/回放结论升级为实物集成结论。
- **G-01/G-02 已按 Wong D1=A 一次性落盘（全离线）**：Wong 2026-10-24 批准选项 A、**不接受降覆盖**（D2 作废），记录 `decisions/stage4_raw_address_optionA_20261024_r01.md`（承接 DSH 初裁 `stage4_raw_address_d1_d4_20261024_r01.md`）。落盘内容：地址图 **r03** 新增 `raw_frame=[0x12000000,0x12C00000)`（12 MiB）+ `raw_meta=[0x12C00000,0x12C08000)`（32 KiB），把**本阶段自设**禁区条目精确缩减为 `[0x12C08000,0x20000000)`（其余禁区不动）；两 region 状态 `PROPOSED_STAGE4_OWNED_PENDING_APPROVAL_AND_REVIEW`（**非 FROZEN**、`enable_required=true`），登记 owner/access/cache 维护方向/完成序/容量；契约 **r05** 同版本重绑 + 消费方（阶段5/6）重绑清单。地址图与契约 `status` 仍 **`DRAFT_PENDING_REVIEW`**。
- **条件①三方交叉核对已闭环**：`report/evidence/S4-CTRL/t21_raw_address_crosscheck_20261024_r05/`（exit 0）⇒ **2B**（冻结件自证：候选起点即其专属窗口末端）、**阶段5**（送显三缓冲 `0x00114C00/0x00703800/0x00CF2400`，上界 `0x00F95400`）、**阶段3**（书面事实 `0x00110C00`、单缓冲、采集=显示共用）**均不相交**；`condition_1_status=SATISFIED_BY_BOUND_FACTS`。**保留条款已写入地址图 notes**：阶段3 帧基址为运行期分配、无链接期静态保证，消费方须运行期回读、禁止硬编码。
- **复审非阻断 N-1..N-4 已同批处理**：N-1 新增顶层 `binding_byte_basis`（默认磁盘字节；**跨树引用按已提交 blob 口径**，dbdf 两项与 w5 G0 字段改绑 blob + 磁盘注记；实测发现 w5 工作树在编辑中、dbdf 已推进 HEAD `0ad2000c`）；N-2 G-01 补写“设计级阻断（窗口内缺口 1,233,660 B）、已由 Wong 批准 A”并写准 `next_owner`；N-3 三处 `--evidence-dir` 已用新 RunId 重跑（`t21_contract_optionA_20261024_r02`、`t21_raw_g0_gap_registry_20261024_r05`、`t21_frame_period_p_plan_20261024_r03`）；N-4 `readiness_doc.sha_note` 更正为「属 S4-B 冻结快照证据、可从 `f6fa9f0` 复原」。
- **本批自检结果（新 RunId）**：契约自检 **26 PASS/0 FAIL**、缺口复算 **11/11 + 状态纪律**、P 校验 **6/6 负向对照**、交叉核对 **条件① SATISFIED**、契约消费方回归 **10/10 OK**，全部 **exit 0**；批次清单 `report/evidence/S4-CTRL/t21_optionA_landing_20261024_r01/landing_manifest.json`。
- **复审结论 `CHANGES_REQUIRED`（针对 `d29ef5f`，3 阻断 + 4 非阻断）与修复**：B-1 `stage5_display_g0_fields` 重绑 w5 已提交 blob `10d24a39…`（`8eac7007…` 经 `replaces` 记为修 r02 前修订），并标注**待阶段5 r02 复审结论、未冻结**；B-2 `stage3_window_address_facts` **三处**（契约/registry/地址图 factsources）统一补 `byte_basis=git_blob_content` 并重绑 dbdf 新 HEAD `6fa77a64` 的 blob `d5ba4b6b…`（原磁盘值 `19f754d8…` 失效；缺口复算脚本同步支持按声明口径复算）；B-3 新增 `scripts/stage4_s4ctrl/check_bound_tree_heads.py` + `bound_trees.json`，**fail-closed 断言**（任一被绑树实际 HEAD ≠ 记录值即 FAIL），实测 **5/5 一致 exit 0**；N-a 更正 dbdf `.gitattributes` 事实（确有 `report/evidence/S3-T05/** -text`，2026-10-01 起；差额成因＝`-text` 生效前入库 + 索引 stat 缓存）；N-b `overlap_proof` 文字统一为「全部顶层 region 逐对 28 对（含跨空间）；ddr 内 21 对」；N-c `ps_app_arena` 加「2B 应用视角」注（与阶段3/5 低 DDR 事实区间重叠属既有事实，与候选区无关）；N-d `capacity.frame_coverage` 改为「逐帧复用同一 region（单帧独占，非并发容量）」。
- **修复过程由 fail-closed 流程捕获 2 个真实缺陷**：① 日志变量名冲突致首轮 tmp 日志缺失（检查器已运行、result JSON 有效）；② 契约内 `stage4_address_map` 绑定漏改（自检 25/1 FAIL、口径复测 exit 1）⇒ 修正后全绿。中间批次 RunId 保留不覆盖。
- **复审修复批次清单**：`report/evidence/S4-CTRL/t21_optionA_landing_20261024_r02/landing_manifest.json`（含 `bound_trees.json` 与漂移断言结果）。
- **005 回执状态**：`dsh_mailbox/DSH-20261024-005-2b-address-confirm-raw-region.md` 已发出；`codex_mailbox/` 截至本轮无 `CDX-20261024-*` 回执（2B 部分已由其冻结件自证，回执用于留档）。
- **等待中 / 下一步**：**独立复审（固定提交 + 被审 SHA）通过前 region 不得标 FROZEN**；硬件窗口实测（CPU1 保持停止、无其他 DDR consumer、板上未占用、cache 可见性）完成前 **`ENABLE=0`、不访问候选区、不装载位流**；阶段4 板级窗口仍依 `CDX-20261023-019` 暂缓，需 lead 签 OFFER。
- **待排期改进项**：`handoff_check.py` 祖先/successor 语义（须连同 38 个单测与证据包一起改并重审）——本轮不展开。

## 必须保持的接口与边界（承接）

- 2B 正式冻结 `07c3d3958578b9cc9d3b8eae3758711fe08724c2`：1000 连续任务、108 ACK 闭环样本；109 黄金 ≠ 109 ACK 闭环。
- UART 方案 B：`s2bu/1.1` 正文不变、扩展关闭；时间/丢帧/过期/状态只记 PS 侧（`(session_id, frame_id, result_seq)` 唯一映射）。
- 候选上限 12675 可行、12676 硬错误；4096 禁用；注入须位于被验收预处理前；`capture_time_available=false`、`capture_time_ns=0` 哨兵，`injection_start_ns` 不得冒充采集时间。
- 保护旧已冻结离线链与全部旧 RunId：`s4_ps_decode.*`、`s4_uart_protocol.*`、`s4_offline_host.c`、`run_s4b_offline_chain.py`、`build_s4b_manifest.py`、`test_s4_ps_decode.py`；不得改写 `d4f30e3`/`d13610d` 的历史提交与证据。
- 2B/阶段3/阶段5/阶段6 工作树与厂商原件只读；本树一次只跑一个重型任务；不 push。
- **换行/字节口径前提（2026-10-24 更正）**：本树**存在 `.gitattributes`**（根 + 嵌套 `docs/stage4/`、`report/evidence/`、`scripts/stage4_s4ctrl/`、`scripts/stage4_s4b/`、`verification/`），其 `-text` **覆盖** w4 的 `docs/stage4/**` 与 `report/evidence/**`（`check-attr text: unset`），故这些文件 disk==blob；**未覆盖**跨树引用（dbdf `report/evidence/S3-T05/**` 为 `text: unspecified` ⇒ 我此前“本树无 .gitattributes”的陈述**有误，以本条为准**）。**不再新增覆盖**（lead 决定，与阶段3 同口径）；契约将新增顶层**绑定字节口径声明**（记录工作树磁盘字节 SHA；跨换行环境复算须 `-c core.autocrlf=false` 或用 blob 口径），并按 N-1 把 dbdf 两项改绑为 blob 内容口径。

## 当前交接行（11 字段，2026-10-25 22:55 UTC+8）

任务=`BGR888 输入契约 r06 修订与 fail-closed 证据` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`2c1dcd6e81efdfd9d4ed6f70b5d1af9016b985de` | 允许修改范围=`docs/stage4/ 契约/registry/readiness/地址/计划、scripts/stage4_s4b/、scripts/stage4_s4ctrl/、verification/ 两项定向测试、report/evidence/S4-CTRL/s4_bgr888_contract_20261025_r01/**、report/evidence/S4-CTRL/s4_t21_manifest_immutability_20261025_r01/**、.codex/STATE.md` | 未提交改动归属=`本轮 17 个 tracked 文件（含 .codex/STATE.md）与两个新 RunId evidence 归当前 Codex，尚未提交；旧 12 项 ELF/MAP 未跟踪文件未动` | 让出声明=`Developer 已停写；runtime 路径只读审计结束；独立 Reviewer PASS（S4-20261025 历史清单不可变修复）；未操作硬件` | 心跳(UTC+8)=`2026-10-25 22:55` | 证据入口=`report/evidence/S4-CTRL/s4_bgr888_contract_20261025_r01/delivery_manifest.json；report/evidence/S4-CTRL/s4_t21_manifest_immutability_20261025_r01/verification_summary.json` | 恢复命令=`git -C D:/codex-worktrees/w4 rev-parse HEAD; git -C D:/codex-worktrees/w4 status --short` | 状态/下一接手方=`IN_PROGRESS（r06 独立复审 PASS，runtime NOT_IMPLEMENTED，RAW G0 CHANGES_REQUIRED_NOT_CLOSED；注入集成用例 11/12 且剩余用例为 sandbox BLOCKED）/ 下一步=证据与差异最终核验并精确提交；随后阶段5消费侧改绑`

## 历史交接行（task-21，2026-10-25 05:31 UTC+8）

任务=`task-21 RAW registry 重复事实修复（R4-03 PASS；跨树窗口仍失效）` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`06c9ab83e4215b6ea5ec9fd827b59549e425a285` | 允许修改范围=`docs/stage4/S4B_raw_system_g0_gap_registry.json、scripts/stage4_s4b/audit_raw_system_g0_gaps.py、verification/test_s4_raw_g0_registry.py、report/evidence/S4-CTRL/t21_address_binding_fix_20261025_r01/**、.codex/STATE.md` | 未提交改动归属=`本轮 registry/checker/test、修复 RunId 与 STATE 已提交；原有12项 ELF/MAP 保留不动、不入提交` | 让出声明=`Developer 已停写；Reviewer R4-03 PASS；无硬件/Vivado操作` | 心跳(UTC+8)=`2026-10-25 05:31` | 证据入口=`report/evidence/S4-CTRL/t21_address_binding_fix_20261025_r01/delivery_manifest.json` | 恢复命令=`git -C D:/codex-worktrees/w4 log -1 --oneline; git -C D:/codex-worktrees/w4 status --short` | 状态/下一接手方=`IN_PROGRESS（两项P2已关闭；旧跨树窗口FAIL_STABLE_DRIFT 1/5，RAW系统G0/P/4-D/G5仍未过）/ 下一步=等待输入版本稳定后重新建审查窗口；继续task-26离线前置，推理依赖仍BLOCKED`

## 历史交接行（已被上行取代，不再代表写权）

任务=`task-21 阶段4 接续（DSH 认领 w4）：契约改绑真实彩色 + 应用已批准项 + RAW 系统 G0 收口 + 帧周期 P 方案（全离线）` | 负责人=`DSH 阶段4 总控（stage4-lead）` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`f6fa9f0d84274f1a0d03e6f87263fb550ebc6656` | 允许修改范围=`docs/stage4/、scripts/stage4_s4ctrl/、scripts/stage4_s4b/、verification/、report/evidence/S4-CTRL/、.codex/STATE.md`（主目录与其他树、硬件均无授权） | 未提交改动归属=`12 项未跟踪 6 ELF/6 map 属 Codex 本机恢复产物，留原位不入 Git；本轮新文件随本次提交` | 让出声明=`w4 由 DSH 阶段4 总控持有至本轮收尾；硬件使用权未随交接，阶段4 板级依 CDX-20261023-019 暂缓，恢复须另行申请窗口` | 心跳(UTC+8)=`2026-10-24 01:00` | 证据入口=`report/evidence/S4-CTRL/t21_takeover_20261024_r02/、t21_contract_colour_rebind_20261024_r02/、t21_raw_g0_gap_registry_20261024_r03/、t21_frame_period_p_plan_20261024_r01/` | 恢复命令=`git -C D:/codex-worktrees/w4 log --oneline -3; git -C D:/codex-worktrees/w4 status --short; python -B D:/codex-worktrees/w4/scripts/stage4_s4ctrl/verify_shared_io_contract.py` | 状态/下一接手方=`IN_PROGRESS / 本轮收尾后由 DSH 项目总控指派独立复审与后续（含硬件窗口申请）`
