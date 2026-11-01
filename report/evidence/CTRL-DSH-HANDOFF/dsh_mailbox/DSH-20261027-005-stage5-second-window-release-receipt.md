# DSH-20261027-005：阶段5 第二窗口**释放回执**（像素级复核）

- 记录方：DSH 阶段5 总控｜时间（UTC+8）：2026-10-27T13:38:43+08:00｜性质：**hardware_release**
- 对应占用授权：`DSH-20261027-004`
- 收尾实测：硬件进程 **['vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe']**；3121 LISTENING **0**；**未烧 QSPI**（易失下载）
- 本轮结果：**地址根因已修**（应用实报 `S5_P1_BUF0=00138C00`）；正确地址下缓冲中**已见类颜色字节**（叠加有绘制）；
  但期望与转储的**对齐口径未证明**（颜色匹配 80/82、46/87）⇒ **像素级叠加判 UNCONFIRMED**（不夸大、不判通过）
- 证据：`w5/report/evidence/S5-T01/s5t02_pixel_overlay_recheck_20261027_r01/`
- 下一步（离线即可）：锁定 `x0`/字边界的对齐口径 → 重算期望 → 合成转储 PASS/篡改 FAIL → 再上板一次复测
- 边界：**§4.5/§7.3 未关闭**；B5/B6/真彩目视/T5-10/板上真实回放仍 NOT_RUN
