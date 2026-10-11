"""按ROOT明确预算修复新运行包装；原失败和原件保持。"""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parent
OLD=WORK.parent/"maxpool_geometry_factor_20261012_r01"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ("run_stage.py","finalize.py"):
    source=OLD/name;text=source.read_text(encoding="utf-8")
    text=text.replace("maxpool_geometry_factor_20261012_r01","maxpool_geometry_factor_20261012_r02")
    if name=="run_stage.py":
        text=text.replace('cache_bytes>314572800','cache_bytes>(671088640 if stage=="guard" else 314572800)')
        text=text.replace("RSS_1G_OR_CACHE_300M_OR_1500S_OR_NO_PROGRESS_240S_OR_DISK_RAM_512M","RSS_1G_OR_CACHE_GUARD_640M_BACKEND_300M_OR_1500S_OR_NO_PROGRESS_240S_OR_DISK_RAM_512M")
    else:
        text=text.replace('<=314572800','<=(671088640 if s=="guard" else 314572800)')
        text=text.replace('1GiB/300MiB','1GiB/guard合计640MiB、backend300MiB')
        text=text.replace('外层1GiB/300MiB预算','外层1GiB；两个独立PCH编译合计640MiB、backend300MiB预算')
        marker='    runtime=main/"execution_raw";runtime.mkdir()'
        text=text.replace(marker,'''    failure=main/"r01_failed_raw";failure.mkdir()
    old=WORK.parent/"maxpool_geometry_factor_20261012_r01"
    for name in ("guard_native.json","guard_stderr.log","guard_stdout.log","guard_adapter.json","initial_source.json","run_stage.py"):
        copy(old/name,failure/name)
    old_evidence=ROOT/"report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r01"
    for name in ("geometry_compile.log","geometry_simulation.log","engine_compile.log"):
        copy(old_evidence/name,failure/name)
    copy(WORK/"budget_repair_receipt.json",failure/"budget_repair_receipt.json")
'''+marker)
        text=text.replace('"limitations":limits}','"r01_failure":{"native_exit_code":1,"reason":"旧300MiB合计缓存守卫真实失败，非设计失败，保留原判定。","cache_bytes_at_diagnosis":438587316,"geometry_vectors_pass":82591,"new_budget_authorization":"ROOT明确仅S11 guard两个独立编译合计640MiB，RSS1GiB与backend300MiB不变。"},"limitations":limits}',1)
    target=WORK/name;assert not target.exists();target.write_text(text,encoding="utf-8",newline="\n")
freeze=json.loads((ROOT/"report/evidence/S2B-T17/conv_feature_address_20261011_r01/source_freeze.json").read_text(encoding="utf-8"))
hashes={p["path"]:sha(ROOT/p["path"]) for p in freeze["source_files"]}
old=json.loads((OLD/"initial_source.json").read_text(encoding="utf-8"))
drift={p:{"r01":h,"r02":hashes[p]} for p,h in old["source_sha256_pre"].items() if hashes[p]!=h}
assert set(drift)=={"board/s2b_inference_platform.md"}
old["source_sha256_pre"]=hashes;old["new_wrapper_sha256"]=sha(WORK/"run_stage.py")
with (WORK/"initial_source.json").open("x",encoding="utf-8") as f:json.dump(old,f,ensure_ascii=False,indent=2)
receipt={"old_native_capture":{"path":(OLD/"guard_native.json").relative_to(ROOT).as_posix(),"sha256":sha(OLD/"guard_native.json")},"old_cache_diagnosis_bytes":438587316,"old_limit_bytes":314572800,"guard_combined_cache_limit_bytes":671088640,"backend_cache_limit_bytes":314572800,"rss_limit_bytes":1073741824,"authorization":"ROOT本任务明确授权640MiB仅两个独立编译PCH合计；不追认r01、不降低功能/时序指标。","metadata_drift_before_r02":drift,"reuse":"原runner必须一次完整运行；r02必要复跑82591全字段，不追加第三次。","wrapper_sha256":sha(WORK/"run_stage.py"),"finalizer_sha256":sha(WORK/"finalize.py")}
with (WORK/"budget_repair_receipt.json").open("x",encoding="utf-8") as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
print(json.dumps({"status":"PREPARED_R02","source_files":len(hashes),"guard_cache_limit_bytes":671088640,"wrapper_sha256":receipt["wrapper_sha256"]}))
