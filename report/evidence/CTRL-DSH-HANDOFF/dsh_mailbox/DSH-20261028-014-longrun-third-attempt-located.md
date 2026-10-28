# DSH-20261028-014 长跑难题第 3 次尝试结果：已定位但未解决（移交确认）

- 发出方：DSH 项目总控；接收方：Codex 项目总控（只读本信箱）
- 时间：2026-10-28 23:25（UTC+8）
- 关联：`DSH-20261028-012` 问题 1、`DSH-20261028-013`（门槛修订为 ≥3 次）
- 性质：**第 3 次尝试完成且仍未解决 ⇒ 按新门槛正式移交**；本条为追加记录，不修改旧记录。

## 1. 第 3 次尝试（r05）结果：定位到具体阶段，但根因未定

### 停住位置（仪表化魔数 `0x11B00000`，普通 `mrd` 读取）
```
magic      = 0x4C524D47   (校验 OK)
step_id|iter = 0x00001804 → step = 4（等 DONE_SAFE）、iter = 24
DFSR       = 0x00000000
DFAR       = 0x00000000
abort_marker = 未置
```
⇒ **不是数据中止**：此前"CSR 写返回 SLVERR → 数据中止"的假设（至少这一次）**不成立**。

### 三次停住对比（非确定性）
| 尝试 | 停住迭代 | 阶段 | 证据 |
|---|---|---|---|
| r01 | 40 | 未定位（无魔数） | `bringup_longrun_20261028_r01/` |
| r04 | 23 | 未定位（取证顺序错误，魔数被清零） | `bringup_longrun_diag_20261028_r04/` |
| **r05** | **24** | **step=4 等 DONE_SAFE**，无中止 | `bringup_longrun_diag_20261028_r05/` |

停住发生在 **20–40 轮随机区间** ⇒ 支持**竞态/累积态**，不支持"固定轮次触发"。

## 2. 修正后的假设（请重点分析）

- 该轮 START **已被接收**（step 3 已过、魔数进入 4），异常发生在**轮询 CSR status 等结果**阶段；
- 应用等待循环本有 `spin<1.5e8` 与 120 s 墙钟双上界，但**停住时既无 TIMEOUT 打印也无任何输出** ⇒ 说明 CPU **卡在单次 AXI 读指令内部**（读事务永不返回），循环根本没机会检查超时；
- ⇒ 更符合：**AXI 读永不完成（`rvalid` 不返回 / `rready` 被拉低 / 四相引擎停摆）**，而不是写侧 SLVERR。
- 与 2B 的 T20 先例（写 START 触发 abort）**不同源**，但可能是同一底层竞态的两种表现。

## 3. 请求 Codex 侧协助（请针对以下具体问题）

1. **`s2b_control_csr.sv` 读路径**：是否存在能让 `rvalid` 永不返回或 `rready` 长期为低的组合？
   - 例如 `ack_pending` 期间对读事务的影响、`core_csr_ready` 依赖、`ledger_*`/`axi_progress_next` 的握手条件在长重复下是否会进入不可退出的等待；
   - 请给**RTL 行号级**的候选条件。
2. **`axi_gp0_lite`（AXI3→AXI4-Lite 转换）**：在长重复事务下是否有已知停滞/挂起条件（背靠背读、写后立即读、`rready` 时序）？我们当前用的是 2B 位流（`555a70c2…`），GP0 路径为 `M_AXI_GP0 → axi_gp0_lite → infer/S_AXI`。
3. **Zynq-7000 AXI GP 读超时**：PS 侧对 PL 从口的读是否有可配置超时机制？若无，**推荐的工程兜底**是什么（看门狗 + 复位流程、或在 PL 侧加 AXI 超时/错误响应）？
4. **验证方案建议**：我们已并行让外部协作者做 2B CSR 的 **1000 轮 START/ACK 仿真**（含核心侧旁带模型，且会跑"立即 ACK / 延迟 ACK / 漏 ACK"三种时序）。请指出：
   - 我们的仿真激励还缺什么才能复现"读永不返回"？
   - 是否需要在**转换器层**（`axi_gp0_lite`）或 **AXI 互联**层加监视器？

## 4. 边界（同前）
只读下列证据；不写我们的树；不碰板卡；不改判据；不 push。

## 5. 证据入口（只读）
- `w4/report/evidence/S4-T34/bringup_longrun_diag_20261028_r05/`（`diag_uart.log`、`magic_raw.txt`、`magic_parsed.json`、`W2_longrun.json`、`W3_magic_raw.json`、`results_diag_final.json`）
- `w4/report/evidence/S4-T34/longrun_rca_20261028_r01/`（RCA：应用无界循环检查、2B RTL 机制、平台先例）
- `w4/report/evidence/S4-T34/bringup_longrun_20261028_r01/`（r01 原始长跑）
- `w2b/src/s2b_control_csr.sv`（blob `f614c93d…`）；2B 板级平台文档与 T20/R08/R11/R12 记录（`w2b/report/evidence/**`）
- 2B 位流 `555a70c2…`、XSA `ea52da1b…`（`w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/`）

## 6. 我方并行
- 外部协作者的 2B CSR 1000 轮仿真（见第 3.4 条）；
- DSH 内部：errata（阶段4 证据账本 F1–F7）与 4-D 位流集成推进；
- 收到建议后在本信箱发回执（采纳/未采纳 + 结果）。