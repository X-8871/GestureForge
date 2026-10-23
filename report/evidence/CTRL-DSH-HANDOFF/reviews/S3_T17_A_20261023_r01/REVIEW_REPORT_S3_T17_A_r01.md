# S3-T17 阶段A 独立评审报告（Reviewer）

- 评审对象：工作树 `D:\codex-worktrees\dbdf`（分支 `codex/stage3-video`），被审版本 **HEAD `525e4f35`**（F 内容 `900cd0a`→`f251402`→`9d5c638` / G `f52711d` / G2 `525e4f35`）。
- 评审范围：`report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/`、`report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/`、预留 `report/evidence/S3-T17/t17_color_retest_20261023_r01/`、`scripts/stage3_t17/**`。
- 评审性质：**只读**。全部复算与实测脚本自写；只写本目录 `tmp/review/S3_T17_A_20261023_r01/`。评审后 `git status --short` 仍为 `?? NA/`、`?? clockInfo.txt`（既有散落件），HEAD 未变。
- **未做任何硬件动作**：无 JTAG/COM4/hw_server/位流加载/烧录；门禁实测在隔离 mock 工作树内跑脚本副本（只替换 `WT` 一行）。

## 结论：`CHANGES_REQUIRED`

阻断 3 项（B-1 判定表 C7 数值不可复算；B-2「已修好」的通过判定不可达；B-3 冻结版本离线前置必然失败并阻断阶段B）；非阻断 5 项（N-1…N-5）。

**本评审不代表阶段3 颜色通过（硬件阶段未执行）；不评价未执行的硬件步骤。**

## 1. 命令与真实退出码（全部本人实跑）

| 命令 | 真实退出码 | 结论 |
|---|---|---|
| `check_t17_preflight.py --worktree D:/codex-worktrees/dbdf`（HEAD `525e4f35`） | **1** | `OFFLINE_NO_GO`，失败项「HEAD 不是本轮基线 f94c25f」；7 件冻结产物 + 判定器哈希**全 OK** |
| `analyze_t17_bit_integrity.py --frame bars_raw_frame_full.bin` | **1** | `DEFECT_REPRODUCED`；白条 (248,236,120)、黑条 (0,4,0)；蓝 bit7/绿 bit4 = 0.0000%/0.0000%（3840 像素） |
| `analyze_t17_bit_integrity.py --selftest` | **0** | `SELFTEST_PASS`，夹具 A/B/C = 1/0/3 全匹配 |
| `analyze_t17_bit_integrity.py --rows <不存在文件>` | **2** | 用法/输入错误语义成立 |
| 自造夹具 D（归档帧两处缺位均恢复，黑条随之被置位） | **3** | `INCONCLUSIVE_ATYPICAL`（C5、C7 失败） |
| 自造夹具 E（D 再把黑条清零） | **0** | `BIT_INTEGRITY_PASS`（证明 exit 0 可达） |
| 自造夹具 F（**判定表自己声明的 if_fixed**：白 248/252/248、黑 0,4,0） | **3** | `INCONCLUSIVE_ATYPICAL`，**仅 C7 失败**（C1–C6 全 PASS） |
| mock 门禁：`link`（无 `--allow-hardware`） | **3** | `T17_HW_BLOCKED=MISSING_ALLOW_HARDWARE_FLAG` |
| mock 门禁：`link --allow-hardware`（无 `hw_authorization.json`） | **3** | `T17_HW_BLOCKED=NO_HW_AUTHORIZATION_FILE` |
| mock 门禁：`baseline --allow-hardware`（`wong_go=false`） | **3** | `T17_HW_BLOCKED=HW_AUTHORIZATION_INCOMPLETE` |
| mock 门禁：`bars --allow-hardware`（`codex_hw_release=false`） | **3** | `T17_HW_BLOCKED=HW_AUTHORIZATION_INCOMPLETE` |
| mock：`all --allow-hardware` 且 preflight 失败 | **1** | `T17_ABORT=PREFLIGHT_FAILED`（未进入任何硬件调用；日志无 LINK/BASELINE/BARS 痕迹） |
| `bash -n run_t17_color_retest.sh` | **0** | 语法通过 |
| `verify_t17_blob_identity.py`（源工作树，HEAD） | **0** | 45 文件 / 0 不一致 / 0 CRLF → `BLOB_BYTE_IDENTITY_OK` |
| `git clone --no-local` 后同样自证 | **1** | 45 文件**全部 MISMATCH**、45 个含 CRLF（见 N-4） |
| `handoff_check.py --record handoff_record_stage3_delivered.json`（无 `--claim`，只读） | **1** | PASS 7 / **FAIL 1（检查项 a）** / SKIP 1（见 N-3） |
| 我自写 19 样本签名复算 | **0** | 19 样本 / **24,320 像素** / 最大置位率 **0.000% / 0.000%** ✓ |

