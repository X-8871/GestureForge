"""ROOT单槽准入后执行已冻结组合miter；不自动运行其他任务。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/"verification"))
import test_s2b_backend_coordinates_rtl as support

parser=argparse.ArgumentParser()
parser.add_argument("--run-id",required=True)
parser.add_argument("--toolchain",type=Path,required=True)
args=parser.parse_args()
assert re.fullmatch(r"s12_conv_cones_20261012_r\d+",args.run_id)
work=ROOT/"tmp/2B/S2B-T17"/args.run_id
evidence=ROOT/"report/evidence/S2B-T17"/args.run_id
assert work.parent.is_dir() and evidence.parent.is_dir() and not work.exists() and not evidence.exists()
assert args.toolchain.is_dir()
prepared=HERE/"cones_input_r03_ready"
receipt=json.loads((prepared/"prepared_receipt.json").read_text(encoding="utf-8"))
inputs={Path(item["path"]).name:Path(item["path"]) for item in receipt["files"]}
assert receipt["status"]=="PREPARED_NOT_RUN"
for item in receipt["files"]:assert support.sha(Path(item["path"]))==item["sha256"]
assert subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==receipt["source_commit"]
assert support.sha(ROOT/"src/s2b_conv_tile_engine.sv")==receipt["candidate_raw_sha256"]
checker=support.load_checker();checker.check_static(ROOT)
freeze=json.loads((ROOT/"tmp/2B/S2B-T17/s12_combined_prepare_20261012_r01/source_freeze_prepare.json").read_text(encoding="utf-8"))
bindings={item["path"]:support.sha(ROOT/item["path"]) for item in freeze["source_files"]}
work.mkdir();evidence.mkdir()
report={"status":"FAIL","task_id":"S2B-T17-S12","source_commit":receipt["source_commit"],"run_id":args.run_id,"runs":[],"prepared_input":receipt,"prepared_receipt_sha256":support.sha(prepared/"prepared_receipt.json"),"source_sha256_pre":bindings,"script_sha256":support.sha(Path(__file__)),"g2":"NOT_RUN","sta":"NOT_RUN","g3":"NOT_RUN"}
begin=time.monotonic()
try:
    source=work/"source";source.mkdir()
    snapshot=evidence/"source_snapshot";snapshot.mkdir()
    for path in bindings:
        target=snapshot/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,target)
    for name in ("s2b_conv_tile_engine_original.sv","s2b_conv_tile_engine.sv","s2b_conv_tile_engine_next_mutant.sv"):
        shutil.copyfile(inputs[name],source/name)
        shutil.copyfile(inputs[name],evidence/name)
    shutil.copyfile(ROOT/"src/s2a_network_descriptor_pkg.sv",source/"s2a_network_descriptor_pkg.sv")
    for name in ("tb_s12_conv_cones.sv","vectors.dat"):
        shutil.copyfile(inputs[name],evidence/name)
    shutil.copyfile(inputs["tb_s12_conv_cones.sv"],work/"tb_s12_conv_cones.sv")
    shutil.copyfile(prepared/"prepared_receipt.json",evidence/"prepared_receipt.json")
    shutil.copyfile(prepared/"fixture.patch",evidence/"fixture.patch")
    shutil.copyfile(Path(__file__),evidence/"cones_run.py")
    shutil.copyfile(HERE/"cones_prepare.py",evidence/"cones_prepare.py")
    tools=args.toolchain/"mingw64/bin";make=args.toolchain/"usr/bin"
    verilator=checker.exact_file(tools/"verilator_bin.exe")
    env=os.environ.copy();env["PATH"]=str(make)+os.pathsep+str(tools)+os.pathsep+env.get("PATH","")
    env["VERILATOR_ROOT"]=str(args.toolchain/"mingw64/share/verilator");env["PYTHONUTF8"]="1"
    report["tool_versions"]={"python":sys.version,"verilator":subprocess.check_output([str(verilator),"--version"],env=env,cwd=work,text=True,timeout=30).strip()}
    command=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","--top-module","tb_s12_conv_cones","--Mdir","obj_dir","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1",*["source/"+name for name in ("s2a_network_descriptor_pkg.sv","s2b_conv_tile_engine_original.sv","s2b_conv_tile_engine.sv","s2b_conv_tile_engine_next_mutant.sv")],"tb_s12_conv_cones.sv"]
    def check_diagnostics(stage):
        log=(evidence/(stage+".log")).read_text(encoding="utf-8")
        blocks=re.findall(r"%Warning-[\s\S]*?(?=%Warning-|make(?:\[|:)|\Z)",log)
        controlled=[]
        drivers=receipt["controlled_drivers"]
        for block in blocks:
            if re.match(r"%Warning-(?:LATCH|UNOPTFLAT)\b",block):raise ValueError("禁止的生产/bench组合诊断："+block)
            if not block.startswith("%Warning-MULTIDRIVEN"):continue
            # 仅允许明示TB层级驱动的实际寄存器；必须出现该TB的精确驱动行。
            tb_lines=[int(n) for n in re.findall(r"tb_s12_conv_cones\.sv:(\d+)",block)]
            matches=[d for d in drivers if d["tb_line"] in tb_lines and re.search(r"\b"+re.escape(d["signal"])+r"\b",block)]
            if not matches:raise ValueError("未登记MULTIDRIVEN，不能全局豁免："+block)
            controlled.append({"raw":block,"tb_drivers":matches,"scope":"仅clk恒0组合域TB主动驱动；公共boundary/layer0无强制内部信号。"})
        report.setdefault("controlled_multidriven_diagnostics",{})[stage]=controlled
        report["new_production_forbidden_diagnostics"]=[]
    lint_command=["--lint-only" if item=="--binary" else item for item in command]
    support.execute("lint",lint_command,work,evidence,env,report,600)
    check_diagnostics("lint")
    support.execute("compile",command,work,evidence,env,report,600)
    check_diagnostics("compile")
    simulation=[str(work/"obj_dir/Vtb_s12_conv_cones.exe"),"+VECTOR_PATH="+str(evidence/"vectors.dat")]
    support.execute("simulation",simulation,work,evidence,env,report,600)
    simulation_log=(evidence/"simulation.log").read_text(encoding="utf-8")
    found=re.findall(r"PASS S12_CONV_CONES vectors=(\d+) alias=(\d+) tile=(\d+) full=(\d+) extent=(\d+) next=(\d+)",simulation_log)
    assert len(found)==1 and int(found[0][0])==receipt["vectors"] and all(int(x)>0 for x in found[0][1:])
    report["actual_counts"]=dict(zip(("vectors","alias_mutant_mismatches","tile_mutant_mismatches","full_mutant_mismatches","extent_mutant_mismatches","next_mutant_mismatches"),map(int,found[0])))
    report["source_sha256_post"]={p:support.sha(ROOT/p) for p in bindings}
    assert report["source_sha256_post"]==bindings
    report["status"]="PASS_CONV_CONES_G1"
except Exception as exc:report["error"]=repr(exc)
finally:
    report["seconds"]=time.monotonic()-begin
    report["limits"]=["仅内部受控组合域，不是公开START可达性证明；不以未消费next地址作合同。","私有域仅21完整480bit命中；不声明私有任意U32等价。","FF三RHS文本例外绑定；公开boundary/private layer0另验证实际写入/全部周期。","源绑定43；scratch测试源码另绑定，不更改生产RTL/黄金。"]
    (evidence/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":report["status"],"seconds":report["seconds"],"error":report.get("error")},ensure_ascii=False),flush=True)
raise SystemExit(0 if report["status"]=="PASS_CONV_CONES_G1" else 2)
