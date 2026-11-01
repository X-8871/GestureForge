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
        print(f"{tag}: COMPILE FAIL\n{c1.stderr[-1000:]}")
        results[tag] = {"built": False}
        continue
    if c1.stderr.strip():
        print(f"{tag}: warnings:\n{c1.stderr[-500:]}")
    c2 = subprocess.run([str(GCC), *CF, *defs, f"-specs={BSP / 'Xilinx.spec'}",
                         f"-I{BSP / 'include'}", f"-I{ROOT / 'src'}",
                         f"-Wl,-Map={(ROOT / 'build' / (tag + '.map')).as_posix()},--cref,--gc-sections",
                         str(obj), *[str(o) for o in OBJS], "-o", str(elf),
                         f"-L{BSP / 'lib'}", "-Wl,-T", f"-Wl,{LD}",
                         "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                         "-lgcc", "-lc", "-lm", "-Wl,--end-group"],
                        cwd=str(ROOT), capture_output=True, text=True)
    if c2.returncode != 0:
        print(f"{tag}: LINK FAIL\n{c2.stderr[-1000:]}")
        results[tag] = {"built": False}
        continue
    sha = hashlib.sha256(elf.read_bytes()).hexdigest()
    results[tag] = {"built": True, "elf": elf.name, "sha256": sha, "size_bytes": elf.stat().st_size}
    print(f"{tag}|{sha}|{elf.stat().st_size}")
    obj.unlink(missing_ok=True)

sz = subprocess.run([str(SIZE), "--format=berkeley", str(ROOT / "build" / "s5_display_app_p3q_producer.elf")],
                    capture_output=True, text=True)

def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

record = {
    "task": "S5-P3Q-PRODUCER-A-rev5",
    "built_utc8": datetime.now(CN).isoformat(timespec="seconds"),
    "identity": "A（sidecar @+0x100；n_dets<=14 fail-closed；flush 0x120）",
    "rev5_changes": [
        "writer: lock odd -> flush lock line -> DSB -> payload (result_time last) -> flush 288B -> DSB -> lock even -> flush lock line -> DSB",
        "reader: invalidate-first (lock+payload) -> s1 (odd retry) -> payload -> DMB -> s2 (must equal s1, even) -> retry<=3",
        "session uniqueness claim narrowed: within-session constant only; cross-POR not claimed (stage7 R-14)",
    ],
    "source_sha256": {
        "src/s5_display_app.c": sha256_of(ROOT / "src" / "s5_display_app.c"),
        "src/s5_display_app.h": sha256_of(ROOT / "src" / "s5_display_app.h"),
        "src/s5_publish_abi.h": sha256_of(ROOT / "src" / "s5_publish_abi.h"),
        "src/s5_result_abi.h": sha256_of(ROOT / "src" / "s5_result_abi.h"),
        "src/s5_real_source.c": sha256_of(ROOT / "src" / "s5_real_source.c"),
        "src/s5_timebase.c": sha256_of(ROOT / "src" / "s5_timebase.c"),
        "src/vdma_ctrl.c": sha256_of(ROOT / "src" / "vdma_ctrl.c"),
        "tools/real_source_selftest.c": sha256_of(ROOT / "tools" / "real_source_selftest.c"),
        "build_s5_display_app.py": sha256_of(ROOT / "build_s5_display_app.py"),
    },
    "toolchain": {"gcc": str(GCC), "version": "arm-xilinx-eabi-gcc 13.4.0",
                  "bsp": str(BSP), "lscript": str(LD)},
    "cflags": CF,
    "variants": results,
    "size_berkeley": sz.stdout.strip(),
    "display_trio": "未重编（阶段5 冻结物保持 e4ba0cb4…/cbf5ebe3…/2c880e4e…）",
    "archives": ["build/rev2_archived/（rev2 作废存档）", "build/rev3_archived/（rev3 存档）"],
    "note": "旧 E3(s6e_e3_age_20261030_r01)/E5 证据保留原判、不复用；板窗用新 RunId 跑 E6 系列",
}
(ROOT / "build" / "p3q_producer_A_rev5_record.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print("record written", sha256_of(ROOT / "build" / "p3q_producer_A_rev5_record.json"))
print(sz.stdout.strip())
