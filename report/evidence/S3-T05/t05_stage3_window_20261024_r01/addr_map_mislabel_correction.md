# `jtag_addr_map_read.tcl` MM2S 偏移错标更正（评审 N-3）

- **缺陷**：本窗口首版 `scripts/stage3_t05/jtag_addr_map_read.tcl` 把 MM2S 的帧地址/stride 标在
  `0x18/0x1C/0x20/0x28`，这些地址在本设计上读回**全 0**（并非 MM2S 地址寄存器）。
- **正确位置（本窗口实测）**：MM2S 通道 `VSIZE=0x50(0x000002D0)`、`HSIZE=0x54(0x00000F00)`、
  `STRIDE=0x58(0x00000F00)`、**帧地址 `0x5C(0x00110C00)`**（见 `mm2s_scan_final.txt`）。
- **对本窗口结论的影响**：**无**。地址事实（采集与显示共用 `0x00110C00`）使用的是
  `mm2s_scan_final.txt` 的 `0x50/0x54/0x58/0x5C` 与 `addr_scan_final.txt` 的 `0xAC`，
  **未依赖**错标的 `0x18..0x28` 读数。
- **更正动作**：`jtag_addr_map_read.tcl` 已改为读 `0x50/0x54/0x58/0x5C`，输出字段名同步更正；
  原始日志 `addr_map_final2.txt` **保持原样不改写**（失败证据保留），其 MM2S 标签按本文件说明理解。
