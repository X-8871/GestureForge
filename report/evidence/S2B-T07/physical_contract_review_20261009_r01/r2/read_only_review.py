import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


# 本脚本只核对文件绑定和时序公式，不执行RTL或软件功能测试。
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = "report/evidence/S2B-T07/physical_contract_20261009_r02"
OLD = "report/evidence/S2B-T07/physical_contract_20261009_r01"
SERIAL = "report/evidence/S2B-T06/serial_port_recheck_20261009_225453_r01"
DOC = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
DESIGN = "docs/obsidian-project/02-方案设计/系统设计.md"
EXPECTED = {
    DOC: "bd7070276702a6f8faa1ee9e592fed7c0a2c46c8eda4e9faac34a07a01971bad",
    DESIGN: "7aea2ed8a47423f80cda74aea98064f971b7da290509931387b33a2d28b8c33a",
    ".codex/STATE.md": "5348fc5a38c1687b4795ad6e324ff364fe0e390312d82a59b93786f8e8a1cca2",
    ".gitattributes": "6c9162bcb5672e8c97ade6836dc210e4c61cce90dea3e30c91a160003c68470c",
    f"{RUN}/delivery_manifest.json": "6be1e8cde3de1875054126893e8865d026e5e3106d3cc843ef8e197e0367c8cf",
    f"{RUN}/layout_result.json": "34bc0b1aa4a632ad4fdabd5154ee181ab3f3a7708cafff2968a863263a2f7b1f",
    f"{RUN}/candidate_revision_result.json": "ef483418c13bf0fbdd9d78f47c8e143f10b766ca092c7014cc92d3520322be0b",
    f"{SERIAL}/delivery_manifest.json": "ede0b5090943b7c8e7bad04f3ac0acf83587b5fee7d0b03ba5d9b9bba15803ec",
}


def file(relative):
    current = ROOT
    for part in Path(relative).parts:
        assert part in {p.name for p in current.iterdir()}, relative
        current /= part
    assert current.is_file() and not current.is_symlink(), relative
    return current


def sha(relative):
    return hashlib.sha256(file(relative).read_bytes()).hexdigest()


def obj(relative):
    return json.loads(file(relative).read_text(encoding="utf-8"))


def save(name, data):
    target = OUT / name
    assert not target.exists(), name
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


start = time.perf_counter()
baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
assert baseline == "3f6e327a0ff9adc04ed6c98c1578862b8c2fae64"
fixed = [{"path": relative, "sha256": sha(relative), "match": sha(relative) == expected} for relative, expected in EXPECTED.items()]
assert all(row["match"] for row in fixed)
bound_files = []
for run in (RUN, SERIAL):
    for row in obj(f"{run}/delivery_manifest.json")["files"]:
        actual = sha(row["path"])
        assert actual == row["sha256"], row["path"]
        bound_files.append({"path": row["path"], "sha256": actual})
bindings = obj(f"{RUN}/source_snapshot_bindings.json")
for row in bindings["files"]:
    assert sha(row["original_path"]) == sha(row["snapshot_path"]) == row["sha256"]
for row in bindings["external_official_bsp_sources"]:
    assert file(row["snapshot_path"]).read_bytes() == file(row["reuse_from"]).read_bytes()
    assert sha(row["snapshot_path"]) == row["sha256"]
for row in bindings["reused_results"]:
    assert file(row["source"]).read_bytes() == file(row["destination"]).read_bytes()
    assert sha(row["destination"]) == row["sha256"]
assert sha(f"{RUN}/review_receipt_r01.json") == "ecc1b9fba11399ebf1b1f23fdd7855d6c44cda21f3378576e9a4ceb602f20878"
assert sha(f"{OLD}/snapshots/s2b_physical_interface_candidate.md") == "e14ea46239d987336ea0ee53afb962b77733626294447c47b7f06f158dc06242"
assert sha(f"{OLD}/snapshots/系统设计.md") == "2e2589afc37defbd48b023635f3755fe1a267c4613375559518951e5dc78408e"

# 不调用Developer公式脚本，以日历中的后续沿独立定位最早真实采样。
rows = []
for production in range(4):
    future_status_edges = [edge for edge in range(production + 1, production + 9) if edge % 4 in (0, 3)]
    status_edge = min(future_status_edges)
    error_edge = min(edge for edge in range(status_edge + 1, status_edge + 9) if edge % 4 == 1)
    rows.append({"producer_phase": production, "status_delta": status_edge - production, "error_delta": error_edge - production, "error_after_status": error_edge - status_edge})
