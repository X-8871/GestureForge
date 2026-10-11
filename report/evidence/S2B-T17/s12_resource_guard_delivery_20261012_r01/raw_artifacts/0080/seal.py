"""冻结r04出生门禁与supervisor pin的源码、真实轻量结果及失败原件。"""
import hashlib
import json
from pathlib import Path

W = Path(__file__).resolve().parent
ROOT = W.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sources = {
 "tmp/2B/S2B-T17/s12_resource_guard_20261012_r01/guard.py": "17d0d101b1946d2c47a48ce2e9050dea8822c5983b1c497c4ce5e799e159ec78",
 "tmp/2B/S2B-T17/s12_resource_guard_20261012_r01/tool_receipt.json": "7288e4d49315b2fd23503d55727eb33fa40f58734f77a48a43f9e9ed5154860a",
 "tmp/2B/S2B-T17/s12_resource_guard_20261012_r01/raw_manifest_final.jsonl": "4c6e4e49556fb66302e5a34cc21ab6d5091c80c9349fa9289046c7b19a21e46a",
 "tmp/2B/S2B-T17/s11_guard_supervisor_20261012_r02/supervisor.py": "bbe74e023603ee686a746b92d7dc5c2cb8066b3554eb5e65176bb1f6af88b9f9",
 "tmp/2B/S2B-T17/independent_s12_resource_guard_first_observation_review_20261012_r01/final_review_receipt.json": "a51b043c65acfebb5790e72e2438cddb59ca6752dfb190caff17d481ffb22ec2",
 "tmp/2B/S2B-T17/independent_s12_resource_guard_first_observation_review_20261012_r01/raw_manifest_r02.jsonl": "333dcf5bea6b21ab55070966fc540151ea9ced929a8f566439250dd1605b2ced",
}
for path, expected in sources.items():
    assert sha(ROOT / path) == expected, path
guard_sha = sha(W / "guard.py")
sup_sha = sha(W / "supervisor.py")
assert guard_sha == "a2f5c581b79a40116bf59c240a7b8c0fe35bac4db7b26a79ce5ba14c451a18ac"
assert sup_sha == "193416f869463c38065e257545720032438ab12c7bbe30beec6bc8c53d8f9ca0"
read = lambda name: json.loads((W / name).read_text(encoding="utf-8"))
failed, passed = read("r04_native_receipt.json"), read("r04_native_receipt_r02.json")
regression, supplement = read("selftest_result.json"), read("supplement_result.json")
birth, pin = read("birth_test_result.json"), read("supervisor_pin/test_result.json")
assert failed["native_exit_code"] == 1 and len(failed["executions"]) == 1
assert passed["native_exit_code"] == 0 and len(passed["executions"]) == 4
assert all(x["native_exit_code"] == 0 for x in passed["executions"])
assert regression["status"] == supplement["status"] == "PASS_G1_ONLY"
assert birth["status"] == "PASS_BIRTH_GATE_G1_ONLY" and pin["status"] == "PASS_SUPERVISOR_PIN_G1_ONLY"
assert regression["guard_sha256"] == supplement["guard_sha256"] == birth["guard_sha256"] == pin["pinned_guard_sha256"] == guard_sha
assert pin["supervisor_sha256"] == sup_sha
actual = next(x for x in pin["cases"] if x["case"] == "actual_owned_standin_5s_live_ready_terminal")
assert actual["live_samples"] >= 3 and actual["elapsed_seconds"] >= 10
assert actual["supervisor_return_code"] == 2 and actual["child_native_exit_code"] == 7
clarification = dict(schema_version=1, affected_receipts=[dict(path=name,sha256=sha(W/name)) for name in ("r04_native_receipt.json", "r04_native_receipt_r02.json")],
                    issue="outer command字段来自sys.argv，未包含解释器-B/-X utf8；各executions子命令已完整记录。原件不改写。",
                    actual_outer_commands_from_tool_invocations=[["C:\\Users\\22061\\AppData\\Local\\Programs\\Python\\Python312\\python.exe", "-B", "-X", "utf8", str(W/name)] for name in ("r04_run.py", "r04_run_r02.py")],
                    actual_outer_exit_codes=[1,0], evidence_source="本会话exec_command实际调用参数及返回，非执行时sys.orig_argv采集",
                    child_native_codes_preserved=True)
with (W / "native_command_clarification.json").open("x", encoding="utf-8") as f:
    json.dump(clarification,f,ensure_ascii=False,indent=2)
