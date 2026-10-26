# HUD 遮挡量化 RunId `s5t03_hud_occlusion_20261026_r01`
> 本包为**元/过程包**（量化输出，schema 为 `gestureforge_s5t03_hud_occlusion_v1`）：
> **不适用** `gestureforge_s5t03_json_contract` 的 `artifact_kinds`（该契约未包含本 schema）。
> 标注：`input_scope_label = synthetic_replay`、`status = PRELIMINARY`。

> 数字口径：本摘要逐项取自本包 `results.json` / `manifest.json` / `console/`（机器可读权威）；冲突以 JSON 为准。

- 被测代码提交（本包 `source_commit`）：`74daae3b5f30…`
- 本包独立套件日志：`Ran 104 tests` / OK（SHA `182cada9eecc…`）
- `checks = {"failures": [], "passed": true}`

## 1. 方法（差分栅格化，不假设 HUD 几何）
`A` = 只画边框的非背景像素集；`B` = 边框 + HUD；`occluded` = **逐像素比较颜色是否仍是原框线色**（`A` 中颜色改变者）；
结构交叉核验 = "HUD **面板矩形**内的框线像素"（两法必须相等）。`ratio = |occluded| / |A|`。

⚠️ **口径缺陷与修正（本轮实证）**：最初用 `A \ B` 是错的——HUD 不透明面板颜色同样"非背景"，
被覆盖的框线像素仍留在 `B` 里，导致把 76%–100% 的遮挡**严重低估为 ~0**；已改为逐像素颜色比较，
并以面板矩形交叉核验（`methods_consistent` 全为 `true`）。

## 2. 结果（9 用例 = 3 几何 × 3 布局；`limit = 0.10`）
| 几何 | 布局 | 框数 | 框线像素 | 被遮挡 | 遮挡率 | 判定 |
|---|---|---|---|---|---|---|
| `landscape_1280x720` | `far_bottom_right` | 1 | 2587 | 0 | 0.0 | WITHIN_LIMIT |
| `landscape_1280x720` | `top_left_under_hud` | 1 | 1927 | 1473 | 0.764401 | EXCEEDS_LIMIT |
| `landscape_1280x720` | `mixed_three` | 3 | 5281 | 1475 | 0.279303 | EXCEEDS_LIMIT |
| `portrait_720x1280` | `far_bottom_right` | 1 | 2607 | 0 | 0.0 | WITHIN_LIMIT |
| `portrait_720x1280` | `top_left_under_hud` | 1 | 1747 | 1747 | 1.0 | EXCEEDS_LIMIT |
| `portrait_720x1280` | `mixed_three` | 3 | 5173 | 1319 | 0.254978 | EXCEEDS_LIMIT |
| `oddw_683x384` | `far_bottom_right` | 1 | 1379 | 0 | 0.0 | WITHIN_LIMIT |
| `oddw_683x384` | `top_left_under_hud` | 1 | 1027 | 853 | 0.830574 | EXCEEDS_LIMIT |
| `oddw_683x384` | `mixed_three` | 3 | 2817 | 783 | 0.277955 | EXCEEDS_LIMIT |

- `max_occlusion_ratio = 1.0`；`mean = 0.378579`；
  零遮挡布局：`['far_bottom_right']`；超限几何：`['landscape_1280x720', 'oddw_683x384', 'portrait_720x1280']`
- 远端框（未与面板相交）遮挡**恰为 0**（不得虚报）；面板下框 76%–100%（真遮挡）。

## 3. 阈值语义（重要）
`limit = 0.1` 是**本仓库离线渲染告警阈值**，**不是** Wong/阶段7 冻结的验收指标，
也不代表任何板级指标；改阈值只改判定串。板级真彩目视下的 HUD 遮挡须板上窗口验证（NOT_RUN）。

## 4. 边界
- 只量化**框线像素**被 HUD 覆盖的比例，不含标签文字覆盖口径；输入为**合成**归一化坐标；
- **真实回放接入 / 板上动态映射 / 摄像头 = NOT_RUN**；**不接板卡**、不联网；PNG 供抽检，JSON 为权威；
- **G0/G1/G3/G4/G5 均未通过**。
