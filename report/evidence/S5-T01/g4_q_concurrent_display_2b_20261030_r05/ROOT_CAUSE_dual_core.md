# 双核并发失败的根因记录（供 G4 遗留项引用）

- 事实：M4-b ELF 与显示长跑 ELF **装载地址同为 0x100000**（e_entry=0x100000，代码/数据段重叠）。
  XSDB 对两个核分别 `dow` 时，后一次下载会覆盖先一次写入的镜像区域 ⇒ **两核无法各跑一个不同 ELF**。
- 证据：r03 UART 出现两股“显示 banner”交织；r08 停核后 core0 PC=0x001010b0、UART 无任何 M4B 行；
  r05 con core1 报 `Already running` 等异常都与此一致。
- 结论：并发测量不能用“双核各 dow 一个 ELF”，改用 r09 分时方案：
  单核跑显示长跑建流 → 停显示 CPU（VDMA 是 PL 硬件，持续读帧存 ≈221 MB/s）→ 单核 dow/run M4-b。
  r09 结果：M4-b `elapsed_ms=47420`（基线 47287，**+133 ms / +0.28%**）、VDMA 全程 RS=1/Halted=0、
  计算期间累计欠载 delta=0 ⇒ 显示带宽并发对 2B 影响可忽略。
- r09 证据目录：`g4_q_concurrent_display_2b_20261030_r09/`（含 W3_judgement_rejudged.json、window_close.txt）。
