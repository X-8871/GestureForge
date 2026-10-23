# S3-T17 阶段3 色彩复测：到货前离线准备包（2026-10-23）

- 任务：共享看板 `task-17`（阶段3 色彩复测：新摄像头到货前后，DVP 位完整性 + 真彩通路）。
- 工作树/分支：`D:\codex-worktrees\dbdf` / `codex/stage3-video`；接管基线 HEAD `f94c25f`，**本修复轮冻结 HEAD 见 `.codex/STATE.md` 交接行与 `report/evidence/S3-T17/t17_fix_20261023_r01/`**。
- **前提（评审 N-4）**：本仓库系统级 `core.autocrlf=true` => 按工作区口径复核哈希/自证必须 `git -c core.autocrlf=false clone`（或 `git cat-file blob <rev>:<path>`）；DSH 已决定暂不为本三范围加 `.gitattributes -text`。
- 本包性质：**纯离线准备**。本次**未接触任何硬件**（无 JTAG/COM4/hw_server/烧录），阶段 B 待 Wong 开工信号 + 硬件窗口书面确认。
- 运行状态：颜色子项仍为 `DEFERRED_PENDING_MODULE`（Wong 2026-10-22 决定）；本包**不宣称颜色通过**。

## 1. 触发与现状（先用证据核对过）

| 事实 | 依据 |
|---|---|
| 新摄像头今晚到货、型号与上次相同 | Wong 2026-10-23 告知（主 STATE HL-T28 行） |
| 上次颜色结论：无补偿基线上「两字节 MSB 同时丢失」 | `report/evidence/S3-T05/t05_color_msb_missing_20261022_r01/`（白条 B5=15(120)、G6=59(236)） |
| 该结论数值已由 DSH 项目总控独立复核；**电气定位未证** | `dsh_mailbox/DSH-20261022-007-colorbar-recheck.md` |
| 部署位流（灰度）`44e609cc…` / XSA `90e1bdee…`；颜色未通过 | `report/evidence/S3-T05/t05_stage3_closeout_20261022_r01/` |
| 复测必须用**无补偿基线**位流 `7cb33068…` + 只读 ELF，禁用灰度/补偿位流 | `t05_freeze_20261021_r01/README.md` §5、CDX-20261022-009 §3-C |
| `0x503D` 是**传感器内部彩条**寄存器；上次无摄像头时不可用，**有摄像头后重新可用** | `report/evidence/S3-T14/v12_bars_freeze_tool_20261022_r01/README.md` |

## 2. 接线口径（本轮实际使用的通道）

- 模块插 **J11**，走模块的 **CMOS2** 通道；约束文件 `board/stage3/hardware/an5642_j11_cmos2.xdc`（`PACKAGE_PIN F17 = cmos1_d[9]`）。
  - 注意：`board/stage3/board_test_runbook.md` 仍写 J10/CMOS1，属旧（2026-10-03）口径；**以本树 STATE 与实际构建脚本 `run_t04_camera_j11_cmos2_build.sh` 为准**（J11+CMOS2 当前能出图）。
- 采集 1280×720、RGB565、DVP（`0x4300=0x60`、`0x501F=0x01` ISP RGB）。
- 帧缓冲内存序 **B,G,R**，每行 3840 字节；行地址 = `FRAME0 + y×stride`，**运行期回读**取 `ADDR_S2MM/STRIDE_S2MM`，禁止硬编码旧地址。
- `cmos_d[9]` = 两个 DVP 字节各自的 MSB；字节布局 **第一字节 = `{b[4:0], g[5:3]}`（MSB=`B[4]`）、第二字节 = `{g[2:0], r[4:0]}`（MSB=`G[2]`）**，16 位字 `R=word[4:0]`、`G=word[10:5]`、`B=word[15:11]` => 帧缓冲 **offset0（蓝）bit7** 与 **offset1（绿）bit4** 恒 0、**offset2（红）完好**。
  - **命名限制（评审 N-1，已据实更正）**：「蓝/绿」是帧缓冲通道名，字节↔通道对应来自归档网表（`…/t05_takeover_20261021_r03/channel_mapping_report.json`：offset0=B、offset1=G、offset2=R）；**DVP 字节序有厂商源码 + 网表双重依据**——已入库参考 `report/evidence/S3-T05/t05_github_ref_20261020_r01/cmos_8_16bit_ref.v`（sha256 `08a325356fdb46fcbd87e1b594a2b5d3c30954b68d18e4ea22d36e914cd414b9`，3318 B）第 157 行 `pdata_o <= {pdata_i_d0,pdata_i};`（先到字节进高半字）。**命名限制仍保留**：阶段B 报告用数值判据（offset0 bit7、offset1 bit4、offset2 完整）陈述，不单独依赖通道命名。（旧文「厂商源码已被缓存清理、盘上未找到」不实，本轮实查盘上有 56 份同名源码，全部含该拼接语句。）
