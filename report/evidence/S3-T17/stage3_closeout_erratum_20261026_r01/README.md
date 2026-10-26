# 阶段3 收尾冻结证据 勘误（对独立复审 CHANGES_REQUIRED 的响应）

- RunId：`stage3_closeout_erratum_20261026_r01`；被审基线：tag `stage3-close-20261026` → `5faa151`（复审范围 `5faa151` + 记账提交 `7e4a0a5`/`5353440`/`cefc279`）。
- 原则：**勘误不改历史**。`report/evidence/S3-T17/stage3_closeout_20261026_r01/`、`…/t17_g3_reconfirm_20261026_r02/` 的既有字节**一律保留不重写**；本文档为**权威更正**，与原记录冲突时以本文档为准。
- 板级事实未被推翻：复审独立复算三个冻结哈希一致，并用项目权威判定器对 `bars_frame/frame_full.bin` 复算得 **BIT_INTEGRITY_PASS（C1–C7 全过；白条 248/252/248；黑条 0/4/0）**。**板级工作不重做**；修复范围是记录与边界。

## P1（阻断）彩条会话越界 —— 已关闭：另立登记 + 边界声明

- **事实**：彩条读写会话发生于 **18:53–18:54**，晚于 r02 的 README/manifest/hashes（18:45–18:46）与"收窗干净"结论；r02 `window_plan` 禁止写传感器寄存器且步骤中无彩条；r02 README §4"本窗口未写任何寄存器/传感器寄存器…未启用彩条"与同目录 `uart_barsg3.txt`（`S3_DIAG12_BARS … after=0x80`、`S3_DIAG6_SENS … 503D=0x80`）**直接矛盾**。原记录有误。
- **更正**：彩条会话**不属于 r02 窗口**，其正式登记 RunId = **`stage3_closeout_erratum_20261026_r01`（本 RunId 的 `bars_session/` 子目录）**；r02 的窗口边界与"只读/未写 503D"结论**仅适用于 18:45–18:46 的那次会话**，不适用于 18:53–18:54 的彩条会话。
- **彩条会话完整登记**（补齐复审要求的身份与授权）：
  | 项 | 值 |
  |---|---|
  | 授权依据 | Wong 2026-10-26「都可以」+「交给你来做」（委托完成真彩判据；含下载窗口已授权） |
  | 位流 / XSA | `7cb33068…`（1,668,969 B）/ `1f5b138e…`（633,089 B）——**与冻结基线同源**（`tmp/s3r06/t04_sof_fix_20261020_r01`） |
  | 应用 ELF | `an5642_j11cmos2_v12_bars_freeze.elf` **`527a74fca6ea0774c3462501…`，310,368 B**（`tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/app/`） |
  | 下载记录 | `run_t05_board_capture.sh <t04_sof_fix_20261020_r01> <v12 ELF> barsg3 55` → **`T05_DOWNLOAD_EXIT=0` / `T05_ALL_DONE=1`** |
  | 传感器写入 | `S3_DIAG12_BARS=503D before=0x00 after=0x80 readback=0x80 write_status=0`（写前回读、写后校验）；冻结/取帧 `S3_DIAG11_HALT=1 … FB=0x00114C00 … t=20` |
  | 恢复 | 重下部署应用（`… v10_read.elf`）→ **`T05_DOWNLOAD_EXIT=0`**；`S3_DIAG5_SENS … 503D=0x00`、`S3_DIAG7_AWB … 503D=0x00` ⇒ **已写回 0x00** |
  | 判定器原始输出 | `bars_session/bit_integrity_bars.stdout.txt`（`analyze_t17_bit_integrity.py --frame bars_frame/frame_full.bin` → **exit 0**，C3/C4/C5/C6/C7 PASS，`requires_human_visual=true`） |
- **status/口径更正**：r02 `manifest.status=PARTIALLY_CONFIRMED_HUMAN_VISUAL_PENDING` **对其窗口仍正确**；收尾记录中"真彩判据本轮完成"更正为「**真彩的机器判据已通过**（彩条满量程、色相顺序、缺位签名不存在；判定器自身要求人工目视）」——**人工目视仍以 2026-10-24 Wong 原话为准**，并由判定器 `requires_human_visual=true` 佐证。R02 遗留空目录 `bars_probe/`、`jt_probe/` 不属入库产物。

## P2（阻断）暗帧判据行不可复现 —— 已关闭

- **事实（离线复算）**：`scripts/stage3_t05/analyze_missing_msb_signature.py rows/row_y100,400,600.bin` → **exit 0**，stdout 末行"判定：符合『两个字节 MSB 同时恒 0』签名"（`p2_darkframe_msb_signature.stdout.txt`）。我此前的 `analyze_t17_bit_integrity.py --frame rows/frame_full.bin` 调用**路径不存在** → **exit 2（输入错误）**（`p2_darkframe_t17_attempt.stdout.txt`）。故 r02 记录的"exit 1"**错误**。
- **更正**：暗帧检查所用脚本 = **`scripts/stage3_t05/analyze_missing_msb_signature.py`**，其**真实退出码 0**，其输出语义 = 「**符合缺位签名**」；该判据的**前提是明亮/彩条帧**（对比 `t17_g3_bars_session`：同一判据家族在亮帧上给出 `BIT_INTEGRITY_PASS`），因此对暗帧（max 8–12、蓝=0）**不适用**，**不构成缺位/故障证据**。原结论方向正确，命令与退出码已更正并附 stdout。

