# M2 复审（2026-10-29，独立只读复核）：CHANGES_REQUIRED（判据基座与记录注释需更正）

- 任务：D 项「M2 复审」；复审对象 = 阶段4 板级 M2 判据「无其他 DDR consumer」（2026-10-27 记录为 PASS）
- 复审者：DSH 项目总控（本轮无第三方 Reviewer；**本复审不构成独立 Reviewer 结论**，只做事实级复核）
- 依据资料：UG585 v1.2 p.150「PL reconfiguration flow」step 5（本地正式资料）
- 复核脚本：`verify_m2_basis.py`（只读，用归档十进制读数重算 hex/位；输出 `verify_m2_basis_output.json`，exit 0）
- 复审输入（只读）：`report/evidence/S4-B/s4_ddr_four_measurements_20261027_r01/execution_20261027_r05/M2_consumer_check.log`、
  `execution_20261027_r04/M2_result.json`、`execution_20261027_r05/M2_result.json`、`execution_20261027_r05/README.md`

## 1. 结论

**CHANGES_REQUIRED**（阻断 M2 作为"已闭合门禁"的引用，但不推翻"本轮未见 PL 已配置"这一事实）。

- 结论"PL 未配置"**在换用正确寄存器后仍成立**：`INT_STS(0xF800700C)` 读数 `0xA802000A` 的 **bit[2] = 0**（PCFG_DONE 未置位）。
- 但归档记录把 PCFG_DONE 归到**错误的寄存器与位**，并有两处 **hex 注释与原始十进制读数不符**：
  这不是措辞问题，是可复现的判据基座错误；按项目证据规则（判据必须有正确基座），M2 需勘误后重记。

## 2. 事实（逐条可复算）

| # | 项 | 归档记录 | 实际（由原始十进制重算） | 判定 |
|---|---|---|---|---|
| F1 | PCFG_DONE 所在寄存器/位 | 记录按 `STATUS(0xF8007014)` 的 **bit1** 解释 | UG585 v1.2 p.150 step 5：PCFG_DONE = **`INT_STS(0xF800700C)` bit[2]** | **错误** |
| F2 | `DEVCGF_STATUS` hex | `0x40000010`（r04 JSON、r05 README/JSON） | 十进制 1073744432 = **`0x40000A30`** | **不符** |
| F3 | `DEVCGF_CTRL` hex | `0x4E00FFFF`（r04 JSON） | 十进制 1308680319 = **`0x4E00E07F`** | **不符** |
| F4 | `INT_STS` 是否被解释 | 仅记录十进制，未解读 bit | bit[2]=0、bit[1]=1、bit[3]=1 | 未使用（本可支持结论） |
| F5 | `STATUS` bit4 | 未记录 | =1（PCFG_INIT 口径，见 Linux zynq-fpga 驱动惯例） | 未使用 |
| F6 | r03 记录 | `"M2 本轮无数据；P1 步骤3 已读到 DevCfg STATUS=0x40000010（bit1 PCFG_DONE=0…）"` | 与 F1/F2 同源错误，且该轮 M2 实为 NOT_RUN | 需一并勘误 |

原始读数（来自 `execution_20261027_r05/M2_consumer_check.log`）：
`M2_DEVCGF_CTRL=1308680319`、`M2_DEVCGF_INT_STS=2818703370`、`M2_DEVCGF_STATUS=1073744432`。

## 3. 影响

- **不影响**：M1（两核 Suspended、PC1 不推进）与"唯一调试客户端"这两条旁证；它们本身仍成立。
- **影响**：M2 作为"构造性排除无其他 DDR consumer"的门禁，其判据链里有一步基座错误；若后续以 M2 为前置解锁 `ENABLE=1` 或 M4 复验，必须先更正。
- **不得据此改称**：M2 仍不是"总线测量"；本次复审也不把它改判为 PASS。

## 4. 关闭条件（建议由阶段4 执行）

1. 新增勘误记录（新 RunId，不改写 2026-10-27 旧记录）：
   - 以 `INT_STS(0xF800700C) bit[2]` 为唯一 PCFG_DONE 判据，写明 UG585 v1.2 p.150 step 5；
   - 修正两处 hex 注释（F2/F3），并把"0x40000010 / bit1"标注为**记录缺陷**；
   - 补一条限制：`INT_STS` 可被写 1 清除，**单次为 0 ≠ 从未配置过**；因此 M2 的准确表述应为
     "本轮未见 PCFG_DONE 置位（INT_STS[2]=0）⇒ 构造性推断 PL 未配置"，而非"排除"。
2. 若要把 M2 抬到更强证据：在同一窗口内**顺序**读 `INT_STS` → 写 1 清 `PCFG_DONE_INT` → 再读，并记录两次值；
   或在已知已配置 PL 的窗口做一次正控（读同一寄存器得到 bit[2]=1），证明该位的可观测性。
   **不得**通过"读 PL CSR 看是否挂"来判 PL 是否配置——未配置 PL 的 AXI 读会永久挂起并导致 DAP 粘连（2026-10-29 已实证）。
3. 勘误落盘后，在阶段4 STATE 的 M2 条目加指针；`ENABLE=1` 的前置条件文本同步改为新的表述。

## 5. 复审边界

- 只做了只读复核：未上板、未读寄存器、未改任何旧证据、未改冻结件。
- 复审者非独立第三方；如用于门禁，需再走独立 Reviewer（`rev-s5` 或等价）确认。
- 不主张 G3/G4/G5；不改变阶段4 其他判据。