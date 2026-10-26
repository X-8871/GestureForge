# S5-T03 多几何渲染验证 RunId `s5t03_multi_geometry_render_20261026_r02`

- 时间（UTC+8）：2026-10-26 22:52–22:53；执行方：DSH 阶段5 总控（w5 接管后）
- 范围：**离线**多几何渲染（不接板卡、不联网）；输入为**合成**归一化坐标；**不宣称任何关口通过**
- 命令与退出码：
  ```
  python -B scripts/stage5_t03/s5t03_multi_geometry_render.py --out report/evidence/S5-T03/s5t03_multi_geometry_render_20261026_r02   # exit 0
  python -B -m unittest scripts.stage5_t03.test_s5t03_multi_geometry_render \
      scripts.stage5_t03.test_s5t03_long_run_replay scripts.stage5_t03.test_s5t03_replay_display \
      scripts.stage5_t03.test_s5t03_skeleton                                                                  # Ran 75 tests, OK, exit 0
  ```

## 1. 覆盖的几何（同一组归一化框，四种画布）
| 几何 | 源 | 画布 | 映射（冻结参考） | 逐像素结果 |
|---|---|---|---|---|
| `landscape_1280x720` | 1280×720 | 1280×720 | `R.original_norm_to_display_px` | ✅ 相等（6029 px，缺失 0 / 多余 0） |
| `portrait_720x1280` | 720×1280 | 720×1280 | 同上 | ✅ 相等（6365 px） |
| `oddw_683x384` | 683×384 | 683×384 | 同上 | ✅ 相等（3217 px） |
| `canvas_683x384_k2_1920x1080` | 683×384 | 1920×1080 | `R.canvas_fit` + `R.original_norm_to_canvas_px`（整数倍 k 居中，不拉伸） | ✅ 相等（6417 px） |

判定方式：只画边框（`draw_labels=False`/`draw_hud=False`）时，**非背景像素集合恰好等于** `R.border_pixel_sets` 并集——
线宽（2 px 偶数居中）、取整（`round_half_up(v·(span−1))`）、钳位全部由冻结参考决定，**渲染层无第二套几何**。

## 2. 冻结几何数值（T5-01/T5-07 显示侧补充）
- **奇数宽 683×384**：`letterbox_geometry` → new **416×233**、offset **(0, 91)**、下补边 **92**、`asymmetric_padding=true`（非对称保留，未对称化）。
- **整数倍画布**：`canvas_fit(683,384,1920,1080)` → **k=2**、绘制 **1366×768**、offset **(277,156)**。
- 判别：画布-fit 若误用 exact 映射会得到**不同像素**（本包记录 `exact_vs_canvas_fit_differ=true`，并有用例锁死）。

## 3. 产物
```
s5t03_multi_geometry_render_20261026_r02/
├─ results.json        # 权威：四几何逐像素结果、几何数值、判别字段、限制
├─ keyframes/          # 8 张（每几何 2 张：overlay（带标签/HUD）+ border_only（仅边框））
├─ manifest.json       # 工具/参数哈希、checks、限制、NOT_RUN
└─ console/            # stdout.txt + command.txt + **本包独立** unittest_all.txt（75 项 OK）
```

## 4. 判别力自证（影子树变体，w5 未改）
| 变体 | 退出码 | 失败用例 |
|---|---|---|
| V0 基线 | 0 | 无（7/7 绿） |
| V1 画布-fit **误用 exact 映射** | 1 | `test_01`、`test_03` |
| V2 渲染层**自写 1 px 线宽** | 1 | `test_01`、`test_04` |
（脚本：`tmp/5/S5-T03/adversarial_multigeom.py`）

## 5. 诚实边界
- 输入为**合成**归一化坐标；本包只验证**显示层几何与绘制**，不验证采集/推理。
- 画布 ≠ 源分辨率时为**画布适配**（整数倍不拉伸）；**不代表**板级 HDMI 时序支持该分辨率（板级未验证）。
- 画布-fit 路径不含管线决策（用冻结 `R.canvas_fit` + `R.original_norm_to_canvas_px` 直接映射），已在 `results.json.geometries[].mode` 标注。
- **真实回放接入 / 板上动态映射 / 摄像头路径 = NOT_RUN**；PNG 仅供人工抽检，**JSON 为权威**；**G0/G1/G3/G4/G5 均未通过**。
