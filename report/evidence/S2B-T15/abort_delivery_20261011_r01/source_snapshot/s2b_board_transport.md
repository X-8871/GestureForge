# 2B CPU0 与 PC 的 UART 候选运输接口

版本：`s2bu-candidate/1.1`；日期：2026-10-11（UTC+8）。对应 `vitis/s2b_inference_app.c`、`vitis/build_s2b_inference.py`、`verification/s2b_board_transport.py`。本文件定义部署及数据运输候选，尚未完成完整平台冻结或板上验收。1.1 增加未冻结 PS 诊断的 DAP 辅助 ABORT 与显式诊断 ACK；40 B `S2BU/1` 头、普通 RUN、模型、GFINT8W1、输入、D9 解码/NMS 和 AXI/CSR 语义保持原定义及 `s2b-physical-candidate/0.1.1`，不得由运输层更改。

## 部署与内存

CPU0 standalone BSP 使用实际新 XSA、UART1、SDT，禁止 `USE_AMP`。UART1 使用已冻结 PS profile 的 MIO 48..49、基址 `0xE0001000`，BSP 输入时钟 100 MHz；配置 115200、8N1、无流控，并回读配置。启动代码实际启用 DCache 并检查 SCTLR.C；对 `[0x43C00000,0x43D00000)` 设置 BSP `DEVICE_MEMORY`。CPU1 停核、唯一 cacheable DDR 映射、MMU 宏及板卡生命周期由总控独立核实；应用不会停止另一个核。

SDT 实际 BSP 使用 `xiltimer.h`、`xtimer_config.h` 和 `globaltimer_sleep_zynq.c`。应用以 `usleep(1)` 启动真实 global timer，再使用 XTime_GetTime 和非零 COUNTS_PER_SECOND=CPU clock/2 观察期限；不能使用旧 timestamp=0 宏代替时钟。构建保存实际 timer 编译命令及源码；上述常数不是板上吞吐或延迟实测结果。

应用 linker 仅声明 `[0x00100000,0x01100000)` 16 MiB 和 `[0x10000000,0x12000000)` 32 MiB 专属 arena。arena 为 64 B 对齐、NOLOAD 独立节，不进入启动 `.bss` 清零范围。ELF 检查全部 SHF_ALLOC 节、LOAD 段、VMA/LMA、入口、heap、stack 和 arena，禁止下载字节落入 arena。heap 1 MiB、stack 64 KiB；应用 staging 为 5,903,100 B，可复用接收一个输入，解码 double 数组 202,800 B，不缓存 109 个输入。

业务输入与 GF8 分别写在 `0x10000000`、`0x10100000`。只有各自有效字节可被 CPU 复制。feature 外包络为 `[0x11000000,0x11ADADB8)`，外侧缓存维护 padding 仍属于独占 arena；缓存维护按 64 B 外对齐。CPU 在完整长度/CRC 校验成功及 `IDLE_PS` 后装载。START 前执行 DSB、input/GF8 Flush、DSB、feature Flush、Invalidate、DSB。PL 所有权期间不读写或维护 arena。终态安全且身份匹配后整 feature Invalidate、DSB，再读取双头。

`build_s2b_inference.py` 配置由 `S2B_INFERENCE_CONFIG` 的精确绝对路径指定，真实入口为 Vitis2026.1 `vitis.bat -s`。每次新 workspace 和新 RunId，自建 CPU0 BSP、应用及同 XSA `ps7_init.c/.h/.tcl` 的最小 OCM init ELF，记录实际源码 SHA、工具/API/原生退出码、map、ELF 和 BSP 缓存/MMU 来源。OCM init 不执行 FabricInit、boot image 加载或 PL 配置。`UNIT_ONLY_PS_XSA` 仅供离线编译；正式运行要求 `FULL_PLATFORM_BOUND` 新整网 XSA 的重新构建产物。CLI wrapper 返回 0 不能证明业务成功，必须核对 `build_details.json.status`。

## 二进制帧

