# 驱动离线自检 · 复审重跑副本（2026-10-29 r01）

- **来源**：独立复审按其设计运行 `run_bringup_driver.py --offline-selftest` 时，向原 RunId
  `bringup_driver_v3_20261028_r01/` 写入了 `offline_selftest.json` 与 `SELFTEST_load_phantom.xsdb_error_text.txt`。
- **本 RunId 用途**：把这两件**移出**原 RunId，保留复审重跑的真实产物；原 RunId 已用
  `git checkout --` 恢复为提交态（原证据不可变）。
- **结果**：`verdict=PASS`、`OFFLINE_SELFTEST_PASS (57/57) exit=0`。
- **说明**：本目录内容为**重跑副本**，与提交态原件（原 RunId）逐字节可能不同（时间戳/顺序），
  因此不以 commit_blob 覆盖新文件；见 `manifest.json` 的 `hash_basis` 说明。

## 文件
| 文件 | SHA-256 |
|---|---|
| `offline_selftest.json` | `7979ad4c07ed7b8f5283e42b6a045b4ee17fe484f1d9a6edb4df9d9e68a2a311` |
| `SELFTEST_load_phantom.xsdb_error_text.txt` | `f513b0819935b42c715acce7e1559510dd71327ecaa5b5aa6543d87aa105a5e8` |

## 边界
离线；未上板；不改判据；`ENABLE=0`；不 push；不主张 G3/G4/G5；M3/M2 未闭环。
