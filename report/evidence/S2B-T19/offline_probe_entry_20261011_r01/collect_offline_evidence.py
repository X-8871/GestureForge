"""仅归档T19本次轻量测试新证据，不执行SDK/串口/板卡或覆盖旧文件。"""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT=Path(__file__).absolute().parents[4]
CACHE=Path(__file__).absolute().parent
TEMP=ROOT/"tmp/2B/S2B-T19"
REPORT=ROOT/"report/evidence/S2B-T19/offline_probe_entry_20261011_r01"
SOURCE=[ROOT/"vitis/run_s2b_visibility_probe.py",ROOT/"verification/test_s2b_visibility_probe.py"]
assert TEMP.is_dir() and CACHE.is_dir() and REPORT.is_dir()

def sha(file):
    """流式绑定现存原字节。"""
    digest=hashlib.sha256()
    with file.open("rb") as src:
        for block in iter(lambda:src.read(1048576),b""):digest.update(block)
    return digest.hexdigest()

def save(file,data):
    """新名称独占创建UTF8原件。"""
    assert file.parent.is_dir() and not file.exists()
    with file.open("x",encoding="utf-8",newline="\n") as out:json.dump(data,out,ensure_ascii=False,indent=2);out.write("\n")

def copy(source,target):
    """仅复制本任务小日志与源码，复核字节一致。"""
    assert source.is_file() and target.parent.is_dir() and not target.exists()
    with target.open("xb") as out:out.write(source.read_bytes())
    assert sha(source)==sha(target)

def relative(file):
    """正式清单使用仓库相对路径，原件记录保留绝对路径。"""
    return file.relative_to(ROOT).as_posix()

baseline=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode("ascii").strip()
start=time.monotonic();before={str(x):sha(x) for x in SOURCE}
snapshot=REPORT/"source_snapshot";assert not snapshot.exists();snapshot.mkdir()
for file in SOURCE:copy(file,snapshot/file.name)
for name in ("run_offline_tests.py","collect_offline_evidence.py"):copy(CACHE/name,REPORT/name)
prior=set(TEMP.iterdir())
command=[sys.executable,"-B",str(CACHE/"run_offline_tests.py"),str(REPORT/"unittest_final_result.json")]
env=dict(os.environ,PYTHONIOENCODING="utf-8")
native=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60,env=env)
log=REPORT/"unittest_final.log"
with log.open("xb") as out:out.write(native.stdout);out.write(native.stderr)
result=json.loads((REPORT/"unittest_final_result.json").read_text(encoding="utf-8"))
assert native.returncode==result["native_exit_code"]
assert before=={str(x):sha(x) for x in SOURCE}
new=sorted(set(TEMP.iterdir())-prior)
archive=REPORT/"mock_case_evidence";assert not archive.exists();archive.mkdir()
mapping=[]
for index,directory in enumerate(new):
    assert directory.is_dir() and directory.parent==TEMP
    if directory.name.startswith("unit_lifecycle_"):
        run=directory/"report/evidence/S2B-T19/run"
        if not run.is_dir():continue
        dest=archive/("case_%03d"%index);dest.mkdir()
        for file in sorted(run.iterdir()):
            assert file.is_file()
            if file.name=="input_config.json":continue
            target=dest/file.name;copy(file,target)
            mapping.append({"source":str(file),"archived":relative(target),"sha256":sha(file),"bytes":file.stat().st_size,"scope":"OFFLINE_MOCK_NOT_HARDWARE"})
    elif directory.name.startswith("unit_preflight_"):
        file=directory/"preflight_calls.jsonl"
        if file.is_file():
            target=archive/("preflight_%03d.jsonl"%index);copy(file,target)
            mapping.append({"source":str(file),"archived":relative(target),"sha256":sha(file),"bytes":file.stat().st_size,"scope":"UNIT_SCHEMA_FIXTURE_NOT_APPROVAL"})
