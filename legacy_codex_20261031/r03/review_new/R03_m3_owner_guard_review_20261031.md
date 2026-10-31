# R-03 独立复核：M3 Job/端口所有权门禁（2026-10-31）

## 结论

**CHANGES_REQUIRED。** 此结论只针对下列 5 个新冻结文件。两项此前所有权阻断已关闭，28 项隔离测试和本机 Windows Named Job 正控通过；仍有一项收尾证据失败会被错误报告为成功的问题，修复并补测后可复审。

## 被审版本

| 文件 | SHA-256 |
|---|---|
| `m3_w02/owner_guard.py` | `d712b1b208d7b792ac81eedab50ed6e84745a3fa7b20696e04172812e8478efb` |
| `m3_w02/hold_hw_server.py` | `68bf3362ca41ddf6b36d99efeff012c4a85f71231620d50b20fb9e0e56277345` |
| `m3_w02/run_step.py` | `62c9d5eae234d7c4afb3bffd1c315bd6998875b44c1797c9bb26fda70ea83795` |
| `m3_w02/capture_phase.py` | `938fa6e3dc62fa6326ce14b9e5d9e0186d4beab3d3d64daecfee3c9e672de626` |
| `m3_w02/test_owner_guard.py` | `e1a2cf79653299f6fdc875a8adc8f9159a7abe9d8dff8a391a8ea957844ea009` |

上述 SHA 与总控冻结值逐项一致。`job_launcher.py` 仅作为未改的既有 Job 库依赖供静态核对与本机正控调用，不在本轮待审 5 文件内。

## 已关闭的两个阻断

- 端口唯一来源已绑定：holder 要求 `--port` 与 `port.txt` 相同；启动记录同时绑定 port 数值和文件 SHA；客户端重读启动记录、校验租约与 `port.txt` 摘要，并在执行前后核验端口所有权。`server_close.json` 已存在时客户端拒绝执行。
- Holder 为本轮生成 `Local\M3_OWNER_<uuid4>` Job 名。创建同名对象返回 `ERROR_ALREADY_EXISTS` 时关闭该句柄并拒绝附着。开始监听前，holder 用自己 Job 句柄的活动 PID 与 Windows `Get-NetTCPConnection` 的 listener PID 校验归属；Job 线程或监听身份不符时 fail closed。客户端以 `JOB_OBJECT_QUERY` 打开命名 Job，比较活动 PID 和 listener OwningProcess，并在查询前后复核 Job 与收窗状态。capture 与单步均执行前、后复核。
- 租期门禁：严格 JSON schema、重复字段拒绝、明确 UTC+8 时间、租期至多 9 分钟、`max_seconds` 至多 520、R03 及更新 RunId、授权/context 路径与 SHA 绑定，且显式说明本地门禁不替代外部板窗授权和初始就绪核验。
- `now` 与预算在端口空闲查询后取得；holder 的 budget 为 `min(520, lease.max_seconds, floor(lease.ends_at-now)-10)`。既有 `job_launcher.run_job` 在进程创建前启动单调时钟，并以该 budget 等待本轮根进程；holder 的 owner 查询、客户端和 capture 在 Job 租期内进行。run_step/capture 再扣步骤上限与收尾预留。当前路径把慢的端口 preflight 算在租约剩余时间内、但不算进 Job 预算；开始时重新按绝对 lease end 截断，因此未发现超过 9 分钟租约的静态路径。

## CHANGES_REQUIRED

**[P2] `server_close.json` 写入失败仍返回成功** — `hold_hw_server.py` 的收尾分支在 `_write_json_new(server_close.json, result)` 遇到 `OSError` 时只打印 stderr；未把 `close_status` 改成失败，也未改变后续退出码。若独占创建因磁盘满、拒绝访问或文件冲突失败，holder 仍打印 `CLOSED_BY_REQUEST` 并以 0 退出，尽管本轮收尾证明未落盘。

这会让调用方把“无收尾记录”误当正常成功；后续客户端仍会因 Job/监听所有权缺失而 fail closed，但本轮闭环记录与进程码自相矛盾。关闭条件：记录写失败时设置 `FAILED_CLOSE`（或等价失败状态）、以非零退出，并增加隔离 mock 覆盖 `_write_json_new(server_close.json, …)` 抛出 `OSError` 的反例，确认不会输出/返回成功。

## 验证

- `C:\Users\22061\.local\bin\python3.11.exe -B -m unittest -v test_owner_guard`（工作目录为 `m3_w02`，临时目录设为 `D:\FPGA_Competition\tmp`）：**exit 0，28/28通过**。用例覆盖端口值/hash不匹配、外部 PID 接管、Job 查询失败、Job 在线程核验期间退出、server_close竞态、已有命名 Job 拒绝、租期超限及客户端前后核验。
- Windows Native 正控（exit 0）：通过当前 `hold_hw_server.OwnedJob` + 未改 `job_launcher.Native` 启动唯一命名 Job 中的短时 Python `sleep(3)` 子进程；独立 `owner_guard.query_named_job_pids` 返回 PID `[60676]`，与当前 Job 句柄查询的 PID `[60676]` 一致。Job 清理后 `cleanup_confirmed=true`、`job_handle_closed=true`、`root_wait_after_job_close=0`；再次 `OpenJobObjectW(JOB_OBJECT_QUERY)` 得到对象不存在。该正控只启动/结束本审查自建的 Python 进程，不使用 socket、不启动厂商工具或硬件；临时目录已自动清理。
- 未运行真实 listener 查询、XSDB、Vivado、hw_server、硬件或 DSH 窗口；未修改 5 个待审文件；未暂存或提交。

## 剩余限制

单步与 capture 的前/后所有权检查是时点核验，不能将其描述成并发抢占下的原子锁。若执行期间 postcheck 失败，wrapper 会记为失败；是否存在执行中途 listener 替换，需由具体错误证据判断。本轮不声称硬件 ready，也不构成板窗授权；目前没有新 OFFER，禁止启动。