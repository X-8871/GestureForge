# 旧审查克隆清理与恢复

本次只清理下表五套独立临时克隆。父目录的原始审查报告、脚本、失败日志继续保留；含独有提交的 FINAL_A/envC 未列入删除范围。正式工作树、原始验收证据、模型数据和部署产物未列入删除范围。

| ZIP 前缀 | 原目录（相对 D:\FPGA_Competition\tmp\review） | 恢复提交 |
|---|---|---|
| 0/ | FINAL_A_20261023_r01/envA | f3c537d1b37646ec779e3eb6fecdc4330bb1d7e3 |
| 1/ | S5_T24_r03_20261024_r01/w5clone | 93493f814a8198971ad96d910388409b5461806d |
| 2/ | S5_T24_r03_20261024_r01/w5mut | 93493f814a8198971ad96d910388409b5461806d |
| 3/ | S5_T22_r02_20261024_r01/clone_w5 | a60d73b62f20fb5e849a2099523f283c0d7b2ad9 |
| 4/ | S6_T23_20261024_r01/w6clone | 93e0a82fac949efd9f5c5e069ab1bde37ac44357 |

## 已执行的保全核验

- 五套克隆的 HEAD、所有命名引用及 reflog 引用对象均存在于主仓库，引用的对象闭包无缺失。
- 克隆没有未提交的 tracked 差异；逐个工作文件计算原始 Git blob SHA-1 和 SHA-256。原始字节等于 HEAD blob 的文件可由主仓库恢复；换行变体、独有输出及其他不相等文件全部进入 ZIP。
- Git 配置、索引、引用与日志等元数据进入 ZIP；Git objects 缓存由主仓库对象恢复。
- ZIP 已执行 CRC 检查，并对全部归档条目逐项校验 SHA-256。各文件清单与归档总 SHA-256 见 plan.json。
- 准备结束重新核对工作文件大小、mtime 和 HEAD；删除前再次核对精确路径、进程引用、锁与归档哈希。

## 恢复步骤

1. 从 plan.json 找到目标的精确路径和 head；确认目标路径不存在，不覆盖已有目录。
2. 执行 git clone --no-hardlinks --no-checkout D:\FPGA_Competition <目标绝对路径>。
3. 执行 git -C <目标绝对路径> -c core.autocrlf=false checkout --detach <head>，恢复提交原始字节。
4. 核对 unique_files_and_git_metadata.zip 的 SHA-256 与 plan.json 一致；从 ZIP 中提取对应编号前缀下的内容，移除编号前缀后覆盖到刚创建的目标根目录，恢复原始换行变体、独有文件与 Git 元数据。不得提取到原始工程工作树。
5. 按 clone_N_files.jsonl 核对恢复文件 SHA-256。清单中的 git_blob 表示源对象；recovery=zip 表示原始字节已归档。Git objects 目录不要求逐文件复现，只要求已验证引用的 Git 对象可读。

本包是清理审计与恢复依据，不构成阶段验收结论。实际删除结果和空间变化见 after.json 与 deletion_receipts.jsonl。
