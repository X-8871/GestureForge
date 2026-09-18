# D6 robustness 数据可用性盘点 R1

状态：BLOCKED_NO_INDEPENDENT_ROBUSTNESS_ROWS_IN_APPROVED_MANIFEST。

本次只读盘点绑定当前批准 manifest：D:/FPGA_Data/HaGRIDv2/manifest.csv，SHA-256 fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74，158,680 行。行数为 train 118,001、val 15,195、官方 test 25,484；manifest 中没有 robustness split。现有 person_id 和 session_id 均未跨 train/val/test。

目标类图像分布（train/val/test）为：fist 23,543/2,999/4,998；palm 23,710/2,999/4,997；one 23,872/2,999/4,997；two_up 22,688/2,999/4,996；three 22,721/2,998/5,000。no_gesture 文件夹行数为 1,464/199/496，已全部属于既有 split，不能因此视为独立的 robustness non-target bucket。

已批准的 5 张真实 no_hand 图像为 train 3、val 2、test 0；它们也已经属于现有 split。manifest 没有 multi-hand、occlusion 或 small-target 的图像级条件字段/审计标签。按 Wong 已批准的 person/session 完全隔离要求，本 manifest 不提供可直接构造的独立 robustness set。

因此，当前不能运行或报告 robustness 结果。需要额外的独立样本来源并完成类别/条件审计；不能把现有 train、val、test 图像重新贴成独立 robustness 样本。本盘点未递归枚举未出现在 manifest 中的文件，未打开或标注图像，也未运行模型或生成精度指标。

机器报告：20260918_s1_t02_d6_robustness_inventory_r1.json。
