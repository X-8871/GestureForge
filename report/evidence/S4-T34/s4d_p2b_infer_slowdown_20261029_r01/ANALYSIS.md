# P2b 上 2B 推理核为何比 2B 基线慢 ~2×：离线归因 + 一条 ≤6 min 板上测量方案

- 任务：共享任务板 `task-1`（DSH 项目总控 → perf-analyst 子 agent）
- RunId：`s4d_p2b_infer_slowdown_20261029_r01`
- 时间：2026-10-29（UTC+8）｜性质：**纯离线只读分析**，未碰板卡 / JTAG / COM4 / hw_server，未跑 Vivado 综合实现，未改任何源码，未 git 操作
- 写区：仅本目录（其中 `s4d_p2b.xsa` + `xsa_p2b/*.hwh` 是从 P2b 证据目录**复制**来的只读副本，用于读取 SmartConnect 的真实参数）

---

## 1. 结论先行

**主因（H1，支持）：P2b 把 2B 核的 `M_AXI` 从"直连 HP0"改成了"经 `smc_data` SmartConnect(2S/1M)→ HP0"，而 2B 核是个"单 outstanding、单 beat、ID 恒 0"的**延迟完全无法隐藏**的主端 —— 每一拍 word 访问都要走完整 AR→R 往返，SMC 的整条流水（SI 端 MMU + SI 协议转换 + transaction regulator + 节点 FIFO + switchboard + MI 端 AXI3 转换 + exit pipeline）全部串在这条往返上，而 SMC 对这一路 SI 的 regulator 又被配成 outstanding=1，所以连"用并发掩盖延迟"这条退路都没有。**

- 2B 核的主端形态（RTL，两个位流完全相同）：
  - `m_axi_arlen = 4'd0`、`m_axi_awlen = 4'd0`（突发长度恒为 1 拍）—— `w2b/src/s2b_hp0_word_adapter.sv:181-182`
  - `m_axi_arid/awid/wid = 6'd0`（ID 恒 0）—— 同上 `:176-178`
  - 同一时刻只允许一笔读在飞行，且只有收到 R 之后才对核心回 `mem_ready` —— 同上 `:312-327`、`:172-173`
  - 接口元数据自己声明 `NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 1` —— `w2b/src/s2b_inference_top.sv:53`
- 2B 基线是**真·直连**：`infer/M_AXI` 直接接 `ps7/S_AXI_HP0`，BD 里注入的 IP 只有控制面的 `axi_gp0_lite`，数据面 0 个 bridge/buffer：
  - `w2b/vivado/s2b_inference_platform.tcl:286-287`（"HP0 原生 AXI3 直接连接；任何额外 bridge/buffer 都使当前可见性证明失效"）
  - 同文件 `:340-358` 审计：`infer/M_AXI` = AXI3/64bit/ID6，`ps7/S_AXI_HP0` = AXI3/64bit/ID6，并用 `DIRECT_HP0_AUDIT_FAIL` 强制两端点唯一
  - 同文件 `:360-361` 单元闭包只剩 `/ps7 /axi_gp0_lite /rst_fclk0 /const_zero /const_one /infer`
- P2b 是**经 SMC**：`s4d_0/M_AXI_RD`→`smc_data/S00_AXI`，`infer_0/M_AXI`→`smc_data/S01_AXI`，`smc_data/M00_AXI`→`ps7_0/S_AXI_HP0`：
  - `.../pl_v2_p2b_bitstream_20261029_r01/bd_merged_p2b.tcl:75-81`、地址 `:92-93`
  - SMC 真实参数（从 P2b XSA 的 `s4d_p2b_smc_data_0.hwh` 读出）：`s01_entry_pipeline_s01_mmu`（`C_S_PROTOCOL=1`=AXI3、`C_NUM_READ_OUTSTANDING=1`）、`s01_entry_pipeline_s01_transaction_regulator`（`C_NUM_READ_OUTSTANDING=1`、`C_NUM_READ_THREADS=1`、`C_S_ID_WIDTH=6`→`C_M_ID_WIDTH=2`）、`s01_entry_pipeline_s01_si_converter`、`s01_nodes_s01_{ar,aw,b,r,w}_node`（`C_FIFO_OUTPUT_REG=1`、`C_M_SEND_PIPELINE=1`）、`switchboards_*_switchboard`（`C_M_PIPELINES=1`、`NUM_SI=2`）、`m00_nodes_m00_*_node`（`C_S_LATENCY=1`、`C_FIFO_OUTPUT_REG=1`、`C_NUM_OUTSTANDING=1`）、`m00_exit_pipeline_m00_exit`（`M_PROTOCOL=AXI3`、`C_NUM_READ_OUTSTANDING=1`、`C_M_ID_WIDTH=0`）。即 **AR 方向 ≥5 级、R 方向 ≥4 级寄存/流水 + 两端协议转换**，全部落在"每拍一次往返"的关键路径上。

