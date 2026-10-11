import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

# 独立快审仅调用无写入校验函数及AST提取的纯history校验段，绝不执行collect/source/seal。
ROOT = Path.cwd().resolve()
OUT = Path(__file__).absolute().parent
W = ROOT / "tmp/2B/S2B-T17/s10_collection_20261012_r02"
OLD = W.parent / "s10_collection_20261012_r01"
COMMIT = "1eed350c43aae4cdee1f8179a93ce87d75d9f2a8"
started = time.monotonic()
seen = {}
checks = []
commands = []


def read(path, role="input"):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    seen[path.relative_to(ROOT).as_posix()] = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "role": role}
    return data


def obj(path):
    return json.loads(read(path).decode("utf-8"))


def check(name, condition, evidence):
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "evidence": evidence})


def validate_row(row):
    data = read(ROOT / row["path"])
    return hashlib.sha256(data).hexdigest() == row["sha256"] and len(data) == row["bytes"]


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


for name, expected in [("collector.py", "212c435081d15347d0353351f9bd893e85869173e8c5ce338ab8492ed1ce4e32"), ("native.py", "ca5f2b0a2b670d0ac73068480d8f7dd1f50921172ceaa44f3773dad627b1c2fd"), ("prepared_receipt.json", "7449541264cc74262a471c13b35f63af8dd5dbc42d74120960586c4508483a0a")]:
    check("固定输入SHA：" + name, hashlib.sha256(read(W / name, "source" if name.endswith(".py") else "input")).hexdigest() == expected, expected)
