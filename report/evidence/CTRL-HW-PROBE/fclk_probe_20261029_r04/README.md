# FCLK / 电平转换 / CSR 读 探针 r04–r05（2026-10-29 09:45–10:00，DSH）

## 目的
长跑静默停住的候选根因：PL 侧无时钟/无响应。用 JTAG 读 SLCR 判断 FCLK0 状态，并测试使能后 CSR 是否响应。

## 结果（普通命令，无 -force）
### r04：上电态 vs 系统复位+init 后
| 寄存器 | 上电态 A | init 后 B |
|---|---|---|
| 0xF8000900 LVL_SHFTR_EN | 0x00000000 | **0x00000000**（init 不使能移位器） |
| 0xF8000170 FCLK_CTRL0 | 0x00101800 | **0x00600600** |
| 0xF8000180 FCLK_CTRL1 | 0x00101800 | 0x00101800（未变） |
| 0xF8000190 FCLK_CTRL2 | 0x00101800 | 0x00101800（未变） |
| 0xF8000100 ARM_PLL_CTRL | 0x0001A008 | — |
| 0xF8000120 APER_CLK_CTRL | 0x1F000400 | 0x1F000200 |

（`dow init.elf` 仍无可见输出 ⇒ **不能确认 init 是否真正执行**；B 的值变化说明 SLCR 至少被写过。）

### r05：尝试置位 FCLK0 的 bit0 并读 CSR
- 写前 `0xF8000170=0x00600600`；解锁后写 `0x00600601`（仅置 bit0）；上锁后读回**仍为 0x00600600** ⇒ **bit0 写入未生效**（该位语义/写保护未确认，**不据此下结论**）。
- 随后编程 PL（Vivado exit 0 / PROGRAM_DONE）+ 置 `0xF8000900=0x0F`（读回 0xF）→ CSR 读：**`Timeout waiting for the Instruction Complete bit`**（再次）。

## 结论与边界
- **已证**：系统复位会清 PL 配置；LVL_SHFTR_EN 上电/init 后为 0（**init.elf 不使能移位器**）；移位器=0 时 CSR 读必失败。
- **未证**：CSR 超时的原因（PL 无时钟 vs 位流未真正配置 vs 从口复位未释放）——JTAG 侧无法区分；
  `0xF8000170` 的 bit0 写入未生效，说明**不能靠 JTAG 猜字段布局**。
- **决定性方法（下一步）**：在应用内、**首次 CSR 访问之前**用 PS 直接读 SLCR 并打印：
  `0xF8000170`（FCLK0）、`0xF8000900`（移位器）、`0xF8000120`（APER_CLK）、`0xF8000240`（FPGA_RST_CTRL）。
  PS 读 SLCR 不依赖 PL，即使 PL 挂死也能打印 ⇒ 一次判定根因。
- 边界：全程未用 -force；DAP 在 CSR 超时后需整机断电；`ENABLE=0`、未烧 QSPI、未改线。
