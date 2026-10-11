"""绑定 R3 实际被测 checker 快照，保留后续 S3 依赖变化和原审查记录。"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path.cwd()
RUN = ROOT / "report/evidence/S2B-T19/root_software_delivery_20261011_r01"
ORIGINAL = ROOT / "report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01/delivery_manifest_r03.json"
ARCHIVE = ROOT / "report/evidence/S2B-T19/independent_probe_reviews_archive_20261011_r01/delivery_manifest_r02.json"
CHECKER = RUN / "source_snapshot/verification/check_s2b_inference_platform.py"


def sha(path):
    """核验原字节而不修改来源。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert RUN.is_dir() and not RUN.is_symlink()
assert sha(ORIGINAL) == "bf7bae1ed9827159ed70f5115d43734959ac6b293e415180d6005ca85263d153"
assert sha(ARCHIVE) == "7ee56d662363b447671fe552ab6cc65d8bed6ab7af24c7b2205e7a51c2204cc0"
manifest = json.loads(ORIGINAL.read_text(encoding="utf-8"))
rows = []
rebound = []
for row in manifest["files"]:
    if row["path"] == "verification/check_s2b_inference_platform.py":
        assert sha(CHECKER) == row["sha256"]
        rebound.append({"original_path": row["path"], "snapshot_path": CHECKER.relative_to(ROOT).as_posix(),
                        "sha256": row["sha256"], "source_commit": manifest["source_commit"]})
        row = {**row, "path": CHECKER.relative_to(ROOT).as_posix()}
    assert (ROOT / row["path"]).is_file() and sha(ROOT / row["path"]) == row["sha256"], row["path"]
    rows.append(row)
assert len(rebound) == 1
receipt = ROOT / "tmp/2B/S2B-T19/independent_probe_review_20261011_r03/review_receipt.json"
assert sha(receipt) == "78a094a0e4ac3894554941f96eea9a8bb887d6c88d0054506197f9232378ed47"
binding = {
    "status": "SAME_REVIEWED_SOFTWARE_SOURCE_OLD_CHECKER_SNAPSHOT_PINNED",
    "role": "ROOT_ARCHIVAL_BINDING", "baseline": manifest["source_commit"], "rebound": rebound,
    "original_manifest": {"path": ORIGINAL.relative_to(ROOT).as_posix(), "sha256": sha(ORIGINAL)},
    "independent_receipt_sha256": sha(receipt),
    "reason": "R3停止后独立S3任务修改同一checker；保留R3被测1f8d原件，不回退共享源码，不把S3作为已被R3验证的平台。",
    "limitations": ["只绑定软件G2，原manifest和receipt不改写。", "完整runtime兼容、postroute/bit/cold/cache/model/G3仍未批准或执行。"]}
path = RUN / "source_dependency_binding.json"
assert not path.exists()
with path.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(binding, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
rows += [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": role}
         for p, role in [(ORIGINAL, "input"), (ARCHIVE, "input"), (path, "result"), (Path(__file__), "source")]]
manifest.update(run_id="root_software_delivery_20261011_r01", evidence_dir=RUN.relative_to(ROOT).as_posix(), files=rows)
manifest["checks"].append({"name": "R3被测checker快照绑定", "status": "PASS",
    "command": f'"{sys.executable}" -B "{__file__}"', "exit_code": 0,
    "reason": "原1f8d rawSHA与实际R3被测源一致，仅记录路径快照绑定，未执行S3或部署。"})
manifest["limitations"].append(binding["reason"])
out = RUN / "delivery_manifest.json"
assert not out.exists()
with out.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": "SEALED_R3_SOFTWARE_ONLY", "manifest_sha256": sha(out), "files": len(rows)}, ensure_ascii=False))
