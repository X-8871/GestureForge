# S4-B PS INT8 张量诊断入口

## 目的和边界

本入口从冻结的 S2B CPU0 应用受控派生，复用其 S2BU/1.1 UART 收包、CSR、缓存维护、PL 调度、结果 ACK 和 S2A T62 后处理。请求必须携带已准备好的 416×416 INT8 CHW 张量；它用于诊断真实 PS 推理路径和后处理，不含 RGB resize、letterbox 或量化预处理。

ELF/map 中对低 DDR 输入区及 PS app arena 的核验只表示当前恢复输入和链接脚本下的离线布局结果，不代表共享地址图草案已经批准，也不代表板上真实PS分配、缓存一致性或实物会话范围已验证；地址图仍为 `DRAFT_PENDING_REVIEW`。

完整 RGB 注入仍为 `BLOCKED_PENDING_G0`。本诊断单元的构建与离线准备不重建 Vitis 平台、XSA 或 PL；实际硬件操作由另行具备正式交接的受控调用执行。Host API 与日志解码回归属于 `OFFLINE_ONLY`；任何 host mock 都不得标记为真实 PS 或 PL 执行。

## 冻结输入和派生身份

- 基础应用：`D:\FPGA_Competition\w2b\vitis\s2b_inference_app.c`，SHA-256 `9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39`。
- BSP 恢复包：`D:\FPGA_Competition\w2b\report\evidence\S2B-T15\recovery_inputs_20261019_r02\recovery_bundle.zip`，SHA-256 `50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436`。构建器先核对 ZIP 与其成员清单，再在本次 `tmp/4/S4-B-REAL-01/<RunId>/` 解包；不原位执行包内脚本。
- 冻结 XSA、S2A 模型清单、冻结回执及 2B 交付清单的实际路径、长度、SHA-256 和构建前后复核结果保存在本次 `external_inputs_inventory.json`。BSP 头文件、静态库、linker script 和编译输入只从恢复包复用；不复制进 Git 或证据目录。
- `build_s4b_ps_tensor.py` 必须收到非零 u64 `boot_seed` 和不回绕的 u32 session 闭区间。每个成功准入的 `RUN` 依次分配一个 `session_id`；同一 PS 启动内不回绕、不复用。跨重启唯一性不由程序自动保证，必须由操作负责人预留互斥 boot seed/session 范围。r01–r11 都是 `BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE`，不能据构建配置声称范围已预留。
- 派生应用启动横幅为 `S2B-INFERENCE/1 READY SOURCE=... XSA=... MODEL=... DIAG=s4b-ps-tensor/1 TRACE_ABI=1`。这是 READY 身份文本；`S2BU/1.1` 是 UART 字节帧协议，两者不是同一前缀。`SOURCE` 是派生应用 C 文件 SHA。最终装载身份还绑定本轮交付清单中的 ELF SHA、map SHA 和日志 ABI。冻结 2B PC Host 对 READY 身份做精确校验，不能关闭或绕过校验；后续硬件任务必须实现严格绑定这些新值的 adapter。受控 adapter 已实现，见下文；当前硬件门禁仍未闭合。

## UART 输入和日志关联

S2BU/1.1 字节协议保持原样。`OP_WEIGHTS` 权重响应与 `OP_RUN` 推理结果属于不同操作。`RUN` 的 staging 前 8 字节是两个 u32 timeout 参数，随后必须是恰好 519,168 字节的 INT8 CHW 张量。请求头中的原始图像宽高只供逆映射。PL 两个 heads 长度仍为 5,070 和 20,280 字节。

每个成功准入的 RUN 先分配 session，再计算输入 CRC 并复制张量到冻结 arena。每个进入单帧推理路径的结果尝试产生一条记录，包括失败终态。权重加载响应、查询响应、参数拒绝及其他 UART 帧不会增加推理日志条数。记录计数来自日志头的 `record_count`，不能从 UART 总帧数推算。

关联字段按各自用途解释：

- PS 日志主键：`(session_id, result_seq)`。`result_seq` 在本 session 内从 1 开始，并等于 `repeat_index + 1`。
- S4-A 结果 join 键：`(session_id, frame_id, repeat_index)`。
- UART 可观测键：`(frame_id, repeat_index, sequence)`；UART request `sequence` 只用于一致性核对。S2BU/1.1 字节协议不携带 `session_id` 或 `result_seq`。

日志头为 144 字节，容量 1,000 条，单条记录 184 字节；全部字段为 u32 小端字。C API 在写日志时检查容量，满后拒绝新 RUN，不覆盖已提交记录。计数饱和，不回绕。CRC 使用 IEEE CRC-32。

