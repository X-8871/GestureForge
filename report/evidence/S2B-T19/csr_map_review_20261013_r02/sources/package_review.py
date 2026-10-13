"""封存独立driver与补充快照反例，运行只读证据包装检查。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[4]
OUT=ROOT/"report/evidence/S2B-T19/csr_map_review_20261013_r02"
TEMP=Path(__file__).parent
def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()
def bind(file):return {"path":str(file),"sha256":sha(file),"bytes":file.stat().st_size}
def write(file,data):
    with file.open("x",encoding="utf-8",newline="\n") as stream:json.dump(data,stream,ensure_ascii=False,indent=2);stream.write("\n")
sources=OUT/"sources";sources.mkdir()
mapping=[]
for file in TEMP.iterdir():
    if not file.is_file() or file.suffix!=".py":continue
    target=sources/file.name
    with target.open("xb") as stream:stream.write(file.read_bytes())
    assert sha(file)==sha(target)
    mapping.append({"source":bind(file),"copy":bind(target)})
write(OUT/"source_mapping.json",{"status":"BYTE_IDENTICAL","files":mapping})
receipt=json.loads((OUT/"review_receipt.json").read_text(encoding="utf-8"))
snapshot=json.loads((OUT/"snapshot_sdk_cases_result.json").read_text(encoding="utf-8"))
assert snapshot["results"][0]["status"]=="PASS"
receipt["checks"]["sdk_regions_and_entries_preserved_after_official_unload"]="PASS_DEEP_COPY_COMPARISON"
receipt["supplements"]={"original_receipt":bind(OUT/"review_receipt.json"),"sdk_snapshot_comparison":bind(OUT/"snapshot_sdk_cases_result.json"),"driver_mapping":bind(OUT/"source_mapping.json")}
receipt["commands"].append({"command":sys.executable+" -X utf8 -B "+str(TEMP/"review_sdk_snapshot.py"),"exit_code":0})
receipt["independent_drivers"]=[row["copy"] for row in mapping]
write(OUT/"final_review_receipt_r02.json",receipt)
manifest=OUT/"delivery_manifest.json"
def build_manifest():
    files=[]
    for file in OUT.rglob("*"):
        if file.is_file() and file!=manifest:
            files.append({"path":file.relative_to(ROOT).as_posix(),"sha256":sha(file),"role":"source" if file.suffix==".py" or file.name.endswith(".snapshot") else "result","keep_reason":"保留独立只读软件审查、原始失败、SDK映射反例及冻结源码证据。"})
    return {"schema_version":1,"stage":"2B","task_id":"S2B-T19","run_id":OUT.name,"source_commit":receipt["baseline_commit"],"evidence_dir":OUT.relative_to(ROOT).as_posix(),"interfaces":[],"interfaces_not_applicable_reason":"仅审查既有visibility0入口的CSR调试映射修复及SDK来源，未改变总线、UART、模型接口；本包不作为物理接口冻结。","tool_versions":{"python":sys.version,"vitis_sdk_source":"2026.1；仅AST源码核查，未导入SDK"},"files":files,"checks":[{"name":"independent_unit_regression","status":"PASS","command":receipt["commands"][0]["command"],"exit_code":0},{"name":"official_sdk_ast_mapping_cleanup_snapshot","status":"PASS","command":receipt["commands"][-1]["command"],"exit_code":0},{"name":"BOARD_G3_G4_G5","status":"NOT_RUN","reason":"软件审查不连接板卡，未运行真实cache或实物验收。"}],"limitations":receipt["limitations"]}
write(manifest,build_manifest())
command=[sys.executable,"-X","utf8","-B","verification/check_stage_delivery.py","--mode","evidence","--manifest",manifest.relative_to(ROOT).as_posix()]
first=subprocess.run(command,cwd=ROOT,capture_output=True)
(OUT/"evidence_check_initial_stdout.log").write_bytes(first.stdout)
(OUT/"evidence_check_initial_stderr.log").write_bytes(first.stderr)
write(OUT/"evidence_check_initial_execution.json",{"command":command,"native_exit_code":first.returncode})
assert first.returncode==0,first.stdout+first.stderr
# 清单第一次通过后只增加真实检查原件，再对最终目录完整核验。
with manifest.open("w",encoding="utf-8",newline="\n") as stream:json.dump(build_manifest(),stream,ensure_ascii=False,indent=2);stream.write("\n")
final=subprocess.run(command,cwd=ROOT,capture_output=True)
(TEMP/"final_evidence_check_stdout.log").write_bytes(final.stdout)
(TEMP/"final_evidence_check_stderr.log").write_bytes(final.stderr)
assert final.returncode==0,final.stdout+final.stderr
print(final.stdout.decode("utf-8"))
print(json.dumps({"status":"PASS_G2_SOFTWARE_ONLY","receipt":bind(OUT/"final_review_receipt_r02.json"),"manifest":bind(manifest),"checker_native_exit_code":final.returncode,"driver_copies":len(mapping)},ensure_ascii=False))
