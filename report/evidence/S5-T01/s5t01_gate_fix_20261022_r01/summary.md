# S5-T01 §0 门禁误判修复 RunId `s5t01_gate_fix_20261022_r01`

- 时间（UTC+8）：2026-10-22 19:10–19:45
- 依据：`CDX-20261022-014-stage5-display-runbook-r02.md` **§0（前置任务）**；本包取代 `CDX-20261022-011`。
- 目标：修正门禁把**普通操作文档**误判为硬件占用的问题；修正后须经独立审查才能依赖它放行。
- 状态：**已实现 + 隔离合成测试 19/19 PASS**；**独立审查已派发（结论另附）**；真实只读门禁在审查结论后执行。

## 1. 缺陷与根因

- v1 `mailbox_entries/detect_release` 把信箱**所有 MD** 按"有释放词且无否定词"二分：命中→让出、未命中→占用，并取**最后一条**。
- 结果：任何普通文档（如运行书 `CDX-20261022-014` 正文出现"释放/独占"）都会被当成**最新占用**，使此前有效让出（`CDX-20261022-007`）失效。**该结果不能证明 Codex 实际重新占板。**

## 2. 修复内容（v2，登记表驱动）

| 机制 | 内容 |
|---|---|
| 登记表 | `scripts/stage5_t01/hardware_handoff_registry.json`：25 条，逐条 `id/file/sha256/order_key/kind/hardware_scope/issuer`，状态类仅 `hardware_occupation`/`hardware_release` |
| 中性化 | `hardware_request`/`operation_doc`/`delivery_receipt`/`ack`/`report`/`decision` **不改变硬件状态**（§0.1、§0.3） |
| 绑定 | 文件必须存在且 SHA-256 一致；带 `evidence_quote` 者**引用原文必须命中** ⇒ 否则证据矛盾 → BLOCKED |
| 不可识别即阻断 | 未登记文件若**文件名或 `hw_handoff_kind:` 声明标记**自称硬件交接 → BLOCKED；未登记且不自称 → 中性 |
| 顺序与范围 | 同 scope 按 `order_key` 排序；让出必须**晚于**最近占用且 scope 覆盖请求范围 |
| fail-closed | `index.lock`、进程枚举失败、命中硬件/重型进程 → 均 BLOCKED（不得删检查"修好"） |
| 授权绑定 | `--authorized-by/--authorization-note` 必须另给 `--authorization-source` + SHA-256，且 note 为原文**子串**；否则**拒绝授权**；授权**不能覆盖真实占用**（§0.6） |
| 只读 | 不连板卡、不起 `hw_server`、不写寄存器（§0.5 先做纯解析/替身测试） |

## 3. 隔离合成测试（`console/unittest_gate_v2.txt`，真实退出码 0）

`python -B -m unittest scripts.stage5_t01.test_hardware_gate -v` → **Ran 19 tests … OK，exit 0**

| # | 情形 | 期望 | 结果 |
|---|---|---|---|
| 01 | 让出→普通文档 | 仍 RELEASED、GO（普通文档中性） | PASS |
| 02 | 让出→新占用 | BLOCKED、OCCUPIED | PASS |
| 03 | 占用→有效让出（按序） | GO、RELEASED | PASS |
| 04 | 普通文档正文含"释放/独占" | 中性、不冒充通知 | PASS |
| 05 | 未登记但文件名含交接语义 | BLOCKED（不可识别） | PASS |
| 06 | 未登记但含 `hw_handoff_kind:` 声明标记 | BLOCKED | PASS |
| 07 | 登记项哈希不匹配 | BLOCKED（证据矛盾） | PASS |
| 08 | `evidence_quote` 未命中原文 | BLOCKED | PASS |
| 09 | 让出早于占用（顺序矛盾） | OCCUPIED、BLOCKED | PASS |
| 10 | `index.lock` | BLOCKED | PASS |
| 11 | 进程枚举失败 | BLOCKED（fail-closed） | PASS |
| 12 | 命中硬件进程 | BLOCKED | PASS |
| 13 | `--release-id` 不匹配 | BLOCKED | PASS |
| 14 | 授权缺原文/哈希 | 授权被拒、BLOCKED | PASS |
| 15 | 授权绑定原文（非空信箱但无状态类记录） | GO、basis=`operator_authorization`、`ownership_unverifiable=true` | PASS |
| 16 | 授权 + 真实占用 | BLOCKED（授权不能覆盖占用） | PASS |
| 17 | 登记表缺失 | BLOCKED | PASS |
| 18 | **真实信箱 + 真实登记表**（替身进程/锁）只读核对 | RELEASED；让出=`CDX-20261022-007`；最近占用=`CDX-20261022-006`；GO | PASS |
| 19 | 登记表覆盖全部真实信箱 MD | 无漏登记 | PASS |

