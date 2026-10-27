# 阶段4 · D1=A 四项板级实测执行计划书（S4-T31，2026-10-27 r01）

- 状态：**PREPARED_PENDING_WINDOW**（计划与载荷登记就绪；**未开窗、未接触板卡**）。
- 授权：Wong 原话「准」⇒ `report/evidence/CTRL-DSH-HANDOFF/decisions/window_s4_four_measurements_authorization_20261027_r01.md`（主仓 `c628f60`）；窗口签发：DSH 项目总控。
- 依据：`decisions/stage4_raw_address_d1_optionA_20261027_r01.md` §3（乙）；候选区 **`[0x12000000,0x12C08000)`**（raw_frame 12,582,912 B + raw_meta 32,768 B）。
- 边界：**未获「开窗」指令前不得启动 `hw_server`/`xsdb`、不得装载、不得访问板卡**；不 `ENABLE=1`、不 FROZEN、不烧 QSPI、不改线、不写候选区外地址、不结束他方进程、不 push。

## 0. 窗口总预算（≤45 min，硬上限）

| 阶段 | 预算 | 内容 |
|---|---|---|
| P0 开工核对 | 3 min | 无他方 hw_server/xsdb/Vivado 进程；3121 空闲；COM4 未被占用；四树无 `index.lock` |
| P1 连接与 smoke | 4 min | `xsdb` 连接 3121、列 targets、**Tcl 语法/命令可用性 smoke**（本计划所带脚本未在离线期执行过，见 §6 风险 R5） |
| P2 M1 | 3 min | CPU1 状态 |
| P3 M2 | 4 min | 无其他 DDR consumer |
| P4 M3 | 18 min | 只读快照 → 写-回读 → **恢复原字节 + 逐字校验** |
| P5 M4 | 6 min | cache 维护/可见性（见 §5 的适用性裁决） |
| P6 收尾 | 5 min | 断连、证据落盘、退出码汇总、恢复确认 |
| 余量 | 2 min | 只用于**正常收尾**，不得用于扩大范围 |

**任一阶段超时 3 min 未推进 ⇒ 进入 §7 停止条件。**

## 1. M1 · CPU1 保持停止

- 载荷：**无 ELF**（纯 JTAG 寄存器/目标查询）。
- 命令（窗口内）：
  ```
  set XSDBN="D:\Xilinx\2026.1\Vitis\bin\xsdb.bat"
  %XSDBN% scripts\stage4_s4b\m1_cpu1_state.tcl
  ```
  Tcl 内容：`connect -url tcp:127.0.0.1:3121` → `targets` → 定位 APU（`APU`/`psu_cortexa53_0/1` 或 Zynq `ARM Cortex-A9 MPCore #0/#1`）→ 对 CPU1 目标执行 `state` → 打印 `M1_CPU1_STATE=<value>` → `disconnect` → `exit 0`。
- **判定阈值**：CPU1 目标状态必须为 **`halted`**（或等价“已停止且 PC 未推进”），且**两次采样间隔 ≥2 s 的 PC 不变**。
- 证据：`m1_cpu1_state.log`（原始 stdout）+ `m1_result.json`（`cpu1_state`、两次 PC、时间戳、退出码）。
- 失败即停：CPU1 非 halted ⇒ **M1=FAIL，整窗停止**（不得尝试 halt 它——那是改状态，超出授权）。

## 2. M2 · 无其他 DDR consumer

- 载荷：**无 ELF**；只读寄存器/目标查询。
- 命令：`%XSDBN% scripts\stage4_s4b\m2_consumer_check.tcl`
- Tcl 内容：列 **全部** JTAG targets（断言只有本会话预期的 APU/PL 目标，无第二个调试会话占用）；读 **PCAP 状态**（`mrd` 到 `0xF8007000` 区间内的 PCAP status 字，Zynq-7000 为 `0xF8007000`；**只读**）；打印 device configured 位。
- **判定阈值（三条全过）**：
  1. 无**其他** hw_server 客户端（P0 已核 + `targets` 数量与预期一致）；
  2. **PL 未配置**（PCAP configured=0）⇒ 由构造保证 PL 无 master；**若 PL 已配置**：必须能给出**已登记身份**的位流（否则无法排除 PL master ⇒ **M2=FAIL/BLOCKED，停**）；
  3. CPU1 halted（M1 PASS）且 CPU0 状态记录在案（不要求 halted，但须如实记录，若 CPU0 在跑则说明可能存在其他 consumer ⇒ 需人工判读）。
