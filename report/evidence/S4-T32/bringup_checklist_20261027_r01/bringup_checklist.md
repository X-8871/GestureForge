# 4-D bring-up 执行清单（定稿 r01，2026-10-27）

- 用途：**一次 60 min 板级窗口**内跑完 bisect → DDR 位测试 → M4-a → M4-b → M3 复检，证据可复核。
- 前置依赖（缺一不可）：**4-D 位流 `s4d_preproc.*`**（新身份，不覆盖 `c7efcb72…`/`555a70c2…`）。
- 板卡状态：**已释放给阶段6**（`DSH-20261027-010`）；本清单**不得**在未获授权时执行。

## 0. 开窗前检查（5 项，任一不满足即停）
| # | 检查 | 通过判据 |
|---|---|---|
| 0a | 窗口授权 | lead 明确"开窗"指令 + 证据目录 `window_*/` 不存在（新 RunId） |
| 0b | P0 门禁 | 3121 无 LISTENING（TIME_WAIT 不计/不清）；无 `hw_server`/`xsdb`/`vivado`；无 `.git/index.lock`；COM4 空闲；**不判断/不结束任何含 mcp 的进程** |
| 0c | 载荷哈希 | 4-D bit / XSA / init.elf / M4-a ELF / M4-b ELF / DDR 测试快照区参数，全部与登记 SHA 逐一比对通过 |
| 0d | 工具版本 | 驱动 v3 已提交且 SHA 已核对（含 bisect + DDR 位测试段） |
| 0e | 边界确认 | `ENABLE=0`；不烧 QSPI；不改线；不发独立 `stop`；不 push |

## 1. 分段与时间盒（60 min）
| 段 | 内容 | 预算 | 判据 |
|---|---|---|---|
| S1 | bisect（3 次整区只读 dump：复位后 / 装 PL 后 / init+con 后） | 6–8 | 四选一结论写入 `bisect_result.json` |
| S2 | DDR 位图样测试（`0x11AE0000–0x11B00000`，128 KiB，4 图样 × T0/T1/T2，收尾按快照恢复 diff=0） | 5–8 | T0–T2 全等 ⇒ PASS；任一单 bit 差异 ⇒ `DDR_BIT_ERROR_SUSPECTED` |
| S3 | M4-a（`rst -processor -stop` → `con` → `M4A READY` → R/F 对拍 → W 后恢复逐字节） | 6 | 全过 ⇒ PASS；无横幅 ⇒ FAIL 即停 |
| S4 | M4-b 首轮（8 步 + 首拍门控 + head13/head26 逐字节 + ACK → `is_idle`） | 10 | 全过 ⇒ PASS；首拍 DONE ⇒ INCONCLUSIVE（不记 PASS） |
| S5 | M3 整区复检（只读 dump vs `41907f53…`） | 12 | diff=0 ⇒ PASS；否则 FAIL/未闭合 |
| S6 | 收尾（disconnect → 停 hw_server → 3121 核验 → 结果 JSON） | 5 | 3121 无 LISTENING、无残留 |
| — | **合计** | **44–49 min**（余量给重试禁止项留白，不用于重试写入） | — |

**顺延规则**：时间不足时按 `S4 → S5 → S2T3 → S1` 的反向优先级放弃（M4-a/M4-b 优先保住）；放弃项记 `NOT_RUN（时间不足，未降判据）`。

## 2. 证据格式（每段统一）
```
<run_dir>/
  window_instruction.txt            # 开窗指令原文 + 起止时间
  S1_bisect/{D0.bin,D1.bin,D2.bin,*.sha256.txt,*.exit_code.txt,bisect_result.json}
  S2_ddr/{snapshot.bin,readback_<pat>_T<n>.bin,restore.bin,restore_verify.json,ddr_result.json}
  S3_m4a/{*.log,*.exit_code.txt,m4a_result.json,uart.log}
  S4_m4b/{m4b_uart.log,m4b_result.json,*.exit_code.txt}
  S5_m3/{recheck_dump.bin,recheck_result.json,*.exit_code.txt}
  S6_teardown/teardown.json
  results_window_<id>.json          # 汇总：逐步 status + 真实退出码 + 结论 + 未做项
  landing_manifest.json             # 内联 hash_basis=commit_blob + hash_basis_commit
```
门禁：`check_manifest_hash_basis.py --mode strict` **必须 exit 0**。

## 3. 停止条件（任一命中即停、保留现场、报 lead）
1. 任一步真实退出码 ≠ 0；
2. M3/恢复 diff ≠ 0；
3. 同一状态两次 dump 互不相同（`READ_UNSTABLE`）；
4. DDR 任一处单 bit 差异（记 `DDR_BIT_ERROR_SUSPECTED`，不记 PASS）；
5. 时间到 60 min；
6. 出现任何非预期总线/进程干扰（如他方 session 占用）。

## 4. 恢复入口（窗口中断后）
- **不重跑已完成段**：以 `results_window_*.json` 中最后 `PASS/NOT_RUN` 段为起点；
- **不重复写 DDR**：若 S2 已写入但未完成恢复 ⇒ 仅允许"按快照恢复 + diff=0 校验"，**不得**再写新图样；
- hw_server 残留检查：3121 LISTENING / 进程 / 锁三项同时确认后再自起；
- 脚本**不得现场修改**；驱动缺陷 ⇒ 停窗、离线修、重新提交后再开窗。

## 5. 与其它口径的关系
- `M3/M2` 在 `REGION_CHANGED` 未解释前**不得**写成通过；
- 4-D 地址规划**不得**假定候选区"已证明空闲"；
- `ASSUMED_UNVERIFIED`：DDR bank/row 映射（S2 以 stripe 实测覆盖代替断言）、T3 保持结论（独立长跑）。

## 6. 当前就绪差距（如实）
| 依赖 | 状态 |
|---|---|
| 4-D 位流 `s4d_preproc.*` | ❌ 未产出（PL v2 RTL/BD 未完成） |
| 驱动 v3（含 bisect + DDR 位测试段） | ❌ 未实现（现有 v2 只有 PL 装载/M4-a/M4-b/M3 复检） |
| DDR 测试区快照参数 | ✅ 已定稿 `0x11AE0000–0x11B00000` |
| 参考快照 `41907f53…` | ✅ 窗口 A′ 已产 |
| 板卡 | ⛔ 已释放给阶段6，不得抢占 |
