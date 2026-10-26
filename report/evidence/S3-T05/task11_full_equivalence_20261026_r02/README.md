# task-11 G0 比较契约定案与启动阻塞记录 r02

结论：**比较口径已由总控确定；完整顺序等价仍为 `BLOCKED_NOT_RUN`，task-11 未通过，阶段 3 G5 未通过。** Wong 将缺失的比较口径交由总控决定。本记录固定拟执行边界，但不把契约选择等同于 G0 放行或等价证明。

## 已确定的比较契约

1. **比较对象**：对同一 patched `alinx_ov5640` IP 封装进行完整 RTL 与对应 OOC 功能网表的顺序等价比较。按实例化 XCI 参数 `BUFFER_DEPTH=2048`、`DEBUG_OV5640=false` 配置 RTL；不得使用 RTL 默认深度 4096 冒充当前网表配置。
2. **输入和输出边界**：参考与实现侧所有 top-level 外部输入施加同一输入轨迹；比较全部 top-level 可观察输出及控制信号。全量静态端口映射见 `port_mapping.json`，包括 `cmos_d[9:2]` 到 8-bit `cmos_d`、18 位 FIFO bundle、AXIS、未使用/裁剪端口。配置实例的 `m_axis_video_tready` 按 XCI `driver_value=1` 绑定为 1；不设内部 cutpoint，不假定局部中间状态或 cut-input 逐拍相等。
3. **双时钟关系**：`cmos_pclk` 与 `m_axis_video_aclk` 是两个无固定相位关系的独立时钟输入。参考与实现接收相同的两条时钟轨迹，但不对两时钟之间增加同步、同相或固定频率比假设；验证引擎必须支持该异步多时钟比较。
4. **初态、复位和厂商原语**：按实际 Vivado/XPM/UNISIM 网表及模型版本中的 INIT/GSR 和 FIFO/复位同步语义建模。静态映射显示外部 `m_axis_video_aresetn` 未接入内部网表核，RTL 数据通路也未消费该端口；内部 `cmos_aresetn` 由 `cmos_pclk` 计数逻辑产生，极性转换后连接内部原语。不得把外部 `m_axis_video_aresetn` 误当作内部 FIFO 复位，不得强制内部状态相等、改写原语行为或凭空补充复位脉冲/持续时间。任何引擎必需的合法复位前提必须从绑定的模型与设计连接中逐项给出并纳入假设清单。
5. **通过判据**：需要覆盖全部合法可达状态并给出完整、非有界截断的顺序等价结论；无未解释 black box、unsupported primitive、被忽略输出、未关闭分区或仅有界/仿真结果。保留全部假设、分区映射、工具版本、license/执行日志；同时证明非空有效轨迹以排除 vacuity。反例必须按唯一 RunId 完整保存。

## 当前阻塞（不是 G0_PASS）

- 没有可用 SEC 引擎绝对路径或 license 状态；此前只读盘点未发现可用的 Yosys/SBY/EQY/求解器或 Formality/Conformal/Jasper 环境。未安装、下载或启动替代工具。
- 既有 OOC XCI 已记录参数 `BUFFER_DEPTH=2048`、`DEBUG_OV5640=false`；RTL/XCI/网表的 12 个封装端口及内部 18 位 FIFO 映射已静态列出，但 `build_report.json` 没有生成源码提交号。OOC 输入同版来源、XPM/UNISIM 模型版本、复位/INIT/GSR 状态语义绑定仍未完成。
- 所以该契约已定，**工具/输入身份关口未满足**；证明命令不运行，task-11 继续 `BLOCKED_NOT_RUN`。旧局部 SOF 穷举和静态阈值译码结果不升格为完整 task-11。

详细已有输入清单与候选工具盘点见 `../task11_full_equivalence_20261026_r01/README.md`、`result.json` 和 `manifest.json`。本 r02 只记录比较契约决定与未闭合启动条件，不改写旧 RunId，也不修改 RTL、XCI、网表、工具或缓存。
