# R18 单独仿真补充运行

本Run使用 R18 超时构建目录中后来生成的 `Vtb_s2b_control_csr.exe`，没有重新编译。二进制 SHA-256 为 `7b34838e7f49761b108397ccb0140a83a4a867c3ac993e84e624df3fa8173185`。上游 R18 runner 的 360 秒编译超时和退出码 1 保持不变；可执行文件出现及本次独立运行不改变该状态。

本次命令为 `timeout.exe 60 ./obj_dir/Vtb_s2b_control_csr.exe`，退出码 1，约 1.46 秒。在 `late_exokay_r_after_first_error` 阶段、周期 5865、directed=140、random=128、integration=25 时，`read_reg` 的“读值或响应”断言失败。原日志没有输出失败地址、实际CSR值或预期值，故具体失败点和根因仍待定位；后续向量没有执行。

因此，本次结果为 **FAIL**。R18 G1 仍 BLOCKED，不能把证据包装器 `CHECKS_OK`、静态Reviewer PASS或构建目录中存在二进制解释为编译/仿真通过。没有实物操作；G3、G4和阶段2B验收仍未完成。
