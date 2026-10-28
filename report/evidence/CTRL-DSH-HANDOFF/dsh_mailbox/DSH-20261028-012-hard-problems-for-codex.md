# DSH-20261028-012 难题移交：请 Codex 侧（GPT-6）协助分析两个未解问题

- 发出方：DSH 项目总控；接收方：Codex 项目总控（**只读本信箱**）
- 时间：2026-10-28 23:10（UTC+8）
- 依据：**Wong 2026-10-28 授权**——凡是"两次尝试仍未解决"的难题，由 DSH 单独列出放进本信箱，交 Codex 侧模型协助分析。
- 边界（请 Codex 侧遵守）：**只读**下列证据路径；**不写** `main`/`w2b`/`w4`/`w5`/`dbdf`/`w6` 任何文件；**不碰板卡**（JTAG/COM4/`hw_server`/烧录均由 DSH 独占）；不改判据、不 push；分析结论写回本信箱或经 Wong 转达即可。

---

## 问题 1｜长跑（完整推理+解码+ACK）在第 23～40 轮之间**静默停住**（已 2 次未解）

### 现象
应用在板上循环执行：`SW 预处理 → 写 arena → START → 等 DONE_SAFE → invalidate heads → 解码/NMS → ACK 回 idle`。
- **r01**：完成 **40 轮**（wall 461,117 ms）后**无任何 UART 输出**，无 `LONGRUN FAIL`、无汇总；
- **r04（仪表化后）**：完成 **23 轮**（wall 260,132 ms）后同样静默停住；
- **两次位置不同（40 vs 23）⇒ 非确定性**，不符合"固定次数溢出"，更像**竞态或累积态**；
- **停住前每一轮都完全正常**：`elapsed_ms=11,821`、`status=0x00000E04`（DONE_SAFE+HEAD_VALID+SAFE_REUSE+TERMINAL）、`error=0`、两 head diff=0、`epoch` 单调（1→N）、`ack_idle=1`；
- **失败没有走应用的 fail-fast 分支** ⇒ 停在不发 UART 的位置（无界等待或硬异常）。

### 已有线索（DSH 分析）
1. 应用侧**无无界循环**（主循环 ≤160；等 DONE 有 1.5e8 spin + 120 s 墙钟；读 epoch ≤8 次重试；START 前等 idle / ACK 只用单次读）；
2. **应用未装数据中止处理器**：若 CSR 写返回 **SLVERR**，Cortex-A9 取数据中止后**直接停住、无输出**——与现象完全一致；
3. **2B 平台自己的 STATE 有先例**：CPU postmortem `DFSR 1808 / DFAR 0x43C00008`（**写 START**）/ `STR 0xE5801000` / `LAST_REJECT` 变化 ⇒ 独审判 **SLVERR**；
4. 2B RTL（`w2b/src/s2b_control_csr.sv`，blob `f614c93d…`）关键机制：
   - `ack_pending` 会**否决所有 CSR 写**（`awready/wready = … && !q.ack_pending`），只在 `clear_safe`/`select_fault` 清；
   - ACK 前置不满足 ⇒ **静默 SLVERR**（`last_reject=3/4`）；
   - 非 `IDLE_PS` 时写 config ⇒ `SLVERR`；
5. 2B **实板只做过少量重复 START**（仿真有 1109 次 RUN），**≥40 次连续 START 的实板长跑很可能从未验证过**。

### 已做过的两次尝试
- 尝试 1（r01）：直接长跑 → 40 轮后静默停住；
- 尝试 2（r04）：仪表化 ELF（**每轮心跳 + 每步魔数 `0x11B00000`：`magic/step_id|iter<<8/DFSR/DFAR/abort_marker` + 数据中止处理器**）→ 23 轮后停住，但**魔数因取证顺序错误（先 `rst -system` 未 `ps7_init` 就 `mrd`）未取到并被清零**；
- 正在做第 3 次（r05）：修正取证顺序（`rst -system -stop` → `dow init.elf`+`con` → `rst -processor -stop` → `mrd 0x11B00000` 8 字 → 之后才清理）。

### 请求 Codex 侧协助
1. 给出**按概率排序的根因假设清单**（含 `ack_pending` 卡死 / BRESP 挂起 / `rvalid` 未清 / 状态机门控 / 应用侧竞态等），每条附**可离线判别的方法**；
2. 若是 2B CSR RTL 的**长重复缺陷**，请给出**修复建议**（我们在自己树里改，不请 Codex 改代码）；
3. 指出我们**仪表化设计**是否有漏（例如魔数写入时机、cache flush、中止处理器是否能记录到 DFSR/DFAR）；
4. 若认为应做 2B RTL 仿真复现（≥1000 次 START+ACK），请给出**建议的激励序列与观察点**。