receipt = dict(schema_version=1, task_id="S2B-T17", version="S12_guard_r04_and_supervisor_pin", status="PASS_G1_ONLY",
               developer_stop="STOP_NO_FURTHER_WRITES", source_commit_at_initial="932051cdacdf02f729d6a7554b07118d05e96aa4",
               source_bindings=sources, guard_sha256=guard_sha, supervisor_sha256=sup_sha,
               guard_diff_r03_sha256=sha(W / "source_diff_r03.patch"), supervisor_diff_sha256=sha(W / "supervisor_pin/source_diff.patch"),
               added_guard_lines=2, supervisor_changed_lines=2,
               guard_regression_mock_tests=regression["mock_tests"], guard_supplement_mock_tests=supplement["tests"],
               guard_real_owned_canaries=regression["actual_canaries"], birth_counterexample_window_tests=birth["tests"], supervisor_checks=pin["tests"],
               total_successful_expectation_cases=regression["mock_tests"]+regression["actual_canaries"]+supplement["tests"]+birth["tests"]+pin["tests"],
               old_r03_counterexample_reproduced=birth["original_r03_reproduced"], removed_birth_gate_mutant_reproduced=birth["removed_gate_mutant_reproduced"],
               mutant_sha256=birth["mutant_sha256"], first_failure_native_exit_code=failed["native_exit_code"], successful_native_receipt=passed,
               failure_explanation="新出生时间门禁提前正确拒绝；旧测试只匹配祖先链身份变化导致1项断言失败。保存failed_selftest_r01.py及原日志；新独立r02运行只扩展正确拒绝原因匹配。",
               actual_supervision=actual, native_command_clarification_sha256=sha(W / "native_command_clarification.json"),
               monitoring_declaration="规定节拍离散监测执行通过", continuous_absolute_tree_peak_bytes=None, short_lived_unobserved_objects="UNKNOWN",
               thresholds=dict(sample_interval_seconds=1, owned_tree_rss_bytes=6*1024**3, available_ram_bytes=512*1024**2,
                               c_disk_free_bytes=8*1024**3, logs_no_change_seconds=900, external_supervision_seconds=5),
               old_s11_budget_pass=False, old_r03_originals_unchanged=True, git_commit_performed=False,
               limitations=["仅本次G1；ROOT独立复审前不可用于Vivado重型任务，原r03 PASS被首次观测CR限定，旧原件不改写。",
                            "新guard比r03仅增加candidate→ROOT逐边parent.birth<=child.birth门禁；保存parent、首次known_lineage及stop_one机制保留。根以上launcher不纳入年龄检查。",
                            "旧r03和删出生门禁mutant的错误授权被实际mock复现，期望反例不是候选通过或真实OS复用证明。",
                            "真实轻量父子阈值canary只停自有对象；同目录无关自有兄弟保持活，随后按保存birth正常清理。",
                            "真实supervisor替身仅经import注入；生产CLI只固定新guard及SHA且拒fixture；监督器从不终止对象。实际root后续身份由固定guard负责，本替身不证明heavy集成。",
                            "supervisor初次root样本漂移/guard初次及READY后身份漂移均failclosed；真实5秒LIVE和READY→TERMINAL(code2/child7)只属于轻量替身。",
                            "上一轮r01中断时只创建sup测试源码，从未启动canary；r01原件保持不动。",
                            "离散live集合RSS非原子；连续绝对峰及未曾采到短命对象未知；不继承旧S11预算PASS。",
                            "真实native命令及原字节保留；外层sys.argv漏解释器flags已单独澄清且未覆盖原件。工具调用总量未完整计数。",
                            "未运行UART/JTAG/hw_server/板卡探测/ROSS/Vivado重型任务；未修改生产、Git或正式证据。复制保留的native_run/supplement_native/supervisor_pin.native_run为未执行备选包装，实际入口为r04_run及r04_run_r02。"])
with (W / "tool_receipt_r04.json").open("x", encoding="utf-8", newline="\n") as f:
    json.dump(receipt,f,ensure_ascii=False,indent=2)
files = sorted(p for p in W.rglob("*") if p.is_file())
size = sum(p.stat().st_size for p in files)
assert size <= 32*1024**2
rows = [dict(path=p.relative_to(W).as_posix(), bytes=p.stat().st_size, sha256=sha(p)) for p in files]
with (W / "raw_manifest_r04.jsonl").open("x", encoding="utf-8", newline="\n") as f:
    for row in rows:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
for row in rows:
    assert sha(W / row["path"]) == row["sha256"]
print(json.dumps(dict(status="PASS_G1_ONLY_STOP", guard_sha256=guard_sha, supervisor_sha256=sup_sha,
                     cases=receipt["total_successful_expectation_cases"], tool_receipt_sha256=sha(W / "tool_receipt_r04.json"),
                     raw_manifest_sha256=sha(W / "raw_manifest_r04.jsonl"), raw_files=len(rows), indexed_bytes=size,
                     actual_supervision=actual),ensure_ascii=False))
