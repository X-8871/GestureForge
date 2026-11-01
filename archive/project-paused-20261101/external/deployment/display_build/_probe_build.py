import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))
ROOT = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01")
GCC = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe")
SIZE = GCC.parent / "arm-none-eabi-size.exe"
READELF = GCC.parent / "arm-none-eabi-readelf.exe"
BSP = Path(r"D:\codex-worktrees\w4\tmp\4\S4-B-REAL-01\s4b_ps_tensor_20261023_r13\bundle_extract\bundle\workspace\ps7\export\ps7\sw\cpu0")

CF = ["-mcpu=cortex-a9", "-mfpu=vfpv3", "-mfloat-abi=hard", "-DSDT",
      "-Wall", "-Wextra", "-O2", "-g3", "-std=gnu11",
      "-ffunction-sections", "-fdata-sections", "-U__clang__"]

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

obj = ROOT / "build" / "ecam_probe.o"
elf = ROOT / "build" / "ecam_probe_ocm.elf"
c1 = subprocess.run([str(GCC), *CF, f"-specs={BSP / 'Xilinx.spec'}",
                     f"-I{BSP / 'include'}", f"-I{ROOT / 'tools'}",
                     "-o", str(obj), "-c", str(ROOT / "tools" / "ecam_probe.c")],
                    cwd=str(ROOT), capture_output=True, text=True)
print("compile:", c1.returncode)
if c1.stderr.strip():
    print(c1.stderr[-800:])
assert c1.returncode == 0

c2 = subprocess.run([str(GCC), *CF, f"-specs={BSP / 'Xilinx.spec'}",
                     f"-I{BSP / 'include'}",
                     "-Wl,-Map=build/ecam_probe_ocm.map,--cref,--gc-sections",
                     str(obj), "-o", str(elf),
                     "-T", str(ROOT / "tools" / "lscript_probe_ocm.ld"),
                     f"-L{BSP / 'lib'}",
                     "-Wl,--start-group", "-lxilstandalone", "-lxil",
                     "-lgcc", "-lc", "-lm", "-Wl,--end-group"],
                    cwd=str(ROOT), capture_output=True, text=True)
print("link:", c2.returncode)
if c2.stderr.strip():
    print(c2.stderr[-1200:])
assert c2.returncode == 0
obj.unlink(missing_ok=True)

sz = subprocess.run([str(SIZE), "--format=berkeley", str(elf)], capture_output=True, text=True)
sec = subprocess.run([str(READELF), "-S", str(elf)], capture_output=True, text=True)
hdrs = subprocess.run([str(READELF), "-h", str(elf)], capture_output=True, text=True)
print(sz.stdout.strip())
entry = [l.strip() for l in hdrs.stdout.splitlines() if "Entry point" in l]
print(entry)
secs = []
for line in sec.stdout.splitlines():
    if " ." in line and ("PROGBITS" in line or "NOBITS" in line):
        secs.append(" ".join(line.split()[:5]))
record = {
    "task": "S5-ECAM-PROBE-OCM",
    "built_utc8": datetime.now(CN).isoformat(timespec="seconds"),
    "purpose": "隔离 DDR：OCM-only 最小探针（不碰 DDR/I2C/帧存/中断/驱动），打印关键 MMIO + 心跳",
    "elf": {"path": str(elf.relative_to(ROOT)), "sha256": sha(elf), "size_bytes": elf.stat().st_size},
    "linker_script": {"path": "tools/lscript_probe_ocm.ld", "sha256": sha(ROOT / "tools" / "lscript_probe_ocm.ld")},
    "source": {"path": "tools/ecam_probe.c", "sha256": sha(ROOT / "tools" / "ecam_probe.c")},
    "sections": secs,
    "size_berkeley": sz.stdout.strip().splitlines()[-1] if sz.stdout.strip() else "",
    "cflags": CF,
    "toolchain": {"gcc": str(GCC), "version": "arm-xilinx-eabi-gcc 13.4.0", "bsp": str(BSP)},
    "notes": [
        "向量表 .vectors 在 OCM 0x0（ENTRY=_vector_table），运行不依赖 VBAR 重设",
        "不访问 0x100000/0x12000000/0x20000000/0x20800000",
        "仅 xil_printf + Xil_In32；无 XIicPs/XGpio/XScuGic",
    ],
}
(ROOT / "build" / "ecam_probe_record.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print("record:", sha(ROOT / "build" / "ecam_probe_record.json"))