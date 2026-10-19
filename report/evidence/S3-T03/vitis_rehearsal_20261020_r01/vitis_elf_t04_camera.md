# 阶段3 T04 摄像头直通 standalone ELF（2026-10-20, run r03）

## 结论

**成功**。用 T04 r03 的 XSA 重新生成了 BSP（未复用 T03 的 BSP/xparameters.h），导入厂商 `an5642_single` 源码、应用诊断补丁后编译链接出可 JTAG 下载的 standalone ELF。

- ELF：`report/evidence/S3-T03/vitis_rehearsal_20261020_r01/an5642_single_t04_r03.elf`（构建源：`tmp/s3r06/vitis_rehearsal_r01/t04_camera_r03/app/an5642_single.elf`）
- 大小 302,004 B；SHA-256 `A3720D8C6D50EA9D4671ECC2029A4341911B350AB9B80D54066B84673C8BFA74`
- `readelf -h`：`Type EXEC`、`Machine ARM`、`Entry point 0x00100000`；`size`：text 58,332 / data 1,592 / bss 18,688,320

## 可重放命令链（完整）

```
D:\codex-worktrees\dbdf\scripts\stage3_t04_vitis\run_stage3_vitis_elf.cmd ^
  "D:\codex-worktrees\dbdf\tmp\s3r06\t04_camera_20261020_r03\design_1_wrapper.xsa" ^
  "D:\codex-worktrees\dbdf\tmp\s3r06\vitis_rehearsal_r01\t04_camera_r03" ^
  "D:\codex-worktrees\dbdf\tmp\stage3_reference\AX7020_2023.1\course_s2_vitis\22_ov5640_single\Vitis\auto_create_vitis\src\an5642_single" ^
  "an5642_single.elf" ^
  "D:\codex-worktrees\dbdf\board\stage3\software\sensor\s3_t04_app_diag.patch"
```

参数：`<XSA> <OUT_DIR> <APP_SRC_DIR> [ELF_NAME] [PATCH_FILE]`。脚本内部三步：
① 把 XSA 复制到 `<OUT>/_input/`，再 `sdtgen.bat gen_bsp_app.tcl`（HSI：`hsi::open_hw_design` → `create_sw_design` → `generate_bsp`+`write_mss` → `create_sw_design` → `generate_app empty_application`）；
② 导入厂商源码 → `git apply -p1 <patch>`（popd 前记录退出码，另有 `findstr S3_DIAG_APP_ENTER` 自检）；
③ `make -f Makefile.app EXEC=an5642_single.elf`（自动发现顶层 + 一级子目录 `.c`）。

入口是 **sdtgen 的 TCL shell + HSI**（XSCT 在 2026.1 被禁用，详见 `vitis_elf_rehearsal.md` 第二节）。退出码 0，日志 `tmp/s3r06/vitis_rehearsal_r01/t04_camera_r03.log`。
自动发现到的源码：`vdma.c ov5640.c display_demo.c display_ctrl/display_ctrl.c dynclk/dynclk.c i2c/PS_i2c.c`。

## 关键符号地址（`arm-none-eabi-nm --defined-only`）

| 符号 | 地址 | 来源 |
|---|---|---|
| `main` | 0x00109aac | display_demo.c |
| `sensor_init` | 0x00100820 | ov5640.c |
| `i2c_reg16_read` | 0x00101048 | i2c/PS_i2c.c |
| `vdma_write_init` | 0x001006a4 | vdma.c |
| `DisplayInitialize` | 0x00100b08 | display_ctrl |
| `XGpio_Initialize` | 0x00102b5c | BSP gpiops |
| `ov5640_write` / `ov5640_read` | 0x001007d4 / 0x001007ac | ov5640.c |

## 外设溯源（证明 BSP 来自 r03 XSA，而非 T03）

从 r03 XSA 生成的 `xparameters.h` 逐条与 T04 设计一致：

```
XPAR_AXI_VDMA_0_BASEADDR 0x43000000  (DEVICE_ID 0)
XPAR_AXI_VDMA_1_BASEADDR 0x43010000  (DEVICE_ID 1)
XPAR_CMOS_RST_BASEADDR   0x41200000  (DEVICE_ID 0)
XPAR_V_TC_0_BASEADDR     0x43C00000  (DEVICE_ID 0)
XPAR_AXI_DYNCLK_0_BASEADDR 0x43C10000
XPAR_AXIVDMA_0/1_DEVICE_ID → XPAR_AXI_VDMA_0/1_DEVICE_ID（供源码 #define 使用）
```

## 诊断补丁落地证据

- 源码内 4 处：`S3_DIAG_APP_ENTER`（display_demo.c:65）、`S3_DIAG_SENSOR_ID=0x%02X%02X`（:99）、`S3_DIAG_DISPLAY_START status=%d`（:127）、`S3_DIAG_VDMA_WRITE_STARTED`（:137）
- ELF 二进制内 4 条字符串全部命中（对 ELF 做 ASCII 扫描，4/4 True）

## 本次新增的工具坑

1. `hsi::open_hw_design` 会把 XSA 成员**解包到 XSA 所在目录** → 脚本已改为先复制到 `<OUT>/_input/`（详见 `vitis_elf_rehearsal.md` 第七节）。
2. cmd 中 `%errorlevel%` / `%VAR%` 放在**括号块内**会在块解析时提前展开，导致 `git apply` 退出码判空；补丁段落已改为 goto 结构（块外逐行），并加 `findstr` 自检。

## 限制

不连硬件/JTAG、不烧录、不开 hw_server；未跑 Vivado 综合/实现；未改厂商原件；未 git add/commit。
ELF 的 SHA 并非位级可复现（BSP 并行 `make` + `ar` 归档记录 `.o` 时间戳），但段布局与符号地址稳定。