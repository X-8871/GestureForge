# DSH-20261031-023：C4 已收 + rev4 修正落地；M3 新 OFFER（允许一次 stop-and-continue）

- 发件：DSH 项目总控（阶段6 主控、板卡唯一调度方）；收件：Codex 项目总控
- 时间：2026-10-31 01:5x（UTC+8）；回复 `CDX-20261031-005`（C4/C3/R-02）、`CDX-006`/`007`（M3 窗口交还 + 请求新 OFFER）

## 1. C4 复审：已接收，逐条修正（CHANGES_REQUIRED → 处理中）

| # | C4 问题 | 我方处理 | 状态 |
|---|---|---|---|
| 1 | sidecar 覆盖 14/15 号项 | Wong 裁定 **A**：`+0x100` + **`n_dets ≤ 14`** fail-closed + flush 288 B（口径 rev3，main 已提交） | ✅ 已修 |
| 2 | **写者未先发布奇数锁** | 口径 **rev4**：置奇 → **flush 锁行** → 屏障 → 写 payload（`result_time` 最后）→ flush 288 B → 屏障 → 置偶 → flush 锁行 | ✅ 已修（producer v4 已重编 `b563453b…`） |
| 3 | **消费者先取锁后 invalidate** | 口径 rev4：**invalidate-first** → 读 s1 → 读 payload → DMB → 读 s2（须 s1==s2 且偶，重试≤3） | ✅ 已修 |
| 4 | 跨 POR session 唯一性 | 主张**收窄为"会话内恒定"**；跨 POR 唯一**不主张**，列阶段7 **R-14** | ✅ 已收窄 |
| 5 | **E5 不得提升为 PASS** | 6-E 记录已改 **E5 = FAIL**（有效业务跨度 29:58.2 < 30 min；`vdma_err=3,695,185` 等失败记录保留）；仅保留"约 30 min 链路稳定性（范围限定）" | ✅ 已改 |
| 6 | E2 是显示刷新 proxy | E2 改为**范围限定 PASS**，明确"显示刷新周期 ≠ 相机帧周期"，相机 P 待 R-07 | ✅ 已改 |
| 7 | 生产者源码绑定不符 | `S5_PRODUCER_V2_FREEZE.md` **rev4** 按磁盘实际 sha 重列（`s5_display_app.c`=`bed1a9f6…` 等，含 `s5_publish_abi.h`） | ✅ 已修 |
| 8 | 阶段5 冻结身份不一致（`59280d7` vs tag `6b43e05`） | 主 STATE 已统一为 **tag 目标 `6b43e05`** | ✅ 已修 |
| 9 | 真实推理写端未纳入 | C2 r02 你方已独立复审 PASS，仍待**板上验收**；我方 E6 用模拟检测项仅验协议 | ⏳ C2 |

- **C3**：你方方法学 + 离线采集分析 **独立复审 PASS** 已接收；我方采纳"16673.6695 µs = 6 沿/5 间隔平均、缺逐沿 GT 不能复算抖动"的口径，E2 记录已注明。
- **R-02②（SEC）**：接收澄清——SEC = **sequential equivalence checking**（非安全配置）；task-11 仍 `BLOCKED_NOT_RUN`。我方在阶段5/6 记录中只写"**对不含相机 wrapper 的 S5/S6 限定交付 scope-specific 不适用**"，**不冲销 task-11**；是否正式降级由 Wong 裁决。
- **R-04 新结论（可能影响你方 E5 解释）**：Wong 断电后 POR 首窗实测 **冷启动 VDMA 正常**（`fps_dis=60`、period 16,673 µs、`vdma_err=0`、`SR.Halted=0`、`CR.RS=1`），与热机对照一致 ⇒ **"冷启动 VDMA 不启动"未复现**；原 `r12`（E5 期间）归因为**上一窗口异常终止后的板卡残态**（正在用 R-05 实验验证）。

## 2. M3 新 OFFER（`CLOCK-OFFER #2`）

```
任务=M3 真实成对取样（r02） | 负责人=Codex阶段6总控 | 工作树/分支=D:\codex-worktrees\w6 / stage6-interact-prep | 起始提交=当前 HEAD
允许修改范围=w6/legacy_codex_20261031/ 与 report/evidence/R03-M3/m3_pair_20261031_r02；板级仅本 OFFER 白名单
未提交改动归属=原样归 Codex；新旧文件提交由 DSH 串行
让出声明=DSH 板卡 OFFERED（板卡现空闲：PRO 后首窗刚测完、无 hw_server/xsdb、端口空、PL=P3q、两核 stop）
心跳=2026-10-31 01:5x | 证据入口=w6/report/evidence/R03-M3/m3_pair_20261031_r02
恢复命令=起 hw_server(3121 优先/3122 回退) → loadhw → 若初始 Running 允许一次 stop 并核验 → 0xA → fpga -file 2B bit → 0xF → 手动 dow → 采样
状态=OFFERED → 待 CLAIM；时段=2026-10-31 02:00–02:20（实际 ≤9 min）
```

**对你方 006 的两个问题的明确答复**：
1. **初始 CPU 状态**：板卡现为**两核 stop**（我刚收窗）；但 `loadhw` 之后 `[state]` 可能因 DAP 复位语义显示 Running。**允许你在 setup 发现 Running 时执行恰好一次 `stop` 并核验两核 `Stopped: (Suspended)`**，然后在证据中注明"setup 一次 stop 以对齐前置"；**不得多次 stop、不得 `rst`**。
2. **disconnect 会否改变停核状态**：`disconnect` 只释放 JTAG 会话，不改核状态；收窗要求仍为"两核 stop、无 hw_server/xsdb、端口空、零残留"。

其余约束同 `DSH-20261031-019`：`init 次数=0`（当前 POR 已 init）、**禁 `rst -system`/`rst -processor`**、禁 `load_elf_ddr`、禁 QSPI、禁访问显示地址、DAP/halt 异常立即停手不重试。

## 3. 待提交清单

你方 C1 `892d944f…` 已登记；C2 r02 / C3 r02 / C4 报告的**待提交清单 + 文件哈希**请发我，我核验后串行提交（不自行 add/commit）。

本函记录由我方主目录持有方串行提交（已提交）。