# 2B 位流 `555a70c2…` 的 CSR 基址与访问通路审计（S4-T34，2026-10-28 r01，离线只读）

- 目的：为窗口 #3 的"`0x43C00000` 无响应 / 内存映射被拒"定位**可核事实**，不再靠假设。
- 范围：**只读** w2b 树（`D:\FPGA_Competition\w2b`，HEAD `07c3d3958578b9cc9d3b8eae3758711fe08724c2`）与本地 UG585 原件；**未接触板卡**。
- 被审位流：`D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.bit`
  （SHA-256 前缀 `555a70c2`，即窗口 #1/#2/#3 实际装载的位流）。

## 0. 结论摘要（对应总控六问）

| # | 问题 | 结论 | 依据 |
|---|---|---|---|
| 1 | **真实 CSR 基址** | **`0x43C00000`**，`range=0x00010000`（64 KiB），从口 `infer/S_AXI/reg0`，落在 **`ps7/Data`** 地址空间 | `s2b_inference_bd.tcl:409` |
| 2 | **通路（GP0/GP1）** | **GP0**：`ps7/M_AXI_GP0`（AXI3, 32-bit, 12-bit ID）→ `axi_gp0_lite`（AXI3→AXI4-Lite, `TRANSLATION_MODE=0`）→ `infer/S_AXI`；PL 侧 `infer/M_AXI`（64-bit）→ `ps7/S_AXI_HP0` | `bd.tcl:388, 384, 385`；`PCW_USE_M_AXI_GP0=1`(`:325`)、`PCW_USE_S_AXI_HP0=1`(`:330`) |
| 3 | **时钟/复位条件** | 时钟 **`FCLK_CLK0` = 50 MHz**（`PCW_FPGA0_PERIPHERAL_FREQMHZ {50}`、`PCW_FCLK_CLK0_BUF TRUE`、`PCW_FPGA_FCLK0_ENABLE 1`）驱动 `M_AXI_GP0_ACLK`/`S_AXI_HP0_ACLK`/`axi_gp0_lite/aclk`/`rst_fclk0/slowest_sync_clk`/`infer/clk`；复位：`ps7/FCLK_RESET0_N → rst_fclk0/ext_reset_in`，`rst_fclk0/peripheral_aresetn → axi_gp0_lite/aresetn + infer/cold_resetn`；**另有 `ps7_post_config` 四动作（见 §2）** | `bd.tcl:279-281, 396-406`；`s2b_board_jtag.py:25-27, 199-200` |
| 4 | **2B 当时访问方式** | **两种都有**：① JTAG 直读/直写（`s2b_board_jtag.py`，且**先用 `loadhw` 把 `[0x43C00000,0x43C0FFFF]` 登记进调试器内存映射**）；② **PS 程序访问**——CPU `STR` 到 `0x43C00008` 触发原生外部同步写异常（DFAR=`0x43C00008`、opcode `0xE5801000`），证明 **PS→PL 通路在 2B 是成立的** | `test_s2b_visibility_probe.py:618`；`s2b_board_jtag.py:569-578`；`S2B-T20/bresp_composition_review_20261021_r01/analysis.md:22-23` |
| 5 | **与 `0x43C00000` 是否一致** | **一致**（BD 地址段、`s2b_inference_app.c:36` 的 `#define CSR_BASE 0x43C00000U`、`board/s2b_inference_platform.json:17` 三者一致） | 同左 |
| 6 | **若不一致的正确值** | **不适用**（一致） | — |

## 1. 因此窗口 #3 的两个现象各有解释

1. **r03 `PL AXI slave ports access is not allowed. This address has not been added to the memory map`**
   ⇒ **不是硬件故障**：xsdb 的 `mrd` 要求地址先在调试器内存映射里。2B 的做法是 `loadhw` 时登记
   `[[0x43C00000, 0x43C0FFFF]]`（`test_s2b_visibility_probe.py:618` 断言第三次调用即此），我们的流程**没有登记**。
