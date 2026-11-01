# window_close 补全 — `ecam_diag_20261031_r51`

补记时间：2026-10-31T23:47（UTC+8），补记人：board-runner（Team Lead 指示）

## 1. 本轮目的与结论

- 目的：用 **Xilinx XAxiVdma 官方驱动路径**（v29d，与阶段3 同路径）验证 build11f 的 VDMA S2MM 通道能否启动
- **结论：仍失败。**`CfgInitialize=1`（XST_FAILURE）、`DmaStart=9`（XST_DMA_ERROR）；`DmaConfig=0`、`DmaSetBufferAddr=0` 成功；DDR `0x12000000` 全 0；`after1s frmcnt=1`（不增长）
- 驱动侧唯一定位：`XAxiVdma_CfgInitialize` 在初始化时轮询"通道复位完成"超时（`Read channel reset failed`）⇒ **硬件侧 CR.RESET 始终不清**，与 r49a/r50 手写寄存器路径结论一致

## 2. `drv:` 四行返回码（原文）

```
CAM: v29 enter
drv: CfgInitialize=1 (XST_SUCCESS=0)
drv: DmaConfig=0 (VERT=720 HORI=3840 STRIDE=3840 circ=1 sync=1)
drv: DmaSetBufferAddr=0 buf0=0x12000000
drv: DmaStart=9
```

- `XST_FAILURE=1`、`XST_DMA_ERROR=9`（阶段3 BSP `xstatus.h` / `xaxivdma.c`）
- `CfgInitialize` 失败点：`Polls=INITIALIZATION_POLLING; while (Polls && XAxiVdma_ChannelResetNotDone(rd)) Polls--; if (!Polls) return XST_FAILURE;`
- `DmaStart` 失败点：`XAxiVdma_ChannelStartTransfer` 内 `XAxiVdma_ChannelIsRunning()` 为假（CR.RS 读回 0）时返回 `XST_DMA_ERROR`

## 3. `after1s` 与 DDR

```
after1s: cr=00010006 sr=00010000 frmcnt=1
ddr 0x12000000: 00000000 ×10, 00800000, 00000000 ×5
CAM: v29 exit
```

- `CR=0x10006` = bit1(TAIL_EN)+bit2(RESET)，**RS(bit0)=0**
- `SR=0x10000`（build11f FSYNC=0，无 FSZ_MORE）

## 4. 两次运行中快照（17 项）

```
snap1 @17.66s: CAM_CR=0x10001 (cr_running=1) CAM_SR=0x10000
  GPIO_CAM=0x2  PCLK_ACC=0x765570F0  HREF_PIX=0x4D7263A2  VSYNC_CNT=0x02C0
  TL_TLAST=0x4  TL_TUSER=0x2  TAP_VALID=0x208F  TAP_BP=0x0
  IP_TV=0x208F  IP_TV2=0x1C7  IP_TR=0x2  IP_TR2=0x259642F3  IP_RST=0x1
  RST_100(0x43D40000)=0x3   FCLK0(0x43D40008)=0x530B26F9
  FCLK1(0x43D50000)=0xA6171ABA   (0x43D50008)=0x0
  PC=0x00108908 CPSR=0x800D00DF
snap2 @23.63s: CAM_CR=0x10006 (cr_running=0) CAM_SR=0x10000
  GPIO_CAM=0x2  PCLK_ACC=0x9445778B  HREF_PIX=0x61275ED9  VSYNC_CNT=0x0373
  TL_TLAST=0x4  TAP_VALID=0x208F  IP_TV=0x208F（均冻结）
  RST_100=0x3   FCLK0(0x43D40008)=0x64D588B6  FCLK1(0x43D50000)=0xC9AC2184  (0x43D50008)=0x0
  PC=0x00108918 CPSR=0x600E00DF
```

派生（Δt=5.97 s）：
- `0x43D40000 = 0x3` 恒定 ⇒ bit0(rst_100)=1、bit1(rst_all)=1，**两路复位输入已释放**
- `0x43D40008` Δ=298,451,389 ⇒ **≈50.0 MHz（FCLK0 在跑）**
- `0x43D50000` Δ=598,979,530 ⇒ **≈100.3 MHz（FCLK1 在跑）**
- `0x43D50008 = 0`（未使用）

## 5. 门禁与契约

- 四门禁全 PASS：APER 断言（0x017C000D）、DDR 窗口写读、SCCB 总线体检（pre=post=0x3）、PL 探测（2B CSR=0x53324250、camera VDMA VER=0x62000050）
- `--allow-no-por` 已启用，日志保留 `[BOARD_STATE] ⚠️ OVERRIDE：POR 前置未满足仍开窗`
- **未物理 POR**：用 PS7 重初始化 + PL 重编程替代（阶段3 对照实验残留）；残留风险已记录；`board_state.abnormal` 未清除；建议最终验收前由 Wong 物理断电一次
- 未使用 `rst -system` / `rst -processor`；未烧 QSPI；未改接线；未反复写 CR（本轮仅 v29d 驱动尝试一次）

## 6. 边界与下一步

- 未跑相机窗（VDMA 未启动、DDR 无数据）
- 本轮排除项（累计）：SCCB、sensor 出流、FSYNC、tuser 连接、寄存器映射、CR 写序、复位电平（rst_100/rst_all）、三路时钟（FCLK0=50 MHz / FCLK1=100.3 MHz）、官方驱动路径
- 下一步：build11g（重建 `axi_vdma_cam` 实例 + `0x43D60000` axi_resetn 电平、`0x43D60008` lite aclk 计数）→ `ecam_diag_20261031_r52`（build11g + v29d）
- 若 build11g 仍失败 ⇒ 交 Wong 决策"阶段3 采集子图移植"或"接受 R-07 受限"