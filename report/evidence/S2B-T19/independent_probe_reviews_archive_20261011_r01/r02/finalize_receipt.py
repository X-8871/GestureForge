"""冻结独立审查观察与文件哈希，不写项目源代码或原始G1证据。"""
from pathlib import Path
import json
import hashlib
import subprocess
from datetime import datetime, timezone, timedelta

folder = Path(__file__).parent
root = folder.parents[3]
def sha(path):
    """原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
expected = {
    "vitis/run_s2b_visibility_probe.py": "b02000940144536cde87e05da6220c6fe82d3342ab27f7448b226b993f01aa76",
    "verification/test_s2b_visibility_probe.py": "40f633b0a34b2a914476cb862c879bc214da31c7afac8426f3c7439a386d7d4a",
    "verification/check_s2b_inference_platform.py": "1f8d4d4d099f32713ceec04ad4661e110b331394761f83f6efe02d1098f39901",
    "verification/s2b_board_jtag.py": "91bbf5bc8ac5ef9bee37ce6491627a6ac8f38a53b7bba113d1b83447b2ecddf0",
    "report/evidence/S2B-T19/offline_probe_fix_20261011_r01/delivery_manifest.json": "e1d221ca16678f6058a694aae63c033d82675eb11e729d47df77ae8e93ef2828",
    "report/evidence/S2B-T19/runtime_import_probe_20261011_r01/delivery_manifest_r02.json": "796f3a3e0f7fb8d9fe8f705d58af9b40413d3e4ee460a6fa79ee0bbd9f3df376",
    "tmp/2B/S2B-T19/independent_review_20261011_r01/review_receipt.json": "637d985d16d32ceac32c997e6f7d6f8c3cd31ddddceb3d236a41aa9bfe5b4bb9",
}
for relative, value in expected.items():
    assert sha(root/relative) == value, relative
manifest = json.loads((root/"report/evidence/S2B-T19/offline_probe_fix_20261011_r01/delivery_manifest.json").read_text(encoding="utf-8"))
for item in manifest["interfaces"] + manifest["files"]:
    assert sha(root/item["path"]) == item["sha256"]
suite = json.loads((folder/"offline_suite_result.json").read_text(encoding="utf-8"))
commands = [json.loads((folder/name).read_text(encoding="utf-8")) for name in (
    "offline_native.json", "runtime_native.json", "diagnostic_native.json", "native_origins_native.json", "adversarial_native.json", "class_origin_native.json")]
artifact_files = [{"path": str(file.relative_to(root)).replace("\\", "/"), "sha256": sha(file), "bytes": file.stat().st_size}
                  for file in sorted(folder.rglob("*")) if file.is_file() and file.name != "review_receipt.json"]
record = {
    "schema_version": 1, "task_id": "S2B-T19-R2", "role": "INDEPENDENT_REVIEWER", "status": "CHANGES_REQUIRED",
    "reviewed_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "baseline_commit": "0c2f5b58f40f70de974a48582eb7729cf76c0b8e",
    "observed_head_at_close": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip(),
    "source_and_evidence_sha256": expected,
    "scope": ["官方connect失败/身份后服务消失分支，无隐式server launch", "全部bound JSON严格解析及深层数组反例", "SDK真实磁盘AST闭包/33动态TCF代理", "真实Vitis3.13+SDK2026.1+pyserial3.5纯import/helper gate", "SDK native别名实际模块规格与已加载Windows二进制来源", "Session/Target真实方法code与fake错误Class来源反例", "早期UART主错误和secondary cleanup错误共存"],
    "checks": {
        "offline_suite": {"status": "PASS_MOCK_ONLY", "methods": suite["methods"], "subcases": len(suite["subcases"]), "native_exit_code": suite["native_exit_code"], "elapsed_seconds": suite["elapsed_seconds"]},
        "final_manifest_raw_binding_check": {"status": "PASS", "files": len(manifest["files"]), "interfaces": len(manifest["interfaces"]), "total_bindings": len(manifest["files"])+len(manifest["interfaces"])},
        "runtime_gate_as_delivered": {"status": "FAIL", "script_record_native_exit_code": 1, "vitis_wrapper_exit_code": 0, "reason": "官方两个native key共享模块对象且metadata被第二个pyd覆盖，交付来源门禁误拒绝xv_pycommontasks"},
        "runtime_gate_diagnostic_only": {"status": "PASS_IMPORT_ONLY_WITH_IN_MEMORY_PYD_BINDING_CHANGE", "reason": "仅诊断后续官方方法门禁可运行，不是交付配置或_preflight通过，不是硬件通过"},
        "strict_json_adversarial": {"status": "PASS_REJECTION", "documents": ["compat_review", "build_details", "owned_hw_server_identity", "platform_manifest"]},
        "connection_failure_ast_mock": {"status": "PASS", "safe_launches": 0, "127_positive_control_launches": 1},
        "early_uart_cleanup": {"status": "PASS", "primary_error_preserved": True, "secondary_dispose_error_preserved": True},
        "class_origin_adversarial": {"status": "UNEXPECTED_ACCEPTANCE", "mock_only": True},
        "hardware": {"status": "NOT_RUN", "session_created": False, "connection_attempted": False, "serial_opened": False},
    },
    "r1_findings": [{"id": "R1-P1-autolaunch", "status": "CLOSED", "basis": "官方connect AST纯mock正/反控及编排race路径无launch"},
                    {"id": "R1-P2-json", "status": "CLOSED", "basis": "所有文档递归duplicate/nonstandard/schema类型拒绝"},
                    {"id": "R1-P2-sdk-source", "status": "PARTIALLY_CLOSED", "basis": "方法code比较已实现，但新增native实际运行误拒绝与Class provenance遗漏仍阻断"}],
    "findings": [
        {"id": "T19-R2-P1-NATIVE_ALIAS", "priority": 1, "file": "vitis/run_s2b_visibility_probe.py", "lines": [73,124,268],
         "title": "官方native模块别名被当成独立__file__来源，导致真实入口无法运行",
         "impact": "官方Vitis解释器纯import后_runtime必然在xv_pycommontasks来源检查失败，尚不能进入自有session创建与授权visibility0流程。简单重复path配置又与_preflight路径唯一性冲突。",
         "basis": "native_origins.json：sys.modules两个key是同一对象/__name__='vivado'/spec及loader均指向xv_hsmpytasks.pyd；两个GetModuleHandleW均成功，GetModuleFileNameW分别返回真实pyd路径，rawSHA为d49d8961e1c5a5809f8dae247fbab75dbab9e994faae297f81940d7d8fa26aa6及e897cefd76d64ee5cc8435b6cce217978d853bf275cacc48f44a4283a71e136c。",
         "close_when": "建立只适用于这组官方native别名的明确门禁，真实绑定两个已加载原生映像handle/path/rawSHA与官方共享module身份/metadata；保留两个供应文件独立binding与普通模块来源检查。官方解释器纯import必须通过交付配置_runtime/verify_runtime_sources，两个原生路径/哈希/别名关系漂移反例必须拒绝；不得仅放宽file/spec或把所有native统一跳过。",
         "evidence": ["actual_runtime_gate.json", "runtime_diagnostics.json", "native_origins.json"]},
        {"id": "T19-R2-P2-CLASS_ORIGIN", "priority": 2, "file": "vitis/run_s2b_visibility_probe.py", "lines": [145,151,156],
         "title": "接收器Class定义模块及实际dispatch Class别名未绑定",
         "impact": "将Session或Target替换为带官方方法code但来自错误定义模块的fake Class，当前门禁开始前及自有fake receiver验证均接受。只比较type(obj)与当前模块中已替换Class，不能证明真实SDKClass来源。",
         "basis": "class_origin_counterexample.json：Session.__module__='review_wrong_receiver_source'与Target.__module__='review_wrong_target_source'都被接受；所有函数保持未执行的官方源码code object，证据为mock，不是实际SDK对象。",
         "close_when": "在开始前检查Session/Target Class定义模块/名称及真实dispatch.Session使用的Class身份与官方模块Class一致，并在receiver阶段复核；错误Class定义模块/名称、dispatch别名以及替换接收器独立反例必须被拒绝，正常真实官方纯import门禁通过。",
         "evidence": ["class_origin_counterexample.py", "class_origin_counterexample.json"]}
    ],
    "commands": commands,
    "artifact_files": artifact_files,
    "limits": ["G2 CHANGES_REQUIRED，G3/G4/G5未通过；未创建真实SDK会话/连接/serialopen/stop/reset/download，未操作root服务器或硬件。",
               "原G1、原R1失败证据、源文件、STATE与Git提交未改；本代理未提交。",
               "第一次17/53重放既有fixture明确指定ROOT/tmp/2B/S2B-T19父目录，因此tempfile.tempdir未重定位unit_*输出；已向root报告保留，后续独立fixture用mkdtemp覆盖均隔离到本目录。",
               "Vitis包装器外层退出0不能代表脚本内部成功；本审查同时保存脚本状态与外层原生命令码。",
               "完整运行依赖真实compat receipt和root批准仍未到；没有伪造实际PASS或visibility/cold事实。",
               "SDK供应源码来自实机只读检查；底层OS/DLL依赖未做完整源码冻结，峰值内存未测。"]
}
with (folder/"review_receipt.json").open("x", encoding="utf-8") as output:
    json.dump(record, output, ensure_ascii=False, indent=2)
print(json.dumps({"status": record["status"], "receipt_sha256": sha(folder/"review_receipt.json"), "artifact_files": len(artifact_files), "source_still_bound": True}))
