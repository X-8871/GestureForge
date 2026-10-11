"""按封存清单精确复制独审原字节，保留失败及未执行状态。"""

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def digest(raw):
    """计算实际原字节，不规范化换行。"""
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    """仅创建新文件，禁止覆盖已关闭证据。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def bound_file(item):
    """验证精确目标和SHA，拒绝工作区外路径。"""
    path = ROOT / item["path"]
    assert path.is_file() and path.resolve().is_relative_to(ROOT), item["path"]
    raw = path.read_bytes()
    assert digest(raw) == item["sha256"], item["path"]
    return path, raw


def main():
    """只复制原清单指定原件；不扫描编译缓存或变更业务代码。"""
    config_path = Path(sys.argv[1]).resolve()
    assert config_path.is_file() and config_path.is_relative_to(ROOT)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    raw_path, raw_bytes = bound_file(config["raw_manifest"])
    raw_manifest = json.loads(raw_bytes)
    assert raw_manifest["status"] == config["review_status"]
    receipt_path, receipt_bytes = bound_file(config["receipt"])
    receipt = json.loads(receipt_bytes)
    assert receipt["status"] == config["review_status"]
    original_path, original_bytes = bound_file(config["reviewed_manifest"])
    original = json.loads(original_bytes)
    # 本轮原receipt以完整源矩阵固定版本；实际审查脚本另有两份清单的硬编码SHA断言。
    _, freeze_bytes = bound_file(config["source_freeze"])
    freeze = json.loads(freeze_bytes)
    assert receipt["source_sha256"] == freeze["source_sha256"]
    assert receipt["source_commit_at_freeze"] == freeze["source_commit_at_freeze"]
    _, review_bytes = bound_file(config["review_script"])
    for expected in (config["reviewed_manifest"]["sha256"], config["source_freeze"]["sha256"]):
        assert expected.encode("ascii") in review_bytes
    assert receipt["audit"]["bindings_streamed"] == len(original["files"])
    assert receipt["audit"]["sources"] == len(freeze["source_sha256"])
    assert receipt["remaining_heavy"] == []
    raw_files = list(raw_manifest["files"])
    assert all(set(item) == {"path", "sha256", "role"} for item in raw_files)
    raw_files.append({**config["raw_manifest"], "role": "artifact"})
    assert len({item["path"] for item in raw_files}) == len(raw_files)
    assert config["receipt"]["path"] in {item["path"] for item in raw_files}
    for item in raw_files + original["files"] + original["interfaces"]:
        bound_file(item)
    native_files = {item["path"]: item for item in raw_files}
    checks = []
    for item in config["native_checks"]:
        _, native_bytes = bound_file(native_files[item["path"]])
        native = json.loads(native_bytes)
        assert native["native_exit_code"] == item["expected_exit_code"]
        assert type(native["command"]) is list and all(type(arg) is str for arg in native["command"])
        checks.append({"name": item["name"],
                       "status": "PASS" if native["native_exit_code"] == 0 else "FAIL",
                       "command": subprocess.list2cmdline(native["command"]),
                       "exit_code": native["native_exit_code"], "reason": item["reason"]})
    selected_checks = set(config["include_reviewed_checks"])
    assert selected_checks <= {item["name"] for item in original["checks"]}
    checks.extend(item for item in original["checks"] if item["name"] in selected_checks)
    formal = ROOT / config["evidence_dir"]
    assert formal.parent.is_dir() and not formal.exists()
    assert formal.parent.resolve().is_relative_to(ROOT)
    head = subprocess.run(["git", "-c", "core.longpaths=true", "rev-parse", "HEAD"],
                          cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    formal.mkdir()
    copies, mapping = [], []
    for item in raw_files:
        source, raw = bound_file(item)
        target = formal / "raw_artifacts" / source.relative_to(ROOT)
        assert not target.exists() and target.resolve().is_relative_to(formal.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        assert target.read_bytes() == raw
        copies.append({"path": target.relative_to(ROOT).as_posix(),
                       "sha256": item["sha256"], "role": item["role"]})
        mapping.append({"original": item["path"], "copy": copies[-1]["path"],
                        "sha256": item["sha256"], "bytes": len(raw)})
    binding = {"schema_version": 1, "status": "PASS_EXACT_RAW_COPY_ONLY",
               "created_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
               "capture_head": head.stdout.decode("ascii").strip(),
               "reviewed_source_commit": receipt["source_commit_at_freeze"],
               "reviewed_manifest": config["reviewed_manifest"],
               "raw_manifest": config["raw_manifest"], "receipt": config["receipt"],
               "raw_file_count": len(mapping), "raw_bytes": sum(row["bytes"] for row in mapping),
               "files": mapping, "limitations": config["limitations"]}
    binding_path = formal / "archive_binding.json"
    write_json(binding_path, binding)
    script_path = formal / "archive_reviewed_evidence.py"
    shutil.copyfile(Path(__file__), script_path)
    assert script_path.read_bytes() == Path(__file__).read_bytes()
    files = [{**item, "role": "source" if item["role"] == "source" else "input"}
             for item in original["files"]]
    files += [{**config["reviewed_manifest"], "role": "input"}, *copies,
              {"path": binding_path.relative_to(ROOT).as_posix(),
               "sha256": digest(binding_path.read_bytes()), "role": "result"},
              {"path": script_path.relative_to(ROOT).as_posix(),
               "sha256": digest(script_path.read_bytes()), "role": "source"}]
    assert len({item["path"] for item in files}) == len(files)
    manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T17",
                "run_id": formal.name, "source_commit": receipt["source_commit_at_freeze"],
                "evidence_dir": config["evidence_dir"], "interfaces": original["interfaces"],
                "files": files, "checks": checks,
                "tool_versions": {"python": sys.version}, "limitations": config["limitations"]}
    manifest_path = formal / "delivery_manifest.json"
    write_json(manifest_path, manifest)
    print(json.dumps({"status": "COPIED_FROZEN_REVIEW_RAW_ONLY", "raw_files": len(mapping),
                      "raw_bytes": binding["raw_bytes"], "binding_count": len(files),
                      "manifest": manifest_path.relative_to(ROOT).as_posix(),
                      "manifest_sha256": digest(manifest_path.read_bytes()),
                      "mapping_sha256": digest(binding_path.read_bytes())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
