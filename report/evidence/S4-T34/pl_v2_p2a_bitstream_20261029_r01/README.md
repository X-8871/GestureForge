# P2a：4-D 预处理 PL 首个位流（lead 执行，2026-10-29 10:30–10:50）

## 目的（范围声明）
验证 **PS↔PL 通路与 CSR**（长跑静默停住的根因方向），并首次把 **流水化 v2 引擎**做成真实位流。
**不做**：2B 推理合入（P2b）、输出流消费（VDMA/显示，属合并部署）、板上功能复验。

## 设计
```
PS7：FCLK0=100 MHz、M_AXI_GP0、S_AXI_HP0(64bit)
  GP0 → smc_ctrl → s4d_0/S_AXI   @ 0x43C10000 range 0x80   （控制）
  HP0 ← smc_data ← s4d_0/M_AXI_RD → DDR 0x0..512MiB        （数据）
  复位：FCLK_RESET0_N → proc_sys_reset → peripheral_aresetn
s4d_0 = RTL wrap（CSR + engine_v2 planA + 4KB 拆分 shim + AXIS 打包，AXIS 内部悬空）
```
RTL 版本 = 4 拍流水 + planA（`p_dy_inv_q` 前移），TB 等价已由 lead 复跑（cycles 2,655,174、FNV 一致）。

## 结果（真实退出码）
| 阶段 | 结果 |
|---|---|
| BD 创建 + validate + 地址分配 | exit 0（0 error / 0 critical） |
| synth_1 | 100% |
| impl_1 → write_bitstream | 100% |
| **时序** | **WNS = +0.087 ns、WHS = +0.095 ns、TNS = 0.000、失败端点 0 / 4,012**；`All user specified timing constraints are met.` |
| 时钟 | `clk_fpga_0` 10.000 ns（PS7 FCLK0 = 100 MHz） |
| 资源 | Slice LUT **1,428**（2.68%）｜FF **1,270**（1.19%）｜BRAM 0｜DSP48E1 **2**｜LUT as Memory 55 |
| bitstream | `s4d_preproc_p2a.bit` 4,045,777 B，SHA-256 `3ea14a8697e64c76a3627bbd87dc8e8cf4041a9d209a7bc472a28e68b5a59f89` |
| XSA | `s4d_preproc_p2a.xsa` 273,858 B，SHA-256 `25cb9729db186d194ee2cfd814a53b47cb8d4afac5f3ac1ed9c2d8391b6cbae8` |

⇒ **综合阶段 −0.279 ns 的负裕量在实现后转正**（+0.087 ns），此前"带记录性负裕量进 P2"的判断成立。

## 过程中修掉的两个问题（留痕）
1. **模块重名**：RTL wrapper 与 BD 生成的 wrapper 同名 `s4d_preproc_v2_wrapper` ⇒ 顶层选错、260 个调试 IO 变顶层端口、place 报 IO 超限。改为 `s4d_preproc_v2_wrap`。
2. **顶层 IO 未约束**：外引 M_AXIS 13 个端口无引脚约束 ⇒ bitgen DRC NSTD-1/UCIO-1 失败。P2a 将 M_AXIS 置内部悬空（输出流消费属合并部署）。

## 边界
- 离线构建，**未上板**；`ENABLE=0`；不主张 G3/G4/G5；
- 位流为 **preproc-only**，不含 2B 推理；输出流未引出；跨 4KB 拆分/CSR 保护仅在 RTL/TB 层验证。