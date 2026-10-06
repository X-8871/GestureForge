# ADR-0001：通过认证命名管道传递准备阶段元数据摘要

- 状态：已采用
- 日期：2026-10-06（UTC+8）
- 范围：Stage 3 HDMI-only 实现诊断脚本的受控准备阶段；不授权或描述板上操作。

## 背景

准备阶段要把 Tcl 端计算出的元数据文件数和树 SHA-256 交给 PowerShell 监督器，用于核验 `prepare.result`。标准输出由被监督进程及其子进程共享，不能证明标记实际由预期 Vivado Tcl 进程发出；接受 stdout 标记会允许同一进程树中的辅助进程伪造摘要。Tcl/Vivado 通道实测可以单向写入 Windows 命名管道，但读取管道响应会以 `EAGAIN` 失败，因此双向 ACK 协议不可用。

## 决策

使用每次运行随机命名、单向写入的本地命名管道。服务端在启动 Vivado 前开始等待连接；连接建立后立即通过 Windows 内核查询实际客户端 PID。Vivado 由本轮 `CreateProcessW` 创建的受控 `cmd.exe` 启动；固定本机 `vivado.bat` → `loader.bat` → `rdiArgs.bat` 的 `:RDI_EXEC_DEFAULT` 直接执行 `%RDI_PROG% %RDI_ARGS%`。监督器用 Toolhelp32 进程快照，在本次受控私有 Job 中查找映像路径与预期 Vivado 可执行文件完全匹配、且 `ParentProcessId` 精确等于受控 `cmd.exe` PID 的唯一子进程，固定其 PID 与进程句柄；管道客户端 PID 必须等于该固定 PID。验证时只使用已固定的进程句柄查询存活、进程 PID、映像和 Job 成员关系，不再按管道报告的 PID 重新 `OpenProcess`；进程句柄已退出时直接失败，即使后来有进程复用了相同数字 PID 也不能替代原进程。若受控启动本身就是 Tcl 可执行文件，则复制并固定 `CreateProcessW` 返回的精确进程句柄。目标缺失、多匹配、进程退出、父 PID/映像/Job 不符或快照查询异常，一律失败关闭，不按同映像或同 Job 降级放行。

唯一接受的摘要是目标进程通过管道写入的一条 ASCII 行：自报 PID 必须等于内核查询的客户端 PID，还须匹配本次 RunId，字段与 SHA-256 格式有效，且实际消息长度不超过 256 字节。仅完成上述验证后，监督器才接受文件数和树摘要。身份不符的首个连接立即被拒绝并关闭管道；本轮准备阶段失败，不重试或接受后续客户端。准备阶段 stdout 上出现摘要标记一律视为不可信并使整次准备失败。

较新 .NET 运行时使用 `PipeOptions.CurrentUserOnly`。Windows PowerShell 5.1 的 .NET Framework 不提供该选项，因此通过 `PipeSecurity` 设置受保护 DACL，只给当前用户 SID 授权；若运行时既无该选项也无法创建此安全 ACL，则不启动准备进程。Tcl 打开管道后短暂延时 250 ms，给服务端处理客户端身份核验的时间，再尝试写入一行并关闭；没有 ACK，且该延时不证明核验已完成。服务端只在独立验证通过后接受摘要；写入失败或身份/格式/超时错误均失败关闭，不回退 stdout。管道打开采用有限时长重试。

## 后果

- 监督器依据内核提供的 pipe-client PID，并将其绑定到本轮受控 launcher 的唯一、直接子 Vivado 进程句柄；验证期间复用该固定句柄并确认其仍指向原 PID、仍存活，同 Job、同 Vivado 映像的其他进程即便自报真实 PID也不能通过。原目标退出后，即便数值 PID 被复用，也不能通过已退出的固定句柄验证。
- 一次性单向协议符合 Vivado Tcl 的 Windows 管道行为；服务端不向 Tcl 返回确认。
- 同 Job 同映像 sibling 抢先连接仍可造成拒绝服务：该连接被身份校验拒绝、管道关闭、准备阶段失败；不自动重试，也不把它视为合法摘要。该失败模式须由 sibling 抢连端到端测试确认。
- stdout 中旧式摘要标记不能再被当作可信证据。

## 验证证据

- Windows PowerShell 7 与 Windows PowerShell 5.1 需分别执行监督器自测；真实 Vivado/Tcl 整合须核实内核客户端 PID 等于本次受控 `cmd.exe` 的唯一直接 Vivado 子进程 PID，且子进程 PPID 等于该 `cmd.exe` PID。
- 自测覆盖固定目标句柄退出后以同一数值 PID 验证时失败关闭；覆盖同 Job 同映像 sibling 使用真实 PID 抢连（包括真实 Vivado 同路径 sibling），并端到端断言准备阶段终态失败、`S3_RUNNER_RESULT` 非成功、route 启动回调未执行且已捕获失败状态不被公共异常处理覆盖。真实 sibling 的内核客户端 PID、Toolhelp 父 PID、受控 cmd PID及唯一绑定 Vivado PID分别核对，验证其父 PID 是主 Vivado、而非 cmd，且该连接被拒绝并使可信摘要验收失败。另覆盖非法字符/长度/行数/RunId、stdout 伪造标记与无客户端连接超时；无效认证不得产出可信摘要。原有 ACL 检查仅验证 DACL 结构/current-user SID 配置；**PS7 `CurrentUserOnly` 对不同 Windows 用户的实际拒绝连接行为未由本机自测验证**，不得把此结构检查描述为跨用户实测。
- Vivado Tcl 纯逻辑自测应报告实际执行项数；未执行或受授权阻断时不记为通过。
- 本次仅执行自测：没有运行综合/布局布线，没有生成 bitstream，没有操作板卡。阶段 3 的硬件 G0、板卡版本/端口最终绑定和后续路由诊断仍须按各自验收门推进。
