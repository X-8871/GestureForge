#!/usr/bin/env python3
"""保留首次封包失败，修正外部依赖角色并真实核验新清单。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parent
BASELINE="5ea54b441bd885e10eac4794cbad5ad48c510a49"
STAGES={"direct_r03":"conv_output_address_20261011_r03",
        "boundary":"conv_output_address_boundary_20261011_r01",
        "layer0":"conv_output_address_layer0_20261011_r01",
        "backend":"conv_output_address_trace_20261011_r01",
        "geometry":"conv_output_address_geometry_20261011_r01"}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding="utf-8"))


def write(path,value):
    """只创建新文件，禁止覆盖首次结果。"""
    with path.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write("\n")


def main():
    """清单角色不改变被测代码、刺激、黄金和冻结结果。"""
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==BASELINE
    evidence_parent=ROOT/"report/evidence/S2B-T17"
    assert evidence_parent.is_dir()
    main=evidence_parent/STAGES["direct_r03"]
    freeze=read(main/"source_freeze.json")
    hashes={x["path"]:x["sha256"] for x in freeze["source_files"]}
    assert len(hashes)==42 and all(sha(ROOT/p)==h for p,h in hashes.items())
    stable={name:sha(main/name) for name in ("source_freeze.json","source_diff.patch","g1_summary.json")}
    failure=main/"packaging_first_failure"
    assert not failure.exists()
    failure.mkdir()
    for name in ("finalize_native.json","finalize_stdout.log","finalize_stderr.log","direct_r03_evidence_native.json","capture_finalize.py"):
        source=WORK/name
        assert source.is_file()
        shutil.copyfile(source,failure/name)
    shutil.copyfile(Path(__file__),failure/"repair_packaging.py")
    first=read(failure/"finalize_native.json")
    first_check=read(failure/"direct_r03_evidence_native.json")
    assert first["native_exit_code"]==1 and first_check["native_exit_code"]==2
    write(main/"packaging_repair.json",{
        "status":"PREPARED_FOR_REAL_CHECK",
        "first_finalize_native_exit_code":1,"first_evidence_checker_native_exit_code":2,
        "reason":"首次清单将外部上游及历史运行依赖登记为result/log；新清单统一登记外部依赖为input，保留全部首次原件。",
        "first_manifest":"delivery_manifest.json","current_manifest":"delivery_manifest_r02.json",
        "source_freeze_unchanged":stable,"tested_source_drift":{},
        "scope":"仅证据角色封包修复；不重跑或改变RTL、刺激、黄金、功能判据。"})
    manifests={}
    for stage,runid in STAGES.items():
        evidence=evidence_parent/runid
        assert evidence.is_dir() and not (evidence/"delivery_manifest_r02.json").exists()
        manifest=read(evidence/"delivery_manifest.json")
        prefix=evidence.relative_to(ROOT).as_posix()+"/"
        files={}
        for entry in manifest["files"]:
            entry=dict(entry)
            if not entry["path"].startswith(prefix) and entry["path"] not in hashes:
                entry["role"]="input"
            assert sha(ROOT/entry["path"])==entry["sha256"]
            files[entry["path"]]=entry
        for path in sorted(evidence.rglob("*")):
            if not path.is_file():continue
            assert not any(part in (".runs",".gen",".srcs",".cache") for part in path.parts)
            relative=path.relative_to(ROOT).as_posix()
            role="log" if path.suffix==".log" else "input" if path.name=="address_vectors.txt" else "source" if path.suffix in (".sv",".py",".tcl",".md") else "diagnostic" if path.suffix==".patch" else "result"
            files[relative]={"path":relative,"sha256":sha(path),"role":role}
        assert all(set(entry)=={"path","sha256","role"} for entry in files.values())
        manifest["files"]=list(files.values())
        manifest["limitations"].append("首次清单封包检查native2及外层native1原件保留；delivery_manifest_r02.json为本轮独审入口，未改tested source。")
        target=evidence/"delivery_manifest_r02.json"
        write(target,manifest)
        manifests[stage]={"path":target.relative_to(ROOT).as_posix(),"sha256":sha(target)}
    checks=[]
    for stage,item in manifests.items():
        for mode in ("evidence","inputs"):
            argv=[sys.executable,"-X","utf8","-B",str(ROOT/"verification/check_stage_delivery.py"),"--project-root",str(ROOT),"--mode",mode,"--manifest",str(ROOT/item["path"])]
            started=time.monotonic()
            done=subprocess.run(argv,cwd=ROOT,capture_output=True)
            record={"run_id":STAGES[stage],"mode":mode,"command":subprocess.list2cmdline(argv),"argv":argv,"native_exit_code":done.returncode,"elapsed_seconds":time.monotonic()-started,"stdout":done.stdout.decode("utf-8"),"stderr":done.stderr.decode("utf-8")}
            write(WORK/(stage+"_"+mode+"_native_r02.json"),record)
            assert done.returncode==(0 if mode=="evidence" else 2),record
            checks.append({"stage":stage,"mode":mode,"native_exit_code":done.returncode})
            print(json.dumps(checks[-1],ensure_ascii=False),flush=True)
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    assert all(sha(main/name)==h for name,h in stable.items())
    summary={"status":"STOP_READY_G1_ONLY","source_commit":BASELINE,"stable":stable,"modified":freeze["modified_files"],"manifests":manifests,"checks":checks}
    write(WORK/"final_package_receipt.json",summary)
    print(json.dumps(summary,ensure_ascii=False),flush=True)


if __name__=="__main__":main()
