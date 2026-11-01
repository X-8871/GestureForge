# 恢复受托任务：确认027撤窗、交付收尾清单重发

- Wong已在本chat明确“继续”。当前实际时钟约2026-10-31 13:51 UTC+8；我方已读023/025/026/027及当前STATE，确认027撤回凌晨M3 OFFER并收回板卡。**不沿用过期窗口，不启动hw_server/xsdb，不干扰R-07/后继DSH会话**。
- 凌晨曾因自动审批服务用量上限而中断，一笔端口绑定补丁当时未执行；现服务恢复，已沿相同审批通道继续，不绕过审批。正在修完端口一致性、监听PID属于本轮Job、client在Job结束/端口换owner时拒绝等离线工具问题；未通过独立复审前不申请立即开窗。
- 新M3执行必须按027使用**新OFFER＋新RunId**，不复用未执行的 `m3_pair_20261031_r02` 窗口。工具就绪后另发包含新RunId、固定bit/XSA/app完整SHA、预计≤9分钟的窗口申请；本任务仍保持init=0、reset=0，当前STATE相机流程的放宽不自动套用本M3委托。

## 可先完成的串行提交（无须板卡）

- 已核验源提交 `25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3`（008原86文件），权威清单 `residuals_20261031_r01/delivery_manifest.json` 的**86项Git blob全部一致，strict exit0/0不符**；独立核对数据闭环PASS，未冒充业务或板级PASS。
- 生成器已修复输出链接/覆盖防护，现SHA `6c632f7004c7e67ab819c69e853b84e098dc31510ade5eb66c5e13fb4128f88d`，独立r02复审PASS。正常新建/拒绝已有文件已测试；悬空symlink动态场景因Windows1314未能实测，报告如实保留限制。
- **请按新的精确收尾清单核验并提交**：
  `D:\codex-worktrees\w6\report\evidence\CTRL-LEGACY\closeout_20261031_r01\submission_inventory.json`
  SHA **`1b8136084b70ec5270007c38f15be9ed3f8ba9754278e465781fdd29905b8554`**。
- 清单列**10文件、68752B**，加清单自身＝**11文件**。包括最终M4B诊断复审、修复后的生成器、86项权威manifest/strict原始输出、C4 rev4增量报告、生成器两轮审查。**不包含正在修复的m3_w02、新r02草稿、旧STATE/两份S6A/14旧RunId或其他树**。
- 原 `submission_inventory_final.json` 仅保留为历史提交前快照；其中生成器旧SHA已过期，**不得作为当前输入校验清单**，本次以closeout清单为准。013/014旧哈希的待提交声明被此清单取代，不静默改旧记录。
- 请回传该11文件的串行提交SHA。我方继续按Wong选择不操作main/w6 index/commit、不push。

## C4状态

rev4增量复审仍CHANGES_REQUIRED（报告SHA `e36a4e092ddcf8b163b8e615e5f9394bcb2d2c38102bc6184e64c796e78effcd`）。它固定0ccbe01/w4 07efa67时点；026的新POR后r05结果是后继证据，不能反写旧报告。下一轮将只按补齐的实际源码/ELF/manifest及计时定义关闭条件做限定增量核验，不因状态声明或正向样本自动宣布原子性全部通过。
