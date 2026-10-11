"""归档已STOP独审自身RAW；仅封包，不重跑审查或修改被审来源。"""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
ORIGINAL=ROOT/"tmp/2B/S2B-T17/independent_s12_functional_review_20261012_r01"
FORMAL=ROOT/"report/evidence/S2B-T17/independent_s12_functional_review_20261012_r01"
MAIN=ROOT/"report/evidence/S2B-T17/s12_timing_cones_20261012_r01"
RQ=ROOT/"report/evidence/S2B-T17/s12_requant_rtl_20261012_r01/delivery_manifest_r02.json"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert ORIGINAL.is_dir() and not ORIGINAL.is_symlink() and FORMAL.parent.is_dir() and not FORMAL.exists()
assert sha(ORIGINAL/"final_review_receipt.json")=="e6e4dd2b77a31b55d12b4fe4c1cc1ab1d4905fd3fbf9b4e045dffb38dbf79129"
assert sha(ORIGINAL/"raw_index.jsonl")=="ac8ee8f18964937f94a17a0d0b9834ce270aa9074200f0449b8c784f1e3f5002"
review=json.loads((ORIGINAL/"final_review_receipt.json").read_text(encoding="utf-8"))
assert review["status"]=="PASS" and review["reviewer_stop"]=="STOP_NO_FURTHER_WRITES"
assert review["checks"]["controlled_multidriven"]==262
assert review["diagnostic_correction"]["entries"]==62 and review["diagnostic_correction"]["unique_private_signals"]==31
rows=[json.loads(s) for s in (ORIGINAL/"raw_index.jsonl").read_text(encoding="utf-8").splitlines()]
assert len(rows)==35
paths=[]
for row in rows:
    path=Path(row["path"]);assert path.is_file() and not path.is_symlink() and path.parent==ORIGINAL
    assert sha(path)==row["sha256"] and path.stat().st_size==row["bytes"];paths.append(path)
assert len(set(paths))==35 and set(ORIGINAL.iterdir())==set(paths)|{ORIGINAL/"raw_index.jsonl"}
fixed={"delivery_manifest_r02.json":"2c8e3bd56c1c288333f168a767aadf8b7067f2450e97c25709f271553772ed54","source_freeze.json":"eadf373c59420aa234a5e6394c9ca08066b480bdde6263f91600cf21bbbe02c7","g1_summary.json":"0674603c86f92762d172085323fdd0328d7a364735a87b45e389f0ede9d19549","source_diff.patch":"6be9a040c20520403532aec5a2626292f93b8b91845b21d883b69dae2ceb0a5d"}
assert all(sha(MAIN/p)==h for p,h in fixed.items())
sources=review["modified_files"];assert len(sources)==16 and {p:sha(ROOT/p) for p in sources}==sources
assert sha(RQ)=="00358f98fe4d2584b5a0d2275fc3f9249b7caeb8d06229145234dc53392fca2d"
rq=json.loads(RQ.read_text(encoding="utf-8"));assert len(rq["files"])==65
for row in rq["files"]:assert (ROOT/row["path"]).is_file() and sha(ROOT/row["path"])==row["sha256"]
native=json.loads((ORIGINAL/"native_checker_receipt.json").read_text(encoding="utf-8"))
assert [r["native_exit_code"] for r in native["runs"]]==[0,2]
ast.parse(Path(__file__).read_text(encoding="utf-8"));start=time.monotonic();FORMAL.mkdir();raw=FORMAL/"raw";raw.mkdir();mapping=[]
for path in [*paths,ORIGINAL/"raw_index.jsonl"]:
    target=raw/path.name;assert not target.exists();shutil.copyfile(path,target);assert sha(path)==sha(target)
    mapping.append({"original_absolute_path":str(path),"archive_path":target.relative_to(ROOT).as_posix(),"sha256":sha(target),"bytes":target.stat().st_size})
def write(name,value):
    """只创建UTF-8新文件，禁止覆盖已有证据。"""
    with (FORMAL/name).open("x",encoding="utf-8",newline="\n") as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")
