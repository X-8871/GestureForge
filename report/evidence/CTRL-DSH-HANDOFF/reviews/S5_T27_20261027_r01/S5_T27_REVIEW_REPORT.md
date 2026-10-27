# S5-T27（task-27）交付 + S5-T04 冻结档案漂移 独立复审报告（r01）

- 复审方：DSH 独立 Reviewer（rev-s5），只读；复审期间未写 w5、未动硬件、未运行写仓库命令
- 时间：2026-10-27 19:47–20:05 UTC+8
- 被审工作树：`D:\codex-worktrees\w5`（分支 `stage5-display-prep`）
- 内容提交：`286ae4a2e2070bff7aa3b905687c856c4e78ca4b`；证据/HEAD：`a4c254264ff3b3512efa3cd6f1cbb3488d90f08c`
- 上一轮 PASS 对象：`2797cc3e072a8dfa1287f3e54cd606b46de16f99`（S5-T04 冻结复审）
- 前置冻结：`26b7439` + tag `stage5-offline-freeze-20261027`（77 成员 / 196 文件）
- 复审产物：`D:\tmp\review\S5_T27_20261027_r01\`（`logs/**`、独立检出 `work/clone`、归档 `work/s5t27_archive`、复现运行 `work/repro_regression`）

## 结论

**PASS —— 0 阻断项。**
- **红旗判定：不成立（diff 基点造成的误判）**。所列"冻结档案事后修改"全部发生在**我上轮 PASS 对象 `2797cc3` 之前**（提交 `521e7f9`/`3575dc3`/`2797cc3`）；`2797cc3..a4c2542` 对 `report/evidence/S5-T04/` 的 diff **为空**。冻结成员 187/187 逐路径未改（repo scope；9 个 host 引用不在 diff 范围），`frozen_set.json` 三个提交同一 blob `11e1aeb`，校验器在 `a4c2542` 仍 **exit 0 / 77/77**。**无需重审、无需回退**；仅留 1 条治理注记。
- **task-27 离线交付成立**：回放输入路径**在实现层**真实成立（现场重算字节、逐帧三要素、10 项透传、`replay_not_live` 强制、真调阶段4 契约）；离线回归 **30/0** 由评审独立复跑逐字段复现；`capture_time_ns` 可由阶段3 证据推出。
- 非阻断项 **5 条**（见下表，N1 建议在冻结/交接前修）。

## 一、逐项问题（位置 | 问题 | 影响 | 依据 | 关闭条件）

| # | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| **N1** 非阻断（建议冻结/交接前修） | `report/evidence/S5-T27/…/delivery_manifest.json` + `scripts/stage5_t27/run_s5t27_evidence.py` | 清单 17 项中 **1 项**（证据运行器源码）绑定的是**工作树 LF 字节**（`eeee8529…`，15578 B = blob 字节）；而 `.gitattributes` 没有 `-text` 规则，同一提交在**独立检出**（同机 `core.autocrlf=true`）得到 CRLF（15847 B，`f6f1c2c6…`）⇒ `check_stage_delivery --mode evidence` 在独立副本 **exit 2**（w5 上 **exit 0**） | 实质性结果全部可复现（我在独立检出里重跑证据运行器：`final_exit=0`，M1/M2 均 0，30/0）；但**提交本身不能保证** M1/M2 exit 0 的复现，构成"证据包对检出换行配置敏感"的交付瑕疵（与 S5-T04 r01 同类教训） | 字节实证：CRLF 15847 B 去 CR 后 15578 B，sha256 = `eeee8529eb7665ac…` = 清单声明值（+269 换行字节）；`git cat-file blob HEAD:… | sha256sum` = `eeee8529…`；克隆 checker `logs/s5t27_checker_evidence.txt`（exit 2）；w5 checker `logs/s5t27_checker_evidence_w5.txt`（exit 0） | 给新目录加**子目录** `.gitattributes`（`* -text`，避免改冻结的根 `.gitattributes`）→ 新 RunId 重生成证据/清单 → 在干净检出具 checker exit 0。不改变任何离线结论 |
| **N2** 非阻断（硬化） | `scripts/stage5_t03/s5t03_replay_colour_input.py:334-356` `assert_replay_record` | 守卫只校验 `frame_integrity.value == replay_source_file_sha256`，**不校验 length_bytes/algorithm**（我改 length+1、algorithm=md5 的记录被接受）；也不重读源字节（自洽伪造 sha 的记录被接受）。loader/build 路径的真校验是完备的（三要素全等、字节重算均拒收） | 只要记录由本模块 `build_replay_record` 产生就安全；绕过 build 手搓记录可绕过守卫 | `logs/injections.json`：`record frame_integrity.length+1`/`algorithm=md5` 未被拒收；`validate_frame_integrity(length+1/md5/value)` 三项均拒收 | 守卫增加 length/algorithm 与期望常量比对（或复用 `validate_frame_integrity`）并补负例；属下一轮取数 |
| **N3** 非阻断（文档） | `.codex/STATE.md` 第 62 行 vs 第 27–45 行 | 第 62 行仍写"`task-27` 整体 **NOT_RUN**"，与第 27–45 行"已交付"矛盾（该行是冻结时的历史陈述，未随交付更新） | 状态文档自相矛盾，易被下游误读为未交付 | STATE 第 27/62 行原文 | 改为"task-27 **离线部分已交付**；板上/实时/实物仍未做"；S5-T04 README §8.2 作为冻结时历史记录可保留 |
| **N4** 非阻断（范围刷新） | `scripts/stage5_t03/`（S5-T04 冻结 `file_set` 目录，冻结时 25 个跟踪文件） | task-27 在该**冻结目录内**新增 3 个跟踪文件（现 28 个）。冻结成员未改、校验器仍 77/77（`file_set` 语义只校验登记文件） | 冻结字节身份不受影响；但"冻结实现 = `scripts/stage5_t03/**`"的描述已不等于目录现状，且该校验器**按设计不检测**目录内新增文件 | `git ls-files scripts/stage5_t03`=28 vs `git ls-tree 26b7439`=25；校验器 exit 0 | 下一次重冻结按 doc §5 把新实现纳入冻结集，并同时修 S5-T04 F1–F5 |
| **N5** 非阻断（说明） | `test_s5t03_frozen_replay` / `test_s5t03_stage4_positive_replay` | 套件"`Ran 14 / 0 失败 / skipped 2`"中的 2 skip 是：①`test_s5t03_frozen_replay` **setUpModule** skip（宿主冻结包 fail-closed 拒载）；②`test_s5t03_stage4_positive_replay` **setUpClass** skip（阶段4 契约冻结时 `7228f513…` vs 现状 `4d8dc0d4…`，本卡未更新绑定）。task-27 自身 **14 项全 ok** | 交付说明若被读成"14 项全绿且覆盖阶段4 冻结包消费"，会高估覆盖；实际这 2 个上游模块在本环境被 skip（非 task-27 引入的回归） | `logs/s5t27_3modules_verbose.txt` skip 原因原文；模块单独 `Ran 14 OK` | 在 summary/STATE 注明 2 skip 的原因；阶段4 契约漂移由上游确认后更新绑定（不属本卡） |
| **G1** 治理注记（非缺陷） | `report/evidence/S5-T04/s5_freeze_20261027_r05/**`（非冻结成员） | 冻结提交 `26b7439` 之后、我上轮复审之前，该包文书/清单/console 被修正过一次（§1 误列纠正），并以 `doc_correction_after_freeze.txt` + README §9 + `results_freeze.doc_correction_after_freeze` 披露；`frozen_set.json` 与冻结成员未动 | 档案"可审身份"依赖提交而非不可变对象；tag 只固定字节身份 `26b7439` | 上述留痕；`frozen_set.json` blob 三提交同一；`2797cc3..a4c2542` S5-T04 diff 为空 | 保持"tag=字节身份 / 文书身份=提交"的引用规则；未来任何档案改动必须重新复审并登记（本轮无需动作） |

## 二、红旗四项判定

### 2.1 被改文件是否为冻结集成员 —— **全部非成员（0 个成员）**

`git diff --name-status 26b7439..286ae4a -- report/evidence/S5-T04/` 的 16 个路径，逐一对 `frozen_set.json`（成员 77：58 `file`+19 `file_set`）判定：

| 状态 | 路径 | 成员归属 |
|---|---|---|
| M | `…/s5_freeze_20261027_r05/README.md` | 非成员 |
| M | `…/console/check_evidence_mode_output.txt` | 非成员 |
| A | `…/console/doc_correction_after_freeze.txt` | 非成员 |
| M | `…/delivery_manifest.json` | 非成员 |
| M | `…/hashes_sha256.txt` | 非成员 |
| M | `…/results_freeze.json` | 非成员 |
| A | `…/s5_freeze_f6export_20261027_r01/` 下 10 个文件（5 console + manifest + 2 report + hashes + results） | 非成员 |

另做更直接的证明：**187 个 repo 侧冻结成员路径逐个 `git diff --quiet 26b7439 a4c2542` ⇒ 0 个改动**（9 个 host 绝对路径成员不在 repo diff 范围；校验器在 `a4c2542` 上 77/77 覆盖它们）。`frozen_set.json` 在 `26b7439`/`2797cc3`/`a4c2542` 三处同一 blob `11e1aeb60e03`。⇒ **不存在"冻结成员被事后修改"**。

### 2.2 披露情况 —— **如实且可核对；未"提前修 F2"**

- `console/doc_correction_after_freeze.txt` 原文：`date_utc8=2026-10-27T19:11:12+08:00`；`freeze_commit=26b7439…`；`change=README §1 第 2 项：删除误列的 scripts/stage5_s5a|s5b|s5c（实际不在冻结集内）；新增 §9 说明`；`invariant=冻结集成员/哈希、校验器 exit 0、注入自测 0/1/2、离线套件 142 OK 均未改变`；`reason=…生成器文案缺陷属冻结集成员，冻结后不改，登记为下一轮待修`。
- README §9 与 `results_freeze.json.doc_correction_after_freeze`（`checker_exit_after_correction=0`）、`checker_m2_exit=0` 同步登记。
- **与"留待下次"不矛盾**：本次纠正的是 README **§1 第 2 项**（冻结实现清单误列 s5a/b/c），**不是**我上轮 F2（README §6 "归档副本内跑 checker" 的措辞）——HEAD 上 §6 原文仍为旧措辞；F1–F5 **均未修**（`git diff 2797cc3 a4c2542 -- verification/verify_stage5_frozen_set.py scripts/stage5_t04/build_stage5_frozen_set.py report/evidence/S5-T04/` 为空），并在 STATE 第 20–25 行与提交 `98f34e3` 中逐条登记为"留到下一次重冻结时修"。
- 我上轮 PASS 记录被主仓忠实保存：`report/evidence/CTRL-DSH-HANDOFF/reviews/S5_T04_20261027_r01/` 下 `review_summary.json` sha256 `317848735171eb79…`、`S5_T04_REVIEW_REPORT.md` sha256 `eb517a52631a2305…`，与 STATE 第 18 行声明值**逐字节一致**（未改写复审证据）。

### 2.3 改动后包是否自洽（HEAD `a4c2542` 实测）—— **自洽**

| 检查 | 真实退出码 / 结果 |
|---|---|
| r05 `delivery_manifest.json` 25 条 files 哈希 vs 磁盘 | 0 条不符 |
| r05 `hashes_sha256.txt` 15 行 vs 磁盘 | 0 条不符 |
| `results_freeze.json` 记录 `verify=FROZEN_SET_VERIFIED/exit 0`、`checker_m1_exit=0`、`checker_m2_exit=0` | 与实测一致 |
| r05 `check_stage_delivery --mode evidence`（w5） | **exit 0 / CHECKS_OK** |
| `verify_stage5_frozen_set.py`（w5 HEAD） | **exit 0 / 77/77** |
| `frozen_set.json` sha256 | `109254238e2aede8ab9005ed153e768e611c3ba325a5b1b75b312b415408b1bf`（未变） |
| 26b7439→HEAD 语义 diff | README 11 行、console 3 行、doc_correction 新增 6 行、manifest 哈希更新+新条目、hashes 7 行、results 新增披露块与 `checker_m2_exit`；**无结论性字段被改** |

### 2.4 程序性判断 —— **可审身份未漂移，无需重审/回退**

- 事实：`git diff --name-status 2797cc3 a4c2542 -- report/evidence/S5-T04/` ⇒ **空**；`git diff --stat 2797cc3 a4c2542` 仅 `.codex/STATE.md` + task-27 文件/证据。即：**我上一轮 PASS 的对象之后，S5-T04 档案再无任何改动**。
- 所列"事后修改"（16 路径）与我上轮已审的 `26b7439..2797cc3` 增量**完全一致**（16 条，数量、路径一一对应），发生在 `521e7f9`/`3575dc3`/`2797cc3`。因此"改动发生在 PASS 对象之后"的判断**不成立**（diff 基点是冻结提交 `26b7439`，不是复审对象 `2797cc3`）。
- 结论：`26b7439`（tag）仍是冻结字节身份；`2797cc3` 是我 PASS 的文书身份；`a4c2542` 对 S5-T04 与 `2797cc3` 字节相同。**无需对档案重新复审，无需回退**。治理建议：下游统一引用"tag=字节、提交=文书"，且今后档案改动必须重新复审登记（G1）。

## 三、task-27 本体核查

### 3.1 基线与提交

| 检查 | 真实退出码 | 结果 |
|---|---|---|
| 提交存在/类型 | 0×5 | `26b7439`、`2797cc3`、`286ae4a`、`a4c2542`、`2a2d2cc` 均 commit |
| 祖先关系 | 0/0/0 | `2797cc3→286ae4a→a4c2542`；`26b7439→286ae4a` |
| 工作区 / index.lock | 0 / 不存在 | 干净（含未跟踪 0）、worktree gitdir 无锁 |
| 提交内容 | — | `286ae4a`：5 文件（实现 3 + 证据运行器 + 文档，1404 行新增）；`a4c2542`：13 文件（STATE + S5-T27 证据 12） |
| 未 push | 本轮远端 **不可核验**（`git ls-remote` 两次超时 rc=124，"expected flush after ref listing"）；本地无 upstream、`refs/remotes` 仅 `origin/main`，新提交仅本地 | 如实报告：不能本轮断言远端状态；上轮已核 tag 未 push，且 tag 仍指 `26b7439` |

### 3.2 实现层真伪 —— **真实**（非文档声明）

- `load_replay_source`：读绑定后**现场** `_sha256_file` + `stat().st_size`，与 `source_frame_sha256`/`source_frame_size_bytes` 比对；校验 `source_kind=camera`、`mode=offline_replay`、`timing_claim_scope=replay_only`、`capture_time_available=true`、`capture_time_ns>0`、`stride=width×3`、`BGR888/BGR/top_left`、`size=stride×height`。
- `frame_integrity_of` 每次重算；`validate_frame_integrity` 要求 **algorithm+value+length_bytes 三者全等**（我直接调用三项违规均被拒）。
- 记录携带 `REPLAY_SOURCE_FIELDS` **10 项**（实测 10/10 在位）；`replay_not_live=True` 强制；证据模式 `result_time_ns/inference_time_ns/end_to_end_latency_ns` 一律 `null`（实测 None）；`assert_replay_record` 真调用 **阶段4 `R.validate_result_record`**（我注入"删 geometry / frame_id=-1 / score=2.0 / 缺 state"四类均被阶段4 契约拒收）。
- 评审独立注入（32 例，30 例符合预期；2 例为 N2 守卫层差距）：

| 类别 | 用例 | 观察 |
|---|---|---|
| 记录级 | `replay_not_live=False` / `capture_time_ns=0` / 缺任一 `replay_source_*`（10 项逐个）/ `frame_integrity.value=0*64` / 证据模式设 `result_time_ns` | **全部拒收** |
| 记录级（N2） | `frame_integrity.length+1` / `algorithm=md5` | 守卫**未拒收**（loader/build 会拒） |
| 绑定级 | `capture=0` / `capture_available=False` / `source_kind=synthetic` / `mode=live` / `timing_scope=live` / `integrity.value`、`length`、`algorithm` 三类不符 / 缺必需字段 | **全部拒收** |
| 源帧 | 复制帧翻转 1 字节 / 截断 | **装载即拒收**（实测 sha 不符） |
| CLI | 真实绑定 selftest / 篡改帧绑定 | exit **0**（4 类必失败注入均 rejected）/ exit **2** |

### 3.3 `capture_time_ns = 1792776253000000000` 可核性 —— **可推出，成立**

- 换算：`1792776253 s` → UTC `2026-10-23T17:24:13Z` → **UTC+8 `2026-10-24T01:24:13+08:00`**（余 0 ns）。
- 出处：
  - 阶段3 窗口文档 `D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_stage3_window_20261024_r01\reference_frame_set.md` 第 3 行：**"采集时刻（UTC+8）：2026-10-24 01:24:13（导出完成 01:24:2x）；单次窗口内、板卡独占"**（同文件登记 `frame_full.bin` sha256 `939fce22…` / 2,764,800 B，与本卡源帧一致）。
  - 阶段3 绑定 `…\t05_replay_binding_20261025_r01\replay_input_binding.json`：`capture_time_available=true`、`source_capture_time_text=2026-10-24T01:24:13+08:00`、`source_capture_time_precision=one_second_as_recorded`、`capture_time_ns=1792776253000000000`、`clock_domain=replay_documented_wallclock`、`timestamp_source.path=reference_frame_set.md`、`epoch_note="UTC Unix epoch; derived from the documented UTC+8 wall-clock second, not a PS monotonic counter"`、`additional_precision_claimed=false`；limitations 明确"second-resolution documented wall-clock metadata only"。
- 语义判定：这是**文档化的真实抓取/冻结墙钟（秒级）**，不是曝光时刻、不是 PS 单调时钟、未增加精度；S5-T27 只**透传**该已存在字段（与 S5-T04 冻结集 host 成员同一绑定，字节一致），未新造数值。**可核**。

### 3.4 离线回归复现 —— **真实可复现**

在独立 `--shared` 检出（`a4c2542`，独立 `.git`，干净）内：

| 项 | 证据值 | 评审复跑 |
|---|---|---|
| 判定 | `REPLAY_OFFLINE_REGRESSION_PASS` | 同（exit 0，22 s） |
| 断言 | 30 项 / 失败 0 | 30/0，**逐条断言名与 pass 值相同** |
| 坐标 | `[{"x1":317,"y1":267,"x2":445,"y2":314}]` | 相同 |
| 帧关联 | 240 帧成对、每帧恰一次提交、语义唯一 `B_latest_result_overlay` | `frame_assertions.jsonl` **240 行**，全部成对、drawn、boxes=1 |
| 过期边界 | `age=200000000` 不过期；`200000001` 过期；显式 flag 过期 | 相同；`is_stale` 代码为 `float(age) > float(limit)`（**严格大于**） |
| 长跑 | 106 573 帧；106 572 × 16 890 000 ns | `= 1 800 001 080 000 ns` **精确**；计数单调、可复算；duplicate/out_of_order=0 |
| 判别力 | 篡改冻结包 ⇒ exit 2 | 复现 exit **2** |
| 1 帧重复标注 | `results.frozen_replay_package.replay_content_origin.note`、summary、doc §2、limitations 均写"冻结包仅含 1 帧结果，逐帧重复回放，不是新推理" | 明确，无"240 次真实推理"读法 |
| 套件 | `Ran 14 / 0 失败 / skipped 2`，exit 0 | 复现（14 项 task-27 全 ok；2 skip 见 N5） |
| 证据运行器（独立检出重生成） | — | `final_exit=0`，checker **M1=0 / M2=0**，新 RunId verdict PASS 30/0 |

### 3.5 证据自洽与边界诚实

- **w5 上**：S5-T27 `delivery_manifest.json` 17 项哈希 0 不符；`hashes_sha256.txt` 10 行 0 不符；`check_stage_delivery --mode evidence` **exit 0 / CHECKS_OK**；`--mode inputs` **exit 2**（包内已声明 NOT_APPLICABLE，未伪称通过）；M1 console exit 0；用最终清单再跑（等价 M2）exit 0。**独立检出**：仅 1 项 EOL 差异 → checker exit 2（N1，根因已实证）。
- **边界**：无"板上/实物/G/B 通过"正面断言（全量扫描 0 命中）；`capture_clock=PENDING_MEASUREMENT` 在 doc §4.2/§3(B5) 与 manifest limitations 一致；证据模式时间字段 `null`（`result/inference/end2end`），`capture_time_ns` 明示为"文档化墙钟"而非实测；B1–B10 表逐项"必须上板=**是**"，"部分/是"仅指**离线前置证据**（B5 注 `capture_clock` 仍 PENDING），**未称板级部分通过**；`task-27` 未做项在 doc §4 与 STATE 列明。

## 四、明确回答

1. **`286ae4a`+`a4c2542` 能否作为 task-27 交付？** —— **能（离线交付）**：实现层真实、回归 30/0 可独立复现、证据在 w5 自洽、边界诚实。**但 N1 必须在冻结/交接/把该包当作独立可复现身份之前修复**（否则同提交的干净检出 checker exit 2）；N2/N3/N5 随下一轮取数一并处理。
2. **回放路径是否真在实现层？** —— **是**。装载现场重算 sha256/字节数；逐帧 `frame_integrity` 重算；`validate_frame_integrity` 三要素全等才放行；10 项 `replay_source_*` 真实填充；`replay_not_live` 强制 true；真调阶段4 `validate_result_record`。我自建的 4 类指定注入 + 12 项绑定/帧注入全部被拒；仅守卫层的 length/algorithm 硬化不足（N2）。
3. **离线回归 PASS 是否诚实可复现？** —— **是**。独立检出复跑与证据 30/0 逐字段一致；240 行成对；106 572×16.89 ms = 1 800 001 080 000 ns 精确；`age==200 ms` 不过期、`+1 ns` 过期（代码严格 `>`）；"1 帧结果重复 240 次"明确标注；篡改冻结包 exit 2 复现。
4. **是否破坏 S5-T04 冻结的可审身份？** —— **没有**。16 个"事后修改"档案文件**全部非冻结成员**；187 个 repo 侧冻结成员 **0 改动**；`frozen_set.json` blob 三提交同一；`a4c2542` 校验器 77/77 exit 0；且 **`2797cc3..a4c2542` 对 S5-T04 档案 diff 为空** ⇒ 上轮 PASS 对象之后无漂移，**无需重审或回退**。所列修改实为 `2797cc3` 之前的已披露文字纠正（§1 误列 + §9），F1–F5 确未提前修复。

## 五、真实退出码汇总

| 步骤 | 退出码 |
|---|---|
| `cat-file -t` ×5 / ancestry ×3 | 0 / 0 |
| `git status --porcelain -uall`（复审前后） | 0（空）；index.lock 不存在 |
| `git ls-remote`（远端 tag/main） | **124（超时，本轮不可核验）** |
| `git diff 2797cc3 a4c2542 -- report/evidence/S5-T04/` | 0 且**空输出** |
| S5-T04 冻结成员逐路径 `git diff --quiet`（187 条） | 0 改动 |
| `verify_stage5_frozen_set.py --root w5`（HEAD） | **0 / `FROZEN_SET_VERIFIED` 77/77** |
| S5-T04 checker evidence（w5） | **0 / CHECKS_OK** |
| S5-T04 包清单/哈希自检 | 25 项 / 15 行，0 不符 |
| S5-T27 checker evidence（w5 / 独立检出） | **0 / 2**（后者=N1 EOL） |
| S5-T27 checker inputs（w5） | 2（N/A 声明，未伪称通过） |
| task-27 模块套件（独立检出） | **0**，`Ran 14 tests OK`，23.8 s |
| 3 模块套件 | **0**，`Ran 14 tests OK (skipped=2)`，22.4 s |
| 回归驱动（独立复现） | **0**，`PASS 30/0`，22 s |
| 篡改冻结包回归（判别力） | **2** |
| 证据运行器（独立检出全链路） | **0**，`selftest=0 regression=0 suite=0 checker_M1=0 checker_M2=0 final_exit=0` |
| 评审注入（32 例） | 30 符合预期 / 2 为 N2 守卫差距 |
| 复现构建（S5-T04 侧上轮已验；本轮未重跑） | — |

## 六、限制

- 未连接/加载位流/烧录/占用 JTAG 串口；未评价 B1–B10、G3/G4/G5。
- 远端状态本轮网络不可核验（rc=124）；本地无 upstream、新提交仅本地，上轮已核 tag 未 push。
- 未重跑 S5-T04 冻结运行器本身（上轮已独立复验其产物）；本轮只复验其档案与冻结成员。
- 独立检出使用 `--shared`（对象库与本仓共享）；对字节级结论无影响（checkout 由提交树生成）。
- 评审写入仅 `D:\tmp\review\S5_T27_20261027_r01\`（约 799 MB）；w5 复审前后 status 均空、无锁、HEAD/tag 未变。

## 评审日志索引（`D:\tmp\review\S5_T27_20261027_r01\logs\`）

`verify_s5t04_at_a4c2542.txt`、`s5t04_checker_evidence_w5.txt`、`s5t27_module.txt`、`s5t27_3modules.txt`、`s5t27_3modules_verbose.txt`、`s5t27_checker_evidence.txt`、`s5t27_checker_evidence_w5.txt`、`s5t27_checker_inputs_w5.txt`、`repro_regression.txt`、`runner_replay.txt`、`injections.json`、`injections_console.txt`、`verify_final.txt`。