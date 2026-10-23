# scripts/stage3_t17：阶段3 色彩复测工具（task-17）

到货前离线准备 + 到货后一键复测。全部工具**默认不接触硬件**；硬件阶段需双前提放行。判定口径见
`report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/t17_judgement_table.json`。

## 必读前提（评审 N-4）

- 本仓库系统级 **`core.autocrlf=true`**，而 `.gitattributes` 只覆盖 S2A 各段（DSH 已决定**暂不为本三范围加 `-text`**）。
  因此：**按工作区口径**复核哈希/自证必须用 `git -c core.autocrlf=false clone`（或 `git cat-file blob <rev>:<path>`）；
  否则克隆工作区会是 CRLF，与按 LF 记录的哈希全部不匹配。
- 复跑自证示例：
  ```bash
  git -c core.autocrlf=false clone --shared -b codex/stage3-video D:/FPGA_Competition <空目录>
  python -B <空目录>/scripts/stage3_t17/verify_t17_blob_identity.py --repo-root <空目录> --commit HEAD
  ```
- 离线前置的 HEAD 判据是「**声明基线或其后代**」（`git merge-base --is-ancestor`）；基线默认 `f94c25f`，可用
  `--baseline-commit <rev>` 或 env `T17_BASELINE_COMMIT` 覆盖（评审 B-3）。
- **编码前提（评审 R-1/R-2 已修；**覆盖边界**见 Q-5）**：四个 Python 工具入口都强制 `stdout/stderr = UTF-8 + LF`，
  因此**不需要设置 `PYTHONUTF8`**，在 GBK 控制台或在管道/重定向下都不会因非 GBK 字符崩溃。
  **三层防护与各自覆盖边界（如实说明，评审 Q-5）**：
  ① 入口 `reconfigure(utf-8)`——覆盖「GBK 环境本身」；② 源码内无 `U+21D2`（ASCII `=>`）——覆盖「打印非 GBK 字符」；
  ③ `analyze_…` 的「JSON 先落盘 + 打印 try/except」——**只**保证「打印失败也不改退出码、不丢 JSON」。
  因此 `analyze_…` 的 `--selftest` CLI 回归断言的是**结论/JSON 在 GBK 下不受损**，**不**断言「删掉 ① 必然失败」
  （③ 会兜住）。「入口兜底存在性」由 `verify_t17_blob_identity.py --selftest` 覆盖：该工具**没有**第三层，
  其回归含一条**旧形态突变体**（去 ① + 恢复 `U+21D2`）=> 实测 **rc=1、无 JSON、报 `UnicodeEncodeError '\u21d2'`**。
- **运行位置护栏（评审 Q-A，必须遵守）**：一键执行器 `run_t17_color_retest.sh` 由 `WT` 决定**全部写入位置**
  （evidence/tmp/脚本/ELF 路径）。护栏：**cwd 必须与 WT 指向同一目录**，否则 **exit 2 且不创建任何文件**
  （`T17_GUARD_CWD_MISMATCH=1`）。因此：
  - **须在 dbdf 内运行**：`cd D:/codex-worktrees/dbdf && bash scripts/stage3_t17/run_t17_color_retest.sh …`；
  - 在克隆/别处运行须**显式** `--wt <该工作树>` 或 `T17_WT=<该工作树>`（cwd 也要在该工作树内）；
  - 旧文「可在克隆内跑」的说法**作废**（会让 `WT` 仍指向 dbdf 而静默写坏 dbdf 证据）。
- **纯克隆的已知依赖**：`preflight` 会校验 7 件**未入库**的 `tmp/**` 冻结产物（基线 bit/XSA、三支 ELF、部署 bit/XSA）。
  在一个全新的纯克隆里它们不存在 => `preflight` 返回 **1**（失败项是「缺产物」，**不是** HEAD 判据问题）；
  若只关心 HEAD 判据，用 `--baseline-commit` 复跑并阅读 `checks.artifacts` 逐项结论。

| 工具 | 作用 | 是否碰硬件 |
|---|---|---|
| `run_t17_color_retest.sh` | 一键执行器：`preflight`/`judge`/`link`/`baseline`/`bars`/`all` | `preflight`/`judge` 离线；其余需放行 |
| `analyze_t17_bit_integrity.py` | 位完整性/真彩（机器部分）判定器，含 `--selftest` | 否 |
| `check_t17_preflight.py` | 离线前置：分支/HEAD/锁/重型进程 + 冻结产物实算哈希 + 硬件门禁 | 否 |
| `jtag_t17_link_check.tcl` | 只读 JTAG 链路确认（用 `llength [targets]`/`jtag targets` 判定） | 是（只读） |
| `jtag_t17_dump_rows.tcl` | 安全转储 halt→mrd→con；**base/stride 必须显式传入** | 是（只读） |
| `make_t17_manifest.py` | 实测后打 manifest + hashes（退出码只接受真实值） | 否 |
| `verify_t17_blob_identity.py` | 自证：逐文件比较提交 blob 字节与工作区字节（并统计 CRLF） | 否 |