write("recovery_mapping.json",mapping)
write("recovery_dependencies.json",{"status":"RAW_RECOVERY_INFORMATION_ONLY","original_cwd":str(ROOT),"original_review_directory":str(ORIGINAL),"raw_count":36,"script_dependencies":"原脚本采用项目cwd及固定tmp审查目录；按36映射恢复到原精确路径后依赖保持。不得在已存在目录覆盖执行；此归档不运行脚本。其他依赖只引用未复制。","interpreter":native["interpreter"],"python_version":native["python"],"libraries":"Python标准库；部分旧夹具依赖psutil，缺库原生失败原件保留。","main_dependency":{"paths":fixed,"mode":"真实现有引用，不宣称731件G1数据已恢复。"},"requant_dependency":{"manifest":RQ.relative_to(ROOT).as_posix(),"manifest_sha256":sha(RQ),"referenced_bindings":65,"mode":"真实现有引用，不复制、不伪恢复。"}})
shutil.copyfile(Path(__file__),FORMAL/"archive.py")
limits=["独审原receipt PASS/scope不改；archiver只PACKAGING_PASS。source_baseline891是precommit基线，43候选RAW/16修改尚未提交，不填虚构新sourcecommit。","35ownRAW+raw_index共36精确恢复；G1主manifest/freeze/summary/diff及RQ65仅引用，不伪称恢复其数据。","262实际MULTIDRIVEN及cones31private信号×lint/compile=62 reported_location与旧登记错配的独立补充映射完整保留；不能声称旧登记完全精确。","缺psutil初失败、bundledPython WinError5/native2是环境故障原件，正确Python312独立evidence0/inputs2也保存，不把环境2当设计失败。","功能G2批准不代表STA/预算物理准入/109整网/G3/G4/G5；本次无RTL/Vivado/设备或Git写。"]
write("archive_receipt.json",{"status":"PACKAGING_PASS","source_baseline":review["source_baseline"],"source_role":review["source_role"],"review_status":review["status"],"review_scope":review["scope"],"review_receipt_sha256":sha(raw/"final_review_receipt.json"),"recovery_rows":36,"recovery_mapping_sha256":sha(FORMAL/"recovery_mapping.json"),"source16_pre":sources,"source16_post":{p:sha(ROOT/p) for p in sources},"review_raw_bytes":sum(r["bytes"] for r in mapping),"archive_command":subprocess.list2cmdline([sys.executable,"-X","utf8","-B",str(Path(__file__).resolve())]),"archive_script_sha256":sha(Path(__file__)),"seconds":time.monotonic()-start,"limitations":limits})
files=[]
for path in sorted(FORMAL.rglob("*")):
    if path.is_file():files.append({"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path),"role":"source" if path.suffix==".py" else "log" if path.suffix in (".log",".jsonl") else "result"})
for p,h in fixed.items():files.append({"path":(MAIN/p).relative_to(ROOT).as_posix(),"sha256":h,"role":"input"})
files.append({"path":RQ.relative_to(ROOT).as_posix(),"sha256":sha(RQ),"role":"input"})
files.extend({"path":r["path"],"sha256":r["sha256"],"role":"input"} for r in rq["files"])
assert len({r["path"] for r in files})==len(files)
checks=[{"name":"独审Python312实际evidence","status":"PASS","command":subprocess.list2cmdline(native["runs"][0]["command"]),"exit_code":0,"reason":"原始独立包装检查实际0，不是自报review0。"},{"name":"独审Python312实际inputs","status":"FAIL","command":subprocess.list2cmdline(native["runs"][1]["command"]),"exit_code":2,"reason":"原接口未冻结/历史FAIL/当时整体G2未执行阻断，失败原件保留。"}]
checks.extend({"name":name,"status":"NOT_RUN","command":None,"exit_code":None,"reason":"功能独审不覆盖该实际关口。"} for name in ("S12 STA","G3","G5"))
main=json.loads((MAIN/"delivery_manifest_r02.json").read_text(encoding="utf-8"))
write("delivery_manifest.json",{"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":FORMAL.name,"source_commit":review["source_baseline"],"evidence_dir":FORMAL.relative_to(ROOT).as_posix(),"interfaces":main["interfaces"],"files":files,"checks":checks,"tool_versions":{"Python312":native["python"],"archiver":"S12-FUNCTIONAL-G2-ARCHIVE01/1"},"limitations":limits})
assert {p:sha(ROOT/p) for p in sources}==sources and all(sha(MAIN/p)==h for p,h in fixed.items())
assert sha(ORIGINAL/"final_review_receipt.json")==sha(raw/"final_review_receipt.json") and sha(ORIGINAL/"raw_index.jsonl")==sha(raw/"raw_index.jsonl")
print(json.dumps({"status":"PACKAGING_PASS_CHECKS_PENDING","manifest_sha256":sha(FORMAL/"delivery_manifest.json"),"receipt_sha256":sha(FORMAL/"archive_receipt.json"),"review_receipt_sha256":sha(raw/"final_review_receipt.json"),"recovery_sha256":sha(FORMAL/"recovery_mapping.json"),"recovery_rows":36,"manifest_bindings":len(files),"source16_unchanged":True},ensure_ascii=False),flush=True)
