# R-03 M3 真实取样修订

复用已修复 `state` 查询的r03工具：先核对唯一目标名，选核后调用 `[state]`，不读取不存在的字典键。原r03来源与SHA在prior_README及本轮绑定中保留；此目录为后续正式入口。

新增真实启动路径为 `cmd /c "D:\Xilinx\2026.1\Vitis\bin\xsdb.bat" -no-ini -eval "source {...}"`，真实入口锁定该固定厂商bat。Job底座来自C1已审查实现，本轮删去不适用C1命令行并将M3上限扩大为600秒，超时只清理本次子进程树；不启动hw_server，不reset/init/dow/con/stop/mwr。`xsdb.argv`记录逻辑参数，真实命令行与Job收尾记录在每次capture的launcher子目录。

新capture为v2：上下文/授权快照、启动计划、Job记录和原始日志均逐项绑定；比较器重查上下文状态、官方入口、实际cmd参数、退出码、零残留与日志相等。v1仅保留历史离线字节比较，输出明确不含本轮真实入口证明；本轮板上交付必须两侧均为v2且`hardware_launcher_v2_bound=true`。纯本机mock必须显式标记，不能替代官方入口或板证据。

```powershell
$tool = 'D:\codex-worktrees\w6\legacy_codex_20261031\r03\m3_pair.py'
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -X utf8 $tool capture --help
```

固定范围 `[0x12000000,0x12C08000)` 共12,615,680B，before/after各双读，同窗口/事件/生命周期且before必须等于旧基准 `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf`。两次capture间禁止reset/init/download及候选区写入。真实事件范围仅由有效板卡租约决定。

捕获日志中的worktree_disk哈希为采集时附注；本轮交付manifest另按固定提交的commit_blob绑定程序、输入和原始输出，并过strict检查。PAIR_UNCHANGED/REGION_CHANGED/输入环境错误退出码为0/1/2，工具成功不自动代表完整M3或阶段验收通过。
