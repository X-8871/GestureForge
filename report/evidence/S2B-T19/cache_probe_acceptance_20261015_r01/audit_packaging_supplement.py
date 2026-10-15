#!/usr/bin/env python3
"""只读复核首次失败清单与补充清单；不修改历史输出或连接硬件。"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def main():
    """运行原验收复算，再核对补充封装与保留的真实格式失败。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", required=True)
    args = parser.parse_args()
    folder = pathlib.Path(__file__).resolve().parent
    root = folder.parents[3]
    result = subprocess.run([sys.executable, "-X", "utf8", "-B",
                             str(folder / "audit_cache_probe.py"), "--verify"],
                            cwd=root, capture_output=True)
    assert result.returncode == 0, result.stderr.decode("utf-8")
    original = json.loads((folder / "delivery_manifest.json").read_text(encoding="utf-8"))
    supplement = json.loads((folder / "delivery_manifest_supplement.json").read_text(encoding="utf-8"))
    failure = json.loads((folder / "packaging_failure_execution.json").read_text(encoding="utf-8"))
    errors = json.loads(bytes.fromhex(failure["stdout_hex"]))["errors"]
    assert failure["native_exit_code"] == 2 and failure["first_outer_tool_exit_code"] == 1
    role_errors = [error for error in errors if "role=log" in error]
    assert len(role_errors) == 3
    before = {item["path"]: item for item in original["files"]}
    after = {item["path"]: item for item in supplement["files"]}
    changed = []
    for path, item in before.items():
        assert after[path]["sha256"] == item["sha256"]
        if after[path] != item:
            assert item["role"] == "log" and after[path] == {**item, "role": "input"}
            changed.append(path)
    assert len(changed) == 3 and all(path in "\n".join(role_errors) for path in changed)
    assert original["source_commit"] == supplement["source_commit"]
    assert original["interfaces"] == supplement["interfaces"]
    for item in supplement["files"]:
        assert digest(root / item["path"]) == item["sha256"], item["path"]
    recorded = {item["path"] for item in supplement["files"]}
    own = {p.relative_to(root).as_posix() for p in folder.rglob("*") if p.is_file()}
    assert own - recorded == {(folder / "delivery_manifest_supplement.json").relative_to(root).as_posix()}
    print(json.dumps({"status": "VERIFY_SUPPLEMENT_OK", "bound_files": len(after),
                      "preserved_packaging_failure_native_exit_code": 2,
                      "first_outer_tool_exit_code": 1,
                      "corrected_roles": changed, "cold_lifecycle_proven": False}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "VERIFY_FAILED", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)

