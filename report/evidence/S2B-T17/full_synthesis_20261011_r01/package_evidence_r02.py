"""绑定本次FAIL_TIMING证据；包装通过与STA失败分别记录。"""
from pathlib import Path
import json
import hashlib
import subprocess
import sys
ROOT=Path(__file__).absolute().parents[4]
CACHE=Path(__file__).absolute().parent
RUN=ROOT/"report/evidence/S2B-T17/full_synthesis_20261011_r01"
def digest(path):
    """流式读取已存在的精确文件。"""
    assert path.is_file(),str(path)
    h=hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda:src.read(1048576),b""):h.update(chunk)
    return h.hexdigest()

def save(path,data):
    """创建新UTF8机器原件，不覆盖已有路径。"""
    assert path.parent.is_dir() and not path.exists(),str(path)
    with path.open("x",encoding="utf-8",newline="\n") as out:json.dump(data,out,ensure_ascii=False,indent=2);out.write("\n")

def copy(source,target):
    """复制精简脚本及哈希记录到正式证据。"""
    assert source.is_file() and target.parent.is_dir() and not target.exists()
    with source.open("rb") as src,target.open("xb") as out:
        for chunk in iter(lambda:src.read(1048576),b""):out.write(chunk)
    assert digest(source)==digest(target)

assert RUN.is_dir() and CACHE.is_dir()
for name in ["collect_evidence.py","collect_evidence_r02.py","original_inventory.json","original_inventory_r02.json"]:
    assert digest(CACHE/name)==digest(RUN/name)
copy(Path(__file__).absolute(),RUN/"package_evidence_r02.py")
bindings=json.loads((RUN/"source_git_comparison_r02.json").read_text(encoding="utf-8"))
sta=json.loads((RUN/"sta_classification.json").read_text(encoding="utf-8"))
collected=json.loads((RUN/"collection_result_r02.json").read_text(encoding="utf-8"))
assert collected["collection_native_exit_code"]==0 and collected["sta_native_exit_code"]==2
assert sta["status"]=="FAIL_TIMING" and len(bindings["files"])==24
upstream=ROOT/"report/evidence/S2B-T07/physical_contract_20261009_r02/delivery_manifest.json"
interfaces=json.loads(upstream.read_text(encoding="utf-8"))["interfaces"]
interface_subset=[interfaces[0],interfaces[2]]
checker=ROOT/"verification/check_stage_delivery.py"
assert checker.is_file()
checks=[{"name":"24原快照声明SHA与Git来源核验","status":"PASS","command":"python tmp/2B/S2B-T17/evidence_collection_20261011_r01/collect_evidence_r02.py","exit_code":0,
         "reason":"24份RAW与source_before相同；20份与Gitblob RAW相同，4份精确LF转CRLF可重现。不是把不同RAW声明相同，原快照为实际综合字节。"},
        {"name":"初次Git RAW全相同断言","status":"FAIL","command":"python tmp/2B/S2B-T17/evidence_collection_20261011_r01/collect_evidence.py","exit_code":1,
         "reason":"4份checkout EOL差异导致原断言失败；原collection_result及comparison完整保留，r02只补充来源证明。"},
        {"name":"MCP客户端wait_on_run","status":"BLOCKED","command":"wait_on_run synth_1","exit_code":None,
         "reason":"客户端真实tool isError、300s超时，无native整数退出码；保留故障，不改成成功。"},
        {"name":"原native综合完成","status":"PASS","command":"wait_on_run synth_1","exit_code":0,
         "reason":"真实ROSS history code0/311.587s，5job日志完成、0Critical/0Errors及end marker；不伪造未观察的各子进程OS退出码。"},
        {"name":"50MHz综合STA分类","status":"FAIL","command":subprocess.list2cmdline(collected["sta_command"]),"exit_code":2,
         "reason":"实际分类程序native2/FAIL_TIMING：WNS-76.685、TNS-117866.523、2639 setup failing endpoints；综合成功不代表时序成功。"},
        {"name":"首次归档命名包装检查","status":"FAIL","command":"python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S2B-T17/full_synthesis_20261011_r01/delivery_manifest_probe.json","exit_code":2,
         "reason":"本次新增native_jobs/synth_1目录被识别为工程缓存；旧失败log/清单保留，root批准唯一目录移动到wrapper_native_r01且SHA逐项不变，relocation映射解释旧saved_path。"},
        {"name":"postroute及实板模型验收","status":"NOT_RUN","command":None,"exit_code":None,
         "reason":"当前仅Synthesized，时序失败阻断部署；未执行实现、postroute、位流生成或硬件操作。"}]

def manifest():
    """只绑定本Run的原件和新增证据，不读取正在修改的S1源码。"""
    files=[]
    for path in sorted(RUN.rglob("*")):
        if not path.is_file():continue
        role="source" if "source_snapshot" in path.parts or path.suffix in {".py",".tcl"} else "log" if path.suffix in {".log",".rpt"} else "artifact" if path.suffix==".xdc" else "result"
        files.append({"path":path.relative_to(ROOT).as_posix(),"sha256":digest(path),"role":role})
    return {"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":"full_synthesis_20261011_r01","source_commit":collected["source_commit"],
            "evidence_dir":RUN.relative_to(ROOT).as_posix(),"interfaces":interface_subset,"files":files,
            "tool_versions":{"Vivado":"2026.1 Build6511674","device":"xc7z020clg400-2","Python":sys.version.split()[0]},"checks":checks,
            "limitations":["证据包装成功不代表STA/G2/G3/G4/G5通过；物理candidate0.1.1未冻结，inputs保持受阻。",
                            "Git基线f260880及实际24RAW快照可复核；不消费最新b8d5e5/S1正在修改的源。",
                            "infer2305.652MB仅该job单进程峰；rootsession2453.121MB累计，不混为本次全进程树峰，全tree未测。",
                            "DCP仅ignored缓存路径/SHA引用，不复制、不作为长期冻结依赖；原tmp保留。",
                            "原MCP客户端timeout及quoting/Windows206/chunk故障保留，不能归类为STA设计成功。"]}

probe=RUN/"delivery_manifest_probe_r02.json";save(probe,manifest())
outcomes=[]
for mode in ["evidence","inputs"]:
    command=[sys.executable,"-B",str(checker),"--mode",mode,"--manifest",str(probe)]
    result=subprocess.run(command,cwd=ROOT,capture_output=True)
    log=CACHE/(mode+"_probe_r02.log")
    with log.open("xb") as out:out.write(result.stdout+result.stderr)
    copy(log,RUN/log.name)
    outcomes.append({"mode":mode,"command":command,"native_exit_code":result.returncode,"log_sha256":digest(log)})
    assert result.returncode==(0 if mode=="evidence" else 2)
save(RUN/"packaging_probe_result_r02.json",{"probe_manifest_sha256":digest(probe),"checks":outcomes,"meaning":"evidence0只证包装；inputs2明确候选未冻结与STA FAIL。"})
final=RUN/"delivery_manifest.json";save(final,manifest())
command=[sys.executable,"-B",str(checker),"--mode","evidence","--manifest",str(final)]
result=subprocess.run(command,cwd=ROOT,capture_output=True)
with (CACHE/"evidence_final_r02.log").open("xb") as out:out.write(result.stdout+result.stderr)
print(json.dumps({"manifest":str(final),"sha256":digest(final),"evidence_native_exit_code":result.returncode,
                  "sta_status":sta["status"],"sta_native_exit_code":2,"inputs_probe_native_exit_code":2},ensure_ascii=False))
assert result.returncode==0
