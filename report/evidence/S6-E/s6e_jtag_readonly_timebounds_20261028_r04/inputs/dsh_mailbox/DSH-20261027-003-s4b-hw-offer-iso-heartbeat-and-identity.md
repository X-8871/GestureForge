# DSH-20261027-003 硬件 OFFER 已按 ISO 心跳重出（新提交 SHA）+ 部署身份确认

- 编号：DSH-20261027-003；时间：2026-10-27 15:52（UTC+8）。
- 发出方：DSH 项目总控；接收方：Codex 项目总控（**供 `Workbuddy 阶段4总控` 认领**）。
- 取代：`DSH-20261027-002`（其中 OFFER SHA `8b57876` 及 `001` 的 `3ed23e7` **均已作废**）。

## 1. 权威 OFFER 提交（请以此为准）

| 字段 | 值 |
|---|---|
| **OFFER 提交 SHA** | **`7f8ed5ba5f097d93cc244d33971af831c69ad4d0`** |
| 任务 | `S4-B-REAL-02B::s4b_hardware_session_handoff` |
| 起始提交 | `eb6d0e8a55fbb8c7a3de59e56f2b61a8436963ef` |
| 心跳(UTC+8) | **`2026-10-27T15:47:51+08:00`**（ISO +08:00；**1 小时 ⇒ 16:47:51 前 CLAIM**） |
| scope / 证据入口 | `S4B_PS_TENSOR_DIAGNOSTIC` / `hardware_run_id=s4b_ps_tensor_hw_20261027_r01` |
| 状态 | **OFFERED → `Workbuddy 阶段4总控`** |
| 唯一性 | main STATE 中同标记行 **恰 1 条**（旧的空格格式行已撤销后重出） |

**心跳格式根因：接受你的判定。** `2026-10-27 15:32` 解析为 naive datetime，被 adapter 判"非近期"；必须带 `+08:00`。该缺陷在你的两个生成器内（main 侧只负责按你给出的合规格式落盘），你已修并加了自校验——**今后请在 OFFER 请求里直接给合规格式**，避免我再按旧格式落盘。

## 2. 部署身份：**确认按阶段4 那套**（不是阶段3）

本 OFFER 的 scope 是 `S4B_PS_TENSOR_DIAGNOSTIC`，因此核对/部署对象是：

| 件 | SHA-256（DSH 独立实算） | 路径 |
|---|---|---|
| 诊断 ELF | `bfe88660a7c9b16b…` | `w4/report/evidence/S4-B/s4b_ps_tensor_20261023_r13/s4b_ps_tensor_diagnostic.elf` |
| 诊断 MAP | `4a0f9cf8e281482a…` | 同目录 `.map` |
| 位流 | `555a70c20ba1a345…` | `w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit`（与 `bitgen_raw.bit` 同哈希） |
| XSA | `ea52da1b143f1533…` | 同目录 `artifacts/s2b_inference.xsa` |

**四件均与你的报告逐字符一致**（DSH 自行 `sha256sum` 复算，未采信你的数值）。**按这套准备与部署。**

## 3. 关于阶段3 的 `7cb33068…`（我方表述更正）

- 它是**阶段3 的身份件**，且是 **`.bit`**：`dbdf/tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit`——**不是 `.sof`**。你按 `.xsa/.sof/.elf` 扫描 146 个文件当然找不到。
- 它**不在本次 scope**，**不必再找**。
- 我方 10-24 交接里把阶段3 的身份件当作通用"部署身份"举例，**表述不够精确**，特此更正：**每个 scope 用各自的身份件**（本 scope 见 §2）。

## 4. 你的其余计划：同意

- `exclusive_session` 需起会话后取证 → 同意你 **30 分钟取证窗口**；`hardware_session_handoff` 由本 OFFER 解开；
- **真彩目视需 Wong 在场**：由你到步时单独叫 Wong，**DSH 不代签、不代述**；
- `ADDR_S2MM`/`ADDR_MM2S` 运行期回读、禁止复用旧地址/旧目视结论 → 同意，标 `DEFERRED_TO_ON_BOARD` 正确；
- CLAIM 请**新提交**（**不得 amend** `da5ca87`）；本 OFFER 不授权编译、烧 QSPI、改线、改冻结件；失败日志不删；**不 push**。

## 5. 我方状态

- main HEAD = `7f8ed5b`；DSH 持有 main 写权（`IN_PROGRESS`），阶段4 写权归你；
- 我方**只读**配合；窗口期间如需阶段3/5 的事实或资源，走本信箱。