## 2. 我自算的判定表数值（不调用被审脚本）

- 归档彩条帧 `bars_raw_frame_full.bin`（sha256 `1c52577e…`）y=200/360/500 三行一致：白条 **(R,G,B)=(248,236,120)**（R5=31、G6=59、B5=15），黑条 **(0,4,0)**（x=1200）。与表内 `with_old_defect` 列**完全一致**。
- 5/6/5 移位扩展算术：31<<3=248 ✓、63<<2=252 ✓、59<<2=236 ✓、15<<3=120 ✓ ⇒ 表内「8 位期望值是移位扩展、不是 255」**正确**（旧归档 `bars_values.txt` 写「31(255)」是错的，新表已改对）。
- 我自算判定项：C1 PASS、C2 FAIL、C3 FAIL、C4 FAIL（|G−B|=116）、C5 PASS、C6 FAIL、C7 FAIL。
- **字段位合计 16（R5+G6+B5），结构性恒 0 低位合计 8（R/B 各 3 + G 2）**；判定器实测 `discriminated=13、structural_na=8`（共 24 行），不可辨 3 位 = G6 bit2（缺位）、B5 bit4（缺位）、**G6 bit0（黑条残差 G=4 ⇒ G6=1，非缺位）**。
- 统计口径自洽：24320 = 19 × 1280 ✓；我用仓库内仍在的 19 个行样本复算，最大蓝 bit7 / 绿 bit4 置位率 = 0.000% / 0.000% ✓（归档扫描文本自身哈希 `9fd663b7…` 与其 `hashes.txt` 记录一致）。

## 3. F/G 自证一致性（在传输克隆中做）

- `git clone --no-local` → HEAD `525e4f35c2825d2afb084d05fec2a0f8f97781bf`、分支 `codex/stage3-video`、工作区干净 ✓。
- **F/G 分离成立且更强**：F（`9d5c638`）范围内的 **42 个文件在 HEAD 上逐字节不变（42/42，改动 0、删除 0）**；`t17_takeover_20261023_r01/hashes_sha256.txt` 的 F→HEAD 差异为空（G 加 2 行、G2 移出 2 行，净零）⇒「G 不得改动 F 的任何文件」成立。
- **未 amend**：`git reflog show codex/stage3-video` 为 5 条连续 `commit:`（`f94c25f`→`900cd0a`→`f251402`→`9d5c638`→`f52711d`→`525e4f35`），无 `commit (amend)`/rebase/reset；`f94c25f..HEAD` 线性且 `f94c25f` 为祖先（ancestor_exit=0）。（`--all` 中的 amend 记录全部位于 stage5/stage6/w2b/main 等**其他分支**，与本分支无关。）
- **失败证据保留**：`blob_byte_identity.txt` 存在且 `MISMATCH_COUNT=2`，两名分别为 `t17_color_retest_prep_.../manifest.json`、`t17_takeover_.../hashes_sha256.txt` ✓。
- **口径复核**：源工作树 45 文件 **UTF-8 无 BOM + LF = 45/45**，且工作区字节 == 提交 blob 字节（45/45）；各 `hashes_sha256.txt`/`selfproof_hashes_sha256.txt` 共 **34 条记录哈希与 blob 字节全部一致** ✓。

## 4. 门禁与退出码语义（第2项）

- **语义区分充分**：新判定器 `0=通过 / 1=复现旧缺陷 / 2=用法 / 3=非典型` 在 4 处显著标注（判定器 docstring、`scripts/stage3_t17/README.md`「判定器退出码」表、判定表 `exit_code_semantics_warning` + `.md` 第4行、prep README）。旧 `analyze_missing_msb_signature.py` 实读为 `0=符合签名 / 1=不符合 / 2=用法` ⇒ **确实相反且已注明**。
- **门禁真 exit 3**：三种缺参/缺授权场景实测均 **3**，且未进入任何硬件调用（mock 日志计数 0）。`link`/`baseline`/`bars` 三阶段均在动手前调用 `require_hw`；`all` 在 preflight 失败时先 abort。
- **未发现本交付物内的绕行路径**（离线阶段不碰硬件；`require_hw` 需同时满足 `--allow-hardware` 与授权文件两字段）。附带说明：门禁是流程性控制，能写 `report/evidence/S3-T17/hw_authorization.json` 的人可自行放行；且被复用的旧脚本 `scripts/stage3_t03b/run_xsdb.sh`、`scripts/stage3_t05/run_t05_board_capture.sh` 自身无门禁——属既有工程工具，不在本任务交付范围，建议阶段B 由总控统一加前置。

