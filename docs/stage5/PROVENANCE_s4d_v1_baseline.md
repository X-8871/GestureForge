# 阶段4 v1 草案在阶段5 准备树中的复制出处（PROVENANCE）

更新：2026-10-21（UTC+8）。本文件只说明**来源与复制规则**，不改写任何 w4 已审查交付。

## 复制规则

- 阶段4 准备树 `D:\codex-worktrees\w4`（分支 `stage4-infer-prep`，冻结 HEAD `73c3dadbf16f58f3ce85f34620855f7bdc408f5a`，四项准备各经独立审查 PASS）是**只读输入基线**。
- 本树的下列文件是**逐字节复制**（`cp -p`，复制后逐文件 SHA-256 与源一致，已在开工核验中验证）：

| 本树路径 | w4 源路径 | SHA-256（两树一致） |
|---|---|---|
| `docs/stage5/S5_stage5_display_spec_draft.md` | `docs/stage5/S5_stage5_display_spec_draft.md` | `0b4f537d2efb572d5e67482c7bc095e57bb469701cff11209cbbafe36c0a5032` |
| `docs/stage6/S6_stage6_interaction_spec_draft.md` | `docs/stage6/S6_stage6_interaction_spec_draft.md` | `d7cf98093996fffb23180b078dfa4068dcab5b5031d5bd4c62e4c51baa40a0a1` |
| `docs/stage6/s6_interaction_thresholds.json` | `docs/stage6/s6_interaction_thresholds.json` | `b87234e4f091bac94f9d7cc7c8ab16c180932f60dc8e5160e32cd3278b11ec42` |
| `docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md` | `docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md` | `314335cd55e70630da5dbf591cb6271b8d51e8363825d2e88778b6b6ed64a371` |
| `docs/stage4/s4a_stage4_g0_fields.json` | `docs/stage4/s4a_stage4_g0_fields.json` | `3524d02ae410ae365a9dbfc5f04dcd9f300f8013086a076259a641f7eb8afb87` |

## 使用边界

- 上述复制件在本树内**只作只读基线**：阶段5 的收敛结论写在 `docs/stage5/S5A_stage5_display_g0_spec_v2.md` 与 `docs/stage5/s5a_stage5_display_g0_fields.json`，**不回写**这些复制件；w4 的原始文件也绝不改动。
- 阶段4 S4-A 契约状态仍是 `DRAFT_NOT_FROZEN`；阶段5 引用其字段名与口径时必须同时标注“阶段4 未冻结”，不得冒充阶段4 G0 或阶段4 验收通过。
- 阶段6 的修订意见只写在本树 `docs/stage6/S6D_stage6_revision_suggestions_from_stage5.md`（建议，不生效）；**阶段6 正式准备树由项目总控另行开启**。
- 引用行号以只读主树 `D:\FPGA_Competition` 为准；本树复制件的引用行内容与主树一致（差异只在被引用行之外）。