Hello Wong.

# S4B-PL-FRAME-01 独立 G2 审查记录

## 结论

CHANGES_REQUIRED。冻结版本发现一项阻断缺陷：帧核接受低于 G0 权重域下界的正权重。当前只读审查没有发现第二项已证实的阻断问题；硬件与系统集成不在本次结论内。

## 被审版本与绑定

- 冻结基线：`4639501c7c0badeded139e9a2a76017ca8294adc`
- 当前 HEAD：`d4f30e35937efed07c4f3ff62393e2e3a6a2ebdc`；总控说明该后续提交未改本次四个帧小程序源文件。
- 冻结清单：`report/evidence/S4-B/s4b_pl_frame_g2_20261023_r01/frozen_sources.json`，SHA-256 `28d820ab0034adc99aac74cdb375f8eae9e7a75f95267f0c608112bcb965bb67`。
- 运行清单：`report/evidence/S4-B/s4b_pl_frame_20261023_r07/run_manifest.json`，SHA-256 `da1a3b298da7190f53bdaa5e4bbae090facde8e712ba23b52bb7e1e14af8ec20`。
- 冻结帧源 `src/s4b_preproc_frame.sv` 与快照逐字节一致，SHA-256 `b731d0a2d308263c69d36a8ac04fcbeefd2e93064606919c9a427d924bd31c50`。
- 上游像素核 `src/s4b_preproc_pixel.sv` SHA-256 `4c4563433e9b5d868dde8c9232326afce1ddc4d4297bb548c7fc5252c6e284c1`，其定义作为独立接口语义对照。

## 阻断项：FP64 几何权重最小值常量错位

- 位置：`src/s4b_preproc_frame.sv:56` 定义 `FP64_MIN_WEIGHT_MAG = 63'h03ca000000000000`；`weight_supported` 在第 189 行按此常量比较，并在几何表响应处理第 493 行调用。
- G0 允许域为正零或 `[2^-53, 1]`。`2^-53` 的 binary64 magnitude 位模式为 `0x3ca0000000000000`。冻结的上游像素核在 `src/s4b_preproc_pixel.sv:25,84` 使用该正确下界。
- 帧核当前常量 `0x03ca000000000000` 的指数域是 `0x03c`，远小于期望的 `0x3ca`。结果是低于下界的数仍能通过正常数、非负及最大值检查。例如 `2^-100`（位模式 `0x39b0000000000000`）以及紧邻下界的前一位 `0x3c9fffffffffffff` 都被当前谓词接受；按上游/接口下界，两者都必须拒绝。它们随后会被缓存为几何权重并继续进入像素处理，错误数据不会触发 `ERR_GEOMETRY`。
- 现有 `geometry_fault` 仿真用例检查的是源索引越界，不检查权重范围，所以当前仿真没有覆盖此故障。

### 关闭条件

1. 将帧核下界改为与像素核相同的 magnitude 位模式（例如 `63'h3ca0000000000000`）。
2. 增加 RTL 边界用例：`+0` 与恰好 `2^-53` 接受；紧邻其下的 `0x3c9fffffffffffff` 和代表值 `2^-100` 在 X 表和 Y 表均触发几何错误。断言无 RAW/TENSOR 请求、无像素输出，且错误元数据保持正确。
3. 修复后重新运行适用 Python 检查与 XSim，并以新 RunId 重新冻结、绑定来源与证据；本次冻结内容保持不变。

## 独立探针与已有复核

### 新增纯 Python 阈值探针

- 目录：`D:\codex-worktrees\w4\tmp\4\S4B-PL-FRAME-01\r2_review_20261023_02_weight_domain`
- 命令：`C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\codex-worktrees\w4\tmp\4\S4B-PL-FRAME-01\r2_review_20261023_02_weight_domain\weight_threshold_probe.py`
- 原生退出码：0。该探针读取冻结帧核及上游像素核中的常量，按帧核谓词逐位复算正零、最小允许值、下界前一位、`2^-100`；输出确认当前阈值对后两项产生 false accept。它是纯 Python 的谓词探针，不是 RTL 仿真。
- 脚本 SHA-256：见同目录 `weight_threshold_probe.py`；标准输出、标准错误和退出码分别保存在 `probe.stdout.txt`、`probe.stderr.txt`、`probe.exitcode.txt`。

### Python 单元检查

- 命令：在 `D:\codex-worktrees\w4` 执行 `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest -v verification.test_s4b_preproc_frame`
- `TEMP`、`TMP` 指向本次隔离目录 `D:\codex-worktrees\w4\tmp\4\S4B-PL-FRAME-01\r2_review_20261023_01`。退出码 0，5 项通过。原始记录在该目录 `python_unit.stdout.txt`、`python_unit.stderr.txt`、`python_unit.exitcode.txt`。
- 该套件主要验证 fixture 绑定、布局和小尺寸参考向量；通过不能关闭本报告的权重下界缺陷。

### 独立 fixture 重建

- 命令：在 `D:\codex-worktrees\w4` 执行 `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B verification\run_s4b_preproc_frame.py --run-dir D:\codex-worktrees\w4\tmp\4\S4B-PL-FRAME-01\r2_review_20261023_r1_fixtures`
- `TEMP`、`TMP` 指向同一新 RunId，退出码 0。重建的 CHW 小向量、描述符、内存镜像及 88 字节大样本前缀与 r07 绑定值一致；输出记录在 `r2_review_20261023_r1_fixtures\prepare.stdout.txt`、`prepare.stderr.txt`、`prepare.exitcode.txt`。

开发者 r07 包中的 XSim 日志与报告已作为既有证据查看；本审查未启动 Vivado/XSim，也未操作硬件。r07 只覆盖两个 4×4 完整输出及 `202×329→416` 的通道 0 前 88 字节；它不证明完整 416 帧吞吐或板上行为。

## 其余审查范围与限制

静态核对了 descriptor 范围/重叠检查、活动几何表读取和 X/Y 源界限、CHW 与 64 字节 padding、四邻点顺序、64 位单 outstanding 内存口的请求保持/响应记账、abort 排空、sticky protocol fault 与结果保持。对覆盖范围内未发现第二项已证实的阻断项。部分非法 descriptor 分支没有独立仿真用例，作为覆盖限制保留给修复轮回归核对。

该结论只针对冻结的局部抽象内存口帧小程序 G2。真实 AXI/HP0、物理 DDR 地址、PS 协议、系统 G0、4D、整帧吞吐、G3 板测均未由本审查验证；清单记录硬件 `NOT_RUN`。
