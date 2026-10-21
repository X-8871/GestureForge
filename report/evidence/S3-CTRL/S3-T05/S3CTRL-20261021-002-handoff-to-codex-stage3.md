# S3CTRL-20261021-002 阶段三交接：DSH 阶段三总控 → Codex 阶段三总控

- 类型：**跨方阶段交接（OFFERED）**
- 时间：2026-10-21 15:05（UTC+8）
- 交出方：DSH 侧阶段三总控（窗口 `lead`）
- 接手方：**Codex 阶段三总控**
- 工作树／分支：`D:\codex-worktrees\dbdf` / `codex/stage3-video`
- HEAD（交出时）：`402b074`；本交接文档与 `.codex/STATE.md` 更新随同一次提交落在其之后
- 交接依据：`.codex/STATE.md` 末尾 11 字段交接行已置 `OFFERED`（心跳 `2026-10-21 15:05`）
- 交出方状态：**已停止写入该工作树**；除本次交接提交外不再改动

---

## 1. 阶段目标与已达成结论

**目标（第一版）**：AN5642(OV5640) → 扩展口 → PL 采集/DDR 缓冲 → HDMI → 显示器，**原始画面直通**；单通道；不加 CNN／检测框／手势交互。

**已达成的可复现结论**：

1. **实物实时直通成立**：SOF 修复位流 `7cb33068…8710`（XSA `1f5b138e…cb0e3`）在 J11+CMOS2 上出画面；Wong 目视“手在镜头前动、画面跟着动”；v6 指纹诊断（3 处 × 64 KB，`sum32+CRC-32`，读前 `Xil_DCacheInvalidateRange`）t≈5/10/15/20/25 s **15/15 互不相同**，传感器 `0x4202=0x00` 仍在流。
2. **帧同步缺陷已修**：厂商 IP `alinx_ov5640.v` 的 `s_axis_tuser` 由“`cmos_vsync` 下降沿”改为“hblank 连续低 ≥ `GAP_THRESH=16384` pclk 后的第一个有效像素”（行间隙 612 pclk < 阈值 < 场间隙 38452 pclk）；补丁 `board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch`；清 sticky 后 20 s 内无新错误。
3. **引脚映射无误**（五路独立证据）：AX7020 V3.0 手册 Table 7.5.1、官方 `23_ov5640_dual` XDC、模块原理图网名序列、原理图文字坐标配对、GitHub 社区 AN5642 工程信号顺序。J11 与 J10 变体的 16 个信号落点均有 io_placed 逐条证据（J10 阳性 16/16、J11 阴性对照 0/16、与官方 XDC 归一化后 IDENTICAL 16/16）。
4. **通道事实**：模块 **CMOS1 无 I2C ACK**（两种连接器两次验证）⇒ 模块 CMOS1 侧故障；**CMOS2 可用**（CHIPID=0x5640、1280×720、VTS=0x2E4、PCLK≈84 MHz）。
5. **已作废的旧判断**：基于 JTAG 标记法（halt 的 A9 上 `mwr/mrd`）得出的“冻结单帧／帧缓冲全 0／显示全黑”不成立——该方法经 CPU 数据 cache，不能作为 DDR 内容证据；已改用应用侧 cache 正确判据。

## 2. 唯一技术阻塞：蓝通道 B[4] 缺位（详细）

### 2.1 现象（4 组独立数据一致）

RGB565 的 **B[4]（蓝最高位）恒为 0** ⇒ 蓝通道上限只有 120，**任何数据里都没有 >127 的蓝像素**；R/G 正常可达 248/236；画面整体偏黄。

数据来源：白纸填满画面 / 实景（AWB 开）/ 实景（AWB 关）/ 传感器彩条（`0x503D=0x80`）。
反证：手动白平衡把 B 增益推到 3.5×（`0x3400..0x3405` 写 `0x0E00`，回读 `match=1,1,1`，字段 ≥12 位确认）后**蓝仍锁 120**。