## 常用命令

```bash
# 离线（随时可跑，不动板）；**执行器必须先 cd 到工作树**（评审 Q-A 护栏，否则 exit 2）
cd D:/codex-worktrees/dbdf
bash scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id t17_color_retest_20261023_r01
python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --selftest
python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --frame <frame_full.bin>
python -B scripts/stage3_t17/verify_t17_blob_identity.py --selftest   # 自证工具的 CLI 回归（含旧形态突变对照）

# 到货后（需 Wong 开工信号 + 硬件窗口书面确认，并先填 report/evidence/S3-T17/hw_authorization.json）
bash scripts/stage3_t17/run_t17_color_retest.sh all --run-id t17_color_retest_20261023_r01 --allow-hardware

# 在克隆内运行（cwd 与 --wt 都必须指向该克隆）
cd <克隆目录> && bash <克隆目录>/scripts/stage3_t17/run_t17_color_retest.sh preflight --wt <克隆目录>
```

## 硬件安全规则（已内建）

1. `link`/`baseline`/`bars` 需要同时满足：显式 `--allow-hardware` **且** `report/evidence/S3-T17/hw_authorization.json`
   的 `wong_go`、`codex_hw_release` 均为 true；否则**退出 3 且不动板**（离线实测已验证）。
2. 只做易失 JTAG（下载 bit/ELF、halt→mrd→con 只读、写 0x503D 彩条并恢复）；**不烧 QSPI、不改接线**。
3. 自起的 `hw_server` 用完即终止；运行前**已存在**的他人会话一律不终止（只记录）。
4. 转储前必须从运行期回读 `ADDR_S2MM`/`STRIDE_S2MM`；**禁止**使用脚本内建旧地址（本目录的 TCL 不提供默认值）。
5. 每个 RunId 一次；证据目录与输出目录**拒绝已存在**，不覆盖旧轮次。
6. 一次只跑一个重型任务；`preflight` 会先查重型进程与 `index.lock`。

## 判定器退出码（与旧脚本语义相反，报告须注明所用脚本）

| 码 | 含义 |
|---|---|
| 0 | `BIT_INTEGRITY_PASS`（C1–C7 全通过） |
| 1 | `DEFECT_REPRODUCED`（复现「两字节 MSB 同时丢失」旧签名） |
| 2 | `USAGE_OR_INPUT_ERROR`（缺文件/长度非法/彩条段不足） |
| 3 | `INCONCLUSIVE_ATYPICAL`（非典型，需人工判读，不得当通过） |

旧 `scripts/stage3_t05/analyze_missing_msb_signature.py`：`0=符合旧缺位签名`、`1=不符合` => **不可混用**。

C7 口径（评审 B-1/B-2）：**16 字段位**（R5+G6+B5）+ **8 结构性恒 0 低位**（R/B 各 3、G 2）；黑条字段值 ≤ 容差
（R/B:1、G:2）不计不可辨，与 C5 对齐 => 缺陷 `14/16`、修好 `16/16`（严格口径 `13/16` / `15/16`，仅
`--strict-black-bits` 对照用）。

## 执行器 `run_t17_color_retest.sh` 退出码（评审 N-5 补齐）

| 码 | 含义 |
|---|---|
| 0 | 该阶段成功（含 `preflight` 的 `OFFLINE_GO`） |
| 1 | `all` 的 preflight 失败（`T17_ABORT=PREFLIGHT_FAILED`） |
| 2 | 用法错误 / `judge` 判定器用法错误（3 亦可出现，见判定器） |
| 3 | 硬件门禁未放行（`T17_HW_BLOCKED=...`）或目录已存在（`T17_REFUSE=EXISTS`） |
| 4 | **`extract_addr_stride` 取不到 `ADDR_S2MM`/`STRIDE_S2MM`**（`T17_ADDR_STRIDE_MISSING=1`）—— 禁止用旧地址转储 |
| 判定器原码 | `judge` 阶段会把判定器的 0/1/2/3 原样传播 |