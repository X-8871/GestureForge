# S5-T01 阶段5 上板 bring-up 运行书（离线准备件；**尚未执行**）

> 状态：`BLOCKED_NOT_RELEASED`。硬性前置（2B 书面让出 JTAG/COM4 + DSH 宣布空档）**未满足**，本文件只做离线准备，**未连接板卡、未启动 hw_server、未写任何寄存器**。门禁证据：`report/evidence/S5-T01/s5t01_prereq_20261022_r02/`。
> 本运行书不构成阶段5 开工、G1/G2/G3 通过或任何验收。

## 1. 硬性前置（fail-closed，必须先过）

1. `codex_mailbox/` 出现**新的书面让出/释放**通知（编号晚于最近占用通知 `CDX-20261022-006`），且 2B 注明冻结提交、实际释放时间、由谁启动服务。
2. DSH 项目总控据该让出**宣布硬件空档**（主 STATE 记录）。
3. 现场无 `hw_server`/`vivado`/`xsdb`/`vitis`/`xsim` 进程；六棵树无 `index.lock`。
4. 运行门禁并留存 JSON：
   ```bash
   python -B scripts/stage5_t01/check_hardware_gate.py --out report/evidence/S5-T01/<run_id> --release-id <让出通知编号>
   ```
   退出码 **0=GO**；**1=BLOCKED（禁止上板）**；2=环境错误。门禁采用 fail-closed：**进程枚举失败也判 BLOCKED**，且“没看到进程”**不作为**让出依据。

## 2. 输入（只读引用阶段3 灰度 provisional freeze，不复制其技术事实）

