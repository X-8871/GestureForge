# DSH → Codex 交接文档（2026-10-18）

- 作者：DSH（DeepSeek Harness，Team Lead `lead`）
- 接收方：Codex（同一工作区 `D:\FPGA_Competition`）
- 触发：Wong 要求把今晚 DSH 做的事完整交接给 Codex，并明确双方**协作**（不是单方接管）
- 本文档是 Wong 明确要求的**跨 Agent 交接记录**，不替代 `AGENTS.md`、`.codex/STATE.md` 或既有的总控→开发→审查流程
- 时间口径：UTC+8。本文覆盖 2026-10-17 晚 ~ 2026-10-18 凌晨（02:00–03:30）

---

## 0. 协作模型（先读这段）

双方共用仓库，按 **方案 A：按任务轮流独占写** 协作，规则已落在 `AGENTS.md`「与 Codex 共享同一工作区（2026-10-17）」：

| 规则 | 含义 |
|---|---|
| 单写者 | 同一时刻同一文件只有一个写入方；动手前先看 `git status --short` 与 `.git/index.lock` |
| 提交串行 | 不并发 `git add`/`git commit`；提交只含本轮相关文件；不 rebase/reset/clean 对方改动；不自动推送 |
| 重资源互斥 | 16 GB 本机同一时刻只跑一个重型综合、实现或整网仿真；启动前核对 Vivado/xsim 进程 |
| 证据互不覆盖 | 各自用新 RunId 与独立目录，不重跑、不改写对方 RunId 下的证据与失败记录 |
| 状态入口 | `AGENTS.md` 与 `.codex/STATE.md` 是双方共同入口；任务边界各自更新 STATE，不同时改同一段 |

本次 DSH 的写范围**只限于**：DSH 自己的 DSH 配置、`D:\tmp` 下的临时探针、本交接文档与 STATE 交接行。**没有**修改 `src/`、`sim/`、`vivado/`、`docs/`、`report/` 中任何工程文件。

---

## 1. DSH 今晚做了什么（按时间顺序）

### 1.1 本地知识库（AMD 文档检索）

| 步骤 | 结果 |
|---|---|
| 解压知识库包 | `20260918.qwen3-embedding-0.6b.tar.gz`（4.14 GB，MD5 与官方一致）→ `C:\amd-doc-search` |
| 安装 WSL | 系统缺 WSL；从镜像 `ghproxy.net` 下载 `Microsoft.WSL_2.7.13.0_x64_ARM64.msixbundle`（494.9 MB），管理员权限安装成功（内核 6.18.33.2-2，WSLg 1.0.73.2） |
| Docker | Docker Desktop 启动成功，引擎 29.8.2；`doctor` 三项全过（CLI / Daemon / Compose 1.145.0） |
| 拉起文档栈 | `amd-embedded-doc-search configure --start --mcp-port 8080`：导入 **725,911 篇文档**完成，llama.cpp / Weaviate / mcp-server 三容器运行，MCP 端点为 `http://127.0.0.1:8080/mcp/doc-search` |
| **当前状态** | Wong 因内存不足（Weaviate 建索引吃 5 GB + CPU 100%）要求停止：已 `stop` 掉容器（**数据卷保留**），Docker Desktop 已退出，WSL 已 `shutdown` |

> 下次要用：`cd C:\amd-doc-search` → `.\amd-embedded-doc-search.exe start`（**不需要重新导入**）；用完 `stop`。
> DSH 侧 MCP 条目 `mcp-doc-search` 已配好，服务未运行时显示 disconnected，启动后自动重连。

### 1.2 模型接入（已交付可用）

在 DSH 里新增了阿里云百炼路由 **JL-ds**，并修掉两个真实故障：

