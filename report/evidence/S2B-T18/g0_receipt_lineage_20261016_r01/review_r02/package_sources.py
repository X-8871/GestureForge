"""保存本轮独审源码原字节并封装已有审查结果，不重新运行测试。"""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
SOURCES = {
    "vitis/run_s2b_model_acceptance.py": "ad24b68b5ab19c680e0c2af51df8186be25d49c1731eff24e0b7076f58abd7ba",
    "verification/test_s2b_model_acceptance_runner.py": "6ce6d47b48358e937993f7d37cf7b293bce0244f05803a43244192c8fd1264fc",
    "verification/s2b_csr_acceptance_flow.py": "136b7bf5831363080ac1224fbe32c07c7dac001b63ad59198de098688cf6046b",
    "verification/test_s2b_csr_acceptance_flow.py": "1bc9c8dc9fa7d869d93140fc9bdc32947eebf9e5354a8abe1d49b35cb7ae7942",
}


def sha(path):
    """按原字节计算摘要。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """拒绝覆盖，绑定实际原件与真实独立审查记录。"""
    target = RUN / "source_snapshot"
    target.mkdir(exist_ok=False)
    for name, expected in SOURCES.items():
        source = ROOT / name
        if not source.is_file() or sha(source) != expected:
            raise RuntimeError("待审源码发生漂移：" + name)
        out = target / name
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, out)
    rows = []
    for p in sorted(RUN.rglob("*")):
        if p.is_file():
            rows.append({"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p),
                         "role": "source" if p.suffix == ".py" else "result"})
    manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T18",
        "run_id": RUN.parent.name + "_review_r02",
        "source_commit": "6448ba4e1bfbab5275741fd55184cdfb588c4fc9",
        "evidence_dir": RUN.relative_to(ROOT).as_posix(), "interfaces": [],
        "interfaces_not_applicable_reason": "本Run封存主机验收流程源码及隔离测试的独审结果，不批准具体平台部署或改变接口语义。",
        "files": rows,
        "checks": [{"name": "independent_source_review", "status": "PASS", "exit_code": 0,
                    "command": "独立Reviewer只读核对四文件并运行两个定向unittest模块及git diff --check",
                    "reason": "真实Reviewer回报34项通过，失败路径原始错误及T20文件绑定阻断关闭；原始测试stdout未另行保存。"},
                   {"name": "hardware_validation", "status": "NOT_APPLICABLE", "exit_code": None,
                    "command": None, "reason": "仅主机流程源码与隔离替身测试；109/1000和CSR实板验收未执行。"}],
        "limitations": ["审查使用隔离替身，不能证明硬件通过。", "保留原业务review清单，不将其替代标准包装清单。"]}
    with (RUN / "source_delivery_manifest.json").open("x", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("SOURCE_SNAPSHOTS_BOUND")


if __name__ == "__main__":
    main()
