"""只读核查开发原件、冻结源码、正式接口和旧T16稳定拒绝门禁。"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

run = Path(__file__).resolve().parent
root = run.parents[3]
sys.path.insert(0, str(root))
from verification import check_stage_delivery as delivery


def sha(path):
    """按完整原字节计算SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


expected = {
    "verification/s2b_csr_busy_observer.py": "de15f04086f025de2786ebdb08d2c913b1a88073dcaadd4a0f3057f39d9dd3f2",
    "verification/test_s2b_csr_busy_observer.py": "13d33dbbe33986ef0e8d1dc90587552b50504fb9734a6b34b95ed12a82fdcc12",
    "report/evidence/S2B-T20/busy_observer_20261011_r03/delivery_manifest.json": "adbfceaebfc2856a9b21afe8fb031184bd245fdb7723d057e7635624247786b4",
}
for relative, digest in expected.items():
    assert sha(root / relative) == digest, relative
manifest_path = root / "report/evidence/S2B-T20/busy_observer_20261011_r03/delivery_manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
records = []
for index in (1, 2, 3):
    folder = root / f"report/evidence/S2B-T20/busy_observer_20261011_r{index:02d}"
    path = folder / "delivery_manifest.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    for item in document["files"]:
        assert sha(root / item["path"]) == item["sha256"], item["path"]
    result = delivery.check_manifest("evidence", str(path), str(root))
    assert result["status"] == "CHECKS_OK", result
    execution = json.loads((folder / "execution.json").read_text(encoding="utf-8"))
    records.append({"path": str(path), "sha256": sha(path), "files_verified": len(document["files"]),
        "packaging": result, "execution": execution})
execution = records[-1]["execution"]
for relative, digest in execution["source_sha256"].items():
    assert sha(root / relative) == digest, relative
for relative in ("verification/s2b_csr_busy_observer.py", "verification/test_s2b_csr_busy_observer.py"):
    assert (root / relative).read_bytes() == (manifest_path.parent / "source_snapshot" / Path(relative).name).read_bytes()
assert execution["exit_code"] == 0
log = (manifest_path.parent / "unittest.log").read_text(encoding="utf-8")
assert "Ran 68 tests" in log and "\nOK\n" in log
baseline = "6d3fd8567b579a51d4042667d47af7d94f2f5a97"
old = subprocess.check_output(["git", "show", baseline + ":verification/s2b_board_jtag.py"], cwd=root).decode("utf-8")
current = (root / "verification/s2b_board_jtag.py").read_text(encoding="utf-8")


def function_dump(source, name):
    """忽略行号后比较旧严格快照门禁函数结构。"""
    tree = ast.parse(source)
    matches = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(matches) == 1
    return ast.dump(matches[0], include_attributes=False)


assert function_dump(old, "negative_start") == function_dump(current, "negative_start")
assert function_dump(old, "stable_csr") == function_dump(current, "stable_csr")
result = {"status": "PASS_BINDINGS_AND_LEGACY_GATE", "source_and_manifest_sha256": expected,
    "actual_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
    "supplied_baseline": baseline, "g1_source_sha256": execution["source_sha256"], "developer_runs": records,
    "legacy_negative_start_and_stable_csr_ast_unchanged": True,
    "interfaces": manifest["interfaces"], "checks": manifest["checks"],
    "notes": ["r01原生单元失败和包装失败原件保留；源码逆patch重建在原execution明确披露，非现场采样。",
              "r02 65项回归通过、首包装失败原件仍保留；r03 68项及真实源码快照完整。",
              "CHECKS_OK只说明包装与绑定，不能代替测试、独立审查或实板。"]}
(run / "binding_audit_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("PASS", sum(item["files_verified"] for item in records), "developer file bindings; 8 dependency hashes; legacy gates unchanged")
