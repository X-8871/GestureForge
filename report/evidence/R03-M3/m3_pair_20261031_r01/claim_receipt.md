# M3 板窗正式 CLAIM（3121，01:20开始）

任务=`M3真实成对取样，仅只读保持事件` | 负责人=`Codex受托遗留任务总控` | 工作树/分支=`D:\codex-worktrees\w6 / stage6-interact-prep` | 起始提交=`892d944f6a1c04a8956fce200f9edc416edce8c6` | 允许修改范围=`本轮独立legacy目录与report/evidence/R03-M3/m3_pair_20261031_r01；板级仅DSH019/021/022白名单` | 未提交改动归属=`原STATE历史差异/两规格/14旧目录原样保留；本轮新文件归Codex，提交由DSH串行` | 让出声明=`已核验DSH019 OFFER、021当前POR已init与只读事件批准、022正式身份A；接受租约，当前CLAIMED，01:20前不启动` | 心跳(UTC+8)=`2026-10-31T01:18:00+08:00` | 证据入口=`w6/report/evidence/R03-M3/m3_pair_20261031_r01；r03/review_new/R03_independent_review_20261031.md` | 恢复命令=`按DSH021不重复init，0xA→固定2B bit→0xF→手动dow且不con；before前原快照恢复；before/after各双读；stop核验后只关闭自建Job` | 状态/下一接手方=`CLAIMED / Codex在01:20开始；实际占板≤9分钟且01:45前全部清理，随后交还DSH`

- 实际预定端口 **3121**，01:15及pre_verified快照均无hw_server/xsdb/vivado/xsim/vitis进程、3121/3122无监听；空闲内存2,992,824 KiB。开始前还会复核，若占用不干扰原会话。
- 固定位流SHA：`555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`；XSA `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`；init ELF `237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1`（170,592B，仅登记、不运行）；app ELF `87e049b4db8f7debd212f91b354648c2e83f845d419048ae5783d1a9923bdc52`（254,568B，仅dow、不con）。完整路径已在003登记且本轮13文件身份快照再次核验。
- M3源码独立复审PASS，43/43纯本机mock exit0；硬件尚未启动。Job硬超时最多520秒，并按01:45租期剩余时间缩短、预留10秒收尾。DAP/halt或任何步骤失败立即收窗不重试。
- 当前POR已init：**本窗init次数0、reset次数0**；不使用load_elf_ddr，不写QSPI，ENABLE=0。此保持事件不声称真实推理活动期间保持性。
