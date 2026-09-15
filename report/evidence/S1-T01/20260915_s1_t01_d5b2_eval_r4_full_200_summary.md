# S1-T01-D5B2-FULL-R1 全量 valid 评估摘要

## 结论

本次为流程与输出闭环验证，不作最终精度阈值结论。官方 Darknet 单进程 `detector test` 已通过 runtime stdin 清单读取全部 15,195 张验证图，生成完整 JSON、JSONL 和逐图 JSON。workflow 报告状态为 `EXECUTED_REVIEW_REQUIRED`，退出码为 0；未设置 mAP 下限或精度门槛。

## 时间与命令

- 启动/进入 Darknet：2026-09-15 20:17:18（UTC+8）
- Darknet 完成：2026-09-15 20:46:12（UTC+8）
- workflow 输出收尾：2026-09-15 20:47:24（UTC+8）
- cwd：`D:\FPGA_Data\darknet`
- source commit：`59596d7880f6504768df41d6daa586f5cb2b932f`
- 命令：

```text
D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe detector test D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture_eval_r2.data D:\FPGA_Data\HaGRIDv2\darknet_inputs\configs\gesture_yolov4_tiny_416_short.cfg D:\FPGA_Data\HaGRIDv2\darknet_inputs\diag_s1_t01_d5b2_200\backup\gesture_yolov4_tiny_416_diag_200_200.weights -dont_show -out D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5b2_eval_r4_full_200\evaluation.json
```

## 输入绑定与哈希

- Darknet exe：`358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`
- 评估权重：`ba3ba3bff1b12c0f3b5b23df9c5fb22ea9744eeb05f78ea1fe109ccc73671017`
- 项目 cfg：`76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`
- external data cfg：`ff9e3d1a2b43de9d70a1884f6181c6d0a495713575ed7331712c7ea1e1d93d3e`
- names：`5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`
- source valid.list：`8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c`
- runtime_valid.list：`14604d2313c6bdbdb206ae979f60d7681ffc8ed27ccd2ad5191985ae631c4f60`
- manifest：`fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`
- dataset report：`9b2e4336e30ab49dfd4dfcfa4c9363be8ab82ec13f9fe80c55d8a3412b3277be`
- dataset approval：`90f37987de1cea597515926115fe064ed20df3f83f40ca45a04b41b86c0da213`
- environment report：`fa5e1265b0106d1e7357b18f387fc1c5d5dc9f3ce623f1a33734f1021de43d11`
- workflow：`5ead5ca061f1b41f3124d7e3865398065be7d13bfd1e6a6ddbbed152d6382e04`

runtime 清单共 15,195 行，每行由 `_darknet_cli_path(source valid.list 对应图片)` 生成，并经 canonical-resolve 逐行同序绑定；source 清单未修改。

## 输出与审计

- 报告：[20260915_s1_t01_d5b2_eval_r4_full_200.json](D:/FPGA_Competition/report/evidence/S1-T01/20260915_s1_t01_d5b2_eval_r4_full_200.json)
  - SHA-256：`843ed924af2b6799b75eed57fe799c8dba232409b2188bea07a11e1ee04d12e8`
- 原始 run-dir：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5b2_eval_r4_full_200`
- evaluation.json：3,947,295 bytes，SHA-256 `31d1979458293e2026b98ceefd3d986686851902d8cbcb9a9e28f2d75a84e4e4`
- evaluation.jsonl：10,357,804 bytes，15,195 条，SHA-256 `44ab2dc4c26fe2193010c4777c71bc5c1d6c69c6446db9ff1ffd105653c0a220`
- detections：15,195 个逐图 JSON，总计 5,284,313 bytes；首文件 SHA `d7dfbb83f0d81e743a2d0695f859890213e3d969db0abfce44505dc48e93020a`，末文件 SHA `ed7b647bf4c14b085c72543473a38d9992770f8a3b032bee20958e4685be73a2`
- evaluate.log：3,308,501 bytes，SHA-256 `baf5740a33e173ae11f75a8e0cd95dfa39f6fa1e4689a237a69ef7815751f2e9`
- `frame_id`、filename canonical 绑定、class/name、score、坐标和 objects 数组：全部通过
- Wong 批准 no_hand：friend_004 对应 valid 第 15,194 条，`box_count=0`、`objects=[]`
- OOM/NaN/Inf/损坏/STOP_RE：未观察到

## 限制

本证据证明的是官方 workflow 的全量执行与结构化输出闭环，不证明 mAP、召回率或最终部署精度；原始大型输出保留在 D 盘 run-dir，不复制进 Git。Developer 未提交 Git。
