# 交付提交与哈希闭环独立审查

## 结论

**CHANGES_REQUIRED（仅针对清单生成器的输出路径防护）**。本次 86 项交付与 `25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3` 的提交 blob、范围和 strict 哈希结果一致；但生成器对最终输出文件名未做符号链接拒绝，存在可复现的目录边界绕过条件。此次实际 `delivery_manifest.json` 是授权目录内的普通文件，未观察到本次运行发生越界写入。

## 核验结果

- 原始 `submission_inventory.json` 有 85 个唯一文件条目。manifest 的 86 项恰为这 85 项加清单自身 `report/evidence/CTRL-LEGACY/residuals_20261031_r01/submission_inventory.json`，没有额外或缺失路径。
- `25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3` 的提交变更路径共 86 项，与 manifest 文件路径集合完全相同；逐项计算 85 个原始条目的 Git blob SHA-256 与长度，全部匹配原待提交清单。清单自身磁盘字节与提交中对应 blob 也一致（17,032 字节，SHA-256 `6e761828ff2c1b38e24f48ed44c41e3ba0fa3031e749451c78a0f1e604a2fa8e`）。
- 独立对 86 个 manifest 条目执行 `git cat-file blob <commit>:<path>` 并重算 SHA-256/长度，86/86 一致。每项及 manifest 级 `hash_basis` 均为 `commit_blob`，`source_commit` 与 `hash_basis_commit` 均为指定完整提交号。原清单注明其哈希是工作区字节；生成器先以提交 blob 重算并与该清单核对，再把 blob 哈希写入 manifest，没有把磁盘哈希伪装成提交 blob 哈希。
- 原始 strict 记录：`strict_execution.json` 为 exit 0；`strict_stdout.json` 为 `mode=strict`、86 checked、0 mismatch、0 skipped、`verdict=OK`；`strict_stderr.txt` 为 0 字节。按原记录的唯一 manifest 路径只读复跑一次，结果仍为 86 checked、0 mismatch、`OK`、exit 0。命令未显式传 `--commit`，校验器从 manifest 的 `hash_basis_commit` 解析提交；该提交与核验的 source commit 一致。
- 提交清单仅落在允许前缀 `legacy_codex_20261031`、`report/evidence/R03-M3`、`report/evidence/CTRL-LEGACY`。变更路径集合中没有 `.codex/STATE.md`、`docs/stage6/` 两份规格或其他旧证据目录；14 个旧目录、其他工作树业务文件、编译缓存均未混入。提交路径集合与清单精确相等，不依赖当前工作区状态推断。

## 需修复项

- `legacy_codex_20261031/build_commit_manifest.py:44-47,53` 将输出父目录 `resolve(strict=True)` 后检查边界，但只用 `output.exists()` 检查最终文件。对一个指向授权目录外、目标尚不存在的 dangling symlink，`exists()` 返回 false；随后 `write_text()` 会跟随该链接并在外部目标创建文件，绕过父目录边界检查。
- 关闭条件：创建输出时拒绝符号链接并采用原子独占、禁止跟随链接的创建方式（例如 `O_CREAT|O_EXCL|O_NOFOLLOW`，或经验证等价方案）；在隔离目录做越界链接拒绝验证后，再重建 manifest 并重跑 strict。此次报告仅记录问题，没有改动生成器。

## 业务状态与范围

- 这是遗留诊断和实现索引的身份绑定核验。strict 只证明固定提交的文件身份与哈希一致，不代表业务验收或板级验收。
- manifest 与 `validation_summary.json` 保留限制：M3 成对采样 `NOT_RUN`；C2 `board=NOT_RUN`；C4 状态为 `FAIL`、审查为 `CHANGES_REQUIRED`。这些状态不被 strict 的 `OK` 覆盖。
- 未运行硬件、Vivado 或其他厂商工具。Git Bash 启动因 `E_ACCESSDENIED` 失败，按项目规则使用 PowerShell 与本机 Python 做文件核验；没有修改被审文件或原 RunId，也没有暂存或提交。

## 审查基线

- source commit：`25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3`。
- 证据目录：`report/evidence/CTRL-LEGACY/residuals_20261031_r01/`。
- 复核范围：原始提交清单、commit blob、manifest、strict 原始 stdout/stderr/execution、生成器与相关限制摘要。