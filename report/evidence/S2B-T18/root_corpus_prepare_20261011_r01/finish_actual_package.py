"""保留首次清单格式失败，修正正式文档和命令字符串后冻结新增封包。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).absolute().parents[4]
run = root / "report/evidence/S2B-T18/root_corpus_prepare_20261011_r01"
assert run.is_dir() and Path(__file__).parent.is_dir()

def digest(path):
    """实际原字节哈希，新增包装文件均为小文件。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    """独占新增文件，不覆盖首次失败或准备原件。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2); stream.write("\n")

manifest = json.loads((run / "delivery_manifest.json").read_text(encoding="utf-8"))
document = root / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
assert document.is_file() and "G0_FROZEN" in document.read_text(encoding="utf-8")
manifest["interfaces"][0].update(path=document.relative_to(root).as_posix(), sha256=digest(document))
for check in manifest["checks"]:
    if isinstance(check["command"], list):
        check["command"] = subprocess.list2cmdline(check["command"])
failure = Path(__file__).parent / "packaging_process.json"
assert failure.is_file()
shutil.copyfile(failure, run / "initial_packaging_failure.json")
shutil.copyfile(Path(__file__), run / Path(__file__).name)
manifest["checks"].append({"name": "首次封包格式失败", "status": "FAIL",
    "command": "python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S2B-T18/root_corpus_prepare_20261011_r01/delivery_manifest.json",
    "exit_code": 2, "reason": "原生检查器2：接口原填report清单及两命令数组，违反既有格式；原清单和完整诊断保留，r02修正。"})
inventory = [{"path": path.relative_to(root).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size}
             for path in sorted(run.rglob("*")) if path.is_file()]
save(run / "package_inventory_r02.json", {"schema_version": 1, "files": inventory,
    "excluded_self_and_final_manifest": ["package_inventory_r02.json", "delivery_manifest_r02.json"],
    "hardware_execution": "NOT_RUN", "reason": "最终全文件SHA/字节数；自身与最终manifest由总控固定哈希，避免自引用。"})
known = {item["path"] for item in manifest["files"]}
manifest["files"] += [{"path": path.relative_to(root).as_posix(), "sha256": digest(path), "role": "result"}
    for path in sorted(run.rglob("*")) if path.is_file() and path.relative_to(root).as_posix() not in known]
save(run / "delivery_manifest_r02.json", manifest)
results = []
for mode in ("evidence", "inputs"):
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
               "--manifest", (run / "delivery_manifest_r02.json").relative_to(root).as_posix()]
    process = subprocess.run(command, cwd=root, capture_output=True, encoding="utf-8")
    results.append({"command": command, "exit_code": process.returncode, "stdout": process.stdout, "stderr": process.stderr})
final = {"checks": results, "manifest": {"path": str(run / "delivery_manifest_r02.json"),
    "sha256": digest(run / "delivery_manifest_r02.json"), "bytes": (run / "delivery_manifest_r02.json").stat().st_size},
    "inventory": {"sha256": digest(run / "package_inventory_r02.json"), "bytes": (run / "package_inventory_r02.json").stat().st_size},
    "preparation": {"sha256": digest(run / "preparation.json"), "bytes": (run / "preparation.json").stat().st_size},
    "hardware_execution": "NOT_RUN", "file_count": len(list(run.rglob("*")))}
assert final["preparation"]["sha256"] == "3d87b85e2e46becde90be7a071eb094d6dfb6b559d0301ece6333460a3a502cb"
save(Path(__file__).parent / "final_packaging_process.json", final)
print(json.dumps({"native_exit_codes": [item["exit_code"] for item in results], **{key: final[key] for key in ("manifest", "inventory", "preparation")}}, ensure_ascii=False))
sys.exit(0 if [item["exit_code"] for item in results] == [0, 2] else 2)
