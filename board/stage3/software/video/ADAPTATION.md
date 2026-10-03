# S3-VAXIS-01：厂商 AXI4-Stream 背压适配

## 固定输入与差异

参考缓存固定在提交 fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327。单路和双路 alinx_ov5640.v 都必须是 Git blob 1c43d5a28bc1904b452dec80e5eab5803ba9cdab，且缓存工作树字节与该 blob 一致；准备脚本在任何复制前逐项核对。

仅作两处 RTL 替换：

- TVALID 由 FIFO 非空与同步后的 fifo_ready_maxis 决定，不读取 TREADY。
- FIFO rd_en 等于 TVALID 与 TREADY 的握手。

其他 RTL、复位、像素拼接、采集时序和调试参数不在补丁中。厂商原始字节只复制到本次唯一 tmp 运行目录的 vendor_original；适配副本、输入来源及 SHA-256 记录在 source_manifest.json。此目录外不复制厂商文件，Git 中不含厂商原始 RTL 或寄存器表。

## 运行

从仓库根目录用 PowerShell 执行：

    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/s3_test_video_axis.ps1 -RunName <唯一运行名>

运行名只含英文字母、数字、下划线和连字符。运行目录必须不存在；准备文件、编译产物、波形/仿真数据和日志都写入项目 tmp 下的该目录。每个 Vivado 工具调用默认限时 120 秒，可用 TimeoutSeconds 参数调整。脚本仅接受以下工具路径：

    D:\Xilinx\2026.1\Vivado\bin\xvlog.bat
    D:\Xilinx\2026.1\Vivado\bin\xelab.bat
    D:\Xilinx\2026.1\Vivado\bin\xsim.bat

runner 在编译前检查本次准备清单、固定提交、单路/双路来源 blob 与 SHA，并再次计算实际传给 xvlog 的适配顶层和像素拼接模块哈希。结果文件记录每条工具命令、进程退出码、超时状态、日志路径及哈希；只有 xvlog、xelab、xsim 均以退出码 0 结束且仿真 PASS 计数满足要求，整体才报告 PASS。

仅验证进程退出码采集策略（不调用 Vivado、不创建运行目录）：

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s3_test_video_axis.ps1 -ValidateExitCodePolicy

自测覆盖 launcher 退出码缺失（含读取错误与无读取错误）、launcher/sentinel 不匹配、匹配 0 与匹配非零。launcher 退出码缺失或读取失败时，即使 sentinel 为 0 也必须拒绝 CAPTURED，并保持接受的 exit_code 为空。

## 验证范围与限制

仿真编译真实的厂商 alinx_ov5640.v 适配副本和真实 cmos_8_16bit.v。仅 XPM FIFO 以同一时钟的 FWFT 仿真模型替代；模型提供 FIFO 首字直通、空/满判断和握手弹出计数，不模拟异步 CDC。测试台只为跳过长启动计数而强制内部复位释放及 fifo_ready；复位功能本身不作为测试对象。测试实例将 DEBUG_OV5640 设为 0，以免引入厂商 ILA 仿真库。

测试经真实厂商像素拼接与顶层管线积累多拍，检查 TREADY 为 0 时 TVALID 保持、TDATA/TLAST/TUSER 稳定、没有 FIFO 弹出；恢复 TREADY 后逐拍核对顺序和弹出数量，并检查 FIFO 空时 TVALID 为 0。比较基准取自同次运行期间进入 FIFO 的数据，不验证像素格式或传感器图像语义。

本测试不覆盖传感器像素格式、I2C、真实复位行为、跨时钟 CDC、真实 XPM 实现、实际板卡时序、HDMI 输出、持续运行或硬件行为。无 Vivado 综合、实现、bitstream 或烧录步骤；主机仿真 PASS 不等于板级验收通过。
