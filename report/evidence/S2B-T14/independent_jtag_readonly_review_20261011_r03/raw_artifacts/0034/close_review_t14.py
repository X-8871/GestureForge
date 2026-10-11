import ast
import difflib
import hashlib
import json
from pathlib import Path

# 字符串限制文本不代表可执行命令；按语法树验证包装脚本的实际进程调用。
root = Path.cwd().resolve()
out = Path(__file__).resolve().parent
e = root / "report/evidence/S2B-T14/jtag_readonly_20261011_r02"
initial = json.loads((out / "review_result.json").read_text(encoding="utf-8"))
failed = [x["name"] for x in initial["checks"] if x["status"] == "FAIL"]
assert failed == ["修复包装未重复硬件"], failed
source = (e / "package_r02.py").read_text(encoding="utf-8")
tree = ast.parse(source)
calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
subprocess_calls = [node for node in calls if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess"]
actual = [ast.unparse(node) for node in subprocess_calls if node.func.attr in {"run", "check_output", "Popen", "call", "check_call"}]
assert len(actual) == 2
assert any(node.func.attr == "check_output" and ast.literal_eval(node.args[0]) == ["git", "rev-parse", "HEAD"] for node in subprocess_calls)
assert any(node.func.attr == "run" and isinstance(node.args[0], ast.Name) and node.args[0].id == "command" for node in subprocess_calls)
command_defs = [node.value for node in ast.walk(tree) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "command" for target in node.targets)]
assert len(command_defs) == 1 and isinstance(command_defs[0], ast.List)
command_text = ast.unparse(command_defs[0])
assert "verification/check_stage_delivery.py" in command_text and "'--mode', 'evidence'" in command_text and "'--project-root'" in command_text
assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) and any(alias.name == "xsdb" for alias in node.names) for node in ast.walk(tree))
assert not any(isinstance(node, ast.Attribute) and node.attr in {"start_debug_session", "connect", "targets", "mrd", "mwr", "stop", "rst", "reset", "dow", "con", "fpga"} for node in ast.walk(tree))
old_source = (e / "package.py").read_text(encoding="utf-8")
diff = "".join(difflib.unified_diff(old_source.splitlines(keepends=True), source.splitlines(keepends=True), fromfile="package.py", tofile="package_r02.py"))
with (out / "package_encoding_diff.txt").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(diff)
assert 'if path.name != "vitis_probe.stdout.log":' in source
assert hashlib.sha256((e / "delivery_manifest_r02.json").read_bytes()).hexdigest() == initial["reviewed_manifest_hash"]
correction = {"name": "包装实际AST调用范围复核", "status": "PASS", "original_reviewer_false_positive": "字符串Stop-Process来自限制说明文字，原审查器用字符串匹配误报；原native2/stdout/stderr保持原样。", "actual_subprocess_calls": actual, "actual_checker_command_definition": command_text, "hardware_reexecution": "NOT_RUN", "sdk_import_or_target_api": "NONE", "evidence": "冻结package.py与package_r02.py差异及AST确认：仅Git HEAD查询和轻量evidence检查，未重跑Vitis或服务。"}
initial["status"] = "PASS"
initial["checks"].append(correction)
initial["resolved_reviewer_failures"] = [correction]
initial["findings"] = []
initial["reviewer_stop"] = "STOP_READONLY_REVIEW_FROZEN"
with (out / "final_review_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(initial, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": "PASS", "checks": len(initial["checks"]), "resolved_reviewer_false_positives": 1, "hardware": "NOT_RUN"}, ensure_ascii=False))
