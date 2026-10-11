"""T19-R3新Run包装；严格保留既有失败，无硬件操作。"""
from pathlib import Path
import sys
import json
import hashlib
import subprocess
import os
from datetime import datetime,timezone,timedelta

ROOT=Path(__file__).absolute().parents[4];CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01"
assert REPORT.is_dir() and CACHE.is_dir()
def sha(file):
    """流式原字节绑定。"""
    h=hashlib.sha256()
    with file.open("rb") as src:
        for block in iter(lambda:src.read(1048576),b""):h.update(block)
    return h.hexdigest()
def save(file,value):
    """独占创建UTF8文件，不覆盖旧Run。"""
    assert file.parent.is_dir() and not file.exists()
    with file.open("x",encoding="utf-8",newline="\n") as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write("\n")
def copy(file,target):
    """只归档小原件并校验字节。"""
    assert file.is_file() and target.parent.is_dir() and not target.exists()
    with target.open("xb") as out:out.write(file.read_bytes())
    assert sha(file)==sha(target)
def rel(file):return file.relative_to(ROOT).as_posix()

sources=[ROOT/"vitis/run_s2b_visibility_probe.py",ROOT/"verification/test_s2b_visibility_probe.py"]
tests=json.loads((REPORT/"unittest_final_result.json").read_text(encoding="utf-8"))
native=json.loads((REPORT/"unittest_final_native.json").read_text(encoding="utf-8"))
actual=json.loads((REPORT/"actual_runtime_source_gate.json").read_text(encoding="utf-8"))
launcher=json.loads((REPORT/"runtime_launcher_result.json").read_text(encoding="utf-8"))
assert native["source_unchanged"] and native["source_before"]=={rel(p):sha(p) for p in sources}
for p in sources:assert sha(REPORT/"source_snapshot"/p.name)==sha(p)
for p in (Path(__file__),CACHE/"runtime_source_gate.py",CACHE/"run_offline_tests.py"):copy(p,REPORT/p.name)
receipt=ROOT/"tmp/2B/S2B-T19/independent_probe_review_20261011_r02/review_receipt.json"
assert sha(receipt)=="b012a80117dce51ae9d33c751a3ea34acce993a223de4a6ea67d46a03b498a03"
assert sha(receipt)==sha(REPORT/"upstream_r02_review_receipt.json")
old_runs=[]
for run_name in ("offline_probe_entry_20261011_r01","offline_probe_fix_20261011_r01"):
    run=REPORT.parent/run_name;assert run.is_dir()
    files={rel(p):sha(p) for p in run.rglob("*") if p.is_file()}
    for filename in ("delivery_manifest.json","delivery_manifest_r03.json"):
        manifest=run/filename
        if not manifest.is_file():continue
        obj=json.loads(manifest.read_text(encoding="utf-8"))
        for row in obj["files"]:
            if row["path"].startswith(rel(run)+"/"):assert files[row["path"]]==row["sha256"]
    old_runs.append({"run":rel(run),"raw_files":files,"old_manifest_binding_to_mutated_project_sources":"不重写旧清单；仅复核其Run内部原字节，旧声明仍为历史原件。"})
save(REPORT/"old_run_raw_verification.json",{"old_runs":old_runs})
archive=REPORT/"mock_case_evidence";assert not archive.exists();archive.mkdir();mapping=[]
earliest=(REPORT/"source_snapshot").stat().st_ctime
temp=ROOT/"tmp/2B/S2B-T19"
for index,folder in enumerate(sorted(temp.glob("unit_*"))):
    if not folder.is_dir() or folder.stat().st_ctime<earliest:continue
    if folder.name.startswith("unit_lifecycle_"):
        run=folder/"report/evidence/S2B-T19"
        if not run.is_dir():continue
        for number,sub in enumerate(sorted(run.iterdir())):
            if not sub.is_dir():continue
            target=archive/("case_%03d_%02d"%(index,number));target.mkdir()
            for file in sorted(sub.iterdir()):
                if not file.is_file() or file.name=="input_config.json":continue
                copy(file,target/file.name);mapping.append({"source":str(file),"archive":rel(target/file.name),"sha256":sha(file)})
    elif folder.name.startswith("unit_preflight_"):
        file=folder/"preflight_calls.jsonl"
        if file.is_file():
            target=archive/("preflight_%03d.jsonl"%index);copy(file,target)
            mapping.append({"source":str(file),"archive":rel(target),"sha256":sha(file)})
