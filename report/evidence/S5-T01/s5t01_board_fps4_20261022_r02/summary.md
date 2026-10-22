# S5-T01 §3 可信帧事件与四种 FPS RunId `s5t01_board_fps4_20261022_r02`（权威）

- 时间（UTC+8）：2026-10-22 19:20–19:35
- 依据：`CDX-20261022-014 §3`（5-B）；设计核验见 `../s5t01_gate_fix_20261022_r01/S5T01_S3_frame_event_design.md`
- 被测件：`s5t01_case5_r04.elf` SHA256 `29fe895a…3aed`（rev r04，单用例 5 常显）+ 冻结灰度位流 `44e609cc…c4afb`（易失）
- 结论：**四个 FPS 语义中三个已实测**（video_refresh / display / 以及"推理 NA"的显式标注），**两个独立事件源交叉吻合**；`unique_frame_update_fps` 本轮仅到**用例级**；延迟给出**明确边界**（非光子到屏幕）。

## 1. 事件源与实现（本次新增于 P1 rev r04）

| 事件源 | 接线/编号 | 用途 |
|---|---|---|
| MM2S 帧完成中断 | `axi_vdma_0.mm2s_introut` → `xlconcat_0.In0` → PS `IRQ_F2P[0]` ⇒ **GIC 61** | `display_fps` |
| VTC 中断 | `v_tc_0.irq` → `xlconcat_0.In1` → `IRQ_F2P[1]` ⇒ **GIC 62** | `video_refresh` |
| 内容提交 | 应用侧（render+flush 完成） | `unique_frame_update_fps` / 延迟起点 |

- `XScuGic` 初始化：`S5_P1_EVENTS_INIT=0`（0=成功）。
- MM2S：`CR` 置 `CR[23:16]=1`（帧计数阈值=1 ⇒ **每帧一次 IRQ**）+ `bit12 FrmCntIrqEn` + `RS=1` → `MM2S_CR_ARMED=00011001`；ISR 内按 W1C 清 IRQ 位。
- VTC：`IER=0xFFFF3F00`（实测写回值）；ISR 内 W1C 自清。
- 计时源：平台 `XTime`，`counts_per_second=383333343`（日志自报，复算用同一值）。

## 2. 实测结果（`console/recompute_fps.json`，`recompute_fps.py` 从原始日志独立复算）

| 指标 | 实测 | 定义/起止事件 |
|---|---|---|
| **`display_fps`** | **59.206 fps** | MM2S FrmCntIrq：连续两次**帧完成**中断；窗口 16.35 s、968 事件 |
| **`video_refresh_events_per_s`** | **118.351 /s** | VTC 中断事件率 |
| **`video_refresh_frames_per_s`** | **59.175 fps** | = 事件率 ÷ **2**（实测每帧 2 次 VTC 事件：ISR 位 12/13/16 同置，逐位计数相等） |
| `unique_frame_update_fps` | **用例级**（`S5_P1_SHOW uniq_case_updates`，每 6 s 切换一次） | 内容提交；**frame_id 级需 T5-05** |
| `inference_fps` | **NOT_APPLICABLE**（屏/日志打印 `NA`） | 无阶段4 注入源；**不用 0 伪装** |
| `commit_to_frame_complete_ns` | 0.221 / 9.085 ms（样本） | `t_overlay_commit` → 其后**首个 MM2S 帧完成事件**；**明确不是光子到屏幕** |

- **交叉验证**：两个互不依赖的事件源（VTC 视频时序 vs MM2S DMA 帧完成）给出 59.18 与 59.21 fps，相对差 **0.05%** ⇒ 事件采集自洽。
- **预热处理**：首窗口含启动前遗留事件（VTC 128 / MM2S 64），聚合时**剔除 1 个窗口**；原始窗口值全部保留可复算。
- **复算一致性**：`recompute_fps.py` 对 17 个窗口逐行重算与板上打印值**全部一致**（`all_rows_match_logged=true`，exit 0）。
- **历史负向证据**：同一日志的 `pre_boot` 段来自 r03 应用，其 `video_refresh=0`（当时按 bit0/1 计数，实机事件位是 12/13/16）——保留在 `segments` 中，说明"事件位选择错误会导致 0 值"，不可当作真实 0 帧率。

## 3. 与"旧测法失败"的关系（D-3 根因确认）

- 旧测法只置 `FrmCntIrqEn` 并轮询 `SR[23:16]`，恒为 1（阈值=0 + IRQ 未清除）⇒ 测不出。
- 本次改为**阈值=1 + 中断计数 + ISR 清理**后，事件稳定 59–60/s ⇒ **根因假设被实测确认**。

## 4. 未完成 / 限制

- `unique_frame_update_fps` 仅为**用例级**，不是 frame_id 级（T5-05 未做）。
- `inference_fps` 为 NA：本轮无阶段4 冻结结果注入，**不得**用合成用例冒充推理帧率。
- 延迟只给 `commit→首个帧完成事件` 边界，**没有**物理呈现（光子到屏幕）测量方法。
- VTC 每帧 2 次事件的**位语义**仅由实测计数推断（b12=b13=b16 同置、120/s、等于 2×59.2），未查 IP 文档逐位确认；若后续要用该位做更细事件，需按 PG016 复核。
- 视频源为 **PS 合成图**，不涉及真实采集；本轮未烧 QSPI，`0x503D` 未改，`hw_server` 已清理不驻留。

## 5. 证据文件

- `console/uart_fps4r04.log`（原始 UART，含 `S5_FPS4`/`S5_LAT`/`S5_P1_*` 标记）
- `console/recompute_fps.json` / `console/recompute_stdout.txt`（独立复算，exit 0）
- `console/capture_fps4r04.txt`（下载 + UART + 只读转储全过程）、`console/build_r04.log`、`console/input_hashes.txt`
- 历史（位选择错误）：`../s5t01_board_fps4_20261022_r01/`（保留，不覆盖）