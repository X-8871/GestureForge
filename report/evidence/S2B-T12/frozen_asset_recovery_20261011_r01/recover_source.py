"""保留旧检出字节，仅从哈希已核验的Git对象恢复四份冻结索引。"""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[4]
evidence = root / "report/evidence/S2B-T12/frozen_asset_recovery_20261011_r01"
assert root.name == "FPGA_Competition" and evidence.is_dir()
baseline = "df379f9ae6e899247b3f099a2cf2bc1fb526abe6"
rows = [
    ("report/evidence/S2A-T25/cpu_layer_golden_index.json", "2d76f9e284130c96374de6ea3525e0c92778b0f701c8894cd4d127234c8d3c72", "cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d"),
    ("report/evidence/S2A-T29/cpu_decode_nms_reference.json", "26392c8d7f5ca8643a26c149411c66d6f2343a544f8c4f03d32584dc4e071d33", "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231"),
    ("report/evidence/S2A-T68/candidate8x8_109_20261006_130252/d9_109_candidate8x8_109_resume_20261007_023531.json", "268958192a66efaaa6faaecc94267e22d4c4a4e53928037031a5ad5de2a48a40", "fcdf60ef68990a13ba634ee6cb2df71ad152d7f9d5a05d6625f5f3af296523ab"),
    ("report/evidence/S2A-T68/candidate8x8_109_20261006_130252/recovery_manifest_20261007_023531.json", "f80cf9f9832687b254fc1aa7fec2521199e47eb417750e57e1e98a9a52143ce2", "eefe285f1c03673143d1fa0563f153626fe90d86be2d245ced59a05d8a7e65a2")]

def sha(data):
    """哈希原始字节。"""
    return hashlib.sha256(data).hexdigest()

verified = []
for relative, old_sha, target_sha in rows:
    path = root / relative
    assert path.is_file() and not path.is_symlink()
    old = path.read_bytes()
    assert sha(old) == old_sha
    command = ["git", "show", baseline + ":" + relative]
    process = subprocess.run(command, cwd=root, capture_output=True, check=True)
    blob = process.stdout
    assert sha(blob) == target_sha and old.replace(b"\r\n", b"\n") == blob
    verified.append((path, old, blob, command, process.returncode))
originals = evidence / "original_checkout_bytes"
originals.mkdir()
records = []
for path, old, blob, command, returncode in verified:
    original = originals / path.name
    with original.open("xb") as stream:
        stream.write(old)
    assert sha(path.read_bytes()) == sha(old)
    path.write_bytes(blob)
    assert path.read_bytes() == blob
    records.append({"path": path.relative_to(root).as_posix(), "before_sha256": sha(old),
        "after_sha256": sha(blob), "original_bytes": len(old), "restored_bytes": len(blob),
        "preserved_original": original.relative_to(root).as_posix(),
        "git_command": command, "git_exit_code": returncode, "difference": "仅CRLF检出转换，JSON业务内容未更改"})
with (evidence / "recovery_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump({"status": "PASS_EXACT_GIT_BLOB_RECOVERY", "source_commit": baseline, "files": records,
        "limitations": ["只恢复四份冻结索引，不证明新PL或实板推理通过。"]}, stream, ensure_ascii=False, indent=2); stream.write("\n")
tool_copy = evidence / "recover_source.py"
with tool_copy.open("xb") as stream:
    stream.write(Path(__file__).read_bytes())
files = [{"path": record["path"], "sha256": record["after_sha256"], "role": "input"} for record in records]
files += [{"path": p.relative_to(root).as_posix(), "sha256": sha(p.read_bytes()), "role": "source" if p.suffix == ".py" else "result"}
          for p in sorted(evidence.rglob("*")) if p.is_file()]
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T12", "run_id": evidence.name,
    "source_commit": baseline, "evidence_dir": evidence.relative_to(root).as_posix(),
    "interfaces": [], "interfaces_not_applicable_reason": "按已冻结Git对象恢复检出字节，不修改业务接口。",
    "files": files, "checks": [{"name": "冻结字节恢复", "status": "PASS", "exit_code": 0,
        "command": "python -B " + str(Path(__file__)), "reason": "每个Git show原生0，恢复前原始字节保存；SHA与CRLF差异断言逐项通过。"}],
    "tool_versions": {"Python": "3.12.10", "Git": subprocess.check_output(["git", "--version"], text=True).strip()},
    "limitations": ["未执行PL模型或板上测试，不计为2B G3/G5。"]}
with (evidence / "delivery_manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2); stream.write("\n")
print(json.dumps({"status": "PASS_EXACT_GIT_BLOB_RECOVERY", "files": len(records)}, ensure_ascii=False))
