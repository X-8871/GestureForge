# S1-T01 独立复审接力提示词（2026-09-14，修复后版本）

> 本文件包含旧固定版本的历史复核要求；文件末尾“本轮修复后权威输入”优先。开发侧不代替独立复审签结。

请在不修改共享工程实现、不代替开发签结的前提下，独立复审 `S1-T01 训练环境与数据准备` 当前交付。复审对象固定为 Git 提交 `1e0641d45c95f4ca8336ef8b191efcd3f3cf9e4d`；其中 AUD-S1-T01-004～006 的开发修复提交为 `48cbd749721917c30346dafd631a5e11941b654c`，HaGRIDv2 数据准备与证据交付提交为 `9174c465481b153872c83cf4312679438641a6ec`。工作区已有与本任务无关的改动：`docs/obsidian-project/总控.md`、`docs/obsidian-project/项目接手提示词.md`、`vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr` 以及两张板卡照片；不得把它们纳入本次审查版本。

任务规格固定为原 Vault 任务记录 `S1-T01_训练环境与数据准备.md`（本轮更新后源文件 SHA-256：`61379EDD0CC78BFCBFF6F40A85C15BB8D69E032D366A5FEE8BD697FC5C327D00`）和《B方案实施与阶段验收计划》v3.0。范围边界：五类带框检测；YOLOv4-tiny 优先作为上板候选；完整 YOLOv4 仅作 PC 对照；输入尺寸和性能尚未冻结；不把 32×32 分类规格带入本任务；本任务不包含正式长训、INT8、RTL 或板卡验收。

请按以下顺序核查：

1. 对 `AUD-S1-T01-004～006` 逐项检查代码、回归测试和修复边界：
   - 004：不能因任意同名文件、`nvidia-smi` 查询或伪造输出通过；必须要求可执行 Darknet 版本/帮助命令和明确的 `S1_T01_CUDA_SMOKE_PASS` 设备运算结果。
   - 005：清单中的图片和标签必须同 stem、标签扩展名为 `.txt`，并拒绝同一标签被多行映射；错配 stem 回归必须覆盖。
   - 006：支持的 PNG/BMP/PNM/JPEG 必须校验完整像素载荷，截断 PNM 等损坏输入不得自动通过；截断回归必须覆盖。
2. 复核 AUD-S1-T01-007 的测试计数修正，以及当前提交与证据的版本绑定。
3. 核验真实 HaGRIDv2 数据证据：
   - 数据根目录：`D:\FPGA_Data\HaGRIDv2`
   - 正式清单：`D:\FPGA_Data\HaGRIDv2\manifest.csv`
   - 清单 SHA-256：`74d4a0abec61ea4698caf0479ffb8fffd0b27f308166d81e13a5c20ad06aecb4`
   - 许可证 SHA-256：`14f4845e9c8d3de875cbac4139491da368ab1040a7f565e02894477279134d22`
   - 清洁清单报告：`D:\FPGA_Competition\report\evidence\S1-T01\20260914_hagrid_dataset_check_clean.json`
   - 该报告应显示 `158675/158675` 图片和标签有效、跨 split 完全重复为 0、人员/会话交叉为空、状态为 `PASS_AUTOMATED_MANUAL_PENDING`。
4. 复核 AC02/AC03 自动结果及其限定：`session_id=hagridv2_official_split_<split>` 是官方 split 分区键，不得表述为物理采集 session；Wong 自有多会话数据尚未提供。
5. 打开并复核 15 张真实 SVG 叠框候选：
   - 目录：`D:\FPGA_Competition\report\evidence\S1-T01\20260914_hagrid_previews_clean`
   - 人工复核单：`D:\FPGA_Competition\report\evidence\S1-T01\20260914_hagrid_visual_review.md`
   - 明确记录每类 2 个带框样本和 5 个无手样本是否通过；框是否贴合目标、类别语义是否正确、无手图是否确实无目标。不得用自动解码结果代替人工观察。
6. 复核 G0/AC01：最新探针证据 `20260914_environment_recheck.json` 的退出码为 2；RTX 4060 Laptop 可由 `nvidia-smi` 查询，但 `nvcc`、官方 Darknet 和固定 CUDA 设备冒烟程序均未提供。不得把 PyTorch 已安装或 GPU 可查询改写为 official-darknet-cuda 就绪。
7. 明确 AC05～AC07、G1、G2、G4 仍未执行：没有小样本训练、10 步更新、检查点保存/恢复、完整验证集评估、训练配置或真实精度结果。不得把单元测试、公开数据规模或自动清单检查写成训练精度。

