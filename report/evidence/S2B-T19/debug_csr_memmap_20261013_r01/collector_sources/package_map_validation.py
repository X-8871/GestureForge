"""固定映射修复离线验证及历史失败，不将G1当作实物验收。"""
from pathlib import Path
import hashlib
import json
import subprocess
root=Path(__file__).absolute().parents[4]
folder=root/"report/evidence/S2B-T19/debug_csr_memmap_20261013_r01"
def sha(path):
    """绑定实际字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):
    """新证据独占写入UTF-8。"""
    with path.open("x",encoding="utf-8",newline="\n") as output:
        json.dump(data,output,ensure_ascii=False,indent=2);output.write("\n")
def row(path,role):
    """按真实角色登记。"""
    return {"path":path.relative_to(root).as_posix(),"sha256":sha(path),"role":role,"keep_reason":"保留本次离线命令、失败原件或源码快照，不证明G3。"}
final=json.loads((folder/"entry_r06/execution.json").read_text(encoding="utf-8"))
assert final["native_exit_code"]==0 and final["source_unchanged"]
assert all(sha(root/name)==value for name,value in final["source_sha256_after"].items())
sources=folder/"collector_sources";sources.mkdir()
for name in ("run_validation.py","package_map_validation.py","package_failed_board_run.py","fix_failed_manifests.py","recheck_failed_manifests.py"):
    original=Path(__file__).with_name(name);(sources/name).write_bytes(original.read_bytes())
history=[]
for execution in sorted(folder.glob("*/execution.json")):
    actual=json.loads(execution.read_text(encoding="utf-8"))
    history.append({"run":execution.parent.name,"native_exit_code":actual["native_exit_code"],"elapsed_seconds":actual["elapsed_seconds"],"source_sha256":actual["source_sha256_after"]})
save(folder/"summary.json",{"status":"PASS_G1_SOFTWARE_ONLY","final_methods":28,"final_run":"entry_r06","source_sha256":final["source_sha256_after"],"history":history,
    "initial_targeted_attempt":"首次targeted fixture缺calls字段，6方法/12errors；原始输出仅工具对话，未另存raw。",
    "failure_reasons":{"entry_r01":"Bundled Python无serial，测试夹具改用已绑定pyserial源目录。","entry_r03":"沙箱拒绝路径祖先只读枚举，非RTL或硬件失败。","entry_r04":"新断言禁止所有FPGA观察，误拒复位config_status。","entry_r05":"已缩小con断言但仍误拒config_status；entry_r06禁止fpga(file)而允许状态观察。"},
    "hardware_execution":"NOT_RUN","independent_review":"独立审查另有实际收据，不由本汇总生成。","partial_cleanup_limit":"SDK loadhw在memmap建立前失败时unloadhw可能早返；本修复检测残留并报失败，不声称design已closed。"})
manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T19","run_id":folder.name,
    "source_commit":subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,check=True).stdout.decode("ascii").strip(),
    "evidence_dir":folder.relative_to(root).as_posix(),"interfaces":[],"interfaces_not_applicable_reason":"仅修复已批准visibility0入口的调试地址映射，不改变物理总线、UART或模型接口；正式平台范围仍沿用原批准。",
    "tool_versions":{"python":final["python_version"],"vitis_sdk_source":"2026.1；本包未导入SDK运行时"},
    "files":[row(path,"source" if path.suffix==".py" else "result") for path in sorted(folder.rglob("*")) if path.is_file()]+[row(root/"report/evidence/S2B-T19/cache_probe_20261013_r01/input_config.json","input")],
    "checks":[{"name":"最终28项离线回归","status":"PASS","command":subprocess.list2cmdline(final["command"]),"exit_code":0}],
    "limitations":["G1只有模拟SDK与串口，实际注册和CSR/cache需实板新Run。","历史失败完整保留；collector_sources是当前脚本版本，不冒充每个旧Run即时快照。","峰值内存未测；独立审查另行执行。"]}
save(folder/"delivery_manifest.json",manifest)
print(json.dumps({"status":"PACKAGED_G1_ONLY","files":len(manifest["files"])}))
