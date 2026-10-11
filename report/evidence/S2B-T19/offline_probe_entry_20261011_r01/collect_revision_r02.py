"""保留全部r01原件，补齐部分connect失败的disconnect默认通道清理证据。"""
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
REPORT=ROOT/"report/evidence/S2B-T19/offline_probe_entry_20261011_r01"
TEMP=ROOT/"tmp/2B/S2B-T19"
assert REPORT.is_dir() and TEMP.is_dir()

def sha(file):
    """流式原字节SHA。"""
    h=hashlib.sha256()
    with file.open("rb") as src:
        for block in iter(lambda:src.read(1048576),b""):h.update(block)
    return h.hexdigest()

def save(file,data):
    """只创建新文件，UTF8/LF。"""
    assert file.parent.is_dir() and not file.exists()
    with file.open("x",encoding="utf-8",newline="\n") as out:json.dump(data,out,ensure_ascii=False,indent=2);out.write("\n")

def copy(source,target):
    """只归档新单元原件，不复制正式审批fixture或大型资产。"""
    assert source.is_file() and target.parent.is_dir() and not target.exists()
    with target.open("xb") as out:out.write(source.read_bytes())
    assert sha(source)==sha(target)

def rel(path):
    """清单精确仓库相对路径。"""
    return path.relative_to(ROOT).as_posix()

started_at=datetime.now(timezone(timedelta(hours=8))).isoformat();started=time.monotonic()
old_files={rel(x):sha(x) for x in REPORT.rglob("*") if x.is_file()}
snapshot=REPORT/"source_snapshot_r02";assert not snapshot.exists();snapshot.mkdir()
sources=[ROOT/"vitis/run_s2b_visibility_probe.py",ROOT/"verification/test_s2b_visibility_probe.py"]
source_sha={rel(x):sha(x) for x in sources}
for source in sources:copy(source,snapshot/source.name)
copy(Path(__file__),REPORT/"collect_revision_r02.py")
prior=set(TEMP.iterdir())
command=[sys.executable,"-B",str(CACHE/"run_offline_tests.py"),str(REPORT/"unittest_final_result_r02.json")]
env=dict(os.environ,PYTHONIOENCODING="utf-8")
native=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60,env=env)
with (REPORT/"unittest_final_r02.log").open("xb") as out:out.write(native.stdout);out.write(native.stderr)
tests=json.loads((REPORT/"unittest_final_result_r02.json").read_text(encoding="utf-8"))
assert native.returncode==tests["native_exit_code"] and source_sha=={rel(x):sha(x) for x in sources}
archive=REPORT/"mock_case_evidence_r02";assert not archive.exists();archive.mkdir()
mapping=[]
for index,directory in enumerate(sorted(set(TEMP.iterdir())-prior)):
    assert directory.parent==TEMP and directory.is_dir()
    if directory.name.startswith("unit_lifecycle_"):
        run=directory/"report/evidence/S2B-T19/run"
        if not run.is_dir():continue
        dest=archive/("case_%03d"%index);dest.mkdir()
        for source in sorted(run.iterdir()):
            if source.name=="input_config.json":continue
            target=dest/source.name;copy(source,target)
            mapping.append({"source":str(source),"archived":rel(target),"sha256":sha(source),"bytes":source.stat().st_size})
    elif directory.name.startswith("unit_preflight_"):
        source=directory/"preflight_calls.jsonl"
        if source.is_file():
            target=archive/("preflight_%03d.jsonl"%index);copy(source,target)
            mapping.append({"source":str(source),"archived":rel(target),"sha256":sha(source),"bytes":source.stat().st_size})
assert all(sha(ROOT/path)==digest for path,digest in old_files.items())
save(REPORT/"mock_archive_mapping_r02.json",{"hardware_execution":"NOT_RUN","entries":mapping,"original_files_unchanged":old_files})
baseline=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode("ascii").strip()
save(REPORT/"offline_result_r02.json",{"status":"PASS_OFFLINE_VISIBILITY_ENTRY_ONLY" if native.returncode==0 else "FAIL_OFFLINE_TESTS","source_commit":baseline,"source_sha256":source_sha,"command":command,"native_exit_code":native.returncode,"tests":tests,"started_at_utc8":started_at,"finished_at_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"elapsed_seconds":time.monotonic()-started,"full_suite_invocations":6,"hardware_execution":"NOT_RUN","sdk_runtime_import":"NOT_RUN","serial_runtime_import":"NOT_RUN","change":"session已创建但connect抛异常时，官方disconnect(chan=None)尝试清理该自有会话默认通道；仍不回收root server。","sdk_api_basis":{"path":r"D:\Xilinx\2026.1\Vitis\cli\xsdb\session.py","sha256":sha(Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\session.py")),"lines":"disconnect定义645，chan=None采用当前通道；闭合自身channel，不kill server。"},"r01_timestamp_note":"offline_result.json的started_at_utc8是在汇总写入时采样，应作为汇总写入时间；本r02单独记录真实开始/结束。","formal_compatibility_receipt":"NOT_AVAILABLE_NOT_RUN","official_cold_basis":"ROOT_SELECTION_PENDING_NOT_RUN","peak_process_tree_memory_bytes":None,"acceptance":"仅G1候选软件离线，不证明G2/G3/visibility/cold。"})
old=json.loads((REPORT/"delivery_manifest.json").read_text(encoding="utf-8"))
manifest={key:old[key] for key in ("schema_version","stage","task_id","run_id","evidence_dir","interfaces","tool_versions","limitations")}
manifest["source_commit"]=baseline
manifest["checks"]=old["checks"]
manifest["checks"][0]={"name":"offline_unittest_native_r02","status":"PASS" if native.returncode==0 else "FAIL","command":" ".join(command),"exit_code":native.returncode}
manifest["files"]=[row for row in old["files"] if not row["path"].startswith(rel(REPORT)+"/")]
for row in manifest["files"]:row["sha256"]=sha(ROOT/row["path"])
for file in sorted(REPORT.rglob("*")):
    if file.is_file():
        role="source" if file.suffix==".py" else "log" if file.suffix in (".log",".jsonl") else "artifact" if file.suffix==".bin" else "result"
        manifest["files"].append({"path":rel(file),"sha256":sha(file),"role":role})
save(REPORT/"delivery_manifest_r02.json",manifest)
package={}
for mode in ("evidence","inputs"):
    cmd=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(REPORT/"delivery_manifest_r02.json")]
    check=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30,env=env)
    with (CACHE/(mode+"_final_r02.log")).open("xb") as out:out.write(check.stdout);out.write(check.stderr)
    package[mode]=check.returncode
final={"tests":native.returncode,"methods":tests["methods"],"subcases":len(tests["subcases"]),"packaging":package,"manifest_sha256":sha(REPORT/"delivery_manifest_r02.json"),"source_sha256":source_sha}
save(CACHE/"final_collection_status_r02.json",final);print(json.dumps(final,ensure_ascii=False))
raise SystemExit(0 if native.returncode==0 and package=={"evidence":0,"inputs":2} else 2)
