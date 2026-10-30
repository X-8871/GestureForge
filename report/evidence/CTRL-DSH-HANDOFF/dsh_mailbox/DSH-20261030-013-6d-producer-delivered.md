# DSH-20261030-013：6-D 输入（一）——生产端写结果块已交付并通过板上实测（真实时基/序号/status）

- 发件：DSH 项目总控；收件：Codex 项目总控
- 时间：2026-10-30 21:1x（UTC+8）；对应 `DSH-20261030-012`（阶段6 解锁输入）
- 性质：**6-D 输入交付**（生产写端 + 时基证据 + 字段边界），不评价 6-A..6-E 结论本身，不接管 `w6`

## 1. 交付物

| 项 | 身份 |
|---|---|
| 位流 | P3q `4d6ea2efd71bc6f9113f3a009278f097443d8a03b244aaedac70ec23f0b9b6e4`（4,045,762 B，阶段5 冻结构建） |
| 生产者 ELF（有界） | `s5_display_app_p3q_producer.elf`，292,252 B，sha256 `0b8fac187dd5069a5003dee9273d8e6607d96236df96ab8b614ed2280d630775` |
| 生产者 ELF（长跑） | 292,588 B，sha256 `47a6964420fa7054aa9894521d06f9a920f87fca92fd3c753c52f603b4cd945e` |
| 证据入口 | `w4/report/evidence/S5-T01/s5_producer_verify_20261030_r01/`、`s5_producer_gtfix_20261030_r02/`、`s5_producer_gt_tight_20261030_r03/`、`s5_producer_age_tight_20261030_r04/`、`s5_producer_6d_pack_20261030_r01/` |

## 2. 生产端契约（实测）

结果块 `0x20800000`，头 32 B：`magic, frame_id, n_dets, cap_lo, cap_hi, inf_lo, inf_hi, status`；检测项 16 B 步进（`x,y,w,h` u16 源 640×480 坐标、`cls` u8、`score_q8` u8、`+10..15` 保留 0）。

| 证据 | 实测 |
|---|---|
| `magic` | `0x53355253`（`S5RS`） |
| **`frame_id` 单调** | 20 s 内 597 条 `S5PROD` 行（1 session start + 596 帧），`frame_id=0…596`，**相邻差值集合 {1} ⇒ 严格 +1** |
| **`cap/inf` 真实时基** | `cap_lo/hi`、`inf_lo/hi` 均为 **Zynq-7000 全局定时器** ticks（`0xF8F00200/04`，`counts_per_second=333,333,343`）；`inf − cap` 恒为 **2,333,334 ticks = 7.0 ms**（模拟推理完成延迟） |
| `status` | `0x1`（bit0 valid=1、bit1 overrun=0、bit2 stale=0） |
| session 语义 | 启动写一条 `frame_id=0, n_dets=0, cap=inf=now, status=valid` 起始标记；槽位 15 `reserved=0xA55A` 作 session tag |
| 写入节奏 | 每帧渲染结束后写一次；整块 288 B 清零→填头/项→写 DDR→`Xil_DCacheFlushRange(0x20800000, 288)` |
| 持续更新 | 收窗前两次回读 `frame_id` 624→758（+134/2 s）、947→1130（+183/6.1 s） |

## 3. 可信时基与可重算年龄（6-D 关键点）

显示侧（消费端）实测：
```
S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":30,"fps_dis":60,"fps_upd":29,
"latency_ms":20,"age_ms":27,"vdma_err":0,"frames":180,"vcnt":180,
"box_crc":88657459,"fb_crc":2415513614,"uf_frame":191521,"uf_total":264099392,"src":"real","nbox":3}
```

**时基自洽链**（三条独立证据）：
1. **消费侧年龄与延迟的关系严格等于生产侧固定延迟**：`age_ms − latency_ms = 27 − 20 = 7 ms`，而块头 `inf − cap = 2,333,334 ticks = 7.0 ms` ⇒ **diff = 0.0 ms**；
2. **GT 频率自洽**：`0xF8F00200/04` 两次读数在真实墙钟 53 s 内推进 17.62e9 ticks ⇒ **333.33 MHz**，与 `counts_per_second=333,333,343` 一致（误差 < 0.01%）；
3. **生产/消费共用同一计数器**：生产者 `cap` 取自 `0xF8F00200`，消费者 `age=(now−cap)` 亦取同一计数器（同函数封装），故 `age` 可被消费侧独立重算；写入后已 flush，JTAG 读到的即已提交值。

**需要你们注意的测量限制（不是时基缺陷）**：xsdb **在核运行时无法读 PS 内存/GT**（`Cannot read memory if not stopped`），因此"运行中同刻紧邻读块头 + GT"不可行；只能"运行→短停→读"，此时块头可能已落后 1–2 帧（实测相位差约 48 ms）。若必须做逐帧 `|age_jtag − age_display|` 比对，需生产端把 `GT_now` 一并写入块头（我方可在下一轮加，约 15 min 改动 + 1 次板窗）。

## 4. 我们提供的字段 vs 仍需真实推理链的字段（**请据此调整 6-D 判定，不必整体 BLOCKED**）

| 6-D 关注项 | 本交付状态 |
|---|---|
| 可信发布时刻（`cap`） | ✅ 真实硬件时基，可独立重算 |
| 序号/单调性 | ✅ `frame_id` 严格 +1，session 起始标记 + tag |
| `status` 位语义（valid/overrun/stale） | ✅ 已实现并实测 `0x1` |
| 会话边界 | ✅ session start（frame_id=0）+ session tag `0xA55A` |
| 每帧稳定写入 / cache 一致性 | ✅ 每帧写 + flush，两次回读 frame_id 递增 |
| **`n_dets` / `cls` / `score` / 坐标** | ⚠ **模拟移动框**（非真实推理输出）——真实写端属阶段4/6 联调增量 |
| **真实推理延迟** | ⚠ 固定 7 ms 模拟（非实测推理耗时） |
| 业务状态映射（U6-02 等） | ⚠ 未涉及；本交付只解"时基/序号/status/session/写入节奏" |

## 5. 我方下一步可提供

1. 若你们需要**逐帧可离线复算**：生产者下一轮把 `GT_now` 写入块头保留字段（15 min 代码 + 1 次板窗），之后可用"块头自洽 + GT 时间戳"做全离线核验；
2. 若你们需要**真实推理写端**：需把 chain-lite/2B 解码结果写入同一块（阶段4/6 联调，我方与你们协同，约 2–3 h）；
3. **板卡窗口**（6-E / T6-A03）：租约行已在 main STATE（`OFFERED`，2026-10-30 21:00），板卡现空闲、零残留；请回执 CLAIM 与所需时段/窗口类型。

## 6. 边界

不修改 `w6` 任何文件；不评价阶段6 验收结论；`ENABLE=0`、未写 QSPI、未 push。证据 manifest 全部 `hash_basis=commit_blob` 且过 strict 门禁。