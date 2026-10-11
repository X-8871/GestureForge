"""只归档已STOP的final-pins独审RAW，外部大包仅精确引用。"""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
BASE="09b4c6f60fb74c2fda1b56d2f316ca374dfae7cf"
ORIGINAL=ROOT/"tmp/2B/S2B-T17/independent_s12_final_pins_review_20261012_r01"
FORMAL=ROOT/"report/evidence/S2B-T17/independent_s12_final_pins_review_20261012_r01"
UP=ROOT/"report/evidence/S2B-T17/s12_source_preflight_20261012_r02"
MAIN=ROOT/"report/evidence/S2B-T17/s12_timing_cones_20261012_r01"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding="utf-8"))
git=["git","-c","core.longpaths=true","-c","maintenance.auto=false","rev-parse","HEAD"]
assert subprocess.check_output(git,cwd=ROOT,text=True).strip()==BASE
assert ORIGINAL.is_dir() and not ORIGINAL.is_symlink() and FORMAL.parent.is_dir() and not FORMAL.exists()
assert sha(ORIGINAL/"final_review_receipt.json")=="3e50f8ed70c54066d0cfb11a05780e3861ea6b4a7d043ec2f11d5859692ae38b"
assert sha(ORIGINAL/"raw_index.jsonl")=="48a4caf57782738c815881c69557f5ec4c85a2b0a2de4236962520c0733ba81d"
review=read(ORIGINAL/"final_review_receipt.json");seal=read(ORIGINAL/"seal.json")
assert review["status"]=="PASS_FINAL_PINS_G2_ONLY" and review["stop"] is True and review["source_commit"]==BASE
assert seal["status"]=="STOP_FROZEN_REVIEW" and seal["source_commit"]==BASE and seal["raw_files"]==209
for name in ("receipt","raw_index"):
    row=seal[name];p=Path(row["path"]);assert p.parent==ORIGINAL and sha(p)==row["sha256"] and p.stat().st_size==row["bytes"]
indexed=[json.loads(s) for s in (ORIGINAL/"raw_index.jsonl").read_text(encoding="utf-8").splitlines()]
assert len(indexed)==209
paths=[]
for row in indexed:
    p=Path(row["path"]);assert p.is_file() and not p.is_symlink() and p.is_relative_to(ORIGINAL)
    assert sha(p)==row["sha256"] and p.stat().st_size==row["bytes"];paths.append(p)
assert len(set(paths))==209
all_paths=sorted(set(paths)|{ORIGINAL/"raw_index.jsonl",ORIGINAL/"seal.json",ORIGINAL/"final_review_receipt.json"})
assert {p for p in ORIGINAL.rglob("*") if p.is_file()}==set(all_paths)
refs={}
for row in review["frozen_input_bindings"]:
    p=Path(row["path"]);assert p.is_file() and sha(p)==row["sha256"] and p.stat().st_size==row["bytes"]
    refs[p.relative_to(ROOT).as_posix()]=row["sha256"]
assert sha(UP/"delivery_manifest.json")=="e312b08f61bc1b0a3afe6a52a8a3b80df804b72434c15a498508a03edaff70be"
upstream=read(UP/"delivery_manifest.json")
for row in upstream["files"]:
    p=ROOT/row["path"];assert p.is_file() and sha(p)==row["sha256"];refs[row["path"]]=row["sha256"]
freeze=read(UP/"source_freeze.json");assert len(freeze["source_files"])==43
sources={r["path"]:r["sha256"] for r in freeze["source_files"]};assert {p:sha(ROOT/p) for p in sources}==sources
source16=read(MAIN/"source_freeze.json")["modified_files"];assert len(source16)==16 and {p:sha(ROOT/p) for p in source16}==source16
tool_root=Path(review["reviewed_work_directory"]);tools={str(tool_root/r["path"]):r["sha256"] for r in review["tools"]}
assert len(tools)==6 and {p:sha(Path(p)) for p in tools}==tools
functional=ROOT/"report/evidence/S2B-T17/independent_s12_functional_review_20261012_r01"
dependent={MAIN/"delivery_manifest_r02.json":"2c8e3bd56c1c288333f168a767aadf8b7067f2450e97c25709f271553772ed54",functional/"raw/final_review_receipt.json":"e6e4dd2b77a31b55d12b4fe4c1cc1ab1d4905fd3fbf9b4e045dffb38dbf79129",functional/"delivery_manifest.json":"54c278e530fa9f80ccb3c9fa94ff645583dfa7832b4974a3e225547fafe14d8a"}
for p,h in dependent.items():assert p.is_file() and sha(p)==h;refs[p.relative_to(ROOT).as_posix()]=h
assert [r["native_exit_code"] for r in review["native_records"]]==[1,0,0,0,2]
ast.parse(Path(__file__).read_text(encoding="utf-8"));began=time.monotonic();FORMAL.mkdir();mapping=[]
for p in all_paths:
    relative=p.relative_to(ORIGINAL);target=FORMAL/"raw"/relative
    assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    assert sha(p)==sha(target)
    mapping.append({"original_absolute_path":str(p),"archive_path":target.relative_to(ROOT).as_posix(),"sha256":sha(target),"bytes":target.stat().st_size,"indexed":p in paths})
def write(name,value):
    """创建UTF-8新证据，禁止覆盖历史产物。"""
    with (FORMAL/name).open("x",encoding="utf-8",newline="\n") as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write("\n")
