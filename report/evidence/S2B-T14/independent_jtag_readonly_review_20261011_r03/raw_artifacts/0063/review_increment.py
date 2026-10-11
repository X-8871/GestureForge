import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

# 只读增量核验实际cmd转录；不运行服务脚本、不访问SDK或硬件。
root = Path.cwd().resolve()
out = Path(__file__).resolve().parent
e = root / "report/evidence/S2B-T14/jtag_readonly_20261011_r02"
prior = root / "tmp/2B/S2B-T14/independent_jtag_readonly_review_20261011_r02"
checks = []
seen = {}
started = time.monotonic()

def raw(path, role="input"):
    path = Path(path)
    if not path.is_absolute():
        path = root / path
    assert path.is_file() and not path.is_symlink(), str(path)
    value = path.read_bytes()
    key = path.relative_to(root).as_posix()
    seen[key] = {"path": key, "sha256": hashlib.sha256(value).hexdigest(), "role": role}
    return value

def obj(path):
    return json.loads(raw(path))

def check(name, ok, evidence):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "evidence": evidence})

old = obj(e / "delivery_manifest_r02.json")
new = obj(e / "delivery_manifest_r03.json")
relay = obj(e / "executed_command_input_relay.json")
check("旧r02与新r03/relay冻结SHA", hashlib.sha256(raw(e / "delivery_manifest_r02.json")).hexdigest() == "2a34d5dee052c78650b332dbd771e4862cadf08e1653c7a86fa57fcd7260ad75" and hashlib.sha256(raw(e / "delivery_manifest_r03.json")).hexdigest() == "44ef98756380bdd9e5c7218ca619b0782bf504a78e243a06da869f2f833bf585" and hashlib.sha256(raw(e / "executed_command_input_relay.json")).hexdigest() == "c9c5b35fabcf5df5de3c6cbf47ce56022b957a67d197900d54de1497ae39c348", "三份原件不改写")
check("旧27绑定保留/新29仅加两项", len(old["files"]) == 27 and len(new["files"]) == 29 and new["files"][:27] == old["files"] and {Path(x["path"]).name for x in new["files"][27:]} == {"delivery_manifest_r02.json", "executed_command_input_relay.json"}, "原结果/日志/源码未变化")
for entry in new["files"]:
    value = raw(entry["path"], entry["role"])
    check("绑定SHA：" + Path(entry["path"]).name, set(entry) == {"path", "sha256", "role"} and hashlib.sha256(value).hexdigest() == entry["sha256"], entry["sha256"])
check("relay披露逐字转录及未捕获argv", relay["observation_source"] == "ROOT_TOOL_CALL_INPUT_RELAY" and relay["source_commit"] == old["source_commit"] and "外层PowerShell启动argv未捕获" in relay["limitations"][0] and "不是该次实际cmd输入" in relay["limitations"][1], relay["limitations"])
for name, script, result in (("本任务独占服务启动", "start_owned_server.ps1", "start_server_native.json"), ("本任务服务身份核对与闭合", "close_owned_server.ps1", "close_server_native.json")):
    rows = [x for x in relay["calls"] if x["name"] == name]
    assert len(rows) == 1
    row = rows[0]
    before = next(x for x in old["checks"] if x["name"] == name)
    after = next(x for x in new["checks"] if x["name"] == name)
    original_result = obj(e / result)
    target = root / "tmp/2B/S2B-T14/jtag_readonly_20261011_r02" / script
    assert target.is_file()
    expected = "$ErrorActionPreference='Stop'; & '" + str(target.resolve()) + "'"
    check("实际cmd转录与原结果：" + name, row["tool"] == "exec_command" and row["input"] == {"cmd": expected} and row["result"] == original_result and after["command"] == expected and after["exit_code"] == before["exit_code"] == original_result["exit_code"] == 0, {"command": expected, "return_chunk": original_result["chunk_id"], "host_exit_code": original_result["exit_code"], "outer_argv_captured": False})
    expected_after = dict(before)
    expected_after["command"] = expected
    expected_after["reason"] += " 实际工具cmd输入见executed_command_input_relay.json，外层shell argv未采集。"
    check("仅command及来源说明更正：" + name, after == expected_after, "PASS/码/名称不修改")
