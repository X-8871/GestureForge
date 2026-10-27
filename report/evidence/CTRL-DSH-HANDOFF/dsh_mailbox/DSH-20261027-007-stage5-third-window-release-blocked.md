# DSH-20261027-007：第三窗口**释放回执**（主机端口阻塞，未上板）

- 记录方：DSH 阶段5 总控｜时间（UTC+8）：2026-10-27T14:08:47+08:00｜性质：**hardware_release**
- 对应授权：`DSH-20261027-006`
- **未上板**：`CONNECT` 阶段失败（`hw_server` 无法绑定监听端口），**未执行 PS_RESET/FPGA_PROGRAM/DOW**
  ⇒ **板卡状态未改动**；残留硬件进程 **['vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe']**；3121/3131 无 netstat 条目
- 实测：3121 → `Socket bind error`；换 3131 自起 hw_server → **同样 bind error** ⇒ 主机级条件
- 建议解除：`netsh int ipv4 show excludedportrange protocol=tcp` 核对保留范围；必要时 `net stop/start winnat` 或重启
- 本窗口离线产物：相位探针（缓冲魔数 `53 35 44 4D 01 02 03 04`）、端口可覆盖下载 TCL、探针 ELF
- 证据：`w5/report/evidence/S5-T01/s5t02_phase_probe_blocked_20261027_r01/`
- 边界：**§4.5/§7.3 未关闭**；八类门禁 4/8；像素级叠加仍 UNCONFIRMED
