# 说明：本 RunId 已被取代（S4-A 契约 r02 → r04）

- `s4c_replay_20261021_r03` 是在 S4-A 契约 **r02**（sha256
  `77b5ceeb7db39b8185ecdfba06629ca7437bad827429e4943a94181ea869d8b5`）下产出的，其
  `replay_golden_109.json` / `replay_subset8_seed20261021.json` 的
  `comparison_spec.s4a_contract_alignment.contract_sha256` 记录的是 r02 值。
- Lead 随后将契约升级为 **r04**（sha256
  `1d7fd5f02bc4948fc6aa16734bf7bd258c1be34d2141f67eb487a2449f3be350`，本工作树
  `docs/stage4/s4a_stage4_g0_fields.json` 当前内容）：对拍口径未变（阈值 0.25 含等号、
  NMS 0.45、每图 ≤15 框、5 类顺序、两头 5,070/20,280 B 与 scale、score/xyxy ≤1e-6、
  离散字段全等），新增的 `candidate_count_pre_threshold` 为可选诊断字段，`candidate_count`
  改为阈值后/NMS 前口径，二者均不参与本工具的对拍。
- 因此本 RunId 的契约绑定值已过时，仅为“契约 r02 + 工具 sha256
  `9e63154464bcded27005a52465f4753562d7d0c1a70a98ff9574269219ba0df9`”这一时点的真实证据，
  予以保留但不再作为最终交付证据。
- 最终证据见同根下后续 RunId（契约 r04，manifest 的工具/测试/驱动 SHA 与当前工作树一致）。
- 本目录内容未被改写，仅为保留审计轨迹。