已排除：显示器（Wong 确认菜单与其他内容正常）、AWB/ISP（关掉 AWB 蓝更低）、通道/字节序错位（彩条色相与顺序正确）、565→888 扩展（量级不足）。

### 2.2 已定位范围

- 位序依据：厂商 IP 取 `cmos_d[9:2]` 当字节，RGB565 第二字节 = `{G[2:0], B[4:0]}` ⇒ **B[4] = 该字节 bit4 = DVP 的 `cmos_d[6]`**；同一逻辑在厂商 `cmos_8_16bit.v` 与社区工程源码中一致（`pdata_o <= {pdata_i_d0, pdata_i}`）。
- **J10 交叉验证（决定性）**：把模块改插 J10、用官方 `23_ov5640_dual` 的 cmos2 映射（B[4] 对应线换到 R14，与 J11 的 F20 完全不同）重建位流 `d4ce330b…` 后上板：I2C 正常（CHIPID=0x5640）、实时指纹正常变化，**但蓝仍锁 120、>127 蓝像素为 0** ⇒ **排除板侧 J11/F20**。
- 结论：根因在**模块 D6 走线/触点**或**传感器 B4 输出**（无第二块模块、未做电气测量，未再细分；两条路修法相同）。

### 2.3 PL 重建位补丁“构建成功但实机未生效”（接手方第一优先）

- 变体内容：厂商 IP 内新增
  `wire[15:0] s_axis_tdata_bluefix = {s_axis_tdata[15:5], s_axis_tdata[3:0], s_axis_tdata[3]};`
  （即 `B'[4:0] = {B[3:0], B[3]}`，只有 bit4 语义变化）并用于输出 `xpm_fifo_async` 的 `.din({s_axis_tdata_bluefix, s_axis_tlast, s_axis_tuser})`；`.dout` 直接驱动 `m_axis_video_tdata`。
- 补丁：`board/stage3/software/sensor/alinx_ov5640_blue_msb_rebuild.patch`（`6609a59d…`，3 hunks，+5/−2），与 SOF 补丁**顺序可交换**（双向实测同结果）。
- 构建：RunId `tmp/s3r06/t04_bluefix_20261020_r01`，**退出码 0**；bit `0819d0da1508cdc43f72d8ab67e8d4173de3ddc656e3fbfa957a72c061c119d7`、XSA `fed8f652…`；WNS 1.1027 / WHS 0.0404 / DRC 0 Error。
- 上板：J11 实机下载，下载日志与哈希确认烧的就是该 bit（`FPGA_PROGRAM` OK），**但 DDR 蓝直方图与修复前完全同构**：
  修复前后都只有蓝值 ∈ {0,8,16,…,120}（16 个离散值），**且仍出现奇数域值**（8/24/40/…，对应 5 位域 1/3/5）。
  若补丁生效，5 位域应为 `{b3,b2,b1,b0,b3}`，**不可能出现域值 1/3/5**，且应出现 c1>127（域值 ≥17）。
  ⇒ 判定：**该 RTL 改动没有进入运行中的设计**（不是板子没烧对、也不是测量方法问题）。
- 已核对的证据链：`.gen/…/ipshared/564b/src/alinx_ov5640.v` 含补丁且 mtime `14:11:56` **早于** bit `14:19:45`；BD 只有一个相机 IP，`alinx_ov5640_0/m_axis_video → axis_subset_converter_0/S_AXIS`，转换器 `TDATA_REMAP="tdata[4:0],3'b000,tdata[10:5],2'b00,tdata[15:11],3'b000"`（即输出 MSB 字节 = `{tdata[4:0],000}` = 蓝）。
- 建议排查顺序：
  1. 查该 BD IP 的 OOC 综合是否真读了打过补丁的源：`project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/` 与综合日志中的文件清单/读取路径；
  2. 查工程或 BD 是否引用了**另一份未打补丁的 IP 源**（例如官方 demo 的原路径），或 IP 的 OOC 输出被缓存复用（考虑 `reset_run`/`reset_target`、删除 `.gen` 后重新 `generate_target`）；
  3. 备选实现：在 BD 内以自研 RTL 模块插在 IP 与 `axis_subset_converter_0` 之间做同样的位重建（强制 BD 重建并留下落点证据），或在应用侧对帧缓冲做后处理（注意撕裂与 CPU 性能，且需 cache 维护）；
  4. 若确认是模块/传感器硬件缺陷且无备件，可将其记为**已知硬件限制**并把“实时直通 + 正确色序”作为第一版验收，暖色偏作为已知偏差。

