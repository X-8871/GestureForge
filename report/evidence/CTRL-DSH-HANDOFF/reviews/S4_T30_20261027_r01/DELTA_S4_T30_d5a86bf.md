# S4-T30 增量核对报告（4 项非阻断修复）

- 被核提交：**`d5a86bffa1c5217076efcacb494b37f0c980d6a9`**（父 `e39f6de6f83fc06783ee9b97e86afabef0170e89`；作者=提交者 `2026-10-27T20:00:58+08:00`；17 文件；未 push）
- 复审方：DSH 阶段3 总控（只读）；工作区 `D:\tmp\review\S4_T30_20261027_r01\`（仓库外）
- **w4 未被写**：核查前后 `status` sha256 `784eef0a…`、`index` sha256 `d7206c0d…`、HEAD `d5a86bff` 三者**逐字节不变**
- 未运行写仓库命令；未动硬件；**不重审全案**（只核 4 项 + 有无引入新问题）

## 结论：**DELTA_FAIL**

**4 项未全部关闭 ⇒ `S4-T30` 暂不能标为已完成。** 技术语义**无回归**（地址/长度/owner/状态词/2B 区间/契约版本全部未变），问题集中在**证据哈希基座**与**防复发断言**两处，属"再修一轮即可关闭"的量级。

| 项 | 判定 | 依据 |
|---|---|---|
| NB-1 时间戳 | **数据层真修**；**断言未落地（未完全关闭）** | 契约 `19:44:56`、缺口表 `19:45:21`，**均 ≤ 提交 `20:00:58`**；`timestamp_source`/`updated_utc8_source` 如实写明来源与"手填笔误"成因。**但**：本提交 17 文件**无任何脚本**（`diff-tree | grep '\.py|\.sh|\.tcl'` → 空）；全树 `git grep -nE '(at_utc8|updated_utc8).*(<=|<|greater|future|commit)'` → **0 命中** ⇒ 声称的"脚本内断言"**不存在**，防复发机制缺失 |
| NB-2 STATE 交接行 | **真修** | 负责人=`DSH 项目总控（Wong 2026-10-27 直接指令接管）`；让出声明=`无书面 OFFERED 行（原持有方未出 OFFERED）；本次接管依据为 Wong 2026-10-27 直接指令，属直接指令接管，非 OFFER 交接`；心跳=`2026-10-27T20:00:09+08:00`（≤ 提交 `20:00:58`）；状态=`IN_PROGRESS DSH 项目总控`；与顶部写权行一致，**未伪装 OFFERED→CLAIMED** |
| NB-3 对数 | **真修** | r01/r02 README 均写 **28 对**（`C(8,2)`；ddr 内 21 + 跨 ddr↔pl_mmio 7）；manifest reason 同步；`mechanical_checks.B.pairs=28` 未变；我独立复算 **28/0** |
| NB-4 路径名 | **路径名真修**；**同包 `files[].sha256` 基座未修净（新问题）** | 4 个真实文件名齐备、`/` 分隔、含"OID 与对象身份不变，仅路径名更正"说明。**但**：r01 `files[]` 13 项中 **8 项**的 sha **不等于被审提交 `e39f6de6` 的 blob**（7 项=工作区 disk CRLF 字节，1 项=中间态旧值）；r02 `files[]` 12 项中 **9 项**为 disk CRLF 字节；**两个 manifest 均无 `hash_basis` 基座字段**，r02 亦无"提交后复算/自引"说明 |

## NB-4 证据基座缺陷（量化，可复跑）

| manifest | files | 等于提交 blob | 等于工作区 disk(CRLF) | 既非提交也非盘上 |
|---|---|---|---|---|
| r01（`s4_d1a_landing_20261027_r01`） | 13 | **3**（address map / proposal / verifier） | **7** | **3**（contract `4d8dc0d4`=被审 blob 但≠新提交；gap registry `56795350` 两不匹配；STATE `61e015a0`=被审 blob） |
| r02（`s4_d1a_landing_20261027_r02`） | 12 | **3** | **9** | 0 |

- 示例：`…/r01/exits.txt` 记录 `41679eb138a2…` = 工作区 disk（CRLF，42 B）；提交 blob = `d08ef8ec7e64…`（LF，41 B）⇒ 按"绑定被审提交"验证会 **FAIL**。
- 因此派单所述"r01 的 `files[].sha256` 描述被审提交 `e39f6de6` 的 blob（不是修后工作树）"**不成立**（仅 5/13 成立）。
- 根因：manifest 在**提交前**按工作区字节生成，且未声明基座、未做提交后复算（与本项目既有 `-text`/CRLF 基座问题同类）。

## 有无引入新问题（逐项）

| 检查 | 结果 |
|---|---|
| 提交范围 | 17 文件**全在授权路径**（`docs/stage4/`、`report/evidence/S4-CTRL/`、`.codex/STATE.md`），越界 **0** ✅ |
| 25 项未提交 | 与提交清单**交集为空** ⇒ 未被卷入 ✅；`index.lock` 不存在 ✅；未 push（434 提交未推送）✅ |
| 语义未变 | 地址图 blob **未变**（`7c20ac89…`）；契约仅 `post_freeze_rebinds` 变（`nonbinding_diff=[]`），`1.3.0/FROZEN_OFFLINE_ONLY/r07` **未变**；缺口表仅 `basis_bindings`/`updated_utc8`/`updated_utc8_source` 变，**gap 条目 0 变化**；G-01/G-02 仍 `PARTIALLY_CLOSED_OFFLINE` ✅ |
| 连带重绑诚实 | `basis_bindings[shared_input_contract]=25bc30d5…` **== 修后契约文件实际字节 SHA** ✅；`address_map=7c20ac89…` ✅；未借机改语义 ✅ |
| 三器自跑（真实退出码） | `verify_d1a_landing` **0**（7/7）、`verify_shared_io_contract` **0**（27/0）、`audit_raw_system_g0_gaps` **0**（17/17+13/13+3/3）；产出与 r02 证据**逐项一致**（status/checks/passes 全 equal）✅ |
| 退出码记录 | r02 `exits.txt`=`mechanical=0 selfcheck=0 gap_audit=0`，四个 `*.exit_code.txt` 齐 ✅；r01 首轮 FAIL 保留（`gap_audit.exit_code.txt=exit=1`）✅ |
| 关口/状态断言 | 全量扫描 **0** 处"G0 通过/ENABLE=1/已冻结"式断言 ✅ |
| r01/r02 关系表述 | r01 README："本文件为复审基线原文更正；修后复跑证据见 r02" ✅；r02 README：被审基线 `e39f6de6` ✅（但 r02 manifest 未含提交绑定/复算，见上） |

## 需再修（极小一轮）

1. **r01/r02 `files[].sha256` 基座**：二选一——(a) 改为**提交 blob 基准**（r01 绑定 `e39f6de6f83fc06783ee9b97e86afabef0170e89`、r02 绑定 `d5a86bffa1c5217076efcacb494b37f0c980d6a9` 的提交内 blob）；或 (b) 保留"生成时工作区字节"但**新增 `hash_basis` 字段显式声明**，并另附**提交后复算表**（对提交内 blob 的 SHA）。同时修正 r01 中 gap registry 的 `56795350…`（两不匹配）。
2. **NB-1 防复发断言**：在产生 `post_freeze_rebinds.at_utc8` / `updated_utc8` 的脚本中加入 **fail-closed** 断言（写入时刻 ≤ HEAD 提交时刻），并附**负向自测**（构造未来时间戳必须失败）。
3. （建议）r02 增加"本包由提交 `d5a86bff` 承载"的说明（提交号不可自引，但可由复核方记录）。

## 边界

本报告只核 4 项非阻断修复及是否引入新问题；**不重审全案**、不评板级；PASS/DELTA 结论均不代表阶段4 验收或关口通过。未改 w4、未 push。
