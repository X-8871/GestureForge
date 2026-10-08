# PS UART/DDR 前置检查

本应用供阶段2B前置检查使用，只消费经独立审查绑定的 S2B-T04 PS-only、无位流 XSA。它不消费检测网络或 PS/PL 总线接口。离线 ELF 构建与布局核验通过仍不代表 UART/DDR 已实测；本次硬件执行状态必须保持 `NOT_RUN`，直至获得明确实物授权并保留真实串口结果。

当前离线成功候选为 `ps_smoke_20261008_r01/build_08`，固定上游提交 `90652b45ef31e763bd3e6f7527e2fd080ece61a8`；正式批准为 `docs/obsidian-project/04-提交材料/阶段验收/stage2b_ps_platform_offline_freeze_20261009.md`，版本 `s2b-ps-platform/1.0.1`，SHA-256 `89512d94859abf083e958a2e53139d8f4ab0c0a61989c76eb8794eba9c9db6c1`。本次实际软件源码另按 SHA 绑定，不把上游提交当成未提交软件的版本证明。

## 软件行为

`s2b_ps_smoke.c` 使用实际 SDT BSP 的 `XUartPs_LookupConfig(UINTPTR BaseAddress)`，UART1 基地址必须同时与 XSA、canonical BSP 宏及 BSP 的 stdin/stdout 一致。运行时配置 115200、8 数据位、无校验、1 停止位、无流控，关闭 UART 中断，并回读数据格式、工作模式及流控位。发送为每字节有界轮询；每个等待最多 10,000,000 次寄存器/驱动检查，这不是经过实测的秒数超时。

UART 首先输出 ASCII `BEGIN S2B-T06-1`，随后 `BUILD c_sha256=... xsa_sha256=...` 绑定本次实际C源码及固定XSA，再输出 UART 配置、buffer 起点和半开区间结束地址、字节数、word 数、对齐及缓存行及运行配置。BUILD 宏由构建时核验的文件SHA-256生成；`SMOKE_VERSION` 只标程序协议版本。BUILD 行不是运行ELF的自哈希，实际ELF仍由PC文件校验和授权下载记录绑定。UART 初始化失败返回非零并发布 `s2b_smoke_result=0x81`，UART 发送或格式化失败发布 `0x83`；UART 本身失效时不能保证发出 FAIL/END。状态对象64B对齐，每次发布都执行赋值、DSB、实际 BSP FlushRange、DSB，将状态写回 DDR，避免 DAP 物理读看到旧缓存值。状态 `2` 只在最终 PASS 和 END 全部发送成功后发布。

DDR 对象为 1 MiB、64 字节对齐、静态存储期的 `.s2b_smoke_buffer` 专属 NOLOAD 节。2 轮，每轮以下 8 个确定性模式，每项写入及核验 262,144 个 32-bit word。完整成功共核验 4,194,304 个 word。没有随机样本。

| pattern | 每个 word 的期望值 |
|---|---|
| 0 | `0x00000000` |
| 1 | `0xFFFFFFFF` |
| 2 | `0xAAAAAAAA` |
| 3 | `0x55555555` |
| 4 | 当前 word 索引 |
| 5 | 当前 word 索引按位取反 |
| 6 | `1 << (word_index & 31)` |
| 7 | 模式6按位取反 |

每项完整写入后执行屏障、`Xil_DCacheFlushRange`、屏障、`Xil_DCacheInvalidateRange`、屏障、逐 word 读回。实际 Cortex-A9 BSP 代码确认维护 32B 缓存行及 L1/L2；编译拒绝 `USE_AMP`。程序显式启用 DCache，读写使用 volatile 指针，范围完全对齐。该流程核验 DDR 中的该对象，不是只在缓存内回读，也不是全 DDR 扫描或完整 DDR 稳定性认证。

出错时核验完当前模式的全部 word，输出首个 byte offset、expected/actual、该项总不匹配数及累计核验量，随后停止后续项并输出 FAIL/END。成功时应出现 16 行 PATTERN_PASS，以及 `PASS passes=2 patterns=8 verified_words=4194304 mismatches=0` 和 `END S2B-T06-1`。仅有 BEGIN、部分 PATTERN_PASS 或调试器未返回都不能算通过。

## 地址与独占证明

