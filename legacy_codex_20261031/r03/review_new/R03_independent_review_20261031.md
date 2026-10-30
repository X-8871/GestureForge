# R-03 独立复审（2026-10-31）

## 结论

**PASS（源码审查）**。新版 M3 取样工具及 `hold_hw_server.py` 通过只读审查；未启动厂商工具、hw_server 或板卡连接。该结论不代表真实板级执行或 G3/G4。

## 被审版本 SHA-256

- `m3_pair.py`：`475805761decab570d7b5da8b5d2fd762496adc8a0beb2b63625c387b94f61c2`
- `job_launcher.py`：`ece49b79505236c8ec0d5f34105b4131b0f79eb65eaf05f0521f51aa1238c0c7`
- `test_m3_pair.py`：`0685c957ef04409c184785edda19c3ad2f3938eee382ce8bae8561166ad2dbb2`
- `test_windows_launcher.py`：`9de7b6378742cdf16969d3f3bd40fa732a70dbb31f70c777527b9932061bac48`
- `README.md`：`3f1b906cca5e39bc4311cf9f159ab7ed164530c839fa4f6c0bf00697fa9ea003`
- `hold_hw_server.py`：`fc4d8c8efa88122f82e7a4c6e65a3e9fd738202fdc1f38d027d97ca471e75fd0`

## 核查与验证

- 复核固定区间 `[0x12000000, 0x12C08000)`、before/after 双读、固定 before 基准 `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf`、状态查询 `[state]`、目标唯一性、上下文语义和跨采样身份绑定；Tcl 仅连接、查询状态、`mrd` 与断开，没有复位、初始化、下载、运行或写内存命令。
- v2 校验绑定官方 `xsdb.bat` 快照、实际 cmd `/c` 与 `-eval source` 命令行、Job 执行记录、原始日志、退出/清理状态及上下文/授权输入快照；before/after 要求 BAT 摘要一致。超时路径保留 launcher 执行记录和 stdout/stderr，并由 capture 写出部分日志；失败不产出成功 manifest。
- `hold_hw_server.py` 只允许指定日期/窗口、指定端口且端口空闲时显式启动固定 `hw_server.bat`；进程加入本轮 Job。`stop`、输入关闭、启动异常或动态租期预算超时均收窗；normal stop 才返回 0，hard timeout 返回 124。租期在 01:45 结束并预留 10 秒收尾。
- 命令：`python.exe -B -X utf8 -m unittest -v test_m3_pair test_windows_launcher`，退出码 0，43/43 项通过（5.422s）；含真实 cmd.exe 对本地占位 BAT 的测试及自建 Python 子进程树超时清理。
- `ast.parse` 对上述 5 个 Python 文件通过，退出码 0。

## 限制

代码侧绑定官方 `xsdb.bat` 入口；完整 XSDB 依赖链身份（BAT/helper/exe/DLL）由总控计划在独立的 pre/post host tool identity 快照核验，本报告未审查该后续证据。文件摘要与执行记录提供一致性校验，不构成签名或防对抗伪造认证。无真实 XSDB、hw_server 或硬件运行证据。
