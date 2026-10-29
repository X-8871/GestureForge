# 探针窗口（P2a 位流 + 探针应用）：定位"首次 CSR 读挂住"的根因
# 顺序：rst-system -> init.elf(ps7_init) -> program PL(P2a) -> LVL_SHFTR_EN=0xF(读回) -> dow probe.elf -> con -> 抓 UART
import subprocess, threading, time, re, sys, os, hashlib

XSDB = r"D:/Xilinx/2026.1/Vitis/bin/xsdb.bat"
VIVADO = r"D:/Xilinx/2026.1/Vivado/bin/vivado.bat"
INIT = r"D:/codex-worktrees/w4/report/evidence/S4-B/s4b_ps_tensor_20261023_r13/verified_payload/init.elf"
BIT = r"D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit"
PROBE = r"D:/tmp/lead/probe_app_20261029_r01/s4d_ps_app_sw0_longrunP.elf"
OUT = r"D:/tmp/lead/probe_window_2b_20261029_r01"
os.makedirs(OUT, exist_ok=True)

uart_lines = []
stop_flag = {"v": False}

def uart_reader():
    try:
        import serial
    except Exception as e:
        uart_lines.append("UART_IMPORT_FAIL %s" % e)
        return
    try:
        ser = serial.Serial("COM4", 115200, timeout=0.2)
    except Exception as e:
        uart_lines.append("UART_OPEN_FAIL %s" % e)
        return
    t0 = time.time()
    while not stop_flag["v"] and time.time() - t0 < 60:
        try:
            b = ser.readline()
        except Exception as e:
            uart_lines.append("UART_READ_FAIL %s" % e); break
        if b:
            uart_lines.append("%.3f %s" % (time.time() - t0, b.decode("utf-8", "replace").strip()))
    try: ser.close()
    except Exception: pass

def run_xsdb(tcl, tag):
    p = subprocess.run([XSDB, "-eval", "source " + tcl.replace(chr(92), chr(47))], capture_output=True, text=True, timeout=1800)
    txt = (p.stdout or "") + (p.stderr or "")
    open(os.path.join(OUT, tag + ".log"), "w", encoding="utf-8").write(txt)
    print("==", tag, "exit=", p.returncode)
    return p.returncode, txt

def w(name, tcl):
    p = os.path.join(OUT, name)
    open(p, "w", encoding="utf-8", newline="\n").write(tcl)
    return p

# ---------- 1) reset + ps7_init ----------
t1 = w("s1.tcl", """
connect -url tcp:127.0.0.1:3121
puts [targets]
targets -set -filter {name =~ "*Cortex-A9*#0*"}
rst -system -stop
after 800
targets -set -filter {name =~ "*Cortex-A9*#0*"}
rst -processor -stop
dow %s
con
after 2500
rst -processor -stop
mrd 0xF8000900 1
mrd 0xF8000170 1
mrd 0xF8000240 1
""" % INIT.replace("\\", "/"))
c1, x1 = run_xsdb(t1, "S1_reset_init")

# ---------- 2) program PL ----------
pt = w("prog.tcl", """
open_hw_manager
connect_hw_server -url localhost:3121
open_hw_target
current_hw_device [lindex [get_hw_devices xc7z020*] 0]
set_property PROGRAM.FILE {%s} [current_hw_device]
program_hw_devices [current_hw_device]
refresh_hw_device -update_hw_probes false [current_hw_device]
puts "PROGRAM_OK"
close_hw_target
disconnect_hw_server
close_hw_manager
""" % BIT)
pv = subprocess.run([VIVADO, "-mode", "batch", "-nojournal", "-nolog", "-source", pt,
                     "-log", os.path.join(OUT, "prog.log")], capture_output=True, text=True, timeout=900)
print("== program_pl exit=", pv.returncode, "PROGRAM_OK=", "PROGRAM_OK" in (pv.stdout or ""))

# ---------- 3) 0xF + probe app + UART ----------
th = threading.Thread(target=uart_reader, daemon=True)
th.start()
t3 = w("s3.tcl", """
connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
rst -processor -stop
mwr 0xF8000008 0xDF0D
mwr 0xF8000900 0x0000000F
mwr 0xF8000040 0x0
mwr 0xF8000240 0x00000000
mwr 0xF8000004 0x767B
mrd 0xF8000900 1
mrd 0xF8000170 1
mrd 0xF8000240 1
dow %s
mwr 0xF8000008 0xDF0D
mwr 0xF8000900 0x0000000F
mwr 0xF8000004 0x767B
puts "PROBE_HOLD=[state]"
con
after 6000
puts "PROBE_RUN_STATE=[state]"
mrd 0xF8000900 1
mrd 0xF8000170 1
mrd 0xF8000240 1
""" % PROBE)
c3, x3 = run_xsdb(t3, "S3_probe_app")
time.sleep(3)
stop_flag["v"] = True
th.join(timeout=70)
open(os.path.join(OUT, "uart.log"), "w", encoding="utf-8").write("\n".join(uart_lines))
print("== uart lines =", len(uart_lines))
for l in uart_lines[:40]:
    print("UART:", l)
print("== S3 log tail ==")
print("\n".join(x3.strip().splitlines()[-14:]))