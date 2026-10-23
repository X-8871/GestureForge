# S4-B PS INT8 张量诊断入口

## 目的和边界

本入口从冻结的 S2B CPU0 应用受控派生，复用其 S2BU/1.1 UART 收包、CSR、缓存维护、PL 调度、结果 ACK 和 S2A T62 后处理。请求必须携带已准备好的 416×416 INT8 CHW 张量；它用于诊断真实 PS 推理路径和后处理，不含 RGB resize、letterbox 或量化预处理。

ELF/map 中对低 DDR 输入区及 PS app arena 的核验只表示当前恢复输入和链接脚本下的离线布局结果，不代表共享地址图草案已经批准，也不代表板上真实PS分配、缓存一致性或实物会话范围已验证；地址图仍为 `DRAFT_PENDING_REVIEW`。

完整 RGB 注入仍为 `BLOCKED_PENDING_G0`。本任务不重建 Vitis 平台、XSA 或 PL，不运行板卡、UART、JTAG、Vivado 或 xsim。Host API 与日志解码回归属于 `OFFLINE_ONLY`；任何 host mock 都不得标记为真实 PS 或 PL 执行。

## 冻结输入和派生身份

- 基础应用：`D:\FPGA_Competition\w2b\vitis\s2b_inference_app.c`，SHA-256 `9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39`。
- BSP 恢复包：`D:\FPGA_Competition\w2b\report\evidence\S2B-T15\recovery_inputs_20261019_r02\recovery_bundle.zip`，SHA-256 `50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436`。构建器先核对 ZIP 与其成员清单，再在本次 `tmp/4/S4-B-REAL-01/<RunId>/` 解包；不原位执行包内脚本。
- 冻结 XSA、S2A 模型清单、冻结回执及 2B 交付清单的实际路径、长度、SHA-256 和构建前后复核结果保存在本次 `external_inputs_inventory.json`。BSP 头文件、静态库、linker script 和编译输入只从恢复包复用；不复制进 Git 或证据目录。
- `build_s4b_ps_tensor.py` 必须收到非零 u64 `boot_seed` 和不回绕的 u32 session 闭区间。每个成功准入的 `RUN` 依次分配一个 `session_id`；同一 PS 启动内不回绕、不复用。跨重启唯一性不由程序自动保证，必须由操作负责人预留互斥 boot seed/session 范围。r01–r11 都是 `BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE`，不能据构建配置声称范围已预留。
- 派生应用启动横幅为 `S2B-INFERENCE/1 READY SOURCE=... XSA=... MODEL=... DIAG=s4b-ps-tensor/1 TRACE_ABI=1`。这是 READY 身份文本；`S2BU/1.1` 是 UART 字节帧协议，两者不是同一前缀。`SOURCE` 是派生应用 C 文件 SHA。最终装载身份还绑定本轮交付清单中的 ELF SHA、map SHA 和日志 ABI。冻结 2B PC Host 对 READY 身份做精确校验，不能关闭或绕过校验；后续硬件任务必须实现严格绑定这些新值的 adapter。本任务没有该 adapter，也不执行串口命令。

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

## 后续硬件操作计划（PLAN_ONLY）

此计划当前不可执行：没有 S4-B 受控 adapter，也没有板卡授权或会话交接。本节代码模板第一行无条件抛错；其余是未来 adapter 的契约占位，不是已经存在的 API 或命令。不得复制运行，也不得用此计划替代身份审查、范围预留或授权。

2B 冻结的 `verification/s2b_board_jtag.py` 中 `JtagController(session, bindings, evidence_dir)` 只借用已有 `localhost:3121` XSCT 会话。实际方法是 `select_and_gate()`、`system_reset_stop(cold_basis)`、`deploy()`、`verify_bindings()`、`gate()`、`stable_csr(label)`、`words(address, count)`、`state(label)` 和 `call(name, function, ...)`。它不创建或关闭会话。`deploy()` 保持冻结顺序：system-stop 后确认 EOS0 → CPU0 下载 OCM init ELF → `cpu0.con("--block", timeout=30)` 命中 ready/fail 检查点并核验 ready result=2、原返回码=0 → DDR normal=1 → `fpga.fpga(file=...)` 完整配置并确认 EOS1 → 按冻结 XSA 生成 postconfig、恢复冷 CSR 默认值 → CPU0 下载 DDR app ELF → `cpu0.con()`。各调用由原控制器的绑定核验和目标门禁包围。这里不能跳过 init、DDR、PL 或 postconfig 步骤。

