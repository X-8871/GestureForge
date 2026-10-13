"""保留初次清单，按检查器要求使用FAIL记录真实非零inputs退出码。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[4]
HERE = Path(__file__).absolute().parent
OUT = ROOT / "report/evidence/S2B-T19/pc_nvlist_review_20261013_r01"
CHECK = HERE / "package_check_r02"
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
manifest_path = OUT / "delivery_manifest.json"
assert OUT.is_dir() and manifest_path.is_file()
assert sha(manifest_path) == "8f7837c7c1d56adc131f2df19f246a32ce823857ef63792822492b213ad4ea42"
assert not CHECK.exists()
raw = manifest_path.read_bytes()
original = OUT / "delivery_manifest_initial.json"
assert not original.exists()
with original.open("xb") as stream:
    stream.write(raw)
snapshot = OUT / "collector_sources/repair_package.py"
assert snapshot.parent.is_dir() and not snapshot.exists()
shutil.copyfile(Path(__file__), snapshot)
manifest = json.loads(raw.decode("utf-8"))
changed = 0
for check in manifest["checks"]:
    if check["name"] == "independent_G1_inputs":
        assert check["status"] == "BLOCKED" and check["exit_code"] == 2
        check["status"] = "FAIL"
        changed += 1
assert changed == 1
for path, role, reason in ((original, "result", "初次独审清单：BLOCKED携带退出码2违反检查器schema，保留原字节。"),
                           (snapshot, "source", "当前包装修复脚本快照，只修复清单状态表达，不改变审查原件及源码。")):
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role, "keep_reason": reason})
previous = json.loads((HERE / "package_check_r01/execution.json").read_text(encoding="utf-8"))
manifest["checks"].append({"name": "initial_review_package_schema", "status": "FAIL",
    "command": subprocess.list2cmdline(previous["command"]), "exit_code": previous["exit_code"],
    "reason": "初次独审包装使用BLOCKED+exit_code2，检查器要求BLOCKED的exit_code为null；现用FAIL如实记录非零退出码，原清单和日志保留。"})
manifest["limitations"].append("包装schema失败与最终软件PASS区分；两次包装检查原日志及执行收据位于tmp/2B/S2B-T19/pc_nvlist_review_20261013_r01/package_check_r01和package_check_r02。")
assert manifest_path.is_file() and manifest_path.read_bytes() == raw
with manifest_path.open("w", encoding="utf-8", newline="\n") as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
CHECK.mkdir()
command = [sys.executable, "-X", "utf8", "-B", "verification/check_stage_delivery.py", "--mode", "evidence",
           "--manifest", manifest_path.relative_to(ROOT).as_posix()]
started = time.monotonic()
result = subprocess.run(command, cwd=ROOT, capture_output=True)
for name, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
    with (CHECK / name).open("xb") as stream:
        stream.write(data)
receipt = json.loads((OUT / "review_receipt.json").read_text(encoding="utf-8"))
assert sha(OUT / "review_receipt.json") == "ee6cf6fe55daf89225b9746ba4d595fdd26042cc5e1513c9159b1e40edc6bf21"
assert {path: sha(ROOT / path) for path in receipt["source_sha256"]} == receipt["source_sha256"]
execution = {"command": command, "exit_code": result.returncode, "elapsed_seconds": time.monotonic() - started,
    "manifest_path": str(manifest_path), "manifest_sha256": sha(manifest_path),
    "source_sha256": receipt["source_sha256"], "receipt_sha256": sha(OUT / "review_receipt.json"),
    "stdout_sha256": sha(CHECK / "stdout.log"), "stderr_sha256": sha(CHECK / "stderr.log"),
    "actual_hardware_calls": 0, "repeated_tests": 0}
with (CHECK / "execution.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(execution, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"exit_code": result.returncode, "manifest_sha256": execution["manifest_sha256"],
    "files_bound": len(manifest["files"]), "check_execution": str(CHECK / "execution.json")}, ensure_ascii=False))
sys.exit(result.returncode)