构建脚本读取实际固定 XSA 的 `PCW_DDR_RAM_BASEADDR/HIGHADDR`，并要求与实际自动生成 linker DDR 区域完全一致。低于该 origin 的启动保留区保持不分配。把原 DDR 区域缩为 16 MiB 的应用区，紧接着新增 1 MiB `s2b_smoke_ddr` 区域，专门接收 buffer；其余 DDR 不由本应用声明使用。地址从真实上游推导，源码不手填物理 buffer 地址。原先跨全 DDR 的默认 linker 不是安全窗口证据。

`check_s2b_ps_smoke_layout.py` 联合检查实际文件 SHA-256、XSA HWH、BSP UART/stdio 宏、缓存驱动源码、linker Memory、ELF32 ARM header/program/section/symbol 和 GNU map。它要求：buffer 精确 1 MiB、64B 对齐、独占 NOBITS/ALLOC/WRITE 节、唯一对象、全部其他 ALLOC 位于应用区、全部 LOAD 无重叠且位于分区包络、LOAD 文件字节不进入 buffer、没有32位溢出、入口与 `_vector_table` 一致。

全部 user/IRQ/supervisor/abort/FIQ/undef 栈和 heap 的边界、大小及所属节单独核验；user stack/heap 各16 KiB。运行时再次核对 buffer 对象、链接边界和生成头常量，并要求 MPIDR 指示 CPU0，再允许第一次写入。buffer 自定义节位于默认启动 `.bss` 之外；第一次模式完整写入每个 word。

本次实际分区为应用 `[0x00100000,0x01100000)`、buffer `[0x01100000,0x01200000)`；smoke 诊断状态位于 `0x00114140`。这是该 ELF 在独占运行前提下的链接归属证明；实物 DDR 型号、时序、初始化适用性及稳定性仍未验证。

## 固定 OCM 初始化方案

固定 XSA 内没有 `ps7_init.py`。本包采用生成的最小 `s2b_ps_init.c`，只调用同一 XSA 的原字节 `ps7_init.c/h`，成功/失败分别进入无限 WFE 的独有 `s2b_ps_init_ready` / `s2b_ps_init_fail`。不采用旧尝试中的 FSBL ELF；旧 build_06 的 `-U PS7_POST_CONFIG` 未阻止源码重新定义，真实 FAIL 及源码快照保留为诊断。

初始化链接脚本逐字节使用本机官方 `D:\Xilinx\2026.1\data\embeddedsw\lib\sw_apps\zynq_fsbl\src\lscript.ld`，SHA-256 `508b0c05a5dc0258613e3985c179d24f1ed1f3be571d7c6ad564939113766f4a`。实际 XSA/BSP linker regions、ELF 全部 ALLOC/LOAD、6种模式栈、heap、向量、清零区及 MMUTable 均证明只分配低 OCM `[0,0x30000)` 和高 OCM `[0xFFFF0000,0xFFFFFE00)`；顶部512字节保留给 CPU1。官方 linker 的未使用 `.rsa_ac` 保留区仍在 OCM，没有加入 RSA/FSBL 启动库。

进入 main 前的实际 A9 GCC 启动源、编译命令、ELF/map 和反汇编已绑定：`boot.S` 维护 CP15/SCU/L2及SLCR寄存器，使用 OCM 的 MMUTable/模式栈；`__cpu_init` 只有 CP15 操作；`xil-crt0.S` 清零的 BSS/SBSS 均在 OCM。本次 `.init_array` 只有 Thumb `frame_dummy`，地址 `0x485`；其空弱钩子和所有数据引用均在 OCM。实际 `xtimerinit`/`TimerInst` 已被链接 GC 删除，未在初始化前启动计时器构造函数。编译为 SDT，无 `USE_AMP`、`SHAREABLE_DDR` 或 profiling；启动例程不释放 CPU1。

main 先 Flush 全部 DCache、Disable DCache，再检查 CPU0并调用 ps7_init。这个全缓存维护仅适用于下文冷启动 JTAG、无旧应用及 CPU1/DMA/PL writer 静止的前提，不能用于正在运行的 Linux/AMP 环境。原 ps7_init 读取 `0xF8007080` 选择硅版本，然后执行 MIO、PLL、clock、DDR、peripheral 初始化表；官方函数名是 `ps7GetSiliconVersion`。联合检查按完整标识符接受它，拒绝 FSBL 的 `GetSiliconVersion`，并证明最终 ELF 不链接 `ps7_post_config`、`LoadBootImage`、`FabricInit`、`XDcfg_Transfer` 或 handoff 入口。

