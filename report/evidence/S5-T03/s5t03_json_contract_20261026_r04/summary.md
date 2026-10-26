# JSON 契约 v1.0.3 校验证据 RunId `s5t03_json_contract_20261026_r04`

> 数字口径：本摘要逐项取自本包 `manifest.json` / `console/`（机器可读权威）；冲突以 JSON/日志为准。
> 本包为**元/过程包**（校验器输出）：**不适用**该契约本身（无 `results.json` 与产物 schema）。
> 标注：`input_scope_label = synthetic_replay`、`status = PRELIMINARY`；PNG/MP4 非验收依据（本包无 PNG/MP4）。

- 被测代码提交（本包 `source_commit`）：`33a8f9423748…`
- 契约版本：**1.0.3**（`.json` 与 `.md` 同步）
- 本包独立套件日志：`Ran 116 tests` / OK（SHA `66d01f53105b…`）

## 1. 正向校验（exit 0，含**事件日志键位核对**与**文件哈希实测**）
```
OK   s5t03_offline_replay_display_20261026_r06        kind=replay_display frames=240 errors=[]
OK   s5t03_offline_long_run_replay_20261026_r04       kind=long_run_replay frames=106573 errors=[]
OK   s5t03_multi_geometry_render_20261026_r02         kind=multi_geometry_render frames=None errors=[]
contract=gestureforge_s5t03_json_contract v1.0.3 packages=3 failed=0
```

## 2. 本轮关闭的阻断（复审 R-1）与 N-1..N-4
| 项 | 问题 | 处置 | 实测 |
|---|---|---|---|
| **R-1** | BL-1 只闭环一半：**`.md` §6** 仍留幻影键（`rseq/state/drawn/boxes/sr/sk/ar/af/zd/verdict/outcome`），标题仍 1.0.1，而证据 manifest 又把该 `.md` 绑定为契约交付物 ⇒ 交付物自相矛盾且无从发现 | `.md` §6 改为实物 compact 键（submit 11 / commit 12）、标题升版本；**新增 `.md`↔`.json` 键位逐字比对测试** | `.md §6 == .json` 断言通过；幻影键 `verdict`/`rseq` 显式断言不存在 |
| **N-1** | `legend_ref` JSON 指针少一级 | 改为 `#/newly_frozen_for_skeleton_only/log_artifacts/compact_fields_*` | 契约断言通过（并核对 params 图例键集相等） |
| **N-2** | 只检首个事件日志 | **所有** `logs/events_*` 文件都检 | 第二个日志混入幻影键 → **exit 1**（新用例 `test_11`） |
| **N-3** | 缺事件日志不算错 | 要求日志的种类缺日志即违约 | 删 `logs/` → **exit 1**（新用例 `test_10`） |
| **N-4** | 说明键可被静默删除 | `frame_assertion_required_vs_stable` 纳入 `contract_required_keys` | 删除 → **exit 2** |

## 3. 判别力（负向，均临时契约/副本）
非对象契约 6 类 → exit 2；短 required/缺 `artifact_kinds`/删 `stability` → exit 2；键位改错（含多键/缺键）→ exit 1；
子目录多余 `manifest.json` → exit 1；`schema_version` 值错 → exit 1；哈希漂移 → exit 1；`passed=false` → exit 1；
`.md` 键位漂移 → 测试失败（防 R-1 复发）。

## 4. 边界
- 只证明结构契约、哈希与键位一致；不代表接口语义正确、测试成功、独立审查通过或 G0/G2/G4/G5；
- **真实回放接入 / 板上 / 摄像头 = NOT_RUN**；不接板卡、不联网；PNG/MP4 非验收依据；**G0/G1/G3/G4/G5 均未通过**；
- 前序 `…_r01`/`_r02`/`_r03` 保留不删，已被本包取代。
