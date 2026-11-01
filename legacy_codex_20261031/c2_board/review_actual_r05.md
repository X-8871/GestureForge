# R05 C2 实际运行独立复审

审查结论：**FAIL（整体 CHAINB/C2 集成未通过；推理、解码与发布子链取得部分成功）**。本审查只读源码和 R05 留存证据，没有启动硬件或改动被审源码、ELF、既有报告。

## 版本与证据身份

运行目录：`D:\codex-worktrees\w6\report\evidence\R05-C2\c2_real_20261101_r05`

- 实际 ELF：`artifacts\c2_real_chainb_display.elf`，1,345,984 B，SHA-256 `77BC9EE36CB6E9D0BA13F82043D7CBCF633A05C152ABC73F7E4CF62377F2292C`。
- UART 捕获：`uart.bin`，SHA-256 `7054793884D57DD29735F2C369E7A0EC21F3D3A74CB6D34103F7E832BBE8A85B`。
- 发布源码 `src/c2_s5_publish.c`：SHA-256 `DF23E8D33F1B6DD9F92DBDA4DA72FA02B505E3C03F3C91BCA60675F43F72CD0C`；应用源码 `src/s4d_ps_app.c`：`B295C476B3417BEA15A23356E2EFA7C747F70312EA290F32C6EC185EDC00B42E`。
- 显示调用源码 `src/c2_display_hook.c`：`0DDB20AB25D2A28FA983DCB3FF698D75D2838F6F0B5EB0917D8C149327660145`；VTC `src/vtc_ctrl.c/.h`：`8BA7D212B4F5D5EC2781BC84B9041CBE218DD935596644ACD72DE5BF532B6FA6` / `68D1555CD3A78AFF5D206A90229C1184CDD096B3C00F09B441ECB42C24162458`；VDMA 头文件：`543CBB9D070AF895E441E78D05A36AFCB960DAF184D5E99A79BE40CDEC95DFD3`。
- P3q XSA：`D:\tmp\lead\p3q_video_20261030_r01\out\s4d_p3q_r01.xsa`，SHA-256 `DFEFC883B0FE267CF8BFFC3F76B15067B9AB7ED99779670D661F8261907FE96D`。

上述 SHA-256 由只读 `Get-FileHash -Algorithm SHA256` 核算。源码位置、UART、编排结果、XSDB 脚本及 P3q HWH 以只读 `Get-Content`/`rg` 核查；检索和哈希命令成功返回。未重新编译或运行 host 测试。

## 已取得的正向证据

UART 显示：

1. fixture 写入 DDR 完成，来源明确是 `camera=0`，因此这是 RAW fixture 路径，不是真实摄像头采集。
2. SW preprocess 返回 `rc=0`，张量 CRC32 为 `0x5B183B50`，519,168 B。
3. PL 2B 返回 `done=1`，耗时 47,287 ms，`status=0x00000E04`、`error=0`；decode `rc=0,count=1,raw=2`，并输出一条检测。
4. 发布报告 `publish_rc=0`，SID 10359、seq 0、最终 seqlock 2、1 条 detection、status 1、business_state 3。软件随后对 result block 做 cache invalidate，并核对两次相同偶数锁、magic 和数量，得到应用内 readback 通过。

权重确实执行了独立 XSDB/JTAG DDR 读回：`program.tcl` 在应用启动前向 `0x10100000` 写入并读出 5,903,100 B；`weights_verified.json` 标记 `before_con=true`。留存读回文件 `weights_readback.bin` SHA-256 为 `F6FEB6D489318EE9774FC406E9222CD9B881FBE33A40F32362366CF38693CC39`，与本次 TCL 指定的权重源文件同长同哈希。这项权重 DDR 读回为 PASS。

## 阻断：显示阶段没有返回，整体链路失败

UART 在 `C2 PUBLISH RESULT` 行后结束；未出现 `C2 DISPLAY RESULT`、`CHAINB STEP=7 ACK` 或最终 `CHAINB RESULT`。外部运行器在最长 95 秒接收窗口后记录 `RuntimeError('inference/deadline timeout')`。因此：

- 推理、decode 和发布子链通过；应用内 result-block 局部读回通过。
- 显示服务没有取得返回码，ACK/idle 未执行，最终 `C2_IntegrationPass` 条件未满足；R05 编排 `orchestration_result.json` 为 `FAIL`。
- `readback\readback.tcl` 仅存在脚本，`readback\result_block.bin` 与 `readback\frame_a.bin` 不存在；XSDB 独立结果块/帧 DDR 读回是 **NOT_RUN**。UART 的软件读回不能替代 JTAG 读回。
- 没有 `C2 DISPLAY RESULT`，也没有物理 HDMI/scanout 观测。即便显示函数返回，源码也将 `physical_scanout` 明确标为 `NOT_VERIFIED`。
- `close.tcl` 的结果为退出码 0，确认 Cortex-A9 #0/#1 均 stopped/suspended；清理完成。它只证明 CPU 会话正常收尾，不证明应用完成。编排器最终 FAIL 来自 95 秒应用截止，不应归因于事后 close。取 PC 的 forensic 脚本未成功：XSDB 报 `no register match: r14`，所以没有 PC/调用栈证据。

