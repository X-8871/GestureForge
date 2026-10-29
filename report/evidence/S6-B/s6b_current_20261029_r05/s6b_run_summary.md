# S6-B 离线回归封装摘要（RunId s6b_current_20261029_r05）

- 26 条确定性矩阵和 4 项判别探针来自 `s6b_current_20261029_r03`。r03 清单中的 `src/stage6/s6_core.py` 原始 SHA-256 与本包当前工作树字节完全一致；动作层、参数装载、矩阵驱动和探针也逐项一致。
- 本包重新运行 `python -B -m unittest discover -s verification -p 'test_s6b*.py'`，保存 39 项回归输出。新增 `frame_id` uint32 检查覆盖 0、0xFFFFFFFE、0xFFFFFFFF，拒绝 -1、2^32、bool、float 和超大整数，并逐项核对非法输入前后状态不变。
- 已绑定 S6-A v1.8 JSON/规格、U6-02 r07 批准回执、阶段4 S4B r07 / 1.3.0 冻结离线契约快照及 main 统一 `check_stage_delivery.py`、`check_manifest_hash_basis.py` 固定副本。各清单逐项声明 `hash_basis=worktree_disk`，`source_commit` 固定为运行时 HEAD。
- 阶段4 r07 契约 SHA-256：`7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145`；`reviewed_commit=5f9a04a045f4aaa7516759513f660f9872cbab61`，契约冻结范围 `OFFLINE_ONLY`。契约没有独立的 `frozen_commit` 字段。
- B25 同会话 `frame_id`“大幅回退”没有数值判据，按 `BLOCKED` 登记；实现保留 B23 倒序处理，不猜复位阈值。

本包只证明离线注入和软件回归。没有板卡、JTAG、串口、摄像头、HDMI 或实时会话操作；T6-A03 仍 `NOT_RUN`，真实阶段4/5 集成仍 `BLOCKED`，不声称 G3/G4/G5。
