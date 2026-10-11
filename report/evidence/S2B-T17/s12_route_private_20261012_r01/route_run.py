"""仅在ROOT单槽准入后运行完整ROUTE通用/私有query与语义变体。"""
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

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/"verification"))
import test_s2b_backend_coordinates_rtl as support
parser=argparse.ArgumentParser();parser.add_argument("--run-id",required=True);parser.add_argument("--toolchain",type=Path,required=True);args=parser.parse_args()
assert re.fullmatch(r"s12_route_private_20261012_r\d+",args.run_id)
work=ROOT/"tmp/2B/S2B-T17"/args.run_id;evidence=ROOT/"report/evidence/S2B-T17"/args.run_id
assert work.parent.is_dir() and evidence.parent.is_dir() and not work.exists() and not evidence.exists()
prepared=HERE/"route_input";receipt=json.loads((prepared/"prepared_receipt.json").read_text(encoding="utf-8"))
assert receipt["status"]=="PREPARED_NOT_RUN" and args.toolchain.is_dir()
for item in receipt["files"]:assert support.sha(Path(item["path"]))==item["sha256"]
assert subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==receipt["source_commit"]
assert support.sha(ROOT/"src/s2b_route_query.sv")==receipt["candidate_raw_sha256"]
assert support.sha(ROOT/"verification/test_s2b_route_address_guard_rtl.py")==receipt["oracle_sha256"]
checker=support.load_checker();checker.check_static(ROOT)
freeze=json.loads((ROOT/"tmp/2B/S2B-T17/s12_combined_prepare_20261012_r01/source_freeze_prepare.json").read_text(encoding="utf-8"))
bindings={item["path"]:support.sha(ROOT/item["path"]) for item in freeze["source_files"]}
work.mkdir();evidence.mkdir();begin=time.monotonic()
report={"status":"FAIL","task_id":"S2B-T17-S12","source_commit":receipt["source_commit"],"run_id":args.run_id,"runs":[],"prepared_input":receipt,"source_sha256_pre":bindings,"script_sha256":support.sha(Path(__file__)),"g2":"NOT_RUN","sta":"NOT_RUN","g3":"NOT_RUN"}
try:
    snapshot=evidence/"source_snapshot";snapshot.mkdir()
    for path in bindings:
        target=snapshot/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,target)
    names=("s12_route_query_original.sv","s2b_route_query.sv","s12_route_query_alias.sv","s12_route_query_unused.sv","tb_s12_route_private.sv")
    for name in names:shutil.copyfile(prepared/name,work/name);shutil.copyfile(prepared/name,evidence/name)
    for name in ("vectors.dat","prepared_receipt.json"):shutil.copyfile(prepared/name,evidence/name)
    for path in (Path(__file__),HERE/"route_prepare.py"):shutil.copyfile(path,evidence/path.name)
    tools=args.toolchain/"mingw64/bin";make=args.toolchain/"usr/bin"
    verilator=checker.exact_file(tools/"verilator_bin.exe")
    env=os.environ.copy();env["PATH"]=str(make)+os.pathsep+str(tools)+os.pathsep+env.get("PATH","")
    env["VERILATOR_ROOT"]=str(args.toolchain/"mingw64/share/verilator");env["PYTHONUTF8"]="1"
    report["tool_versions"]={"python":sys.version,"verilator":subprocess.check_output([str(verilator),"--version"],cwd=work,env=env,text=True,timeout=30).strip()}
    command=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--top-module","tb_s12_route_private","--Mdir","obj_dir","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1",*names]
    for stage,cli in (("lint",["--lint-only" if s=="--binary" else s for s in command]),("compile",command)):
        support.execute(stage,cli,work,evidence,env,report,600)
        log=(evidence/(stage+".log")).read_text(encoding="utf-8")
        if re.search(r"%Warning-(?:LATCH|UNOPTFLAT|MULTIDRIVEN)\b",log):raise ValueError("ROUTE公开端口bench不允许三类组合/多驱动诊断")
    support.execute("simulation",[str(work/"obj_dir/Vtb_s12_route_private.exe"),"+VECTOR_PATH="+str(evidence/"vectors.dat")],work,evidence,env,report,600)
    log=(evidence/"simulation.log").read_text(encoding="utf-8")
    found=re.findall(r"PASS S12_ROUTE_PRIVATE vectors=(\d+) hits=(\d+) misses=(\d+) alias=(\d+) unused=(\d+)",log)
    assert len(found)==1
    actual=list(map(int,found[0]));assert actual[:3]==[receipt["vectors"],receipt["private_hit_vectors"],receipt["private_miss_vectors"]] and all(v>0 for v in actual[3:])
    report["actual_counts"]=dict(zip(("vectors","hits","misses","alias_mutant_mismatches","unused_source1_mutant_mismatches"),actual))
    report["source_sha256_post"]={p:support.sha(ROOT/p) for p in bindings};assert report["source_sha256_post"]==bindings
    report["status"]="PASS_ROUTE_PRIVATE_G1"
except Exception as exc:report["error"]=repr(exc)
finally:
    report["seconds"]=time.monotonic()-begin
    report["limits"]=["完整query公开组合端口，不是engine公共START周期测试；与generic周期及backend START另证互补。","私有命中完整96bit冻结形状，未命中ARG域明确不同，不称私有任意U32等价。","两个变体均完整query模块，只有实际RTL八输出差异非零才称击杀。","尚非STA/G2/G3/109完整数值证明。"]
    (evidence/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":report["status"],"seconds":report["seconds"],"error":report.get("error")},ensure_ascii=False),flush=True)
raise SystemExit(0 if report["status"]=="PASS_ROUTE_PRIVATE_G1" else 2)
