# 阶段 3 HDMI 软件编译诊断（2026-10-07）

## 结论

HDMI-only 补丁涉及的三个 C 文件已用 Vitis 2026.1 自带的 Cortex-A9 GCC 13.4.0 完成目标文件编译，`-Wall -Wextra` 无警告、退出码为 0。可复核命令轨迹与输出保存在 `tmp/s3r05/vitis_hdmi_compileonly_official_xc7z020_minus2_20261007/compile_only_objects_reverified/compile_reverify.log`，对象文件在同目录。此结果使用临时占位 `xparameters.h`/`bspconfig.h`，只证明源码可通过当前驱动头文件的语法与代码生成；不构成真实 BSP 编译/链接、可启动 ELF、硬件适配、bitstream 或板测证据。

本轮仍不能交付可上板镜像。已授权的一次 Vivado T03 诊断在综合阶段因 `xa7z020` 的 Synthesis 授权不可用而失败；Vitis 2026.1 从随厂商例程提供的旧 XSA 未识别任何处理器或 OS 域，无法生成 BSP。

## 证据与边界

- 目标器件为 `xa7z020clg400-1I`。受控 T03 运行记录 `tmp/s3r04/t03_hdmi_impl_20261007_userauth_02/run_status.txt` 为 `FAILED_AT_SYNTHESIS_RUN_WAIT`，Vivado 日志报告没有适用于 `Synthesis`/`xa7z020` 的有效许可。`opt_design`、布局、布线、时序签核均未开始；该目录内没有 `.bit`、`.bin` 或 `.mcs`。本次用户授权为单次诊断，已使用，不据此自行重跑 Vivado。
- 可用的厂商 HDMI 软件例程 XSA 来自固定官方源码提交 `fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327`，由 Vivado 2023.1 生成，标注器件 `xc7z020clg400-2`；它与本板 `XA7Z020 -1I` 不同，只作为离线软件探针，不能作为本板下载输入。
- Vitis 2026.1 的 XSA 平台导入在隔离工作区创建了平台目录；目前仅工作区 `vitis_workspace_03/hdmi_compileonly_platform/vitis-comp.json` 留有清单，显示 `processorsMap: {}`、`supportedOS: []`、`domains: []`。当前磁盘上工作区 `vitis_workspace_02/` 没有 `.xsa`、`.bit` 或 `vitis-comp.json`。未保存添加 `ps7_cortexa9_0` 域时的原始控制台错误，因此本记录不引用其错误原文；现有证据只确认没有可用处理器/OS 域清单，也没有 BSP、应用构建或链接产物。AMD 的 2026.1 文档说明该软件平台支持 Zynq 7000，并支持从 XSA 创建平台；本次导入结果的具体原因尚未查明。[平台概述](https://docs.amd.com/r/en-US/ug1400-vitis-embedded/Vitis-Unified-Software-Platform-Overview)、[从 XSA 创建平台](https://docs.amd.com/r/en-US/ug1400-vitis-embedded/Creating-a-Platform-Component-from-XSA)
- 当前仅工作区 `vitis_workspace_03/hdmi_compileonly_platform/hw/sdt/design_1_wrapper.bit` 留有旧 `design_1_wrapper.bit`；SHA-256 为 `c4574dc7477ba814e721711089ad79c14ffa626c98a9da9473f3346944649c1c`，与 XSA 同名成员一致。它是原 XSA 的解包副本，不是新生成的 bitstream。没有运行 Vivado 实现、下载、烧录或操作板卡。
- 备用交叉编译使用临时夹具 `tmp/s3r05/vitis_hdmi_compileonly_official_xc7z020_minus2_20261007/compile_only_fixture/`：`XPAR_AXI_DYNCLK_0_BASEADDR` 来自旧 XSA HWH；设备 ID、CPU 频率及 `bspconfig.h` 是只为源码编译设置的占位值/空配置，并非生成 BSP。三个对象文件在 `compile_only_objects_reverified/`；未链接 `libxil` 或生成完整应用。

## 下一步门槛

等待 Wong 提供更新后的 Vivado License Manager 状态截图及官方 `AX7020_V3.0_User Manual`（目录 `D:\FPGA_Competition\摄像头资料\官方资料`）。收到后先核对 Basic/Enterprise 对目标器件的有效授权与板卡修订、视频接口，再准备匹配 `XA7Z020CLG400-1I` 的硬件平台/XSA。由于之前的一次 Vivado 授权已消耗，任何新的 Vivado 实现运行需 Wong 重新明确授权。当前尚未到可上板步骤，不索要板卡照片。
