"""保留初次封存并精确更正命令转录中的反斜杠，再绑定最终全量原件。"""
import hashlib
import json
from pathlib import Path

W = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old_path = W / "native_command_clarification.json"
old = json.loads(old_path.read_text(encoding="utf-8"))
native = json.loads((W / "r04_native_receipt_r02.json").read_text(encoding="utf-8"))
executable = native["executions"][0]["command"][0]
corrected = dict(old)
corrected["actual_outer_commands_from_tool_invocations"] = [[executable, "-B", "-X", "utf8", str(W/name)] for name in ("r04_run.py", "r04_run_r02.py")]
corrected["corrects_prior_clarification_sha256"] = sha(old_path)
corrected["literal_correction"] = dict(previous=old["actual_outer_commands_from_tool_invocations"][0][0], actual=executable,
                                        reason="第一次转录Python解释器字符串多转义反斜杠；本次复用executions中sys.executable真实返回值，不重新拼写路径。原命令执行不受影响，原件保留。")
with (W / "native_command_clarification_r02.json").open("x", encoding="utf-8") as f:
    json.dump(corrected,f,ensure_ascii=False,indent=2)
prior = W / "tool_receipt_r04.json"
receipt = json.loads(prior.read_text(encoding="utf-8"))
receipt["prior_receipt_sha256"] = sha(prior)
receipt["native_command_clarification_sha256"] = sha(W / "native_command_clarification_r02.json")
receipt["native_command_clarification_path"] = "native_command_clarification_r02.json"
receipt["limitations"].append("初次外层命令flags澄清中的解释器字符串多转义反斜杠；独立r02澄清复用原生子命令真实sys.executable，未改旧元数据或执行原件。最终消费tool_receipt_r04_r02.json。")
with (W / "tool_receipt_r04_r02.json").open("x", encoding="utf-8") as f:
    json.dump(receipt,f,ensure_ascii=False,indent=2)
files = sorted(p for p in W.rglob("*") if p.is_file())
size = sum(p.stat().st_size for p in files)
assert size <= 32*1024**2
rows = [dict(path=p.relative_to(W).as_posix(), bytes=p.stat().st_size, sha256=sha(p)) for p in files]
with (W / "raw_manifest_r04_r02.jsonl").open("x", encoding="utf-8", newline="\n") as f:
    for row in rows:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
for row in rows:
    assert sha(W / row["path"]) == row["sha256"]
print(json.dumps(dict(status="PASS_G1_ONLY_STOP", guard_sha256=receipt["guard_sha256"], supervisor_sha256=receipt["supervisor_sha256"],
                     receipt_path=str(W / "tool_receipt_r04_r02.json"), receipt_sha256=sha(W / "tool_receipt_r04_r02.json"),
                     raw_path=str(W / "raw_manifest_r04_r02.jsonl"), raw_sha256=sha(W / "raw_manifest_r04_r02.jsonl"),
                     raw_files=len(rows), indexed_bytes=size),ensure_ascii=False))
