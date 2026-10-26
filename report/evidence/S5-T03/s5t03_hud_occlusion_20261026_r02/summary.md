# HUD 遮挡量化 RunId `s5t03_hud_occlusion_20261026_r02`

> 数字口径：本摘要逐项取自本包 `results.json` / `manifest.json` / `console/`（机器可读权威）；冲突以 JSON 为准。
> 本包为**元/过程包**（schema `gestureforge_s5t03_hud_occlusion_v1`）：**不适用** `gestureforge_s5t03_json_contract` 的 `artifact_kinds`。
> 标注：`input_scope_label = synthetic_replay`、`status = PRELIMINARY`。

- 被测代码提交（本包 `source_commit`）：`33a8f9423748…`（本包由**当前代码**重跑，套件日志同为当前基线）
- 本包独立套件日志：`Ran 116 tests` / OK（SHA `93f49f3ba66d…`）
- `checks = {"failures": [], "passed": true}`

## 1. 方法
`A` = 只画边框的非背景像素集；`B` = 边框 + HUD；`occluded` = **A 中颜色不再是原框线色**的像素（逐像素比较）；
结构核验 = "HUD **面板矩形**内的框线像素"，两法必须相等。`ratio = |occluded| / |A|`。
早期用 `A \ B` 是错误的（HUD 底色同样"非背景"）——会把 76%–100% 低估为 ~0，已由 `test_03` 永久锁死。

## 2. 结果（9 用例；`limit = 0.1`）
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

- `max = 1.0`；`mean = 0.378579`；
  零遮挡：`['far_bottom_right']`；超限几何：`['landscape_1280x720', 'oddw_683x384', 'portrait_720x1280']`

## 3. 阈值与边界
`limit` 是**本仓库离线告警口径**（非验收指标、不代表板级）；板级真彩遮挡 NOT_RUN；只量化**框线像素**（不含标签文字口径）；
**真实回放接入 / 板上 / 摄像头 = NOT_RUN**；不接板卡；**PNG 非验收依据**（仅人工抽检）、JSON 为权威；**G0/G1/G3/G4/G5 均未通过**。