assert [row["status_delta"] for row in rows] == [3, 2, 1, 1]
assert [row["error_delta"] for row in rows] == [5, 4, 3, 2]
revision = obj(f"{RUN}/candidate_revision_result.json")
for independent, claimed in zip(rows, revision["csr_phase_formula"]["producer_consumer_rows"]):
    assert independent["status_delta"] == claimed["status_sample_E_plus"]
    assert independent["error_delta"] == claimed["associated_error_code_sample_E_plus"]
assert 3 + 4 + 7 * 4 == 35 <= 40
reset_edge = 2
abort_consumer_edge = reset_edge + 1
confirmation = min(edge for edge in range(reset_edge + 2, reset_edge + 9) if edge % 4 in (0, 3))
assert confirmation == 4 and confirmation - reset_edge == 2

def approved_section(text):
    begin = text.index("### 阶段2B物理异常恢复原则")
    return text[begin:text.index("### 阶段2B具体物理接口候选", begin)]

current_design = file(DESIGN).read_text(encoding="utf-8")
old_design = file(f"{OLD}/snapshots/系统设计.md").read_text(encoding="utf-8")
assert approved_section(current_design) == approved_section(old_design)
serial_original_hashes = {
    "enumerate_serial.py": "467109daf9a0ec66af35c54331f8a38249d141bd0762f8034294e00602cd5cdb",
    "enumeration.stderr.log": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "enumeration.stdout.log": "76467585cd0ae23e602c542464b51c56502ba2d943cfb9d6b2b3e0ea2157fe7c",
    "execution.json": "116da3e8df9035a1f2c24fd12763db481fde6fbb447a186c976f7c68fde95ff8",
    "collector_failure.json": "ac8af5fd97eb01b349f76c747340dc34add49a3a49c517030c885bb83791d081",
    "port_result.json": "668c04036bec0741b26fda2b4a9f42f4b0259f536f1e2030b09fa484b4c14d5a",
}
for name, expected in serial_original_hashes.items():
    assert sha(f"{SERIAL}/{name}") == expected
serial_failure = obj(f"{SERIAL}/collector_failure.json")
assert serial_failure["exit_code"] == 1
assert obj(f"{SERIAL}/execution.json")["exit_code"] == 0
diagnostic = obj(f"{SERIAL}/checker_exit_diagnostic.json")
assert diagnostic["original_root_tool_observation"]["outer_tool_exit_code"] == 1
assert diagnostic["native_recheck"]["native_exit_code"] == 2

commands = []
env = dict(os.environ, PYTHONIOENCODING="utf-8")
for run, mode, expected in ((RUN, "evidence", 0), (RUN, "inputs", 2), (SERIAL, "evidence", 0), (SERIAL, "inputs", 2)):
    argv = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", f"{run}/delivery_manifest.json"]
    before = time.perf_counter()
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, env=env)
    name = ("t07" if run == RUN else "t06") + "_" + mode + ".log"
    target = OUT / name
    assert not target.exists()
    target.write_bytes(result.stdout + result.stderr)
    commands.append({"argv": argv, "native_exit_code": result.returncode, "expected": expected, "elapsed_seconds": time.perf_counter() - before, "log_path": str(target), "log_sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    assert result.returncode == expected
save("independent_facts.json", {
    "source_commit": baseline, "fixed_hashes": fixed, "manifest_bound_files": bound_files,
    "source_snapshot_count": len(bindings["files"]), "r01_receipt_and_snapshot_preserved": True,
    "layout_and_projection_reused_byte_identical": True, "approved_recovery_section_unchanged": True,
    "csr_formula_rows": rows, "arming_conservative_bound": 35, "candidate_limit": 40,
    "reset_phase2_abort_phase3_first_safe_status_phase0": {"S": reset_edge, "abort": abort_consumer_edge, "status_confirmation": confirmation},
    "serial_original_failure_1_native_enumeration_0_preserved": True,
    "commands": commands, "elapsed_seconds": time.perf_counter() - start,
    "scope": "只读哈希/原字节/相位公式与包装核查，不是RTL或软件功能测试"
})
print(json.dumps({"status": "INDEPENDENT_R2_FACTS_OK", "files": len(bound_files), "status_deltas": [row["status_delta"] for row in rows], "error_deltas": [row["error_delta"] for row in rows], "native_exit_codes": [row["native_exit_code"] for row in commands]}, ensure_ascii=False))
