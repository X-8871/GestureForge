"""冻结本次工具候选与实际原件；不生成产品或硬件通过结论。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone, timedelta

base = Path(__file__).resolve().parent
root = base.parents[3]
sup = base.parent / "s11_guard_supervisor_20261012_r01"
old = base.parent / "s10_resource_guard_20261012_r02/guard.py"
old_sup = base.parent / "s10_guard_supervisor_20261012_r01/supervisor.py"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(old) == "be8d51ba18cf331458e1d747578f332c4e5cc4b72604a3fb6d09e15030abb4d4"
assert sha(old_sup) == "d8c6e2e53b4b3012a139a2ab33969d0c308dc2a42e49976cad205b02ba8b578c"
assert sha(base / "guard.py") == "9cad1ddf5f1b2d48b99c6d10451756536b25c4abf613f0af8b16e0ffd629f86c"
block = lambda b, name, end: b.split(("    def "+name+"(").encode(), 1)[1].split(("    def "+end+"(").encode(), 1)[0]
for name, end in (("stop_one", "progress"), ("root_terminal", "event"), ("limits", "validate"), ("validate", "get_root"), ("get_root", "verified_chain"), ("verified_chain", "collect")):
    assert block(old.read_bytes(), name, end) == block((base/"guard.py").read_bytes(), name, end)
expected = old_sup.read_bytes().replace(b's10_resource_guard_20261012_r02/guard.py', b's11_resource_guard_20261012_r01/guard.py').replace(sha(old).encode(), sha(base/"guard.py").encode())
assert expected == (sup/"supervisor.py").read_bytes()
for path in list(base.glob("*.py")) + list(sup.glob("*.py")):
    ast.parse(path.read_text(encoding="utf-8"))
patch = ""
for before, after in ((old,base/"guard.py"),(old_sup,sup/"supervisor.py")):
    patch += "".join(difflib.unified_diff(before.read_text(encoding="utf-8").splitlines(True), after.read_text(encoding="utf-8").splitlines(True), fromfile=str(before.relative_to(root)), tofile=str(after.relative_to(root))))
(base/"source_diff.patch").write_text(patch, encoding="utf-8", newline="\n")
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
commands = [read(base/(n+".native.json")) for n in ("lineage_r01","lineage_r02","lineage_r03","base_final","supplement_final")]
commands.append(read(sup/"native_receipt.json"))
assert all(x["native_exit_code"] == 0 for x in commands)
assert max(x.get("sampled_owned_test_tree_rss_peak_bytes",x.get("sampled_peak_tree_rss_bytes",0)) for x in commands) <= 128*1024*1024
latest = read(base/"lineage_tests_r03/result.json")
assert len(latest["cases"]) == 13 and all(x["pass"] for x in latest["cases"])
assert read(base/"selftest_final/selftest_results.json")["status"] == "PASS"
assert read(base/"supplement_final_results.json")["status"] == "PASS"
assert len(read(sup/"selftest_result.json")["cases"]) == 8
head = subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,check=False)
assert head.returncode == 0 and head.stdout.decode().strip() == "1eed350c43aae4cdee1f8179a93ce87d75d9f2a8"
inputs = [old,old_sup,base.parent/"s10_root_run_20261012_r01/resource_plan.json",
          base.parent/"s10_resource_guard_20261012_r02/selftest.py",base.parent/"s10_resource_guard_20261012_r02/fixture.py",
          base.parent/"s10_resource_guard_20261012_r02/supplement_selftest.py",
          base.parent/"s10_guard_supervisor_20261012_r01/selftest.py",base.parent/"s10_guard_supervisor_20261012_r01/fake_guard.py",
          base.parent/"s10_guard_supervisor_20261012_r01/native_test.py"]
receipt = {"schema_version":1,"task":"S11-RG-D1","status":"PASS_G1_TOOL_FIXTURES_ONLY","developer_stop":True,
    "at_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"source_commit":head.stdout.decode().strip(),
    "sources":{"guard.py":sha(base/"guard.py"),"supervisor.py":sha(sup/"supervisor.py"),"source_diff.patch":sha(base/"source_diff.patch")},
    "before_bindings":[{"path":str(p.relative_to(root)),"sha256":sha(p)} for p in inputs],
    "commands":commands,"seed":20261012,"new_cases":latest["cases"],"base_cases":5,"stop_request_and_output_refusal_cases":2,
    "supervisor_fixture_cases":8,"supervisor_body_only_fixed_path_and_sha_changed":True,"stop_one_raw_unchanged":True,
    "stop_one_block_sha256":hashlib.sha256(block((base/"guard.py").read_bytes(),"stop_one","progress")).hexdigest(),
    "tool_test_budget":{"original_bytes":80*1024*1024,"original_80MiB_met":False,"root_authorized_revised_bytes":128*1024*1024,"maximum_sampled_test_tree_rss_bytes":max(x.get("sampled_owned_test_tree_rss_peak_bytes",x.get("sampled_peak_tree_rss_bytes",0)) for x in commands)},
    "production_limits":{"new_run_tree_rss_limit_bytes":6442450944,"new_run_available_ram_stop_bytes":536870912,"minimum_c_disk_free_before_dispatch_bytes":8589934592,"resource_sample_interval_seconds":1},
    "limitations":["只候选工具G1，等待另一独立Reviewer；不批准真实运行预算、STA、硬件或任何产品关口。","前两轮功能native0但超过原80MiB工具夹具目标，原件保留；第三轮已在开始前派发，不因约10MiB差额继续重复。ROOT仅将本次工具测试预算调为128MiB。","样本树RSS是20/25ms离散读回，不是整机/连续绝对峰；OS当前子树枚举可能不包含已成为孤儿的夹具对象，guard样本另保留其历史已核真实RSS。","复用和字段变化、UNKNOWN是显式自有夹具注入；读取期间退出/helper退出/ROOT退出均为自有轻量进程自然退出。","所有夹具串行且清理逐项六字段核查；未探测/停止实际11112或其它窗口对象，未运行Vivado/硬件。","r01/r02较早睡眠夹具版本只作功能/资源异常留证；最终r03及适用回归绑定当前实际源码。","S10/S9旧BLOCKED及缺测不补PASS，不导入旧lineage或RSS，不改变正式阈值。","Python/Git Bash启动及apply_patch失败保留工具调用原返回，不把宿主码伪作未启动子程序native码。"],
    "raw_manifest_path":"raw_manifest.jsonl","git_written_or_committed":False}
with (base/"tool_receipt.json").open("x",encoding="utf-8",newline="\n") as stream:
    json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write("\n")
files = list(base.rglob("*")) + list(sup.rglob("*"))
rows = [{"path":str(p.relative_to(root)).replace("\\","/"),"sha256":sha(p),
         "role":"source" if p.suffix==".py" else "log" if p.suffix==".log" or p.name in {"events.jsonl","samples.jsonl","journal.jsonl"} else "diagnostic" if p.suffix==".patch" else "result"} for p in files if p.is_file() and p.name != "raw_manifest.jsonl"]
rows += [{"path":str(p.relative_to(root)).replace("\\","/"),"sha256":sha(p),"role":"input"} for p in inputs]
with (base/"raw_manifest.jsonl").open("x",encoding="utf-8",newline="\n") as stream:
    for row in sorted(rows,key=lambda x:x["path"]):
        stream.write(json.dumps(row,ensure_ascii=False)+"\n")
print(json.dumps({"developer_stop":True,"guard_sha256":sha(base/"guard.py"),"supervisor_sha256":sha(sup/"supervisor.py"),"tool_receipt_sha256":sha(base/"tool_receipt.json"),"raw_manifest_sha256":sha(base/"raw_manifest.jsonl"),"bindings":len(rows)},ensure_ascii=False))
