# 长跑静默停住 · 离线根因分析（S4-T34，2026-10-28 r01）

- 事实：`bringup_longrun_20261028_r01` 跑到 **iter=40（wall 461,117 ms）** 后**无任何 UART 输出**，
  无 `LONGRUN FAIL`、无 `LONGRUN RESULT`；40 轮内每轮 `elapsed_ms=11821`、`status=0x00000E04`、`error=0`、
  `epoch_lo=1→40`、`ack_idle=1`、首轮框与离线参考 **abs diff 0.0**。
- 结论：**不是判据失败，而是在不可中断操作中停住**（应用未进入 fail-fast 分支）。

## A1 应用侧（无无界循环）
| 等待/循环 | 上界 | 位置 |
|---|---|---|
| 主循环 | `iter<=160` | app `for (iter = 1u; iter <= S4D_LR_MAX_ITERS; …)` |
| 等 DONE_SAFE | `spin<1.5e8` **且** `wall>=120 s` | app `for (spin = 0u; spin < S4D_M4B_SPIN_MAX; …)` |
| 读 epoch | ≤8 次重试 | `s4d_read_epoch` |
| START 前等 idle / ACK 回 idle | 单次读，无循环 | app L894 / L677 |
| invalidate 后 | 仅 cache 维护 + DSB | `s4d_region_invalidate` |
- 无跨轮增长的缓冲/指针；`det[15]`、`first` 固定复用。
- **应用未安装数据中止处理器** ⇒ 若 CSR 写返回 SLVERR，CPU 取数据中止后无输出停住（交待清楚）。
- `xil_printf` 的 UART TX 等待是无界的（次要可能，未排除）。

## A2 2B RTL 侧（`w2b/src/s2b_control_csr.sv`，blob `f614c93d…`）
| 项 | 事实 | 评估 |
|---|---|---|
| `epoch` | 64 bit（L49），START 接受 +1（L245），全 1 饱和保护（L241） | 40 远未回绕 |
| `ack_pending` | 写入 ready 被其否决（L92/93/109）；ACK 时若 `status_shadow[2:1]≠0` 则置位并挂起 B 响应（L270）；`clear_safe` 才清（L296） | **若常置 ⇒ 后续所有 CSR 写永久停等** |
| `first_selected/first_pending/visibility_confirmed` | ACK 前置（L182-184）；每轮重置（L246/L293/L296） | 未见随次数累积；`visibility_confirmed` 抖动会**静默拒 ACK** |
| `ledger` | ACK 前置；`status[12]=!ledger_empty_next` | 账本未闭合 ⇒ ACK 被拒（SLVERR） |

## A3 平台先例（决定性）
`w2b/.codex/STATE.md`（blob `da6ae3b1…`）原文：
> CPU原生postmortem保存**DFSR1808/DFAR43C00008**/PC C344/**STR e5801000**/LAST_REJECT变化，独审判**SLVERR**

`DFAR=0x43C00008` = **写 START 寄存器**；与本轮“静默停住”现象**同源**。
**2B 的重复覆盖**：模型/仿真做过 **1109 次 RUN**（T18，非实板）；实板 R08 只做“忙 START 拒绝/ACK/重接受”，
**未记录 ≥40 次连续 START 的实板长跑** ⇒ 该路径很可能**首次触达**。

## A4 定位（第 41 轮）
最后一次输出在 `iter=40` 的进度行（ACK 之后），第 41 轮首个 AXI 操作依次为：
`读 epoch(0x50/0x54) → is_idle(0x0C) → 7 次写(0x14..0x2C) → 写 START(0x08) → 等 DONE`。
**最可能停点：第 41 轮的首次 CSR 写（L898 写 0x014）**——若上一轮 ACK 留下 `ack_pending=1` 或状态非
`IDLE_PS`，写返回 SLVERR → Cortex-A9 数据中止 → 无输出。

候选排序：① CSR 写 SLVERR→数据中止（与 T20 同源）；② `ack_pending` 常置→写停等；③ `q.rvalid` 未清→读停等；④ UART TX 阻塞。

## B 仪表化方案（下一步实现）
- 心跳**每轮一行**；每步把 `step_id|iter<<8` 写到 **0x11B00000**；
- **安装数据中止处理器**（`Xil_ExceptionRegisterHandler(XIL_EXCEPTION_ID_DATA_ABORT_INT, …)`），
  记录 `DFSR/DFAR + 当前 step` 到 0x11B00000 后停机 ⇒ 主机一次普通 `mrd` 即可定位；
- 收尾清零 0x11B00000，W4 校验“候选区 diff=0 且魔数区全 0”；
- **如实说明**：AXI 访问无法在软件侧限时，故以“每步魔数 + 中止处理”替代“每步有界超时”。

## 依据清单（含 `hash_basis`）
| 文件 | 位置 | hash_basis | 哈希 |
|---|---|---|---|
| `w2b/src/s2b_control_csr.sv` | L49/92/93/107/109/182-184/237-241/245-246/L270/L293-296/L338-339 | `commit_blob` | `f614c93d…` |
| `w2b/.codex/STATE.md` | T20 postmortem 行（DFSR/DFAR/STR/SLVERR） | `commit_blob` | `da6ae3b1…` |
| `w2b/docs/.../s2b_physical_interface_candidate.md` | L94 AXI-Lite 写槽位契约 | `commit_blob` | `682b96f1…` |
| `vitis/stage4/ps/s4d_ps_app.c` | 长跑循环与等待 | `worktree_disk` | `0a97ace45a16e842…` |

## 边界
离线分析；未上板；不改判据；`ENABLE=0`；不主张 G3/G4/G5；M3/M2 未闭合。
