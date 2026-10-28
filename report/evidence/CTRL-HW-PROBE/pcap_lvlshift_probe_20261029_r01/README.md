# PCAP/电平转换 探针（2026-10-29 02:18–02:21，DSH）

## 目的
定位"应用首次读 CSR 就挂住"（r06）的性质：是 PL 未配置、还是 PS↔PL 通路不通。

## 步骤与原始结果（全部普通命令，未用 -force）
1. 枚举：targets = APU / A9#0 Running / A9#1 Running / xc7z020；jtag = HS1 / arm_dap(4ba00477) / xc7z020(23727093)。
2. 编程前 DevCfg 读数：0xF8007000=4E00E07F、0xF8007004=0000001A、0xF8007008=00000508、0xF8007080=30800100。
3. Vivado batch `program_hw_devices`（bit `555a70c2…`）：exit 0，输出 `PROGRAM_DONE`。
4. 编程后 DevCfg 读数：与编程前**完全相同**。
5. `mrd 0xF8000900`（LVL_SHFTR_EN）= **0x00000000** ⇒ 电平转换未使能。
6. CSR 读（未使能）：`Cannot access FPGA: Level shifters are not enabled`。
7. 写 SLCR：解锁 `0xF8000008=0xDF0D` → `0xF8000900=0x0000000F` → 锁 `0xF8000004=0x767B`；回读 `0xF8000900=0x0000000F`（确认写入）。
8. 再次 CSR 读：`Timeout waiting for the Instruction Complete bit` ⇒ AXI 读已发出、**无响应**。
9. 随后 DAP 进入粘连态：`APB AP transaction error, DAP status 0xF0000021 / 0x30000021`；A9 核从 targets 消失，`rst -dap` 返回 Invalid target。

## 结论与边界（不许overclaim）
- **已证**：本次探针把 CSR 读做成了"**AXI 读无响应**"（timeout），与长跑停住的现象同类（PS 侧对 PL 读不返回，CPU 无 AXI 超时 ⇒ 永久挂住）。
- **未证**：**不能**据此判定位流损坏——本探针**未运行 `ps7_init`**，FCLK0 与 `peripheral_aresetn` 未配置，PL 从口无时钟/复位时本就无响应。
- 新线索：`program_hw_devices` 报成功后 `LVL_SHFTR_EN=0`；若应用路径里 init 之后该位仍为 0，则**首次 CSR 读必挂**，可解释 r06。
- 边界：DAP 已粘连，按项目规则**只能整机断电（12V+USB ≥10 s）**恢复；期间不得再用 `-force`。

## 下一步（断电后）
1. `dow init.elf; con`（执行 ps7_init）→ 停核 → 读 `0xF8000900`；
2. 读 CSR ID `0x43C00000`：
   - 若 SHFTR=0 ⇒ 应用路径未使能电平转换（**根因**）；
   - 若 SHFTR=0xF 但 CSR 仍 timeout ⇒ 位流/PL 时钟复位问题（另查 DevCfg PCFG_DONE）。