save(REPORT/"mock_archive_mapping.json",{"hardware_execution":"NOT_RUN","entries":mapping,"preserved_tmp_directories":[str(x) for x in new],"fixture_receipts":"仅隔离tmp中schema测试fixture，不是正式独审批准。"})
failure=REPORT/"failure_r01"
save(failure/"failure_classification.json",{"native_test_exit_code":1,"methods":9,"failures":1,"errors":6,"category":"TEST_HARNESS_ASSERTIONS","reason":"初版测试引用不同模块实例的异常类型，并错误要求未知JTAG链触核；测试修复后重新执行。","log_sha256":sha(failure/"unittest.log"),"source_sha256":{x.name:sha(x) for x in failure.glob("*.py")},"hardware_execution":"NOT_RUN"})
serial=Path(sys.executable).parent/"Lib/site-packages/serial"
assert serial.is_dir()
pyserial=[{"path":str(x),"sha256":sha(x),"bytes":x.stat().st_size} for x in sorted(serial.rglob("*.py"))]
sdk=Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb")
sources=[ROOT/x for x in ("verification/s2b_board_jtag.py","verification/s2b_board_transport.py","verification/check_s2b_inference_platform.py","verification/check_s2b_ps_smoke_layout.py","verification/check_stage_delivery.py","verification/test_s2b_board_jtag.py","src/s2b_control_csr.sv")]
bound={relative(x):sha(x) for x in sources}
record={"status":"PASS_OFFLINE_VISIBILITY_ENTRY_ONLY" if native.returncode==0 else "FAIL_OFFLINE_TESTS","source_commit":baseline,"source_sha256":before,"dependency_sha256":bound,"command":command,"native_exit_code":native.returncode,"tests":result,"full_suite_invocations":5,"previous_attempts":"初版原失败一次及保留日志复跑一次；r02/r03各一次；本次最终一次。","started_at_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"elapsed_seconds":time.monotonic()-start,"hardware_execution":"NOT_RUN","vitis_or_vivado_started":False,"sdk_runtime_import":"NOT_RUN","pyserial_runtime_import":"NOT_RUN","pyserial_available_version":"3.5","pyserial_files":pyserial,"sdk_sources":[{"path":str(sdk/name),"sha256":sha(sdk/name)} for name in ("__init__.py","target.py","session.py","xsdb_debug_session.py")],"actual_t15_build_details":{"path":relative(ROOT/"report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"),"sha256":sha(ROOT/"report/evidence/S2B-T15/full_build_20261011_r01/build_details.json")},"formal_compatibility_receipt":"NOT_AVAILABLE_NOT_RUN","official_cold_basis":"ROOT_SELECTION_PENDING_NOT_RUN","peak_process_tree_memory_bytes":None,"limits":["全部生命周期数据来自mock SDK/串口，原UART文件是mock真实协议字节，不能称硬件观测。","schema测试中的PASS/role只是UNIT fixture；独审来源由root固定真实原件。","Vitis2026.1解释器载入pyserial3.5尚未执行；只读确认本机purePython文件存在与完整SHA。","新implemented XSA/bit/兼容性独审尚未绑定；入口不能据本测试执行硬件。","入口始终cold_lifecycle_proven=false；不发布visibilityPASS；成功亦停止CPU0。","单进程测试峰值可得，全进程树峰值未测；无硬件时间或速度结论。"]}
save(REPORT/"offline_result.json",record)
save(REPORT/"config_contract.json",{"schema_version":1,"candidate_scope":"visibility0_cache_probe_only","config_keys":["schema_version","source_commit","run_dir","build_details","bindings","compat_review","cold_basis","owned_hw_server_identity","uart_identity","cpu_seed","dap_seed","response_timeout_seconds","pyserial_files"],"binding_keys":["init_elf","app_elf","xsa","bit","csr_source","interface","sdk_target","tool_source","elf_parser","delivery_parser","transport_source","entry_source","platform_checker","sdk_init","pyserial_init"],"binding_shape":{"path":"root必须选定精确绝对路径","sha256":"完整原字节SHA256"},"compatibility":"采用root冻结flat s2b-runtime-platform-compatibility/1.0.0；compiled_xsa为T15实际编译XSA，implemented_xsa为新实现XSA，不得混同。","invocation":"Vitis2026.1 vitis.bat -s vitis/run_s2b_visibility_probe.py；root显式设置S2B_VISIBILITY_PROBE_CONFIG为绝对JSON路径。--help/导入零SDK串口。","deployment_ready":False,"acceptance":"程序保存原观察/API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING；不创建独审来源、不证明cold/visibility。"})
old=json.loads((ROOT/"report/evidence/S2B-T17/full_synthesis_20261011_r01/delivery_manifest.json").read_text(encoding="utf-8"))
interfaces=old["interfaces"]
for item in interfaces:assert sha(ROOT/item["path"])==item["sha256"]
checks=[{"name":"offline_unittest_native","status":"PASS" if native.returncode==0 else "FAIL","command":" ".join(command),"exit_code":native.returncode},{"name":"initial_test_harness_failure_preserved","status":"FAIL","command":"python -m unittest verification.test_s2b_visibility_probe -v","exit_code":1,"reason":"原测试包装缺陷已修复；失败原件与源码保留，不是硬件FAIL。"},{"name":"real_visibility0_execution","status":"NOT_RUN","command":None,"exit_code":None,"reason":"本任务禁止硬件执行；实际兼容receipt/bit/cold依据等待root与独审。"}]
def manifest():
    """包装所有新证据，候选接口仍未冻结。"""
    files=[]
    for file in sorted(REPORT.rglob("*")):
        if not file.is_file() or file.name=="delivery_manifest.json":continue
        role="source" if file.suffix==".py" else "log" if file.suffix in (".log",".jsonl") else "artifact" if file.suffix==".bin" else "result"
        files.append({"path":relative(file),"sha256":sha(file),"role":role})
    for file in SOURCE+sources:files.append({"path":relative(file),"sha256":sha(file),"role":"source"})
    file=ROOT/record["actual_t15_build_details"]["path"];files.append({"path":relative(file),"sha256":sha(file),"role":"input"})
    return {"schema_version":1,"stage":"2B","task_id":"S2B-T19","run_id":REPORT.name,"source_commit":baseline,"evidence_dir":relative(REPORT),"interfaces":interfaces,"files":files,"checks":checks,"tool_versions":{"python":sys.version,"sdk":"2026.1来源文件只读绑定，SDK未导入","pyserial":"3.5文件存在，串口未导入"},"limitations":record["limits"]}
save(REPORT/"delivery_manifest_probe.json",manifest())
package=[]
for mode in ("evidence","inputs"):
    cmd=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(REPORT/"delivery_manifest_probe.json")]
    test=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30,env=env)
    with (REPORT/(mode+"_probe.log")).open("xb") as out:out.write(test.stdout);out.write(test.stderr)
    package.append({"mode":mode,"command":cmd,"native_exit_code":test.returncode})
save(REPORT/"packaging_probe_result.json",{"status":"PACKAGING_ONLY","checks":package,"does_not_establish":"G2/G3/G4/G5、cold或visibilityPASS"})
save(REPORT/"delivery_manifest.json",manifest())
final={}
for mode in ("evidence","inputs"):
    cmd=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(REPORT/"delivery_manifest.json")]
    test=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30,env=env)
    with (CACHE/(mode+"_final.log")).open("xb") as out:out.write(test.stdout);out.write(test.stderr)
    final[mode]=test.returncode
save(CACHE/"final_collection_status.json",{"tests":native.returncode,"packaging":final,"manifest_sha256":sha(REPORT/"delivery_manifest.json"),"source_sha256":before})
print(json.dumps({"tests":native.returncode,"packaging":final,"manifest_sha256":sha(REPORT/"delivery_manifest.json"),"methods":result["methods"],"subcases":len(result["subcases"]),"source_sha256":before},ensure_ascii=False))
raise SystemExit(0 if native.returncode==0 and final["evidence"]==0 and final["inputs"]==2 else 2)