串口开头只允许一行小于 320 B 的 ASCII banner：`S2B-INFERENCE/1 READY SOURCE=<C源码SHA> XSA=<XSA SHA> MODEL=<模型SHA>\r\n`。其后全部为二进制，不扫描 magic 重同步，不清串口缓冲，不自动重试。

固定 40 B 头为 little-endian `<4sHH8I>`：

| 字节偏移 | 类型 | 字段 |
|---|---|---|
| 0 | 4 byte | ASCII `S2BU` |
| 4 | u16 | version=1 |
| 6 | u16 | op；响应为请求 op OR `0x8000` |
| 8 | u32 | sequence，从 1 连续递增，拒绝 `0xFFFFFFFF` |
| 12 | u32 | frame_id |
| 16、20 | u32、u32 | 原图 width、height |
| 24 | u32 | repeat_count，RUN 为 1..1000；其他为 1 |
| 28 | u32 | payload_len，必须与 op 的精确长度相符 |
| 32 | u32 | payload 的 IEEE CRC32 |
| 36 | u32 | 前 36 B 的 IEEE CRC32 |

CRC 使用 reflected polynomial `0xEDB88320`、初始 `0xFFFFFFFF`、最终 XOR `0xFFFFFFFF`；`123456789` 的答案为 `0xCBF43926`。CRC 覆盖原字节。坏头、长度、CRC、seq、参数均不允许 START；错误后 fail-stop，需总控保存证据并显式恢复。不存在可信的流内重同步。

| op | 请求 payload | 准入 |
|---|---|---|
| 1 LOAD_WEIGHTS | 精确 5,903,100 B GFINT8W1 | IDLE，未处于 WAIT_DAP |
| 2 RUN_INPUT | u32 coreDeadline、u32 drainDeadline、精确 519,168 B CHW INT8 | IDLE、已装权重、两个 deadline 非零 |
| 3 IDLE_DIAGNOSTICS | u32 mode、u32 arg1、u32 arg2 | IDLE 时 mode 0 读诊断，1 非法 input 长度 START，2 正常 START 后等待 DAP ABORT；mode 1/2 的参数为非零 coreDeadline/drainDeadline；仅 pending 时 mode 3 为 ACK_DIAGNOSTIC，参数为 epochLo/epochHi |
| 4 CACHE_PROBE | u32 phase、u32 cpu_seed、u32 dap_seed | 仅 initial visibility0、IDLE、epoch0、从未 START/LOAD；seed 不同 |

RUN 的原图几何范围 1..65535；frame_id 必须容纳全部重复项。一次 RUN 仅发送一个输入，repeat=1000 可完成固定 sample000 连续稳定性候选测试，每个结果 frame 和 epoch 递增；完整 109 黄金样本逐次装载与核对。coreDeadline 默认 `0xFFFFFFFF`，drainDeadline 必须依据实际 profile 显式指定；32 位预算、板上测量与期限选择不由 UART 层伪造。

## 响应与归还

所有响应 payload 先含 40 B `<Q8I>`：u64 epoch；u32 PHYS_STATUS、ERROR_CODE、LAST_REJECT、raw_candidate_count、box_count、repeat_index、repeat_total、response_code。响应头保持 seq/几何/repeat，frame 为请求 frame+index。

response_code：0 成功；1 坏头；2 payload CRC；3 seq；4 长度/op；5 准入状态；6 参数；7 板端/探针失败；8 软件观察期限；9 C 解码失败；10 WAIT_DAP_ABORT 中间响应。普通失败仅含 metadata，禁止携带成功头/框；CACHE_PROBE 失败保留实际 256 B。诊断 mode1 的运输成功仍携带真实 ERROR_SAFE/ERROR_CODE=3；mode2 最终成功携带 ERROR_SAFE/ERROR_CODE=8。两者均不是推理成功，code10 也不是安全归还。

RUN 成功必须完整携带 head13 的 5,070 B INT8、head26 的 20,280 B INT8，再携带 `box_count` 个 `<ii5d>`，每框 48 B：int32 class_id、source_order、IEEE754 binary64 score/x1/y1/x2/y2。最大 15 框；不使用 printf 文本截断精度。INT8 按冻结模型的两头 scale 转 double，直接复用原字节冻结 `s2a_ps_decode_nms_reference.c/.h`。

