# 说明：本 RunId 已被取代（驱动侧汇总 bug，非工具失败）

- `s4c_replay_20261021_r01` 是 S4-C 驱动的第一轮真实执行，全部步骤本身的退出码都符合期望：
  s0=0、s1（全量 109）=0、s2（子集）=0、s3（--actual 正对照）=0、s4（1 字节篡改反向例）=1、
  s5（篡改自检）=0、s6（unittest）=0；全量报告 `status=PASS`、`mismatch_total=0`。
- 但驱动脚本自身的“反例定位判定”有 bug：它把期望字段错拼为
  `<sample_id>.head13.tensor_sha256`，于是 `acceptance.s2_tamper_localized=false`，
  驱使整体 `status=FAIL`。
- 该 bug 只影响驱动侧的验收汇总，不影响对拍工具的判定：本目录
  `replay_actual_tamper_test_fist_000.json` 中该样本的 mismatch 记录确实是
  `field=head13.tensor_sha256`（kind=byte）。
- 驱动修正后已重跑为 `report/evidence/S4-C/s4c_replay_20261021_r02/`，最终交付证据见后续 RunId。
- 本目录文件内的路径字符串仍指向迁移前的旧证据根
  `report/evidence/S4-CTRL/S4C/…`，因为阶段4 证据根随后按 Lead 决定统一为
  `report/evidence/<TASK>/<run_id>/`；迁移未改写文件内容。