本轮 S4-B `external_inputs_inventory.json` 绑定恢复 ZIP、冻结回执/清单、XSA、模型及工具的实际路径和 SHA；bitstream 从 inventory 已绑定的 2B 冻结清单中取得准确路径和 SHA；init ELF 从该 inventory 已绑定的恢复 ZIP 成员清单校验后取得；app ELF、map、派生源码身份、TRACE ABI 和 seed/session 配置来自本轮 `delivery_manifest.json`、`derived_source_sha256.json`、`run_config.json` 和 `memory_ranges.json`。缺任何条目、哈希不符、当前草案未批准或会话/范围未经核验时，模板必须在门禁前停止。

源码和交付物的来源分别核验：2B交付manifest不是完整源码清单。控制器、传输层与ELF parser虽未列于该manifest，均存在于inventory已绑定的冻结Git提交 `07c3d3958578b9cc9d3b8eae3758711fe08724c2`。未来adapter须通过 `git cat-file blob <commit>:<path>` 取得原字节，在本次唯一临时目录中建立完整必需导入闭包，逐项验证路径/长度/SHA后才导入；不能先import当前工作树文件再检查。必需闭包如下，导入后的 `__file__` 也必须指向已核验副本，同名已加载模块或未绑定来源须拒绝。

| 冻结Git路径 | 原始Git blob字节SHA-256 |
|---|---|
| `verification/s2b_board_jtag.py` | `dbd1de2241518e679312746a7386c7e5fb1a5a2e242b88dff052b1ca8907b0c6` |
| `verification/s2b_board_transport.py` | `7dda231e2888c0ed9d95952dcba4d41c9eaf7423e008e4d179b3f7d2c5f0b334` |
| `verification/check_s2b_ps_smoke_layout.py` | `6c12023cc9660d392a0f3e393df2ebaf425af8a4cbb51886a35749d0c6fa0f77` |
| `verification/check_stage_delivery.py` | `788ddcef961cab1a1db917292abbceb41dc6957ca4b8f1c76841158ddc48c112` |

`csr_source`及`s2bu/1.1`接口文档由冻结交付manifest绑定，不能使用占位路径。`sdk_target`来自本次会话交接记录，`cold_basis`来自本次获准硬件Run的冷生命周期依据，均不是2B冻结文件。本轮没有这两类硬件记录。捕获比较的可选惰性导入支链为 `s2b_fixed_capture_check.py → s1_t02_d9_yolo_decode.py → s1_t02_d6_detection_metrics.py`；若未来adapter调用它，也须先从同一冻结commit取得和核验全部源码。D9/D6当前工作树CRLF字节与Git blob不同，因此不能拿Git SHA去绑定当前文件；隔离副本绑定实际取得的Git字节。以上来源规则仍是待实现adapter契约。

