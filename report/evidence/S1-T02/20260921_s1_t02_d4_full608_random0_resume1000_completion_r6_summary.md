# full608 random=0 恢复训练完成记录

- 运行：`s1_t02_d4_full608_formal_r9_resume1000`
- 工作流：`resume`，从 `yolov4_5class_608_formal_r6_random0_1000.weights` 的第 1000 步恢复，seed=`424242`。
- 结果：观察到 `1001..6000` 共 5000 个更新步，工作流退出码 `0`，Darknet 退出码 `0`，报告状态 `EXECUTED_REVIEW_REQUIRED`，错误为空。
- 输入绑定：manifest、train/valid 清单在 preflight、before child、after child 三个采样点一致；manifest SHA-256 为 `FD60E7A67161F242276A1B97B09AD07C0D7F41D30067266BB99620ABE6D7ED74`。
- 权重：`6000.weights`、`final.weights`、`last.weights` 均为 256,102,140 bytes，SHA-256 均为 `1C1A4237F69853A7C1813C40F792FC7F3F5B5F1949AACE4869D700FC8589B152`。
- 原始报告 SHA-256：`80DEC8B6B5D2E5061B4D34A85A9140DF1E66C4511D23B6CD630F1AC1EA881837`。
- 原始日志 SHA-256：`2F422827E155FB3F7C7913DD54D2E1172414E64D8BB0B2E63AEBF0A55E897065`。

该记录不代表精度、泛化、INT8、资源、板上验证或阶段1通过；这些仍需独立复查和后续评估。
