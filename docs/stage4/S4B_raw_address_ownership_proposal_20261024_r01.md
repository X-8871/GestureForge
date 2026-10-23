# ADR-S4B-RAW-ADDR-01（待决提案）：RAW/META 地址与所有权候选方案

- 状态：**待决（DECISION_REQUESTED）**。日期：2026-10-24（UTC+8）；提出方：DSH 阶段4 总控（本树 `D:\codex-worktrees\w4`，task-21）。
- 范围：**规范层面候选方案**——只给出可选区间、所有权登记方式、代价与对 4-D 的影响；**不修改任何实现/地址图/契约**，也不自行扩大既有批准范围。
- 决策权：本提案涉及**集成与接口语义**（地址准入禁区、物理 owner、输入覆盖范围）。按 `AGENTS.md`，**是否越出既有批准范围由 DSH 项目总控先行裁决；若改变已批准部署/接口边界或输入覆盖口径，须报 Wong**。阶段4 写入方不自行决定。
- 依据本次算术：`report/evidence/S4-CTRL/t21_raw_address_proposal_20261024_r01/raw_address_options_arithmetic.json`（脚本 `scripts/stage4_s4b/check_raw_address_options.py`，**exit 0**）。本提案不含任何硬件执行。
- 对应缺口：`docs/stage4/S4B_raw_system_g0_gap_registry.json` 的 **G-01（地址与准入）** 与 **G-02（owner 登记）**，二者当前均为 `BLOCKED_PENDING_APPROVAL` / `OPEN_REQUIRES_DESIGN_OR_REVIEW`。

## 1. 已核验约束（只读算术，非批准）

| 事实 | 值 |
|---|---|
| 2B 专属窗口 | `[0x10000000,0x12000000)`（32 MiB） |
| 窗口内冻结对象 | tensor `[0x10000000,0x1007EC00)`、GF8 权重 `[0x10100000,0x106A12FC)`、feature 包络 `[0x11000000,0x11ADADB8)` |
| 窗口内空洞（连续） | `0x1007EC00..0x10100000`（529,408 B）、`0x106A12FC..0x11000000`（**9,825,540 B**）、`0x11ADADB8..0x12000000`（5,395,016 B） |
| **最大连续空洞** | **9,825,540 B** |
| 最大单帧 packed RGB888（109 帧清单） | **11,059,200 B**（1920×1920，2 帧） |
| 现有草案区间 | `injection_frame_rgb` `[0x10700000,0x10B00000)` 4 MiB，`PROPOSED_STAGE4_OWNED_PENDING_G0`，仅支持 **12/109** 帧 |
| 现行准入禁区 | `[0x12000000,0x20000000)`（地址图 `must_not_access`） |
| META 需求 | 32,768 B（mailbox/几何表/结果区，偏移见 readiness §8.2） |
| 对齐 | storage `align_up(logical,8)`；cache 维护区间按 **64 B 向外取整** |

**结论（算术）**：`9,825,540 B < 11,059,200 B` ⇒ **在 2B 窗口内无法容纳最大冻结帧**；全 109 覆盖必须①扩到窗口外（缩减禁区），或②按预冻结子集缩小输入范围。二者都需要批准。

## 2. 候选方案对照

| 选项 | RAW 区间 | 可用容量 / 余量 | 支持帧数 | 是否动禁区 | 代价 |
|---|---|---|---|---|---|
| **A**（readiness §8.2 原案） | `[0x12000000,0x12C00000)` 12 MiB + META `[0x12C00000,0x12C08000)` | 12,582,912 / **+1,523,712 B** | **109/109** | 是（占禁区 12.03 MiB，占该跨段 5.4%） | 需批准缩减 `must_not_access` 跨段；文档改动最小（readiness §8.2 已按此撰写）；RAW/META 相邻、单一 mailbox base |
| **C**（最小足迹变体） | `[0x12000000,0x12B00000)` 11 MiB；META 移到窗口内空洞 `[0x11ADADC0,0x11ADEDC0)`（64 B 对齐） | 11,534,336 / **+475,136 B** | **109/109** | 是（占禁区 11.0 MiB） | 需批准缩减禁区 **且** 批准窗口内空洞的 owner 登记；须修 readiness §8.2 的 META base；余量较小 |
| **B**（窗口内 9 MiB） | 草案区 + 相邻空洞 `[0x10700000,0x11000000)` 9 MiB（含 META） | 9,404,416 / **−1,654,784 B**（容不下最大帧） | **107/109**（排除 2 帧 1920×1920 `two_up`） | 否（仍在 2B 窗口内） | 需批准占用窗口内空洞 + **变更输入覆盖口径**（≤8 MiB 子集须预先冻结样本清单；readiness 已注明该子集保留五类/3 负样本/2 multibox/4 合成，但不含两张 1920×1920） |
| **E**（复用 `ps_app_arena` 上部） | r13 已用上界以上（`>0x0082FED0`）至 arena 末 | 9,240,880 / **−1,818,320 B** | 107/109 | 否 | 所有权属 PS 应用 linker arena；须先冻结 4-D 最终 ELF 布局再登记内部切分；把地址批准耦合到应用构建 |

