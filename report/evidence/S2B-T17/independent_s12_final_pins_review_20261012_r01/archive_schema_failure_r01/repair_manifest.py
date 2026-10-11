"""仅复制上游原接口N/A说明至新r02，保留首次归档包装失败。"""
import hashlib
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FORMAL=ROOT/"report/evidence/S2B-T17/independent_s12_final_pins_review_20261012_r01"
OLD=FORMAL/"delivery_manifest.json";NEW=FORMAL/"delivery_manifest_r02.json"
UP=ROOT/"report/evidence/S2B-T17/s12_source_preflight_20261012_r02/delivery_manifest.json"
CAP=HERE/"capture";RAW=FORMAL/"archive_schema_failure_r01"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert FORMAL.is_dir() and CAP.is_dir() and not NEW.exists() and not RAW.exists()
assert sha(OLD)=="829a5fb3dc8f3faee9873f0d2449c5da8a87432c0f5576994c2f915355cb0341"
assert sha(UP)=="e312b08f61bc1b0a3afe6a52a8a3b80df804b72434c15a498508a03edaff70be"
old=json.loads(OLD.read_text(encoding="utf-8"));up=json.loads(UP.read_text(encoding="utf-8"))
assert old["interfaces"]==up["interfaces"]==[] and isinstance(up["interfaces_not_applicable_reason"],str) and up["interfaces_not_applicable_reason"]
native=json.loads((CAP/"native_receipt.json").read_text(encoding="utf-8"))
assert [r["native_returncode"] for r in native["runs"]]==[0,2,2]
assert native["status"]=="FAILED_PARTIAL_PRESERVED" and native["source43_stable"] is True
RAW.mkdir();mapping=[]
for p in sorted(CAP.iterdir()):
    assert p.is_file();target=RAW/p.name;shutil.copyfile(p,target);assert sha(p)==sha(target)
    mapping.append({"original_absolute_path":str(p),"archive_path":target.relative_to(ROOT).as_posix(),"sha256":sha(target),"bytes":target.stat().st_size})
shutil.copyfile(Path(__file__),RAW/Path(__file__).name)
def write(path,value):
    """创建新UTF-8证据，禁止覆盖原件。"""
    with path.open("x",encoding="utf-8",newline="\n") as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write("\n")
write(RAW/"raw_restore_mapping.json",mapping)
write(RAW/"repair_note.json",{"scope":"仅补上游原interfaces_not_applicable_reason及绑定首次失败，所有原review/源/工具/原清单保留。","upstream_sha256":sha(UP),"original_manifest_sha256":sha(OLD),"original_interface_NA":up["interfaces_not_applicable_reason"],"original_codes":{"archive":0,"evidence":2,"inputs":2,"outer_capture":1},"original_error":"interfaces为空时必须提供interfaces_not_applicable_reason；不是逻辑/物理设计失败。","repair_script_sha256":sha(Path(__file__)),"limits":"不重复RAW归档/Reviewer/RTL，不把新包装0追認原失败。物理准入/STA/PNR/G3/G5状态不变。"})
new=json.loads(OLD.read_text(encoding="utf-8"));new["interfaces_not_applicable_reason"]=up["interfaces_not_applicable_reason"]
files={r["path"]:r for r in new["files"]}
files[OLD.relative_to(ROOT).as_posix()]={"path":OLD.relative_to(ROOT).as_posix(),"sha256":sha(OLD),"role":"diagnostic"}
for p in sorted(RAW.rglob("*")):
    if p.is_file():files[p.relative_to(ROOT).as_posix()]={"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"role":"source" if p.suffix==".py" else "log" if p.suffix in (".log",".jsonl") else "result"}
new["files"]=list(files.values())
new["checks"].append({"name":"首次归档evidence包装失败","status":"FAIL","command":native["runs"][1]["command"],"exit_code":2,"reason":"仅漏上游原接口N/A说明；首次环境/包装失败原件保存，不解释为独审逻辑或物理失败。"})
new["limitations"].append("r02只补上游原接口N/A说明，原manifest/212review RAW/receipt/recovery映射不变；首次archive0/evidence2/inputs2/outer1保留，后续包装只分列当前结果。")
write(NEW,new)
assert sha(OLD)=="829a5fb3dc8f3faee9873f0d2449c5da8a87432c0f5576994c2f915355cb0341"
print(json.dumps({"status":"SCHEMA_NA_REPAIRED_CHECKS_PENDING","manifest_r02_sha256":sha(NEW),"manifest_bindings":len(files),"failure_raw_copied":len(mapping)},ensure_ascii=False),flush=True)