| 项目 | 值 |
|---|---|
| 提供商 id | `jl-ds` |
| 显示名 / 模型 | **JL-ds** / `deepseek-v4.1-flash` |
| 端点 | `https://dashscope.aliyuncs.com/compatible-mode/v1`（按量计费，扣 Wong 的百炼账号） |
| 上下文 / 最大输出 | 1,000,000 / 393,216 |
| 输入模态 | text + image |
| 推理档位 | `off` / `low` / `high` / `max`（默认 high） |
| 密钥 | 存放于**用户环境变量 `JL_DS_API_KEY`**，不落配置文件、不进 Git |

配置文件：`C:\Users\22061\.dsh\profiles\desktop\cordis.patch.yml`（备份 `cordis.patch.yml.bak-20261017`）。

#### 故障 1：`400 developer is not one of [...]`（已修）

百炼兼容端点只接受 `system/assistant/user/tool/function`。DSH 的 pi-ai 适配器在组装请求时有：

```js
const instructionRole = model.reasoning && compat.supportsDeveloperRole ? "developer" : "system";
```

`deepseek-v4.1-flash` 是推理模型，`supportsDeveloperRole` 默认 true → 系统指令被发成 `developer` → 400。
修复：两个路由都加 `compat.supportsDeveloperRole: false`。

#### 故障 2：推理档位配错（已修）

最初用 `thinkingFormat: qwen` 只表达"开/关"。实测百炼文档与接口：`deepseek-v4.1-flash` 支持 `reasoning_effort = low | high | max`（默认 high），`thinking_budget` 不支持。已改为 `supportsReasoningEffort: true` + 四档 `reasoningEfforts`。

#### 实测数据（供参考，非验收结论）

| 任务 | 档位 | 思维链 tokens | 耗时 | 输出费用（忙时） |
|---|---|---|---|---|
| 12 球天平（难） | low / high / max | 15,426 / 11,313 / 9,518 | 141 / 103 / 76 s | ¥0.127 / 0.094 / 0.083 |
| Ramsey（中） | low / high / max / off | 1,272 / 1,222 / 954 / 0 | 16.9 / 21.6 / 14.5 / 11.7 s | — |

结论：档位更像"推理策略"而非长度旋钮，难题上 max 反而更短更快更完整。

### 1.3 ROSS 技能

`C:\Users\22061\.dsh\skills` 下 50 个 ROSS 技能目录（hls 22、vai 13、segcfg 7、vivado 6、hw 2），DSH 技能目录已可调用（`vivado-rtl-lint`、`vivado-simulate-rtl`、`hw-ila-debug` 等）。
注意：ROSS 以**技能**形态安装，不是 DSH npm 插件，所以"插件页"里看不到它，这是预期行为。

### 1.4 Vivado 工具链接入与全流程实测（重点）

**发现并修复许可问题（这是今晚最关键的一条）**：

- 现象：`synth_design` 直接失败 —— `Failed to get the license for feature 'Synthesis' and/or device 'xc7z020'. Explanation: A license feature for Synthesis was found but is expired.`
- 根因：Vivado 自动找到 `C:\Users\22061\Downloads\Xilinx.lic` 里 **2026-10-06 已过期的 Enterprise 试用**条目，于是拒绝综合，**不会**自动退回免费档。
- 修复：抽取**仅含有效条目**的 BASIC 许可到 `D:\Xilinx_licenses\basic_only.lic`（`Vivado_Basic_Package` / `Vivado_Synthesis` / `Vivado_Implementation` / `Vivado_Simulation`，有效期至 **2027-08-07**），并把 `XILINXD_LICENSE_FILE` 注入 DSH 的 MCP 配置：

```yaml
# cordis.patch.yml → mcp-vivado.config.env
XILINXD_LICENSE_FILE: 'D:\Xilinx_licenses\basic_only.lic'
```

- 生效方式：击杀 ROSS daemon（`ROSS.exe --kill-all`）后重连，Vivado 日志确认 `A valid Vivado Design Suite BASIC license has been detected`。

**实测结果（探针工程 `D:\tmp\vivado_test`，不涉及仓库文件）**：