ready 仅在原返回码为 `PS7_INIT_SUCCESS=0`、结果对象写为 `2` 并执行 DSB 后调用。状态和原返回值在 DCache 已关闭的 OCM，对应调试器读取具有明确归属。ready/fail 机器码只有停驻循环，不能继续到加载旧 boot image、配置 PL 或跳转别的程序。

## 离线重建

入口 `build_s2b_ps_smoke.py` 通过本机 Vitis 2026.1 Python CLI 执行。本候选使用已核验的 schema1 `inputs_manifest_r03.json`，SHA-256 `9b35050163c2cc47306e2b5f5fc4ed0e5d9835afa1fd158ff68a3959ef123778`。`verification/check_stage_delivery.py --mode inputs` 已退出0；它只核对输入绑定。新运行同样必须先核对已审冻结的精确 XSA、SHA、提交和正式批准，不能用“最新 XSA”或单独 `frozen=true` 替代批准依据。

构建配置 JSON 必须包含且仅包含下列字段：`schema_version=1`、`source_commit`、`xsa`、`xsa_sha256`、`xsa_source_commit`、`inputs_manifest`、`inputs_manifest_sha256`、`workspace`、`artifact_dir`、`command`。路径均为逐分量核验的绝对路径。`workspace` 必须位于本仓库 `tmp/2B/S2B-T06/`，`artifact_dir` 必须位于 `report/evidence/S2B-T06/`。两个目标均须全新；已有运行或大小写冲突立即拒绝，失败记录不会删除。

先核对本机存活重型进程、空闲内存和磁盘。命令通过 PowerShell 启动已核验的安装；普通文件准备仍使用 Git Bash。将两个环境变量设为当前精确配置，执行：

```powershell
$env:S2B_PS_SMOKE_MODE = 'build'
# 此变量必须填写本次真实、已绑定的绝对配置路径。
$env:S2B_PS_SMOKE_CONFIG = '<本次构建配置绝对路径>'
& 'D:\Xilinx\2026.1\Vitis\bin\vitis.bat' -s 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\vitis\build_s2b_ps_smoke.py'
```

上面的配置路径是说明占位值，不能直接执行。实际配置 `report/evidence/S2B-T06/ps_smoke_20261008_r01/build_config_08.json` 已完成一次构建，其目标已存在；再次执行必须被拒绝。复建须另建配置，填写全新 workspace/artifact 名称及相应真实 command，保持固定上游 SHA。新 CLI 进程创建独占 Vitis server 和全新工作区，建立内部名 `ps7`、domain `cpu0` 的 standalone `ps7_cortexa9_0` 平台，显式设置 `ps7_uart_1` stdin/stdout，构建 BSP、smoke 空应用和最小 OCM 初始化应用。平台禁用自动 boot BSP，脚本不部署或连接目标。实际 2026.1 API build 返回 protobuf 整数 `SUCCESS=0`；脚本按实际 descriptor 比较，不能当成布尔 True。

本机 `vitis.bat -s` 曾在 Python 脚本失败时仍返回0。因此 CLI0 必须与完整 `build_details.json` 的 `PASS_OFFLINE_BUILD_AND_LAYOUT`、每项真实命令退出码及联合 layout PASS 一起判定。当前 build_08 wrapper退出0、27次API调用/6个子命令、43.564秒；峰值内存未测。smoke 编译开启 `-Wall -Wextra -Werror`；原字节初始化源码的 signedness warning 已保留，初始化编译使用 `-Wall -Wextra`。

预计首次平台及应用构建数分钟；实际耗时写入 `build_details.json`。非零返回、OOM、损坏数据或30分钟无新进度停止并保留工作区及日志，诊断后使用新的工作区/产物名称。不能覆盖旧 RunId。生成头、默认及定制 linker、实际 BSP 头/driver 源、ELF、map、readelf 原文、布局检查和真实命令/退出码进入必要证据；生成工程与编译缓存留在 tmp。构建过程检查源码和上游哈希未改变。

离线布局核验命令为实际 `layout_binding.json` 路径：

```bash
python -B verification/check_s2b_ps_smoke_layout.py --manifest '<实际layout_binding.json绝对路径>' --self-test
```

