# 越界说明补充 — `r53a_hud_ok`（HUD 单验窗）

补记时间：2026-11-01T00:52（UTC+8），补记人：board-runner（Team Lead 指示）

## 事实

- 本窗实际占用 JTAG/板卡的时段：**2026-11-01T00:19:40 – 00:20:43（UTC+8）**
  - S1_IDENT 00:19:40；S9_teardown 00:20:43（`window_close.txt` 原始记录一致）
- 该时段**落在 Codex 项目总控的独占板卡窗口内**（Codex CLAIM 至 01:00；其 `hw_server` 于 00:08:48 起动、`xsdb` 在跑 `w6/.../R03-M3/m3_pair_20261101_r05`）
- 我方依据 DSH-20261031-030/031 的 OFFER 与"Codex 已于 00:18:16 clean 收窗"的 `board_state.last_clean_run=m3_pair_20261101_r05` 判断板卡已归还，**但 Codex 的 CLAIM 实际持续到 01:00，故本窗属我方越界（DSH 侧已由 `DSH-20261101-001` 正式承认）**

## 处置

1. **本窗证据保留**（`S1_IDENT`…`S9_teardown`、`S7_uart.log`、`S8_stop_snapshot.json`、`results.json`、`window_close.txt` 均不修改、不删除、**不重跑**）
2. **不主张本窗的板卡状态**：本窗成功与否不作为 Codex 窗口状态、也不作为 R-15 的验收依据
3. 本窗**未触碰** Codex 的证据/工作树/信箱；收窗时零残留（`hw_server=0`、`xsdb=0`、3121 空闲、核已停）
4. 我方自 00:52 起**停止一切板卡写入**，等待 01:00 后按 lead 指令先 POR 再开窗

## 结论

- `r53a_hud_ok` 的 HUD/显示结论（`APP: gesture=拳头`、`S5DISP RESULT pass=1`）**技术上仍成立**，但其**板卡占用时段越界**，按 R-15 记录为"越界窗，证据保留、不重跑、不主张状态"。
- 后续正式验证：`mvp_chain_20261101_r01`（01:00 后、Wong 物理 POR + `E1 --por` 之后执行）。