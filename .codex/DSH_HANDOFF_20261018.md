# DSH → Codex 交接文档（2026-10-18，v2 交接核实修正版）

- 作者：DSH（DeepSeek Harness，Team Lead `lead`）
- 接收方：Codex（同一仓库 `D:\FPGA_Competition`，当前 2B 工作树 `w2b`）
- 触发：Wong 要求把 DSH 本轮动作完整交接给 Codex，并明确双方**按任务轮流独占写**协作
- 修订：**v2 = 按 Wong 2026-10-18 指令逐条核实后的修正版**；v1（同日 51f7130）中若干声明被证实不准确，对照见 §9
- 本轮性质：**只做离线审计与入口补齐**；未做 XDC、reset_run、重新综合、上板、烧写、JTAG 访问
- 时间口径：UTC+8

---

## 0. 协作模型与统一入口

方案 A（按任务轮流独占写），规则在根 `AGENTS.md`「与 Codex 共享同一工作区（2026-10-17）」：

| 规则 | 落地要求 |
|---|---|
| 单写者 | 同一文件同一时刻只有一个写入方；开工前核对对方是否已**明确让出** |
| 锁 | 锁路径必须用 `git rev-parse --git-path index.lock` 解析（不能硬编码 `.git/index.lock`，工作树的 gitdir 不同） |
| 无锁 ≠ 空闲 | 还要核对进程、会话归属、资源占用（本机 16 GB，只允许一个重型任务） |
| 提交串行 | 不并发 `git add/commit`；只提交本轮相关文件；不 rebase/reset/clean 对方改动；不推送 |
| 证据互不覆盖 | 各自新 RunId、独立目录；不改写对方 RunId 与失败记录 |
| STATE 分工 | 主目录 `.codex/STATE.md` 只放**全局状态、当前任务归属、各阶段入口**；阶段工作树（`w2b`）STATE 放**该阶段技术事实**，不互相复制矛盾全文 |

**上一方未明确让出的任务只读**：不抢占、不结束对方进程、不并发提交、不跑重型任务。

本轮实测锁状态（2026-10-18 10:45）：`main` 与 `w2b` **均无 index.lock**；无 vivado/xsim/hw_server/cs_server 进程；端口 3121 无监听；RAM 可用约 5.9 GB。

---

## 1. 本轮准确工作树 / 分支 / 提交

`git worktree list`（2026-10-18）：

| 工作树 | 分支 | 提交 | 本轮角色 |
|---|---|---|---|
| `D:\FPGA_Competition` | `main` | 基线 `51f7130`（v1 交接提交），本轮结束提交见 §11 | **DSH 写入方** |
| `D:\FPGA_Competition\w2b` | `codex/stage2b-dma-g0` | `2e9e3c6` | **只读审计**（Codex 所有，未写入） |
| `D:\codex-worktrees\96a3` | `codex/stage2b-t01-board-audit` | `e26feea` | 未访问（较早 2B 工作树） |
| `D:\codex-worktrees\dbdf` | `codex/stage3-video` | `896e6c7` | 未访问（阶段 3） |

`w2b` 未提交改动 **104 项**（含 `.codex/STATE.md`、`vitis/run_s2b_model_qualification.py` 两处已跟踪修改 + 大量未跟踪证据目录）；归属 Codex，DSH 未改。

主目录本轮 DSH 精确写范围：`.codex/STATE.md`、`.codex/DSH_HANDOFF_20261018.md`、`report/evidence/CTRL-DSH-HANDOFF/handoff_20261018_r01/**`、`tmp/CTRL-DSH-HANDOFF/**`（tmp 属忽略目录）。

---

## 2. DSH 2026-10-17 夜 ~ 10-18 凌晨的动作（修正版）

### 2.1 本地文档栈（AMD 文档检索）

| 项 | 事实 | 证据等级 |
|---|---|---|
| 包解压 | `20260918.qwen3-embedding-0.6b.tar.gz` → `C:\amd-doc-search`（images 3.27 GB、models 1.12 GB、CLI 20260918） | 配置事实（可复核目录） |
| WSL 安装 | `Microsoft.WSL` 2.7.13.0，内核 6.18.33.2-2（本轮 `wsl --version` 复核） | 原始证据（命令输出） |
| Docker | 客户端/引擎 29.8.2；Docker Desktop 产品版本 4.95.0.242831；`doctor` 三项通过（当时输出） | 原始证据（当时输出，本轮引擎已停，未能复跑 doctor） |
| 文档导入 | `weaviate-docs-import-1 exited with code 0`，`importing docs: 725911/725911 (100.0%)` | **原始证据**：`D:\tmp\docsearch_configure.log`（2.66 MB，UTF-16LE），摘录见证据包 `docsearch_configure_key_lines.txt` |
| 容器状态 | 3 容器起来后 mcp-1 因 Weaviate 建索引领先超时 crash-loop（日志中 8 次 FATA），随后用户以内存不足要求停止 | 原始证据（同一日志） |
| 当前状态 | 容器已 `stop` 并移除；**数据卷保留**（下次 `start` 不需重新导入）；Docker Desktop 已退出 | 配置事实 |
| MCP 条目 | DSH 配置内 `mcp-doc-search` → `http://127.0.0.1:8080/mcp/doc-search`；服务未运行故 disconnected | 配置事实 |

