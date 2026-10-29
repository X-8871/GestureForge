# CDX-20261026-001 main 与阶段3写权交接 OFFER

- 编号：CDX-20261026-001；时间：2026-10-26 19:05（UTC+8）。
- 发出方：Codex 项目总控（让出方）。
- 接收方：DSH 项目总控。
- 用户指令：main 交接行置 OFFERED，由 DSH 项目总控认领阶段3。

## OFFER 范围

- main：项目总控与全局状态写权。
- 阶段3：D:\codex-worktrees\dbdf，分支 codex/stage3-video；阶段3状态已单独追加 OFFERED 行。
- 不包含 w4、w5、w6、w2b 或 96a3 的工作树写权。
- 本次交接只授权写权转移，不授权新增编译、下载、烧录或板级活动；需继续遵守既有 Wong 窗口授权规则。

## 现场核验与改动归属

- main HEAD：bdb7a360916641382a04f018c668774543e45b8e；增加本记录前 status 为 409 项（17 修改、392 未跟踪），增加本记录后应为 410 项。既有内容与本记录均保留，不清理、不回退、不全量暂存。
- 阶段3 HEAD：7e4a0a5699c9034d6b6f3e42b2aa5bee24b5aeb3；增加 OFFER 行前 4 项未跟踪，增加 STATE 行后共 5 项（1 修改、4 未跟踪），均保留。
- 核验时两树均无 index.lock；Vivado、XSDB、hw_server、Vitis、XSCT、XSim 等进程未发现；netstat 未发现 3121 LISTENING。
- Codex 未执行硬件、编译或技术工作。本 OFFER 不构成技术验收或板级状态核验。

## 状态待核对

- DSH 当前阶段3 STATE 顶部记录标注阶段3收尾 G5 PASS、记录性局限及冻结基线；旧 18:03 快照与旧交接行仍记载 G5 未通过。请 DSH 项目总控 CLAIM 后核对并统一表述；本次仅记录该差异，不作独立技术裁定。
- 本 OFFER 尚未 CLAIMED。请 DSH 项目总控按 handoff_check 契约分别核验 main 和阶段3，完成后在 STATE/信箱明确回执 CLAIMED；回执前 Codex 不宣称写权已转移。
- 新增状态行与本记录留在工作区，未提交；接手方串行核验差异后决定其提交方式。
