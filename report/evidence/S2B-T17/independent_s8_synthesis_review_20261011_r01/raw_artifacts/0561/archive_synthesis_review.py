"""按独立审查停止后的清单逐字节归档S8真实失败证据审查。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
CACHE = Path(__file__).resolve().parent
REVIEW = ROOT / "tmp/2B/S2B-T17/independent_s8_synthesis_review_20261011_r01"
FORMAL = ROOT / "report/evidence/S2B-T17/independent_s8_synthesis_review_20261011_r01"
MAIN = ROOT / "report/evidence/S2B-T17/s8_platform_20261011_r01/s8_delivery_manifest_r02.json"


def sha(path):
    """核对真实普通文件原字节。"""
    assert path.is_file() and not path.is_symlink(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    """只创建新目标，拒绝覆盖已有运行。"""
    assert path.parent.is_dir() and not path.exists(), path
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """归档不改变原STA失败，也不新增设计或板上批准。"""
    config = json.loads((CACHE / "archive_synthesis_review_config.json").read_text(encoding="utf-8"))
    receipt_path = REVIEW / "final_review_receipt.json"
    raw_path = REVIEW / "raw_manifest.jsonl"
    assert sha(receipt_path) == config["receipt_sha256"]
    assert sha(raw_path) == config["raw_manifest_sha256"]
    assert sha(MAIN) == "a63839ea6e82b71fa28c6f9bd37223123ffeda3df5f122978b9b420c8c962e0e"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    original = json.loads(MAIN.read_text(encoding="utf-8"))
    assert receipt["status"] == "PASS" and receipt["reviewer_stop"] is True
    assert receipt["source_commit"] == original["source_commit"]
    for name, expected in config["reviewed_source_sha256"].items():
        assert sha(ROOT / name) == expected, name
    rows = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == config["raw_rows"] and len({r["path"] for r in rows}) == len(rows)
    assert all(set(r) == {"path", "sha256", "role"} for r in rows)
    for path, role in ((receipt_path, "result"), (raw_path, "artifact"), (Path(__file__).resolve(), "source")):
        name = path.relative_to(ROOT).as_posix()
        if name not in {r["path"] for r in rows}:
            rows.append(dict(path=name, sha256=sha(path), role=role))
    assert FORMAL.parent.is_dir() and not FORMAL.exists()
    FORMAL.mkdir()
    files = []
    mapping = []
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
        name = target.relative_to(ROOT).as_posix()
        files.append(dict(path=name, sha256=row["sha256"], role=row["role"]))
        mapping.append(dict(original=row["path"], copy=name, sha256=row["sha256"], bytes=source.stat().st_size))
    path = FORMAL / "archive_binding.json"
    save(path, dict(status="PASS_EXACT_COPY_ONLY", review_scope=receipt["scope"],
        source_commit=receipt["source_commit"], receipt_sha256=config["receipt_sha256"],
        raw_manifest_sha256=config["raw_manifest_sha256"], original_raw_rows=config["raw_rows"],
        copied_files=len(mapping), files=mapping,
        limitations=["仅独立核查实际综合失败证据；50MHz仍失败，postroute/bit/runtime/BOARD/G3–G5未批准。"] ))
    files.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path), role="result"))
    manifest = dict(schema_version=1, stage="2B", task_id="S2B-T17", run_id=FORMAL.name,
        source_commit=receipt["source_commit"], evidence_dir=FORMAL.relative_to(ROOT).as_posix(),
        interfaces=original["interfaces"], tool_versions=dict(python=sys.version), files=files,
        checks=list(original["checks"]), limitations=list(original["limitations"])+[receipt["scope"],"独立PASS范围见原始receipt，不改判STA或板上状态。"])
    initial = FORMAL / "delivery_manifest.json"
    save(initial, manifest)
    closed_checks = []
    for mode, expected in (("evidence", 0), ("inputs", 2)):
        command = [sys.executable, "-X", "utf8", "-B", str(ROOT / "verification/check_stage_delivery.py"),
                   "--mode", mode, "--manifest", str(initial), "--project-root", str(ROOT)]
        started = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
        paths = []
        for suffix, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
            path = CACHE / ("synthesis_archive_"+mode+"."+suffix)
            with path.open("xb") as stream:
                stream.write(data)
            paths.append(path)
        path = CACHE / ("synthesis_archive_"+mode+".native.json")
        save(path, dict(command=command, native_exit_code=result.returncode, elapsed_seconds=time.monotonic()-started, peak_memory_bytes=None))
        paths.append(path)
        assert result.returncode == expected, (mode, result.returncode, result.stdout.decode("utf-8"))
        closed_checks.extend(paths)
        manifest["checks"].append(dict(name="ROOT独立审查归档包装："+mode, status="PASS" if expected == 0 else "FAIL",
            command=subprocess.list2cmdline(command), exit_code=result.returncode, reason="包装核验；原STA失败及候选未冻结阻断继续保留。"))
    for source in closed_checks:
        target = FORMAL / source.name
        shutil.copyfile(source, target)
        assert sha(source) == sha(target)
        files.append(dict(path=target.relative_to(ROOT).as_posix(), sha256=sha(target), role="log" if target.suffix == ".log" else "result"))
    files.append(dict(path=initial.relative_to(ROOT).as_posix(), sha256=sha(initial), role="artifact"))
    final = FORMAL / "delivery_manifest_r02.json"
    save(final, manifest)
    command = [sys.executable,"-X","utf8","-B",str(ROOT / "verification/check_stage_delivery.py"),
               "--mode","evidence","--manifest",str(final),"--project-root",str(ROOT)]
    result = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=55)
    for suffix,data in (("stdout.log",result.stdout),("stderr.log",result.stderr)):
        with (CACHE / ("synthesis_archive_final."+suffix)).open("xb") as stream:
            stream.write(data)
    save(CACHE / "synthesis_archive_final.native.json",dict(command=command,native_exit_code=result.returncode))
    assert result.returncode == 0,result.stdout.decode("utf-8")
    print(json.dumps(dict(status="ARCHIVED_S8_FAILED_SYNTHESIS_REVIEW_ONLY",manifest_sha256=sha(final),
        bindings=len(files),raw_bytes=sum(r["bytes"] for r in mapping)),ensure_ascii=False))


if __name__ == "__main__":
    main()