`--self-test` 在实际 ELF 的内存解析副本上注入地址、属性、stack、LOAD、对象大小和入口错误，并检查 ELF 格式/缓存行及初始化停点拒绝路径；本次14个负例全部拒绝，并通过官方硅版本函数的精确标识符正例。不执行 ARM 程序。schema1 evidence 包装 `CHECKS_OK` 也仅证明文件绑定完整。

## 人工操作包的固定文件

以下仅供独立审查通过并另获实物授权后执行，本轮所有连接、枚举、断点、下载、初始化及UART/DDR实测均为 `NOT_RUN`。唯一固定 XSA 路径为：

```text
C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T04\ps_platform_20261008_r02\candidate_attempt1\s2b_ps_only.xsa
```

成功产物目录精确为：

```text
C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T06\ps_smoke_20261008_r01\build_08
```

| 固定文件 | SHA-256 |
|---|---|
| 上述 XSA | `a57948c60cfc573b710f562ed7177b0422313d6b77f100856410370273f3eb58` |
| build_08/s2b_ps_smoke.elf | `8b9803682c9585a8dad91daf96f3f102de948466025e0cf28ee4b96e6cfde428` |
| build_08/s2b_ps_smoke.map | `7273e22fd811804eafe538b173c42bbf50b3311e6c489c69f23add95cf28b218` |
| build_08/s2b_ps_init.elf | `366ad1f4831eba9db0510c0e5343d34e3b355f72c8f8bcae419903814246024c` |
| build_08/s2b_ps_init.map | `aebac0c4c66014d859f38b34f409afee4039dc6ec516d25f4cf74d509df35efa` |
| build_08/ps7_init.c | `95f228bce034590569f2bec887cf2e7375997c62c935e43fe1e9d4a3a1818393` |
| build_08/ps7_init.h | `d72dc2b72ce57dfafb611386a1363809c809acf393916abb99fa90aed869b7f8` |
| build_08/s2b_ps_init.c | `813c09cda9e5843cb09690b7f166edec0325fcf9dec403a598928c6e3d828796` |
| build_08/layout_binding.json | `e18449c721fcfe4113cf31acaa31c82f7c65d5b274bc8ef6043869199a11d1b1` |
| build_08/layout_check.json | `8157f317a8eba88cfe17528501c1ce0a646b2838213b34349c04a8b656a0bfb0` |
| vitis/s2b_ps_smoke.c | `d2bb6f0941c2e3765c5a71f889d2e7e1e0428429237f5443510e81cedd16786b` |

`ps7_init.tcl` 是保留的同 XSA 来源证据，本人工路线不 source 它。新构建即使机器码停止地址相同，也必须改用新 ELF/map/layout 的真实 SHA和地址重新审批绑定，不能套用本表。

## 实物授权后的操作顺序

### 1. 核实冷启动与独占条件

由 Wong 核实 XC/-2 厂商声明与 XA 照片冲突、实际 PCB 版本、供电、UART 接线/电平、DDR及PS_CLK来源，按该PCB厂商手册核对 JTAG启动跳线及 cascade 连接方式。XSA 的 MIO48 TX/MIO49 RX、BANK501 1.8V 是逻辑候选，不能替代实际连接器/桥接芯片电平核实；DDR board delay 候选也不是实测校准。

本路线要求电源冷启动进入非安全 JTAG slave/cascade，BootROM 已结束，CPU1 保持停止，PS DMA/外设 DMA/其他 DDR writer 均静止，PL没有加载位流或活跃 writer，没有其他编程/调试客户端。不能从 Linux、AMP、旧 FSBL/旧 boot image 或正在运行的应用中跳入。本应用不建立这些物理条件。

UG585 v1.15（2026-02-06）说明非安全模式 BootROM结束后恢复JTAG，JTAG cascade示例以CPU WFE交出控制；这些是本流程的启动依据，实际板卡状态还须人工确认。[JTAG与调试条件](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/JTAG-and-Debug-Considerations)、[JTAG启动示例](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Example-JTAG-Boot-Sequence)。官方 BootROM寄存器示例表中 JTAG 的 DevCfg UNLOCK为 `0x757BDF0D`；据此推断已完成的冷JTAG可供原 ps7GetSiliconVersion读取MCTRL，无需旧 FSBL InitPcap。示例值来自官方开发板，不能宣称本板已测，也不把对写口UNLOCK的读取当成完成证明。[BootROM寄存器示例](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Registers-Modified-by-the-BootROM-Examples)。

