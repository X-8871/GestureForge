# multi_geometry RunId `s5t03_multi_geometry_render_20261026_r02`

> **数字口径声明**：本摘要的提交号、测试数、耗时、计数与不变量**逐项取自本包**
> `results.json` / `manifest.json` / `console/run.txt` / `console/unittest_all.txt`（机器可读权威）；
> 摘要若与之冲突，**以 JSON/日志为准**。本摘要由生成器按上述文件派生，不做模板复制。

- 生成时刻（本包 `results.json.generated_utc8`）：2026-10-26T22:50:51+08:00
- 被测代码提交（本包 `source_commit`）：`e6ac5af28333…`
- 状态标签：`PRELIMINARY`；输入范围：`synthetic_replay`
- 本包独立套件日志：`Ran 75 tests` / OK（日志 SHA `74f27caeba1c…`）
- 命令：
  ```
  python -B scripts/stage5_t03/s5t03_multi_geometry_render.py --out report/evidence/S5-T03/s5t03_multi_geometry_render_20261026_r02
  ```

## 1. 覆盖的几何（同一组归一化框）
| 几何 | 源 → 画布 | 映射 | 逐像素 |
|---|---|---|---|
| `landscape_1280x720` | [1280, 720] → [1280, 720] | `R.original_norm_to_display_px (fit=exact)` | ✅ 相等 （6029 px，缺 0 / 多 0） |
| `portrait_720x1280` | [720, 1280] → [720, 1280] | `R.original_norm_to_display_px (fit=exact)` | ✅ 相等 （6365 px，缺 0 / 多 0） |
| `oddw_683x384` | [683, 384] → [683, 384] | `R.original_norm_to_display_px (fit=exact)` | ✅ 相等 （3217 px，缺 0 / 多 0） |
| `canvas_683x384_k2_1920x1080` | [683, 384] → [1920, 1080] | `R.canvas_fit + R.original_norm_to_canvas_px (整数倍 k 居中)` | ✅ 相等 （6417 px，缺 0 / 多 0） |

## 2. 冻结几何数值
- 奇数宽 683×384：`{"src_width": 683, "src_height": 384, "new_width": 416, "new_height": 233, "offset_x": 0, "offset_y": 91, "pad_right": 0, "pad_bottom": 92, "asymmetric_padding": true}`
- 整数倍画布：`{"scale_k": 2, "drawn_width": 1366, "drawn_height": 768, "offset_x": 277, "offset_y": 156}`
- `numeric_checks`：{"oddw_new_416x233": true, "oddw_offset_0_91": true, "oddw_pad_bottom_92": true, "oddw_asymmetric": true, "canvas_fit_k2": true, "canvas_fit_1366x768": true, "canvas_fit_offset_277_156": true}

- `checks = {"failures": [], "passed": true}`；关键帧 8 张

## 3. 限制（本包自述）
- 输入为合成归一化坐标；只验证显示层几何与绘制，不验证采集/推理。
- 画布 ≠ 源分辨率时为**画布适配**（整数倍不拉伸）；**不代表**板级 HDMI 时序支持该分辨率。
- 画布-fit 路径不含管线决策（用冻结 `R.canvas_fit` + `R.original_norm_to_canvas_px` 直接映射）——已在 §geometries 标注。
- 关键帧 PNG 供人工抽检；JSON 为权威。G0/G1/G3/G4/G5 均未通过。

## 4. NOT_RUN（本包自述）
- 真实回放接入（无阶段4 冻结回放结果包）
- 板上动态映射与绘制（本轮不接板卡）
- 板级 HDMI 时序对非 1280×720 分辨率的支持（未做板上验证）
- 摄像头真实采集路径
- T5-10 板上回归
