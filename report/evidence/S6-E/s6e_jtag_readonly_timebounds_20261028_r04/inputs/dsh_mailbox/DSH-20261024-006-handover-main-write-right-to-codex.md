# DSH-20261024-006 项目总控写权交接：DSH → Codex（OFFERED）

- 编号：DSH-20261024-006；时间：2026-10-24 10:35（UTC+8）。
- 依据：Wong 2026-10-24 10:29 指示「**已插上板卡和摄像头，查询目前各阶段状况然后更新交接文档，把写权交给Codex**」。
- 类型：**正式交接（OFFERED）**。DSH 自本条提交后**停止写入**（main 与四棵阶段树均交回；只读）。
- 关联：main `.codex/STATE.md` 11 字段交接行（同日 10:35 更新为 `OFFERED / Codex 项目总控`）、各树 STATE、`decisions/**`。

## 1. 交接范围

| 对象 | 现状 | 说明 |
|---|---|---|
| main `D:\FPGA_Competition`／`main` | HEAD **`f773256`**（交接提交前）；未提交 **406 项** | **写权 OFFERED 给 Codex 项目总控**。406 项中 DSH 本轮只提交过 `.codex/STATE.md` 与 `report/evidence/CTRL-DSH-HANDOFF/**`；其余为 Codex/用户历史改动与未跟踪产物，**DSH 未触碰、未清理** |
| `D:\codex-worktrees\dbdf`／`codex/stage3-video` | HEAD **`2487eb8`**，dirty 2（`NA/`、`clockInfo.txt`，无归属残留） | 阶段3，随 main 一并交回 |
| `D:\codex-worktrees\w4`／`stage4-infer-prep` | HEAD **`ced5bde`**，dirty 13（12 项 Codex 恢复产物 6 ELF/6 map + 1 项范围外回放链方案） | 阶段4，DSH 曾接续认领；**写权交回 Codex** |
| `D:\codex-worktrees\w5`／`stage5-display-prep` | HEAD **`93493f8`**，**干净** | 阶段5，交回 |
| `D:\codex-worktrees\w6`／`stage6-interact-prep` | HEAD **`8d232ab`**，**干净** | 阶段6，交回 |
| `D:\FPGA_Competition\w2b` | HEAD `07c3d39`，dirty 182 | 2B 冻结树（Codex 侧，保持不动） |
| 阶段7 | 未建树 | Wong 决定暂不开 |

**DSH 子代理**（`stage3-lead`/`stage4-lead`/`stage5-lead`/`stage6-lead4` 等）**全部 inactive，不再派单**；其名字保留，Codex 可自行决定是否复用同一工作树与任务卡。

## 2. 各阶段当前事实（截至 2026-10-24 02:43 的最后提交）

**阶段3（dbdf）** — 已完成：颜色子项（新模块实测，6/6 哈希复核）；**≥30 分钟实时耐久**（31 min 15 s、7 轮、退出码全 0、无复位/死锁）；参考帧集（`frame_full.bin` `939fce22…`、0 全零行、B/G/R、1280×720、stride 3840）；**静态地址事实**（采集 S2MM 与显示 MM2S **同址 `0x00110C00`**、单缓冲、**运行期分配无静态保证**）；**真彩目视**（Wong 01:41「画面可接受，正常颜色」，人工观察、部署/端口/接线变更即失效）；J10 按 Wong 决定**范围排除**（非"已修复"）；I/O delay（I1–I3）与 C2 按 Wong 决定**记为已记录局限**（未宣称已验证、交付前重评）；`38-249` 归因经 **DCP 只读重跑确认**（`×5` 本已声明，问题在主源引脚/时钟对象关联；工具建议"define as primary clock"**未实施**）。
**未关闭**：完整独立 G2；VDMA 粘滞 `0x00015810` **PARTIAL**（`FSZ_MORE` 根因未定，需板级密集采样 + PG020 手册）；TIMING-17/36 与 I/O delay；无 ILA（BASIC 许可）；task-11（RTL↔网表等价性/阈值未核）。**整体 G5 未通过 ⇒ 未冻结**。
**最近一次改动**：`2487eb8`（处理复审 N-1 `manifest.source_commit` 口径、N-7"自终止 3 个 bash"无时点快照）——**该提交与 `f517ca9` 均未经复审**。
证据：`report/evidence/S3-T05/t05_stage3_window_20261024_r01/`、`t05_offline_closeout_20261024_r01/`、`t05_dcp_readonly_20261024_r01/`。

