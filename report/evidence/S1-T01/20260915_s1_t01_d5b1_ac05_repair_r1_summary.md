# S1-T01-D5B1-AC05-REPAIR-R1

状态：`EXECUTED_REVIEW_REQUIRED`；本摘要对应新的 stateless-SGD 隔离诊断，不覆盖旧 r1。

## 结论

选定并完成可复核路线：复制官方 Darknet 源到 `D:\FPGA_Data\darknet_ac05_debug_r1`，只在副本的 `convolutional_kernels.cu` 对 GPU 原始 `weight_updates/bias_updates/scale_updates` 逐层逐步扫描有限性；诊断 cfg 保持 YOLOv4-tiny 416、5 类、原 anchors/预处理，仅设 `momentum=0、decay=0、adam=0、max_batches=12`。因此没有需要持久化的 momentum/Adam 缓冲，旧有 stateful r1 不被改写或冒充通过。

训练命令实际运行到 1--12 步，并在第 10 步保存候选 checkpoint；恢复命令从未改动的第 10 步 checkpoint 独立继续 11--12 步。恢复日志显示 `seen 64`、`trained: 0 K-images (0 Kilo-batches_64)`、`Done! Loaded 38 layers`；恢复起点 10 由命令参数和 checkpoint 文件名绑定。训练与恢复原始更新扫描的 nonfinite 均为 0，权重 payload 均为有限值，恢复后模型参数发生有限变化。

## 证据入口

- 主报告：`D:\FPGA_Competition\report\evidence\S1-T01\20260915_s1_t01_d5b1_ac05_repair_r1.json`，SHA256 `cbecaed68b65a1f3b1ff42565b7b45ab1b6a6c5888e3e5a8f669ffabaaeb17e5`。
- 梯度/权重机器证据：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\ac05_repair_r1\runs\ac05_gradient_finite_evidence.json`，SHA256 `164a69a18dc7f332520f134ecba632a08a1b68debefbe6094addf62a2e50d2fc`。
- 语义澄清 v2：`D:\FPGA_Competition\report\evidence\S1-T01\20260915_s1_t01_d5b1_ac05_repair_r1_semantic_clarification_v2.json`，SHA256 `bb9c1c1191797eb0afadc779804ed140e73343f0a72c620d8d20bacad36856b5`；仅 metadata clarification，旧 approval SHA `90f37987de1cea597515926115fe064ed20df3f83f40ca45a04b41b86c0da213` 不变。
- 训练日志：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\ac05_repair_r1\runs\train_exec\train.log`，SHA256 `505857e1b98c0d7668f7a6a6c72d398ea916385a4df522ceffd11d2072ea181f`。
- 恢复日志：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\ac05_repair_r1\runs\resume_exec\resume.log`，SHA256 `6c4043003404914cf598ac1daa717db49a96f14c3acb3552370007cc97aa6191`。
- 训练 `_10` checkpoint：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\ac05_repair_r1\backup\gesture_yolov4_tiny_416_stateless_12_10.weights`，SHA256 `dc00c45cbe4bbb38ea5c225143af34b6db05425011c974f9ce65416e0b692845`。
- 恢复 `_12` checkpoint：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\ac05_repair_r1\resume_backup\gesture_yolov4_tiny_416_stateless_12_12.weights`，SHA256 `adc4a4eeef5c2ada560d87d47674146345d43491804998c7aff9b67c9603b4bd`。

## 输入与版本绑定

- 官方源：`D:\FPGA_Data\darknet`，本地 HEAD `59596d7880f6504768df41d6daa586f5cb2b932f`；源工作树 `git diff --quiet` 退出码 0。
- debug exe SHA256 `c1a3f7ed46477600f0041ace75dd1e5c8c19b91e8e7a3b29f79eb66ac9231c9d`；patch 文件 SHA256 `479197043fb8aaf7087f732dabd7f9aa4102fdea5e01ba9b1e0e62139c0568ee`。
- 诊断 cfg SHA256 `fb1a6209d4917739907756113e70852a425a51c2a434789c86cf66df2f31edd3`；固定项目 cfg SHA256 `76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`；训练 data SHA256 `610e2ec228661b5b5d7b67ef336b6853840e8751f633553dd61abcedfdf0cd82`；恢复 data SHA256 `2dbfc27db9c38e711d5d26e19c5f5c854bd639ef8fa6eb9b91b198ae3b57bc44`；固定 gesture.data SHA256 `379e02c6a68ccea896f5f16375879d0a52b698a66bd05dfcc7eba66c2068e3c8`。
- manifest SHA256 `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`；dataset report SHA256 `9b2e4336e30ab49dfd4dfcfa4c9363be8ab82ec13f9fe80c55d8a3412b3277be`；approval SHA256 `90f37987de1cea597515926115fe064ed20df3f83f40ca45a04b41b86c0da213`；names SHA256 `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`。
- valid/train/backup 仅通过隔离 `.data` 配置绑定；原始清单、标签、manifest、旧 approval 和旧 r1 报告未改写。

## 命令与退出码

- CMake configure：退出码 0；Release darknet build：退出码 0。
- 首次配置 preflight 因 `saveweights=1、savelast=1` 被 workflow 以退出码 2 拒绝，未启动训练；该失败报告保留。修正为 `saveweights=2、savelast=1` 后真实训练退出码 0。
- 训练：官方 argv 为 `darknet detector train data cfg initial_weights -dont_show`，cwd 为官方源根，退出码 0，观测 1--12 步。
- 恢复：官方 argv 为 `darknet detector train resume_data cfg checkpoint_10 -dont_show`，cwd 为官方源根，退出码 0，观测 11、12 步。PATH 只在进程及子进程临时加入 pthread/CUDA 目录。

## friend_005 语义

Wong 提供并授权内部项目使用的 `friend_005` 是真实风景/空场景负样本，不是人物肖像；无可见手，标签为空，manifest row 158681、val、role=no_hand，图像 SHA 与原 approval 一致。该澄清不把任何 `no_gesture` 重新解释为 `no_hand`。

## 限制

本证据仅覆盖 AC05 专用 stateless-SGD 短训/恢复闭环；不证明旧 stateful r1 的优化器状态恢复，不作全量评估或精度门槛结论，也未执行 AC06、量化、RTL、烧录或最终规格冻结。代码仓库本轮无修改、未提交 Git。
