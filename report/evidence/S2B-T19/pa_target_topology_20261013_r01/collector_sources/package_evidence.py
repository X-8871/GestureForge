"""按既有stage_delivery格式打包本轮离线证据，保留原生失败与最终源码绑定。"""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

root=Path(__file__).resolve().parents[4]
run_id="pa_target_topology_20261013_r01"
folder=root/"report/evidence/S2B-T19"/run_id
baseline="c8742858fbb23331763358775daa44dafb95db94"
names=["verification/s2b_board_jtag.py","verification/test_s2b_board_jtag.py",
       "vitis/run_s2b_visibility_probe.py","verification/test_s2b_visibility_probe.py"]
def digest(file):
    """哈希只绑定实际原字节。"""
    return hashlib.sha256(file.read_bytes()).hexdigest()
def save(name,data):
    """独占创建UTF8证据文件。"""
    with (folder/name).open("x",encoding="utf-8",newline="\n") as out:
        json.dump(data,out,ensure_ascii=False,indent=2);out.write("\n")

current={name:digest(root/name) for name in names}
finals={name:json.loads((folder/(name+"_run_result.json")).read_text(encoding="utf-8"))
        for name in ("special_final_r08","consumers_final_r09")}
if any(row["exit_code"]!=0 or row["before_source_sha256"]!=current or row["after_source_sha256"]!=current for row in finals.values()):
    raise RuntimeError("最终回归失败或源码发生漂移，禁止封包为G1通过")
save("g1_summary.json",{"status":"PASS_OFFLINE_G1_ONLY","source_commit":baseline,"source_sha256":current,
     "final_native_results":{name:{"exit_code":row["exit_code"],"elapsed_seconds":row["elapsed_seconds"],"command":row["command"]} for name,row in finals.items()},
     "hardware_calls":0,"independent_review":"NOT_RUN_BY_DEVELOPER","hardware_validation":"NOT_RUN",
     "peak_memory_bytes":None,"tool_call_count":None,"limitations":["真实公共unloadhw原因未知，下一次实板Run才可能产生诊断栈。"]})
snapshot=folder/"source_snapshot";snapshot.mkdir()
for name in names:
    file=root/name
    (snapshot/("before_"+file.name)).write_bytes(subprocess.check_output(["git","show",baseline+":"+name],cwd=root))
    shutil.copyfile(file,snapshot/("after_"+file.name))
original=root/"report/evidence/S2B-T19/cache_probe_20261013_r04/jtag_result.json"
data=json.loads(original.read_text(encoding="utf-8"))
call=[row for row in data["calls"] if row["api"]=="session.targets.properties"][-1]
save("actual_r04_topology.json",{"original_path":str(original),"original_sha256":digest(original),
                                  "call":call,"properties":ast.literal_eval(call["return_repr"]),
                                  "actual_exception":data.get("error"),"actual_traceback":data.get("traceback")})
sdk_root=Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb")
save("sdk_basis.json",{"sources":{name:{"path":str(sdk_root/name),"sha256":digest(sdk_root/name)}
                                  for name in ("target.py","session.py","_tcf_children_exec_context.py","_tcf_node_launch.py","_tcf_node_memmap.py")},
     "pa_origin":"Memory.getChildren与RunControl子目标合并，loadhw递归暴露CPU各自的PA子ctx；__get_access_modes按Name使用CPU子目标。",
     "display_side_effect":"_get_all_children_of_the_node原地展开APU的children缓存，parent文本APU与level1不代表真实父ctx；实际parent_ctx仍各CPU。",
     "dynamic_selection":"执行官方AST已验证Session.targets(current id)返回精确新Target；旧_id不修改，固定_ctx与链保持。",
     "unload_status":"UNKNOWN_PUBLIC_API_DID_NOT_RETURN",
     "unload_candidates":"公共unloadhw内部包含_run_ctx、递归children、MemoryMap.set与HSI design.close；原日志不能区分具体卡点。",
     "hardware_calls_in_this_patch":0,"physical_stack_dump":"NOT_RUN；离线计时器mock反例不证明真实挂起栈。"})
collector=folder/"collector_sources";collector.mkdir()
for name in ("run_checks.py","package_evidence.py"):
    shutil.copyfile(Path(__file__).parent/name,collector/name)
checks=[]
for file in sorted(folder.glob("*_run_result.json")):
    receipt=json.loads(file.read_text(encoding="utf-8"))
    check={"name":file.stem,"status":"PASS" if receipt["exit_code"]==0 else "FAIL",
           "command":subprocess.list2cmdline(receipt["command"]),"exit_code":receipt["exit_code"],
           "elapsed_seconds":receipt["elapsed_seconds"]}
    if receipt["exit_code"]!=0:
        check["reason"]=("sandbox父目录枚举/既有serial依赖读取PermissionError，未代表实现失败。" if "special_r01" in file.name
                         else "多个独立mock复用同一诊断路径，被独占创建检查拒绝；已按独立Run分目录保留原件。" if "focused_r06" in file.name
                         else "新反例误用package与helpers top-level两个同名异常类，已按实际helpers类型修正；原件保留。")
    checks.append(check)
checks.append({"name":"新PA兼容与卸载栈实板验证","status":"NOT_RUN","command":None,"exit_code":None,
               "reason":"本Developer仅离线；真实新版SDK卸载是否返回及具体卡点需后续独立设备Run。"})
files=[]
for file in sorted(folder.rglob("*")):
    if file.is_file():
        files.append({"path":file.relative_to(root).as_posix(),"sha256":digest(file),
                      "role":"source" if file.suffix==".py" else "input" if file.name in ("actual_r04_topology.json","sdk_basis.json") else "result",
                      "keep_reason":"本轮源码/官方依据、真实故障输入或离线回归原件；不代表实板G3。"})
save("delivery_manifest.json",{"schema_version":1,"stage":"2B","task_id":"S2B-T19","run_id":run_id,"source_commit":baseline,
     "evidence_dir":folder.relative_to(root).as_posix(),"interfaces":[],
     "interfaces_not_applicable_reason":"只修复既有visibility0调试SDK目标枚举与公共卸载诊断，不改变任何UART、模型、PS/PL地址或物理接口。",
     "tool_versions":{"python":sys.version,"vitis_sdk_source":"2026.1只读官方源；没有实际硬件调用"},
     "files":files,"checks":checks,"limitations":["真实r04公共unloadhw未返回原因UNKNOWN；不冒充finally完成。",
     "本轮无实板栈，空诊断文件不能算已dump。","阶段2B G3/G4/G5与模型部署验收仍由总控后续执行。","峰值内存未测；初始环境与反例失败原件保留。"]})
print(json.dumps({"source_sha256":{name:digest(root/name) for name in names},"manifest_sha256":digest(folder/"delivery_manifest.json"),"files":len(files)},ensure_ascii=False))
