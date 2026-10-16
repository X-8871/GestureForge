"""封装因已知监督器边界被拒绝启动的准备记录。"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
preflight = json.loads((RUN / "preflight/delivery_manifest.json").read_text(encoding="utf-8"))
paths = [path for path in RUN.rglob("*") if path.is_file() and path != RUN / "delivery_manifest.json"]
manifest = {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T11", "run_id": RUN.name,
    "source_commit": "abe095e1bff4586193149bbe837bc9bd855b2a03",
    "evidence_dir": RUN.relative_to(ROOT).as_posix(), "interfaces": preflight["interfaces"],
    "files": [{"path": path.relative_to(ROOT).as_posix(),
               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "role": "source" if path.suffix in (".py", ".sv", ".prj", ".tcl", ".ini") else "result",
               "keep_reason": "保留被拒绝执行的实际准备输入、静态诊断和mock检查；不作原生执行证据。"}
              for path in sorted(paths)],
    "checks": [{"name": "native_execution_admission", "status": "BLOCKED", "command": None,
                "exit_code": None, "reason": "独立Reviewer认为已知旧监督器终态资源/期限缺陷阻断重型诊断。"},
               {"name": "rtl_matrix", "status": "NOT_RUN", "command": None, "exit_code": None,
                "reason": "尚未启动compile/elaborate/simulation；预备输入不是动态结果。"}],
    "limitations": ["本Run从未启动原生工具或硬件。", "后续须新RunId绑定新监督器G2，不覆盖本Run。"],
    "tool_versions": {"Python_packager": sys.version}}
(RUN / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
