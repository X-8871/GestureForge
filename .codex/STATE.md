# 阶段3 状态（AN5642 原始视频链路）

更新：2026-10-20 12:40（UTC+8）。工作树 `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`。
规则见 `D:\FPGA_Competition\AGENTS.md`；本文件只记阶段技术事实，不复制主 STATE。

## 目标与第一版范围

- 第一版：AN5642(OV5640) → 扩展口 → PL 采集/DDR 缓冲 → HDMI → 显示器【原始画面直通】，先单通道；不加 CNN/检测框/手势交互。
- 路线：T01/T02 资料（旧轮）→ T03 HDMI 独立画面 ✔ → T04/T05 采集直通（进行中）→ T06 耐久/证据包（可选）。

## 器件与环境（现行事实）

- 器件 **XC7Z020-2CLG400I**，Vivado part `xc7z020clg400-2`（丝印 XA7Z020，JTAG 名 `xc7z020`；-1/-2 时序签核未关闭）。
- BASIC 许可 `D:\Xilinx_licenses\basic_only.lic` 必须按进程注入 `XILINXD_LICENSE_FILE`。**BASIC 不支持 `create_debug_core`（Vivado 12-29205）**，也不支持 >5 探针 ILA。
- Vivado 2026.1 Tcl 模式；XSCT 禁用（软件侧走 HSI+make）；JTAG 用 Tcl 版 `xsdb.bat`。本机 16 GB，同时只跑一个重型综合/实现；`TEMP/TMP=D:\tmp`。

## 已完成（S3-T03b HDMI）

- 官方 `14_vdma_hdmi_out` 重建到比特流并在实物 JTAG 启动成功；WNS 1.2925、DRC 0 error；bitstream `7143427f…50d7f`、XSA `02174319…7b96c`、ELF `f6686cd7…6aa9f`。
- dynclk RUNNING/LOCK=0x7E8FA401、VDMA CR/SR、v_tc 回读正常。证据 `report/evidence/S3-T03/t03b_hdmi_build_20261020_r01/`。

## 已完成（S3-T04/T05 采集直通）

- 官方 `22_ov5640_single`、J11 变体、J11+CMOS2 变体均在 `xc7z020clg400-2` 构建到比特流/XSA（时序为正、DRC 0 error）。
- 通道事实：**CMOS1 无 I2C ACK**（J10 官方映射与 J11 自制映射两次独立验证）→ 判为模块 CMOS1 侧故障；**CMOS2（模块插 J11）可用**：CHIPID=0x5640、1280×720、VTS=740、PCLK≈84 MHz。
- **S3-T05 关键更正（2026-10-20 12:3x，证据 `report/evidence/S3-T05/t05_board_diag5_20261020_r01/`）**：
  1. 传感器在流（`0x4202=0x00`、`0x4740=0x20`、`0x503D=0x00`）；
  2. **帧缓冲有真实且随时间变化的图像数据**（v5 修 cache 语义后的 UART 读数 + JTAG 直读物理 DDR 互相印证）；
  3. 旧结论“S2MM 没写数据/帧缓冲全 0/因此显示全黑”**不成立**：零值是 v4 应用“memset 后未做 cache 维护”的 CPU 视角假象；
  4. **唯一确定缺陷是帧同步**：S2MM SR 恒为 `bit4 INT + bit11 FSZ_MORE/SOFLate + ErrIrq`（Halted=0），即数据/TLAST 在流但 **TUSER(SOF) 从未被认出**；在线把 CR 的 FSYNC_SRC 由 `00` 改 `10`（显式 tuser）**无改善**，软件侧改 fsync 源无效；
  5. 厂商 IP 的 SOF 只在 `cmos_vsync` 下降沿产生（`alinx_ov5640.v` 140–143），而 HREF/PCLK/数据都通 → **疑似该路 VSYNC 未到达 IP**（未用 ILA 直接观测）。
- J11-CMOS2 引脚映射已**独立核验正确**：AX7020 V3.0 手册 Table 7.5.1（PDF p.29–31）逐针比对 16 个信号，全部一致（pclk=K19、vsync=J19、href=H18、sda=F16、scl=F19…），并与官方 `23_ov5640_dual` XDC 的 cmos2 顺序、模块原理图网络名三方一致。记录 `report/evidence/S3-T05/t05_ctrl_20261020_r01/verification_record.md`。

## 已完成（S3-T05 实时直通，2026-10-20 12:3x–13:2x）

- **SOF 修复变体**：厂商 IP `alinx_ov5640.v` 的 `s_axis_tuser` 由“`cmos_vsync` 下降沿”改为“hblank 连续低 ≥ `GAP_THRESH=16384` pclk 后的第一个有效像素”（16 位饱和计数器；行间隙 612 pclk < 阈值 < 场间隙 38452 pclk）。补丁 `board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch`；位流 `7cb33068…8710`、XSA `1f5b138e…cb0e3`（WNS 1.0545、DRC 0 error）。
- **实物实时画面成立**：Wong 接 HDMI 显示器出图；v6 指纹诊断（3 处 × 64 KB，`sum32+CRC-32`，读前 `Xil_DCacheInvalidateRange`）在 t≈5/10/15/20/25 s 的 **15/15 指纹互不相同** ⇒ S2MM 在持续写帧；传感器 `0x4202=0x00` 仍在流。证据 `report/evidence/S3-T05/t05_v6_board_20261020_r01/`、画面照片 `…/t05_monitor_20261020_r01/`（原始字节 `fb3359c6…8a095`）。
- **作废的判断**：基于 JTAG 标记法（halt 的 A9 `mwr/mrd`）得出的“冻结单帧/缓冲全 0”结论作废——该方法经 CPU 数据 cache，不可作为 DDR 内容证据；已在证据中如实记录并改用应用侧 cache 正确判据。
- 仍存在（不影响直通）：S2MM SR 启动后一次粘滞错误 `0x00015810`（INT+FSZ_MORE/SOFLate+ErrIrq），清 sticky 后 20 s 内不复现；偏色（Wong 反馈“偏黄”）**未归因**，彩条版 ELF（`503D=0x80`）已上板待判读。

