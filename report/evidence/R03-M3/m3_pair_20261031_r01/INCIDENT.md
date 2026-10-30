# M3 r01：初始核状态不符，停止并收窗

结论：**BLOCKED，capture before / event / after / compare 全部 NOT_RUN**。01:20:08.792615 UTC+8建立本轮受Job约束hw_server，端口3121；setup第一次选中的唯一目标为 `ARM Cortex-A9 MPCore #0`，`[state]`实际返回 `Running`，不满足DSH-019/021/022的“两核stop”前置。原始日志在 `setup/launcher/stdout.bin` / `stderr.bin`；脚本按失败路径在任何loadhw/SLCR/编PL/dow/DDR写之前退出。

本轮没有配置PL、没有dow应用、没有运行init/con/reset、没有候选区写入、没有m3_pair capture。既有PL保持DSH租约所述P3q，本窗未独立证明该位流身份，不以租约声明替代实测。

按租约只执行一次close收尾：两个唯一A9目标均为 `Stopped: (Suspended)`，标记 `M3_CLOSE_CORES_STOPPED`；没有DAP异常或halt超时。随后向本轮持有进程输入stop，Windows Job结束，`CLOSED_BY_REQUEST`、cleanup_confirmed=true、thread_joined=true。精确结束时间见 `server/server_close.json`；实际占板约一分钟，远少于9分钟。post快照证明hw_server/xsdb/vivado/xsim/vitis进程0、3121/3122监听0，13个工具/部署文件身份与pre完全相同，查询退出0。

XSDB进程层返回0，但setup stderr明确 `ERROR: CPU_NOT_STOPPED: Running`，所以本步骤**语义失败**，不得因Job的 `PASS_PROCESS_ONLY` 或进程码0称PASS。close进程码0、必需标记与无错误检查均通过。此行为也再次说明需要同时检查真实状态与完整标记，不能只看XSDB进程退出码。

按“任何步骤失败立即收窗、不重试”未在本RunId或原窗重跑。下一次必须取得DSH新OFFER并使用新RunId，先澄清初始核状态/会话释放是否改变停核状态。不能把本次停核后状态扩大为重新开窗时状态，也不自行恢复或重试。