expected_new = dict(old)
expected_new["files"] = new["files"]
expected_new["checks"] = new["checks"]
expected_new["limitations"] = new["limitations"]
check("其余manifest字段与check/限制保持", new == expected_new and len(new["limitations"]) == len(old["limitations"]) + 1 and new["limitations"][:-1] == old["limitations"] and all(new["checks"][i] == old["checks"][i] for i in (0, 3, 4)), "无验收状态或工具版本扩张")
old_receipt = obj(prior / "final_review_receipt.json")
old_raw = raw(prior / "raw_manifest.jsonl", "artifact")
check("旧独立receipt/raw未改", hashlib.sha256(raw(prior / "final_review_receipt.json")).hexdigest() == "74918612225fa9105e16a5a7ac5d4c691a27ff9e8568fa3c811d3e1a74e7a974" and hashlib.sha256(old_raw).hexdigest() == "94db5024be7cd835f985ff07652e779a0137c01a0109a0f6361eb77663a7beb6" and old_receipt["status"] == "PASS", "只继承已审只读连接/归属/清理结果准确性")
old_records = [json.loads(line) for line in old_raw.decode("utf-8").splitlines()]
check("旧78审查原件全部未改", len(old_records) == 78 and all(hashlib.sha256(raw(x["path"], x["role"])).hexdigest() == x["sha256"] for x in old_records), 78)
checker = prior / "check_stage_delivery_snapshot.py"
argv = [sys.executable, "-B", "-X", "utf8", str(checker), "--mode", "evidence", "--manifest", str(e / "delivery_manifest_r03.json"), "--project-root", str(root)]
t = time.monotonic()
cp = subprocess.run(argv, cwd=root, capture_output=True, check=False)
for suffix, content in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
    with (out / ("evidence." + suffix)).open("xb") as stream:
        stream.write(content)
native = {"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - t}
with (out / "evidence.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(native, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
check("新manifest实际machine evidence0", cp.returncode == 0 and json.loads(cp.stdout)["status"] == "CHECKS_OK", native)
result = {"status": "PASS" if all(x["status"] == "PASS" for x in checks) else "CHANGES_REQUIRED", "source_commit": old["source_commit"], "reviewed_manifest_hash": "44ef98756380bdd9e5c7218ca619b0782bf504a78e243a06da869f2f833bf585", "scope": "T14 r03实际exec_command cmd转录更正增量审查，继承既有只读连接/服务归属/清理证据PASS", "checks": checks, "commands": [native], "review_elapsed_seconds": time.monotonic() - started, "peak_memory_bytes": None, "reviewer_stop": "STOP_READONLY_INCREMENT_REVIEW_FROZEN", "limits": ["relay为ROOT逐字转录，外层shell argv未捕获，不声称恢复外层argv", "旧r02命令为等价复现写法，其原件和既有审查均完整保留", "只更正两条命令，不重跑硬件；清理宿主0与真实服务退出-1保持分列", "inputs业务上游不适用；evidence0仅包装，未验证BOOT0/EOS/DDR/PSinit/时钟/模型/109/1000/G3-G5", "未读写S9、不操作SDK/ROSS/硬件/Git/STATE/正式证据"], "findings": []}
with (out / "review_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
with (out / "inputs_raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
    for entry in sorted(seen.values(), key=lambda x: x["path"]):
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
print(json.dumps({"status": result["status"], "checks": len(checks), "failed_checks": [x for x in checks if x["status"] == "FAIL"], "review_elapsed_seconds": result["review_elapsed_seconds"]}, ensure_ascii=False))
raise SystemExit(0 if result["status"] == "PASS" else 2)