**放大器（H5，支持）：adapter 对"非整字读"会退化成逐字节单拍事务**（`rmask != 4'b1111` 时 `arsize=3'd0`，一个 lane 一笔 AR，最多 3~4 笔/字）—— `s2b_hp0_word_adapter.sv:214`、`:322-325`、`:233-241`。这条 RTL 在两个位流里一样，但它把"每笔 AXI 事务的固定延迟"对总运行时间的敏感度放大了数倍，是本次"延迟一涨、时间就翻倍"的结构性土壤。

**结论一句话**：P2b 不是"算得更多"，而是"等得更多"——同一份 RTL、同一时钟、无任何 AXI 错误，多出来的 ≥1.93e9 个核周期全部是内存等待，且等待只可能来自那条新增的 SmartConnect 跳。

---

## 2. 定量周期账（这是本次最硬的定量证据）

| 量 | 2B 基线位流 | P2b 位流 | 出处 |
|---|---|---|---|
| 单帧完成/终止 | `done=1`，`status=0x00000E04`（DONE_SAFE），`error=0` | 未完成，`error=5`（TIMEOUT），`status=0x00000C05`（ERROR_SAFE） | 见 §4 证据 |
| 实测墙钟 | **47,287 ms**（40 轮恒定，1 ms 分辨率下逐轮完全相同） | **85,899 ms 仍未完成** | `bringup_longrun_probe_20261029_r05/W2_uart_stamped.log:12`；`s4d_chainlite_a_p2b_20261029_r03/chain_uart_output.txt:27` |
| 折算核周期（FCLK0=50 MHz） | 2,364,350,000 ≈ **2.364e9** | **> 4,294,967,295**（=0xFFFFFFFF） | 2B：47.287 s×50 MHz；P2b：见下 |
| 比值 | 1.000 | **≥ 1.817**（下界，因超时） | 4.295e9 / 2.364e9 |

**P2b 的 85,899 ms 不是"跑满 86 秒"，而是"内核 32-bit 周期超时恰好烧完"——这同时给了我们一个免费且自校准的时钟/超时验证：**

- `core_timeout` 是**核周期计数器**判据：`(elapsed_cycles + 32'd1) >= timeout_cycles ⇒ error_code = TIMEOUT_ERROR`（`w2b/src/s2a_control_csr.sv:244-248`），`elapsed_cycles` 在 START 被接受时清 0、busy 期间每核时钟 +1（同文件 `:186`、`:253`），`TIMEOUT_ERROR = 3'd5`（同文件 `:59`）。
- 应用把 `S4D_NET_TIMEOUT_CYCLES = 0xFFFFFFFFu` 写进 `0x028`（`vitis/stage4/ps/s4d_ps_app.c:330`、`:673-674`）。
- 因此终态出现的时刻 = 0xFFFFFFFF 个**核时钟**。实测 85,899 ms ⇒ 4,294,967,295 / 0.085899 s = **49.9997 MHz**。
- 反解的意义：① **P2b 里 `infer_0/clk` 确实就是 50.000 MHz**（H4 被实测否证）；② 超时值 0xFFFFFFFF 在这条链上传导正确、未被截断（否则不会正好落在 85.899 s）；③ 这也意味着 **50 MHz + 32-bit 周期超时 ⇒ 单帧可测上限硬顶 85.899 s**，任何"比基线慢 1.82× 以上"的帧永远测不到真值，只能得到下界。这本身就是"为什么这次只拿到 >85.9 s 而不是具体时间"的原因。

**为什么"多出来的周期一定是等待、不是计算"：**

