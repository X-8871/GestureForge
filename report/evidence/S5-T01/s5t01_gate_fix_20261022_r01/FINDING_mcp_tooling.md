# FINDING：MCP 工具包装器被门禁误判为硬件占用（2026-10-23）

- 发现时间（UTC+8）：2026-10-23 00:25
- 发现方式：让出前跑真实只读门禁 → `BLOCKED`，唯一剩余原因不是信箱也不是锁，而是**进程名含 "vivado" 的 MCP 工具包装器**
- 影响：门禁在"无 `hw_server`、3121 未监听、无锁、登记表状态 RELEASED"的情况下仍阻断 ⇒ 会误伤合法使用

## 1. 事实（实测）
| 项 | 实测 |
|---|---|
| `hw_server` / `xsdb` / `vitis` / `xsim` / `cs_server` | **0 个** |
| 3121 端口监听 | **无** |
| 被命中的进程 | `vivado-mcp-server-windows-amd64-2026.9.1.exe` × 5（PID 10888/15236/25076/29184/31596） |
| 命令行（CIM 实测） | `"C:\Users\22061\.codex\tools\ross-2026.9.1\vivado-mcp-server-windows-amd64-2026.9.1.exe" --stdio` |
| 身份判读 | **ROSS 的 MCP stdio 工具包装器**（IDE 工具链），不是板卡会话；属 Codex 侧工具，本阶段**未终止**（不 kill 他人进程） |
| 命中原因 | 门禁 `PROCESS_PATTERNS` 含 `"vivado"`，按**子串**匹配进程名 |

## 2. 处置（不删校验、只做分类）
- 新增 `TOOLING_PATTERN = vivado[-_]mcp[-_]server`：命中者归入 **`tooling_processes`**（在 JSON 中**透明可见**），**不阻断**。
- 真实硬件进程（`hw_server`/`xsdb`/`vitis`/`xsim`/`cs_server`，以及非 MCP 的 `vivado`）**仍然 fail-closed 阻断**（`test_12` 锁死）。
- 新增 `--process-check stub-tooling` 与 `test_35`：工具进程 → `GO` 且单列；硬件进程 → 阻断。
- **未删除任何检查**；进程枚举失败仍阻断（`test_11`）。

## 3. 证据
- 误报现场（BLOCKED）：`console/real_gate_post_register.txt` / `post_register_real_gate/hardware_gate.json`
- 分类后（GO）：`console/real_gate_post_tooling.txt` / `post_tooling_real_gate/hardware_gate.json`
- 测试：`python -B -m unittest scripts.stage5_t01.test_hardware_gate` → **35/35 PASS，exit 0**（`console/unittest_gate_v2_4.txt`）
- 工具哈希（本轮末）：见 `console/tool_hashes_post_tooling.txt`

## 4. 状态与限制（必须复审）
- **本改动未经独立审查**（第 3 轮审查针对的是 v2.2 及之前版本）。在复审确认前：
  - 该分类**只作辅助判定**；硬件使用的依据仍是"登记表状态 + 现场 `hw_server`/3121 实测 + 明确让出记录"。
  - 若复审要求改为**命令行级判定**（例如要求命令行含 `--stdio` 且不含 `-s`/端口参数）或要求跨根同名/端口监听一并纳入，须按轮次修复后再依赖。
- 已知边界：当前按**进程名**分类（非命令行）；若将来出现名为 `vivado-mcp-server` 的**真实**硬件会话，会漏判。故复审时应评估是否加端口 3121 监听检测作为第二道门（本轮未加，避免扩大改动面）。
- 建议下一轮：① 用命令行 + 端口监听双重判定；② 把"工具进程"写进 §0 口径（避免其他阶段误读）。