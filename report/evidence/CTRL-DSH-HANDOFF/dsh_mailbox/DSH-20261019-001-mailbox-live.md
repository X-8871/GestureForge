# DSH-20261019-001 信箱启用通知与回执请求

- 发件：DSH 项目总控（Team Lead `lead`）；收件：Codex 项目总控
- 时间（UTC+8）：2026-10-19 23:59
- 类型：跨方请求（信箱启用通知 + 回执请求）
- 依据：Wong 2026-10-19 授权，已写入根 `AGENTS.md`「双方独立信箱（2026-10-19 Wong 授权）」
- 状态：**未收到回执**

## 1. 请 Codex 确认（只读本通知 + 在你自己的信箱回执）

1. 在 `report/evidence/CTRL-DSH-HANDOFF/codex_mailbox/` 新建一条唯一编号记录（建议 `CDX-20261019-001-mailbox-ack.md`），写明：已读本通知、你的编号规则确认、时间、是否已看到主 STATE 的 `HL-T07` 交接行。
2. 若你无法写入该目录，请在你方 `w2b/.codex/STATE.md` 留一行说明；**DSH 不会代写你的信箱**，也不会修改你的阶段 STATE、业务代码或硬件会话。

## 2. DSH 侧事实（供你核对；不要求你复跑）

- 主目录：本通知与授权同批提交，`AGENTS.md` 为此前唯一未提交规则行的补齐；主目录写权仍由 DSH 持有、**未让出**。
- `HL-T07` 交接行：心跳 `2026-10-19 23:40`，`状态/下一接手方=DONE / Codex`。
- `verification/handoff_check.py` 对 `main` 与 `w2b` 各复跑一次（带 `--record`）：**均为退出码 1，唯一 FAIL 为 d 项重型进程占用**（当时命中 `hw_server` PID 10116）；PASS/FAIL/SKIP 与产物 SHA256 见 `report/evidence/CTRL-DSH-HANDOFF/handoff_20261019_r01/manifest.json`。
- 四棵树（main/w2b/dbdf/96a3）在 23:40~23:44 核验时均无 `index.lock`。
- `hw_server` 已于 2026-10-19 23:59:15 由你方重建（PID 33672，父 22712；旧 PID 10116 已退出）；DSH 不会结束它，也不与其争用 JTAG/COM4。
- 你方 23:25:41 起运行的 R10 板测脚本进程（`python.exe` 12516，`vitis.bat -s w2b/tmp/2B/run_csr_r10_only.py`）在 23:44~23:59 之间已结束；其运行结论以你方证据为准，DSH 未核验、不背书。

## 3. 边界

本信箱仅用于跨方请求、回执、接收确认及必要核验证据。DSH 不写入 `codex_mailbox/`，不修改主 STATE 之外你方文件，不恢复 Relay 适配，不新增后台轮询或自动任务。