# 阶段3 状态（AN5642 原始视频链路）

更新：2026-10-24 00:33（离线前置；提交 `78273a6`/`8e04597`/`0e23d3c`）→ **01:28 板级窗口收窗**（提交另附）。工作树 `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`。**`dbdf` 唯一写入方 = DSH 阶段3 总控（stage3-lead）**（`CDX-20261022-015` r03 §2.3）；其他窗口与旧任务卡对本树**只读**。
*更正：本文件此前两处曾写「01:05/01:12」，那是估计值；实际离线前置提交时刻为 `00:30:35`/`00:33:57`/`00:34:32`，已按 git 实际时刻更正（避免再出现"声明时刻与证据不符"）。*
**2026-10-24 Wong 三问三答：「1.可开工」「2.现在用的是 J11，J10 不需要管了」「3.由 DSH 接手」(w4)** ⇒ 阶段3 板级**单次窗口**已据此执行完毕（授权文件 `report/evidence/S3-T17/hw_authorization.json`，引用决策记录 `decisions/stage_3_4_direction_20261024_r01.md`、`DSH-20261024-004`、Codex `CDX-20261023-018` §3.1 不争用）；**J10 已移出未闭合项、记为「范围排除」**。
**当前口径（顶部）**：颜色子项 = **`PASS_VERIFIED_NEW_MODULE`**（新模块实测解除受阻）；**当前部署 = 无补偿实时彩色**；**阶段3 整体 G5 未通过**（阶段A 小任务 G5 ≠ 阶段3 G5）；`DEFERRED_PENDING_MODULE` 仅为旧模块期历史标签。

## 当前彩色部署（唯一口径；每次硬件使用前重新核对现场与产物）
- 位流 **无补偿 SOF `7cb33068…`**（1,668,969 B）；XSA **`1f5b138e…`**（633,089 B）；应用 **`an5642_j11cmos2_v10_read.elf` `1457cda4…`**（015 §2.2 身份；本轮已实算复核一致）。
- 构建来源 `e9b853f`（本分支）、`xc7z020clg400-2`、Vivado 2026.1；约束 `an5642_j11_cmos2.xdc` `2dae928c…`；补丁 `alinx_ov5640_sof_hrefgap.patch` `fd854a62…`（GAP_THRESH=16384；HTS=1892/VTS=740 ⇒ 612<16384<38452）；WNS **1.054525** / WHS 0.058931 / TNS=THS=0；DRC 0 error、8 warning、0 critical。
- 传感器与格式：CMOS2（J11）CHIPID `0x5640`（TRY0/1/2 均应答；旧模块仅 TRY0）、1280×720、PCLK≈84 MHz；DDR 内存序 **B,G,R**、每行 3840 B、行地址 = `FRAME0 + y×stride`（**运行期回读**，禁硬编码）。
- 颜色证据：`report/evidence/S3-T05/t05_new_module_reverify_20261023_r01/`（提交 `b98ce73`）—— 缺位签名**消失**（蓝 bit7 21.719–39.141%、绿 bit4 38.047–50.156%；旧模块 `0.000%/0.000%`）、彩条 8 条满量程且色相顺序正确（白 `B5=31`、绿 `G6=63`；旧模块 15/59）、实景 `B/R≈0.85–0.99`（旧模块 0.45）；**本轮独立实算该证据 `hashes.txt` 6/6 一致**。
- 彩条工具纪律（015 §2.4）：v12 **会写传感器寄存器**，只在明确授权 + 独占窗口按**既定彩条用例**使用；用前保存原值、写后读回、结束**恢复 `0x503D=0x00`** 并留恢复后实时流证据；**不得当通用重置工具**（复测轮已按此执行）。
- G2 固定材料：`report/evidence/S3-T05/t05_closeout_prep_20261024_r01/g2_material_list.json`（含本轮实算哈希与时序/DRC 基线）。

