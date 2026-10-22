# S5-T01 §3 可信帧事件与四种 FPS：事件源核验与设计（离线，未实现）

- 时间（UTC+8）：2026-10-22 19:40
- 依据：`CDX-20261022-014-stage5-display-runbook-r02.md` §3（5-B）。本文件只记录**核验事实与设计**，实现与板测另起 RunId。
- 状态：**设计就绪，尚未实现/未板测**（不得据此声称 FPS 已测得）

## 1. 事件源核验（只读 XSA/BSP，未碰板卡）

对冻结设计的 `design_1_wrapper.xsa`（`90e1bdee…`）解包 `design_1.hwh`，并查阶段3 BSP 的 `xparameters.h`：

| 事实 | 值 | 出处 |
|---|---|---|
| 显示通道 VDMA | `axi_vdma_0`（MM2S，`XPAR_AXI_VDMA_0_BASEADDR=0x43000000`，`INCLUDE_MM2S=1 / INCLUDE_S2MM=0`） | `xparameters.h:38-45` |
| 采集通道 VDMA | `axi_vdma_1`（S2MM，`0x43010000`） | `xparameters.h:78+` |
| **MM2S 帧完成中断** | `mm2s_introut`（LEVEL_HIGH, INTERRUPT）→ `xlconcat_0.In0` → PS7 `IRQ_F2P[0]` ⇒ **GIC ID 61** | hwh `<CONNECTION INSTANCE="xlconcat_0" PORT="In0"/>`；`xparameters.h` `XPAR_FABRIC_AXI_VDMA_0_MM2S_INTROUT_INTR 61U` |
| **VTC 中断** | `v_tc_0.irq` → `xlconcat_0.In1` → `IRQ_F2P[1]` ⇒ **GIC ID 62** | hwh `<CONNECTION INSTANCE="xlconcat_0" PORT="In1"/>`；`XPAR_FABRIC_V_TC_0_IRQ_INTR 62U` |
| S2MM 中断 | `s2mm_introut` 仅声明为 INTERRUPT 端口，**无 CONNECTION** ⇒ 未接入 | hwh |
| PS 侧织物中断 | `PCW_USE_FABRIC_INTERRUPT=1`，`IRQ_F2P = xlconcat_0_dout` | hwh |
| 显示帧由时序驱动 | `XPAR_AXI_VDMA_0_USE_FSYNC=1`、`FLUSH_ON_FSYNC=1` ⇒ MM2S 每帧由 VTC 的 fsync 启动 | `xparameters.h:56-57` |
| VTC 实例 | `v_tc_0`，`XPAR_V_TC_0_BASEADDR=0x43C00000`；寄存器 `ISR@0x04`、`IER@0x0C` | `xparameters.h:686+`、`xvtc_hw.h:150-156` |
| BSP 支持 | `xscugic.h`/`xvtc.h` 头与 `XScuGic_CfgInitialize`/`XScuGic_Connect`/`XVtc_*` 符号均在 `libxil.a` | BSP include/lib |

⇒ **可以做真正的中断型帧事件**（不必只靠轮询），且能把「视频刷新」与「显示帧完成」分开取材。

## 2. 判定：为什么"帧计数不推进"（D-3 根因假设，待实测确认）

- 现有 P1 只置 `CR` bit12（FrmCntIrqEn）后轮询 `SR[23:16]`，观察到恒为 1。
- 成因假设（与寄存器语义一致，待实测）：**`CR[23:16]` 是帧计数阈值**；`CR=0x00010001` 时阈值为 0，计数器在首次到达阈值后即停，且**未应答的帧完成 IRQ 未被清除**（无 ISR，也未写 1 清零），故计数不再推进。
- 拟修法：`CR = (CR & 0x00FFFFFF) | (1<<16) | RS | FrmCntIrqEn`（阈值=1 ⇒ **每帧一次 IRQ**），并在 ISR 中按 W1C 清除 `SR` 的 IRQ 位（bit9/10/11/12）后再计数。

## 3. 四种 FPS 的定义、起止事件与分母口径（§3.4/§3.5）

| 指标 | 定义（本轮拟用） | 起止事件 | 数据源 |
|---|---|---|---|
| `video_refresh_fps` | 视频时序刷新事件频率 | VTC 中断（帧/有效视频边界）连续两次事件 | GIC 62 ISR 计数 + `XTime` 首末时间 |
| `display_fps` | 显示帧**完成**率（本阶段冻结语义下） | MM2S 帧计数 IRQ（`FrmCntIrq`，阈值=1） | GIC 61 ISR 计数 + `XTime` 首末时间 |
| `unique_frame_update_fps` | **不同** `frame_id` 内容实际更新率 | 应用提交事件（内容变更那次 render+flush 完成） | 应用侧计数器（仅在内容变更时 +1） + `XTime` |
| `inference_fps` | 真实推理完成率 | —（**无阶段4 注入源**） | **NOT_APPLICABLE**，屏上/日志显式标 `NA`，**不用 0 伪装**（§5.4） |

- 统一口径：`fps = 窗口内完成事件数 / 窗口单调时间间隔`；保留窗口首末 `XTime`、事件数、窗口长度、预热处理，**可由原始日志复算**。
- 计时源：平台 `XTime`（`COUNTS_PER_SECOND`），记录频率与单位换算；回绕按 64 位计数，不做取模猜测。
- 延迟：只报告**实际测到的边界** `commit_to_frame_complete_ns` = 应用提交（`t_overlay_commit`）到其后**首个 MM2S 帧完成事件**的时间；**不称"光子到屏幕"**（§3.6）。
- 中断服务只做必要计数/时间戳（ISR 内不打印），UART 日志在非中断上下文输出。

## 4. 待办（下一步实现）

1. P1 rev r03：XScuGic 初始化（ID 61/62）、MM2S 与 VTC ISR、VTC `IER` 使能与原始 `ISR/IER` 记录、`CR[23:16]=1`。
2. 短动态序列验证事件持续推进（先 `S5_FPS4` 原始计数），再与显示状态/视频观察比对；不可靠即 `NOT_VERIFIED`。
3. 原始事件日志（逐窗口 count + 首末时间 + 原始 `SR`/`ISR`）落证据，附复算脚本。
4. 与 HUD 13 字段统一（§5.4）：无摄像头 ⇒ `capture_fps=NA`；无阶段4 ⇒ `inference_fps=NA`。