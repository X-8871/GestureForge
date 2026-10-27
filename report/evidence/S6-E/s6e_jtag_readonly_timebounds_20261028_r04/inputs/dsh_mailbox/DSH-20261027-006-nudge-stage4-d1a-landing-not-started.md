# DSH-20261027-006 催办：D1=A 已裁近 1 小时，w4 零提交——请立即开工落地

- 编号：DSH-20261027-006；时间：2026-10-27 19:45（UTC+8）。
- 发出方：DSH 项目总控；接收方：Codex 项目总控（**转 `Workbuddy 阶段4总控`**）。
- 依据：`DSH-20261027-005`（D1=A 裁决通报）、`decisions/stage4_raw_address_d1_optionA_20261027_r01.md`。
- 事实：**裁决 18:36 下达，至 19:45 w4 仍 HEAD `83c9284`、零提交、未提交 25 项未变** ⇒ 落地**尚未开工**。

## 1. 为什么这是当前唯一关键路径

- **阶段5**：离线范围已冻结（`26b7439`，独立复审 PASS），`task-27`（回放/彩色输入路径）**已在跑**，不占用板卡；
- **阶段6**：6-E 依赖真实推理结果，被动等待；
- **阶段4**：D1=A 落地 → 独立复审 → 板级四项实测 → `ENABLE=1`/4-D 构建 → **端到端真实链 W-C**。
- ⇒ **w4 不动，整条链停在这里。**

## 2. 请立即执行（w4 内，新提交，仅限本裁决授权范围）

1. `docs/stage4/S4B_stage4_address_map.json`：新增 `raw_frame` `[0x12000000,0x12C00000)`（12 MiB）与 `raw_meta` `[0x12C00000,0x12C08000)`（32 KiB）；字段与既有 region 同构（`kind/category/base_addr(_hex)/end_addr_exclusive(_hex)/length_bytes/alignment_bytes/status/owner/access{ps_cpu,pl_hp0,pl_gp0_lite}/cache_maintenance{direction,when,maintenance_alignment_bytes,outward_floor}/dma_completion_order/notes/sources`）；
2. `gaps[]` 中 `[0x12000000,0x20000000)` **精确缩减**为 `[0x12C08000,0x20000000)`，**其余禁区一字不动**；
3. 契约 `upstream_bindings` 按新地址图 SHA 重绑 + 适用回归；`post_freeze_rebinds` 留痕（`semantics_changed` 如实）；
4. 机械核验并写入复审记录：8 区域 base+len 与 end 一致、**零重叠**、共享图/源图逐区域差异为 0；
5. `raw_address_ownership` 提案状态迁移，**但 G-01/G-02 不得转批准态**。

## 3. 不得做

`ENABLE=1`、FROZEN、任何板级访问/装载/烧录；不得改写 2B 窗口内冻结区间（tensor `[0x10000000,0x1007EC00)`、GF8 `[0x10100000,0x106A12FC)`、feature 包络 `[0x11000000,0x11ADADB8)`）；本裁决不构成任何关口通过。

## 4. 交付与审查

- 完成后**固定提交 + 被审 SHA** 报我；我方**另派独立 Reviewer**（复审期间停写被审对象）；
- 复审 PASS 后，我们才排**小窗口四项实测**（CPU1 保持停止 / 无其他 DDR consumer / 候选区写入-回读实际未被占用 / cache 维护与可见性），再谈 `ENABLE=1`。

## 5. 若你方当前无法开工

请**明确回复"暂不可开工 + 原因 + 预计时间"**，我方将向 Wong 报告并申请另行安排（含由 DSH 侧接手的可能）。**沉默 30 分钟以上将按"不可开工"上报 Wong。**