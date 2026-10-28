"""构建阶段4 PS 应用（v2：链接 r13 冻结解码参考，去掉 weak 桩）。S4-T34。

与 v1 的差别：
  · 额外编译 `verification/s2a_ps_decode_nms_reference.c`，使 `s2a_t62_decode_nms` 以**强符号**进入 ELF；
  · `s4d_ps_app.c` 内已把 `s2a_decode_nms_reference` / `s2b_network_start_from_tensor` 的 weak 桩
    替换为强实现（解码直调 r13 冻结参考；网络启动按 2B CSR 冻结语义）；
  · 一次构建 **PREPROC_SRC=0（SW）与 =1（PL）两变体**，各自产出 ELF/map/build_record；
  · 用 `arm-none-eabi-nm` 断言 `s2a_t62_decode_nms` 为 **T（强符号）**，不是 W/weak；
  · 证据落 `report/evidence/S4-T34/ps_decode_link_20261028_r01/`。

退出码：0=两变体均构建且 nm 断言通过；1=编译/链接失败；2=依赖缺失；3=nm 断言失败。
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
REF_C = W / "verification" / "s2a_ps_decode_nms_reference.c"
REF_H = W / "verification" / "s2a_ps_decode_nms_reference.h"
BUNDLE = W / "tmp" / "4" / "S4-B-REAL-01" / "s4b_ps_tensor_20261023_r13" / "bundle_extract" / "bundle" / "workspace"
BUILD = W / "tmp" / "4" / "S4-T34" / "ps_app_build"
EVID = W / "report" / "evidence" / "S4-T34" / "ps_decode_link_20261028_r01"
GCC = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe")
SIZE = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-size.exe")
NM = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-nm.exe")
STRONG_SYMBOL = "s2a_t62_decode_nms"


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
    """构建两变体并记录证据。"""
    ap = argparse.ArgumentParser()
    ap.add_argument("--define", action="append", default=[])
    args = ap.parse_args()
    for p in (SOURCE, REF_C, REF_H, GCC, SIZE, NM):
        if not p.exists():
            print(f"[FAIL] 依赖缺失：{p}")
            return 2
    include = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0" / "include"
    libdir = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0" / "lib"
    spec = BUNDLE / "ps7" / "export" / "ps7" / "sw" / "cpu0" / "Xilinx.spec"
    lscript_src = BUNDLE / "infer" / "src" / "lscript.ld"   # r13 infer 工程脚本（DDR 区，容纳解码 double 缓冲）
    for p in (include, libdir, spec, lscript_src):
        if not p.exists():
            print(f"[FAIL] BSP 依赖缺失：{p}")
            return 2
    BUILD.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    # 构建专用链接脚本副本：去掉 r13 专属的 arena 尺寸断言，保留 app budget 断言
    lscript = BUILD / "lscript_s4t34.ld"
    kept = []
    for line in lscript_src.read_text(encoding="utf-8").splitlines():
        if "arena address" in line or "arena LMA" in line or "arena size" in line:
            kept.append("/* 构建副本：r13 arena 专属断言已移除（本应用不声明 32MiB arena） */")
            continue
        kept.append(line)
    lscript.write_text("\n".join(kept) + "\n", encoding="utf-8", newline="\n")
    log = BUILD / "build_v2.log"
    if log.exists():
        log.unlink()

    results = {}
    for variant, meaning in ((0, "PS 软件预处理（兜底）"), (1, "PL 新块 CSR")):
        tag = f"sw{variant}" if variant == 0 else "pl"
        common = ["-DSDT", f"-DPREPROC_SRC={variant}"] + [f"-D{d}" for d in args.define] + [
            "-mcpu=cortex-a9", "-mfpu=vfpv3", "-mfloat-abi=hard", "-MMD", "-MP",
            f"-specs={spec.as_posix()}", f"-I{include.as_posix()}",
            f"-I{(W / 'verification').as_posix()}", f"-I{(W / 'vitis' / 'stage4' / 'ps').as_posix()}",
            "-Wall", "-Wextra", "-O2", "-g3", "-std=gnu11",
            "-ffunction-sections", "-fdata-sections", "-U__clang__"]
        obj = BUILD / f"s4d_ps_app_{tag}.o"
        ref_obj = BUILD / "s2a_ps_decode_nms_reference.o"
        elf = BUILD / f"s4d_ps_app_{tag}.elf"
        mapf = BUILD / f"s4d_ps_app_{tag}.map"
        code_c, _ = run([str(GCC), *common, "-o", str(obj), "-c", str(SOURCE)], BUILD, log)
        code_r, _ = run([str(GCC), *common, "-o", str(ref_obj), "-c", str(REF_C)], BUILD, log)
        if code_c != 0 or code_r != 0:
            print(f"[FAIL] 编译失败 variant={variant} app={code_c} ref={code_r}；日志 {log}")
            return 1
        code_l, _ = run([str(GCC), *common, f"-Wl,-Map={mapf.as_posix()},--cref,--gc-sections",
                         str(obj), str(ref_obj), "-o", str(elf), f"-L{libdir.as_posix()}",
                         "-Wl,-T", f"-Wl,{lscript.as_posix()}",
                         "-Wl,--start-group", "-lxilstandalone", "-lxiltimer", "-lxil",
                         "-lgcc", "-lc", "-lm", "-Wl,--end-group"], BUILD, log)
        if code_l != 0:
            print(f"[FAIL] 链接失败 variant={variant} exit={code_l}；日志 {log}")
            return 1
        code_sz, size_out = run([str(SIZE), "--format=berkeley", str(elf)], BUILD, log)
        code_nm, nm_out = run([str(NM), "-C", str(elf)], BUILD, log)
        hit = [ln for ln in nm_out.splitlines() if ln.strip().endswith(STRONG_SYMBOL)]
        strong = bool(hit) and hit[0].split()[1] == "T"
        nm_summary = {
            "exit": code_nm,
            "symbol": STRONG_SYMBOL,
            "lines": hit,
            "is_strong_T": strong,
            "weak_W_present": any(ln.split()[1] == "W" for ln in hit),
        }
        if not strong:
            print(f"[FAIL] nm 断言失败 variant={variant}：{nm_summary}")
            return 3
        for a in (elf, mapf):
            shutil.copy2(a, EVID / a.name)
        record = {
            "task_id": "S4-T34",
            "phase": "PS 应用真实解码接线（v2）",
            "purpose": "去掉 weak 桩：s2a_decode_nms_reference 直调 r13 冻结参考；s2b_network_start_from_tensor 按 2B CSR 冻结语义实现",
            "variant": "sw" if variant == 0 else "pl",
            "preproc_src": variant,
            "preproc_src_meaning": meaning,
            "built_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
            "toolchain": {"gcc": str(GCC), "gcc_version": "arm-none-eabi (GCC)",
                          "size_exit": code_sz, "size_output": size_out.strip()},
            "inputs": {
                "source": {"path": str(SOURCE.relative_to(W)).replace("\\", "/"), "sha256": sha(SOURCE)},
                "decode_reference_c": {"path": str(REF_C.relative_to(W)).replace("\\", "/"), "sha256": sha(REF_C)},
                "decode_reference_h": {"path": str(REF_H.relative_to(W)).replace("\\", "/"), "sha256": sha(REF_H)},
                "linker_script": {"path": str(lscript), "sha256": sha(lscript)},
            },
            "nm": nm_summary,
            "outputs": {
                "elf": {"path": str(EVID / elf.name), "sha256": sha(EVID / elf.name),
                        "size_bytes": (EVID / elf.name).stat().st_size},
                "map": {"path": str(EVID / mapf.name), "sha256": sha(EVID / mapf.name)},
            },
            "exit_codes": {"compile_app": code_c, "compile_ref": code_r, "link": code_l,
                           "size": code_sz, "nm": code_nm},
            "limitations": [
                "网络启动强实现按冻结 CSR 语义编写，**未上板**验证（板卡归阶段5）",
                "SW 预处理仍未实现几何 resize/pad（仅 BGR→RGB + INT8 打包最小路径）",
                "解码输入取自 arena 固定偏移（head13 0x01A46100 / head26 0x01AD5E80，非连续）",
                "链接脚本沿用 r13 infer 工程（text/data/bss 位于 DDR 0x00100000 起）；权重区 0x00100000 与代码的相对布局须在 bring-up 窗口核对（离线不判）",
                "未在板上运行；不属于 G3",
            ],
            "boundary": "离线编译；未接触板卡；ENABLE=0；不构成任何关口通过。",
        }
        (EVID / f"build_record_{record['variant']}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        results[record["variant"]] = {
            "elf_sha256": record["outputs"]["elf"]["sha256"],
            "elf_size": record["outputs"]["elf"]["size_bytes"],
            "map_sha256": record["outputs"]["map"]["sha256"],
            "nm_T": strong,
            "size": record["toolchain"]["size_output"],
        }
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())