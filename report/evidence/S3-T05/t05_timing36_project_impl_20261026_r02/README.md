# TIMING-36 隔离工程修正与实现验证 r02

## 结果

在全新隔离工程副本中，只修改本地 `vendor_src/my_ip/rgb2dvi_v1_3/src/rgb2dvi_clocks.xdc` 及其生成副本 `rgb2dvi_clocks.xdc`：删除 `PixelClk → SerialClk ×5` 这一条 generated-clock 约束。随后 `generate_target all` 从本地 IP repository 重新生成目标；副本源码与生成 XDC 均保持为同一 27 字节内容。Vivado 完整 reset 并重跑综合、implementation/route，之后接续 bitstream generation。

- 综合：`synth_design Complete!`，100%；implementation：`route_design Complete!`，100%；bitstream generation：`write_bitstream Complete!`，100%，外层进程退出码均为 0。
- 路由方法学汇总：TIMING-36/30 各从基线 1 降为 0；SerialClk 端口仅关联 `I=2.000 ns` 自动时钟。
- TIMING-17=240、TIMING-18=1、TIMING-9=1 保留。DRC 汇总 8 项全为 Warning。
- STA 摘要：WNS=1.055 ns、TNS=0/21479，WHS=0.059 ns、THS=0/21344；但 `check_timing` 仍有 `no_clock=240`、`unconstrained_internal_endpoints=520`、`no_input_delay=9`、`no_output_delay=5`。因此“用户指定 timing constraints met”只适用于当前已约束路径；这不是完整时序签核。
- 候选 bitstream：临时工程中 `design_1_wrapper.bit`，SHA-256 `6b23e209effd55a440447c59608f76bbb03cd4f06b3832f0777843cc54a67b01`，大小 1,668,969 字节。只生成、未烧录、未做板上验证。

该结果验证了目标约束行在隔离工程完整综合和路由后可去除 TIMING-36/30，且保留真实 2 ns SerialClk。它还不是已提交的正式工程修复：输入工程和 IP repository 是既有 `tmp/s3r06` 的副本；本次没有修改可复现的正式项目构建入口。r01 的脚本查询失败记录单独保留。

## 固定输入与输出身份

- 原 routed DCP（基线参考，不作为 r02 重新综合的输入）：SHA-256 `17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728`
- 原 XPR：SHA-256 `f7606f5b3a53a852b88f3494c35e552aaa3861a7270b71354e8e9a73796c2087`
- 原 BD：SHA-256 `89af040079575324c649265703a8bb3fa4e582d96ed88f442a8753a9df29324a`
- 原 IP 时钟 XDC：SHA-256 `e6ceadc3fcfcf59fe1f5eaf13f8f94d862e9513ad6cd2e850a035c312c8d2002`
- 新 routed DCP：SHA-256 `e5f5a429a1eff9e6602f3bca92cefdcca562f1ee39a8e2a0aba0351c58562a84`
- 路由导出的 XDC：SHA-256 `0d1d8a3f161baad7fe8ca2a48d69f1a9029f26f0e42f1258960f774b162e8676`，不含该错误约束行
- Vivado：2026.1 Build 6511674；器件 `xc7z020clg400-2`；BASIC 许可证（未读取许可证内容）

## 复现与边界

在项目工作树根目录执行 `run_project_impl.tcl`，随后执行 `run_bitstream.tcl`；两者均固定到本 RunId 的隔离项目副本。`validate_implementation.py` 对原始输入哈希、两个候选 XDC、运行状态、报告摘要、STA 缺口与 bitstream/DCP 哈希作断言。

为避免证据清单依赖 Vivado `.srcs`、`.gen`、`.runs` 生成目录，`outputs/` 保存了输入 BD 与基线 routed DCP 的精确副本，以及本次 Vivado 打开后的 XPR、生成 XDC、路由 DCP 和 bitstream。验证脚本同时逐字节核对归档副本与隔离工程中的原文件；临时工程仍保留在 `tmp/3/S3-T05/t05_timing36_project_impl_20261026_r02/` 作为复现环境。

启动时 Vivado 报告原项目 BoardPart 未找到，并提示一个 XCI 内容已变化；目标 Part 仍为 XPR 的 `xc7z020clg400-2`。本次未修改 `D:/FPGA/AX7Z020`、主目录、正式工程源文件或板卡。TIMING-17/18、I/O delay、task-11、VDMA bit11 根因、板上身份/颜色/运行期地址复核仍开放；阶段3 G5 仍未通过。
