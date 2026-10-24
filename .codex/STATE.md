# 阶段3 状态（AN5642 原始视频链路）

**2026-10-24 Codex 接续**：依据主目录 `DSH-20261024-006-handover-main-write-right-to-codex.md` 正式 OFFERED，总控已接管；本树原 DSH 独占写声明自该交接后失效。本轮阶段3 Developer 已停写；r02 G2 修订材料经独立复审 `PASS`（仅关闭上一轮四项整改），起点 `1d54894be4d547955034eeff8bce853dd4286fac`，未操作硬件。
**本轮替代阅读入口**：`report/evidence/S3-T05/t05_g2_reconciliation_20261024_r01/README.md` —— 修订上轮 G2 `CHANGES_REQUIRED`：保留旧窗口前材料；纠正当前写权/审查状态、task-11 静态 PASS 与顺序 `NOT_RUN`、跨树内容绑定和 VDMA 拆位。r02 修订审查已 `PASS`；阶段3 G5 仍未通过。旧 RunId 及历史 DSH 作者/运行事实不改写。README/清单中的 `PENDING_REVIEW` 是生成时快照，审查结果见本 STATE。

更新：2026-10-24 00:33（离线前置）→ **01:28 板级窗口收窗**（提交 `0ad2000`）→ **01:41 Wong 真彩目视「画面可以接受，正常颜色」** → **02:1x DSH 离线收尾材料**（历史提交）→ **19:43 Codex G2 材料修订**。工作树 `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`。按 DSH-20261024-006 正式交接，当前树负责人为 Codex 项目总控；本轮唯一文件写入方为其授权的阶段3 Developer，该 Developer 已停写并将材料交总控复审；其他窗口只读。
*更正：本文件此前两处曾写「01:05/01:12」，那是估计值；实际离线前置提交时刻为 `00:30:35`/`00:33:57`/`00:34:32`，已按 git 实际时刻更正（避免再出现"声明时刻与证据不符"）。*
**2026-10-24 Wong 三问三答：「1.可开工」「2.现在用的是 J11，J10 不需要管了」「3.由 DSH 接手」(w4)** ⇒ 阶段3 板级**单次窗口**已据此执行完毕（授权文件 `report/evidence/S3-T17/hw_authorization.json`，引用决策记录 `decisions/stage_3_4_direction_20261024_r01.md`、`DSH-20261024-004`、Codex `CDX-20261023-018` §3.1 不争用）；**J10 已移出未闭合项、记为「范围排除」**。
**当前口径（顶部）**：颜色子项 = **`PASS_VERIFIED_NEW_MODULE`**（新模块实测解除受阻）；**当前部署 = 无补偿实时彩色**；**阶段3 整体 G5 未通过**（阶段A 小任务 G5 ≠ 阶段3 G5）；`DEFERRED_PENDING_MODULE` 仅为旧模块期历史标签。

## 当前彩色部署（唯一口径；每次硬件使用前重新核对现场与产物）
- 位流 **无补偿 SOF `7cb33068…`**（1,668,969 B）；XSA **`1f5b138e…`**（633,089 B）；应用 **`an5642_j11cmos2_v10_read.elf` `1457cda4…`**（015 §2.2 身份；本轮已实算复核一致）。
- 构建来源 `e9b853f`（本分支）、`xc7z020clg400-2`、Vivado 2026.1；约束 `an5642_j11_cmos2.xdc` `2dae928c…`；补丁 `alinx_ov5640_sof_hrefgap.patch` `fd854a62…`（GAP_THRESH=16384；HTS=1892/VTS=740 ⇒ 612<16384<38452）；WNS **1.054525** / WHS 0.058931 / TNS=THS=0；DRC 0 error、8 warning、0 critical。
- 传感器与格式：CMOS2（J11）CHIPID `0x5640`（TRY0/1/2 均应答；旧模块仅 TRY0）、1280×720、PCLK≈84 MHz；DDR 内存序 **B,G,R**、每行 3840 B、行地址 = `FRAME0 + y×stride`（**运行期回读**，禁硬编码）。
- 颜色证据：`report/evidence/S3-T05/t05_new_module_reverify_20261023_r01/`（提交 `b98ce73`）—— 缺位签名**消失**（蓝 bit7 21.719–39.141%、绿 bit4 38.047–50.156%；旧模块 `0.000%/0.000%`）、彩条 8 条满量程且色相顺序正确（白 `B5=31`、绿 `G6=63`；旧模块 15/59）、实景 `B/R≈0.85–0.99`（旧模块 0.45）；**本轮独立实算该证据 `hashes.txt` 6/6 一致**。
- 彩条工具纪律（015 §2.4）：v12 **会写传感器寄存器**，只在明确授权 + 独占窗口按**既定彩条用例**使用；用前保存原值、写后读回、结束**恢复 `0x503D=0x00`** 并留恢复后实时流证据；**不得当通用重置工具**（复测轮已按此执行）。
- G2 当前材料：`report/evidence/S3-T05/t05_g2_reconciliation_20261024_r01/g2_material_list_r02.json`（对上轮 `CHANGES_REQUIRED` 做修订；r02 独立复审 `PASS`，见本 STATE）；旧 `t05_closeout_prep_20261024_r01/g2_material_list.json` 保留原字节，仅作窗口前历史材料。