人工证据另建全新 `report/evidence/S2B-T06/<本次人工RunId>/`，普通目录准备用 Git Bash；不写回本离线Run。记录授权、板卡身份/PCB、跳线、供电、接线、冷启动时间及上述独占条件。先运行本包 inputs/layout/evidence只读检查，并核对文件表SHA；任何不符停止。

### 2. 先开启串口原始字节记录

操作员只需填写两个真实值：已核实的COM端口和新人工Run目录。下面两个尖括号值是占位值，替换并核验后才执行。串口读取用PowerShell/.NET，因为本机需要Windows串口接口；文件以CreateNew打开，拒绝覆盖。独立终端保持采集运行，另一个终端执行下文调试步骤。

```powershell
$uartPort = '<实际COM端口>'
$uartRaw = 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T06\<本次人工RunId>\uart_raw.bin'
$serial = [System.IO.Ports.SerialPort]::new($uartPort, 115200, [System.IO.Ports.Parity]::None, 8, [System.IO.Ports.StopBits]::One)
$serial.Handshake = [System.IO.Ports.Handshake]::None
$serial.DtrEnable = $false
$serial.RtsEnable = $false
$serial.ReadTimeout = 200
$bytes = [byte[]]::new(4096)
$raw = [System.IO.File]::Open($uartRaw, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
$captureClock = [System.Diagnostics.Stopwatch]::StartNew()
try {
    $serial.Open()
    while ($captureClock.Elapsed.TotalSeconds -lt 600) {
        try { $count = $serial.Read($bytes, 0, $bytes.Length) }
        catch [System.TimeoutException] { continue }
        $raw.Write($bytes, 0, $count)
        $raw.Flush()
        [Console]::Write([System.Text.Encoding]::ASCII.GetString($bytes, 0, $count))
    }
} finally {
    $serial.Close()
    $serial.Dispose()
    $raw.Dispose()
}
```

600秒是人工采集保护上限，未实测为性能指标。出现串口打开失败即停止后续下载。采集必须从初始化前持续至 smoke END/异常停止；完整终止CPU并保存状态后以Ctrl+C结束采集。超时或中断生成的原始文件保留，不能续写/覆盖后当成一次完整成功。

### 3. 启动本次独有hw_server与Python XSDB

只使用本机已核验的2026.1 Python流程。`xsdb_help_probe*.json`、`xsdb_operating_basis_r03.json` 绑定真实帮助/实现；本轮没有创建调试会话。旧XSCT虽然退出0，但安装已禁用且探针脚本未执行，不作为操作依据。

先确认没有既有hw_server且3121端口未被监听，防止接入其他会话。新人工目录下 `hw_server_stdout.log/hw_server_stderr.log` 必须不存在。通过官方batch配置环境，隐藏启动自己的server；`-stcp::3121` 与实际可执行文件内嵌 `-s<url>` 用法一致。若server异常退出或没有监听，保留日志并停止，不让connect另起未知server。

```powershell
$manualRun = (Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T06\<本次人工RunId>').FullName
if (@(Get-CimInstance Win32_Process -Filter "Name='hw_server.exe'").Count -ne 0) { throw '已有hw_server，先核实归属' }
if (@(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue).Count -ne 0) { throw '3121已被占用' }
$serverOut = Join-Path $manualRun 'hw_server_stdout.log'
$serverErr = Join-Path $manualRun 'hw_server_stderr.log'
if ((Test-Path -LiteralPath $serverOut) -or (Test-Path -LiteralPath $serverErr)) { throw '拒绝覆盖server日志' }
$hwLauncher = Start-Process -FilePath $env:ComSpec -ArgumentList '/d', '/c', '"D:\Xilinx\2026.1\Vitis\bin\hw_server.bat" -stcp::3121' -WindowStyle Hidden -PassThru -RedirectStandardOutput $serverOut -RedirectStandardError $serverErr
Get-CimInstance Win32_Process -Filter "Name='hw_server.exe'" | Select-Object ProcessId, ParentProcessId, ExecutablePath, CommandLine
Get-NetTCPConnection -LocalPort 3121 -State Listen
```

