# M4-b 状态解码 / preload 地址 / 超时判定（S4-T34，2026-10-28 r01，离线）

- 输入事实：窗口 #4 r05（`bringup_window4_20261028_r05`）实测 UART：
  `spin=0 status=0x00001102`、`spin=1 status=0x00000C05 error=0x00000005`、
  `M4B RESULT={"pass":0,"done":2,...,"status":3077,"error":5}`。
- **全离线**：未接触板卡；`w2b` 只读；不改判据；不主张 G3/G4/G5。

## 1. status 位拆解（位定义出自 `w2b/src/s2b_control_csr.sv:359-363`）

| 位 | 含义 | `0x1102` | `0x0C05` |
|---|---|---|---|
| `[2:0]` | state：0 IDLE_PS / 1 ARMING / 2 RUN / 3 RECOVERING / 4 DONE_SAFE / 5 ERROR_SAFE / 6 FAULT_ISOLATED（`sv:43-44`） | **2 = RUN** | **5 = ERROR_SAFE** |
| bit8 | owner(PL) | **1** | 0 |
| bit9 | head(HEAD_VALID) | 0 | 0 |
| bit10 | safe_reuse | 0 | **1** |
| bit11 | terminal | 0 | **1** |
| bit12 | `!ledger_empty_next`（账本非空） | **1** | 0 |
| bit13 | first_pending | 0 | 0 |

**两次 spin 的跃迁**：
- `spin=0`：**state=RUN、PL 持有(owner=1)、账本非空(bit12=1)、无 head、非 terminal**
  ⇒ **START 已被硬件接收，PL 已进入 RUN 且事务在飞**（不是"没启动"）。
- `spin=1`：**state=ERROR_SAFE、owner 已释放、safe_reuse+terminal 置位、账本已空、无 head**
  ⇒ PL 在 RUN 后**以"安全终态"结束**，并给出 `error=5`。**这是 PL 主动上报的终态，不是轮询超时**。

## 2. `error=5` 的官方含义 = **CORE_TIMEOUT**（核心超时）

| 依据 | 原文/事实 |
|---|---|
| `s2b_physical_interface_candidate.md:73`（blob `682b96f1…`） | `0x010 ERROR_CODE`：`0 NONE`、**`1..7` 为保留的 2A 码**、`8 ABORTED`、`9 AXI_S…` |
| `stage2b_fixed_input_acceptance_20261022.md:22`（blob `e75560c2…`） | "R12 正常 START、**CORE=10000/DRAIN 最大值错误5安全ACK**…" ⇒ **core 超时对应的 error 码就是 5** |
| `w2b/.codex/STATE.md:25`（blob `da6ae3b1…`） | "R12 真实完成正常 START 47.4058308s、**CORE10000/DRAIN 最大值→ERROR_SAFE5**/ACK" |
| `s2b_control_csr.sv:209`（blob `f614c93d…`） | `error_code = (core_csr_rdata>=1 && <=7) ? core_csr_rdata : 6` ⇒ 1..7 **由 PL 内核/适配器上报**（非 CSR 层自造） |
| `s2b_control_csr.sv:253-255` | CSR 层**配置校验**码另有分工：地址不符→`2`、字节数不符→`3`、超时为 0→`1` ⇒ **`5` 不是配置错误** |

⇒ `error=5` = **CORE_TIMEOUT**：PL 在核心期限（`core_timeout` 周期数）内未完成推理，转入 ERROR_SAFE 并置 safe_reuse/terminal（可安全复用、无需 DRAIN 恢复）。

## 3. 为什么是 CORE_TIMEOUT：`core_timeout=400` 太小（根因）

应用源码 `vitis/stage4/ps/s4d_ps_app.c`（w4 HEAD `3e83900e…`，blob `564b1a64…`）：

```c
L466:  s4d_wr(S4D_CSR_CORETO_W, 400u);    /* core_timeout  = 400 周期 */
L467:  s4d_wr(S4D_CSR_DRAINTO_W, 400u);   /* drain_timeout = 400 周期 */
```

- 400 周期 @ 名义 50 MHz = **8 µs**；
- 而 2B 实测**真实整帧 START 完成 = 47.4017962 s**（R11，`w2b/.codex/STATE.md:24`）；
- 2B **冻结部署值**为 `CORE_TIMEOUT_CYCLES = DRAIN_TIMEOUT_CYCLES = 0xFFFFFFFF`
  = 名义 **85.8993459 s** @50 MHz（`stage2b_fixed_input_acceptance_20261022.md:41`）；
- 2B 的完整 START 包络估算 = ×50 MHz ×1.25 = **2,962,864,425 周期**（`w2b/.codex/STATE.md:28`）。

⇒ 400 周期必然**立刻**触发 core timeout ⇒ 与实测"RUN 一拍后即 ERROR_SAFE(5)"完全一致。

## 4. preload 地址核对 —— **符合（无地址错误）**

### 4.1 由 RTL 配置校验反证（最强证据）
`s2b_control_csr.sv:253-257`：START 时若
`input_addr != 0` **或** `weight_addr != 0x00100000` **或** `input_bytes != 519168` **或**
`weight_bytes != 5903100` **或** `core_timeout == 0` **或** `drain_timeout == 0`
⇒ **立即 ERROR_SAFE 且 error_code ∈ {1,2,3}**。
实测 `spin=0` 已达 **RUN** ⇒ **上述全部校验通过** ⇒ **地址与字节数全部正确**（`core_timeout/drain_timeout` 也非 0，故未触发 code 1）。

