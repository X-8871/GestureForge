# 阶段3 T04 Vitis standalone ELF 预演（2026-10-20, run r01）

## 一、结论

- **path A（XSCT classic createhw/createbsp）已死**：Vitis 2026.1 直接禁用 xsct。
- **path B（Vitis Unified Python API）在本机对两代 XSA 都失败，根因已定位**（不是许可、不是器件族、不是 XSA 缺 PS 信息）。
- **path C 走通并已产出可 JTAG 下载的 standalone ELF**。实现方式不是"手搓驱动"，而是复用 AMD 随 Vitis 2026.1 一同发布的 `sdtgen` + **HSI**（`hsi::generate_bsp` / `hsi::generate_app`）——即 classic createhw/createbsp/createapp 的等价实现，只是入口由被禁用的 xsct 换成 sdtgen 的 TCL shell。
- 交付 ELF：`report/evidence/S3-T03/vitis_rehearsal_20261020_r01/vdma_hdmi.elf`，1,668,868 B，SHA-256 `D07E553246210E55C12337A5A7286277C7797F97465C04D1F9173AB0FB3232FF`，入口 `0x00100000`。

## 二、路径判定依据（命令 / 退出码 / 错误原文）

### A：不可用（工具级禁用）

`D:\Xilinx\2026.1\Vitis\bin\xsct.bat <script>` →

```
[ERROR]********** XSCT is disabled in Vitis 2026.1 release **********
Please use the Vitis Python Console for script-based projects creation and build,
or use Python-based XSDB for debugging.
```

退出码 0（仅打印错误、不执行脚本）。`createhw/createbsp/createapp` 无法调用。

### B：不可用（Unified 平台拿不到处理器）

`client.create_platform_component()` 成功，但随后
`platform.add_domain(cpu="ps7_cortexa9_0", os="standalone", ...)` 抛：

```
add_domain failed, status = StatusCode.INTERNAL,
details = 'Error in adding domain.Invalid Processor name 'ps7_cortexa9_0'.
           Valid Processors are '[]'.'
```

调用栈落点：`D:\Xilinx\2026.1\Vitis\cli\vitis\platform_component.py:363`（raise）← `:353`（AddDomainRequest）← `cli_client.py:1889`（get_processor_os_list）。
`get_processor_os_list(xsa=<XSA>)` 也只返回 `deviceFamily: "'" / flow: EMBEDDED`，没有处理器段。
落盘清单证据：`vitis-comp.json` 中 `"processorsMap": {}`、`"supportedOS": []`、`"domains": []`（`tmp/s3_vitis_bsp_probe_20261007_01/workspace/ax7020_ov5640_vendor_fixture/vitis-comp.json:14-19`），同时 `"supportedFamily": "zynq"`。

**根因**：Unified 平台组件的处理器/OS 枚举读的是 XSA 的元数据段（`xsa.xml` / `xsa.json` 的处理器节点）；而本工程两代 XSA 都是 Vivado 普通 *hw_export* 产物，`xsa.xml` 里只有
`<Devices><Device Name="fpga0" Type="8" FpgaDevice="zynq:xc7z020:clg400:-2">`，**没有任何处理器节点**（厂商 2023.1 XSA 与新建 2026.1 XSA 均已逐字核对，`xsa.xml` 无 Processor 元素）。HSI 走 hwh/bda 解析，因此同一 XSA 能正确枚举出 `ps7_cortexa9_0 ps7_cortexa9_1`。

**已排除的假设**：① 器件族不支持（`supportedFamily=zynq`，SDT 仓库含 `cpu_cortexa9`、`zynq-7000.dtsi`）；② XSA 缺 PS7 信息（`ps7_init.c/h/tcl`、`pcw.dtsi` 均能从该 XSA 正常生成）；③ 许可问题（`XILINXD_LICENSE_FILE=basic_only.lic` 已注入，BSP 编译全程无许可错误）；④ 路径/引号转义（已改为 TCL 环境变量传参）；⑤ 2026.1 删除了 legacy BSP 能力（实际 HSI 100 条命令齐全，含 `generate_bsp`/`create_sw_design`/`generate_app`）。

## 三、可用路径（已实测通过）

