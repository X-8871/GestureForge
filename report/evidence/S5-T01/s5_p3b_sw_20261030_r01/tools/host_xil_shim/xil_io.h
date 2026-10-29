/*
 * host_xil_shim/xil_io.h —— 主机自检用的 Xil_In32/Xil_Out32 替身声明
 *
 * 目的：让 vdma_ctrl.c / vtc_ctrl.c 这两个**真正会跑在板上的源文件**（含寄存器序列、
 * 位域、回读校验逻辑）在主机上原样编译运行，MMIO 由 tools/vtc_vdma_selftest.c
 * 用一块假寄存器堆实现。这样离线就能验证“写序列 + 回读校验 + 双缓冲选择”逻辑，
 * 不需要板卡、也不需要改被测源码（只换头文件搜索顺序）。
 *
 * 注意：本文件不在 ARM 构建里出现（ARM 用 BSP 的 include/xil_io.h）。
 */
#ifndef S5_HOST_XIL_IO_SHIM_H
#define S5_HOST_XIL_IO_SHIM_H

#include <stdint.h>

uint32_t Xil_In32(uint32_t addr);
void Xil_Out32(uint32_t addr, uint32_t val);

#endif /* S5_HOST_XIL_IO_SHIM_H */