```python
raise RuntimeError("PLAN_ONLY：硬件 adapter 尚不存在；禁止执行此模板")

from pathlib import Path
import json
import struct
import subprocess
import sys

project = Path(r"D:\codex-worktrees\w4")
run_id = "s4b_ps_tensor_20261023_r12"
evidence = project / "report/evidence/S4-B" / run_id
temporary = project / "tmp/4/S4-B-REAL-01" / run_id
manifest = json.loads((evidence / "delivery_manifest.json").read_text(encoding="utf-8"))
inventory = json.loads((evidence / "external_inputs_inventory.json").read_text(encoding="utf-8"))
derived = json.loads((evidence / "derived_source_sha256.json").read_text(encoding="utf-8"))
run_config = json.loads((evidence / "run_config.json").read_text(encoding="utf-8"))
memory = json.loads((evidence / "memory_ranges.json").read_text(encoding="utf-8"))

# 以下解析器均为未实现的受控adapter契约占位，必须从清单逐项校验路径、角色、SHA和外部输入状态。
def evidence_binding(relative_path):
    raise NotImplementedError("契约占位：必须唯一匹配本轮manifest并重新计算文件SHA")

def external_binding(label):
    raise NotImplementedError("契约占位：必须唯一匹配inventory且核对before/after SHA")

def freeze_artifact_binding(relative_path):
    raise NotImplementedError("契约占位：必须由inventory绑定的2B冻结manifest解析并核对")

def recovery_member_binding(member_name, extracted_path):
    raise NotImplementedError("契约占位：必须核对恢复ZIP SHA、成员清单和解包字节")

def prepare_verified_git_tools(commit, relative_paths):
    raise NotImplementedError("契约占位：核对inventory冻结commit，git cat-file取得完整导入闭包到唯一目录，导入前逐项核验上表原字节与精确路径")

def hardware_record_binding(role):
    raise NotImplementedError("契约占位：只接受本次获准硬件Run的真实会话交接/冷生命周期记录，不能从2B冻结清单伪造")

def import_verified_controller(tool_bindings):
    raise NotImplementedError("契约占位：完整闭包导入前核验已通过后才载入；拒绝预加载同名模块/未绑定来源，复核各模块__file__并返回真实JtagController")

tool_bindings = prepare_verified_git_tools(
    "07c3d3958578b9cc9d3b8eae3758711fe08724c2",
    ("verification/s2b_board_jtag.py", "verification/s2b_board_transport.py",
     "verification/check_s2b_ps_smoke_layout.py", "verification/check_stage_delivery.py"))
# 此调用只能发生在整个源码闭包验证后；上方没有导入任何2B项目模块。
JtagController = import_verified_controller(tool_bindings)

identity = {
    "ready_banner": derived["embedded_ready_banner"].rstrip("\\r\\n"),
    "SOURCE": derived["derived_s4b_ps_app_sha256"],
    "XSA": external_binding("冻结XSA引用")["sha256"],
    "model_sha256": external_binding("冻结模型manifest")["sha256"],
    "TRACE_ABI": 1,
    "trace_log_abi": derived["trace_log_abi"],
    "boot_seed": int(run_config["boot_seed"], 0),
    "session_first": int(run_config["session_first"], 0),
    "session_last": int(run_config["session_last"], 0),
}

# 每个JtagController绑定项都必须是{path, sha256}；下列额外项保存本轮身份来源。
bindings = {
    "bit": freeze_artifact_binding("report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit"),
    "xsa": external_binding("冻结XSA引用"),
    "init_elf": recovery_member_binding(
        "bundle/workspace/reference/init.elf",
        temporary / "bundle_extract/bundle/workspace/reference/init.elf"),
    "app_elf": evidence_binding("s4b_ps_tensor_diagnostic.elf"),
    "model": external_binding("冻结模型manifest"),
    "SOURCE": evidence_binding("derived_source_sha256.json"),
    "TRACE_ABI": evidence_binding("vitis/stage4/ps/s4b_ps_trace.h"),
    "boot_seed": evidence_binding("run_config.json"),
    "session_range": evidence_binding("run_config.json"),
    "csr_source": freeze_artifact_binding("src/s2b_control_csr.sv"),
    "interface": freeze_artifact_binding("docs/obsidian-project/02-方案设计/s2b_board_transport.md"),
    "sdk_target": hardware_record_binding("sdk_target"),
    "tool_source": tool_bindings["verification/s2b_board_jtag.py"],
    "elf_parser": tool_bindings["verification/check_s2b_ps_smoke_layout.py"],
    "delivery_parser": tool_bindings["verification/check_stage_delivery.py"],
    "transport_source": tool_bindings["verification/s2b_board_transport.py"],
    "cold_basis": hardware_record_binding("cold_basis"),
}

# session必须是总控已连接并交接的对象；此处没有连接、选择或关闭硬件会话的代码。
session = None  # 契约占位：只允许使用已交接且目标身份已核验的localhost:3121会话。
adapter = None  # 契约占位：当前不存在S4-B RUN/READY/双读导出/安全停止adapter。
evidence_dir = Path("<新的获准硬件RunId目录>")
if session is None or adapter is None:
    raise RuntimeError("缺少已交接会话或受审adapter；停止，不访问硬件")

controller = JtagController(session, bindings, evidence_dir=evidence_dir)
controller.verify_bindings()
controller.select_and_gate()  # 只读目标/CPU1/CPU0/JTAG启动模式门禁。
controller.system_reset_stop(cold_basis=bindings["cold_basis"])
controller.deploy()  # 按上文完整顺序执行init→ready码→DDR→PL→postconfig→app。

# 契约占位：adapter必须核验完整S2B-INFERENCE/1 READY横幅身份，不得改宽旧Host校验。
adapter.require_ready_identity(identity)
# 契约占位：只通过冻结S2BU/1.1字节协议发送；RUN负载为2个u32 timeout + 519168B INT8_CHW_416。
adapter.submit_s2bu_run(payload_path=Path("<获准的519168字节张量路径>"), identity=identity)
# 收到timeout、状态/epoch/frame不匹配、UART失败或日志满时停止；不得ACK、reset、释放或重试。

trace_header = memory["trace_header"]
trace_records = memory["trace_records"]
header_address = trace_header["start"]
records_address = trace_records["start"]
records_words = trace_records["size_bytes"] // 4  # 46000个u32，即184000字节。
assert trace_header["size_bytes"] == 144 and records_words == 46000

# 先由adapter确认run_active=0、PS处于安全空闲/安全终态、CSR无PL owner及pending，且两次CSR稳定。
adapter.require_safe_snapshot_preconditions(controller, identity)
controller.verify_bindings()
controller.gate(both=False)
assert controller.state("cpu1").startswith("Stopped")
assert controller.state("cpu0") == "Running"
controller.call("cpu0.stop.after_safe_point", controller.targets["cpu0"].stop)
controller.gate()
assert controller.state("cpu0").startswith("Stopped")
assert controller.state("cpu1").startswith("Stopped")

# 真实API为APU mrd('--value', address=..., size=..., word_size=4)。每次全区读取均有36+46000 words。
# 如果该SDK对连续读取有长度限制，adapter必须先在独立核验中确认分块语义；此处不猜最大长度。
header_1 = controller.words(header_address, 36)
records_1 = controller.words(records_address, records_words)
header_2 = controller.words(header_address, 36)
records_2 = controller.words(records_address, records_words)
assert header_1 == header_2 and records_1 == records_2
assert header_1[17] == header_2[17] == 0  # run_active在两次全区快照前后均为0。
adapter.require_safe_snapshot_postconditions(controller, identity)

def words_le(words):
    return struct.pack("<" + "I" * len(words), *words)

snapshot_1 = words_le(header_1) + words_le(records_1)
snapshot_2 = words_le(header_2) + words_le(records_2)
dump = (struct.pack("<8sIIIII", b"S4BPSDMP", 1, 144, 184, 1000, 184144)
        + snapshot_1 + snapshot_2)
dump_path = Path("<本次硬件RunId下的新双读快照路径>")
dump_path.write_bytes(dump)
subprocess.run([
    sys.executable, "-B", str(project / "scripts/stage4_s4b/decode_s4b_ps_trace.py"),
    str(dump_path), "--expected-source-sha256", identity["SOURCE"],
    "--expected-boot-seed", hex(identity["boot_seed"]),
    "--output", str(dump_path.with_suffix(".decoded.json")),
], check=True)
```

