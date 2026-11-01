"""构建阶段5 P3b-sw 显示应用（离线编译，不接触板卡/JTAG/Vivado）。

做了什么
  1. 用 Vitis 2026.1 的 arm-none-eabi-gcc + 既有 BSP（r13 导出）+ 既有链接脚本，
     把 s5_display_app.c / vdma_ctrl.c / s5_timebase.c 编译链接成 ELF；
  2. 记录 ELF 的 sha256、size（berkeley 格式）、map、输入文件哈希、退出码；
  3. 用主机 gcc 编译同一份绘图源码做离线渲染自检（PPM → PNG），证明布局/字体/框绘制可用；
  4. 全部产物落 build/，构建记录落 build/build_record.json。

退出码：0=ARM ELF 构建成功且主机自检通过；1=编译/链接失败；2=依赖缺失；
        3=主机自检失败（ARM ELF 仍可用，但要在报告里记）。

用法：
  python build_s5_display_app.py [--skip-host]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
BUILD = ROOT / "build"
TOOLS = ROOT / "tools"

# 既有链路（只读引用，不修改）
W = Path(r"D:\codex-worktrees\w4")
BUNDLE = W / "tmp" / "4" / "S4-B-REAL-01" / "s4b_ps_tensor_20261023_r13" / "bundle_extract" / "bundle" / "workspace"
BSP = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0"
INCLUDE = BSP / "include"
LIBDIR = BSP / "lib"
SPEC = BSP / "Xilinx.spec"
LSCRIPT = Path(r"D:\codex-worktrees\w4\tmp\4\S4-T34\ps_app_build\lscript_s4t34.ld")

GCC_BIN = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin")
GCC = GCC_BIN / "arm-none-eabi-gcc.exe"
SIZE = GCC_BIN / "arm-none-eabi-size.exe"
NM = GCC_BIN / "arm-none-eabi-nm.exe"

SOURCES = ["s5_display_app.c", "vdma_ctrl.c", "vtc_ctrl.c", "s5_timebase.c", "s5_real_source.c"]

CFLAGS = [
    "-mcpu=cortex-a9", "-mfpu=vfpv3", "-mfloat-abi=hard", "-DSDT",
    "-Wall", "-Wextra", "-O2", "-g3", "-std=gnu11",
    "-ffunction-sections", "-fdata-sections", "-U__clang__",
]


def sha256(path: Path) -> str | None:
    """文件 SHA-256（小写十六进制）。"""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def run(cmd: list[str], cwd: Path, log: Path) -> tuple[int, str]:
    """执行命令，stdout+stderr 追加到日志并返回。"""
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    out = (proc.stdout or "") + (proc.stderr or "")
    with log.open("a", encoding="utf-8") as fh:
        fh.write("$ " + " ".join(str(c) for c in cmd) + "\n" + out + "\n")
    return proc.returncode, out


def ppm_to_png(ppm: Path, png: Path) -> bool:
    """把 PPM 转 PNG（有 Pillow 才做，没有就跳过）。"""
    try:
        from PIL import Image
    except Exception:
        return False
    Image.open(ppm).save(png)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-host", action="store_true", help="跳过主机渲染自检")
    args = ap.parse_args()

    deps = [GCC, SIZE, INCLUDE, LIBDIR, SPEC, LSCRIPT] + [SRC / s for s in SOURCES]
    missing = [p for p in deps if not p.exists()]
    if missing:
        for p in missing:
            print(f"[FAIL] 依赖缺失：{p}")
        return 2

    BUILD.mkdir(parents=True, exist_ok=True)
    log = BUILD / "build_s5_display_app.log"
    if log.exists():
        log.unlink()

    objects = []
    for s in SOURCES:
        obj = BUILD / (Path(s).stem + ".o")
        rc, out = run([str(GCC), *CFLAGS, f"-specs={SPEC.as_posix()}",
                       f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                       "-o", str(obj), "-c", str(SRC / s)], BUILD, log)
        if rc != 0:
            print(f"[FAIL] 编译 {s} 失败 rc={rc}\n{out[-2000:]}")
            print(f"日志：{log}")
            return 1
        objects.append(str(obj))

    elf = BUILD / "s5_display_app.elf"
    mapf = BUILD / "s5_display_app.map"
    rc, out = run([str(GCC), *CFLAGS, f"-specs={SPEC.as_posix()}",
                   f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                   f"-Wl,-Map={mapf.as_posix()},--cref,--gc-sections",
                   *objects, "-o", str(elf),
                   f"-L{LIBDIR.as_posix()}",
                   "-Wl,-T", f"-Wl,{LSCRIPT.as_posix()}",
                   "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                   "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
    if rc != 0:
        print(f"[FAIL] 链接失败 rc={rc}\n{out[-3000:]}")
        print(f"日志：{log}")
        return 1

    rc_sz, size_out = run([str(SIZE), "--format=berkeley", str(elf)], BUILD, log)

    # G3/S6-F 30 min 长跑变体：仅 main 单元加 -DS5_LONG_RUN=1，重新编译该单元后与其余 .o 链接。
    longrun = {"built": False, "elf": "s5_display_app_longrun.elf", "sha256": None, "size_bytes": None}
    try:
        lr_obj = BUILD / "s5_display_app_longrun.o"
        lr_elf = BUILD / "s5_display_app_longrun.elf"
        rc_lr, out_lr = run([str(GCC), *CFLAGS, "-DS5_LONG_RUN=1",
                             f"-specs={SPEC.as_posix()}",
                             f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                             "-o", str(lr_obj), "-c", str(SRC / "s5_display_app.c")], BUILD, log)
        if rc_lr == 0:
            others = [o for o in objects if not o.endswith("s5_display_app.o")]
            rc_lrl, out_lrl = run([str(GCC), *CFLAGS, "-DS5_LONG_RUN=1",
                                   f"-specs={SPEC.as_posix()}",
                                   f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                                   f"-Wl,-Map={(BUILD / 's5_display_app_longrun.map').as_posix()},--cref,--gc-sections",
                                   str(lr_obj), *others, "-o", str(lr_elf),
                                   f"-L{LIBDIR.as_posix()}",
                                   "-Wl,-T", f"-Wl,{LSCRIPT.as_posix()}",
                                   "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                                   "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
            if rc_lrl == 0:
                longrun["built"] = True
                longrun["sha256"] = sha256(lr_elf)
                longrun["size_bytes"] = lr_elf.stat().st_size
            else:
                print(f"[WARN] 长跑 ELF 链接失败 rc={rc_lrl}\n{out_lrl[-1500:]}")
        else:
            print(f"[WARN] 长跑 ELF 编译失败 rc={rc_lr}\n{out_lr[-1500:]}")
    except Exception as exc:  # 长跑变体失败不阻断主产物
        print(f"[WARN] 长跑变体构建异常：{exc}")

    # G3-A 空闲测速变体：-DS5_IDLE_PROBE=1（10 帧渲染 + 3 s 空闲测 READSTR 周期）
    idleprobe = {"built": False, "elf": "s5_display_app_idleprobe.elf", "sha256": None, "size_bytes": None}
    try:
        ip_obj = BUILD / "s5_display_app_idleprobe.o"
        ip_elf = BUILD / "s5_display_app_idleprobe.elf"
        rc_ip, out_ip = run([str(GCC), *CFLAGS, "-DS5_IDLE_PROBE=1",
                             f"-specs={SPEC.as_posix()}",
                             f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                             "-o", str(ip_obj), "-c", str(SRC / "s5_display_app.c")], BUILD, log)
        if rc_ip == 0:
            others = [o for o in objects if not o.endswith("s5_display_app.o")]
            rc_ipl, out_ipl = run([str(GCC), *CFLAGS, "-DS5_IDLE_PROBE=1",
                                   f"-specs={SPEC.as_posix()}",
                                   f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                                   f"-Wl,-Map={(BUILD / 's5_display_app_idleprobe.map').as_posix()},--cref,--gc-sections",
                                   str(ip_obj), *others, "-o", str(ip_elf),
                                   f"-L{LIBDIR.as_posix()}",
                                   "-Wl,-T", f"-Wl,{LSCRIPT.as_posix()}",
                                   "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                                   "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
            if rc_ipl == 0:
                idleprobe["built"] = True
                idleprobe["sha256"] = sha256(ip_elf)
                idleprobe["size_bytes"] = ip_elf.stat().st_size
            else:
                print(f"[WARN] 空闲测速 ELF 链接失败 rc={rc_ipl}\n{out_ipl[-1500:]}")
        else:
            print(f"[WARN] 空闲测速 ELF 编译失败 rc={rc_ip}\n{out_ip[-1500:]}")
    except Exception as exc:  # 探针变体失败不阻断主产物
        print(f"[WARN] 空闲测速变体构建异常：{exc}")

    # P3b 回归变体：-DS5_VDMA_BASE=0x43C40000u -DS5_NO_VTC=0（旧架构：VDMA 在 0x43C40000、有 VTC）
    p3b = {"built": False, "elf": "s5_display_app_p3b.elf", "sha256": None, "size_bytes": None}
    try:
        pb_obj = BUILD / "s5_display_app_p3b.o"
        pb_elf = BUILD / "s5_display_app_p3b.elf"
        pb_defs = ["-DS5_VDMA_BASE=0x43C40000u", "-DS5_NO_VTC=0",
                   "-DS5_UF_FRAME_REG=0x43C10000u", "-DS5_UF_TOTAL_REG=0x43C10000u"]
        rc_pb, out_pb = run([str(GCC), *CFLAGS, *pb_defs,
                             f"-specs={SPEC.as_posix()}",
                             f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                             "-o", str(pb_obj), "-c", str(SRC / "s5_display_app.c")], BUILD, log)
        if rc_pb == 0:
            others = [o for o in objects if not o.endswith("s5_display_app.o")]
            rc_pbl, out_pbl = run([str(GCC), *CFLAGS, *pb_defs,
                                   f"-specs={SPEC.as_posix()}",
                                   f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                                   f"-Wl,-Map={(BUILD / 's5_display_app_p3b.map').as_posix()},--cref,--gc-sections",
                                   str(pb_obj), *others, "-o", str(pb_elf),
                                   f"-L{LIBDIR.as_posix()}",
                                   "-Wl,-T", f"-Wl,{LSCRIPT.as_posix()}",
                                   "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                                   "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
            if rc_pbl == 0:
                p3b["built"] = True
                p3b["sha256"] = sha256(pb_elf)
                p3b["size_bytes"] = pb_elf.stat().st_size
            else:
                print(f"[WARN] P3b 回归 ELF 链接失败 rc={rc_pbl}\n{out_pbl[-1500:]}")
        else:
            print(f"[WARN] P3b 回归 ELF 编译失败 rc={rc_pb}\n{out_pb[-1500:]}")
    except Exception as exc:
        print(f"[WARN] P3b 回归变体构建异常：{exc}")
    rc_nm, nm_out = run([str(NM), "-C", "--defined-only", str(elf)], BUILD, log)
    symbols = [ln.split()[-1] for ln in nm_out.splitlines() if ln.strip()]
    # 注意：-O2 会把只在本编译单元内调用的函数内联，随后 --gc-sections 把原始副本回收，
    # 所以 S5Display_RenderFrame / S5Sim_NextFrame 这类“只有 main 调用”的函数可能不在符号表里。
    # 这里只断言“必然存在”的对外入口（VDMA/时间基座/文字/缩放）确实进了 ELF。
    required_symbols = ["main", "S5Draw_Text", "S5Draw_CameraLetterbox",
                        "S5Vdma_Init", "S5Vdma_Start", "S5Vdma_WaitNotReading",
                        "S5Vtc_Init", "S5Real_Parse", "S5Ticks_Now"]
    # P3m 默认（S5_NO_VTC=1）：主程序不调用 VTC，vtc_ctrl.c 的函数被 --gc-sections 回收 → 不要求 S5Vtc_Init
    required_symbols = [s for s in required_symbols if s != "S5Vtc_Init"]
    missing_syms = [s for s in required_symbols if s not in symbols]

    # 主机渲染自检（同一份绘图源码）
    host = {"built": False, "ran": False, "exit": None, "pngs": []}
    if not args.skip_host:
        host_gcc = shutil.which("gcc")
        if host_gcc is None:
            print("[WARN] 未找到主机 gcc，跳过渲染自检")
        else:
            host_exe = BUILD / "host_render_test.exe"
            rc_h, out_h = run([host_gcc, "-std=gnu11", "-O2", "-Wall", "-Wextra",
                               "-DS5_HOST_TEST", f"-I{SRC.as_posix()}",
                               str(TOOLS / "host_render_test.c"),
                               str(SRC / "s5_display_app.c"), "-o", str(host_exe)],
                              BUILD, log)
            host["built"] = rc_h == 0
            if rc_h != 0:
                print(f"[WARN] 主机自检编译失败 rc={rc_h}\n{out_h[-2000:]}")
            else:
                # 以仓库根为工作目录运行：渲染产物按 "build/xxx.ppm" 落盘
                rc_r, out_r = run([str(host_exe)], ROOT, log)
                # 再渲染一套字面布局（S5_LAYOUT_BARS=1，G0 文本的自相矛盾备选方案）
                bars_exe = BUILD / "host_render_test_bars.exe"
                rc_b, out_b = run([host_gcc, "-std=gnu11", "-O2", "-Wall", "-Wextra",
                                   "-DS5_HOST_TEST", "-DS5_LAYOUT_BARS=1",
                                   f"-I{SRC.as_posix()}",
                                   str(TOOLS / "host_render_test.c"),
                                   str(SRC / "s5_display_app.c"), "-o", str(bars_exe)],
                                  BUILD, log)
                rc_rb = -1
                if rc_b == 0:
                    rc_rb, out_rb = run([str(bars_exe)], ROOT, log)
                    out_r = out_r + out_rb
                host["ran"] = (rc_r == 0) and (rc_rb == 0)
                host["exit"] = rc_r
                host["bars_variant_exit"] = rc_rb
                print(out_r.strip())
                for ppm in sorted(BUILD.glob("*.ppm")):
                    png = ppm.with_suffix(".png")
                    if ppm_to_png(ppm, png):
                        host["pngs"].append(png.name)
                if rc_r != 0:
                    print("[WARN] 主机渲染自检失败")

    # VTC/VDMA 寄存器序列自检：用假寄存器堆原样跑 vtc_ctrl.c + vdma_ctrl.c
    reg_selftest = {"built": False, "ran": False, "exit": None, "output": ""}
    if not args.skip_host:
        host_gcc = shutil.which("gcc")
        if host_gcc is not None:
            st_exe = BUILD / "host_vtc_vdma_selftest.exe"
            rc_s, out_s = run([host_gcc, "-std=gnu11", "-O2", "-Wall", "-Wextra",
                               "-DS5_HOST_TEST", "-DS5_VDMA_BASE=0x43C40000u", "-DS5_NO_VTC=0",
                               f"-I{(TOOLS / 'host_xil_shim').as_posix()}",
                               f"-I{SRC.as_posix()}",
                               str(TOOLS / "vtc_vdma_selftest.c"),
                               str(SRC / "vtc_ctrl.c"), str(SRC / "vdma_ctrl.c"),
                               "-o", str(st_exe)], BUILD, log)
            reg_selftest["built"] = rc_s == 0
            if rc_s != 0:
                print(f"[WARN] VTC/VDMA 自检编译失败 rc={rc_s}\n{out_s[-2000:]}")
            else:
                rc_run, out_run = run([str(st_exe)], ROOT, log)
                reg_selftest["ran"] = rc_run == 0
                reg_selftest["exit"] = rc_run
                reg_selftest["output"] = out_run.strip()
                (BUILD / "selftest_vtc_vdma.txt").write_text(
                    out_run.strip() + "\n", encoding="utf-8", newline="\n")
                print(out_run.strip())
                if rc_run != 0:
                    print("[WARN] VTC/VDMA 自检 FAIL")

    # 真实数据源自检：结果块 ABI + raw 画面 + 回退路径（同一份 s5_real_source.c / s5_display_app.c）
    real_selftest = {"built": False, "ran": False, "exit": None, "output": "", "pngs": []}
    if not args.skip_host:
        host_gcc = shutil.which("gcc")
        if host_gcc is not None:
            rs_exe = BUILD / "host_real_source_selftest.exe"
            rc_rs, out_rs = run([host_gcc, "-std=gnu11", "-O2", "-Wall", "-Wextra",
                                 "-DS5_HOST_TEST", f"-I{SRC.as_posix()}",
                                 str(TOOLS / "real_source_selftest.c"),
                                 str(SRC / "s5_real_source.c"),
                                 str(SRC / "s5_display_app.c"),
                                 "-o", str(rs_exe)], BUILD, log)
            real_selftest["built"] = rc_rs == 0
            if rc_rs != 0:
                print(f"[WARN] 真实源自检编译失败 rc={rc_rs}\n{out_rs[-2500:]}")
            else:
                rc_rsr, out_rsr = run([str(rs_exe)], ROOT, log)
                real_selftest["ran"] = rc_rsr == 0
                real_selftest["exit"] = rc_rsr
                real_selftest["output"] = out_rsr.strip()
                (BUILD / "selftest_real_source.txt").write_text(
                    out_rsr.strip() + "\n", encoding="utf-8", newline="\n")
                print(out_rsr.strip())
                for ppm in sorted(BUILD.glob("*.ppm")):
                    png = ppm.with_suffix(".png")
                    if ppm_to_png(ppm, png) and (png.name not in real_selftest["pngs"]):
                        real_selftest["pngs"].append(png.name)
                if rc_rsr != 0:
                    print("[WARN] 真实源自检 FAIL")

    # P3n 回归三变体（显示独立体地址：VDMA 0x43C00000、UF 0x43C10000 单寄存器）
    p3n_elfs = {}
    p3n_defs = ["-DS5_VDMA_BASE=0x43C00000u", "-DS5_NO_VTC=1",
                "-DS5_UF_FRAME_REG=0x43C10000u", "-DS5_UF_TOTAL_REG=0x43C10000u"]
    for tag, extra in (("p3n", []),
                       ("p3n_longrun", ["-DS5_LONG_RUN=1"]),
                       ("p3n_idleprobe", ["-DS5_IDLE_PROBE=1"])):
        rec = {"built": False, "elf": f"s5_display_app_{tag}.elf", "sha256": None, "size_bytes": None}
        try:
            defs = [*p3n_defs, *extra]
            obj = BUILD / f"s5_display_app_{tag}.o"
            out_elf = BUILD / f"s5_display_app_{tag}.elf"
            rc1, o1 = run([str(GCC), *CFLAGS, *defs, f"-specs={SPEC.as_posix()}",
                           f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                           "-o", str(obj), "-c", str(SRC / "s5_display_app.c")], BUILD, log)
            if rc1 == 0:
                others = [o for o in objects if not o.endswith("s5_display_app.o")]
                rc2, o2 = run([str(GCC), *CFLAGS, *defs, f"-specs={SPEC.as_posix()}",
                               f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                               f"-Wl,-Map={(BUILD / (tag + '.map')).as_posix()},--cref,--gc-sections",
                               str(obj), *others, "-o", str(out_elf),
                               f"-L{LIBDIR.as_posix()}",
                               "-Wl,-T", f"-Wl,{LSCRIPT.as_posix()}",
                               "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                               "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
                if rc2 == 0:
                    rec["built"] = True
                    rec["sha256"] = sha256(out_elf)
                    rec["size_bytes"] = out_elf.stat().st_size
                else:
                    print(f"[WARN] {tag} 链接失败 rc={rc2}\n{o2[-1200:]}")
            else:
                print(f"[WARN] {tag} 编译失败 rc={rc1}\n{o1[-1200:]}")
        except Exception as exc:
            print(f"[WARN] {tag} 构建异常：{exc}")
        p3n_elfs[tag] = rec

    # P3p（fsync 版）三变体：S5_VDMA_FSYNC=1 + P3p underflow 双寄存器语义
    p3p_elfs = {}
    p3p_defs = ["-DS5_VDMA_FSYNC=1", "-DS5_VDMA_BASE=0x43C00000u",
                "-DS5_UF_FRAME_REG=0x43C10000u", "-DS5_UF_TOTAL_REG=0x43C10008u"]
    for tag, extra in (("p3p", []),
                       ("p3p_longrun", ["-DS5_LONG_RUN=1"]),
                       ("p3p_idleprobe", ["-DS5_IDLE_PROBE=1"])):
        rec = {"built": False, "elf": f"s5_display_app_{tag}.elf", "sha256": None, "size_bytes": None}
        try:
            defs = [*p3p_defs, *extra]
            obj = BUILD / f"s5_display_app_{tag}.o"
            out_elf = BUILD / f"s5_display_app_{tag}.elf"
            rc1, o1 = run([str(GCC), *CFLAGS, *defs, f"-specs={SPEC.as_posix()}",
                           f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                           "-o", str(obj), "-c", str(SRC / "s5_display_app.c")], BUILD, log)
            if rc1 == 0:
                others = [o for o in objects if not o.endswith("s5_display_app.o")]
                rc2, o2 = run([str(GCC), *CFLAGS, *defs, f"-specs={SPEC.as_posix()}",
                               f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                               f"-Wl,-Map={(BUILD / (tag + '.map')).as_posix()},--cref,--gc-sections",
                               str(obj), *others, "-o", str(out_elf),
                               f"-L{LIBDIR.as_posix()}",
                               "-Wl,-T", f"-Wl,{LSCRIPT.as_posix()}",
                               "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                               "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
                if rc2 == 0:
                    rec["built"] = True
                    rec["sha256"] = sha256(out_elf)
                    rec["size_bytes"] = out_elf.stat().st_size
                else:
                    print(f"[WARN] {tag} 链接失败 rc={rc2}\n{o2[-1200:]}")
            else:
                print(f"[WARN] {tag} 编译失败 rc={rc1}\n{o1[-1200:]}")
        except Exception as exc:
            print(f"[WARN] {tag} 构建异常：{exc}")
        p3p_elfs[tag] = rec

    # P3q 生产者版三变体（S5_PRODUCER=1：每帧真实写结果块到 0x20800000，给 6-D 提供写端）
    p3q_prod = {}
    for tag, extra in (("p3q_producer", []),
                       ("p3q_producer_longrun", ["-DS5_LONG_RUN=1"]),
                       ("p3q_producer_idleprobe", ["-DS5_IDLE_PROBE=1"])):
        rec = {"built": False, "elf": f"s5_display_app_{tag}.elf", "sha256": None, "size_bytes": None}
        try:
            defs = ["-DS5_PRODUCER=1", *extra]
            obj = BUILD / f"s5_display_app_{tag}.o"
            out_elf = BUILD / f"s5_display_app_{tag}.elf"
            rc1, o1 = run([str(GCC), *CFLAGS, *defs, f"-specs={SPEC.as_posix()}",
                           f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                           "-o", str(obj), "-c", str(SRC / "s5_display_app.c")], BUILD, log)
            if rc1 == 0:
                others = [o for o in objects if not o.endswith("s5_display_app.o")]
                rc2, o2 = run([str(GCC), *CFLAGS, *defs, f"-specs={SPEC.as_posix()}",
                               f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                               f"-Wl,-Map={(BUILD / (tag + '.map')).as_posix()},--cref,--gc-sections",
                               str(obj), *others, "-o", str(out_elf),
                               f"-L{LIBDIR.as_posix()}",
                               "-Wl,-T", f"-Wl,{LSCRIPT.as_posix()}",
                               "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                               "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
                if rc2 == 0:
                    rec["built"] = True
                    rec["sha256"] = sha256(out_elf)
                    rec["size_bytes"] = out_elf.stat().st_size
                else:
                    print(f"[WARN] {tag} 链接失败 rc={rc2}\n{o2[-1200:]}")
            else:
                print(f"[WARN] {tag} 编译失败 rc={rc1}\n{o1[-1200:]}")
        except Exception as exc:
            print(f"[WARN] {tag} 构建异常：{exc}")
        p3q_prod[tag] = rec

    # 生产者 v2 故障注入变体（S5_PROD_FAULT=5：none→no_hand→stale→overrun→invalid 相位轮换）
    p3q_prod_fault = {"built": False, "elf": "s5_display_app_p3q_producer_fault.elf",
                      "sha256": None, "size_bytes": None}
    try:
        tag = "p3q_producer_fault"
        defs = ["-DS5_PRODUCER=1", "-DS5_PROD_FAULT=5"]
        obj = BUILD / f"s5_display_app_{tag}.o"
        out_elf = BUILD / f"s5_display_app_{tag}.elf"
        rc1, o1 = run([str(GCC), *CFLAGS, *defs, f"-specs={SPEC.as_posix()}",
                       f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                       "-o", str(obj), "-c", str(SRC / "s5_display_app.c")], BUILD, log)
        if rc1 == 0:
            others = [o for o in objects if not o.endswith("s5_display_app.o")]
            rc2, o2 = run([str(GCC), *CFLAGS, *defs, f"-specs={SPEC.as_posix()}",
                           f"-I{INCLUDE}", f"-I{SRC.as_posix()}",
                           f"-Wl,-Map={(BUILD / (tag + '.map')).as_posix()},--cref,--gc-sections",
                           str(obj), *others, "-o", str(out_elf),
                           f"-L{LIBDIR.as_posix()}",
                           "-Wl,-T", f"-Wl,{LSCRIPT.as_posix()}",
                           "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                           "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
            if rc2 == 0:
                p3q_prod_fault["built"] = True
                p3q_prod_fault["sha256"] = sha256(out_elf)
                p3q_prod_fault["size_bytes"] = out_elf.stat().st_size
            else:
                print(f"[WARN] {tag} 链接失败 rc={rc2}\n{o2[-1200:]}")
        else:
            print(f"[WARN] {tag} 编译失败 rc={rc1}\n{o1[-1200:]}")
    except Exception as exc:
        print(f"[WARN] 故障注入变体构建异常：{exc}")

    # 寄存器序列自检的 P3p 版（校验 CR 的 fsync 位）
    reg_selftest_fsync = {"built": False, "ran": False, "exit": None}
    if not args.skip_host:
        host_gcc = shutil.which("gcc")
        if host_gcc is not None:
            fs_exe = BUILD / "host_vtc_vdma_selftest_fsync.exe"
            rc_fs, out_fs = run([host_gcc, "-std=gnu11", "-O2", "-Wall", "-Wextra",
                                 "-DS5_HOST_TEST", "-DS5_VDMA_BASE=0x43C40000u",
                                 "-DS5_VDMA_FSYNC=1",
                                 f"-I{(TOOLS / 'host_xil_shim').as_posix()}",
                                 f"-I{SRC.as_posix()}",
                                 str(TOOLS / "vtc_vdma_selftest.c"),
                                 str(SRC / "vtc_ctrl.c"), str(SRC / "vdma_ctrl.c"),
                                 "-o", str(fs_exe)], BUILD, log)
            reg_selftest_fsync["built"] = rc_fs == 0
            if rc_fs == 0:
                rc_fsr, out_fsr = run([str(fs_exe)], ROOT, log)
                reg_selftest_fsync["ran"] = rc_fsr == 0
                reg_selftest_fsync["exit"] = rc_fsr
                (BUILD / "selftest_vtc_vdma_fsync.txt").write_text(
                    out_fsr.strip() + "\n", encoding="utf-8", newline="\n")
                print(out_fsr.strip())
            else:
                print(f"[WARN] fsync 寄存器自检编译失败 rc={rc_fs}\n{out_fs[-1500:]}")

    record = {
        "task_id": "S5-P3B-SW",
        "phase": "阶段5 HDMI 显示链 PS 侧显示软件（离线编译）",
        "built_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "boundary": "离线编译 + 主机渲染自检；未接触板卡/JTAG/COM4/hw_server，未跑 Vivado，未 git 提交",
        "toolchain": {
            "arm_gcc": str(GCC),
            "arm_gcc_version": run([str(GCC), "--version"], BUILD, log)[1].splitlines()[0],
            "linker_script": str(LSCRIPT),
            "bsp": str(BSP),
        },
        "inputs": {s: {"path": str(SRC / s), "sha256": sha256(SRC / s)} for s in SOURCES}
                  | {
                      "s5_font8x16.h": {"path": str(SRC / "s5_font8x16.h"),
                                        "sha256": sha256(SRC / "s5_font8x16.h")},
                      "lscript": {"path": str(LSCRIPT), "sha256": sha256(LSCRIPT)},
                  },
        "outputs": {
            "elf": {"path": elf.name, "sha256": sha256(elf), "size_bytes": elf.stat().st_size},
            "map": {"path": mapf.name, "sha256": sha256(mapf), "size_bytes": mapf.stat().st_size},
            "size_berkeley": size_out.strip(),
            "longrun_elf": longrun,
            "idleprobe_elf": idleprobe,
            "p3b_elf": p3b,
        "p3n_elfs": p3n_elfs,
        "p3p_elfs": p3p_elfs,
        "p3q_producer_elfs": p3q_prod,
        "p3q_producer_fault_elf": p3q_prod_fault,
        "reg_selftest_p3p_fsync": reg_selftest_fsync,
        },
        "symbol_check": {"required": required_symbols, "missing": missing_syms},
        "exit_codes": {"compile": 0, "link": rc, "size": rc_sz, "nm": rc_nm},
        "host_render": host,
        "reg_selftest_vtc_vdma": {k: v for k, v in reg_selftest.items() if k != "output"},
        "real_source_selftest": real_selftest,
        "limitations": [
            "未上板：VDMA/VTC 时序、DDR 带宽、rgb2dvi/TMDS 均未与硬件联调",
            "VDMA 2 帧存与 BD 的 c_num_fstores=2 一致；上板仍需读回 0x18 确认",
            "VTC 生成器已按 720p60 编程并回读校验，但未上板验证实际时序输出（无示波器/无 TMDS）",
            "真实源只在主机用 fixture/合成数据验证；板上需生产端实际写 0x20800000 才能验通",
            "结果块 ABI 文本写 16 B/项但字段合计 12 B：本实现按 16 B 步进读取（4 B 填充），生产端必须一致",
        ],
    }
    (BUILD / "build_record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    print("=" * 70)
    print(f"ELF      : {elf}")
    print(f"sha256   : {record['outputs']['elf']['sha256']}")
    print(f"size     : {record['outputs']['elf']['size_bytes']} B")
    print(f"size(berkeley): {' '.join(record['outputs']['size_berkeley'].split())}")
    print(f"longrun ELF: built={longrun['built']} sha256={longrun['sha256']} "
          f"size={longrun['size_bytes']}")
    print(f"idleprobe ELF: built={idleprobe['built']} sha256={idleprobe['sha256']} "
          f"size={idleprobe['size_bytes']}")
    print(f"p3b ELF: built={p3b['built']} sha256={p3b['sha256']} size={p3b['size_bytes']}")
    for tag, rec in p3n_elfs.items():
        print(f"{tag} ELF: built={rec['built']} sha256={rec['sha256']} size={rec['size_bytes']}")
    for tag, rec in p3q_prod.items():
        print(f"{tag} ELF: built={rec['built']} sha256={rec['sha256']} size={rec['size_bytes']}")
    print(f"p3q_producer_fault ELF: built={p3q_prod_fault['built']} "
          f"sha256={p3q_prod_fault['sha256']} size={p3q_prod_fault['size_bytes']}")
    for tag, rec in p3p_elfs.items():
        print(f"{tag} ELF: built={rec['built']} sha256={rec['sha256']} size={rec['size_bytes']}")
    print(f"P3p fsync selftest: built={reg_selftest_fsync['built']} "
          f"ran={reg_selftest_fsync['ran']} exit={reg_selftest_fsync['exit']}")
    print(f"symbols  : missing={missing_syms}")
    print(f"host test: built={host['built']} ran={host['ran']} pngs={host['pngs']}")
    print(f"VTC/VDMA selftest: built={reg_selftest['built']} ran={reg_selftest['ran']} "
          f"exit={reg_selftest['exit']}")
    print(f"real-source selftest: built={real_selftest['built']} ran={real_selftest['ran']} "
          f"exit={real_selftest['exit']}")
    print("=" * 70)

    if missing_syms:
        print("[FAIL] ELF 缺少必需符号")
        return 1
    if shutil.which("gcc") is not None:
        if not host["built"]:
            print("[FAIL] 主机渲染自检编译失败")
            return 3
        if not reg_selftest["built"]:
            print("[FAIL] VTC/VDMA 自检编译失败")
            return 4
        if not real_selftest["built"]:
            print("[FAIL] 真实源自检编译失败")
            return 5
    if not args.skip_host and host["built"] and not host["ran"]:
        return 3
    if not args.skip_host and reg_selftest["built"] and not reg_selftest["ran"]:
        return 4
    if not args.skip_host and real_selftest["built"] and not real_selftest["ran"]:
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
