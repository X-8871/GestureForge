# S4D 4-D bring-up 计划与 M3/M4-a/M4-b 验收判据（2026-10-27 r01，离线编写）

- 任务：S4-T32 Phase 3 交付（计划与判据）。**本文件不执行任何板级动作**；bring-up 窗口由 DSH 依 Wong 授权另行签发。
- 前置：Phase 2 构建产物（bit/XSA/ELF）齐全且登记完整 SHA-256；地址图 RAW/META 已登记 owner 并解除 `BLOCKED`；`ENABLE=1` 另行批准（**本次不解锁**）。
- 总预算：**≤45 min / 窗口**，超时即收窗留证。

## 0. 第 0 步（窗口开门前 5 min，全部只读）

| # | 检查 | 判据 |
|---|---|---|
| 0.1 | 他方调试进程 | 无 `hw_server`/`xsdb`/`vivado` 精确镜像名进程（`vivado-mcp-server-*` 属 MCP 包装，**不结束、不误判**） |
| 0.2 | 3121 | 只看 `LISTENING`；`TIME_WAIT` 不计、不清理 |
| 0.3 | 门禁文件 | 无 `.git/index.lock`；开窗指令存在 |
| 0.4 | 载荷身份 | bit/XSA/ELF/驱动 SHA-256 与 `payload_registry_4d.json` 逐项一致（不符即停） |
| 0.5 | 串口 | COM4 未被占用（115200 8N1） |
| 0.6 | 记录 | 写 `window_open.txt`（UTC+8）+ P0 结果 JSON |

## 1. 装载与初始化（≤8 min）

1. `hw_server -s tcp::3121`（或由驱动自启）；`xsdb` 连 `tcp:127.0.0.1:3121`。
2. `targets -set -filter {name =~ "*Cortex-A9*#0*"}` → `rst -system -stop`（**整系统复位并挂起全部核**，不执行独立 `stop`）。
3. `dow <init.elf>` → `con` → 等 PS/DDR 就绪（~6 s）。
4. `dow <s4d_app.elf>`（4-D 应用；**不 con**，留待 M1/M2/M3 后再启动）。
5. 取证：`targets` 回显必须含 `#0 (Suspended)`、`#1 (Suspended)`。

## 2. M3 判据（候选区写-回读 + 恢复）——用修复版 `m3_candidate_rw.tcl`

| 判据 | 要求 | 不满足 |
|---|---|---|
| M3-1 | 快照：整区 `[0x12000000,0x12C08000)` 12,615,680 B 只读落盘 + SHA-256 | FAIL |
| M3-2 | 写入：**图案文件**（主机预生成，`mwr -bin -file <file> <addr> <words>`）整区写入，退出码 0 | FAIL |
| M3-3 | 回读：整区回读落盘，退出码 0 | FAIL |
| M3-4 | 占用判定：回读与图案文件**逐字节相等** ⇒ 区域未被占用（PASS）；不等 ⇒ 记录差异偏移表，仍须继续恢复 | 差异即 FAIL（但必须恢复） |
| M3-5 | 恢复：`mwr -bin -file <snapshot> <addr> <3153920>`（**必须带字数**），退出码 0 | FAIL 即停 |
| M3-6 | **整区恢复后 dump 必须采**：再次整区回读落盘，与快照 **逐字节差异必须 = 0** | 差异≠0 ⇒ 立即停、保留现场 |
| M3-7 | 证据 | `m3_snapshot_orig.bin`、`m3_pattern.bin`、`m3_readback_pattern.bin`、**`m3_post_restore.bin`**、各自 SHA-256、差异偏移表、真实退出码 |

> 历史教训（窗口5）：`mwr` 无 `-pattern`、`mwr -bin -file` 缺字数 ⇒ 未真正写入/恢复；本判据已按修复版脚本固化，且**不得**再用"restored"命名装写入后镜像。

## 3. M4-a 判据（cache 维护/可见性，最小 ELF）

用 `m4a_cache_probe.elf`（SHA `fa8f22e0…`）+ `init.elf`，UART 命令 `R/I/F/W`，在候选区内 1 KiB 子区间：

| 判据 | 要求 |
|---|---|
| M4a-1 | JTAG 读原值 → UART `R` → PS CRC 与 JTAG 字节 CRC 一致 |
| M4a-2 | JTAG 写图案 → UART `F`（flush+invalidate）→ PS CRC == 图案 CRC |
| M4a-3 | JTAG 恢复原值 → UART `I` → PS CRC == 原值 CRC |
| M4a-4 | UART `W`（PS 写图案 + flush）→ PS CRC == 图案 CRC；随后 JTAG 恢复并逐字节校验差异 0 |
| M4a-5 | 任一 CRC 不符 ⇒ M4-a=FAIL；收尾**不 stop** |

