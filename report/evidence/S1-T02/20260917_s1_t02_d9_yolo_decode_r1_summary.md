# S1-T02-D9：tiny416 原始检测头解码参考与合成黄金测例

状态：候选1、候选2的 `CHANGES_REQUIRED` 历史及初始 `PASS` 撤回均保留。独立 Reviewer Herschel 对候选3指定哈希给出 G2 `PASS`，范围仅限 CPU 数值解码参考；本摘要/证据是 PASS 后的状态同步版本，总控 metadata-only independent re-review 仍待进行。此任务未提交。

## 交付范围

- 新增 `verification/s1_t02_d9_yolo_decode.py`：接收 13×13 与 26×26 两头 sigmoid 前 raw logits，输出复用 D6 `Prediction` 的归一化 xyxy/class score；支持 Darknet 原生扁平 entry-plane 布局及 `[3,10,H,W]` CPU tensor/嵌套序列。
- 新增 `verification/test_s1_t02_d9_yolo_decode.py`：13 项固定、合成、纯 CPU 测例；不读训练数据/权重，不启动 Darknet。通过仓库相对路径实算 D2/D6 源文件 SHA，并检查 PASS 状态、Reviewer 及审核候选哈希与证据声明一致；不依赖 `D:\` 数据盘。
- 证据 JSON：`20260917_s1_t02_d9_yolo_decode_r1.json`，分别绑定 Reviewer 实际审核的候选3哈希和 PASS 后状态同步快照哈希，另绑定 Darknet、D2/D6 与配置来源。

## 规则与黄金值

Darknet `yolo_layer.c` 核对了 `entry_index` 的 anchor/entry/row/col 平面索引，`forward_yolo_layer` 对 x/y、objectness、class 的 sigmoid 与 `scale_x_y` 仿射，`get_yolo_box` 的 exp/anchor 解码，以及检测分数为 objectness×class。实现固定 `new_coords=0`、`scale_x_y=1.05`；阈值按 D6 的 `>=`，与 Darknet `get_yolo_detections` 的严格 `>` 不同。NMS 直接调用 D6 `stable_nms`，固定类别内 IoU 0.45、每图最多 15 个。

手算黄金：13×13 头 row=6、col=6、local anchor 0 经 mask 3 映射至 anchor 81×82；tx=`ln(3)`、ty=`-ln(3)` 经 sigmoid 和 1.05 scale/bias 后为 0.7625、0.2375。原图 200×99 letterbox 至 416×205，顶部 floor padding=105；obj/class logits 均为 0，score=0.25。最终归一化 xyxy 为约 `(0.42283653846153846, 0.26146341463414634, 0.6175480769230769, 0.6614634146341464)`，测试独立比较手算有理数。

边界框逐坐标显式裁剪至 `[0,1]`，裁剪后零面积框丢弃；测试覆盖奇数补边的 floor 偏移、补边区框丢弃与裁剪边界。

奇数补边与 Darknet C 后处理有明确且预期的差异：`99×200 → 416×416` 时 resize 为 `205×416`，横向总 pad 为 211 px。D2 的左 pad 是 `211//2=105` px；Darknet `correct_yolo_boxes` 逆变换用 `211/2.0=105.5` px。测试选用 13×13 头 `row=6,col=3`、81×82 anchor，右边界在 D2 语义下为 `47.5/205`，按 Darknet C 半像素语义则为 `47.0/205`，两者相差 `0.5/205`。D9 严格采用 D2 固定像素 pad；不改 D2，也不声称奇数边界逐值等同 Darknet C 后处理。

## 配置来源更正与复审状态

只读配置核对结果：正式 D8 tiny416 与正式 D4 tiny416 cfg 的 SHA-256 均为 `5475dff0daa8ac791ffbfcd10a188aa63d146244e561d62867ac59d627725376`，两头 masks 均为 `3,4,5 / 1,2,3`。正式 D4 tiny320 cfg SHA-256 为 `92135520eeed9c77460dde4bab5bd4fd99a171cdba9849cc484bd3c02161fb94`，masks 同样为 `3,4,5 / 1,2,3`；Darknet 上游 tiny cfg SHA-256 为 `a6415c2e303f7b3647913a7bb3675f0fe7234049d8875ae7d75c01b8e4dcb854`，masks 也相同。

初始版本误把非正式 `official_darknet_seeded/cfg/yolov4-tiny-custom.cfg`（SHA-256 `4996aceacba657fb8390ac976ed0cf7cdc96085a18bd4827f05f5f2c7f300b8e`，masks `3,4,5 / 0,1,2`）标作正式 D4 tiny416 对照。该文件已在证据中明确标为非正式并排除于正式配置比较；正式配置不存在此前所称的 D8/D4 tiny416 mask 差异，不需要据此提出配置决策。

