# 长抓取窗口：2B 位流 + 细分探针应用，UART 抓 180 s（应用每轮 ~11.8 s）
import subprocess, threading, time, os

XSDB = r"D:/Xilinx/2026.1/Vitis/bin/xsdb.bat"
VIVADO = r"D:/Xilinx/2026.1/Vivado/bin/vivado.bat"
INIT = r"D:/codex-worktrees/w4/report/evidence/S4-B/s4b_ps_tensor_20261023_r13/verified_payload/init.elf"
BIT = r"D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit"
PROBE = r"D:/tmp/lead/probe_app_20261029_r01/s4d_ps_app_sw0_longrunP.elf"
OUT = r"D:/tmp/lead/probe_long_20261029_r01"
os.makedirs(OUT, exist_ok=True)

lines = []
stop = {"v": False}

def reader():
    import serial
    try:
        ser = serial.Serial("COM4", 115200, timeout=0.3)
    except Exception as e:
        lines.append("OPEN_FAIL %s" % e); return
    t0 = time.time()
    while not stop["v"] and time.time() - t0 < 200:
        try:
            b = ser.readline()
        except Exception as e:
            lines.append("READ_FAIL %s" % e); break
        if b:
            s = b.decode("utf-8", "replace").strip()
            lines.append("%.2f %s" % (time.time() - t0, s))
            print("U:", lines[-1], flush=True)
    try: ser.close()
    except Exception: pass

def w(name, t):
    p = os.path.join(OUT, name)
    open(p, "w", encoding="utf-8", newline="\n").write(t)
    return p.replace("\\", "/")

def xsdb(tcl, tag):
    p = subprocess.run([XSDB, "-eval", "source " + tcl], capture_output=True, text=True, timeout=900)
    txt = (p.stdout or "") + (p.stderr or "")
    open(os.path.join(OUT, tag + ".log"), "w", encoding="utf-8").write(txt)
    print("==", tag, "exit=", p.returncode, flush=True)
    return p.returncode, txt

# 1) reset + ps7_init
t1 = w("s1.tcl", """connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
rst -system -stop
after 800
targets -set -filter {name =~ "*Cortex-A9*#0*"}
rst -processor -stop
dow %s
con
after 2500
rst -processor -stop
""" % INIT.replace("\\", "/"))
xsdb(t1, "S1_init")

# 2) program PL
pt = w("prog.tcl", """open_hw_manager
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
print("program_pl exit=", pv.returncode, "PROGRAM_OK=", "PROGRAM_OK" in (pv.stdout or ""), flush=True)

# 3) 0xF + app + con（不再 mrd，避免把核停下）
th = threading.Thread(target=reader, daemon=True); th.start()
t3 = w("s3.tcl", """connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
rst -processor -stop
mwr 0xF8000008 0xDF0D
mwr 0xF8000900 0x0000000F
mwr 0xF8000240 0x00000000
mwr 0xF8000004 0x767B
mrd 0xF8000900 1
dow %s
mwr 0xF8000008 0xDF0D
mwr 0xF8000900 0x0000000F
mwr 0xF8000004 0x767B
puts "PRE_CON=[state]"
con
after 2000
puts "POST_CON=[state]"
""" % PROBE.replace("\\", "/"))
xsdb(t3, "S3_app")
time.sleep(180)
stop["v"] = True
th.join(timeout=30)
open(os.path.join(OUT, "uart.log"), "w", encoding="utf-8").write("\n".join(lines))
print("TOTAL_LINES=", len(lines))