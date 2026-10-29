# 阶段4 状态（写权：DSH 项目总控（Wong 2026-10-27 指令接管）；离线推理链已冻结，板级项未闭合）

**写权：DSH 项目总控（Wong 2026-10-27 直接指令接管；原 Workbuddy 阶段4总控停写）。覆盖 `docs/stage4/`、`scripts/stage4_s4ctrl/`、`scripts/stage4_s4b/`、`verification/`、`report/evidence/S4-CTRL/`、`report/evidence/S4-B/`、`.codex/STATE.md`；不覆盖 main、dbdf、w2b、w5、w6 与厂商原件。**

- **裁决指针（S4-T30 依据）**：`report/evidence/CTRL-DSH-HANDOFF/decisions/stage4_raw_address_d1_optionA_20261027_r01.md`——Wong 2026-10-27 原话「A」：D1 允许缩减禁区、选选项 A（`raw_frame=[0x12000000,0x12C00000)` 12 MiB + `raw_meta=[0x12C00000,0x12C08000)` 32 KiB、109/109、余量 +1,523,712 B）；D2 不接受降覆盖；D3 META 不强制连续；D4 linker 冻结不作前置 ⇒ E 排除。
- **S4-T30 禁止事项**：`ENABLE=0` 保持；**不 FROZEN**；无板级/位流/烧录；不改 2B 冻结区间（tensor `[0x10000000,0x1007EC00)`、GF8 `[0x10100000,0x106A12FC)`、feature `[0x11000000,0x11ADADB8)`）；不清理/不暂存/不代提交原持有方 **25 项**未提交改动；不 push；不得把「裁决已下」写成「已批准 G0」。
- **接管核验事实**：项目总控 `handoff_check` = **PASS 7 / FAIL 1**，唯一 FAIL 为检查项 **g（证据入口）**；成因是项目总控证据目录在 **main**、检查器按**工作树**解析相对路径 ⇒ **路径基准差异，非状态缺陷**；据此不改写接管结论。

任务=`S4-T30::d1a_address_landing` | 负责人=`DSH 项目总控（Wong 2026-10-27 直接指令接管）` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`83c9284ad2296b9b2c836250cee615e255533615` | 允许修改范围=`docs/stage4/、scripts/stage4_s4ctrl/、report/evidence/S4-CTRL/、.codex/STATE.md` | 未提交改动归属=`原持有方 Workbuddy 的 25 项未提交改动：不清理/不暂存/不回退/不代提交` | 让出声明=`无书面 OFFERED 行（原持有方未出 OFFERED）；本次接管依据为 Wong 2026-10-27 直接指令，属直接指令接管，非 OFFER 交接` | 心跳(UTC+8)=`2026-10-27T20:00:09+08:00` | 证据入口=`report/evidence/S4-CTRL/s4_d1a_landing_20261027_r01/（复审 PASS）；修 4 项非阻断后见 s4_d1a_landing_20261027_r02/` | 恢复命令=`git --no-optional-locks -C D:/codex-worktrees/w4 rev-parse HEAD; python -B scripts/stage4_s4ctrl/verify_d1a_landing.py --run-dir <新RunId>` | 状态/下一接手方=`IN_PROGRESS DSH 项目总控（4 项非阻断已修，待同 Reviewer 增量核对）`

## 2026-10-29 长跑停住定位（A 项）与 DAP 粘连（板级暂停）

- **RunId `bringup_longrun_probe_20261029_r02` = INVALID_RUN（自伤，不作为任何证据）**：预载真实 fixture RAW（0x12000000）+ 权重 GF8（0x10100000）后，板上 **`tensor_crc32=0x5B183B50` 复现**（与离线一致）；但执行器复用 `load_elf_ddr` 时**未置位 `_PL_STATE["programmed"]`**，该函数走了 `rst -system -stop` → **清掉刚编程的 2B PL 配置** → 应用首次 `0x43C00000` 读永不完成（末行打印 `LONGRUN PROBE slcr shftr=0x0000000F fclk0=0x00600600 aper=0x1F000200 fpga_rst=0x00000000`，静默 150 s）→ 停核失败 → **DAP 粘连 `0x30000021/0xF0000021`**。作废与根因见 `report/evidence/S4-T34/bringup_longrun_probe_20261029_r02/ERRATA_INVALID_RUN.md`；对照：14:38 同 ELF 窗口（init 先跑、后编程 PL、不再系统复位）首次 CSR 读成功。
- 该窗口 W0 打开时候选区与 M3 快照差异 **11,850,821 B**（已按快照重写，`restore_diff=0`）；**W4 收尾恢复未完成**（DAP 粘连，dump/恢复均失败）⇒ 下个窗口第一步必须做 W0 式 dump 对比，不得默认候选区干净。
- **板上现状：DAP 粘连，必须整机断电（12V+USB ≥10 s）才可能恢复；未用 `-force`、未尝试任何"清粘连"写操作。断电前不得再上板。** 收窗后进程已清零（hw_server/xsdb/vivado 0，3121 仅 TIME_WAIT）。
- 已备好修正版执行器（**尚未执行**）：`D:\tmp\lead\probe_long_20261029_r03\run_probe_longrun_r03.py`（sha256 `f525ac03…7d7aeb`；编程 PL 后只 `rst -processor -stop`，含 state 可读性门禁、记录区 8 字、CSR `-mem-ranges` 修正、DevCfg 读、DAP 不可用即停）。
- 已备好 P2b 4-D 复验执行器（**尚未执行**）：`D:\tmp\lead\p2b_board_20261029_r01\run_p2b_4d.py`（sha256 `9be5e855…d7fb95`；M3 只读复检 + M4-a + M4-b，装载不复跑 init、编程 PL 后不系统复位）。
- 已归档 preproc v2 构建输入 RTL（原先只在 `D:\tmp\lead\p2a_20261029_r01\src\rtl`，**不在任何 git 树** ⇒ 冻结位流不可复现）：`report/evidence/S4-T34/pl_v2_rtl_archive_20261029_r01/`（9 文件，`manifest.json` 声明 `hash_basis=commit_blob`，与原构建输入逐字节相同）。
- **S4-T35 离线结论（preproc 上板前置，未上板）**：P2a/P2b 的 `s4d_0/M_AXIS` **无消费者**（BD `interface_nets` 无该网）⇒ 引擎 FIFO 满后停在 `S_XQ`，`busy` 常 1、`done` 不来、张量不落 DDR；且引擎源图基址固定 DDR `0x0` ≠ ABI `0x12000000` ⇒ **冻结位流上 `tensor_crc32=0x5B183B50` 不可达**，C 项需新位流（AXIS→DMA/HP0 写通路 + 源图基址方案），属重型任务、待 Wong 裁决。另：旧基线 `PREPROC_SRC=1` 写的是 `0x43C00000+0x200..0x27C`（在 P2a/P2b 里是 2B infer 空间）⇒ 不会启动预处理且会写 2B CSR，变体已删除。变体 ELF：`D:\tmp\lead\s4t35_pl_preproc_20261029_r01\build\s4d_ps_app_pl_selfcheck.elf` sha256 `a577a5cb…9fa01d`（带 SLCR 前置闸，防读挂死）。
- r02 保全阶段的 CSR 三读**无效**（`loadhw -memrange` 为无效选项；解析把回显地址当值）⇒ 判读时丢弃；r03 已修。
- **C 项解阻进展（离线，未上板）**：已构建 **P2c 候选位流** `report/evidence/S4-T34/pl_v2_p2c_dma_bitstream_20261029_r01/`
  —— preproc 源图基址改 `0x12000000`（RTL 参数 `SRC_BASE`，仅 3 处 `rd_addr`）+ 新增 `s4d_axis8_to_axis64` 打包器 +
  **AXI DMA S2MM（非 SG，MM/STREAM 均 64b）→ smc_data → HP0**，DMA 寄存器 `0x43C20000`。
  构建：bit sha256 `0c8ec476…e8352f`（4,045,770 B）、XSA `3f0ed9ea…07e38e`；50 MHz 下 **WNS +0.226 / WHS +0.036**；
  LUT 46.54%、FF 10.90%、BRAM 23.93%、**DSP 71.82%（仅余 62）**。打包器 xsim 自检 `PACKER_TB_RESULT=PASS beats=3`。
  **未上板、无整链仿真、应用侧 DMA 编程未验证、未冻结**；`ENABLE=0`。
  **⚠ r01 已作废**：rev-s5 复审发现 AXI DMA `c_sg_length_width=14` ⇒ 519,168 B 被截断成 11,264 B（构建/DRC/时序全绿也发现不了）；
  见该目录 `ERRATUM_DMA_LENGTH_WIDTH.md`。**不得把 r01 位流当 P2c 使用。**
- **P2c r02（当前唯一可用候选，仍未上板）**：`report/evidence/S4-T34/pl_v2_p2c_dma_bitstream_20261029_r02/`
  —— 修复 `c_sg_length_width=23`（生成 netlist 实测 `wire [22:0] s2mm_length`）+ 把 `SRC_BASE` 改成可参数化
  （engine/wrapper 默认 0 = 冻结基线，BD 覆盖 `0x12000000`）。**3 个冻结 TB 原样复跑逐项一致**：
  `cycles=2655174/2676472/2713979`、engine `FNV dut=gold=0x39a2a8950a11322e`、`P2C_TB_REGRESSION=PASS`（判据已强制 FNV）。
  反压/多帧自检 TB：`PACKER_BP_TB_RESULT=PASS frames=8 bytes=104`。
  构建：bit sha256 `022f48fb…d52ca4`、XSA `8051dd48…61bf4c`；**WNS +0.039 / WHS +0.042**（TNS/THS 0，⚠ 余量仅 39 ps）；
  LUT 46.69%、FF 10.88%、BRAM 23.93%、DSP 71.82%；DRC 0 error。
  **manifest 已过统一门禁**：`check_manifest_hash_basis.py --mode strict` = `entries_checked 26 / mismatched 0 / verdict OK / exit 0`（commit `c2b4ddd`）。
  应用变体（stage4-lead）：`D:\tmp\lead\s4t35_pl_preproc_20261029_r01\build\s4d_ps_app_pl_dma.elf`
  sha256 `56c6967b…ac93100`（267,904 B，6 项编译退出码全 0；含 LENGTH 回读自检、IOC 完成判据、每帧 halt/重武装、IRQ_CLR 顺序）。
  **复审**：rev-s5 初复审 `CHANGES_REQUIRED`（B1/B2）→ 增量复审 **`PASS`**（`D:\tmp\reviews\p2c_design_20261029_r01\REVIEW_DELTA.md`）。
  仍**未上板**：`tensor_crc32=0x5B183B50` 仍是目标；无整链仿真；`SRC_BASE` 是参数非寄存器；未冻结、不主张 G2–G5。
- **M2 复审（D 项）= CHANGES_REQUIRED**（`report/evidence/S4-T34/m2_review_20261029_r01/`，含可复算脚本）：
  ① 归档记录把 PCFG_DONE 归到 `STATUS(0xF8007014) bit1`，而 UG585 v1.2 p.150 step 5 明确 **PCFG_DONE = `INT_STS(0xF800700C) bit[2]`**；
  ② 两处 hex 注释与原始十进制不符（STATUS 实为 `0x40000A30` 而非 `0x40000010`；CTRL 实为 `0x4E00E07F` 而非 `0x4E00FFFF`）。
  结论"PL 未配置"换用 `INT_STS[2]=0` 后仍成立，但须以**勘误**重记，且表述降为"构造性推断"；`INT_STS` 可被写 1 清除，单次为 0 ≠ 从未配置。**旧记录未改写。**
- 边界：以上均未主张 G3/G4/G5；未写 QSPI、未改线、`ENABLE=0`、未 push。

## 本轮结果（四项实测窗口；P1 smoke 失败已收窗，2026-10-27 20:44 UTC+8）

- **窗口结论（lead 指定写入）**：`开窗 20:43:36 → 收窗 20:44:29（53 s）｜P0 PASS｜P1 smoke FAIL（脚本未选目标即 mrd）｜M1–M4a NOT_RUN｜未写 DDR、无副作用｜会话清理 PASS`。**不是 M1–M4 的技术结论，不构成任何通过。**
- **修复（离线，窗口1 后）**：四个 Tcl 全部改为**先选目标再 mrd/rrd**、`targets` 按结构化元素解析；新增 `p1_smoke.tcl`（三步断言，退出码 11/12/13 指失败步）；驱动加入 P1 三步记录与 PRELOAD 装载流程。
- **装载流程（不需新授权，落在"允许易失下载"内）**：`dow init.elf → con（PS/DDR 就绪）→ dow 最小 ELF → M1/M2/M3（CPU1 由构造保持 halted）→ M4-a 仅 con CPU0 → UART 交互`；**不执行 `stop`**；若仍需显式 stop，须 Wong 授权。
- **窗口2（2026-10-27 20:53:28 开窗）结论**：`P0 PASS｜P1 三步 smoke PASS（targets/选目标/只读）｜LOAD FAIL（rst -processor → Invalid reset type，发生在任何 dow 之前 ⇒ 未下载任何载荷）｜M1 FAIL（脚本 info target 非 xsdb 子命令 ⇒ 无 state/PC 证据）｜M2 PARTIAL_INVALID（mrd 返回 ADDR: 空值）｜M3/M4-a NOT_RUN｜P4 清理 PASS（3121 已关、无残留）`。**候选区未被写入、未发 stop、无副作用；非技术结论、不构成任何通过。**
## S4-T32（4-D 离线构建）进展（2026-10-27）

- **Phase 1 = DONE**：三栏盘点/数据流与增量/地址分配（D1=A 内）/接口冻结/构建计划/风险清单 → `docs/stage4/S4D_4d_design_freeze_20261027_r01.md`、`S4D_4d_address_allocation_20261027_r01.json`；验证器 `verify_4d_address_allocation.py` **exit 0**；提交 `c7748bf`。
- **Phase 2 = DONE（基线）**：`build_r01` 因 ENTERPRISE license 过期被阻断（证据保留）；改用 Wong 的 **BASIC license**（`basic_only.lic`，sha256 `59679b8d…`，4 INCREMENT `exp=07-aug-2027`，`HOSTID=00ff79e0276d`）在 `build_r02` 重跑：**SYNTH OK / IMPL OK / bitstream 产出**，耗时 ≈**11.5 min**；**时序收敛 WNS +0.296 ns / TNS 0.000 / WHS +0.090**；利用率 Slice LUTs 17,087、Slice Reg 4,271、BRAM 32（22.86%）、DSP 145（65.91%）。
  - 产物：bit `c7efcb7a…`（4,045,776 B）、XSA `22d4b70d…`（841,362 B）；证据 `report/evidence/S4-T32/phase2_build_r02_20261027_r01/`；门禁 `manifests=1 checked=5 mismatched=0` exit 0。
  - **诚实边界**：该 bit/XSA 是**2B 冻结平台重建**，**不含** `s4b_preproc_frame` 新块与 AXI-Lite `0x200..0x27c` ⇒ **不是 4-D 位流**；4-D 增量 RTL 仍需实现后重建。2B 冻结身份仍是 `555a70c2…`（本次重建产物不同属工具/流程差异，不替换冻结身份）。
