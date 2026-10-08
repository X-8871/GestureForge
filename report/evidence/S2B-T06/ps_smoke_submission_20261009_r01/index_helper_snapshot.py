"""在独立Git暂存文件中核对本任务范围、原始字节和恢复滤镜。"""

from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time


def run(args, root, environment=None, data=None, required=True):
    result = subprocess.run(args, cwd=root, env=environment, input=data, capture_output=True)
    if required and result.returncode:
        raise RuntimeError((args, result.returncode, result.stderr.decode("utf-8", "replace")))
    return result


def batch_hashes(paths, root, environment, filtered=False):
    arguments = ["git", "cat-file", "--batch"]
    if filtered:
        arguments.append("--filters")
    lines = [":"+path+(" "+path if filtered else "") for path in paths]
    raw = run(arguments, root, environment, ("\n".join(lines)+"\n").encode("utf-8")).stdout
    offset = 0
    values = {}
    for path in paths:
        end = raw.index(b"\n", offset)
        fields = raw[offset:end].split()
        assert len(fields) == 3 and fields[1] == b"blob", (path, fields)
        size = int(fields[2])
        body = raw[end+1:end+1+size]
        assert len(body) == size and raw[end+1+size:end+2+size] == b"\n"
        values[path] = hashlib.sha256(body).hexdigest()
        offset = end+2+size
    assert offset == len(raw)
    return values


def main():
    root = Path.cwd()
    temporary = root / "tmp/2B/S2B-T06"
    assert temporary.is_dir()
    run_id = sys.argv[1]
    assert run_id.isalnum()
    index = temporary / ("candidate_index_"+run_id)
    assert not index.exists()
    before_index = run(["git", "diff", "--cached", "--binary"], root).stdout
    assert not before_index
    before_head = run(["git", "rev-parse", "HEAD"], root).stdout
    environment = dict(os.environ)
    environment["GIT_INDEX_FILE"] = str(index)
    run(["git", "read-tree", "HEAD"], root, environment)
    allow = {".gitattributes", ".codex/STATE.md",
             "docs/obsidian-project/04-提交材料/阶段验收/stage2b_ps_smoke_offline_freeze_20261009.md"}
    binding = {}
    for rel in ("report/evidence/S2B-T06/ps_smoke_20261008_r01/delivery_manifest.json",
                "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01/delivery_manifest.json"):
        manifest = root / rel
        obj = json.loads(manifest.read_text(encoding="utf-8"))
        allow.add(rel)
        binding[rel] = hashlib.sha256(manifest.read_bytes()).hexdigest()
        for item in obj["files"] + obj["interfaces"]:
            if item["path"] in binding:
                assert binding[item["path"]] == item["sha256"]
            binding[item["path"]] = item["sha256"]
            if item["path"].startswith("report/evidence/S2B-T06/") or item.get("role") == "source":
                if item["path"] != "verification/check_stage_delivery.py":
                    allow.add(item["path"])
    paths = sorted(allow)
    assert all(" " not in path and "\n" not in path for path in paths)
    stdin = b"".join(path.encode("utf-8")+b"\0" for path in paths)
    ignore = run(["git", "check-ignore", "-z", "--stdin"], root, environment, stdin, False)
    assert ignore.returncode in (0,1)
    ignored = set(ignore.stdout.decode("utf-8").rstrip("\0").split("\0")) - {""}
    started = time.perf_counter()
    for forced in (False, True):
        selected = [path for path in paths if (path in ignored) == forced]
        if not selected:
            continue
        args = ["git", "add"] + (["-f"] if forced else []) + ["--pathspec-from-file=-", "--pathspec-file-nul"]
        run(args, root, environment, b"".join(path.encode("utf-8")+b"\0" for path in selected))
    staged = run(["git", "diff", "--cached", "--name-only", "-z"], root, environment).stdout.decode("utf-8").rstrip("\0").split("\0")
    assert set(staged) == allow, (set(staged)-allow, allow-set(staged))
    raw = batch_hashes(sorted(binding), root, environment)
    restored = batch_hashes(sorted(binding), root, environment, True)
    differences = [path for path, expected in binding.items() if raw[path] != expected or restored[path] != expected]
    check = run(["git", "diff", "--cached", "--check"], root, environment, required=False)
    log = temporary / ("candidate_index_"+run_id+"_whitespace.log")
    with log.open("xb") as output:
        output.write(check.stdout+check.stderr)
    assert run(["git", "diff", "--cached", "--binary"], root).stdout == before_index
    assert run(["git", "rev-parse", "HEAD"], root).stdout == before_head
    receipt = {"status": "PASS_PRIVATE_INDEX" if not differences and check.returncode == 0 else "CHECKS_REQUIRED",
               "staged_files": len(paths), "force_ignored_files": len(ignored), "bound_files": len(binding),
               "raw_and_restored_differences": differences, "whitespace_exit_code": check.returncode,
               "whitespace_log": str(log), "whitespace_log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
               "elapsed_seconds": time.perf_counter()-started, "index": str(index),
               "shared_head_unchanged": True, "shared_index_unchanged": True, "allowlist": paths,
               "hardware_execution": "NOT_RUN"}
    output = temporary / ("candidate_index_"+run_id+"_receipt.json")
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({key: value for key,value in receipt.items() if key != "allowlist"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
