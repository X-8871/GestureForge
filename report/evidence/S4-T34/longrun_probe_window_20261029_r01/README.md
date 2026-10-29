# 探针窗口：长跑首次 CSR 读挂死定位（2026-10-29 11:40–12:15，lead 执行）

## 目的
r06：应用打印到 `LONGRUN STEP=1` 后 1100 s 零输出，停在首次 CSR 访问。用「探针应用 + 两种位流 A/B」定位：
是 PS 侧配置（电平转换/时钟/复位）问题，还是 PL/CSI 侧问题。

## 探针应用
`s4d_ps_app_sw0_longrunP.elf` SHA `faa399b268e35a2f7d0bef7ecbcb38ebef444abdd7fb0a50351db46e3d6def2c`：
在首次 `s4d_is_idle()` 之前打印 `LVL_SHFTR_EN / FCLK_CTRL0 / APER_CLK_CTRL / FPGA_RST_CTRL`（PS 读 SLCR，不依赖 PL）。

## 窗口流程（两次，同一脚本、只换位流）
`rst -system -stop → dow init.elf(ps7_init) → Vivado program_hw_devices(exit 0) → LVL_SHFTR_EN=0xF(读回) → dow 探针应用 → con → 抓 COM4`

### A/B 结果
| 位流 | UART | 结论 |
|---|---|---|
| **P2a（我方 preproc 设计，CSR@0x43C10000）** | `PROBE slcr shftr=0x0F fclk0=0x00600600 aper=0x1F000200 fpga_rst=0x0` → `RESULT={"exit":1,"reason":"not_idle","status":519168}` | **CSR 读返回**（地址未映射，值无意义），应用 fail-fast 退出 |
| **2B（`555a70c2…`，CSR@0x43C00000）** | 同上 PROBE 行 → **之后无任何输出**（无 RESULT/DONE） | **首次 CSR 读挂死**（与 r06 同现象复现） |

⇒ **SLCR 状态两次完全相同**（`shftr=0xF`、`fpga_rst=0`、`fclk0=0x00600600`）⇒ **不是电平转换/时钟/复位配置问题**。

## 挂死后 JTAG 侧取证（关键）
在挂死现场（核已停）用 `loadhw` + `mrd` **直接读 2B CSR**：
```
LOADHW   = s2b_inference_wrapper
CSR_ID   = 0x53324250        ("S2BP")
CSR_STATUS = 0x00000C05      (低 3 位 = 5 = ERROR_SAFE；bit10/bit11 = safe_reuse/terminal)
DDR 读    = 0x11B00000 → 0x00000000（应用魔数在 cache 未刷，故物理读 0，不能据此判"未写入"）
核心状态  = Stopped: (Vector Catch)，PC=0x00000000，CPSR=0x000001D3(SVC)
```
⇒ **PL 从口对 JTAG 侧读是响应的**（ID/STATUS 正常返回），**挂的是 PS 侧访问路径**
（GP0 → `axi_gp0_lite`(AXI3→AXI4-Lite 转换) → 2B CSR）。这与 Codex 2026-10-29 的提醒一致：
"需核对实际 AXI3 单拍事务约束与冻结 XSA 配置"。

## 结论（分级）
- **已证**：① P2a 位流（我方 smartconnect + AXI4-Lite 从口）PS 侧读正常；② 2B 位流对该应用**首次 CSR 读即挂**；③ 挂死时 JTAG 读 2B CSR 正常且状态为 ERROR_SAFE；④ SLCR 两次一致。
- **未证**：挂死的具体环节（转换器 / PS AXI 属性 / 时钟域）。**未**做 AXI 事务级抓取；**未**读 DFSR/DFAR（无中止记录）。
- **可执行修复方向**：4-D 合并 BD **不用 2B 的 `axi_gp0_lite` 转换器**，改用 **smartconnect（AXI4-Lite 从口，本窗口已证可用）**——这正是 P2a 的做法。

## 边界
未改任何判据；未用 `-force`；`ENABLE=0`；未烧 QSPI；不主张 G3/G4/G5。