> 未做：一次真实的文档检索查询（停栈前未来得及）。**本轮不重启高内存文档栈、不重新导入。**

### 2.2 DSH 模型路由 `jl-ds`

脱敏配置差异（`C:\Users\22061\.dsh\profiles\desktop\cordis.patch.yml`，密钥仅在用户环境变量，不落文件）：

```yaml
providers:
  jl-ds:                                        # 新增 provider
    api: openai-completions
    baseURL: https://dashscope.aliyuncs.com/compatible-mode/v1
    apiKeyEnv: JL_DS_API_KEY                    # 值在 HKCU\Environment，长度 116，未写入任何文件
    reasoning: high
    compat:
      thinkingFormat: qwen
      supportsReasoningEffort: true
      supportsDeveloperRole: false
    models:
      - id: deepseek-v4.1-flash
        name: JL-ds
        contextWindow: 1000000
        maxTokens: 393216
        reasoningEfforts: { "off": , low: low, high: high, max: max }
  openai:
    compat:
      supportsDeveloperRole: false              # 新增（该 provider 原无 compat）
```

**适配器实际发送行为**（来自打包代码 `@earendil-works/pi-ai/dist/api/openai-completions.js` L631-638，本地解出副本 `D:\tmp\openai-completions.js`）：

```js
else if (compat.thinkingFormat === "qwen" && model.reasoning) {
    params.enable_thinking = !!options?.reasoningEffort;
    if (options?.reasoningEffort && compat.supportsReasoningEffort) {
        const effort = model.thinkingLevelMap?.[options.reasoningEffort] ?? options.reasoningEffort;
        if (typeof effort === "string") params.reasoning_effort = effort;
    }
}
```

并且 DSH 适配器（`dsh-llm-pi-ai/lib/index.js`）在模型声明 `reasoningEfforts` 时会置 `reasoning: true` 并生成 `thinkingLevelMap`（L586-606）；`off` 档在更上层被解析为“不发 reasoning 字段”（L1755）。

因此本配置下的**预期**线上行为：
- `off` → `enable_thinking=false`，无 `reasoning_effort`
- `low/high/max` → `enable_thinking=true` + `reasoning_effort=<同名档位>`

已验证 / 未验证必须分清：

| 项 | 状态 |
|---|---|
| API 接受 `reasoning_effort=low/high/max` | 已证实（对百炼端点直连 curl，3 次均 HTTP 200） |
| `enable_thinking=false` 关闭思维链 | 已证实（curl，`reasoning_content` 为空、completion=1 token） |
| `400 developer is not one of [...]` 修复 | **部分证实**：源码路径确会因 `model.reasoning && supportsDeveloperRole` 发 `developer` 角色（L: `const instructionRole = ...`），置 false 后预期走 `system`；**但没有 DSH 出口请求抓包**，未在 DSH 层复现“修复后不再报 400” |
| 档位在 DSH 内实际生效 | 未验证（无 DSH 层请求/响应记录） |

> 结论：字段存在**不等于**已在 DSH 内验证修复成功；本轮不删字段（删除会更难复核），但保留上述限制。

### 2.3 ROSS 技能数量（修正）

- `C:\Users\22061\.dsh\skills`：**50 个目录、49 个 `SKILL.md`**
- 分布：`hls-*` **21**、`vai-*` **13**、`segcfg-*` **7**、`vivado-*` **6**、`hw-*` **2** = 49
- 唯一无 `SKILL.md` 的目录是 `hls-scripts`（共享脚本目录，非技能）
- v1 写的“50 个技能”不准确（50 是目录数）。未重装、未增补缺项。

### 2.4 Vivado 许可修复（已证实）