write("recovery_mapping.json",mapping)
write("recovery_dependencies.json",{"status":"RAW_RECOVERY_INFORMATION_ONLY","original_cwd":str(ROOT),"original_review_directory":str(ORIGINAL),"index_count":209,"deduplicated_recovery_count":len(mapping),"count_explanation":"209索引明确不含随后生成receipt及seal；额外raw_index/receipt/seal按实际去重，因此212，不伪造211。","source_commit":BASE,"original_interpreter":review["native_records"][1]["command"][0],"scripts":"原审查脚本与夹具按mapping原相对布局恢复；其固定项目cwd和sourcepre r02依赖路径保持。此归档不运行审查，禁止覆盖尚存在的原目录重放。","external_references":"sourcepre现有有效绑定/功能G2及主G1仅引用，未恢复/复制其大数据；恢复脚本须另具备这些精确固定依赖。","sourcepre_manifest_sha256":sha(UP/"delivery_manifest.json"),"sourcepre_binding_count":len(upstream["files"]),"sourcepre_freeze_sha256":sha(UP/"source_freeze.json"),"sourcepre_tools":tools})
shutil.copyfile(Path(__file__),FORMAL/"archive.py")
limits=["archiver只PACKAGING_PASS；原PASS_FINAL_PINS_G2_ONLY/scope/source_commit09b4保持原字节，不扩大为物理预算/时序或板上通过。","209 indexed RAW加index/receipt/seal实际去重212件；主G1/功能G2/sourcepre240有效绑定只引用，不复制约25MB、不伪称恢复。","原Reviewer p.sha误用native1、新audit_r02 native0、21正负、37RAW+6明确EOL、checker0/2及UNKNOWN1全部RAW保留，连续OS绝对峰null，不把UNKNOWN轻量采样当重型预算PASS。","原真实物理准入BLOCKED，启动须ROOT重新满足4.5GiB RAM及C8GiB门槛；新actual预算/综合/STA/PNR未执行，G3/G5阻断不改判。","无RTL/Vivado/ROSS/硬件/进程停止或Git/STATE写；工具6/source43/生产16/sourcefreeze均前后绑定。"]
write("archive_receipt.json",{"status":"PACKAGING_PASS","source_commit":BASE,"review_status":review["status"],"review_receipt_sha256":sha(FORMAL/"raw/final_review_receipt.json"),"source_index_sha256":sha(FORMAL/"raw/raw_index.jsonl"),"indexed_count":209,"recovery_count":len(mapping),"raw_bytes":sum(r["bytes"] for r in mapping),"recovery_sha256":sha(FORMAL/"recovery_mapping.json"),"source43_pre":sources,"source43_post":{p:sha(ROOT/p) for p in sources},"source16_pre":source16,"source16_post":{p:sha(ROOT/p) for p in source16},"tools6_pre":tools,"tools6_post":{p:sha(Path(p)) for p in tools},"source_freeze_sha256":sha(UP/"source_freeze.json"),"archive_command":subprocess.list2cmdline([sys.executable,"-X","utf8","-B",str(Path(__file__).resolve())]),"archive_script_sha256":sha(Path(__file__)),"seconds":time.monotonic()-began,"limitations":limits})
files=[]
for p in sorted(FORMAL.rglob("*")):
    if p.is_file():files.append({"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"role":"source" if p.suffix in (".py",".sv",".tcl") else "log" if p.suffix in (".log",".jsonl") else "result"})
files.extend({"path":p,"sha256":h,"role":"input"} for p,h in refs.items())
assert len({r["path"] for r in files})==len(files)
checks=[{"name":"独审初audit fixture失败","status":"FAIL","command":subprocess.list2cmdline(review["native_records"][0]["command"]),"exit_code":1,"reason":"最初p.sha误用测试夹具失败，原件保留，不追认或称物理设计失败。"}]
for i in (1,2,3,4):
    r=review["native_records"][i];checks.append({"name":"独审实际native记录"+str(i),"status":"PASS" if r["native_exit_code"]==0 else "FAIL","command":subprocess.list2cmdline(r["command"]),"exit_code":r["native_exit_code"],"reason":"原独立实际轻量检查码；inputs2是未冻结/未执行/历史失败阻断，不能作重型预算或STA批准。"})
checks.append({"name":"实际物理准入","status":"BLOCKED","command":None,"exit_code":None,"reason":"原准入RAM低于4.5GiB；ROOT须启动前重核，本归档不派发heavy。"})
checks.extend({"name":n,"status":"NOT_RUN","command":None,"exit_code":None,"reason":"final-pins逻辑独审未执行该真实物理/实板关口。"} for n in ("S12 synthesis","S12 STA","S12 PNR","G3","G5"))
write("delivery_manifest.json",{"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":FORMAL.name,"source_commit":BASE,"evidence_dir":FORMAL.relative_to(ROOT).as_posix(),"interfaces":upstream["interfaces"],"files":files,"checks":checks,"tool_versions":{"Python312":sys.version,"archiver":"S12-FINAL-PINS-G2-ARCHIVE01/1"},"limitations":limits})
assert {p:sha(ROOT/p) for p in sources}==sources and {p:sha(ROOT/p) for p in source16}==source16 and {p:sha(Path(p)) for p in tools}==tools
assert subprocess.check_output(git,cwd=ROOT,text=True).strip()==BASE
assert sha(UP/"source_freeze.json")=="0de84aeabee7b87c5246bba57624e108b8fe32cb0aa5b49a8eb55af7ced3d2a4"
print(json.dumps({"status":"PACKAGING_PASS_CHECKS_PENDING","manifest_sha256":sha(FORMAL/"delivery_manifest.json"),"receipt_sha256":sha(FORMAL/"archive_receipt.json"),"recovery_sha256":sha(FORMAL/"recovery_mapping.json"),"source_index_sha256":sha(FORMAL/"raw/raw_index.jsonl"),"indexed_count":209,"recovery_count":len(mapping),"formal_bindings":len(files)},ensure_ascii=False),flush=True)
