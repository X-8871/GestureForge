# S5 W-E 板级窗口计划与就绪核对（2026-10-28 r01）

> 授权：Wong 2026-10-28 允许阶段5 使用板卡；`lead` 指令按 W-E 执行。
> **口径**：本窗口不主张 G5、不主张 B1–B10 全部完成；未执行项一律 `NOT_RUN`，不降级、不用离线证据冒充板上证据。

## 1. 当前环境事实（只读核对，2026-10-28 09:5x）

| 项 | 事实 |
|---|---|
| w5 | HEAD `0808013`，工作树干净，无 `index.lock` |
| 3121 端口 | **无 LISTENING**（板卡侧 hw_server 未起；板卡空闲） |
| 相关进程 | 仅 `vivado-mcp-server-windows` ×3（MCP 桥接，按 DSH-20261027-017 非板级占用；**不清、不杀**） |
| w4 状态 | 阶段4 冻结进行中，**只读引用**，不写入 |

## 2. 部署身份（装载前必须明确；身份不明不得装载）

| 候选 | 路径 | SHA-256 | 登记来源 | 可用性 |
|---|---|---|---|---|
| 阶段3 摄像头通路 bit | `dbdf/report/evidence/S3-T05/t05_timing36_project_impl_20261026_r02/outputs/design_1_wrapper.bit` | `6b23e209effd55a440447c59608f76bbb03cd4f06b3832f0777843cc54a67b01` | 阶段3 证据包（本表现场计算，未在上游清单二次确认） | 候选 |
| 4-D 合并部署 bit | `w4/report/evidence/S4-T32/phase2_build_r02_20261027_r01/s4d_inference.bit` | `c7efcb7a6a621b26cfba7e6ea57a930d00b6cfbd994b59791601d67aa89bc25a` | w4 S4-T32 构建 RunId（上游未冻结/未授权装载） | **未授权** |
| 4-D XSA | 同目录 `s4d_inference.xsa` | `22d4b70d88749c2c2fbb3bed1e02e57dfe65ee3710872bdcc1fc550c3f79bfab` | 同上 | **未授权** |
| 4-D PS 应用 ELF | `w4/report/evidence/S4-T32/phase2_ps_app_20261027_r01/s4d_ps_app.elf` | `861aecd794b5ddb6162b9c42fab194c83287bb94fe64091211bc96cc005a9d78` | 同上 | **未授权** |
| 2B 平台 bit `555a70c2…` | **未在 w5/w2b 可读 STATE/文档中找到登记条目** | — | **身份来源不明** | **BLOCKED（身份不明）** |

**结论**：当前**唯一可证明身份来源**的是阶段3 摄像头通路 bit（`6b23e209…`）但上游清单未二次确认；4-D 合并部署未授权；2B `555a70c2…` 身份不明 ⇒ **按其规则不得装载**。**在装载前需 `lead` 指定权威部署及其登记 RunId。**

## 3. B1–B10 本窗口可执行性（逐项）

| 项 | 判定 | 缺什么 |
|---|---|---|
| B1 部署身份一致性 | **BLOCKED_BY_DEPLOYMENT** | 权威 bit/XSA/ELF 登记 RunId（见 §2） |
| B2 真彩目视 | **NEEDS_WONG_PRESENT**（⇒ 本窗口 `NOT_RUN`） | Wong 在场目视；截图不替代 |
| B3 ≥100 帧五元组+顺序规则（板级） | **BLOCKED_BY_DEPLOYMENT** | 需真实链部署（摄像头→PL→结果显示）；离线 240 帧已达，不能替代 |
| B4 板上坐标映射/绘制 | **BLOCKED_BY_DEPLOYMENT** | 显示叠加部署 |
| B5 实时过期边界 | **BLOCKED_BY_DEPLOYMENT** | 真实结果发布节奏 |
| B6 30 分钟长跑（板级） | **BLOCKED_BY_DEPLOYMENT** | 真实链部署 |
| B7 HUD 屏上视觉 | **NEEDS_WONG_PRESENT**（⇒ `NOT_RUN`） | Wong 在场 |
| B8 异常注入（断流/超时） | **BLOCKED_BY_DEPLOYMENT** | 真实链 |
| B9 重连/恢复 | **EXECUTABLE（受限）** | 仅在权威部署装载后才成立；当前无授权部署 ⇒ 实际 `NOT_RUN` |
| B10 采集 FPS / 端到端延迟 | **BLOCKED_BY_DEPLOYMENT** | 真实链 + 时钟口径 |

> 结论：**本窗口 0 项可执行**（除"连接/身份一致性核验"本身），全部受部署身份阻塞；`NEEDS_WONG_PRESENT` 2 项（B2/B7）。

## 4. 窗口计划（若 `lead` 指定权威部署后执行）

- 时长：≤45 min（可申请 60）；**先做 P0 门禁**。
- **第 0 步 P0 门禁（只看不清理）**：`netstat -ano | grep :3121` 只读确认 LISTENING；`tasklist` 确认无他人 `hh_server/vivado/xsdb`；**不清理 TIME_WAIT、不杀 `vivado-mcp-server-*`、不碰 Codex 会话**；记录 bit/XSA/ELF 三 SHA 与登记 RunId。
- 装载顺序：`connect_hw` → 校验设备 IDCODE/part → `program_device(bit, probes?)` → 回读 `get_hw_info`；ELF 通过 Vitis/UART 阶段交给阶段3/2B 既有流程（**不在本窗口改 ELF 加载方式**）。
- 每项判定阈值：B1 身份三 SHA 全等 + IDCODE 匹配；B3 五元组成对 ≥100 帧且 0 重复/0 乱序未声明；B4 像素坐标逐值一致；B5 `==200 ms` 不过期、`+1 ns` 过期；B6 1800 s 无丢帧/无异常；B9 断连重连后恢复；B10 采集 FPS 与端到端延迟（时钟口径须标注）。
- **停止条件**：身份不符 / IDCODE 不符 / 任一步真实 FAIL / 温度或电源异常 / UART 无响应 / 需要写阶段4 候选区 / Wong 离场（B2、B7 需在场）。
- **恢复入口**：`vivado-mcp` 会话断开后重连 `connect_hw`；失败 RunId 保全不改写，新 RunId 重试；回滚不涉及 QSPI。
- **证据格式**：每 B 项独立 RunId `report/evidence/S5-B<N>/s5b<N>_<topic>_<date>_rNN/`；`console/**` 存真实命令+退出码；`delivery_manifest.json` **内联** `hash_basis=commit_blob` + `hash_basis_commit`；判定字段 `B<N>_VERDICT ∈ {PASS,FAIL,INCONCLUSIVE,NOT_RUN}`。

## 5. 共享区纪律

不写阶段4 候选区 `[0x12000000,0x12C08000)`；不烧 QSPI；不改线；不改 `ENABLE`；不发独立 `stop`；不 push；w4 只读。

## 6. 当前状态

**窗口尚未开启**：未连接板卡、未装载任何 bit/ELF、未做任何硬件写操作。因 §2 部署身份未获授权/未登记，按"身份不明不得装载"暂停，待 `lead` 指定权威部署后再执行 P0。