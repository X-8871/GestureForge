"""冻结R3独立复审收据，明确软件门禁通过与实板审批边界。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import subprocess
import json
import hashlib

folder = Path(__file__).parent
root = folder.parents[3]
def sha(file):
    """原字节SHA。"""
    return hashlib.sha256(file.read_bytes()).hexdigest()
sources = {
    "vitis/run_s2b_visibility_probe.py": "96e923c49ef7c1bdcbbecfb8b3f0cba4eb51af7212a3a64f5aefe256c2856f2c",
    "verification/test_s2b_visibility_probe.py": "fb195817d9e5720c48172dd3d2d0c590a526d4b152f7f9406af71dd3d5c24087",
    "report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01/delivery_manifest_r03.json": "bf7bae1ed9827159ed70f5115d43734959ac6b293e415180d6005ca85263d153",
    "tmp/2B/S2B-T19/independent_probe_review_20261011_r02/review_receipt.json": "b012a80117dce51ae9d33c751a3ea34acce993a223de4a6ea67d46a03b498a03",
}
for file, expected in sources.items():
    assert sha(root/file) == expected, file
manifest = json.loads((root/"report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01/delivery_manifest_r03.json").read_text(encoding="utf-8"))
for item in manifest["files"]+manifest["interfaces"]:
    assert sha(root/item["path"]) == item["sha256"], item["path"]
suite = json.loads((folder/"offline_suite_result.json").read_text(encoding="utf-8"))
runtime = json.loads((folder/"actual_runtime_gate.json").read_text(encoding="utf-8"))
query = json.loads((folder/"native_query_counterexamples.json").read_text(encoding="utf-8"))
commands = [json.loads((folder/file).read_text(encoding="utf-8")) for file in ("offline_native.json", "runtime_native.json", "manifest_native.json", "query_native.json")]
assert suite["native_exit_code"] == 0 and suite["methods"] == 18 and len(suite["subcases"]) == 73
assert runtime["inner_exit_code"] == 0 and commands[1]["outer_exit_code"] == 0 and len(runtime["rows"]) == 13
assert query["native_exit_code"] == 0
assert runtime["single_process_peak_working_set_bytes"] < 300*1024*1024
record = {
    "schema_version": 1, "task_id": "S2B-T19-R3", "role": "INDEPENDENT_REVIEWER", "status": "PASS",
    "scope": "SOFTWARE_G2_VISIBILITY0_ENTRY_NATIVE_CLASS_FIXES_ONLY",
    "reviewed_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "baseline_commit": "5a676b700af4c27297977379417b1694dd64840e",
    "observed_head_at_close": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip(),
    "source_and_evidence_sha256": sources,
    "source_recheck_at_close": "UNCHANGED",
    "findings": [],
    "closed_findings": [
        {"id": "T19-R2-P1-NATIVE_ALIAS", "status": "CLOSED", "basis": "生产verify_sdk_files保持192独立供应文件完整binding/重复物理路径拒绝，verify_native_alias明确验证两个key共享vivado模块身份/元数据及两个不同已加载Windows映像handle/path/rawSHA。真实官方_runtime通过；元数据、共享关系、物理来源与hash反例拒绝。", "evidence": "actual_runtime_gate.json"},
        {"id": "T19-R2-P2-CLASS_ORIGIN", "status": "CLOSED", "basis": "生产开始前检查Session/Target定义module/name/qualname，dispatch.Session及session.Target与官方模块Class对象相同。R2错误定义模块反例在真实已导入Class上拒绝，alias/Class/code/ordinaryorigin漂移也拒绝，且未实例化真实Session或Target。", "evidence": "actual_runtime_gate.json"},
    ],
    "checks": {
        "offline_suite": {"status": "PASS_MOCK_ONLY", "methods": 18, "subcases": 73, "native_exit_code": 0, "elapsed_seconds": suite["elapsed_seconds"], "sdk_imported": suite["xsdb_loaded"], "serial_imported": suite["serial_loaded"]},
        "actual_production_source_gate": {"status": "PASS_IMPORT_ONLY", "sdk_bindings": runtime["sdk_count"], "serial_bindings": runtime["serial_count"], "vitis_python": runtime["python"], "pyserial_version": runtime["serial_version"], "inner_exit_code": runtime["inner_exit_code"], "outer_exit_code": commands[1]["outer_exit_code"], "runtime_native_origins": runtime["native_actual"], "adversarial_rejections": runtime["rows"]},
        "loaded_native_query_helper": {"status": "PASS_WINDOWS_API_MOCK_ONLY", "positive_controls": 1, "rejections": 4, "cases": query["rows"]},
        "manifest": {"status": "PASS_RAW_BINDINGS_AND_CHECKS_OK", "files": len(manifest["files"]), "interfaces": len(manifest["interfaces"]), "total_bindings": len(manifest["files"])+len(manifest["interfaces"]), "native_exit_code": commands[2]["native_exit_code"], "meaning": "只确认包装及原字节关联，不替代G2语义审查或真实验收。旧FAIL原件保留且不当作当前通过测试。"},
        "full_preflight": {"status": "BLOCKED", "execution": "NOT_RUN", "reason": "正式bit/implemented XSA与真实compat独审receipt未具备。SDK_GATE_ONLY配置不是完整部署配置或批准。"},
        "hardware": {"status": "NOT_RUN", "session_created": False, "connection_attempted": False, "serial_opened": False, "postroute_approved": False, "cache_approved": False, "cold_lifecycle_approved": False, "G3": "NOT_RUN", "G4": "NOT_PASSED", "G5": "NOT_PASSED"},
    },
    "commands": commands,
    "metrics": {"runtime_inner_seconds": runtime["elapsed_seconds"], "runtime_outer_seconds": commands[1]["elapsed_seconds"], "runtime_single_process_peak_working_set_bytes": runtime["single_process_peak_working_set_bytes"], "runtime_peak_process_tree_memory_bytes": None, "offline_peak_memory_bytes": None, "repetitions": {"offline_suite": 1, "actual_runtime_with_faults": 1, "native_query_helper_mock": 1, "manifest_checker": 1}},
    "artifacts": [{"path": str(file.relative_to(root)).replace("\\", "/"), "sha256": sha(file), "bytes": file.stat().st_size} for file in sorted(folder.rglob("*")) if file.is_file() and file.name != "review_receipt.json"],
    "limitations": [
        "本PASS仅软件G2门禁修复与离线回归，不是正式compat审批、完整bit/postroute/cache、G3/G4/G5或2B阶段通过。",
        "真实Vitis实验只运行共享生产SDK/serial源核验与import/helper；没有创建SDKSession、连接、打开串口、stop/reset/download或操作服务器。",
        "附加13个来源反例使本次完整轻量实验outer14.969秒/inner12.296秒，超过单baseline预期10秒；未为追求时间重复运行或改动正式指标。单进程峰值108580864B小于300MiB；全进程树及离线suite峰值未测。",
        "所有本轮新增脚本、日志、fixture和回执只在本审查目录；强制patch mkdtemp的显式dir。",
        "原R1/R2、开发首失败与包装失败原件未改；正式源文件、STATE和Git未修改或提交；读写使用UTF8。",
        "SDK原始供应源码与两个pyd原字节实际核验；底层OS/DLL/标准库未作全供应链冻结。"
    ],
}
with (folder/"review_receipt.json").open("x", encoding="utf-8") as output:
    json.dump(record, output, ensure_ascii=False, indent=2)
print(json.dumps({"status": record["status"], "scope": record["scope"], "receipt_sha256": sha(folder/"review_receipt.json"), "artifact_files": len(record["artifacts"])}))
