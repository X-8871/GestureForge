# S4-T30 独立复审报告（D1=A 落盘）

- 被审提交：**`e39f6de6f83fc06783ee9b97e86afabef0170e89`**（父 `83c9284ad2296b9b2c836250cee615e255533615`；分支 `stage4-infer-prep`；作者/提交者时间 `2026-10-27T19:46:50+08:00`）
- 复审方：DSH 阶段3 总控（独立 Reviewer，**只读**）；时间：2026-10-27（UTC+8）
- 复审工作区：`D:\tmp\review\S4_T30_20261027_r01`（**仓库外**）；**未写 w4**：前后快照 `status` sha256 `784eef0a…`、`index` sha256 `1e9a8729…`、HEAD 全部**逐字节不变**
- 未运行任何会写仓库的命令（无 `fsck --lost-found`/`gc`/仓内 clone）；未动硬件

## 结论：**PASS**（0 阻断 / 4 非阻断）

四条必答：①**可**作为 D1=A 落地交付（非阻断修完/登记后）；②"接管前已存在"披露**属实**，未把前序成果记成本轮成果；
③**无**任何关口/`ENABLE`/冻结被不当推进；④证据**可复现**（三项检查器本地实跑逐项一致）。

## 1. 基线与范围（全部实跑）

| 项 | 命令 | 真实退出码/结果 |
|---|---|---|
| 提交存在且为 commit | `git cat-file -t e39f6de6f83fc06783ee9b97e86afabef0170e89` | 0 / `commit` |
| 父提交 | `git rev-parse e39f6de6f83fc06783ee9b97e86afabef0170e89^` | 0 / `83c9284ad2296b9b2c836250cee615e255533615`（与自报一致） |
| 21 文件是否全在授权范围 | `git diff-tree -r --name-only e39f6de6f83fc06783ee9b97e86afabef0170e89` | **21 文件，越界 0**（`docs/stage4/`、`scripts/stage4_s4ctrl/`、`report/evidence/S4-CTRL/`、`.codex/STATE.md`） |
| `index.lock` | `git rev-parse --git-path index.lock` + 存在性 | 路径解析成功，**文件不存在** |
| 工作树 | `git status --short` | **25 项**未提交/未跟踪（22 项在 `report/evidence/S4-B/**`，余为 `.pylibs/` 等），与提交清单**交集为空** ⇒ **未卷进提交** |
| 未 push | `@{u}` / `rev-list HEAD --not --remotes` | 无 upstream；433 个提交未推送 ⇒ **未 push** 属实 |

## 2. 自报 blob 复核（逐个 `git rev-parse` + 字节 SHA-256）

| 角色 | 提交内实际路径 | OID（实际） | 自报前缀 | 匹配 | 字节 SHA-256 |
|---|---|---|---|---|---|
| 地址图 | `docs/stage4/S4B_stage4_address_map.json` | `e6e83448fa0a…` | `e6e83448` | ✅ | `7c20ac89a35e66c9dc4559fd66a7c9be8150d1bb532e59cf27036d12b9ead29e`（与自报 `7c20ac89…` 一致） |
| 契约 | `docs/stage4/s4b_shared_input_result_contract.json` | `18f2862af32f…` | `18f2862a` | ✅ | `4d8dc0d4b2c5cf65…`（与自报 `4d8dc0d4…` 一致） |
| 缺口表 | `docs/stage4/S4B_raw_system_g0_gap_registry.json` | `1c0b74e6c136…` | `1c0b74e6` | ✅ | `acddf072fae147b1…` |
| 提案 | `docs/stage4/S4B_raw_address_ownership_proposal_20261024_r01.md` | `2c40d832d714…` | `2c40d832` | ✅ | `1e6550d5e3b6c9ac…` |
| STATE | `.codex/STATE.md` | `d558e0a2e508…` | `d558e0a2` | ✅ | `61e015a06dbabd5e…` |
| 核验器 | `scripts/stage4_s4ctrl/verify_d1a_landing.py` | `b1b80c04307a…` | `b1b80c04` | ✅ | `986040d6f1f1488a…` |
| 证据清单 | `report/evidence/S4-CTRL/s4_d1a_landing_20261027_r01/landing_manifest.json` | `c5db9dae7468…` | `c5db9dae` | ✅ | `eb95f8c286ff095a…` |

