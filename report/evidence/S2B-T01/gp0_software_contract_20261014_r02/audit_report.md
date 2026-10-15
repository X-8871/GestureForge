# GP0 软件单拍契约静态审计

日期：2026-10-14（UTC+8）

任务：S2B-T01 / RunId `gp0_software_contract_20261014_r02`

## 结论与边界

本Run核对了T15实际构建的 `infer.elf` 原字节、ELF32 ARM节表、保存的readelf/objdump、预处理应用、CPU0 BSP/MMU源码，以及与T15同SHA的T19 visibility=1 XSA/HWH静态审计。结果支持一个受限的软件输入契约：该实际应用由CPU0单核执行、无中断重入/并发提交、CPU1停核且没有其他GP0控制writer时，CSR通过32-bit、4-byte对齐、Device映射的标量load/store访问。证据是静态支持，不是板上AXI观测；选定指令是抽样核对，不构成逐条覆盖整个ELF的形式化证明。

G0可以评审这一软件输入契约、CPU/写入者运行前提、mode0单拍要求及安全受控的G3测试计划。没有必要把G3实物事务波形前置成G0输入。绑定XSA的mode0要求SI所有事务为single-beat，但本审计没有观测 `AWLEN/ARLEN`，也不推断PS互连/转换器动态事务、Lite侧行为、响应/READY背压或reset恢复。mode0下不得故意发送burst。候选整体仍未冻结，其他G0阻断继续有效；本Run不宣布G0通过。

## 基线与哈希绑定

- 本审计HEAD：`0aaea57de30ee83833244bb2eb6e1caf802e39ce`。
- T15应用构建提交：`8bbdcf821020dcb8f0909e8b5e6089ee51d120dc`；应用源码 SHA-256：`9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39`。当前源码与T15保存的 `source_snapshot/s2b_inference_app.c` 字节相同。
- 实际 `infer.elf`：SHA-256 `a7ca427ab06f5f81a650bcb0d2bda3ed0adb716c3c2cb226c34519e695d47869`，390612 bytes；T15 delivery manifest 与 build_details 均绑定此SHA。原ELF未复制到本Run。
- T15 XSA：SHA-256 `90f8d0b9e857f8beb9d99a6264b96441f9ba9b4b0af0568dbbcc064aecba6065`；T19平台源提交 `f92823f0bd577a49db543868f44c4f63b670d8e0`。T15 build_details、T19 XSA及既有HWH审计绑定相同XSA字节。
- T15 delivery manifest SHA-256：`9abedb7b0b54363cfc96d40213b32d5ba7bdcad7c88e7f5f676f81ca7ccb4d65`；T19 delivery manifest SHA-256：`0f32ff262d24dc49ff66e65d38653c27b0aaf53fffb263def51cf927412ca1ad`。旧GP0 HWH审计绑定候选前版SHA `69de8697f2b4d2f49fe5925a8985a71937a28a9b4848c9f793feb91e481816d9`；当前候选文档SHA `c15a04022ba30aed16956e3b02764a07659b92bea046c59243dc68f2c12ebaa2`。候选版本/冻结状态未由本Run变更。
- R01现存最终文件作为历史输入绑定：R01脚本 `dd5aac076d59756ee8d5fa36a7ec7ef66cd27496db1f245ab2764c636f8635d6`、JSON `f15c9ffdf06d43d43c62a1b4dfbf33fb561c5af6ac5d5cf0aff9a0ec7088d1c8`、报告 `d4dbb9c2e15b249db95b839117434faed135d6f7fa1c3715c7a5702105550bbf`、manifest `f9f00f09744b4f55c92e66125bd1192a1581396ffe5e453f55a0355368c98516`。
- 首次拒覆盖命令stdout原始捕获：`report/evidence/S2B-T01/gp0_software_contract_20261014_r02/overwrite_guard_check.json`，SHA-256 `9c67fe77fa5846d39ef515be9cfff3eadd6d798616682631f560fd188728a7a3`；字节编码CP936、行尾CRLF，原字节保留且不作为UTF-8文件解析。最终机器结果另存于 `overwrite_guard_check_utf8.json`（UTF-8/LF），绑定在本Run manifest中。
- 完整输入路径、文件长度和SHA见同目录 `software_contract.json` 的 `input_bindings`。大ELF、反汇编和原构建材料只按路径/SHA绑定，不复制或改写。

## ELF头和节表核对

直接解析ELF头得到：ELF32、little endian、ARM machine=40、ET_EXEC、entry=`0x00100000`；完整文件SHA先核验后解析。用节名表解析节表，不根据固定文件偏移猜测指令位置。

