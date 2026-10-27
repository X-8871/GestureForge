# S4-T30 · D1=A 地址落盘复核（2026-10-27 r01）

- 工作树 D:\codex-worktrees\w4（分支 `stage4-infer-prep`）；任务卡 `task-30`；执行方 DSH 阶段4 总控。
- **接管核对**：HEAD `83c9284`；`index.lock` 不存在；无 vivado/xsim/hw_server/xsdb 进程；**25 项未提交改动属原持有方**（不清理/不暂存/不回退/不代提交）。
- **裁决**：`decisions/stage4_raw_address_d1_optionA_20261027_r01.md`（Wong 原话「A」）。

## 重要事实：落盘主体在接管时已存在

`raw_frame`/`raw_meta`、禁区缩减、契约重绑在本卡接管时**已存在于 HEAD `83c9284`**（前序 Workbuddy 轮次完成，且地址图整体已由 Wong 2026-10-27 14:15 批为 `APPROVED`）。
本卡实际新增：① 禁区条目**缩减算术补记**（12,615,680 B = 12,582,912 + 32,768）；② **机械核验器**与实跑证据；③ **提案状态迁移**登记；④ **STATE 写权行**改 DSH + 裁决指针 + 禁止事项。
**未改动**：两 region 的 status 保持提案态（`PROPOSED_STAGE4_OWNED_PENDING_APPROVAL_AND_REVIEW`，非 `FROZEN_STAGE4`）；2B 冻结区间一字未动。

## 机械核验结果（全部真实退出码）

| 检查 | 命令 | 退出码 |
|---|---|---|
| 机械核验 A–G | `python -B scripts/stage4_s4ctrl/verify_d1a_landing.py --run-dir <本目录>` | **0**（7/7） |
| 契约自检 | `python -B scripts/stage4_s4ctrl/verify_shared_io_contract.py --evidence-dir <本目录>/contract_selfcheck` | **0**（27/0） |
| 缺口审计 | `python -B scripts/stage4_s4b/audit_raw_system_g0_gaps.py --evidence-dir <本目录>/gap_audit_r02` | **0**（13/13、17/17） |

- A：8 区域 `base + length_bytes == end_addr_exclusive` 且 hex/整数一致。
- B：8 区域两两 **21 对零重叠**。
- C：共享图与源图 8 区域 `base_addr_hex`/`length_bytes`/`status`/`owner_from_source` **差异 0**。
- D：`raw_frame`/`raw_meta` 与 2B 冻结对象 tensor `[0x10000000,0x1007EC00)`、GF8 `[0x10100000,0x106A12FC)`、feature `[0x11000000,0x11ADADB8)` **不相交**（字面区间 + 图中 region 双路核对）。
- E：存在禁区 `[0x12C08000,0x20000000)`、不存在 `[0x12000000,…)`；缩减量 **12,615,680 B**；**其余 8 条禁区相对基线 `d29ef5f^` 逐条不变**。
- F：两新 region 提案态；共享图 `enable_status=0`；源图 `status=APPROVED` 且有 `approval_history`（事实登记，**不据此提升任何关口**）。
- G：契约 `upstream_bindings.stage4_address_map.sha256` == 当前图 SHA；`post_freeze_rebinds` 有 `to == 该 SHA` 留痕。

## 未做（明确不越界）

1. **板级四项实测**（CPU1 停止 / 无其他 DDR consumer / 候选区未被占用 / cache 可见性）——需授权窗口；
2. **独立复审**——由项目总控另派 Reviewer；
3. **`ENABLE=1` 与 4-D 构建**——须先满足裁决 §3 全部前置；
4. 真实链窗口 W-C（等地址复审 PASS + 实测 + 4-D + P1）。

**边界**：仅写 w4；未动硬件；未 push；`ENABLE=0` 保持；未 FROZEN；本记录**不构成**任何关口（G0/G1/G3/G4/G5）通过。