## 3. 各选项在 4-D 上的影响

- **A / C**：保持**全 109 帧覆盖**（含 2 张 1920×1920 `two_up`），与 readiness「默认 109 全覆盖预算」一致；mailbox/几何表偏移不变（仅 base 变化，C 需改 META base）。代价集中在**治理层**：缩减地址图禁区、登记 RAW/META owner、更新契约 `upstream_bindings`（地址图 SHA）并做适用回归。
- **B / E**：把 4-D 输入范围降为 **107 帧冻结子集** ⇒ 属**需求/覆盖口径变更**，必须预先冻结样本 ID 清单并改写覆盖声明（不得事后按结果挑选子集）；对 `two_up` 类 1920×1920 样本的覆盖缺失需在验收记录中明示。
- 任一选项都**不改变**：`s2bu/1.1` 正文、冻结网络/D2/D9、`≥100 帧`与`≥30 分钟/≥1000 次推理`的 4-D 标准、以及「不合并阶段3 视频 XSA」的已批准路线。

## 4. G-02：所有权登记方式（提案，待批准后执行）

1. **声明新区域**：在 `docs/stage4/S4B_stage4_address_map.json` 增加 `raw_frame`、`raw_meta` 两个 region，字段与既有 region 同构：`kind/category/base_addr(_hex)/end_addr_exclusive(_hex)/length_bytes/alignment_bytes/status/owner/access{ps_cpu,pl_hp0,pl_gp0_lite}/cache_maintenance{direction,when,maintenance_alignment_bytes,outward_floor}/dma_completion_order/notes/sources`。
2. **状态迁移**：`PROPOSED_STAGE4_OWNED_PENDING_G0`（或新增 `BLOCKED`）→ 批准与独立 G0 审查后 → `FROZEN_STAGE4`；同时**精确缩减**对应禁区条目（`gaps[]` 中 `[0x12000000,0x20000000)` 或窗口内空洞规则），保留其余禁区不变。
3. **批准前必须齐备的证据**（区分已具备/待做）：
   - 已具备（本树离线）：区间长度与 8/64 B 对齐算术、容量余量、与 r13 实际分配/历史 framebuffer 的不相交核验（`G-03` 已 CLOSED_OFFLINE；交叉审计仍待独立 G0 审查）。
   - 待做（硬件窗口）：CPU1 保持停止、无其他 DDR consumer、候选区在板上实际未被占用、cache 维护与可见性实测；**未经这些实测不得把 `ENABLE` 置 1**。
   - 待做（治理）：地址图与共享契约同版本更新 + 阶段5/6 消费方重新绑定 + 适用回归。
4. **单写与审查**：地址图由阶段4 写入方独占修改，独立 Reviewer 固定提交审阅；`frozen=true` 不等于已批准，须同时给出批准依据（Wong/DSH 决定记录）。

## 5. 请求的裁决（Decision Request）

| # | 待决问题 | 建议默认 | 决策方 |
|---|---|---|---|
| D1 | 是否允许缩减地址图 `[0x12000000,0x20000000)` 禁区以给 RAW/META 让位 | 若允许：倾向 **选项 A**（与 readiness §8.2 一致、余量最大、单一 mailbox base）；若要求最小禁区占用：**选项 C** | DSH 项目总控先裁；改变已批准部署/接口边界则报 Wong |
| D2 | 若不允许动禁区：是否接受把 4-D 输入降为**107 帧预冻结子集**（选项 B/E） | 不默认；属覆盖口径变更 | Wong（需求层） |
| D3 | META 是否必须与 RAW 连续（决定 A vs C） | 建议不强制连续（readiness 未要求相邻） | DSH 项目总控 |
| D4 | 是否把「4-D 最终 PS 应用 linker 布局冻结」提前为地址批准前置（选项 E） | 不建议（会把地址批准耦合到应用构建） | DSH 项目总控 |

**在裁决前：G-01/G-02 保持 `BLOCKED_PENDING_APPROVAL` / `OPEN_REQUIRES_DESIGN_OR_REVIEW`；`ENABLE=0`、不访问候选区、不装载位流、不做任何板级操作。** 本提案不构成批准，也不改变任何实现。

## 6. 已排除选项

| 选项 | 排除理由 |
|---|---|
| D：把一帧拆到多个非连续空洞 | 帧缓冲必须连续（PL master 单区间寻址）；不成立 |
| F：沿用现有 4 MiB 草案 | 仅支持 12/109 帧，远低于 ≥100 帧要求 |
| 直接改写 D2 语义以接受预缩放输入 | 变更被验收预处理语义，须 Wong 开启规格变更并重建黄金，不在本提案范围 |

## 7. 边界

- 本轮**全离线**：未装载位流、未打开 COM4/JTAG、未起 hw_server、未访问板卡；`P` 与一切硬件项继续 `NOT_RUN`。
- 提案只做规范与算术；不含实现改动、不含地址批准、不含 owner 登记结果。
- 未经独立复审前不得据此修改地址图或契约。