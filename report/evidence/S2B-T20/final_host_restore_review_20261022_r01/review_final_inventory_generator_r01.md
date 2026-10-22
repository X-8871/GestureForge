# 最终冻结清单生成器 G2 审查 R01

- 结论：**CHANGES_REQUIRED**
- 被审文件：`tmp/2B/prepare_final_freeze_20261022.py`
- 被审 SHA-256：`3f42cc278cfad03a69912da5001e538cdbb2811b9956badb0bce58a447e5beb4`
- 审查基线 HEAD：`d569dfbbdbe1c75b552300dedcc6d544e9d38908`
- 文件 SHA-256 已独立复算；AST 静态解析通过。未运行生成器、硬件、`check_stage_delivery.py` 或其他运行态操作。

## 已核范围

- 生成器先拒绝已有固定 RunId，再校验上游后才新建目标目录；文件以独占创建方式写入，不覆盖历史证据。
- PS r02 顶层状态、退出码、空 `cleanup_errors`、source commit、内层验收状态，以及部署、UART、256B cache、真实 weights、sample000、动态 ACK/IDLE 步骤与恢复输入绑定，均有明确门槛。实际生产 wrapper 写出 `raw_logs` 而非 `outputs`；当前版本已读取 `raw_logs`，并显式绑定 wrapper 的 `orchestrator_result.json`。
- PS 入口分支状态和步骤名称与真实 runner 一致；safe-IDLE 为小写 `pre_reset_safe_idle`，BootROM 分支按状态名记录。清单不会把 PS 限定验收描述为完整 G4/G5。
- 上游模型、R08、R12、历史审查/失败状态、源码、正式接口文档、R04 恢复资产和固定输入候选均进入 `file_specs` 哈希绑定。物理接口与 UART 文档的路径、版本、SHA 和 `frozen=true` 字段与文档现有标头一致。
- 新 RunId 中将重建 ELF 逐字节复制并校验预期 SHA；候选清单明确保留 CHANGES_REQUIRED、UNKNOWN、BLOCKED 等状态，不自行判定 G4/G5。
- `inputs_manifest` 和 `delivery_manifest` 字段及角色符合 `check_stage_delivery.py` 接受的结构；生成的证据目录文件清单在静态检查下与预期输出相符。实际 checker 尚未运行，故此处只判断结构，不声称 CHECKS_OK。

## 阻断项

生成器没有绑定或核验 R12 r05 的实际隔离重放回执：`tmp/2B/S2B-T18/csr_r12_finalize_replay_20261022_r05/replay_result.json`。我检查该文件，其记录了 `hardware_access: NONE`、`original_r12_mutated: false`、`finalizer_result.status: CHECKS_OK`、空 `errors`、克隆 RunId 以及 `manifest_sha256`。当前生成器只绑定 report/evidence 下的 R12 `orchestrator_result.json`、`acceptance_result.json` 和 `delivery_manifest.json`；它仅依据复制包内 `orchestrator_result` 的 PASS/退出码确认 R12，并在清单中声明 `ISOLATED_PACKAGE_REPLAY_NOT_A_NEW_BOARD_RUN`，但没有把支撑该隔离重放声明及实际 finalizer/checker 结果的 `replay_result.json` 纳入候选清单。

修复条件：将上述 r05 `replay_result.json` 作为输入绑定，并校验其 `clone_run_id` 与 r05 RunId 一致、`hardware_access` 为 `NONE`、`original_r12_mutated` 为 `false`、finalizer 状态为 `CHECKS_OK` 且无错误，并校验其中的 manifest SHA 与绑定的 R12 r05 `delivery_manifest.json` 实际 SHA 一致。这样能保留原 R12 证据状态并把离线重放与真实板测边界一并封存。

## 复审限制

PS r02 当时仍在板上运行；未读取其可能变化中的运行结果，也未据此判断板测是否 PASS。生成器本身未执行，故不对实际生成物、磁盘写入或 checker 的运行结果作断言。修复后应以新 SHA 重新冻结并复审。
