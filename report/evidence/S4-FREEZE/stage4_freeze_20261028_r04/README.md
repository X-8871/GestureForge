# 阶段4 离线冻结包 r4（S4-T33）

- 本包身份由 annotated tag **`stage4-offline-freeze-20261028-r4`** 标识；**具体提交/树哈希不写进本包**（避免"提交既要包含又要描述自己"），见兄弟目录 `stage4_freeze_20261028_r04_verification/`。
- **设计（r4 起）**：冻结包只放**输入类**成员；**验证输出（退出码/日志/导出证据）移出到兄弟 RunId**（post-freeze 验证证据）。包内 **0 个 `.log`、0 个 gitignore 命中项**。
- 成员 **115**（规格 17 / 校验器 5 / 实现 8 / 证据 85）+ **11 项真实产物身份**（含路径，按文件重算）。
- 验证器：`scripts/stage4_s4ctrl/verify_stage4_freeze_package.py`（commit blob 逐成员；产物按路径重算并拒绝占位；disk 模式不解析 commit；`--selftest` 5 例）。
- 旧 `verification/verify_stage4_frozen_set.py` 是 F1–F8 语义校验器，实测 **exit 1（7/8，F5）**，与成员校验器不同义。

## 包内成员（输入类）
`frozen_set.json`、`README.md`、`results_freeze.json`、`frozen_set_report.json`、`landing_manifest.json`、`delivery_manifest.json`。

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
python -B scripts/stage4_s4ctrl/verify_stage4_freeze_package.py --repo <worktree> --frozen-set <本包>/frozen_set.json
git archive stage4-offline-freeze-20261028-r4 | tar -x -C <export>
python -B <export>/scripts/stage4_s4ctrl/verify_stage4_freeze_package.py --repo <export> --disk
```

## 边界
全离线；不接触板卡；`ENABLE=0`；不改写既有证据；不 push；不动其他树；不主张阶段4 通过/G3/G4/G5。
