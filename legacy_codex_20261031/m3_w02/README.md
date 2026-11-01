# M3 新窗口执行入口

本目录只交付执行工具和模板，不声明获得板卡权限或完成测量。旧 OFFER 全部撤回；必须先收到 DSH 新正式 OFFER，核对当前 POR、唯一一次初始化的实际来源、固定输入身份、端口和资源归属，再落 CLAIM。`ENABLE=0`，不 push、不写 QSPI、不运行 init/reset，不执行应用 `con`。

## 模板与执行目录

`templates/` 源自旧 r02 准备模板；2026-11-01 实测后，restore/event 已补每个新 XSDB 客户端的固定 XSA `loadhw`，否则新连接会拒绝未声明的 PL 地址。setup/close/port 保留原副本。原审查及后续实际 r05 审查均保留在 `r03/review_new/`，不得再将新 restore/event 称为旧模板的逐字节副本。旧 RunId 与旧准备说明保留不动；**不得直接执行模板或复用旧租约**。未来使用 `report/evidence/R03-M3/m3_pair_<日期>_r03` 或更高编号的全新 RunId，保留相同子目录结构复制模板；实际端口仅允许3121/3122，需在租约启动前按 DSH 分配与监听归属核定。

`setup` 固定2B bit/XSA、核状态和CSR检查，只 dow 已登记应用，不 con。`restore` 仅在 before 之前从固定原快照恢复 `[0x12000000,0x12C08000)`，12,615,680 B。before/after 各全区双读；中间事件仅为 `readonly-mrd-sampling-no-candidate-write`。本测量不证明真实推理活动期间 DDR 保持性，也不夹带 C2 板测。

## 本地租约

`owner_guard.py` 的 `LEASE_KEYS` 是本地 JSON 精确字段契约。`run_dir` 是 w6 内正斜杠相对路径；`context_file` 是该 RunId 内正斜杠相对路径；`authorization_file_path` 是现存精确 Windows 绝对路径。分别绑定实际授权与 context SHA，不填未来成功事实。context 必须符合原 `r03/m3_pair.py` 的核状态、masters静置及输入身份要求；需以当前 DSH 事实和实际探测为依据，不能把旧初始化候选当成本次已执行记录。

本地租约时段最多9分钟，应取正式 OFFER 内实际执行的子区间，`max_seconds≤520`；预留收尾时间。它只是执行门禁，不认证外部 OFFER 或物理 POR。

## 串行顺序

以下路径均为绝对路径，不依赖当前工作目录。执行器固定为 `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`，以 `-B -X utf8 <脚本绝对路径> <参数>` 调用；占位参数必须在实际授权/就绪核验后替换。

1. 开 Job 前，用 `D:\codex-worktrees\w6\legacy_codex_20261031\capture_host.py --run <新RunId绝对路径> --phase pre` 持久化即时主机/输入身份；核对无他方会话、端口和 index.lock，不据“无锁”推定资源已让出。额外登记本次 DSH 实际初始化身份，不能只依赖脚本列出的历史候选。
2. 用 `D:\codex-worktrees\w6\legacy_codex_20261031\m3_w02\hold_hw_server.py --execute-board --lease-file <精确租约JSON绝对路径> --port <最终端口>` 启动受控持有进程。只有本轮随机命名 Job 内的监听 PID 被认可，拒绝连接外部服务。
3. 同一总控串行执行 `D:\codex-worktrees\w6\legacy_codex_20261031\m3_w02\run_step.py --lease-file <租约绝对路径> --step setup`，再用同一脚本/租约执行 `--step restore`；然后用 `D:\codex-worktrees\w6\legacy_codex_20261031\m3_w02\capture_phase.py --lease-file <租约绝对路径> --phase before`；再用上述 run_step 执行 `--step event`；最后用上述 capture_phase 执行 `--phase after`。每步必须进程码、语义状态、标记、清理及前后所有权同时通过。原 XSDB bat 由核心工具经 `cmd /c` 调用，不用裸 exe。
4. 离线调用 `D:\codex-worktrees\w6\legacy_codex_20261031\r03\m3_pair.py compare --before <capture_before绝对路径> --after <capture_after绝对路径> --out <全新比较目录绝对路径>`；参数细节先查该脚本 `--help`。比较通过只适用于本次固定事件，不能据此推断推理期间保持性。
5. 正常或失败均只做一次既定 `D:\codex-worktrees\w6\legacy_codex_20261031\m3_w02\run_step.py --lease-file <租约绝对路径> --step close` 收尾，再向持有进程 stdin 发送 `stop`。只清理本轮 Job；DAP/halt 异常不重试部署、不复位。租期预算不足时由 holder 截止清理，保留失败记录，不能写成正常完成。
6. 保存 holder 的收尾 stdout/退出码与 `server_close.json`，运行 `D:\codex-worktrees\w6\legacy_codex_20261031\capture_host.py --run <新RunId绝对路径> --phase post`，确认本轮进程/端口清理及13项固定输入前后一致。归还后的其他方活动另行区分，不结束无关进程。

协议门禁拒绝 before 输出（包括失败半包）出现后的 restore；before 必须有当前身份 setup/restore 成功凭据，event 必须在成功 before 后且 after 未开始，after 必须有 before/event 成功凭据。close 可在任意阶段用于止损。失败不能覆盖原输出重跑；需要新 RunId 和适用新授权。

Windows 端口核验现用 `Get-CimInstance` 查询 `MSFT_NetTCPConnection` 的 State=2/LocalPort，空集合表示无监听；避免 `Get-NetTCPConnection -LocalPort -ErrorAction Stop` 把无匹配对象误作查询失败。真实 CIM 错误仍拒绝执行。2026-11-01 r05 实采已完成四份全区读回与固定基准一致，正常受控收尾；具体范围与原始结果以该 RunId 和独立实际证据审查为准，不推广为推理负载期间保持性。

## 验证与交付边界

Python本机mock不启动真实 socket、XSDB、hw_server 或板卡。历史29项测试后的顺序门禁修复为42项测试；独立结论以新的 ordering 审查报告为准，旧 CHANGES_REQUIRED 报告保留。模板单独执行会绕过 Python 顺序门禁，禁止以此作为正式取样路径。

源文件与报告先给 DSH 精确清单，由 DSH 串行提交；返回实际 SHA 后按 Git blob 建权威清单并运行 strict。未提交磁盘清单只作附注，不代表板上通过或阶段冻结。
