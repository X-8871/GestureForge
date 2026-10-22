# 第四轮独立审查（门禁 tooling 分类）：CHANGES_REQUIRED → 已关闭

- 审查者：第四轮独立审查 subagent（`5a62a684`），只读；产物仅在其系统临时目录（`%TEMP%\rev4_s5t01`）
- 被审版本：HEAD `8af4701`（改动本体 `2f20922`）；三文件 sha256 与 `console/tool_hashes_post_tooling.txt` 一致
- 结论：**CHANGES_REQUIRED**，唯一阻断项 **B1**（测试对本次改动核心逻辑零覆盖）+ 一条非阻断但优先建议（第二道门）
- **关闭状态：已全部关闭**（见 §2、§3、§7）

## 1. 阻断项 B1（原文要点）
`test_12`/`test_35` 只走 `--process-check stub-hit/stub-tooling`，而这两个 stub 在 `main()` 中**硬编码**构造 procs/tooling，**不经过被审的 `real_processes()` 分类代码** ⇒ 复审用变体 A（删分类）/B（`TOOLING_PATTERN` 放宽为 `vivado`）证明：**35/35 仍全绿**，而真实门禁行为已变（A→BLOCKED；B→GO 且把 `vivado.exe` 当工具）。

关闭条件：新增经**真实分类路径**的用例，断言 (a) `vivado-mcp-server-*` → tooling 且 GO；(b) 6 类真实硬件名 → 阻断；(c) 变体 A、B 必须使新用例失败。

## 2. B1 关闭实施
| 关闭条件 | 实施 | 验证 |
|---|---|---|
| 真实分类路径可注入 | 抽出 `classify_process_rows(csv_text)`，`real_processes()` 与新增 `--process-check stub-csv --process-csv <file>` **共用** | `test_36`/`test_37` 经该路径 |
| (a) 工具名 → tooling 且 GO | `test_36` 伪造 CSV：`vivado-mcp-server-….exe` + `notepad.exe` | **PASS**（GO、`hardware_processes=[]`、tooling 精确命中 1 条） |
| (b) 6 类硬件名 → 阻断 | `test_37` 伪造 CSV：`vivado/hw_server/xsdb/vitis/xsim/cs_server` + 1 个 MCP 名 | **PASS**（`exit 1`、硬件 6 条、tooling 1 条） |
| (c) 判别力自证 | `tmp/5/S5-T01/adversarial_r4.py`（隔离副本，不改 w5） | 变体 A：`exit 1`，失败含 `test_36`；变体 B：`exit 1`，失败含 `test_37`；`DISCRIMINATING=True` → `console/adversarial_r4.json` |

测试总数：35 → **40**（新增 test_36/37/38，及端口边界 test_39/40）；`python -B -m unittest scripts.stage5_t01.test_hardware_gate` → **40/40 OK，exit 0**（`console/unittest_gate_v2_4.txt`）。

## 3. 第二道门（复审建议，非阻断但优先）——已实施
- 复审结论：**仅看进程名会漏判**（真实会话若被命名为 `vivado-mcp-server-*` 会被归入 tooling 不阻断）。
- 实施：新增 **3121 端口监听检测**（`port_3121_in_netstat()` / `check_port_3121()` + `--port-check {real,stub-none,stub-listening,stub-csv}`）：
  有 LISTENING ⇒ 视为硬件会话存在并**阻断**（进程名可伪装、端口不可）；端口枚举失败 ⇒ fail-closed 阻断。
- 测试：`test_38`（名字像工具 + 3121 有监听 ⇒ `exit 1`，理由含 "3121"）**PASS**。
- 报告字段：`port_3121_listening` / `port_check_ok` / `port_check_mode`；控制台 `port_3121.txt`。

## 4. 非阻断观察处置
| 观察 | 处置 |
|---|---|
| notes 未说明 tooling 不阻断语义 | 已补 notes（tooling 语义、3121 第二道门、`hardware_process_enumeration_ok` 仅表示枚举成功） |
| 未落 `console/tooling_processes.json` | 已落（另有 `port_3121.txt`） |
| `hardware_process_enumeration_ok` 易误读为"无硬件占用" | notes 已明确澄清 |
| FINDING 记 5 个 PID、实测 4 个 | PID 自然更替；分类结论不受影响 |
| `TOOLING_PATTERN` 接受 `-`/`_` | 保留（更宽容的匹配方向安全） |

## 5. 复审后真实环境复核（Lead 执行）
- 真实只读门禁：`--out post_round4b_real_gate --release-id CDX-20261022-007` → **exit 0 / GO / RELEASED**，
  `hardware_processes=0`、`tooling_processes=4`、`port_3121_listening=false`、`reasons=[]`（`console/real_gate_post_round4b.txt`）。
- 登记表同批次更新到 **28 条**：新增 DSH 侧 `DSH-20261023-011-w4-handoff-confirmation.md`（正文"本记录不声明任何硬件占用或硬件释放" ⇒ `kind=ack`，中性）；
  此前 `CDX-20261023-016/017` 已登记（`hardware_request`/`ack`）。28 条 = 真实信箱 28 个 MD（codex 17 + dsh 11）全覆盖。
- 说明：登记表与真实信箱必须同步——新信箱 MD 出现而未登记时门禁按 BI-2 **正确阻断**（实测 `DSH-20261023-011` 未登记时 `exit 1`；登记后 `exit 0`）。

## 6. 版本与哈希（v2.4 冻结，待第五轮复审）
- `check_hardware_gate.py` = `15a8aa22b301e131d78298447789fec36a2e0c20442c307fa5f1d99c2365142b`
- `test_hardware_gate.py` = `3f7d42abf12b4989b9a4a58063f44e75228003e8323405fc1df5dc61a954b25d`
- `hardware_handoff_registry.json` = `1a761292c003d2500662ae8a539506b577e49e13fd80c077c8f38c97136631ea`
- 详见 `console/tool_hashes_post_round4.txt`。

## 7. 端口边界加固（Lead 自查后追加）
- `port_3121_in_netstat()` 使用严格边界：正则 `:3121(?![0-9])`，避免 `:31210` 误命中。
- 新增 `--port-check stub-csv --port-csv <netstat 文本>`（走**同一解析函数**）：
  - `test_39`：`:31210 LISTENING` + 远程 `10.0.0.1:3121 ESTABLISHED` ⇒ **不阻断**（防误阻断）；
  - `test_40`：真 `0.0.0.0:3121 ... LISTENING` ⇒ **阻断**（第二道门不失效）。
- 判别力自证在 40 用例下仍为 `True`（变体 A → `test_36` 失败；变体 B → `test_37` 失败）。

## 8. 结论与限制
- B1 已按关闭条件 (a)(b)(c) 关闭并留判别力证据；第二道门已实施并加锁；端口边界已加固。
- **v2.4 仍应经第五轮独立复审**后再作为唯一依据；复审前只作辅助判定。
- 已知残留（记录在案）：进程判定仍以**名称**为主（第二道门补端口）；若未来出现既非 MCP 命名又未监听 3121 的真实会话，仍需人工核验。