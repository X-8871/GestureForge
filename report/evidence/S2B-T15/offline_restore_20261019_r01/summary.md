# R04 PS 离线重建与恢复边界

## 结果

- 基线：w2b HEAD `5e26edd`。既有 R04 构建记录绑定源码提交 `03faa2d47a6e49d7475e387cf6b33edda4962c68`、XSA SHA-256 `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`、bit SHA-256 `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`。
- 使用保存的 `app_compile_commands.json`、`init_compile_commands.json` 和新副本 `build.ninja` 导出的链接命令，直接运行 ARM GCC 13.4.0。四个源文件编译及两个 ELF 链接均退出 0；未启动 Vitis、SDK、XSDB、Vivado、串口或板卡服务。
- 新 ELF：infer 389,216 B，SHA-256 `983bbe878dc24a0a009c87aeb8af0feb14e235147e7471bd6566414f8bcf3f71`；init 170,592 B，SHA-256 `9a3622eb7467d4f3afc5eb7f02890b50395edaa03ea7ac33e34c6cabf21e9852`。两者都与原 ELF 字节不同。
- `comparison.json` 记录所有 PT_LOAD 段的地址、文件/内存长度、标志、对齐及原始负载 SHA。布局相同；原始负载差别各为 20 B，定位为 GNU build-id 描述字段。`comparison_buildid_normalized.json` 仅将该 20 B 字段归零后比较，所有 PT_LOAD 逐段字节与 SHA 相同；入口和符号表也相同。infer 的 build-id 数据落在 `.text` 尾部，init 位于 `.note.gnu.build-id`。因此，当前证据支持静态可装载内容在忽略 build-id 标识后等价，不证明 ELF 字节完全相同或板上行为。
- `comparison_sections.json`、`comparison_buildid_normalized.json` 与反汇编日志保留局部差异证据。ELF/去调试 ELF/二进制映像摘要不同的原因不能仅从摘要判断；逐节结果确认除 build-id 外可装载内容相同。

## 输入完整性和可恢复限制

- 指定输入 `report/evidence/S2B-T18/formal_review_20261018_r01/runtime/libxilstandalone.a` 为 359,692 B，SHA-256 `1341903853c1aafcad3ae3ac21f816a59e715dffe46b4b9d126a2c7c6f95cc17`，与 R04 平台归档相同。链接还依赖 `libxil.a`（459,614 B，SHA-256 `184cfec64f93594fd79cc05eb1307917fa8de7ea57201befe8d94b7c6a6c1e23`）、`libxiltimer.a`（18,756 B，SHA-256 `827c61aac0b6cce641268addbef86a6bb291ad8704897832d6ea9e708e33e36b`）、BSP 头文件、Xilinx.spec 和工具链系统库。
- 本次成功构建使用了隔离副本 `tmp/2B/S2B-T15/offline_restore_20261019_r01/r04_workspace/`。副本从既有 2026-10-16 R04 临时工作区复制（73,885,909 B），再把指定 `libxilstandalone.a` 放入副本。恢复脚本消费该已准备副本及原 `*_compile_commands.json`，不会从 Git 自动生成 BSP 或平台文件。
- 初次副本文本改写曾给副本生成的两个 linker script 添加 UTF-8 BOM：infer 6347 B / SHA-256 `7164ac2f54535e1aa5a7764a39a482e7c435b6fbeedd2aab6f679cce56fe9147`，init 6221 B / SHA-256 `ddd4aa279db0df77622d59bafc64864d86499105a66e754372fa2a8e0d7d5c03`。原 R04 linker script 分别为 6344 B / `8f3efdbc02d190d8c4f193a6762bbacb4301f326ba6e334fd21cbc00b6379805` 和 6218 B / `508b0c05a5dc0258613e3985c179d24f1ed1f3be571d7c6ad564939113766f4a`。此差异已披露；静态 PT_LOAD 比较显示在忽略 build-id 后负载相同，但这不是逐字节输入复现。
- 本任务只核验了已有 XSA 内 bit 的身份哈希，没有重建 PL、没有重新生成 XSA，也没有做冷启动恢复、板上运行或整套 BSP SDK 的干净重建。干净 PS ELF 构建不能称为完整 PL 恢复。
- 因 BSP 头文件/库闭包和生成脚本仍依赖现存 R04 临时平台目录，本证据不能声称仅凭 Git 可恢复。未来若需摆脱该磁盘依赖，需要另行冻结 BSP 输入闭包或按正式流程重建并审查平台。

## 命令和日志

- 主运行命令：`python.exe report/evidence/S2B-T15/offline_restore_20261019_r01/restore_offline_build.py`。桌面绑定 Python 实际绝对路径与运行环境见调用记录；工具链与版本、逐文件 SHA、编译及链接命令/退出码见 `machine_result.json`。
- `restore_offline_build.py` 在 `machine_result.json` 已存在时拒绝写入，避免覆盖本次结果。它仅用于已准备好的隔离副本，不负责复制平台、重建 BSP 或恢复 bit。
- 失败尝试的原始上下文及不能恢复的旧日志说明见 `attempt_history.json`；成功编译、链接、Ninja 命令列举和比较结果各有独立日志。