离线 C API 容量回归只检查1000条记录的存储上限、拒绝和不覆盖逻辑，不代表完成了1000次有效推理；真实推理次数当前为NOT_RUN。

## 时间、发布和安全恢复

日志只保存原始 PS global timer ticks，不转换成 ns。时间字段分开表示：`input_write_*` 只包住 CPU 从 staging 到 arena 的 `memcpy` 代码区间，不表示 BSP cache flush 完成或 DDR/PL 可见时刻；另记录写 CSR start 命令前的 PS tick、PS 首次观察到终态后的 tick、后处理结束、日志提交、UART 发送起止以及 ACK 结果。所谓终态时间是 PS 观测时刻，不代表 PL 精确完成周期，也不作为正式 `inference_time_ns`。底层 cache line 操作与 DDR 可见性仍为 `UNKNOWN`，待 G3 实测。

`capture_time_available=false`、`capture_time_ns=0`，并设置 unavailable 注解。时基和 stale 验收口径仍待批准。UART 发送时长独立记录，不能并入推理时间。

提交顺序是：写完整记录和 CRC → 对记录执行 BSP cache flush → DSB → 更新已提交 `record_count` 与 header CRC → flush header → DSB → 才发送 S2BU 响应。UART 返回后再写发送状态并 flush+DSB；只有发送成功才会按冻结应用流程尝试 ACK，随后记录 ACK 结果并再次 flush+DSB。日志发布、响应发送、ACK 是三个独立事件。

冻结应用的安全终态、epoch、frame 和 status 核验继续有效。timeout 或不一致状态会保留真实快照，返回错误响应并停留在失败处理；timeout 不证明消费者停止，不会自动 ACK、复位 PL、释放所有权或重新准入。UART 发送失败时不释放未 ACK 终态。真实硬件上这些恢复与停止行为尚未执行。

## 导出快照和解码

只有在另行获准的导出操作中，PS 已停在明确的安全点、`run_active=0` 且 PL 不持有 arena 时，才可读日志。不要在本任务执行停核或读板。导出端分别按本次 `memory_ranges.json` 中的 `trace_header` 和 `trace_records` 地址读取完整区域两次，并将两份字节原样放进快照文件。两次 header+完整 1,000 槽记录数组必须完全相同；任一变化表示快照不稳定，应丢弃并重新取得获准的稳定快照。

文件格式是 28 字节小端头 `S4BPSDMP, version=1, header_bytes=144, record_bytes=184, capacity=1000, snapshot_bytes=184144`，后续依次为两份 `header(144)+records(184000)`。解码器必须从本轮已核对的 `derived_source_sha256.json` 与 `run_config.json` 显式传入预期派生源码 SHA 和 boot seed，没有可绕过身份核验的默认模式：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B scripts/stage4_s4b/decode_s4b_ps_trace.py <获准导出的双读快照.bin> --expected-source-sha256 <本轮派生SHA-256> --expected-boot-seed <本轮非零u64 seed> --output <解析结果.json>
```

解码器核验两次读取完全相同、header/record CRC、运行身份、记录布局、run 已停止、日志提交标志、容量、session/result 序号、S4-A join 键、每个 RUN 固定元数据、UART sequence 一致性、终态/ACK/发送关系、事件原始ticks顺序、未使用槽为零、capture 不可用字段以及 event 之间的一致性。任何不完整、未提交、损坏、身份不匹配或不稳定记录都会失败。`last_run_incomplete=true` 表示最后一个 RUN 在完整 repeat 前结束；其已提交尝试记录仍保留，不能把它解释成完整 RUN。

## 离线准备与检查

构建入口会先执行严格 host C API 回归、u32 session 耗尽回归、Python 快照与冻结 SHA/锚点、路径越界、完整栈范围变异测试，再从恢复包派生并用官方 AArch32 工具链编译/链接。r11 命令和SHA仍保留在其历史清单中；本轮独立候选使用新RunId和不重叠的构建身份，实际命令为：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B scripts/stage4_s4b/build_s4b_ps_tensor.py --run-id s4b_ps_tensor_20261023_r12 --boot-seed 0x5342424F4F543132 --session-first 0x53422800 --session-last 0x53422BE7
```

