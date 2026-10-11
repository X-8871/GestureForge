"""冻结独立软件审查回执和必要原始证据清单；不修改生产文件或执行Git写入。"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess

run = Path(__file__).resolve().parent
root = run.parents[3]
parent = run.parent
runs = [parent / f"independent_busy_observer_review_20261011_r{i:02d}" for i in range(1, 5)]


def read(path):
    """UTF-8读取冻结结果。"""
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    """绑定完整磁盘字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    """独占新建回执，禁止覆盖已有轮次。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


audit = read(runs[2] / "binding_audit_result.json")
for relative, expected in audit["source_and_manifest_sha256"].items():
    assert sha(root / relative) == expected, relative
for relative, expected in audit["g1_source_sha256"].items():
    assert sha(root / relative) == expected, relative
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
assert head == audit["actual_head"] == "90c87b773fe06684797f6bb3cca2da078a4d49aa"
suite = read(runs[0] / "suite_result.json")
probes = read(runs[0] / "independent_probe_result.json")
public = read(runs[2] / "public_gate_result.json")
raw_selected = read(runs[3] / "independent_probe_result.json")
assert suite["success"] and suite["tests_run"] == 68
assert probes["status"] == "PASS" and probes["count"] == 50
assert public["status"] == "PASS_NEGATIVE_GATES_AND_STATIC_CHAIN" and public["count"] == 18
assert raw_selected["status"] == "PASS" and raw_selected["count"] == 6
executions = []
for folder, label, code, purpose in (
    (runs[0], "suite", 0, "原68项离线回归"),
    (runs[0], "probes", 0, "独立50项原生mock反例"),
    (runs[0], "public", 1, "首轮审查夹具目录不符合公开入口限制，原失败保留"),
    (runs[1], "public", 1, "第二轮审查夹具错误文本期待不符，实际拒绝有效"),
    (runs[2], "public", 0, "13个公开负向、实际109计划/构建核验及4个计划反例"),
    (runs[2], "bindings", 0, "开发三轮99文件与8依赖绑定及旧T16门禁"),
    (runs[2], "g1_evidence", 0, "开发最终清单包装核验"),
    (runs[2], "g1_inputs", 2, "实际未冻结依赖核验失败，不视为板上批准"),
    (runs[3], "raw_selected", 0, "重跑六代表场景保留实际TX/RX/原生原件"),
):
    path = folder / (label + "_native.json")
    result = read(path)
    assert result["exit_code"] == code and result["stopped"] is None
    assert result["sampled_peak_rss_bytes"] < 300 * 1024 * 1024
    executions.append({"record": str(path.relative_to(root)), "sha256": sha(path), "purpose": purpose,
        "status": "PASS" if code == 0 else "FAIL", **result})

for index_path in runs[3].glob("raw_*/raw_stream_index.json"):
    for item in read(index_path)["files"]:
        assert sha(Path(item["preserved_path"])) == item["sha256"]

receipt = {
    "schema_version": 1,
    "task_id": "S2B-T20-BUSY-OBS",
    "role": "INDEPENDENT_REVIEWER",
    "status": "PASS_SOFTWARE_G2_ONLY",
    "reviewed_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "source_commit": head,
    "supplied_baseline": audit["supplied_baseline"],
    "approved_source_sha256": audit["source_and_manifest_sha256"],
    "dependency_source_sha256": audit["g1_source_sha256"],
    "approved_manifest_path": "report/evidence/S2B-T20/busy_observer_20261011_r03/delivery_manifest.json",
    "approved_manifest_sha256": "adbfceaebfc2856a9b21afe8fb031184bd245fdb7723d057e7635624247786b4",
    "findings": [],
    "coverage": [
        {"requirement": "正式物理接口64行拒绝无副作用、70行逐次AXI_PROGRESS诊断",
         "source": "verification/s2b_csr_busy_observer.py:76-119,224-255",
         "evidence": "原68项 + 独立50项；动态0x068原读7→0→7、LAST_REJECT实际0→0→1；首错地址0x06C/70/74严守0。"},
        {"requirement": "公开入口真实类型与全部实际准入、109准备及有序真实LOAD/seed重放",
         "source": "verification/s2b_csr_busy_observer.py:31-47,287-309; verification/s2b_csr_board_acceptance.py:117-215",
         "evidence": "13个公开负向实际进入原preflight/admit拒绝；真实109准备与真实build核验，4个计划反例；旧/未消费LOAD和TX/RX漂移均拒绝。"},
        {"requirement": "CPU0 stop所有权、CPU1静止门禁、异常保持失败锁和原始清理错误",
         "source": "verification/s2b_csr_busy_observer.py:142-168,256-284",
         "evidence": "stop/continue异常和无效、CPU1意外Running、过快/终态等反例；CPU1无stop/con/reset。停止无效时如实保留仍Running和cleanup_errors。"},
        {"requirement": "同RUN真实UART身份、全部双头和非空全框黄金",
         "source": "verification/s2b_csr_busy_observer.py:170-222",
         "evidence": "独立手算两框，完整5070+20280字节；错头/末框/缺框/CRC/seq/frame/epoch/reject、13字节partial和磁盘额外字节全部失败。"},
        {"requirement": "旧T16 negative_start与stable_csr严格门禁不变",
         "evidence": "对6d3fd856基线的两个函数AST逐项相同，未以新动态观察放松旧门禁。"},
    ],
    "counts": {"frozen_regression_tests": 68, "independent_native_cases": 50,
               "public_and_plan_checks": 18, "selected_raw_reruns": 6, "developer_file_bindings": 99,
               "dependency_source_bindings": 8},
    "executions": executions,
    "resources": {"sampled_peak_rss_bytes": max(item["sampled_peak_rss_bytes"] for item in executions),
                  "native_elapsed_seconds_sum": sum(item["elapsed_seconds"] for item in executions),
                  "native_process_runs": len(executions), "tool_call_count": None,
                  "tool_call_count_reason": "未单独计量全部编排/阅读调用；原生命令与进程轮数已逐项记录。"},
    "test_isolation": {"production_function_replacements": [], "manual_latch_or_epoch_changes_in_extra_tests": [],
        "native_mock": "沿用Developer原生夹具，扩展测试设备的stop/con/read实际返回；生产类型/门禁/receipt均未替换。",
        "fixture_start_state": "Developer fixture按显式MOCK_ONLY设置已部署初始状态，仅用于离线；绝不构成实际部署事实。",
        "public_output_root": public["test_output_root_override"],
        "public_output_root_approval": "总控明确允许仅重定向输出ROOT到隔离tmp，保留全部原门禁及同Git HEAD。",
        "created_visibility_or_final_review_receipts": []},
    "preserved_reviewer_failures": [
        {"run": runs[0].name, "label": "public", "exit_code": 1,
         "cause": "公开_new_run要求固定证据父目录，初次临时子目录被正确拒绝；未执行新UART。"},
        {"run": runs[1].name, "label": "public", "exit_code": 1,
         "cause": "预期错误文本包含SHA，而真实文本为绑定文件发生漂移；实际拒绝正确，r03修正审查断言。"}],
    "hardware_execution": "NOT_RUN",
    "public_positive_hardware_admission": {"status": "NOT_RUN", "exit_code": None,
        "reason": "尚无真实visibility1/cache/最终bit独立批准；公开负向与静态链不能证明已获真实正向批准。"},
    "G2": {"status": "PASS", "scope": "仅本软件helper及冻结测试"},
    "G3": {"status": "NOT_RUN", "exit_code": None},
    "G4_G5": {"status": "BLOCKED", "exit_code": None},
    "inputs_check": {"status": "FAIL", "exit_code": 2},
    "limitations": [
        "正式物理/UART接口未冻结；软件G2不批准最终bit、缓存、统一冷恢复、真实SDK/串口或板上验收。",
        "离散DAP只证明规定可观察不变量，不能排除任意读间账本/状态瞬态，未新增ILA证据。",
        "CPU1状态为离散观察，PL时钟仅保证没有暂停命令；未测板卡真实时钟。",
        "68与50项均是离线模拟，额外6次仅为原始证据保留重复，不是新增独立覆盖或实板次数。",
        "r01批量50场景完整原始记录保留tmp但不永久归档；脚本/逐项断言结果/原生日志归档，r04六代表实际TX/RX/原生调用永久归档。",
        "25ms RSS采样不等于瞬时峰值，不包含监督器自身；工具调用总数未测。",
    ],
}
receipt_path = run / "review_receipt.json"
save(receipt_path, receipt)
selected = []
for index, folder in enumerate(runs):
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(folder)
        if index == 0 and len(relative.parts) > 1:
            continue
        if path.name == "raw_delivery_manifest.json":
            continue
        assert not any(part in {"__pycache__", "probe_cases", "suite_cases", "public_cases"} for part in relative.parts), path
        role = "source" if path.suffix == ".py" else "log" if path.suffix in (".log", ".jsonl") else "result"
        selected.append({"path": str(path.relative_to(root)).replace("\\", "/"), "sha256": sha(path), "role": role})
raw_manifest = {"schema_version": 1, "kind": "independent-review-raw/1.0.0", "task_id": "S2B-T20-BUSY-OBS",
    "source_commit": head, "status": "PASS_SOFTWARE_G2_ONLY", "files": selected,
    "archive_instruction": "只复制files逐项原字节及本raw_delivery_manifest.json自身；不按父目录递归复制，不复制临时mock SDK/ELF/模型/整准备库。",
    "omitted_retained_local": ["r01/raw_*批量重复场景原件仅留tmp；未删未覆写，不冒称永久归档。"],
    "limitations": ["本清单仅审查自产原件的哈希索引，非正式stage delivery清单；总控归档后生成符合report/README的阶段清单。"]}
raw_path = run / "raw_delivery_manifest.json"
save(raw_path, raw_manifest)
assert all(sha(root / item["path"]) == item["sha256"] and set(item) == {"path", "sha256", "role"} for item in selected)
print(json.dumps({"status": receipt["status"], "receipt": str(receipt_path), "receipt_sha256": sha(receipt_path),
    "raw_manifest": str(raw_path), "raw_manifest_sha256": sha(raw_path), "archive_file_count": len(selected) + 1,
    "archive_bytes_including_manifest": sum((root / item["path"]).stat().st_size for item in selected) + raw_path.stat().st_size,
    "findings": []}, ensure_ascii=False))