## 可复用命令（Git Bash）

```bash
bash scripts/stage3_t04/run_t04_camera_j11_cmos2_build.sh <新run名>          # J11+CMOS2 构建
bash scripts/stage3_t05/run_t05_board_capture.sh <run_dir> <elf> <tag> 120   # 抓UART+JTAG下载+只读探测
bash scripts/stage3_t03b/run_xsdb.sh D:/codex-worktrees/dbdf/scripts/stage3_t05/jtag_read_safe.tcl
bash scripts/stage3_t03b/run_xsdb.sh D:/codex-worktrees/dbdf/scripts/stage3_t05/jtag_s2mm_fsync_ab.tcl
```
运行目录必须不存在（脚本拒绝覆盖）；重跑一律用新 RunId。
**工具教训（2026-10-20 12:0x）**：对**运行中**的 A9 直接 `mrd` 会触发 “Timeout waiting for the Instruction Complete bit” 并把 DAP 打成 `APB AP transaction error 0x30000021`（APU/A9 从目标树消失）；恢复 = `targets -set *DAP*` → `rst -type system`（**会清 PL 配置**，需重下比特流）。只读探测一律先 `stop` → `mrd` → `con`。

## 未提交改动归属（接手声明，不覆盖不回退）

- 旧轮 9 项未提交改动已由上一窗口提交。本轮未跟踪散落件：`NA/`、`clockInfo.txt`（非本轮产物，保留在工作区不动）。
- 本轮新增未跟踪：`tmp/**`（构建缓存/临时产物，不入提交）。

## 未关闭的阻碍与风险

- **颜色未判读**：Wong 反馈画面“偏黄”；彩条测试图已上板，**待 Wong 目视/拍照判读**（标准 8 条顺序是否正确）以区分“场景/AWB 偏暖”与“通道/打包错位”。
- 启动瞬间一次粘滞错误（见上）；`CRITICAL WARNING [Timing 38-249]`（rgb2dvi SerialClk 与 PIX_CLK 未声明 ×5 关系）仍在：DRC 0 error、时序为正，但不等价于完整 I/O 时序签核。
- 未做耐久/长时间测试；未做色卡或仪器测量；未烧 QSPI。
- 与 2B 硬件互斥：本轮全程现场**无 hw_server/vivado/xsim 进程**（2B 未占用）；跨方请求 `codex_mailbox/CDX-20261020-003` 仍无回执；本树已发 `S3CTRL-20261020-001`，只用自起自停的 xsdb/hw_server。
- ILA 路线受阻：BASIC 许可不支持 `create_debug_core`（Vivado 12-29205）；**未取得任何 ILA 波形**（VSYNC/TUSER 只有行为证据）。

## 下一步

- **等 Wong 判读彩条颜色**（屏幕上现在应是测试图）→ 决定是否需要修通道/打包或只调 AWB；随后做一次普通 ELF 的挥手实时确认与（可选）双通道。
- 恢复入口：`git -C D:/codex-worktrees/dbdf status --short`；证据入口 `report/evidence/S3-T05/`。

## 交接行（11 字段，2026-10-20 13:25）

任务=`S3-T05 阶段3 视频直通：帧同步修复 + 实物实时画面达成 + 颜色判读待办` | 负责人=`阶段3总控（新会话）` | 工作树/分支=`D:\codex-worktrees\dbdf`/`codex/stage3-video` | 起始提交=`41ee5ba` | 允许修改范围=`board/stage3/**`、`scripts/stage3_t04/**`、`scripts/stage3_t05/**`、`report/evidence/S3-T05/**`、`report/evidence/S3-CTRL/**`、`.codex/STATE.md` | 未提交改动归属=`本轮已分批提交：ea16e32/e9b853f/cdde845/cb389a3/3cba2c3/354a737/d1dd2d9；`NA/`、`clockInfo.txt` 为旧散落件、非本轮产物` | 让出声明=`未让出（本树写权仍归阶段3总控）` | 心跳(UTC+8)=`2026-10-20 13:25` | 证据入口=`report/evidence/S3-T05/t05_v6_board_20261020_r01/`、`…/t05_soffix_board_20261020_r01/`、`…/t05_monitor_20261020_r01/`、`…/t05_sof_fix_20261020_r01/`、`…/t05_board_diag5_20261020_r01/`、`…/t05_ctrl_20261020_r01/` | 恢复命令=`bash scripts/stage3_t05/run_t05_board_capture.sh D:/codex-worktrees/dbdf/tmp/s3r06/t04_sof_fix_20261020_r01 D:/codex-worktrees/dbdf/tmp/s3r06/t04_j11cmos2_elf_v6/elf_build/app/an5642_j11cmos2_v6.elf v6 120` | 状态/下一接手方=`IN_PROGRESS / 阶段3总控（无人接管；等彩条颜色判读）`