# S2B-T19 visibility enable pre-review candidate

本目录把当前平台0.1.15源码映射、visibility=0的HP路径原件、T15固定PS/BSP/MMU构建原件和T19缓存先验实板原始观察绑定在一起，供pre-enable独立G2审查。

## 候选结论范围

- HP结论来自Vivado 2026.1读取的`visibility=0` postroute DCP；它不替代`visibility=1`新网表、实现/时序和独立审查。
- CPU/DAP交叉缓存探针实际只覆盖`0x10000000`起始的256字节（64 words），未运行模型；它不证明32MiB全区或整模型缓存一致。
- 生命周期只按受控DAP system reset→OCM初始化→完整PL重配置→应用/探针→停核序列表述。保留原记录`cold_lifecycle_proven=false`；不声称物理POR、断电冷启动、DDR全清零或DBG_RST新上升沿。
- 两份子证明及总proof将必要check记为PASS仅表示已有原件支持这些有界主张。`visibility_proof.json`明确处于`AWAITING_INDEPENDENT_G2`，未启用visibility=1。

## 当前状态

官方静态源码映射覆盖33项。尚未为本包生成独立review receipt；不得据此启动visibility=1平台综合或实板全模型验收。完整模型、T18、T20及G3/G4/G5尚未完成。
