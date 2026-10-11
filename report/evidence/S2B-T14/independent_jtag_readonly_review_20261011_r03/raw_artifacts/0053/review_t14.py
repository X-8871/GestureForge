import ast
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 本脚本只读已关闭原件；不导入XSDB、不执行服务脚本、不调用硬件。
ROOT = Path.cwd().resolve()
OUT = Path(__file__).resolve().parent
RUN = ROOT / "tmp/2B/S2B-T14/jtag_readonly_20261011_r02"
E = ROOT / "report/evidence/S2B-T14/jtag_readonly_20261011_r02"
COMMIT = "5ea54b441bd885e10eac4794cbad5ad48c510a49"
HASH = "2a34d5dee052c78650b332dbd771e4862cadf08e1653c7a86fa57fcd7260ad75"
checks = []
inputs = {}
commands = []
started = time.monotonic()

def read(path, role="input"):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    assert path.is_file() and not path.is_symlink(), str(path)
    value = path.read_bytes()
    key = path.relative_to(ROOT).as_posix()
    inputs[key] = {"path": key, "sha256": hashlib.sha256(value).hexdigest(), "role": role}
    return value

def obj(name):
    return json.loads(read(E / name).decode("utf-8"))

def check(name, condition, evidence):
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "evidence": evidence})

def command(label, argv):
    start = time.monotonic()
    value = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False)
    for suffix, output in (("stdout.log", value.stdout), ("stderr.log", value.stderr)):
        with (OUT / (label + "." + suffix)).open("xb") as stream:
            stream.write(output)
    record = {"command": argv, "native_exit_code": value.returncode, "elapsed_seconds": time.monotonic() - start}
    with (OUT / (label + ".native.json")).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    commands.append(record)
    return value

manifest_raw = read(E / "delivery_manifest_r02.json")
manifest = json.loads(manifest_raw)
check("冻结清单SHA与基线", hashlib.sha256(manifest_raw).hexdigest() == HASH and manifest["source_commit"] == COMMIT and len(manifest["files"]) == 27, {"sha256": HASH, "files": len(manifest["files"])})
for entry in manifest["files"]:
    value = read(entry["path"], entry["role"])
    check("清单字节：" + Path(entry["path"]).name, hashlib.sha256(value).hexdigest() == entry["sha256"] and set(entry) == {"path", "sha256", "role"}, entry["sha256"])
    original = RUN / Path(entry["path"]).name
    if original.is_file():
        check("原件与正式副本：" + original.name, value == read(original, entry["role"]), original.relative_to(ROOT).as_posix())
    if Path(entry["path"]).suffix in {".py", ".ps1", ".json"}:
        value.decode("utf-8", errors="strict")
check("interfaces和inputs业务依赖不适用", manifest["interfaces"] == [] and manifest["interfaces_not_applicable_reason"] == "只读目标枚举与服务生命周期，不消费CSR/AXI/memory业务接口。", "本Run不消费冻结业务接口或模型上游；不新增inputs功能核验，也不批准G0。")
probe = read(E / "jtag_targets_probe.py", "source")
prior = command("prior_probe_git", ["git", "show", COMMIT + ":report/evidence/S2B-T14/jtag_readonly_20261011_r01/jtag_targets_probe.py"])
check("已审probe逐字节未变", prior.returncode == 0 and prior.stdout == probe and hashlib.sha256(probe).hexdigest() == "201dc67de8427662fdf1852309c270eda24f2a9bf70cc2670802b152208c3dc6", "以明确基线Git对象直接比较")
tree = ast.parse(probe.decode("utf-8"))
sdk_calls = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in {"xsdb", "sdk", "session"}:
        sdk_calls.append(node.func.value.id + "." + node.func.attr)
