# S4B RAW 候选 DDR G0 只读审计

- RunId：`s4b_pl_ddr_g0_audit_20261023_r01`，报告最终核验时间：2026-10-23 23:02（UTC+8）。w4 从任务起始提交 `521ea60f880234918831bbfaf42e258acfdfebe0` 前进至并发提交 `4639501c7c0badeded139e9a2a76017ca8294adc`；地址图及r13关键文件SHA在提交后复核不变。
- 本轮冻结 XSA 精确绑定为 `D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.xsa`，SHA-256 `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`。R04生成输入提交为 `6f5c6dc871d92fe32e5d37a58ff693442b793903`；S2B-T18冻结提交为 `16ce2cdf8c00c6214435629d75a5e4b63acb66a9`；r13派生PS应用提交为 `b7aceb8e81fe297511d0581d43c08aabf7df46f9`。选择原因及文件 SHA 见 `audit.json`。
- 冻结 XSA 的 PS 初始化字段为 MT41K256M16TW-107、32-bit DDR、533.333333 MHz；HWH 对应 HP0 为64-bit、50 MHz。它们是静态配置，不证明实板装配或当前加载状态。r13 BSP 声明DDR软件范围 `[0x00100000,0x40000000)`。
- 候选 RAW `[0x12000000,0x12C00000)`（12 MiB），metadata `[0x12C00000,0x12C08000)`（32 KiB）。109个冻结样本按单RAW缓冲串行复用，最大单帧11,059,200 B，余量1,523,712 B，不需减少样本数。
- r13 app arena `[0x00100000,0x01100000)`，2B tensor arena `[0x10000000,0x12000000)`；RAW紧接tensor尾端，候选与已查PS/Tensor区无重叠。Stage3/W5历史三个显示buffer均在 `0x00114C00..0x00F95400` 范围内，不触及候选，且Stage3/video平台排除在本轮并发路线之外。
- 当前草案把 `[0x12000000,0x20000000)` 标为“专属窗口之外、不在本阶段准入范围”。未发现具体owner占用证据；这是策略限制，不等于DDR已被其他消费者占用。地址交叉表可送独立G0审查；物理DDR集成仍为BLOCKED。实板使用前需更新地址图、登记owner并解除blocked记录。
- 假设：Stage4不与Stage3/video共载、无其他DDR消费者、CPU1保持Stopped、未来实板任务拥有独占会话。审计没有读取硬件或验证当前设备状态；W5最终P1 ELF/map未保留在指定构建目录，详情及范围限制见机器报告。
- 未运行 Vivado、SDK、UART、用户脚本或硬件；未改业务源、文档、STATE、Git暂存或提交。w4 readiness文档在审计期间由他方并发修改；本报告未将其变动中的working-tree字节作为固定哈希证据。
