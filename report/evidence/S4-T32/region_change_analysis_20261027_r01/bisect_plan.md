# 候选区 6 字节变化：只读 bisect 方案（并入 4-D bring-up 窗口执行）

- 目的：定位"候选区内容何时首次变化"，判定是 **PL 装载** 阶段、**init.elf 执行** 阶段，还是**两者都不是**（⇒ DDR 保持/读写位问题）。
- 性质：**只读**，除装载位流/ELF 外不写任何内存；执行窗口：4-D bring-up（本方案**不单独开窗**）。
- 预计耗时：3 次整区 dump（各约 33 s）+ 装载与复位 ≈ 6–8 min。

## 前置
1. 窗口授权 + P0 门禁（仅看 LISTENING、不清理 TIME_WAIT、不结束 mcp 进程）；
2. 自起 `hw_server`；位流 `555a70c2…`（4,045,776 B）；`init.elf` `237dd959…`；
3. 参考基线：`window_a_20261027_r01/m3_snapshot_orig.bin`（SHA `41907f53…`）；
4. 全部命令使用**已提交工具**：`scripts/stage4_s4b/m3_candidate_rw.tcl readback`、`program_2b_bit.tcl`（r2）、`xsdb`；**禁止**临时 Tcl。

## 步骤与判定
| 步 | 动作（只读） | 产物 | 判定 |
|---|---|---|---|
| S0 | `targets -set -filter {name =~ "*Cortex-A9*#0*"}; rst -system -stop`；整区 dump | `D0.bin` + SHA + exit | 与参考比较：若 D0 已异于参考 ⇒ **变更早于本窗口**（在窗口 A′ 之后、本次装载之前）⇒ 直接进 S3 结论 |
| S1 | `program_2b_bit.tcl`（解析 `PROGRAM_OK`）→ `rst -system -stop` → dump | `D1.bin` | **D0 vs D1 不同** ⇒ `CHANGED_AT_PL_PROGRAM`（PL 装载阶段）；相同 ⇒ 继续 S2 |
| S2 | `dow init.elf` → `con` → 等 6 s → `rst -system -stop` → dump | `D2.bin` | **D1 vs D2 不同** ⇒ `CHANGED_AT_INIT_EXEC`；相同但 D2 仍异于参考 ⇒ `NEITHER_STAGE`（⇒ DDR 保持/读写位问题） |
| S3 | 汇总三份 dump 互比 + 与参考比 | `bisect_result.json` | 唯一结论四选一：`CHANGED_AT_PL_PROGRAM` / `CHANGED_AT_INIT_EXEC` / `PRE_EXISTING_CHANGE` / `NEITHER_STAGE` |

## 停止条件
- 任一 dump 读取失败（`exit≠0`、字节数≠12,615,680）⇒ 停；
- 发现"同一状态两次 dump 互不相同" ⇒ 记 `READ_UNSTABLE` 并停（本情况已在 r02 排除，但保留判据）；
- 时间超 10 min ⇒ 收尾留证，不追。

## 证据格式
`bisect/D0.bin`、`D1.bin`、`D2.bin`（各 12,615,680 B）、`D*.sha256.txt`、`D*.exit_code.txt`、`D*.log`；`bisect_result.json` 含：三份 SHA、两两 diff 计数与首个差异地址、与参考 diff、最终结论、每步真实退出码。

## 后续分支（取决于结论）
- `CHANGED_AT_PL_PROGRAM` ⇒ 重审 M2"候选区不相交"论证，核对 PL 是否有未登记的 DDR 写路径；
- `CHANGED_AT_INIT_EXEC` ⇒ 核对 init.elf 运行时对 DDR 的间接写入（缓存行回写、BSP）；
- `PRE_EXISTING_CHANGE` / `NEITHER_STAGE` ⇒ 候选区在无写入情况下的内容不稳定 ⇒ 转"读写位/保持"测试（只读 + 授权写入后立刻比对恢复），并暂停以该区为 RAW 缓冲的 4-D 设计假设。
