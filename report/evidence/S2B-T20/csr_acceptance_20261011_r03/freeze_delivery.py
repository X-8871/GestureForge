"""保留首次包装原件，补齐历史失败和真实准备的机器输入绑定后冻结。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).absolute().parents[4]
run = root / "report/evidence/S2B-T20/csr_acceptance_20261011_r03"
assert run.is_dir()

def digest(path):
    """实际原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    """独占新文件，不覆盖先前包装结果。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2); stream.write("\n")

shutil.copyfile(Path(__file__).parent / "packaging_native.json", run / "packaging_native_r01.json")
shutil.copyfile(Path(__file__), run / "freeze_delivery.py")
manifest = json.loads((run / "delivery_manifest.json").read_text(encoding="utf-8"))
inputs = ("report/evidence/S2B-T20/csr_acceptance_20261011_r01/delivery_manifest_r03.json",
          "report/evidence/S2B-T20/csr_acceptance_20261011_r01/unittest_r02.log",
          "report/evidence/S2B-T20/csr_acceptance_20261011_r01/failure_r02_source.py",
          "report/evidence/S2B-T20/csr_acceptance_20261011_r01/failure_r02_test.py",
          "report/evidence/S2B-T18/root_corpus_prepare_20261011_r01/preparation.json")
manifest["files"] += [{"path": relative, "sha256": digest(root / relative), "role": "input"} for relative in inputs]
known = {item["path"] for item in manifest["files"]}
manifest["files"] += [{"path": path.relative_to(root).as_posix(), "sha256": digest(path), "role": "result"}
    for path in sorted(run.rglob("*")) if path.is_file() and path.relative_to(root).as_posix() not in known]
manifest["checks"][0]["command"] += "（最终33项运行；原生进程记录validation_result_r02.json）"
manifest["checks"][-1]["reason"] += " 此为历史独审状态；R2需新Reviewer决定关闭，不能由开发自称G2通过。"
manifest["limitations"] = [item for item in manifest["limitations"] if not item.startswith("R2原始审查")]
manifest["limitations"].append("R1两反例的真实native0及错误放行原件由provenance逐项绑定；其逻辑失败与命令退出分开。")
save(run / "delivery_manifest_r02.json", manifest)
results = []
for mode in ("evidence", "inputs"):
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
               "--manifest", (run / "delivery_manifest_r02.json").relative_to(root).as_posix()]
    result = subprocess.run(command, cwd=root, capture_output=True, encoding="utf-8")
    results.append({"command": command, "native_exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
save(Path(__file__).parent / "packaging_native_final.json", {"checks": results, "hardware_execution": "NOT_RUN"})
print(json.dumps({"native_exit_codes": [item["native_exit_code"] for item in results],
    "source_commit": manifest["source_commit"], "sources": {item["path"]: item["sha256"] for item in manifest["files"] if item["role"] == "source"},
    "manifest_sha256": digest(run / "delivery_manifest_r02.json")}, ensure_ascii=False))
sys.exit(0 if [item["native_exit_code"] for item in results] == [0, 2] else 2)