- 现象：`synth_design` 失败，`Failed to get the license for feature 'Synthesis' and/or device 'xc7z020'. Explanation: A license feature for Synthesis was found but is expired.`
- 根因：Vivado 自动命中了 `C:\Users\22061\Downloads\Xilinx.lic` 内 **2026-10-06 到期的 Enterprise 试用**条目，且不会自动回退免费档。
- 修复：抽取仅含有效条目的 BASIC 许可 → `D:\Xilinx_licenses\basic_only.lic`（`Vivado_Basic/Synthesis/Implementation/Simulation`，有效至 **2027-08-07**）；并在 DSH 的 `mcp-vivado.config.env` 注入 `XILINXD_LICENSE_FILE`（**未**写入用户级环境变量，本轮复核该用户变量为空）。
- 生效验证：批处理探针日志出现 `A valid Vivado Design Suite BASIC license has been detected`，且综合成功（`SYNTH_OK cells=8 nets=11`，exit 0）。

### 2.5 Vivado 探针实测（严格限定，禁止外推）

| 项目 | 结果 | 说明 |
|---|---|---|
| 综合（探针） | ✅ `SYNTH_OK`，exit 0 | 仅 `src/counter.sv`，与真实工程/2B 平台无关 |
| 实现 | ✅ 布/布线成功（探针顶层设计） | 无时序约束 |
| 比特流 | ⚠️ 生成 4,045,762 B | **先被 `NSTD-1`/`UCIO-1` 拒绝，把 DRC 严重度降为 Warning 后才生成**；不得作为板级安全或阶段通过证据；未提交 Git，仅登记 SHA |
| xsim 仿真 | ✅ `xvlog` 0 / `xelab` 0 / `xsim` 0（**三个原生退出码分别记录**） | `tb_counter` 自检通过：打印“计数器测试完成”，`$finish @106 ns`（tb_counter.sv:91），无断言失败 |
| 覆盖率 | ❌ **未采集** | 只跑单个自检测试台，无随机化/回归/覆盖；总批处理退出码不作为通过依据 |
| JTAG | ⚠️ 只读到线缆 `Digilent/210512180081`，器件列表为空 | 板卡未上电；本轮不再访问硬件 |

### 2.6 `AX7Z020_Gesture.xpr` 变更归因（本轮新增核实，修正 v1 的“未动 vivado/”声明）

- 现状：`git status` → ` M vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr`；mtime **2026-10-18 02:26:41**；当前 SHA256 `74629099ac3d509ea2cff78b6d9857125081f8e90d841a99f7ecc2cff2d1be85`
- HEAD 版本 SHA256 `c9b26859645b77055d71766e2719825eFF80DF4732E20E48A4F02F9B0A20DA02`；相对 HEAD 差异 **12 增 / 1 删**（新增 `utils_1` 下 `rom_controller.dcp` File 条目、三个 sim fileset 的 `<Filter Type="Srcs"/>`、`synth_1` 的 `IncrementalCheckpoint` 属性）
- 归因证据：
  - DSH 会话 `vivado-20261018-022030-75e83746` 的 journal（`raw/vivado_61230718_3ce19e70.jou`）在 02:20–02:26 记录了 `open_project` 与 `close_project`；
  - `.xpr` mtime 02:26:41 与 `close_project` 时间吻合；
  - 同时该会话 `open_hw_manager` 生成/更新了工程内 `AX7Z020_Gesture.hw/`（02:26:12，`*.hw/` 已被 .gitignore 忽略）
- **无法归因的部分**：02:26 之前没有任何 `.xpr` 快照或哈希，无法证明这 12 行差异是本次回写引入还是此前已存在（工程内旧 `vivado.log` 2026-10-11 已显示 incremental/BoardPart 条件存在，但那是工程状态，不是文件内容快照）。
- 处置：**不擅自回退**现有差异（Wong 指令）；事实、哈希、差异全文存于证据包 `xpr_worktree_vs_head.diff` / `xpr_head_committed.xml`。

### 2.7 证据包（本轮新增）

- 目录：`report/evidence/CTRL-DSH-HANDOFF/handoff_20261018_r01/`
- `manifest.json`（SHA256 `b0ac4ca77462511db7196c5a24034cd8d526db7b771dc4e0a17d97cdc7d07584`）：区分**运行时绑定证据**（原生退出码、日志文本）与**打包时计算的哈希**（`sha256_packaging_time`），并列出限制
- `raw/`：许可探针脚本与输出、xsim 日志、Vivado 会话 journal/log、proxy log（只读复制；**原件仍留在 `D:\tmp\vivado_test`**，未删除未移动）
- `xpr_*`：`.xpr` 归因证据；`docsearch_configure_key_lines.txt`：文档栈导入完成摘录（原件 2.66 MB 保留在 `D:\tmp`）
- **事后哈希不冒充运行时绑定**；探针 bitstream 不进 Git，仅登记 SHA256 `56cccf11a7165b9327b5c12334d9e9ab8081fbe777694f1fbbfbd6a6f538b9f5`