**阶段4（w4）** — DSH 已接手并留接续记录（`report/evidence/CTRL-DSH-HANDOFF/dsh_claim_20261024_r01/`，`HANDOFF_OK` PASS 9/0）。契约 `s4-shared-io/1.1.0` **r04**（两彩色标签均 `maps_to_source_kind=camera`、回放 `timing_claim_scope=replay_only`；r04 经复审 PASS）→ **r05** + 地址图 **r03**：**A 方案**（`raw_frame=[0x12000000,0x12C00000)` 12 MiB + `raw_meta` 32 KiB；**109/109**；余量 1,523,712 B；**自设禁区精确缩减**至 `[0x12C08000,0x20000000)`；Wong 2026-10-24 批准 A、**不接受降覆盖**）；新增 **fail-closed 跨界漂移断言**（树分类 `STABLE`/`MOVING_PRODUCING`/`MOVING_HOST_REPO`、有效窗口）。
**未关闭**：r03 复审**未完成**（见 §3）；RAW 系统 G0 `CHANGES_REQUIRED_NOT_CLOSED`（G-01 设计级阻断已由 Wong 批 A、G-02 owner 待复审、G-05/07/08/09/10/11/13/14/15 设计类、硬件类全 `NOT_RUN`）；帧周期 P 方案就绪但**数值 `NOT_RUN`**。`status=DRAFT_PENDING_REVIEW`、**`ENABLE=0`**、**未 FROZEN**。
**在办（范围外、未提交完）**：离线真实彩色链桥接——已确认 `load_image_chw()` 即**冻结预处理本体**（BGR→RGB→自带确定性双线性→letterbox 0.5→/255→CHW），`forward_one` **内含量化** ⇒ 桥接**复用零重复数学**；冻结件 SHA 已取（cfg `5475dff0…`、浮点权重 `3984affa…`、GF8 `f6feb6d4…`、校准清单 `d637a2fe…`、激活报告 `6d73283c…`、既有 CPU 参考 `3d5ccedc…`、模块 `0b90ef46…`）；**回放绑定落盘仍待 r03 结论**。

**阶段5（w5）** — r02 复审 **PASS**（0 阻断）；`task-24` r03 交付（`5fd3336`+`93493f8`）：NB-1 等价 `frame_id` 改 fail-closed + 判别力对照；NB-2 影响登记改扫描判据（19 清单/10 包 + `scan_hash_drift.py`）；NB-3 JSON 与流水线 14 条**逐字相等**；NB-4 时间戳；NB-5 补 `capture_time_ns` 非零/`carry_fields` 10 字段断言 + **明写实现层 camera/回放路径未实现**。
**未关闭**：**r03 复审未完成**；`task-27`（实现回放/彩色输入路径 + 离线显示回归）未开工；板级 B1–B10 全 `BLOCKED`（待窗口）。

**阶段6（w6）** — 离线内容**已冻结**（F6d `2f16d668`/G6b `538b792`，tag `stage6-freeze-20261023-r6`；认证/声明附件明列未认证）；`task-23` 交付（`509e39e`/`93e0a82`）：A 组 8 项结清（含 STATE 失实更正、扫描器**死正则**修复、两向注入、批次 C）；B 组 **26 条 6-E 用例**冻结（覆盖运行手册全 11 类；绑定 24 参数 + `stale=200 ms`；`T6-A03` **无值**）；`task-28` 项 2/3（`8d232ab`）：延迟方法学 + 结构禁填造模板 + 窗口包**如实判 `NOT_READY`**（八类门禁仅 `g0_approval` 部分满足）。
**未关闭**：**task-23+task-28 增量复审未完成**；项 1（回放驱动的 6-E 预演）`BLOCKED`（待阶段4 回放结果包 + 阶段5 回归）；6-E 实物未执行；`T6-A03` 数值 `NOT_RUN`；6-D 集成 `BLOCKED`。

## 3. ⚠ 未完成/未放行清单（最重要，请优先处理）

**四份独立复审全部未完成**（复审子代理故障中断，无有效结论）：

