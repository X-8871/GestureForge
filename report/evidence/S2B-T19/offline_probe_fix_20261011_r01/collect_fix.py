"""T19-R1修复的全新证据包装；只做AST/标准库/mock，不导入SDK串口。"""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

ROOT=Path(__file__).absolute().parents[4]
CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T19/offline_probe_fix_20261011_r01"
TEMP=ROOT/"tmp/2B/S2B-T19"
assert REPORT.is_dir() and TEMP.is_dir()

def sha(file):
    """固定原字节，不复制大型依赖。"""
    h=hashlib.sha256()
    with file.open("rb") as src:
        for block in iter(lambda:src.read(1048576),b""):h.update(block)
    return h.hexdigest()

def rel(file):
    """精确仓库相对路径。"""
    return file.relative_to(ROOT).as_posix()

def save(file,value):
    """UTF8/LF只创建新名称，旧失败证据不覆盖。"""
    assert file.parent.is_dir() and not file.exists()
    with file.open("x",encoding="utf-8",newline="\n") as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write("\n")

def copy(source,target):
    """只归档小源码、原UART和日志；校验原字节一致。"""
    assert source.is_file() and target.parent.is_dir() and not target.exists()
    with target.open("xb") as out:out.write(source.read_bytes())
    assert sha(source)==sha(target)

started_at=datetime.now(timezone(timedelta(hours=8))).isoformat();started=time.monotonic()
old=ROOT/"report/evidence/S2B-T19/offline_probe_entry_20261011_r01"
old_raw={rel(file):sha(file) for file in old.rglob("*") if file.is_file()}
sources=[ROOT/"vitis/run_s2b_visibility_probe.py",ROOT/"verification/test_s2b_visibility_probe.py"]
source_sha={rel(file):sha(file) for file in sources}
snapshot=REPORT/"source_snapshot";assert not snapshot.exists();snapshot.mkdir()
for source in sources:copy(source,snapshot/source.name)
for source in (Path(__file__),CACHE/"run_offline_tests.py"):copy(source,REPORT/source.name)
receipt=ROOT/"tmp/2B/S2B-T19/independent_review_20261011_r01/review_receipt.json"
assert sha(receipt)=="637d985d16d32ceac32c997e6f7d6f8c3cd31ddddceb3d236a41aa9bfe5b4bb9"
copy(receipt,REPORT/"upstream_review_changes_required.json")
spec=importlib.util.spec_from_file_location("t19_fix_entry",sources[0]);entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
closure=entry.sdk_source_closure();j,_=entry.helpers()
sdk={name:{"path":str(j.exact_path(file)),"sha256":sha(file)} for name,file in closure.items()}
runtime=ROOT/"report/evidence/S2B-T19/runtime_import_probe_20261011_r01/runtime_result.json"
observed=entry.strict_json(runtime.read_text(encoding="utf-8"))
matched=[]
for module in observed["loaded_modules"]:
    if module["name"].startswith("serial"):continue
    assert sdk[module["name"]]=={"path":module["file"],"sha256":module["sha256"]};matched.append(module["name"])
