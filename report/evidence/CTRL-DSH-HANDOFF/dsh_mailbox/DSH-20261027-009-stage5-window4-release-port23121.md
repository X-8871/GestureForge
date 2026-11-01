# DSH-20261027-009：第四窗口**释放回执（实际端口 23121）**

- 记录方：DSH 阶段5 总控｜时间（UTC+8）：2026-10-27T14:23:35+08:00｜性质：**hardware_release**
- 对应授权/占用：`DSH-20261027-008`；门控 `hw_gate_20261027_r07` = GO
- **实际端口：23121**（hw_server `TCP::23121`、TCL `localhost:23121`、资源检查 `netstat:23121` 三者一致）
- 收尾：残留硬件进程 **['vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe']**；netstat 23121 行数 **0**；未烧 QSPI
- 本轮成果：**像素对齐口径已由探针实证锁定**（字节0=像素x0、3 字节/像素、相位0、字内小端）⇐ 此前"未确认"的一半已关闭
- 仍存差异：box0（cls 0）边框实测为 class 1 颜色 ⇒ 嫌疑 `drawn[]`/`boxes[]` 索引对齐；**像素级仍 UNCONFIRMED**
- 证据：`w5/report/evidence/S5-T01/s5t02_pixel_phase_probe_20261027_r01/`
- 边界：**§4.5/§7.3 未关闭**；八类门禁 4/8；B5/B6/真彩目视/T5-10/板上真实回放 NOT_RUN