**7/7 OID 前缀一致**。**非阻断 NB-4**：派单给出的 4 个路径名与提交内实际文件名不同（OID 指向同一对象），见 §7。

## 3. "接管前已存在"真伪（结论：**属实**）

- `git show 83c9284ad2296b9b2c836250cee615e255533615:docs/stage4/S4B_stage4_address_map.json`：**raw_frame / raw_meta 均存在**；`status=APPROVED`、`approved_by=Wong`、
  `approved_at_utc8=2026-10-27T14:15:07+08:00`、`approval_scope_note`（**"不解除 ENABLE=0，不替代其余七类硬件门禁"**）；
  `gaps` 已为 **9 条**且该条 `base=0x12C08000`、`end=0x20000000` ⇒ **缩减在接管前已完成**。
- `git diff 83c9284ad2296b9b2c836250cee615e255533615..e39f6de6f83fc06783ee9b97e86afabef0170e89 -- docs/stage4/S4B_stage4_address_map.json`：**仅 `gaps[6].shrink_note` 一个字段变化**（基址/长度/状态/批准字段全不变）。
- 契约父/子对比：**语义字段差异 = 0**（`contract_version=1.3.0`、`status=FROZEN_OFFLINE_ONLY`、`revision=r07` 均未变），
  变化仅 `upstream_bindings.stage4_address_map.sha256` + `post_freeze_rebinds`（1→2 条）+ `updated_utc8`/`revision_note`。
- **缩减由谁引入**：`d29ef5f^` 该条 `base=0x12000000` → `d29ef5f` `base=0x12C08000` ⇒ **缩减发生在 `d29ef5f`（前序轮次）**，非本卡。
- 结论：本卡实际新增 = ①缩量算术补记 ②核验器+实跑证据 ③提案状态迁移 ④STATE 写权行 —— 与自报**逐项一致**，**无冒领前序成果**。

## 4. 地址算术（我独立复算，不看其结论）

- **8 个顶层 region**：`base_addr + length_bytes == end_addr_exclusive` **8/8**；hex 与整数一致。
- **两两不相交**：C(8,2)=**28 对**（同一 address_space 21 对 + 跨空间 7 对）⇒ **重叠 0**。
- **与 2B 三冻结区间**：`network_input_tensor`/`gf8_weight_package`/`feature_envelope` **就是**那三个 2B 冻结对象（同 base/end，属**身份**非冲突）；
  **阶段4 新增候选**（`injection_frame_rgb` `[0x10700000,0x10B00000)`、`raw_frame` `[0x12000000,0x12C00000)`、`raw_meta` `[0x12C00000,0x12C08000)`）与三区间**全部不相交（0 命中）**。
- `raw_frame`=12,582,912 B、`raw_meta`=32,768 B；缩量 `12,615,680 = 12,582,912 + 32,768` ✅（文本含千分位数字，逐项核对通过）。

## 5. 禁区缩减 / 契约 / 缺口表 / 提案 / 状态纪律

| 项 | 结果 |
|---|---|
| 缩减精确性 | `gaps[6]`：`0x12C08000 → 0x20000000`，`length=222,265,344` 与跨度一致；**其余 8 条逐条未变**（父子仅 `shrink_note` 变化）；基线 `d29ef5f^` 独立复核为 `0x12000000` ✅ |
| 契约绑定 | `upstream_bindings[id=stage4_address_map].sha256 = 7c20ac89…` **等于地址图实际字节 SHA** ✅；rebind 链 `from=c0855078…`（父文件实测 SHA）→`to=7c20ac89…` **闭合** ✅；2 条 rebind 的 `semantics_changed=false` 有依据（语义字段 diff=0）✅ |
| 版本/冻结态 | 契约 `1.3.0`/`FROZEN_OFFLINE_ONLY`/`r07` **父=子未变** ⇒ 未擅自升级 ✅ |
| 缺口表 | 20 条；**G-01=PARTIALLY_CLOSED_OFFLINE、G-02=PARTIALLY_CLOSED_OFFLINE**（未被静默转批准）✅；`source_checkpoint=d4f30e3`（未完成 RAW G0 检查点） |
| 提案状态 | `DECIDED_PENDING_G0_REVIEW` ✅（`DECISION_REQUESTED`→该态），且明写"本卡不构成任何关口通过"；两 region 仍 `PROPOSED_STAGE4_OWNED_PENDING_APPROVAL_AND_REVIEW`（**非** `FROZEN_STAGE4`）✅ |
| 禁用断言扫描 | 命中 3 处**全为否定/条件式**（"物理基址 enable=1 **之前保持** ENABLE=0"×2；"**未冻结**（FROZEN 仍须硬件实测 + G0 批准）"×1）⇒ **无**"G0 已通过/已批准/ENABLE=1/已冻结"式断言 ✅ |