- **PS 应用（范围扩展）= DONE（骨架）**：`vitis/stage4/ps/s4d_ps_app.c`（mailbox ABI 128/64/64/64 + AXI-Lite 块 + 像素格式显式映射 + `PREPROC_SRC=PL|SW` 开关 + `infer_one_from_pl_tensor` 跳过 CPU memcpy/输入写回）；两种变体均编译链接成功：SW ELF `3f5dda57…`（183,032 B）、PL ELF `935e535e…`（184,572 B）；网络/解码为 weak 桩（完整应用须链接 r13 目标文件）；提交 `d78c036`/`e8ce472`。
- **Phase 3（离线部分）= DONE**：bring-up 计划与 M3/M4-a/M4-b 判据 → `docs/stage4/S4D_4d_bringup_plan_20261027_r01.md`（**M4-b 必须用 4-D 真实 HP0 DMA 路径；不满足即 FAIL，不得用离线证据替代**；M3 必须采整区恢复后 dump）。
- **离线自检/门禁**：Tcl 自检 `SELFCHECK_RESULT=PASS`；`py_compile` 4/4 exit 0；基座门禁 `--commit 480d8f1 --mode strict` = `manifests=1 checked=8 mismatched=0` **exit 0**。
- **阻塞**：需有效 Vivado license 或已授权机器；PS 侧（Vitis）不需该 license，但 4-D PS 应用实现属范围扩展，待 DSH 裁。
- 边界：全离线未接触板卡；`ENABLE=0` 未变；未 FROZEN；未 push；25 项遗留未动。

## 四项实测最终态（2026-10-27，Wong 方案A 第5窗口后；不再开窗口）

- **M1 = PASS**：CPU1 `Stopped: (Suspended)`，PC `ffffff34` 两次（2.5 s）一致；证据 `report/evidence/S4-B/s4_ddr_four_measurements_20261027_r01/execution_20261027_r05/`。
- **M2 = PASS（构造性排除）**：DevCfg STATUS `0x40000010`（`PCFG_DONE`=0 ⇒ PL 未配置）+ CPU0/CPU1 均 Suspended + 唯一调试客户端；**不是总线测量**。
- **M3 = NOT_CLOSED**：`mwr` 无 `-pattern`、`mwr -bin -file` 缺字数 ⇒ 写入中止、恢复未执行；实际仅写 4 字节（`0x12000000` `bfbd8604→00005a5a`），已用 **4 字节精确回写**还原并以 16 B 逐字节复核**差异 0**；整区恢复后 dump = `NOT_CAPTURED`（见 `m3_restore_provenance.json`；原 `m3_snapshot_restored.bin` 已正名 `m3_readback_after_write.bin`）。
- **M4a = NOT_RUN**；**M4b = NOT_APPLICABLE → 并入 4-D bring-up 必测**。
- **`ENABLE=1` 前置未满足**（M3 未闭合 + M4 未闭合）；本次不解锁。
- **4-D 必做**：用修好的驱动/脚本**重跑 M3 与 M4-a 并留证** —— `run_s4_ddr_four_measurements.py` SHA-256 `502db86f…`（提交 `69731b9`）、`m3_candidate_rw.tcl` 已改为「图案文件写入 + 带字数恢复」；这些修复**尚未在任何窗口验证**。
- 未做：不 push、不动 25 项遗留、不改 `ENABLE`、不烧 QSPI。

## 本轮结果（硬件窗口已授权，等待 main OFFER，2026-10-27 14:55 UTC+8）

- **Wong 已授权硬件窗口（R-1 完成）**。R-2 仍需 main 提交 OFFER —— 阶段4 不写 main。
- **OFFER 前置已实测清楚**：main 分支 `main` / HEAD `bdb7a360…`；main STATE **无 OFFER 行**、
  也**无写权行**（OFFER 校验不要求 main 写权行，只要求一行 OFFER）；
  main 工作树**有 423 项未提交改动**（含 `.codex/STATE.md` 已改），提交 OFFER 时只 add STATE。
- **新增两个生成器，把 R-2→R-3→R-4 压到可一键执行**：
  · `scripts/stage4_s4b/make_offer_line.py` —— 读 main HEAD 取起始提交、读 w4 写权负责人拼出
    `OFFERED Workbuddy 阶段4总控`，并用 adapter 自己的 `_parse_state_handoff_rows` **离线自校验**，
    打印可直接粘贴的 11 字段行；已实测 `[OK] 自校验通过`。
  · `scripts/stage4_s4b/make_handoff_record.py` —— 从 OFFER 与 CLAIM 两个提交的 STATE blob
    取真实 Git 身份，组装 `authority_source` / `claim_source` 生成 handoff 门禁记录。
    负控：两个合法但无 OFFER 的提交 → `OFFER 行数为 0` / `exit 1` / **不留残留目录**。
- **执行指引**：`docs/stage4/s4b_main_offer_execution_20261027_r01.md`
  （含精确命令、三个必踩的坑、1 小时/30 分钟的窗口嵌套）。
- **必须提醒 main 侧的三点**：①只 `git add .codex/STATE.md`，否则 423 项全被卷入；
  ②提交后**不得再改 main 的 STATE**（三处一致性会破）；③若生成后 main 又有新提交，必须重跑生成器。
- 门禁维持 **6/8**；`exclusive_session` 需 OFFER 到位后现场取证（30 min 窗口）。
  未启动 hw_server / xsdb，未开串口，未装载位流；`ENABLE=0` 未变。

## 历史（阶段4 冻结签发 + 门禁 6/8，2026-10-27 14:28 UTC+8）

- **判定：`OFFLINE_SCOPE_FROZEN`（离线范围冻结，已正式签发）**，
  文书 `docs/stage4/s4_stage4_freeze_signed_20261027_r01.md`。
  依据：`report/evidence/S4-CTRL/s4_frozen_set_verify_20261027_r05/` → `FROZEN_SET_VERIFIED` / `exit 0` / **8 项全通过**。
  新增可复跑校验器 `verification/verify_stage4_frozen_set.py`（只读；异常 exit 2 不伪装成未通过）。
- **硬件门禁 5/8 → 6/8**：`cold_basis` 以 `basis_kind=independently_proven_cold_lifecycle` 取得——
  实时复算 hw_server 进程 0、3121 无监听、无 hw_axi；全仓交叉核验排除 2026-10-23 复审负控夹具
  （`fake_*`/`api_root_probe`，共 10 条）后**真实板上执行记录为 0**。
  推论：从未建立 JTAG 会话 ⇒ AXI 无遗留事务 ⇒ 等价冷启动。**这不是物理断电凭据**，
  一旦出现任何 AXI 事务或启动过 hw_server 即失效。
  记录 `report/evidence/S4-B/s4b_hw_gates_20261027_r04/`（6 类，manifest 覆盖完整）。
- **为什么没做到 8/8（结构不可达，非取舍）**：Wong 2026-10-27 告知硬件窗口暂时不能授权。
  `hardware_session_handoff` 必须由 main 在 main STATE 提交 OFFER（心跳 1h 有效，阶段4 不得写 main）；
  `exclusive_session` 须执行时现场取证（30 min 窗口），窗口不授权则提前生成必过期。
  提前生成这两类 = 伪造。故按 `OFFLINE_SCOPE_FROZEN` 签发，并把整体冻结的解除条件 R-1..R-7 写入文书。
- **未达成项如实保留**：板级 P / 4-D / G3 / G4 / G5 全部 `NOT_RUN`；`ENABLE=0` 未变；
  `raw_address_ownership` 提案仍 `DECISION_REQUESTED`（其 B 指「4-D 降为 107 帧」，与方向方案的 B 不同）。
- 本轮修正的三处自身缺陷：
  ① 冻结校验器 F3 原读 `result.json.bridge_source`（该字段实际在 `preflight_verification.json`），
     改为读 preflight 并交叉核对 `preflight_sha256`；
  ② F8 声明卫生扫描原把人读文档里的**否定句**（「不能整体冻结」「不宣称 G5 通过」）与契约
     `forbidden_claims` 条目误判为违规；改为否定语境豁免，并把扫描范围收窄为人读文档；
  ③ `make_runtime_gate_records.py` 不支持等价冷启动证明，已加 `--basis-kind` 并内置实时复算闸门
     （检测到活跃 JTAG 会话即拒绝生成）。
- 未接触板卡 / JTAG / COM4 / Vivado / hw_server；未在 main 写任何行；未下载未烧录；未开阶段7。

## 历史（地址图批准 + 门禁 5/8，2026-10-27 14:18 UTC+8）

- **两份地址文档已由 Wong 批准**（`DRAFT_PENDING_REVIEW` → **`APPROVED`**）：
  `docs/stage4/S4B_stage4_address_map.json`（`c0855078…`）与
  `docs/stage4/S4B_shared_address_map.json`（`f16e9a7c…`）。
  签署附 `approved_by=Wong`、`approved_at_utc8`、`review_binding`（指向
  `report/evidence/S4-B/s4b_address_approval_review_20261027_r01/approval_review.json`，`c15dec98…`）。
  **地址、长度、owner、方向语义一字未改**，只改 status 与批准元数据。
- **批准前的机械核验**（写进复审记录，可复跑）：8 区域 base+len 与 end 全部一致、**零重叠**、
  共享图与源图逐区域 `owner_from_source`/base/len/status **差异为 0**（忠实投影）。
- **g0_approval 已成立**：`report/evidence/S4-B/s4b_hw_gates_20261027_r03/` 一次生成 5 类记录
  （operator_authorization / timing_freeze / range_reservation / command_delivery_review / g0_approval），
  机检 `s4b_hw_gate_readiness_20261027_r12` 确认 **5/8 门禁被 adapter 接受**。
  阻断项 13 → **11 项，且全部属 handoff / exclusive_session / cold_basis 三簇**。
- **依赖映射纠错（我上轮写错）**：机检原把 `raw_address_ownership` 标为 `blocks: ["g0_approval"]`，
  但 adapter 的 g0 判定只校验三份文件、**压根不读该提案**（代码内零引用）。已改为 `blocks: []` +
  `affects: [raw_frame/raw_meta 迁移至 FROZEN_STAGE4, mailbox/RAW 路径启用]`。
- **必须注意的歧义（我的表述问题）**：`s4b_raw_address_ownership_proposal_20261024_r01.json` 仍是
  `DECISION_REQUESTED`，**未裁决**。它的选项集是 **A/C/B/E**，其中 B 指「4-D 输入降为 107 帧预冻结子集」，
  与我上一轮请 Wong 裁的「A/B/C 方向方案」**不是同一组选项**。Wong 的"批准"作用于地址图/共享图状态，
  不等于该提案已裁决。其 D1–D4 仍需裁决（D1 禁区让位、D2 4-D 帧数、D3 META 连续性、D4 linker 冻结前置）。
- **冻结契约的冻结后重绑已留痕**：新增 `post_freeze_rebinds`（地址图 SHA `8f554d95…`→`c0855078…`，
  `semantics_changed=false`，不升 r08）。契约 `2848ba03…`。
- 回归：契约自检 27/27、缺口审计 3/3，均 exit 0。`ENABLE=0` 未变，未接触硬件。
- **修掉一个我自己引入的崩溃**：`verify_shared_io_contract.py` 的 `address_map_approved_ok` 调了不存在的
  `sha256_bytes`，批准后首次运行即 `NameError`；已改用该脚本既有的 `sha256_of`（原始字节、不归一化）。

## 历史（硬件门禁 P3–P6 完成 + g0 绑定修复，2026-10-27 13:52 UTC+8）

- **P4/P5/P6 已完成并被 adapter 接受**：`report/evidence/S4-B/s4b_hw_gates_20261027_r02/`
  生成 `operator_authorization`（操作集固定五项）、`timing_freeze`（PS 全局定时器时基 + stale 200 ms，
  引用 Wong 10-23 批准回执）、`range_reservation`（r13 seed/session 闭区间，`existing_reservations=[]`）。
- **P3 已完成**：对 adapter 的 g0 修复做收口复审判 **PASS**（`reviewed_adapter_sha256=463bb429…`，
  记录 `s4b_adapter_review_20261027_r02`），据此签发 `command_delivery_review`。
- **g0_approval 绑定的真缺陷已修**：原实现把 `address_map_sha256` 与**链接 map**（`4a0f9cf8…`）比较，
  填链接 map SHA 可通过、填真实地址图 SHA 反被拒。改为 `_pinned_binding_ok`：绑定必须为
  `{path,sha256}`、路径 resolve 后精确等于仓库固定相对路径、复算字节 SHA、status 从文件读取。
  五组反例全部按预期拒绝（DRAFT 状态 / 链接 map SHA / 错 SHA / 自造 APPROVED JSON / memory_ranges 不符），
  18 例路径绕过矩阵（相对路径、大小写、UNC、设备前缀、硬链接、junction、同字节副本等）全部拒绝。
- **门禁状态**：8 类中 **4 类已成立**（operator_authorization / timing_freeze / range_reservation /
  command_delivery_review），剩 4 类未成立：`hardware_session_handoff`（需 main OFFER）、
  `exclusive_session`（执行时现场）、`g0_approval`（地址图 DRAFT + 共享地址图不存在）、`cold_basis`（物理断电）。
- 机检 `s4b_hw_gate_readiness_20261027_r07`：`BLOCKED / exit 1`，并把 `shared_address_map` 显式列为依赖
  （此前该文件缺失在报告中不可见，属复审建议 S2 已修）。
- 未接触硬件；`ENABLE=0` 未变。

## 历史（结果契约冻结 + 回放包冻结，2026-10-27 12:28 UTC+8）

- **共享结果契约已冻结**：`docs/stage4/s4b_shared_input_result_contract.json` 状态
  `REVIEWED_OFFLINE_ONLY` → **`FROZEN_OFFLINE_ONLY`**（`s4-shared-io/1.3.0` r07）。
  新增 `freeze_record`：绑定被审字节（json `8beea2c5…` / md `07ded4db…`）与复审提交 `5f9a04a`，
  `freeze_scope=OFFLINE_ONLY`，写明允许消费方、禁止声明与变更策略。
  `verify_shared_io_contract.py` 27/27 PASS（新状态须附完整 `freeze_record` 才放行）。
- **task-27 回放结果包已冻结**：`report/evidence/S4-CTRL/s4t27_replay_package_freeze_20261027_r01/`
  —— 10 个文件逐一绑定 SHA/字节（结果包、门结果、交付清单、预检、6 份 head/回放 bin），
  标 `replay_only`，并绑定契约版本与冻结状态；`missing_files=[]`。
  消费规则：必须逐文件复算，不得只校验 package.json。
- **F-2 执行矩阵**：`docs/stage4/s4b_f2_gap_matrix_20261027_r01.json` —— 10 项缺口按
  「复审可关 / 离线可编 / 需 Vivado / 需其他窗口」分类，含依赖链与需 Wong 决策项。
- **G-15（mailbox 接口复审）中途停放**：已做 3 轮独立复审，D1（`result_seq` 语义冲突）已关闭，
  剩余 2 项阻断未关闭（失败行 `result_seq=0` 与 S4-A 主键冲突；`0x274 RESULT_SEQ` 标 RO 却由 PS 发布）。
  **未翻转 G-15 状态**，仍 `OPEN_REQUIRES_DESIGN_OR_REVIEW`；按 Wong「减少复查」指示暂不继续开轮次。
