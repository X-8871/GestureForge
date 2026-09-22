# S1-T02-D2 tiny416 INT8 权重量化参考

状态：`INT8_WEIGHT_REFERENCE_GENERATED_ACTIVATION_SCALE_PENDING`。
模型：416×416，卷积层 21 个，权重值 5877088 个。
权重包：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny_416_int8_weights.gf8`，5903100 bytes，SHA-256=`f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39`。
聚合权重量化 RMSE=`0.0006044735551187254`，最大绝对误差=`0.06570881001541462`，饱和值数量=`3270`。
BN 已按 Darknet 推理 epsilon=1e-5 折叠；权重按输出通道对称量化到 [-127,127]。
激活校准、整数前向、检测头和 mAP 未执行；该证据不代表 INT8 整网或阶段1通过。
