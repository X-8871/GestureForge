# 阶段3 状态（AN5642 原始视频链路）

更新：2026-10-21 23:35（UTC+8）。工作树 `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`。
规则见 `D:\FPGA_Competition\AGENTS.md`。**状态：暂定冻结（Wong 2026-10-21 23:2x 决定；DSH 阶段三总控持有）。**
**冻结配置**：J11+CMOS2；灰度位流 bit `2f72aaa42936225eb7215bd8f138f68e52c27c3ab31ab236c8a3c15f7669af4f`、XSA `bb71c3f6e15b6f22fd0709373c3910f3dc4682214fb0cd6a9f69330a13eaaa12`；应用 `an5642_j11cmos2_v10_read.elf` = `1457cda4…6073`；补丁 `board/stage3/software/sensor/alinx_ov5640_gray_luma.patch`。板上实测：**真灰**（\|R−G\|=\|G−B\|≈2/255）、**实时**（t=5/15/25 指纹互不相同）、传感器寄存器已恢复。冻结记录 `report/evidence/S3-T05/t05_freeze_20261021_r01/`。
**未关闭**：颜色验收待**更换模块到货后复测**（步骤见冻结记录 §5）；task-11 网表交叉核对未完成（补丁已人工逐行审阅）；VDMA 粘滞 `0x00015810`；方法学 TIMING-17/36 与 I/O delay 缺口；J10 半屏未定性；无 ILA；未做 ≥30 min 耐久。**根因**：模块侧 DVP 字节 MSB 线 `cmos_d[9]` 无信号（配置/RTL/映射/FPGA 引脚/场景均已排除）⇒ 真修 = 硬件返修/更换。

## 目标与第一版范围
- 第一版：AN5642(OV5640) → 扩展口 → PL 采集/DDR 缓冲 → HDMI → 显示器【原始画面直通】，单通道；不加 CNN/检测框/手势交互。
- **实时直通已成立，色彩验收未通过，阶段未冻结**；显示通道映射已核对，但缺位及近似补偿伪彩仍阻断颜色验收。

## 器件与环境（现行事实）
- 器件 XC7Z020-2CLG400I，Vivado part `xc7z020clg400-2`；Vivado 2026.1 Tcl；JTAG 用 `xsdb.bat`；XSCT 禁用（软件侧 HSI+make）。
- BASIC 许可 `D:\Xilinx_licenses\basic_only.lic` 须按进程注入 `XILINXD_LICENSE_FILE`；BASIC **不支持** `create_debug_core`（Vivado 12-29205）⇒ **无 ILA 波形**。
- 本机 16 GB：同一时刻只跑一个重型综合/实现；`TEMP/TMP=D:\tmp`；板块硬件会话（2B）与本树互斥，动手前先看进程。

## 已完成（可复现事实）
- **S3-T03b HDMI**：官方 `14_vdma_hdmi_out` 重建到比特流、实物启动成功；bit `7143427f…`、XSA `02174319…`；证据 `report/evidence/S3-T03/t03b_hdmi_build_20261020_r01/`。
- **S3-T04/T05 采集直通 + 帧同步修复**：厂商 IP `alinx_ov5640.v` 的 `s_axis_tuser` 由“`cmos_vsync` 下降沿”改为“hblank 连续低 ≥ `GAP_THRESH=16384` pclk 后的第一个有效像素”。补丁 `board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch`；位流 `7cb33068…8710`、XSA `1f5b138e…cb0e3`（WNS 1.0545、DRC 0 error）。
- **实物实时直通成立**（Wong 目视“跟着动”）：v6 指纹（3 处 × 64 KB，`sum32+CRC-32`，读前 `Xil_DCacheInvalidateRange`）在 t≈5/10/15/20/25 s **15/15 互不相同**；传感器 `0x4202=0x00` 在流。证据 `…/t05_v6_board_20261020_r01/`、画面照片 `…/t05_monitor_20261020_r01/`。
- **模块/通道事实**：CMOS1 通道在两种连接器两次验证中无 I2C ACK，尚不足以单独判定模块物理故障；**CMOS2 当前能采集出图**（模块插 J11）：CHIPID=0x5640、1280×720、VTS=740、PCLK≈84 MHz，但颜色仍未通过。
- **引脚映射五路证据一致** ⇒ 映射无误：AX7020 V3.0 手册 Table 7.5.1、官方 `23_ov5640_dual` XDC、原理图网名序列、原理图文字坐标配对、GitHub 社区 AN5642 工程信号顺序（`…/t05_github_ref_20261020_r01/`）。
- **作废的判断**：基于 JTAG 标记法（halt 的 A9 `mwr/mrd`）得出的“冻结单帧 / 帧缓冲全 0 / 显示全黑”结论作废——该法经 CPU 数据 cache，不可作 DDR 内容证据；已改用应用侧 cache 正确判据。

