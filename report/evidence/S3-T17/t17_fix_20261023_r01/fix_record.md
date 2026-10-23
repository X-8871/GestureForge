# S3-T17 阶段A 修复记录（评审 `CHANGES_REQUIRED` → 修复轮）

- 被审版本：`525e4f35`（评审报告 `tmp/review/S3_T17_A_20261023_r01/REVIEW_REPORT_S3_T17_A_r01.md`）。
- 修复方：DSH 阶段3 总控（`stage3-lead`，看板 `task-18`）；工作树 `D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`。
- **本修复轮未接触硬件**（无 JTAG/COM4/hw_server/位流加载/烧录）；颜色子项仍 `DEFERRED_PENDING_MODULE`。
- 冻结 HEAD 与"修复后重跑"的真实退出码见同目录 `report/evidence/S3-T17/t17_fix_20261023_r01/`（自证提交）。
  本文件中的命令/退出码为**修复过程中在 `525e4f35` 上的实测值**，已逐条给出。

## 一、阻断（3/3 关闭）

### B-1 判定表位计数算错/不可复算 → 关闭
- 位置与改法：
  - `t17_judgement_table.md:27` → 「**14/16**（对齐口径；严格口径 13/16） / **16/16**」+ 计数依据行；
  - `t17_judgement_table.json` `criteria[6]`（C7）→ `16/16` / `14/16（严格 13/16）`，并新增
    `c7_basis`（`field_bits_total=16`、`structural_zero_bits_total=8`、算式字符串、两种口径的实测值）；
  - `t17_judgement_table.json` `boundaries[0]` 与 prep `README.md` §3 → 16 字段位 / 8 结构性低位。
- 可复算依据：R 字段 5 + G 字段 6 + B 字段 5 = **16**；R/B 结构性低位各 3、G 结构性低位 2 = **8**；`16+8=24=3×8`。
- 实测（判定器自身输出，归档缺陷帧 `bars_raw_frame_full.bin`）：
  `字段位 16 / 结构性恒 0 8（共 24）；口径=TOLERANCE_ALIGNED_WITH_C5；可辨 14（对齐口径 14、严格口径 13）`
  —— **评审给出的 13/16 对应"严格口径"**：其第 3 位来自黑条 1 LSB 残差（`G=4 ⇒ G6=1 ⇒ G6 bit0`），
  与 C5 的 `G≤8` 容差冲突（见 B-2）。修复后表内同时写明两种口径，且**判定口径固定为对齐口径（14/16→16/16）**，
  严格口径仅由 `--strict-black-bits` 复现，用于自证修复可见性。

### B-2「已修好」的通过判定不可达 → 关闭
- 原因：`per_bit_table` 要求黑条字段位必须为 0，与 C5 的 `G≤8` 冲突；按表内 `if_fixed`（白 248/252/248、黑 0,4,0）构帧时
  C1–C6 全 PASS、仅 C7 FAIL ⇒ `INCONCLUSIVE_ATYPICAL(3)`。
- 改法（`analyze_t17_bit_integrity.py`）：
  1. 新增 `FIELD_TOLERANCE = {R: TOL_BLACK>>3 = 1, G: TOL_BLACK>>2 = 2, B: 1}`；`per_bit_table(..., strict_black_bits=False)`
     默认对**落在容差内的黑条字段值**不判不可辨（与 C5 一致）；
  2. `evaluate` 同时输出 `per_bit_aligned` 与 `per_bit_strict_variant`，`per_bit_count` 记录口径与两种计数；
  3. 新增 `--strict-black-bits` 仅用于复现旧口径（对照/自证）；
  4. `--selftest` 新增夹具 **D**（两处缺位 OR 恢复、黑条随之被置位 ⇒ 非典型）、**E**（D 再清黑条 ⇒ 通过）、
     **F**（判定表自声明 `if_fixed` ⇒ 对齐口径 **exit 0**）与 **F 的严格口径探针**（⇒ exit 3）。
- 实测（修复中，真实退出码）：
  - `python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --selftest` → **exit 0**，7 例全 `matched=True`
    （A=1、B=0、C=3、D=3、E=0、**F=0**、F 严格探针=3）；
  - `--frame <夹具F>` → **exit 0**（`BIT_INTEGRITY_PASS`，C7 `16/16`）；
  - `--frame <夹具F> --strict-black-bits` → **exit 3**（`INCONCLUSIVE_ATYPICAL`，仅 C7 失败，`15/16`）
    ⇒ 证明①修好后可达 exit 0、②本次修复对旧口径有判别力。

### B-3 冻结版本离线前置必然失败（到货即卡死）→ 关闭
- 原因：`check_t17_preflight.py:32` 把 `EXPECTED_HEAD` 钉在 `f94c25f` ⇒ 在冻结 HEAD 上 `OFFLINE_NO_GO`(1)，
  `run_t17_color_retest.sh all` 必然 `T17_ABORT=PREFLIGHT_FAILED`。
