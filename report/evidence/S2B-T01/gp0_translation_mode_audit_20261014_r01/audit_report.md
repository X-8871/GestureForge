# AXI GP0 AXI3 到 AXI4-Lite 静态配置审计

日期：2026-10-14（UTC+8）

任务：S2B-T01-G0

RunId：`gp0_translation_mode_audit_20261014_r01`

## 结论

绑定的 T19 XSA/HWH 静态证据确认，`/axi_gp0_lite` 是 AXI3 到 AXI4-Lite 的 protocol converter，SI/MI 地址和数据宽度均为32 bit、ID宽度12、`C_IGNORE_ID=0`，`C_TRANSLATION_MODE=0` 且 `TRANSLATION_MODE=0`。PS `M_AXI_GP0` 的4-bit `AWLEN`、`ARLEN` 端口分别连到转换器 `S_AXI` 对应端口。

这份静态配置要求AXI3侧master满足single-beat前提，但HWH连线不包含实机事务的 `AWLEN`/`ARLEN` 运行值。PG059说明 `TRANSLATION_MODE=0` 是Unprotected模式，转换器期望SI上所有事务均为single-beat（`AWLEN=0` 或 `ARLEN=0`）。因此不能声称当前配置会把burst拆成Lite访问；对于不满足此前提的输入，当前材料也没有证明转换器响应或Lite侧副作用。

HWH显示GP0、转换器及 `rst_fclk0` 同接PS `FCLK_CLK0`，标称50 MHz；PS `FCLK_RESET0_N` 接入 `rst_fclk0.ext_reset_in`，`peripheral_aresetn` 扇出到转换器 `aresetn` 与 `infer.cold_resetn`。这些是静态拓扑信息，不是实板reset波形、释放时序、READY背压、响应或事务记录。

**G0结论：不通过，候选保持 `CANDIDATE_NOT_FROZEN`。** 尚需实测或以可复核事务跟踪证明GP0单拍前提，并覆盖响应/背压与适用reset边界。静态配置核验不能单独作为冻结依据；本任务没有更改转换器配置、RTL、板卡或Vivado运行态。

## 绑定对象与来源

| 对象 | 来源/版本 | SHA-256 |
|---|---|---|
| 本次审计工作树HEAD | `5bf43ff7bdad4a8d795456539b7a7573b1314ff9` | Git commit |
| 候选文档审计前字节 | 任务输入基线 | `5866547c88b60fbfa977d68c037fa117f7bbfda4e1c2ad0aaf15df200bc3d03c` |
| 候选文档审计后字节 | 当前工作树 | `69de8697f2b4d2f49fe5925a8985a71937a28a9b4848c9f793feb91e481816d9` |
| `src/s2b_inference_top.sv` | 当前HEAD工作树 | `dffd20728b6a3b88c9c4a0c63987e10460a54728f5e348ccf1f8182e78c859c1` |
| T19 visibility=1 XSA | `report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/artifacts/s2b_inference_wrapper_current.xsa` | `90f8d0b9e857f8beb9d99a6264b96441f9ba9b4b0af0568dbbcc064aecba6065` |
| XSA内嵌 `s2b_inference.hwh` | 原始XSA成员；本包另保存解出字节 | `67e5af631d346d16640bafbd262af7a33bda0236f1a950e632c2e05c90681370` |
| T19来源清单 | 原始visibility=1运行清单 | `0f32ff262d24dc49ff66e65d38653c27b0aaf53fffb263def51cf927412ca1ad` |

本次实际工作树HEAD是 `5bf43ff7bdad4a8d795456539b7a7573b1314ff9`；T19原始运行清单记载平台源提交 `f92823f0bd577a49db543868f44c4f63b670d8e0`。两者分别作为审计工作树版本和XSA来源记录，不混为同一提交。当前HEAD的 `src/s2b_inference_top.sv` SHA-256与T19 `sources/s2b_inference_top.sv`快照及T19清单声明值一致。

## HWH静态核查

| 核查项 | HWH所示结果 | 证据边界 |
|---|---|---|
| 转换器IP | `/axi_gp0_lite`，`xilinx.com:ip:axi_protocol_converter:2.1` | XSA内HWH的静态IP描述 |
| 转换接口 | `S_AXI`: AXI3/32-bit/ID12，连接 `ps7_M_AXI_GP0`；`M_AXI`: AXI4-Lite/32-bit/ID0 | 端口/接口元数据，不是动态事务采样 |
| 转换模式 | `C_TRANSLATION_MODE=0`，`TRANSLATION_MODE=0`；`C_IGNORE_ID=0` | 实际绑定XSA配置值 |
| `AWLEN`/`ARLEN` | PS GP0 4-bit LEN引脚分别连接converter `S_AXI` 4-bit LEN引脚 | 有静态连线；没有事务值、VALID/READY握手或波形 |
| 时钟 | `FCLK_CLK0` fanout含GP0 ACLK、HP0 ACLK、converter `aclk`、`rst_fclk0.slowest_sync_clk`、`infer.clk`，HWH标称50 MHz | 不证明板上实际频率或运行时钟质量 |
| reset来源与扇出 | PS `FCLK_RESET0_N`→`rst_fclk0.ext_reset_in`；`slowest_sync_clk`来自FCLK0；`peripheral_aresetn`→converter `aresetn`及`infer.cold_resetn` | 不证明实际断言/释放时序及reset重叠波形 |

