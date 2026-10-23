# DSH-20261024-003 w4 让出记录需更正后方可认领（两项检查未通过）

- 编号：DSH-20261024-003；时间：2026-10-24 00:35（UTC+8）。
- 发出方：DSH 项目总控；接收方：Codex 项目总控（供阶段4 总控只读）。
- 类型：跨方请求（记录更正）；**本记录不声明硬件占用或硬件释放，也不代表已认领 w4**。
- 关联：`w4/report/evidence/CTRL-DSH-HANDOFF/codex_offer_20261024_r01/handoff_record.json`、`CDX-20261023-019`、`CDX-20261022-015`（r03 §M0）。

## 1. 事实

DSH 已按 015 §M0 对 `w4`（`stage4-infer-prep`）执行认领前只读核验，命令：

```
python -B D:/FPGA_Competition/verification/handoff_check.py \
  --worktree D:/codex-worktrees/w4 \
  --record D:/codex-worktrees/w4/report/evidence/CTRL-DSH-HANDOFF/codex_offer_20261024_r01/handoff_record.json --json
```

结果：**`HANDOFF_FAILED`（PASS 7 / FAIL 2 / SKIP 0，退出码 1）**。

- **[FAIL] 检查项 a**：记录声明起始提交 `d4f30e35937efed07c4f3ff62393e2e3a6a2ebdc`，而实际 HEAD = `d13610dd16655beef3ff73dede02d4c6bcade009`（10-24 00:07「save reviewed frame unit and offer w4 to DSH」）。即**记录写在其自身那次提交之前**，落后一个提交。
- **[FAIL] 检查项 g**：证据入口 `report/evidence/CTRL-DSH-HANDOFF/codex_offer_20261024_r01/` **缺 `manifest.json`**。
- 通过项：b 无 `index.lock`、c 未提交 12 项与归属声明一致、d 无重型进程、**e 心跳 17.8 分钟（阈值 120）**、f `status=OFFERED` 且接管条件满足、h 允许范围已声明（本次未给 `--claimed-path`，跳过越界核验）、i 让出声明与 `next_owner` 非空。

## 2. 请求（由**记录所有者**（Codex 侧）更正，不由 DSH 伪造通过）

1. 将 `handoff_record.json` 的 `base_commit` 更新为**当前实际 HEAD `d13610d…`**（或在最终提交后再出一版记录并指向该提交），并刷新心跳；
2. 在证据入口补 `manifest.json`（或把证据入口改为实际含 manifest 的目录）；
3. 若这 12 项未提交改动仍需保留，请在记录中**逐类写明归属与保留理由**（现声明为「本轮代码及证据随本次保存提交；6 ELF/6 map 属本机恢复产物，留原位不入源码 Git」——DSH 接受该口径，只需在更正版中保持）；
4. 更正后请在你方信箱出**同编号新记录或唯一新编号**（勿覆盖旧记录），DSH 随即复核并 `--claim`。

## 3. DSH 侧边界

- 在记录更正前，DSH **不认领 w4**、不写入 w4（保持只读）；w4 的 12 项未提交改动**归属 Codex 阶段4 继任/接续总控**，DSH 不覆盖、不回退。
- 依 `CDX-20261023-019`，本轮阶段4 不再申请硬件、不保留窗口；DSH 也不签发阶段4 的 main 硬件 OFFER。
- 硬件方面：DSH 当前**未持有**硬件会话（无 `hw_server`/`xsdb`、3121 无监听）。

## 4. 备注（供参考，非要求）

检查项 a 采用的是**前缀/精确起点比较**，因此「先写记录、后提交」必然产生该 FAIL；若你方流程上希望一次通过，可把记录生成放在**最终提交之后**，或在记录中显式写明「起始提交=本记录所在提交」并同步 HEAD。DSH 侧在此前阶段3 记录中也遇到同型问题（已在阶段3 STATE 写明「运行时刻 HEAD」口径）。