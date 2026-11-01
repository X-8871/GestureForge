import io

p = r"src\s5_display_app.c"
s = io.open(p, encoding="utf-8").read()

# include driver header
if '#include "xaxivdma.h"' not in s:
    s = s.replace('#include "xil_cache.h"', '#include "xil_cache.h"\n#include "xaxivdma.h"', 1)

# static config（放在文件静态区；若已存在则跳过）
if "s5_vdma_cfg" not in s:
    anchor = "static uint32_t app_now_ms(void)"
    cfg = '''/* v29：相机 VDMA（S2MM-only, 24bpp, DRE=1, SG=0）驱动配置（与阶段3 对齐） */
static XAxiVdma_Config s5_vdma_cfg = {
    .Name = "s5_cam_vdma",
    .BaseAddress = 0x43C60000u,
    .MaxFrameStoreNum = 1,
    .HasMm2S = 0,
    .HasMm2SDRE = 0,
    .Mm2SWordLen = 0,
    .HasS2Mm = 1,
    .HasS2MmDRE = 1,
    .S2MmWordLen = 2,
    .HasSG = 0,
    .EnableVIDParamRead = 0,
    .UseFsync = 0,
    .FlushonFsync = 0,
    .Mm2SBufDepth = 0,
    .S2MmBufDepth = 0,
    .Mm2SGenLock = 0,
    .S2MmGenLock = 0,
    .InternalGenLock = 0,
    .S2MmSOF = 0,
    .Mm2SStreamWidth = 0,
    .S2MmStreamWidth = 24,
    .AddrWidth = 32,
};

''' + anchor
    s = s.replace(anchor, cfg, 1)

# 替换 v27e 块
lines = s.split("\n")
start = None
for i, l in enumerate(lines):
    if "v27e：v27d 七行最小序列" in l:
        start = i
        break
assert start is not None
end = None
for i in range(start, len(lines)):
    if lines[i].strip() == "}" and lines[i].startswith("            }"):
        end = i
        break
assert end is not None

blk = r'''/* v29：改用 Xilinx XAxiVdma 驱动（与阶段3 相同路径），打印每步 XST_* 返回码。
             * 不在手写 CR/VSIZE/HSIZE/STRIDE/FRMPTR。 */
            {
                XAxiVdma vdma;
                XAxiVdma_DmaSetup ws = {0};
                UINTPTR buf[1];
                volatile uint32_t *crp = (volatile uint32_t *)0x43C60030u;
                volatile uint32_t *srp = (volatile uint32_t *)0x43C60034u;
                volatile uint32_t *rawp7 = (volatile uint32_t *)0x12000000u;
                int st_cfg, st_conf, st_addr, st_start;
                uint32_t k, fc;

                xil_printf("CAM: v29 enter\r\n");
                st_cfg = XAxiVdma_CfgInitialize(&vdma, &s5_vdma_cfg, s5_vdma_cfg.BaseAddress);
                xil_printf("drv: CfgInitialize=%d (XST_SUCCESS=%d)\r\n", st_cfg, XST_SUCCESS);
                ws.VertSizeInput = 720;
                ws.HoriSizeInput = 3840;
                ws.Stride = 3840;
                ws.FrameDelay = 0;
                ws.EnableCircularBuf = 1;
                ws.EnableSync = 1;
                ws.PointNum = 0;
                ws.EnableFrameCounter = 0;
                ws.FixedFrameStoreAddr = 0;
                st_conf = XAxiVdma_DmaConfig(&vdma, XAXIVDMA_WRITE, &ws);
                xil_printf("drv: DmaConfig=%d (VERT=%d HORI=%d STRIDE=%d circ=%d sync=%d)\r\n",
                           st_conf, ws.VertSizeInput, ws.HoriSizeInput, ws.Stride,
                           ws.EnableCircularBuf, ws.EnableSync);
                buf[0] = 0x12000000u;
                st_addr = XAxiVdma_DmaSetBufferAddr(&vdma, XAXIVDMA_WRITE, buf);
                xil_printf("drv: DmaSetBufferAddr=%d buf0=0x%x\r\n", st_addr, (unsigned)buf[0]);
                st_start = XAxiVdma_DmaStart(&vdma, XAXIVDMA_WRITE);
                xil_printf("drv: DmaStart=%d\r\n", st_start);
                s5_cam_bus_delay(0, 1000000u);
                fc = ((*srp) & S5_CAM_SR_FRMCNT_MASK) >> S5_CAM_SR_FRMCNT_SHIFT;
                xil_printf("after1s: cr=%08x sr=%08x frmcnt=%u\r\n",
                           (unsigned)*crp, (unsigned)*srp, (unsigned)fc);
                Xil_DCacheInvalidateRange((UINTPTR)0x12000000u, 64u);
                xil_printf("ddr 0x12000000:");
                for (k = 0u; k < 16u; k++) {
                    xil_printf(" %08x", (unsigned)rawp7[k]);
                }
                xil_printf("\r\n");
                xil_printf("CAM: v29 exit\r\n");
            }'''

lines[start:end + 1] = blk.split("\n")
s = "\n".join(lines)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("app v29 driver block inserted")