## 真实未关闭项（015 r03 §2.4；颜色项通过不替其余项关闭）
*已完成（不再列为未关闭）*：**颜色项**（`PASS_VERIFIED_NEW_MODULE`）、**≥30 分钟实时耐久**、**参考帧集**、**阶段3 地址事实**、**真彩目视（人工观察，2026-10-24 01:41）**。
*未关闭（本清单为准）*：① **VDMA 粘滞 `0x00015810`（PARTIAL，根因未定）**；② **TIMING-17/36 与 I/O delay**（C2/I1/I2/I3 未闭合/未验证）；③ **无 ILA（BASIC 许可）**；④ **task-11 顺序等价 `NOT_RUN`**（静态阈值译码已 PASS）。
- **完整独立 G2**：`report/evidence/S3-T05/t05_g2_reconciliation_20261024_r01/g2_material_list_r02.json` 的上一轮四项整改经独立 Reviewer `PASS`，结论限于本次 G2 修订复核；早期 stdluma/gray 补丁仅人工审阅、未独立 PASS（若重新启用须复审）。阶段3 G5 仍未通过。
- **≥30 分钟实时耐久**：**已达成（2026-10-24 窗口，RunId `t05_stage3_window_20261024_r01`）** —— `00:49:16 → 01:20:31`（**31 min 15 s**），7 轮活写标记全部 **5/5**、`CR=0x00010003`、`MM2S_SR=0x00011000`、无停止/复位/死锁；UART 连续 35 min（三路 CHIPID `0x5640`、`0x503D=0x00`、5 次采样 × 3 站点指纹全异）。**限机读连续性；目视确认已由 Wong 于 01:41 给出（见上）。**
- **VDMA 粘滞 `0x00015810`**：**PARTIAL（不关闭）** —— 既有窗口中一次性 W1C 清除后 `0x00015810 → 0x00011000`，31 min 15 s / 7 轮稳态回读未复现、无功能影响；新离线补充发现首次 `phase=0` 已为 `0x00014810`，bit11 已置位，到 `t=5` 的 `0x00015810` 仅新增 bit12。已提交元数据将 bit11 命名为 `SOFLateErr`，HDL 摘录为 `s2mm_fsize_more_or_sof_late_bit`；不能仅凭此寄存器值唯一归因为 `FSZ_MORE`，实际触发分支仍未定位。未独立核对 PG020 原文，不得称“零错误”。材料：`report/evidence/S3-T05/t05_stage3_window_20261024_r01/vdma_sticky_result.md`、`report/evidence/S3-T05/t05_offline_closeout_20261024_r01/vdma_fsz_more_analysis.md`、`report/evidence/S3-T05/t05_vdma_root_cause_offline_20261025_r01/`。
- **参考帧集（供阶段4 回放）**：**已采集** —— v11 冻结后按**其自报 FB `0x00114C00`** 转储：整帧 2,764,800 B（sha256 `939fce22…`）+ 3 行样本（各 3,840 B），0 全零行、B/G/R 均值 94.1/86.2/93.5、max 248/252/248；格式/字节序/stride/坐标口径见 `…/reference_frame_set.md`。
- **阶段3 地址事实（供阶段4 选址对照）**：**采集与显示共用同一帧缓冲**（实测 `S2MM@0x430100AC = MM2S@0x4300005C = 0x00110C00`，单缓冲 `stride=0x0F00`、`0x2A3000` 字节）；**全部观测地址 < `0x10000000`** ⇒ 与阶段4 候选区 `[0x12000000,0x12C08000)` **不相交**（注意：地址由应用运行期分配，非链接期静态保证）。详见 `…/address_facts.md`。
- **TIMING-17/36 与 I/O delay**：**适用报告已出（离线，基于本版既有报告）** —— `…/t05_offline_closeout_20261024_r01/timing_io_applicability_report.md`：本版 `WNS 1.055/TNS 0/0 of 21479`、`WHS 0.059/THS 0/0 of 21344`、DRC 0E/8W/0C、`no_clock (240)`、`unconstrained_internal_endpoints (520)`；时钟表含 `clk_fpga_0/1`、`axi_dynclk_0_PXL_CLK_O`、`SerialClk`(500 MHz)；**更正**：×5 关系**已声明**在 rgb2dvi 的 `rgb2dvi_clocks.xdc`，`38-249` 归因**已由部署 routed DCP 只读重跑确认**（master source 取在 IP 端口 `PixelClk`、主时钟对象无逻辑路径；方法论 `TIMING-30` 同源），非未闭合项；**C2（`cmos1_pclk` 无 create_clock）+ I1/I2/I3（无 I/O delay）仍 OPEN**——已按 **Wong 2026-10-24 决定备案为「已记录局限」**（`decisions/stage3_io_delay_c2_limitation_20261024_r01.md`，sha256 `e66c44bb…`）：**未宣称已验证、交付前重评**，**禁止**写成已批准/已通过/已闭合，且**不冲抵** TIMING-17/36 未闭合；`CLOCK_DEDICATED_ROUTE FALSE [cmos1_pclk_IBUF]` 保持登记为已知例外；盘上无板级 I/O 时序资料 ⇒ 不得编造数值；DRC 0 error / 局部 WNS>0 **不替代**完整约束签核。
- **无 ILA**（BASIC 许可禁 `create_debug_core`）：以计数器/状态寄存器、cache 一致性取帧、受控转储、离线仿真补足；**不因此免除**功能/时序/耐久标准；本轮不改许可、不植入调试核。
- **真彩目视：已完成（2026-10-24 01:41，人工观察）** —— Wong 原话「**画面可以接受，正常颜色**」；记录 `report/evidence/CTRL-DSH-HANDOFF/decisions/stage3_human_visual_20261024_r01.md`（sha256 `3bed7f85…`）。**效力**：仅对**当前部署**（无补偿 SOF `7cb33068…` + `v10_read` `1457cda4…` + J11/CMOS2 + 现接线/显示链路）与**该时刻**有效；**位流、ELF、视频端口、接线或显示链路任一变更 ⇒ 本判定失效，须重新目视**。**性质**：人工观察证据，**不得**写成仪器测量或像素级对拍。
- task-11：**静态阈值译码已独立核验 PASS**（`task11_threshold_decode_20261024_r01/`；262,144 组 LUT4 输入、0 差异，`PASS_STATIC_THRESHOLD_DECODE`）；此结果仅为静态组合函数。**RTL↔网表顺序等价仍 `NOT_RUN`**，也未验证计数器状态更新、复位、饱和及跨周期关系；不得据静态 PASS 宣称 task-11 全项完成。
- **VDMA 粘滞离线补充**：`report/evidence/S3-T05/t05_vdma_root_cause_offline_20261025_r01/` 绑定首次/后续状态差分、bit11 的本地元数据与 HDL 组合来源，并收窄应用启动顺序观察范围；没有区分真实首帧触发分支，未核对官方 PG020，**仍 PARTIAL/开放**。
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
- **历史归属（DSH 旧轮）**：STATE 统一、旧离线收尾准备、2026-10-24 板级窗口及离线收尾材料等改动，按当时交接记录归 DSH 阶段3 总控；不表示当前仍由 DSH 持有写权。DSH-20261024-006 后当前主目录/阶段3负责人为 Codex。本轮未改 main、w4/w5/w6/w2b、厂商原件或业务代码；未触碰硬件，不提交。

