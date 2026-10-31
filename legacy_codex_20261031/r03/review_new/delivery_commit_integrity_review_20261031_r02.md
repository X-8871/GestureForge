# 交付提交与哈希闭环独立复审（r02）

## 结论

**PASS（生成器输出路径防护代码审查）**。此前发现的 dangling symlink 绕过已由显式符号链接检查和独占创建封闭。正常创建及拒绝已有文件的定向测试通过。悬空符号链接场景因本机无创建 symlink 权限而未实测；代码路径已静态核对，不声称该场景动态测试通过。

本轮只复审生成器，不重复 r01 已完成的 86 项 blob 核对，不重跑 strict；依据总控说明，本轮未改动原 manifest、strict 证据或 86 项提交。业务和板级验收状态不在本轮复审范围。

## 源码核查

- 当前生成器文件：`legacy_codex_20261031/build_commit_manifest.py`。
- 当前工作区文件字节 SHA-256：`6c632f7004c7e67ab819c69e853b84e098dc31510ade5eb66c5e13fb4128f88d`。这是工作区文件哈希；该路径当前不在 HEAD 中，因此此 SHA 不是提交 blob SHA。
- 输出检查先确认父目录解析后位于 `report/evidence/CTRL-LEGACY` 内，再检查 `output.is_symlink()` 和 `output.exists()`；输出使用 `output.open("x", encoding="utf-8", newline="\n")`。显式符号链接检查覆盖 dangling link；独占创建拒绝已经存在的目录项，并避免检查与创建之间被替换后覆盖/跟随链接。
- 与 r01 的问题对应关系：最终文件不再仅依靠 `exists()`；现在是链接拒绝、既有目标拒绝和独占创建三道约束。此次未发现新的输出路径越界条件。

## 定向探测

- 通过实际生成器入口运行隔离探测，Git helper 使用两条 dummy blob 映射，未扫描原始 85 项或重新计算 86 项。
- 唯一临时目录：`report/evidence/CTRL-LEGACY/integrity_probe_r02_db59f8c223e64bfaa4bb9375853809f4/`。正常创建通过；对同一路径重跑时拒绝已有文件，且原文件字节保持不变；探测目录及文件已逐项清理。
- dangling symlink：**NOT_TESTED**。`os.symlink` 返回 Windows 错误 1314（当前进程无创建符号链接的权限）。外部目标在测试前后均不存在；未绕过权限限制。

## 范围与限制

- 复审依据：r01 报告中的提交/哈希闭环结果、当前生成器源码、上述隔离定向探测。r01 记录的 source commit 为 `25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3`；86 项结果本轮未重新验证。
- 没有运行 strict、硬件、Vivado 或其他厂商工具；没有修改生成器、原始 evidence/RunId、原 strict 文件或 86 项提交内容，也没有暂存或提交。
- 本报告仅对当前生成器路径防护给出 PASS；生成器尚未进入 HEAD 的事实仍需总控按项目提交流程处理。此前记录的 M3 未采样、C2 板测未跑及 C4 `CHANGES_REQUIRED` 不受本结论影响。

## 前轮报告

- r01：`legacy_codex_20261031/r03/review_new/delivery_commit_integrity_review_20261031.md`。