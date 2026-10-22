# 说明：本目录的 `delivery_manifest.json` 已被规范路径下的清单取代（首次尝试被拒的失败证据保留）

- 时间：2026-10-22 10:50（UTC+8）
- 事实：
  1. 首次按 `verification/check_stage_delivery.py` 的 schema 尝试在本目录（控制目录，按提示词要求使用 `report/evidence/S5-CTRL/<task_id>/<run_id>/` 布局）生成交付清单，**被检查器拒绝**：`--mode evidence` 退出码 **2**，报告 41 条 schema 违规（未知顶层字段、`evidence_dir` 必须精确等于 `report/evidence/<task_id>/<run_id>`、`files[].role` 取值受限、`checks[].status=PASS` 要求 `exit_code` 严格为 0、`interfaces[].path` 必须在 `docs/` 等）。
  2. 该被拒清单**保留在本目录**（不删除），作为该次失败的原始证据。
  3. 修正后的**权威机器可读交付清单**写在项目检查器要求的规范布局：`report/evidence/S5-A/s5a_g0_20261021_r03/delivery_manifest.json`，`--mode evidence` **退出码 0、errors 为空（CHECKS_OK）**，且输出确定性（两次生成逐字节一致，SHA-256 `6b3176cf514760d36fea1e9ef534c37122cad9ee534b36b99fac23376ae25e48`）。
- 说明：控制目录沿用提示词要求的三段式布局（`S5-CTRL/<task_id>/<run_id>/`），与检查器的两段式 `evidence_dir` 约定不同，故机器清单落在规范路径；两者内容互不覆盖。
- 原始输出副本：本目录 `console/checker_evidence_mode.txt`（规范清单的核验输出）。
- 适用性：`--mode inputs` **不适用**（本任务无冻结的上游接口，按 `report/README.md`「无本地输入的独立任务只对交付证据运行 evidence」），未伪造接口或输入。