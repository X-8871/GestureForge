# S1-T02-D4 formal_r3 CPU RAM 失败证据

- 任务：`S1-T02-D4-FORMAL-R3-CPU-RAM-FAILURE-EVIDENCE`
- formal workflow 报告：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_formal_r4_subdiv64\reports\workflow_formal_r3.json`
- formal 日志：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_formal_r4_subdiv64\workflow_formal_r3\train.log`
- 状态：**EXECUTION_FAILED**，退出码 `2`

## formal_r3 结果

formal_r3 使用 seed `424242`、`subdivisions=64`、`random=1`，日志记录到 `1164/6000`。日志尾部出现：

- `Failed to calloc ...`
- `image.c, make_image(), line #807`
- `Calloc error - possibly out of CPU RAM: Not enough space`

workflow 报告没有 `after_child`，也没有最终 `6000` 权重。1000 checkpoint 存在，大小 `256102140` 字节，SHA-256 为 `9306AA18C04DC68373DA121E9D69BE0A0D0920003C736EBF627D2361372F3CD5`。

## 隔离 CPU/RAM 诊断

`cpu_ram_diag_from_1000_r1` 从 1000 checkpoint 启动，诊断 cfg 的 `max_batches=1020`，日志实际到 `1001/1020`，随机 resize 为 `896 x 896`。总控观测到进程 private memory 约 `14.96 GB`、free commit 约 `5.37 GB` 后终止诊断。该诊断不是正式训练，未生成正式模型，也不用于阶段验收。

## 输入哈希

- cfg：`18735A7D874AADC0A4EA83DEA3C0CC9F48DB8B7233B887EEF9547D58073BF49E`
- data：`A44DB33DE0807064604296D80A95221FC2A17C78FC844DD3D7159112AE9DFAA6`
- manifest：`FD60E7A67161F242276A1B97B09AD07C0D7F41D30067266BB99620ABE6D7ED74`
- formal 日志：`05643B48CDE17893CFE6B47974BE9AFAC22BBCB48EB151B79A20767B426A7613`
- workflow 报告：`03A83190ECDECD2002C6EB853F20D4D3102047A8C4841C8DB1FB53CBA33CA127`
- diag.cfg：`C536C1BA37C6EA447455CF03C00D77903F135F95926415A47375B2CDFA026458`
- diag.data：`102464C51162FE6EF8E080C763C43A725E2400FF3750EE4A4E95EA9000A1136C`

完整路径、大小、时间、哈希及限制见同名 JSON。该证据不代表模型通过、精度通过或阶段通过。
