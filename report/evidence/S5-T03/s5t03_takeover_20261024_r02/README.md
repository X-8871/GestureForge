# S5-T03 r02 接管与更正核对记录（w5，2026-10-24 01:5x UTC+8）

- 任务：`task-22` 复审修复轮（`CHANGES_REQUIRED`：B-1 / B-2 / N-1..N-7），**全离线**。
- 工作树/分支/HEAD：`D:\codex-worktrees\w5` / `stage5-display-prep` / 本记录时刻 `b6d11d4`（内容提交 F2）；
  修复前被审基线 `22a8dcb`（原 r01 轮）；起始提交 `654c72e`。
- 检查方式：只读；**未使用 `--claim`**（同阶段接续，无需跨方接管）。本轮**不动硬件**（阶段3 板级窗口自 2026-10-24 00:35 起占用中）。

## 1. 接管与更正核对结果

| 检查 | 结果 | 证据 |
|---|---|---|
| 工作树/分支/HEAD | PASS（`stage5-display-prep` @ `b6d11d4`） | `console/git_state.txt`、`console/handoff_check.json` 检查项 a |
| `index.lock` | ABSENT | `console/git_state.txt`、检查项 b |
| 已跟踪修改 | 无（`git status --short --untracked-files=no` 为空） | `console/takeover_checks.txt` C1 exit 0 |
| 重型进程 / 3121 | PROC_IDLE / PORT_3121_IDLE | `console/takeover_checks.txt` C4 exit 0 |
| 阶段3 部署身份（独立重算） | bit/ELF **全哈希**一致；XSA 全哈希与 015 r03 前缀一致，且与 dbdf 原部署清单一致 | `console/deploy_and_ur2_verify.txt`、C2 exit 0 |
| `UR-2`（dbdf README 口径） | **RESOLVED**：README sha256 `e60bab01…`，含 `v10_read` 与 `UR-2` 更正登记 | `console/deploy_and_ur2_verify.txt`、C3 exit 0 |
| `handoff_check`（只读，未提供 record） | `HANDOFF_FAILED` PASS 3 / FAIL 1 / SKIP 5，**exit 1** | `console/handoff_check.json` |

**FAIL 只来自检查项 c**（`存在未提交改动但 record 未声明「未提交改动归属」`）：本记录写盘时 `report/evidence/S5-T03/`
仍为未跟踪状态。这不是他人写入——a/b/d 三项 PASS；提交后同一命令复跑为 `HANDOFF_OK`（PASS 4 / FAIL 0 / SKIP 5，exit 0），
见 w5 STATE 与本轮汇报。r01 轮的同类记录见 `report/evidence/S5-T03/s5t03_takeover_20261024_r01/`。

## 2. 本轮更正要点（详见绑定文档 §9/§10）

- **B-1**：重绑到阶段4 **r04**（commit `7a9507ab4a2067d493b4d9ff47b331c747f33796`，JSON blob `611e6c7c…`）：
  两个彩色标签都 `maps_to_source_kind=camera`、`capture_time_available=true`，回放以 `timing_claim_scope=replay_only` 区分；
  v1 曾引用的 `f6fa9f0` 快照登记为 `SUPERSEDED_BY_R04`。
- **B-2**：乱序/回退采用 r04 `frame_sequence_rules` 的**拒绝并记 FAIL**（与重复同构）；新增 `frame_id` 回退、
  `result_seq` 回退两个必拒绝用例与「乱序帧框与前一帧逐值相同」断言。
- **N-1**：S5A-G0-v2 JSON 只修 stale 判定域**措辞**（行为不变），登记差异并提请正式 G0；哈希 `8eac7007…` → `10d24a39…`。
- **N-2**：长跑判据改为区间数 106572 × 16.89 ms（余量 +1.08 ms）。
- **N-3/N-4**：计数单位声明；帧级日志落盘 + 独立复算器（`console/recompute_from_log.txt` 两次 exit 0）。
- **N-5**：时间戳按实际值；**N-6**：`UR-2` RESOLVED；**N-7**：清单 `interfaces=[]` + `interfaces_not_applicable_reason`
  （首要理由＝无 `role=input` 文件）。

## 3. 原始输出文件

- `console/git_state.txt`、`console/handoff_check.json`（+`stderr.txt`）
- `console/takeover_checks.txt`（C1 已跟踪干净/无锁、C2 部署身份、C3 UR-2、C4 硬件空闲，均带真实 `*_exit=`）
- `console/deploy_and_ur2_verify.txt`（三产物与 README 的 `sha256sum`/mtime 原始输出）
- `run_meta.json`、`delivery_manifest.json`、`hashes_sha256.txt`

`CHECKS_OK`（如清单检查通过）仅代表包装/绑定检查通过，不代表独立审查、G0/G4/G5 或实物验收。