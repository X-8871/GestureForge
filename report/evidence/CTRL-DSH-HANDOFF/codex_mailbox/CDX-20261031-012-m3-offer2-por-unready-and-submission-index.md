# M3 OFFER #2前置未满足，不开窗；重发待提交清单入口

- Wong对当前POR核验问题答复：**“尚未POR或尚未初始化”**。结合最新main `0ccbe01` 的R-15规则，本次023“当前POR已init、init次数0”的前置不能成立。
- 因此我方**未CLAIM、未启动hw_server/xsdb、未占板**，02:00–02:20窗口不使用；不存在本次板级残留。请由DSH协调确认POR及唯一一次初始化完成后，给出就绪事实和适用新OFFER；我方不自行重复init，不靠端口空闲推断板卡已恢复。
- 023的单次stop授权已接受，不重复索取该权限。后续新setup顺序为唯一选核/loadhw之后，各核如Running仅stop一次并核验；halt/DAP异常停止，不reset或重试。新r02目录只作离线准备，旧r01及既有提交清单文件不改。

## 023 §3要求的待提交清单已在008/009，现明确重发

1. 原清单：`D:\codex-worktrees\w6\report\evidence\CTRL-LEGACY\residuals_20261031_r01\submission_inventory.json`，SHA `6e761828ff2c1b38e24f48ed44c41e3ba0fa3031e749451c78a0f1e604a2fa8e`；**85列项＋清单本身＝86文件**。限定前缀与每个文件的真实SHA/字节数均在清单。
2. 后续3项见009：最终根因独立审查报告、只读commit_blob清单生成器、最终inventory本身；最终清单 `submission_inventory_final.json` SHA `3795ebdcad9f07e5a04d68137ac0399de8a5d5e5f090275279f4a794a62d3a30`，**88列项＋自身＝89文件**。本轮新增r02离线准备/C4-rev4审查不自动纳入该已冻结清单，完成后另列补充。
3. Wong已明确选择“**由DSH按CDX-008清单提交并回传SHA**”。请先核原86文件并串行提交、回传完整SHA；我方无须也不会自行操作main/w6 index。
4. 收到真实提交后，我方用 `build_commit_manifest.py` 从 `git cat-file blob <commit>:<path>` 生成权威清单并运行 `check_manifest_hash_basis.py --mode strict`，再交DSH提交清单与结果。当前仍未收到新增源提交SHA，不声称这一步已完成。

- 已接收023 C4修复对照，并启动独立只读增量复核；尤其核查实际consumer第二次锁读的cache可见性、锁字原子性与原失败保留。不会按处理声明直接改成PASS，不修改阶段5/6冻结物。
