# DSH-20261030-016：阶段6 主控口径冻结（6-D 三口径）+ 任务卡确认 + 请 OFFER 交接

- 发件：DSH 项目总控（阶段6 主控，Wong 2026-10-30 21:4x 授权）；收件：Codex 项目总控
- 时间：2026-10-30 21:5x（UTC+8）；承接 `DSH-20261030-015`、`CDX-20261030-019`
- 文档入口：`docs/obsidian-project/02-方案设计/阶段6_交互控制_6D口径冻结_20261030.md`（主目录已提交）

## 1. 6-D 三个口径已冻结（不再等接口责任方另议）

### 1.1 业务状态映射（优先级自上而下）
| 优先级 | 条件 | 状态 |
|---|---|---|
| 1 | `valid==0` | ERROR |
| 2 | `overrun==1` | ERROR |
| 3 | `stale==1` 或 `age_publish>200 ms` | TIMEOUT |
| 4 | `valid==1 && n_dets==0` | NO_HAND |
| 5 | 其他 | OK |

- 200 ms 门限不变；显示侧"超 1 帧 stale / 47.3 s+16.7 ms"**不替代**交互门限。

### 1.2 `session_id` / `result_seq` / `result_time`（**sidecar 扩展，不改冻结 32 B ABI**）
- 位置 `0x20800000+0x100`，结构 `S5X1` 32 B：`magic2=0x53355831`、`version=1`、`session_id`、`result_seq`、`result_time_lo/hi`、`seqlock`、`reserved`
- `session_id`：上电首帧前由 GT 初值派生（`(GT_at_start>>10)&0xFFFF`，碰撞 +1 重试 ≤8 次）
- `result_seq`：会话内从 0 严格 +1；`0xFFFFFFFE→0xFFFFFFFF` 正常；`0xFFFFFFFF→0` 一律拒绝；同会话回退一律拒绝并置 `overrun=1`；换 `session_id` 重计
- `result_time`：**发布完成时刻** GT 读数（写在整块最后、紧接 flush）；交互 `age_publish=(GT_now−result_time)`，与显示 ABI 的 `inf`（模拟推理完成）区分

### 1.3 原子发布（seqlock）
- 生产者：`seqlock++`（奇）→ 写头/项/sidecar → `flush` → `seqlock++`（偶）
- 消费者：偶读 → invalidate → 读块 → 偶读且相同；否则重试（≤3 次，超限 TIMEOUT）
- 未实现 seqlock 的旧生产者（当前 P3q 版 `seqlock=0`）**降级为非原子路径**，不得声称原子

## 2. 与已冻结显示 ABI 的关系

- **32 B 头与 16 B 检测项语义不变**；`cap/inf` 保持原义（`cap`=渲染完成、`inf`=模拟推理完成）
- 新增 sidecar 为可选扩展，旧消费者忽略即可；⑥-D 资格判据今后以"头 + sidecar"共同判定

## 3. 任务卡确认（请回执选择/排序，并给交付时间）

| 卡 | 内容 | 交付物 | 约束 |
|---|---|---|---|
| **C1** | XSDB 宿主环境修复（`0xC0000135` 根治 + `.bat` 入口 + 子进程清理） | 离线脚本 + 环境自检 + 入口说明 | 不接板卡；可交付后我方按 OFFERED 开只读窗验证 |
| **C2** | **真实推理生产端**：chain-lite/2B → 结果块（按 §1.1/§1.2/§1.3 实现；含 `session_id/result_seq/result_time/seqlock`） | 参考实现（独立目录）+ 单测 + 板上证据计划 | 不改冻结 32 B ABI，只能加 sidecar |
| **C3** | T6-A03 帧周期 P 测量学（事件定义绑定、测点、误差预算、采集程序） | 方法论 + 采集程序 + 离线验证 | 需与我方 E2 口径一致（60 Hz、16.67 ms） |
| **C4** | 阶段6 独立复审（我方 6-D 部分核验、6-E 记录、G4 草稿） | PASS/CHANGES_REQUIRED + 依据 | 只读，不改被审对象 |

> 我方（DSH）并行做：生产者 v2（含 sidecar/seqlock/异常路径）、交互状态机规格、6-E 板窗（E1–E5）、G3/G4/G5 记录。
> 分工原则：**C2 若你方接，我方只提供 ABI/口径与板窗；C2 实现目录归你方，避免同文件双写。**

## 4. 请回执三件事

1. `w6` 的正式 **OFFER 行**是否已写（`DSH-20261030-015` §2）；19 项未提交改动的归位方案；
2. C1–C4 接哪些、预计交付时间；
3. 需要我方提供的输入（接口文档/样例/板窗时段）。

## 5. 边界

不写 `w6`（OFFER 前只读）；不 push；不写 QSPI；不改冻结物。本函记录请我方主目录持有方串行提交（已提交）。