- 电气安全（Wong 执行实物）：断电插拔；Pin1 对齐；Pin2 是 +5V 供电脚；BANK35 为 3.3V，不得接 5V I/O。

## 3. 判定标准（完整表见 `t17_judgement_table.json` / `.md`）

### ① 位完整性（机器可判）
| 判据 | 修好 | 仍是旧缺陷 |
|---|---|---|
| C2 白条 G 满量程（G8 ≥ 248） | 252 | 236 |
| C3 白条 B 满量程（B8 ≥ 240，等价「出现 >127 的蓝」） | 248 | 120 |
| C6 旧签名不存在（蓝 bit7 与绿 bit4 置位率不同时为 0） | 两者 > 0 | 0.000% / 0.000% |
| C1 白条 R 满量程（对照组） | 248 | 248 |
| C5 黑条零值（负样本） | 0,4,0 | 0,4,0 |
| C7 字段位逐位可辨（16 字段位 = R5+G6+B5；8 结构性低位不计） | **16/16** | **14/16**（对齐口径；严格口径 13/16） |

**边界（必须如实说明）**：「每个字节 8 位逐位可辨」在本链路**不可字面达成**——RGB565 为 5/6/5 移位扩展，R/B 显示字节 bit2..0、G 显示字节 bit1..0 结构性恒 0（合计 **8 位**）；可辨的是 **16 个字段位**（依据 `5+6+5=16`、`3+2+3=8`、`16+8=24=3×8`）。8 位显示值为**移位扩展**（248=31<<3、252=63<<2），故「修好」的期望值不是 255。**C7 口径与 C5 对齐**（黑条字段值 ≤ 容差 R/B:1、G:2 不计不可辨）：对齐口径缺陷 14/16、修好 16/16；严格口径缺陷 13/16、修好最多 15/16（与 C5 冲突，仅 `--strict-black-bits` 对照用）——评审 B-1/B-2 关闭依据。

### ② 真彩帧（机器部分 + 目视）
- 机器部分（C4）：白条中性度 `|R−G|、|G−B|、|R−B| ≤ 8`（旧缺陷下 `|G−B|=116`，画面偏黄）。
- 目视（Wong）：HDMI 上白纸/白条**不偏黄也不偏青**；彩条色相与顺序正确。
- 仅机器部分通过**不构成**颜色验收通过；两者都满足才可建议关闭颜色子项。

### ③ 结论二选一
- **(a) 色通过** => 关闭颜色子项，并通知阶段6 可开始 **6-E 真手势验收**（同时告知阶段5 真彩前端可解除阻塞）。
- **(b) 复现缺陷** => 判**板侧/连接侧**方向（同型号新模块仍复现则基本排除模块），颜色保持 `DEFERRED`，按 §6 定位。

## 4. 一次性准备已完成（本包 = 可执行件）

