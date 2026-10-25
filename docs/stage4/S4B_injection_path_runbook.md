# S4-B 注入通路运行书（离线已验证；板上命令 NOT_RUN）

状态：离线部分已实现并验证；**板上注入（4-D）未执行**。本文档中的板上级命令是**待核验模板**，其中的
设备路径/ELF/串口必须由 4-D 执行人按现场真实产物填入并核对，**不得照抄占位符、不得猜地址或 ELF**。

## 1. 范围与前提

- 覆盖：阶段4 单帧注入及有限序列/背压/故障语义。输入帧在 `consumer_start` 前执行 invalidate + DSB；PL done 后对输出 heads 先 invalidate + DSB 再读取，两处维护分别执行。
- 不覆盖：真实摄像头采集（等阶段3）、UART 协议变更（`s2bu/1.1` 不变，方案 B）、PL 位流构建。
- 前提：2B 已冻结并释放硬件；当前硬件归属以现场会话核验为准（阶段5 正在板测）。4-D 开始前必须取得**正式实物授权与硬件会话交接**（见 S4-A 文档 §10），并用 `verification/handoff_check.py` 核对让出/认领记录。

## 2. 契约与权威

| 对象 | 权威 |
|---|---|
| 输入帧/结果契约 | `docs/stage4/s4b_shared_input_result_contract.json`（`s4-shared-io/1.2.0`，r06，`DRAFT_PENDING_REVIEW`） |
| 缓冲地址/长度/所有者/缓存方向 | `docs/stage4/S4B_stage4_address_map.json` |
| 结果记录字段 | `docs/stage4/s4a_stage4_g0_fields.json`（r06） |
| 板级接口 | `s2b-physical/1.0.0`（2B 冻结）；UART `s2bu/1.1`（方案 B，扩展关闭） |

## 3. 离线构建与验证命令（已执行，可复跑）

```bash
cd D:/codex-worktrees/w4
# 严格编译（0 error / 0 warning 是硬门槛）
d:/mingw64/bin/gcc.exe -std=c11 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wshadow \
  -I vitis/stage4 vitis/stage4/s4_inject_frame.c vitis/stage4/s4_inject_frame_host.c \
  -o tmp/4/S4-FIX-01/<run_id>/build/s4_inject_host.exe
# 单帧 + 小图 + 有限序列 + 故障序列 + 地址图重叠正/反例
python -B scripts/stage4_s4b/run_s4b_injection_offline.py --run-id <run_id> \
  --evidence-dir report/evidence/S4-B/<run_id>
# 单元/集成测试
python -B -m unittest verification.test_s4_inject_frame -v
# 证据清单自查
python -B verification/check_stage_delivery.py --mode evidence \
  --manifest report/evidence/S4-B/<run_id>/delivery_manifest.json
```

离线退出语义：host 的进程退出码 = 第一个非 `try` 操作的 `s4_inject_status`；`0` 表示全部成功。
每条错误都有唯一的 `status_name` 与稳定 `field/reason`，驱动逐条核对期望码（详见 `injection_offline_summary.json`）。

## 4. 状态机与所有权（实现依据）

事件顺序（契约 `input_frame_contract.events.order`）：
`producer_write_start` → `producer_write_complete` → `cache_flush_by_producer` →
`ownership_publish_to_consumer` → `consumer_invalidate` → `consumer_start` →
`consumer_done` → `buffer_release_to_producer`。

- 冻结 2B BSP 在 `w2b/vitis/s2b_inference_app.c:71` 声明 32 B 硬件缓存行参数；实现中的 64 B 是保守维护对齐策略，不代表 Cortex-A9 物理缓存行大小。
- 生产者：写完 → DCache flush（写回，64 B 外对齐）+ DSB → 才可发布所有权。
- 消费者：所有权发布后、读取前 invalidate（64 B 外对齐）+ DSB；读取完成并确认停止后释放才可以被覆盖。
- PL 输出 heads：真实 PL done 后先 invalidate（64 B 外对齐）+ DSB，再读取 heads；此输出维护独立于输入帧事件序列。本轮 host mock 不代表 BSP/PL 已接通。
- 任一事件缺失即该帧不可消费；**不得用超时推断完成**。
- 多缓冲数 ≥ 在途消费者数 + 1；禁止覆盖仍被持有的帧（`ERR_NO_OVERWRITE`）。

## 5. 注入模式的时间语义（不得违反）

