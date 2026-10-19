"""核验R04装载段在剔除GNU build-id数据后的逐字节等同性。"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "verification"))
from check_s2b_ps_smoke_layout import parse_elf

NOTE_HEADER = struct.pack("<III", 4, 20, 3) + b"GNU\0"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    result = {
        "schema_version": 1,
        "normalization": "仅将已确认GNU build-id note的20字节描述字段置零；不改ELF输入文件。",
        "apps": [],
        "limitations": [
            "结果只证明静态ELF装载字节及布局在去掉GNU build-id标识后相同，不替代板上执行。",
            "平台、BSP归档及工具链仍是现有磁盘输入；未验证Git单独恢复完整软件平台或PL。",
        ],
    }
    for app in ("infer", "init"):
        original_path = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts" / f"{app}.elf"
        rebuilt_path = ROOT / "tmp/2B/S2B-T15/offline_restore_20261019_r01/r04_workspace" / app / "build" / f"{app}.elf"
        original = original_path.read_bytes()
        rebuilt = rebuilt_path.read_bytes()
        left = parse_elf(original)
        right = parse_elf(rebuilt)
        normalized_sections = []
        note_descriptions = []
        for model, blob, label in ((left, original, "original"), (right, rebuilt, "rebuilt")):
            by_name = {item["name"]: item for item in model["sections"]}
            if app == "init":
                section = by_name[".note.gnu.build-id"]
                start = section["offset"]
                note = blob[start:start + section["size"]]
                if note[:16] != NOTE_HEADER or len(note) != 36:
                    raise RuntimeError(f"{app} {label}: build-id note结构与GNU ELF note不符")
                note_descriptions.append({"section": section["name"], "file_offset": start + 16, "sha256": sha(note[16:]), "hex": note[16:].hex()})
            else:
                section = by_name[".text"]
                start = section["offset"]
                data = blob[start:start + section["size"]]
                note = data[-36:]
                if note[:16] != NOTE_HEADER:
                    raise RuntimeError(f"{app} {label}: .text尾部未发现GNU build-id note")
                note_descriptions.append({"section": section["name"], "file_offset": start + section["size"] - 20, "sha256": sha(note[16:]), "hex": note[16:].hex()})
        for a, b in zip(left["programs"], right["programs"]):
            if a["type"] != 1 or b["type"] != 1:
                continue
            a_data = bytearray(original[a["offset"]:a["offset"] + a["file_size"]])
            b_data = bytearray(rebuilt[b["offset"]:b["offset"] + b["file_size"]])
            a_file_note = note_descriptions[0]["file_offset"]
            b_file_note = note_descriptions[1]["file_offset"]
            a_segment_offset = a_file_note - a["offset"]
            b_segment_offset = b_file_note - b["offset"]
            if 0 <= a_segment_offset and a_segment_offset + 20 <= len(a_data):
                a_data[a_segment_offset:a_segment_offset + 20] = bytes(20)
            if 0 <= b_segment_offset and b_segment_offset + 20 <= len(b_data):
                b_data[b_segment_offset:b_segment_offset + 20] = bytes(20)
            normalized_sections.append({
                "program_index": len(normalized_sections),
                "physical_original": a["physical"], "physical_rebuilt": b["physical"],
                "virtual_original": a["virtual"], "virtual_rebuilt": b["virtual"],
                "file_size_original": a["file_size"], "file_size_rebuilt": b["file_size"],
                "memory_size_original": a["memory_size"], "memory_size_rebuilt": b["memory_size"],
                "flags_original": a["flags"], "flags_rebuilt": b["flags"],
                "align_original": a["align"], "align_rebuilt": b["align"],
                "normalized_payload_sha256_original": sha(a_data),
                "normalized_payload_sha256_rebuilt": sha(b_data),
                "normalized_payload_identical": a_data == b_data,
            })
        symbols_left = sorted((item["name"], item["value"], item["size"], item["section"]) for item in left["symbols"])
        symbols_right = sorted((item["name"], item["value"], item["size"], item["section"]) for item in right["symbols"])
        result["apps"].append({
            "app": app,
            "original_elf_sha256": sha(original), "rebuilt_elf_sha256": sha(rebuilt),
            "entry_original": left["entry"], "entry_rebuilt": right["entry"],
            "entry_identical": left["entry"] == right["entry"],
            "all_symbols_identical": symbols_left == symbols_right,
            "build_id_notes": note_descriptions,
            "load_segments": normalized_sections,
            "all_load_bytes_identical_after_build_id_normalization": all(item["normalized_payload_identical"] for item in normalized_sections),
        })
    path = OUT / "comparison_buildid_normalized.json"
    with path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
