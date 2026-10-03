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
不能中断不返回的 polled 调用。因此整体接收超时仍是实际 BSP/板上验证前的限制。
传感器适配补丁本身不改底层驱动；需要整体墙钟 deadline 时仍须另行选择并验证底层有限等待或异步方案。

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