| 项目 | 结果 | 证据 |
|---|---|---|
| MCP 官方 `vivado-mcp`（TCL 模式） | ✅ 启动/执行/停止正常 | session `vivado-20261018-022030-75e83746` |
| MCP 社区 `vivado-py` | ✅ GUI 模式下 ping 正常（2026.1）；`connect_hw` 可用 | 需要 `start_gui` 后才有事件循环 |
| 综合 | ✅ 0 errors（`xc7z020clg400-2`，BASIC 授权） | counter 探针 |
| 实现 | ✅ `place_design` / `route_design` 0 errors | — |
| 比特流 | ✅ 生成成功 3.9 MB | `D:\tmp\vivado_test\counter_probe.bit` |
| 仿真 xsim | ✅ `xvlog -sv` → `xelab` → `xsim` 全 exit 0，tb_counter 106 ns 正常结束 | `D:\tmp\vivado_test\xsim_probe.log` |
| JTAG | ⚠️ hw_server 3121 正常、cs_server 启动、线缆识别为 `Digilent/210512180081`，但**器件列表为空** | 板子未上电 |

---

## 2. 明天（上板前）必须处理的三个阻碍

### 阻碍 1（最要紧）：工程没有任何约束文件

- `AX7Z020_Gesture` 的 `constrs_1` **为空**，`D:\FPGA_Competition\vivado\` 下也没有 `.xdc`。
- 后果：直接 `write_bitstream` 会被 DRC 拦住（`NSTD-1` 未指定 IOSTANDARD、`UCIO-1` 未指定引脚位置），且没有 `create_clock`，时序无约束。
  - 这一点我在探针上复现过：加了 `set_property SEVERITY {Warning} [get_drc_checks NSTD-1/UCIO-1]` 才生成出比特流。
- 需要：按 AX7Z020 原理图/BOM 核对引脚后编写 XDC（引脚 + IOSTANDARD + 时钟 + 必要的时序例外）。**不能凭芯片型号推断引脚。**

### 阻碍 2：`synth_1` 是 `synth_design ERROR`，增量检查点不匹配

- `INCREMENTAL_CHECKPOINT` 指向 `...\utils_1\imports\synth_1\rom_controller.dcp`，其 part 为 `xa7z020clg400-1I`，与 run part `xc7z020clg400-2` 不匹配（打开工程即有 CRITICAL WARNING `Runs 36-271`）。
- BASIC 许可**不含** Incremental Compile（工程打开时也有对应 CRITICAL WARNING）。
- 需要：综合前清掉增量设置并 reset run，否则会重复报错。
  - 参考命令（**改工程状态，需 Wong 授权后再执行**）：
    ```tcl
    set_property INCREMENTAL_CHECKPOINT "" [get_run synth_1]
    reset_run synth_1
    ```

### 阻碍 3：板子未上电

- USB 线缆（Digilent 210512180081）已被识别，但 `open_hw_target` 报 `No devices detected`。
- 明天给板子通电后重试；若仍无器件，依次检查：JTAG 线缆、板子供电、跳线/启动模式、驱动。

---

## 3. 交接检查点（Codex 接管后的建议顺序）

1. 读 `AGENTS.md`、`.codex/STATE.md`、本文档；核对 `git status --short`（当前 403 项）与 `.git/index.lock`（当前不存在）。
2. 确认无遗留重型进程（我已关闭全部 Vivado / hw_server / cs_server；RAM 可用 8.3 GB）。
3. 需要 Vivado 前先确认许可：
   - MCP 路径已自动带 `XILINXD_LICENSE_FILE`；
   - 手动开 Vivado 时需自行设置 `XILINXD_LICENSE_FILE=D:\Xilinx_licenses\basic_only.lic`（或把该文件放到 `C:\Users\22061\.Xilinx\`）。
4. 处理阻碍 2（清增量 + reset synth_1，需授权）→ 跑一次真实综合确认工程本身可过。
5. 处理阻碍 1：确认引脚资料后编写 XDC 并加入 `constrs_1`。
6. 板子上电 → `open_hw_target` 确认器件 → 生成比特流 → **烧录需 Wong 单独授权**。
7. 任何写入前按方案 A 更新 STATE 交接行；只提交本轮相关文件。

---

## 4. 环境事实（2026-10-18 03:30 核对）

| 项目 | 值 |
|---|---|
| 工作区 | `D:\FPGA_Competition`（main @ `5d1a4ac`，403 项未提交） |
| 其他工作树 | `D:\codex-worktrees\96a3`、`\dbdf`；`D:\FPGA_Competition\w2b` |
| 磁盘 | C: 41.5 GB 可用；D: 38.8 GB 可用 |
| 内存 | 15.7 GB 总量，当前 8.3 GB 可用 |
| TEMP/TMP | 用户级已设为 `D:\tmp`（Vivado/xsim 共用） |
| Vivado | `D:\Xilinx\2026.1\Vivado\bin\vivado.bat` |
| 许可 | `D:\Xilinx_licenses\basic_only.lic`（BASIC，至 2027-08-07） |
| DSH 配置 | `C:\Users\22061\.dsh\profiles\desktop\cordis.patch.yml`（MCP：`vivado-mcp`、`vivado-py`、`amd-doc-search`） |
| DSH 技能 | `C:\Users\22061\.dsh\skills`（50 个 ROSS 技能） |
| 知识库 | `C:\amd-doc-search`（镜像与数据卷保留，容器已停） |
| 临时探针 | `D:\tmp\vivado_test\`（license_probe、counter_probe.bit、xsim 日志） |

---

## 5. DSH 未完成 / 未验证的事项（明确留给 Codex 或后续）

| 项 | 状态 |
|---|---|
| 真实工程 `AX7Z020_Gesture` 综合/实现/比特流 | ❌ 未跑（有阻碍 1、2，需授权改 run 状态） |
| XDC 约束 | ❌ 不存在，需按原理图编写 |
| 上板烧录与实测 | ❌ 未做（板子未上电；烧录需单独授权） |
| 社区 MCP 的 ILA/VIO 实机验证 | ⚠️ 插件 ping 与 `connect_hw` 通过，未做真实抓取（无器件） |
| 本地文档检索（amd-doc-search）实际查询 | ⚠️ 栈跑通、导入完成、MCP 端点配置好；因内存停栈，未做一次真实检索 |
| 全量整网仿真 | ❌ 未跑（重资源，按规则同时只跑一个） |

---

## 6. 明确不做的事

- 不自动推送 Git、不 rebase/reset/clean 对方改动；
- 不烧录、不删除外部数据、不移动厂商原件 `D:\FPGA\AX7Z020`；
- 不改写 Codex 的 RunId 证据与失败记录；
- 不改 `src/`、`sim/`、`vivado/`、`docs/`、`report/`（本轮 DSH 全程未动）。

---

## 7. 回滚方法（如需撤销 DSH 的环境改动）

| 改动 | 回滚 |
|---|---|
| `cordis.patch.yml` 新增 provider/MCP 条目 | 用 `cordis.patch.yml.bak-20261017` 覆盖（仅该文件） |
| `JL_DS_API_KEY` 环境变量 | `Remove-ItemProperty HKCU:\Environment JL_DS_API_KEY` |
| 许可文件 | 删除 `D:\Xilinx_licenses\`（不影响原 `Downloads\Xilinx.lic`） |
| 知识库栈 | `.\amd-embedded-doc-search.exe purge`（会删数据卷，重新导入约 10 分钟） |
| WSL 包 | 设置 → 应用 → 卸载 "Windows Subsystem for Linux" |
| 临时探针 | 删除 `D:\tmp\vivado_test\` |

---

## 8. 一句话交接

**工具链已经通了（许可修复 + 综合/实现/比特流/仿真/JTAG 全部实测），DSH 与 Codex 按方案 A 共用本仓库轮流独占写；明天上板前必须先补 XDC、清掉不匹配的增量检查点，并给板子上电。**