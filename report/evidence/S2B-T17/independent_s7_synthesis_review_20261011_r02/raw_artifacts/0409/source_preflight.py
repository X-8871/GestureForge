"""核对S7已审源码并保留综合前后原字节快照。"""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PREFLIGHT = ROOT / "report/evidence/S2B-T17/s7_source_preflight_20261011_r01"
EVIDENCE = ROOT / "report/evidence/S2B-T17/s7_platform_20261011_r01"
PROJECT = ROOT / "tmp/2B/S2B-T17/s7p1"
FREEZE = ROOT / "report/evidence/S2B-T17/route_address_guard_20261011_r04/source_freeze.json"
EXPECTED_FREEZE = "a4cc9d6696bc73545c231cf236b5f82d0845423196acacd44c66851904124df7"


def sha(data):
    """返回原字节SHA。"""
    return hashlib.sha256(data).hexdigest()


def git_bytes(*args):
    """保留Git原生退出码；失败立即阻断。"""
    result = subprocess.run(["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", *args],
                            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f"Git失败:{result.returncode}:{result.stderr.decode('utf-8', errors='replace')}")
    return result.stdout


def main():
    """同一次Run只能各执行一次前、后核验。"""
    phase = sys.argv[1]
    assert phase in ("before", "after")
    assert ROOT.is_dir() and PREFLIGHT.parent.is_dir()
    assert sha(FREEZE.read_bytes()) == EXPECTED_FREEZE
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    target = PREFLIGHT / f"source_{phase}.json"
    assert not target.exists(), "不得覆盖已存在的核验记录"
    if phase == "before":
        assert not PREFLIGHT.exists() and not PROJECT.exists() and not EVIDENCE.exists()
        assert not git_bytes("diff", "--cached", "--name-only").strip(), "暂存区必须清晰"
        PREFLIGHT.mkdir()
    else:
        assert PREFLIGHT.is_dir() and PROJECT.is_dir() and EVIDENCE.is_dir()
    spec = importlib.util.spec_from_file_location("s7_platform_checker", ROOT / "verification/check_s2b_inference_platform.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    static = checker.check_static(ROOT)
    assert len(static) == freeze["static_binding_count"]
    assert set(static).issubset(freeze["source_sha256"])
    assert len(freeze["source_sha256"]) == freeze["source_binding_count"]
    assert set(freeze["source_sha256"]) - set(static) == set(freeze["extra_bindings_beyond_static"])
    assert freeze["profile_version"] == "s2b-inference-platform/0.1.7"
    assert freeze["clock_hz"] == 50000000 and freeze["visibility_default"] == 0
    actual_head = git_bytes("rev-parse", "HEAD").decode("ascii").strip()
    before = None
    if phase == "after":
        before = json.loads((PREFLIGHT / "source_before.json").read_text(encoding="utf-8"))
    commit = actual_head if before is None else before["source_commit"]
    files = []
    for name, expected in freeze["source_sha256"].items():
        source = ROOT / name
        assert source.is_file()
        raw = source.read_bytes()
        assert sha(raw) == expected, f"已审源码漂移:{name}"
        blob = git_bytes("show", f"{commit}:{name}")
        if blob == raw:
            relation = "RAW_IDENTICAL"
        else:
            assert blob == raw.replace(bytes([13, 10]), bytes([10])), f"Git非EOL差异:{name}"
            relation = "GIT_LF_TO_RAW_CRLF"
        snapshot = PREFLIGHT / ("source_snapshot" if phase == "before" else "source_snapshot_after") / name
        assert not snapshot.exists()
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, snapshot)
        assert sha(snapshot.read_bytes()) == expected
        files.append({"path": name, "sha256": expected, "bytes": len(raw),
                      "git_blob_sha256": sha(blob), "git_relation": relation,
                      "snapshot": snapshot.relative_to(ROOT).as_posix()})
    originals = freeze["frozen14_sha256"]
    assert len(originals) == 14
    for name, expected in originals.items():
        assert sha((ROOT / name).read_bytes()) == expected
    if phase == "after":
        assert {item["path"]: item["sha256"] for item in before["source_files"]} == freeze["source_sha256"]
    record = {"schema_version": 1, "status": f"PASS_SOURCE_{phase.upper()}_ONLY",
              "created_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "source_commit": commit, "actual_head_at_check": actual_head,
              "source_freeze": FREEZE.relative_to(ROOT).as_posix(),
              "source_freeze_sha256": EXPECTED_FREEZE, "project_dir": str(PROJECT),
              "evidence_dir": str(EVIDENCE), "source_files": files,
              "platform_static_source_count": len(static), "frozen14_sha256": originals,
              "profile_version": "0.1.7", "physical_interface": "s2b-physical-candidate/0.1.1",
              "clock_hz": 50000000, "visibility_parameter": 0,
              "limitations": ["仅核对源码绑定，不能代替STA、独立审查或实板验收"]}
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": record["status"], "source_count": len(files),
                      "git_raw": sum(x["git_relation"] == "RAW_IDENTICAL" for x in files),
                      "git_eol": sum(x["git_relation"] != "RAW_IDENTICAL" for x in files),
                      "head": commit, "manifest_sha256": sha(target.read_bytes())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
