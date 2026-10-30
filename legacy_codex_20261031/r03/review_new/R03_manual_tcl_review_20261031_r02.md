# R-03 手工 Tcl 与准备证据独立复审 r02（2026-10-31）

## 结论

**PASS（静态源码与准备证据范围）**。目标唯一性检查及断连失败处理已修复。未运行 Tcl、厂商工具、hw_server 或硬件；PASS 不代表实时启动前检查或 G3。

## 被审文件 SHA-256

- `setup/setup.tcl`：`5645decb4a652e433ccbbfe5397ec34c1bcce52335002645649315d161f90261`
- `restore/restore.tcl`：`710e596213075077ae52e6dd460a868f6c49268f891f6351f3e32ad3319c3760`
- `event/event.tcl`：`1393ca44b181ea196c4dc390efcce25bfb9f1ad11797c972c915b1c7611f516a`
- `close/close.tcl`：`0be6bc5d236ade5ea4f818086822012b7825284cd0e6ec65fd8664617b1e2885`
- `context.json`：`e64a938769488007149f417d451d3a78524a014899c9b8b9a82027cedd0612a6`
- `authorization.md`：`0cbdaeb67c910290654c316533d0ceaa31f976af78ce8a9a77347f808fe10dd3`
- `pre_verified_host_tool_identities.json`：`1e0207af507f17f42a5a0f7339f69dbaa3bee68e7028701e7abfba7f2ce98a0c`
- `elf_load_ranges.json`：`cc8454d36fdab4be3767f2682333c6412eed7e0686a9789a43e759b5111afc79`
- `claim_receipt.md`：`cd4d5213f19cbf67506ac1dd7446f15af2880b9be7bbbd6197b613cdbffa4eae`

## 核查摘要

- 四份 Tcl 的每次目标选择均通过 `select_unique`：先查 properties 匹配数为 1，再校验名称白名单，随后才设置目标。FPGA 选择也经过该 helper。
- 四份 Tcl 在主体错误时保留失败；主体成功但 `disconnect` 失败时改为非零退出码 2。`setup` 沿用现有 POR，不重复 `init`，不运行应用；`restore` 只在 before 前从固定旧快照写固定候选范围；`event` 只读 CSR/GT 三次；`close` 只核验/必要 stop 两核，不 reset。
- context 与预核验身份中的 bit/XSA/init/app ELF SHA 一致；ELF load segments 与候选范围不重叠；旧快照 SHA 与固定 before 基准一致。
- `claim_receipt.md` 声明 3121、01:18 CLAIMED、01:20 前不启动；与 DSH-021/022 的事件和身份约束一致。pre host 身份快照记录 01:16:25 进程/监听为空，但启动前仍须重新只读核验实际状态。

## 限制

- 未验证 Tcl 在真实 XSDB 上的命令语义、目标枚举结果、硬件状态或 ELF/快照文件的实时内容。
- Tcl 路径使用 `/`，身份记录使用 `\`；本复审未将这两种字面形式规范化或做实时文件解析。
- 未执行任何内容；真实取样及收窗过程仍需单独记录证据。
