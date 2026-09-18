# S1-T02-D4-W5 官方 full 权重来源核验 r5

- 结果：真实来源字节核验 exit=0；此次运行证据待独立 Reviewer 复核，不能据此关闭阶段1。
- 运行版本：Git HEAD `1544af144dc1f5de89e99bb7446d97eb450383a1`；工具 SHA-256 `B0E5C37E9B454AEC3ACFC22BA1925E4D504476F5DB08431C387DF6CA172E18D0`；测试 SHA-256 `1B96B7F0C2FF192F941F29AE0C50D59FED1D3F0C491D4FBA5B5A2E4E7484C650`。
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe D:\FPGA_Competition\report\evidence\S1-T02\s1_t02_d4_w5_stream_hash.py --execute-network-request`。
- 运行时间：`2026-09-18 12:50:41` 至 `2026-09-18 12:51:31`（UTC+8），报告 elapsed=`49.969` 秒。
- 在线结果：request attempts=`2`，confirmed GET=`2`，HTTP responses=`2`，状态码=`302→200`，redirects=`1`，最终状态=`200`。完整流式响应 `170038676` 字节，Content-Length=`170038676`，encoding=`identity`，SHA-256=`11c5286cfbffabc9a3059927401ab3480e9483ceafd3265779a0dc26c769bed0`，匹配固定来源摘要=`True`。响应正文未落盘。
- 本地绑定：本次开始/结束快照均为 `170038676` 字节、SHA-256 `11c5286cfbffabc9a3059927401ab3480e9483ceafd3265779a0dc26c769bed0`，mtime 纳秒值均为 `1789571365490508200`；stable=`true`，matches_remote=`true`。单独的依赖 metadata 行注明 `previous_read_only_measurement`；本次 `local_weight_binding.before/after` 提供了本次读取和稳定性证据。
- 依赖绑定：共 `16` 条记录，其中固定 W1–W4 依赖 `15` 项（11 项内容哈希/大小，4 项基线缺失状态）全部 matches=`true`；另有且仅有1条 full-weight metadata 记录。许可证=`UNRESOLVED`；不作许可法律结论。
- 原始捕获目录：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_w5_full_weight_provenance_r1_retry01`。`stdout.jsonl` SHA-256 `9A0BDC5551BF6622CAF20C8F6B95367674530FD042D88511BAA39AE3DDC18110`，大小 `5801` 字节；`stderr.log` SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`，大小 0 字节；`invocation.txt` SHA-256 `9C4338DB6D7616C3983E1D50B672DB5C91862901D358C424EAC358886A9AE637`。
- 规范 JSON SHA-256 `768022D56BDE61F4B7B24623B76CE0C0AB3EDEA0252A6AFB4B7D1B6E72FE6FC8`，文件 `20260918_s1_t02_d4_full_weight_provenance_r5.json`。
- 限制：此结果只证明运行时 HTTPS 流式对象摘要与固定预期及本地权重快照相符；许可证仍 UNRESOLVED，不代表精度、INT8、资源、G3/G4 或阶段验收通过。