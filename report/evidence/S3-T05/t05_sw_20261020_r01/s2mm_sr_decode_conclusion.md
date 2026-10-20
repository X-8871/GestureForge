# S3-T05-SW：S2MM SR（0x43010034）位定义解码结论（软件侧，未上板）

任务：`task-1`（S3-T05-SW）｜日期：2026-10-20｜时区：Asia/Shanghai｜基线 commit：`41ee5ba003147d77349e8908c38b2efc97752ca8`

本文件回答任务卡的第二个问题——**S2MM SR 错误位的真实含义与"帧计数"**——依据是**三份互相独立的本地原件**
（不是推测、不是网上资料），原文摘录与文件哈希见同目录 `sr_bit_sources/`。

## 一、三份依据与一致性

| 依据 | 文件 | 关键内容 |
|---|---|---|
| ① 驱动头文件（任务卡指定） | `D:\Xilinx\2026.1\data\embeddedsw\XilinxProcessorIPLib\drivers\axivdma_v6_15\src\xaxivdma_hw.h`（SHA-256 `545b5948…a558`） | `HALTED=0x1 IDLE=0x2 ERR_INTERNAL=0x10 ERR_SLAVE=0x20 ERR_DECODE=0x40 ERR_FSZ_LESS=0x80 ERR_LSZ_LESS=0x100 ERR_SG_SLV=0x200 ERR_SG_DEC=0x400 ERR_FSZ_MORE=0x800`；`FRMCNT_MASK=0x00FF0000`、`FRMCNT_SHIFT=16`（CR/SR 共享） |
| ② IP 自带元数据 | `…\axi_vdma_v6_3\component.xml`（`548d9809…30f5`） | `S2MM_VDMASR`（addressOffset **0x34**）逐字段 bitOffset 与语义文本 |
| ③ IP HDL（真值） | `…\axi_vdma_v6_3\hdl\axi_vdma_v6_3_vh_rfs.vhd`（`410cebf4…0590`） | `DMASR_*_BIT` 常量（10731–10751 行）与状态寄存器拼装（19596 行起） |

三者对本设计所用 IP 版本（`axi_vdma_v6_3`；应用实际编译用的是 BSP 里的 `axivdma_v6_17` 驱动，**位掩码同值**）给出的位表**一致**：

| bit | 掩码 | HDL 常量 | 驱动头文件名字 | IP 元数据名字 | 真实语义 |
|---|---|---|---|---|---|
| 0 | 0x1 | `DMASR_HALTED_BIT` | Halted | Halted | 通道已停（RS=0 后置起） |
| 1 | 0x2 | `DMASR_IDLE_BIT` | Idle | Idle | 通道空闲 |
| 4 | 0x10 | `DMASR_DMAINTERR_BIT` | ERR_INTERNAL | **VDMAIntErr** | 见第二节（不是"硬件坏了"的同义词） |
| 5 | 0x20 | `DMASR_DMASLVERR_BIT` | ERR_SLAVE | VDMASlvErr | MM 接口 Slave 错误（会停通道） |
| 6 | 0x40 | `DMASR_DMADECERR_BIT` | ERR_DECODE | VDMADecErr | 地址非法（会停通道） |
| 7 | 0x80 | `DMASR_FSIZEERR_BIT` | ERR_FSZ_LESS | **SOFEarlyErr** | 流入帧尺寸 **小于** 编程 vsize |
| 8 | 0x100 | `DMASR_LSIZEERR_BIT` | ERR_LSZ_LESS | **EOLEarlyErr** | 流入行尺寸 **小于** 编程 hsize |
| 9 | 0x200 | `DMASR_SGSLVERR_BIT` | ERR_SG_SLV | — | SG 取指 Slave 错误 |
| 10 | 0x400 | `DMASR_SGDECERR_BIT` | ERR_SG_DEC | — | SG 取指 Decode 错误 |
| 11 | 0x800 | `DMASR_FSIZE_MORE_OR_SOF_LATE_ERR_BIT` | ERR_FSZ_MORE | **SOFLateErr** | 流入帧尺寸 **大于** 编程 vsize / SOF 迟到 |
| 12 | 0x1000 | `DMASR_IOCIRQ_BIT` | （IXR_FRMCNT） | FrmCnt_Irq | 帧计数中断标志 |
| 13 | 0x2000 | `DMASR_DLYIRQ_BIT` | （IXR_DELAYCNT） | DlyCnt_Irq | 延迟中断标志 |
| 14 | 0x4000 | `DMASR_ERRIRQ_BIT` | （IXR_ERROR） | Err_Irq | 错误中断标志 |
| 15 | 0x8000 | `DMASR_LSIZE_MORE_ERR_BIT` | **驱动头文件漏列** | **EOLLateErr** | 流入行尺寸 **大于** 编程 hsize |
| 16–23 | 0x00FF0000 | `DMASR_IRQTHRESH_LSB/MSB` | FRMCNT_MASK | **IRQFrameCntSts** | 中断帧计数阈值的当前值（≠"已收帧数"，见第三节） |
| 24–31 | 0xFF000000 | `DMASR_IRQDELAY_LSB/MSB` | DELAY_MASK | IRQDelayCntSts | 中断延迟计数当前值 |

