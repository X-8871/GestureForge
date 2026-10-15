"""保留原始失败结果，补充绑定历史源码和必要波形。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
PREFLIGHT = RUN.parent / "control_r18_xsim_preflight_20261016_r01"


def sha(path):
    """按原字节计算哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(RUN / "result.json") == "4031d55b42f40a1af7776a7569f0fbcacd06a9e05d1ad59ab64edb1208b78f11"
assert sha(RUN / "delivery_manifest.json") == "a4bc5b77c7f58b76ff145d85b5ec26b111078037309ebfe319b10887c924c3a3"
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
             else "artifact" if path.suffix == ".wdb"
             else "input" if RUN not in path.parents else "log" if path.suffix in (".log", ".jou") else "result",
     "keep_reason": "保留断言失败时的原始波形用于定位AW槽状态；尚未解析波形，不以它宣称根因。"
                    if path.suffix == ".wdb" else "保留本Run实际输入和失败输出，不把后续工作树当历史输入。"}
    for name, path in sorted(paths.items())]
for stage in result["stages"]:
    assert stage["status"] == "PASS" and stage["native_exit_code"] == 0
    manifest["checks"].append({"name": stage["name"] + "_native",
                               "status": "PASS", "exit_code": stage["native_exit_code"],
                               "command": " ".join(stage["command"]),
                               "reason": "原生退出0且资源/Job监督PASS，清理确认；不代表断言通过。"})
manifest["checks"].append({"name": "rtl_assertion_matrix", "status": "FAIL", "exit_code": 1,
                           "command": "execute_xsim.py",
                           "reason": "XSim已执行；cycle=3308、directed=130、integration=0出现Fatal，驱动退出1，无完整PASS覆盖。"})
manifest["limitations"].append("原始结果/清单不改写；Fatal中文后缀损坏，仅可确认AW相关文本，不能据此确定断言或根因。")
(RUN / "delivery_manifest_historical.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
