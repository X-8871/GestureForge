# S6 E2 安全流程窗 r09 事件：应用卡在 S5Vdma_Init，核不可 halt（冷启动 PS-PL AXI stall）

- RunId：`s6e_e2_frame_period_20261030_r09`；时间 2026-10-30 22:44:06–22:45:01
- 前置：12V 上电后 E1 r04 PASS（APU/A9#0/A9#1/xc7z020，DAP 干净）
- 本次安全流程（零 rst）各步：
  - S2 loadhw + stop：PASS（stop 报 Already stopped 已修正）
  - S3 ps7_init(init.elf 2.5 s)：PASS
  - S4 0xA → fpga -file P3q → 0xF：PASS
  - **S5 PL 只读探测：PASS**（`2B CSR = 0x53324250` 正确、`VDMA CR = 0x10002`）
  - S6 load_elf_ddr(显示长跑 cbf5ebe3…)：PASS（RUN_STATE Running）
- 现象：UART 仅 banner + `TEST PATTERN DRAWN: bars8+border+cross`，此后无 `VDMA: init OK`；60 s 内无帧行
- 停核：**`Cannot halt processor core, timeout`**（PC 仍可读 = **0x001054B4**）
- **PC 归属**：`s5_display_app_longrun.map` → `S5Vdma_Init`（0x001054A0 起，0xe0 字节）内部
  ⇒ 应用在 VDMA 寄存器访问/初始化序列中停住（PS 侧访问 PL AXI-Lite 不完成 ⇒ 总线 stall ⇒ halt 超时）
- 无 APB/DAP 错误码；按 lead 规则**未重试、未 rst -processor、未 rst -system**；hw_server 已杀、端口空、零残留

## 判断
- PL 本身已配置（2B CSR ID 可读正确），但 **VDMA AXI-Lite 的访问在应用运行期不完成**；冷启动（12V 上电）后首次出现，热机（r03 及之前）正常。
- 高度怀疑：当前流程在 PL 配置后**再次运行 ps7_init**（load_elf_ddr 内部会重跑 init.elf），导致已配置 PL 的 PS-PL AXI 路径被重新初始化/毛刺，VDMA 从端访问挂起。

## 建议下一版流程（待 lead 批准）
1. ps7_init → 0xA → fpga → 0xF（只做一次 init，**之后不再跑 init.elf**）
2. 手动 `dow app` → 内联 0xF（fpga_rst_ctrl/lvl_shftr 再确认）→ `con`
3. 采集前先只读探测 `0x43C4002C`（VDMA 版本应为 0x62000050），确认后再继续