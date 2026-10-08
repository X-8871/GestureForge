"""按独立审查冻结清单复制真实证据，并保存原路径映射。"""

from pathlib import Path
import hashlib
import importlib.util
import json
import time


def main():
    root = Path.cwd()
    base = root / "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01"
    helper = base / "root_context/copy_review_inputs.py"
    spec = importlib.util.spec_from_file_location("exact_input_paths", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = module.existing_exact(root, True)
    base = module.existing_exact(base, True)
    rv1 = module.existing_exact(root / "tmp/2B/S2B-T06/rv1", True)
    source = module.existing_exact(rv1 / "review/f04/review_evidence_bindings.json")
    expected = "6bf5e032f670f563d2fa532aa5e66ebf7ecfbf0c83516043ece975c342e79c48"
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        raise RuntimeError("独立审查冻结清单已改变")
    binding = json.loads(source.read_text(encoding="utf-8"))
    if binding["decision"] != "PASS" or binding["file_count"] != 110:
        raise RuntimeError("独立审查不是固定PASS版本")
    records = list(binding["files"])
    records.append({"path": str(source), "relative_to_rv1": source.relative_to(rv1).as_posix(),
                    "sha256": expected, "bytes": source.stat().st_size})
    target = base / "reviewer_r01"
    if any(item.name.casefold() == target.name.casefold() for item in base.iterdir()):
        raise RuntimeError("审查证据目标必须全新")
    target.mkdir()
    rows = []
    seen = set()
    started = time.perf_counter()
    for item in records:
        origin = module.existing_exact(Path(item["path"]))
        relative = origin.relative_to(rv1)
        if relative.as_posix() != item["relative_to_rv1"] or relative.as_posix() in seen:
            raise RuntimeError(f"相对路径或唯一性错误：{origin}")
        seen.add(relative.as_posix())
        data = origin.read_bytes()
        if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise RuntimeError(f"独立审查原件改变：{origin}")
        parent = target
        for part in relative.parts[:-1]:
            child = parent / part
            names = [entry.name for entry in parent.iterdir()]
            if part not in names:
                if any(name.casefold() == part.casefold() for name in names):
                    raise RuntimeError(f"目录大小写冲突：{child}")
                child.mkdir()
            parent = module.existing_exact(child, True)
        destination = parent / relative.name
        if any(entry.name.casefold() == relative.name.casefold() for entry in parent.iterdir()):
            raise RuntimeError(f"目标文件不是全新：{destination}")
        with destination.open("xb") as output:
            output.write(data)
        if destination.read_bytes() != data:
            raise RuntimeError(f"审查证据复制不一致：{destination}")
        rows.append({"source": str(origin), "destination": destination.relative_to(root).as_posix(),
                     "sha256": item["sha256"], "bytes": len(data)})
    receipt = {"status": "PASS_G2_REVIEWER_BYTE_COPY", "files": rows, "copied_files": len(rows),
               "copied_bytes": sum(row["bytes"] for row in rows), "elapsed_seconds": time.perf_counter()-started,
               "original_binding_sha256": expected, "hardware_execution": "NOT_RUN"}
    mapping = base / "reviewer_copy_mapping.json"
    with mapping.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(receipt, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps({key: receipt[key] for key in ("status", "copied_files", "copied_bytes", "elapsed_seconds")},
                     ensure_ascii=False))
    print("mapping_sha256=" + hashlib.sha256(mapping.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