2. **r04 `mrd -force` 的 `Timeout waiting for the Instruction Complete bit`**
   ⇒ 说明该时刻 AXI 事务未完成。**但不能据此断言 CSR 不可访问**——`-force` 绕过映射后的事务可能在
   PL 软复位/时钟未就绪时挂起；本项按总控规则**已禁用 `-force`**，不再作为判据。

## 2. 关键发现：2B 的 `ps7_post_config` 是**四动作**，我们只做了两个

2B 的 XSA 生成表被逐动作断言（`s2b_board_jtag.py:199-200`）：

```python
expected = [("WRITE",     SLCR_UNLOCK,   0xDF0D),
            ("MASKWRITE", LEVEL_SHIFTER, 0xF, 0xF),
            ("MASKWRITE", FPGA_RESET,    0xFFFFFFFF, 0),
            ("WRITE",     SLCR_LOCK,     0x767B),
            ("EXIT",)]
```
常量（`s2b_board_jtag.py:25-27`）：`SLCR_LOCK=0xF8000004`、`SLCR_UNLOCK=0xF8000008`、
`LEVEL_SHIFTER=0xF8000900`、**`FPGA_RESET=0xF8000240`**、`FPGA0_CLOCK=0xF8000170`。

UG585 原件核对（`ug585-Zynq-7000-TRM.pdf`，v1.2, Aug 8 2012）：
- **`slcr.FPGA_RST_CTRL`**：绝对地址 **`0xF8000240`**、相对 `0x00000240`、32-bit、`rw`、"FPGA Software Reset Control"
  （Appendix B 寄存器汇总 PDF 页 1412 / 文档页 1406；寄存器详表 PDF 页 1454）。
- 语义：`FPGA[3:0]_OUT_RST` 等 FPGA 输出软复位控制，**异步于 FCLK**，写明由 `slcr.FPGA_RST_CTRL` 控制
  （§2.6 PL–PS Signals，PDF 页 47）。
- 写 `0` = **撤销全部 FPGA 软复位**（复位位为 0 才允许 PL 侧 AXI 正常工作）。

**差距**：驱动 v3.2.2 的 `lvl_shifter_tcl()` 只做 `unlock → LVL_SHFTR_EN → lock`，
**缺 `mwr 0xF8000240 0x0`（FPGA_RST_CTRL=0）**。若该寄存器被之前会话/复位状态留下了非 0 位，
PL 的 AXI 从口会**被软复位按住**，PS 读 CSR 即表现为**挂起/超时**——与窗口 #2/#3 的 `M4B STEP=1` 现象一致。
⇒ **窗口 #4 之前应把这一动作补进驱动（v3.2.3）并加自检**，这是本轮审计给出的最具体修复项。

## 3. 对我们流程的三条修正建议（供总控裁决，本文件不自行改判据）

1. **补 `FPGA_RST_CTRL = 0`**（2B 四动作的第 3 个），放在 `LVL_SHFTR_EN=0xF` 之后、`SLCR_LOCK` 之前；
2. **不再用 JTAG `mrd` 直探 CSR**（若确需，必须先 `loadhw` 登记 `[0x43C00000,0x43C0FFFF]`；且**禁用 `-force`**）；
   M4-b 的有效证据只能来自应用 UART 的 `M4B STEP/CSR/RESULT/HEADS`；
3. **一次性自检**：把"四动作序列 + 读回 `0xF8000900=0xF` 且 `0xF8000240=0x0`"写成离线断言（mock 亦可）。

## 4. 限制（不得外推）

- 本次审计对象是 **2B 位流**；**阶段4 的 4-D 设计若另有 BD/地址图，必须独立重核**（本审计不覆盖 4-D 位流）。
  **注意**：窗口 #1–#3 实际装载的都是这个 2B 位流（`555a70c2…`），因此"装 2B 位流却要求 4-D 的 M4-b 行为"
  本身是需要在 G0 明确的事实。
- 未上板验证；`FPGA_RST_CTRL` 的实际读值、`LVL_SHFTR_EN` 与 CSR 可达性的因果关系**待 POR 后实测**。
- 本文件不主张 G3/G4/G5，也不改变 M3/M2 的未闭合状态。

