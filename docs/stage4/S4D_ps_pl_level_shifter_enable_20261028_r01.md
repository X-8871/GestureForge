# S4D PS-PL 电平转换器使能依据与流程（2026-10-28 r01，离线编写）

- 任务：S4-T34（4-D bring-up）。**本文件不执行板级动作**；窗口 #3 由 DSH 项目总控签发后执行。
- 起因：窗口 #2（`bringup_window2_20261028_r04`）M4-b 卡在 `M4B STEP=1 read CSR_ID addr=0x43C00000`。
  两条独立证据：
  1. 停核后 `mrd 0x43C00000` → `Cannot access FPGA: **Bitstream is not programmed**`；
  2. 重新 `program_hw_devices` 后 → `Cannot access FPGA: **Level shifters are not enabled**`；
     且"先装 PL 再 init"与"先 init 再装 PL"两种顺序均同样报错（`bringup_window2_order_20261028_r01`）。
  ⇒ 阻断点在 **PS-PL 电平转换器未使能**，不在应用、也不只是 PL 未装载。

## 1. 依据（厂商原件原文核对，非记忆）

文件：`D:\FPGA\AX7Z020\AX7Z020\01_hardware\hardware\04_芯片手册\ZYNQ7000\ug585-Zynq-7000-TRM.pdf`
版本：**UG585 (v1.2) August 8, 2012**（Zynq-7000 EPP Technical Reference Manual）。

| 出处 | 原文要点 |
|---|---|
| **§2.4.8 PS–PL Voltage Level Shifter Enables**（文档页 46） | "The level shifter enables are split into input and output signal groups. If the PL is not powered, the level shifters must be set to **0x0**. If the PL is being configured, the level shifters should be set to **0xA** to disable the input signals and prevent glitches from propagating into the PS. Once the PL is fully configured, the level shifter enables should be set to **0xF**." |
| **§2.5 PL AXI Interfaces 注**（文档页 46） | "**Note:** The PL level shifters must be enabled via LVL_SHFTR_EN before PL logic communication can occur." |
| **§5 Interconnect**（文档页 106/112/113） | "PL level shifters must be enabled via LVL_SHFTR_EN before PL logic communication can occur."（AXI_HP/AXI_GP 通路同样受此约束） |
| **§6 Boot and Configuration — PL Reconfiguration flow using PCAP**（文档页 150） | 步骤 2："**Disable the PL level shifters by writing 0xA to the SLCR LVL_SHFTR_EN register**"；步骤 10："**Enable the PL level shifters by writing 0xF to the SLCR LVL_SHFTR_EN register**" |
| **Appendix B.28 System Level Control Registers (slcr)**（文档页 1405 起，基址 `0xF8000000`） | **SLCR_UNLOCK**：abs `0xF8000008`，`wo`，`UNLOCK_KEY[15:0]`，写入 **`0xDF0D`** 解除写保护（文档页 1411）；**SLCR_LOCK**：abs `0xF8000004`，`wo`，`LOCK_KEY[15:0]`，写入 **`0x767B`** 重新加锁（文档页 1411）；**LVL_SHFTR_EN**：abs **`0xF8000900`**，`rw`，reset `0x00000000`，位定义 bit3 `USER_LVL_INP_EN_0`、bit2 `USER_LVL_OUT_EN_0`、bit1 `USER_LVL_INP_EN_1`、bit0 `USER_LVL_OUT_EN_1`，**bit4 reserved "Do not modify"**，31:5 reserved（文档页 1522） |

结论：写 **`0xF`** 到 `0xF8000900` 即同时使能 bit3..bit0（两组 INP/OUT），且不触碰保留位 bit4。

## 2. 正确序列（v3.2 驱动实现）