## P3（阻断）约束身份与"正式源未改" —— 已关闭

- **事实（实算 + git）**：
  - **in-tree 正式源** `board/stage3/hardware/an5642_j11_cmos2.xdc` = **`d1d3e976f84e0aa5a67ff695d07c83983cf32887c463d6bf25250821f64aa595`（3,751 B）**；
  - **构建输入副本** `tmp/s3r06/t04_sof_fix_20261020_r01/vendor_src/src/constraints/an5642.xdc` = **`2dae928c9458a71ebc9ae741e71f7a274c18afc237676852c53d5e61bbeff5b2`**；
  - 提交 **`9e27f53`（2026-10-26 14:40，冻结提交祖先）**在 in-tree XDC 追加 `set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets cmos1_pclk_IBUF]` 与 `create_clock -name CMOS1_PCLK -period 11.904762 [get_ports {cmos1_pclk}]`（注释明示"**仅为名义 STA 假设**，PCLK 尚未仪器实测，须复核后调整"）。
- **更正**：冻结基线的约束身份**分两行登记**——`frozen_artifacts.constraint_build_input = 2dae928c…`（参与冻结位流构建）与 `frozen_artifacts.constraint_in_tree_source = d1d3e976…`（正式源，含 9e27f53 的名义 create_clock）。局限表述更正为：「**TIMING-36/30 的正式修复未落**；**C2 的 `create_clock CMOS1_PCLK` 已于 `9e27f53` 以名义假设进入 in-tree 源**，**未纳入冻结位流、未签核**（名义 84 MHz 无仪器实测）」。

## P4（阻断）漏一条验收要求 —— 已关闭

- **事实**：验收计划「阶段3」含「**容许丢帧策略和计数口径在任务G0明确**」，并在 `board/stage3/README.md` 自述"丢帧策略及口径仍须在 G0 明确"。
- **更正**：对照表**补一行**：`容许丢帧策略与计数口径（G0 明确）| **OPEN / 未定义** | 依据：验收计划 §阶段3 与 board/stage3/README.md；G0 未见定义记录 ⇒ 记为未定义项，不视为已通过`。并列入 `not_executed`。

## 轻微项（P5–P10）已关闭

- **P5**：`takeover_record.json` 的"未提交改动 5 项"更正为**原始 checker 输出的 8 项**（含 `?? report/evidence/S3-T17/t17_g3_reconfirm_20261026_r01/`）；偏差本身如实记录不变（并已由 19:05 `OFFERED` + 19:15 `HANDOFF_OK` 消除）。
- **P6**：`freeze_commit` 字段缺失 ⇒ 统一改为指向 **tag `stage3-close-20261026`**（`^{}` = `5faa151`），并在 manifest 增补 `freeze_tag`/`freeze_commit` 两键。
- **P7**："第 3 次独立复现"序数**不可核验**（2026-10-20 已有启动瞬态记录、2026-10-24 窗口两次）⇒ 更正为「**再次独立复现**」，并列出各次证据入口，不主张序数。
- **P8**：人工目视决策文件**不在 dbdf**，真实路径 = `D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\decisions\stage3_human_visual_20261024_r01.md`（跨树绝对路径）；"替代接口（AN5642→J11 而非 HDMI 摄像头）经用户确认"**缺少确认记录**（AGENTS 无该条款）⇒ 对照表第 1 行状态**降级为** `PASS_RECORDED_VARIANT_PENDING_USER_CONFIRMATION`，并列入 `recorded_limitations`（待 Wong 一句确认即可升级）。
- **P9**：恢复入口取址纪律 ⇒ 更正为：`run_t05_board_capture.sh` 的下载/复位语义与记录一致，但其只读回读链 `jtag_read_safe.tcl` 使用**默认 base**；**凡需地址的判定必须用 `jtag_t17_dump_rows.tcl`（base 由调用方显式给出、运行期回读 `ADDR_S2MM`）**，恢复入口的地址核对步骤以运行期回读为准，不依赖默认值。
- **P10**：`nz=16384` 的"满非零"存在 16383 例外；"指纹互异 ⇒ 实时"统一收敛为「**帧缓冲内容随时间变化**」（r02 措辞为准）。

## 修正后的判定

收紧后不变：**阶段3 收尾通过（带记录性局限）** —— 但以下表述以本文档为准：真彩为「**机器判据通过 + 人工目视沿用 10-24 记录**」；约束为「构建输入副本/正式源分列」；`丢帧策略与计数口径 = OPEN`；替代接口确认 = **PENDING_USER_CONFIRMATION**。VDMA 首帧 bit11 根因仍 `PARTIAL_OPEN`、task-11 完整 SEC 仍 `BLOCKED_NOT_RUN`（口径不变，未被包装成通过）。