审查历史准确记录如下：候选1因正式 D4 cfg 对照路径错误（把非正式 seeded custom cfg 标为正式配置）而 `CHANGES_REQUIRED`，Reviewer 撤回初始 `PASS`。候选2已正确修复配置来源，但其 D2 文档 SHA 少一个 `f`，且测试未对 D2/D6 仓库文件实际字节做哈希绑定，因此仍为 `CHANGES_REQUIRED`。修复迭代2更正了 D2 SHA，并在仓库内测试实算 D2 与 D6 文件 SHA；解码算法未改。

D2 文档仓库内实际 SHA-256 为 `df95a8438eaa2d451b54ca3f1927c454eaef022c1f8f31a18874980f69702e57`；D6 文件实际 SHA-256 为 `e2294aef39e51e0e3f4f11efbb527be81b6b38744f34de2fbfa8f3cc1c01346f`。证据一致性测试无需访问外部数据盘即可验证 JSON 的文件路径和哈希字段都与仓库内容一致。

Herschel（multi-agent 独立 Reviewer）对候选3给出 `PASS`。其实际审核对象为：

| 候选3文件 | Reviewer 审核 SHA-256 |
|---|---|
| `verification/s1_t02_d9_yolo_decode.py` | `0be8e2dc0878116b5239a20a397f4f063de7b33c2ee38e1d0aadf1ced7d365c6` |
| `verification/test_s1_t02_d9_yolo_decode.py` | `65cbdea3ef4ef03723fa0757efe57de6d886948d0cedba73786ae5686c544157` |
| `report/evidence/S1-T02/20260917_s1_t02_d9_yolo_decode_r1.json` | `bb7f2b038be0b5a992f332d4173066a6d4efb1ec8ff4c1e34b5f50aa12325a3e` |
| `report/evidence/S1-T02/20260917_s1_t02_d9_yolo_decode_r1_summary.md` | `aad555c2dc4e9ca796daad0979b7f98bf7efdf98412f01946b3e7bea3d546e57` |

审查输出目录为 `C:\Users\22061\AppData\Local\Temp\GestureForge_D9_C3_Review_330779624f394a839f2b5d9422b0848a`。该 PASS 仅覆盖被审哈希和 CPU 数值解码范围，不代表训练、精度、板上或阶段通过。

本次最终证据快照只同步 G2 PASS/历史状态，更新测试中的 PASS 与已审哈希一致性断言，并刷新 JSON/摘要哈希；decoder 数学未改。总控后续对该最终状态快照的 metadata-only independent re-review 仍为 `PENDING`，本文不声称其已完成。

本证据不代表训练/权重成功、任何精度/precision/recall/mAP、板上验证或最终 PS/PL 接口冻结。总控的最终快照 metadata-only re-review 尚待进行。

## 验证

| 命令 | 结果 |
|---|---:|
| `$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest verification.test_s1_t02_d9_yolo_decode` | 13 项通过，退出码 0 |
| `$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest discover -s verification -p test_s1_t02_d9_yolo_decode.py` | 13 项通过，退出码 0 |
| `$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest verification.test_s1_t02_d2_numeric_reference` | 11 项通过，退出码 0 |
| `$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest verification.test_s1_t02_d2_calibration` | 5 项通过，退出码 0 |
| `$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest verification.test_s1_t02_d6_detection_metrics` | 12 项通过，退出码 0 |
| `$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest discover -s verification` | 137 项通过，最终退出码 0 |
| `python -X pycache_prefix=C:\Users\22061\AppData\Local\Temp\s1_t02_d9_pycompile_r1 -m py_compile verification/s1_t02_d9_yolo_decode.py verification/test_s1_t02_d9_yolo_decode.py` | 退出码 0 |
| `git diff --check` | 退出码 0 |
| 四个目标文件逐个运行 `git -c core.autocrlf=false diff --no-index --check -- /dev/null <file>` | 每个原始退出码 1（与 `/dev/null` 不同，属预期），四项均无空白诊断输出 |

全量测试期间曾有一次无关 S1-T01 用例在临时目录清理时遇到 Windows `WinError 32`（`immediate_5.log` 仍被占用，退出码 1）；单独重跑该用例退出码 0，随后全量 137 项重跑通过、退出码 0。没有改动该用例或其所属文件。详细尝试记录见证据 JSON。

未启动额外 GPU/数据遍历任务，未调用真实 Darknet，未提交。原有工作区改动保持不变。

执行期间 HEAD 从任务指定基线 `bb0496092d9872d796e23ef4d5f60dac24dc3134` 前进到 `4a73619587d5ee872d37fc079f758480ed8a8cb0`（2026-09-17 12:36:19+08:00）。只读核查显示该并发提交仅更新 `.codex/STATE.md`，未包含 D9 文件；本任务未创建该提交，且未回退或切换仓库状态。