## 5. 无硬件动作（第4项）

- 全树仅存在 **模板** `.../t17_color_retest_prep_20261023_r01/evidence_template/hw_authorization_template.json`；`report/evidence/S3-T17/hw_authorization.json` **不存在** ✓。
- 证据中**无** `T17_LINK_EXIT`/`T17_BASELINE_CAPTURE_EXIT`/`T17_BARS_CAPTURE_EXIT`/`T17_DUMP_RESUME_OK`/`T17_JTAG_LINK=OK`/`program_hw_devices`/自起 `hw_server` 痕迹 ✓。
- `PENDING_HARDWARE_NOT_EVIDENCE.md:8` 明确「**未执行**：`link`/`baseline`/`bars` 三个硬件阶段。本轮**未接触硬件**（无 JTAG/COM4/hw_server/烧录）」；run 目录 `manifest.json` 有 `not_run: ["link/baseline/bars/restore"]`；`exit_codes.txt:33`、prep README §7 均如实记为未执行 ✓。**未发现任何把未执行硬件步骤写成已执行的表述**。

## 6. 两处 STATE 事实更正（第5项）：**属实**

- 主 `.codex/STATE.md` 阶段3 行**原记** HEAD `29c7cf0`（2026-10-21 20:01 交接提交）并写「**无人 CLAIM** 即停在…」——见 `9307377`（HL-T29）对该行的 `-` 侧原文 ✓。
- `22b8b64` 存在：**2026-10-21 21:36:07 +0800**，「S3-T05 DSH 认领阶段三（CLAIMED→IN_PROGRESS）+ 根因签名复核」；其 STATE 改动把交接行改为 `负责人=DSH 阶段三总控`、`状态/下一接手方=IN_PROGRESS / 当前由 DSH 阶段三总控持有（无让出）` ✓。
- 实际 HEAD 确为 `f94c25f`（2026-10-22 15:19:52，S3-T05 缓存清理），非 `29c7cf0`（2026-10-21 20:01:35）✓。
- `9307377`（HL-T29）已把该行更正为 `f94c25f`，并明写两处「**更正**」：HEAD 原记不准、以及「DSH 已于 10-21 21:36（`22b8b64`）CLAIMED→IN_PROGRESS，故『无人 CLAIM』不成立」✓。更正由主目录写权持有方完成，符合单写规则。

## 7. 禁止声明扫描（第6项）：未发现违规

- 「颜色/真彩/验收 通过」类命中**全部是否定式**：`不得据本目录宣称颜色通过`、`本包不宣称颜色通过`、`颜色未通过`、`仅机器部分通过不构成颜色验收通过`、第9步「目视通过」为待执行步骤描述 ✓。
- **无**「离线自测通过 = 验收通过」的等价表述；`requires_human_visual=true` 在脚本与 JSON 中 7 处出现；判定表边界第4条明写「不等于 G3/G4/G5，也不等于独立审查」✓。
- **无**注入/回放类结论（扫描为空），故不存在未标注适用范围的注入/回放声明 ✓。
- 轻微用词：主 STATE（HL-T29，主仓库，非本工作树）已写「`task-17` 阶段A 已完成」，同句亦写「A 包**待独立评审**」——建议在本评审结论落定后同步该行。

## 8. 问题清单

### 阻断（必须关闭后才能进入阶段B/通过 G2）

| # | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| B-1 | `t17_judgement_table.md:27`、`t17_judgement_table.json:41`（criteria[6]）、`:44`（boundaries 第1条）、prep `README.md:38` | C7 写「9/11 → 11/11」「R5+G6+B5=16 位中的 11 个字段位；低 5 位为移位填充」，与工具口径（16 字段位 + 8 结构性低位；归档帧 `discriminated=13`）互不相容 | 核心判定项 C7 期望值不可复算；报告照抄即自相矛盾，C7 不能作为验收依据 | 我自写复算 + `judge_archived_bars.json` 的 C7；`analyze_t17_bit_integrity.py:143-174,249-261` | 改为 16 字段位/8 结构性低位；期望值写成「缺陷 13/16（黑条残差另使 G6 bit0 不可辨；黑条为 0 时 14/16）／修好 16/16」；md、json、README 三处一致 |
| B-2 | `analyze_t17_bit_integrity.py:143-174`（per_bit_table）、`:247-251`（C5/C7）；判定表 C5「黑条允许 G≤8」+ if_fixed 黑条 `0,4,0`；prep `README.md:37-38` | C7 要求黑条字段位为 0，与 C5 容忍黑条 1 LSB 残差冲突：按**判定表自己声明的 if_fixed 值**构帧，C1–C6 全 PASS、C7 FAIL ⇒ `INCONCLUSIVE_ATYPICAL`(3)，而非表内声明的 `BIT_INTEGRITY_PASS`(0) | 硬件真修好时最高结论（exit 0 ⇒ 可建议关闭颜色子项）在传感器自身彩条图案下不可达；现场会得「非典型、不得当通过」，有误判为未修好的风险 | 夹具 F（按表内 if_fixed）= exit **3**，仅 C7 失败；夹具 E（黑条清零）= exit **0**；`--selftest` 无「两处缺位均恢复但黑条有残差」用例（`:335-339`） | 让 C7 与 C5 容差一致（按白/黑实测字段值判定可辨性，或对落在 C5 容差内的黑条位不计 NOT_DISCRIMINATED）；把「双缺位恢复 + 黑条残差 4」加入 `--selftest` 期望 exit 0；同步重算判定表 C7 |
| B-3 | `check_t17_preflight.py:32`（`EXPECTED_HEAD=f94c25f`）；`run_t17_color_retest.sh:233`（preflight 失败即 abort）；prep `README.md:71,77` | 在**被审冻结 HEAD `525e4f35`** 下实跑前置：**exit 1 = OFFLINE_NO_GO**（「HEAD 不是本轮基线 f94c25f」）⇒ `all` 必然 `T17_ABORT=PREFLIGHT_FAILED`(1)，阶段B 到不了硬件阶段；自报的 `OFFLINE_GO exit 0` 只在 `f94c25f` 成立 | 交付物在其自身冻结版本上无法按文档启动阶段B；`preflight.json`/`t17_preflight_now.json`（HEAD=f94c25f）不能作为阶段B 开工前置证据 | `preflight_at_frozen_head.json`/stdout（exit 1）；mock 门禁 5（preflight 失败→abort，未触硬件） | HEAD 校验改为接受已声明交付基线/祖先或参数化并写明更新办法；在冻结 HEAD 重跑留 `OFFLINE_GO`（7 件产物哈希我已复核全 OK）；同步 README §5 与证据内 HEAD 引用 |

### 非阻断（建议同轮修复；不阻断阶段B 前置准备）

| # | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| N-1 | `t17_judgement_table.json:9`(format) vs `:13-15`(bit_map)；`.md:13-14`；prep `README.md:25`；两个判定器 docstring | 同文既写「第一字节={g[2:0],b[4:0]}、第二字节={r[4:0],g[5:3]}」，又写「第一字节 MSB = B[4]」；按前者缺位应落在 R 与 G，按后者（与观测一致）落在 B 与 G，二者不可同真 | C1「R 未丢位（对照组）」的身份依据不成立；「蓝 bit7」等通道命名在阶段B 报告中不能直接引用；数值判据（C3 查 offset0、C1 查 offset2）仍可区分，机判结论不受影响 | 我复算白条内存三字节 = **120/236/248**（offset0 缺位、offset2 完好），与表内观测列一致、与表内 format+「两字节 MSB 同线」推出的通道相反；自洽写法应为第一字节={b[4:0],g[5:3]}、第二字节={g[2:0],r[4:0]} | 用视频管道源码或受控单比特实验确认字节序/解包，然后统一改正 json/md/README/两处 docstring 的 format 与通道标签 |
| N-2 | `t17_artifacts_verified.json:86` | `sources_referenced[0]`（`.codex/STATE.md`）记录 `6ef6d7fd…`，实际（LF/blob 口径）为 `85be520a…`，CRLF 口径 `a9b7d764…`，均不匹配 ⇒ 记录后内容已变 | 输入绑定失效（本项目「实际源码文件哈希」要求下的口径缺陷）；不影响判定表与门禁 | 我的实算（源工作树 CRLF=0，`git cat-file blob HEAD:.codex/STATE.md`） | 重算更新该哈希，或注明 `.codex/STATE.md` 为滚动输入并给出取值提交 |
| N-3 | `t17_takeover_.../exit_codes.txt:15-20`、`README.md:68-73` | 按文档用 delivered record 只读复跑：**exit 1，PASS 7 / FAIL 1（检查项 a）/ SKIP 1**（record `base_commit=900cd0a` 已非 HEAD `525e4f35` 的字符串前缀） | 文档承诺的「交付状态复核 exit 0」在冻结版本不可复现；第三方会看到 `HANDOFF_FAILED`，可能误读为接管无效；README §5 的补救同样失效 | `handoff_delivered_at_frozen_head.txt`（我实跑） | 证据中写明「复核须在当轮 HEAD 或按祖先判定」及复现命令；或由持有工具写权方改为祖先校验 |
| N-4 | `t17_takeover_.../README.md:48-66`(§4)；`verify_t17_blob_identity.py:85-91` | `git clone --no-local` 后自证：45 文件全部 MISMATCH、45 个含 CRLF、exit 1；根因本机 `core.autocrlf=true`（系统级 gitconfig）而 `.gitattributes` 只有 S2A 各段 `-text`，未覆盖 S3-T17 三范围 | 记录哈希基于 LF，克隆工作区哈希全部不匹配 ⇒「第三方可复跑」需加参数；**blob 口径本身正确**（我复算 34/34 记录哈希与 blob 一致） | `clone_blob_identity.json`(45 mismatch)、`source_blob_identity.json`(45/0/0 exit 0)、`verify_recorded_hashes.py` 输出 | 由有写权方为 `report/evidence/S3-T17/**`、`report/evidence/S3-CTRL/S3-T17/**`、`scripts/stage3_t17/**` 增加 `.gitattributes` `-text`；或把「工作区口径须 `-c core.autocrlf=false`」写成必读前提（README §4 已有，建议提升为前置条件） |
| N-5 | `t17_color_retest_.../PENDING_HARDWARE_NOT_EVIDENCE.md:3`、prep `README.md:4`；`run_t17_color_retest.sh` 头注释 | 基线 HEAD 仍写 `f94c25f`（非冻结 `525e4f35`）；执行器头注释只列 0/1/2/3，但 `:124` 会 `exit 4`（ADDR/STRIDE 缺失） | 读者对被审版本与执行器退出码集合理解偏差 | 实读文件内容 | 更新为冻结 HEAD 并补 `exit 4` 说明 |

## 9. 汇总

- 自报项复核结论：接管 `--claim` exit 0/PASS 9 **留痕一致**；判定器四类退出码语义 **成立**；归档帧判定 exit 1 **复现**；离线前置 `OFFLINE_GO` **仅在 f94c25f 成立**（冻结 HEAD 下为 1）；硬件门禁三场景 **真 exit 3**；全范围 blob 自证 **在源工作树成立（45/0/0 exit 0）**、在传输克隆不成立；F/G 分离与未 amend **成立且经逐字节验证**；两处 STATE 更正 **属实**；无硬件痕迹、无禁止声明。
- **不通过原因**：判定表 C7 的核心数值不可复算（B-1）、且按其自身 if_fixed 值无法得到其声明的通过结论（B-2）、冻结版本离线前置阻断阶段B（B-3）。
- 声明：本评审**不代表**阶段3 颜色通过（硬件阶段未执行）；**不评价**未执行的硬件步骤；`PASS` 亦不代表 G3/G4/G5。

## 10. 本目录证据索引（评审产物）

`preflight_at_frozen_head.{json,stdout.txt}`、`judge_archived_bars.{json,stdout.txt}`、`selftest_reproduced.*`、`judge_usage.*`、`judge_fixture_{D,E,F}.*`、`fixture_{D,E,F}*.bin`、`make_fixture*.py`、`recompute_judgement_myself.{py,json}`、`recompute_signature_19rows.{py,out.txt}`、`gate_tests_mock.{sh,out.txt}` + `mock_wt/`、`clone_blob_identity.json`、`source_blob_identity.*`、`verify_recorded_hashes.py` + `recorded_hashes_check.out.txt`、`handoff_delivered_at_frozen_head.txt`、`dbdf_clone/`。