1. 两次构建读的是**同一份 2B 核源码**：18 个 `w2b/src/*.sv` 的最大 mtime 是 `2026-10-16 12:13:58`（`s2b_control_csr.sv`），早于 2B 基线位流构建时间 `2026-10-16 23:15:44`（见 `visibility1_csr_fixed_20261016_r04/artifacts/clocks.rpt` 头），也早于 P2b 构建 `2026-10-29 12:21`。两次构建的 `-sv` 文件清单也完全相同（`s2b_inference_platform.tcl:6-25` 与 `bd_merged_p2b.tcl:24-32` 逐一对应）。（口径：按 mtime 判定，未做逐文件 hash；如需绝对严谨可由 lead 补 `git cat-file blob` 比对。）
2. **时钟相同**：P2b `infer_0/clk ← FCLK_CLK0`，`CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {50}`（`bd_merged_p2b.tcl:41`、`:63`）；2B 基线同一网（`s2b_inference_platform.tcl:288-290`）且被审计断言为 `FREQ_HZ 50000000`（同文件 `:362`、`:365-367`）。再加上 §2 的超时反解，可以认为 50.000 MHz 是**实测**而非只靠配置。
3. **时序都收敛**：P2b `WNS +0.212 / WHS +0.036 ns`，`All user specified timing constraints are met`，单时钟 `clk_fpga_0` 20.000 ns（`reports/timing_route.rpt:144,154,164`）；2B 基线 `setup_slack 0.156 / hold_slack 0.078`（`artifacts/timing_metrics.tcldict`），`clocks.rpt` 同样是 20 ns。→ 不存在"一边在 50 MHz 跑、另一边因时序违例实际跑不起来/行为异常"的可能。
4. **P2b 没有任何 AXI 层面错误**：`error=5` 是唯一的 TIMEOUT 码，不是协议码（协议故障会是 adapter 的 `fault_event_code=11` 并置 `protocol_isolated`，见 `s2b_hp0_word_adapter.sv:109-115`、`:278-286`）；终态 `status=0x00000C05` 里 `bit[10]=1`（=safe 且 **未**isolated，`w2b/src/s2b_control_csr.sv:359-363` 的 bit 定义），`bit[12]=0`（ledger 已空），`error_code=5`。⇒ AXI 事务的握手、ID 回传（adapter 要求 `rid==6'd0`）、响应码全部正常，**唯一症状是"慢"**。
5. 反过来，**PS 侧与 HP0/DDR 的运行时配置在两个位流下是同一份**：PS7 的时钟/DDR/HP 端口寄存器由软件 `ps7_init` 写，而 `init.elf` 是驱动里的**固定常量**（`D:\codex-worktrees\w4\scripts\stage4_s4b\run_bringup_driver.py:118`，registry 内 `verified_payload/init.elf`），两个位流的窗口都走同一条 `load_elf_ddr()` 流程。⇒ 位流之间的**唯一运行时差异 = PL 织物内容（多了 preproc + 两个 SMC）与 infer→HP0 的连接拓扑**。

⇒ 由 1+2+3+4+5：两边的"计算/发请求节奏"完全一致，**多出的 ≥1.93e9 周期只能是 `mem_ready` 迟迟不来**，即每拍访问的平均等待变长（或部分访问被拉得极长）。

6. **不是死锁，是"慢"**：P2b 那次运行在 START 之后每 5 s 采一次 `STATUS`，17 次采样全部是 `state=RUN`，其中 13 次 `bit[12]=1`（adapter ledger 非空 ⇒ 采样瞬间确实有一笔 AXI 事务在飞），4 次 `bit[12]=0`（采样瞬间账本空）。⇒ 事务在持续进出，不是"卡在一笔不回来的事务上"；结合终态 `error=5`（TIMEOUT）而非协议码/隔离，可以判定为**吞吐/延迟问题**而非挂死。（对应 `chain_uart_output.txt:10-27`；bit 定义见 `w2b/src/s2b_control_csr.sv:359-363`。）

**一阶模型（给出量级，不作为结论依据）**：adapter 把一拍访问串行化为 `(AR→R 往返 L) + ~4 拍自身握手`，故 `帧周期 ≈ N·(L+4)`。N 与"自身握手 4 拍"两边相同，所以

```
ratio = (L_p2b + 4) / (L_2b + 4) ≥ 1.817
L_p2b ≥ 1.817·L_2b + 3.27
若 L_2b ≈ 20 拍 ⇒ 增量 ≈ +20 拍
若 L_2b ≈ 30 拍 ⇒ 增量 ≈ +28 拍
若 L_2b ≈ 40 拍 ⇒ 增量 ≈ +36 拍
```

即"每笔访问多等 ~20–36 个 50 MHz 周期"。这与 HWH 里可见的 SMC 流水深度（AR ≥5 级、R ≥4 级 + 两端 AXI3↔AXI4 协议转换）同一量级；但**N（每帧 AXI 事务数）本设计没有任何计数器可读**，所以上式只能给量级，不能给唯一解 —— 这也是 §6 测量方案只做"分类 + 定性闭环"，而不去追"精确 L"的原因。

---

## 3. 假设判定表

