# GestureForge 恢复入口

更新：2026-11-01（UTC+8）。Wong 已决定退出本次竞赛并暂停项目；本入口用于以后恢复开发，不启动当前技术工作。

## 本轮已封存并上传的内容

上传现状（2026-11-01 13:52，UTC+8）：**18个分支、19个标签已上传，远端SHA与本地一致**。从 GitHub 独立网络克隆后，317项归档文件与九树31632项快照文件的提交内容身份全部通过核验，被测main为 `653d94f1830528d13c35bd5729d818e379fb5b8b`。成功回执见 `report/evidence/CTRL-ARCHIVE/github_archive_20261101_r02/receipt.json`；此前网络失败的r01回执保留历史，不再代表当前上传状态。此核验不包括编译、训练集恢复或板级运行。

- `main` 与各阶段原分支、原标签：保留已有提交历史，冻结标签不改动。
- `codex/archive/20261101/main|stage7|96a3|dbdf|w4|w5|w6|w2b|w2c`：各本地工作树的未提交工程文件与筛选后的文档/小型证据快照。原工作区、索引和原作者归属保留；快照不冒充代码审查或阶段验收通过。
- `archive/project-paused-20261101/`：从本地 ignored/外部目录保全的模型、相机/显示/推理源码和部署件、路径/哈希清单，以及各树上传/留存本地项目清单。

2026-11-01后续核对发现首包遗漏部分冻结部署件，新增 `archive/project-paused-20261101-supplement/`，125项文件独立清单，包含14件精确模型/部署产物与来源/初始化/源码记录。阶段5/6仍缺11个冻结ELF，阶段5仍缺两个主C/H源码的精确哈希；当前同名版本不能替代。细节见补包 `gap_audit.json`，不能宣称所有历史冻结包均可完整恢复。

Wong随后明确批准六类公共train/val/test原图清理：已删除158089张、217878893516字节，失败0；614张唯一校准/冻结测试图及标签在原位保留，另有本地副本，原件与副本均完成末尾哈希复核。`report/evidence/CTRL-ARCHIVE/public_images_20261101_r01/receipt.json`保存执行事实。正式工作树与主目录原始证据尚未移除。各树历史清单中的omitted描述上传时点，不能作为当前文件存在性或删除授权；以后按具体清理回执和归档映射核对。

首批清理已另将 `D:\FPGA_Competition\tmp\review` 全树110300文件归档核验后移除副本。正式私有恢复档案为 `D:\GestureForge_Archive\2026-11-01\preserved_local`（约13.56 GiB）：`review_directory_complete.zip`和逐文件清单、`dataset_recovery`的图片/标签备份与清理日志、`local_archive_index.json`。旧清单的C盘前缀已转存，按索引的 `relocation_rule` 映射；原清单字节保留，C盘临时副本已移除。此档案不在GitHub内，也不属于可删缓存；同盘档案不是异机备份。首批汇总见 `report/evidence/CTRL-ARCHIVE/cleanup_20261101_r01/summary.json`。

## 恢复步骤

1. 在全新目录克隆 `https://github.com/X-8871/GestureForge`，读取根 `AGENTS.md` 和本文件；也可按独立离线包回执从 `.bundle` 恢复被封存的提交。项目保持暂停，新的技术任务由 Wong 决定。
2. 先停留在 `main`，运行 `python -B -X utf8 verification/verify_archive_20261101.py --repo .` 核对317项首包；再运行 `python -B -X utf8 verification/check_manifest_hash_basis.py --repo . --paths archive/project-paused-20261101-supplement/manifest.json --mode strict --json` 核对125项补包；然后读取 `archive/project-paused-20261101/worktrees.json` 里的原 HEAD、快照提交与归属。这些验证仅确认文件身份，不代表完整构建或板级成功。
3. 按清单选择原阶段分支或对应封存快照，在独立目录恢复。例如阶段4快照使用 `git worktree add --detach ../GestureForge-w4 origin/codex/archive/20261101/w4`。归档总包和上述校验器位于 `main`，在切换前完成核验；部署件按同一版本组合恢复。
4. 外部源码包的 `original` 字段记录原路径；例如相机 Tcl 仍引用 `D:/tmp/lead/p2c_20261029_r02/src`、w2b 源码及 OV5640 IP。恢复时按清单重建原路径，或在隔离副本明确改为新路径；不能直接认为移动后的旧 Vivado XPR 可重开重建。
5. 安装/定位原工具链（Vivado/Vitis 2026.1、相关 BSP、Python、编译器和适用许可证），先做轻量离线检查，再按任务需要重建。工具链与许可证不随本仓库打包。
6. GitHub首包/补包不含完整训练数据与部分大型证据；本地已保全512张校准图及109项测试依赖（真实图片105张，另4项合成；唯一图片合计614张）。109组完整输入/CPU黄金保留在 `D:\FPGA_Competition\archive\S2A-T68\repair109_20261003_194620\fixtures`。公共全量原图已按批准清理，执行原train/valid/test清单前须重新取得数据，并核对来源、许可、划分和哈希；不将仅剩图片的子集当作原完整评估集合。
7. 上板必须重新确认当前 PCB/模组、端口、部署身份和独立窗口授权；封存提交不授权复位、编程或运行。

## 暂停时的技术事实

- J11 模组曾通过 GPIO bit-bang 读到 OV5640 ID `0x5640`；不能继续沿用早期“未插设备”的猜测。
- 最后已查到的 MVP 板测为 `mvp_chain_20261101_r14`（07:25–07:28，UTC+8）：相机初始化成功、显示约60 fps，但采集 VDMA `SR=0x14810`、推理 `raw_nz=0`、无有效检测框，结论 `MVP_CHAIN_PARTIAL`。
- 当前卡点是有效图像写入 DDR 并被推理正确消费；早期 727/720 行差异不能视为已闭合。旧 STATE 有多轮被后续证据替代的“最终根因”描述，恢复必须按实际 RunId 和原始证据核对。
- 各阶段历史 G4/G5、未执行项和范围限制不因封存变更。未审补丁、未完成构建和采集链失败均不得作为部署批准。

## 清理与安全恢复

只在独立目录恢复和试验，不覆盖当前原件。GitHub 分支上传不能代替未提交、ignored 和大型证据的完整备份。完整空间清理计划另行审核；不得因为能克隆本仓库就直接删除整台机器上的全部项目目录。
