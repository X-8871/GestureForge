"""核对最终任务暂存范围、字节恢复和被审控制文本的Git处理。"""

from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time


def main():
    started = time.perf_counter()
    root = Path.cwd()
    temporary = root / "tmp/2B/S2B-T06"
    previous = temporary / "verify_candidate_index.py"
    assert previous.is_file()
    spec = importlib.util.spec_from_file_location("index_helpers", previous)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    run_id = sys.argv[1]
    assert run_id.isalnum()
    shared = len(sys.argv) == 3 and sys.argv[2] == "shared"
    environment = dict(os.environ)
    index = temporary / ("final_index_" + run_id)
    baseline = helper.run(["git", "rev-parse", "HEAD"], root).stdout.decode().strip()
    assert baseline == "00f51b664fefdaf0c63e605af2427333579fa5f3", baseline
    before = helper.run(["git", "diff", "--cached", "--binary"], root).stdout
    if not shared:
        assert not index.exists() and not before
        environment["GIT_INDEX_FILE"] = str(index)
        helper.run(["git", "read-tree", "HEAD"], root, environment)
    allow = {".gitattributes", ".codex/STATE.md"}
    binding = {}
    origins = {}
    for name in ["ps_smoke_20261008_r01", "ps_smoke_offline_freeze_20261009_r01", "ps_smoke_integration_20261009_r01", "ps_smoke_integration_20261009_r02", "ps_smoke_submission_20261009_r01"]:
        rel = "report/evidence/S2B-T06/" + name + "/delivery_manifest.json"
        path = root / rel
        if name == "ps_smoke_submission_20261009_r01" and not path.exists():
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        expected_origin = "90652b45ef31e763bd3e6f7527e2fd080ece61a8" if name == "ps_smoke_20261008_r01" else baseline
        assert obj["source_commit"] == expected_origin, (name, obj["source_commit"])
        helper.run(["git", "cat-file", "-e", expected_origin + "^{commit}"], root)
        origins[name] = expected_origin
        allow.add(rel)
        binding[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        for item in obj["files"] + obj["interfaces"]:
            old = binding.setdefault(item["path"], item["sha256"])
            assert old == item["sha256"]
            if item["path"].startswith("report/evidence/S2B-T06/") or item.get("role") == "source":
                if item["path"] != "verification/check_stage_delivery.py":
                    allow.add(item["path"])
    formal = "docs/obsidian-project/04-提交材料/阶段验收/stage2b_ps_smoke_offline_freeze_20261009.md"
    allow.add(formal)
    paths = sorted(allow)
    assert all(" " not in item and "\n" not in item for item in paths)
    payload = b"".join(item.encode("utf-8") + b"\0" for item in paths)
    ignored_run = helper.run(["git", "check-ignore", "-z", "--stdin"], root, environment, payload, False)
    assert ignored_run.returncode in (0, 1)
    ignored = set(ignored_run.stdout.decode("utf-8").rstrip("\0").split("\0")) - {""}
    if not shared:
        for forced in [False, True]:
            selected = [item for item in paths if (item in ignored) == forced]
            if selected:
                args = ["git", "add"] + (["-f"] if forced else []) + ["--pathspec-from-file=-", "--pathspec-file-nul"]
                helper.run(args, root, environment, b"".join(item.encode("utf-8") + b"\0" for item in selected))
    staged = helper.run(["git", "diff", "--cached", "--name-only", "-z"], root, environment).stdout.decode("utf-8").rstrip("\0").split("\0")
    assert set(staged) == allow, (set(staged) - allow, allow - set(staged))
    raw = helper.batch_hashes(sorted(binding), root, environment)
    restored = helper.batch_hashes(sorted(binding), root, environment, True)
    differences = [item for item in binding if raw[item] != binding[item] or restored[item] != binding[item]]
    assert not differences, differences
    scope_path = root / "report/evidence/S2B-T06/ps_smoke_integration_20261009_r01/review_scope.json"
    scope = json.loads(scope_path.read_text(encoding="utf-8"))
    controls = []
    for item in scope["controls"]:
        content = (root / item["snapshot"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == item["sha256"]
        assert (root / item["path"]).read_bytes() == content
        expected_oid = helper.run(["git", "hash-object", "--path=" + item["path"], "--stdin"], root, environment, content).stdout.decode().strip()
        staged_oid = helper.run(["git", "rev-parse", ":" + item["path"]], root, environment).stdout.decode().strip()
        assert expected_oid == staged_oid, item["path"]
        filtered = helper.run(["git", "cat-file", "--filters", ":" + item["path"]], root, environment).stdout
        controls.append({"path": item["path"], "reviewed_sha256": item["sha256"], "expected_git_blob": expected_oid,
                         "staged_git_blob": staged_oid, "restored_sha256": hashlib.sha256(filtered).hexdigest(),
                         "reviewed_text_matches_git_processing": True})
    check = helper.run(["git", "diff", "--cached", "--check"], root, environment, required=False)
    log = temporary / ("final_index_" + run_id + "_whitespace.log")
    with log.open("xb") as output:
        output.write(check.stdout + check.stderr)
    assert check.returncode == 0, str(log)
    assert helper.run(["git", "rev-parse", "HEAD"], root).stdout.decode().strip() == baseline
    assert helper.run(["git", "diff", "--cached", "--binary"], root).stdout == before
    receipt = {"status": "PASS_FINAL_INDEX", "mode": "shared" if shared else "private", "baseline_commit": baseline,
               "manifest_source_commits": origins,
               "staged_files": len(paths), "force_ignored_files": len(ignored), "bound_files": len(binding),
               "raw_and_restored_differences": [], "whitespace_exit_code": check.returncode,
               "whitespace_log": str(log), "whitespace_log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
               "controls": controls, "elapsed_seconds": time.perf_counter() - started,
               "shared_index_unchanged": True, "allowlist": paths, "hardware_execution": "NOT_RUN"}
    with (temporary / ("final_index_" + run_id + "_receipt.json")).open("x", encoding="utf-8", newline="\n") as output:
        json.dump(receipt, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps({key: value for key, value in receipt.items() if key != "allowlist"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