- 回归：缺口审计 13/13、3/3 PASS；契约自检 27/27 PASS。`ENABLE=0` 未变，未接触硬件。

## 硬件会话状态（2026-10-27 11:55 UTC+8）

- 板卡已由 Wong 上电连接。只读观测：FTDI `VID_0403&PID_6014` 在设备枚举中，串口 `COM4` 存在，`hw_server` 未运行。
- **上电报告不构成授权**（runbook §「正式硬件交接与门禁」明确：工作树写权交接与板卡上电报告不能替代 OFFER/CLAIM）。当前 `S4-B-REAL-02B` 的 main OFFER 与 w4 CLAIM 均未落库，八类门禁记录 0/8。
- 机检证据：`report/evidence/S4-B/s4b_hw_gate_readiness_20261027_r04/`（`BLOCKED / exit 1`，13 项阻断，判定权归 `s4b_ps_tensor_adapter.validate_hardware_gates`）。
- 注入单元离线就绪：`OFFLINE_PREPARATION_VALID`（ELF `bfe88660…`、派生源 `7c3b57a9…`，prepare 与 validate 均 exit 0）。
- 负控：八份伪造门禁记录（含伪造 `status=PASS`）被 adapter 逐字段拒绝，未产生绿通道；首版机检（r01）存在按存在性判定的绿通道，已留档标 `NOT_EVIDENCE`（r02）。
- 未做：未加载位流、未打开串口、未启动 hw_server/xsdb、未复位、未读日志、未改 `ENABLE`。

## 本轮结果（S4-T26-GATE-RERUN + 离线范围冻结，2026-10-27 07:23 UTC+8）

- **task-26 离线门已在当前桥接器字节上通过**：`report/evidence/S4-CTRL/s4t26_gate_rerun_20261027_r04/`
  （status PASS / exit 0 / 6 项检查全 PASS，桥接器 `c6117bb4…`）。r01 为 NameError 失败留档、r02/r03 为更早字节的同类通过，均保留。两样本四个 head 与材料化黄金逐字节一致
  （sample_000 `07b59ca3…`/`7524ce5c…`、sample_102 `902bb209…`/`f96cca66…`），单字节负控、
  PNG `IMREAD_UNCHANGED`、task-25 回放帧均 PASS，**task-27 回放结果包已生成**（`replay_only`）。
  上一轮 2929/5070、10358/20280 的差异确认为 T25 预处理修复前产物，已不再适用。
- **桥接器改动（r11→r12）**：把“黄金来源目录”与“输出 RunId”解耦（新增 `--golden-run-dir`），
  允许在新 RunId 上重跑权威门而绝不覆盖黄金与旧证据；黄金清单 SHA `47e4cc36…` 仍钉死。
  首次尝试 `s4t26_gate_rerun_20261027_r01` 因 `run_dir` 残留引用报 `NameError`（exit 2），
  该失败证据保留；修好后 r02 才 PASS。
- **B1 producer 断点按决策 A 处置**：`docs/stage4/s4t26_producer_break_decision_20261027_r01.json`
  （SHA `95b70b9d…`）。理由：报告 SHA 由 `sha256_file` 运行期计算、工具 SHA 与记录一致，
  数值完整性由 SHA 链保证；重跑 512 样本标定会改变冻结 scale 并使 2A/2B/阶段4 三条线证据失效。
  G0 新增 `--accept-producer-break`（默认关闭），命中后该项记为 `ACCEPTED_WITH_DOCUMENTED_BREAK`
  而非 PASS；G0 r30 结果为 **`CLOSED_WITH_ACCEPTED_BREAK` / exit 0**（`accept_producer_break=true` 已写入 command 与字段，`shared_input_contract` 记录 1.3.0/r07）；同字节无开关的 **r29 仍 `BLOCKED / exit 2`**，默认 fail-closed 有同字节留证。
- **B3 绑定字节口径**：`docs/stage4/S4B_binding_byte_basis_registry_20261027_r01.json`，4 条绑定逐一复算一致
  （契约绑 CRLF 归一化、材料化清单绑原始字节、工具绑原始字节）；契约自身已有 `binding_byte_basis` 声明。
  另修正上一轮文档/STATE 中工具 SHA 的抄录错误（应为 `288390f8…f104a353…`）。
- **门禁对齐器** `s4t26_gate_reconcile_20261027_r17`：**PASS / exit 0**（0 项未闭合，`g0.run_id=r34`）。
  修正三处：RunId 前缀白名单漏新 RunId（改全目录扫描）、G0 固定 r13（改最新已闭合/`--g0-run`）、
  `--g0-run` 曾可接任意路径把断点洗成 PASS（现限定证据根下 RunId 名并校验 preflight 自洽，产物记录 `g0.run_id`/`selection_mode`/`preflight_sha256`）。
- **阶段4 判定：`OFFLINE_SCOPE_FROZEN`（离线范围冻结）**，记录见 `docs/stage4/s4_stage4_freeze_record_20261027_r01.md`。
  已关闭：共享 IO 契约升 r07、按规则重绑两处过期绑定（桥接器→`c6117bb4…` 按 worktree_disk_bytes、w5 显示字段→`af51a4bf…` 按 git_blob_content，旧值均入 `replaces`；契约字节 `8beea2c5…`），并独立复审登记 `REVIEWED_OFFLINE_ONLY`（被审 `5f9a04a`，json `8beea2c5…`/md `07ded4db…`）。
  仍未闭合：RAW 系统 G0 有 10 项设计/复审缺口 + 4 项硬件依赖；
  P / 4-D / G3 均 `NOT_RUN`；`ENABLE=0`；真实 C/PL BGR→RGB `NOT_IMPLEMENTED`。
  因此**不宣称 G3/G4/G5 整体通过**，板级项须另行硬件窗口与正式 OFFER。
- 全程未操作板卡/JTAG/COM4/摄像头/HDMI/Vivado/hw_server，未下载、未烧录。

## 历史（S4-T26-PRODUCER-AUDIT，2026-10-27 00:53 UTC+8）

- 接管：以现场 HEAD `0fcd67595ae5be85b99ee93928a9b265786f3af0` 生成 successor 记录并真实 `--claim`，取得 **`HANDOFF_OK / exit 0 / 9 PASS / 0 FAIL / 0 SKIP`**（2026-10-27 00:41:39）。首次执行即通过，无失败重试；上一窗口在 `e65ea51` 上的 claim 未被沿用。证据 `report/evidence/S4-CTRL/w4_workbuddy_takeover_20261027_r02/`。
- 保护核验：既有 15 项（1 项 STATE 差异 + 12 个 ELF/MAP + 两个 task-26 证据目录）原位、原归属；19 个未跟踪文件 SHA **19/19 一致**；STATE 既有未提交差异（27 增/8 删）仍在工作区、未提交。claim 后工作区为 16 项，增量仅本窗口自己的新证据目录。
- **task-26 状态口径修正（重要）**：`2929/5070、10358/20280` 的 T29 控制差异产生于 T25 预处理修复（`e65ea51`，桥接器 `8a80c33c…`）**之前**；该修复后的诊断探针 `s4t26_layer_divergence_20261026_r02` 记录 `LAYER_MATCH_AND_REQUIRED_GATES_PASS`、38/38 层逐字节一致（layer 30/37 为 yolo 别名层，`t25_stored=false`，不与独立存储张量比对）、两样本 head13/head26 与黄金完全一致、D9/NMS 2→1。本窗口独立复算四份 head 二进制，**全部与黄金逐字节一致**。诊断探针只是“观察 `forward_one` 局部变量”，**不是权威门运行**，不得据此把 task-26 改称 PASS。
- 阻断归因拆分：**B1** activation producer 身份不可复现（记录 `f025f5ab…`/`0487e694…`，固定路径现值 `879148e0…`/`ef907ba3…`，4+5 个候选副本零命中；固定路径 mtime 分别晚 15,995/15,964 秒 ⇒ 报告后被重建覆盖；报告 SHA 由 `sha256_file` 运行期计算，工具 raw SHA `288390f8…` 与记录一致）；**B2** 当前桥接器字节无任何权威门 PASS 运行（7 次桥接结果全部早于 `e65ea51`）；**B3** 绑定字节口径歧义（T29 参考 raw `26392c8d…` vs CRLF 归一化 `24361a13…`，契约绑归一化、材料化清单绑原始，内容同源非漂移）；**B4** 旧 r02 证据缺输入身份字段（当前代码已输出，需重跑落盘）。四项均未闭合；**B5（task-27 输入包）为下游依赖，不计入本轮阻断**。
- 本轮交付（离线、只读）：`scripts/stage4_s4ctrl/audit_t26_producer_provenance.py`（fail-closed 身份/绑定审计，报告 SHA 钉死 + 换钉需 `--allow-repin`，绑定审计无跳过开关）、`scripts/stage4_s4ctrl/reconcile_t26_gate_evidence.py`（门禁证据对齐，须 status=PASS + 整型 exit 0 + 运行期桥接器 SHA 等于当前字节 + 五项必备检查全 PASS）、`verification/test_s4t26_failclosed.py`（20 项子进程负控 + 1 项函数级真值表）、`docs/stage4/s4t26_status_audit_20261027_r03.md`（现状审计 + 关闭条件 + 责任方）。真实结果：审计 `BLOCKED / exit 1`（7 项未闭合）、对齐 `BLOCKED / exit 1`（2 项未闭合）、负控 `PASS / exit 0`；均**不自动变绿**；`reconcile` 的 `PASS` 只表示证据文件内部自洽且满足判定条件，不表示门已在实机跑过（伪造自洽证据根同样可得 PASS）。
- 留档不作证据（本窗口更早迭代，原样保留、不引用其结论）：`s4t26_producer_audit_20261027_r00/`（首跑 TypeError，已补 `NOT_EVIDENCE` manifest，无 `audit.json` 结论）、`…_r01|r02|r03/`、`s4t26_gate_reconcile_20261027_r01|r02|r03|r04/`、`s4t26_failclosed_selftest_20261027_r01|r02|r03|r04|r05|r06/`。结论一律以 audit_r04 / gate_reconcile_r05 / failclosed_selftest_r07 为准。
- 复核记录：第 1 轮 Reviewer `CHANGES_REQUIRED`（P1–P10，含“时间戳当通过”“`--no-binding-audit` 绿通道”“报告未钉死”）；第 2 轮 `CHANGES_REQUIRED`（F1 `False == 0` 绿通道、F2 非法结构 JSON 崩成 exit 1、F3 文档与 r00 manifest 不同步、F4 负控自述不实、R1 STATE 哈希口径）；第 3 轮 `CHANGES_REQUIRED`（`RecursionError` 逃逸成 exit 1、落盘失败留 0 字节残文件、单运行结果损坏被降级为“没跑过”）；第 4 轮 `CHANGES_REQUIRED`（负控 T17 的残留断言写在临时目录上下文之外，属恒真断言）；第 5 轮 Reviewer 以变异测试确认 T17 在重新引入缺陷时确实失败，判 `PASS`。全部已修并重新留证。评审用 SHA 均为**整文件工作区原始字节**口径（如 STATE 顶部块以 `D:\codex-worktrees\w4\.codex\STATE.md` 整文件计、非行区间；工作区为 CRLF、180 处，`core.autocrlf=true`，LF 归一化后哈希不同）。
- 未做：真实网络推理、权威门运行、单字节负控、PNG 检查、task-27 包、任何板卡/JTAG/COM4/摄像头/HDMI/Vivado/hw_server 操作。`ENABLE=0`、RAW 系统 G0 未闭合、P/4-D/G3/G5 `NOT_RUN`、`s4-shared-io r06 DRAFT_PENDING_REVIEW`、真实 C/PL BGR→RGB 运行时 `NOT_IMPLEMENTED` 全部不变。
- 下一步最小可验收任务：**B2 可行性预检**（只读）——核对当前 `task_blockers`/静态检查在 G0 仍 BLOCKED 时是否允许门运行，产出“能否重跑、缺什么”的机器可读结论；不执行推理。B1 须 Wong 在“登记 provenance 断点”与“授权重跑 512 样本标定”之间裁决。

## 当前交接行（11字段，2026-10-27 08:12 UTC+8）

任务=`S4-HW-WINDOW：硬件窗口已授权，等待 main OFFER 后 CLAIM→取证→开跑` | 负责人=`Workbuddy 阶段4总控` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`54e32c479ba0aa3c1e70de403a3d7e6ae7e3d701` | 允许修改范围=`docs/stage4/、scripts/stage4_s4ctrl/、scripts/stage4_s4b/、verification/、report/evidence/S4-CTRL/、.codex/STATE.md；不含 main、dbdf、w2b、w5、w6、厂商原件、信箱与任何硬件` | 未提交改动归属=`Codex 既有 12 个 ELF/MAP 与两个遗留证据目录保持原位未动（STATE 已由本窗口提交）；本轮新增 gate_rerun_r01|r02|r03、g0_inputs_r15..r30、gate_reconcile_r06..r15、gate_rerun_r01..r04、contract_verify_r01..r02、gap_audit_r01..r02、basis_sync_r01..r03 及文档归 Workbuddy 阶段4总控` | 让出声明=`仅 w4；未操作硬件、未下载、未烧录、未开阶段7；离线门 PASS 不等于 G3/G4/G5 通过；producer provenance 为已登记断点，不表示可复现` | 心跳(UTC+8)=`2026-10-27 14:55` | 证据入口=`report/evidence/S4-CTRL/s4t26_gate_rerun_20261027_r04/replay_forward_bridge_result.json；report/evidence/S4-CTRL/s4t26_g0_inputs_20261026_r36/preflight_verification.json；report/evidence/S4-CTRL/s4t26_gate_reconcile_20261027_r18/reconcile.json；docs/stage4/s4_stage4_freeze_record_20261027_r01.md；docs/stage4/s4b_main_offer_execution_20261027_r01.md；report/evidence/S4-CTRL/s4_frozen_set_verify_20261027_r05/frozen_set_verification.json；docs/stage4/s4_stage4_freeze_signed_20261027_r01.md；report/evidence/S4-B/s4b_hw_gates_20261027_r04/gate_records_index.json；report/evidence/S4-B/s4b_address_approval_review_20261027_r01/approval_review.json；report/evidence/S4-B/s4b_adapter_review_20261027_r02/adapter_review.json；report/evidence/S4-CTRL/s4t27_replay_positive_20261027_r01/task27_replay_result_package_positive.json；docs/stage4/s4_hardware_handoff_unblock_plan_20261027_r01.md` | 恢复命令=`python -B -X utf8 scripts/stage4_s4ctrl/replay_forward_bridge.py --run-dir report/evidence/S4-CTRL/s4t26_gate_rerun_<新RunId>; python -B -X utf8 verification/check_s4t26_g0_inputs.py --run-id s4t26_g0_inputs_20261026_r<NN> --accept-producer-break; python -B scripts/stage4_s4ctrl/reconcile_t26_gate_evidence.py --evidence-dir report/evidence/S4-CTRL/s4t26_gate_reconcile_<新RunId>` | 状态/下一接手方=`OFFLINE_SCOPE_FROZEN + 硬件窗口已授权（R-1 完成）；R-2 main OFFER 待提交（阶段4 不写 main），行已生成并自校验；OFFER 后 1 小时内完成 CLAIM→handoff 记录→机检，30 分钟内建会话并开跑`

