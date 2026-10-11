"""记录真实原生退出码，初次包装不修改，最终日志放缓存避免自引用。"""
from pathlib import Path
import json,hashlib,subprocess,sys,shutil
root=Path.cwd();directory=root/"report/evidence/S2B-T17/conv_validation_20261011_r15";work=root/"tmp/2B/S2B-T17/conv_validation_20261011_r15"
manifest=directory/"delivery_manifest.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=manifest.read_bytes();(directory/"delivery_manifest_precheck.json").write_bytes(raw)
records=[]
for mode in ("evidence","inputs"):
 cmd=[sys.executable,"-X","utf8","verification/check_stage_delivery.py","--mode",mode,"--manifest",str(manifest)]
 p=subprocess.run(cmd,capture_output=True);path=directory/("delivery_"+mode+"_precheck.log");path.write_bytes(p.stdout+p.stderr)
 records.append({"mode":mode,"command":cmd,"native_exit_code":p.returncode,"log_sha256":sha(path),"manifest_sha256":hashlib.sha256(raw).hexdigest()})
 if p.returncode!=(0 if mode=="evidence" else 2):raise RuntimeError("包装门禁非预期退出")
(directory/"delivery_precheck_native.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
shutil.copyfile(work/"package.log",directory/"package_initial_manifest.log")
shutil.copyfile(Path(__file__),directory/Path(__file__).name)
v=json.loads(raw);declared={x["path"] for x in v["files"]}
for path in directory.iterdir():
 key=path.relative_to(root).as_posix()
 if path.is_file() and path!=manifest and key not in declared:v["files"].append({"path":key,"sha256":sha(path),"role":"log" if path.suffix==".log" else "artifact" if path.suffix==".py" else "result"})
manifest.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
final=[]
for mode in ("evidence","inputs"):
 cmd=[sys.executable,"-X","utf8","verification/check_stage_delivery.py","--mode",mode,"--manifest",str(manifest)]
 p=subprocess.run(cmd,capture_output=True);path=work/("final_delivery_"+mode+".log");path.write_bytes(p.stdout+p.stderr)
 final.append({"mode":mode,"command":cmd,"native_exit_code":p.returncode,"log_sha256":sha(path)})
 if p.returncode!=(0 if mode=="evidence" else 2):raise RuntimeError("最终包装门禁非预期退出")
freeze=json.loads((directory/"source_freeze.json").read_text(encoding="utf-8"))
for key,digest in freeze["source_sha256"].items():
 if sha(root/key)!=digest:raise RuntimeError("STOP源漂移")
(work/"final_native_delivery.json").write_text(json.dumps({"manifest_sha256":sha(manifest),"files":len(v["files"]),"final":final},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"manifest_sha256":sha(manifest),"source_freeze_sha256":sha(directory/"source_freeze.json"),"files":len(v["files"]),"native_exit_codes":[x["native_exit_code"] for x in final],"source_bindings_unchanged":len(freeze["source_sha256"])},ensure_ascii=False))
