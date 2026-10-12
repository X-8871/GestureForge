"""隔离接口反例与原生包装证明；不执行生产source或Vivado。"""
import ast
import copy
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
import collector as c
import compat_pins as p

ROOT=c.ROOT
OWN=c.WORK
OLD=p.WORK

def digest(path):
    """读取实际原字节SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command,name):
    """保存直接子进程身份及实际等待返回码和原生流。"""
    started=time.monotonic()
    with (OWN/(name+".stdout.bin")).open("xb") as out,(OWN/(name+".stderr.bin")).open("xb") as err:
        child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err)
        try: birth=psutil.Process(child.pid).create_time()
        except psutil.Error: birth="UNKNOWN"
        code=child.wait(timeout=30)
    return dict(command=command,pid=child.pid,create_time_unix=birth,native_exit_code=code,direct_wait_exit_code=code,elapsed_seconds=time.monotonic()-started,stdout=c.binding(OWN/(name+".stdout.bin")),stderr=c.binding(OWN/(name+".stderr.bin")))

def function_map(path):
    """AST仅比较函数，区别允许修改的顶层绑定。"""
    return {node.name:ast.dump(node,include_attributes=False) for node in ast.parse(path.read_text(encoding="utf-8")).body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}

def main():
    """真实原件只读；反例使用明确标注的独立内存fixture。"""
    p.require_ready()
    freeze=c.read(c.FREEZE)
    before_sources={row["path"]:digest(c.exact(ROOT/row["path"])) for row in freeze["source_files"]}
    assert len(before_sources)==43 and before_sources=={r["path"]:r["sha256"] for r in freeze["source_files"]}
    old_tools={name:digest(OLD/name) for name in ("collector.py","native.py","compat_pins.py","source_freeze.json","prepared_receipt.json","source_before.native.json")}
    initial_git=run(["git","-c","core.longpaths=true","-c","maintenance.auto=false","status","--short"],"git_before")
    head=run(["git","-c","core.longpaths=true","-c","maintenance.auto=false","rev-parse","HEAD"],"head")
    assert (OWN/"head.stdout.bin").read_text(encoding="utf-8").strip()==p.SOURCE_COMMIT
    call=c.read(ROOT/"tmp/2B/S2B-T17/s12_physical_launch_root_20261012_r01/wait.tool.json")
    item=dict(command="wait_on_run synth_1",code=0,output="FIXTURE_ONLY_NOT_NATIVE_HISTORY")
    accepted=c.wait_client_handoff(call,item,"wait")
    cases=[]
    def reject(name,mutate,label="wait"):
        """所有终态fixture只用于纯接口拒绝断言。"""
        fixture=copy.deepcopy(call); terminal=copy.deepcopy(item)
        payload=c.mcp_json(fixture); mutate(fixture,payload,terminal)
        fixture["result"]["content"][0]["text"]=json.dumps(payload,ensure_ascii=False)
        try: c.wait_client_handoff(fixture,terminal,label)
        except (ValueError,KeyError,TypeError) as error: cases.append(dict(name=name,status="REJECTED",reason=str(error))); return
        raise AssertionError("反例未拒绝："+name)
    for label in c.LABELS:
        if label!="wait": reject("非WAIT running："+label,lambda f,x,h:None,label)
    for label in c.LABELS:
        if label!="wait": reject("非WAIT error："+label,lambda f,x,h:f["result"].update(isError=True),label)
    reject("running非字符串true",lambda f,x,h:x.update(status=True))
    reject("running缺失",lambda f,x,h:x.pop("status"))
    reject("running不是终态",lambda f,x,h:x.update(status="completed"))
    reject("客户端session不同",lambda f,x,h:x.update(session_id="fixture_other"))
    reject("客户端session缺失",lambda f,x,h:x.pop("session_id"))
    reject("input session不同",lambda f,x,h:f["input"].update(session_id="fixture_other"))
    reject("input缺失",lambda f,x,h:f.pop("input"))
    reject("client command不同",lambda f,x,h:x.update(command="close_project"))
    reject("input command不同",lambda f,x,h:f["input"].update(command="close_project"))
    reject("history command不同",lambda f,x,h:h.update(command="close_project"))
    reject("history未完成",lambda f,x,h:h.update(code=None))
    reject("history失败",lambda f,x,h:h.update(code=1))
    reject("history bool假0",lambda f,x,h:h.update(code=False))
    reject("history缺码",lambda f,x,h:h.pop("code"))
    reject("client带码",lambda f,x,h:x.update(exit_code=0))
    reject("错误不能移交",lambda f,x,h:f["result"].update(isError=True))
    original={name:function_map(OLD/name) for name in ("collector.py","compat_pins.py")}
    new={name:function_map(OWN/name) for name in original}
    changed={name:[key for key in original[name] if original[name][key]!=new[name].get(key)] for name in original}
    added=[key for key in new["collector.py"] if key not in original["collector.py"]]
    assert changed=={"collector.py":["collect","seal"],"compat_pins.py":[]} and added==["wait_client_handoff","prepared_source_before"]
    assert digest(OWN/"native.py")==old_tools["native.py"]
    assert p.WORK==OLD and c.WORK==OWN and c.CACHE==OLD/"synth_cache" and c.PROJECT==OLD/"project" and c.PRE==p.SOURCE_PRE
    before_path,before_native=c.prepared_source_before(p.SOURCE_COMMIT)
    commands=[run([sys.executable,"-X","utf8","-B",str(OWN/name),"--help"],name.replace(".py","")+"_help") for name in ("collector.py","native.py")]
    assert all(r["native_exit_code"]==0 for r in commands)
    cache=OWN/"isolated_native_cache"; assert not cache.exists(); cache.mkdir()
    code="import sys,runpy;from pathlib import Path;sys.path.insert(0,"+repr(str(OWN))+");import collector;collector.CACHE=Path("+repr(str(cache))+");sys.argv=['native.py','--prefix','s12_handoff_g1_rejected','--','source','--commit','"+"0"*40+"','--phase','after'];runpy.run_path("+repr(str(OWN/"native.py"))+",run_name='__main__')"
    wrapper=run([sys.executable,"-X","utf8","-B","-c",code],"native_isolated_rejection")
    actual=c.read(cache/"s12_handoff_g1_rejected.native.json")
    assert wrapper["native_exit_code"]==actual["native_exit_code"]==1 and actual["command"][4]==str(OWN/"collector.py")
    assert "SOURCE_COMMIT" in (cache/"s12_handoff_g1_rejected.stderr.log").read_text(encoding="utf-8")
    after_sources={row["path"]:digest(c.exact(ROOT/row["path"])) for row in freeze["source_files"]}
    final_git=run(["git","-c","core.longpaths=true","-c","maintenance.auto=false","status","--short"],"git_after")
    assert initial_git["native_exit_code"]==final_git["native_exit_code"]==head["native_exit_code"]==0
    assert (OWN/"git_before.stdout.bin").read_bytes()==(OWN/"git_after.stdout.bin").read_bytes()
    assert before_sources==after_sources and old_tools=={name:digest(OLD/name) for name in old_tools}
    result=dict(status="PASS_G1_HANDOFF_INTERFACE_ONLY_STOP",created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),source_commit=p.SOURCE_COMMIT,actual_wait_original=c.binding(ROOT/"tmp/2B/S2B-T17/s12_physical_launch_root_20261012_r01/wait.tool.json"),positive_fixture=dict(native_history=item,accepted=accepted,client_exit_code=None,client_timeout=False),negative_cases=cases,ast_changed_functions=changed,ast_added_functions=added,native_bytes_unchanged=True,old_tools_unchanged=old_tools,source43_unchanged=after_sources,source_before_original=c.binding(before_path),commands=[initial_git,head,*commands,wrapper,final_git],new_tools=[c.binding(OWN/name) for name in ("collector.py","native.py","compat_pins.py")],limitations=["纯接口正例history code0为明确fixture，不是实际native history；尚未运行collect/seal。","真实包装隔离到自有cache，拒绝badcommit返回1证明调用新collector；未执行source-after/prepare/source-before。","原products监测GAP保留，接口G1不代表STA、资源连续监测、G2或G3通过。"])
    c.save(OWN/"g1_receipt.json",result)
    print(json.dumps(dict(status=result["status"],negative_cases=len(cases),receipt=c.binding(OWN/"g1_receipt.json")),ensure_ascii=False))

if __name__=="__main__":
    main()
