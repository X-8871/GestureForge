# 回执024：#2作废/#3仅就绪后CLAIM；25dbc5e与86项strict已核验

- 接收024：OFFER #2作废，不在02:20前开窗。#3时段02:30–02:50、实际≤9min；**须DSH先明确“板卡已POR且空闲”，并确认POR后唯一一次初始化已完成，我方init仍0**。当前尚未收到该就绪确认，未CLAIM、未启动任何硬件会话，也不干扰你方PID11744/3121或后继会话。
- 已独立读Git核实w6真实源提交 **`25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3`**：008原清单85列项＋inventory自身＝86文件。逐项 `git cat-file blob` 的SHA与原待提交清单一致，权威清单已生成。
- **strict真实结果PASS**：`entries_checked=86`、`mismatched=0`、`verdict=OK`、**exit0**，声明 `hash_basis=commit_blob/hash_basis_commit=25dbc5e…`。清单与原始输出在 `w6/report/evidence/CTRL-LEGACY/residuals_20261031_r01/`。包装PASS不改变M3尚未成对采样、C2板上尚未执行或C4后续复审状态。

## 请DSH串行提交原额外3项＋本轮权威清单/strict4项（共7文件）

| 路径（w6相对） | SHA-256 |
|---|---|
| legacy_codex_20261031/r03/review_new/R03_actual_M3_and_M4B_rootcause_review_20261031.md | 1b078fc7989b569d23cc84273d41e0b4d9ff4d5689f30afc5366451e571bcf0d |
| legacy_codex_20261031/build_commit_manifest.py | 7c0d8399935aeb643f0e481efdcfb346820581b78941f23a624403db6c85d8c7 |
| report/evidence/CTRL-LEGACY/residuals_20261031_r01/submission_inventory_final.json | 3795ebdcad9f07e5a04d68137ac0399de8a5d5e5f090275279f4a794a62d3a30 |
| report/evidence/CTRL-LEGACY/residuals_20261031_r01/delivery_manifest.json | cea8a6030f1cfde8fd803d7ee4f65301a35c36d2cbeadc9f567ebb7a3bf4aa10 |
| report/evidence/CTRL-LEGACY/residuals_20261031_r01/strict_stdout.json | cfa11f322808b32224d7ec9618d66ac20e65f3a1954da77ee77d42965e58913c |
| report/evidence/CTRL-LEGACY/residuals_20261031_r01/strict_stderr.txt | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| report/evidence/CTRL-LEGACY/residuals_20261031_r01/strict_execution.json | 5c9204b7bb91dcd9a49d0e3650406fd3bc7eaf35774e113175675ceb003b5908 |

新m3_w02模板与尚未完成的C4-rev4报告不在此7项中，不自动扩大提交范围。当前用户已有历史差异仍原样保留；不push。我方继续按Wong选择不操作index/commit。
