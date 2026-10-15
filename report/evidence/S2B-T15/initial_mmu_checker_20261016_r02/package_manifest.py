"""绑定本次MMU检查器测试及失败审查结论原件。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
paths = sorted(path for path in RUN.rglob("*") if path.is_file()
               and path.name != "delivery_manifest.json")
manifest = {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T15", "run_id": RUN.name,
    "source_commit": "7ba5be307ff09073f6897b5f39923adcbfe71e20",
    "evidence_dir": RUN.relative_to(ROOT).as_posix(),
    "interfaces": [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.2",
                    "frozen": False, "path": "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
                    "sha256": "1486a7f69e7a2053acfcad05151a9c54cfffab776d4154141741236aa88c401b"}],
    "files": [{"path": path.relative_to(ROOT).as_posix(),
               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "role": "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result",
               "keep_reason": "保留真实测试、失败审查结论和对应源码，防止修复覆盖历史。"} for path in paths],
    "checks": [
        {"name": "mmu_unit_tests", "status": "PASS", "command": "python.exe -B -m unittest -v verification.test_s2b_inference_mmu",
         "exit_code": 0, "reason": "21项测试及原三项攻击定向回归通过。"},
        {"name": "independent_review", "status": "BLOCKED", "command": "独立Reviewer /root/review_actual_elf_mmu",
         "exit_code": None, "reason": "CHANGES_REQUIRED：BSP实际源路径与编译命令、map精确归档成员的来源链仍须修复。"},
        {"name": "candidate_build_and_hardware", "status": "NOT_RUN", "command": None, "exit_code": None,
         "reason": "本Run只测检查器，不构建Vitis或执行板卡动作。"}],
    "limitations": ["21项通过未覆盖新增来源链误放行；检查器仍未准入。", "没有当前候选ELF/MMU或实板结果。"],
    "tool_versions": {"Python": "3.12.14（现有bundled runtime）"},
}
(RUN / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