## 当前唯一技术阻塞（交给接手方）
- **原始现象**：未重建显示蓝时，RGB565 的 B[4] 在既有四组样本（白纸 / 实景 AWB 开 / 实景 AWB 关 / 彩条）中全为 0，蓝上限 120、无 >127 蓝像素，画面偏黄。R 最大 248、G 最大 236，但 G 同时缺 bit4，不能称绿色正常。旧轮手动 B 增益 3.5× 后仍锁 120，说明该增益操作未补回缺位；这不完整排除 ISP/格式/采样配置。通道映射已有源码、网表与样本互证，物理链路根因尚未确认。
- **2026-10-21 归因纠正**：J10/J11 都有偏黄，但共有 RTL/格式处理没有被排除，不能据此证明模块硬件故障。转换器与 HDMI 网表显示 DDR offset0（蓝）来自输入字 `[15:11]`；蓝 bit7 与绿色缺失的 bit4 都对应 DVP 字节 MSB／`cmos_d[9]`，不是旧记载的 D6。根因仍待定位，不改接线、不测电气。
- **2026-10-21 OOC 排查完成**：旧 bit `0819d0da…19d7` 的 OOC 确实综合补丁源；RAM 写端保留完整重建连接。旧补丁作用低 5 位，实际改变显示红（DDR offset2），不是显示蓝。旧三个行样本 offset2 恰为重建后的 16 档数值，推翻“未进入运行设计”结论；旧产物保留。证据 `report/evidence/S3-CTRL/S3-T05/t05_takeover_20261021_r02/`（checker 0）。
- **本轮构建/上板已完成**：65,536 词穷举、独立 G2、安全转储替身测试通过。运行 `tmp/s3r06/t04_display_bluefix_20261021_r01` 实现退出 0，bit `0f3b74e4…b61d`、XSA `b9a56572…f17`，WNS 1.249946 ns、WHS 0.006289 ns、DRC 0 error；实际易失下载/传感器 ID/15 个变化指纹/安全转储通过，maxB=248，近似重建数值字母表匹配。证据 `report/evidence/S3-T05/t05_display_bluefix_20261021_r01/` 与 `t05_display_bluefix_board_20261021_r01/`。
- **目视失败**：Wong 确认实时正常，但阴影偏蓝、白色亮部偏黄；照片呈大片黄与紫蓝伪彩。近似拉伸低 4 位不能区分原本相差最高位的两种强度，不能作为恢复真彩的修复。机读重建判据 PASS 不等于 G3/G4/G5，旧补偿位流仅保留为失败实验，不冻结。
- **2026-10-21 DSH 复核（新增签名证据，只读、未上板）**：用**已有 19 个行样本**（J11+J10、AWB 开/关、手动增益 B=3.5×、传感器彩条、白纸、暗行，共 24,320 像素）统计：**蓝 8 位 bit7 置位率 0.000%、绿 8 位 bit4 置位率 0.000%**，全部样本无一例外。二者分别来自 DVP 两个字节各自的 MSB，而两字节 MSB 在厂商 IP 里走**同一条 `cmos_d[9]`** ⇒ **该线无信号**是唯一能同时解释两个缺位的单一故障（也解释了为何只补蓝一位的近似补偿必然出伪彩：绿的一位同样丢失，且猜位在低蓝/暗部产生 ±128 跳变）。证据 `report/evidence/S3-T05/t05_msb_line_diagnosis_20261021_r01/`（脚本 `scripts/stage3_t05/analyze_missing_msb_signature.py`，判定 exit 0）。
- **2026-10-21 v9 上板（配置侧排除，关键否定结论）**：干净基线（SOF 修复 `7cb33068…8710`）+ `v9_read.elf`（`b2e8fa55…97b5`）回读：`0x3017=0xFF`、`0x3018=0xFF`（D 脚**输出使能全开**）、**`0x301D=0x00`、`0x301E=0x00`（D[9:0] output select = 正常数据通路，不是寄存器固定值）**、`0x4741=0x00`、`0x4745=0x00`（测试图案与位序均默认）；且这四个寄存器**不在厂商 init 表内**、保持 POR 默认 ⇒ **「软件/配置把该线覆盖成固定值」的假设排除**。同轮在干净基线下按已核实的 `FRAME0=0x00110C00` 安全转储 3 行（halt→dump→resume 正常），蓝 bit7 / 绿 bit4 置位率仍 **0.000% / 0.000%**。证据 `report/evidence/S3-T05/t05_v9_board_20261021_r01/`。
- **当前下一步**：① **硬件路径（唯一根治）**：厂家返修/更换（只寄模块、不寄 AX7020 板卡；沟通材料 `S3CTRL-20261021-002` + Wong 手上 ALINX 返修单）；可先做免费尝试——**断电后重插模块并目视 J3 pin3（CMOS2_D9）有无弯针/氧化**（本树不改接线，仅建议）。② **可选、非必需**：`v9_orderdbg`（改 `0x4745` 调试位序）可再区分「传感器该脚未输出」与「模块走线断」，但两者修法相同（都在模块侧），且会打乱输出且不自动恢复 ⇒ **建议不做**，仅留档备用。③ **明示的过渡手段（不构成修复）**：若作品需要更好观感，可做「双位重建 + 平滑滤波」补偿位流，材料中必须标注「近似补偿、非真实修复、不用于颜色验收」——**是否做由 Wong 决策**。④ **颜色验收在硬件修复前保持受阻/FAIL**；实时性、帧同步修复、映射与 VDMA 基本功能均已单独成立。
- **验收判据**：数值重建分布只证明实验补丁生效，不证明真彩；仍须实际缺位根因与正确颜色证据、Wong 目视“不偏黄也不偏青”及适用耐久/时序验收，不能降低标准。

