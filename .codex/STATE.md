# 阶段3 状态（AN5642 原始视频链路）

**2026-10-24 Codex 接续**：依据主目录 `DSH-20261024-006-handover-main-write-right-to-codex.md` 正式 OFFERED，总控已接管；本树原 DSH 独占写声明自该交接后失效。本轮阶段3 Developer 已停写；r02 G2 修订材料经独立复审 `PASS`（仅关闭上一轮四项整改），起点 `1d54894be4d547955034eeff8bce853dd4286fac`，未操作硬件。
**本轮替代阅读入口**：`report/evidence/S3-T05/t05_g2_reconciliation_20261024_r01/README.md` —— 修订上轮 G2 `CHANGES_REQUIRED`：保留旧窗口前材料；纠正当前写权/审查状态、task-11 静态 PASS 与顺序 `NOT_RUN`、跨树内容绑定和 VDMA 拆位。r02 修订审查已 `PASS`；阶段3 G5 仍未通过。旧 RunId 及历史 DSH 作者/运行事实不改写。README/清单中的 `PENDING_REVIEW` 是生成时快照，审查结果见本 STATE。

更新：2026-10-24 00:33（离线前置）→ **01:28 板级窗口收窗**（提交 `0ad2000`）→ **01:41 Wong 真彩目视「画面可以接受，正常颜色」** → **02:1x DSH 离线收尾材料**（历史提交）→ **19:43 Codex G2 材料修订** → **2026-10-25 05:33 SOF 局部转移复核**。工作树 `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`。按 DSH-20261024-006 正式交接，当前树负责人为 Codex 项目总控；本轮 Developer 已停写、R3-03 对局部证明独立复审 PASS；其他窗口只读。
*更正：本文件此前两处曾写「01:05/01:12」，那是估计值；实际离线前置提交时刻为 `00:30:35`/`00:33:57`/`00:34:32`，已按 git 实际时刻更正（避免再出现"声明时刻与证据不符"）。*
**2026-10-24 Wong 三问三答：「1.可开工」「2.现在用的是 J11，J10 不需要管了」「3.由 DSH 接手」(w4)** ⇒ 阶段3 板级**单次窗口**已据此执行完毕（授权文件 `report/evidence/S3-T17/hw_authorization.json`，引用决策记录 `decisions/stage_3_4_direction_20261024_r01.md`、`DSH-20261024-004`、Codex `CDX-20261023-018` §3.1 不争用）；**J10 已移出未闭合项、记为「范围排除」**。
**当前口径（顶部）**：颜色子项 = **`PASS_VERIFIED_NEW_MODULE`**（新模块实测解除受阻）；**当前部署 = 无补偿实时彩色**；**阶段3 整体 G5 未通过**（阶段A 小任务 G5 ≠ 阶段3 G5）；`DEFERRED_PENDING_MODULE` 仅为旧模块期历史标签。
**2026-10-25 20:08 W1 更新**：Wong 已授权 30 分钟只读窗口（不重启应用、不写寄存器、不烧录、不改线）；RunId `report/evidence/S3-T17/t17_w1_readonly_20261025_r01/`。窗口前置重查四树均无 `index.lock`，无 `hw_server/xsdb/vivado/vitis`、无 3121 监听；主机未枚举 COM/USB/JTAG 设备，且内存查询被拒绝，故窗口 `BLOCKED_BEFORE_WINDOW`、实际时长 0、未创建硬件会话或操作板卡。待主机枚举设备后重新执行窗口前置核对；本项不关闭 VDMA 根因或阶段3 G5。
**2026-10-25 20:17 W1 复查**：Wong 补充 `COM4`；.NET 与注册表确认串口名存在，但 PnP/CIM 无端口结果且未发现 JTAG 设备。Vivado MCP 无活动会话，自动审批拒绝仅为探测 JTAG 而启动 Vivado；未绕过、未开窗、未操作板卡。Wong 选择先让 JTAG 在 Windows 枚举；复查记录 `report/evidence/S3-T17/t17_w1_readonly_20261025_r02/`，该条件满足前不重试。
**2026-10-25 20:24 G2 状态**：阶段3完整 G2（原 r02 + 新 VDMA 时序勘误）经独立 Reviewer `PASS`，复核基线 `78f2bde`。已分开绑定应用 UART `phase=0=0x00014810`、`t=5s=0x00015810`、独立只读探测与 W1C 值；旧 r02 字节保留。该 PASS 仅关闭完整 G2 证据审查，不关闭 VDMA 根因、G3/G4/G5；VDMA 仍 `PARTIAL`、根因 `OPEN`，阶段3 G5 未通过。
**2026-10-26 W1 更新**：Windows 只读枚举发现 FTDI `USB\VID_0403&PID_6014\210512180081` 与 COM4；保留的 r03 XSDB 记录确认 Digilent JTAG-HS1、`arm_dap`、`xc7z020` IDCODE `0x23727093`，但首个 `mrd 0x43010030` 超时。新 RunId `report/evidence/S3-T17/t17_w1_readonly_20261026_r01/` 用 XSDB `state` 门禁后确认 A9 从 Running 变 Stopped，再读 `S2MM_SR` `0x43010034` 仍超时；脚本因此未读运行期地址，读取错误后 state 不再被判为 halted，未执行 `con`，未写寄存器/复位/烧录。XSDB wrapper exit 0、探测 exit 2；随后确认无 `xsdb/hw_server` 进程或 3121 监听。最终 A9 状态未由本次证据明确确认；部署身份、当前真彩目视、VDMA 状态与运行期地址均未完成，W1 收窗，失败证据保留且不重跑旧 RunId。板卡 JTAG 已枚举，但本结果不关闭 VDMA 根因或阶段3 G3/G4/G5。

