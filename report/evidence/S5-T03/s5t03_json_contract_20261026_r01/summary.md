# JSON 契约 v1 校验证据 RunId `s5t03_json_contract_20261026_r01`

> 数字口径：本摘要的提交号/测试数取自本包 `manifest.json` 与 `console/`（机器可读权威）；冲突以 JSON/日志为准。

- 被测代码提交（本包 `source_commit`）：`b9cd4c5e55c0…`
- 契约：`gestureforge_s5t03_json_contract` v1.0.0
  （`docs/stage5/s5t03_json_contract_v1.json` 机器可读 + `s5t03_json_contract_v1.md` 说明）
- 工具：`scripts/stage5_t03/validate_s5t03_json.py`（只读；退出码 0=通过 / 1=违约 / 2=输入或环境错误）
- 本包独立套件日志：`Ran 88 tests` / OK（SHA `2474f49e23b1…`）

## 1. 校验结果（真实退出码 0）
```
OK   s5t03_offline_replay_display_20261026_r06        kind=replay_display frames=240 errors=[]
OK   s5t03_offline_long_run_replay_20261026_r04       kind=long_run_replay frames=106573 errors=[]
OK   s5t03_multi_geometry_render_20261026_r02         kind=multi_geometry_render frames=None errors=[]
contract=gestureforge_s5t03_json_contract v1.0.0 packages=3 failed=0
```
三个最终包**全部通过**结构契约：短跑 240 行逐帧断言、长跑 106573 行（gzip + compact）、多几何无逐帧断言（该种类不要求）。

## 2. 判别力（负向用例，均在**临时副本**上，未改动任何证据）
- 缺必需字段（`numeric_checks`）→ FAIL；状态标签错（`DONE`）→ FAIL；缺计数键 → FAIL；
- 长跑缺 `one_commit_event_per_frame` → FAIL；重放类缺逐帧断言 → FAIL（多几何同条件通过）；
- `manifest.files[]` 缺 `sha256` → FAIL；契约缺键/契约文件缺失 → **fail-closed 抛错**；
- 种类判定：无法判定（无 counters/invariants/geometries）→ 抛错，**不默认成某一类**；
- CLI 退出码：全通过 `0` / 违约 `1` / 未指定包 `2`。

## 3. 稳定 vs 细节（阶段6/7 只可用稳定）
- **稳定**：公共必需字段、14 项计数语义、长跑不变量、逐帧断言稳定子集、`manifest.files[].path/sha256`、
  `manifest.tools[].path/sha256`、`limitations`、`not_run`；
- **细节（不得依赖）**：`process_seconds`、`render.*`、`demo.*`、`keyframes[].png_path`、`artifacts.*`、
  `logs.*`、`manifest.eol_status`、`console/*`、PNG/MP4。

## 4. 边界
- 只覆盖**离线合成**产物（`synthetic_replay` / `PRELIMINARY`）；**真实回放接入 / 板上动态映射 / 摄像头 = NOT_RUN**；
- **不接板卡**、不联网；PNG/MP4 不作验收依据；**G0/G1/G3/G4/G5 均未通过**；
- `CHECKS_OK` 仅表示**结构契约**通过，不代表接口语义正确、测试成功、独立审查通过或 G0/G4/G5。