> 结论 1：**bit11（0x800）在驱动头文件里叫 `ERR_FSZ_MORE`、在 IP 元数据里叫 `SOFLateErr`，是同一个物理位**，
> HDL 常量名字直接写成 `FSIZE_MORE_OR_SOF_LATE`。所以"FSZ_MORE"与"SOF 迟到"不是两种解释，而是同一现象的两种命名。
> 结论 2：驱动头文件**没有** bit15（0x8000，`EOLLateErr`）的掩码，且把 bit9/bit10 标为 SG 取指错误；判读时应以 IP 元数据/HDL 为准。

## 二、bit4（0x10）在本 IP 里的真实置位条件

IP 元数据 `component.xml` 对 `VDMAIntErr` 的原文：

```
This error occurs during one of the following conditions.
  (a) HSIZE or VSIZE register were written zeros or
  (b) Internal error received from helper core axi_datamover or
  (c) Transferred frame size is lesser than programmed vsize (SOFEarlyErr).
In case (a) and/or (b) channel stops (that is, the VDMACR.RS bit is set to 0 and remains cleared).
In case (c), channel does not stop or halt.
```

HDL 进一步给出该位在本设计里的**实际 OR 项**（`hdl_s2mm_instance_portmap_and_dmainterr.txt`）：

* S2MM 状态寄存器实例的端口映射：`dma_interr_set => s2mm_dma_interr_set`（72572 行）——用的是**含帧尺寸错误的"全量"版本**；
  `dma_interr_set_minus_frame_errors` 只用于错误中断 `err` 的组合，**不是** SR bit4 的来源。
* 数据搬运包装里（62298–62308 行）：

```
interr_minus_frame_errors <= interr_i or zero_size_err;
interr <= interr_i or zero_size_err
                   or fsize_mismatch_err
                   or s2mm_fsize_more_or_sof_late;
```

* SR 的 bit4 由 sticky 进程 `DMASR_DMAINTERR`（19428 行）置起，输入即 `dma_interr_set`。

> 结论 3：**本设计（`axi_vdma_v6_3`，S2MM）的 SR bit4 = sticky( datamover 内部错误 | HSIZE/VSIZE 写 0 | 帧尺寸偏小 | 帧尺寸偏大/SOF 迟到 )**。
> 因此 **bit4 与 bit11 同时为 1，正是"帧尺寸偏大/SOF 迟到"这一条件的直接后果**，"ERR_INTERNAL"这个名字在此**不等于**"芯片/数据搬运硬件故障"。
> 通道是否真的停，要看 bit0（Halted）与 CR bit0（RS）。

## 三、对已有实测 SR 读数的判读（数据来自 S3-T04 记录，非本任务新测）

来源：`report/evidence/S3-T04/t04_camera_j11cmos2_20261020_r01/cmos2_bringup_diag_20261020.md`（VSIZE 试验）：

| SR 读数 | bit4 INT | bit11 FSZ_MORE | bit12 FRMCNT_IRQ | bit14 ERR_IRQ | Halted | SR[23:16] | CR[23:16] |
|---|---|---|---|---|---|---|---|
| `0x00015810` | 1 | 1 | 1 | 1 | 0 | 1 | 1 |
| `0x00014810` | 1 | 1 | 0 | 1 | 0 | 1 | 1 |
| `0x00010810` | 1 | 1 | 0 | 0 | 0 | 1 | 1 |

> 结论 4：这四条读数（含 720/721/740/2000 四种 VSIZE）都是 **bit4+bit11，Halted=0**。
> 按结论 3，这与"流入流的帧边界/SOF 不匹配（帧尺寸偏大、SOF 迟到）"**完全一致**，而与元数据里会停通道的 (a)/(b) 两种情形不符。
> 这支持 T04 记录中"任何 VSIZE 都报 FSZ_MORE ⇒ 流入的流里没有可识别的帧起始（SOF）"的方向；
> **但注意**：SR 位是 **sticky（写 1 清除）**，四条读数里 bit11 一直为 1 也可能包含首次错误后的粘滞，不能单凭 SR 判断"每一帧都错"。
> 该问题正是 S3-T05-ILA（5 探针：pclk/vsync/href/tuser/tlast）要独立回答的。