| 节 | ELF type | VMA | 文件偏移 | size | align | 静态含义 |
|---|---:|---:|---:|---:|---:|---|
| `.text` | 1 PROGBITS | `0x00100000` | `0x1000` | `0xd6a4` | 64 | 可执行代码，VA→file offset按节映射计算 |
| `.mmu_tbl` | 1 PROGBITS | `0x00110000` | `0x10000` | `0x4000` | 1 | 启动翻译表 |
| `.s2b_tensor_ddr` | 8 NOBITS | `0x10000000` | `0x15000` | `0x2000000` | 64 | ELF中的32MiB NOLOAD arena声明 |

直接ELF解析结果与既有 `elf_layout.json` 及 `app_readelf.log` 的entry、`.text`、arena字段一致。以下文件偏移都是由 `.text` 的 `sh_offset + (VA - sh_addr)`计算得出。

## R01可恢复性记录

R01的三份初步字节仅保留历史SHA：脚本 `a285412c272387013f3fa932aaaa28a10db5f62b303a5642aba4edb1183e57af`、JSON `69f2eb66540da92a560471f3d66780bd02da734e5c972796e1f27263a22fdf67`、报告 `6d74d5cd95107f11cc4bd70c5b57c7cb8b3e09e7ba2f1d29936822a8cef4b980`；这些初稿原字节无法恢复，本Run不生成仿制副本。R01现存最终四个文件保持原字节，并作为本Run的输入哈希绑定。根据独立审查处置，R01未通过G2，不能作为冻结上游。本R02从实际ELF和外部输入重新采集静态事实，不把R01初稿丢失当作阻断，也不追认R01。

## 启动MMU与CSR Device属性

实际ELF入口 `0x00100000` 的word为 `0xea000031`，objdump解为跳转 `_boot`。启动路径先执行 `bic` 清SCTLR.M，然后加载 `.mmu_tbl` VMA `0x00110000`并写TTBR0，设置DACR，之后从ELF字面量 `0x00001005` 写SCTLR，紧跟 `DSB SY`、`ISB SY`，再分支到 `_start`。`0x1005` 的SCTLR M(bit0)、C(bit2)、I(bit12)均置位。实际应用后续又调用 `Xil_SetTlbAttributes`，传入 `CSR_BASE=0x43c00000` 和 `DEVICE_MEMORY=0xC06`，再调用 `Xil_DCacheEnable`。T15 BSP `xil_mmu.c`以1MiB section表项 `(Addr & 0xFFF00000) | attrib` 更新属性，并刷新D-cache、失效TLB/branch predictor、执行DSB/ISB；其section边界覆盖64KiB CSR窗口。

下面逐项给出这些ELF样例word的VA、经ELF `.text` 节表映射得到的文件偏移、ELF原字节及保存反汇编。样例只核验列出位置，不覆盖所有控制流或证明整个系统不可能存在其他master。