current_text = read(W / "collector.py", "source").decode("utf-8")
native_text = read(W / "native.py", "source").decode("utf-8")
old_text = read(OLD / "collector.py", "source").decode("utf-8")
check("原生wrapper字节未变且只调用r02collector", read(W / "native.py") == read(OLD / "native.py", "source") and 'str(exact(WORK/"collector.py"))' in native_text and 'WORK=ROOT/"tmp/2B/S2B-T17/s10_collection_20261012_r02"' in current_text, "r01 source包装保持，未来r02 collector由WORK限定")
tree = ast.parse(current_text)
old_tree = ast.parse(old_text)
nodes = {x.name: x for x in tree.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))}
old_nodes = {x.name: x for x in old_tree.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))}
changed = [name for name in old_nodes if ast.dump(old_nodes[name]) != ast.dump(nodes[name])]
check("差异仅准备/关闭标签/收集失败保留", set(changed) == {"prepare", "closed_gate", "collect"} and set(nodes) - set(old_nodes) == {"failed_setup_expected", "check_failed_setup"}, {"changed": changed, "added": sorted(set(nodes) - set(old_nodes))})
receipt = obj(W / "prepared_receipt.json")
prior = obj(OLD / "prepared_receipt.json")
labels = ["source", "builder", "setup_failed", "setup", "launch", "wait", "open_run", "reports", "query_xdc", "close"]
check("准备绑定旧r01/新r02/十标签", all(validate_row(x) for x in receipt["prepared_scripts"] + receipt["predecessor_scripts"] + [receipt["predecessor_preparation"], receipt["existing_source_before"], receipt["setup_failed_actual"], receipt["source_freeze"]]) and receipt["history_labels"] == labels and receipt["setup_failed_native_exit_code"] == 1 and receipt["source_count"] == 43 and receipt["static_count"] == 33, "43/33/18/8，准备不自报source/collect已执行")
before = obj(ROOT / receipt["existing_source_before"]["path"])
freeze = obj(ROOT / receipt["source_freeze"]["path"])
check("真实source_before基线/profile/闭包", before["source_commit"] == COMMIT and before["source_count"] == 43 and before["platform_static_source_count"] == 33 and before["profile_version"] == "s2b-inference-platform/0.1.10" and before["source_sha256"] == {x["path"]: x["sha256"] for x in freeze["source_files"]}, "仅声明依赖，不读43源码或当前综合")
before_native = obj(W.parent / "s10_root_run_20261012_r01/s10_source_before_r01.native.json")
prepare_native = obj(W / "s10_preparation_r02.native.json")
check("真实before/prepare包装0分列", before_native["native_exit_code"] == prepare_native["native_exit_code"] == 0 and prepare_native["host_shell_exit_code"] is None and str(W / "collector.py") in prepare_native["command"] and str(OLD / "collector.py") in before_native["command"] and all(validate_row(x) for x in prepare_native["closed_logs"] + before_native["closed_logs"]), "旧source_before实际0；新prepare实际0，不冒充当前collect0")
spec = importlib.util.spec_from_file_location("readonly_collector_r02", W / "collector.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
failed = c.failed_setup_expected()
read(c.SETUP_FAILED_ACTUAL)
success = c.mcp_json(obj(c.CACHE / "s10_setup_actual.tool.json"))
check("首次setup失败1与成功0分列", failed["code"] == 1 and success["exit_code"] == 0, "错20261011路径原件完整，成功使用20261012；未执行任何MCP")
# 从原AST逐条提取history段，保持原逻辑；跳过所有collect写入与报告扫描。
body = nodes["collect"].body
begin = next(i for i, n in enumerate(body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "history" for t in n.targets))
end = next(i for i, n in enumerate(body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "native" for t in n.targets))
probe = ast.FunctionDef(name="probe_history", args=ast.arguments(posonlyargs=[], args=[ast.arg(arg="gate")], kwonlyargs=[], kw_defaults=[], defaults=[]), body=copy.deepcopy(body[begin:end]) + [ast.Return(value=ast.Name(id="paired", ctx=ast.Load()))], decorator_list=[])
module = ast.fix_missing_locations(ast.Module(body=[probe], type_ignores=[]))
namespace = dict(c.__dict__)
exec(compile(module, str(W / "collector.py") + "::PURE_HISTORY_AST", "exec"), namespace)
fixtures = OUT / "fixtures"
fixtures.mkdir()
history = []
calls = []
for label in labels:
    command = failed["command"] if label == "setup_failed" else failed["command"].replace("s10_platform_20261011_r01/setup_synthesis.tcldict", "s10_platform_20261012_r01/setup_synthesis.tcldict") if label == "setup" else "close_project" if label == "close" else "wait_on_run synth_1" if label == "wait" else "SYNTHETIC_" + label
    code = 1 if label in {"builder", "setup_failed"} else 0
    output = failed["output"] if label == "setup_failed" else ("status {synth_design Complete!} progress 100% " * 5 + "status {Not started} progress 0% " * 5 + "clock_period 20.000") if label == "query_xdc" else "SYNTHETIC_ONLY"
    item = {"command": command, "code": code, "output": output, "elapsed": 336.601 if label == "wait" else 0.01}
    history.append(item)
    result = {"isError": True, "content": [{"type": "text", "text": "SYNTHETIC client timeout after 300s"}]} if label == "wait" else {"content": [{"type": "text", "text": json.dumps({"exit_code": code, "output": output})}]}
    path = fixtures / (label + ".json")
    save(path, {"input": {"command": command}, "result": result})
    calls.append({"label": label, "path": path.relative_to(ROOT).as_posix()})
history_path = fixtures / "history.json"
save(history_path, {"content": [{"type": "text", "text": json.dumps({"history": history})}]})
gate = {"mcp_history": {"path": history_path.relative_to(ROOT).as_posix()}, "design_mcp_records": calls}
paired = namespace["probe_history"](gate)
check("合成十history失败行/客户端超时不混码", len(paired) == 10 and paired[2]["native_history"]["code"] == 1 and paired[3]["native_history"]["code"] == 0 and paired[5]["native_history"]["code"] == 0 and paired[5]["client_timeout"] is True and paired[5]["client_exit_code"] is None and paired[1]["client_exit_code"] == 1, "数据全部合成，仅setup_failed字段复用实际关闭原件")
rejections = []
for field, replacement in [("code", 0), ("command", failed["command"] + " altered"), ("output", "hidden failure")]:
    item = {**failed, field: replacement}
    try:
        c.check_failed_setup(item)
    except ValueError as error:
        rejections.append({"field": field, "reason": str(error)})
check("失败code/command/output改写均拒绝", len(rejections) == 3, rejections)
short = fixtures / "history_missing_failed.json"
save(short, {"content": [{"type": "text", "text": json.dumps({"history": history[:2] + history[3:]})}]})
try:
    namespace["probe_history"]({**gate, "mcp_history": {"path": short.relative_to(ROOT).as_posix()}})
    rejected = False
except ValueError as error:
    rejected = "数量不同" in str(error)
check("丢失败行history数量拒绝", rejected, "9不能充作10")
argv = [sys.executable, "-B", "-X", "utf8", str(W / "collector.py"), "collect", "--commit", COMMIT]
start = time.monotonic()
cp = subprocess.run(argv, capture_output=True, check=False, timeout=10)
for suffix, data in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
    (OUT / ("missing_gate." + suffix)).write_bytes(data)
record = {"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - start}
save(OUT / "missing_gate.native.json", record)
commands.append(record)
check("独立缺gate原生1且未进collect", cp.returncode == 1 and "缺少ROOT明确关闭门禁" in cp.stderr.decode("utf-8") and "collect(args.commit,args.gate)" not in cp.stderr.decode("utf-8"), "仅main参数拒绝，未执行实际collect")
check("OS/capture/native分列仍保留", 'raw_os_process_exit_code=None' in current_text and 'products_native_exit_code=products_native,products_capture_exit_code=products_capture' in current_text and 'host_shell_exit_code=None' in native_text, "OS未捕获null；products native/capture及client/nativewait分别绑定")
result = {"status": "PASS" if all(x["status"] == "PASS" for x in checks) else "CHANGES_REQUIRED", "scope": "S10 collector r02增量：首次setup失败原件/十history/新旧工具与source_before绑定/原生包装和缺gate拒绝", "source_commit": COMMIT, "checks": checks, "findings": [x for x in checks if x["status"] == "FAIL"], "commands": commands, "reviewer_stop": "STOP_READONLY_COLLECTOR_REVIEW", "elapsed_seconds": time.monotonic() - started, "peak_memory_bytes": None, "limitations": ["合成history不是S10实际综合结果；仅首次失败原件和已关闭setup返回读取", "未执行prepare/collect函数/source/seal、STA、ROSS、Vivado、硬件或owned进程查询/停止", "正式S10输入闭合及输出收集仍由ROOT在关闭后执行；此PASS不批准实际证据包、STA或部署", "未重复读全43源码或191历史文件；当前重型任务未触碰"]}
save(OUT / "review_result.json", result)
save(OUT / "review_inputs.json", list(seen.values()))
print(json.dumps({"status": result["status"], "checks": len(checks), "findings": result["findings"], "elapsed_seconds": result["elapsed_seconds"]}, ensure_ascii=False))
raise SystemExit(0 if result["status"] == "PASS" else 2)
