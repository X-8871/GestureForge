# S1-T01 独立复审接力提示词（2026-09-14）

请在不修改共享工程实现、不代替开发签结的前提下，独立复审 `S1-T01 训练环境与数据准备` 当前交付。复审对象固定为 Git 提交 `1e0641d45c95f4ca8336ef8b191efcd3f3cf9e4d`；其中 AUD-S1-T01-004～006 的开发修复提交为 `48cbd749721917c30346dafd631a5e11941b654c`，HaGRIDv2 数据准备与证据交付提交为 `9174c465481b153872c83cf4312679438641a6ec`。工作区已有与本任务无关的改动：`docs/obsidian-project/总控.md`、`docs/obsidian-project/项目接手提示词.md`、`vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr` 以及两张板卡照片；不得把它们纳入本次审查版本。

任务规格固定为原 Vault 任务记录 `S1-T01_训练环境与数据准备.md`（当前源文件 SHA-256：`C7DA418D22575D0D87604F816E8F3874EAC2D37ABE665D06E8B9F40D75EC776D`）和《B方案实施与阶段验收计划》v3.0。范围边界：五类带框检测；YOLOv4-tiny 优先作为上板候选；完整 YOLOv4 仅作 PC 对照；输入尺寸和性能尚未冻结；不把 32×32 分类规格带入本任务；本任务不包含正式长训、INT8、RTL 或板卡验收。

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

建议复核命令（受控解释器）：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s verification -p 'test_*.py' -q
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_environment_probe.py --report report\evidence\S1-T01\20260914_environment_recheck.json
```

已知复核结果：全量 Python 回归 14 项通过、退出码 0；Python 编译检查退出码 0；证据 JSON 解析退出码 0；环境探针退出码 2，属于当前环境未就绪的预期失败。数据全量检查已耗时约 34 分钟并退出 0，已有报告时请先读取报告，不要无依据重复启动长检查。

请以表格回传：问题编号、审查版本、文件位置、复现命令/退出码、证据路径、独立结论（已关闭/未关闭/不适用）和剩余关闭条件。特别回传 AC04 的人工叠框观察结果，以及是否接受 `session_id` 的分区键限定。本复审不得直接修改实现代码，也不得代替阶段1或板卡验收签结。