| # | 假设 | 判定 | 一句话依据（详见 §4） |
|---|---|---|---|
| **H1** | 2B 的 AXI 主在 P2b 经 SmartConnect 后每拍延迟变大（2B 基线是直连） | **支持（主因）** | 2B 基线数据面直连 HP0 且有 `DIRECT_HP0_AUDIT`；P2b 经 `smc_data` 2S/1M；2B 主端单 outstanding/单 beat ⇒ 延迟 100% 暴露；SMC 对该 SI 的 regulator 也是 outstanding=1 |
| **H2** | HP0 位宽/时钟域配置不同（64 vs 32 / ACLK 非 50 MHz / 有 CDC） | **反驳** | HP0 两边都是 64-bit AXI3、ID6；SMC 内部全 64-bit（`C_AXI_RDATA_WIDTH=64`,`C_RDATA_WIDTH=64`,`…_exit M_PROTOCOL=AXI3`），无位宽转换；单时钟 50 MHz、无 CDC（P2b 时序报告只有 `clk_fpga_0`；2B 基线 `clocks.rpt` 只有 `clk_fpga_0`）；PL 侧 `infer_0/clk` 两边同源 FCLK0 |
| **H3** | preproc 的 `M_AXI_RD` 与 infer 共用 `smc_data` 产生仲裁/未完成事务残留 | **反驳（板上 1 次读即可闭环）** | ① preproc 读 shim 只在 `rd_req` 时发 AR，空闲时 `arvalid=0` 且只允许 1 笔突发（`s4d_axi4_rd_shim.sv:110-124`、`:25`）；② 出问题的那次 P2b 运行用的是 `PREPROC=INJECTED_TENSOR`，preproc 根本没被 START（`s4d_ps_app.c:649`）；③ P2b 终态 ledger 已空、无 isolated、无 fault_detail ⇒ 不存在"未完成事务残留"；④ 板上用 `0x43C10008/0x18` 可一次性证明 preproc 全程 0 次启动（见 §6） |
| **H4** | P2b 里 2B 核的 `clk` 实际不是 50 MHz | **反驳（实测级）** | BD 明确 `infer_0/clk ← FCLK_CLK0` 且 FCLK0=50 MHz（`bd_merged_p2b.tcl:41,63`）；**超时反解得 49.9997 MHz**（0xFFFFFFFF 周期 / 85,899 ms）；SLCR `0xF8000170` 探针值 `0x00600600` 在 2B 与 P2b 两个窗口逐次完全相同（`probe_window_2b_20261029_r01/uart.log:6` vs `probe_window_p2b_20261029_r01/uart.log:6`） |
| **H5** | 其他：地址映射/Prot/QoS/仲裁/beat 上限 | **部分支持（放大器）** | 地址与属性两边一致（都 0x0/1 GB→HP0；adapter 恒 `arcache=awcache=0, arprot=awprot=0, arqos=awqos=0`，`:189-194`）；**真正的 H5 项是"逐字节退化"**：非整字读每 lane 一笔单拍 AR（`:214`,`:322-325`）⇒ 放大器；另有一条工程性限制：**32-bit 周期超时把单帧可测上限钉在 85.899 s**，导致慢帧只能测到下界 |

---

## 4. 逐条证据与出处

### H1（支持）——直连 vs 经 SMC

| 事实 | 出处 |
|---|---|
| 2B 基线：`infer/M_AXI` 直连 `ps7/S_AXI_HP0`，注释明确"任何额外 bridge/buffer 都使可见性证明失效" | `w2b/vivado/s2b_inference_platform.tcl:286-287` |
| 2B 基线：`DIRECT_HP0_AUDIT_FAIL` 强制 HP0 网上只有 `infer/M_AXI` 和 `ps7/S_AXI_HP0` 两个端点；两边 `PROTOCOL AXI3 / DATA_WIDTH 64 / ID_WIDTH 6` | 同文件 `:340-358` |
| 2B 基线：BD 单元闭包 = ps7 + 1 个控制面 `axi_protocol_converter` + reset/const + infer（数据面零 IP） | 同文件 `:360-361` |
| P2b：`smc_data` 2S/1M，S00=preproc `M_AXI_RD`，S01=`infer_0/M_AXI`，M00=`ps7/S_AXI_HP0` | `bd_merged_p2b.tcl:75-81` |
| P2b：两个 SI 都映射到 HP0 同一 1 GB DDR 段 | 同文件 `:92-93` |
| P2b SMC 内部：SI1 入口 MMU（AXI3）+ si_converter + **transaction regulator（读/写 outstanding=1, threads=1）** + ar/aw/r/w/b 节点（输出寄存 + 发送流水=1）+ 2×1 switchboard（M 侧流水=1）+ MI AR/AW 节点（`C_S_LATENCY=1`）+ MI exit pipeline（**AXI3**，读 outstanding=1，MI ID 宽=0） | P2b XSA `s4d_p2b_smc_data_0.hwh`（本目录 `xsa_p2b/s4d_p2b_smc_data_0.hwh`），模块 `s01_entry_pipeline_s01_{mmu,si_converter,transaction_regulator}`、`s01_nodes_s01_*`、`switchboards_*`、`m00_nodes_m00_*`、`m00_exit_pipeline_m00_exit`、`s01_axi2sc`、`m00_sc2axi` |
| 2B 主端形态（单 outstanding、单 beat、ID=0、收到 R 才回 ready） | `w2b/src/s2b_hp0_word_adapter.sv:109-110,172-173,176-182,312-327`；接口元数据 `w2b/src/s2b_inference_top.sv:53` |

推理要点：**单 outstanding + 单 beat + "收到响应才回 ready"= 该主端的吞吐被钉死为 `1 word / 往返延迟`。** 任何串在往返上的额外级数/转换都按 1:1 变成整帧时间。SMC 连"并发掩盖"都不给（regulator outstanding=1），因为它的 SI 参数是从主端声明的 `NUM_READ_OUTSTANDING 1` 推出来的。

