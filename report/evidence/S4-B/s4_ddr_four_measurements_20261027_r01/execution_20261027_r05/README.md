# S4-T31 第5窗口（Wong 方案A）执行记录

- 开窗 `2026-10-27T21:13:16+08:00`（见 `…/preparation/window5_open.txt`），收窗约 `21:22`。
- 驱动：**仅** `scripts/stage4_s4b/run_s4_ddr_four_measurements.py`（提交 `69731b9`，SHA-256 `502db86f…`）；**无任何临时 Tcl**。

## 结果

| 步 | 结果 | 真实退出码 | 说明 |
|---|---|---|---|
| P0 | **PASS** | 0 | 无他方 debug 进程、3121 无 LISTEN、无 index.lock；MCP 进程未被误判/未结束 |
| P0b hw_server | **PASS** | 0 | 由驱动自行启动（PID 记录），收尾由驱动停止并核验 3121 无 LISTEN |
| P1 smoke | **PASS** | 0 | 三步全 OK（第 4 次连续） |
| PRELOAD | **PASS** | 0 | `rst -system -stop` → `dow init.elf` → `con` → `dow m4a_cache_probe.elf`（位置参数、as_posix 路径） |
| M1 | **PASS** | 0 | CPU1 `Stopped: (Suspended)`；PC `ffffff34` 两次一致；`#0/#1` 均 Suspended |
| M2 | **PASS** | 0 | DevCfg STATUS `0x40000010`（PCFG_DONE=0）、两核 Suspended、唯一客户端 ⇒ 构造性排除 |
| **M3** | **FAIL** | 0（语义 FAIL） | `mwr` 无 `-pattern`（写入中止）、`mwr -bin -file` 缺字数（恢复未执行）⇒ 恢复校验不过即停 |
| M4-a | **NOT_RUN** | — | M3 FAIL 即停 |
| P4 清理 | **PASS** | 0 | 3121 无 LISTEN、无残留进程 |

## M3 现场与恢复（关键）

- 实际写入仅 **4 字节**：`0x12000000` `bfbd8604 → 00005a5a`（标记字 0x5A5A0000）。
- 驱动按规则**立即停**、保留快照（`m3_snapshot_orig.bin` 12,615,680 B）与三份 dump。
- **最小精确恢复**：`mwr 0x12000000 0x0486bdbf`（快照前 4 字节小端），随后 `mrd -bin -file` 复核：
  **前 16 字节与快照逐字节相等，差异 0**（`remediation_restore/remediation_result.json`）。
- 恢复期间单独启停 `hw_server`，结束后 `LISTEN=0 / PROCS=0`。

## 边界
未写候选区外地址；未烧 QSPI；未改 ENABLE；**未发独立 stop**；未 push；未动 25 项遗留；未结束 MCP 进程；M4-b `NOT_APPLICABLE`；**未解锁 ENABLE=1**。

## 证据更正（2026-10-27，按 DSH 项目总控逐字节核验）

- `m3_snapshot_restored.bin` **原命名与内容不符**：它装入的是**写入后回读**，不是恢复后镜像（与 `m3_readback_pattern.bin` 逐字节相同，sha256 `77c929ac…`）。已**正名**为 `m3_readback_after_write.bin`。
- `restore_method` = **4 字节精确回写**（`mwr 0x12000000 0x0486bdbf`，即快照前 4 字节 `bfbd8604` 小端）；
  `post_restore_readback` = **16 B**（`remediation_restore/fix_readback16.bin`，覆盖唯一被写字节）；
  `full_region_post_restore_dump` = **NOT_CAPTURED**；
  `inference` = **仅写过 4 字节且已按快照回填 ⇒ 区域等价于原状**（依据 `m3_snapshot_orig.bin` 与 `fix_readback16.bin` 前 16 B 逐字节相等）。
- 差异证据：`orig vs readback_after_write` **恰为 4 字节**，偏移 `0x0–0x3`，值 `bf bd 86 04 → 00 00 5a 5a`，**与写入范围一致**。
- 详见 `m3_restore_provenance.json`。
