"""S12主交付工具：prepare不封存；全部真实回归结束后才可finalize。"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
BASE="891f750045ce141a8152c96025da559ff1d3a321"
RUNS={"pool":"s12_pool_timing_20261012_r01","boundary":"s12_conv_boundary_20261012_r01","layer0":"s12_conv_layer0_20261012_r01","cones":"s12_conv_cones_20261012_r03","private_route":"s12_route_private_20261012_r01","feature":"s12_conv_feature_20261012_r01","output":"s12_conv_output_20261012_r01","backend":"s12_backend_timing_20261012_r01","generic_route":"s12_route_generic_20261012_r01"}
FIVE=("src/s2b_maxpool_engine.sv","src/s2b_conv_tile_engine.sv","src/s2b_route_query.sv","src/s2b_route_engine.sv","src/s2b_network_backend.sv")
MAIN=ROOT/"report/evidence/S2B-T17/s12_timing_cones_20261012_r01"
TOOLGUARD=ROOT/"report/evidence/S2B-T17/s12_resource_guard_delivery_20261012_r01/delivery_manifest_r02.json"
parser=argparse.ArgumentParser();parser.add_argument("--mode",choices=("prepare","finalize"),required=True);args=parser.parse_args()

def sha(path):
    """流式核验，避免大向量重复驻留内存。"""
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1048576),b""):h.update(block)
    return h.hexdigest()

def read(path):return json.loads(path.read_text(encoding="utf-8"))
def write(path,value):
    """只创建精确新文件，不覆盖任何原件。"""
    with path.open("x",encoding="utf-8",newline="\n") as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")

def copy(source,target,mapping):
    """保留RAW字节并绑定原路径、恢复路径、SHA和长度。"""
    assert source.is_file() and not target.exists()
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);assert sha(source)==sha(target)
    mapping.append({"original_path":source.relative_to(ROOT).as_posix(),"archived_path":target.relative_to(ROOT).as_posix(),"sha256":sha(target),"bytes":target.stat().st_size})

sys.path.insert(0,str(ROOT/"verification"));import check_s2b_inference_platform as checker
started=time.monotonic();static=checker.check_static(ROOT)
assert TOOLGUARD.is_file() and sha(TOOLGUARD)=="139d5b72f9faa0bb58943b0dcff0d5e70ebcd8d189246e061a4df6013f8c3dce"
original_prepare=ROOT/"tmp/2B/S2B-T17/s12_combined_prepare_20261012_r01/source_freeze_prepare.json"
paths=[x["path"] for x in read(original_prepare)["source_files"]]
assert len(paths)==43 and len(set(paths))==43 and len(static)==33 and set(static)<=set(paths)
current={p:sha(ROOT/p) for p in paths};records=[];pending=[]
for stage,run in RUNS.items():
    validation=ROOT/"report/evidence/S2B-T17"/run/"validation.json"
    native=(ROOT/"tmp/2B/S2B-T17"/run/"native_receipt.json") if stage=="pool" else HERE/(run+"_capture")/"native_receipt.json"
    if not validation.is_file() or not native.is_file():pending.append(stage);records.append({"stage":stage,"run_id":run,"status":"NOT_RUN_OR_RUNNING"});continue
    v=read(validation);n=read(native);inner_pre=v["source_sha256_pre"];inner_post=v["source_sha256_post"]
    outer_pre=n["source_pre"];outer_post=n["source_post"]
    assert inner_pre==inner_post and outer_pre==outer_post and n["native_returncode"]==0 and n["supervisor_stop"] is None
    assert v["status"].startswith("PASS")
    assert all(inner_post.get(p)==current[p] and outer_post.get(p)==current[p] for p in FIVE)
    drift={p:{"tested":h,"final_candidate":current[p]} for p,h in outer_post.items() if p in current and current[p]!=h}
    assert not drift or (stage=="pool" and set(drift)=={"verification/test_s2b_conv_validation_rtl.py"})
    records.append({"stage":stage,"run_id":run,"status":v["status"],"validation_path":validation.relative_to(ROOT).as_posix(),"validation_sha256":sha(validation),"native_path":native.relative_to(ROOT).as_posix(),"native_sha256":sha(native),"inner_source_count":len(inner_post),"outer_source_count":len(outer_post),"tested_source_drift":drift,"native_command":n["command"],"native_returncode":n["native_returncode"],"elapsed_seconds":n["elapsed_seconds"],"sampled_peak_rss_bytes":n["sampled_tree_peak_rss_bytes"],"source_stable_within_run":True,"actual_fields":{k:v[k] for k in ("geometry_coverage","engine_simulation_counts","actual_coverage","actual_counts","simulation_counts","public_entries","layer0","boundary") if k in v},"runs":v["runs"]})
functional=ROOT/"tmp/2B/S2B-T17/s12_root_run_20261012_r01/functional_subchecks_root_verification_20261012_r03.json";assert functional.is_file() and sha(functional)=="e696ba350a57848a7b42c6ce7bf4d863d472c41860b37c423c932371f2cf26aa"
backend_source=ROOT/"verification/test_s2b_backend_coordinates_rtl.py"
assert "timeout = min(timeout,600)" in backend_source.read_text(encoding="utf-8")
execution_policy_corrections={"backend_and_generic_route":{"source_path":backend_source.relative_to(ROOT).as_posix(),"source_sha256":sha(backend_source),"actual_inner_execute_timeout_seconds":600,"actual_outer_total_timeout_seconds":600,"source_basis":"execute中timeout=min(timeout,600)；调用simulation1200只是请求值，经min后有效600。generic ROUTE实际复用backend.execute。","preserved_inaccurate_metadata":"旧supervisor receipt limits中的backend内simulation1200说明以及generic ROUTE resource_budget旧300MiB保留原件；实际execute/外层缓存640MiB。","scope":"只纠正交付解释，不改原源码/runner/日志/receipt/实际预算或退出码。"}}
plan={"status":"TOOL_PREPARED_G1_PENDING" if pending else "TOOL_PREPARED_ALL_DECLARED_RUNS_COMPLETE","source_commit":BASE,"pending":pending,"runs":records,"source_path_count":len(paths),"static_count":len(static),"limitations":"这里只是准备/原件读取；不封存源码，不等于整体G1/G2/STA/G3。内外来源数由每个真实JSON派生，POOL跨run runner漂移单独记录。"}
plan["execution_policy_corrections"]=execution_policy_corrections
plan["root_record"]={"path":functional.relative_to(ROOT).as_posix(),"sha256":sha(functional),"scope":"ROOT对9组native/validation/来源绑定核查；其artifacts逐RAW核验为backend5+generic ROUTE41=46件，不能扩大为所有raw或整体G2/STA。"}
if args.mode=="prepare":
    print(json.dumps(plan,ensure_ascii=False));raise SystemExit(0)
assert not pending and MAIN.parent.is_dir() and not MAIN.exists()
assert subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==BASE
rq=ROOT/"report/evidence/S2B-T17/s12_requant_rtl_20261012_r01";assert read(rq/"archive_summary.json")["status"]=="PASS_G1_REQUANT_WHITEBOX_SUBCHECK_ONLY"
review=ROOT/"tmp/2B/S2B-T17/independent_s12_requant_rtl_review_20261012_r01";rr=read(review/"final_review_receipt.json");assert rr["status"]=="PASS" and rr["reviewer_stop"]=="STOP_NO_FURTHER_WRITES"
assert rr["reviewed_source_hashes"]["src/s2b_conv_tile_engine.sv"]==current["src/s2b_conv_tile_engine.sv"]
frozen={p:sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256};assert frozen==checker.FROZEN_CORE_SHA256
MAIN.mkdir();mapping=[];snapshot=MAIN/"final_source_snapshot"
for p in paths:copy(ROOT/p,snapshot/p,mapping)
modified=subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","diff","--name-only",BASE,"--",*paths],cwd=ROOT,text=True).splitlines()
diff_command=["git","-c","core.longpaths=true","-c","maintenance.auto=false","diff","--no-ext-diff","--no-color",BASE,"--",*modified]
diff=subprocess.check_output(diff_command,cwd=ROOT)
with (MAIN/"source_diff.patch").open("xb") as stream:stream.write(diff)
freeze={"schema_version":1,"source_commit":BASE,"profile":"s2b-inference-platform/0.1.12","active_rtl_sources":read(ROOT/"board/s2b_inference_platform.json")["rtl_sources"],"source_files":[{"path":p,"sha256":current[p],"bytes":(ROOT/p).stat().st_size,"snapshot":(snapshot/p).relative_to(ROOT).as_posix()} for p in paths],"frozen14":frozen,"modified_files":{p:current[p] for p in modified},"tested_source_drift":{r["stage"]:r["tested_source_drift"] for r in records if r["tested_source_drift"]},"initial_prepare":{"path":original_prepare.relative_to(ROOT).as_posix(),"sha256":sha(original_prepare),"scope":"原始prepare保持；仅43路径清单消费，旧bytes/snapshot/modified/engine字段不继承。"},"source_diff_sha256":sha(MAIN/"source_diff.patch"),"ff_contract":{"public_ports":"不变；私有参数默认0且backend固定域1。","allowed_rhs_exception":"仅CONV ST_TILE_PREP patch_height/patch_width/patch_byte_count三个RHS；不能称整个CONV FF后缀字节不变。","evidence_path":"report/evidence/S2B-T17/"+RUNS["cones"]+"/prepared_receipt.json"},"engine_raw_unchanged":False}
observed=subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","rev-parse","HEAD"],cwd=ROOT,text=True).strip();assert observed==BASE
commit_role={"source_commit_role":"实际precommit Git baseline，不是候选43 RAW所属Git tree。","actual_observed_head":observed,"actual_source_worktree_snapshot":{"state":"UNCOMMITTED_CANDIDATE_RAW","modified_paths":modified,"source_paths_count":len(paths),"snapshot_directory":snapshot.relative_to(ROOT).as_posix(),"binding":"source_files中的RAW SHA/bytes及source_diff_sha256；ROOT提交后另捕获实际newcommit physical43 freeze。"}}
freeze.update(commit_role)
write(MAIN/"source_freeze.json",freeze)
for path in (Path(__file__),HERE/"regression_supervisor.py",original_prepare,functional):copy(path,MAIN/"execution_raw"/path.name,mapping)
for r in records:
    native=ROOT/r["native_path"]
    for path in sorted(native.parent.iterdir()):
        if path.is_file() and path.name in ("native_receipt.json","runner.stdout.log","runner.stderr.log","samples.jsonl"):copy(path,MAIN/"execution_raw"/r["stage"]/path.name,mapping)
for run in ("s12_conv_cones_20261012_r01","s12_conv_cones_20261012_r02"):
    capture=HERE/(run+"_capture");assert read(capture/"native_receipt.json")["native_returncode"]==2
    for path in sorted(capture.iterdir()):
        if path.is_file():copy(path,MAIN/"failed_execution_raw"/run/path.name,mapping)
for name in ("repair_cones_r03.py","cones_repair_r03.stdout.log","cones_repair_r03.stderr.log","cones_repair_r03.native_receipt.json"):
    copy(HERE/name,MAIN/"failed_execution_raw"/"r03_prepare_first"/name,mapping)
for path in sorted(review.iterdir()):
    assert path.is_file();copy(path,MAIN/"requant_narrow_review_raw"/path.name,mapping)
for kind in ("feature","output","backend"):
    path=HERE/(RUNS[kind]+"_diagnostics")/"receipt.json";assert path.is_file();copy(path,MAIN/"diagnostics"/(kind+".json"),mapping)
for name in ("review_backend_diagnostics.py","backend_diag.native_receipt.json","backend_diag.stdout.log","backend_diag.stderr.log"):
    copy(HERE/name,MAIN/"diagnostics"/name,mapping)
write(MAIN/"raw_restore_mapping.json",mapping)
limits=["source_commit891为实际precommit Git baseline/actual_observed_head；本轮43 RAW包含16未提交候选变化，不是Git891 tree。实际worktree快照/diff/角色见source_freeze及g1_summary，ROOT提交后另捕获physical43/newcommit，不填未知futurecommit。","G1功能与整S12独立G2/STA/G3分别判断；S11真实postroute FAIL，S12 STA尚未执行。","private1仅冻结480bit CONV/96bit ROUTE可达域；default0通用U32语义仍保留，不宣称private任意U32等价。","CONV private1 layer0公开START/CPU黄金真实数值；其余20个CONV层仅有白盒数学/派发控制证据，不称21个CONV层完整数值或109整网。","backend15非CONV数值fulltrace与38层CONV stub调度分别判断；stub不是CONV数值。backend.execute实际min(timeout,600)，simulation调用1200不是有效内超时；generic ROUTE亦使用此execute。旧supervisor误述1200及ROUTE旧300MiB metadata保持原件，实际execute及外层缓存640MiB。","组合域TB受控MULTIDRIVEN逐条绑定；不全局豁免生产新异常；峰是离散采样，非连续绝对峰。","POOL跨run validation runner来源变化单列；各run内pre/post稳定不等于所有run均等于最终43源。","REQ独审只批准138791二态数值子检查；不扩大为整个S12 G2或预算重型PASS；用户板卡拔掉，本轮无设备操作。"]
summary={"status":"PASS_S12_G1_FUNCTIONAL_ONLY","source_commit":BASE,"profile":freeze["profile"],"source_closure_count":43,"static_count":33,"active_rtl_count":18,"derived_rtl_count":8,"frozen14_count":14,"runs":records,"prior_failed_attempts":{"cones_r01":"不存在ST_REQUANT测试夹具编译1/runner2/wrapper1；未执行仿真。","cones_r02":"五处private enum身份转换编译1/runner2/wrapper1；未执行仿真。","r03_prepare_first":"轻量驱动登记预期数错误native1；未执行RTL；新准备原生0，登记148逐赋值。"},"requant_narrow_g2":{"status":"PASS","scope":rr["scope"],"receipt_sha256":sha(review/"final_review_receipt.json"),"raw_manifest_sha256":sha(review/"raw_manifest.jsonl")},"toolguard_dependency":{"path":TOOLGUARD.relative_to(ROOT).as_posix(),"sha256":sha(TOOLGUARD),"scope":"仅已封存工具逻辑/绑定G2依赖；不替代本轮实际重型资源样本/预算结论。"},"independent_review":"NOT_RUN","sta":"NOT_RUN","g3":"NOT_RUN","limitations":limits}
summary.update(commit_role)
summary["execution_policy_corrections"]=execution_policy_corrections
summary["root_record"]=plan["root_record"]
write(MAIN/"g1_summary.json",summary)
interfaces=read(ROOT/"report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r02/delivery_manifest.json")["interfaces"]
files={p:{"path":p,"sha256":h,"role":"source"} for p,h in current.items()}
external=[ROOT/r["validation_path"] for r in records]+[rq/"delivery_manifest_r02.json",rq/"archive_summary.json",original_prepare,TOOLGUARD]
for run in (*RUNS.values(),"s12_conv_cones_20261012_r01","s12_conv_cones_20261012_r02"):external.extend(p for p in (ROOT/"report/evidence/S2B-T17"/run).rglob("*") if p.is_file())
external.extend(p for p in rq.rglob("*") if p.is_file())
for path in [*sorted(MAIN.rglob("*")),*external]:
    if not path.is_file():continue
    assert not set(path.parts)&{".runs",".gen",".srcs",".cache","obj_dir"} and path.suffix.lower() not in (".exe",".o",".obj",".gch",".dcp",".bit")
    own=path.is_relative_to(MAIN);relative=path.relative_to(ROOT).as_posix()
    role="input" if not own else "log" if path.suffix in (".log",".jsonl") else "source" if path.suffix in (".py",".sv",".tcl",".md") else "diagnostic" if path.suffix==".patch" else "result"
    files[relative]={"path":relative,"sha256":sha(path),"role":role}
checks=[]
for r in records:
    command=r["native_command"];command=subprocess.list2cmdline(command) if isinstance(command,list) else command
    assert isinstance(command,str) and command.strip()
    checks.append({"name":r["stage"]+"真实runner","status":"PASS","command":command,"exit_code":r["native_returncode"],"reason":"真实原生结果绑定，范围见g1_summary；不是独立整包批准。"})
    for x in r["runs"]:
        assert x["exit_code"]==0
        checks.append({"name":r["stage"]+" "+x["name"],"status":"PASS","command":subprocess.list2cmdline(x["command"]),"exit_code":x["exit_code"],"reason":"真实子命令/log/native，不填自报审查码。"})
checks.extend({"name":n,"status":"NOT_RUN","command":None,"exit_code":None,"reason":why} for n,why in (("整S12 G2","ROOT后续独立审查。"),("S12 STA","尚未真实综合实现，S11 postroute仍FAIL。"),("G3","板卡由用户拔掉，未操作硬件。")))
manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":MAIN.name,"source_commit":BASE,"evidence_dir":MAIN.relative_to(ROOT).as_posix(),"interfaces":interfaces,"files":list(files.values()),"checks":checks,"tool_versions":{r["stage"]:read(ROOT/r["validation_path"])["tool_versions"] for r in records},"limitations":limits}
write(MAIN/"delivery_manifest.json",manifest)
assert current=={p:sha(ROOT/p) for p in paths}
print(json.dumps({"status":"MAIN_CREATED_CHECKS_NOT_RUN","source_freeze_sha256":sha(MAIN/"source_freeze.json"),"manifest_sha256":sha(MAIN/"delivery_manifest.json"),"summary_sha256":sha(MAIN/"g1_summary.json"),"source_diff_sha256":sha(MAIN/"source_diff.patch"),"seconds":time.monotonic()-started},ensure_ascii=False))
