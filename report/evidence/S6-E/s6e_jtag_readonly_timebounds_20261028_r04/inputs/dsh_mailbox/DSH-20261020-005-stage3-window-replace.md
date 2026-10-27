# DSH-20261020-005 阶段三窗口更换（旧会话压缩锁 + 插件 v4 报错修复）

- 发件：DSH 项目总控；收件：Codex 项目总控（并供 Wong 查阅）
- 时间（UTC+8）：2026-10-20 11:48
- 类型：事故与窗口更换通知（**不覆盖** `DSH-20261019-001`、`DSH-20261020-002`、`DSH-20261020-003`、`DSH-20261020-004`）

## 1. 事故事实（DSH 独立复核，非转述）

- 卡死会话 `session-f067ad85-4434-4f6a-bc01-d6c43068a0c5`（工作区 `D:\FPGA_Competition`，创建 2026-10-20 00:24）。
- 日志 `C:\Users\22061\.dsh\sessions\--D-FPGA_Competition--\session-f067ad85-4434-4f6a-bc01-d6c43068a0c5\session.v4.jsonl.zstd`：2,098,576 B、SHA-256 `b08f03edeae2fba850f055a34075ee94107907722e4ee1615580f425c4446695`、末次写入 04:36:44.475、此后无写入。
- 实测：**1093 个 zstd 帧（背景材料写 2703，以实测为准）、2093 条事件、seq 0–2091、无重复 seq、0 解析错误、`compaction/start`=1、`compaction/end`=0**；末三事件 seq2089 `tool/result`、seq2090 `step/end`、seq2091 `compaction/start`（`compactionId=58ec4c74-1321-45c6-b788-28661a9a1b58`、`turn=5`）。
- 该未闭合的 `compaction/start` 构成持久压缩锁 → 旧会话持续 busy、发消息失败、**不能自愈**。
- 该窗口在挂起前**已完成 9 个 `dbdf` 提交**（00:51–04:34，HEAD `41ee5ba`：HDMI 工程已重建并 JTAG 实物启动、CMOS2 通道 1280×720 传感器可用、仅剩 S2MM 缺 SOF）。

## 2. 修复证据与入口

- 根因：第三方插件 `dsh-batch-tool-calls` 在压缩成功后注入一条提醒，来源仍是 v3 格式 `{kind:'plugin'}`；`lib/index.js:60` 定义该来源、`:231` 为注入门控（`:18` 自述这是唯一往对话写消息的动作）。
- 修复：`C:\Users\22061\.dsh\profiles\desktop\cordis.patch.yml` 新增 `batch-tool-calls` 覆盖（`reassertAfterCompaction:false`、`reassertEverySteps:0`），备份 `cordis.patch.yml.bak-20261020-batch-fix`；生效配置 `cordis.yml:1346` 已带新值（覆盖已应用/热重载）。
- 证据入口：`report/evidence/CTRL-HARNESS/session_compaction_lock_20261020_r01/` —— `README.md`、`verify_incident.mjs`（只读、可复跑）、`verification_6checks.json`（**6/6 PASS**）、`session_tail_events.json`、`patch_diff.txt`、`manifest.json`。
- 边界：不清洗旧日志、不重启 DSH、不伪造 `compaction/end`；**不把「新会话不会再报 v4 错」写成已验证结论**（需以新会话实际运行为准）。

## 3. 窗口更换决定

- 决定（Wong 2026-10-20 11:39）：阶段三改为**新窗口 + 新会话**接手，提示词 v2 由 DSH 项目总控交付；旧会话降级为**只读证据源**——不修复、不写回、不追加。
- 阶段三 Git 写入树不变：`D:\codex-worktrees\dbdf`（分支 `codex/stage3-video`）；**HEAD、未提交项与硬件占用均以新窗口核验为准**。
- 新会话 id 待新窗口创建后由 DSH 回填主 STATE 阶段入口表。

## 4. 边界

主目录写权仍由 DSH 持有、**未让出**；DSH 不写入 `dbdf`/`w2b`、不结束任何进程、不推送、不烧录、不新增后台轮询或自动任务。阶段三窗口的跨方请求请经项目总控转达（本信箱仅由 DSH 项目总控写入）。