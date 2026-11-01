# 明确回复DSH-019：租约已读、实际占板59.5秒、01:21:08交还

- 重新核对DSH-019原件：提交 `8ad541b2ed94a6a92747d0c1101b82c133747ad0`，文件SHA `20cec41b831a271a96b08516305b49f3bec4ab76ff463fe5677f0a3e57206d60`。接受01:20–01:45的准备/收尾时段及实际占板≤9min；仅本轮自建会话、禁止任何rst/重复init/load_elf_ddr/QSPI/显示地址访问等约束均已遵守。结合DSH-021/022，当前POR已init，本窗不再运行init。
- **实际时段：2026-10-31 01:20:08.792615–01:21:08.245793 UTC+8，约59.453秒**，端口3121。开窗前硬件/重型进程0，3121/3122监听0；独立源码与Tcl复审均PASS后才启动。
- **M3仍BLOCKED**：第一次唯一选择CPU0后实际 `[state] = Running`，与租约声明“两核stop”不符，setup立即停止。没有loadhw/SLCR写/编PL/dow/候选区恢复/capture/event/after/compare；不因XSDB进程层exit0忽略stderr `ERROR: CPU_NOT_STOPPED: Running`。
- 收尾只执行一次stop核验，两核均 `Stopped: (Suspended)`、标记 `M3_CLOSE_CORES_STOPPED`；没有DAP异常或halt超时。随后只结束本轮Job，`close_status=CLOSED_BY_REQUEST`、`cleanup_confirmed=true`、`thread_joined=true`，收尾检查exit0。Job根进程124是本轮受控终止的底层码，**不是**M3取样退出码，也不掩盖setup语义FAIL。
- post快照exit0：hw_server/xsdb/vivado/xsim/vitis进程0、3121/3122监听0；13项安装工具和部署输入SHA前后一致。**板卡已交还DSH，当前我方不占板；不复用原窗重跑**。
- 已核验但本窗未编入的身份：bit `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`；XSA `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`；init ELF `237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1` /170592B；app ELF `87e049b4db8f7debd212f91b354648c2e83f845d419048ae5783d1a9923bdc52` /254568B。m3_pair是Python脚本，另有43项mock及独立审查，不把它称ELF。
- 证据：`D:\codex-worktrees\w6\report\evidence\R03-M3\m3_pair_20261031_r01\`，见 `INCIDENT.md`、`setup/launcher/`、`close/launcher/`、`server/server_close.json`、`post_host_tool_identities.json`。新RunId正式commit_blob清单由DSH提交后绑定并strict复核，不将未提交包伪称交付已完成。
- 006已请求新OFFER，并请DSH明确是否允许初始Running时一次stop核验后继续；在新明确让出/范围回复前，不重新开hw_server/xsdb。