## 交接行（11 字段，2026-10-25 00:29 UTC+8；本轮阶段3离线补充独立复审 PASS）
任务=`阶段3 VDMA 粘滞状态离线补充；触发根因仍 PARTIAL` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\dbdf`/`codex/stage3-video` | 起始提交=`25629e507acb5b59486589481b4713a77a60e5d1` | 允许修改范围=`report/evidence/S3-T05/t05_vdma_root_cause_offline_20261025_r01/**、.codex/STATE.md` | 未提交改动归属=`本轮 RunId 证据与本行 STATE 更新归当前 Codex；NA/、clockInfo.txt 保持历史归属，未修改；tmp/** 不进入提交` | 让出声明=`阶段3工作树仍由 Codex 项目总控持有；本轮未转移工作树写权、未操作硬件` | 心跳(UTC+8)=`2026-10-25 00:29` | 证据入口=`report/evidence/S3-T05/t05_vdma_root_cause_offline_20261025_r01/`、`report/evidence/S3-T05/t05_stage3_window_20261024_r01/`、`report/evidence/S3-T05/t05_sw_20261020_r01/sr_bit_sources/` | 恢复命令=`只读核验：git -C D:/codex-worktrees/dbdf status --short；python -B D:/FPGA_Competition/verification/check_stage_delivery.py --mode evidence --project-root D:/codex-worktrees/dbdf --manifest report/evidence/S3-T05/t05_vdma_root_cause_offline_20261025_r01/manifest.json` | 状态/下一接手方=`IN_PROGRESS（evidence checker CHECKS_OK；本轮离线补充 Reviewer PASS；VDMA 根因仍未关闭、阶段3 G5 未通过）/ 下一接手方=Codex 项目总控核对并完成提交`
