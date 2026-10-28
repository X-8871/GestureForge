# 阶段4 离线冻结 r3（S4-T33）

- tag：`stage4-offline-freeze-20261028-r3`（annotated）；成员 **115**（规格 17 / 校验器 5 / 实现 8 / 证据 85）+ **11 项真实产物身份**（含路径，按文件重算）。
- **冻结身份**：以 **commit blob** 为准（`frozen_set.json` 的 blob SHA 由 `frozen_set_report.json` 记录）；磁盘字节值仅作附注并列。
- 验证器：**`scripts/stage4_s4ctrl/verify_stage4_freeze_package.py`**（成员按 commit blob；产物身份按路径重算并拒绝占位；`--selftest` 5 例；**disk 模式不再解析 commit**，可在无 `.git` 导出内复跑）。
- 旧 `verification/verify_stage4_frozen_set.py` 是 **F1–F8 语义校验器**，语义不同；其当前实测结论为 **exit 1（7/8，F5 硬件门禁记录缺 `hardware_session_handoff` 等）**，**不得**表述为"验证器全通过"。

## r2 → r3 修正
1. **CRITICAL-1**：disk 模式原先仍强制 `git rev-parse`，在无 `.git` 导出内必然 exit 2；已改为 disk 模式跳过 commit 解析，并用**真 `git archive`** 重跑，记录真实文件数与新的 exit/stdout（不再沿用 r1/r2 旧文件）。
2. **CRITICAL-2**：`frozen_set_report.json` 曾为 r1 遗留（freeze_id/hash/verifier 路径均旧）；已按 r3 数据重生成。
3. **MAJOR-3**：工作区脏项逐条列入 `not_frozen`（含状态 M/?? 与原因），数量与 `git status` 实况一致；唯一被改的冻结成员 `build_record.json` 已从 blob 取回；不再声称"干净"。
4. **MINOR-4**：明确"冻结身份 = commit blob"，磁盘值仅附注（两者并列写入 `frozen_set_report.json`）。
5. **MINOR-5**：`results_freeze.json.exit_codes` 填真实值；旧 F1–F8 验证器 exit 1 及其原因记入包内。

## 成员分类计数
| 分类 | 数量 |
|---|---|
| 规格 spec | 17 |
| 校验器 verifier | 5 |
| 实现 implementation | 8 |
| 证据 RunId evidence_runid | 85 |
| **成员合计** | **115** |
| 产物身份 artifact_identity | 11 |

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
python -B scripts/stage4_s4ctrl/verify_stage4_freeze_package.py --repo <worktree> --frozen-set <frozen_set.json>
# 无 .git 导出（真 git archive）：
git archive HEAD | tar -x -C <export>       # 本仓用 Python tarfile 解包以避开中文路径
python -B <export>/scripts/stage4_s4ctrl/verify_stage4_freeze_package.py --repo <export> --disk
```

## 边界
全离线；不接触板卡；`ENABLE=0`；不改写既有证据；不 push；不动其他树；不主张阶段4 通过/G3/G4/G5。

## r3 → r4 修正（交付清单可满足性）
1. 交付清单**不再收录任何 `*.log`**：包内日志已移出到 `tmp/4/S4-T33/logs_r4/`（`*.log` 属 gitignore，不可入库）；退出码证据由 `results_freeze.exit_codes` 与 `exit_*.txt`（内含 `commit=` 与 `tree=`）承载。
2. 新增**清单生成器** `scripts/stage4_s4ctrl/build_freeze_package_manifests.py`：写盘前对 `files[]` 每个路径执行 `git cat-file -e <commit>:<path>`，任一失败 ⇒ **exit 3**；`.log`/`git check-ignore` 命中 ⇒ **exit 4**（防复发）。
3. 干净导出从**冻结提交**重建，`frozen_set_report.checks.clean_export.export_commit` 写明所用提交与 tree。
4. 每轮 `exit_*.txt` 内容为 `exit=<code> commit=<commit> tree=<tree>`，因此各轮证据文件天然不同。