### 2.4 修复生效的验收判据

- DDR 帧缓冲蓝值分布变为：**≤127 的值全部为 16 的倍数，且出现 >127 的值**，`maxB > 127`；
- 再由 Wong 目视确认“不偏黄、也不偏青”（避免过冲）；
- 证据需含：位流/XSA SHA-256、时序/DRC、落点或直方图证据、命令与真实退出码。

## 3. 关键事实与入口

### 3.1 环境

- 器件 `XC7Z020-2CLG400I`（Vivado part `xc7z020clg400-2`）；Vivado 2026.1 Tcl；JTAG `xsdb.bat`；软件侧走 HSI+make（XSCT 禁用）。
- BASIC 许可 `D:\Xilinx_licenses\basic_only.lic` 需按进程注入 `XILINXD_LICENSE_FILE`；**不支持 `create_debug_core`（12-29205）⇒ 无 ILA 波形**。
- 本机 16 GB：**同一时刻只跑一个重型综合/实现**；`TEMP/TMP=D:\tmp`。

### 3.2 关键寄存器地址与配置（PS 侧）

`axi_vdma_1` S2MM `0x43010000`（CR +0x30 / SR +0x34）、`axi_vdma_0` MM2S `0x43000000`、`cmos_rst` `0x41200000`、`v_tc` `0x43C00000`、`axi_dynclk` `0x43C10000`；IIC `0xE0004000`。
帧缓冲 base `0x00110C00`、行 stride `0x0F00`（3840 B）、VSIZE `0x02D0`（720）、3 B/像素。

### 3.3 复现命令（Git Bash）

```bash
bash scripts/stage3_t04/run_t04_camera_j11_cmos2_build.sh <新run名>          # SOF 修复变体
bash scripts/stage3_t04/run_t04_camera_j11cmos2_bluefix_build.sh <新run名>   # SOF + 蓝位重建
bash scripts/stage3_t04/run_t04_camera_j10_cmos2_build.sh <新run名>          # J10 + 官方 cmos2 映射
bash scripts/stage3_t05/run_t05_board_capture.sh <run_dir> <elf> <tag> 120   # 抓UART + JTAG 下载 + 只读探测
bash scripts/stage3_t03b/run_xsdb.sh D:/codex-worktrees/dbdf/scripts/stage3_t05/jtag_dump_rows3.tcl D:/codex-worktrees/dbdf/tmp/3/S3-CTRL/t05_live_r01
```
- 运行目录必须不存在（脚本拒绝覆盖）；重跑一律新 RunId；`*.log` 被 gitignore，关键日志另存 `.txt`。
- **工具红线**：对**运行中**的 A9 直接 `mrd` 会触发 “Timeout waiting for the Instruction Complete bit” 并把 DAP 打成 `APB AP transaction error 0x30000021`；恢复 = `targets -set *DAP*` → `rst -type system`（**清 PL 配置，需重下比特流**）。只读一律 `stop` → `mrd` → `con`。

### 3.4 证据索引（`report/evidence/S3-T05/`）

