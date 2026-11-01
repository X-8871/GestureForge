# 4-D PS 长跑（口径 A：≥30 min 连续 / ≈150 帧）—— 判据（**窗口执行前写死，不得放宽**）

- 任务：S4-T34，RunId `bringup_longrun_20261028_r01`
- 目标：在 2B 平台位流上，以 **SW 预处理（PS 实现）** 的链路连续长跑 ≥30 min，验证链路稳定性
  （每轮 START → DONE_SAFE → invalidate → 解码 → ACK 回 idle）。

## 0. 固定输入与身份（窗口 IDENT 必核）

| 项 | 值 |
|---|---|
| 位流 | `s2b_inference.bit` SHA-256 前缀 `555a70c2…` |
| 初始化 ELF | `init.elf` `237dd959…` |
| **长跑 ELF** | `s4d_ps_app_sw0_longrun.elf` **`f9951d78d3fbbb50d280e0740d2fc3e989fcd85a4ecf9af67427b6ec58177031`**（271,904 B） |
| 驱动 | v3.2.6 `311ef177…` |
| fixture RAW（640×480 BGR888） | `ce37aa772aec9d45084edc37f3a1e0fe1b258385ec57b1fd994d98614792dad4`（**FIXTURE_GENERATED 非实拍**） |
| 权重 GF8 | 5,903,100 B（SHA 见 `fixture_manifest.json`） |
| 离线张量 CRC-32 | `0x5B183B50`（与 chain-lite-B 同一 fixture 口径） |
| 离线参考框 | `bringup_chainlite_b_20261028_r01/offline_reference_boxes.json` |
| M3 快照 | `41907f53…` |

## 1. 判据（**事先写死**）

| 编号 | 判据 | 来源 |
|---|---|---|
| LR-1 | `wall_ms >= 1,800,000` | 应用汇总 `LONGRUN RESULT.wall_ms_*`（高低 32 位拼接） |
| LR-2 | `iterations >= 140` | 同上 |
| LR-3 | `failures == 0` | 同上 |
| LR-4 | **每轮** `status == 0x00000E04`（DONE_SAFE + HEAD_VALID + SAFE_REUSE + TERMINAL）且 `error == 0` | 应用内逐轮校验；失败即停并打印 `LONGRUN FAIL iter=…` |
| LR-5 | **每轮** `decode_rc == 0`、`count == 1`、`raw == 2`、`ack_idle == 1` | 同上 |
| LR-6 | 框 8 字段**逐轮逐位一致**（与第 1 轮 bit-identical：class/order + 5 个 double 的 IEEE 位模式） | 应用内 `s4d_lr_box_equal` |
| LR-7 | `epoch` 单调递增 | 应用内校验 |
| LR-8 | 第 1 轮框与离线参考 `offline_reference_boxes.json` **abs diff ≤ 1e-9** | 主机侧 W3 比对（板端打印 `LONGRUN BOX` 位模式） |
| LR-9 | 应用汇总 `exit == 0` 且 `within_judgement == 1` | `LONGRUN RESULT` |

## 2. 停止规则

- 任一轮失败 ⇒ **应用自身立即停**并打印 `LONGRUN FAIL iter=<n> why=<原因> status=… error=… decode_rc=… count=… raw=… ack_idle=… elapsed_ms=… spin=…`；驱动收尾并保 UART 原文；
- `W0`/`W4` 候选区 `diff != 0` ⇒ 停；
- 窗口时间到 ⇒ 收尾（不中途改判据）；
- 运行期**不轮询 `mrd`**、不做其他板级动作；`ENABLE=0`、不烧 QSPI、不改线；禁 `-force`、禁 JTAG 直探 CSR。

## 3. 预算

1800 s 运行 + 装载/两次恢复 ≈ 8 min ⇒ 40 min 内可完成（窗口上限 45 min）。
UART 采集上限 **2100 s**（35 min）；应用侧每轮一条进度（每 10 轮）+ 失败即时 + 结束一行汇总，避免刷爆串口。

## 4. 边界

覆盖 **2B 平台位流 + SW 预处理（PS 实现）**；fixture 为生成样例（非摄像头实拍）；
**不主张 G3/G4/G5**；M3/M2 未闭合；`ENABLE=0`、未写 QSPI、未改线、未 push。

## 5. 本轮状态

- 离线阶段：长跑 ELF 已构建（新 SHA，见上表）、离线自检 `verify_longrun_v1.py` **7/7 PASS exit 0**；
- 窗口阶段：**待 lead 签发后执行**（本 README 于窗口前写定，执行结果另见 `results_longrun.json` / `window_close.txt`）。