CPU 按 PHYS_STATUS→epoch HI/LO/HI→frame/code/reject→PHYS_STATUS 读取；仅安全状态前后一致、同 epoch/frame、HEAD_VALID 与 ERROR_CODE 正确才消费头。RUN 必须 DONE_SAFE；ERROR_SAFE 单独记录失败。`FAULT_ISOLATED`、不安全状态或 400 s CPU 观察超时不会清账本、ACK、reset 或访问 arena。UART 完整发送并排空后才写 matching ACK epoch 和 ACK；发送有 10 s 观察期限，TX 不完成即 fail-stop，不无限阻塞归还，也不发布假成功 capture。物理线是否已被 PC 接收仍由 PC 原字节及 CRC 验证。

CPU 不故意执行会产生 AXI SLVERR 的 busy START、非法 CSR 方向/编码，避免 ARM DataAbort。这些板上负例由总控独立审查后的 JTAG DAP 脚本执行，读取 LAST_REJECT 验证零副作用；当前为 `BOARD NOT_RUN`，RTL 或 hostmock PASS 不代替实板 PASS。

## DAP 辅助诊断 ABORT 与显式 ACK

mode2 的状态读取和 ABORT 写入之间可能出现真实终态；额外重读无法消除竞态，冻结 CSR 会拒绝终态 ABORT 并返回 SLVERR。实际 BSP `asm_vectors.S` 的 DataAbort 向量保存故障地址、调用 `DataAbortInterrupt` 后以 `subs pc,lr,#8` 返回故障指令；`Xil_ExceptionRegisterHandler` 只注册 C 回调，不提供修改返回 PC 的接口。应用因此不执行 ABORT 的 CPU MMIO STR，不替换异常向量或吞掉其他 DataAbort。BSP 源码及构建来源保存在本次构建证据。

1. PC 发送 op3/mode2 后，CPU 正常配置并 START；仅实际一致快照为 ARMING/RUN、OWNER_PL、无 SAFE/HEAD_VALID/TERMINAL、错误码0且同 frame/下一 epoch 时，输出 code10、精确40 B metadata。CPU 不访问 arena，也不 ACK。
2. PC 仅用 `WireSession.receive_abort_ready(request)` 接收该中间响应，返回 `(meta, heads, detections)`，后两项为空；普通 `receive` 拒绝 code10。该 API 记录原请求与实际 epoch，保留上一已完成 epoch，进入 WAIT_FINAL。
3. 总控 T16 `dap_abort(epoch, wait_final=...)` 独立核对实际 CSR/epoch/owner 后通过已审 SDK DAP 写 ABORT。它保存真实总线拒绝和原终态；如状态在读取后转终态，SDK 捕获实际 SLVERR，不能伪造 ABORT 成功或覆盖原核心错误。此步骤不由 CPU 应用执行。
4. `wait_final` 使用同原请求 `WireSession.receive(request, 0)`，必须消费最终响应。CPU 只对真实 ERROR_SAFE、同 frame/epoch、错误码8发 code0；完整 TX 后保留终态，进入 `diag_ack_pending`。T16 可随后独立读取稳定 ERROR_SAFE/8。DONE、原错误5等其他终态均发真实失败 code7；不安全/观察超时发 code8。失败不 ACK、不提前宣称 SAFE，不读取 head；应用永久 fail-stop，PC 保留失败原字节。
5. T16 独立最终证明通过后，PC 调用 `WireSession.acknowledge_abort(next_sequence)`。它以新连续 seq、原 frame、payload `<III>(3, epochLo, epochHi)` 发 op3/mode3；CPU 重新核对 pending、同 frame/epoch 和安全终态，再写 matching ACK，响应实际 IDLE_PS/同 epoch/错误码0，host 消费后清除 pending。最终成功响应本身不自动 ACK。

