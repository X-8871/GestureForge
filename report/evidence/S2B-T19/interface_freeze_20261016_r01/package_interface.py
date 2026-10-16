"""按原字节封存已独审的接口与实验规程，不授予具体硬件验收通过。"""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "report/evidence/S2B-T19/interface_freeze_20261016_r01"
SOURCES = ["docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
           "docs/obsidian-project/02-方案设计/s2b_board_transport.md",
           "board/s2b_inference_platform.json", "board/s2b_inference_platform.md",
           "verification/check_s2b_inference_platform.py", "verification/s2b_board_acceptance.py"]
REVIEW = ROOT / "report/evidence/S2B-T19/cache_probe_independent_20261016_r01/review_provenance.json"


def sha(p):
    """按原字节计算摘要。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    """排他创建证据目录并绑定独立审核原件。"""
    if sha(REVIEW) != "134be86654f04a21dbd0fdb1c6aad4a3ad86aabf38dc2fab1a0523bf9856ae7b":
        raise RuntimeError("独立审查原件漂移")
    RUN.mkdir(exist_ok=False)
    for name in SOURCES:
        out = RUN / "source_snapshot" / name
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, out)
    shutil.copyfile(REVIEW, RUN / REVIEW.name)
    shutil.copyfile(Path(__file__), RUN / Path(__file__).name)
    files = [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p),
              "role": "result" if p.name == REVIEW.name else "source"}
             for p in sorted(RUN.rglob("*")) if p.is_file()]
    data = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T19", "run_id": RUN.name,
            "source_commit": "b6133a12dbcd0d59cfe659c0f3562a445e30d159",
            "evidence_dir": RUN.relative_to(ROOT).as_posix(), "interfaces": [],
            "interfaces_not_applicable_reason": "本Run冻结接口定义与受控实验规程本身；具体部署批准及G3/G4/G5独立验收。",
            "files": files, "tool_versions": {"Python": "3.12.14"},
            "checks": [{"name": "independent_interface_review", "status": "PASS", "exit_code": 0,
                        "command": "独立Reviewer审查六文件精确diff并执行check_static及git diff --check",
                        "reason": "真实审查原件已固定SHA；只批准接口定义与受控有限实验规程。"},
                       {"name": "hardware_phase_acceptance", "status": "NOT_APPLICABLE", "exit_code": None,
                        "command": None, "reason": "本包不是具体部署或板上验收，109/1000/恢复仍未执行。"}],
            "limitations": ["G0_FROZEN字段仅描述两个接口文档的确定版本及实验规程。", "所有原始失败与未测项保持原结论。"]}
    with (RUN / "delivery_manifest.json").open("x", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("INTERFACE_SCOPE_PACKAGED")


if __name__ == "__main__":
    main()
