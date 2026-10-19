# T18 正式模型 R02 证据绑定审计

## 范围与结论

本目录只审计并恢复原正式运行 R02 的三项历史源码绑定，不重跑硬件或模型，不修改 R02 原始目录、仓库代码或 HEAD。原运行结果文件记录 `PASS_MODEL_CORPUS_AND_STRESS_ONLY`、109 个冻结输入、1000 次连续压力、`native_exit_code=0`，结束 epoch=1109、sequence=111；此处按原结果记录其 PASS，不扩大为 G4/G5 或模型语义独立复核结论。

针对原 `delivery_manifest.json` 执行只读 evidence checker，结果为 `CHECKS_FAILED`，完整输出保存在 `original_checker_failure.txt`，退出码 2。错误只有原清单 files[9240]、[9241]、[9243] 的当前工作树源码 SHA 漂移。其他原清单条目在这次检查中未报错。三项原 SHA 均在 Git 历史中找到完全匹配的 blob，原字节快照存于 `source_snapshot/`；提交、blob、路径、原 SHA 与快照 SHA 见 `source_blob_lookup.json` 和 `original_binding.json`。

## 两个 source_commit 字段

原 `delivery_manifest.source_commit` 记录 `50d68308ae6431775cff99c135628cd31773dc74`；原 `orchestrator_result.source_commit` 记录 `e9fac6cbb1a0b7b60cd33e348dd1d304388de043`。二者都是各自文件中实际记录的不同 commit 值。本审计不将其等同、不推断它们指向相同运行源码，也未以这两个字段证明该次上板运行的全部源码身份。对三处漂移源码，已独立证明的是原 SHA 与所列 Git 历史 blob 精确相同。

## 检查边界与限制

新 `delivery_manifest.json` 的 `source_commit` 绑定本次只读归档所用的仓库 HEAD `54e6c8d607d9bbf3479d71ff820880aa2653c9ba`。运行 checker 得到 `CHECKS_OK` 只表示新审计包路径、文件枚举和 SHA 绑定通过；不证明 T18 模型语义、上板结果或 2B 阶段验收通过。原 9104 个运行文件仍在原目录，本审计未复制、改写或重新解释原始大文件。

当前工作树三个同名源码 SHA 分别为 `17c35429833c7267f35479caf5704e123127f1c637470acb210d429f3507eced`、`dbd1de2241518e679312746a7386c7e5fb1a5a2e242b88dff052b1ca8907b0c6`、`629c0595d0f415868d60cecd72358a98ab6cc2c1fefdc0ce12ab780e43c91794`。新包用历史快照保存原绑定，不覆盖原 manifest 或当前源码。