| 目录 | 内容 |
|---|---|
| `t05_ctrl_20261020_r01/` | 开工核验、J11 引脚 16 信号核对表、工具事件记录 |
| `t05_board_diag5_20261020_r01/` | v5 上板：SR 判读、fsync A/B、cache 语义更正 |
| `t05_monitor_20261020_r01/` | 显示器照片（含 SHA-256）与冻结帧假设的撤回 |
| `t05_sof_fix_20261020_r01/` | SOF 修复补丁、构建报告 |
| `t05_v6_board_20261020_r01/` | **实时性判定**（15/15 指纹不同）、彩条照片与判读 |
| `t05_color_analysis_20261020_r01/` | 按 DDR 字节测的 8 条彩条三元组（`row360.bin`） |
| `t05_v7_board_20261020_r01/` | AWB 寄存器回读 + AWB 开/关 A/B（AWB 排除） |
| `t05_bluebit_20261020_r01/` | 增益补不回丢位（反证）+ 四路映射复核 |
| `t05_j10_cmos2_20261020_r01/` | J10 变体构建 + 落点 16/16 + 阴性对照 |
| `t05_j10_board_20261020_r01/` | **J10 交叉验证结论**（蓝仍锁 120 ⇒ 模块侧） |
| `t05_bluefix_20261020_r01/` | 蓝位重建补丁与构建（**未生效**，含顺序可交换实测） |
| `t05_github_ref_20261020_r01/` | 社区工程外部对照（顺序/拼装/寄存器表一致） |
| `t05_sw_v7/v8_20261020_r01/` | v7/v8 应用补丁、ELF、构建证据 |

## 4. 边界与红线（接手方必须遵守）

- 只写 `D:\codex-worktrees\dbdf`；`D:\FPGA_Competition` 与 `D:\FPGA\AX7Z020` 只读；**不得写两个 mailbox 目录**（`codex_mailbox/` 只 Codex 项目总控写、`dsh_mailbox/` 只 DSH 项目总控写）。
- 不烧 QSPI／不写非易失、不改接线、不做电气测量、不做不可逆操作；传感器寄存器改动保持易失。
- 同一时刻只跑一个重型综合/实现；动手前核对既有 Vivado/xsim 进程与 2B 硬件会话（`hw_server`）。
- 提交串行、只提交本轮相关文件；不 `rebase`/`reset`/`clean` 对方工作；不自动推送。
- 修改前先读 `.codex/STATE.md` 与 `AGENTS.md`；接手后请在交接行更新心跳与状态（`CLAIMED`→`IN_PROGRESS`）。

## 5. 可直接粘贴给 Codex 阶段三总控的提示词

