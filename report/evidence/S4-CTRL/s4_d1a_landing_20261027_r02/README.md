# S4-T30 · 4 项非阻断修复复核（2026-10-27 r02）

- 被审基线：`e39f6de6f83fc06783ee9b97e86afabef0170e89`（复审 **PASS**，0 阻断 / 4 非阻断；报告归档主仓 `report/evidence/CTRL-DSH-HANDOFF/reviews/S4_T30_20261027_r01/`，main 提交 `c5d6928`）。
- 本 RunId 只做**非阻断修复复核**，不改任何被审语义（地址/长度/owner/状态词/契约版本均未变）。

## 修复项

| 项 | 问题 | 处置 |
|---|---|---|
| **NB-1** | 契约 `post_freeze_rebinds[1].at_utc8`=19:50:00、缺口表 `updated_utc8`=19:52:00 **晚于提交 19:46:50** | 改用**文件系统真实 mtime**：契约 `19:44:56`、缺口表 `19:45:21`（均 ≤ 提交时刻）；新增 `timestamp_source`/`updated_utc8_source` 说明来源与被更正值，成因如实记为「手填时间戳笔误」 |
| **NB-2** | 顶部写权行已改 DSH，但 **11 字段交接行**仍 `负责人=Workbuddy`/`CLAIMED`/心跳 16:51:46 | 交接行改为 **DSH 接管**；如实写明本次接管依据是 **Wong 直接指令、原持有方无书面 OFFERED 行**；心跳取真实时刻 |
| **NB-3** | 证据写「21 对零重叠」，核验实际 **28 对** | 改为 **28 对**并注明分解：`C(8,2)=28`，其中 **ddr 内 7 region 两两 21 对** + **跨 ddr↔pl_mmio 7 对**；核验器输出 `pairs=28` 未变 |
| **NB-4** | 派单卡路径名不存在（`docs/stage4/s4_shared_io_contract.json` 等） | 证据写入**真实路径**并统一 `/` 分隔：`docs/stage4/s4b_shared_input_result_contract.json`、`docs/stage4/S4B_raw_system_g0_gap_registry.json`、`docs/stage4/S4B_raw_address_ownership_proposal_20261024_r01.md`、`report/evidence/S4-CTRL/s4_d1a_landing_20261027_r01/landing_manifest.json`。**OID 与对象身份不变，仅路径名更正** |

## 连带一致化（必需）

NB-1 改动契约字节 ⇒ 缺口表 `basis_bindings[shared_input_contract]` 必须重绑，否则缺口审计会 FAIL：
`4d8dc0d4…` → `25bc30d5…`（本 RunId 已记录，复跑审计 PASS）。

## 复跑结果（真实退出码）

| 检查 | 退出码 |
|---|---|
| 机械核验 A–G | **0**（7/7） |
| 契约自检 | **0**（27/0） |
| 缺口审计 | **0**（13/13） |

**未做**：板级四项实测、`ENABLE=1`/4-D、真实链 W-C。**边界**：仅写 w4；`ENABLE=0`；未 FROZEN；无板级访问；未 push；原持有方 **25 项**未提交改动未清理未暂存未代提交。