本轮产物写入 `report/evidence/S4-B/s4b_ps_tensor_20261023_r12/`，解包和临时对象写入 `tmp/4/S4-B-REAL-01/s4b_ps_tensor_20261023_r12/`。实际 builder 命令退出码为 0；派生 app SHA-256 为 `1be7a551e26f61be1327cdb56672b08d86d17d16433ac405ebd263d5f35bf436`，READY 身份为 `S2B-INFERENCE/1 READY SOURCE=1be7a551e26f61be1327cdb56672b08d86d17d16433ac405ebd263d5f35bf436 XSA=ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6 MODEL=9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a DIAG=s4b-ps-tensor/1 TRACE_ABI=1`。本轮 ELF 为 432548 字节、SHA-256 `f61300d26dc0b66410b9348b5e96719e7c06061ce807cbc86a8149962471718e`；map 为 369452 字节、SHA-256 `0fbeab6d269a5f31cc50be5c00e8bf4671bfbe99975cfe7e15e190f605d45b00`。逐条 stdout/stderr、命令及退出码见本目录 `machine_result.json`、`commands.json`。r12 配置为 `boot_seed=0x5342424f4f543132`、session范围 `0x53422800–0x53422be7`，仍标记 `BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE`；未产生硬件范围预留。最终装载身份还必须核对本轮 `delivery_manifest.json` 和 `external_inputs_inventory.json`；离线产物不代表实物运行。更换 RunId、配置、调试路径或链接环境须重新构建并核验新的 ELF/map SHA，不能假定与 r11/r12 相同。

## 02B 受控 adapter 与 r13 one-shot

源码入口为 `scripts/stage4_s4b/s4b_ps_tensor_adapter.py`。CLI 只有离线 `prepare` / `validate`；硬件调用为 `execute_prepared(...)`，由已有 XSDB session 和 UART stream 的实际持有者调用。函数不创建、关闭或自动寻找这些外部连接。原 PLAN_ONLY 占位模板已由实际实现替代；执行前须核对独审的准确版本与硬件门禁，当前硬件执行仍为 `NOT_RUN`。

上文 r12 是历史构建。r13 派生 app SHA-256 为 `7c3b57a9989b6fe8026d67b19c6abd75b8de1284302d08be2c201893fbd8f102`，ELF SHA-256 为 `bfe88660a7c9b16b4d4360ccf33a7540ee215b7d2ae940408b24bdf83c15ec07`；准确配置及完整身份以 `report/evidence/S4-B/s4b_ps_tensor_20261023_r13/` 的实际清单为准。r13 使用 seed `0x5342424f4f543133`、session `0x53422c00–0x53422fe7`，仍是 `BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE`。不得把离线范围解释为硬件预留。

r13 在成功 RUN 的全部 repeat、UART 与 ACK 流程完成且 `s4b_ps_trace_end_run(1)` 成功后发布成功并进入永久 WFE 停泊。普通命令成功继续接收；失败进入失败停泊。独立反汇编已核对真正 RUN 成功分支 `0x10d5b0→0x10d5bc→0x10d5c4→0x10d338`。历史 r12 的接收循环不能用于此 one-shot 导出依据；更换 ELF 后须重新核验。

### 离线准备

在工作树根执行下列实际 CLI。每次替换为新的、尚不存在的 RunId；已存在目录会被拒绝。

```powershell
& 'C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4_s4b/s4b_ps_tensor_adapter.py prepare --project-root 'D:\codex-worktrees\w4' --source-run-id s4b_ps_tensor_20261023_r13 --run-id <新的离线准备RunId>
& 'C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4_s4b/s4b_ps_tensor_adapter.py validate 'D:\codex-worktrees\w4\tmp\4\S4-B-REAL-02B\<同一离线准备RunId>\adapter_preparation.json'
```

准备时重建 ELF/map/派生源码/seed/session/日志范围身份，核对冻结恢复 ZIP 的精确成员集合及 init 成员原字节，核对固定 Git commit 中四个控制器工具 blob，尚不 import 或执行 SDK。validate 重算实际输入，拒绝重绑旧 ELF、伪造 init、自签来源及文件变化。后续无关 Git 提交可前进，实际被绑定源码和产物必须保持匹配。离线通过状态是 `OFFLINE_PREPARATION_VALID`，不代表硬件可用。

### 正式硬件交接与门禁

实际调用前，八类记录必须分别满足 `validate_hardware_gates` 的字段和当前产物摘要：`operator_authorization`、`hardware_session_handoff`、`exclusive_session`、`g0_approval`、`command_delivery_review`、`timing_freeze`、`range_reservation`、`cold_basis`。缺失时 `execute_prepared` 返回 `BLOCKED_BEFORE_HARDWARE`、SDK/UART 调用数 0。

硬件交接来自 main 与 w4 的真实已提交 STATE 记录。工作树写权交接与板卡上电报告不能替代它：

