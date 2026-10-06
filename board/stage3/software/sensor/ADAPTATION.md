# S3-SW01 厂商摄像头错误处理适配

参考仓库：AX7020_2023.1，固定提交 fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327。
源目录：course_s2_vitis/22_ov5640_single/Vitis/auto_create_vitis/src/an5642_single。
输入为 i2c/PS_i2c.c、i2c/PS_i2c.h、ov5640.c、ov5640.h。

四个文件未见明确版权/许可声明；仓库内其他软件许可不能推定适用于它们。
这里仅保存差异补丁、准备脚本及测试，不把整份厂商寄存器表入库，不声明厂商源可再分发。
准备脚本验证固定 HEAD 及各源 Git blob，再复制原始字节和应用精确补丁。
原始字节保留于运行目录 vendor_original，现存注释/许可不会从原始副本抹去；
适配副本统一为 UTF-8/LF，原源少量旧编码注释会出现替代字符，寄存器值不变。
新增代码注释为中文。来源及逐文件 SHA-256 见 source_manifest.json。

接口：两个 read 返回 int 状态，通过 u8* 输出；所有失败保留调用者输出。
返回底层原始错误码；本层参数/外层忙/ID/缺终止符分别为 -1001/-1002/-1003/-1004。
send/recv 失败立即返回，不重试或复位；调用者须提供已正确初始化、七位地址模式的 XIicPs。
SDT 下设备查找参数为 UINTPTR，传统为 u16，传感器初始化不再隐式选择控制器。
sensor_init 先读取 0x300A/B 并校验 0x5640，然后沿用厂商表逐项写入。
sensor_write_array 必须传实际对象长度（含终止符）；无终止符写完指定范围后返回表错误；
中途写失败即返回，已有成功写入不回滚。调用者虚报对象长度不在可保护范围内。
厂商模式参数、寄存器顺序和延时逻辑均不改，不代表已冻结视频模式或硬件时序。

## 本机底层超时证据与限制

只读源：D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23\src。
xiicps_master.c SHA-256：6e002edfd94b80b0dfdd54215c0a536e5fbe06380d7a40f0418b6e52066e3b10。
xiicps.h SHA-256：a96553e979223be1828a781f1bdeb818c61db661e154337b8cf3b4bf10b500ca。
xiicps_xfer.c SHA-256：628414e27016be423ca950af493d522556587e4e04f1eef0e1ce7b10ecffbc1f。
发送函数在 master.c:369–389 的完成等待中使用 TX_MAX_LOOPCNT=1000000（第72行）及 usleep(1)；
第344行 FIFO 续发等待没有同样计数。这里短传输为1–3字节，仍不把局部计数当完整墙钟界限。
接收在 master.c:501 调用 XIicPs_MasterPolledRead；xfer.c:171 起等待字节和错误状态，
没有有限计数，且错误掩码未包含 TO；第183行 FIFO 等待亦无软件超时。
hw.h 中存在默认超时常量不证明此接收路径用了它。
本层 busy 仅在底层调用前后最多查询 S3_I2C_BUSY_LIMIT 次（默认10000），不是毫秒时限，
不能中断不返回的 polled 调用。S3-SW03 overlay 为接收轮询增加有限软件计数，但在其集成到实际 BSP
并完成验证前，整体接收超时仍是限制；有限计数也不构成硬实时墙钟保证。S3-SW03 不改发送路径，
也不提供异步事务取消语义。

## IICPS 接收硬件 TO 错误 overlay

`iicps_v3_23_hw_timeout.patch` 是针对本机 Vitis 2026.1 `iicps_v3_23` 的最小差异包，
不修改 `D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23\src` 安装原件，也尚未集成进本项目 BSP。
原件 `xiicps_master.c`、`xiicps_xfer.c`、`xiicps.h`、`xiicps_hw.h` 的 SHA-256 锁定值见
`report/stage3_iicps_hw_timeout_20261003.json`；补丁只改前两个文件中的 polled receive 路径。
使用时须先把官方驱动源复制到独立、可弃置的 BSP/测试副本，再在那里应用该补丁；
不得直接修改 Vitis 安装目录。当前无经验证的 Vitis BSP overlay 集成步骤。

修复范围：`XIicPs_MasterPolledRead` 在每次 FIFO 服务后重新读 ISR，并将 `TO` 纳入错误掩码；
Zynq 大读取 FIFO-full 等待也轮询这些错误，在写入下一段传输长度前再次检查。外层
`XIicPs_MasterRecvPolled` 将 `TO` 纳入最终错误掩码，使它与 NACK 一样返回 `XST_FAILURE`；
仲裁丢失既有返回码不变。该错误位只报告控制器硬件超时，不是对 API 调用设置的软件墙钟期限；
UG585 将其定义为 SCL 被主控或从设备持续拉低超过 Timeout register 周期。即使初始化后
驱动重置该寄存器为 `0xFF`，仍不能据此声称全路径具备固定毫秒上限或所有死锁都能返回。

