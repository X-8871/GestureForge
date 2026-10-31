# C3 计数器与 GT 快照采集核心

本目录补充 `c3/analyze_frame_period.py` 的采集端。`collector.py` 只通过显式注入的 `read_counter()`、`read_gt()` 回调执行同步读取；每轮固定按 `GT_before → counter → GT_after` 取样，并输出既有 CSV 列：

```text
sample_index,event_kind,sample_kind,counter_type,counter_modulus,counter_value,clock_id,gt_before,gt_after
```

仅支持 `counter_type=monotonic` 和 `sample_kind=counter_snapshot`。GT 必须在无符号 64 位范围内；相邻 bracket 要满足 `current.gt_before >= previous.gt_after`，等于允许，违反时以 `GT_ROLLBACK` 失败且不追加无效样本。单调计数器或 GT 回退/回绕均失败关闭；不以模运算推断回绕。每个有效快照留在结果中；容量满、达到轮询上限、GT 无进展或回调失败均以非目标状态返回，已采样本仍可保存。

事件累计数为 `last_counter_value - first_counter_value`。`elapsed_gt_ticks` 是首末 `GT_before` 的 start-to-start 附注；采集时长门限及 `duration_target_reached` 统一使用 `elapsed_gt_bounds.lower >= min_duration_ticks`，该下界由首末读取 bracket 保守计算。`max_poll_gap_upper_ticks` 按相邻样本 `current.gt_after - previous.gt_before` 的最大值计算。

## 离线运行

请在 `D:\codex-worktrees\w6\legacy_codex_20261031\c3_collect` 目录执行以下相对路径命令。命令行只提供固定合成演示；不接受来源参数，也没有硬件、UART、JTAG、socket 或 vendor 工具入口：

```text
python -B collector.py --demo
python -B collector.py --demo --csv samples.csv
python -B -m unittest -v
```

演示来源固定为 `synthetic`，核心 API 的 `origin` 默认也是 `synthetic`；只有集成代码显式指定时才可标作 `host_callback_unverified`。状态 `TARGET_REACHED` 只表示两个采集门限达到，不是 C3 实测、T6-A03 或阶段验收。CSV 使用独占创建；目标已存在时抛出 `FileExistsError`，不覆盖旧数据。`write_csv()` 可导出成功、未达标或失败结果中已保留的原始样本；既有 CSV schema 不含采集状态，调用方必须把同一 `CollectionResult.to_dict()` 状态摘要与 CSV 一起保存。禁止单独凭 CSV、分析器的 `captured` 输入标签或非空周期值宣称一次完整的 `captured` 采集。CLI 将状态摘要输出到标准输出；库调用方应将摘要作为旁文件持久化。可由 `SnapshotCollector` 在离线测试中注入确定性回放回调。

## 后续集成边界

- 物理事件定义、测点、时钟身份、GT 频率校准与误差预算继续以 [`../c3/方法学.md`](../c3/方法学.md) 和 DSH 的冻结证据为准。`event_kind` 是调用方描述，不能证明寄存器实际映射到所填物理事件。
- 后续 `read_gt()` 适配必须读取同一块板上已校准 GT，并保证一致的 64 位读数；若硬件总线读数可能撕裂，HI-LO-HI 重试由适配方实现。禁止用宿主机时钟冒充板上 GT。当前核心无法从任意回调认证时钟来源，摘要会把回调身份/频率声明标成调用方未验证。
- 真实相机周期必须在有效 VSYNC/SOF 边沿对应的单调硬件计数器处测量；S2MM、READSTR、HDMI VSYNC、推理完成和结果发布各自独立。没有证据绑定测点/计数器身份或 GT 校准时，真实测量仍为 `BLOCKED`。
- 这是运行在宿主 Python 环境中的采集核心，不是在 Cortex-A9 上直接执行的固件。后续集成方须在适用 OFFER/授权下提供可信 `read_counter`/`read_gt` 回调或由目标固件导出的原始样本；不得把任意回调的调用方自报身份提升成已认证 `captured` 来源。核心仅使用 `synthetic` 或 `host_callback_unverified` 来源标签，不能自行生成 `captured` 标签。
- `counter_snapshot` 记录的是计数器读取与 GT 读界，不是无损逐沿时间戳，也不是 `event_bracket`。它不能单独给出逐沿 jitter、漏沿证明或 `event_bracket` 区间。需要这些结论时必须由固件保存无损逐沿时间戳/FIFO，并另行审查。
- 合成测试只验证序列、边界及与现有 CSV 分析器的互通。本轮真实板上回调、测点/计数器身份和 GT 时钟校准均为 `NOT_RUN`；真实采集保持 `BLOCKED`。