## 历史交接（2026-10-27 00:29；已由上方本轮接管取代）

## Workbuddy 协作治理交接（2026-10-27 00:29 UTC+8）

- Wong 明确后续主力为 **DSH + Workbuddy**；Codex 退出默认主力写权，既有提交、未提交产物归属及历史证据继续保留。本窗口只完成协作治理，不开展阶段4技术工作。
- Workbuddy 项目总控已按 Codex 2026-10-27 00:21 的正式 OFFER 执行真实 `--claim`：首次因证据入口缺通用 `manifest.json` 返回 `HANDOFF_FAILED / exit 1`；第二次使用 w4 STATE 已有的 r10 通用清单入口并补充 `--claimed-path` 越界核验，取得 **`HANDOFF_OK / exit 0 / 9 PASS / 0 FAIL / 0 SKIP`**。证据：`report/evidence/S4-CTRL/w4_workbuddy_takeover_20261027_r01/`。
- 基线保持 `e65ea51e8c0a5e4c735756ea1aad6bbd101dfb51`。既有15项（含12个ELF/MAP及两个Codex证据目录）保持原位、原归属，不清理、不覆盖、不批量提交；本轮新增接管证据归 Workbuddy。
- Wong 指定阶段4另开新窗口。本窗口取得写权后仅作治理登记，现将 w4 **正式 OFFERED 给 Workbuddy 阶段4总控新窗口**；新窗口仍须独立执行 `--claim` 并取得 `HANDOFF_OK`，不得把本窗口的 claim 当作新窗口认领。
- 本交接不包含 main、其他工作树或硬件权限。板卡、JTAG、COM4、Vivado、下载和烧录仍按既有授权及独立窗口办理；`ENABLE=0`、task-26 `BLOCKED`、P/4-D/G3/G5 `NOT_RUN` 不变。
- main 的三分工规则、信箱与全局 STATE 应由 main 的合法写权方另行更新；本记录不冒充 main 写权或全局交接完成。

## 历史交接行（11字段，2026-10-27 00:29 UTC+8；Workbuddy 新窗口 OFFER，已由上方 OFFLINE_SCOPE_FROZEN 交接行取代）
任务=`阶段4协作治理交接：Workbuddy项目总控已认领，转交Workbuddy阶段4总控新窗口；不做技术推进` | 负责人=`Workbuddy 项目总控（本窗口，让出方）` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`e65ea51e8c0a5e4c735756ea1aad6bbd101dfb51` | 允许修改范围=`新窗口CLAIMED后仅w4内阶段4相关docs/stage4/、scripts/stage4_s4ctrl/、scripts/stage4_s4b/、verification/、独立新RunId的report/evidence/S4-CTRL/与.codex/STATE.md；不包含main、其他树或硬件` | 未提交改动归属=`Codex原15项保持原位与原归属；本窗口仅新增w4_workbuddy_takeover_20261027_r01证据及本治理STATE块；新窗口不得清理、覆盖或批量提交既有项` | 让出声明=`Wong明确仅完成协作格局，阶段4另开窗口；本窗口真实claim HANDOFF_OK/exit0后停止w4写入并OFFERED；新窗口须重新claim；技术阻碍和ENABLE=0不变，无硬件操作` | 心跳(UTC+8)=`2026-10-27 00:29` | 证据入口=`report/evidence/S4-CTRL/w4_workbuddy_takeover_20261027_r01/claim_record.json；report/evidence/S4-CTRL/w4_workbuddy_takeover_20261027_r01/handoff_check.json` | 恢复命令=`git --no-optional-locks -C D:/codex-worktrees/w4 rev-parse HEAD; git --no-optional-locks -C D:/codex-worktrees/w4 status --short; 读取w4/.codex/STATE.md顶部当前交接行及w4_workbuddy_takeover_20261027_r01证据后，以本OFFER记录执行handoff_check --claim` | 状态/下一接手方=`OFFERED / Workbuddy 阶段4总控新窗口；next_owner=Workbuddy 阶段4总控；待新窗口正式CLAIMED`

---

# 阶段4 状态（写权：Codex 项目总控已正式 OFFERED；next_owner=Workbuddy 项目总控）

本次交接于 2026-10-27 00:21 UTC+8 按 Wong 明确决定生效，以下当前交接行优先于本文件其余历史写权及任务继续执行陈述。Codex 完成本次 STATE 更新后停止 w4 写入；Workbuddy 尚须正式 CLAIMED。本次仅交接 w4，不包含硬件、main 或其他工作树写权；阶段技术阻碍及 ENABLE=0 保持有效。

## 当前任务结果（S4-T26-GOLDEN-REBIND，2026-10-26）

- 提交 `138d096358210d84f930eb8af616b1112aef543d`；checker r13 SHA `e0a454dbca52f38512075539170e2645a2bd79a490de63ad971b8360b1b8d801`、bridge r10 SHA `6780446fc4f0d774b5868896b455deec8fc3dcd9e1ffa12a6990577138e57f26` 经独立 Reviewer PASS。决策记录与黄金材料化清单位于 `docs/stage4/s4t26_golden_rebind_decision_20261026_r01.md`、`report/evidence/S4-CTRL/s4t26_golden_rebind_20261026_r02/`。
- T25 冻结切片材料化与 SHA 核验通过。sample_102 raw-head 真实前向逐字节匹配；sample_000 真实前向的 head13/head26 均与 T29 不同，D9/NMS、单字节扰动及 task-25 回放按门控停止；结果 BLOCKED，未生成 task-27 包。旧校准样本标为 `NOT_USED_HISTORICAL`；Darknet r03/r04 控制失败仍非黄金来源。
- G0 r13 为 `BLOCKED / exit 2 / 0 FAIL`，阻断项为 activation producer 来源 SHA 与当前 EXE/hook 不一致。`ENABLE=0`、RAW G0 OPEN、P/4-D/G3/G5 NOT_RUN；未操作硬件。原有 STATE 差异和12个 ELF/MAP 均保留，不纳入本次代码提交。

## 当前任务结果（S4-T26-GOLDEN-CONTROL，2026-10-26 21:31 UTC+8）

- w4 当前提交 `f73132398e21ae1604f6318640cd94bc1b68d5ac`；task-26 检查器 r12 / 桥接器 r09 已独立 Reviewer PASS 后提交。检查器 SHA `583fcfd902c42b49164c9eea10b0816c2f4d7230c5c909c39e6730ebedab5a34`，桥接器 SHA `bad7f8a99707d6d8fe485c63b6e14a46bc9ffdb79719c993b657a25f94d3f9fb`。固定审查基线为 `4c726f17d4a83df9e6fbd8b1a9863c0ac2fb256e` 且按祖先关系验证；r10 的 `33988ed7e8a97a9d5395b8cfd136a327c37d7dc9` 仅作历史记录。
- G0 r12：**BLOCKED / exit 2，无 FAIL**。cv2 既有 Python 3.12.10、校准图身份/SHA、task-25 package/frame 祖先绑定、桥接器动态 HEAD 契约与原13项保护均 PASS；仅 activation producer 来源 SHA 和校准 raw head13/head26 oracle 未闭合。
- T29 `test_fist_000` 控制：r04 Darknet 前向 exit 0；hook 的 layer29/36 输出经冻结 scale 量化后与黄金不一致，分别 `2929/5070`、`10358/20280` 字节不同，结论 **BLOCKED**。r03 的启动失败（`0xC0000135`）及 r04 完整日志、float dump、对拍与清单保留于 `report/evidence/S4-CTRL/s4t26_golden_control_20261026_r03/`、`..._r04/`；G0 记录见 `s4t26_g0_inputs_20261026_r12/`。
- 按控制门槛立即停止：G0 已只读核验校准图像 SHA `c116ba1d…35ee70b`，但未对其推理，未生成新 raw head 或 producer/activation 记录；D9/NMS、负向对照、PNG 检查与 task-27 包均 `NOT_RUN`。
- ENABLE=0，RAW G0 未闭合，P、4-D、G3、G5 均 `NOT_RUN`。未操作板卡/JTAG/COM4/Vivado/下载/烧录。原13项改动继续保留，本 STATE 增量未暂存。

## 当前任务（S4-T26-GOLDEN-CONTROL，2026-10-26 20:44 UTC+8）

- Wong 明确撤回 `d2262bc` 的 w4 OFFER，由 Codex 继续 task-26；**DSH 不 claim**。仅修改 w4；不操作板卡、JTAG、COM4 或 Vivado，不改写 main/dbdf/w2b/w5/w6。
- 起始提交 `d2262bca4c562cf2ff9037e6ed098e37f3d62596`；原有 STATE 差异及 12 个 ELF/MAP 已逐项核验、保持原位。初始归属与 SHA：`report/evidence/S4-CTRL/s4t26_golden_control_20261026_r01/initial_snapshot.json`；原始 STATE 临时恢复快照在该清单声明的 tmp 目录，不纳入提交。
- 执行顺序：修正固定提交/祖先绑定并独立复审 → 当前 Darknet/hook 对 T29 `test_fist_000` 导出 layer 29/36、按冻结 scale 量化并逐字节控制对拍 → **仅完全一致后**生成指定校准样本新黄金和 producer 记录，再推进真实推理/回放。任何控制差异立即停止，结果保持 BLOCKED。
- `ENABLE=0`、RAW 系统 G0 未闭合、P/4-D/G3/G5 NOT_RUN 继续有效；本任务不自动解除这些关口。

## 历史交接行（11字段，2026-10-27 00:21 UTC+8；正式 OFFER，已被 00:29 治理交接取代）
任务=`阶段4 w4 写权移交 Workbuddy；保全 task-26 阻断状态与既有差异` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`e65ea51e8c0a5e4c735756ea1aad6bbd101dfb51` | 允许修改范围=`接收方正式 CLAIMED 后仅 w4 内阶段4 task-26 相关 docs/stage4/、scripts/stage4_s4ctrl/、scripts/stage4_s4b/、verification/、独立新 RunId 的 report/evidence/S4-CTRL/ 和 .codex/STATE.md；保护既有差异及证据，不覆盖旧 RunId；本次 Codex 仅修改 STATE，不授予硬件、main 或其他树写权` | 未提交改动归属=`现场15项：.codex/STATE.md 为原有用户差异及 Codex 状态增量；12个ELF/MAP为 Codex 本机恢复产物；report/evidence/S4-CTRL/s4t26_g0_inputs_20261026_r11/ 与 s4t26_golden_rebind_20261026_r01/ 为既有 Codex task-26 证据目录；19个未跟踪文件逐项 SHA 及原始 STATE/差异已保全于证据快照；全部留原位、不清理、不覆盖、不暂存或批量提交，归属不因交接改写` | 让出声明=`Wong 已明确决定向 Workbuddy 移交 w4；Codex 完成本次 STATE 交接更新后停止所有 w4 写入；现场 HEAD 保持不变、暂存区为空、index.lock 不存在，未发现 Git/Vivado/XSDB/hw_server/Vitis/XSCT/XSim 引擎进程或3121监听；未操作硬件；不包含硬件、main 或其他工作树写权；不代表阶段验收通过` | 心跳(UTC+8)=`2026-10-27 00:21` | 证据入口=`C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\w4_offer_workbuddy_20261027_0021\snapshot.before.json（逐文件SHA）；同目录 STATE.before.md、tracked.before.patch；report/evidence/S4-CTRL/s4t26_golden_rebind_20261026_r02/；report/evidence/S4-CTRL/s4t26_golden_control_20261026_r01/initial_snapshot.json` | 恢复命令=`git --no-optional-locks -C D:/codex-worktrees/w4 rev-parse HEAD; git --no-optional-locks -C D:/codex-worktrees/w4 status --short; git --no-optional-locks -C D:/codex-worktrees/w4 diff -- .codex/STATE.md（只读核对并对照保全快照；不 reset/clean/覆盖；认领前重查锁与资源）` | 状态/下一接手方=`OFFERED / Workbuddy 项目总控；next_owner=Workbuddy 项目总控；待接收方正式 CLAIMED`

## 收尾快照（2026-10-26 18:03 UTC+8；优先于旧交接行）

- **阶段4未冻结。** 当前 HEAD `33988ed7e8a97a9d5395b8cfd136a327c37d7dc9`。BGR888 契约 r06 的定向包经独立复审 PASS，但契约仍标 `DRAFT_PENDING_REVIEW`；RAW 系统 G0 为 `CHANGES_REQUIRED_NOT_CLOSED`，候选 region 未冻结且 `ENABLE=0`。
- **未闭合阻碍**：真实 C/PL BGR→RGB 运行时未实现；task-26 回放桥真实推理因缺可导入 `cv2` 的既有解释器、冻结校准样本绑定的 raw head13/head26 黄金及冻结参数 SHA 而 `BLOCKED/exit 2`；注入集成 11/12，剩余用例为 sandbox 阻断；RAW G0 尚有 D2 整帧/padding、HP0 owner/排空、平台 BD/XSA、PS RAW task 冲突、协议、资源/布线时序与 mailbox ABI 等缺口；帧周期 P、4-D、真实彩色回归及 G5 未完成。Wong 批准 stale limit 为 200 ms；该决策本身不冻结 r06 契约或完成实测。
- Wong 报告手册断电重启后 JTAG/A9 恢复；本轮未独立验证或操作板卡。阶段4 板级窗口仍须按 `CDX-20261023-019` 由 lead 正式 OFFER；在硬件前置/授权完成前保持 `ENABLE=0`，不访问候选 RAW region。
- 当前 13 个状态项为本树既有 `STATE.md` 改动及 12 个未跟踪 ELF/MAP（6 对），全部保留；不在本轮提交/改写业务契约、脚本或构建产物。所有阶段活动已按 Wong 指令停止。Codex 仍持本树写权，Wong 表示后续交接给 DSH，但尚无正式 `OFFERED/CLAIMED`。

## 历史交接行（11字段，2026-10-26 18:03 UTC+8；已被后续多轮交接取代）
任务=`阶段4状态收尾：暂停开发与硬件活动，记录 RAW G0、回放/P 和 G5 阻碍，准备后续 DSH 交接` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`33988ed7e8a97a9d5395b8cfd136a327c37d7dc9` | 允许修改范围=`本轮仅 .codex/STATE.md；不改契约、地址图、脚本、构建产物或硬件` | 未提交改动归属=`已有 STATE 差异及 12 个未跟踪 ELF/MAP 保持原样，未暂存或清理；本轮状态摘要归当前 Codex` | 让出声明=`按 Wong 指令停止一切开发/硬件活动；未进行 Vivado/JTAG/COM 操作，region 仍 ENABLE=0/非 FROZEN；用户报告 JTAG/A9 恢复但未独立验证；当前尚未正式向 DSH OFFER` | 心跳(UTC+8)=`2026-10-26 18:03` | 证据入口=`report/evidence/S4-CTRL/s4_bgr888_contract_20261025_r01/delivery_manifest.json；report/evidence/S4-CTRL/s4t26_forward_bridge_20261024_r07/delivery_manifest.json；report/evidence/S4-CTRL/t21_raw_address_crosscheck_20261024_r05/raw_address_owner_crosscheck.json` | 恢复命令=`git -C D:/codex-worktrees/w4 rev-parse HEAD; git -C D:/codex-worktrees/w4 status --short` | 状态/下一接手方=`IN_PROGRESS（活动暂停；RAW G0、推理、P、4-D/G3/G5 均未闭合）/ 等 Wong 正式交接给 DSH；交接前写权属 Codex`

