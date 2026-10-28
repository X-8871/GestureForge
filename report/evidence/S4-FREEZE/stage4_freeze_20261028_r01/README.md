# 阶段4 离线冻结 r2（S4-T33）

- tag：`stage4-offline-freeze-20261028-r2`（annotated）；成员 **115**（规格 17 / 校验器 5 / 实现 8 / 证据 85）+ **11 项产物身份（全为真实 SHA-256 + 路径，可按文件重算）**。
- 验证器：**`scripts/stage4_s4ctrl/verify_stage4_freeze_package.py`**（成员按 commit blob 校验；产物身份按路径重算并拒绝占位形态；`--selftest` 5 例）。
- **与旧验证器的区别（同名不同义，已改名避免混淆）**：`verification/verify_stage4_frozen_set.py` 是旧的 **F1–F8 语义校验器**（检查契约/地址图/门禁语义），**不**校验冻结集成员哈希；本冻结集使用上面的 freeze_package 验证器。

## 成员分类计数
| 分类 | 数量 |
|---|---|
| 规格 spec | 17 |
| 校验器 verifier | 5 |
| 实现 implementation | 8 |
| 证据 RunId evidence_runid | 85 |
| **成员合计** | **115** |
| 产物身份 artifact_identity | 11 |

## r1 → r2 修正说明
1. 2B XSA 由"前缀+补零"占位改为**真实** `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`（848,620 B）；
2. 其余 10 项逐条从实际文件重算，全部为真实 64 位十六进制；
3. 验证器升级：拒绝尾部 ≥8 个 0/f 或"前缀+同字符体"的占位哈希；artifact 必须给 path 并按文件重算；干净导出中不可达的仓库外产物记 `[SKIP]` 并计入跳过（不静默）；
4. `--selftest` 增加第 5 例 `placeholder_hash ⇒ 非 0`；
5. 新验证器改名 `verify_stage4_freeze_package.py`；旧语义验证器保留；
6. r1（tag `stage4-offline-freeze-20261028-r1`，commit `4bb27b6`）保留为历史并列入 `superseded`。

## 明确未做清单（逐条，不美化）
1. `M3=FAIL/未闭合（REGION_CHANGED 6 字节、根因未定）`
2. `M4-a=NOT_RUN`
3. `M4-b=NOT_RUN`
4. `M4-b 长跑（≥30 min/≥1000 次）=NOT_RUN`
5. `PL 预处理 v2=未完成`
6. `4-D 位流=未产出`
7. `PS 真实解码=离线与 r13 逐字段一致、但应用接线未完成/无新 ELF`
8. `候选区 owner=未登记/BLOCKED`
9. `ENABLE=1 未解锁`
10. `G3/G4/G5 未主张`

## 复现
```
python -B scripts/stage4_s4ctrl/verify_stage4_freeze_package.py --selftest
python -B scripts/stage4_s4ctrl/verify_stage4_freeze_package.py --repo <worktree> \
    --frozen-set report/evidence/S4-FREEZE/stage4_freeze_20261028_r01/frozen_set.json
```
干净导出：`git archive HEAD | tar -x -C <export>`（本仓用 Python `tarfile` 解包以避免中文路径问题），随后加 `--disk` 或无 `.git` 自动切 disk 模式。

## 边界
全离线；不接触板卡；`ENABLE=0`；不改写既有证据 RunId；不 push；不动 25 项遗留；不主张阶段4 通过/G3/G4/G5。