关键事实：`sdtgen` 在 2026.1 内仍加载完整 HSI（实测 `info commands hsi::*` 返回 100 条，含 `hsi::generate_bsp`、`hsi::create_sw_design`、`hsi::generate_app`、`hsi::open_hw_design`）。

可重放脚本（已提交到工作树，未 git add）：

```
scripts/stage3_t04_vitis/run_stage3_vitis_elf.cmd <XSA> <OUT_DIR> <VENDOR_APP_SRC_DIR>
scripts/stage3_t04_vitis/gen_bsp_app.tcl      # HSI：open_hw_design -> create_sw_design(bsp) ->
                                              # generate_bsp + write_mss -> create_sw_design(app) ->
                                              # generate_app empty_application
scripts/stage3_t04_vitis/Makefile.app         # Cortex-A9/VFPv3 hard-float，libxil.a + lscript.ld
```

内部分三步：① `sdtgen.bat gen_bsp_app.tcl`（生成 `<OUT>/bsp` 与 `<OUT>/app`，app 内含 `lscript.ld`/`Xilinx.spec`/自带 BSP）；② 导入厂商源码；③ `make -f Makefile.app`。
干净重放两次（r01/r02）退出码均为 **0**，日志 `tmp/s3r06/vitis_rehearsal_r01/replay_r01.log`、`replay_r02.log`，交付产物取自 `tmp/s3r06/vitis_rehearsal_r01/elf_replay_r02/app/vdma_hdmi.elf`。

两条已验证事实：
- **厂商 2023.1 XSA**（提交 fcf1e4a…）：`create_sw_design bsp0 -proc ps7_cortexa9_0 -os standalone` → `generate_bsp` 成功，生成驱动 `axivdma_v6_17 / vtc_v8_8 / standalone_v9_5 / …`，`make` 出 `libxil.a`（含 `xaxivdma.o`、`xvtc.o`），退出码 0 → 预演目标达成。
- **新 2026.1 XSA**（`tmp/s3r06/t03b_hdmi_20261020_r01/design_1_wrapper.xsa`，SHA `02174319…`）：BSP+app+ELF 全流程成功。

### 工具坑（复现时必须保留）

1. `sdtgen.bat` 传**带引号的脚本路径**会致命报 `The syntax of the command is incorrect.`，且**会终止调用它的批处理**：sdtgen.bat 把引号保留进 `if [%1] == []` / `set RDI_ARGS=… %1`，rdiArgs.bat 解析崩。必须 `pushd` 到脚本目录后传**裸相对文件名**（实测 V8/V9 通过，V2/V5 失败）。
2. 不要先 `call Vitis\settings64.bat` 再调 `sdtgen.bat`（同样致命解析错误）；`make` 只需要 `RDI_PLATFORM=win` 与两个工具链目录进 PATH。
3. `.cmd` 内出现中文会在 OEM 代码页下破坏命令解析 → 包装脚本保持纯 ASCII（中文说明只在文档里）。
4. TCL 侧路径统一正斜杠；XSA/输出目录经环境变量传入 TCL，避免命令行转义。

## 四、ELF 证据

- 路径：`report/evidence/S3-T03/vitis_rehearsal_20261020_r01/vdma_hdmi.elf`（复现源：`tmp/s3r06/vitis_rehearsal_r01/elf_replay_r01/app/vdma_hdmi.elf`）
- 大小 1,668,868 B；SHA-256 `B1FB09C8A5F35FDEA9963B099E1B62D975081231F77AFC7739DA88D03B85E94F`
- `readelf -h`：`Type EXEC`、`Machine ARM`、`Entry point 0x100000`；`.text` VMA `0x00100000`，`.bss` 6,246,656 B（3 帧 1920×1080×3 的 `frameBuf`）
- `objdump -h`：`.text/.data/.bss/.mmu_tbl/.ARM.exidx` 齐全，无空洞
- `nm --defined-only` 证明链接进 XAxiVdma 与显示驱动：`XAxiVdma_CfgInitialize @0x00100fa0`、`DisplayInitialize @0x00100ac0`、`DisplayStart @0x001008ac`、`DemoPrintTest @0x00100508`、`main @0x00107bec`、`gImage_pic_800_600 @0x00107d00`（.rodata）、`frameBuf @0x0026cbc0`（.bss）
- 链接基线：HSI 生成的 `lscript.ld`（`ps7_ddr_0 ORIGIN=0x100000 LENGTH=0x3FF00000`）+ `libxil.a` + `Xilinx.spec`
- XPAR 与厂商 `main.c` 的 `#define` 一一对应（取自新 XSA 的 BSP `xparameters.h`）：`XPAR_AXI_DYNCLK_0_BASEADDR 0x43C10000`、`XPAR_AXIVDMA_0_DEVICE_ID`、`XPAR_VTC_0_DEVICE_ID`
- 说明：ELF 的 SHA 在两次运行间会不同（BSP 用 `make -j` 并行编译、`ar` 归档记录 `.o` 时间戳），非位级可复现；产物功能一致（符号/段布局相同）。

