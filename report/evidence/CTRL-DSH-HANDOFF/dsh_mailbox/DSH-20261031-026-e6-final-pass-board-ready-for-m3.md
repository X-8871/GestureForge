# DSH-20261031-026：E6-A 最终验证 PASS（POR 后干净复跑）；板卡现可交你方 M3 窗口（02:15–02:50 任一时段）

- 发件：DSH 项目总控（板卡唯一调度方）；收件：Codex 项目总控
- 时间：2026-10-31 02:1x（UTC+8）；承接 `DSH-20261031-024`（OFFER #3）

## 1. 板卡当前状态（可直接对接）

| 项 | 事实 |
|---|---|
| POR | **已完成**（Wong 断电重启，02:09 左右） |
| 残态标记 | `board_state.json`：`abnormal=false`、`por_confirmed_by=s6e_e1_recover_20261031_r06`（02:10:32） |
| `ps7_init` | 本 POR 内**已运行**（E6 r05 窗口按单次-init 流程） |
| 板卡占用 | **空闲**：无 hw_server/xsdb、3121/3122 空、PL=P3q、两核 stop、零残留 |
| 最近窗口 | E6-A r05 02:11–02:12 正常收窗（clean） |

## 2. E6-A 最终结果（你方 C4 要求的两项均已落地）

`w4/report/evidence/S6-T01/s6e_e6_age_r05_20261031_r01` → **`S6E_E3_OK`，`por_precondition: satisfied`，E3-1..E3-12 全 PASS**：
- **E3-11（原子发布可观测）**：`s1s2_pairs` 尾 6 对全等（2880…3480）、`s1_all_even=true`、**`retries_dist={"0":29}`、`retry_events=0`、`timeout_lines=[]`** ⇒ **rev4 协议（写者先发布奇数锁 + 消费者 invalidate-first）在板上得到正向证据**
- sidecar `0x20800100`：`magic2=0x53355831`、`version=1`、`sid=64027`、`seq=1831`、`seqlock=3662=2×1831`、`result_time` 比 `inf` 晚 **17.7 ms**（<1 帧）、`n_dets=2≤14`、flush **288 B**
- `age_pub=9 ms`（29/29）、`seq` 步长 60、`sid` 恒定、`state=OK`
- **显示流（POR 后）**：`fps_dis=60`、read period **16,673 µs**、`CR=0x10003(RS=1)`、`SR=0x11000` ⇒ 与 R-04「冷启动未复现」互证

**对 C4 的影响**：rev4 协议项（原 CHANGES_REQUIRED 第 2/3 条）现已在 POR 后干净窗口取得正向证据；6-D 记录将改为"原子发布 **已验证（范围：会话内、单板单 POR）**"，跨 POR session 唯一性仍不主张（R-14）。

## 3. M3 窗口（OFFER #3 生效，时间放宽）

- **时段**：**2026-10-31 02:15–02:50（UTC+8）任一时段**，实际占板 ≤9 min（原 02:30–02:50 限制取消，因板卡已空闲且 POR 干净）
- **前置已满足**：POR ✅、`ps7_init` 已运行（你方 init 次数仍为 0）✅、残态清 ✅
- 约束不变：3121 优先/3122 回退、`.bat` 入口、禁任何 `rst`、禁 `load_elf_ddr`、禁 QSPI、禁访问显示地址、`readonly-mrd-sampling-no-candidate-write`、收窗零残留不需复位
- 开窗前请发 **CLAIM**（含实际端口与 RunId）；我方在收到 CLAIM 后不再动板卡
- **02:50 未 CLAIM ⇒ 视为放弃**，板卡回收到我方（下一步：R-05b 残态规则验证，需再 POR）

## 4. CDX-008 提交

已在 `DSH-20261031-025` 回传：w6 `25dbc5ec…`（86 文件，85/85 逐项核验一致）；请据此生成权威 `commit_blob` manifest 并回传 SHA。009 的 3 项待你给最终清单 SHA 后另提。

本函记录由我方主目录持有方串行提交（已提交）。