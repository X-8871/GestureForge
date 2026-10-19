"""逐项比较原R04与隔离重建ELF的装载布局和数据。"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "verification"))
from check_s2b_ps_smoke_layout import parse_elf


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def first_difference(left: bytes, right: bytes) -> dict[str, int] | None:
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return {"offset": index, "original_byte": a, "rebuilt_byte": b}
    if len(left) != len(right):
        return {"offset": min(len(left), len(right)), "original_size": len(left), "rebuilt_size": len(right)}
    return None


def compare(app: str) -> dict:
    original_path = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts" / f"{app}.elf"
    rebuilt_path = ROOT / "tmp/2B/S2B-T15/offline_restore_20261019_r01/r04_workspace" / app / "build" / f"{app}.elf"
    original = original_path.read_bytes()
    rebuilt = rebuilt_path.read_bytes()
    left = parse_elf(original)
    right = parse_elf(rebuilt)

    segment_rows = []
    load_left = [item for item in left["programs"] if item["type"] == 1]
    load_right = [item for item in right["programs"] if item["type"] == 1]
    fields = ("physical", "virtual", "file_size", "memory_size", "flags", "align")
    for index in range(max(len(load_left), len(load_right))):
        if index >= len(load_left) or index >= len(load_right):
            segment_rows.append({"index": index, "present_original": index < len(load_left), "present_rebuilt": index < len(load_right), "equal": False})
            continue
        a = load_left[index]
        b = load_right[index]
        a_data = original[a["offset"]:a["offset"] + a["file_size"]]
        b_data = rebuilt[b["offset"]:b["offset"] + b["file_size"]]
        layout = {field: {"original": a[field], "rebuilt": b[field], "equal": a[field] == b[field]} for field in fields}
        segment_rows.append({
            "index": index,
            "layout": layout,
            "payload_bytes_original": len(a_data),
            "payload_bytes_rebuilt": len(b_data),
            "payload_sha256_original": digest(a_data),
            "payload_sha256_rebuilt": digest(b_data),
            "payload_equal": a_data == b_data,
            "first_difference": first_difference(a_data, b_data),
        })

    def alloc_exec(blob: bytes, model: dict) -> list[dict]:
        result = []
        for section in model["sections"]:
            if section["flags"] & 0x6 != 0x6:
                continue
            begin = section["offset"]
            data = blob[begin:begin + section["size"]]
            result.append({"name": section["name"], "address": section["address"], "size": section["size"], "type": section["type"], "flags": section["flags"], "offset": section["offset"], "sha256": digest(data), "data": data})
        return result

    section_left = alloc_exec(original, left)
    section_right = alloc_exec(rebuilt, right)
    section_comparison = []
    by_name_right = {item["name"]: item for item in section_right}
    for a in section_left:
        b = by_name_right.get(a["name"])
        if b is None:
            section_comparison.append({"name": a["name"], "present_original": True, "present_rebuilt": False, "equal": False})
        else:
            section_comparison.append({
                "name": a["name"],
                "metadata_equal": all(a[key] == b[key] for key in ("address", "size", "type", "flags")),
                "sha256_original": a["sha256"],
                "sha256_rebuilt": b["sha256"],
                "data_equal": a["data"] == b["data"],
                "first_difference": first_difference(a["data"], b["data"]),
            })
    for b in section_right:
        if b["name"] not in {item["name"] for item in section_left}:
            section_comparison.append({"name": b["name"], "present_original": False, "present_rebuilt": True, "equal": False})

    executable_indices_left = {item["index"] for item in left["sections"] if item["flags"] & 0x6 == 0x6}
    executable_indices_right = {item["index"] for item in right["sections"] if item["flags"] & 0x6 == 0x6}
    symbols_left = {item["name"]: item for item in left["symbols"] if item["section"] in executable_indices_left}
    symbols_right = {item["name"]: item for item in right["symbols"] if item["section"] in executable_indices_right}
    symbol_diff = []
    for name in sorted(set(symbols_left) | set(symbols_right)):
        a, b = symbols_left.get(name), symbols_right.get(name)
        if a != b:
            symbol_diff.append({"name": name, "original": a, "rebuilt": b})

    return {
        "app": app,
        "original": {"path": str(original_path), "bytes": len(original), "sha256": digest(original), "entry": left["entry"], "flags": left["flags"]},
        "rebuilt": {"path": str(rebuilt_path), "bytes": len(rebuilt), "sha256": digest(rebuilt), "entry": right["entry"], "flags": right["flags"]},
        "entry_equal": left["entry"] == right["entry"],
        "elf_flags_equal": left["flags"] == right["flags"],
        "load_segment_count_original": len(load_left),
        "load_segment_count_rebuilt": len(load_right),
        "load_segments": segment_rows,
        "all_load_layout_fields_equal": len(load_left) == len(load_right) and all(all(item.get("layout", {}).get(field, {}).get("equal", False) for field in fields) for item in segment_rows),
        "all_load_payloads_equal": len(load_left) == len(load_right) and all(item.get("payload_equal", False) for item in segment_rows),
        "alloc_executable_sections": [{key: value for key, value in item.items() if key != "data"} for item in section_comparison],
        "all_alloc_executable_section_data_equal": bool(section_comparison) and all(item.get("equal", item.get("metadata_equal", False) and item.get("data_equal", False)) for item in section_comparison),
        "executable_symbol_differences": symbol_diff,
        "executable_symbol_sets_equal": not symbol_diff,
    }


def main() -> None:
    result_path = OUT / "comparison.json"
    result = {
        "schema_version": 1,
        "comparison_tool": "verification/check_s2b_ps_smoke_layout.py:parse_elf",
        "comparison_scope": "ELF headers, PT_LOAD addresses/size/flags/alignment/payload SHA256, SHF_ALLOC|SHF_EXECINSTR section data and executable symbols",
        "apps": [compare("infer"), compare("init")],
        "limitations": [
            "本比较只判断PS ELF的静态装载布局和静态内容；不执行CPU，不证明板上行为。",
            "PT_LOAD的memory_size超出file_size部分为零初始化区，不存在文件负载字节可供哈希；只比较长度与地址属性。",
            "ELF字节差异若仅位于调试、符号或非装载元数据，不推断其功能影响；必须结合上述逐段结果解释。",
        ],
    }
    with result_path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
