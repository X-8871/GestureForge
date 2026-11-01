# window_close 补全 — `ecam_diag_20261031_r49a`

补记时间：2026-10-31T22:44（UTC+8），补记人：board-runner（Team Lead 指示）

## 1. 本轮目的与结论

- 目的：验证 build11e（`axi_vdma_1/axi_resetn ← rst_100/peripheral_aresetn`，FSYNC=0）是否解除 VDMA S2MM 通道的强制复位
- **结论：未解除，`RESET_STUCK` 仍复现**（`clear_reset` 后 CR 仍 `0x10004`，`start` 后仍 `0x10004`，`after1s` `frmcnt=1`，DDR `0x12000000` 全 0）

## 2. 判据原文（UART 关键行）

```
CAM: vdma cold VER=0x62000050 CR=0x10001 SR=0x10000
CAM: vdma hot  VER=0x62000050 CR=0x10004 SR=0x10000
CAM: vdma step CR(0x30)<=RESET    off=0x30 w=0x4 r=0x10002 expect=0x0 ok=1
CAM: vdma step SR.HALTED==1       off=0x34 w=0x0 r=0x1 expect=0x1 ok=1
CAM: vdma step VSIZE(0xA0) kick-off off=0xA0 w=0x2D0 r=0x2D0 expect=0x2D0 ok=1
CAM: vdma step SR.HALTED==0       off=0x34 w=0x0 r=0x0 expect=0x0 ok=1
CAM: vdma SR=0x10000 halted=0 err=0x0 frmcnt=1
CAM: v27 enter
regs[30-5c]: cr=00010004 sr=00010000
clear_reset: cr=00010004
RESET_STUCK cr=00010004
halted: sr=00010000 (expect bit0=1)
cfg: vsize=000002D0 hsize=00000F00 stride=00000F00 frmptr=12000000
start: cr=00010004 (expect bit0=1, bit2=0)
RESET_SET_BY_START cr=00010004 (continuing for data)
kick: cr=00010004 sr=00010000
after1s: cr=00010004 sr=00010000 frmcnt=1
regs[a0-ac]: vsize=000002D0 hsize=00000F00 stride=00000F00 frmptr=12000000
CAM: v27 exit
ddr 0x12000000: 00000000 …（前 16 u32 仅 0x00800000 一个零散位）
```

## 3. 两次运行中快照（halt/read/con，均成功 resume）

```
snap1 @17.77s: CAM_CR=0x10001 (cr_running=1) CAM_SR=0x10000
  IP_TV(0x43CE0000)=0x2091  IP_TV2(+0x08)=0x1C7  IP_TR(0x43CF0000)=0x1  IP_TR2(+0x08)=0x2593E905
  GPIO_CAM=0x1  TL_TLAST(0x43CB0000)=0x4  TL_TUSER(+0x08)=0x1
  TAP_VALID(0x43CC0000)=0x2091  TAP_BP=0x0  IP_RST(0x43CD0000)=0x1
  PCLK=0x76AEF5FD  HREF=0x4DADB27F  VSYNC=0x02C2  PC=0x00108670 CPSR=0x800D00DF
snap2 @23.59s: CAM_CR=0x10004 (cr_running=0) CAM_SR=0x10000
  IP_TV=0x2091（不变） TAP_VALID=0x2091（不变） TL_TLAST=0x4（不变）
  PCLK=0x93D7AC81  HREF=0x60DF1A9E  VSYNC=0x0371（仍增长 ⇒ sensor 出流正常）
  PC=0x0010867C CPSR=0x600E00DF
```

## 4. 身份说明（重要，避免误读）

- 本轮 S1_IDENT 实际装载 ELF sha = `7c1ae719…`（403,880 B，22:39:03 开窗时磁盘版本）
- 同一窗口运行期间（22:39:19）`video-sw` 将该文件替换为 v27e `8fd0ef8e…`（404,976 B），故本目录 `window_close.txt` 头部按收窗时磁盘哈希显示为 `8fd0ef8e…`，**与实际装载不一致**；以上判据均基于实际装载的 `7c1ae719…`
- 位流：build11e bit `c74a1fd4…` / XSA `a03ec976…`（身份核验 PASS，ps7_init 由 XSA 提取，27,602 B `0c07e86f…`，APER=0x017C000D）

## 5. 门禁与契约

- 四门禁全 PASS：APER 断言（0x017C000D）、DDR 窗口写读、SCCB 总线体检（pre=post=0x3）、PL 探测（2B CSR=0x53324250、camera VDMA VER=0x62000050）
- `--allow-no-por` 已启用，日志保留 `[BOARD_STATE] ⚠️ OVERRIDE：POR 前置未满足仍开窗`
- **未物理 POR**：本窗用 PS7 重初始化 + PL 重编程替代（阶段3 对照实验残留）；**残留风险已记录；`board_state.abnormal` 未清除；建议最终验收前由 Wong 物理断电一次**
- 未使用 `rst -system` / `rst -processor`；未烧 QSPI；未改接线

## 6. 边界与下一步

- 本窗未跑相机窗（VDMA 未启动、DDR 无数据，不满足相机窗前置）
- 下一步：build11f（`s2mm_prmry_resetn` 显式连接 + 三路时钟同域 + `0x43D40000` rst 电平 / `0x43D50000` FCLK 计数），届时用 v27e `8fd0ef8e…` 跑 `ecam_diag_20261031_r50`
- 若 build11f 仍 `RESET_STUCK` ⇒ 转 VDMA IP 配置/重生成方向