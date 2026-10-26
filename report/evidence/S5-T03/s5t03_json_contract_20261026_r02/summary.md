# JSON 契约 v1.0.1 校验证据 RunId `s5t03_json_contract_20261026_r02`

> 数字口径：本摘要的提交号/测试数取自本包 `manifest.json` 与 `console/`（机器可读权威）；冲突以 JSON/日志为准。

- 被测代码提交（本包 `source_commit`）：`74daae3b5f30…`
- 契约版本：**1.0.1**（`docs/stage5/s5t03_json_contract_v1.json`；校验器只读该文件）
- 工具：`scripts/stage5_t03/validate_s5t03_json.py`
- 本包独立套件日志：`Ran 104 tests` / OK（SHA `10f180a8ac4c…`）
- 命令另见 `console/command.txt`；套件命令另见 `console/suite_command.txt`

## 1. 正向校验（exit 0）
```
OK   s5t03_offline_replay_display_20261026_r06        kind=replay_display frames=240 errors=[]
OK   s5t03_offline_long_run_replay_20261026_r04       kind=long_run_replay frames=106573 errors=[]
OK   s5t03_multi_geometry_render_20261026_r02         kind=multi_geometry_render frames=None errors=[]
contract=gestureforge_s5t03_json_contract v1.0.1 packages=3 failed=0
```

## 2. 契约专项复审 B1–B6 的关闭与实测（退出码）
| 项 | 问题 | 处置 | 实测 |
|---|---|---|---|
| B1 | 短跑包无 `assertion_mode`（却被声明为稳定必需） | 降为**稳定可选**；校验器改为逐帧检查 `frame_assertion_stable_required` | 缺 `result_seq` 的逐帧条目 → **exit 1** |
| B2 | `schema_version` **值**无守卫 | 与 `artifact_kinds[kind].schema_version` 逐值比对 | 值改 `_v2`/乱填 → **exit 1** |
| B3 | `manifest.files[].sha256` 只查键存在 | **实测**文件内容哈希；并检出未列入文件 | 篡改 `results.json` → **exit 1** |
| B4 | `checks.passed=False` 仍 exit 0 | 要求 `passed is True` 且与 `failures` 自洽 | 改 `passed=false` → **exit 1** |
| B5 | 契约本体缺键静默放过/崩成 1 | 契约必填键 fail-closed，**退出码 2** | 逐个删除 `contract_required_keys` 中任一键 → **exit 2**（19/19 命中） |
| B6 | 退出码语义与文档不符 | 固定 0/1/2 | 包目录不存在 → 2；`--packages-from` 文件不存在 → 2；无参数 → 2 |

## 3. 契约内容变更（v1.0.1）
- `results.stream.frame_period_ns` 升为**稳定**（阶段6 T6-A03 帧周期来源；短跑与长跑均提供）；
- `manifest.tools` 记法改为 **role→对象映射**（消费者不得写 `tools[0]`）；
- 登记事件日志拒绝原因键为 **`rr`**（此前文档误写 `reason`），并如实描述"两处原因串可能不同"；
- 新增 `manifest_cross_checks`（run_id/source_commit/schema_version 一致性）、`unclassified_policy`（未逐键列出的容器内字段一律视为 detail）。

## 4. 判别力（负向，均在临时副本/临时契约上，未改动任何证据）
- 8 类结构变体（缺必需字段、状态标签错、缺计数键、长跑缺不变量、重放类缺逐帧断言、
  `manifest.files[]` 缺 sha256、`input_scope_label` 错、`checks` 缺 passed）→ **exit 1**；
- 追加变体（counters/invariants 变 list、tools 清空、逐帧缺字段、缺 results.json、limitations 非数组）→ **exit 1**；
- 本轮新增：schema 值错、文件哈希漂移、`passed=false`、契约缺键、三种环境错误 → 见 §2 实测列。

## 5. 边界
- 只覆盖**离线合成**产物（`synthetic_replay`/`PRELIMINARY`）；**真实回放接入 / 板上 / 摄像头 = NOT_RUN**；
- **不接板卡**、不联网；PNG/MP4 非验收依据；**G0/G1/G3/G4/G5 均未通过**；
- 本校验只证明**结构契约与文件哈希**；不代表接口语义正确、测试成功、独立审查通过或 G0/G2/G4/G5。
- 前序 `s5t03_json_contract_20261026_r01` 绑定**契约 v1.0.0 + 旧校验器**，已被本包取代（保留不删）。
