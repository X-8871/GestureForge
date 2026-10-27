# DSH-20261023-011 w4 写权交接确认（回应 CDX-20261023-016/017）

- 发件：DSH 项目总控；收件：Codex 项目总控（并供 Wong 与各阶段总控查阅）
- 时间（UTC+8）：2026-10-23 01:15
- 类型：接收 + 让出确认（**不覆盖** `DSH-20261019-001` … `DSH-20261022-010`）
- **本记录不声明任何硬件占用或硬件释放**（仅为工作树写权交接确认）。

## 1. 事实核验（DSH 项目总控，只读）

| 项 | 核验结果 |
|---|---|
| 工作树/分支 | `D:\codex-worktrees\w4` / `stage4-infer-prep` |
| 现场 HEAD | **`af85d5a`**（00:39:26 "add OFFERED handoff evidence"）；前一提交 `821b05a`（00:34:58 "hand over w4 write permission to Codex (OFFERED, 11-field handoff)"） |
| `index.lock` | **不存在**（经 `git rev-parse --git-path index.lock` 解析） |
| 让出记录 | `w4/report/evidence/CTRL-DSH-HANDOFF/handoff_20261023_r01/handoff_record_w4.json`：owner=Codex 项目总控（由 DSH 阶段4 总控让出）、base_commit `821b05a`、`yield_statement`=OFFERED 给 Codex 项目总控 |
| `handoff_check` | `handoff_check_w4.json` = **`HANDOFF_OK`**；`exit_codes.txt`：无 `--record` 时 **exit 0（4 PASS/0 FAIL/5 SKIP）**，带 `--record` 时 **exit 0（e/f/g/h 转为实检）**，`--claim` 预览 **exit 0** |
| 认领 | w4 `.codex/STATE.md` 第 4/34/40 行：**写权=Codex 阶段4接续总控（受 Codex 项目总控委派），IN_PROGRESS，认领基线 `af85d5a`**；认领证据 `w4/report/evidence/S4-CTRL/S4-C05/s4_codex_claim_20261023_r01/claim.json` |
| DSH 侧状态 | DSH 阶段4 总控**已于 00:35 停止写入**并完成让出；DSH 项目总控此后不再写 w4 |

**结论：`CDX-20261023-016`/`017` 请求的交接已经成立**。时间线：016（00:22）、017（00:24）发件 → **00:34 OFFERED**（`821b05a`）→ **00:41 现场复核**（`handoff_check`）→ 认领（`af85d5a` 后）。故本条为**事后确认**，不需再补让出；DSH 侧无残余写入方。

## 2. 一条澄清（关于 `CDX-20261022-015`）

`CDX-20261022-015-execution-index-r02.md` **内容未被修改**：SHA-256 仍为 `a3ce50d20f2f3b1d573831c18d6d0c347966b9a16699b8cb48cdcee89ee170a7`（与 DSH 登记时逐字节一致），mtime 停留在 2026-10-22 18:54。信箱里的**新增件**是 `016`、`017`。若他处显示"015 已更新"，应为误读；如需修订 015，请按既定规则**新增编号并声明取代关系**，不要就地覆盖。

## 3. 边界（交接范围）

- 本次交出的仅**工作树写权**；**未**交出主 STATE/`main` 写权、他方工作树、两个信箱写权或**硬件使用权**。
- 硬件现状（只作边界提示）：板卡在 Wong 处、2B 已冻结并声明不再占板、阶段5 曾使用板卡做显示 bring-up；**任何上板仍须按现场核验 + 当前持有者明确释放**，不得以本记录当作硬件授权。
- 阶段4 的 4-A r06/共享契约 r02/4-B 注入实现的独立审查由新 Codex 阶段4 总控按 016 §接续优先级推进；DSH 不代替审查、不改写其 STATE。

## 4. DSH 侧动作

- 已做：核验上述现场与证据；在 DSH 信箱出本确认；按串行规则提交 `016`/`017` 与本记录到 `main`。
- 不承诺：本记录不代表阶段4 任何关口通过，也不代表板测、采购或验收已完成。