| 复审 | 被审基线 | 状态 |
|---|---|---|
| 阶段3 窗口证据修复轮 | `f517ca9`（及后续 `2487eb8`） | **未判**（BL-1 迁移登记/BL-2 自证产物/BL-3 manifest 字段已修但未复判） |
| 阶段4 A 方案 r03 | `ced5bde` | **中途失败**（T3/T5e/T5f 有效；T5a/T5c/T5d 因复审者把隔离仓放在 `tmp/` 下被前缀规则误判；且复审期间 dbdf/w5/main 推进） |
| 阶段5 task-24 r03 | `93493f8` | **失败，无输出** |
| 阶段6 task-23 增量 | `509e39e`/`93e0a82`/`8d232ab` | **失败，无输出** |

⇒ **各阶段最新交付只做了自证，不得视为已审查通过**。建议接管后优先重派这四份复审（可合并同阶段相邻提交）。

其他未落盘项：阶段4 回放绑定；阶段5 `task-27`；阶段6 `task-28` 项1；阶段3 的 BL 修复后复审。

## 4. 板卡与摄像头（Wong 已重新插上，2026-10-24 10:29）

- **当前无任何 host 会话**（DSH 10:30 核验）：`hw_server`/`xsdb`/Vivado/vitis 进程 **0**、**3121 无监听**、COM4 未占用。**板卡虽已插上，但"插上"不等于已核验就绪。**
- **重连后必须先重做受连接判据**（拔插使旧判据失效）：
  1. **部署身份**逐字符核对：无补偿 SOF `7cb33068…`、XSA `1f5b138e…`、`an5642_j11cmos2_v10_read.elf` `1457cda4…`；
  2. **真彩目视重做**（Wong 在场）；
  3. **运行期回读** `ADDR_S2MM`/`ADDR_MM2S`（阶段3 已证为运行期分配，**禁止硬编码旧地址**）。
- 摄像头：**J11/CMOS2**、1280×720、DVP；**J10 已由 Wong 移出范围**（范围排除，非"已修复"）。
- 窗口方案草案（可直接采用）：`report/evidence/CTRL-DSH-HANDOFF/decisions/board_window_merged_plan_draft_20261024_r01.md` — **W1 阶段3**（VDMA `FSZ_MORE` 根因密集采样 + 地址复读）→ **W2 阶段4**（真实链 + 帧周期 P 实测 ≥1000 帧）→ **W3 阶段5**（B1–B10，含 30 min 真实长跑）→ **W4 阶段6**（6-E 实物）；**W2 未完成则 W3/W4 不启动**；每次窗口先做第 0 步现场核对。

## 5. 在办规则（请继承）

1. **跨界绑定＝路径 blob（内容权威）+ 树 HEAD（仅陈旧性检测）**；树分类 `STABLE`（任何移动即 FAIL）/`MOVING_PRODUCING`/`MOVING_HOST_REPO`（移动属预期但须重核 blob，**不得静默 PASS**）；口径与 PASS 有效窗口须**写入被审提交**。
2. **自证必须打印范围；范围不覆盖被认证对象即 FAIL**（阶段3 已有 `--certify` fail-closed + must-fail 自测）——**"按范围的字面通过"＝假证书**。
3. **复审者禁跑会写入仓库的命令**（`fsck --lost-found`/`gc`/仓内克隆）。
4. 交审后**停写被审对象**；引用基线必须写**提交号 + 被审 SHA**；同范围改动须**另审**；不得 amend/rebase 已被引用的提交。
5. 「已批准」≠「实现已同步」；「离线/回放」≠「实物」；**数值禁止填造**（`T6-A03`、P 等）；`P` 与硬件项保持 `NOT_RUN` 直到实测。
6. 失败证据不删、不覆盖；RunId 不重跑不覆盖；**不 push**；一次只跑一个重型任务。
7. 人工目视＝**人工观察证据**，须写失效条件。
8. 主线 Wong 长期方向：「**先完成作品、少一些验证，第一版能过即可**」。

## 6. 接管检查清单（建议顺序）

1. 核对 main 与四棵树 HEAD/status、无 `index.lock`、无重型进程；
2. 读本文件 + `AGENTS.md` + 各树 `.codex/STATE.md`；
3. 复核/重派 §3 的四份未完成复审；
4. 重做 §4 的受连接判据，确认板卡就绪；
5. 决定各阶段恢复顺序（建议按 `board_window_merged_plan_draft` 的 W1→W4）；
6. 接管完成后在 main STATE 交接行标 **`CLAIMED`** 并更新心跳。

## 7. 边界

- 本条只写入 DSH 信箱，**不覆盖**旧记录；不代表任何阶段通过或已冻结；不代表板卡已被占用；不授予 DSH 任何后续写权。