| 项 | 内容 | 入口 |
|---|---|---|
| 部署位流（首选） | **标准亮度灰度** bit `44e609cc…` / XSA `90e1bdee…`（板上测 `|R−B|=0.0`、近中性；亮度式 `Y=(77R8+150G8+29B8)>>8`） | `D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_stdluma_20261022_r01\`；收尾清单 `…\t05_stage3_closeout_20261022_r01\manifest.json` |
| 备选 | 纯绿灰度 bit `2f72aaa4…`（仅当首选不可用时使用，须在 manifest 记理由） | `…\S3-T05\t05_gray_board_20261021_r01\` |
| 视频源图案 | 传感器内置图案：写 `0x503D`（v12 工具，**仅易失**）→ 结构化图案（灰度下为亮度条），便于核对叠框位置与逆映射 | `…\S3-T14\v12_bars_freeze_tool_20261022_r01\`（含“使用前须确认硬件占用未让出”） |
| 取帧 | v11 变体（停 S2MM + 保持） | `…\S3-T05\t05_sw_v11_20261022_r01\` |
| 板上现状（阶段3 收尾时） | 标准亮度灰度 + v10_read、实时、无 HALT —— **上板前必须现场只读复核，不得复用旧状态** | 同上收尾清单 |

- 无摄像头方案：视频源 = 冻结灰度位流 + 传感器内置图案；**视频源零新增 PL**。
- 用完必须把 `0x503D` **写回 `0x00`**（v12 工具的恢复步骤），并记录回读值。

## 3. 叠框实现路径（运行前必须二选一并写入 manifest 的 `overlay_path`）

| 路径 | 说明 | 前置/风险 |
|---|---|---|
| **P1 PS 软件叠框（默认建议）** | 冻结位流零改动；PS 按注入计划把框/标签像素写入送显缓冲 | 需先只读核对送显缓冲**布局、地址与所有权**（引用阶段3 软件既有事实，**不得猜地址**）；须在帧边界写入或使用独立缓冲，否则与 VDMA 读竞争致撕裂 |
| P2 PL 叠框 | 新增 PL 叠框逻辑并重建位流 | 工作量与新位流/XSA 哈希绑定；与“视频源零新增 PL”不冲突，但本轮任务卡的 G1/G2 目标用 P1 即可先达成 |

- 若无法确认缓冲布局/所有权：**停止并报告**，不猜地址、不改阶段3 工程。

## 4. 脚本化检测结果注入

- 注入计划为 JSON（逐帧）：字段名与 S5-A 契约一致（`frame_id`/`state`/`detection_count`/`detections[]`(`class_id`/`class_name`/`score`/`xyxy`/`source_order`)/`stale`/`dropped_frames` 等）。
- 离线先校验（可重复、无需硬件）：
  ```bash
  python -B scripts/stage5_t01/validate_injection_plan.py --plan docs/stage5/s5t01_injection_plan_example.json
  ```
  退出码 0=可用；1=计划不合法；2=输入错误。校验内容：契约必需字段、`state` 合法性、零框语义、≤15 框、类别顺序与 `class_name` 一致性、分数区间、正面积、坐标经冻结逆映射可落像素。
- 坐标路径：**只用**契约 `xyxy`（归一化原图坐标，阶段4 语义）；绘制走 `verification/s5_display_geometry_reference.py` 的 `original_norm_to_display_px` + `border_pixel_sets`；**禁止**在板上代码或脚本里重写几何/取整规则。

## 5. 测量定义（起止事件，沿用 S5-A 契约）

- **采集 FPS**：帧首发有效像素写入帧缓冲 → 下一帧同一事件；声明整段平均或滑动窗口；接收帧数与有效帧数分别给出。
- **结果/注入更新率**：注入记录发布 → 该记录提交送显；与采集/显示帧率分列。
- **显示 FPS**：输出帧起始 → 下一帧起始。
- **两个年龄分别记录**：`age_result_ns = t_overlay_commit − t_result_publish`；`age_frame_ns = t_overlay_commit − t_capture(frame_id)`；语义 B 下“端到端延迟”只能指 `age_frame`，**不得**伪称同帧。
- **预热/丢帧/超时/过期清除**：分别计数与清单，不得用平均值掩盖；过期清除每结果只计一次并记录原因（`stale_flag`/`age_frame_exceeds_limit`/`both`）。
- 所有时间同一 PS 单调时钟；事件写帧级日志（`frame_id`、事件类型、时间戳），统计量必须可由日志复算。

## 6. 验收表（G1/G2 + G3 部分；逐项标 PASS/FAIL/BLOCKED/NOT_RUN/NOT_APPLICABLE）

| 用例 | 内容 | 备注 |
|---|---|---|
| T5-01 | 非方形视频与补边逆映射 | 阶段3 源为 1280×720（非方形）→ 可验；竖屏/683×384 无源则记 NOT_APPLICABLE 并说明 |
| T5-02 | 边缘框/四角/部分越界/零面积 | 注入计划覆盖；零面积不绘制 |
| T5-03 | 多框（≤15）与零框（无手） | 零框不画框、`boxes=0`，与过期/丢失区分 |
| T5-04 | 过期清除 | `age==limit` 不过期；`limit+1` 过期且计数+1 |
| T5-05 | ≥100 帧结果—帧号对应 | 记录五元组，可按 `frame_id` 索引 |
| T5-06 | 分数/置信度用词 | 界面/日志字段名为 `score`，无依据不出现“置信度” |
| T5-08 | FPS/延迟分别测量 | 真实统计（非离线占位）；写明起止事件与分母口径 |
| T5-09 | 连续 30 分钟无死锁 | 受硬件窗口限制；未做则 NOT_RUN 并说明 |
| T5-11 | 预热/丢帧/超时不隐藏 | 注入故障与计数单列 |
| T5-12 | 显示语义一致性 | 单包内 `display_semantics` 唯一 |

## 7. 证据布局（`report/evidence/S5-T01/<run_id>/`）

- `hardware_gate.json`（门禁结论与 release-id）、`bit_xsa_hashes.json`（位流/XSA 实际哈希与来源 RunId）、`commands.json`（命令 + **真实退出码**）、`console/*.txt`、`overlay_path` 声明、截图或照片（含实测时间）、数值表（CSV/JSON：逐帧 FPS/延迟/计数）、`manifest.json`（源码/工具/输入/产物哈希、限制、未执行项）、`summary.md`（逐项状态）。
- 不适用项须写理由；失败证据保留不删；一律新 RunId，不覆盖既有运行。

## 8. 停止条件与收尾

- **停止**：门禁非 GO；无法确认缓冲布局/所有权；VDMA sticky `0x00015810` 复现且未定性；出现停帧/花屏无法解释；需要烧录 QSPI 或长期驻留 `hw_server`；与 2B/阶段3/阶段4 抢占硬件。
- **收尾**：`0x503D` 写回 `0x00` 并回读确认为 0；退出 `hw_server`（不驻留）；板卡恢复到已知状态（记录位流指纹）；在信箱/STATE 记录实际释放时间与占用窗口。
- **禁止**：改 `w4`/`dbdf`/`w2b`/主树；写两个 mailbox 目录；烧录 QSPI；长期驻留 `hw_server`；并行重型任务；结束他人进程。

## 9. 复现/恢复命令

```bash
# 门禁（每次上板前必跑）
python -B scripts/stage5_t01/check_hardware_gate.py --out report/evidence/S5-T01/<run_id> --release-id <让出编号>
# 注入计划离线校验
python -B scripts/stage5_t01/validate_injection_plan.py --plan docs/stage5/s5t01_injection_plan_example.json
# 上板命令/脚本在门禁 GO 后按本轮 run 记录逐步执行；执行前先只读复核板上位流指纹与传感器寄存器
```

- 本运行书与门禁脚本均为**离线准备件**；`s5t01_prereq_20261022_r02` 的证据显示当前 `decision=BLOCKED`（缺书面让出），进程枚举成功且无硬件进程。