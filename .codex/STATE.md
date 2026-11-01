# 项目状态入口

更新：2026-11-02（UTC+8）。当前目标：暂停封存与获准清理，不恢复开发、训练、综合或板级操作。

## 当前管理与边界

- Wong已退出本次竞赛，保留以后继续项目的可能。Codex为唯一项目最高总控；DSH最高管理权已按2026-11-01用户直接指令撤销，旧归属/租约仅为历史。
- 根AGENTS.md继续约束单写者、证据、串行提交与硬件授权；整理清理不提高G0–G5结论。
- GitHub：`https://github.com/X-8871/GestureForge`。恢复先读 `RESUME.md`，只在新目录试验。

## 保存与清理结果

- 18分支/19标签保留，317项首包及125项补包已上传核验。历史回执：`report/evidence/CTRL-ARCHIVE/github_archive_20261101_r02/receipt.json`。
- 首包 `archive/project-paused-20261101/`，补包 `archive/project-paused-20261101-supplement/`，快照 `codex/archive/20261101/*` 不冒充独立审查或阶段验收通过。
- 按明确批准已删除公共六类train/val/test原图158089张/217878893516字节，失败0；614张唯一校准/冻结测试图及标签原位保留。全量训练/评估需重新下载图片。
- 109组完整输入/CPU黄金原位：`archive/S2A-T68/repair109_20261003_194620/fixtures`。标注、划分、许可、自采资料按保留清单处理。
- 首批tmp/review的110300文件保全核验后移除；私有包 `D:\GestureForge_Archive\2026-11-01\preserved_local`，约13.56GiB，旧C路径按 `local_archive_index.json` 映射。
- 后续26项范围645593个捕获文件已完整核验后清理：八棵辅助工作树、主树可迁生成物、训练运行目录、项目测试缓存；Git当前仅登记主树 `D:\FPGA_Competition`，阶段分支及标签仍在。
- 另62个受限缓存文件、20个原所有者测试目录24673个文件分别ZIP保全核验后移除，未修改ACL或他方权限。
- 主树原16项业务差异保持；有意保留的未跟踪源码、历史信箱与黄金数据不作全量暂存、reset或git clean。
- 完整私有包：`D:\GestureForge_Archive\2026-11-01\cleanup_complete_r02`，依赖同级 `git\GestureForge_after_cleanup_20261101.bundle`；215383个唯一内容对象核验通过，阶段7/6实际恢复及Git状态/暂存/未暂存差异对照通过。
- 最终清理索引和卷空间口径：`report/evidence/CTRL-ARCHIVE/cleanup_complete_20261101_r02/summary.json`；原始执行、失败及修正记录留在私有包，不覆盖旧回执。
- 补充 `D:\tmp\review` 的59983文件/7367383318字节及C盘23个测试目录48299文件/2275241965字节均完整归档后清理成功，两个删除器退出0；旧ZIP重复以可逆前缀+tail保全后移除。
- 后续清理区间D盘净增约84.8GiB，末尾采样可用约247.7GiB，详细时间与背景写入口径见最终summary；原16项业务差异仍逐字节一致。
- 六处旧工具会话配置、共享安装包、厂商原件 `D:\FPGA\AX7Z020`、工具链和Vault保留。私有包不在GitHub，同盘保存不是异机备份。

## 恢复限制与技术事实

- 11个阶段5/6 ELF及阶段5两份C/H精确冻结身份仍缺，见补包 `gap_audit.json`；同名漂移件不能替代，不宣称历史冻结包全恢复。
- 109组张量/黄金自身校验通过；104条旧 `input.source` 图片绑定使用张量身份，属现有元数据问题，未修改冻结清单，不按该字段验证或重建原图。
- `scripts/restore_cleanup_archive.py` 按scope恢复，默认跳过嵌套Git元数据。partial clone缺失历史、未初始化gitlink和路径边界限制见RESUME。
- 最后已核对整链：`mvp_chain_20261101_r14`，2026-11-01 07:25–07:28 UTC+8；OV5640 ID `0x5640`、初始化成功、显示约60fps，但VDMA `SR=0x14810`、推理 `raw_nz=0`、无有效框，`MVP_CHAIN_PARTIAL`。
- 技术卡点仍是有效图像写入DDR并由推理正确消费。历史单模块冻结与旧根因描述不能替代当前整链证据，未审补丁不得部署。
- 各阶段历史冻结、未闭合项及未执行验收按封存快照STATE和RunId复核，本轮不做技术验收。
- 旧完整主STATE保留在Git历史main `b553968666967eac986cdff60b69759cd5afb2dd`；当前入口替代其中旧活动状态与路径存在性描述。

## 下一步

- 完成当前整理收尾及远端/离线保存，新的技术任务由Wong决定。
- 以后恢复先核验首包、补包和私有scope，重建工具环境并明确版本组合；板级操作另须独立窗口授权与现场资源检查。
