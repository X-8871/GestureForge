"""验证输入包并在新目录直接编译、链接R04的infer/init应用。"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path


GCC = r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe"
NOTE_HEADER = struct.pack("<III", 4, 20, 3) + b"GNU\0"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes())


def dump_json_exclusive(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def run(command: str, cwd: Path, log_path: Path) -> int:
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
    with log_path.open("x", encoding="utf-8") as stream:
        stream.write(completed.stdout)
    with log_path.with_suffix(log_path.suffix + ".exit_code").open("x", encoding="ascii") as stream:
        stream.write(f"{completed.returncode}\n")
    return completed.returncode


def replace_workspace(command: str, old_root: str, bundle_workspace: Path) -> str:
    new_windows = str(bundle_workspace)
    new_posix = new_windows.replace("\\", "/")
    command = command.replace(old_root, new_windows)
    command = command.replace(old_root.replace("\\", "/"), new_posix)
    if old_root in command or old_root.replace("\\", "/") in command:
        raise RuntimeError("编译/链接命令仍引用旧tmp工作区")
    return command


def extract_gcc_link(generator_line: str) -> str:
    start = generator_line.find(GCC)
    end = generator_line.find(r" && C:\WINDOWS\system32\cmd.exe /C", start)
    if start < 0 or end < 0:
        raise RuntimeError("无法从捕获的Ninja链接命令中提取GCC主体")
    return generator_line[start:end]


def parse_elf(data: bytes) -> dict:
    if len(data) < 52 or data[:7] != b"\x7fELF\x01\x01\x01":
        raise ValueError("ELF必须为32位小端格式")
    fields = struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
    kind, machine, version, entry, phoff, shoff, flags, ehsize, phsize, phnum, shsize, shnum, shstr = fields
    if (kind, machine, version, ehsize, phsize, shsize) != (2, 40, 1, 52, 32, 40):
        raise ValueError("ELF类型/架构/表项大小不符合ARM32要求")
    if phoff + phnum * phsize > len(data) or shoff + shnum * shsize > len(data):
        raise ValueError("ELF表被截断")
    section_rows = [struct.unpack_from("<IIIIIIIIII", data, shoff + index * shsize) for index in range(shnum)]
    name_table_row = section_rows[shstr]
    names = data[name_table_row[4]:name_table_row[4] + name_table_row[5]]
    sections = []
    for index, row in enumerate(section_rows):
        end = names.find(b"\0", row[0])
        if end < 0:
            raise ValueError("ELF节名字符串无终止符")
        sections.append({"index": index, "name": names[row[0]:end].decode("ascii"), "type": row[1], "flags": row[2], "address": row[3], "offset": row[4], "size": row[5]})
    programs = []
    for index in range(phnum):
        row = struct.unpack_from("<IIIIIIII", data, phoff + index * phsize)
        if row[1] + row[4] > len(data) or row[4] > row[5]:
            raise ValueError("ELF程序段范围无效")
        programs.append({"index": index, "type": row[0], "offset": row[1], "virtual": row[2], "physical": row[3], "file_size": row[4], "memory_size": row[5], "flags": row[6], "align": row[7]})
    return {"entry": entry, "flags": flags, "sections": sections, "programs": programs}


def build_id_file_offset(data: bytes, parsed: dict, app: str) -> int:
    if app == "init":
        section = next(item for item in parsed["sections"] if item["name"] == ".note.gnu.build-id")
        note_start = section["offset"]
        note = data[note_start:note_start + section["size"]]
        if len(note) != 36 or note[:16] != NOTE_HEADER:
            raise ValueError("init ELF GNU build-id note结构不符")
        return note_start + 16
    section = next(item for item in parsed["sections"] if item["name"] == ".text")
    note_start = section["offset"] + section["size"] - 36
    note = data[note_start:note_start + 36]
    if len(note) != 36 or note[:16] != NOTE_HEADER:
        raise ValueError("infer ELF .text尾部GNU build-id note结构不符")
    return note_start + 16


def differing_ranges(left: bytes, right: bytes) -> list[dict]:
    changes = []
    length = min(len(left), len(right))
    index = 0
    while index < length:
        if left[index] == right[index]:
            index += 1
            continue
        start = index
        while index < length and left[index] != right[index]:
            index += 1
        changes.append({"offset": start, "length": index - start, "original_first": left[start], "rebuilt_first": right[start]})
    if len(left) != len(right):
        changes.append({"offset": length, "original_size": len(left), "rebuilt_size": len(right)})
    return changes


def compare_loads(original_path: Path, rebuilt_path: Path, app: str) -> dict:
    original = original_path.read_bytes()
    rebuilt = rebuilt_path.read_bytes()
    left = parse_elf(original)
    right = parse_elf(rebuilt)
    left_note = build_id_file_offset(original, left, app)
    right_note = build_id_file_offset(rebuilt, right, app)
    load_left = [item for item in left["programs"] if item["type"] == 1]
    load_right = [item for item in right["programs"] if item["type"] == 1]
    segments = []
    keys = ("physical", "virtual", "file_size", "memory_size", "flags", "align")
    layout_equal = len(load_left) == len(load_right)
    normalized_equal = layout_equal
    note_only = layout_equal
    for index, (a, b) in enumerate(zip(load_left, load_right)):
        fields = {key: {"original": a[key], "rebuilt": b[key], "equal": a[key] == b[key]} for key in keys}
        layout_equal = layout_equal and all(value["equal"] for value in fields.values())
        a_data = bytearray(original[a["offset"]:a["offset"] + a["file_size"]])
        b_data = bytearray(rebuilt[b["offset"]:b["offset"] + b["file_size"]])
        raw_diff = differing_ranges(a_data, b_data)
        a_note_rel = left_note - a["offset"]
        b_note_rel = right_note - b["offset"]
        a_has_note = 0 <= a_note_rel and a_note_rel + 20 <= len(a_data)
        b_has_note = 0 <= b_note_rel and b_note_rel + 20 <= len(b_data)
        if a_has_note != b_has_note:
            note_only = False
        if a_has_note:
            a_data[a_note_rel:a_note_rel + 20] = bytes(20)
        if b_has_note:
            b_data[b_note_rel:b_note_rel + 20] = bytes(20)
        normalized_diff = differing_ranges(a_data, b_data)
        only_note = all(item["offset"] >= a_note_rel and item["offset"] + item["length"] <= a_note_rel + 20 for item in raw_diff) if a_has_note else not raw_diff
        note_only = note_only and only_note
        normalized_equal = normalized_equal and not normalized_diff
        segments.append({
            "index": index,
            "layout": fields,
            "payload_sha256_original": sha256(original[a["offset"]:a["offset"] + a["file_size"]]),
            "payload_sha256_rebuilt": sha256(rebuilt[b["offset"]:b["offset"] + b["file_size"]]),
            "raw_difference_ranges": raw_diff,
            "all_raw_differences_inside_build_id": only_note,
            "normalized_payload_sha256_original": sha256(a_data),
            "normalized_payload_sha256_rebuilt": sha256(b_data),
            "normalized_payload_equal": not normalized_diff,
            "normalized_difference_ranges": normalized_diff,
        })
    return {
        "original": {"path": str(original_path), "bytes": len(original), "sha256": sha256(original), "entry": left["entry"]},
        "rebuilt": {"path": str(rebuilt_path), "bytes": len(rebuilt), "sha256": sha256(rebuilt), "entry": right["entry"]},
        "entry_equal": left["entry"] == right["entry"],
        "build_id_original_hex": original[left_note:left_note + 20].hex(),
        "build_id_rebuilt_hex": rebuilt[right_note:right_note + 20].hex(),
        "pt_load_layout_equal": layout_equal,
        "raw_differences_confined_to_build_id": note_only,
        "pt_load_equal_after_exact_build_id_normalization": normalized_equal,
        "segments": segments,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-root", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--bundle-archive", required=True, type=Path)
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    manifest_path = bundle / "manifest.json"
    result_path = args.evidence_root / "machine_result.json"
    if args.build_root.exists() or result_path.exists():
        raise FileExistsError("指定RunId或結果已存在；拒絕覆寫")
    log_names = [f"{app}-{kind}-{index:02d}.log" for app in ("infer", "init") for kind, count in (("compile", 2),) for index in range(count)] + [f"{app}-link.log" for app in ("infer", "init")]
    if any((args.evidence_root / name).exists() for name in log_names):
        raise FileExistsError("已有同名命令日志；拒绝覆盖")
    args.evidence_root.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = bundle / item["path"]
        if not path.is_file() or path.stat().st_size != item["bytes"] or file_sha(path) != item["sha256"]:
            raise ValueError(f"输入包文件校验失败: {item['path']}")
    old_root = manifest["captured_workspace_root"]
    workspace = bundle / "workspace"
    args.build_root.mkdir(parents=True)
    result = {
        "schema_version": 1,
        "status": "BUILDING",
        "hardware_execution": "NOT_RUN",
        "bundle_archive": {"path": str(args.bundle_archive), "bytes": args.bundle_archive.stat().st_size, "sha256": file_sha(args.bundle_archive)},
        "bundle_manifest_sha256": file_sha(manifest_path),
        "compiler_path": GCC,
        "compiler_version": "",
        "inputs": manifest["files"],
        "commands": [],
        "outputs": [],
        "limitations": [
            "使用包内既有R04 BSP静态库和工具链安装目录；不重建BSP SDK。",
            "不重建PL/XSA/bitstream，不执行板上或冷启动恢复。",
        ],
    }
    version = subprocess.run([GCC, "--version"], text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result["compiler_version"] = version.stdout.splitlines()[0] if version.stdout else ""
    (args.evidence_root / "gcc-version.log").write_text(version.stdout, encoding="utf-8")
    if version.returncode:
        result["status"] = "COMPILER_VERSION_FAILED"
        result["exit_code"] = version.returncode
        dump_json_exclusive(result_path, result)
        return version.returncode
    commands = json.loads((bundle / "commands/link_commands.json").read_text(encoding="utf-8"))
    for app in ("infer", "init"):
        build_dir = args.build_root / app / "build"
        build_dir.mkdir(parents=True)
        compile_db_name = "app_compile_commands.json" if app == "infer" else "init_compile_commands.json"
        compile_db = json.loads((bundle / "commands" / compile_db_name).read_text(encoding="utf-8"))
        (build_dir / "CMakeFiles" / f"{app}.elf.dir").mkdir(parents=True)
        for index, item in enumerate(compile_db):
            command = replace_workspace(item["command"], old_root, workspace)
            log_path = args.evidence_root / f"{app}-compile-{index:02d}.log"
            code = run(command, build_dir, log_path)
            result["commands"].append({"app": app, "kind": "compile", "index": index, "command": command, "exit_code": code, "log": log_path.name})
            if code:
                result["status"] = "COMPILE_FAILED"
                result["exit_code"] = code
                dump_json_exclusive(result_path, result)
                return code
        generator_line = commands[app]["generator_line"]
        link_command = replace_workspace(extract_gcc_link(generator_line), old_root, workspace)
        log_path = args.evidence_root / f"{app}-link.log"
        code = run(link_command, build_dir, log_path)
        result["commands"].append({"app": app, "kind": "link", "command": link_command, "exit_code": code, "log": log_path.name})
        elf = build_dir / f"{app}.elf"
        result["outputs"].append({"app": app, "path": str(elf), "exists": elf.is_file(), "bytes": elf.stat().st_size if elf.is_file() else None, "sha256": file_sha(elf) if elf.is_file() else None})
        if code or not elf.is_file():
            result["status"] = "LINK_FAILED"
            result["exit_code"] = code or 1
            dump_json_exclusive(result_path, result)
            return result["exit_code"]
    comparisons = []
    for app in ("infer", "init"):
        reference = bundle / "reference" / f"{app}.elf"
        rebuilt = args.build_root / app / "build" / f"{app}.elf"
        comparisons.append({"app": app, **compare_loads(reference, rebuilt, app)})
    result["comparisons"] = comparisons
    equal = all(item["entry_equal"] and item["pt_load_layout_equal"] and item["raw_differences_confined_to_build_id"] and item["pt_load_equal_after_exact_build_id_normalization"] for item in comparisons)
    result["status"] = "PASS_PT_LOAD_EQUAL_AFTER_BUILD_ID_ONLY" if equal else "BUILT_WITH_PT_LOAD_DIFFERENCE"
    result["exit_code"] = 0
    dump_json_exclusive(result_path, result)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"恢复构建失败: {error}", file=sys.stderr)
        raise SystemExit(1)