### H2（反驳）

- HP0：2B 基线审计 AXI3/64/ID6（`s2b_inference_platform.tcl:346`）；P2b `CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {64}`（`bd_merged_p2b.tcl:44`）+ SMC MI `C_RDATA_WIDTH=64/C_WDATA_WIDTH=64/M_PROTOCOL=AXI3`（hwh）。
- SMC SI1：`s01_axi2sc` `C_AXI_RDATA_WIDTH=64 / C_SC_RDATA_WIDTH=64`、`s01_*` 全 64-bit ⇒ **没有 32↔64 位宽转换**（若存在，会额外增加 beat 拆分/合流）。
- 时钟域：P2b 时序报告只有单时钟 `clk_fpga_0`（20 ns）；2B 基线 `clocks.rpt` 也只有单时钟、无 generated clock、无 CDC 约束需求。两边 `infer_0/clk`/`infer/clk` 都接 FCLK0。
- 运行时 PS7（含 HP0 端口、DDR 控制器）由同一份 `ps7_init` 编程 ⇒ 两个位流下 HP0/DDR 的运行时配置本就相同。

### H3（反驳）

- `s4d_axi4_rd_shim.sv:110-124`：`S_IDLE` 下只有 `rd_req` 有效才置 `m_axi_arvalid`；`:25` 注释"不做 outstanding 排队（同一时刻只有 1 笔未完成突发）"；`:163` `m_axi_rready = rd_ready && (st == S_R)`。⇒ 未被 START 时该主端**不产生任何 AR**，谈不上仲裁。
- 出问题的 P2b 运行用 `PREPROC=INJECTED_TENSOR`（`s4d_ps_app.c:649`、`:663-666` 只做 PS 侧 memcpy + flush），preproc 的 CSR 从未被写 ⇒ preproc 引擎未启动。
- P2b 终态：`ledger` 已空（`status bit[12]=0`），无 isolated（`bit[10]=1`），`error=5` 而非协议码 11 ⇒ 无"未完成事务残留"。
- 但要注意：**"共用 smc_data"仍是设计上的耦合**——一旦 4-D 链真的开始用 PL preproc（`PREPROC_SRC=1`），preproc 的 240-beat 突发会和 infer 的单拍抢同一个 MI（`m00_nodes_m00_*` 的 `C_NUM_OUTSTANDING=1`），那时 H3 会从"反驳"变成"真实风险"。建议 4-D 合并时把 preproc 放 HP1（见 §7）。

### H4（反驳，实测级）

- BD：`connect_bd_net ps7_0/FCLK_CLK0 infer_0/clk`（`bd_merged_p2b.tcl:63`）+ `PCW_FPGA0_PERIPHERAL_FREQMHZ {50}`（`:41`）。
- 实测：0xFFFFFFFF 核周期 / 85,899 ms = 49.9997 MHz（§2）。
- 旁证：SLCR `0xF8000170` 读值 `0x00600600` 在两个位流的窗口里完全相同（2B：`D:\tmp\lead\probe_window_2b_20261029_r01\uart.log:6`；P2b：`D:\tmp\lead\probe_window_p2b_20261029_r01\uart.log:6`），且 40 轮逐轮恒定。
- 结论：**P2b 时钟与 2B 基线同频 50 MHz，H4 出局。**

### H5（部分支持：放大器 + 测量天花板）

- **放大器（真正的 H5 项）**：`s2b_hp0_word_adapter.sv:214` 一次只装一个 byte lane，`:322-325` `arsize = (rmask==4'b1111) ? 2 : 0`、`araddr` 低两位按 lane 替换；`:233-241` 每个 lane 收到 R 后按 `remaining` 继续 —— 即"整字读 = 1 笔 8 B 单拍；非整字读 = 1~3 笔 1 B 单拍"。INT8 特征图的按字节读会把事务数放大到最多 3~4 倍，而每笔事务在 P2b 都要多付 SMC 的固定延迟。
- 地址映射：两边都把 `0x00000000/0x40000000` 映射到 `HP0_DDR_LOWOCM`（2B `:305-306`；P2b `:92-93`）；物理地址由 guard 从逻辑地址 +0x1_0000_0000 的 33-bit 溢出判定后取低 32 位（`w2b/src/s2b_request_guard.sv:46,68-73`），两边一致 ⇒ 不是"地址变了导致换 bank/DDR 页"。
- AXI 属性：adapter 恒 `arcache=awcache=4'd0`、`arprot=awprot=3'd0`、`arqos=awqos=4'd0`（`:189-194`）⇒ 位流之间不会因 QoS/Cache 属性改变访问路径。
- **测量天花板**：`core_timeout` 是 32-bit 核周期（`s2a_control_csr.sv:37,208,244-248`），50 MHz 下最大可表示 85.899 s。⇒ 比基线慢 ≥1.82× 的帧**在现有 RTL 下无法测出真值**。这是本次结论只能写"≥1.817×"的根因，也是 §7 建议之一。

