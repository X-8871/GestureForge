# 阶段3 状态（AN5642 原始视频链路）

更新：2026-10-21 19:39（UTC+8）。工作树 `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`。
规则见 `D:\FPGA_Competition\AGENTS.md`。**Codex 阶段三总控已完成 OFFERED→CLAIMED→IN_PROGRESS；基线 `d476df8db21614df35bb3ccb11843b1beca88212`，接管核验无 index.lock、重型任务或 hw_server/3121 监听；仅保留原有 NA/、clockInfo.txt。当前定位 OOC 实际输入及蓝位重建数据路径。**

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
- **当前下一步**：以官方资料检查 DVP 字节 MSB／`cmos_d[9]` 的输出使能、数据选择、位序及采样连接；区分传感器配置、RTL/采样与物理链路，暂不判硬件损坏。当前 UART 实机回读 `0x4300=0x60`、`0x501F=0x01`，与 RGB565 初始化一致，不能仅凭伪彩转判 Bayer/RAW 或 YUV，也不再盲调 AWB。不改接线、不测电气。
- **验收判据**：数值重建分布只证明实验补丁生效，不证明真彩；仍须实际缺位根因与正确颜色证据、Wong 目视“不偏黄也不偏青”及适用耐久/时序验收，不能降低标准。

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
- S2MM 旧轮记录清 sticky 后 20 s 无复现；本轮 UART 仍见粘滞错误 `0x00015810`（INT + FSZ_MORE/SOFLate + ErrIrq），不能宣称当前全程无错，需单独验证。
- `CRITICAL WARNING [Timing 38-249]`（rgb2dvi SerialClk 与 PIX_CLK 未声明 ×5 关系）仍在：DRC 0 error、时序为正，但不等价于完整 I/O 时序签核。
- J10 目视“上半黑、下半黄白”**未定性**（J10 约束与官方 XDC 16/16 一致，非映射错）。
- 未做耐久/长时间测试、未做色卡或仪器测量、未烧 QSPI、未改接线；所有传感器寄存器改动均为易失。
- 跨方：`codex_mailbox/CDX-20261020-003` 无回执；本树已发 `S3CTRL-20261020-001`、`S3CTRL-20261021-002`。**不得写两个 mailbox 目录**。

## 未提交改动归属（接手声明，不覆盖不回退）
- 本阶段已提交（分支 `codex/stage3-video`，**未 push**）：`ea16e32 e9b853f cdde845 cb389a3 3cba2c3 354a737 d1dd2d9 e7fe2c9 fbcfc1e fe5177d f2345c3 1b437e3 c51b593 402b074`。
- 未跟踪散落件：`NA/`、`clockInfo.txt`（旧轮、非本阶段产物，保留不动）；`tmp/**` 为构建缓存，不入提交。

## 交接行（11 字段，2026-10-21 15:05）
任务=`S3-T05 阶段3：实时直通成立；近似重建目视失败，定位 DVP MSB 缺失` | 负责人=`Codex 阶段三总控` | 工作树/分支=`D:\codex-worktrees\dbdf`/`codex/stage3-video` | 起始提交=`d476df8db21614df35bb3ccb11843b1beca88212` | 允许修改范围=`board/stage3/**`、`scripts/stage3_t03b/**`、`scripts/stage3_t04/**`、`scripts/stage3_t05/**`、`report/evidence/S3-T05/**`、`report/evidence/S3-CTRL/**`、`.codex/STATE.md` | 未提交改动归属=`NA/、clockInfo.txt 为原有散落件保留不动；本轮 STATE 及范围内变更归 Codex；tmp/** 不入提交` | 让出声明=`DSH 于 2026-10-21 15:05 OFFERED 并停止写入；Codex 于 18:28 核验后 CLAIMED→IN_PROGRESS，写权独占` | 心跳(UTC+8)=`2026-10-21 19:39` | 证据入口=`report/evidence/S3-T05/t05_display_bluefix_board_20261021_r01/README.md`；`report/evidence/S3-T05/t05_codex_g2_20261021_r01/` | 恢复命令=`先读本轮 README 与 visual_result.json，候选已完成构建/易失上板，禁止重复启动；近似补偿位流仍有伪彩，不冻结。继续只读官方格式/DVP 资料和 cmos_d[9] 路径核查；任何后续板测先核对 2B hw_server，A9 读取先 stop 后 mrd 最后 con` | 状态/下一接手方=`IN_PROGRESS / Codex 阶段三总控`