将真实hw_server PID、启动时间、完整路径与父进程链保存，必须证明来自本次 `$hwLauncher.Id`，其native路径为 `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe`，SHA-256 `e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3`。监听尚未出现时检查本次日志，不用固定等待时间当成就绪证据。归属确认后开启交互Python；同时另录该控制台的全部输入/输出及时间。

```powershell
& 'D:\Xilinx\2026.1\Vitis\bin\vitis.bat' -i
```

在该Python控制台逐组执行。只连接已经核实为本次启动的本地server，不使用远程/XVC：

```python
import xsdb
session = xsdb.start_debug_session()
channel = session.connect(host='127.0.0.1', port=3121, server='hw_server')
print(channel)
```

连接后在启动server的PowerShell重新核验监听PID/进程身份与刚才的本次server相同；若connect触发了额外自动启动或原server已退出，停止并断开，不开始目标操作。确认后继续Python：

```python
print(session.targets('--target_properties'))
```

按真实目标列表核对授权板卡/JTAG链以及同一APU的Cortex-A9 CPU0/CPU1。目标ID不能固定写2/3；多板、名称不明、链不符或缺少CPU1时停止，不猜目标。JTAG的xc7z020名称不能证明XC系列/-2速度级。人工从当前列表填写两个ID，再核对打印对象：

```python
cpu0_id = int(input('填写当前已核实的CPU0目标ID: '))
cpu1_id = int(input('填写当前已核实的CPU1目标ID: '))
assert cpu0_id != cpu1_id
cpu0 = session.targets(id=cpu0_id)
cpu1 = session.targets(id=cpu1_id)
print(cpu0, cpu1)
cpu0.stop()
cpu1.stop()
print(cpu0.state(), cpu1.state())
print(cpu0.rrd(reg='pc'))
print(cpu0.mrd('--value', address=0xF800025C, size=1, word_size=4))
print(cpu0.mrd('--value', address=0xF8007080, size=1, word_size=4))
```

实际实现使用 `--target_properties` 下划线，并在按ID选择时返回Target对象；不能照搬旧帮助中的hyphen/None描述。两核必须Stopped；保存BootMode原值（低3位应为JTAG的0）及MCTRL硅版本字段，与冷启动/身份记录联合核对。寄存器读取拒绝、BootROM仍执行、前提不符都停止，禁止加force/mwr绕过。此处不调用processor/system reset；任何意外reset都会使DDR/CPU1/PL条件失效，必须停下并重新确认完整冷JTAG流程。

### 4. 只在OCM完成同一XSA的PS初始化

先下载本包OCM初始化ELF，设置硬件断点到**实际ELF**的两个函数入口，核对断点status没有安装错误后再运行：

```python
cpu0.dow(file=r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T06\ps_smoke_20261008_r01\build_08\s2b_ps_init.elf', auto_stop=True, set_entry=True)
print(cpu0.rrd(reg='pc'))
ready_bp = cpu0.bpadd(addr='0x00001D08', type='hw')
fail_bp = cpu0.bpadd(addr='0x00001D18', type='hw')
print(ready_bp.status(), fail_bp.status())
```

人工核对两个断点均已在CPU0安装成功后，再执行：

```python
try:
    cpu0.con('--block', timeout=30)
except Exception:
    cpu0.stop()
    print(cpu0.state(), cpu0.rrd(reg='pc'))
    raise
print(cpu0.state(), cpu0.rrd(reg='pc'), cpu1.state())
print(cpu0.mrd('--value', address=0x00009200, size=1, word_size=4))
print(cpu0.mrd('--value', address=0x000039C0, size=1, word_size=4))
```

下载后PC应为向量入口0。唯一继续条件是CPU0停在ready硬件断点/PC `0x1D08`、CPU1仍Stopped、OCM结果 `0x9200` 为2、原返回值 `0x39C0` 为0，且无异常。30秒只是操作超时保护，未实测。fail地址 `0x1D18`、结果0/1/0x81/0x82、非零返回码、其他断点、异常或超时都停止并保存PC/状态/原值；不能仅凭WFE、等待秒数或Stopped判初始化成功。禁止继续执行此初始化ELF；ready之后保持停止并下载下一份ELF。

### 5. 下载smoke并取得完整结果

