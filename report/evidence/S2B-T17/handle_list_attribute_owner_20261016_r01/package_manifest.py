"""绑定属性值所有权修复和独立微型验证，不改写原始记录。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
paths = sorted(path for path in RUN.rglob("*") if path.is_file() and path.name != "delivery_manifest.json")
paths += [ROOT / name for name in ("verification/s15_job_guard.py", "verification/test_s15_direct_vivado_bitgen.py",
                                  "verification/s2b_process_supervisor.py", "verification/test_s2b_process_supervisor.py")]
manifest = {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T17", "run_id": RUN.name,
    "source_commit": "c2ed441aa012966f93c1905f03aeb6ed1d5cfd56",
    "evidence_dir": RUN.relative_to(ROOT).as_posix(), "interfaces": [],
    "interfaces_not_applicable_reason": "本小任务修复操作系统进程属性数组的生命周期，不更改PS/PL/模型接口；RTL和实物另验。",
    "files": [{"path": path.relative_to(ROOT).as_posix(),
               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "role": "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result",
               "keep_reason": "保留实际源码、旧所有权探针、初稿失败及独立真实微型回归原件。"} for path in paths],
    "checks": [{"name": "legacy_lifetime_probe", "status": "PASS", "exit_code": 0,
                "command": "python -B legacy_lifetime_probe.py（记录的旧HEAD 9bcf023）",
                "reason": "真实Initialize/Delete、模拟Update后GC令数组weakref失效；未复现WinError87。"},
               {"name": "targeted_owner_fixture", "status": "PASS", "exit_code": 0,
                "command": "python -B -m unittest verification.test_s15_direct_vivado_bitgen.DirectSpawnFixtureTests.test_handle_list_value_owner_lives_until_attribute_list_delete -v",
                "reason": "独立目标测试1项通过。"},
               {"name": "direct_and_supervisor_regression", "status": "PASS", "exit_code": 0,
                "command": "串行python -B -m unittest DirectSpawnFixtureTests；python -B -m unittest verification.test_s2b_process_supervisor",
                "reason": "独立direct9项和supervisor10项通过，原始命令与日志保留。"},
               {"name": "rtl_and_hardware", "status": "NOT_RUN", "exit_code": None, "command": None,
                "reason": "本Run没有XSim或硬件操作。"}],
    "limitations": ["旧probe模拟Update，没有同址复用或WinError87复现。", "独审PASS仅为指定源码和轻量回归。"],
    "tool_versions": {"Python": "3.12.10", "psutil": "7.2.2", "OS": "Windows"},
}
(RUN / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
