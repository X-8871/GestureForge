# T13 平台候选构建 r03

本Run基于提交 `f971ff9cf842e3ebd852d36e832f301845fd56a3`，并在 `source_snapshot/` 保存Vivado XPR列出的18份实际SystemVerilog输入及平台脚本、元数据、接口文档和checker。各快照按运行时字节计算SHA-256；其中 `src/s2a_network_descriptor_pkg.sv` 与基线提交内容不同，清单绑定实际快照哈希。控制CSR实际哈希为 `4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1`。

Vivado 2026.1会话PID 24236已正常关闭，原生日志退出码0，构建耗时71.367秒，返回 `INFERENCE_PLATFORM:BUILD_CANDIDATE_OK`。结果是visibility=0的Block Design与no-bit XSA候选；未运行综合、实现或生成bitstream。XSA SHA-256：`0607120b1733ee17582ab0c508c366fca7b1f49d32afffe87a070a346df04252`。可将本Run明确绑定的该XSA及清单用于后续Vitis BSP build，不继承旧XSA。

静态checker退出码0，输出 `PLATFORM_STATIC:OK visibility=0 rtl_sources=18`。`products.tcldict.helper_raw`原始状态为FAIL：native WARNING累计数由9降至1，helper计算出emitted=-8、导出2条WARNING，故报告捕获不完整；原件保留。针对原生日志字节片段的独立reconciliation为2 WARNING、0 CRITICAL WARNING、0 ERROR，结果见 `products.tcldict.native.log`，不覆盖helper原FAIL。validate记录 `native_counts_before=2`、`native_counts_after=9`、`unprinted_warning_count=7`，但切片日志未打印对应7条WARNING，内容未知，按限制保留。

PS配置中DDR `MT41K256M16TW-107` 来自开发板手册输入，不证明实装料号或PCB/电源/时序绑定。该产物无bitstream，不是综合/实现、板上、G0或阶段验收证据；须按正式冻结入口继续验证。XSA、Vivado会话日志/Journal、原捕获字典和必要源码快照均在本Run目录内绑定。
