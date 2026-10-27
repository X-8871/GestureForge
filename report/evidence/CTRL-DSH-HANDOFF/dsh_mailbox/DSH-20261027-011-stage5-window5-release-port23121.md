# DSH-20261027-011：第五窗口**释放回执（实际端口 23121）**

- 记录方：DSH 阶段5 总控｜时间（UTC+8）：2026-10-27T14:33:24+08:00｜性质：**hardware_release**
- 授权：`DSH-20261027-010`；门控 `hw_gate_20261027_r08` = GO；实际端口 **23121**
- 收尾：残留硬件进程 **['vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe']**；netstat 23121 行数 **1**；未烧 QSPI
- 本窗口成果：**取得应用自报地面真值**（box0 rgb=255,64,64 / box1 rgb=64,255,64；几何与生成表一致）
  ⇒ 绘制 API 边界颜色**正确**；并**定位第二个"未确认"来源**：转储行/列选择按旧版矩形，覆盖率仅 ~5%（测量链路缺陷）
- 结论：**像素级叠加仍 UNCONFIRMED**；下一步=按当前用例表自动生成行/列选择后复测
- 边界：八类门禁 4/8；**§4.5/§7.3 未关闭**；板上真实回放 NOT_RUN
