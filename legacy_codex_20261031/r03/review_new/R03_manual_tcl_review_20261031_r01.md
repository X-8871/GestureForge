# R-03 手工 Tcl 与准备证据独立复审 r01（2026-10-31）

## 结论

**CHANGES_REQUIRED，当前版本不建议开窗执行。** 原因：会造成硬件目标变更的 Tcl 操作缺少目标唯一性前置核验；断连错误也被忽略。未执行任何脚本、厂商工具或硬件操作。

## 被审文件 SHA-256

- `setup/setup.tcl`：`3173286efd25849ac440fa2b66c4342c089161fe6c011f8527ad952e2644832d`
- `restore/restore.tcl`：`74027125ad5a9adf221b1190c088b56a14fa9aa7eb3188766e53f42f755f3b4e`
- `event/event.tcl`：`9d5c4a2a842e3749221755764ea158d884ed24108f2511549ac986f8f2b64d85`
- `close/close.tcl`：`de5af984a033301d94b883adc24ad14481bab1b7620559ce07540d4f9103fae7`
- `context.json`：`e64a938769488007149f417d451d3a78524a014899c9b8b9a82027cedd0612a6`
- `authorization.md`：`0cbdaeb67c910290654c316533d0ceaa31f976af78ce8a9a77347f808fe10dd3`
- `pre_verified_host_tool_identities.json`：`1e0207af507f17f42a5a0f7339f69dbaa3bee68e7028701e7abfba7f2ce98a0c`
- `elf_load_ranges.json`：`cc8454d36fdab4be3767f2682333c6412eed7e0686a9789a43e759b5111afc79`

## 阻断项

1. `setup/setup.tcl` 对 A9 核使用唯一目标检查，但选择 `*xc7z020*` 后直接执行 `fpga`，未验证 FPGA 目标恰好一个或目标身份。编程前必须核实目标数及名称/设备身份。
2. `restore/restore.tcl` 在写候选 DDR 前对两个 A9 目标只执行 `targets -set -filter` 和 `[state]`；`event/event.tcl` 与 `close/close.tcl` 也未验证 A9 目标唯一性。对候选区整段 `mwr`、CSR 读取和 `stop`，应逐核先检查过滤结果恰为一个并核验目标名称，再选择目标；不匹配时立即失败。
3. 四份 Tcl 都执行 `catch {disconnect}` 但忽略结果。若断连失败，脚本仍可能返回成功。应将断连失败并入退出错误状态。

关闭条件：上述目标唯一性与名称核验覆盖所有 A9/FPGA 选择；断连失败返回非零；冻结新 SHA 后只读复审。

## 已核实范围与限制

- `setup` 沿用已有 POR 初始化，不重复 `init`，只执行授权的 0xA/FPGA/0xF/ELF `dow` 与 CSR idle 检查；没有 `con`，与本轮两核停止、无推理活动的只读取样口径一致。未见 reset/应用运行命令。
- `restore` 仅在 before 前从 `m3_snapshot_orig.bin` 写固定候选区 `[0x12000000,0x12C08000)`，字数 3,153,920；准备证据记录的快照大小 12,615,680、SHA-256 与固定旧基准一致。`event` 只读 CSR/GT 三次并核两核状态；未引入 arena 操作。
- ELF 段从 `0x100000` 与 `0x108000` 开始，第二段内存结束地址为 `0x24F210`，均远离候选区；manifest 声明 `candidate_overlap=false`。
- context 的 bit/XSA/init ELF/app ELF SHA 与身份清单一致。pre 身份查询在 01:16:25+08:00 返回空进程/监听、退出码 0、`hardware_started=false`；此快照不是开窗时的实时空闲证明，应按租约要求在开窗前重新核验。
- `authorization.md` 中 DSH-019 租约仍是 `OFFERED → 待 CLAIM`，当前文件集没有 CLAIM 回执。DSH-021/022要求开窗前 CLAIM 并声明端口；须另行核验保存该回执。
- 这次复审为静态读取；没有验证实际 XSDB/Tcl 语义、硬件响应或真实进程/端口状态。
