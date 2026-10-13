"""保留旧包装并补齐真实失败源码、命令与退出码；不修改运行结论。"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

root=Path(__file__).absolute().parents[4]
parent=root/"report/evidence/S2B-T19"
run=parent/"cache_probe_20261013_r01"
execution=parent/"cache_probe_execution_20261013_r01"
validation=parent/"cache_probe_packaging_20261013_r02"
validation.mkdir()
def sha(path):
    """绑定原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):
    """JSON使用UTF-8。"""
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def row(path,role):
    """只登记核验过的实际文件。"""
    return {"path":path.relative_to(root).as_posix(),"sha256":sha(path),"role":role,"keep_reason":"保留真实失败、包装修复或源码绑定；不表示模型通过。"}
launcher=json.loads((execution/"vitis_execution.json").read_text(encoding="utf-8"))
for folder in (run,execution):
    path=folder/"delivery_manifest.json"
    raw=path.read_bytes();(validation/(folder.name+"_manifest_before.json")).write_bytes(raw)
    manifest=json.loads(raw)
    manifest["checks"][0].update(command=launcher["command"],exit_code=launcher["native_exit_code"],
        reason="启动器原生退出0，但入口visibility_probe_result原生结果2/FAILED；first CSR被TCF拒绝，app/cache未运行。")
    manifest["files"]=[row(p,"input" if p.name=="input_config.json" else "source" if p.suffix in (".py",".ps1") else "result") for p in sorted(folder.rglob("*")) if p.is_file() and p!=path]
    if folder==run:
        manifest["files"] += [row(p,"source") for p in sorted((execution/"source_snapshot").rglob("*.py"))]
    save(path,manifest)
results=[]
for folder in (run,execution):
    for mode in ("inputs","evidence"):
        command=[sys.executable,"-X","utf8","-B","verification/check_stage_delivery.py","--mode",mode,"--manifest",str(folder/"delivery_manifest.json")]
        env=os.environ.copy();env["PYTHONIOENCODING"]="utf-8"
        actual=subprocess.run(command,cwd=root,env=env,capture_output=True)
        label=folder.name+"_"+mode
        (validation/(label+"_stdout.log")).write_bytes(actual.stdout)
        (validation/(label+"_stderr.log")).write_bytes(actual.stderr)
        results.append({"command":command,"native_exit_code":actual.returncode,"expected_exit_code":2 if mode=="inputs" else 0})
save(validation/"execution.json",{"checks":results,"previous_packaging_failure":"旧evidence检查缺少source/command/exit_code，宿主返回1；原始输出未另存，旧清单字节保留。","hardware_execution":"NOT_RUN"})
paths=[p.relative_to(root).as_posix() for folder in (run,execution,validation) for p in sorted(folder.rglob("*")) if p.is_file()]
Path(__file__).with_name("failed_board_stage_paths_r02.nul").write_bytes(b"".join(p.encode("utf-8")+b"\0" for p in paths))
print(json.dumps(results,ensure_ascii=False))
sys.exit(0 if all(x["native_exit_code"]==x["expected_exit_code"] for x in results) else 1)
