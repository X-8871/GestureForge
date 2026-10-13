"""独立绑定审查范围、全部G1清单文件和原生校验结果。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[4]
OUT = ROOT / "report/evidence/S2B-T19/pc_nvlist_review_20261013_r01"
G1 = ROOT / "report/evidence/S2B-T19/pc_nvlist_20261013_r01"
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
read = lambda path: json.loads(Path(path).read_text(encoding="utf-8"))
baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
result = read(OUT / "rerun_r02/run_result.json")
assert baseline == result["baseline"] == "6019ed956f0008c4a97b42dc9e0aebb74f31f5c5"
assert result["status"] == "PASS" and result["tests_run"] == 92 and result["exit_code"] == 0
assert result["source_sha256"] == result["after_source_sha256"]
for path, expected in result["source_sha256"].items():
    assert sha(ROOT / path) == expected

manifest = read(G1 / "delivery_manifest_r02.json")
assert manifest["source_commit"] == baseline
bound = []
for row in manifest["files"]:
    path = ROOT / row["path"]
    assert path.is_file() and sha(path) == row["sha256"], row["path"]
    bound.append({"path": row["path"], "sha256": row["sha256"]})
old = read(G1 / "delivery_manifest.json")
revised = json.loads(json.dumps(manifest))
assert revised["files"].pop() == {"path": str((G1 / "delivery_manifest.json").relative_to(ROOT)).replace("\\", "/"),
    "sha256": sha(G1 / "delivery_manifest.json"), "role": "result", "keep_reason": "原始包装失败清单，缺少历史FAIL原因，不覆盖。"}
for row in revised["checks"]:
    if row["status"] == "FAIL":
        assert row.pop("reason")
assert old == revised

collector = G1 / "collector_sources"
original = (collector / "prepare_visibility_config.py").read_bytes()
derived = (collector / "prepare_visibility_config_nvlist.py").read_bytes()
old_sha = b"06c1f46d9906d39e76f9befddcdb50eaf20cf485ddb5e5d48145ab0553143432"
new_sha = b"4f69f848f71acb4b2ff7709a4ab40bbb892f0b205137d434f7a5f302805e1f85"
assert original.count(old_sha) == 1 and original.replace(old_sha, new_sha) == derived
record = read(collector / "config_nvlist_derivation.json")
assert record["original_sha256"] == sha(collector / "prepare_visibility_config.py")
assert record["derived_sha256"] == sha(collector / "prepare_visibility_config_nvlist.py")
for path, expected in ((record["original"], original), (record["derived"], derived)):
    assert Path(path).read_bytes() == expected

actual = read(G1 / "final_r03/actual_cpu1_rrd_r02.json")
assert sha(actual["source"]) == actual["source_sha256"]
assert actual["row"] in read(actual["source"])["calls"]
for folder, expected_count in (("final_r03", 89), ("consumers_dependencies_r05", 79)):
    source_result = read(G1 / folder / "run_result.json")
    log = (G1 / folder / "unittest.stderr.log").read_text(encoding="utf-8")
    assert source_result["exit_code"] == 0
    assert source_result["after_run_source_sha256"] == result["source_sha256"]
    assert f"Ran {expected_count} tests" in log and log.rstrip().endswith("OK")

checks = []
for mode, expected in (("evidence", 0), ("inputs", 2)):
    command = [sys.executable, "-X", "utf8", "-B", "verification/check_stage_delivery.py", "--mode", mode,
               "--manifest", "report/evidence/S2B-T19/pc_nvlist_20261013_r01/delivery_manifest_r02.json"]
    started = time.monotonic()
    completed = subprocess.run(command, cwd=ROOT, capture_output=True)
    for label, data in (("stdout", completed.stdout), ("stderr", completed.stderr)):
        with (OUT / (mode + "." + label + ".log")).open("xb") as stream:
            stream.write(data)
    checks.append({"command": command, "exit_code": completed.returncode, "expected_exit_code": expected,
                   "elapsed_seconds": time.monotonic() - started, "mode": mode,
                   "stdout_sha256": sha(OUT / (mode + ".stdout.log")), "stderr_sha256": sha(OUT / (mode + ".stderr.log"))})
    assert completed.returncode == expected

receipt = {"schema_version": 1, "task_id": "S2B-T19", "status": "PASS", "scope": "G2_SOFTWARE_PC_NVLIST_ONLY",
    "baseline": baseline, "source_sha256": result["source_sha256"], "sdk_target_path": result["sdk_target_path"],
    "sdk_target_sha256": result["sdk_target_sha256"], "reviewer": "independent_subagent_pc_nvlist_independent_review",
    "command": [sys.executable, "-X", "utf8", "-B", str(Path(__file__).absolute())], "native_exit_code": 0,
    "review_runner_sha256": sha(Path(__file__).parent / "independent_review.py"), "review_closure_sha256": sha(__file__),
    "independent_result": {"path": str(OUT / "rerun_r02/run_result.json"), "sha256": sha(OUT / "rerun_r02/run_result.json"),
                           "tests_run": 92, "exit_code": 0, "elapsed_seconds": result["elapsed_seconds"]},
    "g1_manifest": {"path": str(G1 / "delivery_manifest_r02.json"), "sha256": sha(G1 / "delivery_manifest_r02.json"), "bound_file_count": len(bound)},
    "verified_g1_files": bound, "packaging_checks": checks, "blocking_findings": [],
    "reviewed_semantics": ["官方rrd nvlist字典及int32全范围、N/A/空值异常拒绝", "实际rrd函数及CPU接收器身份",
        "原始异步stdout/stderr保存", "复位前失败拒绝物理变更", "部署失败锁止、只停本次CPU0、自有断点清理及非零返回",
        "仅一处helper SHA配置派生", "历史失败保留、修订清单仅补reason及绑定旧清单"],
    "historical_runs": [{"path": str(OUT / "run_result.json"), "sha256": sha(OUT / "run_result.json"),
        "classification": "ENVIRONMENT_FAILURE", "native_exit_code": 1,
        "reason": "初次沙箱拒绝访问：114个ERROR为父路径枚举WinError5，9个ERROR为既有pyserial源码读取PermissionError。获准访问后92项全部通过。"}],
    "actual_hardware_calls": 0, "peak_memory_bytes": None,
    "limitations": ["软件G2通过不代表结构化PC或cache实板通过，G3/G4/G5未核验。", "79消费者仅核查真实原件及哈希，不复跑。",
        "SDK仅执行AST提取的__print_regs函数，不加载真实会话或设备。", "峰值内存未测；不批准visibility1或完整模型验收。"]}
with (OUT / "review_receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": receipt["status"], "scope": receipt["scope"], "bound_file_count": len(bound),
                  "receipt_sha256": sha(OUT / "review_receipt.json")}, ensure_ascii=False))
