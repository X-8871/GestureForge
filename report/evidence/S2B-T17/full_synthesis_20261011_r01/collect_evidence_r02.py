"""归档单次原生综合证据；只新增文件，不操作Vivado或修改原件。"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import time

ROOT=Path(__file__).absolute().parents[4]
CACHE=Path(__file__).absolute().parent
RUN=ROOT/"report/evidence/S2B-T17/full_synthesis_20261011_r01"
BASE="f260880aa68c3aeb45405bb2dcd92d0b32bb9b16"

def exact(path,kind):
    """逐个确认精确路径和类型，不猜相邻文件名。"""
    assert path.exists() and (path.is_dir() if kind=="directory" else path.is_file()),str(path)
    return path.absolute()

def digest(path):
    """流式哈希避免大文件占用内存。"""
    h=hashlib.sha256()
    with exact(path,"file").open("rb") as src:
        for part in iter(lambda:src.read(1048576),b""):h.update(part)
    return h.hexdigest()

def save(path,data):
    """新文件使用UTF8，遇到已有文件直接失败。"""
    exact(path.parent,"directory");assert not path.exists(),str(path)
    with path.open("x",encoding="utf-8",newline="\n") as out:json.dump(data,out,ensure_ascii=False,indent=2);out.write("\n")

def copy(source,target):
    """独占创建副本并逐字节绑定来源。"""
    exact(source,"file");exact(target.parent,"directory");assert not target.exists(),str(target)
    with source.open("rb") as src,target.open("xb") as dst:
        for part in iter(lambda:src.read(1048576),b""):dst.write(part)
    assert digest(source)==digest(target)
    return {"original_path":str(source),"saved_path":target.relative_to(ROOT).as_posix(),"sha256":digest(target),"bytes":target.stat().st_size}

exact(ROOT,"directory");exact(CACHE,"directory");exact(RUN,"directory")
started=time.monotonic()
original={p.relative_to(ROOT).as_posix():digest(p) for p in RUN.rglob("*") if p.is_file()}
save(CACHE/"original_inventory_r02.json",original)
result={"schema_version":1,"status":"FAIL_COLLECTION","source_commit":BASE,"hardware_execution":"NOT_RUN","post_route":"NOT_RUN","command":sys.argv,"peak_process_tree_memory_bytes":None}
try:
    before=json.loads(exact(RUN/"source_before.json","file").read_text(encoding="utf-8"))
    assert before["source_commit"]==BASE and len(before["source_files"])==24
    subprocess.run(["git","cat-file","-e",BASE+"^{commit}"],cwd=ROOT,check=True)
    comparisons=[]
    for row in before["source_files"]:
        path=exact(ROOT/row["snapshot"],"file")
        git=subprocess.run(["git","show",BASE+":"+row["path"]],cwd=ROOT,capture_output=True,check=True)
        git_sha=hashlib.sha256(git.stdout).hexdigest();raw_sha=digest(path)
        raw=path.read_bytes()
        comparisons.append({"source_path":row["path"],"snapshot":row["snapshot"],"declared_sha256":row["sha256"],"snapshot_sha256":raw_sha,
                            "git_blob_sha256":git_sha,"git_blob_oid":subprocess.check_output(["git","rev-parse",BASE+":"+row["path"]],cwd=ROOT).decode().strip(),
                            "bytes":path.stat().st_size,"git_bytes":len(git.stdout),"declared_match":raw_sha==row["sha256"],"git_raw_byte_match":raw_sha==git_sha,
                            "snapshot_crlf_count":raw.count(b"\r\n"),"git_crlf_count":git.stdout.count(b"\r\n"),
                            "snapshot_crlf_to_lf_equals_git":raw.replace(b"\r\n",b"\n")==git.stdout,
                            "git_lf_to_crlf_equals_snapshot":git.stdout.replace(b"\n",b"\r\n")==raw})
    save(RUN/"source_git_comparison_r02.json",{"schema_version":1,"source_commit":BASE,"status":"VERIFIED_RAW_SNAPSHOT_WITH_GIT_CHECKOUT_EOL_DIFFERENCES" if all(x["declared_match"] and (x["git_raw_byte_match"] or x["git_lf_to_crlf_equals_snapshot"]) for x in comparisons) else "FAIL_SOURCE_PROVENANCE","files":comparisons,
                                           "current_head_observed":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode().strip(),"current_worktree_source_used":False})
    assert all(x["declared_match"] and (x["git_raw_byte_match"] or x["git_lf_to_crlf_equals_snapshot"]) for x in comparisons)
    native_parent=exact(ROOT/"tmp/2B/S2B-T13/i5/s2b_inference_candidate.runs","directory")
    saved_parent=RUN/"native_jobs";assert not saved_parent.exists();saved_parent.mkdir()
    mappings=[];jobs=[];dcps=[]
    names=["s2b_inference_infer_0_synth_1","s2b_inference_ps7_0_synth_1","s2b_inference_axi_gp0_lite_0_synth_1","s2b_inference_rst_fclk0_0_synth_1","synth_1"]
    for name in names:
        directory=exact(native_parent/name,"directory");saved=saved_parent/name;assert not saved.exists();saved.mkdir()
        logfile=exact(directory/"runme.log","file");text=logfile.read_text(encoding="utf-8")
        assert "synth_design completed successfully" in text and "0 Critical Warnings and 0 Errors encountered." in text
        assert (directory/".vivado.end.rst").is_file() and not (directory/".vivado.error.rst").exists()
        for source in sorted(directory.iterdir()):
            if source.is_file() and (source.suffix in {".log",".rpt",".tcl"} or source.name in {".vivado.begin.rst",".vivado.end.rst","__synthesis_is_complete__"}):mappings.append(copy(source,saved/source.name))
            if source.is_file() and source.suffix==".dcp":dcps.append({"path":str(source),"sha256":digest(source),"bytes":source.stat().st_size,"copied":False,"keep_reason":"原ignored综合恢复诊断缓存；不作为长期冻结依赖，Git源及原生Tcl可重建。"})
        metric=re.search(r"synth_design: Time \(s\): cpu = (\d+):(\d+):(\d+) ; elapsed = (\d+):(\d+):(\d+) .*?peak = ([\d.]+)",text)
        assert metric
        jobs.append({"run":name,"native_completion":"PASS_LOG_AND_DONE_MARKER","raw_process_exit_code":None,"raw_process_exit_reason":"本整理未观察已退出子进程exit；保留原日志/完成marker及MCP wait实际code0。",
                     "elapsed_synth_design_seconds":sum(int(metric[i])*factor for i,factor in [(4,3600),(5,60),(6,1)]),"reported_single_process_peak_mb":float(metric[7]),
                     "reported_process_id":int(re.search(r"Process ID\s*:\s*(\d+)",text)[1]),"native_command_header":text.split("with args ",1)[1].splitlines()[0].strip()})
    save(RUN/"native_archive_mapping.json",{"files":mappings,"jobs":jobs,"dcp_references":dcps,"process_tree_peak_bytes":None,"queue_elapsed_seconds":None,"queue_elapsed_reason":"约319秒为总控报告；未构造精确聚合耗时，不相加不同job耗时/内存。"})
    raw=exact(RUN/"root_mcp_calls_and_history.json","file");calls=json.loads(raw.read_text(encoding="utf-8"))
    history=json.loads(calls["history"]["content"][0]["text"])["history"]
    assert len(calls["calls"])==7 and len(history)==7
    wait_client=[x for x in calls["calls"] if x["command"]=="wait_on_run synth_1"]
    wait_native=[x for x in history if x["command"]=="wait_on_run synth_1"]
    assert len(wait_client)==1 and wait_client[0]["result"]["isError"] is True and "300s" in str(wait_client[0])
    assert len(wait_native)==1 and wait_native[0]["code"]==0 and wait_native[0]["elapsed"]==311.587
    save(RUN/"mcp_native_classification.json",{"raw_path":raw.relative_to(ROOT).as_posix(),"raw_sha256":digest(raw),"calls":7,
                                            "wait_client_status":"FAIL_TIMEOUT_300S","wait_native_code":0,"wait_native_elapsed_seconds":311.587,
                                            "history_summary":[{k:x.get(k) for k in ["id","command","code","elapsed","timestamp"]} for x in history],
                                            "root_session_reported_cumulative_peak_mb":2453.121,"process_tree_peak_bytes":None,
                                            "limitations":["保留客户端失败，不把native成功改写成客户端SUCCESS。","根会话2453.121MB为累计报表峰，不是本次全进程树峰。","Python quoting SyntaxError、Windows206命令长及chunk截断由总控报告；此整理不重跑或改写其旧失败记录。"]})
    copy(exact(CACHE/"classify_sta.py","file"),RUN/"classify_sta.py")
    classification=[sys.executable,str(RUN/"classify_sta.py"),str(RUN),str(RUN/"sta_classification.json")]
    sta=subprocess.run(classification,cwd=ROOT,capture_output=True)
    with (RUN/"sta_classification.log").open("xb") as out:out.write(sta.stdout+sta.stderr)
    parsed=json.loads((RUN/"sta_classification.json").read_text(encoding="utf-8"))
    assert sta.returncode==2 and parsed["status"]=="FAIL_TIMING"
    assert parsed["timing"]["wns_ns"]==-76.685 and parsed["timing"]["tns_ns"]==-117866.523
    assert parsed["timing"]["setup_failing_endpoints"]==2639 and parsed["worst_setup_path"]["logic_levels"]==239
    assert parsed["clock"]["frequency_mhz"]==50 and parsed["resources"]=={"lut":42820,"ff":4003,"bram_tiles":32,"dsp":186}
    assert all(x==0 for x in parsed["check_timing"].values())
    assert parsed["timing"]["ths_ns"]==0 and parsed["timing"]["hold_failing_endpoints"]==0
    assert all(digest(ROOT/relative)==expected for relative,expected in original.items())
    result.update(status="COLLECTED_FAIL_TIMING",sta_native_exit_code=sta.returncode,sta_command=classification,snapshot_count=24,native_jobs=5,
                  original_files_unchanged=True,original_inventory_sha256=digest(CACHE/"original_inventory_r02.json"),
                  limitations=["综合完成但50MHz综合STA失败，不执行实现/postroute/实板。","不消费正在修改的S1工作树源，不将最新HEAD称为原综合基线。","DCP仅记录ignored路径和SHA，不复制或作为长期冻结依赖。","同重型作业worker身份由总控观测，本整理不推断全进程树峰。"])
except BaseException as error:
    result["error"]=repr(error)
    raise
finally:
    result["elapsed_seconds"]=time.monotonic()-started
    result["collection_native_exit_code"]=0 if result["status"]=="COLLECTED_FAIL_TIMING" else 1
    save(RUN/"collection_result_r02.json",result)
    print(json.dumps(result,ensure_ascii=False))
sys.exit(result["collection_native_exit_code"])
