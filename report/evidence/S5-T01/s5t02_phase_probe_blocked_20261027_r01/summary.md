# S5-T01 相位探针上板尝试：**主机端口绑定阻塞**（未改动板卡状态） RunId `s5t02_phase_probe_blocked_20261027_r01`

## 1. 结论
- 第三窗口（Wong「均可以」，门 `hw_gate_20261027_r05` = **GO**）**未能完成上板**：
  `hw_server` 在本机无法绑定监听端口 ⇒ xsdb `connect` 失败。
- **失败发生在 `CONNECT` 阶段**（序列：CONNECT → PS_RESET → FPGA_PROGRAM → PS7_INIT → DOW → RUN）
  ⇒ **本次未执行 PS_RESET / 未编程 PL / 未下载 ELF**，**板卡状态未被改动**。
- 不是板卡、代码或授权问题：**授权已 GO**、探针 ELF 已构建并绑定哈希（`s5_probe.elf`）。

## 2. 实测诊断（真实输出）
| 尝试 | 端口 | 结果 |
|---|---|---|
| 官方脚本（自起 hw_server） | 3121 | `Cannot create listening port tcp:127.0.0.1:3121: Socket bind error.` → `T03_DL_FAIL=CONNECT:` |
| 自起 hw_server + 端口可覆盖 TCL | **3131** | `Cannot create listening port TCP::3131: Socket bind error.` → `S5DL_FAIL=CONNECT:` |

`netstat` 对 3121/3131 **无任何条目**（无 LISTENING/TIME_WAIT）；硬件进程残留 **['vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe', 'vivado-mcp-server-windows-amd64-2026.9.1.exe']**。
⇒ 两端口**都**绑不上、且无可见占用者 ⇒ 指向**主机级条件**（Windows 保留/排除端口范围、`winnat` 服务状态、
或 socket 耗尽），而非某一个端口被独占。

## 3. 建议的解除办法（需 Wong 或管理员侧执行）
1. `netsh int ipv4 show excludedportrange protocol=tcp` 查看是否覆盖 3121/3131（含动态范围）；
2. 若覆盖：`net stop winnat` → `net start winnat`（或重启）后重试；
3. 若为 socket 耗尽：结束长期占用套接字的进程 / 重启主机；
4. 若确认是**其他写入方占着板卡会话**（本机不可见），请在信箱协调后再开窗口。

## 4. 本窗口内仍完成的事项（离线，不依赖端口）
- **相位探针已实现**：`s5_render` 在动态映射模式下于缓冲行 0 起始写 `53 35 44 4D 01 02 03 04`
  并在像素 1 写已知色 `11 22 33` ⇒ 下一次转储可**实证**定位字节↔像素边界（离线相位扫描已排除"简单相位"假设：三种相位最高仅 0.254 匹配率）；
- 端口可覆盖下载 TCL：`scripts/stage5_t01/jtag_download_port.tcl`（忠实复制官方步骤顺序）；
- 探针 ELF：`s5_probe.elf` SHA-256 见 `console/inputs_sha.txt`。

## 5. 边界
- **未改动板卡**；**§4.5/§7.3 未关闭**；八类门禁 **4/8**（阶段4 文档已核）；
  B5/B6/真彩目视/T5-10/板上真实回放仍 **NOT_RUN**；像素级叠加仍 **UNCONFIRMED**（待探针转储定案）。
