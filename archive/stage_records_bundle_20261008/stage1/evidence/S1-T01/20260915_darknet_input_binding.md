# S1-T01-D3 官方 Darknet 输入绑定证据

## 范围与边界

本记录只固定外部数据到官方 Darknet 的输入绑定，不启动 Darknet 训练、不生成权重、不修改官方源码、不把图片、标签或大清单复制进 Git。由于官方 `D:\FPGA_Data\darknet\src\utils.c:275-299` 对当前 `dataset/...` 路径不执行 COCO/PascalVOC 的目录替换，图片同目录 `.txt` sidecar 是实际运行所需的标签接口。

## 冻结外部产物

- manifest：`D:\FPGA_Data\HaGRIDv2\manifest.csv`，158680 行，SHA-256 `FD60E7A67161F242276A1B97B09AD07C0D7F41D30067266BB99620ABE6D7ED74`。
- `D:\FPGA_Data\HaGRIDv2\darknet_inputs\train.list`：118001 行，SHA-256 `4d8e965e7fc3f5d8a9f1ec3613fadb72c50b8463f78feebf863fd26978c8e3fa`。
- `D:\FPGA_Data\HaGRIDv2\darknet_inputs\valid.list`：15195 行，SHA-256 `8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c`。
- `D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names`：严格五类顺序，SHA-256 `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`。
- `D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.data`：classes=5、train/valid/names/backup/saveweights/savelast 完整，10>5>0，SHA-256 `379e02c6a68ccea896f5f16375879d0a52b698a66bd05dfcc7eba66c2068e3c8`。
- `D:\FPGA_Data\HaGRIDv2\darknet_inputs\binding_check.json`：准备摘要，SHA-256 `bea2ee6ef160254f0eca5d7e35c84c50ae9a81d6e561cba2fd6f524d274191a9`。

Sidecar 现态：158680/158680 存在且与 manifest label 逐项匹配，冲突 0；空标签 2165、非空标签 156515、总字节 7356346；manifest 顺序标签总 SHA-256 `53ead6cdc59fde6e801b34cb87c7d41c5e7ad2c8c4c6b4318632663b579542b4`。新增 5 张 no_hand 的同目录 sidecar 均为 0 字节。

## 独立复审

Reviewer 在隔离临时目录只读重算 manifest、六项 SHA、全量 sidecar、train/valid 集合与顺序、names/data 解析及官方映射，未修改受审文件或切换分支；验证退出码 `0`，结论 `PASS`。原始审查摘要：`C:\Users\22061\AppData\Local\Temp\review-d3-4d7e865621cc403aac29dabe20c46284\S1-T01-D3_independent_review.json`。

Reviewer 说明：`created/existing` 的历史 provenance 不能仅由当前后态重建；可复核现态为 158680 个 sidecar 全部存在且内容匹配，conflicts=0。该限制不改变当前输入绑定结论。

## 结论

D3 输入绑定达到本任务自动与独立审查标准；外部产物仍不属于 Git 交付物。该结论不等于 CUDA/Darknet 环境、小样本训练/恢复/评估或 S1-T01/阶段1通过。