- 证据：`m2_consumer_check.log` + `m2_result.json`（targets 清单、PCAP status 原始字节、PL configured 位、判定结论）。
- **不适用说明**：DDR 总线级活动（AXI HP 端口计数器）**不可读**——无该测量路径的设计内探针 ⇒ 本项以「PL 未配置 + CPU1 halted + 无第二客户端」**构造性证明**替代，并在证据中显式标注该替代关系（不得表述为“总线上无事务”的直接测量）。

## 3. M3 · 候选区未被占用（写-回读 + 恢复）

- 载荷：**无 ELF**（`mrd`/`mwr` 直接访问 DDR）。
- 范围硬约束：**仅** `[0x12000000,0x12C08000)`，长度 **12,615,680 B**；脚本内置区间断言（任何越界地址 ⇒ 立即 `exit 2`）。
- 步骤：
  1. **只读快照**：`mrd -bin -file snapshot_orig.bin 0x12000000 0x00C08000`（按字长分块；快照 SHA-256 落盘）。**快照完成前不得写入任何字节。**
  2. **写-回读**：对整区写入确定性图案（`0xA5A5A5A5` 填充；每 64 KiB 首字写 `0x5A5A0000 | chunk_index` 以定位块），逐块回读比对；**逐块差异计数**。
  3. **恢复**：`mwr -bin -file snapshot_orig.bin 0x12000000`（同长回写）。
  4. **逐字校验**：再次 `mrd` 整区到 `snapshot_restored.bin`，与 `snapshot_orig.bin` 做**逐字节相等**比较（`fc /b` 与 SHA-256 双判据），并记录**差异字节数必须为 0**。
- **恢复原字节算法（写死）**：
  ```
  baseline = mrd(0x12000000, 12615680)          # 只读，先落盘 snapshot_orig.bin
  write_pattern(range)                           # 仅该区间
  readback = mrd(0x12000000, 12615680)           # 写后回读，判占用
  restore = mwr(0x12000000, baseline)            # 回写原字节
  verify  = mrd(0x12000000, 12615680)
  assert sha256(verify) == sha256(baseline) and diff_bytes(verify, baseline) == 0
  assert range_span == 12615680 and addr_min == 0x12000000 and addr_max_exclusive == 0x12C08000
  ```
- **判定阈值**：写后回读全部等于图案 ⇒ 该区**未被占用**（PASS）；任一块不符 ⇒ **区域被占用（FAIL，但仍是有效测量）**，仍须完成恢复并校验。
- **失败即停**：恢复校验差异 ≠ 0 ⇒ **立即停、保留现场**（不重试写、不再写其他地址），把 `verify` dump 与差异偏移表作为现场证据。
- 证据：`snapshot_orig.bin`、`readback_pattern.bin`（或其分块 SHA 清单）、`snapshot_restored.bin`、`m3_result.json`（两块 SHA、差异字节数、块级差异表、耗时、退出码）。
- **时间风险**：12,615,680 B 经 JTAG 需 4 次整区传输（快照/回读/回写/校验）。P4 开始前先做 **64 KiB 速率探针**并外推：若预计 >18 min，则按 §8 的**分层抽样降级**执行（并如实标 `M3=SAMPLED_PARTIAL`，不得表述为整区通过）。

## 4. M4 · cache 维护与可见性

- **适用性裁决（本计划即定，避免窗口内临时决定）**：
  - **M4-a（cache 维护：flush/invalidate 后 PS 回读与写出可见）**：需 **PS 侧代码**执行 cache 操作。既有载荷 `s4b_ps_tensor_diagnostic.elf`（`bfe88660…`）**是业务诊断程序**（张量/权重绑定），用它会引入业务功能，违反本卡“不加业务功能”要求 ⇒ **不复用**。
  - **M4-b（DMA 可见性：PL/DMA 观察者看到维护后的一致数据）**：需要 **PL 侧 consumer**（DMA master）。在不改设计、不装载 4-D 位流的前提下**不存在该观察者** ⇒ **如实标 `NOT_APPLICABLE`**，理由：无可用的已登记 PL consumer 载荷；改写设计即超出本次授权。
  - 因此：**若最小测量 ELF 未能在离线期构建并登记哈希，则 M4 整体标 `NOT_APPLICABLE`（M4-a 缺载荷 / M4-b 缺观察者）**，并在汇报中明确：**本次窗口不足以闭合 M4**，`ENABLE=1` 前置将因此**不满足**，需另出裁决/另开窗口。
- 若离线期成功构建最小 ELF（见 §9 待办）：M4-a 命令 `%XSDBN% -eval "connect -url tcp:127.0.0.1:3121; targets; dow -file <minimal.elf>; con; ..."`（具体以 ELF 的固定 UART/寄存器协议为准），判定：flush → JTAG 写 → PS 回读一致；invalidate → PL/CPU 读一致。**协议未定前不得写入本计划为可执行命令。**

## 5. 证据格式（统一）

