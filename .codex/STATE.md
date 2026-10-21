# 阶段3 状态（AN5642 原始视频链路）

更新：2026-10-21 15:05（UTC+8）。工作树 `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`。
规则见 `D:\FPGA_Competition\AGENTS.md`。**本文件末尾交接行为 `OFFERED`：本树写权让出给 Codex 阶段三总控接手。**

## 目标与第一版范围
- 第一版：AN5642(OV5640) → 扩展口 → PL 采集/DDR 缓冲 → HDMI → 显示器【原始画面直通】，单通道；不加 CNN/检测框/手势交互。
- **第一版主目标已达成**（实物实时画面 + 色彩通道顺序正确）；唯一遗留技术问题 = 蓝通道缺位（见“当前唯一技术阻塞”）。

## 器件与环境（现行事实）
- 器件 XC7Z020-2CLG400I，Vivado part `xc7z020clg400-2`；Vivado 2026.1 Tcl；JTAG 用 `xsdb.bat`；XSCT 禁用（软件侧 HSI+make）。
- BASIC 许可 `D:\Xilinx_licenses\basic_only.lic` 须按进程注入 `XILINXD_LICENSE_FILE`；BASIC **不支持** `create_debug_core`（Vivado 12-29205）⇒ **无 ILA 波形**。
- 本机 16 GB：同一时刻只跑一个重型综合/实现；`TEMP/TMP=D:\tmp`；板块硬件会话（2B）与本树互斥，动手前先看进程。

## 已完成（可复现事实）
- **S3-T03b HDMI**：官方 `14_vdma_hdmi_out` 重建到比特流、实物启动成功；bit `7143427f…`、XSA `02174319…`；证据 `report/evidence/S3-T03/t03b_hdmi_build_20261020_r01/`。
- **S3-T04/T05 采集直通 + 帧同步修复**：厂商 IP `alinx_ov5640.v` 的 `s_axis_tuser` 由“`cmos_vsync` 下降沿”改为“hblank 连续低 ≥ `GAP_THRESH=16384` pclk 后的第一个有效像素”。补丁 `board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch`；位流 `7cb33068…8710`、XSA `1f5b138e…cb0e3`（WNS 1.0545、DRC 0 error）。
- **实物实时直通成立**（Wong 目视“跟着动”）：v6 指纹（3 处 × 64 KB，`sum32+CRC-32`，读前 `Xil_DCacheInvalidateRange`）在 t≈5/10/15/20/25 s **15/15 互不相同**；传感器 `0x4202=0x00` 在流。证据 `…/t05_v6_board_20261020_r01/`、画面照片 `…/t05_monitor_20261020_r01/`。
- **模块/通道事实**：CMOS1 通道无 I2C ACK（两种连接器两次验证）⇒ 模块 CMOS1 侧故障；**CMOS2 通道可用**（模块插 J11）：CHIPID=0x5640、1280×720、VTS=740、PCLK≈84 MHz。
- **引脚映射五路证据一致** ⇒ 映射无误：AX7020 V3.0 手册 Table 7.5.1、官方 `23_ov5640_dual` XDC、原理图网名序列、原理图文字坐标配对、GitHub 社区 AN5642 工程信号顺序（`…/t05_github_ref_20261020_r01/`）。
- **作废的判断**：基于 JTAG 标记法（halt 的 A9 `mwr/mrd`）得出的“冻结单帧 / 帧缓冲全 0 / 显示全黑”结论作废——该法经 CPU 数据 cache，不可作 DDR 内容证据；已改用应用侧 cache 正确判据。

## 当前唯一技术阻塞（交给接手方）
- **现象**：RGB565 的 **B[4]（蓝最高位）恒为 0** ⇒ 蓝上限 120、**无任何 >127 的蓝像素**（4 组独立数据：白纸 / 实景 AWB 开 / 实景 AWB 关 / 彩条），R/G 正常到 248/236，画面偏黄。手动白平衡 B 增益推到 3.5×（`0x0E00`，回读 `match=1,1,1`）**蓝仍锁 120** ⇒ 靠增益补不回。已排除：显示器、AWB/ISP、通道/字节序错位、565→888 扩展。
- **范围**：J10 交叉验证（B[4] 对应线换到完全不同 FPGA 脚 R14）**蓝仍锁 120** ⇒ 排除板侧 J11/F20；根因在**模块 D6（DVP 第二字节 bit4 = B[4] ← `cmos_d[6]`）走线/触点或传感器 B4 输出**（无第二块模块、不做电气测量，未再细分；两条路修法同）。
- **PL 重建位补丁未生效（接手方第一优先）**：task-6 已构建变体——厂商 IP 内加 `wire[15:0] s_axis_tdata_bluefix = {s_axis_tdata[15:5], s_axis_tdata[3:0], s_axis_tdata[3]};` 并用于输出 `xpm_fifo_async` 的 `.din`；bit `0819d0da1508cdc43f72d8ab67e8d4173de3ddc656e3fbfa957a72c061c119d7`、XSA `fed8f652…`（WNS 1.1027、DRC 0 error）。已在 J11 实机下载（下载日志 + 哈希确认烧的就是该 bit），**但 DDR 蓝直方图与修复前完全同构**（蓝值 ∈{0,8,…,120}、含奇数域值 8/24/40…）⇒ **补丁没有进入运行中的设计**。
  建议排查顺序：① 该 BD IP 的 OOC 综合是否真读了打过补丁的源（查 `.runs/design_1_alinx_ov5640_0_0_synth_1/` 与综合日志的文件清单；`.gen/…/ipshared/564b/src/alinx_ov5640.v` 已含补丁且 mtime(14:11:56) 早于 bit(14:19:45)）；② 工程/BD 是否引用了另一份未打补丁的 IP 源（如官方 demo 原路径）；③ 备选：在 BD 内用自研 RTL 模块插在 IP 与 `axis_subset_converter_0` 之间做同样的位重建（强制 BD 重建），或应用侧软件后处理帧缓冲（注意撕裂与 CPU 性能）。
