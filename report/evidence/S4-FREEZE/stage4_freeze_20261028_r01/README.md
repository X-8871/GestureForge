# 阶段4 离线冻结 r1（S4-T33）

- 冻结身份：tag `stage4-offline-freeze-20261028-r1`（annotated）；成员 **115** 项；
  `hash_basis_commit` = 含最新验证器的提交；验证器 `scripts/stage4_s4ctrl/verify_stage4_frozen_set.py`。
- **冻结 ≠ 验收通过**：只表示当前交付物身份可复现；**不主张 G3/G4/G5，不写"阶段4 通过"**。

## 成员分类计数
| 分类 | 数量 |
|---|---|
| 规格 spec | 17 |
| 校验器 verifier | 5 |
| 实现 implementation | 8 |
| 证据 RunId evidence_runid | 85 |
| **成员合计** | **115** |
| 产物身份 artifact_identity（仓库外） | 11 |

## 明确未做清单（逐条，不美化）
1. `M3=FAIL/未闭合（REGION_CHANGED 6 字节、根因未定）`
2. `M4-a=NOT_RUN`
3. `M4-b=NOT_RUN`
4. `M4-b 长跑（≥30 min/≥1000 次）=NOT_RUN`
5. `PL 预处理 v2=未完成`（letterbox/AXI-Lite/BD/build_r03 均未做）
6. `4-D 位流=未产出`
7. `PS 真实解码=离线与 r13 逐字段一致、但应用接线未完成/无新 ELF`
8. `候选区 owner=未登记/BLOCKED`
9. `ENABLE=1 未解锁`
10. `G3/G4/G5 未主张`

## 复现
```
python -B scripts/stage4_s4ctrl/verify_stage4_frozen_set.py --selftest
python -B scripts/stage4_s4ctrl/verify_stage4_frozen_set.py     --repo <worktree> --frozen-set report/evidence/S4-FREEZE/stage4_freeze_20261028_r01/frozen_set.json
git archive HEAD | tar -x -C <export>   # 导出副本内可加 --disk 或无 .git 自动切 disk 模式
```

## 边界
全离线；不接触板卡；`ENABLE=0`；不改写既有证据 RunId；不 push；不动 25 项遗留。
