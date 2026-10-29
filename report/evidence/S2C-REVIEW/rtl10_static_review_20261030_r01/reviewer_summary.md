# S2C 独立静态审查摘要

- task_id：`S2C-REVIEW`
- run_id：`rtl10_static_review_20261030_r01`
- 工作树：`D:\FPGA_Competition\w2c`
- 基线：`756f5828fd1d8356f4f51a21b52554aa1f48d6a7`
- 范围：RTL10/RTL08 首 tile 与 engine 原型审查、RTL07r07 桥协议证据核验，以及此前集成/runner/OOC 静态结论归档。
- 执行限制：本 Reviewer 没有启动编译器、仿真、Vivado、板卡或硬件服务；只读核验总控已生成的 RTL07/RTL10 运行证据。综合时序和板级帧率不在本包结论内。

## RTL10 审查结果

旧版 `sim/tb_s2c_rtl10_engine_axi.sv` 冻结 SHA256 为 `4ff1db0a14b293671df1ddc25aa8ccd0ac87a038a60512950f359b20f222cf23`，静态结论为 **CHANGES_REQUIRED**：AR/AW/W 反压只累计 stall 次数，没有验证 AXI 源通道在等待握手时保持 VALID 和负载。该原版快照保留在 `source_snapshot/tb_s2c_rtl10_engine_axi.sv`。

Developer 修复版 SHA256 为 `ee4933216c0fad2ce1beb7fd0f64370f4b2580358c06cfa208abc818be9fbe08`，静态复审 **PASS（仅源码审查）**，快照为 `source_snapshot/tb_s2c_rtl10_engine_axi_EE493321.sv`。

- `sim/tb_s2c_rtl10_engine_axi.sv:206-263` 对 AR/AW/W/R/B 五路加入 stall 负载监视。前一周期 `VALID && !READY` 后，下一采样边沿直至握手均要求 VALID 持续且相应 ID/地址/LEN/SIZE/BURST/控制、WDATA/WSTRB/WLAST、RDATA/RRESP/RLAST、BRESP 不变；只有 `hard_reset` 清除监视状态。拼接宽度分别为 AR/AW 60、W 79、R 73、B 8 位，与字段宽度一致。
- `sim/tb_s2c_rtl10_engine_axi.sv:568-572` 检查每个 R 握手有活动读请求、beat 索引没有越界、RLAST 仅位于该 AR 段最后一个 beat，且不超过已接受 AR 的总 beat 账本。最终断言 `AR beat total = R = 499`，见 `:699-704`。
- R/B 响应模型用寄存器驱动 VALID 与负载；R 仅在收到 RREADY 后清除/推进，B 仅在收到 BREADY 后清除，反压时保持。桥 RTL 对 RID/RLAST、BID 及响应条件有协议检查；TB 模型固定返回 ID 0、OKAY，没有错误 ID/响应故障注入覆盖。
- AR/AW 属性检查包括 ID=0、INCR、单 outstanding、允许的 SIZE/LEN、对齐和 4KiB 边界；写侧检查 AW 长度、ID、对齐和 4KiB，WID、全字节 WSTRB 与 WLAST。模型还强制首个写突发 W 可先于 AW 接受。详细契约见随包快照 `source_snapshot/s2c_lane32_bulk_interface_20261030.md`。
- 黄金数据与 DUT 独立：TB 读取固定 T66 输入、权重及首层 NCHW 输出 golden；物理 W 通道接收的数据逐字节映射比较 golden，要求首 tile 的 8192 字节唯一、无重复且完整。输入/权重/golden/fixture manifest 的 SHA256 见 manifest 的 `fixture_snapshot` 项。该 fixture 是单层输出样本，不代表整网五类检测的全帧等价。
- TB 中预期检查为 615 个 bulk 命令、8 个 legacy 请求、111 AR、512 AW、1024 W、499 R、512 B、1523 个 AXI 数据 beat；首 tile 完成后 abort 并检查 ledger/活动请求归空。以上是源码中的断言预期，不是本次已运行的观测值。
- 静态未见自比较或明显采样竞态：模型和 DUT 在上升沿采样，响应由寄存器延迟产生。此次未编译/运行，因此不据此宣称这些检查已执行通过。