- `source_kind=file_injection` / `synthetic`：`capture_time_available=false`，`capture_time_ns=0` 哨兵且 `measurement_scope.unavailable_fields` 必须包含该字段；注入起点只记录在 `injection_start_ns`，**不是采集时间**。
- 提供了 `capture_time_ns` 的注入帧会被拒绝（`ERR_CAPTURE_TIME_FORGED` → `19`）。
- `camera` 模式必须提供非零真实 `capture_time_ns`，`capture_time_available=true` 且 `unavailable_fields` 不得包含它；否则拒绝。
- 当前 RAW 注入契约要求 `BGR888`（每像素 B/G/R）；平台 `byte_order=little` 与像素通道顺序分离。冻结 D2 必须先逐像素 B/G/R→R/G/B，再 resize/归一化/量化。
- Stage3 旧证据中的 `source_byte_order=BGR` 仅表示像素通道顺序，映射为 `pixel_format=BGR888`、`channel_order=[B,G,R]`；不映射成平台 `byte_order`，旧证据不改写。
- **运行期状态 `NOT_IMPLEMENTED`**：现有 C 注入描述符仅接受 RGB888/RGB565/GRAY8/INT8_CHW_416，C enum 值 `1=RGB565`；G0 readiness 的独立候选 `mailbox_pixel_format_code=1` 映射到 BGR888，但没有 mailbox PS driver 执行该映射，禁止直接 cast。PL RAW 读取无通道重排，且当前 RTL 源码未发现 `s4b_preproc_frame` 的顶层实例。本文的构建及板上模板在 mailbox 映射实现、BGR888 实现、PL 顶层接入、独立审查与适用验证完成前不可用于声称或执行 BGR888 RAW 验收。
- legacy `RGB888`/`RGB565` 描述符路径仅按其自身实现范围使用；`INT8_CHW_416` 严格限定为 416x416 三平面 CHW INT8（519,168 B），只覆盖网络+后处理；直接写显示缓冲只覆盖显示。

## 6. 4-D 板上注入命令模板（**NOT_RUN**，须按现场产物填写并核对）

> 以下命令在**获得硬件授权后**由 4-D 执行；本轮未执行。变量必须替换为现场核验过的真实值：
> `ELF`=新构建的 PS 应用 ELF（含 SHA-256）、`BIT`/`XSA`=本次位流与平台、`PORT`=当前归属的 COM 口、
> `FRAME_FILE`=待注入帧文件、`RUN_ID`=新 RunId（不得复用）。**不得使用占位符充当真实值**。

```bash
# 0) 授权与会话核验（只读，必须 PASS 才继续）
python -B D:/FPGA_Competition/verification/handoff_check.py --worktree D:/codex-worktrees/w4 \
  --record <当前硬件负责人给出的 11 字段记录> --json

# 1) 记录产物身份（必须先记后跑）
sha256sum "$BIT" "$XSA" "$ELF" "$FRAME_FILE"

# 2) 烧写/加载（易失；按 2B 冻结的部署规程，禁止 QSPI 非易失写）
#    具体 xsdb/vitis 命令沿用 2B 冻结部署脚本；本阶段不另行发明烧写流程。

# 3) 启动 PS 应用（方案 B：UART 只传既有字段；时间/丢帧/过期写 PS 日志）
#    COM 口与波特率 115200 8N1 按现场会话核验后使用
#    <SERIAL_TOOL> --port "$PORT" --baud 115200 --capture <run_id>/uart_raw.bin

# 4) 单帧注入（PS 侧）：装载 → producer flush + DSB → 发布 → PL 读取输入帧前 invalidate + DSB → consumer start → 等 PL done → 输出 heads invalidate + DSB → 读 heads → 确认消费者停止/复位 → 释放
#    由 ELF 内实现调用；每帧必须记录 (session_id, frame_id, result_seq, frame_integrity, injection_start_ns)

# 5) 导出证据：heads 原始 INT8（head13 5,070 B / head26 20,280 B）、逐框结果、PS 侧日志
#    离线对拍（不得跳过上游 SHA）：
python -B verification/s4_replay_compare.py --actual <ACTUAL_DIR> --run-id <RUN_ID> \
  --json-out <新建的 REPORT_JSON>

# 6) 停止与恢复：停止消费者 → 释放所有在途缓冲 → 复位会话（seq/epoch）→ 记录终态；
#    失败时先保全原始日志与串口原字节，恢复只由当前硬件持有者执行。
```

## 7. 判错分层（4-D 使用）

预处理不一致 / PL 整数头不一致 / PS 后处理不一致 / 模型识别错误分别计数；逐框比较数量/类别/坐标/分数；
不得用最高类别代替逐框比较；不得把错误记成零框成功。

## 8. 已知限制

- 离线仅用主机 mock DDR/cache 与 gcc 编译；缓存回调只验证离线状态机与可见性建模，**不代表真实 PS/BSP 接通**；未接板卡、未接真实串口、未跑 PL，PL resize/letterbox 输入预处理也未接入。
- 本注入驱动未执行板上注入、真实 UART、摄像头、PL 时间/期限/吞吐或 S4-C 全量回放。历史 `report/evidence/S4-C/s4c_replay_20261021_r05/` 已有 109/109 纯 CPU golden 回放 PASS；其范围限于冻结 heads 的解码/NMS，不能作为本注入驱动、D2 预处理或真实 PL/PS 输出的实测结论。
- 地址图中 `unresolved_regions`（阶段3/阶段5 未授权区域、显示缓冲精确边界）不得被本阶段访问或猜地址。
- 契约中 `stale_limit_ns` 仍为 `DRAFT_PENDING_APPROVAL`（草案 200 ms），正式批准前不作为验收门槛。