## task-26 G0 接续结果（2026-10-26 19:32 UTC+8；r10 为最终固定输入预检）

- 修复两轮 Reviewer 意见后，权威直接命令运行 `s4t26_g0_inputs_20261026_r10` 返回 **BLOCKED / exit 2**，无 FAIL。既有 Python 3.12.10 可导入 `cv2 4.13.0`；校准清单 SHA `d637a2fe…a1a35c`、D8 cfg `5475dff0…725376`、weights `3984affa…f7d8a`、GF8 `f6feb6d4…93cc39`、S4-A r06 与 activation report SHA 均匹配冻结绑定。缺失必需文件/绑定和 task-25 字段分类为 BLOCKED；task-25 状态核验使用 `--no-optional-locks` 并记录 dbdf index 前后 SHA 不变；RunId 必须显式提供且已存在目录拒绝覆盖。
- 缺失输入故障注入 `r08`（S4-A 路径不存在）与 `r09`（task-25 包目录不存在）均完整生成 preflight 与 delivery manifest、返回 BLOCKED/2、无 FAIL；正式输入未被改动。Reviewer 对 r07 的 CHANGES_REQUIRED 为“缺输入时 delivery manifest 仍无条件计算 SHA/解引用”；当前检查器用可空 SHA 与空输入记录关闭该项，r08/r09 已覆盖两条缺失路径。
- task-25 包从明确提交 `584b07664e88a18bf786ba9565a138861e136d76` 消费，清单 SHA `616da71d…067b6e`；源帧提交 `0ad2000cbc4af7b29f299c2277465bba608a8129`，SHA `939fce22…6752f0`，1280×720 BGR888 输入字段完整。其 `capture_time_ns` 是秒级 `replay_documented_wallclock`，仅作 `replay_only`；不把 `injection_start_ns` 当采集时间。
- 阻断：冻结校准样本 `D:\FPGA_Data\HaGRIDv2\dataset\fist\fist\98529267-1eda-43a6-8e38-245947ecb312.jpg`（SHA `c116ba1d…35ee70b`）的历史记录只有 metrics/integer_stats，无同 SHA 的独立 raw head13/head26 黄金；activation report 引用的 Darknet EXE SHA `f025f5ab…229948`、hook 源 SHA `0487e694…7ef7d65` 与固定路径当前字节不符；旧桥接入口固定 w4/dbdf HEAD 与本任务指定基线/精确 task-25 来源不符，未执行该入口。
- 实际网络推理、raw head 对拍、D9/NMS、负向对照、PNG `IMREAD_UNCHANGED` 检查和硬件运行均 `NOT_RUN`；未生成 task-27/28 冻结推理结果。继续保持 `ENABLE=0`、RAW 系统 G0 未闭合、P/4-D/G3/G5 `NOT_RUN`；s4-shared-io r06 仍 `DRAFT_PENDING_REVIEW`。
- 验收证据：权威目录 `report/evidence/S4-CTRL/s4t26_g0_inputs_20261026_r10/`（预检 JSON SHA `72f87a8b…65233a`；检查器 SHA `c31d09e4…62025d`）。dbdf task-25 输入与显式提交核验通过，状态检查 index SHA 前后相同；r03-r09 作为前置诊断/故障注入尝试原样保留。既有 12 个 ELF/MAP 哈希复核未变、既有 STATE 差异保留。

## 历史交接行（11字段，2026-10-26 19:40 UTC+8；OFFER 已由当前任务撤回）
任务=`S4-CODEX-T26-OFFLINE G0 阻断收尾并交还 w4 写权` | 负责人=`Codex 项目总控（当前让出方）` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`33988ed7e8a97a9d5395b8cfd136a327c37d7dc9` | 允许修改范围=`docs/stage4/；scripts/stage4_s4ctrl/；scripts/stage4_s4b/；verification/；report/evidence/S4-CTRL/；.codex/STATE.md` | 未提交改动归属=`task-26 检查器和 r03-r10 证据已提交于 29b7c231；原有 .codex/STATE.md 用户差异及 12 个 ELF/MAP 未提交、未改动` | 让出声明=`独立 Reviewer PASS；task-26 G0 BLOCKED/exit 2；Codex 已停止 w4 写入并 OFFERED 给 DSH 项目总控；未启动硬件、Vivado、JTAG、COM4 或板测；阶段3与硬件仍归 DSH` | 心跳(UTC+8)=`2026-10-26 19:40` | 证据入口=`report/evidence/S4-CTRL/s4t26_g0_inputs_20261026_r10/manifest.json` | 恢复命令=`git -C D:/codex-worktrees/w4 rev-parse HEAD; git -C D:/codex-worktrees/w4 status --short` | 状态/下一接手方=`OFFERED / DSH 项目总控（待 DSH claim）`

