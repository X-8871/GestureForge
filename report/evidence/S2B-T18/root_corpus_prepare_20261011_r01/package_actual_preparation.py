"""封装实际准备与独审原件；只新增证据，不改变既有参考或操作设备。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone

root = Path(__file__).absolute().parents[4]
run = root / "report/evidence/S2B-T18/root_corpus_prepare_20261011_r01"
raw_prepare = Path(__file__).parent
review = root / "tmp/2B/S2B-T18/independent_actual_prepare_review_20261011_r01"
assert root.is_dir() and run.is_dir() and raw_prepare.is_dir() and review.is_dir()
baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
assert baseline == "f3a0b0514c90983c41c8729b93f18d627bfc1bb5"

def digest(path):
    """分块读取原字节，避免一次载入大型索引。"""
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for raw in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(raw)
    return sha.hexdigest()

def binding(path):
    """精确核验完整路径和文件类型，返回实际哈希与字节数。"""
    assert path.is_file() and not path.is_symlink(), str(path)
    return {"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size}

def save(path, data):
    """独占新文件，不覆盖任何旧运行产物。"""
    assert path.parent.is_dir() and not path.exists()
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2); stream.write("\n")

def copy_bound(item, target):
    """复制已实际核验的原件，并记录源与副本的闭合映射。"""
    source = Path(item["path"])
    assert binding(source) == item
    assert target.parent.is_dir() and not target.exists()
    shutil.copyfile(source, target)
    copied = binding(target)
    assert copied["sha256"] == item["sha256"] and copied["bytes"] == item["bytes"]
    return {"original": item, "copy": copied}

approved = {"receipt.json": "bbbd4d10cf9db0cafd8e435e55d346520cc0f156f71358648057b5494da3df88",
            "raw_audit_result.json": "fee00e00d7510d0b5cc72e83b97e33ebc70ccf26c6a7bc39dec5ed994fb5f5b7",
            "native_process.json": "4eed40acd28cdb66b769c0284c88fffa9005bff6b7712efcbfe0d0e814dfe035"}
for name, sha in approved.items():
    assert digest(review / name) == sha
receipt = json.loads((review / "receipt.json").read_text(encoding="utf-8"))
audit = json.loads((review / "raw_audit_result.json").read_text(encoding="utf-8"))
assert receipt["status"] == audit["status"] == "PASS_OFFLINE_PREPARATION_INTEGRITY"
assert receipt["hardware_execution"] == audit["hardware_execution"] == "NOT_RUN"
prep = run / "preparation.json"
assert binding(prep) == audit["preparation"]
assert digest(prep) == receipt["approved_preparation_sha256"] == "3d87b85e2e46becde90be7a071eb094d6dfb6b559d0301ece6333460a3a502cb"
before = {str(path): binding(path) for path in run.rglob("*") if path.is_file()}
review_files = receipt["raw_files"] + [binding(review / "receipt.json")]
assert {str(path) for path in review.rglob("*") if path.is_file()} == {item["path"] for item in review_files}
copy_review = run / "independent_review"
copy_root = run / "root_prepare_raw"
assert not copy_review.exists() and not copy_root.exists()
copy_review.mkdir(); (copy_review / "source_snapshot").mkdir(); copy_root.mkdir()
maps = []
for item in review_files:
    relative = Path(item["path"]).relative_to(review)
    maps.append(copy_bound(item, copy_review / relative))
prepare_items = [audit["root_prepare_native_process"]["binding"]] + audit["root_prepare_logs"]
assert {str(path) for path in raw_prepare.iterdir() if path.is_file() and path.name != Path(__file__).name} == {item["path"] for item in prepare_items}
for item in prepare_items:
    maps.append(copy_bound(item, copy_root / Path(item["path"]).name))
root_process = json.loads((copy_root / "prepare_process.json").read_text(encoding="utf-8"))
review_process = json.loads((copy_review / "native_process.json").read_text(encoding="utf-8"))
assert root_process["exit_code"] == review_process["exit_code"] == receipt["native_exit_code"] == 0
assert len(audit["rows"]) == receipt["reviewed_input_count"] == 109
assert sum(len(row["head_tensors"]) for row in audit["rows"]) == receipt["reviewed_head_count"] == 218
for row in audit["rows"]:
    for item in [row["reference"]] + [dict((key, head[key]) for key in ("path", "sha256", "bytes")) for head in row["head_tensors"].values()]:
        assert binding(Path(item["path"])) == item
source_deps = {relative: {"reviewed_original": {key: item[key] for key in ("path", "sha256", "bytes")},
    "frozen_snapshot": binding(copy_review / "source_snapshot" / Path(item["snapshot"]["path"]).name)}
    for relative, item in audit["source_bindings"].items()}
assert len(source_deps) == 6
assert source_deps["verification/check_s2b_inference_platform.py"]["frozen_snapshot"]["sha256"] == "7245a7331c7c1081e7a9145bc3054a3fcc4553951b5cef545e504b434f25abd3"
save(run / "source_deps.json", {"schema_version": 1, "source_commit_at_packaging": baseline,
    "review_git_head": audit["git_head"], "source_deps": source_deps,
    "scope": "仅声明本次实际准备及独审所用六源码快照；平台checker为该次7245版本，不代表后续profile。"})
external = {"weights": audit["weights"], "inputs": [row["input"] for row in audit["rows"]],
    "golden_slices": [{"index": row["index"], "heads": {name: {key: item[key] for key in
       ("raw_golden_path", "byte_offset", "bytes", "slice_sha256")} for name, item in row["head_tensors"].items()}} for row in audit["rows"]]}
save(run / "external_asset_bindings.json", {"schema_version": 1, "bindings": external,
    "scope": "外部资产不复制；权重/109输入哈希与218golden切片来自已批准独审原字节，未重复重哈希大型golden shards。",
    "approved_review_receipt": binding(copy_review / "receipt.json")})
shutil.copyfile(Path(__file__), run / Path(__file__).name)
save(run / "raw_copy_map.json", {"schema_version": 1, "maps": maps,
    "commands": {"prepare": root_process, "independent_review": review_process},
    "actual_review_inner_seconds": audit["actual_seconds"], "review_peak_working_set_bytes": audit["peak_working_set_bytes"],
    "original_count": len(before), "scope": "闭合原件到副本映射，不执行或重写原命令。"})
assert all(binding(Path(path)) == item for path, item in before.items())
inventory = [binding(path) for path in sorted(run.rglob("*")) if path.is_file()]
save(run / "package_inventory.json", {"schema_version": 1, "created_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "source_commit": baseline, "files": inventory, "original_unchanged": True,
    "excluded_self_and_final_manifest": ["package_inventory.json", "delivery_manifest.json"],
    "hardware_execution": "NOT_RUN", "limits": receipt["limitations"]})
plan = json.loads(prep.read_text(encoding="utf-8"))
files = []
source_paths = {item["frozen_snapshot"]["path"] for item in source_deps.values()}
for path in sorted(run.rglob("*")):
    if path.is_file():
        files.append({"path": path.relative_to(root).as_posix(), "sha256": digest(path),
                      "role": "source" if str(path) in source_paths else "log" if path.suffix == ".log" else "result"})
for key in ("model_manifest", "samples_manifest", "golden_source"):
    item = plan[key]; path = Path(item["path"])
    assert digest(path) == item["sha256"]
    files.append({"path": path.relative_to(root).as_posix(), "sha256": item["sha256"], "role": "input"})
physical = root / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T18", "run_id": run.name,
    "source_commit": baseline, "evidence_dir": run.relative_to(root).as_posix(), "files": files,
    "interfaces": [{"name": "T01冻结模型/量化/检测头", "version": "gestureforge_s2a_model_manifest_v1",
        "path": Path(plan["model_manifest"]["path"]).relative_to(root).as_posix(), "sha256": plan["model_manifest"]["sha256"], "frozen": True},
        {"name": "PS/PL物理候选", "version": "s2b-physical-candidate/0.1.1", "path": physical.relative_to(root).as_posix(),
         "sha256": digest(physical), "frozen": False}],
    "checks": [{"name": "实际109样本准备", "status": "PASS", "command": root_process["command"], "exit_code": 0,
        "reason": "真实准备原生命令0/1.829s；原preparation SHA保持。"},
        {"name": "独立实际准备完整性", "status": "PASS", "command": review_process["command"], "exit_code": 0,
         "reason": "validate_plan/GF8/109输入/218头切片/全reference字段/sample000框手算；内审2.484s、外进程2.619s、RSS107798528B。"},
        {"name": "板上109+1000与阶段验收", "status": "NOT_RUN", "command": None, "exit_code": None,
         "reason": "本包仅离线准备；visibility、runtime兼容性、最终PL、STA及G3/G4/G5未由该包批准。"}],
    "tool_versions": {"python_packaging": sys.version, "SDK": "NOT_RUN", "Vivado": "NOT_RUN"},
    "limitations": receipt["limitations"] + ["source_commit为封包HEAD，独审git_head与实际六源码快照单独保存。",
        "外部资产依赖通过external_asset_bindings绑定；检查器只核验仓库内清单，不能代替外部资产独审。"]}
save(run / "delivery_manifest.json", manifest)
results = []
for mode in ("evidence", "inputs"):
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
               "--manifest", (run / "delivery_manifest.json").relative_to(root).as_posix()]
    process = subprocess.run(command, cwd=root, capture_output=True, encoding="utf-8")
    results.append({"command": command, "exit_code": process.returncode, "stdout": process.stdout, "stderr": process.stderr})
save(raw_prepare / "packaging_process.json", {"checks": results, "final_manifest": binding(run / "delivery_manifest.json"),
    "preparation": binding(prep), "all_evidence_file_count": len(files), "hardware_execution": "NOT_RUN"})
print(json.dumps({"native_exit_codes": [item["exit_code"] for item in results], "manifest": binding(run / "delivery_manifest.json"),
                  "preparation": binding(prep), "originals": len(before), "copies": len(maps)}, ensure_ascii=False))
sys.exit(0 if [item["exit_code"] for item in results] == [0, 2] else 2)
