# S4B-PL-SYSTEM-G0-03 独立规格审查

结论：**CHANGES_REQUIRED**。本审查只判断冻结系统规格能否支撑参数化离线RTL/PS/host开发，不批准物理地址、硬件交接或实板G0/G3/G4。

## 冻结版本

- HEAD：4639501c7c0badeded139e9a2a76017ca8294adc
- 规格：report/evidence/S4-B/s4b_pl_system_g0_review_20261023_r01/frozen_specification.json，SHA-256 2b8bb49fa520a22623f1737eb4fe75848eb6e16e67e4b4fc9f6655741fd4a8cc
- 文档与快照 SHA-256：e6ae30a5328b041505d1101fd2c4332723571f025017600d806af3fbe7c3f77d，67,656 B

## 必须关闭的规格问题

1. **PS侧golden tensor比较不可实现**（文档行205、289、297–298）。文档要求PS在network前把完整519,168 B tensor与冻结D2直接参考逐字节比较，但PS不做像素预处理，RAW/geometry没有expected tensor/hash/CRC，metadata仅32 KiB且没有host确认阶段。改为PS记录PL tensor CRC；DONE后由host经JTAG读取tensor并与CPU D2参考逐字节比较、再核对head/boxes；只有host完成核对后发送既有RESULT_CONSUMED。比较失败时保持结果未消费并禁止下一帧，不需要PS存整份golden或新增opcode。
2. **旧CSR START屏障覆盖不足**（文档行331、337及冻结S2B CSR语义）。外部CSR 0x008 START只检查旧network controller的IDLE_PS；预处理持有HP0时它仍可能空闲。需明确整个preprocessor owner持有期都原子拒绝外部START且无副作用，只有匹配token在TENSOR_READY可启动network。
3. **COMMIT精确回显未定义**（§8.2）。需要求COMMIT逐字段匹配已接受RAW_BEGIN的width、height、stride、pixel format、logical/storage bytes、raw CRC及授权buffer身份；不匹配必须在任何接受/所有权状态副作用前拒绝并有反例覆盖。
4. **session跨启动唯一性无来源**（§§8.1–8.2）。每次PS启动/reset要求新非零u32 session_id，但本地u64 boot_seed不在协议字段中且没有u32分配/耗尽规则。需定义跨启动不复用来源和生命周期，或正式缩小保证并解决相应规格决策。
5. **injection_start_ns缺少PS时钟域来源**（§8.3与S4-A契约）。host_raw_first_write属于host时钟，文档又禁止未经校准的跨域相减；需定义PS域捕获/经校准转换，或一致地定义显式不可用/空值策略，不能把host时间标成PS时间。

## 已核对范围与边界

冻结规格JSON、正文、快照及HEAD哈希匹配；绑定的S4-A、S2B、D2、PS与geometry源文件哈希只读核对匹配。对3-opcode生命周期、128B/64B记录字段与CRC、24B geometry记录、未用slot清零、JTAG_RAW_TASK边界以及“≥30分钟”和“≥1000次”两个独立最低值做了静态核查。通过项不消除以上阻断项。

未改源码、正式文档、STATE或Git；未运行硬件、Vivado、重型测试或新探针。该结论不审查另行运行的整帧PL小程序，也不构成物理地址批准、硬件交接、实板验证或G3/G4通过。
