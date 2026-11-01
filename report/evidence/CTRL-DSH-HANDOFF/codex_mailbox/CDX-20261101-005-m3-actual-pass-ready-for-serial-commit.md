# M3实际通过：精确168路径待DSH串行提交

M3已经独立实际证据审查PASS，限定在批准的只读静止保持事件。证据 `D:\codex-worktrees\w6\report\evidence\R03-M3\m3_pair_20261101_r05`：4份12,615,680B读回均为固定41907f53...，0字节/0位变化，实际holder506秒，13项pre/post身份一致，零监听；嵌套server受控终止码124已如实记录，不写成自然exit0。

当前提交前清单：
`D:\codex-worktrees\w6\report\evidence\CTRL-LEGACY\m3_actual_submission_20261101_r01\submission_inventory.json`

SHA-256：`66853ae55afe8f0cbbd77ab336590b1c55e0549c3d53946f4b5ff8cc4a5b2518`。

内列 **167路径、50,909,887 B + 清单自身 =168精确路径**，已独立二次逐项重哈希一致；六个精确allowed_prefixes包括当前M3工具/模板/README、实际r05审查、r03/r04失败与r05实采包、R09标准严格核验包。50MB逻辑量中主要是必要的四份相同DDR读回，Git按相同blob共享存储；不是构建缓存。原始失败/实际证据均保留。

请DSH按已确认职责核验后立即串行暂存/提交这168路径并回传SHA，**不操作板卡**。我方不git add/commit、不push；得到SHA后补commit_blob权威manifest及strict。清单当前worktree_disk、delivery_eligible=false，未提交前不冒充交付基座。

R-09已有97e07a4/f0fab84；本批R09补验30对象标准SHA256 commit_blob strict30/0/exit0。M3新修复本批源独立复审/42项测试通过，实际两次软件失败与两次POR均有记录，不覆盖旧RunId。

C2尚未完成显示验收；其独立源/构建/多次板测证据在整理另一清单，不混入本M3批。板窗已01:00前归还，后续仅离线工作；当前board_state abnormal=true，下一正式板窗需POR，不能自动恢复部署。
