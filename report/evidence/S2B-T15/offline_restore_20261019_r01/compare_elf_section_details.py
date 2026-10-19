"""定位R04原ELF与隔离重建ELF的可装载节逐字节差异。"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "verification"))
from check_s2b_ps_smoke_layout import parse_elf


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def diff_ranges(left: bytes, right: bytes) -> list[dict]:
    changes = []
    limit = min(len(left), len(right))
    index = 0
    while index < limit:
        if left[index] == right[index]:
            index += 1
            continue
        start = index
        while index < limit and left[index] != right[index]:
            index += 1
        changes.append({"offset": start, "length": index - start, "original_first": left[start], "rebuilt_first": right[start]})
    if len(left) != len(right):
        changes.append({"offset": limit, "original_size": len(left), "rebuilt_size": len(right)})
    return changes


def compare(app: str) -> dict:
    original_path = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts" / f"{app}.elf"
    rebuilt_path = ROOT / "tmp/2B/S2B-T15/offline_restore_20261019_r01/r04_workspace" / app / "build" / f"{app}.elf"
    original = original_path.read_bytes()
    rebuilt = rebuilt_path.read_bytes()
    left = parse_elf(original)
    right = parse_elf(rebuilt)
    rows = []
    right_sections = {item["name"]: item for item in right["sections"]}
    for a in left["sections"]:
        if not (a["flags"] & 0x2):
            continue
        b = right_sections.get(a["name"])
        if b is None:
            rows.append({"name": a["name"], "present_original": True, "present_rebuilt": False})
            continue
        a_data = original[a["offset"]:a["offset"] + a["size"]] if a["type"] != 8 else b""
        b_data = rebuilt[b["offset"]:b["offset"] + b["size"]] if b["type"] != 8 else b""
        ranges = diff_ranges(a_data, b_data)
        symbols = []
        for sym in left["symbols"]:
            if sym["section"] == a["index"] and sym["value"] <= a["address"] + (ranges[0]["offset"] if ranges else 0):
                symbols.append(sym)
        nearest = max(symbols, key=lambda sym: sym["value"], default=None)
        rows.append({
            "name": a["name"], "section_index": a["index"], "type": a["type"],
            "flags": {"original": a["flags"], "rebuilt": b["flags"], "equal": a["flags"] == b["flags"]},
            "address": {"original": a["address"], "rebuilt": b["address"], "equal": a["address"] == b["address"]},
            "size": {"original": a["size"], "rebuilt": b["size"], "equal": a["size"] == b["size"]},
            "file_offset": {"original": a["offset"], "rebuilt": b["offset"], "equal": a["offset"] == b["offset"]},
            "sha256_original": sha(a_data), "sha256_rebuilt": sha(b_data),
            "changed_bytes": sum(item.get("length", 0) for item in ranges),
            "difference_ranges": ranges[:64],
            "nearest_original_symbol": nearest,
        })
    return {"app": app, "original_sha256": sha(original), "rebuilt_sha256": sha(rebuilt), "entry_equal": left["entry"] == right["entry"], "allocatable_sections": rows}


def main() -> None:
    result_path = OUT / "comparison_sections.json"
    result = {
        "schema_version": 1,
        "method": "parse_elf helper plus SHF_ALLOC section byte comparison",
        "apps": [compare("infer"), compare("init")],
        "limitations": ["静态ELF比较不替代CPU仿真、板上运行或完整PS/PL冷启动恢复验证。"],
    }
    with result_path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
