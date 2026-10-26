# S4-T26 黄金来源与双样本门改绑决策

- 决策日期：2026-10-26（UTC+8）
- 批准依据：Wong 在任务 S4-T26-GOLDEN-REBIND 中明确批准的范围变更。
- 适用工作树：D:\codex-worktrees\w4，分支 stage4-infer-prep。
- 决策状态：已批准；只调整 task-26 离线 raw-head 与阳性检测验证样本绑定。

## 黄金来源

r03/r04 Darknet 控制实验及原始失败证据继续保留。r04 的当前 Darknet/hook 前向退出码为 0，但 layer 29/36 量化输出与 T29 test_fist_000 冻结张量不逐字节一致（2,929/5,070 与 10,358/20,280 字节不同）。因此当前 Darknet/hook 未复现 T29，不作为 task-26 黄金来源；不得据此生成或覆盖黄金。T25 冻结分片与 T29 张量记录是本决策指定的黄金字节来源。

## 样本绑定

| 门 | 样本 | T25 索引 | 图像 SHA-256 | 目标 |
|---|---|---:|---|---|
| raw_head_gate | approved_no_hand_001 | 102 | 10f1f104343cae97abf817316de3a75bacb646da6c686a2204eedcc2611f34f4 | raw head13/head26 逐字节对拍；负样本只关闭 raw-head 门 |
| positive_detection_gate | test_fist_000 | 0 | 6dbd72693bc6ad2af6121ffe95e2ee5e9c14597a4c4d16a6db8cdf07d8e43b0e | 阳性真实前向及 D9/NMS 检测输出覆盖 |

原校准图 98529267-1eda-43a6-8e38-245947ecb312.jpg（SHA-256 c116ba1d…35ee70b）保留为历史记录，状态 NOT_USED_HISTORICAL，不再作为 G0 原始 head 门。负样本不得替代阳性检测/显示覆盖。

## 提取与完整性

从 T25 冻结压缩分片以 zlib 解压，在 T25 索引声明的 byte_offset/byte_length 处原样切片 layer 29 与 36。必须分别验证压缩分片 SHA、解压整流 SHA、T25 tensor SHA 与 T29 tensor_sha256；禁止重新量化或手工构造张量。新 .bin 文件与哈希见同 RunId 的 golden_materialization_manifest.json。源 T25/T29 索引、分片和历史 activation report 均只读且原字节不改。

## 执行顺序与结论纪律

材料化及文件 SHA 全部通过后，才可运行 sample_102 的真实前向逐字节对拍、sample_000 的真实前向与 D9/NMS、单字节输入扰动负向对照及 PNG IMREAD_UNCHANGED 像素检查。任一前向或对拍失败时保持 BLOCKED，不生成 task-27 输入。task-27 结果（若生成）须标记 replay_only，并明确区分上述两道门；旧校准图为 NOT_USED_HISTORICAL。

本决策不解除 ENABLE=0，不闭合 RAW 系统 G0，不表示 P、4-D、G3 或 G5 通过。