pending 期间禁止 LOAD/RUN/其他诊断。mode3 在没有 pending、错误 phase/frame/epoch、旧 seq 或错误长度/CRC 时拒绝，且不能清账本。缺少最终响应、重复最终响应、错误 owner/epoch、截断或断线使 host fail-stop，不能重发原 seq 或进入下一任务。mode2 的短 core deadline、读后终态交错、DAP 竞态拒绝、原核心 fault、DONE 和排空期限隔离均保存实际状态/码并禁止 ACK。正常 RUN 的完整结果 TX 后 matching ACK 流程保持不变。

## CACHE_PROBE 与外部 DAP 步骤

公共 host API：`Header.pack/unpack`、`make_request`、`WireSession.banner/send/receive`。op4 payload 为 `struct.pack('<III', phase, cpu_seed, dap_seed)`，响应 `meta['probe_bytes']` 为真实 256 B bytes；证据序列化应转 hex 或保存二进制。UART 原字节始终保留，失败响应抛 `TransportError`。启动身份要求与后续推理使用同 ELF/BSP/MMU/宏来源。

1. 总控核对 initial visibility0、CPU1 停核、CPU0/生命周期及新平台身份。不得先发送 LOAD/RUN。phase0 写 `[0x10000000,0x10000100)` 的 64 个 LE u32，word i=`cpu_seed XOR ((0x9E3779B9*i) mod 2^32)`；应用 Flush+DSB，再实际读取 256 B 输出并进入 WAIT_DAP。
2. CPU phase0 读取后至 phase1 不再写该区；WAIT_DAP 不接受 LOAD/RUN。总控选择已核实的 APU/MEM-AP 直 DDR 内存 context，独立 DAP 完整 mrd 比较 CPU pattern，完整 mwr 写入相同公式的 dap_seed pattern，再独立 mrd 比较写入。
3. Vitis SDK 的 `mwr` 默认自动 flush/invalidate CPU cache，可能掩盖 CPU 的 Invalidate 缺失。总控必须审核实际 SDK 源码并绑定其 SHA，使用 `mwr('--bypass_cache_synq', address=0x10000000, size=64, word_size=4, words=list)`，并证明实际 APU/MEM-AP context 和 `mrd.__get_memory_tgt` 没有隐式 CPU cache sync。`mrd` 没有同名 bypass 选项，不能凭选项名称声称已绕过。
4. 总控完成 DAP 验证后明确发送 phase1，相同 seed pair、正确 phase 顺序、IDLE/epoch0。CPU 真实 Invalidate+DSB、逐 word 比较后输出实际 256 B；成功才能结束 WAIT_DAP。身份、顺序或数据失败保留原字节，永久 fail-stop，不 START/reset/ACK。

hostmock 只验证上述软件状态与字节行为；不能填写 `cpu_cross_master_readback` 实板证明。HP nonbufferable/direct BD 排空依据、同 ELF cacheprobe 证明和 HP→CPU 黄金整网数据验证由不同真实证据绑定，完整部署仍需总控审查批准。

## PC 采集与证据

PC 在开串口前按工作树冻结 model/sample/D9 索引 SHA 核对 GF8 和逐输入实际长度/SHA。大型资产复用 `D:\FPGA_Competition\report\evidence\S2A-T68\candidate8x8_109_20261006_130252`，不复制整套。UART RX 原字节立即保存，TX 保存原 header、完整计划 payload SHA/来源及实际发送长度/SHA；不重复存储大型输入。

每个真实响应核对头/payload CRC、seq、frame、重复 index/total、连续 epoch、状态和完整双头/框；捕获 head 与冻结 CPU 黄金逐字节核对，所有框按现有 D9 精度检查。独立从黄金文件提取参考双头，调用 `s2b_fixed_capture_check.py`；绝不能用捕获数据生成黄金。失败、断线、截断、重复、丢失、坏帧均非零退出，保留已收原字节、事件和完整失败结果，不清空串口或自动复位 PL。

离线命令：`python -m unittest verification.test_s2b_board_transport -v`。覆盖独立 CRC/端序、坏头/长度/seq/截断/身份/响应码、1000 连续模拟响应、真实 C hostmock 和全部 109 冻结 CPU C 解码。仿真、离线构建、独立审查、实板操作分别判定。实际 UART、cacheprobe、双核、SLVERR、HP 排空与整网运行未执行时均保留 `NOT_RUN`。