save(REPORT/"sdk_source_closure.json",{"schema_version":1,"source_selection":"官方XSDB导入AST转发闭包；tcf.services.DefaultServiceProvider按service_name构造*Proxy模块，绑定其可加载代理；HSI实际Windows两个pyd。","modules":sdk,"module_count":len(sdk),"total_bytes":sum(file.stat().st_size for file in closure.values()),"root_import_only_evidence":{"path":rel(runtime),"sha256":sha(runtime),"matched_nonserial_modules":matched},"runtime_created_session_here":False,"runtime_import_here":False,"limits":["这是SDK源码/直接Python扩展模块闭包；操作系统、Python标准库及底层DLL没有逐项源码冻结。","root独立import-only证明解释器可导入和当时模块来源，不证明本脚本的会话、下载或缓存G3。"]})
save(REPORT/"preliminary_diagnostics.json",{"hardware_execution":"NOT_RUN","diagnostics":[{"native_exit_code":1,"category":"SOURCE_CLOSURE_EXPLORATION","reason":"首轮枚举TCF目录全部.py命中未由官方*Proxy工厂导入的ContextReset.py SyntaxError line50；改为官方工厂的*Proxy.py来源。","source_snapshot":"当时入口精确快照未保存，不伪造SHA。"},{"native_exit_code":1,"category":"SOURCE_CLOSURE_RESOURCE_GATE","reason":"初4MiB单文件门禁拒绝实际4680192B的xv_hsmpytasks.pyd；现每文件8MiB、源码总量32MiB，实测闭包7583181B。","source_snapshot":"当时入口精确快照未保存，不伪造SHA。"}]})
save(REPORT/"config_contract.json",{"schema_version":1,"candidate_version":"s2b-visibility-probe-config/0.2.0","config_keys":sorted(entry.CONFIG_KEYS),"key_count":len(entry.CONFIG_KEYS),"change":"新增sdk_files；旧13键候选配置将拒绝，当前为14键。","binding_keys":["init_elf","app_elf","xsa","bit","csr_source","interface","sdk_target","tool_source","elf_parser","delivery_parser","transport_source","entry_source","platform_checker","sdk_init","pyserial_init"],"sdk_files":"JSON对象，key为sdk_source_closure()返回的实际模块名，value仅{path:精确绝对路径,sha256:原字节64位SHA256}；闭包缺项、多项、重复路径和实际来源漂移均拒绝。","strict_json":"所有消费的config/build/compat/platform_manifest/server元数据和系统查询JSON拒重复嵌套键、NaN/Infinity；schema_version只接受int，bool拒绝。解析前保留原字节；坏config创建唯一config_rejection Run而不接硬件。","connection":"官方session.connect(url='TCP:localhost:3121',server='hw_server')；官方异常分支不会auto-launch，不能改回127.0.0.1。","runtime":"建立SDK会话前绑定模块__file__/SHA及Session/Target/reset/Breakpoint真实方法code和接收器；已有SDK会话拒绝，避免清理调用方资源。","compatibility":"继续root冻结flat receipt：compiled_xsa是实际T15旧编译XSA，implemented_xsa为root新平台，不同文件；真实独审来源、bit与官方cold依据仍需root固定。","run_api":"run(config)的config为精确JSON绝对路径；仅root显式调用后可接SDK/COM4。--help/导入无SDK串口。","deployment_ready":False})
before=set(TEMP.iterdir())
command=[sys.executable,"-B",str(CACHE/"run_offline_tests.py"),str(REPORT/"unittest_final_result.json")]
env=dict(os.environ,PYTHONIOENCODING="utf-8")
native=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=150,env=env)
with (REPORT/"unittest_final.log").open("xb") as out:out.write(native.stdout);out.write(native.stderr)
tests=entry.strict_json((REPORT/"unittest_final_result.json").read_text(encoding="utf-8"))
assert tests["native_exit_code"]==native.returncode and source_sha=={rel(file):sha(file) for file in sources}
archive=REPORT/"mock_case_evidence";assert not archive.exists();archive.mkdir();mapping=[]
for index,directory in enumerate(sorted(set(TEMP.iterdir())-before)):
    assert directory.parent==TEMP and directory.is_dir()
    if directory.name.startswith("unit_lifecycle_"):
        run=directory/"report/evidence/S2B-T19"
        for run_index,folder in enumerate(sorted(run.iterdir())):
            if not folder.is_dir():continue
            targetdir=archive/("case_%03d_%02d"%(index,run_index));targetdir.mkdir()
            for file in sorted(folder.iterdir()):
                if file.name=="input_config.json":continue
                target=targetdir/file.name;copy(file,target)
                mapping.append({"source":str(file),"archive":rel(target),"sha256":sha(file),"bytes":file.stat().st_size})
    elif directory.name.startswith("unit_preflight_"):
        file=directory/"preflight_calls.jsonl"
        if file.is_file():
            target=archive/("preflight_%03d.jsonl"%index);copy(file,target)
            mapping.append({"source":str(file),"archive":rel(target),"sha256":sha(file),"bytes":file.stat().st_size})
