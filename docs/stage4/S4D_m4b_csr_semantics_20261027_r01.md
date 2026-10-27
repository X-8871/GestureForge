# S4D M4-b CSR 语义与自检序列（唯一权威：r13 诊断应用源码，2026-10-27 r01）

- 权威来源：`report/evidence/S4-CTRL/s4_ps_adapter_closure_20261023_r01/inputs/r13_build_text/derived_app_source.c`
  （= r13 板上真实跑通 `s4b_ps_tensor_diagnostic`、拿到 1 框 `PASS_EXACT_TRACE_UART_JOIN` 的应用源文本）。
- **本文件取代此前自拟语义**（曾错误假设 `0x008` 写 1 = START、`0x00C` bit0 = BUSY；该假设作废）。
- 边界：本文只做离线语义抽取；M4-b 判据必须在窗口内实测，**不得**用本文或离线证据替代实测。

## 1. 寄存器表（逐项标出处行号）

| 偏移 | 方向 | 语义 | 出处行 |
|---|---|---|---|
| `0x000` | R | ID = `0x53324250`（ASCII `S2BP`） | L619 |
| `0x004` | R | VERSION = `0x100` | L619 |
| `0x008` | **W** | **命令编码**：`1` = START（配置后启动）；`4` = **ACK 提交**（需 epoch/frame/status 匹配且 `is_idle()` 前置） | L367、L291 |
| `0x00C` | R | **status 字**：`[2:0]` = state（`0` IDLE、`1` ARMING、`2` RUN、`4` DONE_SAFE、`5` ERROR_SAFE、`6` FAULT_ISOLATED）；`bit8` OWNER_PL、`bit9` HEAD_VALID、`bit10` SAFE_REUSE、`bit11` TERMINAL、`bit12` AXI_PENDING、`bit13` FIRST_PENDING | L43–L52、L202–L204、L470 |
| `0x010` | R | error code（`DONE_SAFE` 时须为 0） | L210、L222 |
| `0x014` | W | frame id | L365 |
| `0x018` | W | 写 `0`（**语义未知，见 §4 ASSUMED_UNVERIFIED**） | L365 |
| `0x01C` | W | input_bytes（OP_RUN 时 = 519,168） | L365、L463 |
| `0x020` | W | input base = `0x00100000` | L366 |
| `0x024` | W | weight bytes = 5,903,100 | L366 |
| `0x028` | W | core timeout | L367 |
| `0x02C` | W | drain timeout | L367 |
| `0x030/034` | R | arena base `0x10000000` / arena bytes `0x02000000` | L620 |
| `0x038/03C` | R | feature 起止 `0x01000000` / `0x01ADADB8` | L621 |
| `0x040/044` | R | head13 偏移 `0x01A46100` / 字节 5,070 | L622 |
| `0x048/04C` | R | head26 偏移 `0x01AD5E80` / 字节 20,280 | L623 |
| `0x050/054` | R | **epoch 低 / 高**；读取须"读高→读低→再读高"，两次高相等才接受（8 次重试） | L195–L196 |
| `0x058` | R | frame | L210 |
| `0x05C/060` | W | **ack_epoch 低 / 高**（ACK 前写入，配合命令 4） | L290 |
| `0x064` | R | reject code | L210 |

常量：`INPUT_BYTES=519168`（L31）、`WEIGHT_BYTES=5903100`（L32）、`HEAD13_BYTES=5070`（L33）、`HEAD26_BYTES=20280`（L34）、`ARENA_BYTES=0x02000000`（L35）。

## 2. 板上真实时序（r13 成功路径）

