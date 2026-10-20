# S3-T05 只读核验记录（阶段3总控，2026-10-20 11:51–12:2x UTC+8）

工作树：`D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`／起始 HEAD `41ee5ba`。
本记录只含**只读核验**与**工具事故**，不含板上实验结果（另见同目录后续文件）。

## 1. 开工核验（只读）

| 项目 | 结果 |
|---|---|
| `git status --short` | 仅 2 项未跟踪：`NA/`、`clockInfo.txt`（2026-10-06/10-20 旧物，非本轮产物） |
| HEAD | `41ee5ba`（旧窗口 04:34 提交），与主 STATE 记录一致 |
| `index.lock` | 四棵树（主目录、dbdf、96a3、w2b）均不存在 |
| 重型进程 | 无 vivado/xsim/hw_server/vitis/xsdb 残留；FreeMB≈5.7–6.4 GB |
| 2B 状态 | w2b HEAD `bca323b`、未提交 143 项；无 hw_server/vivado → 无硬件争用（信箱 `CDX-20261020-003` 仍无回执） |
| 旧会话导出 | `verify_incident.mjs` 退出 0：1093 帧、2093 事件、seq 0–2091、compaction_end=0（与既有记录一致；背景材料的“2703 帧”不成立） |

## 2. J11-CMOS2 引脚映射复核（独立，结论：正确）

方法：PyMuPDF 提取 `D:\FPGA_Competition\摄像头资料\Wong搜集的资料\AX7020 User Manual_V3.0.pdf` 第 29–31 页正文（Table 7.5.1 J11 扩展口引脚分配），逐针与
`board/stage3/hardware/an5642_j11_cmos2.xdc` 比对；并与官方 `23_ov5640_dual` 的
`Vivado/auto_create_project/src/constraints/an5642.xdc`（cmos2 通道，J10 映射）逐条比对信号顺序。

| 模块 J3 针号 | 信号（CMOS2 组） | J11 针 | 手册 FPGA 脚 | 本变体 XDC | 一致 |
|---|---|---|---|---|---|
| 3 | D9 | PIN3 | F17 | cmos1_d[9]=F17 | ✅ |
| 4 | SDA | PIN4 | F16 | cmos1_i2c_sda=F16 | ✅（I2C 实测有 ACK） |
| 5 | D6 | PIN5 | F20 | cmos1_d[6]=F20 | ✅ |
| 6 | SCL | PIN6 | F19 | cmos1_i2c_scl=F19 | ✅（I2C 实测有 ACK） |
| 7 | D7 | PIN7 | G20 | cmos1_d[7]=G20 | ✅ |
| 8 | D2 | PIN8 | G19 | cmos1_d[2]=G19 | ✅ |
| 9 | HREF | PIN9 | H18 | cmos1_href=H18 | ✅ |
| 10 | D8 | PIN10 | J18 | cmos1_d[8]=J18 | ✅ |
| 11 | D3 | PIN11 | L20 | cmos1_d[3]=L20 | ✅ |
| 12 | RESET | PIN12 | L19 | cmos_rstn[0]=L19 | ✅ |
| 13 | D4 | PIN13 | M20 | cmos1_d[4]=M20 | ✅ |
| 14 | D5 | PIN14 | M19 | cmos1_d[5]=M19 | ✅ |
| 15 | D1 | PIN15 | K18 | cmos1_d[1]=K18 | ✅ |
| 16 | D0 | PIN16 | K17 | cmos1_d[0]=K17 | ✅ |
| 17 | VSYNC | PIN17 | J19 | cmos1_vsync=J19 | ✅ |
| 18 | PCLK | PIN18 | K19 | cmos1_pclk=K19 | ✅ |

