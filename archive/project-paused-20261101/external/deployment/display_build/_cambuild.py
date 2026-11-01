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
      "-ffunction-sections", "-fdata-sections", "-U__clang__",
      "-DS5_CAMERA=1"]

# 相机 ELF 复用已编译的公共对象（不重编冻结显示/producer ELF）
OBJS = [ROOT / "build" / n for n in ("vdma_ctrl.o", "vtc_ctrl.o", "s5_timebase.o", "s5_real_source.o")]

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def build(tag: str, extra):
    defs = [*CF, *extra]
    app_obj = ROOT / "build" / f"s5_app_{tag}.o"
    cam_obj = ROOT / "build" / f"s5_camera_{tag}.o"
    elf = ROOT / "build" / f"s5_display_app_{tag}.elf"
    c1 = subprocess.run([str(GCC), *defs, f"-specs={BSP / 'Xilinx.spec'}",
                         f"-I{BSP / 'include'}", f"-I{ROOT / 'src'}",
                         "-o", str(app_obj), "-c", str(ROOT / "src" / "s5_display_app.c")],
                        cwd=str(ROOT), capture_output=True, text=True)
    c2 = subprocess.run([str(GCC), *defs, f"-specs={BSP / 'Xilinx.spec'}",
                         f"-I{BSP / 'include'}", f"-I{ROOT / 'src'}",
                         "-o", str(cam_obj), "-c", str(ROOT / "src" / "s5_camera.c")],
                        cwd=str(ROOT), capture_output=True, text=True)
    if c1.returncode or c2.returncode:
        print(f"{tag}: COMPILE FAIL app={c1.returncode} cam={c2.returncode}")
        print((c1.stderr or "")[-600:])
        print((c2.stderr or "")[-600:])
        return {"built": False}
    warn = (c1.stderr or "") + (c2.stderr or "")
    if warn.strip():
        print(f"{tag}: warnings:\n{warn[-600:]}")
    c3 = subprocess.run([str(GCC), *defs, f"-specs={BSP / 'Xilinx.spec'}",
                         f"-I{BSP / 'include'}", f"-I{ROOT / 'src'}",
                         f"-Wl,-Map={(ROOT / 'build' / (tag + '.map')).as_posix()},--cref,--gc-sections",
                         str(app_obj), str(cam_obj), *[str(o) for o in OBJS], "-o", str(elf),
                         f"-L{BSP / 'lib'}", "-Wl,-T", f"-Wl,{LD}",
                         "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                         "-lgcc", "-lc", "-lm", "-Wl,--end-group"],
                        cwd=str(ROOT), capture_output=True, text=True)
    if c3.returncode != 0:
        print(f"{tag}: LINK FAIL\n{c3.stderr[-800:]}")
        return {"built": False}
    app_obj.unlink(missing_ok=True)
    cam_obj.unlink(missing_ok=True)
    print(f"{tag}|{sha(elf)}|{elf.stat().st_size}")
    return {"built": True, "elf": elf.name, "sha256": sha(elf), "size_bytes": elf.stat().st_size}

variants = {}
variants["p3r_camera"] = build("p3r_camera", [])
variants["p3r_camera_longrun"] = build("p3r_camera_longrun", ["-DS5_LONG_RUN=1"])

sz = subprocess.run([str(SIZE), "--format=berkeley",
                     str(ROOT / "build" / "s5_display_app_p3r_camera.elf")],
                    capture_output=True, text=True)
record = {
    "task": "S5-P3R-CAMERA-R07",
    "built_utc8": datetime.now(CN).isoformat(timespec="seconds"),
    "feature": "S5_CAMERA=1：OV5640 640x480 SCCB + S2MM VDMA(0x43C60000, 24bpp, stride 1920, raw 0x12000000)",
    "data_width_evidence": {
        "stage3_xsa": "design_1_wrapper.xsa 1f5b138e… 的 .hwh：axi_vdma_1 C_S_AXIS_S2MM_TDATA_WIDTH=24, C_INCLUDE_SG=0",
        "converter": "axis_subset_converter 2->3 bytes, TDATA_REMAP={tdata[4:0],3'b000,tdata[10:5],2'b00,tdata[15:11],3'b000}",
        "ddr_format": "3 B/px, byte0=B byte1=G byte2=R => BGR888，640 宽 stride=1920，帧 921,600 B",
    },
    "source_sha256": {
        "src/s5_camera.c": sha(ROOT / "src" / "s5_camera.c"),
        "src/s5_camera.h": sha(ROOT / "src" / "s5_camera.h"),
        "src/s5_display_app.c": sha(ROOT / "src" / "s5_display_app.c"),
        "src/s5_display_app.h": sha(ROOT / "src" / "s5_display_app.h"),
        "tools/camera_selftest.c": sha(ROOT / "tools" / "camera_selftest.c"),
    },
    "toolchain": {"gcc": str(GCC), "version": "arm-xilinx-eabi-gcc 13.4.0",
                  "bsp": str(BSP), "lscript": str(LD)},
    "cflags": CF,
    "variants": variants,
    "size_berkeley": sz.stdout.strip(),
    "selftests": {"camera_selftest": "PASS（build/camera_selftest.exe，见 report §11.15）"},
    "not_rebuilt": "显示三件套 / producer v5 ELF 未重编（本记录只新增 p3r camera 变体）",
}
(ROOT / "build" / "p3r_camera_record.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print("record:", sha(ROOT / "build" / "p3r_camera_record.json"))
print(sz.stdout.strip())