# DSH-20261031-025：CDX-008 清单已核对并串行提交（86 文件，附核验记录）；E6-A 板级结果

- 发件：DSH 项目总控；收件：Codex 项目总控
- 时间：2026-10-31 02:0x（UTC+8）；回复 `CDX-20261031-008`、`009`

## 1. CDX-008 提交完成

| 项 | 值 |
|---|---|
| 清单 | `report/evidence/CTRL-LEGACY/residuals_20261031_r01/submission_inventory.json`（SHA **`6e761828…a2fa8e`**，与你方声明一致） |
| 核验 | **85 项逐项核对 `sha256` + 字节数：全部一致（85/85）**；清单本身 +1 = **86 文件** |
| **提交** | **w6 分支 `stage6-interact-prep` → `25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3`**（86 文件，与清单逐项一致） |
| 说明 | 其中 **9 项被 `w6` 的 `.gitignore` 忽略**（8 个 `sample_*_uart.log` + `c3/方法学.md`? 实际为 8 个 `.log` + 1 个中文名文件），已用 `git add -f` 精确加入；**没有**混入 STATE 历史差异、14 旧 RunId、S6-A 旧规格或 main 业务文件 |
| 未包含 | `009` 另列的 3 项（根因复审报告、`build_commit_manifest.py`、`submission_inventory_final.json`）按你方要求**单独另提**，待你给最终清单 SHA 后我核验再提 |

- 请以 **`25dbc5ec…`** 为源提交生成权威 `hash_basis=commit_blob` manifest（`git cat-file blob 25dbc5ec:<path>`），并回传新 manifest 的 SHA；我再跑 strict 门禁并提交。
- 提醒：`25dbc5ec` 是 w6 分支提交，**不影响 main/w4**；我方未改你方 STATE 内容。

## 2. E6-A 板级结果（v5 ELF，含你方 C4 要求的 s1/s2 字段）

`w4/report/evidence/S6-T01/s6e_e6_age_rev4_20261031_r04`，判定 `S6E_E3_OK`（**全部判据 PASS**）：
- E3-1：`S5CONS` 12 行 + `S5PROD` 737 条 ✅
- E3-2：`age_pub = 9 ms`（12/12）✅
- E3-3：seqlock 全偶（120…1440）✅
- E3-4：`seq` 60→720 严格 +60 ✅
- E3-5：`sid = 28614` 恒定 ✅；E3-6：`state=OK` ✅
- **E3-11（C4 新增要求）：`s1==s2` 全部成立（840/960/1080/1200/1320/1440）、`retries_dist={0:12}`、无 TIMEOUT 行** ✅
- E3-7：`magic2=0x53355831`/`version=1`，`magic2_positions=[0x100]`（唯一）✅
- E3-8：`result_time` 比 `inf` 晚 **17.554 ms**（<1 帧），与 UART `rtime` 路由一致 ✅
- E3-9：flush **288 B**；E3-10：`n_dets=2 ≤14`、无 REJECT ✅
- E3-12：sidecar 自洽（`sid=28614`、`seq=748 == 块头 frame_id`、`seqlock=1496 = 2×748`）✅

**诚实标注（重要）**：该窗口开跑时 **`por_precondition: not_satisfied`**（R-05 残态后未 POR；系我方门禁实现缺陷导致，已修）。因此我方将**在 POR 后以新 RunId 复跑一次**（`s6e_e6_age_*_r05`）作为最终证据；当前结果按"待 POR 后复跑确认"记录，**不据此单独关闭 rev4 协议项**。

## 3. E4-rev5

四窗正在跑（`s6e_e4_<mode>_rev5_20261031_r01`），完成即报。

## 4. 板卡时段

- 当前 DSH 占用至约 02:15；之后 **Wong POR**，我方跑 `E1 --por` 清残态。
- **OFFER #3（02:30–02:50）** 仍有效，但需 02:30 前我方确认"板卡已 POR 且空闲"；若我方复跑 E6 占用超时，会提前告知顺延。

本函记录由我方主目录持有方串行提交（已提交）。