---

## 3. 事实分级

**已证实（有可复核原始证据）**：许可属性与修复、BASIC tier、探针综合/实现/xsim 原生退出码、xsim 自检结果、`.xpr` 被本次会话回写的时间与差异、文档栈导入 725911/725911 完成、WSL/Docker 版本、技能 49/50 分布、R14 阻断与收据状态。

**已纠正（v1 不准确）**：技能数量 50→49；xsim 结论改为“原生退出码 + 自检 + **无覆盖**”；`D:\tmp\vivado_test` 证据已封包；“补 XDC/清增量”不再是通用下一步（仅主目录小工程）；回滚改为精确条目。

**无法核实（明确保留）**：`.xpr` 12 行差异是否全由本次回写引入（无前态快照）；DSH 层是否真的不再发 `developer` 角色（无请求抓包）；文档栈是否真能完成一次检索（停栈前未试）；板卡器件（未上电，未访问）。

---

## 4. 阶段 2B 真实状态对齐（只读审计，DSH 未写入 `w2b`）

- **R14 = 最新且仍有效的阻断**：`report/evidence/S2B-T19/single_sample_qualification_20261017_r14/model_qualification_result.json`
  - `status=BLOCKED`、`hardware_execution=NOT_RUN`、`hardware_attempted=false`、`cold_lifecycle_proven=false`、`native_exit_code=2`
  - 错误：`VisibilityProbeError('必须通过Vitis2026.1脚本入口')`，抛出点 `vitis/run_s2b_visibility_probe.py:373`（`require("v2026.1" in os.environ.get("XILINX_VITIS_VERSION",""))`）→ 运行器未在 Vitis 2026.1 脚本入口环境中启动
  - 记录 `source_commit=2e9e3c6`，但**实际执行的是 HEAD + 未提交改动**（见下），源码归属需按未提交差异处理
  - 该 Run 的 `identity.before_sdk` 快照记录当时存在 `hw_server.exe`（Vitis 路径，PID 13632）监听 3121；**当前已无该进程、3121 无监听**
- **收据与锚点**：
  - 最新独立 Reviewer 收据 r04：`qualification_single_sample_review_20261017_r04/qualification_receipt.json`，`role=INDEPENDENT_REVIEWER`、`status=PASS`、`source_commit=a270d024`、文件 SHA256 `f6d94bb6...`（与工作区锚点一致）
  - 其 `review_outcome.json` 明确范围：“仅批准 visibility=1 的 sample000 单样本资格入口机制；**不代表硬件启动已发生或 sample000 结果通过**”，`g3/g4/g5=NOT_PASSED`
  - **HEAD（2e9e3c6）绑定的仍是 r01 收据**（`8a64ad52...`）；指向 r04 的改动**未提交**，且路径写成绝对盘符（可移植性问题）
  - 收据 PASS ≠ 实板通过；R14 的 `hardware_execution=NOT_RUN` 是当前事实
- **`w2b/.codex/STATE.md` 过时点（建议 Codex 修正，DSH 不写）**：头部仍写 `HEAD=b0099b8`（实际 `2e9e3c6`）；正文称“当前正式资格收据仍不支持签发”，而 r04 PASS 收据已存在（范围仅限入口机制）；另缺 R14 BLOCKED/`native_exit_code=2`/Vitis 入口要求这一最新阻断。
- **未被过时 STATE 误导的核查结论**：不能因为旧 STATE 说“缺收据”就断定收据缺失；也不能因为收据 PASS 就推断实板通过。两者都已按原文件核对。

---

## 5. 上板前阻碍（**仅针对主目录小工程 `vivado/AX7Z020_Gesture`**）

| 阻碍 | 事实 | 与 2B 的关系 |
|---|---|---|
| 无约束文件 | `constrs_1` 为空，`vivado/` 下无 `.xdc`；bitgen 会被 `NSTD-1`/`UCIO-1` 拦 | **无关**：2B 平台在 `w2b`，有自己的 XSA/bit 与约束链 |
| `synth_1` 状态 `synth_design ERROR` + `INCREMENTAL_CHECKPOINT` 指向 `xa7z020clg400-1I` 的 dcp 与 run part `-2` 不符；BASIC 许可不含 Incremental | 打开工程即有 CRITICAL WARNING | **无关**：不得据此改动 `w2b` 的 run |
| 板卡未上电（只读枚举到线缆） | 本轮不访问 JTAG | 2B 的板级门依旧关闭 |