## 可复用命令与工具教训
```bash
bash scripts/stage3_t04/run_t04_camera_j11_cmos2_build.sh <新run名>          # SOF 修复变体
bash scripts/stage3_t04/run_t04_camera_j11cmos2_bluefix_build.sh <新run名>   # SOF + 蓝位重建
bash scripts/stage3_t04/run_t04_camera_j10_cmos2_build.sh <新run名>          # J10 + 官方 cmos2 映射
bash scripts/stage3_t05/run_t05_board_capture.sh <run_dir> <elf> <tag> 120   # 抓UART + JTAG 下载 + 只读探测
# 读取前核实当前 ELF 的 FRAME0/stride，并手动创建全新、空的输出目录；再使用已审安全脚本：
bash scripts/stage3_t03b/run_xsdb.sh D:/codex-worktrees/dbdf/scripts/stage3_t05/jtag_dump_display_channels.tcl <新建空输出目录>
```
- 重跑一律用新 RunId；调用方先核对新输出目录不存在，安全转储则要求手动创建的新空目录。不是所有旧脚本都防覆盖，`run_t05_board_capture.sh` 使用 `mkdir -p`，不能原样复用旧 tag；`*.log` 被 gitignore，关键日志另存 `.txt`。
- **禁止原样执行历史 `jtag_dump_rows3.tcl`**：该旧脚本暂停失败后仍可能读内存，恢复失败也不能可靠报告非零；仅保留历史，不作为接续工具。
- **工具教训**：对**运行中**的 A9 直接 `mrd` 会触发 “Timeout waiting for the Instruction Complete bit” 并把 DAP 打成 `APB AP transaction error 0x30000021`（A9 从目标树消失）；恢复 = `targets -set *DAP*` → `rst -type system`（**会清 PL 配置**，需重下比特流）。只读一律 `stop` → `mrd` → `con`。