save(REPORT/"mock_archive_mapping.json",{"hardware_execution":"NOT_RUN","mock_receipts":"仅隔离tmp的fixture，不是真实兼容批准","entries":mapping})
baseline=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode("ascii").strip()
dependencies=[ROOT/p for p in ("verification/s2b_board_jtag.py","verification/s2b_board_transport.py","verification/check_s2b_inference_platform.py","verification/check_s2b_ps_smoke_layout.py","verification/check_stage_delivery.py","verification/test_s2b_board_jtag.py","src/s2b_control_csr.sv")]
limitations=["只有R3 G1，独立R3审查、完整preflight真实产物审批、部署及G3/G4/G5未完成。","正式config仍14键/sdk_files192文件和两不同physical路径；sdk_gate_only_config为纯导入专用证据，不能传入run(config)作部署。","纯导入实际执行生产共享source helper及_runtime，不创建任何真实SDK Session/connect/Serialopen/CPU/reset/download。","原生模块官方vivado共享对象的metadata仅精确例外；其他模块来源门禁保持，两实际已加载pyd映像路径/SHA各自校验。","官方SDK源/直接Python扩展模块绑定；OS、标准库和native映像的其他依赖DLL不声称全闭包冻结。","Vitis外层码和inner状态分记，只有inner实际PASS可说明SDK_GATE_ONLY通过，不能推出cold/cache/compat PASS。","首全量回归中的本代理并行source edit造成SHA失败、捕获异常限定名错误与初错误方法调用均保留，最终源码停写后回归通过。","可测仅单进程峰值，全进程树峰值未测；未更改旧证据/STATE/profile/checker，也未提交。"]
save(REPORT/"config_contract.json",{"schema_version":1,"candidate_version":"s2b-visibility-probe-config/0.2.1","formal_key_count":14,"sdk_module_count":192,"new_formal_keys":[],"sdk_gate_only_json":"本Run真实JSON原字节经strict_json读取；生产verify_sdk_files及verify_serial_files共同用于_preflight和_runtime，没有mock源码映射或config绕门禁开关。","native_rule":"两个module key必须同对象/name vivado，metadata精确HSI ExtensionFileLoader；GetModuleHandleW/GetModuleFileNameW当前进程不同映像精确路径及physical SHA；不改sdk_files的两个不同路径。","class_rule":"Session/Target定义module/name/qualname准确，dispatch.Session/session.Target别名一致，原methods code和receiver gate保留。","full_preflight":"NOT_RUN_NO_FORMAL_COMPAT_RECEIPT","deployment_ready":False})
save(REPORT/"offline_result.json",{"status":"PASS_R3_OFFLINE_AND_ACTUAL_SOURCE_GATE_ONLY","source_commit":baseline,"source_sha256":{rel(p):sha(p) for p in sources},"dependency_sha256":{rel(p):sha(p) for p in dependencies},"offline_native_exit_code":native["native_exit_code"],"methods":tests["methods"],"subcases":len(tests["subcases"]),"offline_metrics":{key:tests[key] for key in ("elapsed_seconds","single_process_peak_working_set_bytes","peak_process_tree_memory_bytes")},"sdk_outer_exit_code":launcher["outer_exit_code"],"sdk_inner_exit_code":actual["inner_exit_code"],"sdk_status":actual["status"],"full_suite_runs":2,"targeted_boundary_replay_runs":1,"wrong_method_invocation_runs":1,"sdk_pure_import_runs":1,"hardware_execution":"NOT_RUN","cold_lifecycle_proven":False,"timestamp_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"limits":limitations})
assert tests["native_exit_code"]==native["native_exit_code"]==0 and launcher["outer_exit_code"]==actual["inner_exit_code"]==0
assert actual["status"]=="PASS_ACTUAL_VITIS_SOURCE_GATE_ONLY"
assert all(row["session_is_none"] for key in ("globals_before","globals_after") for row in actual[key].values())
checks=[{"name":"offline_r3_tests","status":"PASS","command":" ".join(native["command"]),"exit_code":native["native_exit_code"]},{"name":"actual_vitis_source_gate_only","status":"PASS","command":" ".join(launcher["command"]),"exit_code":actual["inner_exit_code"]},{"name":"preliminary_source_edit_failure_preserved","status":"FAIL","command":"python -B -m unittest verification.test_s2b_visibility_probe -v","exit_code":1,"reason":"首开发中测试原生1保留；最终停写版本18methods全部通过。"},{"name":"full_deployment_preflight","status":"NOT_RUN","reason":"正式bit/implemented XSA兼容性独审尚未批准，不制造receipt。"},{"name":"hardware_visibility0_probe","status":"NOT_RUN","reason":"纯导入没有任何Session/连接/串口打开，不发布cold/cache/visibility PASS。"}]
old=json.loads((REPORT.parent/"offline_probe_fix_20261011_r01/delivery_manifest.json").read_text(encoding="utf-8"))
def manifest():
    """整包哈希含所有失败，包装PASS与业务关口分开。"""
    files=[]
    for file in sorted(REPORT.rglob("*")):
        if not file.is_file() or file.name=="delivery_manifest.json":continue
        role="source" if file.suffix==".py" else "log" if file.suffix in (".log",".jsonl") else "artifact" if file.suffix in (".bin",".raw") else "result"
        files.append({"path":rel(file),"sha256":sha(file),"role":role})
    for file in sources+dependencies:files.append({"path":rel(file),"sha256":sha(file),"role":"source"})
    return {"schema_version":1,"stage":"2B","task_id":"S2B-T19","run_id":REPORT.name,"source_commit":baseline,"evidence_dir":rel(REPORT),"interfaces":old["interfaces"],"files":files,"checks":checks,"tool_versions":{"offline_python":sys.version,"actual_vitis_python":actual["python"],"vitis":"2026.1实际纯导入","serial":actual["serial_version"]},"limitations":limitations}
env=dict(os.environ,PYTHONIOENCODING="utf-8")
save(REPORT/"delivery_manifest_probe.json",manifest());probe=[]
for mode in ("evidence","inputs"):
    command=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(REPORT/"delivery_manifest_probe.json")]
    proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30,env=env)
    with (REPORT/(mode+"_probe.log")).open("xb") as out:out.write(proc.stdout);out.write(proc.stderr)
    probe.append({"mode":mode,"native_exit_code":proc.returncode,"command":command})
save(REPORT/"packaging_probe_result.json",probe);save(REPORT/"delivery_manifest.json",manifest());final={}
for mode in ("evidence","inputs"):
    command=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(REPORT/"delivery_manifest.json")]
    proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30,env=env)
    with (CACHE/(mode+"_final.log")).open("xb") as out:out.write(proc.stdout);out.write(proc.stderr)
    final[mode]=proc.returncode
status={"offline":tests["native_exit_code"],"methods":tests["methods"],"subcases":len(tests["subcases"]),"runtime_outer":launcher["outer_exit_code"],"runtime_inner":actual["inner_exit_code"],"source_sha256":{rel(p):sha(p) for p in sources},"manifest_sha256":sha(REPORT/"delivery_manifest.json"),"packaging":final}
save(CACHE/"final_status.json",status);print(json.dumps(status,ensure_ascii=False))
raise SystemExit(0 if final=={"evidence":0,"inputs":2} else 2)
