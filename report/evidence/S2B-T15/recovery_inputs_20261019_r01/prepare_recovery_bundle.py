"""打包最小R04 PS构建输入并仅从解包内容执行一次离线重建。"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "report/evidence/S2B-T15/recovery_inputs_20261019_r01"
TEMP = ROOT / "tmp/2B/S2B-T15/recovery_inputs_20261019_r01"
STAGE = TEMP / "bundle_source"
EXTRACTED = TEMP / "bundle_extract"
BUILD = TEMP / "fresh_build"
ARTIFACTS = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts"
OLD = ROOT / "tmp/2B/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04"
NINJA = Path(r"D:\Xilinx\2026.1\Vitis\bin\ninja.exe")
BUNDLE = EVIDENCE / "r04_ps_minimal_recovery_bundle.zip"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def write_exclusive(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)


def capture_link_line(app: str) -> dict:
    build = OLD / app / "build"
    command = [str(NINJA), "-C", str(build), "-t", "commands", f"{app}.elf"]
    done = subprocess.run(command, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = EVIDENCE / f"ninja-list-{app}.log"
    write_exclusive(log, done.stdout.encode("utf-8"))
    write_exclusive(log.with_suffix(log.suffix + ".exit_code"), f"{done.returncode}\n".encode("ascii"))
    if done.returncode:
        raise RuntimeError(f"只读列举{app}原始链接命令失败: {done.returncode}")
    candidates = [line for line in done.stdout.splitlines() if f"-o {app}.elf" in line]
    if len(candidates) != 1:
        raise RuntimeError(f"无法唯一定位{app}链接命令: {len(candidates)}")
    return {"generator_line": candidates[0], "source_command_log": log.name, "source_command_exit_code": done.returncode}


def main() -> int:
    if BUNDLE.exists() or STAGE.exists() or EXTRACTED.exists() or BUILD.exists():
        raise FileExistsError("recovery_inputs RunId已存在；拒绝覆盖或重跑")
    if (EVIDENCE / "machine_result.json").exists():
        raise FileExistsError("machine_result.json已存在；拒绝覆盖或重跑")
    STAGE.mkdir(parents=True)
    mapping = {
        "workspace/infer/src/s2b_inference_app.c": ARTIFACTS / "source_snapshot/s2b_inference_app.c",
        "workspace/infer/src/s2a_ps_decode_nms_reference.c": ARTIFACTS / "source_snapshot/s2a_ps_decode_nms_reference.c",
        "workspace/infer/src/s2a_ps_decode_nms_reference.h": ARTIFACTS / "source_snapshot/s2a_ps_decode_nms_reference.h",
        "workspace/infer/src/s2b_inference_platform.h": ARTIFACTS / "s2b_inference_platform.h",
        "workspace/infer/src/lscript.ld": ARTIFACTS / "lscript.ld",
        "workspace/init/src/ps7_init.c": ARTIFACTS / "ps7_init.c",
        "workspace/init/src/ps7_init.h": ARTIFACTS / "ps7_init.h",
        "workspace/init/src/s2b_ps_init.c": ARTIFACTS / "s2b_ps_init.c",
        "workspace/init/src/lscript.ld": ARTIFACTS / "init_lscript.ld",
        "workspace/ps7/export/ps7/sw/cpu0/Xilinx.spec": OLD / "ps7/export/ps7/sw/cpu0/Xilinx.spec",
        "workspace/ps7/export/ps7/sw/cpu0/lib/libxilstandalone.a": ROOT / "report/evidence/S2B-T18/formal_review_20261018_r01/runtime/libxilstandalone.a",
        "workspace/ps7/export/ps7/sw/cpu0/lib/libxil.a": OLD / "ps7/export/ps7/sw/cpu0/lib/libxil.a",
        "workspace/ps7/export/ps7/sw/cpu0/lib/libxiltimer.a": OLD / "ps7/export/ps7/sw/cpu0/lib/libxiltimer.a",
        "commands/app_compile_commands.json": ARTIFACTS / "app_compile_commands.json",
        "commands/init_compile_commands.json": ARTIFACTS / "init_compile_commands.json",
        "provenance/build_details.json": ARTIFACTS / "build_details.json",
        "provenance/delivery_manifest.json": ARTIFACTS / "delivery_manifest.json",
        "reference/infer.elf": ARTIFACTS / "infer.elf",
        "reference/init.elf": ARTIFACTS / "init.elf",
    }
    for relative, source in mapping.items():
        if not source.is_file():
            raise FileNotFoundError(f"必需输入缺失: {source}")
        destination = STAGE / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    runner_source = EVIDENCE / "rebuild_from_bundle.py"
    if not runner_source.is_file():
        raise FileNotFoundError(f"缺少bundle重建脚本: {runner_source}")
    shutil.copyfile(runner_source, STAGE / "rebuild_from_bundle.py")

    old_root = str(OLD)
    link_commands = {app: capture_link_line(app) for app in ("infer", "init")}
    link_payload = {"captured_workspace_root": old_root, **link_commands}
    (STAGE / "commands/link_commands.json").write_text(json.dumps(link_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for relative in ("workspace/infer/src/lscript.ld", "workspace/init/src/lscript.ld", "workspace/ps7/export/ps7/sw/cpu0/Xilinx.spec"):
        payload = (STAGE / relative).read_bytes()
        if payload.startswith(b"\xef\xbb\xbf"):
            raise RuntimeError(f"冻结输入出现意外UTF-8 BOM: {relative}")

    files = []
    for path in sorted(STAGE.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            files.append({"path": path.relative_to(STAGE).as_posix(), "bytes": len(data), "sha256": sha(data), "origin": str(mapping.get(path.relative_to(STAGE).as_posix(), runner_source if path.name == runner_source.name else path))})
    manifest = {
        "schema_version": 1,
        "bundle_id": "r04_ps_minimal_recovery_bundle_20261019_r01",
        "captured_workspace_root": old_root,
        "r04_source_commit": "03faa2d47a6e49d7475e387cf6b33edda4962c68",
        "xsa_sha256": "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6",
        "bit_sha256": "555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7",
        "files": files,
        "external_dependencies": [
            {"path": r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe", "role": "官方ARM GCC及其同安装目录中的libgcc/libc/libm/头文件"},
        ],
        "scope": "PS infer/init ELF离线编译链接输入；不含Vivado平台工程或BSP源码重建材料。",
    }
    (STAGE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with zipfile.ZipFile(BUNDLE, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(STAGE.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(STAGE).as_posix())
    if BUNDLE.stat().st_size > 5 * 1024 * 1024:
        raise RuntimeError(f"恢复输入包超过5MiB预算: {BUNDLE.stat().st_size}")

    EXTRACTED.mkdir()
    with zipfile.ZipFile(BUNDLE, "r") as archive:
        archive.extractall(EXTRACTED)
    archive_sha = file_sha(BUNDLE)
    runner = EXTRACTED / "rebuild_from_bundle.py"
    launch_command = [sys.executable, str(runner), "--build-root", str(BUILD), "--evidence-root", str(EVIDENCE), "--bundle-archive", str(BUNDLE)]
    completed = subprocess.run(launch_command, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    write_exclusive(EVIDENCE / "bundle-runner.stdout.log", completed.stdout.encode("utf-8"))
    write_exclusive(EVIDENCE / "bundle-runner.stdout.log.exit_code", f"{completed.returncode}\n".encode("ascii"))
    record = {
        "schema_version": 1,
        "bundle_path": str(BUNDLE),
        "bundle_bytes": BUNDLE.stat().st_size,
        "bundle_sha256": archive_sha,
        "bundle_manifest_sha256": file_sha(EXTRACTED / "manifest.json"),
        "unpacked_directory": str(EXTRACTED),
        "fresh_build_directory": str(BUILD),
        "runner_command": launch_command,
        "runner_exit_code": completed.returncode,
        "result_path": str(EVIDENCE / "machine_result.json"),
    }
    with (EVIDENCE / "bundle_archive_record.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return completed.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"打包准备失败: {error}", file=sys.stderr)
        raise SystemExit(1)
