# XC7Z020-2 同源 OOC 许可受阻记录

状态：`BLOCKED_LICENSE`。实际 Part `xc7z020clg400-2`，top `s2a_stage2a_core_ooc`。

14项隔离RTL源绑定与读取完成；源码从 commit `999238284157bed77cdb3a37e3e6eea52daeefc4` / tree `b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67` 恢复，与旧OOC字节逐项一致。顶层wrapper只有第59/137行显式恢复CRLF，历史SHA唯一匹配。共享src未被读取或改动。

实际 `synth_design` 在许可检查失败：Common 17-348报告Synthesis许可已过期，Common 17-345报告目标xc7z020的有效许可未找到；MCP/Tcl返回1。Tcl耗时 7 秒，MCP自报 6.535 秒；此次source调用1次，同RunId重跑0次。完整原文见 synthesis_failed_tool_result.json。

| 项目 | 本次真实状态 |
|---|---|
| 14项历史字节和隔离Python预检 | PASS |
| 实际目标器件唯一解析、14项RTL读取 | PASS |
| 全核心OOC综合 | FAILED，业务受许可阻碍 |
| LUT/FF/BRAM/DSP资源结果 | NOT_RUN |
| 广义/LDCE/LDPE锁存器检查 | NOT_RUN，latch=-1是未测哨兵 |
| 时钟风险/最差路径、环境等级、DCP | NOT_RUN |

r01失败原记录保留：独立Python被Vivado的PYTHONHOME/PYTHONPATH污染，出现SRE module mismatch，尚未读取RTL或综合。r02仅改用Python -I -B、source显式UTF-8和独立namespace，修复环境后如实暴露许可阻碍。

本次峰值内存和完整ROSS工具调用量未测；旧XA报告的资源或峰值内存没有当作新XC实测数据。历史批准文本以本目录精确快照和Git基线绑定，A板卡文档审计留在r01。

实际工具等级查询为 `ENTERPRISE`（返回0），它不能代替真实Synthesis许可checkout。用户尚未取得有效BASIC许可；下一步输入是有效Vivado 2026.1 BASIC许可的精确路径或许可状态。[AMD许可FAQ](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/licensing-faq.html)、[许可等级支持范围](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado/vivado-licensing-options.html)；官方说明与实际诊断绑定于 license_diagnosis.json。

原始执行窗口快照：vivado_session_execution_snapshot.log（SHA c1eeda743aa02c28353913cd42c0df9107d9e5478d26a9304c070acee14d59bb）与对应.jou（SHA 0605ca164064b8be7ae37a009b1d780f0d9da0b8cf5dac380e21707742e08421）。两者按unknown-8bit原字节保留；覆盖r01环境失败、r02许可失败与ENTERPRISE查询，捕获时会话未关闭，不能称全生命周期日志。捕获范围见 log_capture_record.json；UTF-8 MCP结果另存。

- 新XC器件OOC尚未完成；不能以旧XA综合资源计数代替本次结果。
- 资源、锁存器、时钟风险、工业等级设置和DCP均未运行或未生成，不能称PASS。
- 无XDC/冻结时钟；即使后续许可恢复并综合成功，也不能仅据OOC宣称时序或工业温度达标。
- 未修改许可文件或绕过许可；恢复执行须由主控先核对现有合法许可/工具等级，并使用新RunId。
- 本次没有实物操作、109样本整网重跑或修改原候选RTL。
- CHECKS_OK仅表示失败包绑定/包装完整，不代表业务PASS或G0/G4/G5/实物验收。
