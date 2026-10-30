# DSH-20261031-018：阶段0–6 遗留任务卡（交 Codex）——R-03/R-05/R-08/R-09 + R-02 属你方项

- 发件：DSH 项目总控（阶段6 主控，Wong 授权）；收件：Codex 项目总控
- 时间：2026-10-31 00:5x（UTC+8）；依据：Wong「R-01 暂不解决；其他能解决的自己解决，不能解决的交给 Codex，写一个提示词」
- 我方正在做：R-10（文档勘误）、R-02-③（I/O delay 复核草案）、R-04（冷启动 VDMA 显示流）、R-07（相机接入）
- **R-01（吞吐）Wong 明确暂不解决**，不在本函范围

## 通用约束（全部任务）

- 不碰 `D:\FPGA_Competition` 主目录写入（信箱除外）；不写 `w6` 以外他方工作树；不 push；不写 QSPI；`ENABLE=0`
- 板卡由 **DSH 统一调度**：你方需要板窗须申请（我会写 OFFRED 租约行），**禁止自行开 hw_server/xsdb 会话**
- XSDB 入口用 `cmd /c "D:\Xilinx\2026.1\Vitis\bin\xsdb.bat" -eval "..."`（裸 `xsdb.exe` 会 `0xC0000135`）
- 冷启动流程：`ps7_init` **只跑一次**、**禁 `rst -processor`/`rst -system`**，PL 配置后用只读探测确认 PS-PL AXI
- 证据：新 RunId、`hash_basis=commit_blob`、过 `verification/check_manifest_hash_basis.py --mode strict`

## 任务卡 1（R-08）：w6 交接 OFFER（**先做，10 min**）

- 目标：在 `w6/.codex/STATE.md` 写正式 **OFFER 行**（11 字段），并把 19 项未提交改动归位（提交或声明归属）
- 验收：OFFER 行含 `任务/负责人/工作树分支/起始提交/允许修改范围/未提交改动归属/让出声明=OFFERED/心跳/证据入口/恢复命令/状态`；我方 CLAIM 后可记 `DONE`
- 若你方选择"不 OFFER、w6 保持只读归档"，请明确回复该结论，我方按"只读归档"记并关闭 R-08

## 任务卡 2（R-03）：M3 成对取样（阶段4 G5 前置）

- 目标：修 `m3_pair.py` 的 `state` 键缺陷（真实 XSDB 下 exit=2），在 2B 侧完成 M3 成对取样；并解释"47.3 s/帧 + heads 与参考 0 差异"的不自洽（需 2B 侧 ILA/回读；无 ILA 时用 JTAG 回读 + 多次采样替代）
- 基线：阶段4 冻结 `83c9284`；2B 侧归你方；板窗由我方开（约 9 min/窗）
- 交付：修好的脚本 + 新 RunId 证据 + 结论（M3 PASS/FAIL + 根因或明确 BLOCKED 理由）
- 验收：脚本在真实 XSDB 下 exit 0；M3 结论有可复核数据；不自洽项给出根因或明确未定

## 任务卡 3（R-05 / C2）：真实推理写端

- 目标：把 chain-lite/2B 解码结果写入结果块 `0x20800000`，**按冻结口径**（`docs/obsidian-project/02-方案设计/阶段6_交互控制_6D口径冻结_20261030.md`）：
  - 32 B 头 + 16 B 检测项（640×480 源坐标、`cls`、`score_q8`）
  - sidecar `S5X1` @ `+0x100`（`session_id`/`result_seq`/`result_time`/`seqlock`）
  - 业务状态映射（ERROR/TIMEOUT/NO_HAND/OK + 200 ms 门限）
  - **不改冻结 32 B ABI**
- 参考实现：我方 P3q 生产者 v2（`S5_PRODUCER_V2_FREEZE.md`，sha `e964397b…`）——建议复用其 `s5_pub_*` 封装，只替换"检测项来源"
- 交付：独立目录实现 + 单测（离线）+ 板上验证计划；板窗由我方开
- 验收：板上显示真实检测框；`box_crc` 与应用一致；`age_pub≤200 ms`；`state` 映射正确
- **注意**：若你方判断此任务 >1 天，请立即回报，我方用"最小实现（读 chain-lite 解码输出写块）"兜底

## 任务卡 4（R-09 / C3+C4）：测量学与独立复审

- **C3**：T6-A03 帧周期 P 的测量学 —— 事件定义绑定（真 SOF/显示刷新/推理完成）、测点、误差预算、采集程序；与已实测 P=16,673 µs（`fps_dis` 软件法，PARKPTR 切换沿 + GT）对齐；给出"为何该测法等价/不等价于真 SOF"的论证
- **C4**：对阶段5/6 我方证据做**独立复审**（只读）：`S5-T01` G3/G4/G5、`S6-T01` E1–E5、6-D 部分核验；输出 PASS/CHANGES_REQUIRED + 依据
- 验收：C3 方法论文档 + 采集程序（离线可跑）；C4 复审报告（明确被审版本与证据路径）

## 任务卡 5（R-02 属你方项）：阶段3 SEC / ILA

- ② task-11 完整 SEC `BLOCKED_NOT_RUN`：请说明是否仍为交付必需；若不必需，给"不适用"论证，我方转 Wong 裁决
- ④ 无 ILA（BASIC 许可）：给"无 ILA 条件下的替代调试/取证手段"建议（我方现用 UART + JTAG 只读 + GPIO 计数）

## 回报要求

每个任务：结论（PASS/FAIL/BLOCKED）+ 证据路径（新 RunId）+ 关键数字 + 退出码 + 限制；**不要**修改 Phase 5/6 冻结物；不要接管板卡。
本函记录由我方主目录持有方串行提交（已提交）。