## 真实未关闭项（015 r03 §2.4；颜色项通过不替其余项关闭）
- **完整独立 G2**：对上述实际部署（SOF/采集/显示/应用/约束/补丁）独审 —— 材料已固定，**待 DSH 项目总控另派 Reviewer**；早期 stdluma/gray 补丁**仅人工审阅、未独审 PASS**（重新启用须补审查）。
- **≥30 分钟实时耐久**：**已达成（2026-10-24 窗口，RunId `t05_stage3_window_20261024_r01`）** —— `00:49:16 → 01:20:31`（**31 min 15 s**），7 轮活写标记全部 **5/5**、`CR=0x00010003`、`MM2S_SR=0x00011000`、无停止/复位/死锁；UART 连续 35 min（三路 CHIPID `0x5640`、`0x503D=0x00`、5 次采样 × 3 站点指纹全异）。**限机读连续性；"连续画面"目视属 Wong 端（未做）**。
- **VDMA 粘滞 `0x00015810`**：**PARTIAL（不关闭）** —— 启动原值 `0x00015810`（两次独立启动均复现＝启动瞬态）；一次性 W1C 清除后 `0x00015810 → 0x00011000`，**31 分钟 7 次回读未复现**、无功能影响；但**无根因解释**（`FSZ_MORE` 触发源未定位）⇒ 不得称"零错误"。详见 `…/t05_stage3_window_20261024_r01/vdma_sticky_result.md`。
- **参考帧集（供阶段4 回放）**：**已采集** —— v11 冻结后按**其自报 FB `0x00114C00`** 转储：整帧 2,764,800 B（sha256 `939fce22…`）+ 3 行样本（各 3,840 B），0 全零行、B/G/R 均值 94.1/86.2/93.5、max 248/252/248；格式/字节序/stride/坐标口径见 `…/reference_frame_set.md`。
- **阶段3 地址事实（供阶段4 选址对照）**：**采集与显示共用同一帧缓冲**（实测 `S2MM@0x430100AC = MM2S@0x4300005C = 0x00110C00`，单缓冲 `stride=0x0F00`、`0x2A3000` 字节）；**全部观测地址 < `0x10000000`** ⇒ 与阶段4 候选区 `[0x12000000,0x12C08000)` **不相交**（注意：地址由应用运行期分配，非链接期静态保证）。详见 `…/address_facts.md`。
- **TIMING-17/36 与 I/O delay**：TIMING-17 critical 236、TIMING-36 critical 1、`Timing 38-249`（rgb2dvi `SerialClk`×5 未声明）仍开放；准备 `…/t05_closeout_prep_20261024_r01/timing_io_applicability_prep.md`（DRC 0 error / 局部 WNS>0 **不替代**完整约束签核；不加虚假关系或豁免）。
- **无 ILA**（BASIC 许可禁 `create_debug_core`）：以计数器/状态寄存器、cache 一致性取帧、受控转储、离线仿真补足；**不因此免除**功能/时序/耐久标准；本轮不改许可、不植入调试核。
- **真彩目视**（Wong：不偏黄不偏青）：**未做**（窗口内机读证据不能替代）；需 Wong 在场。
- task-11 网表交叉核对未完成（补丁已人工审阅）；未做电气测量、未烧 QSPI、未改接线；传感器寄存器改动均为易失。

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
- 本轮（STATE 统一 + 离线收尾准备 + **板级窗口**）改动归属：`.codex/STATE.md`、`report/evidence/S3-T05/{t05_closeout_prep_20261024_r01,t05_stage3_window_20261024_r01}/**`、`report/evidence/S3-T05/t05_new_module_reverify_20261023_r01/{README.md,hashes.txt}`（UR-2 标题更正）、`report/evidence/S3-T17/hw_authorization.json`、`scripts/stage3_t05/jtag_{liveness_marker,s2mm_sr_clear,addr_map_read,addr_scan,addr_scan_mm2s}.tcl` 归 **DSH 阶段3 总控（stage3-lead）**；不改 `main`/`w4`/`w5`/`w6`/`w2b`/厂商原件；不 push；不写两个 mailbox（只读）。

## 交接行（11 字段，2026-10-24 01:30（板级窗口收窗）；上一条见 Git 历史与接管证据）
任务=`阶段3：STATE 统一（015 r03 §2.3）+ 离线收尾准备（§2.4 不需板卡部分）；板级项待 Wong 开工信号` | 负责人=`DSH 阶段3 总控（stage3-lead）＝ dbdf 唯一写入方` | 工作树/分支=`D:\codex-worktrees\dbdf`/`codex/stage3-video` | 起始提交=`f94c25ff2bd539e2ca45b450334ddc8bb8cde6e7` | 允许修改范围=`board/stage3/**`、`scripts/stage3_t03b/**`、`scripts/stage3_t04/**`、`scripts/stage3_t05/**`、`scripts/stage3_t17/**`、`report/evidence/S3-T05/**`、`report/evidence/S3-T17/**`、`report/evidence/S3-CTRL/**`、`.codex/STATE.md` | 未提交改动归属=`NA/`、`clockInfo.txt` 为旧轮散落件、保留不动；`.codex/STATE.md`、`report/evidence/S3-T05/t05_closeout_prep_20261024_r01/**` 归 DSH 阶段3 总控待提交；`tmp/**` 为构建缓存不入提交` | 让出声明=`015 r03 §2.3 指定 DSH 阶段3 总控为 dbdf 唯一实际写入方；本树自 2026-10-23 10:10 CLAIMED→IN_PROGRESS 独占写入（handoff_check --claim 真实退出码 0）；无让出` | 心跳(UTC+8)=`2026-10-24 01:30` | 证据入口=`report/evidence/S3-T05/t05_stage3_window_20261024_r01/`（**板级窗口：耐久 31min15s、VDMA PARTIAL、参考帧集、地址事实、收窗记录**）、`report/evidence/S3-T05/t05_closeout_prep_20261024_r01/`（STATE 口径 + 阶段B 处置 + G2 材料 + TIMING/VDMA/J10 准备）、`…/t05_new_module_reverify_20261023_r01/`（颜色解除受阻，6/6 哈希复核）、`report/evidence/S3-T17/{t17_closeout_20261023_r01,t17_quickfix_20261023_r01,t17_fix_20261023_r01,t17_color_retest_prep_20261023_r01,t17_guard_ok_20261023_r01}/`（工具与修复轮）、`report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/`（接管与自证）` | 恢复命令=`cd D:/codex-worktrees/dbdf && bash scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id <新RunId>（须在 dbdf 内跑）；python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --selftest；python -B scripts/stage3_t17/verify_t17_blob_identity.py --selftest；获 Wong 开工信号后按 018 §3.3 在单次窗口执行板级项（耐久/VDMA/TIMING/J10/目视）` | 状态/下一接手方=`IN_PROGRESS（颜色项 PASS_VERIFIED_NEW_MODULE；**板级窗口已执行**：耐久达标、VDMA PARTIAL、参考帧集与地址事实已交付；**阶段3 整体 G5 仍未通过**，完整独立 G2 待另派 Reviewer，TIMING/I-O 与真彩目视仍开放；J10=范围排除）/ 下一接手方=DSH 阶段3 总控（dbdf 唯一写入方）`