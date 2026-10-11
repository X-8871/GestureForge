import hashlib
import json
import os
import sys
from pathlib import Path

import psutil

# 冻结当前工具与实际自测结果，不拷贝历史原件，不修改项目正式证据。
out = Path(__file__).absolute().parent
root = out.parents[3]
plan = out.parent / "s10_root_run_20261012_r01/resource_plan.json"
final_tests = json.loads((out / "selftest_r03/selftest_results.json").read_text(encoding="utf-8"))
supplement = json.loads((out / "supplement_results.json").read_text(encoding="utf-8"))
assert final_tests["status"] == supplement["status"] == "PASS"
guard_sha = hashlib.sha256((out / "guard.py").read_bytes()).hexdigest()
assert supplement["source_sha256"] == guard_sha
objects = []
for test in final_tests["cases"]:
    objects.extend(test["identities"])
for path in (out / "rss_stop_tree/monitor/samples.jsonl", out / "stop_request_fixture/monitor/samples.jsonl"):
    for line in path.read_text(encoding="utf-8").splitlines():
        objects.extend(json.loads(line)["members"])
readback = []
for pid, birth in sorted({(x["pid"], x["create_time"]) for x in objects}):
    try:
        process = psutil.Process(pid)
        actual_birth = process.create_time()
        status = "PID_REUSED_OTHER_OBJECT_NOT_TOUCHED" if actual_birth != birth else "STILL_PRESENT"
    except psutil.NoSuchProcess:
        status = "ABSENT"
    readback.append({"pid": pid, "expected_create_time": birth, "status": status})
assert all(x["status"] != "STILL_PRESENT" for x in readback)
with (out / "fixture_final_readback.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump({"status": "PASS", "processes": readback, "no_stop_called": True}, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
entries = []
for path in sorted(out.rglob("*")):
    if not path.is_file():
        continue
    assert path.suffix.lower() not in {".exe", ".obj", ".dcp", ".bit", ".pyc"}
    role = "source" if path.suffix == ".py" else "log" if path.suffix in {".log", ".jsonl"} else "result"
    entries.append({"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role})
entries.append({"path": plan.relative_to(root).as_posix(), "sha256": hashlib.sha256(plan.read_bytes()).hexdigest(), "role": "input"})
manifest = out / "raw_manifest.jsonl"
with manifest.open("x", encoding="utf-8", newline="\n") as stream:
    for row in sorted(entries, key=lambda x: x["path"]):
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
native = {name: json.loads((out / name).read_text(encoding="utf-8")) for name in ("selftest.native.json", "selftest_r02.native.json", "selftest_r03.native.json", "supplement.native.json")}
receipt = {"schema_version": 1, "status": "PASS_TOOL_SELFTEST_ONLY", "task": "S10-RG1", "developer_stop": "STOP_NO_ACTIVE_GUARD_OR_FIXTURE", "source_commit": "3f24c94564d10103aaa00db07356f666b085f687", "guard_path": str(out / "guard.py"), "guard_sha256": guard_sha, "plan_path": str(plan), "plan_sha256": hashlib.sha256(plan.read_bytes()).hexdigest(), "python": sys.executable, "psutil_version": psutil.__version__, "actual_commands": native, "final_cases": [{k: x[k] for k in ("name", "pass", "actual_status", "native_exit_code")} for x in final_tests["cases"]], "supplement": supplement, "raw_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(), "raw_manifest_lines": len(entries), "limits": {"tree_rss_bytes": 6442450944, "available_ram_stop_bytes": 536870912, "c_disk_free_stop_bytes": 8589934592, "interval_seconds": 1}, "initial_failure": {"native_exit_code": 1, "reason": "父链返回末端根身份导致资源夹具根先结束；仅自有测试子对象遗留，夹具自然退出后真实读回ABSENT。错误版源码、stdout/stderr/native及案例原件完整保留。", "fixed": "verified_chain返回候选leaf身份，最终r03真实父子全部停止；清理只用已核身份自有测试对象。"}, "runtime_usage": {"command": [sys.executable, "-B", "-X", "utf8", str(out / "guard.py"), "--plan", "<绝对精确resource_plan.json>", "--binding", "<绝对精确UTF8 binding.json>", "--output-dir", "<不存在的新监测目录>"], "required_binding_keys": ["pid", "create_time", "exe", "cwd", "allowed_run_dirs", "run_id", "source_commit"], "binding_paths": "使用psutil真实exe/cwd返回的逐字符值；ROOT显式绑定本轮每个允许目录，不能加入其它窗口目录。", "stop_request": "仅监测输出目录/STOP_REQUEST普通文件；停止后不重启。", "optional_fields": {"progress_logs": "绝对精确且已存在的本轮日志路径列表", "no_progress_seconds": 900, "max_seconds": "正数观察期限；到期仅停止守卫并BLOCKED，任务保持不动。默认不设期限。"}, "exit_codes": {"0": "已核根正常缺失，未判断设计成功", "2": "资源/STOP_REQUEST触发且完整停止已核本轮树", "3": "BLOCKED或STOP_PARTIAL，须读retained", "1": "启动错误或拒绝覆盖输出，保留调用方stderr"}}, "limits_and_unrun": ["仅新工具开发自测；未启动Vivado、ROSS、硬件或项目重型任务", "PID复用用真实PID错误创建时间模拟，未声称OS实际发生复用", "真实越限由fixture阈值1B触发；未分配GiB，RAM/C盘低阈值分支未真实压低系统资源", "1秒离散采样不是连续峰值；OS不提供跨树原子身份与停止事务", "身份、cwd或实际父链不确定的对象不动，保留根并STOP_PARTIAL/BLOCKED", "可选900秒只观察指定日志size/mtime，不用CPU活动替代设计进度；未等待900秒自测", "父进程缺失/复用终态不会再恢复或重新启动；guard退出后没有持续守护能力", "实际Vivado子进程cwd可读性和允许目录由ROOT启动前核实，本工具自测不等于真实平台准入", "不更改旧S9预算或原件，不批准时序/部署/模型/109/1000/G3-G5", "Reviewer/G2尚未执行；本子代理无源码Git提交权限，ROOT负责审读与消费"], "elapsed_seconds": {"final_selftest": final_tests["elapsed_seconds"], "supplement": supplement["elapsed_seconds"]}, "peak_memory_bytes": None}
path = out / "tool_receipt.json"
with path.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": receipt["status"], "guard_sha256": guard_sha, "receipt_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "raw_manifest_sha256": receipt["raw_manifest_sha256"], "raw_manifest_lines": len(entries), "stop": receipt["developer_stop"]}, ensure_ascii=False))
