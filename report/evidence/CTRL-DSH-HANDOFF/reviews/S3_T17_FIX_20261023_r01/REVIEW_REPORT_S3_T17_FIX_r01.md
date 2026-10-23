# S3-T17 阶段A 修复轮独立复审报告（Reviewer，task-18 fix round）

- 评审对象：工作树 `D:\codex-worktrees\dbdf`（分支 `codex/stage3-video`），被审 **内容提交 F2 `60b00de`**、**复核/自证记录 G3 `f77f363`（HEAD）**。
- 上轮评审：`report/evidence/CTRL-DSH-HANDOFF/reviews/S3_T17_A_20261023_r01/REVIEW_REPORT_S3_T17_A_r01.md`（`CHANGES_REQUIRED`：B-1/B-2/B-3 + N-1..N-5）。
- 评审性质：**只读**；全部复算/实测脚本自写，验证只写 `D:\FPGA_Competition\tmp\review\S3_T17_FIX_20261023_r01\`（含一个 `git -c core.autocrlf=false` 传输克隆 `dbdf_clone_lf`、一个普通克隆 `dbdf_clone_crlf`、自造 5 个整帧夹具）。
- **未做任何硬件动作**：无 JTAG/COM4/hw_server/位流加载/烧录；未运行任何重型综合/实现/仿真。评审前后 dbdf `git status --short` 均为 `?? NA/`、`?? clockInfo.txt`，HEAD 未变。
- **不评价未执行的硬件步骤**；本报告不代表阶段3 颜色通过、G3/G4/G5 或任务验收。

## 结论：`CHANGES_REQUIRED`

三项原阻断（B-1/B-2/B-3）**经我独立复算/复现，实质已关闭**；但本修复轮**新引入 2 处非 ASCII 崩溃缺陷**（同一根因，落在两个交付工具里，均为文档化的自证/判定命令），另有余项：N-1 的关键事实陈述为**假**、N-3 在冻结 HEAD 上**不可复现**。

**阶段B 可执行性（明确回答）**：**可以**——一键执行器 `run_t17_color_retest.sh` 在 56 行 `export PYTHONUTF8=1`，我在克隆里实跑其 `judge` 路径：归档缺陷帧 **exit 1 且写出 JSON**、只修蓝帧 **exit 3 且写出 JSON**，符合语义；`preflight` 路径在同一克隆下 **exit 0**（`T17_PREFLIGHT_EXIT=0`）。**换言之，今晚用一键执行器跑阶段B 不会被下述缺陷挡住。** 但**不建议以现状冻结**：交付的判定器与自证工具在 README/自身 docstring 所给出的**独立命令**下会崩溃，并给出**错误退出码**。

## 1. 新发现：修复轮引入的两处非 ASCII 崩溃（阻断）

代码中引入字符 `'\u21d2'`（"⇒"，**GBK 不可编码**；本机 `core.autocrlf=true`、系统 gitconfig 亦 true，Python 在**非控制台 stdout**（管道/重定向，正是证据留存的常规方式）默认 `stdout_encoding=gbk`）。上轮评审的同类自证命令（pread 前）**不崩**，故属本轮回归。

### R-1 `verify_t17_blob_identity.py:75-77`（N-4 的改动）——无条件崩
```python
print(f"CORE_AUTOCRLF={autocrlf_value}"
      + ("（true ⇒ 若本仓库是 CRLF 检出的克隆，请用 git -c core.autocrlf=false clone 复核）" ...))
