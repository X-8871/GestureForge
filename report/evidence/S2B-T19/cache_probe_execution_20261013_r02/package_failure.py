"""保存PC输出被异步通知污染的真实失败，不声称映射或下载已运行。"""
from pathlib import Path
import hashlib
import json
import subprocess
root=Path(__file__).absolute().parents[4]
source=Path(__file__).absolute().parent
run=root/"report/evidence/S2B-T19/cache_probe_20261013_r02"
folder=root/"report/evidence/S2B-T19/cache_probe_execution_20261013_r02"
assert source.is_dir() and run.is_dir() and folder.parent.is_dir() and not folder.exists()
folder.mkdir()
def sha(path):
    """实际原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):
    """证据独占创建。"""
    with path.open("x",encoding="utf-8",newline="\n") as out:json.dump(data,out,ensure_ascii=False,indent=2);out.write("\n")
def row(path,role):
    """固定证据保存用途。"""
    return {"path":path.relative_to(root).as_posix(),"sha256":sha(path),"role":role,"keep_reason":"保存实际失败、闭合原件或执行源码；不证明G3/G4/G5。"}
cfg=json.loads((run/"input_config.json").read_text(encoding="utf-8"))
result=json.loads((run/"visibility_probe_result.json").read_text(encoding="utf-8"))
jtag=json.loads((run/"jtag_result.json").read_text(encoding="utf-8"))
assert result["native_exit_code"]==2 and result["status"]=="FAILED" and result["cleanup_errors"]==[]
assert "PC真实输出无法解析" in result["error"] and "debug_memory_map" not in result and "serial_config" not in result
mappings=[]
for path in sorted(source.iterdir()):
    if path.is_file():
        target=folder/path.name;target.write_bytes(path.read_bytes());assert sha(target)==sha(path)
        mappings.append({"source":str(path),"target":str(target),"sha256":sha(path),"transformation":"EXACT_BYTES"})
for name,key in (("vitis/run_s2b_visibility_probe.py","entry_source"),("verification/s2b_board_jtag.py","tool_source")):
    raw=subprocess.run(["git","show",cfg["source_commit"]+":"+name],cwd=root,capture_output=True,check=True).stdout
    assert hashlib.sha256(raw).hexdigest()==cfg["bindings"][key]["sha256"]
    target=folder/"source_snapshot"/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    mappings.append({"source_commit":cfg["source_commit"],"source":name,"target":str(target),"sha256":sha(target),"transformation":"GIT_EXACT_BYTES","limitation":"根据真实配置绑定从Git恢复，不冒充即时快照。"})
closed=json.loads((folder/"server_close.json").read_text(encoding="utf-8"))
assert closed["status"]=="OWNED_SERVER_CLOSED" and closed["native_absent"] and not closed["listeners"]
pc=[x for x in jtag["calls"] if x["api"].endswith("rrd.pc")]
save(folder/"summary.json",{"status":"FAILED_PC_STDOUT_INTERLEAVED_INFO","source_commit":cfg["source_commit"],"actual_entry_exit_code":2,
    "launcher_exit_code":json.loads((folder/"vitis_execution.json").read_text(encoding="utf-8"))["native_exit_code"],
    "elapsed_seconds":result["elapsed_seconds"],"pc_observations":pc,"cleanup_errors":result["cleanup_errors"],"server_closed":closed,
    "system_reset":"API_RETURNED，但后续PC解析失败，未完成system_reset记录或EOS观察。",
    "mapping":"NOT_RUN","ps_initialization":"NOT_RUN","pl_download":"NOT_RUN","uart":"NOT_OPENED","cache":"NOT_RUN","model":"NOT_RUN",
    "setup_attempt_limit":"配置生成首次传相对路径被精确绝对路径门禁拒绝，宿主退出1；原输出仅工具对话，不冒充raw文件。",
    "commit_validation_limit":"提交前逐字节检查先因STATE的既有CRLF转换失败；提交后核对150文件通过，仅STATE转换为LF，代码和证据原字节一致。"})
save(folder/"source_mapping.json",mappings)
common={"schema_version":1,"stage":"2B","task_id":"S2B-T19","source_commit":cfg["source_commit"],"interfaces":[],
    "interfaces_not_applicable_reason":"保存已批准visibility0入口在映射前的真实调试输出失败，不改变正式接口或验收条件。",
    "tool_versions":{"vitis":"2026.1","python_packager":"3.12.14"},
    "checks":[{"name":"缓存检查入口","status":"BLOCKED","command":"vitis.bat -s vitis/run_s2b_visibility_probe.py","exit_code":None,"reason":"启动器原生0，入口逻辑结果2/FAILED；异步停止通知混入PC标准输出，映射和PSinit/下载/cache均未执行。"}],
    "limitations":["没有缓存或模型实物结果；真实复位调用完成不证明冷生命周期。","恢复的源码匹配实际绑定SHA，不是即时快照。"]}
for directory in (run,folder):
    files=[row(p,"input" if p.name=="input_config.json" else "source" if p.suffix in (".py",".ps1") else "result") for p in sorted(directory.rglob("*")) if p.is_file()]
    if directory==run:files += [row(p,"source") for p in sorted((folder/"source_snapshot").rglob("*.py"))]
    save(directory/"delivery_manifest.json",{**common,"run_id":directory.name,"evidence_dir":directory.relative_to(root).as_posix(),"files":files})
print(json.dumps({"status":"PACKAGED_REAL_FAILURE","entry_exit_code":2,"sdk_cleanup_errors":[],"server_pid_closed":closed["native_pid"]}))
