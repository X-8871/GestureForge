# S4-T30 · D1=A 地址落盘复核（2026-10-27 r01）

- 工作树 D:\codex-worktrees\w4（分支 `stage4-infer-prep`）；任务卡 `task-30`；执行方 DSH 阶段4 总控。
- **接管核对**：HEAD `83c9284`；`index.lock` 不存在；无 vivado/xsim/hw_server/xsdb 进程；**25 项未提交改动属原持有方**（不清理/不暂存/不回退/不代提交）。
- **裁决**：`decisions/stage4_raw_address_d1_optionA_20261027_r01.md`（Wong 原话「A」）。

## 重要事实：落盘主体在接管时已存在

`raw_frame`/`raw_meta`、禁区缩减、契约重绑在本卡接管时**已存在于 HEAD `83c9284`**（前序 Workbuddy 轮次完成，且地址图整体已由 Wong 2026-10-27 14:15 批为 `APPROVED`）。
本卡实际新增：① 禁区条目**缩减算术补记**（12,615,680 B = 12,582,912 + 32,768）；② **机械核验器**与实跑证据；③ **提案状态迁移**登记；④ **STATE 写权行**改 DSH + 裁决指针 + 禁止事项。
**未改动**：两 region 的 status 保持提案态（`PROPOSED_STAGE4_OWNED_PENDING_APPROVAL_AND_REVIEW`，非 `FROZEN_STAGE4`）；2B 冻结区间一字未动。

## 机械核验结果（全部真实退出码）

| 检查 | 命令 | 退出码 |
|---|---|---|
| 机械核验 A–G | `python -B scripts/stage4_s4ctrl/verify_d1a_landing.py --run-dir <本目录>` | **0**（7/7） |
| 契约自检 | `python -B scripts/stage4_s4ctrl/verify_shared_io_contract.py --evidence-dir <本目录>/contract_selfcheck` | **0**（27/0） |
| 缺口审计 | `python -B scripts/stage4_s4b/audit_raw_system_g0_gaps.py --evidence-dir <本目录>/gap_audit_r02` | **0**（13/13、17/17） |

- A：8 区域 `base + length_bytes == end_addr_exclusive` 且 hex/整数一致。
- B：8 区域两两 **28 对零重叠**（=C(8,2)；分解：ddr 内 7 个 region 两两 **21 对** + 跨 ddr↔pl_mmio **7 对**）。
- C：共享图与源图 8 区域 `base_addr_hex`/`length_bytes`/`status`/`owner_from_source` **差异 0**。
- D：`raw_frame`/`raw_meta` 与 2B 冻结对象 tensor `[0x10000000,0x1007EC00)`、GF8 `[0x10100000,0x106A12FC)`、feature `[0x11000000,0x11ADADB8)` **不相交**（字面区间 + 图中 region 双路核对）。
- E：存在禁区 `[0x12C08000,0x20000000)`、不存在 `[0x12000000,…)`；缩减量 **12,615,680 B**；**其余 8 条禁区相对基线 `d29ef5f^` 逐条不变**。
- F：两新 region 提案态；共享图 `enable_status=0`；源图 `status=APPROVED` 且有 `approval_history`（事实登记，**不据此提升任何关口**）。
- G：契约 `upstream_bindings.stage4_address_map.sha256` == 当前图 SHA；`post_freeze_rebinds` 有 `to == 该 SHA` 留痕。

## 未做（明确不越界）

1. **板级四项实测**（CPU1 停止 / 无其他 DDR consumer / 候选区未被占用 / cache 可见性）——需授权窗口；
2. **独立复审**——由项目总控另派 Reviewer；
3. **`ENABLE=1` 与 4-D 构建**——须先满足裁决 §3 全部前置；
4. 真实链窗口 W-C（等地址复审 PASS + 实测 + 4-D + P1）。

**边界**：仅写 w4；未动硬件；未 push；`ENABLE=0` 保持；未 FROZEN；本记录**不构成**任何关口（G0/G1/G3/G4/G5）通过。

## 非阻断修订说明（2026-10-27 r02，增量核对用）

- **NB-1 时间戳**：契约 ``post_freeze_rebinds[1].at_utc8`` 与缺口表 ``updated_utc8`` 原先手填 19:50:00 / 19:52:00，**晚于提交时刻 19:46:50**（笔误）。已改为**文件系统真实 mtime**：契约 ``2026-10-27T19:44:56+08:00``、缺口表 ``2026-10-27T19:45:21+08:00``，并新增 ``timestamp_source``/``updated_utc8_source`` 说明来源与被更正值。
- **NB-3 重叠对数**：原写「21 对」，实际核验为 **28 对**（``C(8,2)``；ddr 内 7 region 21 对 + 跨 ddr↔pl_mmio 7 对）。核验器输出 ``pairs: 28`` 未变。
- **NB-4 路径名**：派单卡所列 ``docs/stage4/s4_shared_io_contract.json`` 等为派单笔误（派单方已认）；**实际对象与路径**为：
  ``docs/stage4/s4b_shared_input_result_contract.json``、``docs/stage4/S4B_raw_system_g0_gap_registry.json``、
  ``docs/stage4/S4B_raw_address_ownership_proposal_20261024_r01.md``、``report/evidence/S4-CTRL/s4_d1a_landing_20261027_r01/landing_manifest.json``。
  **OID 与对象身份不变，仅路径名更正**；本清单 ``files[].path`` 已统一为 ``/`` 分隔。
- 本文件为**复审基线的原文更正**；修后复跑证据见 ``s4_d1a_landing_20261027_r02/``。

## hash basis 更正（DELTA 修复 ①，2026-10-27 r02）

- 本包 iles[].sha256 已全部改为 **提交 blob 基座**（git cat-file blob e39f6de:<path>，即被审提交的仓库内容权威），并为每项写入 hash_basis="commit_blob" 与 source_commit。
- 原记录的不符成因：清单曾用 Get-FileHash（工作区字节）生成——文本文件在 core.autocrlf 下为 CRLF、提交 blob 为 LF，且个别项在清单生成后又被同一会话重写（中间值）⇒ 出现 blob/disk/中间值三类偏差。
- 并列复算表见 hash_basis_recompute.json（提交 blob SHA-256 与当前磁盘 SHA-256 并列，磁盘值不参与校验）。
- **r01 = 被审提交 39f6de 的 blob 基座快照；r02 = d5a86bf 承载。**

## manifest schema 归属（如实标注，2026-10-27 r03）

- 本包**不使用** `verification/check_stage_delivery.py` 的 manifest schema（`inputs`/`evidence` 模式）。
  该项检查器对本清单**实跑 exit 2**：报缺 `evidence_dir`/`interfaces`/`limitations`，并含**未知字段**
  `boundary`/`card`/`nb_fixes`/`take_over`/`proposal_migration` —— 因本清单是**任务批次自定义格式**，
  不是交付包装格式。**因此不得**对本包声称 `CHECKS_OK` 或「通过 check_stage_delivery」。
- 本包实际使用的校验：专用校验器 `scripts/stage4_s4ctrl/verify_d1a_landing.py`（机械核验 A–G）、
  `scripts/stage4_s4ctrl/verify_shared_io_contract.py`、`scripts/stage4_s4b/audit_raw_system_g0_gaps.py`，
  以及**新基座门禁** `verification/check_manifest_hash_basis.py`（主仓）。
- 若后续确需 `check_stage_delivery` 包装，将**另补**一份 schema 合规的 `delivery_manifest.json`（不复用本文件）。
