"""逐字节保全总控实际诊断，并固定独立集成补审输入。"""

from pathlib import Path
import hashlib
import json
import re
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write("\n")


def main():
    started = time.perf_counter()
    root = Path.cwd()
    run = Path(__file__).parent
    assert run == root / "report/evidence/S2B-T06/ps_smoke_integration_20261009_r01"
    assert run.is_dir() and not run.is_symlink()
    baseline = "00f51b664fefdaf0c63e605af2427333579fa5f3"
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip() == baseline
    assert not subprocess.check_output(["git", "diff", "--cached", "--binary"], cwd=root)
    pairs = [
        ("tmp/2B/S2B-T06/root_freeze_inputs_check_01.log", "diagnostics/root_freeze_inputs_check_01.log"),
        ("tmp/2B/S2B-T06/root_freeze_packaging_checks_02.json", "diagnostics/root_freeze_packaging_checks_02.json"),
        ("tmp/2B/S2B-T06/root_freeze_inputs_check_02.log", "diagnostics/root_freeze_inputs_check_02.log"),
        ("tmp/2B/S2B-T06/root_freeze_evidence_check_02.log", "diagnostics/root_freeze_evidence_check_02.log"),
        ("tmp/2B/S2B-T06/candidate_index_p01_receipt.json", "diagnostics/candidate_index_p01_receipt.json"),
        ("tmp/2B/S2B-T06/candidate_index_p01_whitespace.log", "diagnostics/candidate_index_p01_whitespace.log"),
        ("tmp/2B/S2B-T06/candidate_index_p02_receipt.json", "diagnostics/candidate_index_p02_receipt.json"),
        ("tmp/2B/S2B-T06/candidate_index_p02_whitespace.log", "diagnostics/candidate_index_p02_whitespace.log"),
        ("tmp/2B/S2B-T06/verify_candidate_index.py", "diagnostics/verify_candidate_index.py"),
        (".codex/STATE.md", "controls/STATE.snapshot.md"),
        (".gitattributes", "controls/gitattributes.snapshot.txt"),
    ]
    mapping = []
    for original, relative in pairs:
        source = root / original
        target = run / relative
        assert source.is_file() and not source.is_symlink(), str(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists() and not target.parent.is_symlink(), str(target)
        content = source.read_bytes()
        with target.open("xb") as output:
            output.write(content)
        assert target.read_bytes() == content
        mapping.append({"source": str(source), "destination": target.relative_to(root).as_posix(),
                        "bytes": len(content), "sha256": sha(target)})
    sdk_paths = json.loads((run / "original_sdk_whitespace_paths.json").read_text(encoding="utf-8"))
    assert len(sdk_paths) == len(set(sdk_paths)) == 42
    failures = (run / "diagnostics/candidate_index_p01_whitespace.log").read_text(encoding="utf-8")
    observed = set(re.findall(r"^(report/evidence/S2B-T06/.+?):\d+:", failures, re.MULTILINE))
    assert observed == set(sdk_paths), (observed - set(sdk_paths), set(sdk_paths) - observed)
    initial = json.loads((run / "root_initial_assumption_tool_result.json").read_text(encoding="utf-8"))
    assert initial["exit_code"] == 1 and "AssertionError" in initial["output"]
    repeated = json.loads((run / "diagnostics/root_freeze_packaging_checks_02.json").read_text(encoding="utf-8"))
    assert [item["exit_code"] for item in repeated] == [2, 0]
    assert repeated[0]["result"]["errors"] == ["checks[1] 依赖检查状态为 NOT_RUN，阻断 inputs 核验"]
    acceptance_path = root / "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01/acceptance.json"
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    controls = [{"path": original, "snapshot": (run / relative).relative_to(root).as_posix(),
                 "sha256": sha(root / original)} for original, relative in pairs[-2:]]
    write_json(run / "collection_receipt.json", {
        "baseline_commit": baseline, "mapping": mapping, "elapsed_seconds": time.perf_counter() - started,
        "initial_outer_exit_code": 1, "initial_checker_exit_code": "NOT_RECORDED_ORIGINALLY",
        "observed_repeat_exit_codes": [2, 0], "original_whitespace_failure_files": 42,
        "physical_execution": "NOT_RUN", "shared_index_unchanged_and_empty": True,
        "scope": "保全实际失败及正确的实板依赖阻断；复制不替代软件或实物验收。",
    })
    fixed = [
        "report/evidence/S2B-T06/ps_smoke_20261008_r01/delivery_manifest.json",
        "report/evidence/S2B-T06/ps_smoke_20261008_r01/inputs_manifest_r03.json",
        "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01/acceptance.json",
        "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01/delivery_manifest.json",
        "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01/reviewer_copy_mapping.json",
        "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01/reviewer_r01/review/f04/semantic_review_receipt.json",
        "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01/reviewer_r01/review/f04/review_evidence_bindings.json",
        "verification/check_stage_delivery.py",
        acceptance["formal_record"]["path"],
        *acceptance["source_sha256"],
    ]
    fixed.extend(path.relative_to(root).as_posix() for path in run.rglob("*") if path.is_file())
    fixed = sorted(set(fixed))
    write_json(run / "review_scope.json", {
        "task": "S2B-T06 集成补审", "baseline_commit": baseline,
        "allowed_reviewer_writes": "tmp/2B/S2B-T06/rv1/review/i01/",
        "controls": controls, "source_sha256": acceptance["source_sha256"],
        "files": [{"path": name, "sha256": sha(root / name)} for name in fixed],
        "offline_scope": "仅接受固定PS前置软件与操作包的离线G1/G2；实板G3/G4及阶段2B G5未通过。",
        "physical_execution": "NOT_RUN",
    })
    print(json.dumps({"status": "COPIED_AND_FIXED", "copied_files": len(mapping),
                      "review_files": len(fixed), "scope_sha256": sha(run / "review_scope.json"),
                      "control_sha256": controls, "hardware_execution": "NOT_RUN"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