---

## 5. 证据口径校正（必须回传 lead，影响排期）

任务卡把两个数字都记成"同一重建 M4-b ELF"，但**现有证据不是这样**：

| 数字 | 真实出处 | 应用 | 位流 |
|---|---|---|---|
| 47,287 ms（40 轮恒定） | `report/evidence/S4-T34/bringup_longrun_probe_20261029_r05/W2_uart_stamped.log:12`（末行 `1843.133 LONGRUN DONE` ⇒ 40 轮 × 47.287 s）；该窗口位流经 `IDENT.json:5-6` 固定为 `…/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit`，sha256 `555a70c2…` | `MODE=LONGRUN_SELFCHECK`（探针应用，`PREPROC=SW`） | **2B 基线** `s2b_inference.bit` |
| 85,899 ms 超时 | `report/evidence/S4-T34/s4d_chainlite_a_p2b_20261029_r03/chain_uart_output.txt:27`（`status=0x00000C05 error=0x00000005`；此前 17 条 5 s 间隔 progress，13 条 `0x00001102`=RUN+OWNER+**ledger 未空**，4 条 `0x00000102`=RUN+OWNER+采样瞬间 ledger 空） | `MODE=CHAIN_SELFCHECK`（chain-lite-A，`PREPROC=INJECTED_TENSOR`） | **P2b** `s4d_p2b.bit` |
| `error=5`（两个位流完全同一条 UART） | `s4d_p2b_4d_reverify_20261029_r03/m4b_uart_output.txt:21,23,29` **与** `s4d_m4b_baseline_2b_20261029_r01/m4b_uart_output.txt` 逐行相同 | `MODE=M4B_SELFCHECK` | 2B 基线 **和** P2b —— **M4-b 应用现在两个位流上都快速 error=5，位流无关** |

要点：
1. **47,287 与 85,899 来自两个不同应用**（LONGRUN vs CHAIN-A）。两者跑的是同一个冻结几何（`letterbox_640x480_to_416x416`）、同一 2B 核、同一 in/weight 字节数，**大概率同工作量但未被证明同工作量**。——这是本次分析最重要的口径缺口。
2. **"同一 M4-b ELF 在两块位流上的 A/B"目前并不存在**：M4-b 在 2B 基线位流上同样 `error=5`（21:41–21:50 三次），与 `s4d_m4b_error5_analysis_20261029_r01/ANALYSIS.md` 记录的"超时值与实测不自洽"一致，属**位流无关**的独立问题（TIMEOUT 计数器/转发），不能拿来当 A/B。
3. 因此本文的"≥1.817×"是**跨应用但仍然同构**的下界；§6 的第一件事就是把 2B 基线侧补上 **CHAIN-A**，让 A/B 变成"同 ELF、同应用、同输入、只差位流"。

---

## 6. ≤6 min 板上测量方案（交 lead 排期；一个窗口，两块位流，串行）

**目的**：把 §5 的口径缺口补上（H1 升级为"已证"），同时用 1 次读把 H3 彻底关掉，并确认"纯等待、无错误"。

**前置（离线，不占板卡；约 10 行改动，属 w4 应用侧，不涉 w2b）**：以现有 CHAIN-A ELF（`D:\tmp\lead\rebuild_timeout_20261029_r01\build\s4d_ps_app_sw0_chainA.elf`，sha 见同目录 `.sha256`）为基础做 `CHAIN-A′`：
1. 终态后再打印 4 个 infer 诊断 CSR：`0x064 last_reject`、`0x068 axi_progress`、`0x074 fault_detail`、`0x010 error`（地址见 `w2b/src/s2b_control_csr.sv:364-394`）；
2. 打印 2 个 preproc CSR：`0x43C10008`（bit0 busy / bit1 done_sticky / bit2 error_sticky / bit3 rd_to_seen / bit4 wr_to_seen）与 `0x43C10018`（done_cnt），另加 `0x43C10020`（rd_to_cnt）（地址见 `pl_v2_rtl_archive_20261029_r01/rtl/s4d_preproc_csr.sv:102-110`；base=0x43C10000，见 `bd_merged_p2b.tcl:90`）；
3. `core_timeout` 改为编译期可选：默认 0xFFFFFFFF，另给 `0x20000000`（=10.737 s@50 MHz）一档，**只缩短"等超时"的墙钟，不改变工作量**。

**两段运行（同一 `CHAIN-A′` ELF、同一 `init.elf`、同一装载流程；位流串行）**

