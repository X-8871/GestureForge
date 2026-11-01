# GestureForge

基于 Zynq-7000 / AX7020 的五类带框手势检测工程，使用 YOLOv4-tiny、INT8 推理、相机采集与 HDMI 显示。手势类别固定为 `fist`、`palm`、`one`、`two_up`、`three`；无手画面作为负样本，不是第六类。

**项目已暂停（2026-11-01，UTC+8）。** Wong 已退出本次竞赛，本仓库用于保存已有成果和以后恢复开发。当前没有完成相机到推理再到带框显示的整链验收，封存不代表竞赛完成或板级通过。

## 从哪里开始

- [恢复说明 RESUME.md](RESUME.md)：克隆、校验、选择阶段版本、工具与本地依赖。
- [当前状态](.codex/STATE.md)：暂停状态、管理权、证据入口和限制。
- [工程规则](AGENTS.md)：文件归属、独立审查、Git、资源和硬件授权规则。
- [正式需求与设计](docs/obsidian-project/02-方案设计/)及[阶段验收材料](docs/obsidian-project/04-提交材料/阶段验收/)：需求、接口与历史验收依据。

## 已保存的内容

2026-11-01 已上传 **18 个分支、19 个标签**，保留原历史与冻结标签，没有强推。独立从 GitHub 克隆后，**317 项归档文件、31,632 项工作树快照文件**的提交长度及 SHA-256 校验通过。该检查确认文件身份，不代表完整重建、推理正确或板卡运行成功。

- `main` 保存工程历史、恢复入口和[归档材料](archive/project-paused-20261101/)。
- `codex/archive/20261101/*` 保存各工作树筛选后的未提交源码、文档与小型证据；这些版本没有重新做业务验收。快照是原阶段 HEAD 的独立后继提交，不合并进正式阶段分支。
- 归档材料保存独有的相机、预处理、显示、推理源码，以及选定模型、bit/XSA/ELF、初始化件、原路径和哈希绑定。
- [工作树与提交映射](archive/project-paused-20261101/worktrees.json)、[归档清单](archive/project-paused-20261101/manifest.json)及[上传成功回执](report/evidence/CTRL-ARCHIVE/github_archive_20261101_r02/receipt.json)用于精确选择恢复版本。

### 恢复依赖补充审计

后续按冻结记录核对发现，首包未收齐部分历史部署件。[补包](archive/project-paused-20261101-supplement/)另保存125项文件：14件找到精确身份的模型/部署产物、P3q的38项构建输入，以及初始化、应用源码、构建和绑定记录。原317项首包保持不变，补包使用[独立清单](archive/project-paused-20261101-supplement/manifest.json)。

补齐内容包括正式tiny416配置及`6000.weights`、2B R04的bit/XSA/ELF/初始化与恢复包、阶段3基线bit/XSA及v10/v12 ELF、阶段5/6共用的P3q bit/XSA。找到与复制这些文件不表示重新编译或上板通过。

**仍有遗缺：阶段5的3个、阶段6的8个冻结ELF未找到对应的完整SHA-256；阶段5冻结清单中的两个主C/H源码身份也未匹配。** 当前同名文件存在版本漂移，不能当作原冻结件。阶段6部分源码记录仅提供8位哈希前缀，也不足以证明精确冻结身份。逐项结果、搜索范围、原路径和已知版本见[遗缺审计](archive/project-paused-20261101-supplement/gap_audit.json)。这些缺口保留为开放项；不能宣称所有历史冻结包均可完整恢复。

| 工作树用途 | 原阶段分支 | 封存快照分支 |
|---|---|---|
| 主工作树 | `main` | `codex/archive/20261101/main` |
| 阶段2B | `codex/stage2b-dma-g0` | `codex/archive/20261101/w2b` |
| 阶段2B审计 | `codex/stage2b-t01-board-audit` | `codex/archive/20261101/96a3` |
| 吞吐候选 | `codex/stage2c-throughput` | `codex/archive/20261101/w2c` |
| 阶段3 | `codex/stage3-video` | `codex/archive/20261101/dbdf` |
| 阶段4 | `stage4-infer-prep` | `codex/archive/20261101/w4` |
| 阶段5 | `stage5-display-prep` | `codex/archive/20261101/w5` |
| 阶段6 | `stage6-interact-prep` | `codex/archive/20261101/w6` |
| 阶段7 | `codex/stage7-system-acceptance` | `codex/archive/20261101/stage7` |

## 快速恢复

安装 Git 与 Python 3，在新目录执行：

```bash
git clone https://github.com/X-8871/GestureForge.git
cd GestureForge
python -B -X utf8 verification/verify_archive_20261101.py --repo .
python -B -X utf8 verification/check_manifest_hash_basis.py --repo . --paths archive/project-paused-20261101-supplement/manifest.json --mode strict --json
```

第一项预期返回 `ARCHIVE_FILES_OK`，核验317项首包文件；第二项核验125项补包文件，要求无哈希不一致。先在 `main` 完成这两步，再按恢复说明创建隔离的阶段工作树，例如：

```bash
git worktree add --detach ../GestureForge-w4 origin/codex/archive/20261101/w4
```

