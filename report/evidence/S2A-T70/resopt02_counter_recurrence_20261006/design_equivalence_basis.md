# RESOPT-02 语义等价依据

## 基线与范围

基线 commit 为 6a408b5a8bdab90888fc6ad51b4fce7b38563090，引擎 blob 为 a6dbd8b90dbad632632712b81ef05b6159786b99。本轮仅重写形状校验及线性扫描坐标映射；compute_point_index / tile_width 仍保留原组合除余，以兼容现有白盒台架对该层次信号的直接赋值。接口、lane 并行度、状态周期、请求握手和错误编码不变。

## 描述符形状校验

原条件在先确认 N >= K 与 S != 0 后判断 floor((N-K)/S)+1 == O。令 T=N-K，对 O>0,S>0，等价条件是：(O-1)S <= T < OS，进一步等价于 T < OS <= T+S。实现以 O*S 与 T、T+S 比较，不执行除法。

output_height_numerator / output_width_numerator 与卷积核、stride、输出尺寸均先零扩展到 64 bit。N 最大为三个 32-bit 字段之和，小于 2^34；有效 T+S 小于 2^35。O 和 S 最大为 2^32-1，乘积小于 2^64，因此比较所需 64-bit 运算不溢出。若 N<K、输出为0或 stride为0，原有前置参数分支仍先返回 BAD_ARGUMENT；范围校验与长度校验的先后关系保持不变。有效尺寸全部通过 T70 descriptor 测试；本轮保留原来的 BAD_ARGUMENT 分类和先前错误优先级。

## Feature patch 扫描坐标

基线每个 feature_scan_index 映射为：
channel = index / (patch_height*patch_width)；
y = (index % plane) / patch_width；
x = index % patch_width。
新计数器从每个 tile 的 (channel,y,x)=(0,0,0) 开始，x 最快递增，x 到宽度后归零并递增 y，y 到高度后归零并递增 channel，等价于按通道平面、行、列的 row-major 线性编号。

只在原状态机实际使 feature_scan_index 加一时同步前进坐标：padding 越界填零，或读响应成功且错误码为 NONE。请求等待、响应等待、读错误、地址越界错误、扫描结束均不前进。坐标在 hard_reset、abort、descriptor start 和每个 ST_TILE_PREP 清零。异常/错误优先顺序不变，也不新增状态或周期。

## Reduction 扫描坐标

基线 compute_reduction_index 展开顺序为输入通道、kernel_y、kernel_x，其中 x 最快递增。新计数器在 ST_COMPUTE_PREP / ST_COMPUTE_POINT_PREP 从 (channel,y,x)=(0,0,0) 初始化，每个成功且非末尾的 MAC tap 只前进一次，依次推进 x、y、channel。末 tap、不合法 int8、累加溢出都不前进并直接沿既有路径结束；新空间点重新初始化。hard_reset、abort 和新 descriptor start 清零。group_lane_count 只屏蔽尾组 lane，不影响坐标序列。compute point 的 x/y 除余保留原式。

## Output patch 扫描坐标

基线用 output_point_index / tile_width 与 % tile_width 得到 tile 内 y/x。新计数器在该 tile 的 ST_OUTPUT_SCAN 开始时为 (0,0)，仅在成功 output write response 后前进；x 到 tile_width 后归零并递增 y。内存请求/响应 stall 或错误不会改变坐标。下一个 lane 到来时线性 index 和坐标同时清零；下一 tile 的 compute 完成进入输出扫描前也清零。hard_reset、abort、新 descriptor start 清零。故每次实际写入的地址继续对应相同的线性 output index。

## 周期与 timeout

只增加并行寄存器更新和递增比较，不增加状态转移或握手周期。feature、MAC、requant、output scan 各自的步数仍由原始线性 index/请求响应决定，cycle timeout 无新增周期预算。