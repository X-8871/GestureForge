# 本包 manifest schema 归属

## manifest schema 归属（如实标注，2026-10-27 r03）

- 本包**不使用** `verification/check_stage_delivery.py` 的 manifest schema（`inputs`/`evidence` 模式）。
  该项检查器对本清单**实跑 exit 2**：报缺 `evidence_dir`/`interfaces`/`limitations`，并含**未知字段**
  `boundary`/`card`/`nb_fixes`/`take_over`/`proposal_migration` —— 因本清单是**任务批次自定义格式**，
  不是交付包装格式。**因此不得**对本包声称 `CHECKS_OK` 或「通过 check_stage_delivery」。
- 本包实际使用的校验：专用校验器 `scripts/stage4_s4ctrl/verify_d1a_landing.py`（机械核验 A–G）、
  `scripts/stage4_s4ctrl/verify_shared_io_contract.py`、`scripts/stage4_s4b/audit_raw_system_g0_gaps.py`，
  以及**新基座门禁** `verification/check_manifest_hash_basis.py`（主仓）。
- 若后续确需 `check_stage_delivery` 包装，将**另补**一份 schema 合规的 `delivery_manifest.json`（不复用本文件）。