- 改法：改为**「声明基线或其后代」**判定（`git merge-base --is-ancestor`），基线可参数化
  （`--baseline-commit <rev>` 可重复 / env `T17_BASELINE_COMMIT`），并把关系写入报告
  （`checks.git.baselines[].relation = equal|descendant|unrelated`、`head_check_rule`）。
- 实测（修复中，真实退出码）：
  - `check_t17_preflight.py --worktree D:/codex-worktrees/dbdf`（HEAD `525e4f35`）→ **exit 0 `OFFLINE_GO`**，
    基线关系 `f94c25f=descendant`；
  - 负向对照 `--baseline-commit 0bebc12`（无关提交）→ **exit 1 `OFFLINE_NO_GO`**
    （失败项「HEAD 不是声明基线或其后代」）⇒ 检查仍有判别力；
  - prep `README.md` §5 步骤 1 的期望已同步（写明基线与后代规则、参数化方法）。

## 二、非阻断（5/5 处理）

| # | 处理 | 位置/实测 |
|---|---|---|
| N-1 | 统一 `format`/`bit_map`/README/两处 docstring：**第一字节 `{b[4:0],g[5:3]}`（MSB=B[4]）、第二字节 `{g[2:0],r[4:0]}`（MSB=G[2]）**；新增 `byte_order_evidence`（4 条，含"字节序属推断、需阶段B 确认"）与 `naming_limitation`；阶段B 报告改用数值判据（offset0 bit7 / offset1 bit4 / offset2 完整） | `t17_judgement_table.json:9,12-16`、`.md:13-14`、prep `README:25`、`analyze_t17_bit_integrity.py` docstring |
| N-2 | `.codex/STATE.md` 绑定改为 **blob（LF）`85be520a…`**（= 评审实测值）；顺带把另外 3 条历史输入改为 blob 口径（`t05_color_msb…/manifest.json`→`d445888f…`、`bars_values.txt`→`2c75adca…`、`S3-T14 README`→`d23cdaf7…`）；新增 `hash_convention` 与 `rolling_inputs/rolling_input_note` | `t17_artifacts_verified.json` |
| N-3 | 交付态复核 record 的 `base_commit` 随冻结 HEAD 更新，并在 `525e4f35` 上重跑得 **exit 0**；takeover `README.md` §5 同步；并注明"推荐由主仓写权方把检查项 a 改为祖先判定（本阶段无权改主仓工具）" | takeover `README.md` §5、交付态复核输出（自证提交） |
| N-4 | **不加 `.gitattributes -text`（DSH 决定）**；改为把 `-c core.autocrlf=false` 写进**必读前提**：`scripts/stage3_t17/README.md` 新增「必读前提」节、两个判定器/前置 docstring、runner 头注释、takeover `README.md` §4、prep `README`；`verify_t17_blob_identity.py` 打印 `CORE_AUTOCRLF` 并在 true 时提示；复审**带/不带该参数各跑一次**（结果见自证提交） | 同左 |
| N-5 | 残留基线引用更正：`PENDING_HARDWARE_NOT_EVIDENCE.md:3`、prep `README:4`（改指向本轮冻结 HEAD + 接管基线）；runner 头注释补 **exit 4**（`T17_ADDR_STRIDE_MISSING`）；`scripts/stage3_t17/README.md` 新增执行器退出码表（含 4）与 C7 口径说明 | 同左 |

## 三、过程中发现并自行纠正的问题（如实登记）

- **越界写入（自我纠正，已完全还原）**：修复中执行 `--selftest` 时误用相对路径 `--fixture-dir tmp/3/S3-T17/…`，
  而当前 cwd 是主仓 `D:\FPGA_Competition`，于是在主仓 `tmp\3\S3-T17\t17_analyzer_selftest_r02\` 生成了 5 个夹具
  （2,764,800 B ×5）。已核实路径后**只删除该目录与随之产生的空目录**（`tmp\3\S3-T17`、`tmp\3`），
  主仓 `tmp` 恢复原状；后续一律使用绝对路径。**除此之外本轮未写主仓。**
- **口径不一致**：`sources_referenced` 中 4 条历史输入原按工作区（CRLF）字节记录，与本包 `hash_convention`
  的 blob（LF）口径不一致；已按 blob 重算（见 N-2）。

## 四、边界与未做项

- 未执行任何硬件阶段（`link`/`baseline`/`bars`/`restore`）；硬件双前提（Wong 开工信号 + Codex 书面让出/时间窗）未齐，
  `hw_authorization.json` 不存在 ⇒ 执行器对硬件阶段一律 exit 3。
- 未改主仓工具 `verification/handoff_check.py`（检查项 a 仍为前缀匹配）；未加 `.gitattributes`。
- 本记录**不代表**阶段A 通过、颜色通过或独立审查通过；复审由 DSH 项目总控另派。