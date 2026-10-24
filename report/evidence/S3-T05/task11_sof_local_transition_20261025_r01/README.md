# 两态 PCLK 局部 SOF 转移补充证明

结论：`PASS_SOF_LOCAL_TRANSITION`。这是 task-11 的限定补充，完整 RTL↔网表顺序等价仍为 `NOT_RUN`，阶段3 G5 未通过。没有运行 Vivado、xsim、硬件或摄像头，没有修改 RTL/IP。

固定开发基线 `708aafe9a1c6fbd8fbf6606678e81e05fb4284cf`。输入 RTL、期望补丁 RTL、现存 OOC 功能网表的精确路径、原始字节 SHA-256、大小记录于 `result.json.inputs`。脚本每次先验证这些固定哈希；源码哈希绑定在清单。网表和实际 RTL 仍在现有 tmp 缓存中，本包不复制、不修改缓存；重放前须保留这些输入。网表头说明 Vivado 2026.1、器件 `xc7z020clg400-2`、功能仿真模式，不是部署位流的等价证明。

## 模型、独立依据与归纳边界

状态映射为 RTL 的 16 位 `cmos_hblank_low_cnt` 对应网表 `cmos_hblank_low_cnt_reg[15:0]`，以及同名 `cmos_hblank_d0`、`cmos_hblank_d1`、`s_axis_tuser`，共 19 位。**初态仅假设这 19 位逐位相等，不假设均为 0，也不假设物理上电/INIT/GSR 具有此映射。** 每个 PCLK 上升沿假设边界输入 `cmos_aresetn`、`cmos_hblank`、`cmos_href_16bit_d1`、`full`、`fifo_ready` 在两侧相等且均为 0/1。未证明这些边界输入的生成过程。

由哈希固定的 RTL 中三个 always 块和 valid/FIFO 连接独立推导参考：复位低时所有 19 位清零；否则当前 hblank=1 清计数，hblank=0 递增至 65535 后保持；d0 取当前 hblank，d1 取旧 d0；SOF 触发为旧 d0=0、当前 hblank=1、旧计数≥16384；触发置位优先于 valid 清位，否则 `tuser && valid` 清零，其余保持。`valid = href_d1 && hblank_d1 && !full`，FIFO 写使能为 `valid && fifo_ready`。因此 `fifo_ready=0` 仍可使 valid 清 tuser，不能据本结果宣称 FIFO 已接收 SOF。

解析器从实际网表提取 LUT INIT/端口、CARRY4 的四位 S/DI/CI/CYINIT/O/CO、19 个 FDRE 的 C/CE/D/Q/R，按真实 `cmos_8_16bit_m0` 层级端口映射展平局部锥。对未知驱动、额外状态边界、缺失/重复引脚、宽度错误、组合环及非 PCLK 寄存器拒绝。按 LUT 的 I0 最低地址位、CARRY4 逐位选择进位、FDRE 同步 R 优先于 CE 的两态方程求值。参考递增表由 Python 整数 `min(counter+1,65535)` 枚举产生，不复用被测进位网络或 LUT 表。

穷举所有 `2^(19+5)=16,777,216` 组状态/输入，对计数器 16 位、d0、d1、tuser 和写使能共 20 位比较，合计 `335,544,320` 位比较，差异 0。使用整数位平面同时计算各组，变量的最低有效位顺序记录于结果；每个整数位是一组独立输入，不存在组间进位。计数器所有值均覆盖，包含不一定可达的状态。由任意匹配初态及每步边界相等，转移等价推出任意有限拍数的这 19 位局部状态相等；它不推出完整 IP 的边界输入相等。

附 5 组各 6 拍边界轨迹，起始计数 0、16383、16384、65534、65535，含低电平增计数、上升沿、full 阻塞、fifo_ready=0、valid 清位及同步复位。计数 16383 经低电平一拍达到 16384，再上升触发；65534→65535 后饱和。轨迹均逐拍同时核验参考与网表。另有 5 个负例证明解析器拒绝缺失/重复引脚、未知驱动、错误 FDRE 时钟及错误 CARRY4 宽度。

## 执行和限制

命令（工作目录 `D:\codex-worktrees\dbdf`）：

```powershell
$env:PYTHONIOENCODING='utf-8'
& 'C:/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B scripts/stage3_t05/verify_sof_local_transition.py
```

退出码 0，Python 3.12.14；计算耗时见结果。执行过程中输入解析格式修正后完成计算；首次默认沙箱写新目录被拒（WinError 5，结果未写），经对该精确目录提权后同命令成功。未覆盖旧 RunId。脚本拒绝已存在输出，复核时使用 `--output-dir <已验证不存在且父目录存在的新隔离目录>`，不得覆盖本包。峰值内存未测；计算为轻量 Python 位平面，不占用 Vivado/硬件会话。

完整 task-11 顺序等价、FIFO/CDC、异步复位、四态 X/Z、GSR/INIT/上电、计时/门延迟、边界输入生成、完整 IP 和部署位流等价均 `NOT_RUN`。这里只检查 PCLK 边沿同步复位语义；子模块中的 FDCE 异步行为不在局部边界内。证据包装检查的 `CHECKS_OK` 仅确认文件绑定，不代表 G0/G2/G3/G4/G5 或 task-11 完成。
