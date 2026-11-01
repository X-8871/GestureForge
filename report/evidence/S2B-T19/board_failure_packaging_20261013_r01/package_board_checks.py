"""绑定失败运行包装核验的实际退出码与原始日志。"""
from pathlib import Path
import hashlib
import json
import platform
import subprocess

root = Path.cwd()
out = root / "report/evidence/S2B-T19/board_failure_packaging_20261013_r01"
assert out.is_dir() and not (out / "delivery_manifest.json").exists()
rows = json.loads((out / "execution.json").read_text(encoding="utf-8"))["checks"]
assert len(rows) == 8 and all(r["native_exit_code"] == r["expected_exit_code"] for r in rows)
(out / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = [{"path": p.relative_to(root).as_posix(), "sha256": sha(p),
          "role": "source" if p.suffix == ".py" else "result"}
         for p in sorted(out.iterdir()) if p.is_file()]
for run_id in sorted({r["run_id"] for r in rows}):
    p = root / "report/evidence/S2B-T19" / run_id / "delivery_manifest.json"
    files.append({"path": p.relative_to(root).as_posix(), "sha256": sha(p), "role": "input"})
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T19",
    "run_id": out.name, "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
    "evidence_dir": out.relative_to(root).as_posix(), "interfaces": [],
    "interfaces_not_applicable_reason": "只读包装核查已结束的真实失败运行，不修改或冻结板卡接口。",
    "files": files, "tool_versions": {"python": platform.python_version()},
    "checks": [{"name": r["run_id"] + "_" + r["mode"], "status": "PASS" if r["native_exit_code"] == 0 else "BLOCKED",
                "exit_code": r["native_exit_code"] if r["native_exit_code"] == 0 else None,
                "command": " ".join(r["command"]),
                "reason": "inputs真实原生2，失败和未执行条件保持阻断；不是物理功能成功。" if r["native_exit_code"] else "原件与清单哈希检查通过。"}
               for r in rows],
    "limitations": ["r03扫描链全零；r04目标拓扑失败并在卸载无进度后终止自有SDK。",
                    "evidence0仅表示包装完整，inputs2为预期阻断；PS初始化、缓存、模型及阶段验收未通过。"]}
(out / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(sha(out / "delivery_manifest.json"))
