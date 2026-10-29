# ERRATUM（更正）：4× 差在**除法分母**（宏无括号 + 强转优先级），不是 `XTime_GetTime` 慢

- 关联：同目录 `ANALYSIS.md`（2026-10-29 18:32 版，结论写"`XTime_GetTime` 时基为全局定时器的 1/4"）——**该结论错误，本文件更正**。
- 更正来源：stage4-lead 离线反汇编/预处理证据（2026-10-29 19:0x），lead 复核后采纳。

## 1. 事实（更正后）

1. `XTime_GetTime` **没有问题**：反汇编 `libxiltimer.a(globaltimer_sleep_zynq.c.obj)` 显示它就是双读
   `0xF8F00204 / 0xF8F00200`（与全局定时器同源）；`ps7_init.tcl:593` 把 GT 控制写 `0x9`（prescaler=0）
   ⇒ 333,333,343 Hz，与 JTAG 实测 ≈333.8 MHz 一致。
2. **真正的 4× 在分母**：BSP `xtimer_config.h:14-15`
   `#define XSLEEPTIMER_FREQ  XPAR_CPU_CORE_CLOCK_FREQ_HZ/2`
   `#define COUNTS_PER_SECOND  XSLEEPTIMER_FREQ`
   **没有括号**；应用代码写 `(uint64_t)COUNTS_PER_SECOND` ⇒ 经预处理实际是
   `(uint64_t)666666687/2`，强转先于除法 ⇒ 有效分母 **1,333,333,374**（= 2 × 666,666,687），
   正好是 GT 频率的 **4 倍** ⇒ 所有 `*1000 / COUNTS_PER_SECOND` 的时间被压小 4 倍。
3. 独立佐证：探针 ELF `f9095655…` 在 `0x104654` 处用**字面量 `0x4F790D7E` = 1,333,333,374** 做除数；
   w4 源（`c07c26f7…`）的 `gcc -E` 输出同样展开为 `(uint64_t)666666687/2`。

## 2. 对上一轮结论的影响

- 上一轮实测数字（主机 32.18 s vs 应用 8.096 s = 3.975）**仍然有效**，只是解释改变：
  不是计数器慢，而是**应用把毫秒算少了 4 倍**。
- 因此"时间基座修复"的方案也随之改变：不是"绕开 XTime_GetTime"，而是**修分母表达式**（加括号/用正确字面量）。
- 影响面不变：A 项 30 min 判据实际≈2 h；历史 11.8 s/帧 ≈ 真实 47 s/帧；2B BD FCLK0 设计值 50 MHz。

## 3. 修复（stage4-lead 已实施，离线）

- 统一分母 `S4D_MS_DIV = ((uint64_t)(COUNTS_PER_SECOND))`（**带括号**）；13 处 `XTime_GetTime` 保留/改为显式 GT 读；
  新增 `_Static_assert` 防 BSP 头漂移；未用乘/除 4 的缩放掩盖；未改 BSP、未改 w4。
- 新 ELF（P2c 应用变体）：`build\s4d_ps_app_pl_dma.elf` sha256 `bff4b80f…1f5be6`（269,900 B），
  6 项编译退出码全 0，`check_artifacts.py`=0。
- 自检口径提醒：`TIMEBASE CHECK ratio_x1000≈1000` **本来就会成立**（同源），不能当修复证据；
  真正要看的是 `DIVISOR old_expr_ms ≈ gt_ms/4`（old/gt≈250）⇒ 修复后应变成 old/gt≈1000。

## 4. 待做（需上板）

- 用修好的 ELF 在**同一窗口**同时记：主机时间戳 / GT 口径 ms / 旧表达式口径 ms，验证 host≈GT≈修后值（±2%）。
- 探针/长跑变体（`s4d_ps_app.c` 的 longrunP，sha `f9095655…`）**尚未重建**：需 lead 在 w4 写区按同样方式修分母后重建，
  否则其历史时间数字须 ÷4 换算。

## 5. 边界

未上板复核（本文件只更正结论）；`ENABLE=0`；不主张 G3/G4/G5。