## 显示挂起候选与平台映射

源码顺序是 `C2_DisplayOneFrame → S5Vtc_Init → VDMA`。`S5Vtc_Init` 在带 10,000 µs 复位超时的步骤之前，先直接读取 VTC version 寄存器；该读取本身没有软件超时。

本次 XSA 的 HWH 映射有 infer `0x43C00000..0x43C0FFFF`、s4d `0x43C10000..0x43C1007F`、AXI DMA `0x43C20000..0x43C2FFFF`、VDMA `0x43C40000..0x43C4FFFF` 和 GPIO `0x43C50000..0x43C50FFF`，没有 `0x43C30000` VTC 条目。源码却将 `S5_VTC_BASE` 固定为 `0x43C30000`。**这是可复现的平台地址不一致，也是显示函数未返回的首要排查候选；现有日志没有 PC，不能据此断言根因或断言 CPU 必然卡在该读操作。**

`S5_VDMA_BASE=0x43C40000` 与该 XSA 的 VDMA 映射相符。P3q HWH 将 DDR MEMRANGE 声明为 `0x00000000..0x3FFFFFFF`，覆盖脚本结果区 `0x20800000` 及帧缓冲区 `0x20000000`；HWH 同时声明 DDR capacity 为 `1024 MBits`。脚本使用 XSDB `loadhw -mem-ranges 0x00000000 0x7FFFFFFF` 是 XSDB 地址许可范围，不代表实际 DDR 容量变成 2 GiB。实际 DDR 容量和 P3q/Stage4 BSP 配置匹配关系仍是部署组合限制，不能把 P3q XSA 说成官方匹配的 1 GiB 平台。

时钟读回留存在 `program\launcher\stdout.bin`：FCLK0_CTRL `6292992=0x00600600`、IO_PLL `221192=0x00036008`。结合 HWH 的 FPGA0 外设时钟 50.000000 MHz 和 Zynq PLL/divider 字段，读回支持 FCLK0=50 MHz；不支持把本次运行按 133 MHz 推断。R05 的 GT 计数常数为 333,333,343 ticks/s。

## sidecar 与时间字段

结果块 sidecar 位于 `0x20800100`，32 B 头部字段为：

| 相对偏移 | 字段 | 本次含义/值 |
|---|---|---|
| +0x00 | magic | `0x53355831`（S5X1） |
| +0x04 | version | 1 |
| +0x08 | SID | 10359 |
| +0x0C | result seq | 0 |
| +0x10/+0x14 | result_time ticks | 64 位时间戳 |
| +0x18 | seqlock | 最终偶数 2；发布过程中先置奇数 1 |
| +0x1C | reserved | 0 |

Rev4 发布顺序是 odd-lock flush、288 B payload flush、最后 even-lock 4 B flush。Rev4 的 `result_time` 在 payload flush 之前取样，故它不是最终 even-lock flush 的完成时刻。UART 的 `flush_gap_ticks=850` 表示 receipt 事后读取的 GT 与该较早时间戳之差，按 333,333,343 ticks/s 约为 2.55 µs；这是误差/间隔 receipt，不能改称最终 flush 时间。应用 `age_pub_ms=0` 是毫秒取整后的读回年龄，不证明同一 tick 完成。

源码未发现 950 ms cutoff。可核到的两个业务阈值是：`C2_TIMEOUT_GT_TICKS` 按 GT 常数计算的 200 ms stale 分类阈值，以及显示层 `S5_AGE_LIMIT_MS=33` 的帧新鲜度阈值；它们都不是整网运行硬超时。R05 的 95 秒是 `operator_invocation.py` 的外部 UART/inference 接收截止。

## 收尾状态与待验证项

`orchestration_result.json` 显示 init/program/start 进程及语义退出码均为 0，应用截止触发后 close 退出码为 0，cleanup confirmed。之后板卡由 root 记录通过 POR 恢复；本审查没有再次操作硬件。

尚未通过/未执行：修正并冻结 VTC 基址或 XSA/BSP 映射后重新验证显示调用；最终 CHAINB ACK 与 pass；XSDB 独立读回结果 288 B 和帧缓冲；实体显示输出与物理 scanout；DDR 物理容量及部署 BSP/XSA 对应关系。不得把现有结果表述为完整 C2、HDMI 或官方平台验收通过。

