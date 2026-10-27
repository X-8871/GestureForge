# S5-T03 **带框**阶段4 冻结回放包离线消费 RunId `s5t03_stage4_positive_replay_20261027_r01`

> 上游：`s4t27_replay_positive_20261027_r01`（S4-T27-REPLAY-POSITIVE，
> verdict `FROZEN_REPLAY_ONLY_WITH_DETECTIONS`，生成于 2026-10-27T13:34:08+08:00）；
> 本包=阶段5 的**离线**消费（Wong 2026-10-27 告知"带框的包好了"）。
> 数字全部由本包产物派生；**不是**板上/实物/实时结论。

## 1. 完整性（按上游索引**自己的**规则复算）
| 项 | 登记 | 实测 | 结论 |
|---|---|---|---|
| `package_sha256` | `988f2cae79cc4bfb…` | `988f2cae79cc4bfb…` | OK |
| `gate_result_sha256` | `dcf3455048252b3c…` | `dcf3455048252b3c…` | OK |
| 契约 `json_sha256` | `7228f51350feb0c6…` | `7228f51350feb0c6…` | OK |

## 2. 逐帧结果（契约字段）
- `frame_id=1`、`result_seq=1`、`session_id=1396854863`（replay-only 合成标识）
- 状态 `PRESENT`；检测 **1** 框；候选（阈值前）`2`、NMS 后 `1`
- 框：`class_id=0`（fist）`score=0.7697`
  `xyxy=[0.2481297045148163, 0.3713942307692308, 0.34786113088325127, 0.4362980769230769]` → **`xyxy_px={'x1': 317, 'y1': 267, 'x2': 445, 'y2': 314}`**（画布 1280×720，按冻结参考换算）
- **包内交叉核对**：`boxes[0].xyxy` 与 `detections.t29_reference_predictions[0].xyxy` 逐位一致 ⇒ **True**

## 3. 显示五元组（如实标注不可定义项，不伪造）
```
{
  "displayed_frame_id": 1,
  "result_frame_id": 1,
  "age_result_ns": null,
  "age_frame_ns": null,
  "display_semantics": "B_latest_result_overlay",
  "display_eligible": true
}
```
`age_result_ns`/`age_frame_ns` 为 **null**：冻结包为 `FILE_INJECTION`（`capture_time_ns=0` 哨兵）且**无单调发布时钟** ⇒ 不可定义
（基准声明见 `five_tuple.age_basis`）；**未**用 `injection_start_ns` 冒充实测采集时间。

## 4. 命令与真实退出码
| 步骤 | 退出码 |
|---|---|
| 带框包消费（`s5t03_stage4_positive_replay.py`） | **0** |
| 新增测试（`test_s5t03_stage4_positive_replay`，5 项含篡改/交叉核对/标签守卫） | **0** |
| 全量套件（12 模块） | **0** |

## 5. 限制与 NOT_RUN（不得外推）
- **离线回放**：不是 PL 真实运行、不是 UART 实收、不是真实摄像头采集质量或颜色；
- 时间口径：`capture_time_ns` 为 0 哨兵 ⇒ `end_to_end_latency_ns` **不可定义**；`age_*`/`stale` 不可定义；
- `session_id` 为 **replay-only 合成标识**（非 PS 分配会话号）；
- 板上真实回放仍需硬件 OFFER/CLAIM + **八类门禁（当前 0/8）**；
- **NOT_RUN**：板上真实回放、真实摄像头路径、B5 计数流、B6 30 分钟长跑、真彩目视、T5-10、P/4-D/G3/G4/G5 判定；
- **§4.5/§7.3 未关闭**。
