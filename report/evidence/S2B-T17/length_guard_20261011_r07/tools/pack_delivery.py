#!/usr/bin/env python3
"""封存当前真实源码、已执行及失败原件；不提交、不覆盖旧Run。"""
import collections
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
BASELINE="5cb092dcce3631f310e67228738a674a6a82ce41"
CHANGED=("src/s2b_conv_tile_engine.sv","board/s2b_inference_platform.json","board/s2b_inference_platform.md",
    "vivado/s2b_inference_platform.tcl","verification/check_s2b_inference_platform.py",
    "verification/test_s2b_conv_validation_rtl.py","verification/test_s2b_backend_coordinates_rtl.py",
    "verification/test_s2b_geometry_specialization_rtl.py","verification/test_s2b_route_specialization_rtl.py")
EXTRA=("verification/test_s2b_conv_validation_rtl.py","verification/test_s2b_backend_coordinates_rtl.py",
    "verification/test_s2b_geometry_specialization_rtl.py","verification/test_s2b_route_specialization_rtl.py",
    "sim/tb_s2a_t66_candidate_blackbox.sv","verification/s1_t02_d2_int8_forward.py",
    "report/evidence/S2A-T01/tiny416_model_manifest.json")
def digest(path):
    """哈希始终按实际原字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    """JSON读取始终明确UTF-8。"""
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def write(path,data):
    """本脚本仅创建新证据。"""
    if path.exists():raise ValueError("禁止覆盖："+str(path))
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
def git(*args):
    """只读Git调用保留原字节及真实退出码。"""
    return subprocess.check_output(["git",*args],cwd=ROOT)
def copy(source,target):
    """精确父目录已存在；递归只复制已枚举的文件，不移动源。"""
    if not source.is_file() or source.is_symlink() or target.exists():raise ValueError("复制目标或源无效")
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    if digest(source)!=digest(target):raise ValueError("原字节复制不一致")
    return {"path":source.relative_to(ROOT).as_posix(),"copy":target.relative_to(ROOT).as_posix(),"sha256":digest(source)}

run_id,layer_run=sys.argv[1:3]
if not re.fullmatch(r"length_guard_20261011_r\d+",run_id):raise ValueError("RunId不符")
evidence=ROOT/"report/evidence/S2B-T17"/run_id
if not evidence.parent.is_dir() or evidence.exists():raise ValueError("精确父目录缺失或Run已存在")
evidence.mkdir()
spec=importlib.util.spec_from_file_location("checker",ROOT/"verification/check_s2b_inference_platform.py")
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
static=checker.check_static(ROOT);bindings={**static,**{p:digest(ROOT/p) for p in EXTRA}}
actual_commit=git("rev-parse","HEAD").decode().strip()
if git("diff","--name-only",BASELINE,actual_commit,"--",*bindings).decode().strip():raise ValueError("相关源码提交偏离S5")
profile=read("board/s2b_inference_platform.json")
frozen={p:digest(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
if frozen!=checker.FROZEN_CORE_SHA256:raise ValueError("冻结14原件漂移")
if set(CHANGED)!=set(git("diff","--name-only","--",*CHANGED).decode().splitlines()):raise ValueError("九文件待审差异不符")
for path,sha in bindings.items():copy(ROOT/path,evidence/"source_snapshot"/path)
encoding={p:{"utf8_decode_pass":True,"u_fffd_count":(ROOT/p).read_bytes().decode("utf-8").count("\ufffd")} for p in bindings}
if any(v["u_fffd_count"] for v in encoding.values()):raise ValueError("源码存在UTF8替换字符")
write(evidence/"source_encoding.json",encoding)
raw_mapping=[]
for native_run in ("length_guard_20261011_r01","length_guard_20261011_r02","length_guard_20261011_r03","length_guard_20261011_r04",layer_run,"length_guard_20261011_r06"):
    parent=ROOT/"report/evidence/S2B-T17"/native_run
    if not parent.is_dir():raise ValueError("真实Run缺失")
    for path in sorted(parent.rglob("*")):
        if path.is_file():raw_mapping.append(copy(path,evidence/"raw"/native_run/path.relative_to(parent)))
write(evidence/"raw_copy_mapping.json",raw_mapping)
boundary=read("report/evidence/S2B-T17/length_guard_20261011_r03/validation.json")
layer=read("report/evidence/S2B-T17/"+layer_run+"/validation.json")
for result in (boundary,layer):
    if result["status"]!="PASS" or result["source_sha256_pre"]!=bindings or result["source_sha256_post"]!=bindings:raise ValueError("真实运行未通过或源码不一致")
    if result["frozen14_sha256"]!=frozen or any(r["exit_code"]!=0 for r in result["runs"]):raise ValueError("原件或原生结果不符")
compiled=[]
for native_run in ("length_guard_20261011_r03",layer_run):
    for relative in ("src/s2a_network_descriptor_pkg.sv","src/s2a_conv_tile_engine.sv","src/s2b_conv_tile_engine.sv"):
        actual_source=ROOT/"tmp/2B/S2B-T17"/native_run/"source"/Path(relative).name
        if digest(actual_source)!=bindings[relative]:raise ValueError("实际编译副本漂移")
        compiled.append(copy(actual_source,evidence/"compiled_snapshot"/native_run/Path(relative).name))
write(evidence/"compiled_mapping.json",compiled)
if (layer["actual_coverage"]["bytes"],layer["actual_coverage"]["requests"],layer["actual_coverage"]["cycles"])!=(1384448,2551955,27235743):raise ValueError("完整layer0计数变化")
old_s5=read("report/evidence/S2B-T17/patch_guard_20261011_r07/source_freeze.json")
references=[]
for path in ("report/evidence/S2B-T17/patch_guard_20261011_r07/source_freeze.json",
    "report/evidence/S2B-T17/patch_guard_20261011_r07/delivery_manifest_r04.json",
    "report/evidence/S2B-T17/patch_guard_20261011_r07/cross_version_regression.json",
    "report/evidence/S2B-T17/independent_patch_guard_review_20261011_r01/raw_artifacts/tmp/2B/S2B-T17/independent_patch_guard_review_20261011_r04/final_review_receipt.json",
    "report/evidence/S2B-T17/s5_platform_20261011_r01/timing_summary_synth.rpt",
    "report/evidence/S2B-T17/s5_platform_20261011_r01/timing_worst_synth.rpt",
    "report/evidence/S2B-T17/s5_platform_20261011_r01/utilization_flat_synth.rpt"):
    references.append(copy(ROOT/path,evidence/"references"/path))
integration=[]
for prior_run,scope in (("patch_guard_20261011_r03","完整非零layer0"),("patch_guard_20261011_r04","几何"),
    ("patch_guard_20261011_r05","ROUTE"),("patch_guard_20261011_r06","全部15nonconv真实engine请求trace；CONV控制stub")):
    result=read("report/evidence/S2B-T17/"+prior_run+"/validation.json")
    expected_status={"patch_guard_20261011_r03":"PASS","patch_guard_20261011_r04":"PASS_GEOMETRY_SPECIALIZATION_G1",
        "patch_guard_20261011_r05":"PASS_ROUTE_SPECIALIZATION_DIRECT_G1","patch_guard_20261011_r06":"PASS_BACKEND_COORDINATES_G1"}[prior_run]
    if result["status"]!=expected_status or len(result["runs"])!=2 or any(r["exit_code"]!=0 for r in result["runs"]):raise ValueError("S5真实结果未通过")
    for name in ("validation.json","simulation.log","compile.log"):
        path=ROOT/"report/evidence/S2B-T17"/prior_run/name
        references.append(copy(path,evidence/"references"/prior_run/name))
    runtime_source={p:sha for p,sha in result["source_sha256_pre"].items() if p.endswith(".sv")}
    changed=[p for p,sha in runtime_source.items() if bindings.get(p,digest(ROOT/p))!=sha]
    if prior_run.endswith("r03"):
        if changed!=["src/s2b_conv_tile_engine.sv"] or result["actual_coverage"]!=layer["actual_coverage"]:raise ValueError("layer0新旧计数/影响范围不符")
        status="RERUN_PASS_COUNTS_EQUAL"
    else:
        if changed!=["src/s2b_conv_tile_engine.sv"]:raise ValueError("几何/ROUTE/nonconv的RTL有额外变化")
        # 上述static绑定包括CONV；真正编译的非卷积列表不消费它。
        command=next(r["command"] for r in result["runs"] if r["name"]=="compile")
        if any("s2b_conv_tile_engine.sv" in token for token in command):raise ValueError("旧非卷积编译存在受影响CONV")
        status="BOUND_UNCHANGED_RTL_NOT_RERUN"
    log=(ROOT/"report/evidence/S2B-T17"/prior_run/"simulation.log").read_text(encoding="utf-8")
    integration.append({"run":prior_run,"scope":scope,"status":status,"static_sources_changed":changed,
        "compile_command":next(r["command"] for r in result["runs"] if r["name"]=="compile"),
        "coverage":result.get("actual_coverage",result.get("simulation_counts",result.get("trace_counts"))),
        "trace_lines":[line for line in log.splitlines() if line.startswith("TRACE ")],"trace_summaries":result.get("trace_summaries"),
        "simulation_sha256":digest(ROOT/"report/evidence/S2B-T17"/prior_run/"simulation.log")})
write(evidence/"cross_version_regression.json",{"status":"PASS","integration":integration,"new_layer0_run":layer_run,"scope":"几何/ROUTE/nonconv沿用已绑定S5真实执行；本轮未重跑，CONV完整数值有新实际运行。"})
diff=git("diff","--",*CHANGED);(evidence/"source_changes.diff").write_bytes(diff)
checks=[]
for name,command in (("static_checker",[sys.executable,"-B","verification/check_s2b_inference_platform.py"]),
    ("diff_check",["git","diff","--check","--",*CHANGED])):
    process=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (evidence/(name+".log")).write_bytes(process.stdout)
    checks.append({"name":name,"status":"PASS" if process.returncode==0 else "FAIL","command":subprocess.list2cmdline(command),"exit_code":process.returncode})
    if process.returncode:raise ValueError("末轮静态检查失败")
warnings=[]
for current,prior in (("length_guard_20261011_r03","patch_guard_20261011_r02"),(layer_run,"patch_guard_20261011_r03")):
    texts=[(ROOT/"report/evidence/S2B-T17"/r/"compile.log").read_text(encoding="utf-8") for r in (current,prior)]
    counts=[dict(collections.Counter(re.findall(r"%Warning-([A-Z]+):",t))) for t in texts]
    warnings.append({"current":current,"prior":prior,"warning_counts_current_prior":counts,"new_changed_path_warnings":[line for line in texts[0].splitlines() if "%Warning" in line and "s2b_conv_tile_engine" in line]})
write(evidence/"compile_diagnostics.json",{"status":"PASS_NATIVE_COMPILE_NO_FATAL","comparisons":warnings,
    "reason":"已有-Wall/-Wno-fatal策略不改；新增窄结果零扩展留下未使用高位诊断，原件完整保留。未执行Vivado lint或STA。"})
for run,result in (("length_guard_20261011_r03",boundary),(layer_run,layer)):
    for native in result["runs"]:
        checks.append({"name":run+"_"+native["name"],"status":"PASS","command":subprocess.list2cmdline(native["command"]),"exit_code":native["exit_code"]})
checks.extend([{"name":"historical_ram_preflight_r01","status":"FAIL","command":"python -B verification/test_s2b_conv_validation_rtl.py --run-id length_guard_20261011_r01 --mode boundary --prepare-only","exit_code":2,"reason":"真实脚本返回2，外层exec显示1；未启动编译。r01门禁原件保留。"},
    {"name":"historical_ram_preflight_r04","status":"FAIL","command":"python -B verification/test_s2b_conv_validation_rtl.py --run-id length_guard_20261011_r04 --mode layer0","exit_code":2,"reason":"native_driver捕获真实2，外层exec显示1；未CPU/编译。"}])
checks.append({"name":"historical_packaging_r06","status":"FAIL","command":"python -B tmp/2B/S2B-T17/length_guard_20261011_r02/pack_delivery.py length_guard_20261011_r06 length_guard_20261011_r05","exit_code":1,"reason":"封包器错误把S5特定PASS_GEOMETRY_SPECIALIZATION_G1等状态当作失败；真实S5运行均native0，非设计或测试失败。r06部分包及失败原件保留，本轮按各runner准确状态名核对。"})
for name,reason in (("G2独立审查","源码停止写入，由总控派发Reviewer。"),("S6综合_STA_postroute_bit","本轮只进行仿真等价交付，待G2后由总控执行新的50MHz综合。"),("G3_109整网","仅sample000完整layer0，未进行板卡、109整网或1000次板上运行。")):
    checks.append({"name":name,"status":"NOT_RUN","command":None,"exit_code":None,"reason":reason})
limitations=["物理候选0.1.1未冻结，visibility0，50MHz不变；G2/STA/G3未执行。",
    "数学/结构与逐周期仿真通过不等于50MHz时序收敛；S5真实FAIL_TIMING原件仅为诊断输入。",
    "CONV数值只新执行sample000完整layer0；几何、ROUTE与nonconv是真实S5已绑定结果，本轮未重跑。",
    "原14源码、两个always_ff及公开接口未变；没有Git暂存/提交/分支/ROSS/SDK/串口/板卡操作。",
    "r01/r04资源门禁失败保留；r01宿主退出1与脚本按代码返回2分别记录，r04有真实native2。",
    "r06封包器因错误要求旧特定PASS标签必须等于PASS而native1；原件保留，新Run核对精确状态名与实际native0。",
    "最初两次inline Bash heredoc命令在宿主解释失败、一次apply_patch输出中文编码匹配失败；未启动原生项目检查，未改变目标文件。后续明确UTF8并使用临时脚本。",
    "全Agent工具调用量及全系统峰内存未测；编译/仿真0.1秒采样进程树RSS与CPU进程峰已有实际记录。"]
write(evidence/"g1_summary.json",{"status":"PASS_DECLARED_SCOPE","boundary":boundary["actual_coverage"],"layer0":layer["actual_coverage"],
    "independent_cpu_layer0":layer["independent_cpu_layer0"],"length_proof":boundary["length_proof"],
    "random_coverage":{"vectors":boundary["math_oracle"]["vectors"],"categories":boundary["math_oracle"]["categories"],"seed":boundary["math_oracle"]["length_seed"]},
    "native_runs":boundary["runs"]+layer["runs"],"runner_elapsed_seconds":[boundary["elapsed_seconds"],layer["elapsed_seconds"]],"checks":checks,"limitations":limitations})
write(evidence/"source_freeze.json",{"schema_version":1,"task_id":"S2B-T17-S6","run_id":run_id,
    "freeze_state":"STOPPED_PENDING_INDEPENDENT_REVIEW","source_baseline_commit":BASELINE,"source_commit_at_freeze":actual_commit,
    "s5_source_freeze":{"path":"report/evidence/S2B-T17/patch_guard_20261011_r07/source_freeze.json","sha256":digest(ROOT/"report/evidence/S2B-T17/patch_guard_20261011_r07/source_freeze.json")},
    "profile_version":profile["version"],"physical_interface":profile["physical_interface"],"clock_hz":profile["clock_hz"],"visibility_default":profile["visibility_default"],
    "active_rtl_count":len(profile["rtl_sources"]),"static_binding_count":len(static),"source_binding_count":len(bindings),
    "extra_bindings_beyond_static":[p for p in bindings if p not in static],"source_sha256":bindings,"frozen14_sha256":frozen,"frozen14_unchanged":True,
    "changed_paths":list(CHANGED),"source_diff_sha256":hashlib.sha256(diff).hexdigest(),"g1":"PASS_DECLARED_SCOPE","g2":"NOT_RUN","sta":"NOT_RUN","g3":"NOT_RUN","git_commit":"NOT_PERFORMED_DEVELOPER_ROOT_OWNS_COMMIT"})
write(evidence/"reference_mapping.json",references)
for name in ("native_driver.py","pack_delivery.py"):
    copy(Path(__file__).parent/name,evidence/"tools"/name)
file_metrics=[{"path":p.relative_to(ROOT).as_posix(),"bytes":p.stat().st_size,"sha256":digest(p)} for p in sorted(evidence.rglob("*")) if p.is_file()]
write(evidence/"artifact_metrics.json",{"bytes_total_before_metrics":sum(p["bytes"] for p in file_metrics),"files":file_metrics})
files=[{"path":p,"sha256":sha,"role":"source" if p!=EXTRA[-1] else "input"} for p,sha in bindings.items()]
for p in sorted(evidence.rglob("*")):
    if not p.is_file():continue
    role="log" if p.suffix in (".log",".rpt") else "source" if "source_snapshot" in p.parts else "input" if p.name=="validation_vectors.txt" else "diagnostic" if "diagnostic" in p.name else "artifact"
    files.append({"path":p.relative_to(ROOT).as_posix(),"sha256":digest(p),"role":role})
manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":run_id,"source_commit":actual_commit,
    "evidence_dir":evidence.relative_to(ROOT).as_posix(),"interfaces":read("report/evidence/S2B-T17/patch_guard_20261011_r07/delivery_manifest_r04.json")["interfaces"],
    "files":files,"checks":checks,"limitations":limitations,"tool_versions":boundary["tool_versions"]}
write(evidence/"delivery_manifest_r01.json",manifest)
print(json.dumps({"status":"PACKED_PENDING_WRAPPER_CHECKS","evidence":str(evidence),"bindings":len(bindings),"static":len(static),"manifest_sha256":digest(evidence/"delivery_manifest_r01.json")},ensure_ascii=False))
