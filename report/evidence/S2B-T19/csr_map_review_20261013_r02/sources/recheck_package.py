"""保留沙箱包装失败，提升只读路径枚举后封存并复核目录。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
ROOT=Path(__file__).absolute().parents[4]
OUT=ROOT/"report/evidence/S2B-T19/csr_map_review_20261013_r02"
TEMP=Path(__file__).parent
def bind(file):return {"path":str(file),"sha256":hashlib.sha256(file.read_bytes()).hexdigest(),"bytes":file.stat().st_size}
def write(file,value):
    with file.open("x",encoding="utf-8",newline="\n") as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")
target=OUT/"sources"/Path(__file__).name
with target.open("xb") as stream:stream.write(Path(__file__).read_bytes())
command=[sys.executable,"-X","utf8","-B","verification/check_stage_delivery.py","--mode","evidence","--manifest",(OUT/"delivery_manifest.json").relative_to(ROOT).as_posix()]
manifest=OUT/"delivery_manifest.json"
def update():
    data=json.loads(manifest.read_text(encoding="utf-8"))
    data["files"]=[{"path":file.relative_to(ROOT).as_posix(),"sha256":bind(file)["sha256"],"role":"source" if file.suffix==".py" or file.name.endswith(".snapshot") else "result","keep_reason":"保存独立软件审查、原件失败和可复核源码。"} for file in OUT.rglob("*") if file.is_file() and file!=manifest]
    with manifest.open("w",encoding="utf-8",newline="\n") as stream:json.dump(data,stream,ensure_ascii=False,indent=2);stream.write("\n")
update()
check=subprocess.run(command,cwd=ROOT,capture_output=True)
(OUT/"evidence_check_r02_stdout.log").write_bytes(check.stdout)
(OUT/"evidence_check_r02_stderr.log").write_bytes(check.stderr)
write(OUT/"evidence_check_r02_execution.json",{"command":command,"native_exit_code":check.returncode})
assert check.returncode==0,check.stdout+check.stderr
receipt=json.loads((OUT/"final_review_receipt_r02.json").read_text(encoding="utf-8"))
receipt["checks"]["evidence_manifest_checker"]="CHECKS_OK_NATIVE_0"
receipt["commands"].append({"command":command,"exit_code":0})
receipt["independent_drivers"].append(bind(target))
receipt["supplements"]["finalization_driver_copy"]={"source":bind(Path(__file__)),"copy":bind(target)}
receipt["limitations"].append("首次evidence检查native2为沙箱祖先枚举拒绝；原始stdout/stderr/exit保存，提升只读枚举后的真实checker0分列。")
write(OUT/"final_review_receipt_r03.json",receipt)
update()
final=subprocess.run(command,cwd=ROOT,capture_output=True)
(TEMP/"final_evidence_check_r03_stdout.log").write_bytes(final.stdout)
(TEMP/"final_evidence_check_r03_stderr.log").write_bytes(final.stderr)
assert final.returncode==0,final.stdout+final.stderr
print(final.stdout.decode("utf-8"))
print(json.dumps({"status":"PASS_G2_SOFTWARE_ONLY","receipt":bind(OUT/"final_review_receipt_r03.json"),"manifest":bind(manifest),"checker_native_exit_code":final.returncode},ensure_ascii=False))