工程已提供待编译的 CUDA 冒烟源程序：`D:\FPGA_Competition\verification\s1_t01_cuda_smoke.cu`。当前没有 `nvcc`，因此源程序尚未编译或运行；审查时应将其作为“已提供源、可执行文件未生成”的状态，不得据此判定 AC01 通过。

建议复核命令（受控解释器）：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s verification -p 'test_*.py' -q
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_environment_probe.py --report report\evidence\S1-T01\20260914_environment_recheck.json
```

已知复核结果：全量 Python 回归 14 项通过、退出码 0；Python 编译检查退出码 0；证据 JSON 解析退出码 0；环境探针退出码 2，属于当前环境未就绪的预期失败。数据全量检查已耗时约 34 分钟并退出 0，已有报告时请先读取报告，不要无依据重复启动长检查。

请以表格回传：问题编号、审查版本、文件位置、复现命令/退出码、证据路径、独立结论（已关闭/未关闭/不适用）和剩余关闭条件。特别回传 AC04 的人工叠框观察结果，以及是否接受 `session_id` 的分区键限定。本复审不得直接修改实现代码，也不得代替阶段1或板卡验收签结。

## 本轮修复后权威输入（开发侧，待独立复审）

请固定核查提交 `05faaaf574548d6dccb0976bcbb019b44ad71c81` 及其后仅包含本轮文档绑定的交付提交；最终交付提交完整哈希由开发侧在提交完成后回传。`05faa...` 是本轮代码、测试、数据报告和新预览的实现基线，最终审查应以聊天回传的最新交付提交为固定版本。不得把本文件视为独立签结。

本轮只处理以下问题：

- AUD-S1-T01-004：`verification/s1_t01_environment_probe.py` 现验证结构化 Windows PE；Darknet 需真实执行版本/帮助命令；CUDA 冒烟需真实执行固定 `verification/s1_t01_cuda_smoke.cu` 编译产物并返回 `S1_T01_CUDA_SMOKE_PASS`。新增回归拒绝伪造 PE、伪造 Darknet 输出和伪造 CUDA 成功标记。当前真实环境探针命令退出码 `2`，因为没有 `nvcc`、官方 Darknet 和 CUDA 冒烟可执行文件；AC01/G0 仍不通过。
- AUD-S1-T01-005：图片/标签同 stem、标签扩展名 `.txt`，重复唯一性基于规范化物理路径；新增 `..`、大小写和路径别名重复回归，定向回归退出码 `0`。
- AUD-S1-T01-006：PNG zlib、PNM 精确像素长度、JPEG 表/熵编码和 Pillow 完整 `Image.load()` 检查均已实现；非法 PNG、截断 PNM、空/伪 JPEG 均应生成失败报告而不是无报告异常退出。
- AUD-S1-T01-008：已修正 HaGRIDv2 COCO 框到 YOLO 中心框转换；无手候选只从 `dataset/no_gesture/` 空标签行选择。当前预览目录只保留 15 张新真实 SVG（每类 2 张带框、5 张无手），自动 landmarks 辅助核对 10/10 带框候选的 21 点落框；这不能替代 Wong 的逐张人工观察。
- AUD-S1-T01-009/010：`manifest_all.csv` 是原始输入/去重前证据，`manifest.csv` 是最终清洁/后续检查入口；当前两者路径和 SHA-256 已在 `20260914_sha256_manifest.txt` 分开登记。环境报告、复审接力文件和 CUDA 源随新交付链登记。训练配置、权重、检查点和评估脚本尚未生成，必须登记未执行/未生成，不填伪哈希。

本轮实际验证：13 项定向回归退出码 `0`；清洁数据全量检查退出码 `0`，`158675/158675` 有效，状态 `PASS_AUTOMATED_MANUAL_PENDING`；当前全量 Python 回归 18 项退出码 `0`；11 个 Python 文件 `py_compile` 退出码 `0`。历史 AUD-007 计数保持：8 项定向、12 项修复阶段全量、14 项旧最终提交全量；不能改写为本轮 13/18。

复审材料：

- `report/evidence/S1-T01/20260914_audit_repair.md`
- `report/evidence/S1-T01/20260914_sha256_manifest.txt`
- `report/evidence/S1-T01/20260914_environment_recheck.json`
- `report/evidence/S1-T01/20260914_hagrid_prepare.json`
- `report/evidence/S1-T01/20260914_hagrid_filter_manifest.json`
- `report/evidence/S1-T01/20260914_hagrid_dataset_check_clean.json`
- `report/evidence/S1-T01/20260914_hagrid_previews_clean/`（当前 15 张新 SVG）
- `report/evidence/S1-T01/20260914_hagrid_visual_review.md`（待 Wong 填写）
- `verification/s1_t01_cuda_smoke.cu`

复审必须明确：AUD-004～006 是否按代码与回归关闭；AUD-008 的 15 张新预览是否逐张通过（不能用自动报告替代）；AUD-009/010 的新提交 Git blob 与证据 SHA 是否一致；是否接受 `session_id=hagridv2_official_split_<split>` 仅作为分区键而非物理会话。AC01/G0 仍应记录为失败；AC04 在 Wong 回传前保持未关闭；AC05～AC07、G1、G2、G4 保持未执行。不要把单测、公开数据规模或自动清单检查写成训练精度。

本文件只提供复审输入，不代替独立审查签结。

## Wong 人工回传后的复审关注点

- Wong 已回传：1–10 号带框预览没有问题，带框人工结果为 10/10。
- Wong 已回传：11–15 号是捂脸动作，没有识别，可能不属于五个目标手势范围。请独立复审决定这是否满足 AC04 对“无手/无目标”样本的定义：它们画面中有手，因此不能被开发侧直接记为“确实无手”通过；若验收允许“非五类目标但画面可有手”的负样本，应在复审结论中明确该语义。
- 当前不要把 AC04 写成完全通过；开发侧记录为“带框部分人工通过，无手/非目标负样本语义待独立复审确认”。

## 本轮语义整改后权威输入（开发侧，待独立复审）

本轮从独立复审基线 `f6364bb5dcf6de1d74c30c346fb53e9ac9a89a42` 继续产生后续提交，不修改或重写该基线。复审请以开发侧最终回传的新提交为固定版本，并核对本节列出的代码、报告和证据哈希。

### AUD-S1-T01-008 / AC04

- 新增 `report/evidence/S1-T01/20260914_hagrid_semantic_review.csv`，不覆盖 `D:\FPGA_Data\HaGRIDv2\manifest.csv`。
- 1～10 是 Wong 已回传通过的 `target_gesture` 带框样本。
- 11～15 是 Wong 观察到的捂脸/遮挡动作，登记为 `non_target_gesture`；这些图片中存在手，不是 `no_hand`，不计入无手数量，但可作为五类检测器空标签负样本候选。
- HaGRIDv2 `dataset/no_gesture` 共 2164 条官方记录，均有 `bboxes`，当前未找到可诚实登记的真实无手样本；新增 `report/evidence/S1-T01/20260914_no_hand_collection_sheet.md` 要求 Wong 提供并逐张确认至少 5 张真实无手图片。当前 `no_hand=0/5`。
- 人工观察不能由自动解码、目录名或自动报告替代；AC04 仍未完全关闭，不代替独立审查签结。

### 检查器语义边界

`verification/s1_t01_dataset_check.py` 新增 `--semantic-review`。只有语义表中明确的 `sample_role=no_hand`、`manual_result=confirmed_no_hand` 且有人和实际 UTC+8 时间的空标签样本才计入 `no_hand`；`non_target_gesture` 单独统计；未绑定语义的空标签样本单独统计为 `unclassified_empty_label`。语义表的大小写、`..` 和其他物理路径别名重复绑定会失败。

### 本轮状态

- AC03：随着路径名推断被移除，当前正式 HaGRIDv2 清单的明确 `no_hand` 为 0，待补样本，因此不通过。
- AC04：1～10 带框人工通过 10/10；11～15 非五类目标负样本，不是无手；真实无手 0/5，因此未完全关闭。
- AC01/G0、AC05～AC07、G1、G2、G4：状态不变；没有 nvcc、官方 Darknet、CUDA 设备冒烟可执行文件，也没有训练/恢复/完整评估/真实精度结果。
- 历史 AUD-007 计数不改写：8 项定向、12 项修复阶段全量、14 项旧最终提交全量；本轮新增测试数量单独记录。

### 独立复审建议核对命令

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest verification.test_s1_t01_dataset_check -v
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_dataset_check.py --data-root 'D:\FPGA_Data\HaGRIDv2' --manifest 'D:\FPGA_Data\HaGRIDv2\manifest.csv' --semantic-review report\evidence\S1-T01\20260914_hagrid_semantic_review.csv --report report\evidence\S1-T01\20260914_hagrid_dataset_check_semantic.json
```

请独立复核提交、报告与证据绑定，并单独决定 AC04 是否接受 `non_target_gesture` 作为“五类目标之外”的负样本；不得把它们改写成 `no_hand`，也不得由开发侧代替审查签结。
