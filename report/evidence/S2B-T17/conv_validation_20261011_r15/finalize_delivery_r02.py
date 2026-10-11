"""保留首次包装失败原件；先枚举实际证据，再冻结新清单，日志写缓存。"""
from pathlib import Path
import json,hashlib,subprocess,sys,shutil
root=Path.cwd();evidence=root/"report/evidence/S2B-T17/conv_validation_20261011_r15";work=root/"tmp/2B/S2B-T17/conv_validation_20261011_r15"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for source,name in ((work/"package.log","package_initial_manifest.log"),(work/"check_native_delivery.py","check_native_delivery_failed.py"),(Path(__file__),Path(__file__).name)):
 target=evidence/name
 if target.exists():raise RuntimeError("禁止覆盖")
 shutil.copyfile(source,target)
original=evidence/"delivery_manifest.json";manifest=evidence/"delivery_manifest_r02.json"
if manifest.exists():raise RuntimeError("新清单已存在")
failure={"status":"FAIL_PACKAGING_PRECHECK","checker_native_exit_code":2,"wrapper_exit_code":1,"manifest_sha256":sha(original),"reason":"首次helper先写delivery_manifest_precheck.json再调用evidence门禁，该新文件未声明，检查器正确拒绝；原manifest/原门禁log/原helper完整保留。","log":"delivery_evidence_precheck.log"}
(evidence/"packaging_precheck_failure_native.json").write_text(json.dumps(failure,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
v=json.loads(original.read_text(encoding="utf-8"));existing={x["path"]:x for x in v["files"]}
for p in evidence.iterdir():
 if p.is_file() and p!=manifest:
  key=p.relative_to(root).as_posix()
  existing[key]={"path":key,"sha256":sha(p),"role":"log" if p.suffix==".log" else "artifact" if p.suffix in (".py",".patch",".sv") else "result"}
v["files"]=list(existing.values());v["limitations"].append("r15首个delivery precheck因未声明刚写的precheck清单而native2，原件不改写；r02先绑定全部原件，再把最终门禁日志仅写缓存避免自引用。")
manifest.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
records=[]
for mode in ("evidence","inputs"):
 cmd=[sys.executable,"-X","utf8","verification/check_stage_delivery.py","--mode",mode,"--manifest",str(manifest)]
 p=subprocess.run(cmd,capture_output=True);log=work/("final_r02_delivery_"+mode+".log");log.write_bytes(p.stdout+p.stderr)
 records.append({"mode":mode,"command":cmd,"native_exit_code":p.returncode,"log_sha256":sha(log)})
 if p.returncode!=(0 if mode=="evidence" else 2):raise RuntimeError("最终原生门禁非预期退出")
freeze=json.loads((evidence/"source_freeze.json").read_text(encoding="utf-8"))
for p,digest in freeze["source_sha256"].items():
 if sha(root/p)!=digest:raise RuntimeError("STOP源漂移")
result={"status":"PASS_S4_DEVELOPER_G1_STOP","manifest":"delivery_manifest_r02.json","manifest_sha256":sha(manifest),"source_freeze_sha256":sha(evidence/"source_freeze.json"),"files":len(v["files"]),"source_bindings_unchanged":len(freeze["source_sha256"]),"checks":records}
(work/"final_r02_native_delivery.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
