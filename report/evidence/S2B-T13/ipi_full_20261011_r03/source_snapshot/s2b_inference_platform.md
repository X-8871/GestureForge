# 阶段 2B 全模型平台构建候选

版本 `s2b-inference-platform/0.1.0`，依据 `s2b-physical-candidate/0.1.1`；字段入口为同目录 JSON。此文件说明实际构建和证据约束，不声明物理接口已冻结或阶段 2B 已验收。

用户提供的芯片字符串原样保存为 `XC7Z020-2CLG400I`。Vivado 精确器件候选为 `xc7z020clg400-2`；生成时核对 `get_parts` 唯一返回，并记录可获得的 temperature/grade/speed/package 属性。工具名称不含 `I` 不能单独证明实物工业温度等级。DDR/UART 请求调用冻结 `s2b_ps_platform::requested`，只增加 GP0、HP0、FCLK0/reset 与 50 MHz 配置，不使用通用 board preset 替换厂商字段。

## 模块、地址和物理端口

JSON 声明 18 个 RTL 文件：冻结 2A 全核心综合闭包 14 个，新增 2B guard、word adapter、控制器和 `s2b_inference_top`。顶层只通过 2A 公共 CSR/memory 口连接，不读取或依赖内部状态。adapter 内已有 guard 实例，不重复串接第二套 guard。

PS GP0 为 AXI3、32 位数据、12 位 ID，经 `axi_protocol_converter` 到 AXI4-Lite、32 位数据与完整 32 位地址，再到控制器；地址分配 `0x43C00000` / 64 KiB。控制器自行校验完整地址，不截断到低 16 位后盲目接受。HP0 为原生 AXI3、64 位数据、6 位 ID，直接连接 adapter；保留 AXI3 WID、2 位 LOCK 和 4 位 LEN，不套用 AXI4 的早 B 依赖规则。HP 可寻址 1 GiB 是 PS address segment；PL 许可仍由 guard 逐对象限制，完整模型专属 DDR arena 为 `[0x10000000,0x12000000)`。

软件只发对齐 32 位、单 beat、Device/Strongly-ordered MMIO。Lite 口没有 LEN，转换器可以拆 burst，下游控制器无法判断原 GP0 burst；本结构的单 beat 前提必须由实际 PS 指令、MMU 属性、反汇编和集成输入验证确认。不能宣称控制器拒绝了上游原始 burst。GP0 STATUS 读不是 HP0 写屏障。

FCLK0 50 MHz 同时驱动 GP0/HP0 ACLK、转换器、reset 同步器和完整推理 RTL。FCLK_RESET0_N 接 active-low `proc_sys_reset.ext_reset_in`；aux/debug 接 0、dcm_locked 接 1，同步释放的 peripheral_aresetn 同时接转换器与完整 RTL。此时钟来自 PS，未增加 MMCM；dcm_locked 常量仅表示无独立锁相器，不能证明可见性或实际时序收敛。BD 唯一物理外口为 DDR/FIXED_IO，UART 通过固定 MIO，不增加未经板级资料核验的 PL 引脚约束。

## 冷复位与可见性启用

`cold_resetn` 只用于统一 PS/DDR/PL 冷初始化。运行中禁止软件独立切换 FCLK reset、PS7 reset 或重下 PL 位流；上述操作会丢弃 adapter 账本，随后继续旧 CPU 任务或复用旧 arena 不安全。FAULT 未合法闭合必须停止旧软件和 CPU1/其他 writer，统一初始化 PS/DDR/互连/PL、重新初始化 arena、消除旧 cache 副本并进入新 epoch；总控冷 JTAG 操作须保留实际生命周期证据。此约束由部署流程执行，当前接线没有硬件识别“全体系冷复位”的能力，不能把单独 FCLK reset 自动解释为冷恢复。控制器 soft_reset/cancel 保留物理账本并排空，不连接到该冷复位线。

`PROFILE_VISIBILITY_PROVEN` 默认 0，无软件寄存器可置 1。默认构建可用于离线审阅和静态网表验证，不能宣称 DONE_SAFE 已可用。visibility=0 并不禁止 START；一旦启动则不能依靠该构建取得 SAFE/ACK 后重新读 arena，因此首次先验探针必须全程保持 `IDLE_PS`、epoch=0、从未 START、未 LOAD，由 CPU 合法独占 arena。

首次缓存先验使用 CPU0 ↔ JTAG DAP 第二 master，不让 HP 发起模型任务。T15 公开候选传输为 `S2BU/1`、operation=4、40 字节 header、12 字节 payload（phase/cpu_seed/dap_seed）；仅访问物理 `0x10000000` 起的 256 字节、64 个 word，word i 为 `seed ^ ((0x9e3779b9 * i) mod 2^32)`。phase0 CPU 写 cpu_seed pattern、实际 BSP FlushRange+DSB 后回复 WAIT_DAP；总控 DAP 读取完整 256 字节核对，再写 dap_seed pattern 并完整读回。phase1 使用同一 seed pair，实际 BSP InvalidateRange+DSB，CPU 真实比较 64 word，期间禁止 LOAD/RUN；任何不符 fail-stop。响应为 40 字节 meta 加 256 字节实际原字节，保留 header/payload CRC；成功 code=0，失败 code=7 且保留原字节后停止。该先验须绑定最终同一 ELF、BSP、MMU、编译宏及实际 PS 初始化、统一冷生命周期、CPU1/其他 writer 静止、专属 arena 证据与原始 UART/DAP 读写记录；当前 T15 未冻结时仅说明 ABI，不伪造通过或固定其未交付 SHA。