上述模板中尖括号内容、`evidence_binding`、`external_binding`、`freeze_artifact_binding`、`recovery_member_binding`、`prepare_verified_git_tools`、`hardware_record_binding`、`import_verified_controller` 和 `adapter` 都只是契约占位；`sys`等标准库导入并非待实现API。当前脚本不具备可直接运行的组合。即便移除第一行保护也会在未实现门禁处失败。不得把样例解释为本轮 READY、PL、板卡、串口或DDR已可用。

计划步骤和停止点：

1. **绑定与会话门禁**：取得针对该具体装载、RUN、导出和停止操作的授权及会话交接；确认复用的 `localhost:3121` 会话、目标父链、目标身份、CPU0/CPU1 状态和 JTAG boot mode。绑定必须逐字节匹配本轮manifest/inventory；旧 PC Host 对 `S2B-INFERENCE/1 READY SOURCE=... XSA=... MODEL=... DIAG=s4b-ps-tensor/1 TRACE_ABI=1` 的精确校验不能关闭。当前共享地址图仍为草案，因此缺独立批准时在此停止。
2. **初始化和加载**：只调用冻结的 `select_and_gate()`、`system_reset_stop()`、`deploy()`。预期 init 命中 ready 而非 fail、`INIT_RESULT=2`、原返回码=0、DDR normal=1、全bit完成且 EOS=1、postconfig和冷CSR默认值核验通过、app ELF 入口与下载身份相符。任何返回码、断点、DDR/PL/EOS/CSR或身份不符都停止；仅允许原控制器门禁内对本控制器CPU0执行失败停止和清理自有断点，不复位或操作他人会话。
3. **RUN与结果**：adapter必须使用冻结 S2BU/1.1 字节帧和原Host READY身份校验，分开记录 `OP_WEIGHTS` 与 `OP_RUN`。RUN负载严格是两个u32 timeout和519168B INT8_CHW_416；heads仍为5070/20280字节。预期记录保留session/frame/result_seq/repeat/UART sequence、原始epoch/frame/status及PS ticks。超时、epoch/frame不匹配、物理状态不安全、UART失败或日志满时保留当前owner/pending、未ACK终态和原始日志，不自动ACK、reset、释放或重试。
4. **冻结和双读导出**：只有确认安全CSR、CPU1 stopped、run_active=0、PL没有owner或AXI/first pending且PS消费者已停后，才可门控停止本次CPU0并核验停机状态。随后用APU `mrd('--value', address=..., size=..., word_size=4)` 读取header 36 words和记录区46000 words，两块组成一次全区读取，重复第二次。SDK若不能一次支持该范围，必须先验证受控分块读取的完整性；不猜限制值。两份全区逐字节相同且前后CSR/CPU/run_active保持一致才打包为双读文件；失败时保留已读原始字，不生成解析通过结论。
5. **解码、停止与恢复**：解码命令必须显式传入本次派生 `SOURCE` SHA 和 `run_config.json` 的非零seed。解码或身份失败时保留双读原件，停止后续请求。若安全核验、stop或导出失败，保留CPU/CSR/owner/pending的实际状态；不发ACK、不复位、不释放、不重试，并把当前控制权和证据交还原会话负责人。仅对这次受控会话中的CPU0使用已有 `controller.call("cpu0.stop...", controller.targets["cpu0"].stop)` 并用 `gate()`/`state()`确认；不能停止其它CPU/会话。

每次复现必须新建硬件RunId；本节所列离线命令是该次构建的真实运行命令，旧RunId按规则拒绝覆盖。新RunId、配置、调试路径或链接环境改变后，必须重新生成并核验ELF/map SHA，不能假定其与r11/r12的字节身份一致。r01–r12 seed/session都未预留给硬件，使用前须另行预留互斥且不回绕的范围。上述计划仍为 `PLAN_ONLY`，不构成硬件ready或授权。

交付清单绑定实际源码 SHA、派生 app SHA、ELF/map SHA、冻结 2B/XSA/model/BSP 来源、工具版本与限制。`check_stage_delivery.py --mode evidence` 的 `CHECKS_OK` 只表示包装与哈希绑定通过，不代表 ELF 已上板运行。
