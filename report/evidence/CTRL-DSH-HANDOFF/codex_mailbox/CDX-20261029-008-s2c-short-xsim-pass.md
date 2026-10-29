# CDX-20261029-008：S2C 短 XSim 查表测试已通过

- 时间：2026-10-29（UTC+8）
- 新身份：`D:\FPGA_Competition\w2c`，`codex/stage2c-throughput`，提交 `ece3ede9639942639da3272f6f67e2aaa85b734f`。
- 新 RunId：`D:\FPGA_Competition\w2c\report\evidence\S2C-RTL01\tile16_20261029_04\`。
- 真实命令：`D:\Xilinx\2026.1\Vivado\bin\xsim.bat s2c_rtl01_tile16_lookup_sim -runall`；进程退出码 `0`，日志有 `PASS S2C-RTL01 RTL查表` 与正常 `$finish`；7项确定性断言覆盖 layer0、layer35 完整/边缘 tile 与 generic8/frozen16 参数区分。
- 严格 hash_basis 校验：退出码 `0`、3项、0失配。原始日志在隔离 `tmp` 目录，不列为 manifest 项；日志 SHA-256 见 `result.json`。
- 独立 Reviewer 对该证据和文档状态更新判 `PASS`；范围仅限短查表测试。

仍缺完整帧 cycles、与 2B 冻结 head13/26 和框逐位等价、100 MHz 综合 WNS 与资源实测；当前不具备 ≥80% 把握，不提出上板验证请求。先前 `tile16_20261029_03` XSim 自动审批 HTTP 403 的失败记录保留，本次经同一审批入口获准后实际执行。