补充证据：
- 官方 `23_ov5640_dual` XDC 的 cmos2 端口顺序（d9,sda,d6,scl,d7,d2,href,d8,d3,rstn,d4,d5,d1,d0,vsync,pclk）与手册 J10 PIN3–PIN18（W19,W18,R14,P14,Y17,Y16,W15,V15,Y14,W14,P18,N17,U15,U14,P16,P15）**逐条相符**；模块原理图 `AN5642-2016-12-14.pdf` 的网络名序列亦与之一致。
- `impl_1/design_1_wrapper_io_placed.rpt`（本变体 04:04:32 生成）显示 16 个信号落点与方向正确（pclk/vsync/href 均 INPUT，I2C 两脚 BIDIR/PULLUP）。
- 结论：**J11-CMOS2 的引脚映射不是问题来源**；“CMOS1 无 I2C ACK”在 J10（官方映射）与 J11（自制映射）两次独立验证下都成立，保留“模块 CMOS1 侧故障”判断。

## 3. S2MM SR 位定义更正（来源：`xaxivdma_hw.h` v6.15）

`D:\Xilinx\2026.1\data\embeddedsw\XilinxProcessorIPLib\drivers\axivdma_v6_15\src\xaxivdma_hw.h`：
`Halted=0x1 Idle=0x2 ERR_INTERNAL=0x10 ERR_SLAVE=0x20 ERR_DECODE=0x40 ERR_FSZ_LESS=0x80
ERR_LSZ_LESS=0x100 ERR_SG_SLV=0x200 ERR_SG_DEC=0x400 ERR_FSZ_MORE=0x800`。

据此重解既有读数 `S2MM SR=0x00015810`：`ERR_INTERNAL(0x10)` + `ERR_FSZ_MORE(0x800)` + 高位状态位（含 0x1000/0x4000 与 0x10000，对应 IRQ/帧计数类状态）。
**结论：错误类型是“帧尺寸多于预期 + 数据搬运内部错误”，不是单一 FSZ_MORE**；旧材料把它简写为“FSZ_MORE(0x800) / ERR_INTERNAL(0x10)”的两项并列是准确的，但把它当作唯一结论不足。

## 4. 重要更正：旧“帧缓冲全 0”读数不可信

厂商 `display_demo.c` 在 `DisplayStart()` 之后有一次
`memset(dispCtrl.framePtr[dispCtrl.curFrame], 0, 1920*1080*3);` **且其后没有 cache 维护**。
该 memset 会在 CPU 数据 cache 中留下**脏零行**；之后应用用 CPU 直接读同一地址得到的是 cache 命中值（0），
而且这些脏行被淘汰时还会**回写覆盖 DMA 已写入的图像数据**。

因此：v4 的 `S3_DIAG4_FB=0x00000000 ...` 只能说明“CPU 看到的是自己 memset 的零”，
**不能证明 S2MM 没有把图像写进 DDR**。这一点已在本轮 v5 诊断补丁中修正（flush + invalidate 后再读）。

## 5. 工具事故与恢复（JTAG/DAP）

- 现象：对**运行中**的 A9#0 直接 `mrd`（`scripts/stage3_t03b/jtag_probe.tcl` 之后本人只读探测）触发
  `Timeout waiting for the Instruction Complete bit`；此后 `targets` 只剩 `DAP (APB AP transaction error, DAP status 0x30000021)` 与 `xc7z020`，
  APU/A9 从目标树消失。
- 链体检：`jtag targets` 仍为 `Digilent JTAG-HS1` + `arm_dap (4ba00477)` + `xc7z020 (23727093)` → 线缆/链路正常，问题在 DAP→APB 访问。
- 恢复：`targets -set -filter {name =~ "*DAP*"}` → `rst -type system`；随后 APU/A9 恢复为 `Running`。
  **该复位会清 PL 配置**（PL 另需重新下载比特流；未烧 QSPI、未改非易失）。
- 新规矩：只读探测必须先 `stop` A9 → `mrd` → `con`（见 `scripts/stage3_t05/jtag_read_safe.tcl`）。

## 6. 本轮限制与未执行

- 未做任何电气测量、未接显示器（Wong 2026-10-20 明确“没接显示器”）；HDMI 画面未验证。
- 未烧 QSPI/非易失；未动厂商原件、主工作树、w2b/96a3。
- ILA 波形仍未采集（调试位流由 Developer 任务 task-2 在构建）；传感器是否停流/极性是否异常尚无实测。