| 产物 | 说明 |
|---|---|
| `scripts/stage3_t17/run_t17_color_retest.sh` | 一键执行器：`preflight`/`judge`/`link`/`baseline`/`bars`/`all`；硬件阶段需 `--allow-hardware` + `hw_authorization.json` 双前提 |
| `scripts/stage3_t17/analyze_t17_bit_integrity.py` | 判定器（退出码 0 通过 / 1 复现旧缺陷 / 2 用法 / 3 非典型）；含 `--selftest` |
| `scripts/stage3_t17/check_t17_preflight.py` | 离线前置：分支/HEAD/锁/重型进程 + 冻结产物**实算哈希** + 硬件门禁 |
| `scripts/stage3_t17/jtag_t17_link_check.tcl` | 只读 JTAG 链路确认（**陷阱**：用 `llength [targets]`/`jtag targets`，不用裸 `targets`） |
| `scripts/stage3_t17/jtag_t17_dump_rows.tcl` | 安全转储（halt→mrd→con）：**基地址/stride 必须显式传入**，不内建旧地址 |
| `scripts/stage3_t17/make_t17_manifest.py` | 实测后打包 manifest + hashes（退出码只接受真实值） |

离线自测证据（本次真实执行）：
- `t17_analyzer_selftest.json/.stdout.txt`：`SELFTEST_PASS`（7 例：真实归档缺陷帧→`DEFECT_REPRODUCED`(1)、合成满足→(0)、只修蓝→(3)、双缺位 OR 恢复但黑条被置位→(3)、该例再清黑条→(0)、**判定表自声明 if_fixed 夹具 F→(0)**、夹具 F 严格口径探针→(3)），**退出码 0**；其中夹具 F 的 exit 0 即评审 B-2 关闭证据。
- `t17_archived_frame_judgement.json/.stdout.txt`：对上次归档彩条帧独立复算，得白条 `(248,236,120)`、蓝 bit7/绿 bit4 置位率 `0.000%/0.000%`、**字段位 14/16（严格口径 13/16）**、`DEFECT_REPRODUCED`，**退出码 1** —— 与上次结论一致。
- `t17_preflight_now.json/.stdout.txt`：在接管基线 `f94c25f` 上 `OFFLINE_GO`（7 件冻结产物哈希一致）；**冻结 HEAD 上的复跑见 `report/evidence/S3-T17/t17_fix_20261023_r01/preflight_frozen_head.*`**。
- 硬件门禁实测（**未动板**）：`link`/`baseline`/`bars` 在缺开关或缺授权时一律退出 **3**（`T17_HW_BLOCKED=...`）。
- `t17_artifacts_verified.json`：产物哈希清单；其中 v9/v10/v12 三支 ELF 的 `_input` 位流/XSA 与无补偿基线**逐字节一致** => 无 ELF↔位流错配风险。

## 5. 到货后 15 分钟内可执行的步骤清单

前置（离线，随时可跑）：`bash scripts/stage3_t17/run_t17_color_retest.sh preflight` → 应 `OFFLINE_GO`。
前置判据（评审 B-3 关闭后）：HEAD 只需是**声明基线或其后代**（`git merge-base --is-ancestor`），基线默认 `f94c25f`，可用 `--baseline-commit <rev>` 或 env `T17_BASELINE_COMMIT` 覆盖；因此本交付物在其自身冻结 HEAD（含 `525e4f35` 与后续提交）上都会通过，不再钉死在某一提交。

Wong 开工信号 + 硬件窗口书面确认到位后，写入 `report/evidence/S3-T17/hw_authorization.json`（模板见 `evidence_template/`），然后：

