"""只读核对离线批准、源绑定、审查原件映射和固定部署候选。"""

from pathlib import Path
import hashlib
import json
import re


def sha(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"文件不存在或不是普通文件：{path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path.cwd()
    base = root / "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01"
    approval = json.loads((base / "acceptance.json").read_text(encoding="utf-8"))
    assert approval["decision"] == "APPROVED_OFFLINE_PRECHECK_CANDIDATE_ONLY"
    assert approval["hardware_execution"] == "NOT_RUN"
    assert approval["gate_status"] == {"G1": "PASS_OFFLINE", "G2": "PASS", "G3": "NOT_RUN",
        "G4": "NOT_PASSED", "stage_2B_G5": "NOT_PASSED", "stage_2B_G0": "NOT_PASSED"}
    for relative, expected in approval["source_sha256"].items():
        assert sha(root / relative) == expected, relative
    for key in ("formal_record", "developer_manifest", "independent_review", "reviewer_bindings", "copy_mapping"):
        item = approval[key]
        assert sha(root / item["path"]) == item["sha256"], key
    review = json.loads((root / approval["independent_review"]["path"]).read_text(encoding="utf-8"))
    assert review["decision"] == "PASS" and review["blocking_findings"] == []
    assert review["source_sha256"] == approval["source_sha256"]
    assert review["baseline_commit"] == approval["baseline_commit"]
    assert review["fixed_upstream_commit"] == approval["fixed_upstream_commit"]
    assert review["independent_rebuild"]["native_exit_code"] == 0
    assert review["independent_rebuild"]["effective_exit_code"] == 0
    assert review["independent_rebuild"]["build_details_status"] == "PASS_OFFLINE_BUILD_AND_LAYOUT"
    for value in review["independent_rebuild"]["build_api_results"].values():
        assert value["return_type"] == "int" and value["return_repr"] == "0"
    mapping = json.loads((base / "reviewer_copy_mapping.json").read_text(encoding="utf-8"))
    assert mapping["copied_files"] == 111 and mapping["copied_bytes"] == 4339999
    assert len(mapping["files"]) == len({row["destination"] for row in mapping["files"]}) == 111
    for row in mapping["files"]:
        destination = root / row["destination"]
        assert destination.stat().st_size == row["bytes"]
        assert sha(destination) == row["sha256"]
    original = json.loads((root / approval["reviewer_bindings"]["path"]).read_text(encoding="utf-8"))
    copied = {row["source"]: row for row in mapping["files"]}
    assert len(original["files"]) == original["file_count"] == 110
    for row in original["files"]:
        assert copied[row["path"]]["sha256"] == row["sha256"]
        assert copied[row["path"]]["bytes"] == row["bytes"]
    developer = json.loads((root / approval["developer_manifest"]["path"]).read_text(encoding="utf-8"))
    assert len(developer["files"]) == 284
    for row in developer["files"]:
        assert sha(root / row["path"]) == row["sha256"], row["path"]
    owned = {row["path"] for row in developer["files"] if row["path"].startswith("report/evidence/S2B-T06/ps_smoke_20261008_r01/")}
    dev_manifest = root / approval["developer_manifest"]["path"]
    actual = {path.relative_to(root).as_posix() for path in dev_manifest.parent.rglob("*") if path.is_file()}
    assert actual == owned | {approval["developer_manifest"]["path"]}
    selected = {
        "s2b_ps_smoke.elf": "8b9803682c9585a8dad91daf96f3f102de948466025e0cf28ee4b96e6cfde428",
        "s2b_ps_smoke.map": "7273e22fd811804eafe538b173c42bbf50b3311e6c489c69f23add95cf28b218",
        "s2b_ps_init.elf": "366ad1f4831eba9db0510c0e5343d34e3b355f72c8f8bcae419903814246024c",
        "s2b_ps_init.map": "aebac0c4c66014d859f38b34f409afee4039dc6ec516d25f4cf74d509df35efa"}
    operation = (root / "vitis/s2b_ps_smoke.md").read_text(encoding="utf-8")
    formal = (root / approval["formal_record"]["path"]).read_text(encoding="utf-8")
    for name, expected in selected.items():
        assert sha(dev_manifest.parent / "build_08" / name) == expected
        assert expected in operation and expected in formal
    assert len((root / ".codex/STATE.md").read_text(encoding="utf-8").splitlines()) <= 80
    scope = list(dev_manifest.parent.rglob("*")) + list(base.rglob("*"))
    scope += [root / relative for relative in approval["source_sha256"]] + [root / approval["formal_record"]["path"]]
    secret_pattern = re.compile(rb"AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}")
    hits = [path.relative_to(root).as_posix() for path in scope if path.is_file() and path.suffix != ".elf" and secret_pattern.search(path.read_bytes())]
    assert not hits, hits
    print(json.dumps({"status": "PASS_ROOT_OFFLINE_FREEZE_BINDINGS", "sources": 4,
        "developer_bindings": 284, "reviewer_copies": 111, "selected_deploy_files": 4,
        "source_or_binding_differences": 0, "secret_pattern_hits": 0,
        "hardware_execution": "NOT_RUN", "g3_g4_g5": "NOT_PASSED"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