check("probe仅五类SDK调用", sorted(sdk_calls) == sorted(["xsdb.start_debug_session", "session.connect", "session.targets", "session.disconnect", "sdk.dispose"]), sdk_calls)
check("无目标写入停止下载执行API", not any(isinstance(node, ast.Attribute) and node.attr in {"mrd", "mwr", "stop", "rst", "reset", "dow", "con", "fpga"} for node in ast.walk(tree)), "AST语法树审查，未运行probe")
identity = obj("hw_server_identity.json")
launcher = obj("launcher_identity.json")
close = obj("server_close.json")
native = obj("vitis_probe.native.json")
result = obj("jtag_targets_result.json")
host = obj("host_resource_preflight.json")
host_result = json.loads(host["value"]["output"])
ports = host_result["serial"]
check("22:41 COM4身份和error0", host["value"]["exit_code"] == 0 and len(ports) == 1 and ports[0]["DeviceID"] == "COM4" and ports[0]["PNPDeviceID"] == "USB\\VID_10C4&PID_EA60\\D02E61162787ED11A536569F9D1CC348" and ports[0]["ConfigManagerErrorCode"] == 0 and host_result["tools"] == [], host_result)
preflight = obj("listener_preflight.json")
preflight_result = json.loads(preflight["value"]["output"])
check("启动前服务及3121无占用", preflight["value"]["exit_code"] == 0 and preflight_result["servers"] == preflight_result["listeners"] == [], preflight_result)
expected_identity = {"ProcessId": 28124, "ParentProcessId": 28952, "ExecutablePath": "D:\\Xilinx\\2026.1\\Vitis\\bin\\unwrapped\\win64.o\\hw_server.exe", "CreationTimeFileTimeUtc": "134362033976752080"}
check("完整自有服务身份", identity["status"] == "OWNED_SERVER_READY" and identity["native"] == expected_identity and identity["native_sha256"] == "e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3" and identity["launcher_pid"] == launcher["launcher_pid"] == 28952 and identity["listeners"] == [{"LocalAddress": "0.0.0.0", "LocalPort": 3121, "OwningProcess": 28124}], identity)
server_samples = [x for x in result["calls"] if "server_snapshot" in x]
check("连接前后均核对归属与独占", len(server_samples) == 2 and all(x["exit_code"] == 0 and x["server_snapshot"]["servers"] == [expected_identity] and x["server_snapshot"]["listeners"] == identity["listeners"] for x in server_samples), server_samples)
native_argv = ["D:\\Xilinx\\2026.1\\Vitis\\bin\\vitis.bat", "-s", str(RUN / "jtag_targets_probe.py")]
check("公开Vitis命令及原生0", native["command"] == native_argv and native["native_exit_code"] == 0 and native["elapsed_seconds"] == 6.6595342 and native["peak_tree_rss_bytes"] is None, native)
host_native = obj("vitis_host_return.json")
check("Vitis原生与宿主返回一致", host_native["exit_code"] == 0 and json.loads(host_native["output"]) == native, "宿主6.8757714s与Vitis子进程6.6595342s口径分别保留")
targets = result["targets"]
target_list = list(targets.values())
apu = next(x for x in target_list if x["name"] == "APU")
cpu = [x for x in target_list if x["name"].startswith("ARM Cortex-A9")]
check("四目标同HS1链及两CPU Running", len(target_list) == 4 and {x["name"] for x in target_list} == {"APU", "ARM Cortex-A9 MPCore #0", "ARM Cortex-A9 MPCore #1", "xc7z020"} and {x["jtag_cable_serial"] for x in target_list} == {"210512180081"} and len(cpu) == 2 and all(x["parent_ctx"] == apu["target_ctx"] and x["state_reason"] == "Running" for x in cpu), "仅瞬时枚举，不证明处理器功能、BOOT模式或器件速度等级")
check("SDK disconnect/dispose闭合", result["status"] == "TARGETS_ENUMERATED" and result["cleanup_errors"] == [] and result["expected_hw_server_pid"] == 28124 and [x["api"] for x in result["calls"] if x.get("state") == "DONE"] == ["session.disconnect(chan=channel)", "xsdb.dispose()"], result["finished_at"])
start = read(E / "start_owned_server.ps1", "source").decode("utf-8")
closing = read(E / "close_owned_server.ps1", "source").decode("utf-8")
check("启动脚本占用与精确路径SHA门禁", "Start-Process -FilePath $taskExecutable.FullName" in start and "-WindowStyle Hidden" in start and "$taskServers.Count -ne 0 -or $taskListeners.Count -ne 0" in start and "e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3" in start and "-ArgumentList @('-s','tcp::3121')" in start and "ParentProcessId -ne $PID" in start, "仅自有服务启动，无目标命令")
check("关闭脚本身份四字段及窄Stop范围", closing.count("Stop-Process -Id $taskCurrent.ProcessId") == 1 and all(x in closing for x in ("ExecutablePath -cne $taskIdentity.native.ExecutablePath", "ParentProcessId -ne $taskIdentity.native.ParentProcessId", "CreationDate.ToFileTimeUtc() -cne $taskIdentity.native.CreationTimeFileTimeUtc", "$taskSha -cne $taskIdentity.native_sha256", "$taskProcess.WaitForExit(10000)", "$taskProcess.ExitCode")), "PID/创建时间/父PID/映像SHA均门禁，不按名称批量终止")
start_native = obj("start_server_native.json")
close_native = obj("close_server_native.json")
check("实际启动和关闭host0与JSON一致", start_native["exit_code"] == close_native["exit_code"] == 0 and json.loads(start_native["output"]) == identity and json.loads(close_native["output"]) == close, "真实host命令结果，不伪填服务码")
check("22:44:37服务强制释放真实-1", close["status"] == "OWNED_SERVER_CLOSED" and close["native_pid"] == 28124 and close["native_exit_code"] == -1 and close["identity_checked"] is True and close["native_absent"] is True and close["listeners"] == [] and close["launcher_current"] is None, "服务-1属于本次Stop-Process后的退出，不能解读为正常退出0")
encoding = obj("native_log_encoding_binding.json")
raw_log = read(E / "vitis_probe.stdout.log", "log")
utf8_log = read(E / "vitis_probe.stdout.utf8.log", "log")
try:
    raw_log.decode("utf-8", errors="strict")
    is_utf8 = True
