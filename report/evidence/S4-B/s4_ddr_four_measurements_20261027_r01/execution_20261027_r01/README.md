# S4-T31 四项实测 · 执行记录（2026-10-27 开窗后 P1 失败收窗）

- **开窗**：WINDOW_OPEN_UTC8=2026-10-27T20:43:36+08:00
- **收窗**：WINDOW_CLOSE_UTC8=2026-10-27T20:44:29+08:00（提前收窗，未进入 M1）
- **结论**：`P1_SMOKE_FAILED_WINDOW_CLOSED`（按窗口硬规则）

## 结果

| 阶段 | 结果 | 真实退出码 |
|---|---|---|
| P0 门禁 | **PASS** | 0（无他方进程、3121 空闲、无 index.lock） |
| hw_server 启动 | 成功（PID 26648，3121 监听） | — |
| P1 smoke | **FAIL** | 0（进程退出码），但语义失败：`mrd` 报 `Invalid target` |
| M1/M2/M3/M4-a | **NOT_RUN**（FAIL 即停） | — |
| P4 清理 | PASS（3121 已关、无残留进程） | 0 |

## P1 失败细节（原始输出已保全）

- `xsdb` 版本：**2026.1**（`PENDING_SMOKE` → 真实值已记录）。
- `targets` 可见：APU `ARM Cortex-A9 MPCore #0 (Running)`、`#1 (Running)`、`xc7z020`。
- 只读探测 `mrd 0xF8007014` 失败：`error "Invalid target. Use \"targets\" command to select a target"`
  ⇒ **脚本缺陷**：未先选择目标就 `mrd`（应在脚本内先 `targets -set -filter {name =~ "APU*" }`）。
- **按规则未现场修改脚本**；输出见 `P1_smoke.stdout.txt` / `P1_smoke.stderr.txt`。

## 重要观察（影响下一次窗口）

1. **CPU1 = Running**（非 halted）⇒ 即使修正 `mrd` 语法，**M1「CPU1 保持停止」前置在当板状态下不满足**；
   计划书 §1 明确「不得尝试 halt 它（改状态、超出授权）」⇒ 下一窗口开始前需先决定：由谁/以何种授权把 CPU1 置于 halted（或换用已 halt 的初始状态）。
2. PL 侧状态未探（`mrd` 失败），M2 的「PL 未配置」判定尚待下一次窗口确认。

## 未做

- M1、M2、M3、M4-a **均未执行**（P1 FAIL 即停）；未写任何 DDR 字节；未装载任何载荷；未改 `ENABLE`；未烧 QSPI。

## 清理复核（收窗后）

- 父进程 `hw_server.bat`（PID 26648）终止后，其派生的 `hw_server.exe` **子进程（PID 34184）仍在监听 3121**；
  已按「本窗口自己启动的进程」清理并复核：**`PORT_3121_IN_USE=False`、`RESIDUAL NONE`**，teardown **exit=0**（`P4_teardown.exit_code.txt`）。
- 该「父退出、子存活」现象已记入证据（`P4_teardown_result.json`），供下一次窗口清理时按子进程身份核对。

## 对下一次窗口的前置建议（离线修复项，不由本窗口现场改）

1. Tcl 脚本必须先选目标再 `mrd`：例如 `targets -set -filter {name =~ "APU*"}`；M2 的 DevCfg 读取同样需要先选 APU 或 DAP。
2. `targets` 输出是多行结构化 token（本窗口 16 token），解析应按 `targets -target-properties` 或过滤，而非按行切分。
3. **CPU1 当前为 Running**：M1 前置要求 halted；需先决定授权口径（由谁把 CPU1 置于 halted，或换用初始即 halt 的启动流程），否则 M1 必 FAIL。
