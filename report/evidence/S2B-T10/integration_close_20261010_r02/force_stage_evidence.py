"""仅补暂存本任务被忽略的原始日志，并验证Git对象保留所有证据字节。"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
evidence = ROOT / "report/evidence/S2B-T10"
target = evidence / "integration_close_20261010_r02"
assert evidence.is_dir() and not target.exists()
files = [path for path in sorted(evidence.rglob("*")) if path.is_file()]
missing = []
for path in files:
    relative = path.relative_to(ROOT).as_posix()
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", relative], cwd=ROOT, capture_output=True)
    if tracked.returncode != 0:
        assert path.suffix == ".log", relative
        missing.append(relative)
if missing:
    subprocess.run(["git", "add", "-f", "--", *missing], cwd=ROOT, check=True, capture_output=True)
binding = []
for path in files:
    relative = path.relative_to(ROOT).as_posix()
    indexed = subprocess.check_output(["git", "show", ":" + relative], cwd=ROOT)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert hashlib.sha256(indexed).hexdigest() == actual, relative
    binding.append({"path": relative, "sha256": actual})
subprocess.run(["git", "diff", "--cached", "--check"], cwd=ROOT, check=True, capture_output=True)
target.mkdir()
(target / "git_object_binding.json").write_text(json.dumps({"source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "reason": "初次普通git add遵循全局*.log忽略规则；原始日志必须可由Git恢复，按明确本任务路径补暂存。未强制加入缓存/临时目录。",
            "force_added_original_logs": missing, "all_evidence_bytes_match_index": binding}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"FORCE_ADDED_ORIGINAL_LOGS={len(missing)}; EVIDENCE_GIT_OBJECT_MATCHES={len(binding)}")