**2026-10-26 APU/W1 恢复更新**：APU 读回及恢复 R01、修正门禁后的 R02-R04 均因 DAP APB `0x30000021` 无 A9 target；R01 旧脚本接受 `Stopped: (Suspended)` 的程序偏差已记录，R02-R04 新脚本经独立审查，仅严格 `Stopped` 才执行一次 `con`，但三轮均未查询状态或执行 `con`。无寄存器操作/停机/复位/烧录；最终收窗无硬件进程、3121 监听或 Vivado MCP 会话。A9/HDMI 未恢复或确认；不得再重用这些 RunId，阶段3 G5 仍未通过。证据：`report/evidence/S3-T17/t17_w1_apu_readonly_20261026_r01/`、`report/evidence/S3-T17/t17_w1_recover_a9_20261026_r01/`、`..._r02/`、`..._r03/`、`..._r04/`。

## 当前彩色部署（唯一口径；每次硬件使用前重新核对现场与产物）
- 位流 **无补偿 SOF `7cb33068…`**（1,668,969 B）；XSA **`1f5b138e…`**（633,089 B）；应用 **`an5642_j11cmos2_v10_read.elf` `1457cda4…`**（015 §2.2 身份；本轮已实算复核一致）。
- 构建来源 `e9b853f`（本分支）、`xc7z020clg400-2`、Vivado 2026.1；约束 `an5642_j11_cmos2.xdc` `2dae928c…`；补丁 `alinx_ov5640_sof_hrefgap.patch` `fd854a62…`（GAP_THRESH=16384；HTS=1892/VTS=740 ⇒ 612<16384<38452）；WNS **1.054525** / WHS 0.058931 / TNS=THS=0；DRC 0 error、8 warning、0 critical。
- 传感器与格式：CMOS2（J11）CHIPID `0x5640`（TRY0/1/2 均应答；旧模块仅 TRY0）、1280×720、PCLK≈84 MHz；DDR 内存序 **B,G,R**、每行 3840 B、行地址 = `FRAME0 + y×stride`（**运行期回读**，禁硬编码）。
- 颜色证据：`report/evidence/S3-T05/t05_new_module_reverify_20261023_r01/`（提交 `b98ce73`）—— 缺位签名**消失**（蓝 bit7 21.719–39.141%、绿 bit4 38.047–50.156%；旧模块 `0.000%/0.000%`）、彩条 8 条满量程且色相顺序正确（白 `B5=31`、绿 `G6=63`；旧模块 15/59）、实景 `B/R≈0.85–0.99`（旧模块 0.45）；**本轮独立实算该证据 `hashes.txt` 6/6 一致**。
- 彩条工具纪律（015 §2.4）：v12 **会写传感器寄存器**，只在明确授权 + 独占窗口按**既定彩条用例**使用；用前保存原值、写后读回、结束**恢复 `0x503D=0x00`** 并留恢复后实时流证据；**不得当通用重置工具**（复测轮已按此执行）。
- G2 当前材料：`report/evidence/S3-T05/t05_g2_reconciliation_20261024_r01/g2_material_list_r02.json`（对上轮 `CHANGES_REQUIRED` 做修订；r02 独立复审 `PASS`，见本 STATE）；旧 `t05_closeout_prep_20261024_r01/g2_material_list.json` 保留原字节，仅作窗口前历史材料。