| 段 | 位流 | `core_timeout` | 预期 | 花费（按 21:36–21:40 那次同流程窗口实测的固定开销 ≈136 s + 运行时间） |
|---|---|---|---|---|
| A | 2B 基线 `…/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit`（sha256 `555a70c2…`） | 0xFFFFFFFF | `done=1`、`status=0x00000E04`、`error=0`、`elapsed_ms ≈ 47,000–48,000` | ~3.0 min（136 s 开销 + ~47 s 运行） |
| B | P2b `…/pl_v2_p2b_bitstream_20261029_r01/s4d_p2b.bit`（sha256 `47472d2d…`） | **0x20000000** | `done=2`、`status=0x00000C05`、`error=0x00000005`、`elapsed_ms ≈ 10,737` | ~2.5 min（136 s 开销 + ~11 s 运行） |
| | | | **合计 ≈ 5.5 min，预算上限 6 min**（若复用上一窗口已通过的 IDENT/enum 结果，可再省 ~40 s） | **≤6 min** |

> 若 lead 想把"85.899 s 真超时"也复现一次，把 B 段的 timeout 改回 0xFFFFFFFF 即可（+1.3 min，总计 ~6.3 min，超出 6 min 预算，建议另排一个独立窗口）。

**必须记录的量（每段）**：`elapsed_ms`、`status`、`error`、`last_reject(0x064)`、`axi_progress(0x068)`、`fault_detail(0x074)`、`epoch(0x050/0x054)`、`active_frame(0x058)`、preproc `0x43C10008/0x18/0x20`。

**成功判据（逐条，事先写死，不放宽）**

1. **A 段**：`done=1` 且 `status=0x00000E04` 且 `47,000 ≤ elapsed_ms ≤ 48,000`。⇒ 2B 基线在**同应用**下复现 47.287 s，A/B 口径成立。
2. **B 段**：`error=0x00000005`（TIMEOUT）且 `status=0x00000C05`（若落在 `RECOVERING`/`0x00000C03` 等过渡态，则如实记录原文并说明"恢复未在采样窗内完成"，不算通过）且 **`fault_detail(0x074)==0`** 且 **`last_reject(0x064)==0`**。⇒ 没有协议错/准入错/隔离，纯"等得久"。
3. **B 段**：preproc `0x08` 的 busy/done_sticky/error_sticky/rd_to_seen/wr_to_seen **全 0**，`0x18 done_cnt==0`，`0x20 rd_to_cnt==0`。⇒ preproc 全程既未启动也未发过读，**H3 关闭**（H1 成为唯一剩下的结构性差异）。
4. 1+2+3 同时成立 ⇒ **H1 由"支持"升为"已证主因"**，可以直接据此改 BD（§7 方向 A），不必再做 ILA。
5. **反例/否决判据**：若 A 段也超时或 `done≠1` ⇒ 47,287 与 85,899 不同源（应用/输入不同），本文结论降级为"证据不足"，**不要**据此改 BD；若 B 段 `fault_detail≠0` 或 `error≠5` ⇒ 先查 AXI 协议/准入，而不是查延迟。

**为什么这样设计能"一锤定音"**：同一 ELF + 同一应用 + 同一输入/几何 + 同一 init，唯一变量是位流 ⇒ 时间差只能归因于 PL 数据面拓扑；再用 preproc 计数器把"另一个 SI 在抢"这条旁路彻底排除；用 `fault_detail/last_reject` 把"错误"这条旁路彻底排除。

---

## 7. 修复方向与写区归属

| 方向 | 内容 | 预期 | 写区 |
|---|---|---|---|
| **A（首选，只动 BD）** | 回到 2B 基线的数据面拓扑：`infer_0/M_AXI` **直连 `ps7_0/S_AXI_HP0`**；`s4d_0/M_AXI_RD` 走 **HP1**（或独立的 1S/1M SMC→HP1），控制面继续用 `smc_ctrl`。HP0 独占给推理核，与 2B 基线位流取证一致（47.287 s） | 期望回到 ~47 s 量级 | **BD 构建脚本**（`bd_merged_p2b.tcl` 同源脚本，lead/阶段5 的构建面）。**不涉 w2b 源码** |
| **B（治本，需 w2b/Codex）** | 改 `s2b_hp0_word_adapter`：整字读改为 2 beat 突发或按行突发；把 outstanding 从 1 提到 ≥2；非整字读不再逐 lane 拆单拍。把"每 word 一次往返"降为"每 burst 一次往返"，对延迟的敏感度下降一个数量级 | 收益远大于 A，且未来加 CDC/桥接也稳 | **w2b 是 Codex 写区**；且会触碰 2B 冻结接口语义与可见性证明 ⇒ 需 Codex + 重新冻结/复审 |
| **C（可观测性，需 w2b/Codex）** | `core_timeout` 从 32-bit 核周期改成 ms 计或 64-bit；adapter 增加 AXI 事务计数器（读 CSR 可读） | 解除 85.899 s 天花板，后续任何"慢帧"都能测真值和事务数 | **w2b 是 Codex 写区** |

如果 4-D 合并必须保留"preproc + infer 共用一个 HP"：请至少把 **preproc 放 HP1**，不要让它和单 outstanding 的推理核共用同一个 MI（SMC 的 MI 侧 `C_NUM_OUTSTANDING=1`，一旦 preproc 开始发 240-beat 突发，infer 的每拍往返会被进一步拉长）。