确认步骤4全部条件后移除本次两个断点。CPU0仍停止，**不reset**，保持刚初始化的PS/DDR并再次检查CPU1。下载smoke时不使用force、重定位或bypass_cache_synq。ELF入口为 `0x00100000`；`_exit` 实际机器码在 `0x0010AD58` 自循环，作为本次程序返回的硬件停止点。命中它仍须检查程序状态及原始UART，失败返回同样可能到该点。

```python
ready_bp.remove()
fail_bp.remove()
print(cpu1.state())
cpu0.dow(file=r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T06\ps_smoke_20261008_r01\build_08\s2b_ps_smoke.elf', auto_stop=True, set_entry=True)
print(cpu0.rrd(reg='pc'))
end_bp = cpu0.bpadd(addr='0x0010AD58', type='hw')
print(end_bp.status())
```

人工核对本次smoke断点安装成功且PC为上述ELF入口后，再执行：

```python
try:
    cpu0.con('--block', timeout=120)
except Exception:
    cpu0.stop()
    print(cpu0.state(), cpu0.rrd(reg='pc'))
    raise
print(cpu0.state(), cpu0.rrd(reg='pc'), cpu1.state())
print(cpu0.mrd('--value', address=0x00114140, size=1, word_size=4))
```

120秒是人工保护上限，未作为DDR速度指标实测。唯一成功条件是：本次断点/PC为 `0x0010AD58`、CPU1仍Stopped、已写回DDR的smoke结果为2，并且同一原始文件中有完整BEGIN、正确C/XSA两项BUILD SHA、UART115200/8N1配置、buffer `[0x01100000,0x01200000)`、16行PATTERN_PASS、`PASS passes=2 patterns=8 verified_words=4194304 mismatches=0`、`END S2B-T06-1`，无FAIL/乱码/缺行。仅CPU返回、状态2、工具退出0或部分串口都不足以通过。

smoke状态0x81=UART初始化失败，0x82=布局失败，0x83=发送/格式化失败，0x84=CPU非0，0x85=DDR不匹配，1=仍执行。UART初始化/发送故障可能没有FAIL/END，但状态发布具有DSB/FlushRange/DSB的物理可见性。出现任一失败、超时、异常电流、器件/PCB资料冲突或CPU1状态变化，立即停止CPU0，保留所有日志/寄存器及首错位置，不继续其他板上测项。

### 6. 结束、回传与恢复

CPU保持停止，保存最终PC、两个核的state和诊断值，移除本次断点，关闭本次连接；不恢复CPU1或继续其他程序：

```python
end_bp.remove()
session.disconnect(chan=channel)
xsdb.dispose()
```

异常在end_bp创建前发生时，只移除已经创建的本次断点对象。结束串口采集后保存原始字节及SHA。退出本次Python交互终端；xsdb.dispose并不证明hw_server已结束。回到启动server的PowerShell，重新核验已记录的native PID/启动时间/路径及其与 `$hwLauncher.Id` 的父进程归属后，仅终止本次native server（`Stop-Process -Id <已核验的本次hw_server PID>`），再核实本次launcher退出；不按名字批量结束或触碰其他窗口。

回传新人工Run目录中的原始UART、完整调试控制台/server日志、授权/身份/PCB/跳线/供电/接线/COM参数、冷启动和各步时间、实际下载文件SHA、初始化原返回码/ready断点和smoke最终PC/状态、失败首offset expected/actual及总不匹配。本次离线清单保持NOT_RUN，真实板上结果另立清单。恢复首先确认CPU0/CPU1停止、连接/server归属及电源状态；异常后先诊断、核实既有授权范围及冷JTAG前提，再新建Run重复整个初始化流程，不继续旧初始化WFE、不加载板上旧镜像、不复用旧串口文件。既有授权在对应范围持续有效；范围变化或适用规则明确要求二次确认时才另行确认。首次实物操作仍须明确授权。

参考：已安装 `D:\Xilinx\2026.1\Vitis\cli\examples\embedded\bsp_settings.py`、`platform_uc4_zynq.py`、`linker_script.py`、本次只读 API probe，以及 [AMD 官方 2026.1 scripting tutorial](https://github.com/Xilinx/Vitis-Tutorials/blob/2026.1/Embedded_Software/Feature_Tutorials/04-vitis_scripting_flows/README.md)。示例中的清理工作区代码未被复用。