## 4. M4-b 判据（**4-D 真实 DMA 路径**的 cache 一致性）——本卡重点

> **必须用 4-D 真实 DMA 路径实测**：PL 经 HP0（`infer_M_AXI`，64 位）读写 DDR，**不得**用 CPU 侧自证、离线仿真或静态分析替代。任一判据不满足 ⇒ **M4-b=FAIL**。

| 判据 | 方法与阈值 |
|---|---|
| M4b-1（PS→PL 可见性） | PS 写 RAW 帧（BGR888，109 清单内）→ `Xil_DCacheFlushRange`（64 B 外对齐）→ `DSB` → 启动 PL 预处理；PL 读到的 RAW 与 PS 写的帧**逐字节一致**（PL 侧 CRC 经寄存器/AXI-Lite 回读，PS 侧独立算 CRC） |
| M4b-2（PL→PS 可见性） | PL 写冻结 tensor（519,168 B）→ `tensor-valid` 置位 → PS `Xil_DCacheInvalidateRange(tensor)` → PS 读回的 519,168 B 与**同一 RAW 的冻结 D2 direct reference** 逐字节相等（全量 SHA-256 比对） |
| M4b-3（完成序门控） | 只有 `ledger empty` + `tensor-valid` 同时成立后 PS 才允许读 tensor；注入"提前读"用例（在 `tensor-valid` 前读）必须被门控拒绝（读到的不是半成品、且状态位报错），否则 FAIL |
| M4b-4（反向陈旧检测） | PL 写新 tensor 后、PS 未 invalidate 直接读，允许读到旧值；invalidate 后必须读到新值；若 invalidate 后仍读旧值 ⇒ FAIL（说明维护失效） |
| M4b-5（重复与覆盖保护） | 未 `RESULT_CONSUMED` 时新结果不得覆盖；重复消费必须被拒（状态位/错误码可查） |
| M4b-6（≥30 min / ≥1000 次） | 连续运行 ≥30 min 且累计 ≥1000 次有效推理（ADR §8.7；无 1800 s 上限），逐帧记录 session/frame/result_seq、PL grant tick、host 首写事件、COMMIT、tensor done、network/result done、错误与恢复 |

- 证据：UART 原始日志 + `tensor` 全量 dump SHA-256 + 逐帧 CSV/JSON + AXI-Lite 状态快照 + 差异偏移表。
- **不得**以"离线构建成功""仿真一致""CPU 自证"替代 M4-b 的任何一条。

## 5. 分段预算（≤45 min）

| 段 | 预算 | 内容 |
|---|---:|---|
| S0 | 5 min | 第 0 步门禁 + 启动 hw_server |
| S1 | 8 min | 装载/初始化 + `#0/#1 Suspended` 取证 |
| S2 | 3 min | M1 复核（CPU1 halted，PC 两次一致） |
| S3 | 3 min | M2 复核（DevCfg `mrd -value`；构造性排除） |
| S4 | 12 min | **M3**（快照/写入/回读/恢复/**整区恢复后 dump**） |
| S5 | 6 min | M4-a（UART R/I/F/W） |
| S6 | 8 min | **M4-b 启动**（真实 DMA 路径；判据 M4b-1..M4b-3 首轮，长跑另开窗口） |
| S7 | 5 min | 收尾（停 hw_server、3121 无 LISTEN、汇总） |

> M4b-6（≥30 min/≥1000 次）**必然超出单窗口**：按 ADR §8.7 作为**独立长跑窗口**安排，本计划只做首轮判据 + 长跑前置检查。

## 6. 停止条件（任一命中 ⇒ 立即停、保留现场、报 DSH）

1. 载荷 SHA 不符；2. 需写候选区外地址；3. M1 失败（CPU1 非 halted）；4. M2 无法排除 PL master；5. **M3 恢复差异 ≠ 0**；6. **M4-b 任一判据不符**；7. 复位/挂死/串口异常/异常退出；8. 超 45 min 或 DSH 叫停。

## 7. 恢复入口

- 候选区原字节：`m3_snapshot_orig.bin`（本窗口快照）+ `mwr -bin -file … <addr> <words>`；恢复后必须整区 dump 与快照差异 0。
- 板卡：`rst -system -stop` 后重新下载载荷；不 QSPI、不改线、不改 `ENABLE`。
- 证据回放：`results_4d_bringup.json` + 各步 `*.exit_code.txt`（真实退出码）+ dump SHA-256。

## 8. 明确未做 / 不适用

- 本卡**不含板级动作**：无 hw_server/xsdb 启动、无装载、无烧录；`ENABLE=0`；未 FROZEN。
- M4-b 的**长跑**（≥30 min/≥1000 次）不在单窗口内，另批；本计划不把它标记为已满足。
- 显示叠加（阶段5）不在本卡验收范围。