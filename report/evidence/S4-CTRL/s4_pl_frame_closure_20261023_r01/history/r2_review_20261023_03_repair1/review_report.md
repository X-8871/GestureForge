Hello Wong.

# S4B-PL-FRAME-01 修复轮 1 独立 G2 复审

## 结论

PASS（仅限冻结 r02 的局部帧小程序 G2）。上一轮的权重下界缺陷已修复；所要求的八个 X/Y 正负边界场景有断言，r08 实际 XSim 日志与清单绑定一致。没有发现新增阻断项。

## 被审版本和哈希

- 基线 HEAD：`d4f30e35937efed07c4f3ff62393e2e3a6a2ebdc`。
- 冻结清单：`report/evidence/S4-B/s4b_pl_frame_g2_20261023_r02/frozen_sources.json`，SHA-256 `490aff4f087d8db8aa725b198210b7198d49a0d7cad6fb3e73c288f263a369d5`。
- r08 运行清单：`report/evidence/S4-B/s4b_pl_frame_20261023_r08/run_manifest.json`，SHA-256 `c9ab2e5cf75f60d6e2b90ec06e819a5439e68bbcb5ea81a8f745887757bc49c5`。
- 四份当前源文件均与 r02 冻结快照的字节数和 SHA-256 一致：
  - `src/s4b_preproc_frame.sv`：`cec22f92bee4a05724e81ff47bd164d05bcb09b184c722eeb5317b48fa2218f2`
  - `sim/tb_s4b_preproc_frame.sv`：`8a87a954ce74dd519a875c42bb4b15da5ff80ddf8e2a70334ab15d5827235a5b`
  - `verification/run_s4b_preproc_frame.py`：`7212e1dcae073199f6c0bc6aa5553110b474f25e0aab0e81356762e51c4a4fbf`
  - `verification/test_s4b_preproc_frame.py`：`1e34a237da4e3031837ee3b2e55ea4bbe15db15c889086b0b5c8e541c369d837`
- 相对 r01 冻结内容，RTL 只将下界常量改为 `63'h3ca0000000000000`；testbench 增加八个边界场景。runner、fixture 单测未变化。r08 manifest 仍引用 r01 作为“变更前”比较基线并将已修改源标为不匹配；r02 清单随后以四份新 SHA 和 r08 manifest SHA 建立修复版冻结绑定，未见身份混淆。

## 缺陷关闭与断言核对

帧核现使用与像素核相同的 binary64 `2^-53` magnitude 位模式 `0x3ca0000000000000`。独立 Python 谓词检查正零、恰好下界、下界前一位、`2^-100` 和 1.0 共 5 项，全部符合 G0 域。

testbench 对 X、Y 轴分别覆盖正零和恰好 `2^-53` 接受；分别覆盖 `0x3c9fffffffffffff` 与 `2^-100` 拒绝。拒绝分支核对 `ERR_GEOMETRY`、错误地址/session/frame、预期几何读取数，并断言没有 RAW/TENSOR 请求、写入或像素活动。接受分支确认扫描抵达首个 RAW 请求，再受控 abort；这验证权重域接受，不声称完成对应帧输出。当前每个 X/Y 场景替换表项的第一个权重字；RTL 对保存的首权重和响应中的第二权重都调用同一 `weight_supported`。第二权重字段没有单独替换场景，但实现静态检查未发现两个调用路径存在差异。

## 执行与既有仿真证据

- 独立复核脚本：`D:\codex-worktrees\w4\tmp\4\S4B-PL-FRAME-01\r2_review_20261023_03_repair1\repair1_review_probe.py`。命令为 `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\codex-worktrees\w4\tmp\4\S4B-PL-FRAME-01\r2_review_20261023_03_repair1\repair1_review_probe.py`，原生退出码 0。它核验冻结/运行清单、四源与快照、17 份封存工件哈希、r08 日志及 8 个边界调用；输出和退出码在同目录 `probe.stdout.txt`、`probe.stderr.txt`、`probe.exitcode.txt`。
- 新 RunId 下重跑 Python fixture 单测：工作目录 `D:\codex-worktrees\w4`，命令 `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest -v verification.test_s4b_preproc_frame`；子进程 `TEMP` 与 `TMP` 均指向本 RunId 的 `unit_temp`。原生退出码 0，5 tests 通过。stdout、stderr、退出码分别保存在同目录 `python_unit.stdout.txt`、`python_unit.stderr.txt`、`python_unit.exitcode.txt`。
- 未重新启动 Vivado/XSim；核验 r08 原始归档。`report/evidence/S4-CTRL/s4_pl_frame_closure_20261023_r01/artifacts_r08/simulate.log` SHA-256 为 `60b1e05984efb4ab6abad79743bbba077aabaf88e84bf5979f7c996b1fa0e569`，含 `TEST_PASS ... weight_accept=4 weight_reject=4 ... cycles=30898`，并在 308980 ns `$finish`。完整 `vivado_complete.log` 记录 XSim 结束及 MCP native exit 0；r08 manifest 记录 Vivado native exit 0、耗时 17.459 秒、器件 `xc7z020clg400-2`。独立脚本核对 17/17 封存文件与 inventory 哈希一致。

## 复用的静态结论与限制

本轮变更未触及 r01 已审过的 descriptor、范围/重叠、几何索引、CHW/padding、邻点顺序、单 outstanding 内存口、abort 排空、sticky protocol fault 等实现，复用上一轮对这些不变代码的静态结论。r08 仍只覆盖两个 4×4 完整输出及 `202×329→416×416` 通道 0 前 88 字节后受控 abort；不证明完整 416 帧、整帧吞吐、系统集成、物理地址或板上行为。硬件为 `NOT_RUN`，G3/G4 不在本次 PASS 范围。