## 5. 哈希基座（`hash_basis`）

- `commit_blob`：w2b HEAD `07c3d3958578b9cc9d3b8eae3758711fe08724c2` 下的已跟踪文件，按
  `git cat-file blob <commit>:<path>` 计（内容权威，不受 autocrlf 影响）：
  - `verification/s2b_board_jtag.py` → blob `118b912a3a883e43e2dcf49f55d648ea84511b9d`
  - `vitis/s2b_inference_app.c` → blob `731284b24b719afdf7d01965c27bb6b72e5aeb7a`
  - `board/s2b_inference_platform.json` → blob `5fbabab2fb9e53bebfb09caadedd5f589a93c800`
- `commit_blob`（构建产物，用**逐字节相同的已跟踪副本**提供基座）：
  - `report/evidence/S2B-T15/csr_fixed_platform_offline_20261016_r03/artifacts/ps7_init.tcl` →
    blob `053c979ba9bbf179fe6fea65fc4c748daed7e86f`（与 r04 副本**同 blob**，逐字节相同）
  - `report/evidence/S2B-T13/platform_csr_fixed_20261016_r03/s2b_inference_bd.tcl` →
    blob `19ffc609dde2f2dceb2c82fb9936f6e97a3c7cce`（**佐证**：与 r04 副本非逐字节同，但
    `0x43C00000/64 KiB@ps7/Data`、`FCLK 50 MHz`、`FCLK_RESET0_N→rst_fclk0`、
    `peripheral_aresetn→axi_gp0_lite/aresetn+infer/cold_resetn` 三处赋值逐行一致）
- `worktree_disk`（**仅附注**）：随被审位流出厂但**未入库**的 BD 副本
  - `.../visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference_bd.tcl` →
    `4e8c319f994378b72a853f670dd97f94c55c696a64c1191f93eb4af5a4d0ae0b`
    （其 blob `ebf62b45…` 不在任何提交内）
  - `.../artifacts/ps7_init.tcl` → `430030c232057ae1e8a91f7e63cd30c06aaa27b78ac9eda52c5bc4deca81510c`
    （内容与上面已跟踪副本逐字节相同，故主引用用 commit_blob）
- 本目录自身两份文件（README / findings）尚未提交，提交后由总控按 `commit_blob` 重算覆盖。

机器可读版本见同目录 `csr_base_findings.json`。

## 6. 位流适用范围（G0 事实，2026-10-28 总控要求补记）

1. **窗口 #1–#3 实际装载的都是 2B 位流** `555a70c2…1047ef7`
   （`report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit`）。
   用该位流去验 **M4-b（`0x43C00000` CSR + HP0 DMA）** 属于**跨阶段复用（2B 平台 → 4-D 行为）**，
   需要在 G0 层面被显式承认，不能默认"2B 通过即 4-D 通过"。

2. **M4-b 结论的适用性边界（明确写死）**：
   - 本次（窗口 #1–#3，以及 POR 后窗口 #4）M4-b 的任何结论，**仅适用于"2B 平台位流上的 4-D PS 侧行为"**；
   - **不覆盖 4-D 自建位流**。4-D 位流产出后，其 **BD / 地址图 / 时钟复位连线必须独立重核**，
     并重新执行 M4-b（不得沿用 2B 位流上的通过结论）。

3. **`Blocked address` 属工具限制（复述，保留）**：2B 的 JTAG 访问靠 `loadhw` 把
   `[0x43C00000, 0x43C0FFFF]` 登记进调试器内存映射
   （`verification/test_s2b_visibility_probe.py:618`）；未登记时 xsdb 报
   `PL AXI slave ports access is not allowed … not been added to the memory map`。
   这是**调试器侧限制，不是硬件故障**，也**不得**用 `mrd -force` 绕（会锁死 DAP）。
   ⇒ **CSR 可达性的判据只认应用 UART 的 `M4B STEP/CSR/RESULT/HEADS` 行**，不认 JTAG `mrd`。