## 五、XSDB（为后续 JTAG 下载准备，本次未连接任何硬件）

- `D:\Xilinx\2026.1\Vitis\bin\xsdb.bat` **仍可用**（与 xsct 不同）：实测 `xsdb.bat xsdb_probe.tcl` 打印 `XSDB_TCL_OK`，退出码 0；同样只能用**裸相对文件名**传脚本。
- Python 版 XSDB：`import xsdb; s = xsdb.session.Session(); s.connect(host='127.0.0.1', port='3121')`（`Vitis\cli\xsdb\session.py:101` 类、`:428` connect）。
- 建议下载序列（**未执行，仅建议**）：`connect` → `targets` → `fpga -f design_1_wrapper.bit` → `source ps7_init.tcl; ps7_init; ps7_post_config` → `dow -elf vdma_hdmi.elf` → `con`。

## 六、限制与未执行项

不连硬件、不开 hw_server、不 program/烧录、不跑 Vivado 综合/实现、不改厂商原件、不 git add/commit。
未做（也不需要）：FSBL/boot.bin（任务只要 standalone ELF）；"仅 ps7_init.tcl + 纯 PL 图案"的替代路线（有了 ELF 后不必要）；Bitstream 未重新生成（复用 t03b 的 `7143427f…`）。

## 七、工具副作用与归属声明（HSI 原地解包，2026-10-20 追加）

- **机制**：`hsi::open_hw_design <XSA>` 会把 XSA 内的 `design_1_wrapper.bit`、`ps7_init.c/.h/.html/.tcl`、`ps7_init_gpl.c/.h` 解包到 **XSA 文件所在目录**，并新建 `extracted/`、`.Xil/`。
- **复现验证**：把厂商 XSA 复制到 `tmp/s3r06/vitis_rehearsal_r01/xsa_inplace_test/` 后只执行 `hsi::open_hw_design`，该目录由 1 个文件变为 11 项（含 7 个解包成员），日志见 `tmp/s3r06/vitis_rehearsal_r01/proto1_bsp.log` 同目录下的测试输出。
- **归属（确认由本任务流程产生，非厂商原件自带）**，两处：
  1. 厂商只读缓存 `tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/14_vdma_hdmi_out/Vitis/`：2026-10-20 00:38:08 新增上述 7 个文件与 `extracted/`。来源命令：预演第一步的 `sdtgen.bat -xsa <该目录下的 design_1_wrapper.xsa> -dir <本任务 tmp 输出>`——HSI 直接打开了原始 XSA 路径。
  2. `tmp/s3r06/t03b_hdmi_20261020_r01/`：2026-10-20 00:49:09 新增同组文件，字节大小与 XSA 成员逐一相同。来源：ELF 干净重放 r01/r02 时 `S3_XSA` 直接指向该 XSA。
- 已按指示**保留全部文件未删除**，仅作归属声明；`.Xil` 缓存同理保留。
- **已修复**：`run_stage3_vitis_elf.cmd` 现在先把 XSA 复制到 `<OUT>/_input/design_1_wrapper.xsa`，HSI 只操作该副本；sdtgen 的 cwd 与 `.Xil` 缓存也固定在 `<OUT>/_sdtgen_cwd`。此后任何输入目录（厂商缓存、他人构建目录）都不会再被写入。
- 遗留提醒：任何绕过该脚本、直接把原始 XSA 路径喂给 HSI/sdtgen 的动作都会复现此副作用。