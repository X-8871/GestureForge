"""隔离记录包装检查器的真实进程退出码，避免Windows宿主归一化。"""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[4]
RUN = Path(__file__).absolute().parent
PRIMARY = "report/evidence/S2B-T16/jtag_offline_20261011_r02/delivery_manifest.json"
results = []
for mode in ("evidence", "inputs"):
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", PRIMARY]
    process = subprocess.run(command, cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"), capture_output=True)
    for suffix, raw in (("stdout", process.stdout), ("stderr", process.stderr)):
        with (RUN / f"{mode}_{suffix}.log").open("xb") as stream:
            stream.write(raw)
    results.append({"mode": mode, "command": command, "native_exit_code": process.returncode,
                    "decoded": json.loads(process.stdout.decode("utf-8"))})
with (RUN / "native_packaging_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump({"checks": results, "hardware_execution": "NOT_RUN"}, stream, ensure_ascii=False, indent=2); stream.write("\n")
files = []
for path in sorted(RUN.iterdir()):
    files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "role": "source" if path.suffix == ".py" else ("log" if path.suffix == ".log" else "result")})
for name in (PRIMARY, "verification/check_stage_delivery.py"):
    files.append({"path": name, "sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), "role": "input"})
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T16", "run_id": RUN.name,
    "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
    "evidence_dir": RUN.relative_to(ROOT).as_posix(), "interfaces": [],
    "interfaces_not_applicable_reason": "只对已生成的主交付清单记录包装检查器真实退出码，不消费新业务接口。",
    "files": files, "tool_versions": {"Python": platform.python_version()},
    "checks": [{"name": "主交付evidence包装", "status": "PASS" if results[0]["native_exit_code"] == 0 else "FAIL",
                "command": "python -B verification/check_stage_delivery.py --mode evidence --manifest " + PRIMARY, "exit_code": results[0]["native_exit_code"]},
               {"name": "主交付inputs依赖", "status": "BLOCKED", "command": "python -B verification/check_stage_delivery.py --mode inputs --manifest " + PRIMARY,
                "exit_code": results[1]["native_exit_code"], "reason": "主清单候选接口未冻结，实板与独立审查均NOT_RUN；不宣称部署就绪。"}],
    "limitations": ["仅包装检查原生结果，不代表G2/G3或完整2B通过。", "Windows宿主先前显示1；此处明确保存子进程真实退出码。"]}
with (RUN / "delivery_manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2); stream.write("\n")
print(json.dumps({"native_exit_codes": [r["native_exit_code"] for r in results]}, ensure_ascii=False))
raise SystemExit(0 if [r["native_exit_code"] for r in results] == [0, 2] else 2)