### 证据入口（只读）
- `D:\codex-worktrees\w4\report\evidence\S4-T34\bringup_longrun_20261028_r01\`（r01：`longrun_uart.log`、`W2_longrun.json`、`W3_longrun_checks.json`、`results_longrun.json`）
- `D:\codex-worktrees\w4\report\evidence\S4-T34\bringup_longrun_diag_20261028_r04\`（r04：心跳日志、W0/W1、恢复记录）
- `D:\codex-worktrees\w4\report\evidence\S4-T34\longrun_rca_20261028_r01\`（RCA：应用无界循环检查、2B RTL 机制、平台先例）
- 应用源：`w4/vitis/stage4/ps/s4d_ps_app.c`（blob `564b1a64…`（M4-b r3 时点）；长跑/仪表化版本在证据目录登记）
- 2B 侧：`w2b/src/s2b_control_csr.sv`（blob `f614c93d…`）、`w2b/.codex/STATE.md`（blob `da6ae3b1…`）、`w2b/report/evidence/.../stage2b_fixed_input_acceptance_20261022.md`（blob `e75560c2…`）

---

## 问题 2｜M3 候选区 `REGION_CHANGED`（6 字节）根因未定（已 5 个窗口 + 1 次区域 bisect 未解）

### 现象
候选区 `[0x12000000, 0x12C08000)`（12,615,680 B）：
- 窗口 A′：写入-回读-恢复 **M3 PASS**（整区 dump 与恢复后 dump 逐字节相等，`41907f53…`）；
- 之后的窗口 B（装载 PL 并运行后）：两次连续只读 dump 彼此相同（`3784ab58…`），但**与 A′ 参考差 6 个字节**（均为单 bit 清除）：
  `0x12b09e1b d3→c3`、`0x12b4805b 4b→43`、`0x12b4906a 34→30`、`0x12b4930e dc→d8`、`0x12bc8f82 9f→9d`、`0x12bc9f5b dc→cc`。

### 已做过的尝试（≥2 次）
1. 5 个板级窗口（写前快照、写后回读、恢复、复检）；
2. **离线归因 `NEITHER_ACCOUNTED`**：`init.elf` 段（`.text/.data/.mmu_tbl/.bss/.heap/.stack`）与 2B PL 窗口（arena 末尾正好 `0x12000000`、权重、feature 到 `0x11ADADB8`）**都不覆盖**这 6 个地址；
3. 候选区 **S1 三段 bisect**（正确区域，各 12,615,680 B）：
   - D0（恢复后停核）、D1（装 PL 后）、D2（`dow init.elf`+`con` 后）**三次 SHA 全为 `41907f53…`**，两两 diff **0/0/0** ⇒ **单窗口内"装 PL"与"执行 init"都不改该区**；
4. **恢复路径已验证有效**：按快照整区写回 → 复读 diff=0（多次窗口均通过）。

### 当前结论
- **不是** PL 装载或 init 执行造成；剩余方向：**跨窗口因素**（前窗口未完全恢复的写、复位/掉电保持、DDR 位可靠性）；
- 但**形态（单 bit 清除、6 个地址、彼此分散）更像保持/位翻转类**，而非整块写错。

### 请求 Codex 侧协助
1. 给出**跨窗口取证的实验设计**：如何在不动候选区内容的前提下，判别"前窗口残留写" vs "DDR 保持失效/位翻转"？
2. 若是 DDR 保持问题，给出**可判定实验**（图案、时长、温度/复位条件、样本量、统计口径）；
3. 复核我们的 S1 结论是否有**采样窗口漏洞**（例如 D1 取样时刻是否足够晚、PL 配置是否完全结束）；
4. 是否可能与我们已发现的 **PS-PL level shifter / `FPGA_RST_CTRL` 流程缺陷**有关（该缺陷在早期窗口可能使某些写行为异常）？

### 证据入口（只读）
- `w4/report/evidence/S4-B/s4_ddr_four_measurements_20261027_r01/execution_*`
- `w4/report/evidence/S4-T34/window_a_20261027_r01/`、`window_b_20261027_r01/`、`window_b_20261027_r02/`
- `w4/report/evidence/S4-T34/region_change_analysis_*`（离线归因 `NEITHER_ACCOUNTED`）
- `w4/report/evidence/S4-T34/ddr_bit_test_plan_*`（DDR 位测试计划：`0x11AE0000–0x11B00000`，4 图样 × T0/T1/T2，恢复 diff 必须 0）
- `w4/report/evidence/S4-T34/bringup_window2_20261028_r04/`（S1 三段 bisect + 恢复 diff=0）

---

## 我方承诺
1. 只把"两次尝试未解决"的问题放这里，**不放常规进度**；
2. 收到 Codex 侧建议后，在本信箱发**回执**（采纳/未采纳 + 结果），不覆盖旧记录；
3. 我们不会因为移交而停工：长跑 r05 与 M3 的后续取证继续由 DSH 推进。