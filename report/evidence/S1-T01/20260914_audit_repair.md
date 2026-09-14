# S1-T01 独立复审问题修复记录（开发侧）

日期：2026-09-14（UTC+8）
范围：AUD-S1-T01-004～006、008、009、010。
固定任务规格：原 Vault 任务记录 `S1-T01_训练环境与数据准备.md` 与《B方案实施与阶段验收计划》v3.0。
边界：五类带框检测；YOLOv4-tiny 优先上板候选；完整 YOLOv4 仅 PC 对照；输入尺寸和性能未冻结；不引入 32×32 分类规格。

本文件是开发修复证据，不是独立复审签结。当前状态统一写为“开发修复已完成，待独立复审确认”；不能据此宣称 G0、AC01 或 AC04 通过。

## 修复内容

- AUD-S1-T01-004：环境探针对 Darknet 和 CUDA 冒烟程序要求结构化 Windows PE；Darknet 必须真实执行并返回可识别的版本/帮助输出；CUDA 冒烟必须真实执行并包含 `S1_T01_CUDA_SMOKE_PASS`。固定源程序为 `verification/s1_t01_cuda_smoke.cu`。当前没有 `nvcc`、官方 Darknet 或 CUDA 冒烟可执行文件，环境探针仍应失败。
- AUD-S1-T01-005：图片与标签按同 stem、`.txt` 标签扩展名校验；重复计数使用规范化物理路径，覆盖 `..`、大小写和其他物理路径别名；新增别名重复回归。
- AUD-S1-T01-006：PNG 解压流、PNM 精确载荷长度、JPEG 量化表/霍夫曼表/熵编码和 Pillow 完整像素解码均进入检查；异常输入统一写入报告，不使检查器无报告退出；新增非法 PNG、截断 PNM、空/伪 JPEG 回归。
- AUD-S1-T01-008：HaGRIDv2 的官方归一化 COCO `[left, top, width, height]` 先转换为归一化 YOLO `[center_x, center_y, width, height]`；无手候选只从 `dataset/no_gesture/` 空标签行选取。重新生成 15 张真实 SVG：每类 2 张带框、5 张无手。开发侧用官方 landmarks 做辅助核对为带框 10/10 全部 21 点落框、无手 5/5 路径和空标签符合；仍待 Wong 逐张观察。
- AUD-S1-T01-009/010：重新绑定原始与清洁清单字段和哈希；当前交付将环境报告、复审接力文档、CUDA 源程序及本轮证据纳入同一交付提交。训练配置、权重、检查点和评估脚本尚未生成，保持“未执行/未生成”，不填伪哈希。

## 实际命令、版本和退出码

受控 Python：`C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`；CPython 3.12.14；Pillow 12.3.0。以下命令均在 `D:\FPGA_Competition` 执行。

| 时间/阶段 | 实际命令 | 退出码 | 结果 |
|---|---|---:|---|
| 定向修复回归 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest verification.test_s1_t01_environment_probe verification.test_s1_t01_dataset_check verification.test_s1_t01_prepare_hagrid -v` | 0 | 13 项通过；覆盖 PE/Darknet/CUDA 伪造边界、物理路径别名、PNG/PNM/JPEG 损坏、HaGRID 框转换 |
| 原始标签重建 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_prepare_hagrid.py --data-root D:\FPGA_Data\HaGRIDv2 --manifest D:\FPGA_Data\HaGRIDv2\manifest_all.csv --labels-root D:\FPGA_Data\HaGRIDv2\labels --report report\evidence\S1-T01\20260914_hagrid_prepare.json` | 0 | 17:58:24～17:59:14；158,698 行、156,536 框；原始清单字段和哈希一致 |
| 清洁清单生成 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_filter_manifest.py --input D:\FPGA_Data\HaGRIDv2\manifest_all.csv --output D:\FPGA_Data\HaGRIDv2\manifest.csv --duplicate-report report\evidence\S1-T01\20260914_hagrid_duplicate_analysis.log --report report\evidence\S1-T01\20260914_hagrid_filter_manifest.json` | 0 | 158,698→158,675 行；删除 val 7、test 16；输出清单哈希一致 |
| 清洁数据全量检查 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_dataset_check.py --data-root D:\FPGA_Data\HaGRIDv2 --manifest D:\FPGA_Data\HaGRIDv2\manifest.csv --report report\evidence\S1-T01\20260914_hagrid_dataset_check_clean.json --preview-dir report\evidence\S1-T01\20260914_hagrid_previews_clean` | 0 | 启动 16:44:24；约 74 分钟；158,675/158,675 有效；状态 `PASS_AUTOMATED_MANUAL_PENDING`；PNG/BMP/PNM/JPEG 完整检查路径执行 |
| 环境探针 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_environment_probe.py --report report\evidence\S1-T01\20260914_environment_recheck.json` | 2 | Python/NumPy/`nvidia-smi`/CMake 可用；`nvcc`、官方 Darknet、固定 CUDA 冒烟可执行文件缺失；这是当前环境未就绪的真实失败，不是 AC01 通过 |
| 当前全量 Python 回归 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s verification -p 'test_*.py' -v` | 0 | 18 项通过，1.346 秒 |
| 当前 Python 编译检查 | `$py='C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'; $files=Get-ChildItem verification -Filter *.py -File \| Sort-Object FullName \| ForEach-Object FullName; & $py -m py_compile $files` | 0 | 11 个文件通过 |

