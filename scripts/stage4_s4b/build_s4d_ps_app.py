"""离线构建 4-D PS 应用 ELF（S4-T32 范围扩展；不含板级动作）。

- 编译 `vitis/stage4/ps/s4d_ps_app.c`，链接既有 BSP（r13 构建包内 `ps7/export/ps7/sw/cpu0`）与 init 链接脚本；
- **PREPROC_SRC 编译期开关**：0=PS 软件预处理（兜底，默认）、1=PL 新块 CSR；
- 记录：工具链版本/完整命令/源与产物 SHA-256/大小/真实退出码；
- 明确边界：网络/解码入口为 weak 桩，完整应用需在 Vitis 中链接 r13 既有目标文件；本 ELF 是**可编译骨架**，未上板。

用法：
  python -B scripts/stage4_s4b/build_s4d_ps_app.py [--preproc-src 0|1]
退出码：0=编译+链接成功；1=失败（保留日志）；2=环境缺失。
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
W = Path(r"D:\codex-worktrees\w4")
SOURCE = W / "vitis" / "stage4" / "ps" / "s4d_ps_app.c"
BUNDLE = W / "tmp" / "4" / "S4-B-REAL-01" / "s4b_ps_tensor_20261023_r13" / "bundle_extract" / "bundle" / "workspace"
BUILD = W / "tmp" / "4" / "S4-T32" / "ps_app_build"
EVID = W / "report" / "evidence" / "S4-T32" / "phase2_ps_app_20261027_r01"
GCC = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe")
SIZE = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-size.exe")


def sha(path: Path) -> str | None:
    """文件 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def run(cmd: list[str], cwd: Path, log: Path) -> tuple[int, str]:
    """执行命令并追加日志。"""
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    out = (proc.stdout or "") + (proc.stderr or "")
    with log.open("a", encoding="utf-8") as fh:
        fh.write("$ " + " ".join(cmd) + "\n" + out + "\n")
    return proc.returncode, out


def main() -> int:
    """构建。"""
    ap = argparse.ArgumentParser()
    ap.add_argument("--preproc-src", type=int, default=0, choices=[0, 1])
    args = ap.parse_args()
    if not GCC.is_file():
        print(f"[FAIL] 交叉编译器缺失：{GCC}")
        return 2
    include = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0" / "include"
    libdir = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0" / "lib"
    spec = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0" / "Xilinx.spec"
    lscript = BUNDLE / "init" / "src" / "lscript.ld"
    for p in (SOURCE, include, libdir, spec, lscript):
        if not p.exists():
            print(f"[FAIL] 依赖缺失：{p}")
            return 2
    BUILD.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    log = BUILD / "build.log"
    if log.exists():
        log.unlink()
    common = ["-DSDT", f"-DPREPROC_SRC={args.preproc_src}", "-mcpu=cortex-a9", "-mfpu=vfpv3",
              "-mfloat-abi=hard", "-MMD", "-MP", f"-specs={spec.as_posix()}",
              f"-I{include.as_posix()}", "-Wall", "-Wextra", "-O2", "-g3", "-std=gnu11",
              "-ffunction-sections", "-fdata-sections", "-U__clang__"]
    obj = BUILD / "s4d_ps_app.o"
    elf = BUILD / "s4d_ps_app.elf"
    mapf = BUILD / "s4d_ps_app.map"
    code_c, _ = run([str(GCC), *common, "-o", str(obj), "-c", str(SOURCE)], BUILD, log)
    if code_c != 0:
        print(f"[FAIL] 编译失败 exit={code_c}；日志 {log}")
        return 1
    code_l, _ = run([str(GCC), *common, f"-Wl,-Map={mapf.as_posix()},--cref,--gc-sections",
                     str(obj), "-o", str(elf), f"-L{libdir.as_posix()}",
                     "-Wl,-T", f"-Wl,{lscript.as_posix()}",
                     "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                     "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
    if code_l != 0:
        print(f"[FAIL] 链接失败 exit={code_l}；日志 {log}")
        return 1
    code_sz, size_out = run([str(SIZE), "--format=berkeley", str(elf)], BUILD, log)
    code_ver, gcc_ver = run([str(GCC), "--version"], BUILD, log)
    for a in (elf, mapf):
        shutil.copy2(a, EVID / a.name)
    record = {
        "task_id": "S4-B/S4-T32", "phase": "PS 应用（范围扩展）",
        "purpose": "4-D PS 应用：mailbox ABI + PREPROC_SRC 开关 + infer_one_from_pl_tensor（跳过 CPU memcpy/输入写回）",
        "preproc_src": args.preproc_src,
        "preproc_src_meaning": {0: "PS 软件预处理（兜底）", 1: "PL 新块 CSR"}[args.preproc_src],
        "built_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "toolchain": {"gcc": str(GCC), "gcc_version": (gcc_ver.splitlines() or [""])[0].strip(),
                      "size_exit": code_sz, "size_output": size_out.strip()},
        "inputs": {"source": {"path": str(SOURCE.relative_to(W)).replace("\\", "/"), "sha256": sha(SOURCE)},
                   "linker_script": {"path": str(lscript), "sha256": sha(lscript)},
                   "bsp_libxilstandalone_sha256": sha(libdir / "libxilstandalone.a")},
        "commands": {"compile": " ".join([str(GCC), *common, "-c", str(SOURCE)]),
                     "link": " ".join([str(GCC), *common, str(obj), "-o", str(elf)])},
        "outputs": {"elf": {"path": str(EVID / elf.name), "sha256": sha(EVID / elf.name),
                            "size_bytes": (EVID / elf.name).stat().st_size},
                    "map": {"path": str(EVID / mapf.name), "sha256": sha(EVID / mapf.name)}},
        "exit_codes": {"compile": code_c, "link": code_l, "size": code_sz},
        "limitations": ["网络/解码入口为 weak 桩（返回 -1）；完整 Vitis 应用须链接 r13 既有目标文件",
                        "SW 预处理未实现几何 resize/pad（仅 BGR→RGB + INT8 打包最小路径）",
                        "未在板上运行；不属于 G3"],
        "boundary": "离线编译；未接触板卡；ENABLE=0；不构成任何关口通过。",
    }
    (EVID / "build_record.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"elf_sha256": record["outputs"]["elf"]["sha256"],
                      "elf_size": record["outputs"]["elf"]["size_bytes"],
                      "preproc_src": args.preproc_src,
                      "size_output": record["toolchain"]["size_output"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())