| 记录 | 必需事实 |
|---|---|
| main OFFER | main 当前历史可达提交中的唯一任务 `S4-B-REAL-02B::s4b_hardware_session_handoff`；发送者 DSH；scope 精确为 `S4B_PS_TENSOR_DIAGNOSTIC`；OFFERED 给当前 w4 负责人；近期心跳与恢复命令。证据入口只能是 `hardware_run_id=<完整RunId>`。当前 HEAD 与工作树仍须保有同一未撤销行。 |
| w4 CLAIM | 当前阶段分支历史可达提交中的唯一任务 `S4-B-REAL-02B::s4b_hardware_session_claim`；相同接收者、工作树、scope、RunId；CLAIMED；证据入口精确包含下列六个唯一键。 |
| 不可变绑定 | handoff 的 authority_source / claim_source 绑定各自 commit、STATE 路径、blob OID 和原字节 SHA；提交须在对应受信分支历史可达。顶层 RunId 与两行 RunId 精确一致。 |

CLAIM 的六键格式为：

```text
offer_commit=<main OFFER提交>;offer_blob_oid=<main STATE blob>;offer_sha256=<该blob SHA-256>;offer_source_commit=<OFFER起始提交>;hardware_run_id=<同一完整RunId>;scope=S4B_PS_TENSOR_DIAGNOSTIC
```

前缀相似值、后缀、重复键和多余键均拒绝。调用方的 state_history 不参与授权。阶段5历史释放不是第三个必需交接来源；项目总控负责在 main OFFER 前核对当前跨窗口占用，阶段4不写主 STATE 或项目总控信箱。

其余记录还须证明准确装载/RUN/双读导出/停止自有 CPU0 的操作范围、有效期、排他 SDK peer 和 UART、地址图及时间基准批准、与当前 adapter/产物绑定的独审、互斥 seed/session 范围、旧 AXI 生命周期已清除的冷依据。共享地址图及 stale 门槛仍是草案时不能写成 APPROVED。Wong 告知板卡已上电连接，当前没有本次硬件 OFFER/CLAIM、没有加载或串口操作。

### 获准执行的实际顺序与停止点

1. 先 validate preparation 及八类门禁；输入权重、519168B 张量和独立 tensor binding 必须核验。只消费已交接 session/stream，不尝试接管他人连接。
2. 从固定 `07c3d3958578b9cc9d3b8eae3758711fe08724c2` Git blob 取得并逐项核验四工具导入闭包，然后才导入隔离副本。真实 `JtagController` 执行目标/CPU 状态门禁、system-stop、OCM init→ready/fail 与 INIT_RESULT/DDR 检查→完整 bit→postconfig→DDR app。任何不符保留失败证据并停止。
3. 严格匹配派生 READY 的 SOURCE/XSA/MODEL/DIAG/TRACE_ABI；S2BU/1.1 正文保持不变，分开记录 WEIGHTS 与 RUN。运行前确认本次日志为空且无历史记录；响应、CSR、session/frame/result/repeat/UART sequence 和日志相互核对。
4. 成功 RUN 必须已进入 r13 one-shot 停泊。adapter 在 stop 前紧邻重读完整安全 CSR；变化时不 stop。停止后再次核对 CSR；不一致时在 trace 导出、ACK、reset、retry 或 release 前失败。
5. 安全条件成立后全区读取两次，每次 header 36 words 与 records 46000 words。SDK 的真实46000-word能力尚未核验；若实际失败，保存真实错误，不猜分块长度。两份完整快照、CPU/CSR/run_active 与 UART join 关系均一致才生成双读 dump，再用明确 SOURCE/seed 解码。
6. 失败时 `automatic_recovery=NONE`，保留 CPU/CSR/owner/pending 和原始日志，不自动 ACK、reset、释放或重试；把实际状态交回会话持有者。不结束或关闭外部 session/UART。

硬件 API 的准确参数见实现 `execute_prepared`：除 preparation、hardware_run_id 和 gate_files，还需交接的 xsdb_session/uart_stream、权重/张量/tensor binding、独立 RX/TX 记录路径、frame/width/height/repeat 及 core/drain timeout。本文不提供可绕过持有者与门禁的自动连接命令。每次真实执行使用新硬件 RunId；原始失败证据不可覆盖。

交付与独审仅覆盖此 PS 张量诊断单元，完整 RGB→PL 预处理、109帧 PL 对拍及4D长跑须由各自实现和实物证据验收。包装 `CHECKS_OK` 不代表 G0/G3/G4/G5。