| 用途 | VA | 文件偏移 | ELF原字节（little-endian） | word | 已保存objdump |
|---|---:|---:|---|---:|---|
| 入口向量跳到启动代码 | `0x00100000` | `0x1000` | `31 00 00 ea` | `0xea000031` | `b 1000cc <_boot>` |
| 启动代码先清SCTLR.M | `0x00100154` | `0x1154` | `01 00 c0 e3` | `0xe3c00001` | `bic r0, r0, #1` |
| 读取TTBR0表基址字面量 | `0x00100224` | `0x1224` | `e8 01 9f e5` | `0xe59f01e8` | `ldr r0, [pc, #488] ; 100414 <finished+0x54>` |
| 写TTBR0 | `0x0010022c` | `0x122c` | `10 0f 02 ee` | `0xee020f10` | `mcr 15, 0, r0, cr2, cr0, {0}` |
| 构造全域访问控制值 | `0x00100230` | `0x1230` | `00 00 e0 e3` | `0xe3e00000` | `mvn r0, #0` |
| 写域访问控制寄存器 | `0x00100234` | `0x1234` | `10 0f 03 ee` | `0xee030f10` | `mcr 15, 0, r0, cr3, cr0, {0}` |
| 读取SCTLR配置字面量 | `0x00100238` | `0x1238` | `d8 01 9f e5` | `0xe59f01d8` | `ldr r0, [pc, #472] ; 100418 <finished+0x58>` |
| 启动路径写SCTLR | `0x0010023c` | `0x123c` | `10 0f 01 ee` | `0xee010f10` | `mcr 15, 0, r0, cr1, cr0, {0}` |
| SCTLR写后DSB | `0x00100240` | `0x1240` | `4f f0 7f f5` | `0xf57ff04f` | `dsb sy` |
| SCTLR写后ISB | `0x00100244` | `0x1244` | `6f f0 7f f5` | `0xf57ff06f` | `isb sy` |
| MMU初始化后进入_start | `0x00100338` | `0x1338` | `5f 00 00 ea` | `0xea00005f` | `b 1004bc <_start>` |
| TTBR0表基址字面量 | `0x00100414` | `0x1414` | `00 00 11 00` | `0x00110000` | `.word 0x00110000` |
| SCTLR配置字面量：M/C/I置位 | `0x00100418` | `0x1418` | `05 10 00 00` | `0x00001005` | `.word 0x00001005` |
| MMU属性函数清除地址低20位 | `0x00101220` | `0x2220` | `1f 00 d3 e7` | `0xe7d3001f` | `bfc r0, #0, #20` |
| 合成section描述符属性 | `0x00101228` | `0x2228` | `01 00 80 e1` | `0xe1800001` | `orr r0, r0, r1` |
| 写MMU页表描述符 | `0x00101230` | `0x2230` | `02 01 83 e7` | `0xe7830102` | `str r0, [r3, r2, lsl #2]` |
| MMU属性更新后DSB | `0x00101244` | `0x2244` | `4f f0 7f f5` | `0xf57ff04f` | `dsb sy` |
| MMU属性更新后ISB | `0x00101248` | `0x2248` | `6f f0 7f f5` | `0xf57ff06f` | `isb sy` |
| 实际应用启用DCache | `0x00100fe8` | `0x1fe8` | `10 4f 01 ee` | `0xee014f10` | `mcr 15, 0, r4, cr1, cr0, {0}` |
| CSR读取样例设置基址低位 | `0x0010bc14` | `0xcc14` | `00 30 a0 e3` | `0xe3a03000` | `mov r3, #0` |
| CSR读取样例形成0x43c00000 | `0x0010bc1c` | `0xcc1c` | `c0 33 44 e3` | `0xe34433c0` | `movt r3, #17344 ; 0x43c0` |
| CSR+0x0c的32-bit load样例 | `0x0010bc28` | `0xcc28` | `0c 40 93 e5` | `0xe593400c` | `ldr r4, [r3, #12]` |
| CSR写入样例设置基址低位 | `0x0010bf14` | `0xcf14` | `00 c0 a0 e3` | `0xe3a0c000` | `mov ip, #0` |
| CSR写入样例形成0x43c00000 | `0x0010bf1c` | `0xcf1c` | `c0 c3 44 e3` | `0xe344c3c0` | `movt ip, #17344 ; 0x43c0` |
| CSR+0x14的32-bit store样例 | `0x0010bf70` | `0xcf70` | `14 00 8c e5` | `0xe58c0014` | `str r0, [ip, #20]` |
| CSR写入后的DSB样例 | `0x0010bf74` | `0xcf74` | `4f f0 7f f5` | `0xf57ff04f` | `dsb sy` |
| 实际调用前清零CSR_BASE低位 | `0x0010c560` | `0xd560` | `00 00 a0 e3` | `0xe3a00000` | `mov r0, #0` |
| 实际调用DEVICE_MEMORY参数低半字 | `0x0010c564` | `0xd564` | `06 1c 00 e3` | `0xe3001c06` | `movw r1, #3078 ; 0xc06` |
| 实际调用CSR_BASE高半字 | `0x0010c568` | `0xd568` | `c0 03 44 e3` | `0xe34403c0` | `movt r0, #17344 ; 0x43c0` |
| 实际调用CSR Device属性设置 | `0x0010c56c` | `0xd56c` | `29 d3 ff eb` | `0xebffd329` | `bl 101218 <xil_settlbattributes>` |
| 实际调用DCache启用函数 | `0x0010c570` | `0xd570` | `96 d2 ff eb` | `0xebffd296` | `bl 100fd0 <xil_dcacheenable>` |

这是链接ELF和绑定BSP源码中的静态路径。它支持‘若此ELF确由目标CPU执行，则该CPU虚拟地址映射被设置成Device’的推理；不证明实板已加载该ELF、MMU寄存器当前值、PS互连属性或真实事务。

## 标量访问与对齐

源级 `csr_read` 只调用 `Xil_In32(CSR_BASE + offset)`；预处理后的BSP实现为 `*(volatile u32 *)Addr`。`csr_write` 只调用 `Xil_Out32`（volatile `u32 *`写入）并执行 `DSB SY`。脚本检查了应用全部CSR调用点，偏移均为4的倍数，CSR_BASE本身也按4字节对齐；实际编译配置为Cortex-A9/SDT CPU0 BSP，源码禁止 `USE_AMP`，编译命令不定义 `USE_AMP` 或 `S2B_HOST_MOCK`。BSP `bspconfig.h` 的 `XPAR_CPU_ID=0`。

