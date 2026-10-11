"""只注入自有假guard验证Popen和READY过滤；不运行固定生产guard。"""
import ast
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import supervisor as s

work=Path(__file__).resolve().parent
assert len((work/"supervisor.py").read_text(encoding="utf-8").splitlines())<=130
ast.parse((work/"supervisor.py").read_text(encoding="utf-8"))
assert s.sha(s.exact(str(s.GUARD)))==s.GUARD_SHA
binding=s.identity(__import__("os").getpid()); binding["ppid"]=__import__("psutil").Process().ppid()
bound=work/"fixture_binding.json"
with bound.open("x",encoding="utf-8") as f:json.dump(binding,f)
rows=[]
for name,expected_code,expected_ready in (("valid",0,True),("missing",7,False),("mismatch",9,False),("alert",2,False),("invalid",11,False),("empty",4,False),("identity_loss",6,False),("bad_terminal",8,True)):
    out=work/("fixture_"+name); command=[sys.executable,"-X","utf8","-B",str(work/"fake_guard.py"),"--binding",str(bound),"--output-dir",str(out/"guard"),"--case",name]
    capture=io.StringIO(); original=s.identity
    if name=="identity_loss":
        calls=[0]
        def changed(pid):
            calls[0]+=1; row=original(pid)
            if calls[0]>1:row["create_time"]+=1
            return row
        s.identity=changed
    try:
        with contextlib.redirect_stdout(capture): code=s.supervise(command,dict(binding,cwd=str(work)),out,[dict(path=str(work/"fake_guard.py"),sha256=s.sha(work/"fake_guard.py")),dict(path=str(bound),sha256=s.sha(bound))],interval=0.05)
    finally:s.identity=original
    with (out/"emitted.jsonl").open("x",encoding="utf-8") as f:f.write(capture.getvalue())
    emitted=[json.loads(x) for x in capture.getvalue().splitlines()]; receipt=json.loads((out/"supervisor_receipt.json").read_text(encoding="utf-8"))
    assert code==2 and receipt["child_native_exit_code"]==expected_code,(name,receipt)
    assert receipt["ready"]==expected_ready and sum(x["kind"]=="READY" for x in emitted)==int(expected_ready)
    assert emitted[-1]["kind"]=="TERMINAL"
    assert (out/"stdout.log").read_bytes()=="替身原始stdout\n".encode("utf-8")
    assert (out/"stderr.log").read_bytes()=="替身原始stderr\n".encode("utf-8")
    rows.append(dict(case=name,fixture=True,native_child_code=expected_code,supervisor_code=code,ready=expected_ready,receipt_sha256=s.sha(out/"supervisor_receipt.json")))
result=dict(status="PASS_FIXTURE_ONLY",cases=rows,production_guard_executed=False,real_target_sampled_or_stopped=False,limitations=["身份漂移是导入函数注入，不代表真实PID复用实验。","正常guard0使supervisor2，仅终态阻止派发，不把子码改成2。","ROOT/MCP每5秒消费集成未执行。"])
with (work/"selftest_result.json").open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write("\n")
print(json.dumps(dict(status=result["status"],cases=len(rows),production_guard_executed=False),ensure_ascii=False))