except UnicodeDecodeError:
    is_utf8 = False
decoded = raw_log.decode("gbk", errors="strict")
rows = [line[len("JTAG_PROBE_RESULT "):] for line in decoded.splitlines() if line.startswith("JTAG_PROBE_RESULT ")]
check("GBK外部原字节及UTF8转换准确", not is_utf8 and len(raw_log) == 7763 and hashlib.sha256(raw_log).hexdigest() == encoding["original_sha256"] and decoded.encode("utf-8") == utf8_log and hashlib.sha256(utf8_log).hexdigest() == encoding["derived_sha256"] and len(rows) == 1 and json.loads(rows[0]) == result, "使用Python严格GBK解码独立复核Node TextDecoder结果；无替代字符或原日志改写")
first_fail = obj("package_initial_failure.json")
check("首轮包装失败透明保留", first_fail["status"] == "FAILED_PACKAGING_ONLY" and first_fail["observed_host_exit_code"] == 1 and "首轮未预先单独封存stdout/stderr" in first_fail["observation_source"] and "UnicodeDecodeError" in first_fail["exception"] and "decode(\"utf-8\")" in read(E / "package.py", "source").decode("utf-8"), "首轮stdout/stderr原字节不可恢复，准确说明不伪造")
package = read(E / "package_r02.py", "source").decode("utf-8")
check("修复包装未重复硬件", 'path.name != "vitis_probe.stdout.log"' in package and not any(x in package for x in ("import xsdb", "Start-Process", "Stop-Process", '"-s"')), "r02只变更外部原生日志UTF8判断，读取结果并复制与核验清单")
actual = json.loads(read(RUN / "package_actual_return_r02.json"))
actual_value = json.loads(actual["output"])
check("实际新包装返回0与冻结SHA", actual["exit_code"] == 0 and actual_value["manifest_sha256"] == HASH and actual_value["files"] == 27, actual)
checker_blob = command("checker_git", ["git", "show", COMMIT + ":verification/check_stage_delivery.py"])
assert checker_blob.returncode == 0
checker = OUT / "check_stage_delivery_snapshot.py"
with checker.open("xb") as stream:
    stream.write(checker_blob.stdout)
light = command("evidence", [sys.executable, "-B", "-X", "utf8", str(checker), "--mode", "evidence", "--manifest", str(E / "delivery_manifest_r02.json"), "--project-root", str(ROOT)])
light_result = json.loads(light.stdout)
check("独立真实evidence0", light.returncode == 0 and light_result["status"] == "CHECKS_OK" and light_result["task_id"] == "S2B-T14" and light_result["errors"] == [], "仅范围与绑定包装；不批准G3-G5")
check("原包装检查0及业务未执行", obj("package_check.native.json")["native_exit_code"] == 0 and all(x["hardware_program_execution"] == "NOT_RUN" for x in (identity, close, native, result)) and any(x["status"] == "NOT_RUN" for x in manifest["checks"]), "BOOT0/EOS/DDR/PSinit/时钟/模型/109/1000/G3-G5均未验证")
final = {"status": "PASS" if all(x["status"] == "PASS" for x in checks) else "CHANGES_REQUIRED", "source_commit": COMMIT, "reviewed_manifest_hash": HASH, "scope": "本次readonly JTAG目标枚举、服务归属/独占与清理结果准确性", "checks": checks, "commands": commands, "native_commands_reviewed": [native, {"command": "powershell.exe -NoProfile -File " + str(RUN / "start_owned_server.ps1"), "host_exit_code": 0}, {"command": "powershell.exe -NoProfile -File " + str(RUN / "close_owned_server.ps1"), "host_exit_code": 0, "service_native_exit_code": -1}], "limits": ["只读结果瞬时快照，无BOOT0/EOS/DDR/PSinit/时钟/模型/109/1000/G3-G5验收", "JTAG名称不证明器件系列/速度/温度等级；inputs业务上游不适用，不新增功能批准", "峰内存未测null；Vitis原生耗时6.6595342s", "首次包装严格UTF8失败host1已保留；其stdout/stderr未预先单独封存，不声称恢复原字节", "Reviewer未执行SDK/ROSS/硬件或重型任务，不读写S9候选，不改Git/STATE/正式证据"], "reviewer_stop": "STOP_READONLY_REVIEW_FROZEN", "created_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "review_elapsed_seconds": time.monotonic() - started, "peak_memory_bytes": None}
with (OUT / "review_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(final, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
with (OUT / "inputs_raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
    for row in sorted(inputs.values(), key=lambda x: x["path"]):
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
print(json.dumps({"status": final["status"], "checks": len(checks), "failed_checks": [x for x in checks if x["status"] == "FAIL"], "review_elapsed_seconds": final["review_elapsed_seconds"]}, ensure_ascii=False))
raise SystemExit(0 if final["status"] == "PASS" else 2)
