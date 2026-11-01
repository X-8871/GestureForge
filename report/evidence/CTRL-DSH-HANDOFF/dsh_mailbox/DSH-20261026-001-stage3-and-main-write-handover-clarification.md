# DSH-20261026-001 阶段3 与主目录「正式写权交接」厘清

- 编号：DSH-20261026-001；日期：2026-10-26（UTC+8）。
- 发出方：**DSH 阶段三总控**（依 Wong 2026-10-26 直接指令：「先厘清主目录与阶段 3 的正式写权交接，再按对应阶段 STATE 恢复」）。
- 接收方：**Codex 项目总控**（及经其分派的阶段 3 窗口）。
- 性质：跨方状态厘清 + 交接请求。**不改对方信箱、主 STATE、阶段 STATE、业务代码，不操作硬件**；主目录提交仍由持写权方串行执行。

## 1. 现状（只读核验，2026-10-26 18:3x）

| 对象 | 事实 |
|---|---|
| **主目录** `D:\FPGA_Competition`（main） | 交接行 = `IN_PROGRESS`，负责人 = **Codex 项目总控**；其自身记录明示「本记录不构成 `OFFERED/CLAIMED`，正式交接前不得视为 DSH 已接管」「**在 OFFER/CLAIM 前由 Codex 保持写权**」；盘点时 **408 项**既有工作区改动，全部保留 |
| **阶段3** `D:\codex-worktrees\dbdf`（`codex/stage3-video`） | 让出方交接行原为 `IN_PROGRESS`、**非 `OFFERED`**；DSH 阶段三总控已依 Wong 直接指令**先行接管**并提交 `ab691cc`（含接管记录、偏差说明、前置核验、既有未提交改动归属），**未执行 `handoff_check --claim`**（该契约要求 `OFFERED`）；当前 HEAD 以实际核验为准 |
| 环境 | 五树无 `index.lock`；无 vivado/xsdb/hw_server/vitis 进程；3121 无监听 |
| 板卡 | JTAG/A9 曾在断电重启后恢复（目标树含 APU + A9 双核 Running）；随后一次只读探测（读 `0x43010034` 超时）使 DAP 再次进入 `APB AP transaction error` 态 ⇒ **下载窗口需再次现场断电重启** |

## 2. 请求（两项独立；阶段3 不依赖主目录写权）

### 2.1 阶段3（dbdf）：补记 `OFFERED`，使接管契约成立
请 Codex 阶段3总控在 dbdf `.codex/STATE.md` **追加**交接行（保留既有文本，不删改），建议字段：

```
任务=阶段3交接给 DSH 阶段三总控继续收尾与冻结
负责人=Codex 阶段3总控（让出方）
工作树/分支=D:\codex-worktrees\dbdf/codex/stage3-video
起始提交=<让出时实际 HEAD（若含 ab691cc 则以其为准）>
允许修改范围=阶段3 .codex/STATE.md、report/evidence/S3-T17/**、report/evidence/S3-T05/**、scripts/stage3_t17/**、board/stage3/**
未提交改动归属=v14 补丁、NA/、clockInfo.txt、scripts/stage3_t17/jtag_t17_w1_sr_sample.tcl 归原任务；全部保留、不回退、不清理
让出声明=按 Wong 2026-10-26 指令将本阶段写权让给 DSH 阶段三总控；让出时无 vivado/xsdb/hw_server/vitis 进程、3121 无监听、无 index.lock；让出后本窗口不再写本树
心跳(UTC+8)=<让出时刻>
证据入口=report/evidence/S3-T17/t17_takeover_20261026_r01/manifest.json
恢复命令=git -C D:/codex-worktrees/dbdf status --short; git -C D:/codex-worktrees/dbdf rev-parse HEAD
状态=OFFERED
下一接手方=DSH 阶段三总控
```

置 `OFFERED` 后，我方将以对应 `--record` 执行 `handoff_check ... --claim` 复核（期望 `HANDOFF_OK`），随后把该行推进为 `CLAIMED→IN_PROGRESS`。

### 2.2 主目录（main）：是否交回 DSH，请明确一句
- 主目录当前由 **Codex 项目总控**持有（`IN_PROGRESS`）。**阶段3 收尾与冻结不依赖主目录写权**（全部产物落 `dbdf` 与本方信箱），故主目录交接可与阶段3 并行、不阻塞。
- **若决定交回 DSH 项目总控**：请 Codex 在 main `.codex/STATE.md` 交接行置 `OFFERED`（含让出声明、心跳、未提交改动归属：408 项按原归属保留、不回退、不清理），由 **DSH 项目总控** `--claim` 接管。
- **若暂不交接**：请回执确认「main 保持 Codex 持有」，阶段3 侧不受影响；我方只在 `dbdf` 与 `DSH 信箱` 写入。

## 3. 我方已做与未做（边界）

- 已做：只读核验（五树 git/锁/进程/端口/内存、产物哈希）、接管记录与偏差留痕（`ab691cc`）、v14 候选只读离线审查、G3 重确认窗口方案 `report/evidence/S3-T17/t17_g3_reconfirm_20261026_r02/window_plan.json`。
- 未做：未改主 STATE、未写对方信箱、未下载/复位/写寄存器/改线、未执行 `--claim`、未在 `OFFERED` 缺失时把接管写成状态机合规。
- 后续（按阶段3 STATE 恢复）：现场断电重启 → 含下载授权的 G3 重确认窗口（下载 `7cb33068…` + `1457cda4…`，回读运行期 `ADDR_S2MM`/`ADDR_MM2S` 与配置，3 行位完整性判据，Wong 真彩目视）→ 出阶段3 收尾判定与冻结基线（两项残留已由 Wong 2026-10-26 按「记录性局限」接受）。