每个 M# 产出：① 原始 stdout/stderr（`*.log`）；② 机器可读 `m#_result.json`（`status`、`exit_code`、时间戳、关键数值、边界断言结果）；③ 原始字节 dump（M3）；④ 载荷与工具身份（§9 registry 的 SHA 引用）；⑤ **真实退出码**写文件（不得手填）。全部落在 `report/evidence/S4-B/s4_ddr_four_measurements_20261027_r01/`。

## 6. 风险自陈

- **R1（M3 写 DDR）**：写候选区属**破坏性操作**。缓解：先只读快照并落盘 + SHA；写前再次确认区间断言；写入图案为确定值；恢复用快照回写并做 SHA+逐字节双判据。残余风险：若窗口内掉电/断连，候选区可能停留在图案态——**但只要快照已落盘且在证据目录，可在下一窗口用同一快照恢复**；因此快照落盘与校验是**不可跳过**的前置。
- **R2（M3 时间）**：12.6 MB × 4 次 JTAG 传输可能逼近预算；缓解：速率探针 + 外推 + 抽样降级（并如实标 PARTIAL）。
- **R3（M2 构造性证明的局限）**：无总线级探针，只能以「PL 未配置 + CPU1 halted + 无第二客户端」构造性排除；**不得**表述为直接测量了 DDR 总线。
- **R4（M4-b 不可测）**：DMA 可见性需 PL consumer ⇒ `NOT_APPLICABLE`，且**导致 ENABLE=1 前置不满足**，须另裁。
- **R5（脚本未离线验证）**：边界禁止开窗前启动 `xsdb` ⇒ 本次随附 Tcl **未在真实 xsdb 上跑过**；缓解：窗口第一步 P1 做 smoke（列 targets + 只读一次），脚本失败即停并按 §7 处理，不现场改脚本。
- **R6（他方进程/资源）**：P0 核对不通过 ⇒ 不开口。
- **R7（身份不符）**：装载前必须逐项比对 §9 registry 的 SHA；不符 ⇒ 停。

## 7. 停止条件（任一命中 ⇒ 立即停、保留现场、不扩大范围）

1. 部署/工具身份与 registry 不符；2. 需写候选区外地址；3. M1 失败（CPU1 非 halted）；4. M2 无法排除 PL master（PL 已配置且无已登记位流身份）；5. **M3 恢复校验差异 ≠ 0**；6. 出现复位/挂死/cache 一致性异常/串口异常；7. 超 45 min 或 DSH 项目总控叫停。
停后动作：不重试写、不改配置、不断他方进程，落盘现场（dump + log + 退出码），汇报 DSH 项目总控。

## 8. M3 抽样降级（仅当速率探针外推 >18 min）

分层抽样：头部 64 KiB、尾部 64 KiB、均匀 32 段各 64 KiB，共 **34×64 KiB = 2,176 KiB**；**仍执行完整快照/恢复**（快照与恢复必须整区，否则无法保证原字节恢复），仅把「写-回读」限定到抽样段。结论必须标 `M3=SAMPLED_PARTIAL`，并写明未覆盖比例（≈82.8% 未写测）。

## 9. 载荷登记（详见 `preparation/payload_registry.json`）

| 载荷 | 用途 | 身份 |
|---|---|---|
| `xsdb`（Vitis 2026.1） | M1–M3 执行工具 | `D:\Xilinx\2026.1\Vitis\bin\xsdb.bat`（版本随 registry 记录） |
| `m1_cpu1_state.tcl` / `m2_consumer_check.tcl` / `m3_candidate_rw.tcl` | M1–M3 | 本提交新增，SHA 见 registry；**未在窗口外执行** |
| `s4b_ps_tensor_diagnostic.elf`（r13） | **不复用**（业务功能） | `bfe88660a7c9b16b4d4360ccf33a7540ee215b7d2ae940408b24bdf83c15ec07` |
| 位流 / XSA | **本轮不装载**（PL 保持未配置，便于 M2 构造性证明） | r13 登记 `555a70c2…` / `ea52da1b…`（仅登记，不使用） |
| 最小测量 ELF（M4-a） | 待定 | **未构建** ⇒ M4 当前标 `NOT_APPLICABLE` |

## 10. 未做 / 待办

1. **M4 最小测量 ELF**：离线构建 + 登记（若决定做）；否则 M4 固定 `NOT_APPLICABLE`（M4-b 恒不可测）。
2. **执行驱动**：`run_s4_ddr_four_measurements.py`（门禁 + 逐项证据 + 退出码）——窗口前必须就绪。
3. **开窗**：等 DSH 项目总控指令；本计划书不构成开窗。
4. 本计划**不构成**任何关口通过；结论不得升级为 G0/G4/G5。