## 6. 证据可复现（我在隔离输出目录实跑；w4 只读）

| 检查器 | 我的命令（要点） | 真实退出码 | 结果 | 与提交内结果比对 |
|---|---|---|---|---|
| `verify_d1a_landing.py` | `--run-dir <空目录>` | **0** | A–G **7/7 PASS** | `mechanical_checks.json`：status/checks/failures **SAME** |
| `verify_shared_io_contract.py` | `--evidence-dir <空目录>` | **0** | **27 通过 / 0 失败** | status/failures/passes **SAME** |
| `audit_raw_system_g0_gaps.py` | `--evidence-dir <空目录>` | **0** | **17/17 + 13/13 + 3/3** | status/checks/failures/passes **SAME** |

- 首轮 FAIL **保留未覆盖**：`gap_audit.exit_code.txt = exit=1`，其 stdout 明确记录 2 项 `basis_hash_match` 不一致（address_map/contract 旧 SHA）；`gap_audit_r02 = exit=0`。
- `mechanical_checks.json` 的 `D_disjoint_from_2b_frozen_objects` 明细含逐 (new_region, frozen_object) 的 `hit_literal/hit_map_region`（全 false）✅。
- `review_binding` 指向的批准复审记录 `report/evidence/S4-B/s4b_address_approval_review_20261027_r01/approval_review.json` **已在提交内**且字节 SHA `c15dec98…` 与绑定一致 ✅。

## 7. 非阻断（4 项，须登记/更正；不影响上述 PASS 依据）

| ID | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| **NB-1** | `s4b_shared_input_result_contract.json` `post_freeze_rebinds[1].at_utc8=19:50:00`；`S4B_raw_system_g0_gap_registry.json` `updated_utc8=19:52:00` | 文档内时间戳**晚于**该提交的 author/committer 时间 `19:46:50` | 证据时间线自洽性；不影响技术内容 | 我的实测：`git log -1 --format=%aI/%cI` vs 文件内容 | 说明成因（是否固定日期提交/提交后重写），把受影响时间戳改为真实值或明确标注取值来源 |
| **NB-2** | `.codex/STATE.md` 顶部写权行 vs 11 字段交接行 | 写权行已改 DSH，但交接行仍 `负责人=Workbuddy`、`让出声明=CLAIMED`、`心跳=2026-10-27T16:51:46`、`状态=CLAIMED Workbuddy` | 同一文件内写权与交接状态**不一致**；心跳早于本卡工作时段（19:45–19:52） | STATE diff（父→被审） | 更新 11 字段行（负责人/让出声明/心跳/状态），或注明本卡不改该行的理由 |
| **NB-3** | 证据 `README.md:22`、`landing_manifest.json:107` | 写"**21 对**零重叠"，实际核验为 **28 对**（21 同空间 + 7 跨空间） | 描述低于实际检查强度（非错误结论） | `mechanical_checks.B.pairs=28`；我的复算 28/0 | 改为 28 对并注明分解 |
| **NB-4** | 派单/自报的路径列表 | 4 个路径名与提交内实际文件名不符（契约/gap 表/提案/证据清单） | 下游按错路径取件会取空 | 逐路径 `git rev-parse <rev>:<path>` 失败、实际同角色文件 OID 匹配 | 在任务卡/证据中更正路径（**OID 绑定本身无误**） |

## 8. 明确未做

- 未评**板级四项实测**（未执行，且板卡已拔）；未评 `ENABLE=1`/4-D 构建/真实链窗口 W-C。
- 未改 w4；未 push；未在任何仓库内运行写操作命令。

## 9. 边界

本复审仅针对 `e39f6de6f83fc06783ee9b97e86afabef0170e89` 的 D1=A 落盘内容与证据；**PASS 不代表 G0/关口通过、不代表阶段4 验收或板级通过**。