```text
你是 Codex 侧的【阶段三总控】。DSH 侧阶段三总控已于 2026-10-21 15:05（UTC+8）把阶段三交接给你，
交接依据是 D:\codex-worktrees\dbdf\.codex\STATE.md 末尾 11 字段交接行的「让出声明=OFFERED」，
以及交接文档 D:\codex-worktrees\dbdf\report\evidence\S3-CTRL\S3-T05\S3CTRL-20261021-002-handoff-to-codex-stage3.md
（两者请先完整读一遍，再读 D:\FPGA_Competition\AGENTS.md）。DSH 侧已停止写入该工作树。

【工作树】D:\codex-worktrees\dbdf，分支 codex/stage3-video，交出时 HEAD 402b074（交接文档随后一次提交）。
【接手动作】先核验：工作树/分支/HEAD、git index.lock、重型进程（vivado/xsim）、2B 的 hw_server 会话，
再按 AGENTS.md 的 11 字段交接行把状态从 OFFERED 改为 CLAIMED→IN_PROGRESS 并更新心跳；
不要覆盖或回退既有提交与未跟踪散落件（NA/、clockInfo.txt 保留不动）。

【阶段目标（第一版）】AN5642(OV5640) → 扩展口 → PL 采集/DDR 缓冲 → HDMI → 显示器，原始画面直通，单通道；
不加 CNN/检测框/手势交互。第一版主目标已达成（实时直通 + 色彩通道顺序正确，Wong 已目视确认“跟着动”）。

【唯一技术阻塞（你的第一优先）】RGB565 的 B[4]（蓝最高位）恒为 0：蓝上限 120、任何数据都没有 >127 的蓝像素，
R/G 正常到 248/236，画面偏黄。已排除显示器、AWB/ISP、通道/字节序错位、565→888 扩展；靠增益补不回
（手动 B 增益 3.5× 后仍锁 120）。J10 交叉验证（把 B[4] 对应线换到完全不同的 FPGA 脚 R14）蓝仍锁 120
⇒ 排除板侧 J11/F20，根因在模块 D6 走线/触点或传感器 B4 输出（无第二块模块，未再细分）。

【已构建但“实机未生效”的修复，请先定位原因】变体在厂商 IP 内新增
  wire[15:0] s_axis_tdata_bluefix = {s_axis_tdata[15:5], s_axis_tdata[3:0], s_axis_tdata[3]};
并用于输出 xpm_fifo_async 的 .din（B'[4:0]={B[3:0],B[3]}，只改 bit4 语义），补丁
  board/stage3/software/sensor/alinx_ov5640_blue_msb_rebuild.patch
构建 RunId tmp/s3r06/t04_bluefix_20261020_r01，退出码 0，bit 0819d0da1508cdc43f72d8ab67e8d4173de3ddc656e3fbfa957a72c061c119d7。
已在 J11 实机下载（下载日志+哈希确认烧的就是该 bit），但 DDR 蓝直方图与修复前完全同构
（蓝值仍只有 {0,8,…,120}，且仍出现 5 位域值 1/3/5 —— 补丁生效时这些值不可能出现，且应出现 >127）
⇒ 该 RTL 改动没有进入运行中的设计。建议排查：① 该 BD IP 的 OOC 综合是否真读了打过补丁的源
（查 project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/ 与综合日志文件清单）；
② 工程/BD 是否引用了另一份未打补丁的 IP 源，或 IP 输出被缓存复用（reset_run/reset_target、删 .gen 后重新 generate_target）；
③ 备选：在 BD 内用自研 RTL 模块插在 IP 与 axis_subset_converter_0 之间做同样重建（强制 BD 重建），
或应用侧软件后处理帧缓冲（注意撕裂与 CPU 性能、需 cache 维护）。

【验收判据（修复生效）】DDR 蓝值分布变为「≤127 的值全为 16 的倍数，且出现 >127」，maxB>127；
再由 Wong 目视确认“不偏黄也不偏青”。证据需含位流/XSA SHA-256、时序/DRC、命令与真实退出码、直方图数据。
若确认是模块/传感器硬件缺陷且无备件，可把“实时直通 + 正确色序”作为第一版验收、暖色偏记为已知偏差，但必须在材料中如实标注。

【红线】只写 D:\codex-worktrees\dbdf；D:\FPGA_Competition 与 D:\FPGA\AX7Z020 只读；
不得写两个 mailbox 目录；不烧 QSPI/不写非易失、不改接线、不做电气测量、不做不可逆操作；
同一时刻只跑一个重型综合/实现；动手前核对 2B 的 hw_server；BASIC 许可需按进程注入 XILINXD_LICENSE_FILE
（BASIC 不支持 create_debug_core，故无 ILA）。
【工具红线】对运行中的 A9 直接 mrd 会触发 Timeout 并把 DAP 打成 APB AP transaction error 0x30000021；
恢复 = targets -set *DAP* → rst -type system（会清 PL 配置，需重下比特流）；只读一律 stop → mrd → con。

【恢复命令】
bash scripts/stage3_t05/run_t05_board_capture.sh D:/codex-worktrees/dbdf/tmp/s3r06/t04_bluefix_20261020_r01 \
  D:/codex-worktrees/dbdf/tmp/s3r06/t04_j11cmos2_elf_v8/elf_build/app/an5642_j11cmos2_v8_off.elf bluefix 90
bash scripts/stage3_t03b/run_xsdb.sh D:/codex-worktrees/dbdf/scripts/stage3_t05/jtag_dump_rows3.tcl \
  D:/codex-worktrees/dbdf/tmp/3/S3-CTRL/t05_live_r01

完成后请更新 .codex/STATE.md（心跳、状态、证据入口、下一步），并保持交接行语义与 AGENTS.md 一致。
```