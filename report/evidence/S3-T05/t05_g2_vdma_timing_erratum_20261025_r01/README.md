# 阶段3完整 G2：VDMA 时序勘误 r01

- RunId：`t05_g2_vdma_timing_erratum_20261025_r01`
- 时间：2026-10-25（UTC+8）
- 复核基线：`D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`，HEAD `584b07664e88a18bf786ba9565a138861e136d76`
- 触发：完整 G2 Reviewer 在固定 HEAD `584b076` 上返回 `CHANGES_REQUIRED`，指出 G2 r02 把应用 `phase=0` 首读与 `t=5 s` 读数合并写成“启动值”。
- 边界：本勘误只更正时间点，不重写旧 RunId/旧材料，不定位根因，不把 VDMA 从 `PARTIAL` 升级。

## 更正后的观测顺序

| 观测 | S2MM_SR | 依据 |
|---|---:|---|
| 应用 UART `phase=0` 首读（两次独立启动） | `0x00014810` | `uart_v11.stdout`、`uart_restore.stdout` |
| 应用 UART `t=5 s` 首读及后续样本 | `0x00015810` | 同上 |
| 单独的只读探测 `probe_00_startup.txt` | `0x00015810` | `vdma_sticky_result.md` §1 |
| 一次 W1C 前 → 后 | `0x00015810` → `0x00011000` | `vdma_sticky_result.md` §2 |

`0x00014810 XOR 0x00015810 = 0x00001000`：应用 UART 的 `phase=0` 样本已有 bit11（`0x800`）、bit14（`0x4000`）和 bit4（`0x10`）；到 `t=5 s` 只新增 bit12（`0x1000`）。独立 `probe_00_startup.txt` 的 `0x00015810` 是另一时点的只读探测，不能替代 `phase=0` 首读。清除 `0x15810` 后，31 分钟 7 次回读保持 `0x11000`，表示清除后未重现错误位，不说明启动置位的触发源。

## 对旧 G2 r02 的取代范围

- `g2_material_list_r02.json` 中 `vdma_sticky.startup_value=0x00015810` 与其 README 中“启动时读到 0x15810”的时间表述，现由本勘误取代；应按上表分别记录 `phase=0`、`t=5 s`、独立只读探测和 W1C 前值。
- r02 其它 G2 事实与哈希绑定不因此改变；r02 原始字节和失败审查状态均保留。
- VDMA 仍 `PARTIAL`、根因 `OPEN`；bit11 的位义及快照不能区分具体触发分支，也不能据此声称“零错误”。完整 G2 需 Reviewer 对固定原包加本勘误复核后才能判定。

## 固定来源 SHA-256

- G2 r02 README：`FB8DCD62480F56D96186D45F5A4CA19439A913AD0F525B78C08CDE7E451D465E`
- G2 r02 JSON：`2284153EB49DB274CFA8A7D1FA3DCA468186C24A1BD201624B6EA672CD0848CF`
- 板级窗口 README（含此前 N-4 时序更正）：`D9C6190E76ACE6878AE264D1A43A185D3B8A257E34AAA97A7B8A167FF3595D61`
- `vdma_sticky_result.md`：`1B88969AD26BAA215B02C30A73CD41BEA34DBFC1CF40C22C063DF453F198CADA`
- 原始 UART `uart_v11.stdout`：`D18AB2B3AAAD6F5B9F1AEF2DE6526504DC1118FA2B9031AA2F556615495DB51C`
- 原始 UART `uart_restore.stdout`：`72FA0E45F3BDD131F75223583A582784FABDFE8CC52A28171A18900196B7B846`
- 离线根因补充：`12B6E384944A3EF8A0C5CCB19B1D0A1F49F542AC2EEA3928C49EAD521EBD534A`
