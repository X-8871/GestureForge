"""按停止后的独立审查原件清单归档，不扩展审查或实物批准。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
CACHE = Path(__file__).resolve().parent
ROLES = {"source", "input", "result", "log", "diagnostic", "artifact"}


def exact(relative):
    """验证清单中的精确项目路径，拒绝穿越与符号链接。"""
    path = ROOT / relative
    assert path.resolve().is_relative_to(ROOT) and not path.is_symlink(), relative
    return path


def sha(path):
    """只计算已核验普通文件的原始字节哈希。"""
    assert path.is_file() and not path.is_symlink(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    """创建 UTF-8 新文件，禁止覆盖旧运行。"""
    assert path.parent.is_dir() and not path.exists(), path
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def binding(path, role):
    """绑定项目内文件的精确路径、原字节和用途。"""
    assert role in ROLES
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path), role=role)


def main():
    """复制已审原件，并使用真实子进程检查闭合后的归档。"""
    config_path = exact(sys.argv[1])
    config = json.loads(config_path.read_text(encoding="utf-8"))
    prefix = config["cache_prefix"]
    assert prefix.isidentifier() and prefix.startswith("archive_")
    receipt_path = exact(config["receipt"])
    raw_path = exact(config["raw_manifest"])
    main_path = exact(config["main_manifest"])
    assert sha(receipt_path) == config["receipt_sha256"]
    assert sha(raw_path) == config["raw_manifest_sha256"]
    assert sha(main_path) == config["main_manifest_sha256"]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    original = json.loads(main_path.read_text(encoding="utf-8"))
    assert receipt[config["verdict_field"]] == "PASS" and receipt["reviewer_stop"] == config["expected_reviewer_stop"]
    assert receipt["source_commit"] == original["source_commit"]
    for path, expected in config.get("reviewed_sources", {}).items():
        assert sha(exact(path)) == expected, path
    rows = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == config["raw_rows"]
    assert len({r["path"] for r in rows}) == len(rows)
    assert all(set(r) == {"path", "sha256", "role"} and r["role"] in ROLES for r in rows)
    for path, role in ((receipt_path, "result"), (raw_path, "artifact"),
                       (main_path, "input"), (Path(__file__).resolve(), "source"),
                       (config_path, "input")):
        if path.relative_to(ROOT).as_posix() not in {r["path"] for r in rows}:
            rows.append(binding(path, role))
    for row in config.get("additional_bound_files", []):
        assert set(row) == {"path", "sha256", "role"} and row["role"] in ROLES
        assert sha(exact(row["path"])) == row["sha256"]
        if row["path"] not in {r["path"] for r in rows}:
            rows.append(row)
    formal = exact(config["formal_dir"])
    assert formal.parent.is_dir() and not formal.exists(), formal
    formal.mkdir()
    files, mapping = [], []
    for index, row in enumerate(rows):
        source = exact(row["path"])
        assert sha(source) == row["sha256"], row["path"]
        assert source.suffix.lower() not in {".exe", ".obj", ".o", ".dcp", ".bit"}
        target = formal / "raw_artifacts" / f"{index:04d}" / source.name
        assert target.resolve().is_relative_to(formal) and not target.exists()
        target.parent.mkdir(parents=True)
        shutil.copyfile(source, target)
        assert sha(source) == sha(target) == row["sha256"]
        files.append(binding(target, row["role"]))
        mapping.append(dict(original=row["path"], copy=target.relative_to(ROOT).as_posix(),
                            sha256=row["sha256"], bytes=source.stat().st_size))
    archive_path = formal / "archive_binding.json"
    save(archive_path, dict(status="PASS_EXACT_COPY_ONLY", scope=receipt["scope"],
        source_commit=receipt["source_commit"], receipt_sha256=config["receipt_sha256"],
        raw_manifest_sha256=config["raw_manifest_sha256"], files=mapping,
        original_raw_rows=config["raw_rows"], limitations=config["limitations"]))
    files.append(binding(archive_path, "result"))
    manifest = dict(schema_version=1, stage="2B", task_id=original["task_id"],
        run_id=formal.name, source_commit=original["source_commit"],
        evidence_dir=formal.relative_to(ROOT).as_posix(), interfaces=original["interfaces"],
        tool_versions=dict(python=sys.version), files=files, checks=list(original["checks"]),
        limitations=list(original.get("limitations", [])) + config["limitations"])
    if "interfaces_not_applicable_reason" in original:
        manifest["interfaces_not_applicable_reason"] = original["interfaces_not_applicable_reason"]
    initial = formal / "delivery_manifest.json"
    save(initial, manifest)
    command = [sys.executable, "-X", "utf8", "-B", str(ROOT / "verification/check_stage_delivery.py"),
               "--mode", "evidence", "--manifest", str(initial), "--project-root", str(ROOT)]
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
    closed = []
    for suffix, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
        path = CACHE / (prefix + "." + suffix)
        with path.open("xb") as stream:
            stream.write(data)
        closed.append(path)
    native = CACHE / (prefix + ".native.json")
    save(native, dict(command=command, native_exit_code=result.returncode,
                      elapsed_seconds=time.monotonic()-started, peak_memory_bytes=None))
    closed.append(native)
    assert result.returncode == 0, result.stdout.decode("utf-8")
    for source in closed:
        target = formal / source.name
        assert not target.exists()
        shutil.copyfile(source, target)
        assert sha(source) == sha(target)
        files.append(binding(target, "log" if target.suffix == ".log" else "result"))
    files.append(binding(initial, "artifact"))
    manifest["checks"].append(dict(name="独立审查原件归档包装", status="PASS",
        command=subprocess.list2cmdline(command), exit_code=result.returncode,
        reason="仅确认清单、复制与绑定；业务批准范围严格遵循独立回执。"))
    final = formal / "delivery_manifest_r02.json"
    save(final, manifest)
    command[command.index("--manifest")+1] = str(final)
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
    for suffix, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
        with (CACHE / (prefix + "_final." + suffix)).open("xb") as stream:
            stream.write(data)
    save(CACHE / (prefix + "_final.native.json"),
         dict(command=command, native_exit_code=result.returncode, peak_memory_bytes=None))
    assert result.returncode == 0, result.stdout.decode("utf-8")
    print(json.dumps(dict(status="ARCHIVED_REVIEW_SCOPE_ONLY", manifest=binding(final, "artifact"),
        bindings=len(files), copied_files=len(mapping), raw_bytes=sum(r["bytes"] for r in mapping)),
        ensure_ascii=False))


if __name__ == "__main__":
    main()
