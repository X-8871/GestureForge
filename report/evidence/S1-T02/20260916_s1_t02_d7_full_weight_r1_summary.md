# S1-T02-D7 完整 YOLOv4 PC 对照初始化权重绑定

状态：EXECUTED_REVIEW_REQUIRED；退出码：0；errors：[]。

本任务仅绑定官方 YOLOv4 backbone 初始化权重 `yolov4.conv.137`，不代表五类完成模型、正式训练、精度、最终模型选择或阶段验收通过。

## 来源与下载结果

- 稳定官方 URL：https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.conv.137
- README：`D:\FPGA_Data\darknet\README.md`；SHA-256：`9fc4a7ce8cd6be5221ce1811c5df20645bb12487e6cba11ca54876eaf3f021e2`；命中行：489、567。
- 下载开始（UTC+8）：2026-09-16T23:08:34.5359286+08:00。
- 下载完成（UTC+8）：2026-09-16T23:09:26.0334048+08:00。
- HTTP：GitHub 302 → release-assets.githubusercontent.com 200；最终主机：`release-assets.githubusercontent.com`；未保存临时签名 query。
- Content-Length：170038676 bytes；下载字节数：170038676 bytes；非 HTML 检查：PASS。
- 原子落位：PASS；临时文件清理结果：成功完成后不存在；失败路径清理：隔离受控失败测试 PASS。

## 目标权重

- 实际路径：`D:\FPGA_Data\darknet\weights\yolov4.conv.137`
- 实际 size：170038676 bytes。
- 实际 SHA-256：`11c5286cfbffabc9a3059927401ab3480e9483ceafd3265779a0dc26c769bed0`。
- 目标文件未删除、未重新下载；本轮未触碰真实目标权重。

## 源码与证据绑定

- 竞赛仓库 HEAD：`f30fa9c085b6811adede9b9c88373ffa86f21ad5`。
- 官方 Darknet source：`D:\FPGA_Data\darknet`；commit：`59596d7880f6504768df41d6daa586f5cb2b932f`；tracked diff 退出码：0；tracked source 未修改。现有未跟踪 build/weights 状态不纳入本任务。
- 下载脚本：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d7_full_weight_r1\download_official_yolov4_conv137.ps1`；SHA-256：`f7d9c37fcc812e8b4947d97d496ea53043572f14e06986408ede4a942db9b6ad`。
- 外部 download evidence：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d7_full_weight_r1\download_evidence.json`；SHA-256：`996aed130165ed8702a6a7988d9190dac4cda5468d9d3c3141fcb6acca3c5848`。
- 外部 download log：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d7_full_weight_r1\download.log`；SHA-256：`1915301dc438ba9380df54b3d92aacee4c5201eb91421690edd9af272feefa8e`。

## 离线修复验证

- JSON/UTF-8/敏感信息扫描：PASS；D7 文件中未发现临时签名 query、完整 release-assets query 或未脱敏重定向 URI。
- PowerShell AST 语法检查：PASS，退出码 0。
- 隔离失败路径测试：PASS，受控失败退出码 1；预置的隔离 `.download.tmp` 在 finally 后不存在；隔离目标未创建；未发起网络请求；脚本输出无敏感 query。
- 真实目标权重 size/SHA 校验：PASS，仍为 170038676 / `11c5286cfbffabc9a3059927401ab3480e9483ceafd3265779a0dc26c769bed0`。
- `git diff --check`：PASS。

## 未执行项

training：NOT_EXECUTED；evaluation：NOT_EXECUTED；mAP：NOT_EXECUTED；INT8：NOT_EXECUTED；Vivado：NOT_EXECUTED；板测：NOT_EXECUTED。
