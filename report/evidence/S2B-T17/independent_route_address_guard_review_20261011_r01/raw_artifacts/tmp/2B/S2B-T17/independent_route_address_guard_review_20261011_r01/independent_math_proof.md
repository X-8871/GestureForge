# S7 独立整数证明

审查对象为固定 Git `f53e067ba91abc02ed60cf7f9063884d9ddb79f1` 的 S6 ROUTE 与本轮冻结 S7 两个模块。设 `U=2^32-1`；所有公开 UINT32 参数取任意二态值，INT8 取 -128 至 127。下述是无界整数推导；有限仿真为辅助证据，不承担全域证明。

## query 的前置范围判据

任意 `C,H<=U`，精确积 `C*H<=U^2<2^64`。S6/S7 均先用 64 位计算该积并检查是否超过 U；超过时已置 BAD_RANGE。否则再计算 `(C*H)*W`，两个因子均不超过 U，积仍严格小于 2^64。因此有效消费路径中不存在三因子乘法按 64 位回绕后错误放行。若存在零因子，参数错误优先；不能以正因子证明改变该拒绝域。

没有参数错误时，源数只能为 1 或 2，组数只能为 1 或 2；组 1 的 group_id 只能为 0，组 2 的 group_id 为 0/1、源数为 1、C 为正偶数且选区为对应半区。组数 >=3 双方均拒绝。原 2A 的多组通用语义在旧 S3 已不同，不能据此声称原 2A 的全部公开域等价。源数为 1 时所有 source1 参数及值均未被消费。

没有参数/范围错误时，对于任意被选中源 i，`0<=start_i<end_i<=C_i`；输出通道落在选区长度之和，y<H、x<W，两个源的 H/W 相同。选中源 0 时 `channel=start0+output_channel<end0<=C0`；选中源 1 时 `channel=start1+output_channel-(end0-start0)<end1<=C1`。这些 32 位加减在该域精确，没有溢出或下溢。

前置范围检查进一步给出 `C_i*H*W<=length_i<=U`，`base_i+length_i<=2^32`。令 `p=channel*H+y`，则

`0<=channel*H<=p<=C_i*H-1<=U`，

`0<=p*W<=p*W+x<=C_i*H*W-1<length_i<=U`。

因此两个 32 位乘法及后续加法的每个前缀均精确；窄 offset 等于 S6 的 64 位 offset。又有 `base_i+offset<base_i+length_i<=2^32`，所以地址不超过 U，窄地址和旧地址低 32 位完全相同。旧末项 `offset>=length_i` 与地址超过 U 两项均恒假。

若前置 bad_argument 为真，旧末项最多再次置 bad_range，仍返回 BAD_ARGUMENT。若前置 bad_argument 为假而 bad_range 为真，双方仍返回 BAD_RANGE。这两类都由共同默认赋值输出七个零数据字段。剩余成功域已证明旧末项恒假，故删除末项不改变错误优先或八个公开输出中的任一位。选中值 -128 仍属于前置 BAD_ARGUMENT；倍率 0 或超过 0x80000000 仍拒绝，合法倍率及正负舍入/饱和语句未改。合法幅值 <=127 时 39 位乘积和舍入加法也精确。

## engine 的消费域及逐周期等价

query 返回 NONE 且其三个 shape 输出与 latched 输出 shape 相同，才可能通过 VALIDATE 第一分支。正 H/W 与选区包含关系给出 `E=Cout*H*W<=shape0+shape1<=2U<2^33`（单源同样成立）。因此保留的原 65 位输出三因子乘积在消费域精确，不会发生任意三 UINT32 乘积可能出现的 65 位别名。shape 不同或 query 错误已由未改的第一分支拒绝，不能进入被删分支。

第一分支通过进一步要求 `E<=output_length<=U` 且全部输出因子和长度非零。第二分支通过要求 `output_base+output_length<=2^32`，65 位端点求和对全部 UINT32 域精确。query 的合法坐标同时是输出 shape 的合法坐标，故 `p_out=output_channel*H+y<=Cout*H-1<=U`、`offset_out=p_out*W+x<E<=output_length`，以及 `output_base+offset_out<2^32`。窄前缀精确，原第三分支的 offset/地址回绕条件均恒假。

第一分支未通过时原错误选择仍为 query BAD_RANGE 优先映射 2、query BAD_ARGUMENT 映射 1、其余输出 shape/零/短长度映射 BAD_LENGTH 3；随后端点错误为 BAD_RANGE 2。输出短长度与对象端点同时错误仍返回 3。被删除的第三分支此前从未被成功消费，删除后仍在相同一周期进入 READ_REQUEST，没有新增周期。

已实际从 Git 原字节核对两个模块头部完全一致；query 无时序块。engine 的整个 always_ff 除唯一授权删除的四行分支外逐字一致，剩余时序块 SHA 为 `e73081b55cba12dc9c85ce425f1079c0583d2fbbcdded70964f6ccb1f151e8fb`。从相同 reset 初态归纳：query 的组合输出一致；所有其他寄存器更新、状态迁移、请求响应、背压、结果保持及 abort/reset 优先均相同；唯一分支恒假，因此每个时钟周期所有公开口一致。直接 engine 没有 owner 输入；backend/owner 逻辑本轮字节未改，G1 的真实 backend 逐周期及 owner 掉低覆盖单独核查并仅绑定。

## 辅助实际验证与限制

本轮另建种子 `0x7A110C61`（2047937633），不调用 Developer 的 oracle/cases/vectors；黄金地址按 NCHW 线性展开重新实现。实际运行 9,077 个 query 全八输出和 4,912 个 engine 全十四公开输出，57,695 周期、八态 abort/reset 掩码均 255。包括合法大 CHW、两源选择、两组及 group_id、坐标/组选区非法、零/短长度、多重错误、所有 INT8 值和倍率边界、端点恰为 2^32/最后地址 FFFFFFFF、C*H 或最终 shape 越界、两源元素和超 U；另有响应映射 24 项、raw80、无限请求背压后 abort 和结果背压保持。

该证明限定于二态公开参数和实际 S6/S7 固定源。没有建立四态 X/Z 语义证明；没有新 STA、bitstream、设备、卷积 layer0 数值或完整整网/实物 G3。结论最多为 PASS_G2_ONLY。
