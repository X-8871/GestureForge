import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))
ROOT = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01")
GCC = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe")
SIZE = GCC.parent / "arm-none-eabi-size.exe"
BSP = Path(r"D:\codex-worktrees\w4\tmp\4\S4-B-REAL-01\s4b_ps_tensor_20261023_r13\bundle_extract\bundle\workspace\ps7\export\ps7\sw\cpu0")
LD = Path(r"D:\codex-worktrees\w4\tmp\4\S4-T34\ps_app_build\lscript_s4t34.ld")

CF = ["-mcpu=cortex-a9", "-mfpu=vfpv3", "-mfloat-abi=hard", "-DSDT",
      "-Wall", "-Wextra", "-O2", "-g3", "-std=gnu11",
      "-ffunction-sections", "-fdata-sections", "-U__clang__"]
OBJS = [ROOT / "build" / n for n in ("vdma_ctrl.o", "vtc_ctrl.o", "s5_timebase.o", "s5_real_source.o")]

VARIANTS = [
    ("p3q_producer", []),
    ("p3q_producer_longrun", ["-DS5_LONG_RUN=1"]),
    ("p3q_producer_idleprobe", ["-DS5_IDLE_PROBE=1"]),
    ("p3q_producer_fault", ["-DS5_PROD_FAULT=5"]),
    ("p3q_producer_fault_overrun", ["-DS5_PROD_FAULT=1"]),
    ("p3q_producer_fault_stale", ["-DS5_PROD_FAULT=2"]),
    ("p3q_producer_fault_invalid", ["-DS5_PROD_FAULT=3"]),
    ("p3q_producer_fault_no_hand", ["-DS5_PROD_FAULT=4"]),
]

results = {}
for tag, extra in VARIANTS:
    defs = ["-DS5_PRODUCER=1", *extra]
    obj = ROOT / "build" / f"s5_display_app_{tag}.o"
    elf = ROOT / "build" / f"s5_display_app_{tag}.elf"
    c1 = subprocess.run([str(GCC), *CF, *defs, f"-specs={BSP / 'Xilinx.spec'}",
                         f"-I{BSP / 'include'}", f"-I{ROOT / 'src'}",
                         "-o", str(obj), "-c", str(ROOT / "src" / "s5_display_app.c")],
                        cwd=str(ROOT), capture_output=True, text=True)
    if c1.returncode != 0:
        print(f"{tag}: COMPILE FAIL\n{c1.stderr[-800:]}")
        results[tag] = {"built": False, "error": c1.stderr[-400:]}
        continue
    if c1.stderr.strip():
        print(f"{tag}: warnings:\n{c1.stderr[-400:]}")
    c2 = subprocess.run([str(GCC), *CF, *defs, f"-specs={BSP / 'Xilinx.spec'}",
                         f"-I{BSP / 'include'}", f"-I{ROOT / 'src'}",
                         f"-Wl,-Map={(ROOT / 'build' / (tag + '.map')).as_posix()},--cref,--gc-sections",
                         str(obj), *[str(o) for o in OBJS], "-o", str(elf),
                         f"-L{BSP / 'lib'}", "-Wl,-T", f"-Wl,{LD}",
                         "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                         "-lgcc", "-lc", "-lm", "-Wl,--end-group"],
                        cwd=str(ROOT), capture_output=True, text=True)
    if c2.returncode != 0:
        print(f"{tag}: LINK FAIL\n{c2.stderr[-800:]}")
        results[tag] = {"built": False, "error": c2.stderr[-400:]}
        continue
    sha = hashlib.sha256(elf.read_bytes()).hexdigest()
    results[tag] = {"built": True, "elf": elf.name, "sha256": sha, "size_bytes": elf.stat().st_size}
    print(f"{tag}|{sha}|{elf.stat().st_size}")
    obj.unlink(missing_ok=True)

sz = subprocess.run([str(SIZE), "--format=berkeley", str(ROOT / "build" / "s5_display_app_p3q_producer.elf")],
                    capture_output=True, text=True)
record = {
    "task": "S5-P3Q-PRODUCER-A(rev3)",
    "built_utc8": datetime.now(CN).isoformat(timespec="seconds"),
    "identity": "A（Wong 2026-10-31 裁定）：sidecar @+0x100，n_dets<=14 fail-closed，flush 0x120",
    "sidecar_offset": "0x100",
    "publish_bytes": "0x120",
    "ndets_max": 14,
    "toolchain": {"gcc": str(GCC), "version": "arm-xilinx-eabi-gcc 13.4.0",
                  "bsp": str(BSP), "lscript": str(LD)},
    "cflags": CF,
    "variants": results,
    "size_berkeley": sz.stdout.strip(),
    "display_trio": "未重编（s5_display_app.elf / _longrun / _idleprobe 保持阶段5 冻结物）",
    "rev2_archive": "build/rev2_archived/（rev2 ELF 原样存档，作废）+ S5_PRODUCER_V2_FREEZE_rev2_archived.md",
    "note": "E3 s6e_e3_age_20261030_r01 即 +0x100 偏移（A 一致），可作行为参考，但为 rev1 软件、无 14 框 fail-closed",
}
(ROOT / "build" / "p3q_producer_A_rev3_record.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print("record written")
print(sz.stdout.strip())