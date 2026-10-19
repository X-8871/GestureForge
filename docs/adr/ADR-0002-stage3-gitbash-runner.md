# ADR-0002：阶段 3 诊断控制迁移到 Git Bash 与 .NET 守卫

- 状态：已采用
- 日期：2026-10-07（UTC+8）
- 范围：Stage 3 HDMI-only Vivado 离线诊断的启动、文件控制和路径守卫；不授权或描述板上操作。

## 背景

用户要求本机后续控制文件等操作使用已安装 Git Bash，不再使用 PowerShell。现有 T03 链路由 PowerShell 监督器启动 Vivado，Tcl 通过 PowerShell 完成安全文件 I/O，并在共享验证器中内嵌 PowerShell/C# 路径守卫。该链路还承担输出路径隔离、Windows Job 子进程树监管、超时/无进度停止、准备摘要认证、文件租约和元数据完整性校验；直接改用 Bash `timeout` 或普通文件命令会丢失关键安全语义。

## 决策

以 Git Bash 脚本作为唯一操作入口和文件/流程编排层；将 Bash 无法可靠提供的 Windows 内核能力保留在无第三方依赖的本地 .NET helper 中，包括 NTFS reparse-point/句柄校验、独占输出租约、Windows Job Object 子进程监管及命名管道客户端身份验证。Vivado Tcl 通过该 helper 执行受限安全文件操作与路径守卫，不调用 PowerShell。helper 的构建产物和单次诊断的所有运行输出均写入 `tmp/s3r04/` 下本轮新建的唯一目录。迁移完成后，旧 PowerShell 实现不再是活动生产入口；任何保留的历史或对照代码不得由活动调用链执行。

迁移不得弱化下列约束：输出必须是 `tmp/s3r04/` 的新直接子目录；源码快照提交与清洁状态须精确匹配；准备阶段摘要必须绑定受控 Vivado Tcl 进程身份；Vivado/其后代必须处于本轮专属 Job；硬超时为 60 分钟、无进度停止为 15 分钟；未通过准备完整性和路径守卫不得进入 run；不生成 bitstream，不连接或操作板卡，不干预 Batch109。任何不确定或失败均失败关闭。迁移完成后，旧 PowerShell 实现不得再作为活动生产入口或后备路径。

## 后果

- Git Bash 负责稳定、可审计的本机控制入口；.NET helper 仅实现 Bash/Tcl 无法安全替代的 Win32 原语，避免依赖 PowerShell。
- helper 必须在无外部包、无网络的条件下构建；构建、中间文件、日志和诊断结果不得写到授权运行目录外。
- 旧模式的有效路径守卫回归与 T03 监督器测试须独立通过；仅有 Bash 语法检查或静态检查不构成等价性证据。
- 独立 Reviewer PASS 后才可执行此前已授权的一次 HDMI-only 诊断；若实现不能保留任何安全不变量，不得启动 Vivado。

## 验证要求

- 静态扫描活动 T03 调用链，确认不调用 `powershell.exe`、PowerShell 脚本或其他 Shell 代跑路径。
- 使用本机 Git Bash 与 .NET SDK 验证构建、路径守卫原有模式及失败关闭场景；测试输出只能位于隔离的 `tmp/s3r04/` 子目录。
- 冻结实现哈希并通过独立只读审查后，才允许一次正式受控 HDMI-only 实现诊断；最多运行 60 分钟，连续 15 分钟无进度即停止。