1. **idle 判据**（L200–L204）：`(status & 7) == 0` 且 `SAFE_REUSE` 置位，且 `OWNER_PL|AXI_PENDING|HEAD_VALID|TERMINAL|FIRST_PENDING` 全为 0。
2. **读 epoch**（L191–L199）：双读高字校验，得 `before`；`expected = before + 1`（L368）。
3. **prepare_cache**（L229–L234）：flush 输入区 `arena+0..INPUT_BYTES`、flush 权重区 `0x00100000..WEIGHT_BYTES`、flush+invalidate feature 区，均 64 B 外对齐，前后 `DSB`。
4. **configure_start**（L361–L370）：写 `0x014=frame`、`0x018=0`、`0x01C=input_bytes`、`0x020=0x00100000`、`0x024=WEIGHT_BYTES`、`0x028=core_timeout`、`0x02C=drain_timeout` → **`0x008=1`（START）**。
5. **完成/安全终态**（L214–L224）：state ∈ {`DONE_SAFE(4)`, `ERROR_SAFE(5)`} 且 `(SAFE_REUSE|TERMINAL)` 均置位、`(OWNER_PL|AXI_PENDING|FIRST_PENDING)` 全 0；`DONE_SAFE` 额外要求 `HEAD_VALID` 且 `error==0`。
6. **结果读回**（L266–L269）：`arena+0` 前 256 B、`arena+0x01A46100` head13、`arena+0x01AD5E80` head26；读前 **invalidate** feature/head 对应范围。
7. **ACK 收尾**（L286–L293）：再次 `safe_snapshot` 且 epoch/frame/status 全匹配 → 写 `0x05C=epoch_lo`、`0x060=epoch_hi` → **`0x008=4`** → 必须回到 `is_idle()`。
8. **超时/故障**（L371–L377）：轮询中遇 `FAULT_ISOLATED(6)` 或超时（r13 用 400 s）⇒ 判失败，不 ACK。

## 3. M4-b 自检模式（按上述语义重写）

判据（窗口内实测，任一项不满足即 FAIL，不得离线替代）：

| 编号 | 判据 | 实现 |
|---|---|---|
| M4b-1 PS→PL 可见性 | PS 写的输入张量被 PL 经 HP0 读到并用于推理 | 主机预置输入到 `arena+0`（PS 侧 flush+DSB 后 START）；成功判据由 M4b-2 的结果等价证明 |
| M4b-2 PL→PS 可见性 | PL 写出的 head13/head26 在 PS **invalidate 后**与冻结参考**逐字节相等** | 读回 `arena+0x01A46100`(5,070 B)、`arena+0x01AD5E80`(20,280 B) 与主机预置参考比对，`diff` 必须 0 |
| M4b-3 完成序门控 | START 后、`DONE_SAFE` 前读 `status` 必须观察到 `ARMING(1)`/`RUN(2)` 且 `OWNER_PL` 置位、`HEAD_VALID|TERMINAL|SAFE_REUSE` 未置 → 才算"提前读被门控"；若首次轮询已是 `DONE_SAFE` ⇒ 记 `INCONCLUSIVE`（**不得**记 PASS） | 轮询第一拍快照 |
| M4b-4 陈旧检测 | 运行前 head 与参考不同（可分辨新旧）；相同 ⇒ 无法判新旧 ⇒ FAIL | 运行前 invalidate 后读 head13 首 16 B 比对 |
| M4b-5 ACK 收尾 | `0x05C/0x060` + `0x008=4` 后必须 `is_idle()` | ack 后立即 `is_idle()` |

输出（UART 单行 JSON）：`M4B RESULT={"pass":..,"diff13":..,"diff26":..,"first_diff13":..,"first_diff26":..,"stale":..,"premature":"BLOCKED|INCONCLUSIVE","ack_idle":..}`。

## 4. ASSUMED_UNVERIFIED（必须窗口内只读观测确认，先观察后结论）

| # | 事项 | 依据缺口 | 窗口内确认方式 |
|---|---|---|---|
| A1 | `0x018` 写 `0` 的语义（r13 只写 0，未说明用途） | 源码无注释 | 先按原样写 0；若启动失败，记录 reject/error 后停 |
| A2 | **CSR 版本身份**：r13 写 `0x014/018/01C/020/024/028/02C` 等配置寄存器；而 `w2b/src/s2b_control_csr.sv` 的写白名单被报告为仅 `0x008/0x05C/0x060` | 两处来源冲突（r13 源码 vs 2B RTL） | **窗口前确认所用 bitstream 内含哪一版 CSR**；若用 2B `555a70c2…` 且其 CSR 白名单确为 3 个，则配置写会被拒 ⇒ M4-b 需改用含 r13 版 CSR 的 bit/XSA（`ea52da1b…` 对应平台） |
| A3 | "提前读必须被拒"的**硬件机制**（是拒绝返回还是仅状态位可见） | 源码只体现"轮询 status 观察"，无"拒绝读"的直接证据 | 窗口内只读观测：START 后连续快照 state/OWNER_PL/HEAD_VALID，按观测下结论；不得据源码推断为硬件拒读 |
| A4 | `core_timeout`/`drain_timeout` 取值对本次 519,168 B 结果的影响 | r13 由 host 传入具体值，源码未给常数 | 窗口用 r13 同档值（如 400 s 轮询上限）并如实记录实际值 |
| A5 | 权重必须先装载（5,903,100 B） | r13 先 `OP_WEIGHTS` 再 `OP_RUN` | 窗口须先经 r13 路径装载权重，或在同一应用内实现权重装载；**不得**假定权重已在 DDR |