**本文不主张任何 G3/G4/G5 结论**；所有"预期 47 s"都是回归期望，未上板验证。

---

## 8. 未测项 / 边界 / 如何复核

- **未测**：P2b 的真实单帧时间（受 §2 的 85.899 s 天花板限制，现有 RTL 不可测）；每帧 AXI 事务数 N；每笔访问延迟分布；`smc_data` 内部是否出现"部分访问被拉得极长"（非均匀等待）——现有 RTL 无可读计数器，需方向 C。
- **未做**：任何板卡/JTAG/COM4/hw_server 操作；任何 Vivado 综合/实现；任何源码修改；任何 git 操作。
- **口径限制**：① "同 RTL"按 mtime 判定（18 个文件最大 mtime `2026-10-16 12:13:58` < 2B 位流构建 `2026-10-16 23:15:44` < P2b 构建 `2026-10-29 12:21`），未逐文件 hash；② "≥1.817×"是下界（超时截断）；③ 47,287 与 85,899 目前跨应用（见 §5）。
- **复核命令（只读）**：
  - `Select-String -Path <本目录>\xsa_p2b\s4d_p2b_smc_data_0.hwh -Pattern 's01_entry_pipeline_s01_transaction_regulator'` 核对 SMC 的 outstanding=1；
  - 打开 `bd_merged_p2b.tcl:75-81,92-93` 与 `s2b_inference_platform.tcl:286-287,340-358,360-361` 对照拓扑；
  - 用 `s2b_hp0_word_adapter.sv:176-182,312-327` 复核"单 outstanding 单 beat"；
  - 用 `s2a_control_csr.sv:59,244-248` + `s4d_ps_app.c:330,673-674` 复核 85,899 ms = 0xFFFFFFFF 核周期 @ 50 MHz 的自洽性。

---

## 附：证据文件索引（相对各自工作树）

| 用途 | 路径 |
|---|---|
| P2b BD / 拓扑 / 地址 | `report/evidence/S4-T34/pl_v2_p2b_bitstream_20261029_r01/bd_merged_p2b.tcl:41,44,63,66-72,75-81,90-93` |
| P2b 时序 / 资源 | `report/evidence/S4-T34/pl_v2_p2b_bitstream_20261029_r01/reports/timing_route.rpt:144,154,164`、`reports/util_route.rpt`（LUT 20,976 / FF 8,682 / DSP 147） |
| P2b SMC 真实参数 | 本目录 `xsa_p2b/s4d_p2b_smc_data_0.hwh`（源：`pl_v2_p2b_bitstream_20261029_r01/s4d_p2b.xsa`，sha256 `ddb65f19…`） |
| 2B 基线 BD / 审计 / 地址 | `w2b/vivado/s2b_inference_platform.tcl:6-25,286-290,305-306,340-362` |
| 2B 基线时序 / 资源 | `w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/{clocks.rpt,timing_metrics.tcldict,utilization.rpt}`（LUT 17,250 / FF 4,246 / DSP 145 / BRAM 32） |
| 2B 核 adapter / 顶层 / guard | `w2b/src/s2b_hp0_word_adapter.sv`、`s2b_inference_top.sv:8,53`、`s2b_request_guard.sv:46,68-73` |
| 超时/状态语义 | `w2b/src/s2a_control_csr.sv:37,59,186,208,244-248,253`；`w2b/src/s2b_control_csr.sv:150-172,359-363` |
| 2B 基线 47,287 ms | `report/evidence/S4-T34/bringup_longrun_probe_20261029_r05/W2_uart_stamped.log:12`（共 40 轮） |
| P2b 85,899 ms 超时 | `report/evidence/S4-T34/s4d_chainlite_a_p2b_20261029_r03/chain_uart_output.txt:10-28` |
| M4-b error=5（两个位流同一条 UART） | `s4d_p2b_4d_reverify_20261029_r03/m4b_uart_output.txt:21-29`；`s4d_m4b_baseline_2b_20261029_r01/m4b_uart_output.txt:21-29` |
| error=5 既有离线定位 | `report/evidence/S4-T34/s4d_m4b_error5_analysis_20261029_r01/ANALYSIS.md` |
| SLCR FCLK0 探针（两位流同值） | `D:\tmp\lead\probe_window_2b_20261029_r01\uart.log:6`、`D:\tmp\lead\probe_window_p2b_20261029_r01\uart.log:6` |
| 应用侧超时常量 / CHAIN 流程 | `w4/vitis/stage4/ps/s4d_ps_app.c:330,438-439,649,663-676,681-703` |
| preproc 读 shim / CSR | `report/evidence/S4-T34/pl_v2_rtl_archive_20261029_r01/rtl/s4d_axi4_rd_shim.sv:25,110-124,163`、`.../s4d_preproc_csr.sv:102-110` |