```
# 1) 系统复位（注意：此步会清空 PL）
rst -system -stop
# 2) 配置期间：关输入、防毛刺（UG585 §2.4.8 / §6 步骤 2）
mwr 0xF8000008 0xDF0D          ;# SLCR unlock（UNLOCK_KEY=0xDF0D）
mwr 0xF8000900 0x0000000A      ;# LVL_SHFTR_EN = 0xA
mwr 0xF8000004 0x767B          ;# SLCR lock（LOCK_KEY=0x767B）
# 3) 装 PL（program_hw_devices / driver program_pl）
# 4) 配置完成：使能全部（UG585 §2.4.8 / §6 步骤 10）
mwr 0xF8000008 0xDF0D
mwr 0xF8000900 0x0000000F
mwr 0xF8000004 0x767B
mrd -value 0xF8000900          ;# **读回必须 = 0x0F**，否则 FAIL、不得继续
# 5) dow init.elf + con（ps7_init）→ 停核
# 6) dow <app>.elf → **再写一次 0xF 并读回断言** → con
```

### 对窗口 #3 指令的两处修正（依原文核对）

1. **"重新 lock 写 `mwr 0xF8000008 0x0`" 不成立**：`0xF8000008` 是 **SLCR_UNLOCK**（wo，只认 `0xDF0D`）；
   要重新加锁必须写 **`0x767B` 到 `0xF8000004`（SLCR_LOCK）**。写 0 到解锁寄存器不会加锁，寄存器仍处于解锁态
   （功能上仍能写，但失去写保护，且与 TRM 不符）。
2. **只写 `0xF` 缺少过渡态**：UG585 §2.4.8 与 §6 明确"配置期间 0xA、配置完成 0xF"。v3.2 按 0xA→0xF 两步实现；
   若坚持单步 0xF 也能使能，但会在配置窗口期让输入脚处于使能态，存在毛刺风险。

## 3. 断言与证据

- 读回断言：`mrd -value 0xF8000900` **必须等于写入值**；不符即 FAIL，**不得把不可访问当成可用**。
- 驱动内联断言：每次 ELF 装载（`dow` 之后、`con` 之前）重写 0xF 并读回；不符时 TCL `error` 终止该步。
- 每步真实退出码与 `<tag>.log` 落盘；读回原始串与解析值同时记录（`readback_raw` / `readback`）。

## 4. 与驱动 v3.2 的对应

| 项 | 位置 |
|---|---|
| 常量 `SLCR_UNLOCK_ADDR/SLCR_LOCK_ADDR/LVL_SHFTR_EN_ADDR/SLCR_UNLOCK_KEY/SLCR_LOCK_KEY/LVL_SHFTR_CFG/LVL_SHFTR_ON` | `scripts/stage4_s4b/run_bringup_driver.py` |
| `lvl_shifter_tcl()` / `lvl_shifter_inline_assert()` / `enable_ps_pl_level_shifters()` | 同上 |
| `stage_pspl_setup_and_load()`（复位→0xA→装 PL→0xF+读回→装 init/app） | 同上，`main()` 的 `P2_load_app` 段已改为调用它 |
| `load_elf_ddr()` 不再 `rst -system`（`_PL_STATE["programmed"]` 为真时），并内联重断言 0xF | 同上 |
| 自检项 `lvl_shifter_tcl_exact` / `lvl_shifter_lock_key_is_0x767b_not_zero` / `lvl_shifter_inline_assert_readback` / `lvl_shifter_readback_0xF_pass` / `lvl_shifter_readback_0xA_must_fail` / `pspl_stage_wires_lvl_shifter` / `load_elf_ddr_*` | `offline_selftest()` |

## 5. 限制

- 本文件与 v3.2 的改动**均未上板验证**；`0xA`→`0xF` 与读回断言的实际效果待窗口 #3 实测。
- 若窗口 #3 使能后 `mrd 0x43C00000` 仍失败或应用仍卡 `STEP=1`：**立即停、保留现场与 UART、报总控**，
  不得连续试错（可能是 PL 设计/时钟/复位或地址映射的另一层问题）。
- 说明：FSBL 正常启动流程由 `ps7_post_config` 承担这两步写入（UG585 §6 的 PL 配置流程）；纯 `ps7_init + dow + con`
  不含，因此 JTAG 直连场景必须显式补写。