历史测试计数保持区分：AUD 修复定向回归 8 项；AUD 修复提交阶段全量 12 项；旧最终提交全量 14 项；本轮修复后的新定向回归 13 项；本轮修复后的新全量回归 18 项。不同计数不互相替代。

## 当前数据与证据清单

- 原始清单：`D:\FPGA_Data\HaGRIDv2\manifest_all.csv`，SHA-256 `c0f93b494cd6649fdbf14d5bae0448ed7f9f77ca340a82f6e16b98657cb0c07e`；用途是保留原始 158,698 行输入和去重前证据。
- 最终清洁清单：`D:\FPGA_Data\HaGRIDv2\manifest.csv`，SHA-256 `74d4a0abec61ea4698caf0479ffb8fffd0b27f308166d81e13a5c20ad06aecb4`；用途是后续检查/训练入口，158,675 行、156,518 框。
- 清洁检查：`report/evidence/S1-T01/20260914_hagrid_dataset_check_clean.json`，状态 `PASS_AUTOMATED_MANUAL_PENDING`，自动错误为空，跨 split 完全重复为 0，人员/会话交叉为空；`session_id` 仍只表述为官方 split 分区键，不表述为物理采集 session。
- 原始转换报告：`report/evidence/S1-T01/20260914_hagrid_prepare.json`，`manifest` 明确指向 `manifest_all.csv`，`manifest_sha256` 为原始清单哈希，并记录 COCO→YOLO 转换规则。
- 去重报告：`report/evidence/S1-T01/20260914_hagrid_filter_manifest.json`，同时明确 `input_manifest=manifest_all.csv`、`output_manifest=manifest.csv` 及两者哈希。
- 许可证：`D:\FPGA_Data\HaGRIDv2\license\en_us.pdf`，SHA-256 `14f4845e9c8d3de875cbac4139491da368ab1040a7f565e02894477279134d22`。
- 预览目录：`report/evidence/S1-T01/20260914_hagrid_previews_clean`，当前仅保留 15 个新 SVG；人工复核单为 `20260914_hagrid_visual_review.md`，所有人工状态仍为“待 Wong”。
- CUDA 源：`verification/s1_t01_cuda_smoke.cu`；源程序已提供，当前未编译运行。源存在不能替代 `nvcc` 编译、真实设备运算和可执行文件哈希。
- 原始 ZIP：按用户要求已删除并清理回收站；删除前未采集 ZIP SHA-256，因此只登记解压/CRC/条目数证据，不伪造压缩包哈希。

## 恢复方法与停止条件

恢复前先确认没有同一脚本进程，并读取对应报告状态；不要重复启动全量检查。数据流程恢复命令使用本节的 `prepare`、`filter`、`dataset_check` 原命令，输出路径必须保持一致。CUDA 环境补齐后先编译并运行固定源程序，再将可执行文件路径和 SHA-256 传入环境探针。训练恢复必须先做小样本流程验证并使用配置哈希/既有检查点；出现 OOM、NaN/Inf、数据损坏、清单交叉或无进度超时立即停止。

## 未执行项

- AC01/G0：失败；当前没有 `nvcc`、官方 Darknet 和固定 CUDA 设备冒烟可执行文件。
- AC04：自动检查完成，但 15 张新真实预览尚未由 Wong 逐张填写人工复核单；不代替人工签字。
- AC05～AC07：未执行；没有小样本训练、检查点保存/恢复、完整评估、零预测路径和复跑交接证据。
- G1、G2、G4：未执行；没有真实训练精度或板卡/系统验收证据。
- 正式长训、INT8、RTL、板卡烧录和板卡验收：未执行。

**开发侧交付状态：本轮问题修复和适用自动回归已完成，待独立复审确认；不代替独立审查签结。**

## Wong 人工回传（2026-09-14）

- Wong 回传：1–10 号预览没有问题，带框样本人工通过 10/10。
- Wong 回传：11–15 号为捂脸动作，没有识别，可能不属于五个目标手势范围。
- 记录限定：11–15 号虽可作为五类目标之外的负样本候选，但画面中存在手，不能直接写成“确实无手”通过。AC04 的带框部分通过；无手/非目标负样本语义仍待独立复审确认。
