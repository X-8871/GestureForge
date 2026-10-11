"""只生成新的恢复脚本，保留首轮脚本和失败原件。"""
from collection_common import *

prefix='''
# 已有副本只读核验，不覆盖首轮任何原件。
rawcopy_new=rawcopy
mkdir_new_first=mkdir_new
save_new=save
def rawcopy(source,target):
    """首轮已经复制的文件只核验原字节。"""
    if not target.exists():return rawcopy_new(source,target)
    exact(source);exact(target)
    a=binding(source);b=binding(target)
    require(a["sha256"]==b["sha256"] and a["bytes"]==b["bytes"],"已有副本漂移："+str(target))
    return {"original_path":str(source),"saved_path":rel(target),"sha256":b["sha256"],"bytes":b["bytes"]}
def mkdir_new(path):
    """首轮新建目录仅验证并复用。"""
    return exact(path,"directory") if path.exists() else mkdir_new_first(path)
def save(path,value):
    """相同的首轮JSON仅验证，不重写。"""
    if path.exists():require(read(path)==value,"首轮JSON内容不同："+str(path))
    else:save_new(path,value)
'''
source=exact(CACHE/"collect_s4_synthesis.py").read_text(encoding="utf-8")
start=source.index("    inventories=[];counts={}")
end=source.index("    for name in (",start)
source=source[:start]+'''    inventories=original_check()
    counts=read(REPORT/"s4_collection_original_inventory.json")["directories"]
    require(len(inventories)==142,"原件冻结数量不同")
    for name in ("prepare_recovery_r02.py","seal_collection_r02.py","run_recovery_r02.py","finalize_recovery_r02.py","run_final_recovery_r02.py"):
        rawcopy(CACHE/name,REPORT/("s4_collection_"+name))
'''+source[end:]
source=source.replace("started=time.monotonic()\ntry:",prefix+"\nstarted=time.monotonic()\ntry:",1)
require(source.count("synth/s2b_inference_infer_0.v")==1,"扩展名替换目标不唯一")
source=source.replace("synth/s2b_inference_infer_0.v","synth/s2b_inference_infer_0.sv")
where='    for number in (1,2):'
require(source.count(where)==1,"失败check插入目标不唯一")
source=source.replace(where,'''    first_collector=read(REPORT/"s4_collection_collector.native.json")
    require(first_collector["native_exit_code"]==1,"首轮失败码不同")
    checks.append({"name":"首Collector生成文件扩展名门禁失败","status":"FAIL","command":" ".join(first_collector["command"]),"exit_code":1,"reason":"首轮预设infer生成文件.v不存在，路径门禁原生1；真实只读枚举为.sv，新脚本封装对应原件，不覆盖首轮脚本/日志/失败JSON，不重跑综合。"})
'''+where)
source=source.replace('"s4_collection_failure_r01.json"','"s4_collection_failure_r02.json"')
with (CACHE/"seal_collection_r02.py").open("x",encoding="utf-8",newline="\n") as out:out.write(source)
final=exact(CACHE/"finalize_s4_manifest.py").read_text(encoding="utf-8")
final=final.replace('"s4_collection_collector.native.json"','"s4_collection_recovery_r02.native.json"')
final=final.replace('"finalization_failure.json"','"finalization_recovery_failure.json"')
with (CACHE/"finalize_recovery_r02.py").open("x",encoding="utf-8",newline="\n") as out:out.write(final)
print(json.dumps({"status":"NEW_RECOVERY_SCRIPTS_CREATED","original_collector_preserved":binding(CACHE/"collect_s4_synthesis.py"),"recovery_collector":binding(CACHE/"seal_collection_r02.py"),"recovery_finalizer":binding(CACHE/"finalize_recovery_r02.py")},ensure_ascii=False))
