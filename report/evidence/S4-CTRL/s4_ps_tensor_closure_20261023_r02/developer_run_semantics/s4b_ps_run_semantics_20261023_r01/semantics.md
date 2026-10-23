# S4-B PS运行结束语义

依据r12唯一锚点派生源码：`tmp/4/S4-B-REAL-01/s4b_ps_tensor_20261023_r12/bundle_extract/bundle/workspace/infer/src/s2b_inference_app.c`，SHA-256为 `1be7a551e26f61be1327cdb56672b08d86d17d16433ac405ebd263d5f35bf436`。 `infer_one`仅在`RESPONSE_OK`、UART发送成功且ACK成功时返回成功；其余已记录失败路径会令`service_request`返回0，主服务循环随即结束。因此status 1要求末次session的每条记录均为上述成功组合；派生app也不可能在一条失败attempt之后继续写入记录或新session。 `end_run(0)`写status 2并保留已提交记录；未提交attempt可造成无失败记录的partial。

原始单测命令、退出码和stdout/stderr见同目录文件。
