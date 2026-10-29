# M4-b 阻塞记录：`ERROR_SAFE / error=5` = 内核 TIMEOUT，但与实测运行时间不自洽（2026-10-29 21:2x）

- 现场：`s4d_p2b_4d_reverify_20261029_r03`（P2b 位流）与 `s4d_m4b_baseline_2b_20261029_r01`（2B 基线位流）
  **完全相同的 RESULT**：`done=2 status=0x0C05 error=5`、`diff13=0 diff26=0 first13/26=-1 stale=1 gate=1 ack_idle=0 epoch=1`。
  UART 逐行：`STEP=1 id=0x53324250 ver=0x00000100` → `STEP=2 status=0x00000400` → `STEP=5 START` →
  `STEP=6 TIMEOUT wait spin=0 status=0x00001102`（RUN + OWNER_PL + AXI_PENDING）→
  `STEP=6 TIMEOUT wait spin=1 status=0x00000C05 error=0x00000005`（ERROR_SAFE + TIMEOUT 码）。

## 1. 已定位的事实（RTL 级）

| 事实 | 出处 |
|---|---|
| `error_code=5` 的唯一定义 = **TIMEOUT**（不是 BAD_RANGE/BAD_LENGTH/OVERFLOW） | `w2b/src/s2a_control_csr.sv:59` `TIMEOUT_ERROR = 3'd5` |
| 超时判据：`busy` 期间 `(elapsed_cycles + 1) >= timeout_cycles` ⇒ 置 `TIMEOUT_ERROR` | `s2a_control_csr.sv:244-250` |
| `elapsed_cycles` 在**被接受的 START** 时清 0，busy 期间每核时钟 +1 | `s2a_control_csr.sv:186`、`:250` |
| 2B wrapper 的 ARMING 序列只转发 7 项：frame/input_addr/input_bytes/weight_addr/weight_bytes/**core_timeout(0x28)**/START；**不转发 drain_timeout** | `s2b_control_csr.sv:150-172` |
| 应用写 `core_timeout = drain_timeout = 0xFFFFFFFF` | `vitis/stage4/ps/s4d_ps_app.c:325` |

## 2. 不自洽之处（为什么还不能判"跑太慢"）

- `timeout = 0xFFFFFFFF` ⇒ 超时点 ≈ 4.29e9 个核时钟：50 MHz 下 **85.9 s**，100 MHz 下 42.9 s。
- 同一应用在长跑窗口实测每帧 **47.3 s**（`bringup_longrun_probe_20261029_r05`，40 轮恒定），
  按 50 MHz 计 ≈ 2.37e9 周期 < 4.29e9 ⇒ **不应超时**。
- 而 UART 只打了 **两次** `STEP=6 TIMEOUT wait`（spin=0/1），说明从 START 到终态的时间远小于 85.9 s。
- 与此同时 `diff13=0 / diff26=0`（运行前 `stale=1`）⇒ 若属实，head 输出与参考**完全一致**，
  即网络算完了才进 TIMEOUT —— 与"时间不够"矛盾。

⇒ 现在有两个互斥解释，必须用波形或寄存器时间戳区分：
1. **超时值被截断/转发错误**（wrapper 只转 32-bit，但若有窄化或时序错位，内核看到的 timeout 很小）；
2. **`elapsed_cycles` 被污染**（例如 START 未被内核接受而旧 busy 仍在计数，或 1 个核时钟 ≠ 应用侧 1 个 GT 周期）。

## 3. 建议的下一步（按性价比）

1. **只读取证**（无需改 RTL，1 个 2 分钟窗口）：M4-b 前后读 `0x028`（core_timeout）与 `0x010`（error_code）回读，
   确认 wrapper 侧的 timeout 寄存器确实是 `0xFFFFFFFF`；同时读 `0x050/054`（epoch）与 `0x058`（frame）确认 START 被接受。
2. 若配置回读正确 ⇒ 需要 ILA/波形看内核 `elapsed_cycles` 与 `busy`，属 2B 侧专项（建议交 Codex，2B 是其写区）。
3. 也可以先用**大 frame 输入不变、把 timeout 设为 0xFFFFFF00** 做对照（差值仅 256 周期），若仍立刻超时则证实是"计数器未清零/被污染"而非"跑太慢"。

## 4. 边界

本文件只做离线定位，不替代板上实测；未主张 M4-b 通过。`ENABLE=0`；不写 QSPI、不改线、不 push。