总控随后提供并运行 `report/evidence/S2C-RTL10/engine_axi_20261030_r01/`。本 Reviewer 独立核验其 `worktree_disk` manifest 的全部 24 项哈希，当前 TB/engine/bridge/adapter SHA 与运行快照完全一致；`result.json` 所列三份日志 SHA 与实际日志相符，`xvlog`、`xelab`、`xsim` 均真实退出码 0、无 timeout、无 launch error，xsim 只有 `PASS RTL10 ENGINE_AXI first_tile` required marker 且没有 failure marker。日志的实际结果为：`cycles=36993 bulk_cmd=615 legacy=8 AR=111 AW=512 W=1024 R=499 B=512 AXI_data_beats=1523 output_golden_bytes=8192 seed=32'h32B0_1C08`。这将结论提升为**RTL10首tile engine→真实wrapper→AXI模型短仿真 PASS**，不是全帧、综合或板级达标；其 manifest/result 快照放在 `rtl10_r01_evidence_snapshot/`，原日志仍留在原 RunId，未复制为审查包 items。

## RTL08r04 与 engine 原型审查

engine 当前 SHA256 为 `2c7f2d216b251791e8e87f8d5bbeeaec04b6cd546ae64ff725ba1c531919d918`，相对 `HEAD 756f5828fd1d8356f4f51a21b52554aa1f48d6a7` 增加 bulk 端口和状态机，改动为 238 行新增、2 行改动。本审查未修改源码。静态结论 **PASS（限定于代码与首 tile 原型）**：

- Feature bulk 只在源地址 8B 对齐时启用；长度受 patch 行尾、input 行尾中较小值约束，向下取 8B 倍数并限长 128B。未对齐前缀或不足 8B 尾部回退原单字节通道；每个 `bulk_read_fire` 同步推进 patch byte index/x/y/channel 与 feature bank 写入，命令不跨行。
- Weight bulk 依据 `group_lane_count × reduction_count` 和 lane/reduction 游标计算本组剩余量，限长 128B；每个读字节写入当前 lane 的 weight bank，并在 reduction 尾推进 lane，跨 lane 的线性地址保持连续。验证前约束 `R<=4608`、lane count≤32，19-bit group size/offset 表达范围足够；包尾仍由既有 `quantized_weight_end_wide`/权重长度检查保护。
- Output bulk 长度受 tile row 剩余列限制、按 8B 对齐取整、最多 128B；每个 `bulk_write_fire` 以 lane 与 output point 索引选取 output block 字节，并同步推进 point index/x/y。首 tile 物理写通道的逐字节 8192-byte golden 比较已由 RTL10r01 实际运行覆盖。
- Bulk 命令地址/长度在命令握手前锁存；读写数据和剩余计数只随相应 fire 推进。正常完成仅在所有字节已接受，或最后一个字节与 done 同沿握手时成功；提前成功完成会报 `INTERNAL`，done error 会传给 result。`abort`/`hard_reset` 优先于状态机并抑制内部 bulk 输出；物理 AXI 已声明责任由 bridge 处理，engine 不承担撤回已声明物理 VALID 的职责。
- 未发现当前审查范围内的 feature prefix/suffix、行/对象范围、weight 跨 lane 游标、output advance、提前完成 error/normal-success 或 abort 阻断。RTL08早完成的动态负例发生在 feature/read 命令；`ST_BULK_WRITE` 提前 done 负例未动态注入，虽可静态核对其对称判据，仍作为覆盖限制保留。

RTL08r04 证据目录为 `report/evidence/S2C-RTL08/bulk_tile_20261030_r04/`。本 Reviewer 核验其 `worktree_disk` manifest 六项哈希与文件一致，TB/engine/bank/runner 当前 SHA 与运行快照相同；三个真实工具命令退出码均为 0、无超时/launch error，日志 SHA 与 result 一致，xsim 两个 required marker 均出现且无 failure marker。实测 marker 为 `PASS RTL08首tile`：cycles=35019、feature/weight/output bulk 命令 96/7/512、legacy 8、unique golden 8192、seed `32'h32B0_1C08`；另有 `PASS RTL08早完成错误/成功语义`，error_code=2、提前成功映射为 internal code 6。TB 修复版 `consume_result_handshake` 在 negedge 拉高 READY、下一 posedge 检查 result_valid、下一 negedge 拉低 READY，再检查 engine 回 idle，消除了原 r03 的结果握手竞态。**RTL08 bulk 数据模型不是真实 AXI 桥**；RTL10r01 提供 engine→wrapper→AXI 的首 tile 运行补充。原 RunId 的 logs 未复制到本 Reviewer manifest。