| 用途 | VA | 由ELF节表推导的file offset | ELF原字节（little-endian） | 解码/有效地址 |
|---|---:|---:|---|---|
| LDR word | `0x0010bc28` | `0xcc28` | `0c 40 93 e5` | `0xe593400c`，r3=0x43c00000，由同一函数内MOV/MOVT指令建立，offset `0xc`，EA `0x43c0000c`，32-bit对齐 |
| STR word | `0x0010bf70` | `0xcf70` | `14 00 8c e5` | `0xe58c0014`，r12=0x43c00000，由同一函数内MOV/MOVT指令建立，offset `0x14`，EA `0x43c00014`，32-bit对齐 |

ELF的word指令字节与保存的objdump在相同VA逐项相符。Xil_In32的选定样例是 `LDR r4,[r3,#12]`，有效地址 `0x43c0000c`；写入样例是 `STR r0,[ip,#20]`，有效地址 `0x43c00014`，之后紧接实际 `DSB SY`。它们只示例性核对load/store宽度和屏障；源级对调用点的核对覆盖已列应用CSR调用表达式，但没有建立全ELF控制流、异常处理路径或第三方库无其他CSR writer的证明。

AMD [UG585 v1.15 Device and Strongly Ordered](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Device-and-Strongly-Ordered)说明Device/Strongly Ordered访问保持ARM访问的数量与大小、禁止未对齐及推测访问。结合该ELF的32-bit标量load/store和对齐调用点，这足以支撑受限软件输入契约的静态评审。`DSB SY`不等于GP0事务捕获，也不证明 `AWLEN/ARLEN`。

## CPU0、AMP与arena约束

T15编译使用来自 `ps7_cortexa9_0/cpu0` 的实际BSP，`XPAR_CPU_ID=0`；应用源包含 `USE_AMP` 拒绝编译保护，保存的编译命令没有 `USE_AMP`。ELF中 `.s2b_tensor_ddr` 是地址 `0x10000000`、大小 `0x02000000`、64-byte对齐的NOBITS节。这些是构建和链接事实，不是运行绑定：未证明此ELF当前在CPU0执行、CPU1停核、无中断/重入、无DAP/PS DMA/其他PL writer，也未证明arena在板上DDR中运行时独占。

## G0/G3界线及尚缺静态事实

G0可核对软件输入契约：CPU0实际应用、非AMP、标量对齐32-bit Device CSR访问，以及无中断重入/其他控制writer、CPU1停核等运行前提；可审查在converter mode0下满足single-beat前提的安全G3测试计划。G0可以确认测试对象、边界和停止条件，不要求预先取得G3波形。候选其他HP/cache/恢复/timeout/数据绑定等G0阻断仍在；本Run不宣布整体G0通过。

实际 `AWLEN/ARLEN`、AXI3 `VALID/READY`握手、converter输出Lite事务、读写响应和异常边界、READY背压、PS互连行为、reset断言/释放/重叠与恢复必须由G3实物/集成事务证据确认。静态HWH只能说明XSA中的AXI3→AXI4-Lite连接、32-bit宽度和 `TRANSLATION_MODE=0`；其 `AWLEN/ARLEN`连线没有运行值。AMD [PG059 Protocol CONVERSION Options](https://docs.amd.com/r/en-US/pg059-axi-interconnect/Protocol-CONVERSION-Options)对mode0要求SI所有事务为single-beat。本审计不故意对mode0送burst，不推测违规输入的转换器响应，也不把DSB当作总线观察。

静态材料也不推出CPU实际执行位置、CPU1状态、IRQ/FIQ访问、独立writer/调试访问、实板MMU当前配置、HP0/DDR/cache可见性、whole-model correctness、实物速度和1000连续任务期限。这些依赖运行状态或硬件测量。Wong于2026-10-14确认AX7020目标器件为XC7Z020-2CLG400I、照片所示板卡亦为该型号，Vivado part应核实 `xc7z020clg400-2`；本Run仅记录该用户确认，不把它表述为物理测量鉴定。

## 限制和执行记录

- 只读复用已存在的T15/T19证据；新Run不复制390,612-byte ELF、718,896-byte objdump或其他大型输入，只绑定原路径/哈希。
- 没有调用Vitis/GNU重新编译或执行ELF；没有运行仿真、综合、Vivado、JTAG、UART或板卡操作。
- T15 build_details记载 `hardware_execution=NOT_RUN`；T15 BSP CPU0构建配置不证明上板CPU运行绑定。
- 不改converter配置、RTL、驱动源码、候选版本或正式100样本/1000任务验收指标。
- 全部直接输入/结果字节哈希、选定指令字/文件映射、运行工具和机读限制在 `software_contract.json`。证据包装检查只核对清单及文件绑定，不代表G0/G3/G4/G5通过。
