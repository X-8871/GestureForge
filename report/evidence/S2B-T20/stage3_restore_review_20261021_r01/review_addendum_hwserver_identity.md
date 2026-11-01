# 复审补充：hw_server 身份参数化

- 结论：`PASS`（仅审查本次身份配置差异）
- 恢复脚本 SHA-256：`CB7B6D65958698E4A84DEB3C1D7E1D672BDA2839C96CC4E0A7E15AFB80245EB3`
- 复审范围：原通过版本 `84BD9AD81E818F0A450706E3CDF7FB6FC5E4C8DB5288FCB0E03321D167EF5E79` 后的 hw_server 身份参数化差异；其余结论继承主审查记录。

第18–19行将硬编码的 hw_server 身份改为从精确路径 `D:\FPGA_Competition\w2b\tmp\2B\hw_server_20261021.json` 读取。该文件包含 PID `28624`、预期 `hw_server.exe` 路径及创建时间 `134370593467506410`。读取通过 `r.exact_path` 和 `r.strict_json`；随后原有 `runtime.identity(config)` 在创建XSDB session之前，将配置中的PID、可执行路径、创建时间与实时快照比较，并要求3121监听归属该PID。身份不匹配会在连接硬件会话前拒绝执行。

本次差异没有增加对外部服务的启动、停止或重定向行为；复审未发现阻断项。没有独立重新采集CIM快照，也未运行脚本或连接硬件。
