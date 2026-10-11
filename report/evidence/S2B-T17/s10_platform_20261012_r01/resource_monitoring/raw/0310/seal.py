import hashlib
import json
import sys
from pathlib import Path

import psutil

# 冻结r02最终工具和本轮真实轻量自测，只绑定旧原件SHA，不复制历史目录。
base = Path(__file__).absolute().parent
root = base.parents[3]
old = base.parent / "s10_resource_guard_20261012_r01"
review = base.parent / "independent_s10_resource_guard_review_20261012_r01"
plan = base.parent / "s10_root_run_20261012_r01/resource_plan.json"
expected = [(old / "guard.py", "a6135186733a07b3257ad4f6a36d6ee57b8799b70c0d5fbc6c04abfc51035416"), (old / "tool_receipt.json", "936fad74fc5f3c0f9184238afef8d1563e6458fa7e9fcce667fda4cded1b4c00"), (old / "raw_manifest.jsonl", "a1cf069cbce778af949d148173102ec705dacd413723225cb9fdf0a36aa093be"), (review / "final_review_receipt.json", "d05272a5785583c020b4faec6f9947eec26abf2fe33de7691d09bb72e0d7066a"), (review / "raw_manifest.jsonl", "50eca11439736a669f263cf84b6cfe6ca27ddf6713336f0ead0d5f7f60dd72bc")]
for path, digest in expected:
    assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest
tests = json.loads((base / "selftest_final/selftest_results.json").read_text(encoding="utf-8"))
supplement = json.loads((base / "supplement_final_results.json").read_text(encoding="utf-8"))
target = json.loads((base / "target_final_results.json").read_text(encoding="utf-8"))
assert tests["status"] == supplement["status"] == target["status"] == "PASS"
guard_sha = hashlib.sha256((base / "guard.py").read_bytes()).hexdigest()
assert guard_sha == supplement["source_sha256"] == target["guard_sha256"]
identities = []
for path in base.rglob("samples.jsonl"):
    for line in path.read_text(encoding="utf-8").splitlines():
        identities.extend(json.loads(line)["members"])
for test in tests["cases"] + target["cases"]:
    identities.extend(test["identities"])
readback = []
for pid, birth in sorted({(x["pid"], x["create_time"]) for x in identities}):
    try:
        actual = psutil.Process(pid).create_time()
        status = "PID_REUSED_UNTOUCHED" if actual != birth else "STILL_PRESENT"
    except psutil.NoSuchProcess:
        status = "ABSENT"
    readback.append({"pid": pid, "expected_create_time": birth, "status": status})
assert all(x["status"] != "STILL_PRESENT" for x in readback)
with (base / "fixture_final_readback.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump({"status": "PASS", "processes": readback, "no_stop_called": True}, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
entries = []
for path in sorted(base.rglob("*")):
    if not path.is_file():
        continue
    assert path.suffix.lower() not in {".exe", ".obj", ".bit", ".dcp", ".pyc"}
    role = "source" if path.suffix == ".py" else "log" if path.suffix in {".log", ".jsonl"} else "result"
    entries.append({"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role})
for path in [plan] + [x[0] for x in expected]:
    entries.append({"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": "input"})
manifest = base / "raw_manifest.jsonl"
with manifest.open("x", encoding="utf-8", newline="\n") as stream:
    for row in sorted(entries, key=lambda x: x["path"]):
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
native = {name: json.loads((base / (name + ".native.json")).read_text(encoding="utf-8")) for name in ["base_selftest", "supplement_selftest", "target_selftest", "final_base_selftest", "final_supplement_selftest", "final_target_selftest"]}
assert all(x["native_exit_code"] == 0 for x in native.values())
receipt = {"schema_version": 1, "task": "S10-RG1-R2", "status": "PASS_TOOL_SELFTEST_ONLY_PENDING_INDEPENDENT_REVIEW", "developer_stop": "STOP_NO_ACTIVE_GUARD_OR_FIXTURE", "source_commit": "3f24c94564d10103aaa00db07356f666b085f687", "guard_sha256": guard_sha, "guard_path": str(base / "guard.py"), "actual_commands": native, "closed_findings": [{"id": "RG2-1", "fix": "NoSuch后全新候选PID/出生只读读回；确认缺失/复用原对象才记录HELPER_EXIT_CONFIRMED_CONTINUE。缺测样本RSS为null，继续下次采样；活候选父链未知仍BLOCKED。停止路径NoSuch同样读回候选，不假报已退出。", "evidence": "p1_final_race/monitor与p1_final_parent_nosuch/monitor"}, {"id": "RG2-2", "fix": "每轮持续保存已核(pid,birth)成员及完整身份；根缺失/复用时只读已知成员。活/未知孤儿retained，ROOT_EXITED_WITH_REMAINING/native3或BLOCKED，不追杀。全部已知缺失也不证明未采新生对象或完整树闭合。", "evidence": "p1_final_orphan/monitor；实际child活且retained/非0，清理由自测另外核身份完成。"}], "cases": [{k: x[k] for k in ("name", "pass", "native_exit_code")} for x in tests["cases"] + target["cases"]], "stop_and_output": supplement, "limits": {"interval_seconds": 1, "tree_rss_limit_bytes": 6442450944, "available_ram_stop_bytes": 536870912, "c_disk_free_stop_bytes": 8589934592}, "preserved_inputs": [{"path": str(path), "sha256": digest} for path, digest in expected], "old_r01_raw_lines": 191, "raw_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(), "raw_manifest_lines": len(entries), "usage_gate_NOT_RUN": ["ROOT必须确认守卫native PID身份及首个有效样本后才派发heavy", "MCP长wait期间ROOT每5秒并行读取guard进程与终态，不向同Tcl排入命令；异常终态立即notify并关闭后续派发", "ROOT按实际owned SID/进程读回处置；闭合必须消费guard记录并核所有owned身份无活残留", "此ROOT集成协议由ROOT执行，本工具开发自测未执行或批准集成/真实Vivado准入"], "limitations": ["1秒离散采样与短命helper峰值缺测；null不伪造零", "根终态只读已知成员，未采到的新生对象未知，不能凭ROOT_EXITED/native0认定整树闭合", "真实根先退出/child仍活已复现并非0；父NoSuch异常出口及旧枚举调度部分mock，实际候选/资源/停止真实", "PID复用用真实PID错误出生值模拟，未声称OS实际复用；OS无跨树原子身份/停止事务", "仅低RSS阈值fixture，不分配GiB或真实压低RAM/C盘；900秒日志观察未等待自测", "守卫异常BLOCKED/STOP_PARTIAL后不持续保护，ROOT必须执行使用前门禁及实时终态消费", "r01首轮native1及两P1/Reviewer CHANGES_REQUIRED原件保持SHA；r02不复制191历史原件", "未改正式源/STATE/Git/证据、旧S9预算；未启动Vivado/ROSS/硬件，不批准功能/STA/部署/109/1000/G3-G5", "子代理不提交；ROOT独审后消费"], "elapsed_seconds": {"final_base": tests["elapsed_seconds"], "final_supplement": supplement["elapsed_seconds"], "final_targeted": target["elapsed_seconds"]}, "peak_memory_bytes": None}
path = base / "tool_receipt.json"
with path.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": receipt["status"], "guard_sha256": guard_sha, "receipt_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "raw_manifest_sha256": receipt["raw_manifest_sha256"], "raw_manifest_lines": len(entries), "stop": receipt["developer_stop"]}, ensure_ascii=False))