## 5. 明确未做

- 未接触板卡；未启动 `hw_server`/`xsdb`；`ENABLE=0`；未 FROZEN。
- 未做 PL letterbox / AXI / BD / `build_r03`（按 lead 指令暂停）。
- 本文件的寄存器行号绑定 r13 源文本；若该源文本被替换（不同 SHA），本文件需重绑。

> 窗口参考数据布局：host 把 head13 期望（5,070 B）放到 RAW+0x0000，head26 期望（20,280 B）放到 RAW+0x2000；输入张量与权重需由 host/装载流程预置到 `arena+0` 与 `arena+0x00100000`。

## 6. w2b RTL 交叉核对（`w2b/src/s2b_control_csr.sv`，2026-10-27 补）

r13 源码与 w2b RTL **一致**，此前"仅 3 个可写地址"的说法不完整，已按下表更正（RTL 行号为准）：

| 项 | RTL 事实 | 行号 |
|---|---|---|
| 写白名单 | `address_write_ok = 0x008` **或** `0x014..0x02C` **或** `0x05C` **或** `0x060` | L110–L112 |
| 读白名单 | `<0x074`（除 `0x008`）以及 `0x100..0x13C` | L101–L103 |
| `0x008` 命令 | `wdata==1` = START（ARMING→RUN）；`wdata==2` = ABORT（仅 ARMING/RUN 有效）；`wdata==4` = ACK 提交 | L113–L115、L173–L184 |
| ACK 前置 | `q_safe`、`ack_epoch==epoch`、`status_shadow[2:1]==0`、`ledger_empty`、`!isolated`、`!protocol_isolated`、`!fault_event_valid`、`visibility_confirmed` | L180–L184 |
| `0x00C` status 位 | `[2:0]` state（0 IDLE_PS/1 ARMING/2 RUN/3 RECOVERING/4 DONE_SAFE/5 ERROR_SAFE/6 FAULT_ISOLATED）；`bit8` owner(PL)；`bit9` head(HEAD_VALID)；`bit10` safe_reuse；`bit11` terminal；`bit12` `!ledger_empty_next`；`bit13` first_pending | L359–L363 |
| 读映射 | `0x000`=0x53324250、`0x004`=0x00000100、`0x00C`=status、`0x010`=error_code、**`0x014`=frame**、**`0x018`=input_addr**、`0x01C`=input_bytes、**`0x020`=weight_addr**、`0x024`=weight_bytes、`0x028`=core_timeout | L364–L374 |
| 状态语义 | `state` 见 L43；`q_safe` = DONE_SAFE\|ERROR_SAFE（L86）；`status_shadow` 由内核 4 位状态采样（L200–L203） | L43/L86/L200–L203 |

**与 r13 的对应关系（关键，消除此前"A2 冲突"）**：r13 的 `csr_write(0x018, 0)` = `input_addr=0`（输入在 arena+0）；`csr_write(0x020, 0x00100000)` = `weight_addr=0x00100000`；`csr_write(0x024, WEIGHT_BYTES)` = `weight_bytes`；`0x014` 写 frame、读回也用 `0x014`（r13 另用 `0x058` 读 frame，RTL 读映射未列 0x058 ⇒ 标 A6）。

**新增 ASSUMED_UNVERIFIED**：
| # | 事项 | 缺口 | 窗口内确认 |
|---|---|---|---|
| A6 | `0x058`（r13 读 frame 处）RTL 读映射未列出 | RTL L364–L374 无 0x058 | 窗口内改读 `0x014`；若需 0x058 语义再只读观测 |
| A7 | `visibility_confirmed` 的真实来源与时机（ACK 前置之一） | RTL 引用但未展开 | 窗口内以 ACK 是否被接受（`is_idle` 收敛）反推，不预判 |
