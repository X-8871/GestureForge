"""保存真实上板失败与独占服务闭合；不将启动器零退出码当作验收通过。"""
from pathlib import Path
import hashlib
import json
import subprocess

root=Path(__file__).absolute().parents[4]
run=root/"report/evidence/S2B-T19/cache_probe_20261013_r01"
source=root/"tmp/2B/S2B-T19/board_run_20261013_r01"
dest=root/"report/evidence/S2B-T19/cache_probe_execution_20261013_r01"
baseline="dd1ffe44f2cb0d8a99f79e314febf2bdd44d84e2"

def require(value,message):
    """目标、哈希或实际状态不符合时停止。"""
    if not value:raise RuntimeError(message)

def digest(path):
    """固定实际文件原字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,data):
    """新JSON使用UTF-8独占创建。"""
    with path.open("x",encoding="utf-8",newline="\n") as out:
        json.dump(data,out,ensure_ascii=False,indent=2);out.write("\n")

def row(path,role):
    return {"path":path.relative_to(root).as_posix(),"sha256":digest(path),"role":role,"keep_reason":"保存真实失败、来源或闭合证据，不证明模型或阶段验收。"}

require(run.is_dir() and source.is_dir() and dest.parent.is_dir() and dest.is_dir(),"运行或归档目标不符合")
require(set(path.name for path in dest.iterdir())=={"entry_source_executed.py","tool_source_executed.py","transport_source_executed.py","executed_source_mappings.json"},"已有部分归档范围不符合")
require(not (run/"delivery_manifest.json").exists(),"失败Run已包装，拒绝覆盖")
result=json.loads((run/"visibility_probe_result.json").read_text(encoding="utf-8"))
jtag=json.loads((run/"jtag_result.json").read_text(encoding="utf-8"))
cfg=json.loads((run/"input_config.json").read_text(encoding="utf-8"))
require(result["status"]=="FAILED" and result["native_exit_code"]==2,"不能把其他Run归为本次失败")
mappings=[]
for name in ("uart_identity.json","hw_server_identity.json","launcher_identity.json","server_close.json","server_script_bindings.json","vitis_execution.json","start_owned_server.ps1","close_owned_server.ps1","prepare_owned_server_scripts.py","hw_server_stdout.log","hw_server_stderr.log"):
    original=source/name
    require(original.is_file(),"执行原件缺失："+name)
    target=dest/name;target.write_bytes(original.read_bytes())
    require(digest(target)==digest(original),"原字节复制漂移")
    mappings.append({"source":str(original),"target":str(target),"sha256":digest(target),"transformation":"EXACT_BYTES"})
for name in ("vitis/run_s2b_visibility_probe.py","verification/s2b_board_jtag.py"):
    key="entry_source" if name.startswith("vitis/") else "tool_source"
    expected=cfg["bindings"][key]["sha256"]
    raw=subprocess.run(["git","show",baseline+":"+name],cwd=root,capture_output=True,check=True).stdout
    variants=[("GIT_EXACT_BYTES",raw),("GIT_LF_TO_CRLF",raw.replace(b"\r\n",b"\n").replace(b"\n",b"\r\n"))]
    matches=[(kind,value) for kind,value in variants if hashlib.sha256(value).hexdigest()==expected]
    require(matches,"无法重建已绑定失败源码")
    kind,value=matches[0];target=dest/"source_snapshot"/name
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(value)
    mappings.append({"source_commit":baseline,"source":name,"target":str(target),"sha256":expected,"transformation":kind,"limitation":"根据实际input_config的源码SHA从Git恢复；不是运行时即时快照。"})
launcher=json.loads((dest/"vitis_execution.json").read_text(encoding="utf-8"))
closed=json.loads((dest/"server_close.json").read_text(encoding="utf-8"))
summary={"status":"FAILED_DEBUG_MEMORY_MAP_NOT_REGISTERED","source_commit":baseline,
         "actual_entry_exit_code":result["native_exit_code"],"vitis_launcher_exit_code":launcher["native_exit_code"],
         "elapsed_seconds":result["elapsed_seconds"],"error":result["error"],
         "initialization":jtag.get("initialization"),"ddrc_observation":jtag.get("ddrc_observation"),
         "eos_observations":[{k:x.get(k) for k in ("phase","status","eos","status_word")} for x in jtag.get("configuration_observations",[])],
         "postconfiguration_status":jtag.get("postconfiguration",{}).get("status"),
         "postconfiguration_register_steps":jtag.get("postconfiguration",{}).get("steps",[]),
         "serial_closed":result.get("serial_closed"),"sdk_cleanup_errors":result["cleanup_errors"],
         "owned_server_final":closed,"cache_probe":"NOT_RUN","model_run":"NOT_RUN",
         "limits":["EOS与寄存器观测不证明模型、缓存或完整冷生命周期。","Vitis启动器返回0但入口真实失败2，不能判断运行通过。","源码从绑定SHA重建，不冒充即时采样。"]}
save(dest/"summary.json",summary);save(dest/"source_mappings.json",mappings)
common={"schema_version":1,"stage":"2B","task_id":"S2B-T19","source_commit":baseline,
        "interfaces":[],"interfaces_not_applicable_reason":"保存已批准候选的实际下载失败，不改变或冻结接口；后续修复与实物检查仍受原门禁约束。",
        "tool_versions":{"vitis":"2026.1","packager_python":"3.12.14","vitis_runtime_python":"未单独采集"},
        "checks":[{"name":"缓存先验部署","status":"BLOCKED","reason":"实际入口退出2，first CSR读取被TCF拒绝，调试内存映射尚未登记；app和cache未运行。"}],
        "limitations":summary["limits"]}
for folder in (run,dest):
    manifest={**common,"run_id":folder.name,"evidence_dir":folder.relative_to(root).as_posix(),
              "files":[row(path,"input" if path.name=="input_config.json" else "source" if path.suffix in (".py",".ps1") else "result") for path in sorted(folder.rglob("*")) if path.is_file()]}
    save(folder/"delivery_manifest.json",manifest)
paths=[path.relative_to(root).as_posix() for folder in (run,dest) for path in sorted(folder.rglob("*")) if path.is_file()]
with Path(__file__).with_name("failed_board_stage_paths.nul").open("xb") as out:
    out.write(b"".join(path.encode("utf-8")+b"\0" for path in paths))
print(json.dumps({"archived_files":len(paths),"status":summary["status"],"actual_entry_exit_code":2,"launcher_exit_code":launcher["native_exit_code"]}))
