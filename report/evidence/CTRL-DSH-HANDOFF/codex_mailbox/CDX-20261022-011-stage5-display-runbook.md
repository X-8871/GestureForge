# 阶段5操作文档：动态显示、帧关联、延迟与持续运行

编号：CDX-20261022-011；r01；2026-10-22（UTC+8）。执行方：现有阶段5总控。先读[总入口](CDX-20261022-008-execution-index.md)。

## 1. 已有进展与本次起点

工作树 `D:\codex-worktrees\w5`，分支 `stage5-display-prep`。
本次后续快照HEAD `e4533e1d3b9ef1a80f1350e36f7fb479dbc88dc6`，STATE更新18:50；本阶段仍IN_PROGRESS，原负责人继续独占写入。

必读：
- `docs/stage5/S5A_stage5_display_g0_spec_v2.md`、`s5a_stage5_display_g0_fields.json`
- `docs/stage5/S5T01_stage5_board_bringup_runbook.md`
- `report/evidence/S5-T01/s5t01_board_overlay_20261022_r01/summary.md`
- `report/evidence/S5-T01/s5t01_board_numcheck_20261022_r01/summary.md`
以上均相对w5。

已完成：PS合成背景+预计算框写送显缓冲，板上13/13像素检查；两个UI缺陷已修。
尚未完成：display_fps/延迟、T5-04板上过期边界、T5-05≥100帧关联、T5-11故障计数、T5-09长跑；当前不是阶段5验收通过。
**现有板上P1没有逆映射逻辑，框由主机预计算，不能据此宣称板上动态后处理/叠框完整通过。**

## 2. 5-A：整理已完成项，防止重复与误判

1. 核验最新状态和文件归属，沿现有S5-T01继续；不得重置活跃工作树。
2. 原运行书“尚未执行”及传感器图案入口已经过时：摄像头不在位，0x503D写入未成功。本次输入只用PS合成图或阶段4冻结注入源。
3. D-1为u8斜坡回绕黑带，当前平滑斜坡已修；D-2为标签/HUD压盖，已避让并最后绘HUD。
4. 保留修复后逐像素证据；另检查HUD覆盖用例5红框顶边x23..123的副作用，按布局规格判断可接受性，不能把“标签不重叠”当所有遮挡都消失。
5. 更新本阶段测试矩阵：已离线通过、已板上通过、待板测逐项区分，按T5-01…T5-12已有编号继续。

## 3. 5-B：建立可信帧事件与FPS测量

**待实现/验证**：可靠事件采集。现有FrmCntIrqEn/SR轮询曾不推进，不能用循环次数推算实际FPS。

1. 选定并审查事件源：MM2S帧完成中断+GIC ISR，或可验证的VTC/显示帧事件；根据硬件连接及IP语义确认它实际测量的是传输完成、视频刷新还是呈现。
2. 使用PS单调计时源（如当前平台XTime），记录计数频率、单位转换、回绕处理；中断服务只做必要计数/时间记录，日志异步导出。
3. 先用短动态序列验证事件持续推进，再比对显示状态/视频观察；事件不可靠即NOT_VERIFIED，不报推测值。
4. 分开记录：
   - video_refresh_fps：扫描/视频事件频率；
   - display_fps：按本阶段冻结语义定义的显示帧完成率；
   - unique_frame_update_fps：不同输入frame_id实际更新率；
   - inference_fps：真实推理完成率。
   同一静态帧反复刷新不得当作高帧率推理。
5. FPS统一用指定窗口的完成事件数/单调时间间隔；保留首末时间、事件数、窗口及预热处理，可从原始日志复算。
6. 延迟只报告实际测到的边界：overlay_commit是提交事件，不能改称光子到屏幕。需要物理呈现结论时增加经验证的显示/外部测量方法。

输出：计时/中断实现、单元与短程板测、原始事件日志、复算统计和独立审查。

## 4. 5-C：≥100帧真实消费与动态叠框

1. 消费阶段4冻结的PS侧结果与输入契约。UART方案B缺失的时间/状态字段从PS记录取得，不能声称这些来自UART。
2. 明确本次显示语义：同帧延迟显示或当前画面叠加最新结果。整个实验包语义唯一；若变更则新配置/RunId。
3. 为至少100帧逐帧记录五元组：
   `(displayed_frame_id, result_frame_id, age_result_ns, age_frame_ns, display_semantics)`。
