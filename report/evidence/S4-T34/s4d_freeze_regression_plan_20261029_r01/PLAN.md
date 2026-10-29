# 阶段4/5 冻结回归清单（2026-10-29 r01）

- 目的：为 **G3（实物验证）→ G4（任务验收）** 提供一次可复现、可核对的完整回归；**本清单尚未执行**
- 输入基线：`FROZEN_INPUTS.json`（19 项，`gen_frozen_inputs.py` 生成，fail-closed）
- 执行器：`run_freeze_regression.py`（串行 7 个窗口；任一项 FAIL 立即停并保留现场）
- 边界：`ENABLE=0`、不写 QSPI、不改线、不 push；`rst -system` 在 PL 编程后**绝对禁止**

## 0. 开跑前置（三项全过才允许开板）

1. `python -B gen_frozen_inputs.py --check` → 退出码 **0**（19 项 sha 全对）
2. 板卡空闲：`Get-Process hw_server,xsdb,vivado` 计数 = 0；3121 无 LISTENING
3. 板卡状态干净：上一次窗口若发生过 DAP 粘连，必须先整机断电（12V+USB ≥10 s）并只读枚举确认 A9 两核可枚举

## 1. 冻结候选（本次回归的对象）

| 类别 | 对象 | 身份 |
|---|---|---|
| 合并计算体位流（部署候选） | **P2d** | bit `58c66cdb…1a86a3` / XSA `4ebc631e…26a3ab`，50 MHz，WNS +0.128 |
| 参考平台位流（链路基准） | 2B 基线 | bit `555a70c2…` |
| 应用 ELF | M4-b 收口 / M4-b 重建 / chainA / chainB / P2c-DMA | 见 `FROZEN_INPUTS.json` |
| 数据 | fixture RAW / weights GF8 / bridge input / head13(原始+padded) / head26 / M3 快照 | 见 `FROZEN_INPUTS.json` |
| 驱动 | `run_bringup_driver.py` v3.2.7（`6c41ff4c…`）、`run_window_b_driver.py` | 见 `FROZEN_INPUTS.json` |

**不作冻结**：P2c r02（被 P2d 取代，仅作历史）、P2b/P2a 位流（拓扑已被证伪）、任何 `ENABLE=1` 配置。

## 2. 回归矩阵（7 个窗口，预计 ~45–55 min）

| # | 平台 | 项 | 判据 | 预计 |
|---|---|---|---|---|
| R1 | 2B 基线 | M3 只读复检 + M4-a | M3：12,615,680 B dump 与 `m3_snapshot` **逐字节相等**；M4-a：R/F 应答与 CRC 全对、恢复逐字节相等 | 4 min |
| R2 | 2B 基线 | M4-b 收口 | `pass=1`、`diff13=0`、`diff26=0`、`stale=1`、`gate=1`、`ack_idle=1`、`error=0`、`elapsed_ms≈47287`；`TAIL13 lane01_ok=1 lane23_ok=1` | 6 min |
| R3 | 2B 基线 | chain-lite A | `pass=1`、`decode_rc=0`、`count=1`、`ack_idle=1`、参考逐字段一致（abs≤1e-9） | 5 min |
| R4 | 2B 基线 | chain-lite B | `pass=1`、`tensor_crc32=0x5B183B50`、8 字段 match | 5 min |
| R5 | P2d | 2B 单帧性能 | `done=1`、`error=0`、`elapsed_ms=47000–48000`（回归"慢 2×"不复发） | 6 min |
| R6 | P2d | chain-lite A | `pass=1`、参考一致 | 6 min |
| R7 | P2d | preproc→DMA(HP1) 数据面 | `tensor_crc32=0x5B183B50`、`length_reg=519168`、`pass=1` | 6 min |

（可选加测 R8 = P2d M4-b 收口，若时间允许；已单独验证过 `s4d_m4b_close_p2d_20261029_r02`。）

## 3. 判据口径（写死，不许现场改）

- **A 项长跑**：不纳入本次回归（已由 `bringup_longrun_probe_20261029_r05` 按真实 30 min 口径完成；重跑需 ~40 min，若 G4 要求可加做）。
- **M2**：不重跑；以 `s4d_m2_erratum_20261029_r01` 的勘误基座（`INT_STS[2]`）为准。
- **M3 成对取样**：**不在本清单**（依赖 Codex 的 DDR 读取工具，属外部依赖；已发 `DSH-20261029-007` 请求）。G4 若要闭合 M3，需等对方回复。
- 每项必须留证据到 `report/evidence/S4-T34/<RunId>/` 且 manifest 过 `check_manifest_hash_basis.py --mode strict`（exit 0）。

## 4. 停止条件（任一触发即停，不重试）

1. 任一项结论非 PASS；
2. `APB AP transaction error` / DAP `0x30000021` / 60 s 无 UART；
3. 冻结输入 sha 与 `FROZEN_INPUTS.json` 不符；
4. 出现 `rst -system` 于 PL 编程之后（视为流程违规，立即停并记录）。

发生 2 或 4 时：**整机断电**后重来，并在证据里记 `INVALID_RUN`（不覆盖旧记录）。

## 5. 产物与提交（回归执行者）

1. 每窗口证据目录 + manifest（`hash_basis=commit_blob`，仓库相对路径）；
2. 汇总 `FREEZE_REGRESSION_REPORT.md`：7 项一行一条（RunId / 结论 / 关键数字 / 退出码）；
3. 提交只含本轮证据与 STATE；不混入旧会话脏项；
4. 冻结结论：只有 7 项全 PASS 且输入 sha 未变，才可提出"阶段4/5 可进 G4"。

## 6. 已知风险与缓解

| 风险 | 缓解 |
|---|---|
| DAP 粘连（编程 PL 后系统复位类） | 执行器全程禁用 `rst -system`；装载统一走 `drv.load_elf_ddr`（PL 保持分支） |
| 50 MHz 下单帧 47.3 s 超过窗口 | 所有结果窗 ≥150 s；M4-b/chain 等待窗按 150 s |
| 2B 超时常量回退 | ELF 冻结哈希校验；`core_timeout` 必须 0xFFFFFFFF |
| head13 参考漏写尾 2 字节 | R2 固定用 padded 参考（1268 字）+ 投毒强制 `stale=1` |
| 时序/资源漂移 | 位流只认 `58c66cdb…`；任何改动即作废本清单 |
| 外部依赖（M3/吞吐） | 已在 STATE 标记 `EXTERNAL_DEPENDENCY`；不阻塞 G3 其余项 |