| # | 时间预算 | 步骤 | 命令/要点 | 预期 |
|---|---|---|---|---|
| 1 | 0–1 min | 离线前置 | `run_t17_color_retest.sh preflight` | `OFFLINE_GO`；无 index.lock/无重型进程；基线关系为 `equal`/`descendant` |
| 2 | 1–3 min | **断电**换模块到 J11（Pin1 对齐），上电；记录新旧模块身份 | 实物由 Wong 执行 | 模块插好、供电正常 |
| 3 | 3–4 min | 只读 JTAG 链路确认 | `run_t17_color_retest.sh link --allow-hardware` | `T17_JTAG_TARGET_COUNT ≥ 1`、`T17_JTAG_LINK=OK`；用后自动终止自起 `hw_server` |
| 4 | 4–7 min | 刷**无补偿基线** `7cb33068…` + `v9_read`，抓 UART，只读回读取地址/stride | `run_t17_color_retest.sh baseline --allow-hardware` | UART 见 `S3_DIAG_SENSOR_ID=0x5640`、`0x503D=0x00`；回读到 `ADDR_S2MM/STRIDE_S2MM` |
| 5 | 7–8 min | 安全转储 3 行（y=200/360/500，新空目录） | 执行器自动完成 | 每行 3840 字节，`T17_DUMP_RESUME_OK=1` |
| 6 | 8–9 min | 判定真实场景与黑白 | 执行器自动 `judge` | 看蓝 bit7/绿 bit4 置位率是否终于 > 0 |
| 7 | 9–12 min | 内部彩条 `0x503D=0x80`（v12，易失）→ 转储整帧 → **恢复** | `run_t17_color_retest.sh bars --allow-hardware` | 写前回读 0x00、写后 0x80；恢复后回读 `503D=0x00` |
| 8 | 12–13 min | 彩条判定（决定性） | 执行器自动 `judge bars` | 白条 B5=31(248)、G6=63(252) => 修好；仍 15(120)/59(236) => 复现 |
| 9 | 13–14 min | **HDMI 目视核对**（Wong） | 看白纸/彩条是否仍偏黄 | 不偏黄不偏青 => 真彩目视通过 |
| 10 | 14–15 min | 打包证据 + 结论 | `make_t17_manifest.py` | 新 RunId 目录含 manifest + hashes + 真实退出码 |

异常停止点：传感器 ID 非 `0x5640`/无 ACK、下载或 PS 初始化非 0、转储行长度≠3840、`ADDR_S2MM` 缺失、恢复后 `0x503D` 非 0 —— 一律停止并保全日志，不反复热插拔。

## 6. 若复现缺陷：判板侧方向与可查项

同型号新模块在 J11 仍复现 => 基本排除「上一模块个体故障」，按下列逐项定位（每项独立可查）：
1. **新旧模块 × J11/J10 的 2×2 交叉矩阵**（断电换装、Wong 执行）：新模块在 J11 正常 => 旧模块 D9 通路故障；两连接器都复现 => 系统性问题，继续 2–5。
2. **触点**：断电目视 J11 pin3 与模块 J3 pin3（弯针/氧化/整排错位）、Pin1 对齐。
3. **线序/串阻**：模块 pin3(`CMOS2_D9`) → J11 pin3 → 原理图 33Ω → FPGA `F17`（LVCMOS33/Bank35）；映射已有五路证据一致，仍按实际 PCB/BOM 复核。
4. **对照另一条同字节 MSB 线**（如 D8→J18）与已知良好通道的连续性与电平（需 Wong 授权，不擅自做电气测量）。
5. **原厂例程/另一套板**复现，彻底分离板侧与模块侧。

## 7. 未做项与限制（不得当作通过）

- 阶段 B **未执行**：未动板、未下载、未烧录、未开 COM4、未起 `hw_server`（只有离线判定与门禁测试）。
- 真实场景色彩、曝光、稳定性、几何逆映射、HDMI 物理链路**均未验证**；`≥30 分钟耐久`、VDMA 粘滞 `0x00015810`、方法学 TIMING-17/36 与 I/O delay 缺口、J10「半屏」未定性、无 ILA —— 全部仍开放。
- 彩条为**传感器内部图案**，只测数传通路，不等于真实场景色彩；`0x503D` 写入仅易失，用后必须恢复并回读。
- 判定器只覆盖位完整性与彩条数值；**真彩必须 Wong 目视确认**。
- 本包为阶段 A 准备；阶段3 颜色子项在实测证据与独立审查前保持 `DEFERRED`。

## 8. 证据入口

- 接管与让出链：`report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/`
- 本准备包：`report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/`
- 到货后实测预留 RunId：`report/evidence/S3-T17/t17_color_retest_20261023_r01/`（当前仅离线 preflight 与判定器往返，见该目录 `PENDING_HARDWARE_NOT_EVIDENCE.md`）
- 上次结论：`report/evidence/S3-T05/t05_color_msb_missing_20261022_r01/`、`dsh_mailbox/DSH-20261022-007-colorbar-recheck.md`
- 冻结与复测配方：`report/evidence/S3-T05/t05_freeze_20261021_r01/README.md` §5；Codex 侧操作文档 `codex_mailbox/CDX-20261022-009-stage3-camera-runbook.md`