> **2B 应核对自己的最新失败与资格入口（R14 + 锚点链路），不是补主目录小工程的 XDC 或清它的增量。**

---

## 6. 统一入口与交接记录

- 主目录 STATE：全局状态 + 当前任务归属 + 各阶段入口（2A 已冻结；2B → `w2b/.codex/STATE.md`；3 → `dbdf`）
- 交接记录一行式（本轮已写入主 STATE）：`任务 | 负责人 | 工作树/分支 | 起始提交 | 允许修改范围 | 未提交改动归属 | 状态 | 下一接手方`
- 接手前必查：`git rev-parse --git-path index.lock`、进程/会话归属、对方是否明确让出

---

## 7. 明确不做的事

不推送；不 rebase/reset/clean 对方改动；不写 `w2b`；不结束对方进程；不重启/重装共享工具；不改写对方 RunId 与失败记录；不补跑主目录小工程综合；不补 2A；不进入其他阶段；不烧录、不访问 JTAG、不加载 DDR 模型；不动厂商原件 `D:\FPGA\AX7Z020`。

---

## 8. 回滚（只列本轮**实际**改动的精确条目）

| 改动 | 精确回滚方式 | 注意 |
|---|---|---|
| `jl-ds` provider 块 | 从 `cordis.patch.yml` 删除该 provider 块 | 不通篇覆盖配置；`cordis.patch.yml.bak-20261017` 是更早备份，直接覆盖会丢 MCP 条目 |
| `openai.compat.supportsDeveloperRole` | 删除该单行 | — |
| `mcp-vivado.env.XILINXD_LICENSE_FILE` | 删除该单行 | 删除后需重启 MCP 才会失效 |
| `JL_DS_API_KEY` 用户环境变量 | `Remove-ItemProperty HKCU:\Environment JL_DS_API_KEY` | 仅删该名字 |
| `D:\Xilinx_licenses\basic_only.lic` | 删除该**单个文件** | 原 `Downloads\Xilinx.lic` 不动 |
| 文档栈 | 已 `stop`；镜像与数据卷保留 | **`purge` 会删数据卷（需重新导入），不是默认回滚步骤** |
| WSL 包 | 属系统级安装（Docker 依赖） | **默认不卸载**；如需移除须 Wong 明确决定 |
| 证据包 | 保留（属证据） | `D:\tmp\vivado_test` 原件保留 |

---

## 9. v1 → v2 修正对照

| v1 声明 | v2 修正 |
|---|---|
| “DSH 本轮未动 `vivado/`” | 更正：`open_project/close_project` 导致 `.xpr` 于 02:26:41 回写（12+/1-），`open_hw_manager` 另生成 `*.hw/`；差异前态无快照，不冒充未动 |
| “50 个 ROSS 技能” | 更正：50 目录 / **49 SKILL.md**（hls21/vai13/segcfg7/vivado6/hw2），`hls-scripts` 例外 |
| “xsim 通过（exit 0）” | 更正：三阶段**原生退出码分别** 0/0/0 + 自检通过；**覆盖率未采集**；总退出码不作为通过依据 |
| “bit 生成成功” | 更正：曾因 DRC 被拒，降级 Warning 后才生成；仅证明工具链能出文件 |
| “档位已修好可用” | 更正：源码路径与 API 直连已验证；**DSH 层未做请求抓包**，不宣称 DSH 内已生效 |
| “补 XDC / 清增量是下一步” | 更正：仅针对主目录小工程；2B 下一步是核对自己的资格入口与锚点 |
| “回滚：删除许可证目录 / 覆盖配置 / purge 数据卷 / 卸载 WSL” | 更正：改为逐条精确回滚，上述动作都不是默认步骤 |

---

## 10. 未执行项 / 限制 / 需要 Wong 提供

**未执行**：真实工程综合/实现/比特流；XDC 编写；2B 单样本实板执行；文档栈实际检索；ILA/VIO 实机抓取；100 样本 / 1000 连续任务；主目录小工程 run 状态修改。

**限制**：`.xpr` 内容差异无法完全归因；DSH 层模型请求无抓包；探针与真实工程无时序/约束意义；证据包哈希为打包时计算。

**需要 Wong 输入**：①AX7Z020 引脚/电平资料（写 XDC 用）；②板卡上电与 JTAG 访问授权；③是否授权改动主目录小工程 run 状态（清增量 + reset）；④2B 的 Vitis 2026.1 脚本入口运行方式确认（R14 阻断的直接原因）。

---

## 11. 本轮结束提交

见主目录 STATE「本轮交接记录」一行与最终回复；v1 提交为 `51f7130`。