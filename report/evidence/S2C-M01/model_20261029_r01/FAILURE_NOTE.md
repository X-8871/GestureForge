# S2C-M01 首次模型运行失败记录

RunId：`model_20261029_r01`  
执行目录：`D:\FPGA_Competition\w2c`  
基线：`07c3d3958578b9cc9d3b8eae3758711fe08724c2`  
退出码：`1`（工具返回值实测）

执行命令：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B verification\s2c_throughput_model.py --profile 'D:\wb-out-r3\task_l0\profile.json' --result-output 'D:\FPGA_Competition\w2c\report\evidence\S2C-M01\model_20261029_r01\model_result.json' --manifest-output 'D:\FPGA_Competition\w2c\report\evidence\S2C-M01\model_20261029_r01\manifest.json' --run-id 'model_20261029_r01'
```

实际错误文本：

```text
Traceback (most recent call last):
  File "D:\FPGA_Competition\w2c\verification\s2c_throughput_model.py", line 468, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "D:\FPGA_Competition\w2c\verification\s2c_throughput_model.py", line 416, in main
    if scenario["transactions_by_category"]["output_write_segments"]["segment_bytes"] != writes:
                                                                                         ^^^^^^
NameError: name 'writes' is not defined
```

根因：新增逐层写段断言引用了 `main()` 作用域中不存在的 `writes` 变量。已改为使用 `frozen_budget_reproduced.output_write_bytes_independent_layer_sum`。

该失败发生在结果目录创建之前，`model_result.json` 和成功结果均未生成。命令输出只在本次工具返回中采集；没有另存原始运行日志。失败时执行源码SHA未采集，当前脚本已修复，不能从现有文件恢复失败版本哈希。成功复算另用新RunId `model_20261029_r02`，不复用本RunId。