更新：2026-10-25 05:31（UTC+8）。工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`。规则见 `D:\FPGA_Competition\AGENTS.md`。
**写权：依 `DSH-20261024-006` 正式 OFFER 与 Wong 授权，由 Codex 项目总控接续。task-26 桥接脚本及 r07 包已提交于当前基线 `06c9ab8`；其独立只读复审 PASS（仅代码/证据一致性），真实推理仍 BLOCKED/exit 2。task-21 registry 修复经 R4-03 独立复审 PASS，现已完成总控复核并提交；无硬件/Vivado操作。**

## 当前增量（BGR888 契约 r06，2026-10-25 23:03 UTC+8）

- 当前基线 `2c1dcd6e81efdfd9d4ed6f70b5d1af9016b985de`；契约升为 `s4-shared-io/1.2.0 r06`，**`DRAFT_PENDING_REVIEW`**。共享 `pixel_format` 为名称字符串，支持规格值 `BGR888`；像素通道序 `[B,G,R]` 与平台 `byte_order=little` 分开。D2 离线 Python 参考只做一次逐像素 BGR→RGB，再 resize/归一化/量化。
- **真实 C/PL 运行期仍 `NOT_IMPLEMENTED`**：缺 mailbox PS driver；`s4b_preproc_frame` 未接入实际 RTL top，且当前独立模块未实现 BGR 通道重排。C enum 的 `1=RGB565` 与候选 wire `mailbox_pixel_format_code=1` 仅属不同命名空间，候选映射未冻结，禁止直接 cast。RAW 系统 G0 保持 `CHANGES_REQUIRED_NOT_CLOSED`，地址区非冻结、`ENABLE=0`。
- 唯一证据包 `report/evidence/S4-CTRL/s4_bgr888_contract_20261025_r01/` 绑定 16 个源码路径。定向结果：契约 27/27、upstream 17/17、r06 负例 10/10、G0 依据 17/17 + 离线复算 13/13 + gap 状态 3/3、registry 10/10、地址/词汇 11/11、BGR 映射 2/2；整组注入 11/12，唯一 integration case 因沙箱拒绝创建固定工作树临时目录而未执行成功，不算通过。JSON/占位扫描/CRLF-aware diff check 均通过。
- 当前增量已完成独立复审 PASS：首轮发现历史清单版本误标后，生成器已改为既有清单不可覆盖；r02 清单固定 SHA 核验通过，构建器重跑 exit 0 并保留四份旧清单字节。复审结果及重跑摘要见 `report/evidence/S4-CTRL/s4_t21_manifest_immutability_20261025_r01/`。源码、STATE 及两个新证据 RunId 已提交于 `33988ed`；旧 12 项 ELF/MAP 未跟踪产物未动。仍未闭合：校准样本独立 heads 与 `cv2` 运行环境、RAW G0、真实 PS/PL 集成、帧周期 P、板级窗口和 G5。

## 当前离线修复（task-21，2026-10-25）

- 新 RunId `report/evidence/S4-CTRL/t21_address_binding_fix_20261025_r01/` 修复阶段3重复来源哈希及阶段5两个帧缓冲区的十进制/十六进制矛盾；权威值分别为 `d5ba4b6b…`、`0x00114C00=1133568`、`0x00F95400=16339968`。
- 主入口回归 8/8、registry 12/12 + 11/11依据、delivery evidence `CHECKS_OK`；独立审查 R4-03 `PASS` 仅关闭这两项重复事实缺陷。
- 旧 `bound_trees.json` 当前仍 `FAIL_STABLE_DRIFT`、1/5 匹配；未重绑。RAW系统G0、区域冻结、P实测、板级4-D与G5仍未完成；`ENABLE=0`、未 FROZEN。

## 当前接续增量（task-26，2026-10-24）

- 基线提交 `1046cdc9eedefd903e6b96e0190f4897c6a371db`，分支 `stage4-infer-prep`；主输入契约、地址图和 RAW G0 状态不变，仍 `ENABLE=0`、未 FROZEN，未访问板卡。
- 回放桥 `scripts/stage4_s4ctrl/replay_forward_bridge.py` 增加 heads 捕获、D9 解码入口、量化输入字节扰动检查及两 PNG `IMREAD_UNCHANGED` 像素比较；代码和 r07 证据经独立复审 PASS。该结论不代表真实推理验证通过。
- 当前证据 `report/evidence/S4-CTRL/s4t26_forward_bridge_20261024_r07/`：清单/源码快照哈希一致；状态 `BLOCKED`、退出码 2；冻结校准样本推理、raw heads 对拍、D9/NMS、负向对照及 PNG 像素检查均 `NOT_RUN`。
- 阻塞输入：可导入 `cv2` 的既有解释器；绑定到指定冻结校准样本路径与 SHA 的独立 raw head13/head26 黄金及对应冻结参数来源 SHA。不得安装依赖或以合成烟测冒充网络推理。r01–r06 历史 RunId 全部保留。
- 阶段4仍未冻结：RAW 系统 G0、P 实测、硬件集成及 G5 均未完成；板级窗口按 `CDX-20261023-019` 暂缓，需另行正式 OFFER。

## 当前接续增量（2026-10-24）

- 基线 `ced5bdef5c6f2d623237908ddb74baa4d6fa2bdb`，无 `index.lock`；原有 13 项未跟踪（12 ELF/map + 未完成 `replay_forward_bridge.py`）均保留原位、未修改、不入本轮提交。以下 task-21 内容为历史事实，当前接续以本节为准。
- B-r03-1：`verify_shared_io_contract.py` r07 按 `byte_basis` 单次取得 raw bytes，同一字节同时用于 SHA 与 S4-A/阶段5 JSON 语义解析；固定 blob 不可读、缺修订、未知口径或 SHA 不符均不得回退磁盘。
- 新证据 `report/evidence/S4-CTRL/s4_codex_binding_fix_20261024_r01/`：定向回归 9/9、真实契约自检 26 PASS/0 FAIL（15/15 绑定）、消费方回归 10/10，exit 均0；初始测试夹具错误保留摘要。固定100/磁盘200/契约200现被拒绝，固定200/磁盘100按固定200通过。
- 旧 `bound_trees.json` 的审查有效窗口已失效：w4/main 的 MOVING 与 dbdf/w5 的 STABLE 均已出现 HEAD 漂移。本轮只证明工具字节绑定修复与当前声明文件哈希；未重发跨树有效窗口、未把当前哈希复核升级为系统 G0。旧完整 T 标签报告未找到，不补造映射。
- 接口、地址与109/109覆盖不变；`ENABLE=0`、未 FROZEN、RAW系统G0未闭合；硬件、P实测、4-D/G5仍未完成。以上为 task-21 收尾时的计划快照；task-26 当前状态见本文件上方。

## 接管核对（task-21 目标 1）

- Codex 按 Wong 指令停止写入并交付 `d13610d`；DSH 项目总控以接续记录 `report/evidence/CTRL-DSH-HANDOFF/dsh_claim_20261024_r01/` 正式认领并提交 `f6fa9f0`（承载该认领）。本轮在该 HEAD 上以新记录 `report/evidence/S4-CTRL/t21_takeover_20261024_r02/` 复核：**`HANDOFF_OK` PASS 9 / FAIL 0 / exit 0**（含 `--claimed-path` 越界核验）。
- 核对事实：无 `index.lock`；无重型引擎进程（6 个命中项均为 MCP server 进程，非 Vivado/xsim 引擎）；3121 无监听；**12 项**未跟踪 = 6 ELF + 6 map（`report/evidence/S4-B/s4b_ps_tensor_20261023_r04|r05|r09|r11|r12|r13/s4b_ps_tensor_diagnostic.*`），归属保持 Codex 交接口径（本机恢复产物），**留原位、不入源码 Git、不删不覆盖**，逐文件 SHA 见该 RunId 的 `untracked_sha256.txt`（r13 `.map` SHA 与 readiness 文档引用值一致）。
- **硬件使用权不随工作树交接**：依 `CDX-20261023-019` 本轮不申请、不保留、不占用硬件窗口。
- **已知结构性现象**：DSH 原认领记录写于其自身提交之前（声明 `base_commit=d13610d`），在新 HEAD 上复跑会在检查项 a 报漂移；该 FAIL 已据实保留在 `t21_takeover_20261024_r02/handoff_check_previous_claim_record_drift.json`，判据是认领时刻的 PASS 9 证据，而非事后复跑。
- **交接约定（DSH 项目总控 2026-10-24 裁决）**：交接记录只声明**它被写出的那个提交**，接管时刻的 `--claim` PASS 9 即为认领证据；之后 HEAD 前进造成的检查项 a 漂移属**设计行为**，在 STATE 写明、复跑用 successor 记录即可；`handoff_check.py` 的祖先/successor 语义改造**登记为待排期改进项**（须连同 38 个单测与既有证据包一起改并重审）。

## 本轮交付（task-21）

- **输入契约改绑真实彩色（r04）**：`docs/stage4/s4b_shared_input_result_contract.json` r03→r04 + 人读镜像。新增 `input_source_profiles`：描述性范围标签 `camera_live_colour`（`real_live`）/`camera_capture_replay_colour`（`replay_only`，结论必须标回放）；绑定阶段3 无补偿 SOF `7cb33068…`、运行 ELF `an5642_j11cmos2_v10_read.elf` `1457cda4…`、1280×720/stride 3840、传感器 RGB565、DDR 转储 B/G/R（**不得与模型 RGB888 混同**）、原图坐标口径、逐帧源帧哈希；采集时钟 `PENDING_MEASUREMENT`（未实测不填造）。显式登记 `cdx_015` r02→r03 绑定取代关系（改绑前自检实测 22 PASS/1 FAIL exit 1）。
- **已批准项应用**：`result_contract.stale_rule.stale_limit_ns` 由草案 `null` → **200000000 ns**，`stale_limit_status=APPROVED_BY_WONG` + `approval_reference`（阶段6 批准记录 SHA `d8edb848…`），与 w5 `STALE_AGE_LIMIT_NS` 同源同值；S4-A r06 内 `DRAFT_PENDING_APPROVAL` 标签登记为历史快照（其取代值以批准记录为准，r06 字节未改写）。**『已批准』≠『实现已同步』**：真实链路 stale 判定仍 `NOT_RUN`。
- **RAW 系统 G0 收口**：`docs/stage4/S4B_raw_system_g0_gap_registry.json` 承接 `d4f30e3` 检查点，逐项登记 G-01..G-19 与 J10 范围外不适用项；只读复算 **9/9 算术、8/8 依据件、状态纪律通过**（需硬件缺口一律保持 `NOT_RUN`/`BLOCKED`）；系统 G0 仍 `CHANGES_REQUIRED_NOT_CLOSED`。
- **帧周期 P 实测方案**：`docs/stage4/S4B_frame_period_P_measurement_plan.md` + 证据模板 + 校验器（6/6 负向对照被拒：禁止填造/回放冒充/样本不足/统计矛盾/门禁缺失/计时器未标定）；**数值仍 `NOT_RUN`**，供阶段6 `T6-A03`。
- **契约自检升 r05**：已批准态必须附批准记录且与阶段5 同源；彩色改绑＋批准态共 **8/8** 负向对照被拒；`upstream_bindings` **12/12** 现场复算一致；契约消费方回归 `verification.test_s4_inject_frame` **10/10 OK**。
- **G-01/G-02 待决提案（规范层面，不改实现）**：`docs/stage4/S4B_raw_address_ownership_proposal_20261024_r01.md` + `.json`；算术证据 `report/evidence/S4-CTRL/t21_raw_address_proposal_20261024_r01/`（`scripts/stage4_s4b/check_raw_address_options.py` **exit 0**）。关键事实：2B 窗口内**最大连续空洞 9,825,540 B < 最大帧 11,059,200 B** ⇒ 全 109 覆盖必须扩出窗口或缩小输入范围。候选 **A**（禁区 12 MiB + 相邻 META，109 帧，余量 +1,523,712 B）／**C**（禁区 11 MiB + 窗口内 META，109 帧，余量 +475,136 B）／**B**（窗口内 9 MiB，107 帧，排除 2 张 1920×1920，属需求层覆盖变更）／**E**（`ps_app_arena` 上部，107 帧，耦合 linker 布局）。**裁决前 G-01/G-02 状态不变、`ENABLE=0`、不访问候选区**；D1–D4 见提案 §5。

## 证据入口（本轮新 RunId，`report/evidence/S4-CTRL/`）

- 接管：`t21_takeover_20261024_r02/`（`t21_takeover_20261024_r01/` 为首次尝试失败输出，保留）。
- 契约改绑：`t21_contract_colour_rebind_20261024_r02/`（`…_r01/` 为改绑前基线 22P/1F exit 1）。
- RAW G0：`t21_raw_g0_gap_registry_20261024_r03/`（`…_r01/` KeyError 失败、`…_r02/` 被 r03 取代，均保留）。
- P 方案：`t21_frame_period_p_plan_20261024_r01/`。
- 通用交付检查器：**evidence 模式 4/4 `CHECKS_OK` exit 0**；inputs 模式按设计被阻断（契约/地址图仍 `DRAFT_PENDING_REVIEW` 未冻结，且含 FAIL/NOT_RUN 检查），原始输出在 `tmp/4/S4-T21/t21_delivery_check_20261024_r02/`。
- 落点更正：本轮 RunId 起初误建为 `S4-CTRL/S4-T21/<run_id>`（多一层），已上移为 `report/evidence/S4-CTRL/<run_id>` 以符合 `report/evidence/<task_id>/<run_id>/` 约定；个别结果 JSON 内记录的 `--evidence-dir` 仍为迁移前路径，仅路径字符串差异，内容未改写。

## 未闭合 / 下一步

- 契约 r04、RAW 缺口登记表与 P 方案已经在**被审提交 `7a9507a`** 上通过独立复审 **`PASS`**（阻断 0／非阻断 4）：契约 r04 可作为阶段4 **当前基线**（冻结时必须显式引用 `r04` + 被审 SHA）；G-01 被独立确认为**设计级阻断**（窗口内最大连续可用区 9,825,540 B < 最大帧 11,059,200 B，缺口 **1,233,660 B** ⇒ 批准不足以解决，须 Wong 决定）。
- **流程纠正（下一轮起严格执行）**：① 交审前先声明**固定基线**并**停写被审对象**；审查期间只允许改**审查范围之外**的文件且必须**先报 lead**；② 冻结/引用基线必须写明**提交号 + 被审 SHA**，不得写“最新”；③ 若须在审查期间改动同范围 ⇒ **对新基线另行复审**，不得沿用旧结论。（本次成因是排程重叠，已在 lead 侧记录。）
- RAW 系统 G0 当前缺口：G-01/G-02 均为 `PARTIALLY_CLOSED_OFFLINE`（D1=A 已批准并登记；仍待固定版本独立 G0 复审，region 非 FROZEN、`ENABLE=0` 且不得访问候选区）；D2 整帧/padding 数值（G-04）、HP0 串行 owner 与排空（G-05）、平台 BD/XSA（G-07）、PS RAW task 与旧 memcpy 冲突（G-08）、协议项（G-09/G-10/G-11/G-13）、资源与布线后时序（G-14）、mailbox ABI 审查（G-15）。
- 硬件相关**全部 `NOT_RUN`**：八类门禁与正式 OFFER/CLAIM（G-16）、4-D 验收（G-17）、真实彩色回归（G-18）、帧周期 P（G-19）。
- 4-D 与阶段4 G5 未完成；不得把离线/回放结论升级为实物集成结论。
- **G-01/G-02 已按 Wong D1=A 一次性落盘（全离线）**：Wong 2026-10-24 批准选项 A、**不接受降覆盖**（D2 作废），记录 `decisions/stage4_raw_address_optionA_20261024_r01.md`（承接 DSH 初裁 `stage4_raw_address_d1_d4_20261024_r01.md`）。落盘内容：地址图 **r03** 新增 `raw_frame=[0x12000000,0x12C00000)`（12 MiB）+ `raw_meta=[0x12C00000,0x12C08000)`（32 KiB），把**本阶段自设**禁区条目精确缩减为 `[0x12C08000,0x20000000)`（其余禁区不动）；两 region 状态 `PROPOSED_STAGE4_OWNED_PENDING_APPROVAL_AND_REVIEW`（**非 FROZEN**、`enable_required=true`），登记 owner/access/cache 维护方向/完成序/容量；契约 **r05** 同版本重绑 + 消费方（阶段5/6）重绑清单。地址图与契约 `status` 仍 **`DRAFT_PENDING_REVIEW`**。
- **条件①三方交叉核对已闭环**：`report/evidence/S4-CTRL/t21_raw_address_crosscheck_20261024_r05/`（exit 0）⇒ **2B**（冻结件自证：候选起点即其专属窗口末端）、**阶段5**（送显三缓冲 `0x00114C00/0x00703800/0x00CF2400`，上界 `0x00F95400`）、**阶段3**（书面事实 `0x00110C00`、单缓冲、采集=显示共用）**均不相交**；`condition_1_status=SATISFIED_BY_BOUND_FACTS`。**保留条款已写入地址图 notes**：阶段3 帧基址为运行期分配、无链接期静态保证，消费方须运行期回读、禁止硬编码。
- **复审非阻断 N-1..N-4 已同批处理**：N-1 新增顶层 `binding_byte_basis`（默认磁盘字节；**跨树引用按已提交 blob 口径**，dbdf 两项与 w5 G0 字段改绑 blob + 磁盘注记；实测发现 w5 工作树在编辑中、dbdf 已推进 HEAD `0ad2000c`）；N-2 G-01 补写“设计级阻断（窗口内缺口 1,233,660 B）、已由 Wong 批准 A”并写准 `next_owner`；N-3 三处 `--evidence-dir` 已用新 RunId 重跑（`t21_contract_optionA_20261024_r02`、`t21_raw_g0_gap_registry_20261024_r05`、`t21_frame_period_p_plan_20261024_r03`）；N-4 `readiness_doc.sha_note` 更正为「属 S4-B 冻结快照证据、可从 `f6fa9f0` 复原」。
- **本批自检结果（新 RunId）**：契约自检 **26 PASS/0 FAIL**、缺口复算 **11/11 + 状态纪律**、P 校验 **6/6 负向对照**、交叉核对 **条件① SATISFIED**、契约消费方回归 **10/10 OK**，全部 **exit 0**；批次清单 `report/evidence/S4-CTRL/t21_optionA_landing_20261024_r01/landing_manifest.json`。
- **复审结论 `CHANGES_REQUIRED`（针对 `d29ef5f`，3 阻断 + 4 非阻断）与修复**：B-1 `stage5_display_g0_fields` 重绑 w5 已提交 blob `10d24a39…`（`8eac7007…` 经 `replaces` 记为修 r02 前修订），并标注**待阶段5 r02 复审结论、未冻结**；B-2 `stage3_window_address_facts` **三处**（契约/registry/地址图 factsources）统一补 `byte_basis=git_blob_content` 并重绑 dbdf 新 HEAD `6fa77a64` 的 blob `d5ba4b6b…`（原磁盘值 `19f754d8…` 失效；缺口复算脚本同步支持按声明口径复算）；B-3 新增 `scripts/stage4_s4ctrl/check_bound_tree_heads.py` + `bound_trees.json`，**fail-closed 断言**（任一被绑树实际 HEAD ≠ 记录值即 FAIL），实测 **5/5 一致 exit 0**；N-a 更正 dbdf `.gitattributes` 事实（确有 `report/evidence/S3-T05/** -text`，2026-10-01 起；差额成因＝`-text` 生效前入库 + 索引 stat 缓存）；N-b `overlap_proof` 文字统一为「全部顶层 region 逐对 28 对（含跨空间）；ddr 内 21 对」；N-c `ps_app_arena` 加「2B 应用视角」注（与阶段3/5 低 DDR 事实区间重叠属既有事实，与候选区无关）；N-d `capacity.frame_coverage` 改为「逐帧复用同一 region（单帧独占，非并发容量）」。
- **修复过程由 fail-closed 流程捕获 2 个真实缺陷**：① 日志变量名冲突致首轮 tmp 日志缺失（检查器已运行、result JSON 有效）；② 契约内 `stage4_address_map` 绑定漏改（自检 25/1 FAIL、口径复测 exit 1）⇒ 修正后全绿。中间批次 RunId 保留不覆盖。
- **复审修复批次清单**：`report/evidence/S4-CTRL/t21_optionA_landing_20261024_r02/landing_manifest.json`（含 `bound_trees.json` 与漂移断言结果）。
- **005 回执状态**：`dsh_mailbox/DSH-20261024-005-2b-address-confirm-raw-region.md` 已发出；`codex_mailbox/` 截至本轮无 `CDX-20261024-*` 回执（2B 部分已由其冻结件自证，回执用于留档）。
- **等待中 / 下一步**：**独立复审（固定提交 + 被审 SHA）通过前 region 不得标 FROZEN**；硬件窗口实测（CPU1 保持停止、无其他 DDR consumer、板上未占用、cache 可见性）完成前 **`ENABLE=0`、不访问候选区、不装载位流**；阶段4 板级窗口仍依 `CDX-20261023-019` 暂缓，需 lead 签 OFFER。
- **待排期改进项**：`handoff_check.py` 祖先/successor 语义（须连同 38 个单测与证据包一起改并重审）——本轮不展开。

## 必须保持的接口与边界（承接）

- 2B 正式冻结 `07c3d3958578b9cc9d3b8eae3758711fe08724c2`：1000 连续任务、108 ACK 闭环样本；109 黄金 ≠ 109 ACK 闭环。
- UART 方案 B：`s2bu/1.1` 正文不变、扩展关闭；时间/丢帧/过期/状态只记 PS 侧（`(session_id, frame_id, result_seq)` 唯一映射）。
- 候选上限 12675 可行、12676 硬错误；4096 禁用；注入须位于被验收预处理前；`capture_time_available=false`、`capture_time_ns=0` 哨兵，`injection_start_ns` 不得冒充采集时间。
- 保护旧已冻结离线链与全部旧 RunId：`s4_ps_decode.*`、`s4_uart_protocol.*`、`s4_offline_host.c`、`run_s4b_offline_chain.py`、`build_s4b_manifest.py`、`test_s4_ps_decode.py`；不得改写 `d4f30e3`/`d13610d` 的历史提交与证据。
- 2B/阶段3/阶段5/阶段6 工作树与厂商原件只读；本树一次只跑一个重型任务；不 push。
- **换行/字节口径前提（2026-10-24 更正）**：本树**存在 `.gitattributes`**（根 + 嵌套 `docs/stage4/`、`report/evidence/`、`scripts/stage4_s4ctrl/`、`scripts/stage4_s4b/`、`verification/`），其 `-text` **覆盖** w4 的 `docs/stage4/**` 与 `report/evidence/**`（`check-attr text: unset`），故这些文件 disk==blob；**未覆盖**跨树引用（dbdf `report/evidence/S3-T05/**` 为 `text: unspecified` ⇒ 我此前“本树无 .gitattributes”的陈述**有误，以本条为准**）。**不再新增覆盖**（lead 决定，与阶段3 同口径）；契约将新增顶层**绑定字节口径声明**（记录工作树磁盘字节 SHA；跨换行环境复算须 `-c core.autocrlf=false` 或用 blob 口径），并按 N-1 把 dbdf 两项改绑为 blob 内容口径。

## 历史交接行（11 字段，2026-10-25 23:03 UTC+8；保留历史快照）

任务=`BGR888 输入契约 r06 修订与 fail-closed 证据` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`2c1dcd6e81efdfd9d4ed6f70b5d1af9016b985de` | 允许修改范围=`docs/stage4/ 契约/registry/readiness/地址/计划、scripts/stage4_s4b/、scripts/stage4_s4ctrl/、verification/ 两项定向测试、report/evidence/S4-CTRL/s4_bgr888_contract_20261025_r01/**、report/evidence/S4-CTRL/s4_t21_manifest_immutability_20261025_r01/**、.codex/STATE.md` | 未提交改动归属=`本轮 17 个 tracked 文件（含 .codex/STATE.md）与两个新 RunId evidence 已提交于 33988ed；旧 12 项 ELF/MAP 未跟踪文件未动` | 让出声明=`Developer 已停写；runtime 路径只读审计结束；独立 Reviewer PASS（S4-20261025 历史清单不可变修复）；未操作硬件` | 心跳(UTC+8)=`2026-10-25 23:03` | 证据入口=`report/evidence/S4-CTRL/s4_bgr888_contract_20261025_r01/delivery_manifest.json；report/evidence/S4-CTRL/s4_t21_manifest_immutability_20261025_r01/delivery_manifest.json` | 恢复命令=`git -C D:/codex-worktrees/w4 rev-parse HEAD; git -C D:/codex-worktrees/w4 status --short` | 状态/下一接手方=`IN_PROGRESS（r06 独立复审 PASS，runtime NOT_IMPLEMENTED，RAW G0 CHANGES_REQUIRED_NOT_CLOSED；注入集成用例 11/12 且剩余用例为 sandbox BLOCKED）/ 下一步=阶段5消费侧改绑并解决未闭合接口/集成依赖`

## 历史交接行（task-21，2026-10-25 05:31 UTC+8）

任务=`task-21 RAW registry 重复事实修复（R4-03 PASS；跨树窗口仍失效）` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`06c9ab83e4215b6ea5ec9fd827b59549e425a285` | 允许修改范围=`docs/stage4/S4B_raw_system_g0_gap_registry.json、scripts/stage4_s4b/audit_raw_system_g0_gaps.py、verification/test_s4_raw_g0_registry.py、report/evidence/S4-CTRL/t21_address_binding_fix_20261025_r01/**、.codex/STATE.md` | 未提交改动归属=`本轮 registry/checker/test、修复 RunId 与 STATE 已提交；原有12项 ELF/MAP 保留不动、不入提交` | 让出声明=`Developer 已停写；Reviewer R4-03 PASS；无硬件/Vivado操作` | 心跳(UTC+8)=`2026-10-25 05:31` | 证据入口=`report/evidence/S4-CTRL/t21_address_binding_fix_20261025_r01/delivery_manifest.json` | 恢复命令=`git -C D:/codex-worktrees/w4 log -1 --oneline; git -C D:/codex-worktrees/w4 status --short` | 状态/下一接手方=`IN_PROGRESS（两项P2已关闭；旧跨树窗口FAIL_STABLE_DRIFT 1/5，RAW系统G0/P/4-D/G5仍未过）/ 下一步=等待输入版本稳定后重新建审查窗口；继续task-26离线前置，推理依赖仍BLOCKED`

## 历史交接行（已被上行取代，不再代表写权）

任务=`task-21 阶段4 接续（DSH 认领 w4）：契约改绑真实彩色 + 应用已批准项 + RAW 系统 G0 收口 + 帧周期 P 方案（全离线）` | 负责人=`DSH 阶段4 总控（stage4-lead）` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`f6fa9f0d84274f1a0d03e6f87263fb550ebc6656` | 允许修改范围=`docs/stage4/、scripts/stage4_s4ctrl/、scripts/stage4_s4b/、verification/、report/evidence/S4-CTRL/、.codex/STATE.md`（主目录与其他树、硬件均无授权） | 未提交改动归属=`12 项未跟踪 6 ELF/6 map 属 Codex 本机恢复产物，留原位不入 Git；本轮新文件随本次提交` | 让出声明=`w4 由 DSH 阶段4 总控持有至本轮收尾；硬件使用权未随交接，阶段4 板级依 CDX-20261023-019 暂缓，恢复须另行申请窗口` | 心跳(UTC+8)=`2026-10-24 01:00` | 证据入口=`report/evidence/S4-CTRL/t21_takeover_20261024_r02/、t21_contract_colour_rebind_20261024_r02/、t21_raw_g0_gap_registry_20261024_r03/、t21_frame_period_p_plan_20261024_r01/` | 恢复命令=`git -C D:/codex-worktrees/w4 log --oneline -3; git -C D:/codex-worktrees/w4 status --short; python -B D:/codex-worktrees/w4/scripts/stage4_s4ctrl/verify_shared_io_contract.py` | 状态/下一接手方=`IN_PROGRESS / 本轮收尾后由 DSH 项目总控指派独立复审与后续（含硬件窗口申请）`

## 临时接管交接行（阶段4 4-D bring-up 窗口 #2，2026-10-28；已被下发执行、现收窗）

**窗口结论（一句话）**：R0 记录到上一窗口残留；R1 与两处收尾整区恢复 **diff=0**；S1 三段判定 `NEITHER_STAGE`；**M4-b FAIL**（根因已定位：**PS-PL level shifters 未使能**，PS 访问 `0x43C00000` 被拒，应用卡在 `M4B STEP=1`）；M4-a / M3 复检 / chain-lite `NOT_RUN`。**不主张 G3/G4/G5**；`ENABLE=0` 未碰；未写 QSPI、未改线、未发独立 `stop`、未 push。

任务=`S4-T34 4-D bring-up 窗口#2（临时接管执行；原阶段4 执行体收尾失败）` | 负责人=`stage6-lead4`（**DSH 直接指令接管，非 OFFERED**） | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`5dd2f87bc42460d844746105b02b6727f7c0505b` | 允许修改范围=`本轮仅 report/evidence/S4-T34/bringup_window2_*/** 与 .codex/STATE.md；不改驱动/契约/地址图/构建产物` | 未提交改动归属=`进入时 33 项已声明脏项（比口头记录多 1 项，疑为未跟踪 .pylibs/）**全部原样未清理**；本轮新增 4 个证据目录未提交、归本轮` | 让出声明=`已收窗：hw_server 已停、3121 无 LISTENING（仅 5 个 TIME_WAIT 未清理）、无残留进程、无 index.lock` | 心跳(UTC+8)=`2026-10-28 12:40` | 证据入口=`report/evidence/S4-T34/bringup_window2_20261028_r04/window_close.txt；bringup_window2_restore_20261028_r01/results_restore.json；bringup_window2_diag_20261028_r01/results_diag.json；bringup_window2_order_20261028_r01/results_order.json` | 恢复命令=`git -C D:/codex-worktrees/w4 rev-parse HEAD; git -C D:/codex-worktrees/w4 status --short` | 状态/下一接手方=`窗口#2 结束（M4-b BLOCKED 于 PS-PL level shifters）/ 待 DSH 项目总控裁决后续`

