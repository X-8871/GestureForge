# Wong确认DSH串行提交；008原清单保持，新增3项单独补充

- Wong在当前chat明确选择：**“由DSH按CDX-008清单提交并回传SHA”**。我方继续不git add/commit，不写main/w6的旧差异或冻结物。请按008原清单86文件核对并串行提交，回传完整SHA。
- 008清单本身和已列项原样不变：`submission_inventory.json` SHA `6e761828ff2c1b38e24f48ed44c41e3ba0fa3031e749451c78a0f1e604a2fa8e`。先提交008原范围即可解除权威manifest生成所需的源提交阻塞。

## 后续3项精确补充（不自动混入008）

1. `legacy_codex_20261031/r03/review_new/R03_actual_M3_and_M4B_rootcause_review_20261031.md`，SHA `1b078fc7989b569d23cc84273d41e0b4d9ff4d5689f30afc5366451e571bcf0d`：最终独立审查PASS，限实际失败/收尾证据诚实与M4B离线根因；M3仍BLOCKED/NOT_RUN。
2. `legacy_codex_20261031/build_commit_manifest.py`：只读Git blob生成器，等真实SHA后调用，不操作index/commit；实际字节哈希见最终清单。
3. `report/evidence/CTRL-LEGACY/residuals_20261031_r01/submission_inventory_final.json`：最终清单SHA `3795ebdcad9f07e5a04d68137ac0399de8a5d5e5f090275279f4a794a62d3a30`；列88项＋自身＝89文件、列项566269B，其中包含008原86项和上述前2新增项，自身是第89项。此为工作区身份附注，显式 `delivery_eligible=false/hash_basis=worktree_disk`，不是权威交付manifest。

本轮14个Python文件AST核验exit0；没有因打包重复运行全套测试。新增3项请DSH另核后与后续commit_blob manifest/strict记录一起精确提交，或在008之后单独提交，勿扩大到旧差异。工具/脚本、C2/C3已停写，不占板。

## 新确认的R-03根因

旧M4B失败精确ELF `ada4b30d…` 的ARM反汇编是**400周期（0x190），不是0x40000000**：`0x103738 mov r2,#400`→`0x10373c str r2,[r4,#40]`，同值写+44，50MHz下8µs；历史registration_r3已记载该旧版缺陷。失败done2跳过HEADS比较而diff初值0，不能推断输出已正确。3份后续成功记录有done1/真实HEADS行/47287ms/尾word5A5A0506。最终独立审查已确认；报告与r02原证据均包含在上述范围。

M3新OFFER仍未收到，不自行重开；板卡已01:21:08交还。R-01不处理，ENABLE=0、不push。
