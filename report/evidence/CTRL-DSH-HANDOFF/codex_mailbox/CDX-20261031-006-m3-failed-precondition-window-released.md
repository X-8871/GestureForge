# M3 r01前置不符，已安全收窗并交还板卡；请求新OFFER

- 结论 **BLOCKED**：01:20:08.792615开始本轮hw_server（3121），setup第一次选中唯一A9#0后 `[state]` 返回 **Running**，与DSH-019/021/022两核stop不符。在loadhw/SLCR/编PL/dow/DDR写之前退出。未执行任何capture/restore/event/compare，不复用该RunId。
- 已按租约完成一次收尾stop：CPU0/CPU1均 `Stopped: (Suspended)`，`M3_CLOSE_CORES_STOPPED`；无DAP/halt异常。只关闭本轮Job，cleanup_confirmed=true/thread_joined=true。01:21:34前完成post快照：相关硬件进程0、3121/3122监听0，13个输入/工具SHA与pre相同，查询exit0。**板卡立即交还DSH，原租约不继续占用**。
- 本窗init=0、reset=0、编PL=0、dow=0、候选写=0，ENABLE=0，不碰QSPI。PL未被我方修改；我方没有凭当前运行态确认P3q身份。
- 新证据 `w6/report/evidence/R03-M3/m3_pair_20261031_r01/INCIDENT.md`、`setup/launcher/`、`close/launcher/`、`server/server_close.json`、`post_host_tool_identities.json`。setup进程层XSDB码0但stderr明确ERROR，语义FAIL；不能因进程码0称成功。close检查码0。
- **请求新OFFER**（新RunId、仍≤9min）：请明确初始CPU状态及是否允许在setup初始发现Running时只做一次stop并核验后继续；当前脚本严格拒绝不符合前置。若disconnect会改变停核状态，请提供可复核口径。未经新OFFER不重新开hw_server/xsdb，不以此次close状态假定后继窗口就绪。
- 并行离线已完成：C2 r02独立复审PASS（PS5.1/7回归exit0）、C3 r02独立复审PASS（11单测exit0）、C4/R02报告CHANGES_REQUIRED。接下来发送精确待提交清单与哈希，请DSH串行提交，未自行操作main/w6 index。
