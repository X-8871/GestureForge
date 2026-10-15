"""绑定本次MMU检查器测试及失败审查结论原件。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
paths = sorted(path for path in RUN.rglob("*") if path.is_file()
               and path.name != "delivery_manifest.json")
paths += [ROOT / name for name in ("verification/check_s2b_inference_mmu.py",
                                  "verification/test_s2b_inference_mmu.py",
                                  "vitis/build_s2b_inference.py",
                                  "verification/check_s2b_ps_smoke_layout.py")]
manifest = {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T15", "run_id": RUN.name,
    "source_commit": "43f9b46f3ba0d4341b464c593293d1576fa8a3d6",
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
         "exit_code": 0, "reason": "23项单元测试通过。"},
        {"name": "source_chain_attack_regressions", "status": "PASS", "command": "独立Reviewer运行3项来源链攻击定向回归",
         "exit_code": 0, "reason": "错误源路径、错误归档成员名、错误归档路径均拒绝。"},
        {"name": "candidate_build_and_hardware", "status": "NOT_RUN", "command": None, "exit_code": None,
         "reason": "本Run只测检查器，不构建Vitis或执行板卡动作。"}],
    "limitations": ["独审PASS仅覆盖静态检查器与来源闭包。", "没有当前候选ELF/MMU或实板结果。", "初次封包时自动审批故障阻断提交；后续提交状态以Git记录为准。"],
    "tool_versions": {"Python": "3.12.14（现有bundled runtime）"},
}
(RUN / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