- **验收判据（修复生效）**：DDR 蓝值分布变为「≤127 的值全为 16 的倍数；且出现 >127」且 `maxB > 127`；再由 Wong 目视“不偏黄也不偏青”。

## 可复用命令与工具教训
```bash
bash scripts/stage3_t04/run_t04_camera_j11_cmos2_build.sh <新run名>          # SOF 修复变体
bash scripts/stage3_t04/run_t04_camera_j11cmos2_bluefix_build.sh <新run名>   # SOF + 蓝位重建
bash scripts/stage3_t04/run_t04_camera_j10_cmos2_build.sh <新run名>          # J10 + 官方 cmos2 映射
bash scripts/stage3_t05/run_t05_board_capture.sh <run_dir> <elf> <tag> 120   # 抓UART + JTAG 下载 + 只读探测
bash scripts/stage3_t03b/run_xsdb.sh D:/codex-worktrees/dbdf/scripts/stage3_t05/jtag_dump_rows3.tcl D:/codex-worktrees/dbdf/tmp/3/S3-CTRL/t05_live_r01
```
- 运行目录必须不存在（脚本拒绝覆盖）；重跑一律用新 RunId；`*.log` 被 gitignore，关键日志另存 `.txt`。
- **工具教训**：对**运行中**的 A9 直接 `mrd` 会触发 “Timeout waiting for the Instruction Complete bit” 并把 DAP 打成 `APB AP transaction error 0x30000021`（A9 从目标树消失）；恢复 = `targets -set *DAP*` → `rst -type system`（**会清 PL 配置**，需重下比特流）。只读一律 `stop` → `mrd` → `con`。

## 未关闭的阻碍与风险
- S2MM 启动后一次粘滞错误 `0x00015810`（INT + FSZ_MORE/SOFLate + ErrIrq），清 sticky 后 20 s 内不复现（不影响连续写帧）。
- `CRITICAL WARNING [Timing 38-249]`（rgb2dvi SerialClk 与 PIX_CLK 未声明 ×5 关系）仍在：DRC 0 error、时序为正，但不等价于完整 I/O 时序签核。
- J10 目视“上半黑、下半黄白”**未定性**（J10 约束与官方 XDC 16/16 一致，非映射错）。
- 未做耐久/长时间测试、未做色卡或仪器测量、未烧 QSPI、未改接线；所有传感器寄存器改动均为易失。
- 跨方：`codex_mailbox/CDX-20261020-003` 无回执；本树已发 `S3CTRL-20261020-001`、`S3CTRL-20261021-002`。**不得写两个 mailbox 目录**。

## 未提交改动归属（接手声明，不覆盖不回退）
- 本阶段已提交（分支 `codex/stage3-video`，**未 push**）：`ea16e32 e9b853f cdde845 cb389a3 3cba2c3 354a737 d1dd2d9 e7fe2c9 fbcfc1e fe5177d f2345c3 1b437e3 c51b593 402b074`。
- 未跟踪散落件：`NA/`、`clockInfo.txt`（旧轮、非本阶段产物，保留不动）；`tmp/**` 为构建缓存，不入提交。

## 交接行（11 字段，2026-10-21 15:05）
任务=`S3-T05 阶段3：实时直通已达成；蓝通道 B[4] 缺位（模块侧）待修，且 PL 重建位补丁构建后在实机未生效需定位` | 负责人=`阶段3总控（DSH，本次让出）` | 工作树/分支=`D:\codex-worktrees\dbdf`/`codex/stage3-video` | 起始提交=`41ee5ba`（现 HEAD `402b074`） | 允许修改范围=`board/stage3/**`、`scripts/stage3_t03b/**`、`scripts/stage3_t04/**`、`scripts/stage3_t05/**`、`report/evidence/S3-T05/**`、`report/evidence/S3-CTRL/**`、`.codex/STATE.md` | 未提交改动归属=`本阶段改动已提交；`NA/`、`clockInfo.txt` 非本阶段产物、保留不动；`tmp/**` 不入提交` | 让出声明=`**OFFERED（2026-10-21 15:05）**：本树写权让出给 Codex 阶段三总控；DSH 侧已停止写入（本次提交为最后一次）` | 心跳(UTC+8)=`2026-10-21 15:05` | 证据入口=`report/evidence/S3-T05/`（`t05_v6_board_20261020_r01`、`t05_soffix_board_20261020_r01`、`t05_monitor_20261020_r01`、`t05_sof_fix_20261020_r01`、`t05_color_analysis_20261020_r01`、`t05_v7_board_20261020_r01`、`t05_bluebit_20261020_r01`、`t05_j10_cmos2_20261020_r01`、`t05_j10_board_20261020_r01`、`t05_bluefix_20261020_r01`、`t05_github_ref_20261020_r01`、`t05_sw_v7_20261020_r01`、`t05_sw_v8_20261020_r01`）＋`report/evidence/S3-CTRL/S3-T05/S3CTRL-20261021-002-handoff-to-codex-stage3.md` | 恢复命令=`bash scripts/stage3_t05/run_t05_board_capture.sh D:/codex-worktrees/dbdf/tmp/s3r06/t04_bluefix_20261020_r01 D:/codex-worktrees/dbdf/tmp/s3r06/t04_j11cmos2_elf_v8/elf_build/app/an5642_j11cmos2_v8_off.elf bluefix 90` | 状态/下一接手方=`OFFERED / Codex 阶段三总控`