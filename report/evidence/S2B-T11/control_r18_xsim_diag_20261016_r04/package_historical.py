"""保留精确断言失败原件及启动观测，绑定实际冻结输入。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
PREFLIGHT = RUN / "preflight"


def sha(path):
    """计算原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(RUN / "result.json") == "11edaefc962a7f7d8b3710323f085be7902c2136d52ad35eedb421ac0983604a"
assert sha(RUN / "delivery_manifest.json") == "190842085c3678f304a67451c36164a79162807bcd6090d1b79e7db565692585"
result = json.loads((RUN / "result.json").read_text(encoding="utf-8"))
manifest = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
for entry in result["sources"]:
    if entry["path"].startswith(("src/", "sim/")):
        path = PREFLIGHT / "source_snapshot" / Path(entry["path"]).name
    elif entry["path"].startswith("verification/"):
        path = RUN / "source_snapshot" / Path(entry["path"]).name
    else:
        path = ROOT / entry["path"]
    assert path.is_file() and sha(path) == entry["sha256"]
paths = {entry["path"]: ROOT / entry["path"] for entry in manifest["files"]
         if not entry["path"].startswith(("src/", "sim/", "verification/"))}
for path in RUN.rglob("*"):
    if path.is_file() and path != RUN / "delivery_manifest_historical.json":
        paths[path.relative_to(ROOT).as_posix()] = path
manifest["files"] = [{"path": name, "sha256": sha(path),
                      "role": "source" if path.suffix in (".py", ".sv", ".cmd", ".prj", ".tcl", ".ini")
                              else "artifact" if path.suffix == ".wdb" else "input" if RUN not in path.parents
                              else "log" if path.suffix in (".log", ".jou", ".raw") else "result",
                      "keep_reason": "保留失败时原始AW/epoch波形，尚未解析，不以其宣布根因。" if path.suffix == ".wdb"
                                     else "绑定原生启动快照、实际源码快照和精确断言失败，原件不改。"}
                     for name, path in sorted(paths.items())]
manifest["limitations"].append("原psutil就绪false保留；补充Windows完整原生快照ready=true，未忽略未知名称或降低资源门槛。")
manifest["limitations"].append("AW_ONLY_SLOT于最大epoch持续force后失败；根因须短force/release对照，不代表RTL矩阵或阶段通过。")
(RUN / "delivery_manifest_historical.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
