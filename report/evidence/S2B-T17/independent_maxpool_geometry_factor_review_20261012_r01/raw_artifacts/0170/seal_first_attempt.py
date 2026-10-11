"""冻结功能审查；包装检查与功能结果分别记录，缓存不纳raw清单。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

base=Path(__file__).absolute().parent
root=Path.cwd().resolve()
result=json.loads((base/"attempt2/review_result.json").read_text(encoding="utf-8"))
assert result["status"]=="PASS"
entries={x["path"]:x for x in json.loads((base/"attempt2/review_inputs.json").read_text(encoding="utf-8"))}
def sha(path):
    obj=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):obj.update(chunk)
    return obj.hexdigest()
def bind(path,role="input"):
    assert path.is_file()
    relative=path.relative_to(root).as_posix()
    entries[relative]={"path":relative,"sha256":sha(path),"role":role}
def load(path,role="input"):
    bind(path,role)
    return json.loads(path.read_text(encoding="utf-8"))
g1=root/"report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r02"
freeze=load(g1/"source_freeze.json")
assert all(sha(root/path)==value for path,value in freeze["modified_files"].items())
budget=load(g1/"execution_raw/budget_repair_receipt.json")
assert budget["guard_combined_cache_limit_bytes"]==671088640 and budget["rss_limit_bytes"]==1073741824
cache=root/"tmp/2B/S2B-T17/maxpool_geometry_factor_20261012_r02/rtl_run"
assert cache.is_dir()
cache_sum=sum(x.stat().st_size for directory in (cache/"obj_geometry",cache/"obj_engine") for x in directory.rglob("*") if x.is_file())
assert cache_sum==582754459
guard_native=load(g1/"execution_raw/guard_native.json","log")
backend_native=load(g1/"execution_raw/backend_native.json","log")
assert guard_native["native_exit_code"]==backend_native["native_exit_code"]==0
assert guard_native["peak_tree_rss_bytes"]==742223872 and backend_native["peak_tree_rss_bytes"]==702812160
fields=[list(map(lambda x:int(x,16),line.split())) for line in (base/"attempt2/rtl/independent_vectors.dat").read_text(encoding="utf-8").splitlines()]
coverage={"success_33bit_extent":sum(x[12]==0 and (x[13]>2**32-1 or x[14]>2**32-1) for x in fields),"success_9tap":sum(x[12]==0 and x[15]==9 for x in fields),"success_all_padding":sum(x[12]==0 and x[16]==0 for x in fields),"success_negative_signed_coordinate":sum(x[12]==0 and any(x[i]>=2**63 for i in range(19,53,4)) for x in fields),"kernel2_unused_third_row_high":fields[0][12]==0}
assert all(coverage.values()),coverage
with (base/"supplemental_result.json").open("x",encoding="utf-8") as stream:json.dump({"coverage":coverage,"current_readonly_g1_cache_bytes":cache_sum,"cache_scope":"只读现存两编译缓存总量，核ROOT声明，不把缓存纳长期raw；不是连续峰","source_eight_rechecked":True},stream,ensure_ascii=False,indent=2)
checker_commands=[]
for label,manifest in (("g1",g1/"delivery_manifest.json"),("trace",root/"report/evidence/S2B-T17/maxpool_geometry_factor_trace_20261012_r01/delivery_manifest.json")):
    for mode in ("evidence","inputs"):
        command=[sys.executable,"-B","-X","utf8",str(root/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(manifest),"--project-root",str(root)]
        start=time.monotonic()
        with (base/(label+"_"+mode+".stdout.log")).open("xb") as so,(base/(label+"_"+mode+".stderr.log")).open("xb") as se:native=subprocess.run(command,stdout=so,stderr=se)
        row={"command":command,"native_exit_code":native.returncode,"elapsed_seconds":time.monotonic()-start}
        with (base/(label+"_"+mode+".native.json")).open("x",encoding="utf-8") as stream:json.dump(row,stream,ensure_ascii=False,indent=2)
        checker_commands.append(row)
        assert native.returncode==(0 if mode=="evidence" else 2)
first=load(base/"review.native.json","log")
final=load(base/"review_attempt2.native.json","log")
assert first["native_exit_code"]==1 and final["native_exit_code"]==0
for path in base.rglob("*"):
    if path.is_file() and not any(part.startswith("obj_") for part in path.relative_to(base).parts):
        assert path.suffix.lower() not in {".exe",".obj",".dcp",".bit",".pyc"}
        bind(path,"source" if path.suffix in {".py",".sv"} else "log" if path.suffix==".log" else "input" if path.suffix==".dat" else "result")
manifest=base/"raw_manifest.jsonl"
with manifest.open("x",encoding="utf-8",newline="\n") as stream:
    for row in sorted(entries.values(),key=lambda x:x["path"]):
        assert set(row)=={"path","sha256","role"}
        stream.write(json.dumps(row,ensure_ascii=False)+"\n")
receipt=dict(result)
receipt.update({"checks":len(result["checks"])+6,"supplemental_checks":["八源收尾SHA仍冻结一致","G1真实cache582754459B与640MiB诊断授权、原生峰一致","独立RTL覆盖33extent/9tap/负signed/allpadding/未用第三行","G1与trace evidence0/inputs2仅包装","reviewer首轮KeyError原生1原件保留","修正新attempt2真实原生0"],"coverage":coverage,"g1_actual_cache_bytes":cache_sum,"reviewer_auxiliary_failure":{"native_exit_code":1,"evidence":"review.stderr.log","cause":"独立小UP矩阵误引用不存在的output_channels公开输入；改由input_channels及stride推导","candidate_changed":False},"commands":result["commands"]+checker_commands+[first,final],"raw_manifest_sha256":sha(manifest),"raw_manifest_lines":len(entries),"reviewer_stop":"STOP_READONLY_S11_GEO_REVIEW_FROZEN"})
path=base/"final_review_receipt.json"
with path.open("x",encoding="utf-8",newline="\n") as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write("\n")
print(json.dumps({"status":"PASS","STOP":True,"receipt_sha256":sha(path),"raw_manifest_sha256":sha(manifest),"raw_manifest_lines":len(entries)},ensure_ascii=False))
