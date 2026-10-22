# 第五轮独立审查（门禁 v2.4）：`PASS`

- 审查者：第五轮独立审查 subagent（`69eca76a`），只读；产物仅在其系统临时目录（`D:\tmp`）
- 被审版本：HEAD `ee8f0aa`（审查期间 w5 前进到 `bf15d0b`，但 `git diff --stat ee8f0aa..HEAD` **仅 `.codex/STATE.md`**（心跳 4 行），三文件哈希与 git blob 未变 ⇒ 结论对被审哈希仍有效）
- 哈希（复核一致）：
  - `check_hardware_gate.py` = `15a8aa22b301e131d78298447789fec36a2e0c20442c307fa5f1d99c2365142b`
  - `test_hardware_gate.py` = `3f7d42abf12b4989b9a4a58063f44e75228003e8323405fc1df5dc61a954b25d`
  - `hardware_handoff_registry.json` = `1a761292c003d2500662ae8a539506b577e49e13fd80c077c8f38c97136631ea`
- **结论：PASS（无阻断项）**

## 1. 第四轮阻断项 B1：已真正关闭
- 代码核验：`classify_process_rows()` 被 `real_processes()` 与 `--process-check stub-csv` **共用同一实现**（非两套逻辑）。
- 测试：`python -B -m unittest scripts.stage5_t01.test_hardware_gate -v` → `Ran 40 tests`、`OK`、**exit 0**。
- **对抗复现（审查者自写变体，非照抄 Lead 脚本；副本基线先自证 40/40 OK）**：
  - 变体 A（删分类：命中即硬件）→ **exit 1**，失败 `test_36`/`test_37`/`test_39`（含要求的 test_36）✔
  - 变体 B（`TOOLING_PATTERN = r"vivado"`）→ **exit 1**，失败 `test_37` ✔
  - 追加变体 C（`PROCESS_PATTERNS` 收窄为仅 `hw_server`）→ **exit 1**，失败 `test_36`+`test_37`（额外判别力）✔
- `test_36`/`test_37` 断言的是子进程**真实退出码**，变体注入真实改变该退出码 ⇒ 判别力成立。

## 2. 3121 第二道门与端口边界：未发现 fail-open
- 函数矩阵 **16 例 ALL_AS_EXPECTED**：`0.0.0.0:3121` / `[::]:3121` / `127.0.0.1:3121` / 指定网卡 / 小写 listening → **True**；`:31210` / `:31219` / `:31211` / 仅 ESTABLISHED（本地或远程）/ PID 恰为 3121 / UDP 3121 / IPv6 非 LISTENING / 空文本 → **False**。
- CLI 实测：`[::]:3121 LISTENING` + 进程名全为 MCP 工具 → **exit 1**（"有监听必阻断，即使名字像工具"成立）；`:31210 LISTENING` → exit 0；仅 ESTABLISHED → exit 0；空 port-csv → exit 0。
- **fail-closed 已锁**：缺 `--port-csv` ⇒ `exit 1` + `port_check_ok=false` + "无法枚举端口监听（fail-closed）"；缺 `--process-csv` ⇒ `exit 1` + `hardware_process_enumeration_ok=false`。理由文字与 JSON 字段一致。

## 3. 真实环境复核
`check_hardware_gate.py --out D:\tmp\s5rev5_real_… --release-id CDX-20261022-007` → **exit 0 / GO / RELEASED / release_basis=mailbox_release / effective_release=CDX-20261022-007 / latest_occupation=CDX-20261022-006**；`hardware_processes=[]`、`tooling_processes=4×vivado-mcp-server-…`、`port_3121_listening=false`、`port_check_ok=true`、`reasons=[]`；现场只读核对：无 `hw_server/xsdb/vitis/xsim/cs_server`、`netstat :3121` 命中 0 行、无 `index.lock`。

## 4. 回归（原有检查均在）
未登记自称占用 → BLOCKED；反斜杠前缀占用**被应用** → OCCUPIED；order_key 重复 → BLOCKED；已登记 operation_doc 含"释放/独占" → exit 0 GO 且中性；登记表缺失 → BLOCKED；信箱目录不存在 → BLOCKED（fail-closed）；登记项指向缺席文件 → BLOCKED（"缺席"+"未被应用"）；`hw_server.exe`/`vivado.exe` → 硬件阻断；工具名 + 3121 → 被端口门阻断。

## 5. 登记表一致性（28 条）
28 条 == 真实信箱 28 个 MD（codex 17 + dsh 11）；`registered_not_on_disk=[]`、`on_disk_not_registered=[]`、`hash_mismatch=[]`；`CDX-20261023-016/017`、`DSH-20261023-011` 的 `evidence_quote` 均在正文；`DSH-20261023-011` `kind=ack` 与正文"本记录不声明任何硬件占用或硬件释放"一致（中性）。独立复现：删 DSH-011（27 条）→ **exit 1** 且理由精确指向该文件；28 条完整 → exit 0。

## 6. 非阻断观察（本轮**不改代码**，登记为后续项）
> 纪律：v2.4 三文件哈希已被本 PASS 冻结。任何修改都会使本 PASS 失效并需要新一轮复审；故以下只记录，不在本轮改。
1. **桩开关可得 GO**（`--process-check stub-ok --port-check stub-none`）：测试隔离口的固有面（非本轮新增）。已由 JSON `process_check_mode`/`port_check_mode` 与 console 留痕。
   → **后续项**：建议加 `decision_basis`/`admissible_for_G0_G3` 字段，并规定**任何作 G0/G3 依据的 GO 必须 real 模式**（我方在本轮报告中也已按此纪律声明）。
2. `TOOLING_PATTERN` 为前缀匹配无边界（`vivado-mcp-serverX.exe`、`vivado-mcp-server-hw_server.exe` 会归 tooling）。真实 `hw_server.exe` 仍阻断；3121 门为补偿控制。
   → **后续项**：需要时改为带边界/命令行判定；若出现"既 MCP 命名又未监听 3121"的会话，需人工核验。
3. `test_39` docstring 文字与实现口径不完全一致（判别键是 **LISTENING** 关键字，而非"忽略远程列"；构造 `…10.0.0.1:3121 LISTENING` 会被计为监听，方向为 fail-closed）。
   → **后续项**：改文字或解析本地/远程列。
4. `--port-check stub-csv` + **空** port-csv 得 `port_check_ok=true`（真实 `check_port_3121()` 对空输出 fail-closed）⇒ 仅桩路径语义瑕疵。
   → **后续项**：桩路径也按空输入 fail-closed。
5. "状态类登记项未被应用"守卫可达但冗余（与"缺席"同时触发）——无害。
6. 端口门只覆盖 3121：其他端口且未命中 `PROCESS_PATTERNS` 的真实会话可同时通过两道门（既有已记录残留）。
7. 审查期间 HEAD 由 `ee8f0aa` 前进到 `bf15d0b`（仅 STATE 心跳），不影响结论。

## 7. 结论
- 门禁 v2.4（哈希见上）经**四轮修复 + 五轮独立审查**，最终 **PASS**：B1 已关闭且判别力自证充分；3121 第二道门与 fail-closed 语义经 16 例矩阵 + CLI 实测核验；原有检查回归通过；登记表 28 条与真实信箱一致。
- 该 PASS 覆盖上述三个文件哈希；**保持不变**即可作为阶段5 硬件门禁的依据（仍须遵守：门禁 GO ≠ G3/G4/G5，不自动授予硬件使用权）。
- 6 条非阻断观察转为后续项（见 §6），任一项落地都需新的复审轮次。