### 窗口#2 关键事实
- 驱动 v3.1 SHA `467506d1…`；**v3.1 缺陷**：`load_elf_ddr()` 引用模块级 `INIT_ELF` 但从未赋值（仅第 480 行引用）⇒ 直接走 `--window` 会在 P2/M4-b 装载阶段抛 `NameError`；本轮以 tmp wrapper 注入等价路径规避，**未改驱动源码**。
- `rst -system -stop` 会清空 PL（`mrd 0x43C00000` 报 `Bitstream is not programmed`）；"先装 PL 再跑 init" 与 "先 init 再装 PL" 两序均报 `Level shifters are not enabled` ⇒ 需 `ps7_post_config`/FSBL 流程使能 PS-PL 电平转换器，才能做任何 PS→PL AXI-Lite 访问（M4-b 的前置）。
- 失败尝试按序保留：r01（IDENT 失败：weights 路径笔误）、r02（`INIT_ELF` NameError，预置已写入后恢复未跑）、r03（import 期 NameError，无产物）、r04（正式窗口）；r05 = 收尾恢复核验（`RESTORE_VERIFIED`，diff=0）。

## 窗口#3 中断记录（2026-10-28；**板卡需物理 POR**）

**当前板卡状态：JTAG/PS 目标不可达，需重新上电（POR）后才能继续。禁止他人在此状态下开窗。**

- 现象链：窗口#3 r04 用 `mrd -force 0x43C00000` 探测**无响应**的 PL 从口 ⇒ AXI 事务超时 ⇒
  自 r05 起 `targets` 报 `DAP (APB AP transaction error, DAP status 0x30000021)`、**Cortex-A9 目标消失**；
  DAP 级 `rst -system` 无效（`Invalid target`）；重启 `hw_server` 后 `targets` 返回空。
- **候选区未恢复（重要）**：r04 的 M4-b 预置已写 `head13 → 0x12000000`、`head26 → 0x12002000`
  （5,070 B / 20,280 B），因目标不可达**无法 dump/恢复**。
  **POR 后第一件事**：停核 + `ps7_init` → 整区 dump → 与 M3 快照 `41907f53…` 比对；
  若 diff≠0 则整区写回并复读至 **diff=0**（现成脚本 `tmp/4/S4-T34/finish_restore.py`，指向新 RunId）。
- 已核验：3121 无 LISTENING、无 `hw_server`/`xsdb` 残留、无 `index.lock`。
- 教训（已进 v3.2.2 离线自检）：经 `cmd /c` 传给 xsdb 的 TCL **不得含 `%`**（被当 `%0` 展开）与
  **`&`**（命令分隔符）；**`mrd -force` 不得用于无响应的 PL 地址**（会锁死 DAP/互联）。
- 驱动 v3.2.2 SHA-256 `8aede15a41510d89cf14b77e8189e1533fd1bcfcdd02f27c81d08ad319ae143c`，
  离线自检 39/39 PASS exit 0（`report/evidence/S4-T34/bringup_driver_v322_20261028_r01/`，**未提交**）。
- 窗口#3 证据：`bringup_window3_20261028_r03/`（电平转换器 PASS、CSR 内存映射报错）、
  `r04/`（`-force` 超时 + 内联断言 `&` 缺陷导致装载 exit=255）、`r05/`（DAP 错误态）、
  `bringup_window3_recover_20261028_r01/`（恢复尝试：A9 未回来）。
- 结论：**M4-b 仍未取得有效判定**；M3/M2 未闭合；不主张 G3/G4/G5。

## 窗口#4 阻断记录（2026-10-28 14:51，**POR 后 DAP 仍不可用**）

- **现象**：Wong 于 14:50 完成物理 POR；窗口 #4 于 14:51:27 开窗，**第一步 W0 即停**。
  `targets -set -filter {name =~ "*Cortex-A9*#0*"}` 报
  `no targets found … available targets: 1 DAP (APB AP transaction error, DAP status 0x30000021), 2 xc7z020`
  ⇒ **DAP 仍处错误态、Cortex-A9 未出现**；紧接着的一次式只读 `targets` 探测（新 hw_server）
  甚至**枚举到 0 个器件**（连 DAP/`xc7z020` 都没有），`probe_result.json` 已存。
- **USB-JTAG 线正常**：OS 层 `USB\VID_0403&PID_6014\210512180081` 状态 OK
  （与 xsdb 的 `JTAG-HS1-210512180081` 一致）⇒ 线在、板端 TAP 未响应。
- **本轮未发生任何真实硬件操作**：所有 xsdb 调用均在 `targets` 处报错，DDR 未读未写；
  候选区因 POR 内容未定义，**恢复尚未完成**（需 A9 恢复后按 M3 快照写回并核验 diff=0）。
- **待人工确认**：板卡电源是否真的断开≥10 s 再上电（电源开关/指示灯/12V 适配器）、USB-JTAG 两端排线、
  BOOT 模式开关；确认后我再做一次只读 `targets`，出现 A9 才继续 W0→W4。
- **工具缺陷（fail-open，待修）**：`xsdb -eval` 在 TCL 报错时**进程退出码仍为 0**
  （例：`W0_write.exit_code.txt=0` 但日志是 `no targets found`）⇒ 现有驱动只判进程码会**假成功**。
  建议 v3.2.4 增加"日志错误文本守卫"（`no targets found` / `while executing` / `Memory read|write error`）。
- 证据：`report/evidence/S4-T34/bringup_window4_20261028_r01/`（`W0_restore_candidate.json`、
  `W0_reset_stop|ps7_init|write|dump*.log`、`window_close.txt`）、
  `report/evidence/S4-T34/bringup_window4_probe_20261028_r01/`（`POR_targets.log`、`probe_result.json`）。
- 结论：**M4-b 仍未取得有效判定**；M3/M2 未闭合；不主张 G3/G4/G5。

## 窗口#4 补记（A/B/C 单会话引导结果，2026-10-28 15:03）

- **A/B/C 全部失败**：A9 目标**可选**（`targets -set -filter {name =~ "*Cortex-A9*#0*"}` 不报错），但 `[state]`、`rst -system -stop`、`mrd` 全部报 `APB AP transaction error, DAP status 0xF0000021`；
  `rst -dap` 返回成功但**清不掉**该 sticky 错误；`rst -por` 在 DAP 与 `xc7z020` 上均报 `por not supported for target`；
  `jtag frequency` 需先 `jtag targets` 选目标，故 B 的降频**未生效**。
- **抖动记录**：三次会话 `targets` 渲染均为空，但 A9 目标对象存在且可选 ⇒ **列表渲染与目标对象不一致**。
- **未发生任何 DDR 读/写**：`mrd` 失败，0 个 dump/bin 文件；候选区仍为 POR 后未定义态、**未恢复**（W0 diff = 不适用）。
- **结论/建议**：需 **物理彻底断电（拔 12V ≥10 s）** 才能清 PS 调试 APB sticky 错误；恢复后按 A 的单会话引导重试。
- 驱动 **v3.2.4** SHA `6eb91f15364e6f5bc93ad19ece0e8c1d199bb5a2fd5f65a3a117ba68df8dc786`，自检 **45/45 PASS exit 0**
  （xsdb 日志错误文本守卫 + `dap_recovered()` 双条件 + 注入自检）。
- 证据：`report/evidence/S4-T34/bringup_window4_dapboot_20261028_r01/`（A/B/C 会话日志、修正后 JSON、`summary_abc.json`）；
  `bringup_driver_v324_20261028_r01/`（自检）。
## 窗口#4 有效结果（2026-10-28 18:17–18:21，RunId `bringup_window4_20261028_r05`）

- **四动作修复被实板证实**：`STEP=1` 由"永远挂住"变为读到 `M4B CSR id=0x53324250 ver=0x00000100`
  ⇒ **缺 `FPGA_RST_CTRL=0` + PS-PL 电平转换器 是 CSR 不可访问的根因**（驱动 v3.2.6 四动作 + 双读回：
  `0xF8000900=15(0xF)`、`0xF8000240=0`）。
- **M4-b 判定仍 FAIL（非 INCONCLUSIVE）**：应用跑完 STEP 0–8 并输出
  `M4B RESULT={"pass":0,"done":2,"diff13":0,"diff26":0,"first13":-1,"first26":-1,"stale":1,"gate":1,
  "ack_idle":0,"epoch":1,"status":3077,"error":5}`；**新阻断在 `STEP=6` 等 PL 完成超时**
  （`status` `0x1102→0x0C05`、`error=5`）。PS→PL 通路已通，问题转向 PL 侧完成信号/预置内容/超时预算。
- **W0 恢复 diff=0**（初始即 `41907f53…`）；**W4 收尾恢复**：初始 diff 25,168 → 写回 → **diff=0**。
- 未做 M4-a（M4-b 非 PASS 即停）；未用 `-force`；未做 JTAG CSR 直探。
- 窗口内 3 次尝试均为**工具缺陷**并已修（v3.2.4 错误文本守卫 → v3.2.5 去双引号 → v3.2.6 去 `!`），
  每次 45/45 离线自检 exit 0；**v3.2.6 SHA `311ef177f28f02923be719fba96e6e17d8b3793b76271f3682e4e288f4b2e855`**。
- 清理：3121 无 LISTENING、无残留、无 `index.lock`。**不主张 G3/G4/G5**；M3/M2 未闭合。
## 窗口#6 结果（2026-10-28 19:10–19:14，RunId `bringup_window6_20261028_r03`）—— **M4-b PASS + M4-a PASS**

- **M4-b PASS（判据未改）**：`pass=1, done=1(DONE_SAFE, status=0xE04), error=0, diff13=0, diff26=0, stale=1, gate=1, ack_idle=1, elapsed_ms=11821, spin=80,833,781`。
- **M4-a PASS**：`M4A OK R … crc=0x19D280B0` 与源一致、`M4A OK F … crc=0xFE55DA7C` 匹配、恢复后 `restored_byte_equal=true`。
- W0 `initial_diff=0 / restore_diff=0`；W1 四动作双读回 `0xF8000900=0xf`、`0xF8000240=0x0`；W4 `initial_diff=25219 → restore_diff=0`；
  清理 3121=0 / 无残留 / 无锁；wrapper exit 0（`results_window6.json` = `WINDOW6_ALL_PASS`）。
