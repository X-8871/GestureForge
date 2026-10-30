# 6-D 数据包：生产者契约 + 可信时基自洽（阶段首传）

- RunId：`s5_producer_6d_pack_20261030_r01`；整理时间 2026-10-30T21:11:05+08:00
- 来源窗口：`s5_producer_verify_20261030_r01`（主）/ `s5_producer_gtfix_20261030_r02` / `s5_producer_gt_tight_20261030_r03` / `s5_producer_age_tight_20261030_r04` / `r05`（作废留档）
- PL：P3q `4d6ea2ef…b6e4`；ELF：有界生产者 `0b8fac18…0775`（292,252 B）/ 长跑生产者 `47a69644…cd945e`（292,588 B）
- **口径**：lead 采纳"口径 1 时基自洽"，不要求运行中 |age_jtag−age_display|≤3 ms（工具限制，非时基问题）

## 1) 生产者契约实测
- `S5PROD` 行：r01 20 s 共 **597 条**（1 条 session start + 596 帧行），`frame_id=0,1,…,596`，**相邻差值集合 {1} ⇒ 严格 +1**
- 样例行：`S5PROD frame_id=1 n=2 status=0x1 cap_ms=275594 inf_ms=275601 cap_lo=6390A3A3 inf_lo=63B43E39`
- 块头 8 字段（r04，作者在跑，frame 124）：`53355253 0000007c 00000002 966b23e3 0000002e 968ebe79 0000002e 00000001`
  - magic=0x53355253、**frame_id=124**、n_dets=2、**cap=200,092,099,555**、**inf=200,094,432,889**、status=1
  - **inf − cap = 2333334 ticks = 7.00 ms**
- 检测项 16 B 步进：前 3 项（r04）`S5DISP boxes n=3 crc=88657459 hex=AF 48 78 69 2C8 154 A5 87 22F 63 D2 A5`；r02 块内前 3 项
  `[0] d2 00 fa 00 50 00 46 00 00 41 00 00 00 00 00 00`
  `[1] aa 00 68 01 6e 00 5a 00 01 4a 00 00 00 00 00 00`
  `[2] 82 00 82 00 8c 00 6e 00 02 62 00 00 00 00 00 00`
- `n_dets`/frame_id 增长：r01 624→758（+134/2 s）、r02 947→1130（+183/6.1 s）

## 2) 时基自洽证明（口径 1 核心）✅
- **`age_ms − latency_ms` = 27 − 20 = 7 ms**，与块头 **`inf − cap` = 7.00 ms** 一致（**diff ≈ 0.000 ms**）
- GT 实测速率（`0xF8F00200/04`，333.33 MHz）：
  - 跨窗：r02 GT=133,032,045,794 → r03 GT=150,660,241,658，差 17,628,195,864 ticks = **52.88 s**（对应两窗间隔 ≈53 s）
  - r04 同会话：lo1→lo2 = 2,632,734 ticks = **7.90 ms**（对应同会话 8 次 mrd 的实际耗时）
- 生产/消费共用同一 GT：`counts_per_second=333333343` 与实测 333.33 MHz 自洽；producer `cap_ms × 333.333 = cap_ticks` 逐帧成立
- r04 RESULT：`S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":30,"fps_dis":60,"fps_upd":29,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":20,"age_ms":27,"vdma_err":0,"frames":180,"vcnt":180,"box_crc":88657459,"fb_crc":2415513614,"uf_pix":264099392,"uf_frame":191521,"uf_total":264099392,"src":"real"}`

## 3) GT 地址更正（已实测）
- **`0xF8000B00/04` 不是 GT**：三次窗口读回均为常量（low=0, high=204,476,774，不递增），属 SLCR 区间
- **Zynq-7000 Global Timer = `0xF8F00200`(lo)/`0xF8F00204`(hi)**，实测递增；详见 `GT_ADDRESS_CORRECTION.md`

## 4) 失败/作废记录（保留不删）
- r04 `A-1`（|age_jtag−age_display|≤3 ms）**FAIL**：实测 48.3 ms；根因 = xsdb 读 PS 内存/GT 要求核 stop ⇒ 读数时刻块头 cap 已陈旧 2+ 帧（工具限制）
- r05（运行中快速循环读）**作废**：`Cannot read memory if not stopped. Execution context is running`，见 `producer_r05_loop_ROOTCAUSE_NOT_STOPPED.log`

## 5) 边界声明（必须引用）
- 本生产者提供**真实时基（GT）、帧序号（frame_id 严格 +1）、status、session tag**；
- **`n_dets`/score/坐标是模拟移动框**（用于链路/时基验证），**真实推理写端属后续增量**；
- 未写候选区、未改 PL、未烧 QSPI；RESULT/块头数值均来自同一 P3q 位流 + 有界生产者 ELF。
