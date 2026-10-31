# R03 M3 协议顺序门禁独立审查

## 结论

**PASS（仅限本地执行协议、单步/捕获收据衔接与隔离 mock 范围）**。本次复审的冻结版本可阻止 restore 在 before 捕获开始或留下半包后执行，也按 setup → restore → before → event → after 单调推进。close 可在任一阶段请求一次。此结论不代表本轮获得硬件授权、初始就绪、M3 测量结果或板级通过。

## 核验范围与冻结身份

只读核验了 `m3_w02` 的五个冻结文件；并读取 `r03/m3_pair.py` 中 capture 返回值、manifest 写入与 v2 校验逻辑，未修改源文件或 Git 状态。

| 文件 | SHA-256 |
|---|---|
| `owner_guard.py` | `af8ddf0c5eecd6d2f289a31568e06d1e8905daa9855c639073477b24bd629920` |
| `run_step.py` | `2c5fe46adb306d08771416f7b089ae2929e7d54f1e1f5fc66e52315734645ccf` |
| `capture_phase.py` | `675cf2ccabd838d3c8cd7354b7843a840ea42c7a282f0b87415a80c767716011` |
| `test_owner_guard.py` | `8e14a6359303194ba9e1498916bd586ee0a82f20bd7ffe0c19724acdc9c2cc3b` |
| `hold_hw_server.py` | `e3ba842ee8f22229b73c49d54aec06c3cb84b914bc6235c12a1b84dfdddcb222` |

实际读取到的五个文件 SHA-256 均与任务给定值一致。

## 结果依据

- `owner_guard.assert_protocol_transition()` 在 `run_step.execute_step()` 和 `capture_phase.run_capture_phase()` 中、所有权检查及 runner/capture 调用前调用。setup 要求后续阶段均无执行痕迹；restore 必须有当前租约下的 setup PASS，并拒绝 restore 自身重复痕迹及任何 before/event/after 痕迹；before 必须有 setup、restore PASS；event 必须有 before 的有效 CAPTURED 收据且无 after 痕迹；after 必须有有效 before 与 event PASS。阶段时间戳按 UTC+8 解析并校验顺序。close 可随时执行，但只能有一次，且先前已存在 close 痕迹会阻止其它步骤。
- “阶段痕迹”包括收据、launcher 目录、捕获输出目录与 guard 文件；普通文件、目录、符号链接或路径不可访问都按已存在/失败关闭处理。因此 before 只有输出目录、只有部分 guard、或 guard 无法解析时，restore 会在 owner 查询和 Tcl runner 之前拒绝。setup 也拒绝已出现的后续阶段痕迹。
- 单步收据要求 schema/step、当前 lease 路径及 SHA、RunId、端口及配置文件 SHA、Job 名称、租期内 UTC+8 时间、前后 owner PID 归属、PASS、语义/进程退出码为 0、必需 marker、无 runner/postcheck 错误。捕获收据要求同一执行身份、前后仍由同一 Job PID 监听、`CAPTURED` 返回目录及 SHA，并核对 `capture_manifest.json`、其 SHA-256 旁证和精确字节数。
- 实际 `m3_pair.capture()` 返回 `status/directory/manifest_sha256/read_sha256`；`directory` 与门禁拼出的 `run_dir/capture_<phase>` 一致。它写入 v2 manifest 和 `sha256=… / hash_basis=worktree_disk / bytes=…` 三字段旁证，与门禁的校验格式相符。真实 core 在返回 `CAPTURED` 前检查两份固定长度读回、相同 SHA、marker、错误文本、附属文件摘要及 v2 launcher 元数据；capture wrapper 再将返回的 manifest SHA 绑定到本阶段 guard。该收据链是本机一致性门禁，不是对抗篡改的数字签名。
- 租约路径限定 `report/evidence/R03-M3/m3_pair_YYYYMMDD_r03+`，拒绝准备用 r01/r02；租约 schema 精确键、明确 UTC+8 时间、最长 9 分钟、`max_seconds` 不超过 520。holder 在运行前写 `server_start`，执行预算取 520、租约预算与剩余租期减 10 秒的最小值。它仍只表明本机执行门禁，不替代外部 OFFER/授权/就绪核验。

## 验证

- 源文件精确路径与 SHA-256 核对：成功，退出码 0。
- `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B test_owner_guard.py`（工作目录为 `m3_w02`）：`Ran 42 tests ... OK`，退出码 0。包含完整 mock 正序 setup → restore → before → event → after、before 缺 restore、restore 遇 before 目录/半包 guard、event 缺 before、after 缺 event、前序身份漂移及 fixture 收据不能解锁真实 core runner 等反例。测试输出目录由临时夹具创建并清理；测试中的 PID、监听与 runner/capture 均为 mock，未连接 socket。
- 未启动 XSDB、hw_server、Tcl 或硬件；未读写被审源之外的任务材料；未进行 Git 写操作。

## 限制

PASS 只说明冻结实现的本地顺序门禁与 mock 契约符合本次审查范围。真实 Windows Job/端口监听、厂商工具、板卡状态、外部租期授权与实际采样结果均未在本次执行。