XA Zynq-7000 EN257 另记录：master read 同时 `HOLD=1` 且 `Transfer Size=0` 时，超时可能导致
额外 16 字节读取和 Transfer Size 损坏；该勘误不因屏蔽 TO 而消失。本项目当前摄像头读调用为
1 字节；之后调用本驱动必须使用正的 `ByteCount`，并避免零长度 HOLD 读取。本轮验证不覆盖
`IsRepeatedStart != 0` 时的 HOLD 错误恢复语义；BSP 集成前须核实实例选项并单独验证该路径。

测试入口：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  scripts\test_s3_iicps_hw_timeout.py --run-name <新的唯一运行名>
```

运行名只接受 ASCII 字母、数字、下划线和连字符；证据写到 `tmp/s3_iicps_timeout/<运行名>`，
已存在目录拒绝覆盖。该检查要求固定基线提交是当前 HEAD 的祖先（所以任务提交后仍可复跑），
再核对 Vitis 原件 SHA-256、重放 unified diff 并执行源码契约检查。
它不是实际 BSP 编译或 MMIO 验证；运行时覆盖见同目录 `summary.json`，测试报告不替代阶段审查或验收。

## 复验

在项目根目录运行：powershell/pwsh -File scripts/s3_test_sensor.ps1 -RunName <新的唯一运行名>。
使用已有 gcc，不安装依赖；输出仅到 tmp/<运行名>，已有目录拒绝覆盖。
四种组合：mock/真实 xiicps.h × SDT/传统；真实头仍以主机 stub 提供平台依赖，
不链接或执行真实 MMIO/底层驱动，不等同实际 BSP 构建。
测试为固定定向故障，无随机数；每种底层调用独立计数，覆盖每次表写失败、ID读取失败、
ID错误、busy各阶段不结束、NULL参数、读值保留、长度边界及正常写表。
独立读写逐字节核对 8/16 位寄存器地址与数据；busy 覆盖最后一次查询恢复空闲，
并遍历 sensor_init 两次 ID 读取及每次表写的所有外层检查点，核对首错后的调用计数。
主机 mock 对异常轮询次数报错，runner 对每个测试进程设 30 秒上限并校验 PASS 终态及计数；
这是测试防挂起措施，不提供实际 I2C 事务的截止时间保证。
从原始副本独立提取黄金寄存器项，逐项静态比较并验证正常初始化的实际发送字节。
生成物及日志不入库。本次交付待独立 Reviewer，不自行声称 G2、板测或阶段验收通过。

## S3-SW04 IICPS local software repository 候选包

准备器 scripts/s3_prepare_iicps_repository.ps1 只读本机 Vitis 2026.1
iicps_v3_23 安装源；先核对任务固定的六个核心源 SHA-256 和两份 overlay SHA-256，
再将 src、data 复制到调用者指定的项目 tmp 新目录下：
XilinxProcessorIPLib/drivers/iicps_v3_24/{src,data}。它只在输出副本中把
data/iicps.mdd 的 driver NAME=iicps 保持不变，并将 VERSION 从 3.23 改为 3.24；
然后依次对硬件 TO overlay、软件轮询期限 overlay 执行 git apply --check 和应用。
任一输入哈希、目录安全条件、补丁目标集合或复制源差异不符合固定约束时均失败关闭。

候选包根生成 source_manifest.json，列明复制源与输出逐文件长度/SHA-256、两补丁哈希及应用顺序、
PowerShell/Git 版本、处理步骤与限制；manifest 不递归记录自身哈希。厂商原件只作为只读输入，
不加入 Git，也不写入 Vitis 安装目录。输出目标必须是项目 tmp 下尚不存在的新目录，且其父目录
预先存在；目标已存在、位于 tmp 外或包含重解析点时拒绝，准备器不做递归清理。

PowerShell 5.1 离线验证命令（每次创建新的唯一 tmp/s3_iicps_repository_*，证据与包均保留）：

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\test_s3_prepare_iicps_repository.ps1

AMD [UG1400 2026.1「Modifying the Domain Sources」](https://docs.amd.com/r/en-US/ug1400-vitis-embedded/Modifying-the-Domain-Sources-Driver-and-Library-Code)
说明驱动组件包含 src 与 data 中的 .mdd/.mld 元数据，并要求提升版本后将自建仓库加入 Vitis；
[「Creating a Software Repository」](https://docs.amd.com/r/en-US/ug1400-vitis-embedded/Creating-a-Software-Repository)
说明软件仓库按驱动/服务/BSP/应用等组件目录组织，[「Adding the Software Repository」](https://docs.amd.com/r/en-US/ug1400-vitis-embedded/Adding-the-Software-Repository)
说明可将仓库添加为当前 workspace 的 local repository。当前文档没有明确说明本候选中任务指定的
XilinxProcessorIPLib/ 额外前缀会被 Vitis 2026.1 扫描器接受；因此该包只是离线候选，不推断 Vitis
如何发现或选择其中的 driver。尚未在 Vitis 2026.1 中添加/扫描/选中此仓库，未生成或编译 XA7Z020/-1
BSP，也未板测。后续需在获准的 Vitis workspace 中实测 repository discovery、所选 driver 版本、
BSP regeneration 和目标编译；本节不构成该验证已通过的证据。

## S3-SW03 IICPS 接收软件轮询上限 overlay

软件补丁 `iicps_v3_23_sw_deadline.patch` 必须在前述硬件 TO overlay 后应用，顺序固定为：

1. 在隔离的 BSP/测试副本应用 `iicps_v3_23_hw_timeout.patch`；
2. 再应用 `iicps_v3_23_sw_deadline.patch`。

仓库交付只保存可重放补丁，不把厂商原件作为项目适配文件或提交项。验证脚本仅在
`tmp/s3_iicps_sw_timeout/<运行名>` 下建立隔离重放副本和测试产物，不触碰 Vitis 安装目录。

软件补丁只修改 `xiicps_xfer.c`、`xiicps_xfer.h`、`xiicps_master.c`：
`XIicPs_MasterPolledRead` 返回 `s32`，普通接收等待与 Zynq RX FIFO-full 内循环共用可覆盖宏
`XIICPS_RX_MAX_LOOPCNT`，生产默认 `1000000U`，每次等待调用 `usleep(1U)` 后计数。该值沿用同版
发送路径约 1 秒的轮询计数模式，**只是有限软件轮询界限，不是硬实时或墙钟期限承诺**；
达到上限返回标准 `XST_TIMEOUT`。

`XIicPs_MasterRecvPolled` 先保留并映射已有硬件 ISR 语义：仲裁丢失返回 `XST_IIC_ARB_LOST`，
NACK/硬件 TO 等普通错误返回 `XST_FAILURE`；只有未发现硬件错误且内部读返回 `XST_TIMEOUT`
时才调用 `XIicPs_Abort`，并把软件超时返回为 `XST_TIMEOUT`。固定版本 Abort 将控制寄存器写为
复位值并清 FIFO，释放 HOLD；调用 Abort 前先采样和映射 ISR，因此不会先清状态而掩盖已存在的
仲裁丢失。超时返回点在下一段 `TRANS_SIZE` 写入之前。

固定原件控制流在长读开始时将实例字段 `UpdateTxSize` 置 1，仅在正常完成最后一段时清 0；
`XIicPs_Abort` 不会清除该软件字段。因此纯软件超时路径在 Abort 后只清
`InstancePtr->UpdateTxSize`，不清 `RecvByteCount`、`RecvBufferPtr` 或持久配置
`IsRepeatedStart`。否则同一实例后续 17 字节 Zynq 接收可能误入分段/FIFO-full 路径。

固定只读原件目录：`D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23\src`。
测试每次固定校验以下六个原件 SHA-256，并拒绝任何变化：

| 文件 | SHA-256 |
|---|---|
| `xiicps_master.c` | `6e002edfd94b80b0dfdd54215c0a536e5fbe06380d7a40f0418b6e52066e3b10` |
| `xiicps_xfer.c` | `628414e27016be423ca950af493d522556587e4e04f1eef0e1ce7b10ecffbc1f` |
| `xiicps_xfer.h` | `94a72a32a8c1e1a18a0506c998de88c69e9e1cb612da483cec91bccc7ef64a0b` |
| `xiicps.c` | `c60c4afda63d4b6dbe09066ac67ad2883aae04f81d637b38ccd7c0b7f70b58b3` |
| `xiicps.h` | `a96553e979223be1828a781f1bdeb818c61db661e154337b8cf3b4bf10b500ca` |
| `xiicps_hw.h` | `0013bcfc147a4c7fc1e60bba7368b5742b638661afb7fdf7efb8dab3223b3d9a` |

测试要求固定提交 `806331d6e6193b539dea76058ad38e5bf71d2d70` 是当前 HEAD 的祖先，而非要求 HEAD 精确相等，
因此补丁提交后仍可复验；无关基线及变化的厂商源码均拒绝。测试还扫描固定源目录，确认该 API 恰有一个声明、一个调用和一个定义；按上述顺序重放两补丁后，
抽取真实 `XIicPs_MasterPolledRead` 与 `XIicPs_MasterRecvPolled` 函数体进行主机 mock 编译/运行。
场景覆盖成功、NACK、硬件 TO、仲裁丢失、普通轮询软件超时及 Zynq FIFO-full 软件超时；测试将
宏缩至 `3U`，还覆盖同一实例长读超时后紧接 17 字节短读成功，断言 Abort 前 `UpdateTxSize=1`、
超时返回后标志仅清为 0、`TRANS_SIZE` 序列为 `[252,17]` 且第二次接收不再触发 FIFO 分支。
MMIO、FIFO、平台查询、
底层 `MasterRead` 和 Abort 均由 mock 提供，不等同 Vitis/BSP 全量构建或实物验证。

复验命令（运行名必须全新；证据目录存在时拒绝覆盖）：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  scripts\test_s3_iicps_sw_timeout.py --run-name iicps_sw_timeout_20261006_review1_02
```

本轮运行状态和退出码见任务报告；证据仅落在 `tmp/s3_iicps_sw_timeout/<运行名>`。
