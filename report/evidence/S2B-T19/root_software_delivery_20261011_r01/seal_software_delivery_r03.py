"""将所有冻结外部产物标为输入，封存两次包装失败及最终真实检查。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path.cwd()
RUN = ROOT / "report/evidence/S2B-T19/root_software_delivery_20261011_r01"
REL = RUN.relative_to(ROOT)


def sha(path):
    """核对原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    """禁止覆盖已有记录。"""
    p = RUN / name
    assert not p.exists()
    with p.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return p


def seal(value, name):
    """绑定当前已结束的本轮文件和固定上游输入。"""
    known = {x["path"] for x in value["files"]}
    for p in sorted(RUN.rglob("*")):
        if p.is_file() and p.relative_to(ROOT).as_posix() not in known:
            role = "source" if p.suffix == ".py" else "log" if p.suffix == ".log" else "result"
            value["files"].append({"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": role})
    return save(name, value)


assert RUN.is_dir() and not RUN.is_symlink()
j = json.loads((RUN / "delivery_manifest_r02.json").read_text(encoding="utf-8"))
for x in j["files"]:
    if not Path(x["path"]).is_relative_to(REL) and x["role"] != "source":
        x["role"] = "input"
j["limitations"].append("根r02还漏改外部artifact角色，实际evidence2日志保留；r03将所有外部非source冻结产物视为输入。")
probe = seal(j, "delivery_manifest_r03.json")
results = []
for mode, expected in [("evidence", 0), ("inputs", 2)]:
    args = [sys.executable, "-X", "utf8", "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", str(probe)]
    x = subprocess.run(args, cwd=ROOT, capture_output=True)
    p = RUN / ("packaging_" + mode + "_r03.log")
    assert not p.exists()
    p.write_bytes(x.stdout + b"\nSTDERR\n" + x.stderr)
    results.append({"command": args, "native_exit_code": x.returncode, "log_path": p.relative_to(ROOT).as_posix(), "log_sha256": sha(p)})
    assert x.returncode == expected, x.stdout.decode("utf-8")
save("packaging_result_r03.json", {"status": "PACKAGING_ONLY_COMPLETE_WITH_DEPENDENCIES_BLOCKED", "commands": results,
    "limitation": "只封存软件G2；root snapshot重绑定不是S3平台或实际compat/cold/cache/model批准。"})
final = seal(j, "delivery_manifest_r04.json")
print(json.dumps({"status": "STOP_SEALED_SOFTWARE_G2_ONLY", "files": len(j["files"]), "manifest_sha256": sha(final)}, ensure_ascii=False))
