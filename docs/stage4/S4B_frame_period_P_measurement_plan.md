# 阶段4：帧周期 P 实测方案（供阶段6 `T6-A03`）

- 状态：**方案就绪 / 数值 `NOT_RUN`**。日期：2026-10-24（UTC+8）；所有者：DSH 阶段4 总控（本树 `D:\codex-worktrees\w4`）。
- 依据：`report/evidence/CTRL-DSH-HANDOFF/decisions/stage6_approval_receipt_20261023_r01.md`（`U6-13`：口径已批准 = `t_effective − window_complete`，**数值仍 `NOT_RUN`，待阶段4 实测帧周期 P 后填**；无实测数据不得填造）。
- 本轮**全离线**：未运行硬件、未装载位流、未打开 COM4/JTAG。本方案不产生 P 的数值。

## 1. P 的定义与用途

- **P = 帧周期**：同一会话内相邻两帧「首个有效像素到达 PS 单调计时器」时刻之差，单位秒（证据里同时给 ns）。
- 用途：阶段6 `U6-13` 的交互延迟基准 `t_effective − window_complete` 需要按帧换算窗口完成时间（既有示例在 30 fps 假设下得第 8 帧 233.1 ms）；**该假设不得代替实测 P**。`T6-A03` 数值在 P 实测并被填入证据前保持 `NOT_RUN`。
- 口径边界：P 是**采集侧**帧节奏，不等于推理耗时、也不等于显示刷新率；三者分别测量、分别报告。

## 2. 测量方法（硬件窗口内执行）

1. **前置**：阶段4 板级按 `CDX-20261023-018` §4 八类门禁具备、main 已签发 `S4-B-REAL-02B::s4b_hardware_session_handoff`（scope `S4B_PS_TENSOR_DIAGNOSTIC`）、w4 已写对应 `…_claim` 行；本轮依 `CDX-20261023-019` 不申请、不保留窗口。
2. **来源必须是实时彩色**（`camera_live_colour`，`source_kind=camera`）。抓帧回放（`camera_capture_replay_colour`）**不得**作为 P 的数值来源，只能用于核验采集→时间戳链路是否可用。
3. **计时器**：PS 单调计数器（建议 CPU 全局定时器 / `XTime`）。必须先在证据中记录 `timer_freq_hz`（实测或从 BSP 常量核对），未确定频率即停止，不得用墙钟或 host 时间代替。
4. **采样点**：在每帧「首个有效像素」的可观测事件处取 `capture_time_ns`（实现为采集完成中断/SOF 相关事件；具体抓手在硬件窗口内按实际软件结构确定并记录）。**不得**用注入起点、工具提交时刻或显示刷新时刻充当。
5. **连续性**：连续采集 **≥1000 帧**同一会话（`session_id` 不变、`frame_id` 单调 +1、不复用不回绕）。丢弃帧必须逐帧记录原因（DROPPED/TIMEOUT/CRC 失败/重复/回退），不得静默剔除后再统计。
6. **统计口径**（只在合格帧上计算，并同时保留原始逐帧序列）：
   - `p_mean_ns`、`p_median_ns`、`p_p95_ns`、`p_min_ns`、`p_max_ns`、`p_std_ns`、`jitter_ratio = p_std_ns / p_mean_ns`；
   - 合格帧数 `n_valid`、「相邻间隔数」`n_intervals = n_valid − 1`；
   - 若 `n_valid < 1000`，结果状态只能是 `INSUFFICIENT_SAMPLE`，**不得**取均值冒充 P。
7. **停止条件**：流中断/复位/死锁、计时器频率未知、丢帧比例超过 5%、或出现重复/回退帧未解释 → 立即停止，保留失败证据并以新 RunId 重测。

## 3. 必填证据与绑定

- 证据落点：`report/evidence/<task_id>/<new_run_id>/`（新 RunId，未存在）。
- 部署绑定：无补偿 SOF SHA-256 `7cb33068…ce48710`、XSA 身份、运行 ELF `an5642_j11cmos2_v10_read.elf` SHA-256 `1457cda4…2306073`；三者与现场核对结果。
- 采集绑定：契约 `s4-shared-io/1.2.0`；1280×720、stride 3840 B/行、传感器 RGB565、RAW `pixel_format=BGR888` / `channel_order=B/G/R`、平台 `byte_order=little`、`timer_freq_hz`、`clock_domain`。`byte_order` 不表示像素通道顺序。
- 逐帧序列：`frame_id`、`capture_time_ns`、`frame_integrity`（CRC32/SHA-256 + 字节数）、丢弃/重复原因。
- 源帧哈希：至少绑定用于交叉核验的若干帧（建议 ≥100 帧）的逐帧摘要。
- 机器模板：`docs/stage4/s4b_frame_period_p_evidence_template.json`。
- 校验器：`python -B scripts/stage4_s4b/validate_frame_period_p_evidence.py --record <证据 JSON>`，退出码 0 = 通过、1 = 拒绝、2 = 输入错误。

校验器**结构性地禁止填造**：

| 情形 | 结果 |
|---|---|
| `status=NOT_RUN` 但 `value` 非空 | **拒绝**（禁止填造） |
| `status=MEASURED` 但 `n_valid < 1000` | **拒绝** |
| `status=MEASURED` 但来源不是实时彩色（回放/合成/注入） | **拒绝** |
| `status=MEASURED` 但缺部署绑定/计时器频率/逐帧序列或八类门禁未齐 | **拒绝** |
| 统计量自相矛盾（如 median 不在 [min,max] 内、p95 < median） | **拒绝** |

## 4. 与阶段6 的接口

- 阶段4 实测并把数值填入证据后，阶段6 `T6-A03` 才可由 `NOT_RUN` 变为可计算；阶段6 必须**只读消费**该证据并记录其 RunId 与哈希。
- 在 P 实测前，阶段6 `U6-13` 的结论只能是「口径已批准、数值 `NOT_RUN`」。
- 阶段4 不得代阶段6 填其行为表，也不得把本方案当作已执行证据。

## 5. 限制

- 本方案本身不是实测证据，不含任何 P 数值。
- 不改变阶段6 的 24 项参数与 `stale_age_limit=200ms`（后者已在阶段4 共享契约中同源固定）。
- 真实采集回归的其余要求（≥100 帧真实网络输入逐值比对、≥30 分钟且 ≥1000 次有效推理）另见阶段4 契约与 RAW 系统 G0 缺口登记表 `G-17/G-18`。
