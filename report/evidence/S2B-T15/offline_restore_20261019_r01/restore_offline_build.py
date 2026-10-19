"""在隔离副本中按已捕获命令重编译并链接R04的PS应用。"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ARTIFACTS = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts"
OLD_ROOT = ROOT / "tmp/2B/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04"
NEW_ROOT = ROOT / "tmp/2B/S2B-T15/offline_restore_20261019_r01/r04_workspace"
OUT = Path(__file__).resolve().parent
NINJA = Path(r"D:\Xilinx\2026.1\Vitis\bin\ninja.exe")
GCC = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe")
OBJCOPY = GCC.with_name("arm-none-eabi-objcopy.exe")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_logged(command: str, cwd: Path, log_path: Path) -> int:
    started = time.time()
    completed = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log_path.write_text(completed.stdout, encoding="utf-8")
    log_path.with_suffix(log_path.suffix + ".exit_code").write_text(
        f"{completed.returncode}\n", encoding="utf-8"
    )
    return completed.returncode


def main() -> int:
    if (OUT / "machine_result.json").exists():
        raise RuntimeError("目标RunId已有machine_result.json；拒绝覆盖日志或结果")
    result = {
        "schema_version": 1,
        "method": "captured_compile_commands_plus_captured_ninja_link_command",
        "workspace": str(NEW_ROOT),
        "inputs": {},
        "builds": [],
    }
    input_paths = {
        "build_details": ARTIFACTS / "build_details.json",
        "infer_compile_commands": ARTIFACTS / "app_compile_commands.json",
        "init_compile_commands": ARTIFACTS / "init_compile_commands.json",
        "infer_source": NEW_ROOT / "infer/src/s2b_inference_app.c",
        "decoder_source": NEW_ROOT / "infer/src/s2a_ps_decode_nms_reference.c",
        "init_source": NEW_ROOT / "init/src/s2b_ps_init.c",
        "ps7_init_source": NEW_ROOT / "init/src/ps7_init.c",
        "infer_linker_script": NEW_ROOT / "infer/src/lscript.ld",
        "init_linker_script": NEW_ROOT / "init/src/lscript.ld",
        "libxilstandalone": NEW_ROOT / "ps7/export/ps7/sw/cpu0/lib/libxilstandalone.a",
        "libxiltimer": NEW_ROOT / "ps7/export/ps7/sw/cpu0/lib/libxiltimer.a",
        "libxil": NEW_ROOT / "ps7/export/ps7/sw/cpu0/lib/libxil.a",
        "r04_xsa": ROOT / "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa",
        "r04_bit": ROOT / "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit",
        "captured_gcc_version": ARTIFACTS / "gcc_version.log",
    }
    result["inputs"] = {
        name: {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
        for name, path in input_paths.items()
    }
    version = subprocess.run(
        [str(GCC), "--version"], text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    result["compiler"] = {"path": str(GCC), "exit_code": version.returncode, "version": version.stdout.splitlines()[0]}
    old_win = str(OLD_ROOT)
    old_posix = old_win.replace("\\", "/")
    new_posix = str(NEW_ROOT).replace("\\", "/")

    for app in ("infer", "init"):
        compile_name = "app_compile_commands.json" if app == "infer" else "init_compile_commands.json"
        compile_db = ARTIFACTS / compile_name
        entries = json.loads(compile_db.read_text(encoding="utf-8"))
        build_dir = NEW_ROOT / app / "build"
        entry_results = []
        for index, entry in enumerate(entries):
            command = entry["command"].replace(old_win, str(NEW_ROOT)).replace(
                old_posix, new_posix
            )
            if old_win in command or old_posix in command:
                raise RuntimeError(f"未改写的旧工作树路径: {app} compile command {index}")
            log = OUT / f"{app}-compile-{index:02d}.log"
            code = run_logged(command, build_dir, log)
            entry_results.append({"command": command, "exit_code": code, "log": log.name})
            if code:
                result["builds"].append({"app": app, "compile": entry_results, "exit_code": code})
                (OUT / "machine_result.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                return code

        listing = subprocess.run(
            [str(NINJA), "-C", str(build_dir), "-t", "commands", f"{app}.elf"],
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        (OUT / f"{app}-captured_commands.log").write_text(listing.stdout, encoding="utf-8")
        if listing.returncode:
            raise RuntimeError(f"ninja -t commands失败: {app}: {listing.returncode}")
        link_lines = [line for line in listing.stdout.splitlines() if f"-o {app}.elf" in line]
        if len(link_lines) != 1:
            raise RuntimeError(f"无法唯一定位{app}链接命令: {len(link_lines)}")
        line = link_lines[0]
        gcc = r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe"
        start = line.find(gcc)
        end = line.find(r" && C:\WINDOWS\system32\cmd.exe /C", start)
        if start < 0 or end < 0:
            raise RuntimeError(f"无法提取{app}捕获链接命令的GCC主体")
        link_command = line[start:end]
        if old_win in link_command or old_posix in link_command:
            raise RuntimeError(f"链接命令仍引用旧工作树: {app}")
        link_log = OUT / f"{app}-link.log"
        link_code = run_logged(link_command, build_dir, link_log)
        elf = build_dir / f"{app}.elf"
        build_result = {
            "app": app,
            "compile": entry_results,
            "link_command": link_command,
            "link_exit_code": link_code,
            "link_log": link_log.name,
            "elf_exists": elf.is_file(),
        }
        if elf.is_file():
            build_result["elf_bytes"] = elf.stat().st_size
            build_result["elf_sha256"] = sha256(elf)
            original = ARTIFACTS / f"{app}.elf"
            build_result["original_elf_sha256"] = sha256(original)
            build_result["byte_identical_to_original"] = (
                build_result["elf_sha256"] == build_result["original_elf_sha256"]
            )
            stripped = NEW_ROOT / f"{app}-rebuilt-stripped.elf"
            original_stripped = NEW_ROOT / f"{app}-original-stripped.elf"
            rebuilt_load = NEW_ROOT / f"{app}-rebuilt-load.bin"
            original_load = NEW_ROOT / f"{app}-original-load.bin"
            strip_results = []
            for source, destination in ((elf, stripped), (original, original_stripped)):
                completed = subprocess.run(
                    [str(OBJCOPY), "--strip-debug", str(source), str(destination)],
                    text=True, encoding="utf-8", errors="replace",
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                )
                strip_results.append({"command": [str(OBJCOPY), "--strip-debug", str(source), str(destination)], "exit_code": completed.returncode, "output": completed.stdout})
            build_result["strip_debug"] = strip_results
            if all(item["exit_code"] == 0 for item in strip_results):
                build_result["rebuilt_stripped_sha256"] = sha256(stripped)
                build_result["original_stripped_sha256"] = sha256(original_stripped)
                build_result["stripped_byte_identical"] = (
                    build_result["rebuilt_stripped_sha256"] == build_result["original_stripped_sha256"]
                )
                stripped.unlink()
                original_stripped.unlink()
            load_results = []
            for source, destination in ((elf, rebuilt_load), (original, original_load)):
                completed = subprocess.run(
                    [str(OBJCOPY), "-O", "binary", str(source), str(destination)],
                    text=True, encoding="utf-8", errors="replace",
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                )
                load_results.append({"command": [str(OBJCOPY), "-O", "binary", str(source), str(destination)], "exit_code": completed.returncode, "output": completed.stdout})
            build_result["load_image_export"] = load_results
            if all(item["exit_code"] == 0 for item in load_results):
                build_result["rebuilt_load_image_bytes"] = rebuilt_load.stat().st_size
                build_result["original_load_image_bytes"] = original_load.stat().st_size
                build_result["rebuilt_load_image_sha256"] = sha256(rebuilt_load)
                build_result["original_load_image_sha256"] = sha256(original_load)
                build_result["load_image_byte_identical"] = (
                    build_result["rebuilt_load_image_sha256"] == build_result["original_load_image_sha256"]
                )
                rebuilt_load.unlink()
                original_load.unlink()
        result["builds"].append(build_result)
        if link_code or not elf.is_file():
            result["exit_code"] = link_code or 1
            (OUT / "machine_result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            return result["exit_code"]

    result["exit_code"] = 0
    result["limitations"] = [
        "只重编译和链接infer/init PS ELF；未重建BSP SDK、PL综合实现或bitstream。",
        "链接使用已存在的R04 BSP静态库和工具链运行库，不证明其可从独立Git仓库恢复。",
        "字节一致只说明ELF文件完全相同，不替代板上执行或完整PL恢复验证。",
    ]
    (OUT / "machine_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
