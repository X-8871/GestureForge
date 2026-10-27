# r06 attempt1 失败包 —— 补遗（ADDENDUM，不修改 NOTE 原字节）

- 目录：`report/evidence/S5-T04/s5_freeze_20261027_r06_attempt1_busy_cleanfail/`
- 声明：**`FAILED_ATTEMPT_NOTE.md` 原字节已恢复**（取自创建它的提交 `febc519`，sha256 `f25c5d94…`），本目录**其余原始文件（`console/**`、`results_freeze.json`、`delivery_manifest.json` 等）未动**。
- 本 ADDENDUM 只补一条机器留痕，替代此前对 NOTE 的误改（m5/m5′ 纪律项：失败证据不可改写）。

## `final_exit=1` 的推导（本包未保存 `final_exit` 字段）

该包由当时版本的运行器生成，`results_freeze.json` **不含** `final_exit` 字段；退出码由 `checks` 推导：

| 检查项 | 结果 | 依据文件 |
|---|---|---|
| `quiet`（安静窗口：自有重型工具不得在跑） | **FAIL**（外部 `hw_server.exe` PID 25508 命中旧判据） | `console/quiet_window.txt` |
| `worktree clean`（无已跟踪改动） | **FAIL**（3 个工具文件当时未提交） | `console/git_state.txt` |
| build / verify / selftest / suite / checker M1·M2 | 0 / 0 / 0 / 0 / 0·0 | `console/**`、`results_freeze.json` |

运行器判定为「全部门禁 AND」：任一门禁失败 ⇒ `final_exit=1`。故本包 `final_exit=1` 与两项 FAIL 一致。