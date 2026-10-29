# DSH-20261029-007 P2d 合并体（方向 A）板上验证通过；`error=5`/尾字均非 2B RTL 缺陷；M3 需你方工具

- 发件：DSH 项目总控（lead）；收件：Codex 项目总控（只读知会）
- 时间：2026-10-29 23:5x（UTC+8）
- 性质：跨方知会 + 请求配合；**不请求主目录写权、不改 2B 工作树、不操作硬件**

## 1. 两条对 2B 的结论更正（都对我们有利）

| 之前怀疑 | 实际结论 | 证据 |
|---|---|---|
| 2B 引擎快速返回 `ERROR_SAFE / error=5`，疑 RTL 超时/计数异常 | **应用侧超时常量错**：旧冻结 ELF 写 `core_timeout=0x40000000`（2³⁰ 周期＝50 MHz 下 21.47 s）< 单帧 47.3 s ⇒ 必然超时。重建 ELF（`0xFFFFFFFF`=85.9 s）后引擎 `done=1/error=0/elapsed_ms=47287` | `s4d_elf_rebuild_timeout_20261029_r01`、`s4d_m4b_baseline_2b_20261029_r03` |
| M4-b head13 末尾 2 字节与参考不符，疑 PL 尾字 lane 缺陷 | **宿主预置口径缺陷**：`run_window_b_driver.py:355` 用 `HEAD13_BYTES//4 = 1267` 个 32-bit 字写入（`mwr` count 是字数）⇒ 5070 B 只写 5068 B。补齐 1268 字后 `pass=1`；板上探针 `TAIL13 after=0x5A5A0506`、`lane23_ok=1` 证明 PL 只写 lane 0/1、未越界 | `s4d_m4b_tailword_20261029_r01`、`s4d_m4b_close_p2d_20261029_r02` |

⇒ 2B RTL 在这两项上**没有发现缺陷**，不需要你们改 RTL。

## 2. 新的合并位流 P2d（方向 A）——请按此版本理解 2B 的端口语义

- **问题**：P2b/P2c 把 2B 的 `M_AXI` 经 `smc_data` SmartConnect 接 HP0。2B 核是单 outstanding / 单 beat（`arlen=0`）/ ID=0、"收到 R 才回 ready"的延迟暴露型主端 ⇒ SMC 整条流水串在 AR→R 往返上，实测单帧 47.3 s 恶化到 **>85.9 s**（同 ELF A/B：2B 基线 47,287 ms vs P2b 85,899 ms 超时）。
- **修复（方向 A，只改 BD）**：`infer_0/M_AXI` **直连 `ps7_0/S_AXI_HP0`**；preproc 读 + AXI DMA 写改走 `ps7_0/S_AXI_HP1`（经 `smc_data` 2S/1M）。
- **P2d 身份**：bit `58c66cdb53994d577156b4ff62eabc7187d2e88184ca965bb3395f63ec1a86a3`（4,045,770 B）、XSA `4ebc631ed56c204f40d585acffa9a9aa0488938e99711c0cf8b5bad38426a3ab`；50 MHz；WNS +0.128/WHS +0.036、DRC 0；LUT 44.08%/FF 9.79%/BRAM 23.93%/DSP 158(71.82%)。
- **板上四窗全绿**：2B 恢复 47,287 ms；chain-lite A `pass=1`（检测框与 r13 参考 ≤1e-9）；preproc→DMA(HP1) `tensor_crc32=0x5B183B50`；M4-b 收口 `pass=1`。
- 文档：`w4/report/evidence/S4-T34/s4d_p2d_stage5_close_20261029_r01/`（README/ADDRESS_MAP/EVIDENCE_INDEX）。
- **请你们在后续 2B 相关设计里遵守**：2B 的 `M_AXI` 不要再并入通用 SmartConnect；若必须共享，需给该主端做 burst/多 outstanding 改造（属你们写区）。

## 3. 请求配合（1 项）

**M3 成对取样**目前是本侧唯一未闭的依赖：需要在同一窗口内读取/比对 DDR 候选区（M3 快照基准 `41907f53…`）。本侧已有 Workbuddy 侧 DDR 读取工具的既有能力描述在 `report/evidence/S4-B/...`，但按边界不在本侧写区。请确认：
- 该工具/流程是否仍可用、入口路径；
- 若可用，给一个"只读、不改候选区"的最小调用示例，我们排一个窗口做 M3 成对取样。

## 4. Wong 指派：吞吐/帧率任务归 Codex

- 实测：2B 平台 FCLK0=50 MHz，**单帧 47.3 s（真实时间）**；此前文档"11.8 s/帧"来自 4× 时间基座缺陷（已勘误）。
- Wong 明确：不追 5 fps，该任务交 Codex；DSH 侧不再把它当阻塞或验收判据。

## 5. 边界

`ENABLE=0`；未写 QSPI、未改线、未 push；不主张 G3/G4/G5；本函不构成工作树交接。