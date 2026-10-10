"""提交前只读核对被审源码、Git暂存字节及当前声明证据。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
target = ROOT / "report/evidence/S2B-T10/integration_close_20261010_r01"
assert target.parent.is_dir() and not target.exists()
target.mkdir()
receipt_path = ROOT / "report/evidence/S2B-T10/independent_review_20261010_r01/review_receipt.json"
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
assert receipt["decision"] == "PASS"
for item in receipt["sources"]:
    assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]
    indexed = subprocess.check_output(["git", "show", ":" + item["path"]], cwd=ROOT)
    assert hashlib.sha256(indexed).hexdigest() == item["sha256"]
allowed = {".gitattributes", ".codex/STATE.md", *(x["path"] for x in receipt["sources"])}
staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).splitlines()
assert all(path in allowed or path.startswith("report/evidence/S2B-T10/") for path in staged)
rows = []
for run_id in ["hp0_adapter_20261010_r09", "vivado_lint_20261010_r01", "vivado_lint_20261010_r02", "vivado_lint_20261010_r03", "independent_review_20261010_r01", "root_packaging_repair_20261010_r01", "root_packaging_repair_20261010_r02"]:
    for mode in ("evidence", "inputs"):
        command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", f"report/evidence/S2B-T10/{run_id}/delivery_manifest.json"]
        actual = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        rows.append({"run_id": run_id, "mode": mode, "command": command, "native_exit_code": actual.returncode, "stdout": actual.stdout, "stderr": actual.stderr})
        assert actual.returncode == (0 if mode == "evidence" else 2), rows[-1]
diff = subprocess.run(["git", "diff", "--cached", "--check"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
assert diff.returncode == 0, diff.stdout
followup = ROOT / "tmp/2B/S2B-T10/independent_review_20261010_r01/archive_followup_receipt.json"
assert followup.is_file() and hashlib.sha256(followup.read_bytes()).hexdigest() == "203d320ee2ccdfefa9232f453331a295e91f4bf426807d2bb13de54ed3a374c0"
shutil.copyfile(followup, target / followup.name)
shutil.copyfile(Path(__file__), target / Path(__file__).name)
(target / "actual_validation.json").write_text(json.dumps({"source_commit": receipt["source_commit"], "reviewed_source_matches_worktree_and_index": True, "sources": receipt["sources"], "staged_file_count_before_closure_evidence": len(staged), "staged_scope": "仅本轮源、STATE、属性与S2B-T10原件", "checks": rows, "diff_check": {"command": "git diff --cached --check", "native_exit_code": diff.returncode, "stdout": diff.stdout, "stderr": diff.stderr}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("FINAL_SOURCES_AND_INDEX_MATCH; EVIDENCE_7_NATIVE0; INPUTS_7_NATIVE2; DIFF_NATIVE0")
