# 事故与修复证据包（CTRL-HARNESS / session_compaction_lock_20261020_r01）

任务：阶段三总控窗口更换（旧会话压缩锁事故 + 插件 v4 source 报错修复）。
时间口径：UTC+8。性质：**只读核验**；本轮不解锁、不修复、不重启 DSH、不改写旧日志、不伪造 compaction/end。

## 1. 事故对象

| 项 | 值（实测，非转述） |
|---|---|
| 卡死会话 id | `session-f067ad85-4434-4f6a-bc01-d6c43068a0c5` |
| 工作区 | `D:\FPGA_Competition`（会话 `cwd` 由首事件 `type=session` 记录） |
| 日志路径 | `C:\Users\22061\.dsh\sessions\--D-FPGA_Competition--\session-f067ad85-4434-4f6a-bc01-d6c43068a0c5\session.v4.jsonl.zstd` |
| 日志字节 | 2,098,576 |
| 日志 SHA-256 | `b08f03edeae2fba850f055a34075ee94107907722e4ee1615580f425c4446695` |
| 日志最后写入 | 2026-10-20 04:36:44.475（此后无写入） |
| 解码事件数 | **2093**（seq 0–2091，无重复 seq，0 解析错误） |
| zstd 帧数（魔数计） | **1093**（背景材料写 2703，**以实测为准**：帧间另有 4 字节非帧字段） |
| `compaction/start` 计数 | **1** |
| `compaction/end` 计数 | **0** |
| 最后三事件 | seq2089 `tool/result`、seq2090 `step/end`、seq2091 `compaction/start` |
| 未闭合 compaction | `compactionId=58ec4c74-1321-45c6-b788-28661a9a1b58`、`turn=5`（取自 seq2091 `data`） |
| 消息来源 kind 分布 | `tool-jobs`25、`time-context`16、`user`7、`runtime-context`2、`subagent-settled`2、`agent-instructions`1、`skill-catalog`1、`fallback`1、`agent-message`1、`user-approval`1，其余 2036 条无 source 字段；**未出现被禁止的 `plugin` kind** |

结论（限定范围）：该日志以**未闭合的 `compaction/start` 结尾**，按 DSH 语义构成持久压缩锁，旧会话无法自愈；**本证据只证明日志终态，不证明 DSH 内部状态机实现细节**。

## 2. 根因（第三方插件 `dsh-batch-tool-calls`）

| 项 | 值 |
|---|---|
| 插件目录 | `C:\Users\22061\.dsh\profiles\desktop\node_modules\dsh-batch-tool-calls\` |
| 源码文件 | `lib\index.js`（15,722 B，SHA-256 见 `verification_6checks.json` C1） |
| 来源格式定义 | `lib/index.js:60` `const PLUGIN_SOURCE = Object.freeze({ kind: 'plugin', plugin: name })`（v3 旧格式） |
| 注入门控 | `lib/index.js:231` `const wantsReassert = cfg.reassertAfterCompaction || cfg.reassertEverySteps > 0` |
| 默认值 | `lib/index.js:72` `reassertAfterCompaction: z.boolean().default(true)`；`:101` 归一化 |
| 插件自述 | `lib/index.js:18` 「这是本插件**唯一**会往对话里写消息的动作，可用 `reassertAfterCompaction: false` 关掉」 |

因果链（可复核）：压缩成功后的下一步由 `reassertAfterCompaction` 触发的注入使用 `kind:'plugin'` 的来源，会话格式 v4 要求产生方自有 kind 且不接受 `plugin`，故写入被拒（报错文本 `format v4 message requires a producer-owned source kind`）。

## 3. 修复（配置覆盖，未改插件源码）

- 覆盖文件：`C:\Users\22061\.dsh\profiles\desktop\cordis.patch.yml`（SHA-256 `23459292b2a3645d02f76df1ad2f43be213a417467d87cd40b2ae0f3cde51bc9`，mtime 2026-10-20 07:54:41）
- 修复前备份：`cordis.patch.yml.bak-20261020-batch-fix`（SHA-256 `f58629c3765f4ecc45cb5e4ecce7600939fa2d626805a521ed5a60fa66de00b2`，mtime 07:41:08）
- 生效配置：`cordis.yml` 第 1336 行 `- id: batch-tool-calls`、第 1346 行 `reassertAfterCompaction: false`（SHA-256 `6ef2330e56e12d28b8537bd0b44cc4670a4f74e4de8b67f873ac3a8eea68c3d6`，mtime 07:54:43 → 说明覆盖已应用/热重载）
- 差异：现行 patch 相对备份**纯新增 20 行、0 删除**（无其它配置漂移），见 `patch_diff.txt`
- 处置范围：只关掉「压缩后提醒」这一条注入（`reassertAfterCompaction:false`、`reassertEverySteps:0`），插件静态提示段保持启用

## 4. 核验脚本与结果

- 脚本：`verify_incident.mjs`（自包含、只读，含魔数分帧解码）
- 结果：`verification_6checks.json` → **6/6 PASS**

| 检查 | 内容 | 结果 |
|---|---|---|
| C1 | 插件门控与 `kind:'plugin'` 来源定义仍在源码（根因可复核） | PASS |
| C2 | profile 覆盖含 `batch-tool-calls` 且 `reassertAfterCompaction: false` | PASS |
| C3 | 生效 `cordis.yml` 已带同一取值（覆盖已应用） | PASS |
| C4 | 存在修复前备份，现行 patch 相对备份纯新增、无删除 | PASS |
| C5 | 卡死日志末事件为未闭合 `compaction/start`，且 `compaction/end`=0 | PASS |
| C6 | 魔数分帧可完整解码：1093 帧、2093 事件、seq 0–2091、0 解析错误 | PASS |

## 5. 解码方法（重要更正）

旧日志**不能**用连续流解码：`zlib.zstdDecompressSync(整文件)` 只解首帧（会伪装成功），`zlib.createZstdDecompress()` 在首帧后报 `ZSTD_error_prefix_unknown`。正确做法：

1. 全量读入字节；按 4 字节魔数 `28 B5 2F FD` 收集全部偏移；
2. 以相邻魔数偏移为界，逐帧 `zstdDecompressSync`；
3. 拼接为临时副本（放在 `tmp/`，**不得写回原日志**）后检索；
4. 解码中途失败的帧必须如实记为失败，不得伪造内容。

## 6. 限制与未复核项

- 本包只证明「旧日志终态 + 配置已改 + 生效配置已带新值」；**不证明**新会话不会再触发 v4 报错——该点需以新会话实际运行为准。
- 修复方声明的「行为验证 6/6」未在仓库内找到原始入口，本包只登记其结论，未作为独立通过依据；本包的 6/6 是 DSH 本轮**另做的静态核验**。
- 未重启 DSH、未解锁旧会话、未改插件源码、未改旧日志字节（原 SHA-256 前后一致）。
- 阶段三窗口在本轮的实际接管状态、`dbdf` 的 HEAD 与未提交项、2B 硬件占用均**以新窗口核验为准**。