# Lead 备注（对 ANALYSIS.md 的一处口径更正）

`ANALYSIS.md` 末尾"⚠️ 口径校正"称"**M4-b 应用现在在两个位流上都 error=5（位流无关），同一 M4-b ELF 的 A/B 并不存在**"。经 lead 复核，**这一条不成立**，其余结论（H1 主因、H2/H3/H4 反证、H5 放大器）不变：

- 反例（同一重建 ELF `aaedaf3c…`、同一 2B 基线位流 `555a70c2`）：
  `report/evidence/S4-T34/s4d_m4b_baseline_2b_20261029_r03/m4b_uart.log`
  → `M4B STEP=6 wait done=1 elapsed_ms=47287 status=0x00000E04 error=0`
  → `M4B RESULT={"pass":0,"done":1,"diff13":2,"first26":-1,"stale":0,"gate":1,"ack_idle":1,"epoch":1,"status":3588,"error":0,"elapsed_ms":47287}`
  即 **M4-b 在 2B 基线上是正常完成（47,287 ms）**；`pass=0` 只因参考预置漏写尾 2 字节（见 `s4d_m4b_tailword_20261029_r01/ANALYSIS.md`）。
- 之前"两个位流都 error=5"的观感来自**两次不同 ELF**：P2b 上那两次用的是旧冻结 ELF（`core_timeout=0x40000000` ⇒ 21.47 s 必然超时）或 chain-A ELF，不是同一份 M4-b ELF。
- 因此**同 ELF 的 A/B 是可行的**，已排窗口 `s4d_m4b_p2b_20261029_r01`（P2b 位流 + `aaedaf3c` M4-b ELF，150 s 结果窗）：
  - 若 P2b 上也在 ≈47 s 完成 ⇒ H1 的"慢 2×"结论需要降级（85.9 s 现象另有来源）；
  - 若 P2b 上 >150 s 未完成或 85.9 s 超时 ⇒ 与 H1 一致（≥1.8×，结构性 SMC 串行）。

## 边界

本备注只更正口径，不改 ANALYSIS.md 原文；未上板、未改源码、`ENABLE=0`、不主张 G3/G4/G5。