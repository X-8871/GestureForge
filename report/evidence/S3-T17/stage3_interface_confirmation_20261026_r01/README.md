# 阶段3 视频输入接口确认（用户决策记录）

- RunId：`stage3_interface_confirmation_20261026_r01`；日期：2026-10-26（UTC+8）；记录方：DSH 阶段三总控。
- **用户原话（Wong，2026-10-26）**：「确认以 AN5642/J11 作为阶段3 视频输入」。

## 1. 决策内容与效力

- 阶段3 的视频输入通道正式确认为：**AN5642/OV5640 摄像头模块 → J11（CMOS2）扩展口 → PL 采集/写 DDR → HDMI 输出**。
- 效力：关闭验收计划「阶段3」中「**若不支持 HDMI 摄像头，记录差距并由用户确认替代视频接口**」的**用户确认**环节。
- 对照表第 1 行状态升级：`PASS_RECORDED_VARIANT_PENDING_USER_CONFIRMATION` → **`PASS_RECORDED_VARIANT_USER_CONFIRMED`**（差距仍如实记录：本版**不使用** HDMI 摄像头输入）。

## 2. 已记录的差距（不变）

- 与验收计划原文的"HDMI 摄像头"不同：本版走扩展口 DVP 通道；该差距在本记录与收尾记录中均明示。
- 由此产生的接口事实：`S3_DIAG9_PAD=3017=0xFF 3018=0xFF 301D=0x00 301E=0x00 D9SEL=0 D6SEL=0`、`0x4300=0x60`（RGB565）、`HSIZE=STRIDE=0x0F00`、`VSIZE=0x02D0`（1280×720，行 3840 B）；运行期地址以回读为准（`ADDR_S2MM=ADDR_MM2S=0x00110C00`）。

## 3. 记录关系（勘误不改历史）

- 本记录为**追加**：`report/evidence/S3-T17/stage3_closeout_erratum_20261026_r01/` 中"替代接口确认 = PENDING_USER_CONFIRMATION"为**当时状态**，不重写；本文档为**权威更新**。
- 不改变其他记录性局限：VDMA 首帧 bit11 根因 `PARTIAL_OPEN`、task-11 完整 SEC `BLOCKED_NOT_RUN`、TIMING-17/I-O delay（含 `9e27f53` 的名义 `create_clock` 未签核）、帧率/PCLK 未仪器测量、未录制连续视频、无 ILA、G0 丢帧策略与计数口径 `OPEN`。