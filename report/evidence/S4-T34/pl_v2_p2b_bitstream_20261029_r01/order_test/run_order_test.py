# 用过去跑通过的 driver 流程（reset_stop → 0xA → program PL → 0xF → init+app）复测 2B 位流 + 探针应用
# 目的：判断"首次 CSR 读挂死"是否与上电/装载顺序有关（对比我自写的 rst-system→init→program→0xF 顺序）
import sys, types, time, os
sys.path.insert(0, r"D:/codex-worktrees/w4/scripts/stage4_s4b")
import run_bringup_driver as drv

BIT = r"D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit"
PROBE = r"D:/tmp/lead/probe_app_20261029_r01/s4d_ps_app_sw0_longrunP.elf"
OUT = r"D:/tmp/lead/order_test_20261029_r01"
os.makedirs(OUT, exist_ok=True)
import pathlib
drv.RUN_DIR = pathlib.Path(OUT)
drv.base.RUN_DIR = pathlib.Path(OUT)

# 让身份门通过（探针 ELF 的 SHA 前缀）
drv.APP_SW_PREFIX = "faa399b2"
drv.APP_SW_SHA = "faa399b268e35a2f7d0bef7ecbcb38ebef444abdd7fb0a50351db46e3d6def2c"

args = types.SimpleNamespace(bit=pathlib.Path(BIT), app_elf=pathlib.Path(PROBE), init_elf=pathlib.Path(drv.INIT_ELF))
print("APP_SW_SHA expected:", drv.APP_SW_SHA)
res = drv.stage_pspl_setup_and_load(args)
print("RESULT:", res)

# 应用已在运行：再抓 20 s UART
try:
    import serial
    ser = serial.Serial("COM4", 115200, timeout=0.2)
    t0 = time.time()
    lines = []
    while time.time() - t0 < 20:
        b = ser.readline()
        if b:
            lines.append(b.decode("utf-8", "replace").strip())
    ser.close()
    open(os.path.join(OUT, "uart_after.log"), "w", encoding="utf-8").write("\n".join(lines))
    print("UART_AFTER lines=%d" % len(lines))
    for l in lines[:40]:
        print("U:", l)
except Exception as e:
    print("UART_FAIL", e)