## 真实未关闭项（015 r03 §2.4；颜色项通过不替其余项关闭）
*已完成（不再列为未关闭）*：**颜色项**（`PASS_VERIFIED_NEW_MODULE`）、**≥30 分钟实时耐久**、**参考帧集**、**阶段3 地址事实**、**真彩目视（人工观察，2026-10-24 01:41）**。
*未关闭（本清单为准）*：① **VDMA 粘滞 `0x00015810`（PARTIAL，根因未定）**；② **TIMING-17/36 与 I/O delay**（C2/I1/I2/I3 未闭合/未验证）；③ **无 ILA（BASIC 许可）**；④ **task-11 完整顺序等价 `NOT_RUN`**（静态阈值译码及下述局部转移检查已 PASS）。
- **完整独立 G2**：原 r02 加 `report/evidence/S3-T05/t05_g2_vdma_timing_erratum_20261025_r01/` 经独立 Reviewer `PASS`（基线 `78f2bde`）；修正 r02 对 phase=0 与 t=5s VDMA 值的合并误标。早期 stdluma/gray 补丁仅人工审阅、未独立 PASS（若重新启用须复审）。G2 PASS 不代表实物 G3 或阶段 G5 通过。
- **≥30 分钟实时耐久**：**已达成（2026-10-24 窗口，RunId `t05_stage3_window_20261024_r01`）** —— `00:49:16 → 01:20:31`（**31 min 15 s**），7 轮活写标记全部 **5/5**、`CR=0x00010003`、`MM2S_SR=0x00011000`、无停止/复位/死锁；UART 连续 35 min（三路 CHIPID `0x5640`、`0x503D=0x00`、5 次采样 × 3 站点指纹全异）。**限机读连续性；目视确认已由 Wong 于 01:41 给出（见上）。**
- **VDMA 粘滞 `0x00015810`**：**PARTIAL（不关闭）** —— 既有窗口中一次性 W1C 清除后 `0x00015810 → 0x00011000`，31 min 15 s / 7 轮稳态回读未复现、无功能影响；新离线补充发现首次 `phase=0` 已为 `0x00014810`，bit11 已置位，到 `t=5` 的 `0x00015810` 仅新增 bit12。已提交元数据将 bit11 命名为 `SOFLateErr`，HDL 摘录为 `s2mm_fsize_more_or_sof_late_bit`；AMD PG020 将 bit11 定义为 `SOFLateErr`（S2MM 帧长超过 VSIZE），但现有采样仍未定位具体置位时刻/触发分支，根因保持未定，不得称“零错误”。参考：[PG020 S2MM VDMASR](https://docs.amd.com/r/en-US/pg020_axi_vdma/S2MM_VDMASR-S2MM-VDMA-Status-Register-Offset-34h)。材料：`report/evidence/S3-T05/t05_stage3_window_20261024_r01/vdma_sticky_result.md`、`report/evidence/S3-T05/t05_offline_closeout_20261024_r01/vdma_fsz_more_analysis.md`、`report/evidence/S3-T05/t05_vdma_root_cause_offline_20261025_r01/`。
- **参考帧集（供阶段4 回放）**：**已采集** —— v11 冻结后按**其自报 FB `0x00114C00`** 转储：整帧 2,764,800 B（sha256 `939fce22…`）+ 3 行样本（各 3,840 B），0 全零行、B/G/R 均值 94.1/86.2/93.5、max 248/252/248；格式/字节序/stride/坐标口径见 `…/reference_frame_set.md`。
- **阶段3 地址事实（供阶段4 选址对照）**：**采集与显示共用同一帧缓冲**（实测 `S2MM@0x430100AC = MM2S@0x4300005C = 0x00110C00`，单缓冲 `stride=0x0F00`、`0x2A3000` 字节）；**全部观测地址 < `0x10000000`** ⇒ 与阶段4 候选区 `[0x12000000,0x12C08000)` **不相交**（注意：地址由应用运行期分配，非链接期静态保证）。详见 `…/address_facts.md`。
- **TIMING-17/36 与 I/O delay**：**适用报告已出（离线，基于本版既有报告）** —— `report/evidence/S3-T05/t05_dcp_readonly_20261024_r01/v3_timing_summary.rpt`、`v3_methodology.rpt`：`WNS 1.055/TNS 0/0 of 21479`、`WHS 0.059/THS 0/0 of 21344`、DRC 0E/8W/0C；TIMING-17=240、TIMING-36=1、TIMING-18=1、`no_clock (240)`、`unconstrained_internal_endpoints (520)`、`no_input_delay (9)`、`no_output_delay (5)`。新增只读定位 `report/evidence/S3-T05/t05_timing36_source_probe_20261026_r02/`（独立复审 PASS）：`PixelClk` 接 10 ns `PXL_CLK_O` 网络，`SerialClk` 实际接 2 ns `PXL_CLK_5X_O` 网络；IP XDC 却把 `SerialClk` 作为由 `PixelClk ×5` 产生的时钟，导致 TIMING-36/30。此证实约束与集成后实际拓扑不匹配的诊断，**未修复**；下一步须在隔离实现约束集中更正/移除此约束并复报完整时钟与路径覆盖。`38-249` 归因已确认、非本项未闭合原因。**C2（`cmos1_pclk` 无 create_clock）+ I1/I2/I3（无 I/O delay）仍 OPEN**——依 Wong 2026-10-24 决定只备案为「已记录局限」（`decisions/stage3_io_delay_c2_limitation_20261024_r01.md`，sha256 `e66c44bb…`），不得称已通过/闭合，不冲抵 TIMING-17/36。新增资料核对 `report/stage3_ov5640_dvp_timing_audit_20261007.json`：OV5640 官方 datasheet 的 DVP 模式表没有 DVP data-to-PCLK 数值 min/max；独立 AX7020 双摄样例源码注释中的 PCLK `84 MHz` 未经当前板卡实测，官方资料也未证明其适用于或符合本设计的 1280×720 RGB565 模式，不能作为已证实频率或输入延迟约束值。板标 `AX701020.3.0` 尚未绑定到候选 PCB/路由延迟文件；HDMI sink 型号/接收时序预算也未入证据。**所需延迟输入未齐，不得编造数值**；保留 `CLOCK_DEDICATED_ROUTE FALSE [cmos1_pclk_IBUF]` 已知例外；DRC 0 error / 局部 WNS>0 不替代完整约束签核。
- **无 ILA**（BASIC 许可禁 `create_debug_core`）：以计数器/状态寄存器、cache 一致性取帧、受控转储、离线仿真补足；**不因此免除**功能/时序/耐久标准；本轮不改许可、不植入调试核。
- **真彩目视：已完成（2026-10-24 01:41，人工观察）** —— Wong 原话「**画面可以接受，正常颜色**」；记录 `report/evidence/CTRL-DSH-HANDOFF/decisions/stage3_human_visual_20261024_r01.md`（sha256 `3bed7f85…`）。**效力**：仅对**当前部署**（无补偿 SOF `7cb33068…` + `v10_read` `1457cda4…` + J11/CMOS2 + 现接线/显示链路）与**该时刻**有效；**位流、ELF、视频端口、接线或显示链路任一变更 ⇒ 本判定失效，须重新目视**。**性质**：人工观察证据，**不得**写成仪器测量或像素级对拍。
- task-11：**静态阈值译码已独立核验 PASS**（`task11_threshold_decode_20261024_r01/`；262,144 组 LUT4 输入、0 差异，`PASS_STATIC_THRESHOLD_DECODE`）；`task11_sof_local_transition_20261025_r01/` 经 R3-03 独立审查 `PASS`，对固定 19-bit 初态及相同 5-bit 边界输入穷举 16,777,216 组、335,544,320 位比较为 0 差异，并核对 30 拍轨迹。追加边界审计确认该证明假设五个 cut inputs 逐拍相等，未覆盖其生成/复位、18-bit FIFO 写 bundle、2048 深度双时钟 FIFO 状态及 CDC；当前本机未发现可用的完整多时钟 SEC 工具/许可。除非补齐覆盖五个边界、写数据/FIFO 状态、CDC 与 INIT/GSR 的独立分区等价证明，**完整 RTL↔网表顺序等价及 task-11 仍 `NOT_RUN`**。
- task-25 单帧回放输入绑定：`report/evidence/S3-T05/t05_replay_binding_20261025_r01/` 为标准清单包，检查器 `CHECKS_OK`。新增 sidecar 将参考帧说明中的秒级 UTC+8 墙钟记录转换成 Unix 纳秒表示，标记 `replay_documented_wallclock`/`replay_only`，不声称增加精度或实时性能。它只补齐可消费元数据，不代表阶段4/5契约 G0、推理/回放或阶段3 G5 通过；阶段4契约仍 `DRAFT_PENDING_REVIEW`，阶段5 UR-1 未决。
- **VDMA 粘滞离线补充**：`report/evidence/S3-T05/t05_vdma_root_cause_offline_20261025_r01/` 绑定首次/后续状态差分、bit11 的本地元数据与 HDL 组合来源，并收窄应用启动顺序观察范围；官方 AMD PG020 v6.3 在线页与本地 v6.3 元数据/HDL、v6.17 驱动交叉核对 bit11=`SOFLateErr`、bit12=`FrmCnt_Irq`、bits23:16=`IRQFrameCntSts`。`report/evidence/S3-T05/t05_vdma_bitfield_erratum_20261026_r01/` 勘误旧记录将 `0x1000` 笼统称为帧计数类状态位的表述（旧字节保留）；`0x14810→0x15810` 差值为 bit12。首帧触发分支仍未定位，**仍 PARTIAL/开放**。
- **本轮独立复审**：`PASS`，范围仅为该离线补充证据、13 个绑定文件哈希及 STATE 表述；不表示 VDMA 根因、G3、G5 通过。
- 未做电气测量、未烧 QSPI、未改接线；传感器寄存器改动均为易失。

## 范围排除（非未闭合项；依据 Wong 2026-10-24 决定）
- **J10「半屏黑」**：依据 Wong 2026-10-24「现在用的是 J11，J10 不需要管了」，**J10 不在本阶段部署与验收范围内**（当前部署 = J11/CMOS2，XDC `an5642_j11_cmos2.xdc` `2dae928c…`）。**这不表示 J10 故障已修复或已关闭**；J10 约束与官方 XDC 16/16 一致（非映射错），现象仍未定性。今后若正式需求要求 J10，须重新立项并完成适用审查/验证。依据记录：`report/evidence/CTRL-DSH-HANDOFF/decisions/stage_3_4_direction_20261024_r01.md` §1 第 2 项（sha256 `907084cd…`）。

## 历史（已更正，不作为当前口径；原证据与提交不回退）
- **灰度部署与"灰度微调"**：`44e609cc…`（标准亮度灰度）/`90e1bdee…`、纯绿 `2f72aaa4…`、补偿彩色 `30db09ba…` —— 仅**历史与回退**；灰度微调**不再是必经任务**（Wong 2026-10-22 决定 + 015 §2.2）。
- **旧模块期颜色结论**：「颜色仍受阻 / `DEFERRED_PENDING_MODULE`」「等待新摄像头到货」「颜色验收在硬件修复前 FAIL」—— 属**已更换旧故障件**的历史记录；根因（`cmos_d[9]` 无信号）与返修材料保留为历史证据：`t05_color_msb_missing_20261022_r01/`、`t05_freeze_20261021_r01/`。
- **「阶段三已收尾（灰度交付）」**：2026-10-22 灰度口径的历史决定；阶段3 **未冻结**（015 §2.3/§5）。旧「阶段B 未做」已按下节改写。

## task-17/18/19/20（阶段A 工具准备与三轮修复）——结论保留
- 触发与接管：Wong 2026-10-23 告知新模块到货；`handoff_check --claim` 真实 `HANDOFF_OK`（PASS 9、退出码 0，基线 `f94c25f`）。
- 产物：`scripts/stage3_t17/**`（一键执行器/判定器/离线前置/只读链路确认/参数化安全转储/打包器/自证）+ `report/evidence/S3-T17/{t17_color_retest_prep…, t17_fix…, t17_quickfix…, t17_closeout…, t17_guard_ok…}/`。
- 判定口径：位完整性 = 白条 `G8>=248`、`B8>=240`、旧签名不存在、黑条负样本；C7 = **16 字段位（R5+G6+B5）+ 8 结构性恒 0 低位**，与 C5 容差对齐（缺陷 14/16、修好 16/16；严格口径 13/16、15/16 仅对照）。
- 三轮修复要点：HEAD 判据改「声明基线或其后代」；C7/C5 容差对齐 + 夹具 D/E/F；位计数改 16/8；四工具入口强制 UTF-8+LF（GBK 下 `U+21D2` 崩溃 R-1/R-2 已修，**源码 0 处**）；`analyze --selftest` 两条 CLI 回归；`verify --selftest` 含「旧形态突变体」判别力证明；执行器 **cwd×WT 运行位置护栏**（cwd≠WT ⇒ **exit 2 且不写任何文件**；须在 dbdf 内运行或显式 `--wt`/`T17_WT`）。
- **阶段B 处置**：阶段B 计划步骤 1–4、6–8（离线前置、只读链路、无补偿基线 + 只读回读、安全转储 3 行、彩条写入与恢复、判定）**已由新模块复测覆盖并完成**；**剩余 = 真彩目视 + 板级项**（耐久/VDMA/TIMING/J10），已转入上面「真实未关闭项」，**不再作为"待模块到货"阻塞**；逐条对应见 `…/t05_closeout_prep_20261024_r01/README.md` §3。

## 器件与环境（现行事实）
- 器件 XC7Z020-2CLG400I，Vivado part `xc7z020clg400-2`；Vivado 2026.1 Tcl；JTAG 用 `xsdb.bat`；XSCT 禁用（软件侧 HSI+make）。
- BASIC 许可 `D:\Xilinx_licenses\basic_only.lic` 须按进程注入 `XILINXD_LICENSE_FILE`；BASIC **不支持** `create_debug_core` ⇒ 无 ILA 波形。
- 本机 16 GB：同一时刻只跑一个重型综合/实现/大型仿真；`TEMP/TMP=D:\tmp`；硬件会话跨方互斥，动手前先看进程。

## 已完成（可复现事实，精选）
- **HDMI 输出**：官方 `14_vdma_hdmi_out` 重建并实物启动成功；bit `7143427f…`、XSA `02174319…`；证据 `report/evidence/S3-T03/t03b_hdmi_build_20261020_r01/`。
- **采集直通 + 帧同步修复**：厂商 IP `s_axis_tuser` 改为「hblank 连续低 ≥16384 pclk 后首个有效像素」；实物实时直通成立（3×64 KB 指纹 15/15 互异）；证据 `…/t05_v6_board_20261020_r01/`、`…/t05_monitor_20261020_r01/`。
- **旧模块根因（历史）**：19 行样本 24,320 px 蓝 bit7/绿 bit4 置位率均 `0.000%` ⇒ 两个 DVP 字节 MSB 共线 `cmos_d[9]` 无信号；配置侧已排除（`0x301D/0x301E=0x00`、D 脚输出使能全开、寄存器非 init 表）；证据 `…/t05_msb_line_diagnosis_20261021_r01/`、`…/t05_v9_board_20261021_r01/`。
- **作废判断**：基于 halt 态 A9 `mwr/mrd` 的「冻结单帧 / 帧缓冲全 0 / 显示全黑」结论作废（经 CPU 数据 cache，不可作 DDR 内容证据）。

## 可复用命令与工具教训
- **执行器须在 dbdf 内运行**：`cd D:/codex-worktrees/dbdf && bash scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id <新RunId>`（cwd≠WT ⇒ exit 2）；自测 `python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --selftest`、`…/verify_t17_blob_identity.py --selftest`。
- 实板抓取/转储沿用已审脚本（`scripts/stage3_t05/run_t05_board_capture.sh`、`jtag_dump_display_channels.tcl`）；**重跑一律新 RunId**，地址/stride **运行期回读**。
- **禁止**对运行中 A9 直接 `mrd`（会打坏 DAP：恢复 = `targets -set *DAP*` → `rst -type system`，**会清 PL 配置**）；只读一律 `stop → mrd → con`；**禁止原样执行历史 `jtag_dump_rows3.tcl`**。规则见 `D:\FPGA_Competition\AGENTS.md`；总入口 `CDX-20261022-015`（r03）。

## 未提交改动归属（接手声明，不覆盖不回退）
- 未跟踪散落件：`NA/`、`clockInfo.txt`（旧轮、非本阶段产物，保留不动）；`tmp/**` 为构建缓存，不入提交。
- **历史归属（DSH 旧轮）**：STATE 统一、旧离线收尾准备、2026-10-24 板级窗口及离线收尾材料等改动，按当时交接记录归 DSH 阶段3 总控；不表示当前仍由 DSH 持有写权。DSH-20261024-006 后主目录由 DSH 持写、阶段3由 Codex 持写。本轮仅修改阶段3 task-11/STATE、阶段4 task-21/STATE、阶段6 R6-02/STATE；未改主目录、阶段5、w2b、厂商原件或业务工程，未触碰硬件。阶段3原有 NA/、clockInfo.txt 与阶段4/6历史未跟踪产物均保留未提交。

**2026-10-26 W1 证据汇总（截至 11:46 UTC+8）**：前段“本轮仅修改…”是此前阶段3/4/6离线工作的历史说明。W1 证据现包括 `t17_w1_readonly_20261026_r01/`、`t17_w1_apu_readonly_20261026_r01/`、恢复 R01 与恢复 R02-R04。只读 R01 暂停 A9 后读回超时；恢复 R01 无 A9 target，且旧脚本门禁比批准范围宽（无 `con`）；修正为只接受精确 `Stopped` 的 R02-R04 均无 A9 target，未查询状态或执行 `con`。所有证据保留；未引用旧 r03 与其他未跟踪文件维持原样。

**2026-10-26 TIMING-36 DCP 内存诊断 R01/R02**：新 RunId `report/evidence/S3-T05/t05_timing36_inmemory_constraint_probe_20261026_r01/` 与 `_r02/` 均保留失败证据并通过 delivery manifest 文件绑定检查。R01 精确引脚查询返回 0、退出码 1；R02 找到错误生成时钟（master `axi_dynclk_0_PXL_CLK_O`、2 ns）及串行端口自动时钟 `I`，但 Vivado 2026.1 无 `delete_clocks` 命令，故在修改前以退出码 4 安全停止。没有写回 DCP/XDC或跑实现；TIMING-36/30 未修复。阶段3 G5 仍未通过；Reviewer 复核待完成，后续应走新 RunId 的隔离 XDC 修正和 routed 实现路径，而非尝试单对象时钟删除。

## 交接行（11 字段，2026-10-26 12:33 UTC+8；阶段3 G5 未通过）
任务=`阶段3 G5 收尾；VDMA bit11 根因、task-11 完整等价、TIMING-17/36 与 I/O delay 均开放` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\dbdf`/`codex/stage3-video` | 起始提交=`4b1597d0a01f31df7d6bacdda39696d8b36bd7c8` | 允许修改范围=`阶段3 .codex/STATE.md 与各自新 RunId 证据；不改主目录或其他阶段；任何硬件动作须新窗口授权` | 未提交改动归属=`本轮范围仅为 TIMING-36 r01/r02 诊断证据及本 STATE；NA/、clockInfo.txt、jtag_t17_w1_sr_sample.tcl 原样保留且排除在提交外` | 让出声明=`W1 APU 恢复 R02-R04 均无 A9 target，未查询状态/未执行 con，硬件资源已收窗；bitfield 核验通过但首次 bit11 支路未定位；TIMING-36/30 拓扑失配已定位但未修复，TIMING-17 与 C2/I/O delay 仍开放；task-11 无完整多时钟 SEC 证明；不操作硬件，COM4 读采集授权仍待回复` | 心跳(UTC+8)=`2026-10-26 12:33` | 证据入口=`report/evidence/S3-T05/t05_timing36_source_probe_20261026_r02/delivery_manifest.json；report/evidence/S3-T05/t05_dcp_readonly_20261024_r01/v3_timing_summary.rpt；report/evidence/S3-T05/t05_vdma_bitfield_erratum_20261026_r01/delivery_manifest.json；report/evidence/S3-T17/t17_w1_recover_a9_20261026_r02/delivery_manifest.json；report/evidence/S3-T17/t17_w1_recover_a9_20261026_r03/delivery_manifest.json；report/evidence/S3-T17/t17_w1_recover_a9_20261026_r04/delivery_manifest.json` | 恢复命令=`在 D:\codex-worktrees\dbdf 执行 python -B D:\FPGA_Competition\verification\check_stage_delivery.py --mode evidence --project-root D:\codex-worktrees\dbdf --manifest report/evidence/S3-T05/t05_timing36_source_probe_20261026_r02/delivery_manifest.json` | 状态/下一接手方=`IN_PROGRESS（bitfield定义 PASS、bit11根因 BLOCKED；TIMING-17/36 与 C2/I/O delay OPEN；task-11 NOT_RUN；板级部署身份/HDMI/运行期地址未确认；G5未通过）/ 下一步=先完成已定位的隔离时钟约束诊断，再按授权窗口恢复板级证据，并补齐时序资料与等价工具证明`