## 未关闭的阻碍与风险
- S2MM 旧轮记录清 sticky 后 20 s 无复现；本轮 UART 仍见粘滞错误 `0x00015810`（INT + FSZ_MORE/SOFLate + ErrIrq），不能宣称当前全程无错，需单独验证。
- `CRITICAL WARNING [Timing 38-249]`（rgb2dvi SerialClk 与 PIX_CLK 未声明 ×5 关系）仍在：DRC 0 error、时序为正，但不等价于完整 I/O 时序签核。
- J10 目视“上半黑、下半黄白”**未定性**（J10 约束与官方 XDC 16/16 一致，非映射错）。
- 未做耐久/长时间测试、未做色卡或仪器测量、未烧 QSPI、未改接线；所有传感器寄存器改动均为易失。
- 跨方：`codex_mailbox/CDX-20261020-003` 无回执；本树已发 `S3CTRL-20261020-001`、`S3CTRL-20261021-002`。**不得写两个 mailbox 目录**。

## 未提交改动归属（接手声明，不覆盖不回退）
- 本阶段已提交（分支 `codex/stage3-video`，**未 push**）：`ea16e32 e9b853f cdde845 cb389a3 3cba2c3 354a737 d1dd2d9 e7fe2c9 fbcfc1e fe5177d f2345c3 1b437e3 c51b593 402b074 d476df8 0d47801`；本交接文件另作提交，接手时以实际 HEAD 核验。
- 未跟踪散落件：`NA/`、`clockInfo.txt`（旧轮、非本阶段产物，保留不动）；`tmp/**` 为构建缓存，不入提交。

## 交接行（11 字段，2026-10-21 19:53）
任务=`S3-T05 阶段3：修复 DVP 字节 MSB 无信号（单线 cmos_d[9]）造成的色彩缺失，并完成适用验收` | 负责人=`DSH 阶段三总控` | 工作树/分支=`D:\codex-worktrees\dbdf`/`codex/stage3-video` | 起始提交=`0d47801266a96c950d025702c158734f9bbd25de`（HEAD 以实际核验为准） | 允许修改范围=`board/stage3/**`、`scripts/stage3_t03b/**`、`scripts/stage3_t04/**`、`scripts/stage3_t05/**`、`report/evidence/S3-T05/**`、`report/evidence/S3-CTRL/**`、`.codex/STATE.md` | 未提交改动归属=`NA/`、`clockInfo.txt` 为旧轮散落件、保留不动；`tmp/**` 为构建缓存不入提交；本轮新增证据与 STATE 由 DSH 提交` | 让出声明=`已认领：Codex 于 2026-10-21 19:53 OFFERED，DSH 于 2026-10-21 21:47 CLAIMED→IN_PROGRESS 并独占写入；当前无让出` | 心跳(UTC+8)=`2026-10-21 23:35` | 证据入口=`report/evidence/S3-T05/t05_freeze_20261021_r01/`（冻结记录）、`…/t05_gray_board_20261021_r01/`（板上实测：中性度+实时）、`…/t05_msb_line_diagnosis_20261021_r01/`、`…/t05_v9_board_20261021_r01/` | 恢复命令=`模块到货后按 t05_freeze_20261021_r01/README.md §5 复测颜色：刷回无补偿基线 + v9_read → 安全转储 3 行 → analyze_missing_msb_signature.py 应判“不符合签名”(=修好) → 彩条判色相 → 白纸不发黄` | 状态/下一接手方=`DONE（暂定冻结；颜色项待模块到货复测，重开需按新任务卡）`