- **两处宿主侧修正（应用/ELF/判据未动，ELF 仍 `2404a74e…`）**：
  1) preload 尾部补齐：head13 `5,070→5,072 B` 写 1,268 字（pad 2 B，SHA `ad45b1cc…`）；
  2) M4b-4 前置投毒：两 head 输出区首 64 B 写"参考首字节取反"，使 `stale` 可判定（r02 因干净恢复导致 `stale=0`，按判据判 FAIL 正确）。
- 脚本口径 bug 已修并留痕（`window_close.txt.orig`、`results_window5.json` 保留；另写 `results_window6.json`、`W2_M4b_preload_details.json`）。
- 边界：**M4-b/M4-a 的 PASS 仅覆盖 2B 平台位流上的 4-D PS 侧行为**；不主张 G3/G4/G5；M3/M2 未闭合；`ENABLE=0`、未烧 QSPI、未改线、未 push。
## chain-lite-A + SW 预处理（2026-10-28 20:36–21:30）

- **chain-lite-A PASS**（`bringup_chainlite_a_20261028_r03`）：注入张量 `da26d385…` → PL 网络 → PS 解码/NMS → UART 1 框；
  `CHAIN RESULT pass=1, done=1(DONE_SAFE), error=0, decode_rc=0, count=1, raw=2, ack_idle=1, elapsed_ms=11821`；
  与 r13 冻结参考 8 字段 **abs diff 全 0.0**（容差 1e-9）。ELF `s4d_ps_app_sw0_chainA3.elf` `740815e2…`（登记 r4）。
  过程中修我方两处缺陷：`heads` 传 NULL 被拒、`xil_printf` 不支持浮点（改 IEEE-754 位模式输出）。
- **SW 预处理（离线）**：`vitis/stage4/ps/s4d_sw_preproc.{h,c}` 按**冻结 D2 口径**实现
  （Darknet letterbox + 端点对齐双线性 + `v/255` + 对称量化 1/127 + pad 0.5→64 + CHW）；
  **逐字节对拍 `da26d385…` = BYTE_EXACT_MATCH（diff=0，SHA 完全相同，RGB/BGR 两入口）**；
  设计文档 `docs/stage4/S4D_sw_preprocess_design_20261028_r01.md`；证据 `sw_preproc_pairing_20261028_r01/`。
- **待裁决**：①`s4d_geometry.h`（最近邻 + v-128 + pad0）与冻结 D2 口径**冲突**，未擅自改文件；②源码演进导致
  M4-b 变体重建 SHA 漂移（r3 `2404a74e…` 为冻结产物，按 SHA 引用，不要求可重建同 SHA）。
- chain-lite-B 候选 ELF `s4d_ps_app_sw0_chainB.elf` `fe5bf69d…`（登记 r5），未上板；等 lead 签发窗口。
- 边界：`ENABLE=0`、未烧 QSPI、未改线、未 push、不主张 G3/G4/G5；M3/M2 未闭合。
## chain-lite-B（2026-10-28 21:00–21:05，RunId `bringup_chainlite_b_20261028_r01`）—— **PASS**

- **W2 chainB PASS**：SW 预处理（PS 实现）`tensor_crc32=0x5B183B50`、`bytes=519168`；`done=1(DONE_SAFE)`、`error=0`、
  `decode_rc=0`、`count=1`、`raw=2`、`ack_idle=1`、`elapsed_ms=11821`。
- **W3a**：板上张量 CRC-32 == 离线同一 C 预处理同一 RAW 的 CRC（`0x5B183B50`，519,168 B 全等）。
- **W3b**：框 JSON 与离线参考（同 RAW → 同 C 预处理 → T29 宿主前向 layer 29/36 → 冻结解码）**全字段 abs diff = 0.0**
  （score `0.49468568228974247`、xyxy `[0.22001036858036768, 0.37966094334502554, 0.35691270834270916, 0.4436271183223601]`、order 6930、raw 2）。
- W0 `diff=0`；W1 四动作双读回 `0xa/0x0`、`0xf/0x0`；W4 `initial_diff=918130 → restore_diff=0`；清理 3121=0。
- 窗口内 W3b 参考未就绪曾记 `W3A_PASS_W3B_PENDING`；参考生成后用**已落盘板上 UART** 补做（未重跑），最终 `CHAINLITE_B_PASS`。
- 裁决落实：**D2 权威**写入设计文档顶部，`s4d_geometry.h` 加 `LEGACY_4B_SUPERSEDED_BY_D2` 注释（历史保留）；
  **冻结产物按 SHA 引用**（r3/r4/r5 版本映射已在 `app_elf_registration_r5.json`）。
- 边界：覆盖 **2B 平台位流 + SW 预处理（PS 实现）**；fixture `FIXTURE_GENERATED`（非实拍）；
  不主张 G3/G4/G5；M3/M2 未闭合；`ENABLE=0`、未烧 QSPI、未改线、未 push。
## 长跑（口径 A）离线就绪（2026-10-28 21:20–21:35）—— 待窗口

- 新增 `S4D_LONGRUN_SELFCHECK` 分支：SW 预处理一次 → 循环[读 epoch → START → 等 DONE_SAFE → invalidate → 解码 → ACK]，
  停止：任一轮失败即停 / wall>=1800 s / iter>=160（先到者）；每轮校验 status==0x0E04、error==0、decode_rc==0、
  count==1、raw==2、ack_idle==1、epoch 单调、框逐位与第 1 轮一致。
- 长跑 ELF（新 SHA）：`s4d_ps_app_sw0_longrun.elf` **`f9951d78d3fbbb50d280e0740d2fc3e989fcd85a4ecf9af67427b6ec58177031`**（271,904 B）；
  pl 变体 `570ba45d…`；`nm` 强符号 T；登记 `app_elf_registration_r6.json`。
- 离线自检 `scripts/stage4_s4b/verify_longrun_v1.py`：**7/7 PASS exit 0**（强符号/判据常量/循环与失败即停/汇总字段/ELF 身份）。
- 窗口判据已**事先写死**在 `report/evidence/S4-T34/bringup_longrun_20261028_r01/README.md`（LR-1..LR-9）；
  执行器 `tmp/4/S4-T34/run_longrun.py` 已编译（采集上限 2100 s）。
- 边界：`ENABLE=0`、未烧 QSPI、未改线、未 push、不主张 G3/G4/G5；M3/M2 未闭合。
## 长跑窗口结果（2026-10-28 21:24–22:02，`bringup_longrun_20261028_r01`）—— **FAIL（未达判据）**

- W0 diff=0、W1 四动作双读回 PASS、IDENT PASS、W4 restore_diff=0、清理干净；wrapper exit 1。
- **W2**：预处理 CRC `0x5B183B50` ✓；**完成 40 轮**（每轮 `elapsed_ms=11821`、`status=0x0E04`、`error=0`、
  `epoch_lo=1→40`、`ack_idle=1`），**第 41 轮起静默停止**（最后一次输出 `iter=40, wall_ms=461117`），
  此后至 2100 s 采集上限无任何输出（**无 `LONGRUN FAIL`、无 `LONGRUN RESULT``）。
- 判据：LR-1/LR-2/LR-4/LR-5/LR-9 FAIL（未达 140 轮/1800 s）；LR-8 **真通过**（首轮框 vs 离线参考 abs diff 0.0）；
  LR-3/LR-6/LR-7 为"无 RESULT 可解析"的**空真**，不构成通过（证据内已标注）。
- **诊断判断**：失败为"不可中断操作中静默停住"（最可能 PS 侧 CSR/AXI 无总线超时停等，或硬异常），
  非判据失败；需 **逐轮心跳 + 看门狗**，并**离线核查 2B RTL 的重复 START/ledger/first_selected/visibility 累积位**。
- 未重跑（遵 lead 指示）；运行期未轮询 mrd；无 -force；未写 QSPI；ENABLE 未碰；未改线；未 push。
## 长跑根因 + 仪表化（2026-10-28 22:05–22:20）—— 诊断窗口就绪

- **A 根因**（`report/evidence/S4-T34/longrun_rca_20261028_r01/`）：应用侧**无无界循环**（主循环 160、等 DONE 有 120 s 墙钟、
  读 epoch ≤8、ACK/idle 单次读），且**未装数据中止处理器**；2B RTL 的 `ack_pending` 会否决后续所有 CSR 写（L92/93/109/270），
  ACK 前置不满足即静默 SLVERR（L182-184/L237-240）。**平台先例**：2B T20 postmortem `DFSR=0x1808/DFAR=0x43C00008(写START)/STR e5801000 → 判 SLVERR`，
  与"静默停住"同源。2B 实板只做过忙 START/ACK/重接受，**未记录 ≥40 次连续 START**（模型级 1109 次）。最可能卡点：第 41 轮首次 CSR 写（0x014）。
- **B 仪表化**（新 ELF `s4d_ps_app_sw0_longrunI.elf` = `c822dc0bf85b3068aa2ca9884382af1bf15e5c7ed7a021b19ef3a53d06b897c1`，登记 r7）：
  每轮心跳；每步魔数写 `0x11B00000`（magic/step|iter/DFSR/DFAR/abort，共 5 字，不碰候选区）；`Xil_ExceptionRegisterHandler`
  捕获数据中止；收尾清零魔数区。自检 `verify_longrun_v2.py` **11/11 PASS exit 0**。
- 诊断执行器 `tmp/4/S4-T34/run_diag_longrun.py` 就绪：停住检测（最后心跳后 60 s 收手）→ 普通 `mrd` 读魔数定位 →
  W4 候选区 diff=0 + 魔数区清零 diff=0。等 lead 签诊断窗口（≤20 min）。
- 边界：未重跑原长跑、未改判据；`ENABLE=0`、未烧 QSPI、未改线、未 push；不主张 G3/G4/G5；M3/M2 未闭合。
## 诊断窗口被阻断（2026-10-28 22:17，`bringup_longrun_diag_20261028_r01`）

- **W0 无法执行**：A9 目标枚举不到；`available targets: 1 whole scan chain (DR shift through all zeroes)`；
  `targets`（3 次独立会话）与低层 `jtag targets` **均为空** ⇒ **TAP 不响应**。
- 旁证：USB-JTAG `VID_0403&PID_6014\210512180081` 状态 OK、COM4 在；上一窗口 W4 于 22:02:26 完成且 `restore_diff=0`（当时可达）。
- **未执行** W1/W2/W3 ⇒ **未取得 step_id/iter/DFSR/DFAR，不得据此下长跑根因结论**；结论记 `DIAG_BLOCKED_JTAG_CHAIN`。
- 校验器 fail-closed 生效：`reset_stop_exit=0` 但日志含 `no targets found` ⇒ 判 FAIL（未误判通过）。
- 清理：3121=0、无 hw_server/xsdb/vivado、无 index.lock。
- 待办：请 Wong 检查 12V 供电/指示灯，必要时彻底断电 ≥10 s 重上电；恢复后先做**一次只读枚举**确认，再重开诊断窗口（判据不变）。
## 诊断窗口 r02：主机侧 JTAG 句柄卡住（2026-10-28 22:22，`bringup_longrun_diag_20261028_r02`）

- 枚举重试 3 次（间隔 5 s，逐次留原文）**全空**（`targets` 在 `E_BEGIN/E_END` 间无内容）⇒ `P2_enum_preflight=FAIL`；
  **W1/W2/W3 未执行**，仍无 step_id/iter/DFSR/DFAR。
- 对照探测（全只读）：驱动自起 hw_server（等 10 s 稳定）、Vivado `hw_server.bat`、`xsdb` 自动起 hw_server —— **三种变体均 0 目标**；
  主机无 hw_server/cs_server/vivado/xsdb 进程、3121/3122/3042 无监听；FTDI `VID_0403&PID_6014\210512180081` Status=OK/CM_PROB_NONE/FTDIBUS。
- 判定：**非板卡故障、非"长跑导致 JTAG 失效"**；最一致解释=本机 USB-JTAG（HS1 D2XX）句柄在多次 hw_server 起停后卡住。
- 已请 Wong **拔插 JTAG USB**（板卡不必断电）；恢复后先只读枚举确认，再重跑诊断窗口（判据/停止规则/IDENT 不变）。
- 清理：停自起 hw_server（含 xsdb 自动起的那个）→ 3121=0、无残留、无锁。
- 边界：未改判据、未硬测；禁 `-force`、未做 JTAG CSR 直探；`ENABLE=0`、未烧 QSPI、未改线、未 push；不主张 G3/G4/G5；M3/M2 未闭合。
## errata + 长跑诊断（2026-10-28 23:0x–23:4x）

- **r05 诊断定位**：停住在**第 24 轮 · step=4（等 DONE_SAFE）**；魔数 `0x4c524d47 / 0x00001804`（step4|iter24），
  `DFSR=0 / DFAR=0 / 无中止标记` ⇒ **非数据中止**，更符合"AXI 读不返回 / CSR 相引擎停滞"。三次停住迭代 40/23/24 ⇒ 非确定性。
  采集器曾误报 MAXTIME（`last_rx` 被杂散字节刷新），已按心跳间隔修正结论为 `DIAG_LOCATED_STEP4_ITER24`。
- **errata**（`report/evidence/S4-T34/freeze_errata_20261028_r01/`）：ERRATA.md + ledger_reference.json + naming_map.json
  + supersession.json + manifest.json + delivery_evidence.json；F1–F7 逐条处置；**原文件与冻结文档零修改**；
  `check_manifest_hash_basis --strict` **0**、`check_stage_delivery --mode evidence` **0**（CHECKS_OK）。
- 边界：`ENABLE=0`、未烧 QSPI、未改线、未 push；不主张 G3/G4/G5；M3/M2 未闭合。
## Codex 驳回后的修复（2026-10-29 00:0x–01:4x）

- **A 异常链**：注册移入 `s4d_longrun_selfcheck()` 入口（`Xil_ExceptionInit` + RegisterHandler + noinline/used）；8 字记录区
  `0x11B00000`（magic 0x53344C01/step/done/CSR addr+val/DFSR/DFAR/commit），每次 CSR 访问前写入并 flush+DSB；正常收尾清零。
  nm：handler `t 0x10418c`、longrun `s4d_longrun_selfcheck.isra.0`、`_vector_table T 0x100000`；objdump：两个调用点均在 longrun 内。
  负控（注册移回 chainb）⇒ 检查器 **FAIL**（discriminative=True）✓
- **B S1**：`s1_verdict` 长度前置（INVALID_LENGTH）、`_dump` 三重判定（exit/长度/错误文本）、D2 拆 `d2_keep_pl`（无 rst -system）
  与 `d2_system_reset` 两分支；driver selftest **57/57 PASS exit 0**。
- **C 对比**：旧 `infer.elf a5149989…` vs 新 `longrunK b7a654aa…`：cache/异常指令计数对比 + 源码事务入口对比；
  限制已记（偏移提取不稳、旧源码封装）⇒ 以 r06 的 error_code/last_reject/status 三读作判别。
- 撤回首轮 RCA 的错误推断："2B 未验过 ≥40 次连续 START"；实际同 bit 跑过 1109 RUN。
- 新 ELF `b7a654aa…`（登记 r8）；执行器 v2 已加入"停核→两核 PC/CPSR→记录区→loadhw+三 CSR→才恢复"。