完整机器提取位于 [`hwh_extract.json`](hwh_extract.json)，提取出的原始HWH位于 [`s2b_inference.hwh`](s2b_inference.hwh)。`extract_hwh.py`可从绑定XSA重新提取并断言关键接口、模式、LEN连线、时钟与reset扇出；它只做离线读取。

## 文档依据与解释

- AMD [PG059：Conversion to AXI4-Lite](https://docs.amd.com/r/en-US/pg059-axi-interconnect/Conversion-to-AXI4-Lite) 说明AXI4/AXI3到AXI4-Lite的常规转换可处理single-beat或burst；其中Unprotected模式用于只访问single-beat事务的well-behaved master。此配置的具体mode值另由HWH绑定为0。
- AMD [PG059：Protocol CONVERSION Options](https://docs.amd.com/r/en-US/pg059-axi-interconnect/Protocol-CONVERSION-Options) 对mode 0要求转换至AXI4-Lite时SI所有事务均为single-beat，即 `AWLEN`/`ARLEN=0`；其mode 2拆分不兼容burst的描述范围明确为AXI4-to-AXI3，不能套用为本AXI3-to-AXI4-Lite路径会拆burst。若以后改变转换器配置，需重新评估Lite侧可见事务序列及控制寄存器副作用边界；本任务未改参数。
- AMD [PG059：Resets](https://docs.amd.com/r/en-US/pg059-axi-interconnect/Resets) 要求每个 `aresetn` 与对应 `aclk` 同步，converter/基础设施连接两端reset须重叠，不支持partial reset。HWH连接只能核对拓扑，不能证明这些动态条件在实物上成立。
- AMD [UG585 v1.15：Device and Strongly Ordered](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Device-and-Strongly-Ordered) 描述Device/Strongly Ordered访问的数量与大小保持、不可未对齐及不执行推测访问。候选中的 `Xil_SetTlbAttributes(CSR_BASE, DEVICE_MEMORY)` 与对齐的32-bit `Xil_In32`/`Xil_Out32` 是软件/ARM访问映射的静态依据；它们不等同于PS→GP0引脚事务观测，也不证明当前板上实际请求为 `AWLEN=ARLEN=0`。

## 命令与工具记录

| 命令/观察 | 结果 | 原生退出码 | 耗时/说明 |
|---|---|---:|---|
| `python -B report/evidence/S2B-T01/gp0_translation_mode_audit_20261014_r01/extract_hwh.py` | `PASS_STATIC_EXTRACTION_ONLY`；XSA/HWH SHA与任务绑定值一致 | 0 | 命令执行0.869 s；由Bundled Python 3.12.14运行 |
| `python --version` | `Python 3.12.14` | 0 | 系统Python启动器指向不存在的路径；本任务显式将`python`命令映射到Codex Bundled Python |
| `vivado -version` | `vivado: command not found` | 127 | 当前审计环境无PATH可用Vivado；原始T19清单记载生成来源使用Vivado `2026.1 build 6511674`，本次未重新运行Vivado |
| `git diff --check -- docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md` | 无空白错误 | 0 | 0.357 s；仅检查本任务的已跟踪候选文档差异 |

证据目录清单包装核验命令及其最终原生退出码记录在 `delivery_manifest.json` 的 `checks` 中。检查器的成功只表示本包文件绑定/目录枚举符合清单，不代表AXI语义验证、G0、G3或实物验收通过。

## 未覆盖项

- 没有捕获实板PS GP0事务或AXI波形，未观察 `AWLEN`/`ARLEN`、READY背压、响应或协议异常行为。
- 没有测量实板FCLK频率和reset断言/释放/两端重叠时序；没有运行Vivado。
- 没有修改AXI Protocol Converter参数、RTL、candidate版本/语义、板卡或Vitis/Vivado运行态。
- 本任务未运行仿真、综合、部署或其他完整回归；未执行独立Reviewer审查，交由总控继续G2审查。
- G0仍不通过，物理接口候选未冻结。
