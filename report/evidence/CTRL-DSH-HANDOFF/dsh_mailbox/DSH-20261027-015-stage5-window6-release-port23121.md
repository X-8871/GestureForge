# DSH-20261027-015：第六窗口**释放回执（实际端口 23121）**

- 记录方：DSH 阶段5 总控｜时间（UTC+8）：2026-10-27T15:39:57+08:00｜性质：**hardware_release**
- 授权 `DSH-20261027-014`（Wong「现在上板吧」）；门控 `hw_gate_20261027_r10` = GO；**实际端口 23121**
- 部署成功（`S5DL_ALL_DONE=1`，未烧 QSPI）；新生成器行计划（23 段、边判据 8/8）转储 23 行段、解析 1812 像素
- 结果：**像素级未通过**（box0 21/172、
  box1 102/313）；应用自报颜色/几何**正确**
  ⇒ 成因收窄为**采样缓冲（只读 BUF0）或标签/HUD 覆盖**，非对齐、非 API 颜色
- 收尾：残留硬件进程 **['vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe']**；netstat 23121 行数 **1**
- 与阶段4 的关系：本轮期间 DSH 项目总控向阶段4 发出 `S4-B-REAL-02B` 硬件 OFFER（`DSH-20261027-001/002`）；
  阶段5 本轮为**授权窗口内短时占用并已释放**，未与其认领冲突
- 证据：`w5/report/evidence/S5-T01/s5t02_pixel_confirm_20261027_r01/`
- 边界：**§4.5/§7.3 未关闭**；八类门禁口径（4/8 vs 5/8）待阶段4 明确；板上真实回放 NOT_RUN
