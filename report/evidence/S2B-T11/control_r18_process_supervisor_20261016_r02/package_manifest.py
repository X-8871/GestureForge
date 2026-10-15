"""为本次监督器微型验证生成文件绑定清单。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
sources = [
    "verification/test_s2b_control_csr_rtl.py",
    "verification/s2b_process_supervisor.py",
    "verification/test_s2b_process_supervisor.py",
    "verification/s15_job_guard.py",
]
paths = sorted(path for path in RUN.rglob("*") if path.is_file()
                and path.name != "delivery_manifest.json")
manifest = {
    "schema_version": 1,
    "stage": "2B",
    "task_id": "S2B-T11",
    "run_id": RUN.name,
    "source_commit": "7ba5be307ff09073f6897b5f39923adcbfe71e20",
    "evidence_dir": RUN.relative_to(ROOT).as_posix(),
    "interfaces": [],
    "interfaces_not_applicable_reason": "本小任务验证操作系统进程隔离与资源失败关闭，不变更总线或模型接口；不替代CSR业务验证。",
    "files": [
        {"path": path.relative_to(ROOT).as_posix(),
         "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
         "role": "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result",
         "keep_reason": "保留真实测试记录、工具身份和待审源码绑定，供独立复核。"}
        for path in paths
    ],
    "checks": [
        {"name": "windows_job_fixture_tests", "status": "FAIL",
         "command": "python.exe -B -m unittest -v verification.test_s2b_process_supervisor",
         "exit_code": 1, "reason": "10项中9通过1失败：最后一个测试入口OpenProcess拒绝，未执行目标超时路径。"},
        {"name": "independent_review", "status": "BLOCKED",
         "command": "独立Reviewer /root/review_t13_and_board_probe 只读审查及9项复跑",
         "exit_code": None, "reason": "失败原因正在诊断，尚未完成修复后复审。"},
        {"name": "rtl_and_hardware_acceptance", "status": "NOT_RUN",
         "command": None, "exit_code": None,
         "reason": "本Run不执行RTL或实板测试。"},
    ],
    "limitations": ["未测峰值内存；不是实际内存压力测试。", "独立审查结论另行核对；包装检查不代表G2或阶段验收。"],
    "tool_versions": {"Python": "3.12.10", "psutil": "7.2.2", "OS": "Windows"},
}
(RUN / "delivery_manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