- 修复过程中由测试暴露并修正的**自身缺陷**：① `effective_state` 原要求"让出与占用同时存在"才判 RELEASED（只有让出时误判 UNKNOWN）；② 测试桩把"用真实信箱"的 None 覆盖为空合成目录。

## 4. 只读一致性（替身进程/锁；不碰板卡）

`console/parity_stub.txt` → `{"decision": "GO", "hardware_state": "RELEASED", "effective_release": "CDX-20261022-007", "latest_occupation": "CDX-20261022-006", "reasons": []}`（exit 0）

## 5. §3 事件源核验（本次附带交付，只读 XSA/BSP）

见 `S5T01_S3_frame_event_design.md`：**MM2S 帧完成中断已接入 PS（GIC 61）**、**VTC 中断接入（GIC 62）**、S2MM 中断未接入；`USE_FSYNC=1` ⇒ 显示帧由 VTC 时序驱动；并给出"帧计数不推进"的根因假设（`CR[23:16]` 阈值=0 + IRQ 未清除）与四种 FPS 的事件源/口径设计。**尚未实现、未板测。**

## 6. 工具哈希（`console/tool_hashes.txt`）

- `check_hardware_gate.py` `8b82906e…`；`hardware_handoff_registry.json` `d21fbfab…`；`test_hardware_gate.py` `0b61be9a…`

## 7. 审查结论与 BI-1/BI-2 关闭（2026-10-22 19:35–19:45）

- **审查结论**：`CHANGES_REQUIRED`（2 阻断项 + 5 条非阻断观察），记录见 `REVIEW_r01_CHANGES_REQUIRED.md`。
  审查者独立确认：修复目标已达成（真实门禁中 `CDX-20261022-014` 为中性 `operation_doc`、真实模式 exit 0/GO/RELEASED）、对抗性验证有效（撤回 v2 语义即复现 v1 误判，且 19 项测试在 v1 副本上 `failures=5`）。
- **开发者失败**：`dev-s5-gate` 未产出（后台子代理失败、门禁文件哈希未变）⇒ 由 **Lead 承担集成责任**完成修复。

### 7.1 BI-1 关闭（登记表 schema 强校验，任一不一致 → BLOCKED）
登记文件缺席、缺 `sha256`、同一文件重复登记、`kind` 非法/拼写错误、状态类缺 `order_key`、`file` 目录前缀不匹配、状态类跨信箱 `order_key` 重复（排序歧义）——全部阻断；`OCCUPIED` 时 `release_basis=null`。

### 7.2 BI-2 关闭（未登记文件不得静默中性）
未登记文件若**文件名或正文或 `hw_handoff_kind:` 声明标记**含交接语义 → BLOCKED（不可识别的硬件交接记录）；仅登记表内记录可改变状态。**回归护栏**：已登记为 `operation_doc` 的文件（如 `CDX-20261022-014`）即使正文含"释放/独占"仍必须中性——由 `test_27` 锁死。

### 7.3 修复后验证（真实退出码）
| 命令 | 退出码 | 结果 |
|---|---|---|
| `python -B -m unittest scripts.stage5_t01.test_hardware_gate -v` | **0** | **Ran 28 tests … OK**（原 19 + 新增 9 条覆盖 BI-1/BI-2） |
| 只读一致性（替身进程/锁）`--release-id CDX-20261022-007` | **0** | GO / RELEASED / 让出 `007` / 最近占用 `006` |
| **真实只读门禁**（真实进程/锁；`console/real_gate_postfix.txt`） | **0** | GO / RELEASED；无 `index.lock`、tasklist 枚举成功且无硬件进程 |

- 修复后工具哈希：`check_hardware_gate.py=0a2ebc7d…`、`test_hardware_gate.py=7e1c69a7…`、`hardware_handoff_registry.json=d21fbfab…`（登记表未变）。
- 测试语义随之收紧两条（应视为**行为变更**，已在测试内注明）：未登记且正文含交接语义的文档由"中性"改为"BLOCKED"（`test_04` 更名）；`write_registry` 桩补齐 `neutral_kinds`。

## 8. 未完成 / 限制

- **独立审查结论未回**：审查前不得依赖该脚本放行真实硬件（§0.5）。
- **真实只读门禁（真实进程/锁）尚未执行**：将在审查结论后执行并另附证据。
- 未连接板卡、未启动 `hw_server`、未写寄存器；未改主树/w4/w2b/两个 mailbox（登记表仅**只读**引用其哈希）。
- v1 行为与本次修复前后的差异未做历史重放（仅以合成输入证明中性化语义）。