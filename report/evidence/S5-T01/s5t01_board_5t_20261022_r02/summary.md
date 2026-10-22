# S5-T01 §4/T5-05 ≥100 帧结果消费 RunId `s5t01_board_5t_20261022_r02`

- 时间（UTC+8）：2026-10-22 19:4x
- 依据：`CDX-20261022-014 §4`（5-C）中**与阶段4 无关**的显示侧子项：≥100 帧逐帧五元组、故障计数、动态映射执行
- 被测件：`s5t01_frames_r05b.elf` SHA256 `4260d20a138e3a88d2a9cd8f6b74ef6ba85070cc98542e459b7ad197960aada5`（rev r05，`S5_FRAMES_MODE=1`）+ 冻结灰度位流 `44e609cc…c4afb`（易失）
- 结论：**120 帧结果流已板上消费并逐帧记录五元组；10/10 校验 PASS**（序列与调度模型完全一致、计数一致、语义/年龄/零框/过期规则一致、FPS 可复算）

## 1. 本轮做的语义（与契约一致）

| 项 | 取值 |
|---|---|
| 五元组 | `(displayed_frame_id, result_frame_id, age_result_ns, age_frame_ns, display_semantics)` 逐帧 UART 打印 |
| `display_semantics` | **B**（最新结果叠加），逐帧断言唯一 |
| 帧号改写 | **禁止**：`displayed` 严格 +1；`result` 可为重复（DUP）或乱序（OOO），**如实记录** |
| 过期 | `age_result_ns > 200 ms`（与契约同源常量）⇒ 不画框、`stale_cleared+1`、HUD `STALE` |
| 零框 | `boxes=0` 合法，与过期可区分（过期⇒stale=1） |
| 故障计数 | warm / DROP / TIMEOUT / DUP / OOO 分别计数，**不隐藏**（T5-11 显示侧） |
| HUD | 13 字段（§5.4），缺失值 `NA`；`occ=` 每帧记录 HUD 面板覆盖的框线像素数 |

## 2. 调度模型（确定性、可审阅）

`k=0..119`：`case=k%6`；`age_result = 250ms（k%7==0）否则 k·1ms`；`age_frame = age_result+5ms`；`warm = k<9`；
`DROP: k>9 且 k%17==0`；`TIMEOUT: k>9 且 k%19==0`；`DUP: k>9 且 k%23==0`（沿用上一条 result）；`OOO: k>9 且 k%29==0`（result=k-3）。

## 3. 实测与校验（`console/frame_stream_verify.json`，exit 0）

| 校验 | 结果 |
|---|---|
| 完整轮数 / 运行时长 | 2 个完整轮（+ 抓取窗口内截断轮），44.72 s |
| `(displayed,result)` 序列与模型**完全一致** | PASS |
| 计数与模型一致 | PASS：displayed=107、stale=17、dropped=7、timeouts=6、dup=5、ooo=4、warmup=9、uniq=101 |
| `semantics` 唯一 B / `age_frame>=age_result` / `stale⇒boxes=0` / `stale⇔age>limit` | PASS |
| 观测模式 vs 标记计数可解释 | PASS（OOO 目标撞上一条结果时观测上表现为重复，逐条列出） |
| FPS 可复算 | PASS：`displayed/elapsed_ms` 与板上打印一致（每轮 14.9 s ⇒ display 7.1 fps、unique 6.7 fps） |

- `occ_max=2133` 像素：**HUD 面板遮挡框线像素的实测最大值**（用例 3 的 15 框时最严重）；这是 §2.4 要求的"遮挡量化"，不再把"标签不重叠"当成"没有遮挡"。
- 历史负向证据：`../s5t01_board_5t_20261022_r01/` 保留首轮（`elapsed_ns` 以 `%u` 打印被截断、dup/ooo 观测口径未建模）——**不覆盖、不删除**。

## 4. 未完成 / 限制（不冒充）

- **result 流是合成的**（非阶段4 冻结输出）：只覆盖**显示侧消费语义**（五元组、年龄、过期、零框/多框、计不可隐藏），**不**证明与阶段4 推理链路的集成；后者待阶段4 提供冻结结果后再做（§4 依赖项）。
- `unique_frame_update_fps` 是 **result-frame_id 级**（本轮已可算 6.7 fps），**不是**推理完成率；`inference_fps` 仍为 `NA`。
- 动态映射：框像素仍由宿主端用**冻结参考实现**预计算后嵌入，板上无逆映射逻辑（§4.5 要求"从动态结果实际执行坐标映射"的**板上实现**仍未做；本轮只验证显示侧消费与绘制保真）。
- 未做：阶段4 真实结果注入、跳帧/迟到/重复结果的**跨进程**注入（本轮为进程内调度）、T5-09 长跑（另一 RunId）。

## 5. 证据文件
- `console/uart_frames.log`（原始 UART：`S5_5T`×331、`S5_5T_SKIP`×39、`S5_5T_SUMMARY` 轮次、`S5_P1_*`）
- `console/frame_stream_verify.json` / `frame_stream_stdout.txt`（10/10 PASS，exit 0）
- `console/capture_frames.txt`、`console/build_r05b.log`、`console/input_hashes.txt`
- 校验器：`scripts/stage5_t01/verify_frame_stream.py`