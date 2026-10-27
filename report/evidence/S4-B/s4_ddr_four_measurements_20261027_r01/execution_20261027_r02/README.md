# S4-T31 四项实测 · 执行记录（窗口2，2026-10-27 20:53 开窗）

- 结论：**`STOPPED_AT_LOAD_THEN_M1`** —— 非技术结论，**不构成任何通过**。

## 结果（语义 vs 进程退出码）

| 阶段 | 语义 | 进程退出码 | 说明 |
|---|---|---|---|
| P0 门禁 | **PASS** | 0 | 无他方进程、3121 空闲、无 index.lock |
| P1 smoke | **PASS** | 0 | 三步：targets / 选目标（APU*）/ 只读 全 OK |
| 装载 LOAD | **FAIL** | 0 | `rst -processor` 报 `Invalid reset type`；**在任何 dow 之前失败 ⇒ 未下载任何载荷** |
| M1 CPU1 | **FAIL** | 0 | 脚本在 `info target`（非 xsdb 子命令）中断 ⇒ 无 state/PC 证据 |
| M2 consumer | **PARTIAL_INVALID** | 0 | `mrd` 返回 `ADDR:` 空值 ⇒ 无有效判定 |
| M3 写-回读 | **NOT_RUN** | — | FAIL 即停 |
| M4-a cache | **NOT_RUN** | — | FAIL 即停 |
| P4 清理 | **PASS** | 0 | 3121 已关、无残留进程 |

## 重要事实

- **候选区未被写入**：LOAD 在 `rst` 处失败，早于任何 `dow`；M3 未执行 ⇒ **无需恢复**（`ddr_written=false`）。
- 未发任何 `stop`；未改 `ENABLE`；未烧 QSPI；未 push；未改动 25 项遗留。
- **离线待修脚本缺陷**（窗口内未改）：①`rst -processor` 复位类型在 2026.1 不被接受；②`info target` 非 xsdb 子命令；③`mrd` 需按 `ADDR: VALUE` 解析。
