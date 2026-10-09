# S2B-T06 实板 PS 功能最终审查

独立 R13：PASS，283 项核查、207 次文件绑定。最终收据为 `review/final_review_receipt.json`，SHA-256：`83f2c9593b91b37704ee8d6af190fdfdae889860960dcd83752f09012017d341`。审查实际命令、退出码及日志哈希在收据中。

本目录按原字节复制审查收据、脚本与日志，映射见 `review_copy_mapping.json`。早期两轮 Reviewer 误断言原件保留；修正审查器后复核通过，被审业务包未修改。本次归档首次命令错误重复了一段收据 SHA 参数，校验立即拒绝，未创建目标目录；准确命令重试退出 0，详见 `archive_execution.json`。

实板结果入口：

- `../ps_jtag_retry_20261009_165853_r02/`：真实 PS 初始化成功及旧版 smoke；旧时钟诊断错误保留。
- `../ps_uart_clock_retest_20261009_172557_r01/uart_readable.txt`：新版实际 UART 原字节副本，23 行、16 模式、4,194,304 个 32 位 word、零错误。
- `../ps_uart_clock_fix_delivery_20261009_173128_r01/`：诊断字段修正、实际构建和永久交付证据。

新版复用前轮成功初始化，只下载和运行一次新 smoke。仅检查专属 1 MiB DDR；未做全容量、长期压力、UART RX 回环或实物时钟测量。此结果不代表完整阶段 2B G0/G4/G5 通过。