目标目录必须尚不存在。旧 Tcl/XPR 可能包含 `D:/tmp/lead/...` 等原机绝对路径，需依据归档中的 `original` 路径和依赖清单恢复；不能假设克隆后即可直接重建。Vivado/Vitis、BSP、驱动和许可证需另外准备。上板需要重新核对实物、部署版本及独立授权。

## 暂停时的技术边界

最后核对的整链实验为 `mvp_chain_20261101_r14`（2026-11-01 07:25–07:28，UTC+8）：GPIO bit-bang 读到 OV5640 ID `0x5640`，相机初始化成功，显示约60 fps；采集 VDMA `SR=0x14810`，推理 `raw_nz=0`，无有效检测框，结论为 **`MVP_CHAIN_PARTIAL`**。

有效图像写入 DDR 并由推理正确消费仍未闭合。历史标签、单模块验收和旧报告中的“根因已定”不等于当前整链成功；恢复时以具体 RunId、源码身份和实际证据核对。

## 未上传与清理边界

GitHub **不是原机完整备份**。完整训练图片、校准与冻结测试的原始图片、真实相机帧、部分大型原始证据、工具链及本机配置没有全部包含在上传范围内。各树清单中的 `omitted` 表示未选择上传，不表示可以删除。

经Wong明确批准，2026-11-01已删除六类公共库中158,089张原图（含公共train/val/test），文件逻辑长度约202.9 GiB。保留原位614张唯一图片，覆盖512张校准输入和109项冻结测试中的105张真实图片（其中3张与校准集重合）；另4项是合成测试。保留图片、对应标签及副本均完成删除后哈希复核，详见[图片清理回执](report/evidence/CTRL-ARCHIVE/public_images_20261101_r01/receipt.json)。以后完整训练或全量数据集评估需要重新下载图片。

109组输入张量/CPU黄金结果、614张图片及标签仍在原位；其他独有运行材料、模型及大型原始证据按清单留在仓库或私有恢复档案。标签、标注、划分清单、来源许可、自采数据、厂商原件和工具链不作垃圾删除。`omitted`不能用作批量删除依据。

首批将 `D:\FPGA_Competition\tmp\review` 的110,300个文件完整保全、逐项验证后移除副本。本地首批恢复档案位于 `D:\GestureForge_Archive\2026-11-01\preserved_local`，约13.56 GiB，含审查树ZIP、614张图及标签副本、删除日志和索引；旧回执中的C盘路径按 `local_archive_index.json` 映射。

随后按 Wong「继续进行全部清理」完成26项范围和20个原所有者测试临时目录的清理：八棵辅助工作树、主树可迁出的生成物、训练运行目录及项目测试缓存已在完整归档核验后移除。当前只保留主工作树，18个本地分支、19个标签及原16项业务差异保留。主树仍有有意保留的未跟踪源码、历史信箱和109组黄金，不使用 `git clean` 清空。

第二批私有恢复档案为 `D:\GestureForge_Archive\2026-11-01\cleanup_complete_r02`，使用SHA-256去重压缩及Git blob引用，依赖同级 `git\GestureForge_after_cleanup_20261101.bundle`。26项共645,593个捕获文件已经逐项核验；另62个受权限限制的缓存文件及20目录24,673个文件分别ZIP保全核验。阶段7、阶段6的实际恢复测试通过，Git状态和暂存/未暂存差异与捕获记录一致。恢复工具及命令见 [RESUME.md](RESUME.md)，最终记录见[完整清理汇总](report/evidence/CTRL-ARCHIVE/cleanup_complete_20261101_r02/summary.json)。

这些私有档案不在GitHub内，必须继续保留；同盘档案不是异机备份。六处旧工具会话配置原位保留，未读取秘密内容；共享安装包及无关软件缓存不在本项目清理范围。历史13项精确身份遗缺仍开放；109组自包含张量/黄金核验通过，但其中104条旧 `input.source` 图片绑定使用了张量身份，恢复时须另行纠正，不能按该字段直接验证原图。

末尾又完成 `D:\tmp\review` 的59,983文件完整归档与清理，以及本轮23个C盘恢复测试目录的48,299文件清理；两个删除器均退出0。后续清理区间D盘现场净增约84.8 GiB、末尾可用约247.7 GiB，包含本轮归档成本和背景写入影响，不与首批采样直接相加。机器可读的时间、字节数、范围、保留项和恢复限制均在上述完整清理汇总中。

## 目录索引

| 路径 | 内容 |
|---|---|
| `src/`、`board/`、`vitis/` | RTL、板级与 PS 软件输入 |
| `vivado/`、`build/` | Vivado 工程与历史构建入口，生成物是否保留以清单为准 |
| `scripts/`、`verification/`、`sim/` | 重建、转换、检查与仿真程序 |
| `docs/`、`report/` | 正式设计、验收记录、原始证据和索引 |
| `archive/project-paused-20261101/` | 经筛选的离线恢复材料与工作树映射 |
| `data/`、`skill/`、`web/` | 数据说明、可复用技能与相关页面材料 |

`docs/obsidian-project/` 是指定项目笔记的历史快照；旧总控提示词和协作流程不覆盖当前 `AGENTS.md` 与 STATE。知识库原件不在清理范围内。仓库同步细节见[仓库同步说明](docs/仓库同步说明.md)。
