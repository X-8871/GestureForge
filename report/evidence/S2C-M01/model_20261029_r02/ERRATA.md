# S2C-M01 r01 manifest 哈希转录勘误

2026-10-29（UTC+8）门禁检查r01、r02时发现：r01失败记录manifest中，`D:\wb-out-r3\task_l0\profile.json` 的 `worktree_disk` SHA-256转录少了一个 `f`。原r01失败manifest及其门禁失败输出均保留，未覆盖、未重跑r01。

| 项目 | 值 |
|---|---|
| r01 manifest声明值 | `1318675585a618be650629efb6c83b125c5befb5dbfc691fc60759eafea00e73` |
| 文件实际值 | `1318675585a618be650629efb6c83b125c5befb5dbfc691fc60759efaea00e73` |
| 检查结果 | r01 manifest 1项 mismatch；真实退出码1；原始输出见同任务 `model_20261029_r01/HASH_BASIS_CHECK_FAILED.md` |
| r02处理 | r02成功模型manifest独立从磁盘计算profile哈希；其余hash条目仍逐项按 `worktree_disk` 核验。 |

r02结果由 `model_20261029_r02` 单独运行生成，退出码0。r01只记录作用域变量错误的失败，不承载模型结果。此勘误只说明清单哈希录入错误，不改变profile文件或模型计算。
