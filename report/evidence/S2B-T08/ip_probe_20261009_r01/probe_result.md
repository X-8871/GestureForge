# S2B-T08 隔离 IPI 配置探针

基线 `3d424b9cc207e85375ef4f703ee193806c73bd34`；物理接口依据 `s2b-physical-candidate/0.1.1`，尚未冻结。本运行只检查配置和最小 BD 连接，结果不替代物理 adapter、完整控制路径、时序或实板验收。

已读回 PS GP0 为 AXI3、32-bit 数据、12-bit ID；HP0 为 AXI3、64-bit 数据、6-bit ID。GP0 转换器输入 AXI3、输出 AXI4-Lite，地址/数据均 32-bit，输入 ID 12-bit。FCLK0 与连接后的 ACLK 元数据均为 50 MHz。控制地址为 `0x43C00000` / 64 KiB；HP0 外接主设备地址空间是 `0x00000000` / 1 GiB，该可寻址范围不是 adapter 白名单，未来实现仍须限制到候选逐对象许可范围。

初次外部端口默认 100 MHz，验证报频率不一致；修正外部端口元数据后通过。补充地址分配后仍出现异步复位告警，最终通过 `proc_sys_reset` 在 FCLK0 域同步释放：FCLK_RESET0_N 接 active-low ext_reset_in，aux/debug reset 接 0，dcm_locked 接 1。FCLK0 来自 PS 而非额外 MMCM，常量锁定只用于这个最小探针；完整平台须重新核对时钟稳定及运行中复位条件。该 reset 是初始化通路，不是清空未排空 AXI 账本的恢复方法。

最终验收以 `reset_validate.tcldict`、`reset_connection_readback.tcldict`、`validated_probe.bd` 及完整 native 日志为准。保留此前配置 capture 失败、频率 mismatch、复位告警原件，不能把早期 Tcl rc0 或 FINALIZE_PROBE:OK 当作无 critical warning。

复位配置和 BD 保存成功后，归档因 `FILE_NAME` 返回相对名而失败；`archive_probe.tcl` 使用已核验完整 BD 路径重新打开并复制，不重新创建 IP。初次启动命令的宿主进程退出码未留存，日志明确记录归档 Tcl 错误，不能声称该命令整体成功。最终 archive 命令实际退出码为0；其中 `validate_bd_design` 因 BD 已验证而跳过，capture 只证明该调用完成，不是再次执行全部验证。真实复位验证来自 reset_validate capture；其无 ERROR/CRITICAL WARNING，Vivado 验证增加但未打印的 WARNING 计数仍原样保留，不称零 WARNING。

MCP 原会话失效，后续执行工具在恢复时未提供，采用本地 Vivado 2026.1 batch Tcl。原 MCP startup、native/proxy日志与批处理日志保留。旧 converter r2 capture 的 native_log_source 错绑到 r1 文件，窗口为空，不能单独据此判定无 native 错误；r2 完整 native 日志和最终独立 capture 另行核对。历史 PS/converter 脚本经过重试编辑，归档的是最后内容，不能声称完整恢复每次失败时的源码；原日志和 journal 保留历史执行事实。

`validated_probe_bd.tcl` 是 Vivado 导出的最终 BD 恢复入口；诊断脚本含本机已核验路径及原 RunId，不可原地重跑或覆盖证据，独立恢复应在新临时目录新建相同器件项目并导入导出脚本。插件 helper 属于外部安装依赖，版本和 SHA 记录在运行元数据中。

尚未执行综合、实现、位流、PL 下载、CSR/HP0 实板传输、缓存可见性及整网 deadline 验证。该结果仅证明最小 IPI 配置可连接，完整阶段2B G0/G3/G4/G5仍未完成。
