"""修复外部上游证据角色，原首清单及实际包装失败完整保留。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path.cwd()
RUN = ROOT / "report/evidence/S2B-T19/root_software_delivery_20261011_r01"
REL = RUN.relative_to(ROOT)


def sha(path):
    """记录原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, obj):
    """只新增精确名称。"""
    p = RUN / name
    assert not p.exists()
    with p.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return p


assert RUN.is_dir() and not RUN.is_symlink()
first = RUN / "delivery_manifest.json"
j = json.loads(first.read_text(encoding="utf-8"))
args = [sys.executable, "-X", "utf8", "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", str(first)]
x = subprocess.run(args, cwd=ROOT, capture_output=True)
assert x.returncode == 2
failure = RUN / "packaging_failure_r01.log"
assert not failure.exists()
failure.write_bytes(x.stdout + b"\nSTDERR\n" + x.stderr)
save("packaging_failure_r01.json", {"command": args, "native_exit_code": x.returncode,
    "log_path": failure.relative_to(ROOT).as_posix(), "log_sha256": sha(failure),
    "reason": "新证据目录需把冻结上游result/log作为input，原件不是本轮新result/log。首宿主执行返回1，内层未单独记录；此次原清单复现原生2。"})
for row in j["files"]:
    if not Path(row["path"]).is_relative_to(REL) and row["role"] in {"result", "log"}:
        row["role"] = "input"
known = {x["path"] for x in j["files"]}
for p in sorted(RUN.rglob("*")):
    if p.is_file() and p.relative_to(ROOT).as_posix() not in known:
        role = "source" if p.suffix == ".py" else "log" if p.suffix == ".log" else "result"
        j["files"].append({"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": role})
j["checks"].append({"name": "根归档首清单包装失败保留", "status": "FAIL", "command": " ".join(args),
    "exit_code": 2, "reason": "原清单外部result/log角色错误；只在新清单改为上游input，不改原件。"})
second = save("delivery_manifest_r02.json", j)
results = []
for mode, expected in [("evidence", 0), ("inputs", 2)]:
    args = [sys.executable, "-X", "utf8", "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", str(second)]
    x = subprocess.run(args, cwd=ROOT, capture_output=True)
    log = RUN / ("packaging_" + mode + "_r02.log")
    assert not log.exists()
    log.write_bytes(x.stdout + b"\nSTDERR\n" + x.stderr)
    results.append({"command": args, "native_exit_code": x.returncode, "log_path": log.relative_to(ROOT).as_posix(), "log_sha256": sha(log)})
    assert x.returncode == expected, x.stdout.decode("utf-8")
save("packaging_result_r02.json", {"status": "PACKAGING_ONLY_COMPLETE_WITH_DEPENDENCIES_BLOCKED", "commands": results,
    "reason": "evidence0仅目录/hash，inputs2因候选未freeze、旧FAIL与正式compat/cold/cache/硬件未执行。"})
known = {x["path"] for x in j["files"]}
for p in sorted(RUN.rglob("*")):
    if p.is_file() and p.relative_to(ROOT).as_posix() not in known:
        j["files"].append({"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": "log" if p.suffix == ".log" else "result"})
final = save("delivery_manifest_r03.json", j)
print(json.dumps({"status": "STOP_SEALED_SOFTWARE_G2_ONLY", "files": len(j["files"]), "manifest_sha256": sha(final)}, ensure_ascii=False))
