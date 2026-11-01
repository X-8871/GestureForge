"""封存本次综合恢复链的真实结果，不改写执行原件。"""
from pathlib import Path
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
PARENT = ROOT / "report/evidence/S2B-T14"
R05 = PARENT / "csr_fixed_visibility0_20261016_r05"
result = json.loads((R05 / "result.json").read_text(encoding="utf-8"))
assert result["job"]["cleanup_confirmed"] is True
assert result["artifact_sha256"].get("routed.dcp")


def sha(path):
    """按原字节计算哈希。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


core = ROOT / "tmp/2B/S2B-T13/platform_csr_fixed_20261016_r03/project/s2b_inference_candidate.runs/s2b_inference_infer_0_synth_1"
r03 = PARENT / "csr_fixed_visibility0_20261016_r03"
core_result = json.loads((r03 / "result.json").read_text(encoding="utf-8"))
assert sha(core / "s2b_inference_infer_0.dcp") == core_result["core_dcp_sha256"]
archive = r03 / "completed_core"
archive.mkdir(exist_ok=False)
for name in ("s2b_inference_infer_0.dcp", "runme.log", "s2b_inference_infer_0.tcl", "s2b_inference_infer_0.vds", ".vivado.begin.rst", ".vivado.end.rst", "__synthesis_is_complete__"):
    source = core / name
    assert source.is_file(), source
    shutil.copyfile(source, archive / name)
shutil.copyfile(Path(__file__), PARENT / "csr_fixed_visibility0_20261016_r07/package_family.py")
interface = ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
for number in range(1, 8):
    run = PARENT / f"csr_fixed_visibility0_20261016_r{number:02d}"
    manifest = run / "delivery_manifest.json"
    assert not manifest.exists(), manifest
    actual = json.loads((run / "result.json").read_text(encoding="utf-8"))
    passed = str(actual["status"]).startswith("PASS")
    rows = []
    for path in sorted(run.rglob("*")):
        if not path.is_file():
            continue
        rows.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
                     "role": "source" if path.suffix in (".py", ".tcl", ".sv", ".cmd") else "result",
                     "keep_reason": "保留本轮实际输入、失败诊断或可恢复的完成产物；DCP用于核对实际被顶层消费的综合结果。"})
    data = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T14", "run_id": run.name,
            "source_commit": actual.get("source_commit", result["source_commit"]),
            "evidence_dir": run.relative_to(ROOT).as_posix(),
            "interfaces": [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.2",
                            "frozen": False, "path": interface.relative_to(ROOT).as_posix(), "sha256": sha(interface)}],
            "files": rows,
            "checks": [{"name": "actual_driver_result", "status": "PASS" if passed else "FAIL",
                        "exit_code": 0 if passed else 1, "command": "launch_infer_ooc.py" if number == 3 else "launch_build.py",
                        "reason": "真实驱动终态 " + actual["status"] + "；详细Job状态和原生日志以原件为准。"},
                       {"name": "hardware_validation", "status": "NOT_APPLICABLE", "exit_code": None,
                        "command": None, "reason": "本Run仅为离线综合/实现产物任务，未执行板卡动作；正式2B G3仍未执行。"}],
            "limitations": ["本清单核对包装；不将失败运行、综合完成或产物生成等同独立审查、G0或G3/G4/G5通过。",
                            "r01未启动Vivado；r02内存停止；r03仅核心OOC通过；r04顶层遗留运行状态失败；r05复用四OOC但setup未满足；r06因工具内部设计名检查错误而未优化；r07物理优化和STA通过，因原生XSA更新时间头导致完整bit比较失败，原FAIL保持，另由r08对账原生配置payload和canonical交付。",
                            "全程未下载/执行板卡；109黄金样本、1000连续任务和恢复尚未执行。"],
            "tool_versions": {"Vivado": "2026.1", "packager_python": sys.version.split()[0]}}
    with manifest.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
    print(run.name, actual["status"], len(rows), sha(manifest))