## 先前静态结论归档

- **集成静态审查：PASS（沿用此前 `integration_review` Reviewer 工具 final）**。此前列出的八个文件 SHA 与当前工作树逐项比对均一致，并保留在本包快照/manifest：wrapper `b4444914…e70d2`、backend `8cf005bd…a70c2`、core `25b16d63…c66a6`、top `b24b6883…d082e`、platform JSON `00e4099e…04fcf5`、platform Tcl `601ac13c…0183f7`、checker `71218e62…2ee55`、RTL09 TB `bd1718cd…a3625`。此处只核哈希绑定，代码审查结论来自该独立 Reviewer，不由本包替代。
- **`verification/run_s2c_short_sim.py`：PASS（静态审查）**。归档版本 SHA256 `92d985c66efbca0da25a5e7c59fdee68a6a074d3325c0aafa3865ce48908a4d66`。检查范围包括输入路径/源文件解析与去重、工具/plusarg/模型和 marker 校验在建 RunId 前完成、空/非 PASS marker 拒绝、向量 helper 快照、CIM 忙碌或可用内存低于 2.5 GB 时不创建 RunId、启动 OSError 进入结果记录，以及 stdout/stderr/PowerShell 子进程 UTF-8 设置。runner 的真实运行结果不在本静态 PASS 范围内。
- **`vivado/s2c_lane32_ooc.tcl`：PASS（静态审查）**。SHA256 `c783b82251fbe1a30795cc4086a244b30b15c8b0506f25d1d13cd30858660a71`。脚本静态设置 32 lane、bulk=1、visibility=0、`xc7z020clg400-2` 及 10 ns 时钟，并输出利用率/时序/方法学报告；源和输出路径有路径组件及 reparse 检查。**未执行 Vivado**；仅有时钟约束、没有接口输入/输出延迟，不能据此报告 WNS/TNS/WHS/THS 合格，也没有实现或板级结论。
## RTL07 r07 运行证据审查

独立核验了 `report/evidence/S2C-RTL07/axi3_bulk_bridge_20261030_r07/`。该运行的 manifest 明确 `hash_basis=worktree_disk`，guard、bridge、TB 与 runner 快照 SHA 均与当前源文件一致；manifest 项包含结果和源快照，不把日志列为 item。`result.json` 绑定日志路径及 SHA，三个真实工具命令 `xvlog`、`xelab`、`xsim` 均记录退出码 0、无超时、无启动错误；对应日志 SHA 与结果字段一致，xsim 实际输出包含 PASS marker，failure marker 列表为空。

- xsim 实际 marker：`PASS RTL07 BULK BRIDGE directed_cases=38 random_samples=0`。
- 此前指出的两个边界缺口已由实际日志关闭：未对齐 `0x01000001/8B` 与非 8 倍数 `0x01000000/12B` 均返回 error=1，且 AXI AR/AW/W/R/B 计数为 0。其他边界负例也实际输出零 AXI 访问。
- TB 覆盖 AXI3 合法 B 先于 AW 接受的闭合情形，验证 AW 受阻时不得提前报告完成且 ledger 保持；这属于 38 个 directed case，不含随机样本。
- xelab 有一条 warning：TB 实例的 `bulk_rdata` 端口未连接；本 run 未使用该输出。它不改变本次已通过的桥协议 directed case 结论，但全路径 engine 验证仍需 RTL10。
- 结论仅为 RTL07 桥/guard 短协议仿真 PASS；不代表全帧等价、综合时序、板上帧率或板级达标。详细原始结果与日志保留于原 RTL07 RunId；本 S2C-REVIEW 包快照其 manifest/result 与 TB 源码，不复制日志。

## 限制与关闭条件

RTL07r07、RTL08r04、RTL10r01 的短仿真及源/日志绑定均已只读核验；engine/TB 的范围内静态审查为 PASS。尚无完整 38 层全帧逐位等价、Vivado 综合时序或板级检测帧率结论。RTL08早完成写路径负例未动态覆盖；RTL07 random_samples=0。OOC Tcl 没有执行，不能声称 WNS≥0。仿真 cycles 不得当作板上 fps 或产品达标。