```
`core.autocrlf=true` ⇒ 该打印必含 `⇒` ⇒ 在管道/重定向下**任何一次调用都崩**：
| 我实跑（LF 克隆） | 真实结果 |
|---|---|
| `python -B .../verify_t17_blob_identity.py --repo-root <LF克隆> --commit HEAD --json-out ...`（未设 PYTHONUTF8） | **exit 1 + `UnicodeEncodeError` + 未写出 JSON** |
| 同上 + `PYTHONUTF8=1` | **exit 0**，`检查文件=66 不一致=0 提交内缺失=0 工作区含 CRLF=0`，`BLOB_BYTE_IDENTITY_OK` |
| CRLF 克隆 + `PYTHONUTF8=1` | **exit 1**，`46/46 不一致、46 含 CRLF`（失败证据保留正确） |

- 影响：`scripts/stage3_t17/README.md` §必读前提**逐字给出的 N-4 自证命令**在本机常规调用下崩；且退出码 **1 与该工具的「MISMATCH」退出码同值**，第三方会把「崩了」误读为「字节不一致」，或被告知不可复跑。
- 关闭条件：把 `⇒` 换为 ASCII（`=>`）或全程 `PYTHONIOENCODING=utf-8`/`sys.stdout.reconfigure(encoding="utf-8")`；并在 README 复跑命令里带上编码前提。

### R-2 `analyze_t17_bit_integrity.py:190 + 554-555`（B-2 的改动）——按输入条件崩
`reason` 字符串 `"WHITE_BIT_NOT_SET（白条字段位为 0 ⇒ 缺位）"` 经 `print("不可辨位：" + "；".join(cnt["not_discriminated"]))` 打印。
| 我自造/取用的帧 | 期望 | 未设 PYTHONUTF8（真实） | `PYTHONUTF8=1`（真实） |
|---|---|---|---|
| 我自造**缺陷帧**（全帧掩掉 B[4]/G[2]） | exit 1 | **崩（UnicodeEncodeError），未写 JSON**，进程码 1（与 DEFECT 同值，纯属巧合） | exit 1，JSON 写出，C7 对齐 14/16、严格 13/16 |
| 我自造**只修蓝**帧（应 atypical） | exit 3 | **崩，未写 JSON，进程码 1** ⇒ **错误结论（把「非典型」报成「复现缺陷」）** | exit 3，JSON 写出 |
| 归档缺陷帧 `bars_raw_frame_full.bin` | exit 1 | **崩，未写 JSON** | exit 1，JSON 写出 |
| 我自造**修好帧**（黑条残差在容差内） | exit 0 | exit 0（该帧无 WHITE_BIT_NOT_SET 位，不触发） | exit 0，C7 16/16 |
| 我自造修好帧 `--strict-black-bits` | exit 3 | exit 3（reason 无 `⇒`） | exit 3，C7 15/16 |

- 影响：**最难诊断的那条路径**（真的复现旧缺陷 / 只修好一路）恰恰取不到 `--json-out`；只修好一路时退出码 **1 而非 3**。README §常用命令第 35 行、判定器 docstring 用法均给出**不带 PYTHONUTF8 的独立命令**。
- 缓解事实：一键执行器 `export PYTHONUTF8=1`（第 56 行，既有代码），其 `judge`/`phase_judge` 路径实测正确（见上）；`--selftest` 走 `evaluate()` 不经过该 print，故 7/7 通过——**自测因此无法发现此缺陷**。
- 关闭条件：同上换 ASCII；并把「归档缺陷帧判 exit 1 / 只修一路判 exit 3 且写出 JSON」加入 `--selftest` 的 CLI 级回归（而不只是 `evaluate()` 级）。

## 2. 原三项阻断复核：**实质关闭**

### B-3 冻结版本前置（我自造祖先/非祖先）
前置改为「声明基线或其后代」（`--baseline-commit` 可重复 / `T17_BASELINE_COMMIT`，输出 `baselines[].relation`）。我在**传输克隆**内实跑（为隔离 HEAD 判据、把 7 件冻结产物按原哈希复制进克隆——见 §5 说明）：

| 场景（worktree=LF 克隆，HEAD `f77f363`） | 真实退出码 | relation | 结论 |
|---|---|---|---|
| 默认基线（`f94c25f`） | **0** `OFFLINE_GO` | descendant | ✓ |
| `--baseline-commit 60b00de`（F2，HEAD 的祖先） | **0** | descendant | ✓ |
| `--baseline-commit <HEAD 全长>` | **0** | equal | ✓ |
| `--baseline-commit 0bebc12`（无关提交；我自行 `merge-base --is-ancestor` 复核 exit 1） | **1** `OFFLINE_NO_GO` | unrelated，失败项仅「HEAD 不是声明基线或其后代」 | ✓ 判别力 |
| HEAD 前进到我在克隆里新造的提交 `4f193f2` | **0** | descendant | ✓ 不钉死未来提交 |
| `--baseline-commit <HEAD 的后代提交 f61aa8d>`（HEAD 落后于声明基线） | **1** | unrelated | ✓ 失败关闭 |
| dbdf 工作树默认 | **0** | descendant | ✓ 与自报一致 |

- 负向对照 stdout 实测只见 HEAD 失败项（产物哈希全 OK），证明该判据独立生效。**B-3 关闭成立。**
- 附带（非阻断）：**纯检测克隆**（无 `tmp/s3r06`）跑 preflight 得 exit 1，失败项**全部是 7 件冻结产物缺失**、**不含 HEAD 项**——即 HEAD 规则本身在克隆可复现，但 preflight 的 `exit 0` 依赖**未入库的本地 tmp 缓存**。今晚同机同树可用；第三方从零复跑会看到「缺产物」。建议在 README 注明这一依赖。

### B-2「已修好」可达性（我自造修好帧）
我**不用**被审 helper，自造 1280×720 整帧（白条 `(R,G,B)=(248,252,248)`、黑条 `(0,4,0)`，内存序 B,G,R），并另造缺陷帧（全帧 `b &= 0x7F`、`g &= 0xEF` 模拟同源同断）与只修一路帧：

| 我自造帧 | 真实退出码 | 判定 | C7 |
|---|---|---|---|
| 修好帧（黑条残差 = C5 容差内） | **0** | `BIT_INTEGRITY_PASS` | 对齐 **16/16** |
| 修好帧 `--strict-black-bits` | **3** | `INCONCLUSIVE_ATYPICAL`（仅 C7 失败） | 严格 **15/16** |
| 修好帧、黑条显示值 8（字段 2，恰在容差上限） | **0** | PASS | 16/16 |
| 修好帧、黑条显示值 12（字段 3，超容差） | **3** | atypical | 14/16 |
| 缺陷帧 | **1**（PYTHONUTF8=1 下） | `DEFECT_REPRODUCED` | 对齐 14/16、严格 13/16 |

⇒ ①「修好即 exit 0」可达；②`--strict-black-bits` 仍能指出严格口径差异；③容差边界与 C5 **精确对齐**（G 字段 ≤2 ⟺ 显示 ≤8；实测 2 通过、3 不通过）。**B-2 关闭成立。**

### B-1 位计数复算与两口径自洽
我自写 `my_bitcount.py`（自读帧字节、自算字段与逐位可辨性）复算：

| 量 | 我复算 | 与表内/执行方自报 |
|---|---|---|
| 字段位 R5+G6+B5 | **16** | 一致 |
| 结构性恒 0 低位 3+2+3 | **8**；16+8 = **24 = 3×8** | 一致 |
| 归档缺陷帧（白 248/236/120、黑 0,4,0） | 对齐 **14/16**、严格 **13/16**；对齐不可辨 = {B bit4, G bit2}，严格多出 **G bit0**（黑条 green 显示 4 ⇒ G6 字段=1） | 与判定表、判定器实测一致 |
| 修好帧 | 对齐 **16/16**、严格 15/16（不可辨 = G bit0） | 一致 |
| 8 位移位扩展 | 31<<3=248、63<<2=252、59<<2=236、15<<3=120 | 一致（表内已不再写 255） |

- **两口径是否会被混用**：md §2 的 C7 行在「仍为旧缺陷」列写明 `14/16（对齐口径；严格口径 13/16）`，「修好」列写 `16/16`；紧随的加粗段与 §3 边界、prep README §3、`scripts/stage3_t17/README.md`、JSON `criteria[6]`（`discriminated_used_for_verdict`/`discriminated_aligned`/`discriminated_strict_variant`/`verdict_mode`）与 `c7_basis` **四处一致地**写明「严格口径仅作对照、判定口径固定为对齐」。执行方把上轮 lead 的「13/16→16/16」混搭**明确登记为混搭**，处理正确。
- 唯一可读性小风险：「修好」单元只写 `16/16`，未在同格标注严格口径为 `15/16`（严格值在同段与 §3 已给）。建议补一格即可，**不构成阻断/误用风险**。**B-1 关闭成立。**

## 3. 复审五项在我自己的克隆中的复现（真实退出码）

| 项 | 我的命令与真实结果 | 与自报 |
|---|---|---|
| preflight（默认/负向） | 克隆：0 / `0bebc12`→1；dbdf：0 / 1（见 §2 表） | 一致 |
| `--selftest` | LF 克隆 `--selftest --fixture-dir <绝对> --json-out`：**exit 0**，`SELFTEST_PASS`，A/B/C/D/E/F=1/0/3/3/0/0、F 严格探针 3，**7/7 matched** | 一致 |
| 夹具 F（及严格探针） | 我另造修好帧与 selftest 生成的 `fixture_F.bin` 均 **0（C7 16/16）**；`--strict-black-bits` **3（C7 15/16）** | 一致 |
| `clone` 自证（带/不带 `-c core.autocrlf=false`） | **不带**：LF 克隆 `exit 0`、`66 文件 / 0 不一致 / 0 CRLF`（G3 记录值 46/0/0 是在提交 `60b00de` 上、文件数不同属正常）；**带**（普通克隆）：`exit 0` 语义下 `46/46 失配、46 含 CRLF`→工具 `exit 1`，失败证据**保留** | 一致（但见 R-1：不带 PYTHONUTF8 时工具先崩） |
| 交付态 `handoff_check` | `handoff_check.py --worktree dbdf --record handoff_record_stage3_delivered.json`（只读）→ **exit 1，PASS 7 / FAIL 1（检查项 a）/ SKIP 1** | **不一致（见 §4 N-3）** |

（另：`t17_fix_preflight_20261023_r01/run_log.txt` 尾行 `T17_PREFLIGHT_EXIT=0`；`preflight_frozen_head.stdout.txt` 记录的 HEAD 是 `60b00de`（G3 生成时），非 `525e4f35`——与「冻结修复提交」一致，不矛盾。）

## 4. 非阻断项复核（N-1..N-5）

- **N-1（未实质关闭，事实陈述为假）**：`format`/`bit_map`/`.md`/prep README/两处 docstring 已统一为「第一字节 `{b[4:0],g[5:3]}`、第二字节 `{g[2:0],r[4:0]}`」，`byte_order_evidence` 4 条与 `naming_limitation` 已加，阶段B 改数值判据——方向正确。**但**其第 4 条（DVP 字节序）标为「推断（未独立确认）」，理由写「本轮盘上未找到厂商 `cmos_8_16bit.v`（已被缓存清理）」，**该陈述与磁盘事实相反**：
  - 我在 dbdf 内实查：`cmos_8_16bit.v` 存在 **47 份**（去重后仅 2 种内容），含**已入库**的 `report/evidence/S3-T05/t05_github_ref_20261020_r01/cmos_8_16bit_ref.v`（3318 B）与设计 `vendor_src`（如 `tmp/s3r06/t04_sof_fix_20261020_r01/vendor_src/my_ip/ov5640_ip/src/cmos_8_16bit.v`）；
  - **45/45 份**含 `pdata_o <= {pdata_i_d0, pdata_i};`（先到的字节进**高**半字）。结合归档网表（`m_axis_tdata[15:10]=s_axis_tdata[10:5]`、`[7:3]=[15:11]`、`[23:19]=[4:0]`，`channel_mapping_report.json` 实读命中）与 rgb2dvi 通道注释，**该字节序在本树内有可用依据**，把它降级为「盘上没有」的推断**理由不成立**。
  - 影响：判定结论不受影响（数值判据正确、`naming_limitation` 的保守指引安全），但「依据不可得」是**不实陈述**，且浪费了可确认证据。关闭条件：改用/引用该源码（或改正为「缓存中该文件非唯一/需确认变体」等准确表述），并把通道命名从「身份依据」降为「别名」。
  - 残留命名：判定表 §1「后果」行、C1「对照组：R 未丢位」仍以通道名作身份说明，但同表已列 `命名限制` 行——**可接受**，建议阶段B 报告统一只写 offset0/1/2。
- **N-2（部分/自指）**：`.codex/STATE.md` 绑定已按 blob 口径记为 `85be520a…`——我复算 `dbdf@525e4f35` blob sha256 = `85be520a595e72a160a2a10af7e94dbf2ab07a10c2f9bf4c5ab9a59a9b4169dc` **完全一致**，另 3 条历史输入亦改为 blob 口径并加 `hash_convention`/`rolling_inputs`/`rolling_input_note`。**但 F2 同时改写了 `.codex/STATE.md`**（该提交 14 行变更），故在冻结 HEAD `f77f363` 上其 blob 为 `12d4f753…`，绑定**再次过期**（自指循环）。执行方已用 `rolling_input_note` 说明「随交接更新、按交接行提交复核」，属**已披露残余**，可接受。
- **N-3（未复现，见 §3）**：交付态 record 已刷新为 `base_commit=60b00de`，但其证据 `handoff_delivered_readonly.stdout.txt` 明载 **HEAD=60b00de**（G3 提交之前的时刻）。在**被审冻结 HEAD `f77f363`** 上复跑：**exit 1 / PASS 7 / FAIL 1（a）/ SKIP 1**——因为主仓工具 `verification/handoff_check.py:618` 是 `HEAD.startswith(base_commit)` 前缀比较，`60b00de` 不是 `f77f363` 的前缀。G3 提交信息里的「delivered-state → exit 0」**只在该提交自身的前一刻成立**，对冻结版本不可复现。评估：非阻断（工具在主仓、非本阶段可改；takeover README §5 已说明前缀语义），但**自证记录须写明「exit 0 的运行时刻 HEAD=`60b00de`」**，否则读者会误以为在冻结 HEAD 上成立。
- **N-4（已文档化，但被 R-1 破坏）**：`-c core.autocrlf=false` 已写入工具 README「必读前提」、两个判定器/preflight docstring、runner 头、takeover README、prep README；未加 `.gitattributes`（DSH 决定，属明示取舍）。失败证据（46/46）**保留未抹**。**唯一问题**即 R-1：文档化的复跑命令在非 UTF-8 stdout 下崩溃。
- **N-5（关闭）**：`PENDING_HARDWARE_NOT_EVIDENCE.md:3`、prep `README:4` 已改为「接管基线 `f94c25f`，本修复轮冻结 HEAD 见 STATE 交接行与 `t17_fix_20261023_r01/`」；runner 头与 `scripts/stage3_t17/README.md` 已补 `exit 4`（`T17_ADDR_STRIDE_MISSING`）与执行器退出码表。残留 `f94c25f` 命中仅 3 处，均为「接管基线」或「修复前 EXPECTED_HEAD」的**有意说明**，非过期引用。

## 5. 越界写入与主仓清洁

- 主仓 `D:\FPGA_Competition\tmp\3\S3-T17` **不存在**，`tmp\3` **整体不存在** ⇒ 自我登记的那次越界写入已完全还原 ✓。
- 主仓 `tmp\` 下除 `tmp\review\**`（**上轮评审目录** + **本次评审目录**，均为评审隔离区）外，**无任何 `fixture_*.bin`**；无本轮误写残留 ✓。`report/`、`docs/`、`sim/`、`verification/`、`vivado/` 以及我逐项扫描的其它目录，**10-23 11:00 之后无新写入**（唯一下一条见下）。
- 观察项（非本次评审所写，需归属说明）：主仓 `.codex/STATE.md` 的 mtime = **2026-10-23 11:09:28**（F2/G3 提交之后、本评审会话启动前后），但 `git status/diff` **与 HEAD 完全一致（无内容变更）**，疑为主仓写权方的 touch/重写；建议由 DSH 项目总控确认归属。
- dbdf 工作区 `git status --short` = `?? NA/`、`?? clockInfo.txt`（既有散落件）✓。
- 我自己的克隆/夹具均在 `tmp\review\S3_T17_FIX_20261023_r01\` 内，未落入主仓其它路径。

## 6. V/F/G 自证与版本事实

- **F2/G3 为新增提交、无 amend**：`git reflog show codex/stage3-video` 前两条为连续 `commit:`（`60b00de`、`f77f363`），**无 `commit (amend)`/rebase/reset**；`525e4f35 → 60b00de → f77f363` 线性且两级祖先关系均 `exit 0`；`--graph` 显示单线。
- **F2 范围文件在 G3 逐字节不变**：`diff --name-only 525e4f35 60b00de`（F2 13 文件）与 `diff --name-only 60b00de f77f363`（G3 24 文件）**交集为空**；且对 F2 的 13 个文件逐一比较 `60b00de:<f>` 与 `f77f363:<f>` 的 blob 哈希——**全部相同（0 差异）** ⇒ 「G 不得改动 F 的任何文件」成立，且比上轮更强（本轮 G3 连 F2 的证据目录都换了新目录/新文件名）。
- **失败证据保留**：`clone_with_autocrlf_on.json` = `BLOB_BYTE_IDENTITY_MISMATCH`、`46/46 不一致、46 含 CRLF`，`clone_with_autocrlf_on.stdout.txt` 亦在；未被抹掉或改写为通过 ✓。
- **离线自测 vs 验收**：`fix_record.md:78` 与 `manifest.json:106` 明写「不代表阶段A 通过、颜色通过或独立审查」；我扫描 fix 证据与 `scripts/stage3_t17/**`，**无**「验收通过/颜色通过/真彩通过」类肯定式宣称（命中全部为否定式）✓。
- **无硬件**：`report/evidence/S3-T17/hw_authorization.json` **不存在**（仅模板）；四个硬件阶段 `link/baseline/bars/restore` **未执行**；证据与脚本中**无** `T17_LINK_EXIT=`/`T17_BASELINE_CAPTURE_EXIT=`/`T17_BARS_CAPTURE_EXIT=` 的实测行（仅在 runner 源码里作为待打印字符串）、无 `program_hw_devices`、无自起 `hw_server` 痕迹 ✓。
- **STATE 行数**：dbdf `.codex/STATE.md` = **81 行**（`git cat-file blob` 与本地读取均为 81）；主仓 `.codex/STATE.md` = 80 行。81 行**略超 ≤80 建议**，属次要；内容为跨会话事实且未流水账化，**可接受**，建议下轮交接顺手压缩 1–2 行。

## 7. 问题清单（必须关闭后才能冻结/通过 G2）

| # | 位置 | 问题 | 影响 | 关闭条件 |
|---|---|---|---|---|
| **R-1**（新） | `scripts/stage3_t17/verify_t17_blob_identity.py:75-77` | 打印含 `⇒`(U+21D2)；`core.autocrlf=true` 时**无条件**非 GBK 可编码 ⇒ 管道/重定向下 `UnicodeEncodeError`，**未写 JSON、exit 1**（与该工具 MISMATCH 码同值） | README §必读前提给出的 N-4 自证命令在本机常规调用下崩，且可被误读为「字节不一致」 | 换 ASCII 或强制 UTF-8 stdout；README 复跑命令加编码前提；命令可复跑得 `exit 0 / 不一致=0` |
| **R-2**（新） | `scripts/stage3_t17/analyze_t17_bit_integrity.py:190,554-555` | `not_discriminated` 的 reason 含 `⇒`；凡出现 `WHITE_BIT_NOT_SET`（归档缺陷帧、只修一路）即崩 ⇒ **未写 `--json-out`**；只修一路时进程码 **1 而非 3** | 最关键的「复现缺陷 / 部分修好」路径丢失 JSON 并被错判为 DEFECT；自测不经过该 print，无法发现 | 换 ASCII；`--selftest` 增设 CLI 级回归（归档帧 exit 1、只修一路 exit 3，且 JSON 落盘） |
| **N-1'** | `t17_judgement_table.json` `byte_order_evidence[3]`、`bit_map.naming_limitation`、判定器 docstring | 「本轮盘上未找到厂商 `cmos_8_16bit.v`（已被缓存清理）」**为假**：盘上有 47 份（含 1 份入库），45 份含 `{pdata_i_d0,pdata_i}`，可支撑该字节序 | 依据陈述不实；可用证据未被使用 | 引用/改用该源码确权，或改为准确表述；通道名降为别名 |
| **N-3'** | `report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/handoff_check_delivered.*`、`t17_fix_20261023_r01/handoff_delivered_readonly.*` | 交付态 `handoff_check` 的 `exit 0` 仅在 `HEAD=60b00de` 成立；在冻结 `f77f363` 复跑 = **exit 1 / FAIL 1(a)** | 自证记录对冻结版本不可复现 | 记录中写明运行时刻 HEAD=`60b00de` 与复现命令；或注明须按祖先判定 |

## 8. 未做/边界

- 未执行任何硬件阶段（`link/baseline/bars/restore`）；未运行重型综合/实现/仿真；未改 dbdf 任何文件；未运行主仓工具以外的写操作；未修改主仓 `verification/handoff_check.py`。
- preflight 的「冻结产物哈希」部分我**把 dbdf 的 7 件 tmp 产物按原哈希复制进评审克隆**后复跑（仅为隔离 HEAD 判据）；克隆内 `tmp/` 为忽略目录，不影响仓库状态。**纯检测克隆**下 preflight 因缺 tmp 产物为 exit 1（见 §2 附带项），这是**交付物对本地缓存的依赖**，非 HEAD 判据问题。
- 本报告不代表阶段3 颜色通过、G3/G4/G5、任务验收或独立审查以外的任何结论。

## 9. 本目录证据索引

`dbdf_clone_lf/`（`-c core.autocrlf=false` 传输克隆）、`dbdf_clone_crlf/`（普通克隆）、`pf_clone_artifacts_{default,unrelated,ancestor,equal}.{json,stdout.txt}`、`pf_dbdf_{default,unrelated,ancestor}.{json,stdout.txt}`、`pf_clone_{baseline_descendant,futurehead_default,futurehead_equal,probehead_default}.*`、`make_my_fixtures.py` + `my_fixtures.json` + `myframe_*.bin`（5 帧）、`my_bitcount.py`、`an_*.{json,stdout.txt}`、`an_defect_both_masked.stdout.txt`（崩溃栈）、`selftest_clone.{json,out.txt}` + `selftest_fixtures/`、`blob_lf_clean.*` / `blob_crlf_utf8.*` / `blob_{lf,crlf}.out.txt`（崩溃栈）、`runner_probe/run_t17_color_retest_review.sh`（仅把 `WT` 改指评审克隆）、`runner_judge_{archived,partial}.out.txt`、`direct_partial.out.txt`、`handoff_delivered_review.json`、`analyzer_prefix_525e4f35.py`、`prefix_archived.*` / `new_archived{,_utf8}.*`。