assert all(sha(ROOT/path)==digest for path,digest in old_raw.items())
save(REPORT/"mock_archive_mapping.json",{"hardware_execution":"NOT_RUN","entries":mapping,"old_T19_run_raw_unchanged":old_raw,"unit_receipts":"schema fixture留隔离tmp，不生成真实兼容审批原件。"})
dependencies=[ROOT/file for file in ("verification/s2b_board_jtag.py","verification/s2b_board_transport.py","verification/check_s2b_inference_platform.py","verification/check_s2b_ps_smoke_layout.py","verification/check_stage_delivery.py","verification/test_s2b_board_jtag.py","src/s2b_control_csr.sv")]
baseline=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode("ascii").strip()
save(REPORT/"offline_result.json",{"status":"PASS_OFFLINE_R1_FIX_ONLY" if native.returncode==0 else "FAIL_OFFLINE_TESTS","source_commit":baseline,"source_sha256":source_sha,"dependencies":{rel(file):sha(file) for file in dependencies},"command":command,"native_exit_code":native.returncode,"tests":tests,"started_at_utc8":started_at,"finished_at_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"elapsed_seconds":time.monotonic()-started,"full_suite_runs_this_fix":3,"single_test_replay_runs_this_fix":1,"hardware_execution":"NOT_RUN","vitis_started_here":False,"sdk_or_serial_import_here":False,"formal_compat_receipt":"NOT_AVAILABLE_NOT_RUN","cold_lifecycle_proven":False,"limits":["R1三个阻断修复仅G1；AST会话/TCF/串口为mock，原UART为mock实际协议字节，不是实物。","root提供的真实Python3.13/Vitis2026.1/pyserial3.5 import-only原件仅辅助覆盖来源，不是本脚本连接/部署通过。","首次闭包大小写误识别失败和第二轮并行HEAD变化期间预期分支记录缺失均保留；单项重放0，本次新增源漂移专门回归。","首次T19旧清单checker SHA由于S2并行修改漂移，旧原件不改；本清单绑定停写后当前依赖字节。","最终实际bit/implemented XSA/真实兼容性独审和官方cold basis未绑定；hardware NOT_RUN，不能称G3或visibilityPASS。","仅测试单进程峰值可得，全进程树峰值未测；底层DLL/OS/标准库无逐项源码freeze。"]})
old_manifest=entry.strict_json((old/"delivery_manifest_r03.json").read_text(encoding="utf-8"))
interfaces=old_manifest["interfaces"]
for item in interfaces:assert sha(ROOT/item["path"])==item["sha256"]
checks=[{"name":"offline_r1_fix_tests","status":"PASS" if native.returncode==0 else "FAIL","command":" ".join(command),"exit_code":native.returncode},{"name":"source_closure_case_failure_preserved","status":"FAIL","command":"python -B -m unittest verification.test_s2b_visibility_probe -v","exit_code":1,"reason":"首新回归Windows类名/文件大小写识别错误，原日志及两源码保留，已修。"},{"name":"parallel_head_test_failure_preserved","status":"FAIL","command":"python -B run_offline_tests.py unittest_second_result.json","exit_code":1,"reason":"并行ROOT提交发生于suite生命周期，预期checker记录未产生；单项重放0，新回归隔离fixture观察HEAD并另测真实门禁。"},{"name":"hardware_visibility0_probe","status":"NOT_RUN","command":None,"exit_code":None,"reason":"只修候选软件，不连接SDK/串口，不下载，不产生真实compat receipt或cold/visibility批准。"}]
def manifest():
    """绑定本Run全原件，失败包通过包装也不是语义PASS。"""
    files=[]
    for file in sorted(REPORT.rglob("*")):
        if not file.is_file() or file.name=="delivery_manifest.json":continue
        role="source" if file.suffix==".py" else "log" if file.suffix in (".log",".jsonl") else "artifact" if file.suffix in (".bin",".raw") else "result"
        files.append({"path":rel(file),"sha256":sha(file),"role":role})
    for file in sources+dependencies:files.append({"path":rel(file),"sha256":sha(file),"role":"source"})
    for file in (runtime,ROOT/"report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"):files.append({"path":rel(file),"sha256":sha(file),"role":"input"})
    return {"schema_version":1,"stage":"2B","task_id":"S2B-T19","run_id":REPORT.name,"source_commit":baseline,"evidence_dir":rel(REPORT),"interfaces":interfaces,"files":files,"checks":checks,"tool_versions":{"python":sys.version,"sdk":"2026.1实际文件AST/源码闭包，此处无SDK导入","root_import_only":"Python3.13.0/Vitis v2026.1/pyserial3.5，原件另绑定，不代表运行本脚本"},"limitations":entry.strict_json((REPORT/"offline_result.json").read_text(encoding="utf-8"))["limits"]}
save(REPORT/"delivery_manifest_probe.json",manifest())
probe=[]
for mode in ("evidence","inputs"):
    cmd=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(REPORT/"delivery_manifest_probe.json")]
    checked=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30,env=env)
    with (REPORT/(mode+"_probe.log")).open("xb") as out:out.write(checked.stdout);out.write(checked.stderr)
    probe.append({"mode":mode,"native_exit_code":checked.returncode,"command":cmd})
save(REPORT/"packaging_probe_result.json",{"checks":probe,"scope":"机器包装，不建立G2/G3/cold/visibility"})
save(REPORT/"delivery_manifest.json",manifest())
final={}
for mode in ("evidence","inputs"):
    cmd=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(REPORT/"delivery_manifest.json")]
    checked=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30,env=env)
    with (CACHE/(mode+"_final.log")).open("xb") as out:out.write(checked.stdout);out.write(checked.stderr)
    final[mode]=checked.returncode
result={"native_tests":native.returncode,"methods":tests["methods"],"subcases":len(tests["subcases"]),"packaging":final,"source_sha256":source_sha,"manifest_sha256":sha(REPORT/"delivery_manifest.json")}
save(CACHE/"final_status.json",result);print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if native.returncode==0 and final=={"evidence":0,"inputs":2} else 2)
