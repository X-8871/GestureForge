"""封存 S8 独立审查原件，归档核验不替代设计或实物验收。"""
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
REVIEW = ROOT / "tmp/2B/S2B-T17/independent_s8_maxpool_review_20261011_r01"
FORMAL = ROOT / "report/evidence/S2B-T17/independent_s8_maxpool_review_20261011_r01"
MAIN = ROOT / "report/evidence/S2B-T17/maxpool_address_guard_20261011_r01/delivery_manifest.json"
RECEIPT_SHA = "dbe37b505c8fa928404cea486555b2b0858769b228af9cb587ed875406153bd8"
RAW_SHA = "e25f27b854a79369a074c4c58a8fa7040f81a24d07c41fa1b900f63900847b62"
MAIN_SHA = "da23a571f0ad53a8abbb342adeef4f1bfe07e5dfe8536bd2da8010e4d74bf058"


def sha(path):
    """读取已核验的普通文件原字节。"""
    assert path.is_file() and not path.is_symlink(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    """新建记录，拒绝覆盖已有运行。"""
    assert path.parent.is_dir() and not path.exists(), path
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """固定审查闭包并保存真实机器包装检查退出码。"""
    receipt_path = REVIEW / "final_review_receipt.json"
    raw_path = REVIEW / "raw_manifest.jsonl"
    assert sha(receipt_path) == RECEIPT_SHA and sha(raw_path) == RAW_SHA
    assert sha(MAIN) == MAIN_SHA
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    original = json.loads(MAIN.read_text(encoding="utf-8"))
    assert receipt["status"] == "PASS" and receipt["reviewer_stop"] is True
    assert receipt["source_commit"] == original["source_commit"]
    for name, expected in receipt["reviewed_source_sha256"].items():
        assert sha(ROOT / name) == expected, name
    rows = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 234 and len({row["path"] for row in rows}) == 234
    assert all(set(row) == {"path", "sha256", "role"} for row in rows)
    for path, digest, role in [(receipt_path, RECEIPT_SHA, "result"), (raw_path, RAW_SHA, "artifact")]:
        relative = path.relative_to(ROOT).as_posix()
        if relative not in {row["path"] for row in rows}:
            rows.append({"path": relative, "sha256": digest, "role": role})
    script = Path(__file__).resolve()
    rows.append({"path": script.relative_to(ROOT).as_posix(), "sha256": sha(script), "role": "source"})
    assert FORMAL.parent.is_dir() and not FORMAL.exists()
    FORMAL.mkdir()
    files, mapping = [], []
    for index, row in enumerate(rows):
        source = ROOT / row["path"]
        assert source.resolve().is_relative_to(ROOT) and sha(source) == row["sha256"]
        assert row["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"}
        assert source.suffix.lower() not in {".exe", ".obj", ".o", ".dcp", ".bit"}
        target = FORMAL / "raw_artifacts" / f"{index:04d}" / source.name
        assert not target.exists() and target.resolve().is_relative_to(FORMAL)
        target.parent.mkdir(parents=True)
        shutil.copyfile(source, target)
        assert sha(source) == row["sha256"] and sha(target) == row["sha256"]
        item = {"path": target.relative_to(ROOT).as_posix(), "sha256": row["sha256"], "role": row["role"]}
        files.append(item)
        mapping.append({"original": row["path"], "copy": item["path"], "sha256": row["sha256"], "bytes": source.stat().st_size})
    binding = FORMAL / "archive_binding.json"
    save(binding, {"status": "PASS_EXACT_COPY_ONLY", "review_scope": receipt["scope"],
                   "receipt_sha256": RECEIPT_SHA, "raw_manifest_sha256": RAW_SHA,
                   "source_commit": receipt["source_commit"], "original_raw_rows": 234,
                   "copied_files": len(mapping), "files": mapping,
                   "limitations": ["仅保存独立审查结果，不批准 STA、位流、运行时或实板验收。"]})
    files.append({"path": binding.relative_to(ROOT).as_posix(), "sha256": sha(binding), "role": "result"})
    manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T17",
                "run_id": FORMAL.name, "source_commit": receipt["source_commit"],
                "evidence_dir": FORMAL.relative_to(ROOT).as_posix(),
                "interfaces": original["interfaces"], "tool_versions": {"python": sys.version},
                "files": files, "checks": list(original["checks"]),
                "limitations": list(original["limitations"]) + [receipt["scope"], "ROOT 归档不新增独立批准。"]}
    initial = FORMAL / "delivery_manifest.json"
    save(initial, manifest)
    for mode, expected in [("evidence", 0), ("inputs", 2)]:
        command = [sys.executable, "-B", "-X", "utf8", str(ROOT / "verification/check_stage_delivery.py"),
                   "--project-root", str(ROOT), "--mode", mode, "--manifest", str(initial)]
        started = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
        for suffix, data in [("stdout.log", result.stdout), ("stderr.log", result.stderr)]:
            p = FORMAL / f"root_{mode}.{suffix}"
            with p.open("xb") as stream:
                stream.write(data)
            manifest["files"].append({"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": "log"})
        native = FORMAL / f"root_{mode}.native.json"
        save(native, {"command": command, "native_exit_code": result.returncode,
                      "seconds": time.monotonic() - started, "peak_memory_bytes": None})
        manifest["files"].append({"path": native.relative_to(ROOT).as_posix(), "sha256": sha(native), "role": "result"})
        assert result.returncode == expected, (mode, result.returncode, result.stdout)
        manifest["checks"].append({"name": "ROOT 归档包装 " + mode, "status": "PASS" if expected == 0 else "FAIL",
                                   "command": subprocess.list2cmdline(command), "exit_code": result.returncode,
                                   "reason": "只核对包装；物理候选未冻结，实板及 STA 未运行。"})
    manifest["files"].append({"path": initial.relative_to(ROOT).as_posix(), "sha256": sha(initial), "role": "artifact"})
    final = FORMAL / "delivery_manifest_r02.json"
    save(final, manifest)
    print(json.dumps({"status": "ARCHIVED_S8_G2_ONLY", "bindings": len(manifest["files"]),
                      "raw_bytes": sum(item["bytes"] for item in mapping), "manifest_sha256": sha(final)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