### 4.2 逐项对照 2B 冻结对象

| 项 | 应用/驱动实际 | 2B 冻结对象 | 结论 |
|---|---|---|---|
| 输入张量 | `input_addr=0`（arena+0）+ `input_bytes=519168` ⇒ `[0x10000000, 0x1007EC00)` | tensor `[0x10000000, 0x1007EC00)` | **精确一致** |
| 权重 | `weight_addr=0x00100000` + `weight_bytes=5903100` ⇒ `[0x10100000, 0x106A12FC)` | GF8 `[0x10100000, 0x106A12FC)` | **精确一致**（5,903,100 = 0x5A12FC） |
| head13 输出 | PL 写 `arena+0x01A46100` = `0x11A46100`，5,070 B → 末 `0x11A474CE` | feature 包络 `[0x11000000, 0x11ADADB8)` | **在包络内** |
| head26 输出 | PL 写 `arena+0x01AD5E80` = `0x11AD5E80`，20,280 B → 末 `0x11ADADA8` | 同上（上界 `0x11ADADB8`） | **在包络内** |
| 参考 head（比较基准） | 应用 `ref = S4D_RAW_BASE = 0x12000000`，`ref+0x2000` 为 head26 期望（`s4d_ps_app.c:428/500-501`） | 驱动 preload：head13→`0x12000000`、head26→`0x12002000` | **一致** |

### 4.3 "PL 的 HP0 写入地址由谁决定"
- 由 **PL 侧**（适配器/内核）在运行期经 HP0 直接写入 arena 的固定偏移；
  PS 通过 CSR **只读**寄存器获知该偏移：`0x040/0x044` = head13 偏移/字节、`0x048/0x04C` = head26 偏移/字节
  （`S4D_HEAD13_OFF=0x01A46100`、`S4D_HEAD26_OFF=0x01AD5E80`，见 `s4d_ps_app.c:292-294`；语义表见
  `docs/stage4/S4D_m4b_csr_semantics_20261027_r01.md` §1）。
- **PS 不配置** head 写地址；因此"从 `0x12000000` 读 head"不是读 PL 输出，而是读 **host 预置的参考**——
  应用实现与设计一致，**无地址错**。

## 5. 判定：**是超时问题（CORE_TIMEOUT），不是内核功能错误、不是地址错**

建议（**只调超时/预算，不动判据**）：
1. `core_timeout = drain_timeout = 0xFFFFFFFF`（2B 冻结部署值，名义 85.8993459 s @50 MHz）；
2. 轮询预算：应用当前 `for (spin=0; spin<50000000u; spin++)`（`s4d_ps_app.c:481`）——若单次快照约 1 µs，
   上限仅约 50 s，**低于 2B 实测 47.4 s + 余量**，建议提到 **≥1.5e8 次**（或显式 120 s 墙钟），
   并在 `M4B RESULT` 里同时输出实际耗时；
3. 判据本身（两 diff 逐字节相等、门控、ACK）**不变**。

## 6. 依据清单（含 `hash_basis`）

| 文件 | 行/位置 | hash_basis | 哈希 |
|---|---|---|---|
| `w2b/src/s2b_control_csr.sv`（w2b HEAD `07c3d395…`） | 43-44, 86, 101-115, 173-184, 209, 253-257, 359-363, 364-374 | `commit_blob` | blob `f614c93dfec338f1dcea3ccc09b3a76746e6fcf6` |
| `w2b/docs/.../s2b_physical_interface_candidate.md` | 73（`0x010` 码表） | `commit_blob` | blob `682b96f165708c0f1aa62cf9032dcdac97a7ad5c` |
| `w2b/docs/.../阶段验收/stage2b_fixed_input_acceptance_20261022.md` | 22（CORE=10000→错误5）、41（0xFFFFFFFF=85.8993459 s） | `commit_blob` | blob `e75560c2faca57649cef0437619f38b7a2922ed9` |
| `w2b/.codex/STATE.md` | 24（R11 47.4017962 s）、25（R12 错误5）、28（包络 2,962,864,425） | `commit_blob` | blob `da6ae3b10775c7d65764e2d4e2b32df403645f6b` |
| `w4/vitis/stage4/ps/s4d_ps_app.c`（w4 HEAD `3e83900e…`） | 31-32, 292-294, 428, 466-467, 481, 500-504 | `commit_blob` | blob `564b1a64c4ff4a302f4842cd1028bec63c4f4be9` |
| `docs/stage4/S4D_m4b_csr_semantics_20261027_r01.md` | §1 寄存器表、§2 时序、§6 w2b 交叉核对 | `worktree_disk`（本树文档，提交后由总控按 commit_blob 重算） | — |

## 7. 限制

- 本分析基于**离线源码/文档 + 一次实板 UART**；未在板上验证"改成 0xFFFFFFFF 后能否 DONE_SAFE"。
- `error=5` 的"1..7 = 2A 保留码"中，**5 的 2A 侧字面定义**未在 w2b 文档逐字给出；本文件据 **R12 的 CORE 超时实测**
  与 **RTL 透传 1..7** 判定为 CORE_TIMEOUT，属**有实测支撑的推断**，非文档逐字定义 —— 若需逐字定义，应查 2A 阶段
  的 CSR/内核码表（本轮未展开）。
- 不改 M4-b 判据、不主张 G3/G4/G5；M3/M2 仍未闭合。