> 结论 5（纠正一处易误读）：**SR[23:16] 读到的 `1` 不是"已收到 1 帧"**。
> 依据：驱动头文件把 `0x00FF0000` 明确定义为 CR/SR 共享的 "Frame counter"；IP 元数据说 `IRQFrameCount` 是"内部计数器从该值**递减**，到 0 产生中断"，
> 而 `IRQFrameCntSts` 是"当前中断帧计数值"。实测 S2MM CR=`0x00018003` ⇒ CR[23:16]=IRQFrameCount=**1**，SR[23:16] 也=**1**（计数**没有**递减），
> 且 CR bit4（FrameCntEn=0x10）**=0**（帧计数中断未使能）。因此该字段在本设计里**不能**当作帧计数使用。
> v5 每次采样都会同时打印 CR 与 SR，可直接观察该字段是否变化（唯一可靠的"帧是否真的进来"证据仍是帧缓冲内容与 NZ 变化）。

## 四、v5 打印出来的东西怎么读（上板判读规则）

每次采样打印三行（v5 应用 = `tmp/s3r06/t04_j11cmos2_elf_v5/elf_build/app/an5642_j11cmos2_v5.elf`）：

* `S3_DIAG5_REG phase=… S2MM_CR=… S2MM_SR=… FRMCNT=… HALTED=… IDLE=…`
* `S3_DIAG5_SR_DECODE phase=… INT=… SLV=… DEC=… FSZ_LESS=… LSZ_LESS=… SG_SLV=… SG_DEC=… FSZ_MORE=… FRMCNT_IRQ=… DLY_IRQ=… ERR_IRQ=… LSZ_MORE=…`
* `S3_DIAG5_CFG VSIZE=… HSIZE=… STRIDE=… ADDR=… MM2S_SR=…`
* `S3_DIAG5_NZ site=0/1/2 off=… nz=…/4096 fb0=… +1000=…`（每次采样 3 行）

判读规则：

1. **S2MM 有没有在写 DDR**：`site=0 nz` 是否明显 > 0（4096 个字里非零字个数）；`fb0`/`+1000` 是否为图像样式的数据（不是全 0、也不是全相同）。
2. **是否活视频**：同一次运行三次采样（`S3_DIAG5_SAMPLE=1/2/3`）的 `nz` 与样本字是否**变化**；三次完全相同 ⇒ 静止/停流。
3. **SR 是不是持续报错**：三处 `FSZ_MORE`/`FSZ_LESS`/`INT` 是否恒为 1；`HALTED` 若变 1 ⇒ 通道真的停了（对应元数据的 (a)/(b) 情形），
   否则 bit4/bit11 属于帧边界类错误（结论 3）。
4. **显示侧**：`MM2S_SR` 是否 Halted=0；与 T03 的显示通路结论对照。
5. **传感器是否在流**：`S3_DIAG5_SENS=4202=… 3008=… 4740=… 3035=… 3034=… 4300=… 501F=… 3824=… 503D=…`
   * `4202 == 0x00` ⇒ stream on；`0x01` ⇒ 停流；
   * `3008` bit6=软复位、bit1=standby（0 越好）；
   * `4740` bit5=VSYNC/bit4=HREF/bit3=PCLK 极性（极性错会让 PL 采到错的行/帧边界，与 SR bit11/bit7 现象吻合）；
   * `503D` 是否被意外打开成 test pattern；`3824` 手动 PCLK 分频。
   * **读不到时打印 0xFF**（v5 用带状态检查的读，厂商 `i2c_reg16_read` 不看传输状态、失败会返回未初始化栈值）；
     但 0xFF 也可能是合法值，判读需结合位定义，不能一律当失败。

## 五、局限

* 本文件是**软件侧依据分析**，所有 SR 数值均引用既有 T04 记录；v5 自己的三次采样数值在未上板前不存在（本任务未下载、未运行 ELF）。
* sticky 语义、帧计数字段（结论 5）都要靠 v5 的多次采样与 ILA 才能进一步闭合。
* `S3_DIAG5_NZ` 覆盖 4096 个字（16 KB）：按卡文先做 `Xil_DCacheInvalidateRange(fb, 4096)`，为让整段统计都绕过 cache 又失效了后 12 KB。
* 三处采样偏移中的 `0x400000` 仍在 `DEMO_MAX_FRAME=1920*1080*3` 之内，但**超出** S2MM 实际写入的 720 行（2,764,800 B），
  该处"非零"只能证明"这段地址被写过"，判读以 `site=0` 与三处 `nz` 的时间变化为准。