4. 用顺序帧、跳帧、迟到、重复/乱序结果、零框、多框和边缘框测试。显示frame_id不得强行改成result_frame_id掩盖错配。
5. 从动态结果实际执行坐标映射/绘制并验证；P1预计算框只能保留为显示通路基线。
6. 数值层沿用冻结2A容限：离散字段完全一致、score/归一化坐标绝对误差≤1e-6；像素层按S5A-G0-v2，逆映射参考≤1px、绘制保真≤1px及线宽±0.5px、文本分数≤1e-3。引用参考版本/哈希；若正式G0修订，记录批准依据。
7. 覆盖非方形1280×720、720×1280、683×384的离线几何测试；板上显示模式使用已核验分辨率，不假定这些分辨率都能直接驱动现有HDMI时序。

## 5. 5-D：过期、异常、HUD和长跑

1. 与阶段4共享同一过期阈值和PS时基。现有200ms在阶段5已使用、阶段4仍为草案：先在正式G0关闭该不一致，不另造第二常量。
2. 对 `age==limit`、`age==limit+1`、显式stale_flag执行板上边界测试。
   当前契约：`stale_effective = stale_flag OR age_frame > limit`；每结果只计一次，原因留日志。
3. NO_HAND合法零框显示boxes=0；TIMEOUT/ERROR/过期清除分别记录，不把错误冒充无手。
4. 对HUD13字段逐项核对：capture_fps、inference_fps、display_fps、inference_time_ns、age_result_ns、age_frame_ns、frame_id、boxes、stale_cleared、dropped_frames、timeouts、warmup_state、display_semantics。
   无摄像头时capture_fps不可用；注入时间不能假称采集时间。缺失值按正式契约标示，不能用0伪装实测。
5. 在注入源+真实阶段4输出配置下连续≥30分钟，验证无显示/推理死锁、计数可复算、无旧结果误用；留连续视频及原始日志。仅合成结果长跑可验显示子项，不能验真实推理集成。
6. 注入可控的丢帧/超时/坏结果，核对T5-11计数不隐藏；每个错误预期由G0规定。
7. 新摄像头接入后，对真实采集路径重做帧关联、时延和适用30分钟联调，并回归阶段4数值链。

## 6. 可复用命令与需修订的工具

在w5执行，输入/输出路径和唯一RunId事先核验：

~~~bash
"$PYTHON" -B scripts/stage5_t01/check_hardware_gate.py --out "report/evidence/S5-T01/$RUN_ID" --release-id "$RELEASE_ID"
"$PYTHON" -B scripts/stage5_t01/validate_injection_plan.py --plan "$INJECTION_PLAN" --json
"$PYTHON" -B scripts/stage5_t01/decode_mrd_rows.py --log "$DUMP_LOG" --json "$NEW_REPORT"
"$PYTHON" -B scripts/stage5_s5b/run_s5b_evidence.py --run-id "$RUN_ID"
pwsh -File scripts/stage5_s5c/run_s5c_evidence.ps1 -RunId "$RUN_ID"
~~~

RELEASE_ID必须是当前有效释放记录；门禁通过不自动授予硬件使用权限。INJECTION_PLAN需按真实任务填写，例子不是冻结计划。DUMP_LOG来自已获授权的真实采集；NEW_REPORT必须不存在。PowerShell 7及Python依赖先核验；最后两条会生成证据，仅在相应回归必要时执行。

`scripts/stage5_t01/build_p1_app.sh`现有构建会清建固定 `tmp/5/S5-T01/p1_app/build`。**不要在活动构建或未保全产物时重跑**；负责人先将本轮构建改为新RunId隔离目录/明确安全构建路径并审查，再把最终真实命令登记到阶段运行书。旧bit/ELF保留用于恢复，不覆盖。

目前没有经本包验证的动态帧计数、100帧真实结果消费和长跑一键命令。上述能力先实现、审查、记录命令后再板测；不得用现有照片分析脚本替代动态验证。

## 7. 退出标准

- [ ] 两个已修UI问题及HUD覆盖副作用按规格复核。
- [ ] 可信事件下FPS/延迟可复算，单位和计时边界清楚。
- [ ] ≥100帧五元组、真实动态映射、过期边界、异常计数全部验证。
- [ ] 注入集成与摄像头集成证据分开；完成所需30分钟运行及阶段4回归。
- [ ] 接口、源码、bit/XSA/ELF、布局、输入和日志版本一致，独立审查通过。
- [ ] 全部适用条件满足后才判阶段G4/G5；向阶段6交付可消费的显示语义、年龄和动作显示接口。
