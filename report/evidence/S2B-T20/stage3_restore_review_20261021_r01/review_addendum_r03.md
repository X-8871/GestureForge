# R03 恢复脚本增量审查

- 结论：**PASS（静态审查）**
- 被审脚本：`D:\FPGA_Competition\w2b\tmp\2B\restore_2b_after_stage3_20261021_r03.py`
- SHA-256：`8B88ECC8FE32FBD3AD0A835C55CF81A42324BCA611FC1BEC9F52A8F4BB0B9D41`
- 审查范围：R03 静态控制流、其固定 R02 结果与哈希、阶段3交接状态、映射生命周期/清理；未运行脚本，未连接或操作硬件。

## 核验依据

- R03 固定引用的 `restore_result.json` SHA-256 与实际文件一致：`2fca8c0593ef737a5b5ec24bebcecba522c4154ee5af987f55f4c186483e8d8d`。内容记录两个 VDMA 通道均为 `HALTED_RUNSTOP0`，视频映射已 `UNLOADED_AND_SDK_MAP_EMPTY`，`cleanup_errors` 为空；该次失败发生在后续 CSR 映射注册的既有会话状态门禁，未部署2B。
- R03 固定引用的 `jtag_result.json` SHA-256 与实际文件一致：`9e1c5176788d2a16618fbb9ce638cf22dc5b5edc414ee76bb9d33b2198813f04`。实际记录 system reset 后 `boot_mode=0`、CPU0 PC=`0xFFFFFF28`、CPU1 PC=`0xFFFFFF34`，并有 `after_system_reset` 的 EOS `0` / `PASS` 观测。
- R03 逐字读取 `D:\codex-worktrees\dbdf\.codex\STATE.md` 最后一行并要求 `OFFERED / DSH 阶段三总控`。审查时末行满足该条件，状态文件 SHA-256 为 `2fbc580cf600b58db7c3659eafca76a739ab0b5fa6df7bd7da1ffe24c5d95975`。

## 静态结论

R03 在复用 R02 的已验证停止/EOS0事实后，创建并核实本次 XSDB session，再检查 CPU 停止、boot mode、EOS 和复位后 PC；仅当 PC 仍与固定 R02 结果相符时才执行本次 system reset 和2B部署。R02 的视频映射会话已结束；新 session 在 R03 中只经过目标选择、状态/PC读取、配置状态读取和 system reset，之后才进入固定 CSR helper 的映射门禁，控制流没有在该 session 上预先加载其他 XSA，也没有篡改 SDK 私有映射字典或放宽 helper 门禁。

成功路径仍使用原 controller 的已审部署与 app-stop/CSR IDLE 检查；异常路径保留 `FAILED_RESTORE`，对已触及的 CPU 尝试 fail-stop。finally 中先关闭 controller（该操作只清理其自有断点，不断开 session），再由 pinned helper 卸载本次尝试的 CSR 映射，最后断开 session 和 XSDB；卸载及 disconnect 异常均进入 `cleanup_errors` 并使退出码为2。脚本标记 `RESTORE_ONLY_NOT_ACCEPTANCE`，没有把恢复行为计为验收。

因此该 SHA 的静态审查通过，可由总控按已授权恢复流程决定是否运行。PASS 不代表 R03 已运行、板卡恢复成功或2B验收通过。
