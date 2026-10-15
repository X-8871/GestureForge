"""绑定最终进程保护源码和独立微型回归原始证据。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
sources = ["verification/s15_job_guard.py", "verification/test_s15_direct_vivado_bitgen.py",
           "verification/s2b_process_supervisor.py", "verification/test_s2b_process_supervisor.py",
           "verification/test_s2b_control_csr_rtl.py"]
paths = sorted(path for path in RUN.rglob("*") if path.is_file() and path.name != "delivery_manifest.json")
paths += [ROOT / name for name in sources]
for name in ("tool_versions.json", "python_executable_hash.txt"):
    paths.append(RUN.parent / "control_r18_process_supervisor_20261016_r01" / name)
manifest = {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T11", "run_id": RUN.name,
    "source_commit": "43f9b46f3ba0d4341b464c593293d1576fa8a3d6",
    "evidence_dir": RUN.relative_to(ROOT).as_posix(), "interfaces": [],
    "interfaces_not_applicable_reason": "本小任务验证操作系统进程隔离与资源失败关闭，不修改总线和模型语义，不代替CSR业务验证。",
    "files": [{"path": path.relative_to(ROOT).as_posix(),
               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "role": "source" if path.suffix == ".py" else "input" if RUN not in path.parents else "log" if path.suffix == ".log" else "result",
               "keep_reason": "保留实际源码/快照、独立复跑命令和真实Windows API回执。"} for path in paths],
    "checks": [{"name": "direct_fixture_tests", "status": "PASS",
                "command": "python.exe -B -m unittest verification.test_s15_direct_vivado_bitgen.DirectSpawnFixtureTests -v",
                "exit_code": 0, "reason": "独立复跑8项方法、9个夹具场景通过，无skip。"},
               {"name": "supervisor_tests", "status": "PASS",
                "command": "python.exe -B -m unittest verification.test_s2b_process_supervisor.S2BProcessSupervisorTests -v",
                "exit_code": 0, "reason": "独立复跑10项通过，无skip。"},
               {"name": "rtl_and_hardware", "status": "NOT_RUN", "command": None, "exit_code": None,
                "reason": "本Run仅操作系统微型夹具，没有RTL或板上动作。"}],
    "limitations": ["独审PASS不等于RTL或硬件通过。", "故障读数注入；未测峰值内存。"],
    "tool_versions": {"Python": "3.12.10", "psutil": "7.2.2", "OS": "Windows"},
}
(RUN / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
