"""在不改写失败原件的前提下绑定该Run实际源码快照。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
PREFLIGHT = RUN.parent / "control_r18_xsim_preflight_20261016_r01"


def sha(path):
    """按原字节计算哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(RUN / "result.json") == "e9e1a08bac481c22de5d1b00bdc4a7c942c64e54b6fbe901e8689afd9a62a556"
assert sha(RUN / "delivery_manifest.json") == "1bb8722c668fbcb59d118154d568cb85783a61e1c549e086260fa8d798d367af"
result = json.loads((RUN / "result.json").read_text(encoding="utf-8"))
manifest = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
for entry in result["sources"]:
    if entry["path"].startswith(("src/", "sim/")):
        actual = PREFLIGHT / "source_snapshot" / Path(entry["path"]).name
    elif entry["path"].startswith("verification/"):
        actual = RUN / "source_snapshot" / Path(entry["path"]).name
    else:
        actual = ROOT / entry["path"]
    assert sha(actual) == entry["sha256"], entry["path"]
paths = {entry["path"]: ROOT / entry["path"] for entry in manifest["files"]
         if not entry["path"].startswith(("src/", "sim/", "verification/"))}
for path in RUN.rglob("*"):
    if path.is_file() and path.name != "delivery_manifest_historical.json":
        paths[path.relative_to(ROOT).as_posix()] = path
manifest["files"] = [
    {"path": name, "sha256": sha(path),
     "role": "source" if path.suffix in (".py", ".cmd", ".sv", ".prj", ".tcl", ".ini")
             else "input" if RUN not in path.parents else "log" if path.suffix == ".log" else "result",
     "keep_reason": "保留本Run原始失败输出和实际输入快照，不把后续工作树当作历史运行输入。"}
    for name, path in sorted(paths.items())]
for stage in result["stages"][:2]:
    manifest["checks"].append({"name": stage["name"] + "_native",
                               "status": "PASS", "exit_code": stage["native_exit_code"],
                               "command": " ".join(stage["command"]),
                               "reason": "原生退出0且资源/Job监督PASS，清理确认。"})
manifest["checks"].append({"name": "rtl_simulation", "status": "NOT_RUN", "exit_code": None,
                           "command": None, "reason": "CreateProcessW创建root前WinError87，未启动原生XSim。"})
manifest["limitations"].append("原始结果和清单按字节保留；本补充清单只用冻结快照绑定历史源码，不把当前启动器当历史输入。")
(RUN / "delivery_manifest_historical.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
