# S6-C 离线确定性矩阵封包摘要（s6c_deterministic_matrix_20261029_r06）

- 正式矩阵依据：`report/evidence/S6-C/s6c_deterministic_matrix_20261029_r06/inputs/formal_6c_runbook.md §4`，SHA-256 `697506c743ebc6618c68380a86ab80b62f263ad16dbceefb252f260c2392e89f`。
- 历史 S6-B r08 来源提交 `e735a5afb5b474793408ec1e61da111006c70e60`；其 26 条用例、固定输入、run_report 与 JSONL 日志已在隔离副本通过证据及严格哈希复核。核心 SHA-256 `8cf5c7f0e89110068a00894f764f65f8a4fc3df2c5db55d9f46f243f348995d9` 与当前一致；r08 历史测试 blob 与当前 HEAD `52dc7618153eed61f49f4bca116755dde7a56ac4` 的 blob SHA-256 `8c37e67b30cbad770249f0f0664dc328250c63f060b6ccfe67e19186b04781c3` 一致。
- r04 实际运行日志作为只读输入绑定：S6-B 回归 40 项、S6-C receipt boundary 17 项、C11 duplicate ACK 回放、freeze 及 `git diff --check`；本 RunId 不重跑这些命令。当前新增测试磁盘 SHA-256 `63cdb40865f257d9941fdbf83abbca1ed3c8be0575b2f0bf903de0a7349f73c0` 与 r08 历史测试字节不同，二者各自范围已分开绑定。
- 矩阵表逐项列出历史 26 条的预期、实际、窗口时间边界、固定虚拟输入时序、日志路径/哈希及断言；C11 duplicate ACK 单列为 r04 补充回放，观察到重复 ACK 不重复提交/生效，计数均为 1。
- 第 8 行与整体判定为 **BLOCKED**：已跑的 duplicate/reorder/missing/session-change 子用例通过；B25 同会话大回退阈值未批准，且 `0xFFFFFFFE` 边界的文档/机器规格差异未统一。不得把该行或整体验收标 PASS。
- U6-02 r07 批准回执 SHA-256 `f8b2cde23f11e132b7df62a7e60df6f6a5d560cf4b7d9a4efd464462b2ba7394`；重复 frame 结果按已批准的业务字段口径绑定，不比较接收时间等传输上下文。

本包未访问板卡、JTAG、串口、摄像头或 HDMI。G2 独立审查待进行；G3 未执行；T6-A03 因缺阶段4实测帧周期 P 保持 NOT_RUN；6-E 实物验收未执行；阶段4/5真实结果链路仍 BLOCKED；不声称 G4 或阶段6 G5 通过。
