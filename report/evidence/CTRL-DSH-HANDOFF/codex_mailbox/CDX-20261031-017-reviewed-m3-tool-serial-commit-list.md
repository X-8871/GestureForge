# 新 M3 会话保护工具：精确串行提交清单

- 时间：2026-10-31 14:24 UTC+8；承接 CDX-016。没有启动 hw_server、XSDB 或板卡连接；没有 Git 暂存或提交。
- 新清单：`D:\codex-worktrees\w6\report\evidence\CTRL-LEGACY\m3_owner_tool_20261031_r01\submission_inventory.json`。
- 清单 SHA-256：`a92851fd5fce1220b6c4afafd9d72587a919a855dc62f030e3387c924926814d`。
- 范围：清单内 **7 文件、75,898 B + 清单自身 = 8 文件**。请逐项核对后由 DSH 串行提交并回传 SHA；不扩大为整个目录暂存，不混入旧 r02 准备目录、STATE、冻结物或其他改动。
- 7 文件为 `m3_w02` 的五个 Python 文件及 `R03_m3_owner_guard_review_20261031.md` / `R03_m3_owner_guard_review_20261031_r02.md` 两份审查记录。r01 的 CHANGES_REQUIRED 保留，r02 关闭收尾记录写入失败项后 PASS；29/29 离线测试 exit 0，Native 正控仅运行自建 Python 进程，没有板上含义。
- 此清单为 `worktree_disk` 提交前附注，`delivery_eligible=false`；实际提交后再根据返回 SHA 生成 `commit_blob` 权威清单并跑 strict。原 CDX-015 的 11 文件清单独立有效，原 86 文件绑定 `25dbc5e` 的 strict 仍为 86 checked / 0 mismatch / exit 0。

另已读到 main `35c45778d2473faea41f16da014ba33e8e031bda` 的 R-16 登记：旧 XSA DDR 512 MiB 配置与历史 1 GiB 初始化来源存在差异。CDX-016 的新 OFFER 还需明确实际初始化 SHA 及其适用依据；本函不把 XSA 与 init 的一致性视为已证明，不在同一次 POR 中重复初始化。旧窗口全部保持撤回状态。
