"""仅修复私有实例状态枚举夹具；生成r03且不运行RTL工具。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OLD=HERE/"cones_input_r02";NEW=HERE/"cones_input_r03"
assert OLD.is_dir() and not NEW.exists();NEW.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
upstream=json.loads((OLD/"prepared_receipt.json").read_text(encoding="utf-8"))
for item in upstream["files"]:assert sha(Path(item["path"]))==item["sha256"]
source=(ROOT/"src/s2b_conv_tile_engine.sv").read_text(encoding="utf-8")
enum=re.search(r"typedef enum logic \[4:0\] \{(.*?)\} state_t;",source,re.S)
assert enum and re.search(r"\bstate_t state;",source)
names=re.findall(r"\bST_\w+\b",enum[1]);values={name:i for i,name in enumerate(names)}
states=["ST_IDLE","ST_COMPUTE_PREP","ST_COMPUTE_POINT_PREP","ST_COMPUTE","ST_WEIGHT_SCAN"]
assert [values[s] for s in states]==[0,11,12,13,7]
compile_path=ROOT/"report/evidence/S2B-T17/s12_conv_cones_20261012_r02/compile.log"
diagnostic=compile_path.read_text(encoding="utf-8")
locations=re.findall(r"%Error-ENUMVALUE: tb_s12_conv_cones\.sv:(\d+):(\d+):",diagnostic)
assert locations==[("1982",str(c)) for c in (42,78,122,172,217)]
old_tb=(OLD/"tb_s12_conv_cones.sv").read_text(encoding="utf-8")
original=next(line for line in old_tb.splitlines() if line.startswith("case(v_state)0:u_private.state="))
assert all(original.count("u_private.state=u_private."+name+";")==1 for name in states)
lines=["// 目标为生产声明的state_t state；只改变TB枚举转换，不改变选择值。", "case(v_state)"]
for i,name in enumerate(states):
    label=str(i) if i<4 else "default"
    lines.extend([label+": begin",f'  if (!$cast(u_private.state,u_private.{name})) $fatal(1,"私有state_t转换失败：{name}");',f'  if (($bits(u_private.state)!=5) || (int\'(u_private.{name})!={values[name]}) || (int\'(u_private.state)!==int\'(u_private.{name}))) $fatal(1,"私有状态原值/转换值不一致：{name}");',"end"])
lines.append("endcase")
new_tb=old_tb.replace(original,"\n".join(lines));assert new_tb.count("$cast(u_private.state,")==5
assert all("u_private.state=u_private."+name not in new_tb for name in states)
(NEW/"tb_s12_conv_cones.sv").write_text(new_tb,encoding="utf-8",newline="\n")
for name in ("s2b_conv_tile_engine_original.sv","s2b_conv_tile_engine.sv","s2b_conv_tile_engine_next_mutant.sv"):
    shutil.copyfile(OLD/name,NEW/name);assert sha(NEW/name)==sha(OLD/name)
drivers=[]
for line_no,line in enumerate(new_tb.splitlines(),1):
    for inst in ("u_old","u_generic","u_private","u_next_mutant"):
        assignments=re.findall(re.escape(inst)+r"\.(\w+)(?:\[[^]]+\])?\s*=",line)
        casts=re.findall(r"\$cast\("+re.escape(inst)+r"\.(\w+)\s*,",line)
        drivers.extend({"instance":inst,"signal":signal,"tb_line":line_no,"reason":"受控组合域；clk恒0，完整引擎FF不执行；显式枚举cast失败fatal"} for signal in sorted(set(assignments+casts)))
assert len(drivers)==152
old_keys={(d["instance"],d["signal"]) for d in upstream["controlled_drivers"]}
assert {(d["instance"],d["signal"]) for d in drivers}==old_keys
state_scan=[]
for inst,filename in (("u_old","s2b_conv_tile_engine_original.sv"),("u_generic","s2b_conv_tile_engine.sv"),("u_private","s2b_conv_tile_engine.sv"),("u_next_mutant","s2b_conv_tile_engine_next_mutant.sv")):
    available=set(re.findall(r"\bST_\w+\b",re.search(r"typedef enum logic[^;]+?\} state_t;",(NEW/filename).read_text(encoding="utf-8"),re.S)[0]))
    referenced=set(re.findall(re.escape(inst)+r"\.(ST_\w+)",new_tb));assert referenced<=available
    state_scan.append({"instance":inst,"source":filename,"referenced":sorted(referenced)})
files=[{"path":str(p),"sha256":sha(p),"role":"source"} for p in sorted(NEW.glob("*.sv"))]
files.append(next(item for item in upstream["files"] if Path(item["path"]).name=="vectors.dat"))
receipt=dict(upstream);receipt["files"]=files;receipt["controlled_drivers"]=drivers
receipt["fixture_revision"]={"status":"FIXED_TESTBENCH_ONLY_NOT_RUN","upstream_sha256":sha(OLD/"prepared_receipt.json"),"old_bench_sha256":sha(OLD/"tb_s12_conv_cones.sv"),"new_bench_sha256":sha(NEW/"tb_s12_conv_cones.sv"),"old_compile_sha256":sha(compile_path),"old_compile_native":1,"old_runner_native":2,"old_wrapper_native":1,"locations":locations,"target_declaration":"typedef enum logic [4:0] {...} state_t; state_t state;","enum_values":{s:values[s] for s in states},"state_scan":state_scan,"driver_rows_before":len(upstream["controlled_drivers"]),"driver_rows_after":len(drivers),"limits":"五个private状态赋值改checked cast并比较原值/转换值；向量/oracle/五mutants/完整引擎源码不变。尚未lint/编译/仿真。"}
(NEW/"prepared_receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(NEW/"fixture.patch").write_text("".join(difflib.unified_diff(old_tb.splitlines(True),new_tb.splitlines(True),fromfile="r02/tb_s12_conv_cones.sv",tofile="r03/tb_s12_conv_cones.sv")),encoding="utf-8",newline="\n")
runner=(HERE/"cones_run_r02.py").read_text(encoding="utf-8").replace('prepared=HERE/"cones_input_r02"','prepared=HERE/"cones_input_r03"')
start=runner.index('    log=(evidence/"compile.log")');end=runner.index('    simulation=',start)
body=runner[start:end].replace('    log=(evidence/"compile.log").read_text(encoding="utf-8")','    log=(evidence/(stage+".log")).read_text(encoding="utf-8")')
body=body.replace('    report["controlled_multidriven_diagnostics"]=controlled','    report.setdefault("controlled_multidriven_diagnostics",{})[stage]=controlled')
helper='    def check_diagnostics(stage):\n'+"\n".join('    '+line for line in body.rstrip().splitlines())+'\n'
replacement=helper+'    lint_command=["--lint-only" if item=="--binary" else item for item in command]\n    support.execute("lint",lint_command,work,evidence,env,report,600)\n    check_diagnostics("lint")\n    support.execute("compile",command,work,evidence,env,report,600)\n    check_diagnostics("compile")\n'
compile_start=runner.rindex('    support.execute("compile",command,work,evidence,env,report,600)',0,start)
runner=runner[:compile_start]+replacement+runner[end:]
assert '-Wno-ENUMVALUE' not in runner and runner.count('support.execute("lint"')==1
(HERE/"cones_run_r03.py").write_text(runner,encoding="utf-8",newline="\n")
supervisor=(HERE/"cones_supervisor_r02.py").read_text(encoding="utf-8").replace('"cones_run_r02.py"','"cones_run_r03.py"').replace('"cones_input_r02/prepared_receipt.json"','"cones_input_r03/prepared_receipt.json"')
(HERE/"cones_supervisor_r03.py").write_text(supervisor,encoding="utf-8",newline="\n")
commands=[]
for name in ("repair_cones_r03.py","cones_run_r03.py","cones_supervisor_r03.py"):
    ast.parse((HERE/name).read_text(encoding="utf-8"))
    if name.startswith("repair_"):continue
    command=[sys.executable,"-X","utf8","-B",str(HERE/name),"--help"]
    result=subprocess.run(command,cwd=HERE,capture_output=True,timeout=30);assert result.returncode==0
    (NEW/(name+".help.stdout.log")).write_bytes(result.stdout);(NEW/(name+".help.stderr.log")).write_bytes(result.stderr)
    commands.append({"command":subprocess.list2cmdline(command),"exit_code":result.returncode})
ready={"status":"PREPARED_NOT_RUN","actual_cli_help":commands,"files":[{"path":str(p),"sha256":sha(p),"role":"source"} for p in (HERE/"repair_cones_r03.py",HERE/"cones_run_r03.py",HERE/"cones_supervisor_r03.py",NEW/"prepared_receipt.json",NEW/"fixture.patch")],"limitations":"没有执行lint/编译/仿真；无RTL功能或击杀结论。首RTL按lint→compile→simulation串行，任何失败立即停止。"}
(NEW/"ready_receipt.json").write_text(json.dumps(ready,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":ready["status"],"vectors":receipt["vectors"],"driver_rows":len(drivers),"runner_sha256":sha(HERE/"cones_run_r03.py"),"prepared_sha256":sha(NEW/"prepared_receipt.json"),"ready_sha256":sha(NEW/"ready_receipt.json")},ensure_ascii=False))
