"""只读复核R1原件和真实准备绑定，包装R2新交付；不操作设备。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone

root = Path(__file__).absolute().parents[4]
sys.path.insert(0, str(root))
from verification import s2b_board_acceptance as model
from verification import s2b_board_transport as transport
run = root / "report/evidence/S2B-T20/csr_acceptance_20261011_r03"
old = root / "report/evidence/S2B-T20/csr_acceptance_20261011_r01"
review = root / "tmp/2B/S2B-T20/independent_csr_acceptance_review_20261011_r01"
assert root.is_dir() and run.is_dir() and old.is_dir() and review.is_dir()
baseline = "2a20b1d9b53c9cc49fafdb49b09d78c5ab4f4674"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == baseline

def digest(path):
    """原字节SHA绑定。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    """独占写入新文件，不覆盖失败或审查原件。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2); stream.write("\n")

receipt_path = review / "review_receipt.json"
assert digest(receipt_path) == "97f7479abe00e0d5463a7038b0fd0a7dd0a86e5288b27d1a5ba875e1d2b88b70"
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
# 完整读取审查原件，按磁盘真实header重核对两条反例，不执行原脚本以免覆盖旧Run。
originals = [{"path": path.relative_to(root).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size}
             for path in sorted(review.rglob("*")) if path.is_file()]
counterexamples = []
for name, raw_name in (("prior_state_counterexample", "prior_replaced_model_mock"),
                       ("outstanding_request_counterexample", "outstanding_request_mock")):
    record = json.loads((review / (name + ".json")).read_text(encoding="utf-8"))
    tx = (review / raw_name / "tx.bin").read_bytes()
    rx = (review / raw_name / "rx.bin").read_bytes()
    requests = [transport.Header.unpack(tx[index:index + 40]) for index in range(0, len(tx), 40)]
    responses, offset = [], 0
    while offset < len(rx):
        head = transport.Header.unpack(rx[offset:offset + 40])
        raw = rx[offset:offset + 40 + head.length]
        responses.append({"sequence": head.sequence, "op": head.op, "frame": head.frame,
                          "epoch": transport.META.unpack_from(raw, 40)[0], "sha256": transport.digest(raw)})
        offset += len(raw)
    assert record["native_exit_code"] == 0 and [request.sequence for request in requests] == [1, 2, 3]
    assert offset == len(rx)
    counterexamples.append({"name": name, "old_observed": record["observed"],
                           "requests": [request.__dict__ for request in requests], "responses": responses})
prep = root / "report/evidence/S2B-T18/root_corpus_prepare_20261011_r01/preparation.json"
assert digest(prep) == "3d87b85e2e46becde90be7a071eb094d6dfb6b559d0301ece6333460a3a502cb"
plan = json.loads(prep.read_text(encoding="utf-8"))
model.validate_plan(plan)
weights_path, weights = model.read_bound(plan["weights"])
input_path, sample = model.read_bound(plan["rows"][0]["input"])
save(run / "provenance.json", {"schema_version": 1, "source_commit": baseline,
    "created_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "review_originals": originals, "review_receipt_top_level_fields": sorted(receipt),
    "counterexamples": counterexamples, "real_plan_readonly": {"path": str(prep), "sha256": digest(prep),
    "rows": len(plan["rows"]), "validate_plan": "PASS_OFFLINE_BINDINGS", "weights": {"path": str(weights_path),
    "bytes": len(weights), "sha256": transport.digest(weights)}, "sample000": {"path": str(input_path),
    "bytes": len(sample), "sha256": transport.digest(sample)}, "hardware_execution": "NOT_RUN"},
    "limitations": ["真实冻结资产的只读绑定核验不代表该资产已板上运行或golden通过。",
        "仅串行完整receipt前置受支持；已有abort_ready或直接receive未登记receipt的历史拒绝，须重新建立完整seed前置。",
        "busy与短deadline旧PS热恢复保持BLOCKED；BOARD NOT_RUN。"]})
snapshot = run / "source_snapshot"
assert not snapshot.exists(); snapshot.mkdir()
sources = ("verification/s2b_csr_board_acceptance.py", "verification/test_s2b_csr_board_acceptance.py")
diffs = []
for relative in sources:
    source = root / relative
    shutil.copyfile(source, snapshot / source.name)
    command = ["git", "diff", "--no-index", "--", str(old / "source_snapshot" / source.name), str(source)]
    result = subprocess.run(command, cwd=root, capture_output=True, encoding="utf-8")
    assert result.returncode == 1
    with (run / (source.name + ".diff")).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(result.stdout)
    diffs.append({"command": command, "native_exit_code": result.returncode, "stderr": result.stderr})
shutil.copyfile(Path(__file__).parent / "run_mock_regression.py", run / "run_mock_regression.py")
shutil.copyfile(Path(__file__), run / "package_delivery.py")
save(run / "diff_receipt.json", {"checks": diffs, "expected_nonzero": "git diff --no-index 1表示存在本轮差异。"})
manifest = json.loads((old / "delivery_manifest_r03.json").read_text(encoding="utf-8"))
manifest.update(run_id=run.name, source_commit=baseline, evidence_dir=run.relative_to(root).as_posix())
manifest["files"] = [{**item, "sha256": digest(root / item["path"])} for item in manifest["files"]
                     if item["role"] in ("source", "input")]
manifest["files"].append({"path": receipt_path.relative_to(root).as_posix(), "sha256": digest(receipt_path), "role": "input"})
manifest["files"] += [{"path": path.relative_to(root).as_posix(), "sha256": digest(path), "role": "result"}
                      for path in sorted(run.rglob("*")) if path.is_file()]
validation = json.loads((run / "validation_result_r02.json").read_text(encoding="utf-8"))
manifest["checks"][0].update(command="python -X utf8 -B tmp/2B/S2B-T20/csr_acceptance_20261011_r03/run_mock_regression.py",
    reason=f"33项mock；原生退出0，工作集峰{validation['peak_working_set_bytes']}B，pagefile峰{validation['peak_pagefile_usage_bytes']}B均小于300MiB。")
manifest["checks"].append({"name": "R1 P2旧版本反例", "status": "FAIL", "command": "prior_state_counterexample.py / outstanding_request_counterexample.py（R1保存的旧源运行）",
    "exit_code": 1, "reason": "旧源脚本原生0但两个逻辑断言未满足；审查CHANGES_REQUIRED，原件SHA保持；R2对应负例已拒绝。"})
# 旧历史失败仅引用其原件，不能将旧命令写成新Run实际重跑。
manifest["checks"][1]["reason"] += " 原r01包完整保留，本R2未重跑旧失败版本。"
manifest["limitations"] += ["R2原始审查反例native0表示错误放行；新增FAIL语义不能冒称原生命令exit1。",
    "R2实际仅两个源码变化；四冻结组件未改，未修改或提交其它agent工作。"]
# 历史逻辑失败允许明确原生0，包装FAIL规则要求非零，故保留为BLOCKED并记录真实值于provenance。
manifest["checks"][-1].update(status="BLOCKED", exit_code=None, command=None)
save(run / "delivery_manifest.json", manifest)
checks = []
for mode in ("evidence", "inputs"):
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
               "--manifest", (run / "delivery_manifest.json").relative_to(root).as_posix()]
    result = subprocess.run(command, cwd=root, capture_output=True, encoding="utf-8")
    checks.append({"command": command, "native_exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
save(Path(__file__).parent / "packaging_native.json", {"checks": checks, "hardware_execution": "NOT_RUN"})
print(json.dumps({"checks": checks, "source_sha256": {item: digest(root / item) for item in sources},
                  "manifest_sha256": digest(run / "delivery_manifest.json")}, ensure_ascii=False))
sys.exit(0 if [item["native_exit_code"] for item in checks] == [0, 2] else 2)
