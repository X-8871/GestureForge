"""用冻结快照封装微型运行历史，并保留正式审查阻断。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def sha(path):
    """计算原始文件字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(HERE / "delivery_manifest.json") == "fd47ec8d8539754ed736f1c791f18ffc9fcc91dbe2485dff87cd05145bcabe7b"
for suffix in ("r02", "r03"):
    run = HERE.parent / ("monitored_job_drain_20261016_" + suffix)
    manifest = json.loads((run / "delivery_manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        if entry["path"].startswith("verification/"):
            path = run / "source_snapshot" / path.name
        assert path.is_file() and sha(path) == entry["sha256"], entry["path"]
    files = [path for path in run.rglob("*") if path.is_file()
             and path != run / "delivery_manifest_historical.json"]
    if suffix == "r03":
        prior = HERE.parent / "monitored_job_drain_20261016_r01"
        files.extend(path for path in prior.rglob("*") if path.is_file())
    manifest["files"] = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
                          "role": "input" if run not in path.parents else "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result",
                          "keep_reason": "保留真实历史运行与冻结快照；r01仅原始日志，不能推断其未保存的源码版本。"}
                         for path in sorted(files)]
    manifest["limitations"].append("本补充清单只绑定冻结快照，不把当前工作树当历史被测输入；原清单与原始运行摘要不改。")
    if suffix == "r03":
        for check in manifest["checks"]:
            if check["name"] == "independent_review":
                check.update({"status": "BLOCKED", "command": None, "exit_code": None,
                              "reason": "独立审查CHANGES_REQUIRED：配置参数可绕过资源/排空硬约束，待新Run修复。"})
    (run / "delivery_manifest_historical.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
