# 说明：`s5t01_prereq_20261022_r01` 已被 `s5t01_prereq_20261022_r02` 取代（历史保留）

- 时间（UTC+8）：2026-10-22 13:10
- 原因：r01 的门禁脚本用 `tasklist /FO CSV /NH` 枚举进程，在 Git Bash(MSYS) 下 `/FO` 被改写为路径导致命令失败，而代码把“枚举失败”当作“无进程”返回 `[]`，违反 fail-closed（可能误判放行）。
- 处理：**保留不删**（历史证据）；r01 的 `decision=BLOCKED` 结论未被推翻（当时阻断原因同为“缺 2B 书面让出”），但**其进程检查不可信**，不得引用其进程结论。
- 权威证据：`../s5t01_prereq_20261022_r02/`（含 `hardware_process_enumeration_ok=true` 与原始枚举输出）。