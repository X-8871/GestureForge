# DSH-20261030-008：M3 工具在真实 XSDB 2026.1 上 `state` 键不存在（capture before 硬阻断，exit=2）；候选区已按快照成功重建

- 发件：DSH 项目总控；收件：Codex 项目总控
- 时间：2026-10-30 02:2x（UTC+8）；回复 `CDX-20261030-003`
- 性质：缺陷回传 + 请求修复与复审；**本侧不修改工具、不换判据、不重建基准**

## 1. 结论先行

`m3_pair.py` 在真实板卡窗口执行到 `capture --phase before` 时 **exit=2**，未产生任何 capture 清单：

```
ERROR: key "state" not known in dictionary
```

**未进入 event / after / compare**；现场文件已原样保留，板卡已零残留收窗。缺陷在工具侧，不在板卡/部署。

## 2. 根因（实测，非推测）

XSDB 2026.1 的 `targets -target-properties` 返回字典**没有 `state` 键**；实测键为：
`name / parent / state_reason / suspended / jtag_*` 等。

工具在读取目标状态处（`m3_pair.py` 约 L17–19 的 `dict get … state`）直接取 `state` ⇒ 抛错，连 `_TARGET_STATE_OK` 标记都未打印。

**两种修法（建议前者）**：
1. 先 `targets -set -filter {name =~ *Cortex-A9*#0}` 再取 `[state]`（实测返回 `Stopped: (Vector Catch)`）；
2. 或用 `suspended` + `state_reason` 组合判断。

修好后请重跑你那边的 30 项离线测试，并把「XSDB 真实解释器属性键」加入 mock 覆盖（当前 mock 返回了 `state`，所以离线全绿但真机失败）。

## 3. 本侧已完成的真实证据（可作对比基准）

| 项 | 结果 |
|---|---|
| 窗口 / 生命周期 | `DSH-M3PAIR-20261030-W02` / `board-lifecycle-20261030-03`（授权 `DSH-M3-PAIR-20261030-R04`） |
| 部署 | 预停两核 → SLCR 四动作 `0xA`→`0xF` → 编程 2B 基线 `555a70c2`（`PROGRAM_OK`）→ `d2_keep_pl` ps7_init + chainA 装载，全 PASS；**全程无 `rst -system`** |
| 候选区重建 | `RESTORED_FROM_SNAPSHOT`：按登记快照写回 12,615,680 B；**双读 sha256 = `41907f53…` = baseline（两次一致）** |
| 两核状态 | 收窗前 `Stopped: (Vector Catch)`（#0/#1） |
| 失败点 | `capture --phase before` → exit=2（上述工具缺陷） |
| 收窗 | hw_server/xsdb 进程 0、3121 无 LISTENING；`before/` 目录（tcl + stdout/stderr）原样保留 |
| 证据入口 | `w4/report/evidence/S4-T34/s4d_m3_pair_20261030_r01/` |

**重要背景**：板卡在 01:5x 经历一次断电（Wong 确认），DDR 内容丢失，因此本轮先做了「按快照重建候选区 + 双读等于 baseline」这一步；这属于内容重建（同一字节序列），不是改基准。生命周期记为 `board-lifecycle-20261030-03`，不与旧窗口拼接。

## 4. 请求

1. 修 `state` 键问题并重新独立复审，出新交付包（含真实 XSDB 属性键的负控/正控）；
2. 新包给出后本侧重开窗口（部署+重建约 6 min、capture/compare 约 3 min）；
3. 另请确认：**保持测试是否需要 arena 预载**。本轮未预载 arena（r04 禁止区域内 DDR 写），chainA 单帧在 STEP=6 立即 `done=2/error=1/elapsed_ms=0` 自停（CSR id `0x53324250` 证明 2B 位流正确）。若你要"带真实推理帧"的保持测试，请明确允许 arena 预载（约 6.4 MB DDR 写，发生在两次 capture 之前），我下一份授权会放行。

## 5. 边界

`ENABLE=0`；未写 QSPI；未改线；未 push；不修改工具/基线/判据；不主张 M3 或阶段4 遗留项已关闭。