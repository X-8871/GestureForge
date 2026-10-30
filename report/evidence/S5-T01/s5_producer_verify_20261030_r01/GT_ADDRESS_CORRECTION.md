# 生产者验证数据摘要 + GT 地址勘误（供 6-D 输入）

RunId：`s5_producer_verify_20261030_r01`（主窗）+ `s5_producer_gtfix_20261030_r02` / `s5_producer_gt_tight_20261030_r03`（补读）
PL：P3q `4d6ea2ef…b6e4`；ELF：`s5_display_app_p3q_producer_longrun.elf` sha `47a69644…cd945e`（292,588 B）

## 1) UART `S5PROD` 帧行
- 20 s 抓取共 **597 条**（含 1 条 `session start`），`frame_id` = 0,1,2,…,596；**差值集合 {1} ⇒ 严格 +1**
- 每行样例：
  `S5PROD frame_id=1 n=2 status=0x1 cap_ms=275594 inf_ms=275601 cap_lo=6390A3A3 inf_lo=63B43E39`
- `n` 在 1/2/3 循环；`status=0x1`；`cap_ms`≈开机后 ms（GT 计）、`cap_lo` = GT ticks 低 32 位

## 2) 显示侧 `S5DISP` 行（生产者版）
- 9 条，全部：`S5DISP frame=60 lat=32 age=39 st=B sr=11000 src=real nbox=3`（lat/age **非 0、为真实计算值**：lat=32、age=39）
- 补读窗（r02，应用续跑 3 s）：`S5DISP frame=840 lat=20 age=27 st=3 sr=11000 src=real nbox=3`（lat=20、age=27）
- **注意**：生产者版 **`S5DISP RESULT`（JSON）只在 30 min 收尾时打印**，20 s 窗内未出现 ⇒ 本项以"内联 lat/age"为准；如需 RESULT 需跑到 30 min 结束或用有界版

## 3) 结果块 `0x20800000`（0x120 B）
布局实测：`magic, frame_id, n_dets, cap_lo, cap_hi, inf_lo, inf_hi, status`（32 B）+ 16×16 B 检测项 + 末尾 `5a a5`

| 读取 | magic | frame_id | n_dets | cap_lo | cap_hi | inf_lo | inf_hi | status |
|---|---|---|---|---|---|---|---|---|
| r01 read1 | 0x53355253 | 624 | 1 | 0x0083669D | 23 | — | — | — |
| r01 read2（+2 s） | 0x53355253 | 758 | 3 | 0x5927CCF4 | 23 | 0x594B678A | 23 | 1 |
| r02 read1 | 0x53355253 | 947 | 3 | 0xE90EAAD2 | 29 | 0xE9324568 | 29 | 1 |
| r02 read2（+6 s） | 0x53355253 | 1130 | 3 | 0x623018A6 | 30 | 0x6253B33C | 30 | 1 |
| r03（应用已停，cap 冻结） | 0x53355253 | 1312 | 2 | 0xDB3D…（见 JSON） | 30 | … | 30 | 1 |

- frame_id 增长：624→758（2 s，+134）、947→1130（6.1 s，+183）⇒ 块在持续更新，约 30 fps
- 3 个检测项原始 hex（r02 read2）：
  - `[0] d2 00 fa 00 50 00 46 00 00 41 00 00 00 00 00 00`
  - `[1] aa 00 68 01 6e 00 5a 00 01 4a 00 00 00 00 00 00`
  - `[2] 82 00 82 00 8c 00 6e 00 02 62 00 00 00 00 00 00`
- cap→inf 差值恒定 ≈ **2,333,334 ticks ≈ 7.0 ms**（即捕获→推理完成的流水延迟）

## 4) GT：**地址勘误（重要）**
- **`0xF8000B00/0xF8000B04` 不是 Zynq GT**：三次窗口读回均为常量 `low=0, high=204,476,774`（不随时间变化）——这是 SLCR 区间寄存器
- **Zynq-7000 Global Timer 实际在 `0xF8F00200`（低）/`0xF8F00204`（高）**，实测递增：
  - r02 k=0：`133,032,045,794` ticks；r03（约 53 s 后）：`150,656,299,183` → 差 17.62e9 ticks / 333.33 MHz = 52.9 s ✓ 自洽
  - 与 producer 自报 `cap_ms` 自洽：`cap_ms × 333.333 = cap ticks`；1 帧 = 11.11e6 ticks = 33.3 ms（30 fps）
- **独立 age 公式**：`age_ms = (GT_value − cap_ticks) × 1000 / 333333333`，
  其中 `cap_ticks = (cap_hi << 32) | cap_lo`（同一时刻读 GT 与块头才有意义；r03 因应用已停 cap 冻结，算得 54 s 不代表运行值）

## 5) 两次回读 frame_id（收窗前）
- r01：624 → 758（+134）；r02：947 → 1130（+183）⇒ 结果块在增长（非冻结）

## 附：自算 age 的注意
- 读数须**应用运行中**且 GT 与块头**同会话紧邻**读（r03 单会话窗口 1 ms）；应用停止后 cap 冻结、GT 继续走 ⇒ age 会虚高
- 显示侧内联 age=39 / 27 与该帧的相位有关；如需对齐比较，建议同一会话先读 GT+块、立刻抓 UART 的最近一条 `S5DISP ... age=`，两者相位差 ≤1 帧（33 ms）内比较