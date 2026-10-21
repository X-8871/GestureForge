# 说明：本 RunId 已被取代（证据根迁移 + 工具增强）

- `s4c_replay_20261021_r02` 状态为 PASS，`acceptance` 六项全为 true（全量 109 退出码 0、
  mismatch=0、反例退出码 1 且定位到 `head13.tensor_sha256`、unittest OK、全部步骤符合期望）。
- 其后发生两项变更，故不作为最终交付证据：
  1. 阶段4 证据根按 Lead 决定统一为 `report/evidence/<TASK>/<run_id>/`；本目录由
     `report/evidence/S4-CTRL/S4C/` 原样迁移而来（内部记录的路径字符串仍为迁移前旧根）。
  2. 对拍工具新增 `--actual` 模式的“golden 逐值定位”（首个差异字节偏移、期望/实际字节值、
     差异字节数、最大 INT8 差值）与 `--no-golden-bytes` 降级开关，`verification/s4_replay_compare.py`
     的 SHA-256 因此变化；本目录 manifest 中记录的工具 SHA 只对应旧版本。
- 最终证据见同根下后续 RunId（其 manifest 记录的工具/测试/驱动 SHA 与当前工作树一致）。