"""离线构建 S4-T31 M4-a 最小测量 ELF（Vitis 2026.1 arm-none-eabi-gcc，cortex-a9）。

约束（卡片 + lead 裁定）：
  · **离线构建**：窗口内禁止编译，故本脚本只在离线期运行；
  · 复用**本地** workspace 构建包（BSP include/lib/spec + init 链接脚本），**不引用 w2b**；
  · 只编译一个源文件 `scripts/stage4_s4b/m4a_src/m4a_cache_probe.c`（M4-a 专用，不含业务功能）；
  · 产出 ELF/map + `build_record.json`（工具链版本、完整命令、源/产物/链接脚本/BSP 库 SHA-256、大小）。

用法：python -B scripts/stage4_s4b/build_m4a_measurement_elf.py
退出码：0=构建成功并登记；1=编译/链接失败（原始日志保留）；2=环境缺失。
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))
W = Path(r"D:\codex-worktrees\w4")
SOURCE = W / "scripts" / "stage4_s4b" / "m4a_src" / "m4a_cache_probe.c"
BUNDLE = W / "tmp" / "4" / "S4-B-REAL-01" / "s4b_ps_tensor_20261023_r13" / "bundle_extract" / "bundle" / "workspace"
BUILD = W / "tmp" / "4" / "S4-T31" / "m4a_build"
EVID = W / "report" / "evidence" / "S4-B" / "s4_ddr_four_measurements_20261027_r01" / "preparation" / "payloads"
GCC = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe")
SIZE = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-size.exe")


def sha256_file(path: Path) -> str | None:
    """文件 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def run(cmd: list[str], cwd: Path, log: Path) -> tuple[int, str]:
    """执行命令并把 stdout/stderr 追加到日志；返回 (退出码, 组合输出)。"""
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    text = (proc.stdout or "") + (proc.stderr or "")
    with log.open("a", encoding="utf-8") as handle:
        handle.write("$ " + " ".join(cmd) + "\n")
        handle.write(text + "\n")
    return proc.returncode, text


def main() -> int:
    """编译并链接。"""
    if not GCC.is_file():
        print(f"[FAIL] 交叉编译器缺失：{GCC}")
        return 2
    if not SOURCE.is_file():
        print(f"[FAIL] 源文件缺失：{SOURCE}")
        return 2
    include = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0" / "include"
    libdir = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0" / "lib"
    spec = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0" / "Xilinx.spec"
    lscript = BUNDLE / "init" / "src" / "lscript.ld"
    for path in (include, libdir, spec, lscript):
        if not path.exists():
            print(f"[FAIL] 构建依赖缺失：{path}")
            return 2

    BUILD.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    log = BUILD / "build.log"
    if log.exists():
        log.unlink()

    common = [
        "-DSDT", "-mcpu=cortex-a9", "-mfpu=vfpv3", "-mfloat-abi=hard",
        "-MMD", "-MP", f"-specs={spec.as_posix()}",
        f"-I{include.as_posix()}", "-Wall", "-Wextra", "-O2", "-g3", "-std=gnu11",
        "-ffunction-sections", "-fdata-sections", "-U__clang__",
    ]
    obj = BUILD / "m4a_cache_probe.o"
    elf = BUILD / "m4a_cache_probe.elf"
    mapfile = BUILD / "m4a_cache_probe.map"

    compile_cmd = [str(GCC), *common, "-o", str(obj), "-c", str(SOURCE)]
    code_c, out_c = run(compile_cmd, BUILD, log)
    if code_c != 0:
        print(f"[FAIL] 编译失败 exit={code_c}；日志 {log}")
        return 1

    link_cmd = [str(GCC), *common,
                f"-Wl,-Map={mapfile.as_posix()},--cref,--gc-sections",
                str(obj), "-o", str(elf),
                f"-L{libdir.as_posix()}",
                "-Wl,-T", f"-Wl,{lscript.as_posix()}",
                "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                "-lgcc", "-lc", "-lm", "-Wl,--end-group"]
    code_l, out_l = run(link_cmd, BUILD, log)
    if code_l != 0:
        print(f"[FAIL] 链接失败 exit={code_l}；日志 {log}")
        return 1

    code_sz, size_out = run([str(SIZE), "--format=berkeley", str(elf)], BUILD, log)
    code_ver, gcc_ver = run([str(GCC), "--version"], BUILD, log)

    for artifact in (elf, mapfile):
        shutil.copy2(artifact, EVID / artifact.name)

    record = {
        "task_id": "S4-B/S4-T31",
        "purpose": "M4-a 最小测量程序（cache 维护/可见性）；**不用于推理**，不含业务功能",
        "built_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "offline_build": True,
        "window_time_compilation": "FORBIDDEN（窗口内不得编译）",
        "toolchain": {
            "gcc": str(GCC), "gcc_version": (gcc_ver.splitlines() or [""])[0].strip(),
            "size_tool": str(SIZE), "size_exit": code_sz, "size_output": size_out.strip(),
        },
        "inputs": {
            "source": {"path": str(SOURCE.relative_to(W)).replace("\\", "/"), "sha256": sha256_file(SOURCE)},
            "linker_script": {"path": str(lscript), "sha256": sha256_file(lscript)},
            "xilinx_spec": {"path": str(spec), "sha256": sha256_file(spec)},
            "bsp": {"include_dir": str(include), "lib_dir": str(libdir),
                    "libxilstandalone_sha256": sha256_file(libdir / "libxilstandalone.a"),
                    "libxil_sha256": sha256_file(libdir / "libxil.a"),
                    "libxiltimer_sha256": sha256_file(libdir / "libxiltimer.a")},
        },
        "commands": {"compile": " ".join(compile_cmd), "link": " ".join(link_cmd),
                     "size": f"{SIZE} --format=berkeley {elf}"},
        "outputs": {
            "elf": {"path": str((EVID / elf.name)), "sha256": sha256_file(EVID / elf.name),
                    "size_bytes": (EVID / elf.name).stat().st_size},
            "map": {"path": str((EVID / mapfile.name)), "sha256": sha256_file(EVID / mapfile.name),
                    "size_bytes": (EVID / mapfile.name).stat().st_size},
            "object": {"path": str(obj), "sha256": sha256_file(obj)},
        },
        "exit_codes": {"compile": code_c, "link": code_l, "size": code_sz},
        "boundary": "离线构建；未连接板卡；不含业务功能；缓存维护按 64 B 向外取整；只在候选区内读写。",
    }
    record_path = EVID / "build_record.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"elf_sha256": record["outputs"]["elf"]["sha256"],
                      "elf_size": record["outputs"]["elf"]["size_bytes"],
                      "map_sha256": record["outputs"]["map"]["sha256"],
                      "size_output": record["toolchain"]["size_output"],
                      "build_record_sha256": sha256_file(record_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())