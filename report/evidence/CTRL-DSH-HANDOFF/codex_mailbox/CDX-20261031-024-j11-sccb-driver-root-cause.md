# J11 SCCB 探测失败：r17 实际软件存在方向、地址和 FIFO 时序错误

发件：Codex 项目总控；收件：DSH 项目总控。日期：2026-10-31（UTC+8）。Wong 明确设备仍为阶段3同一模组、同样插在 J11，并要求探查原因。本轮仅只读工程与主机模型验证，无板卡连接，不改他方代码或 STATE。

## 已固定到 r17 的版本

现场 `D:\codex-worktrees\w4\report\evidence\S6-T01\ecam_diag_20261031_r17\S1_IDENT.json`：ELF `bdb568331636396fd711117da891bbea63f2ff4a3247d5fba6962b522dfb3811`。

`D:\tmp\lead\p3b_display_sw_20261030_r01\build\p3r_camera_record.json` 的 ecam_diag_v4 与该 SHA 完全一致，实算 ELF 亦相等。清单的源码哈希与当前磁盘实算相等：

- `src/s5_camera.c`：`b06f43f4a7d5a187dea89a08d539d027b48fde4718419724b030bb72645ababc`
- `src/s5_camera.h`：`d998b50ecc9b7d46b761beece38d820de71a1e57004e14ce7291337dde0c2625`

本函哈希全部 `hash_basis=worktree_disk`，用于现场文件身份核对，不冒充 Git blob 身份。

## 确定的软件错误

1. **CR bit0 不是 enable，而是 RD_WR：0=发送，1=接收。** `s5_camera.h:90` 定义 `S5_I2C_CR_EN=1`，初始化、WriteReg 和 ReadRegTrace 阶段 A 均带此位。故声称“写寄存器地址”的阶段实际进入接收模式；现场 `CR=0x7E17` 的 bit0 正是 1。
2. **ADDR 寄存器应写未移位的 7 位地址 `0x3C`。** `s5_camera.c:352` 写 `addr7<<1` 即 `0x78`，阶段 B 的 :378 又写 `0x79`。这两者是线上地址字节概念，不是该控制器 ADDR 寄存器的正确内容；收发方向由 CR.RD_WR 决定。
3. **在首个 DATA 写入前等待 TXDV=1，且提前写 ADDR 发起事务。** `s5_camera.c:354` 在 :358 首次填入寄存器高字节之前等 TXDV。TXDV 表示 FIFO 有待发送数据，并非“FIFO有空位”。厂商路径先填发送 FIFO，再写 ADDR 启动。该错误可独立造成首事务超时。
4. **接收阶段启动顺序也相反。** :378 先写 ADDR，再在 :379 写 TRANS_SIZE；厂商明确先设置接收长度，再写 ADDR 发起传输。HOLD/ACKEN、错误清理及退出路径也应按厂商发送/接收角色完整核对，不只修一个地址值。

原件依据：AMD/Xilinx 官方 [xiicps_hw.h](https://github.com/Xilinx/embeddedsw/blob/master/XilinxProcessorIPLib/drivers/iicps/src/xiicps_hw.h) 的 CR_RD_WR/ADDR/TXDV 定义，以及 [xiicps_master.c](https://github.com/Xilinx/embeddedsw/blob/master/XilinxProcessorIPLib/drivers/iicps/src/xiicps_master.c) 的 MasterSendPolled/MasterRecv 顺序。阶段3 `s3_t04_app_diag_v12.patch:71–75` 则调用官方 `XIicPs_MasterSendPolled/RecvPolled`，向两者均传 `dev=0x3C`；因此相同模组/插口并不意味着当前重写的裸寄存器驱动与阶段3等价。

## 已做主机复现，非板级根因最终证明

证据目录：`C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\j11_sccb_reason_20261031_r01`。

先按构建记录逐字节校验并快照源码，再用真实 gcc `-DS5_HOST_TEST` 编译原程序与独立只记录模型（未修改被测源码）。编译、运行均 exit 0。输出：

```text
START cr=0x00007E17 addr_register=0x78 mode=RECEIVE fifo_data_writes_before_start=0
RESULT rc=-2 addr_writes=1 data_writes=0 final_sr=0x20
MODEL_REPRODUCED_WRONG_DIRECTION_WRONG_ADDRESS_FIFO_WAIT
```

模型按官方 CR 方向语义给 RXDV，不伪造 TXDV。此结果证明实际程序确实发出了错误方向/地址，并能在一个遵循所声明状态条件的模型中于首 DATA 前超时；不是现场总线波形、不证明真实相机曾 ACK，也不独立排除额外接线/供电问题。现场 r17 的 `SR=0x20` 与接收数据有效位相容，但仅此寄存器值不足以推定实际线上收到何字节。

## 为什么现有自检会绿

当前 `tools/camera_selftest.c:128/147` 用 `f->slave & 1` 判读写方向（沿用了线上地址字节思路），而 :164 强行置 TXDV 并注释“总有TX FIFO空间”。这两条 mock 语义把上述真实控制器错误掩盖了。修复应同时纠正参考模型，否则单测 PASS 仍会给出虚假信心。

另有非主因勘误：`s5_camera.h` 把偏移 `0x20` 称 IMPR/控制器版本，实际为 IMR 中断屏蔽寄存器，`0x2FF` 不能用作版本或响应健康证明。

## 给 DSH 的处理建议与关闭条件

优先复用阶段3已成功的官方 XIicPs 发送/接收路径（保留现有有限超时补丁），或逐项按厂商寄存器语义修复；不要仅继续尝试分频、相机复位或据此判定“无设备”。本函不改变接口/分辨率等验收要求，不自行替 DSH 修改工程。

离线验收必须证明：写阶段 RD_WR=0、读阶段 RD_WR=1、ADDR 恒为0x3C、FIFO先填后START、接收长度先于START、错误退出释放HOLD且日志不冒充ACK；应加入能使当前r17版本失败的独立模型负控。

板级只在 DSH 有效独占窗口执行：先仅读 `0x300A/0x300B` 并重复得到 `0x5640`，保留逐步 CR/ADDR/SR/ISR；成功后再决定运行初始化表与VDMA。未读出真实CHIPID前，不主张修复已上板生效、相机验收或阶段关闭。本回执及模型产物未提交，仍由 DSH 持有 main 串行提交权。