HP 路径另以实际全模型 BD/网表、adapter 两路 AxCACHE=0000、直接 HP0 无桥/无早写响应及官方 AXI3 非 Bufferable / UG585 原始依据独立证明。CPU/DAP 先验只验证上述实际 BSP/cache 路径，不能代替 HP→CPU 模型输出；启用参数 1 后，真实 HP 传输、CPU golden 比对和完整模型结果仍是 G3 必须项。此入口不改变 SAFE 的停止、账本排空和可见性条件。

启用参数由 `run` 同时接收证明 JSON、独立审查 JSON，以及总控从真实独立 Reviewer 返回来源冻结的审查原件 SHA-256。只读检查器只返回 `VISIBILITY_PROFILE:BINDINGS_VERIFIED`，表示文件绑定匹配；总控仍须核对审批来源、原始证据语义和允许的启用范围。

证明 JSON 包含 `schema_version=1`、`status=PASS`、`profile_version`、`source_sha256` 和两项 `hp_path_audit` / `ps_cache_proof`（每项为仓库相对 `path` 及真实 `sha256`）。`source_sha256` 的精确文件集合由检查器的 `check_static` 返回，包含 18 个 RTL、构建脚本、平台字段和检查器本身。源文件或平台配置变化使旧证明失效。

两项证据 JSON 均须 `status=PASS`、同一 `source_sha256`、非空 `evidence_files`（各原始文件 path/hash）与布尔 `checks`。HP 审计要求 `axi3_nonbufferable_basis`、`axcache_0000_full_path`、`direct_hp0_no_bridge`、`no_early_write_response`、`full_model_core_present`。PS 证明要求 `dedicated_32mib_arena`、`cache_maintenance_actual_bsp`、`cpu_dap_prior_probe_idle_no_start`、`same_runtime_bsp_mmu_macros`、`no_use_amp`、`single_cacheable_alias`、`cpu1_other_writers_stopped`、`unified_cold_reset_lifecycle`。

PS 证据的 `prior_probe` 字段包含上述 visibility/state/epoch/start_count/load_count、ABI、地址/长度/word 数、`phase0=FLUSH_DSB_WAIT_DAP`、`phase1=INVALIDATE_DSB_COMPARE`、`dap_read_write_readback=true`。PS 证据与证明 JSON 均含一致的 `runtime_bindings`，其中 `elf`、`bsp`、`mmu`、`macros`、`ps_init`、`cold_lifecycle`、`uart_log`、`dap_log` 各绑定仓库内实际原件 path/hash。实际网表、规范依据和运行记录必须存在原件；布尔字段及哈希只做机器绑定检查，真实过程与语义由 Reviewer 核查。

独立审查 JSON 须 `status=PASS`、`role=INDEPENDENT_REVIEWER`、`approved_profile_sha256` 绑定证明原字节、`visibility_parameter=1`、`cold_reset_only=true`；调用者还须提供从独立 Reviewer 实际交付通道取得并冻结的该原件 SHA-256。机器不能识别真正的 Reviewer 来源，自填 role/PASS 或从自造 receipt 计算哈希都不构成批准。总控核对原始返回来源后才可调用启用入口。该机制防止误用过期文件，不是密码学签名；当前未生成有效证明或启用记录，默认保持 0。

## 隔离重建入口

先执行轻量检查：

```bash
python -B verification/check_s2b_inference_platform.py
```

在总控核对资源、重型占用与会话归属后，使用新的 Tcl batch 会话调用 `::s2b_inference_platform::run repo_root project_dir evidence_dir helper native_log`；全部参数是已核验的绝对路径，project_dir/evidence_dir 必须不存在、互不相同且不嵌套，精确父目录已存在。入口在 source 或创建目录前逐组件核对大小写、名称与类型，拒绝链接、junction/reparse、点组件和可能被 Windows 折叠的新名称；Windows reparse 属性由固定只读 .NET 调用补核，路径作为 Base64 数据传入，失败立即停止。repo_root 指当前工作树，project_dir 放 `tmp/2B/S2B-T13/<新RunId>/project`，evidence_dir 放 `report/evidence/S2B-T13/<新RunId>`；helper 指已安装 ROSS `lib/ipcfg.tcl`，native_log 必须是该 batch 当前实际日志，不能绑定其他会话日志。入口拒绝已有打开项目，不改用户 GUI 工程或厂商原件。

启用 profile 时，在上述参数后追加 proof/review 两个绝对 JSON 路径及固定 review_sha256；三项一起提供且实际字节全部匹配才允许将构建参数置 1。独立运行检查器对应参数为 `--visibility-proof`、`--review`、`--review-sha256`。脚本运行 IPI 配置、强制 BD validate、接口/直接 HP/物理端口读回、输出产品和不含位流 XSA，不运行综合、实现或硬件操作。每项 IP 使用 ROSS capture 和实际参数读回，失败原件保留，重跑另建 RunId；不能清除尝试账本以绕过技能限制。

后续综合/实现由总控独立安排，须保存实际完整闭包和源码哈希、50 MHz 时钟/复位约束、资源/时序结果、bit/XSA/PS 初始化匹配版本及真实 G3 结果。不能用旧 PS-only XSA、1 MiB smoke 或完整失败证据包装检查代替全模型验收。
