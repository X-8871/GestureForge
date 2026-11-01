"""封存 S7 独立审查闭包与真实失败结果，保存批准范围及原生检查输出。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, shutil, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[4]
RUN=Path(__file__).resolve().parent
REVIEW=ROOT/"tmp/2B/S2B-T17/independent_s7_synthesis_review_20261011_r01"
FORMAL=ROOT/"report/evidence/S2B-T17/independent_s7_synthesis_review_20261011_r01"
SOURCE="a5caefba952a08f365d57193696b08c0e1aff2a5"
RAW_SHA="8fd949d2babb98bf8ecff0b6d8692407985bce536f63d0fec6fb1f2229174382"
RECEIPT_SHA="da9ada5561e03861b00d2e22f205a36e977fd59a55f78f611bcd2e9e150ea090"
MAIN=ROOT/"report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_delivery_manifest_r03.json"
MAIN_SHA="63582f7312bb1cb4ac3141ca826cf00e8ef621fac43abc994c82c66e7c1fb296"

def sha(path):
    """核验实际文件类型并按原字节计算哈希。"""
    assert path.is_file() and not path.is_symlink(),path
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,value):
    """只创建一次新记录，禁止覆盖关闭证据。"""
    assert path.parent.is_dir() and not path.exists(),path
    with path.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")

def copy_bound(path,expected,role,target):
    """复制精确闭包原件并再次核对源、目标及角色。"""
    assert path.resolve().is_relative_to(ROOT) and sha(path)==expected
    assert role in {"source","input","result","log","diagnostic","artifact"}
    assert path.suffix.lower() not in {".exe",".obj",".o",".dcp",".bit"}
    assert not target.exists() and target.resolve().is_relative_to(FORMAL)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(path,target)
    assert sha(path)==expected and sha(target)==expected
    return {"path":target.relative_to(ROOT).as_posix(),"sha256":expected,"role":role}

def main():
    """固定独审原件，机器核验只证明包装，不改判 STA 失败。"""
    raw_path=REVIEW/"raw_manifest.jsonl"
    receipt_path=REVIEW/"final_review_receipt.json"
    assert sha(raw_path)==RAW_SHA and sha(receipt_path)==RECEIPT_SHA and sha(MAIN)==MAIN_SHA
    receipt=json.loads(receipt_path.read_text(encoding="utf-8"))
    original=json.loads(MAIN.read_text(encoding="utf-8"))
    assert receipt["status"]=="PASS" and receipt["source_commit"]==SOURCE and receipt["sta"]=="FAIL_TIMING"
    assert receipt["formal_inputs"][0]["sha256"]==MAIN_SHA
    rows=[json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines()]
    assert len(rows)==512 and all(set(row)=={"path","sha256","role"} for row in rows)
    assert len(rows)==len({row["path"] for row in rows})
    for path,expected,role in [(raw_path,RAW_SHA,"artifact"),(receipt_path,RECEIPT_SHA,"result")]:
        name=path.relative_to(ROOT).as_posix()
        if name not in {row["path"] for row in rows}:
            rows.append({"path":name,"sha256":expected,"role":role})
    assert FORMAL.parent.is_dir() and not FORMAL.exists()
    FORMAL.mkdir()
    copies=[]; mapping=[]; total=0
    for row in rows:
        path=ROOT/row["path"]
        target=FORMAL/"raw_artifacts"/row["path"]
        copies.append(copy_bound(path,row["sha256"],row["role"],target))
        size=path.stat().st_size;total+=size
        mapping.append({"original":row["path"],"copy":copies[-1]["path"],"sha256":row["sha256"],"bytes":size})
    for name in ("mcp_stop_postclosure.json","stop_followup_observation_r01.json","s8_resource_preflight_tool_r01.json"):
        path=RUN/name
        copies.append(copy_bound(path,sha(path),"diagnostic",FORMAL/"root_diagnostics"/name))
    script=Path(__file__).resolve()
    copies.append(copy_bound(script,sha(script),"source",FORMAL/script.name))
    binding=FORMAL/"archive_binding.json"
    save(binding,{"status":"PASS_EXACT_COPY_ONLY","source_commit":SOURCE,"review_status":"PASS_EVIDENCE_ACCURACY_ONLY",
        "reviewed_manifest_sha256":MAIN_SHA,"receipt_sha256":RECEIPT_SHA,"raw_manifest_sha256":RAW_SHA,
        "original_raw_rows":512,"copied_review_closure_count":len(rows),"review_closure_bytes":total,"files":mapping,
        "created_at_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "limitations":["512项包含被审输入；复制固定输入避免下轮生产改动使历史清单失效",
        "早先stop自动审批未执行，后来只读PID缺失；不宣称stop成功","STA仍FAIL_TIMING，无实现或实板批准"]})
    copies.append({"path":binding.relative_to(ROOT).as_posix(),"sha256":sha(binding),"role":"result"})
    manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":FORMAL.name,
        "source_commit":SOURCE,"evidence_dir":FORMAL.relative_to(ROOT).as_posix(),
        "interfaces":original["interfaces"],"files":copies,"checks":list(original["checks"]),
        "tool_versions":{"python":sys.version},
        "limitations":list(original["limitations"])+[receipt["scope"],"ROOT复制固定输入，不新增独立批准；当前目标仍是全模型实板与完整2B验收"]}
    manifest["checks"].append({"name":"S7独立失败证据准确性审查","status":"PASS","reason":receipt["scope"]})
    initial=FORMAL/"delivery_manifest.json"
    save(initial,manifest)
    for mode,expected in (("evidence",0),("inputs",2)):
        command=[sys.executable,"-B","-X","utf8",str(ROOT/"verification/check_stage_delivery.py"),
            "--mode",mode,"--manifest",str(initial),"--project-root",str(ROOT)]
        started=time.monotonic();result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=55)
        for suffix,data in (("stdout.log",result.stdout),("stderr.log",result.stderr)):
            target=FORMAL/("root_"+mode+"."+suffix)
            with target.open("xb") as stream:stream.write(data)
            manifest["files"].append({"path":target.relative_to(ROOT).as_posix(),"sha256":sha(target),"role":"log"})
        native=FORMAL/("root_"+mode+".native.json")
        save(native,{"command":command,"native_exit_code":result.returncode,"seconds":time.monotonic()-started,
            "peak_memory_bytes":None,"limitations":["轻量包装检查，不能代表设计或实板通过"]})
        manifest["files"].append({"path":native.relative_to(ROOT).as_posix(),"sha256":sha(native),"role":"result"})
        assert result.returncode==expected,(mode,result.returncode,result.stdout.decode("utf-8",errors="replace"))
        manifest["checks"].append({"name":"ROOT独审归档"+mode,"status":"PASS" if expected==0 else "FAIL",
            "command":subprocess.list2cmdline(command),"exit_code":result.returncode,"reason":"绑定检查；未冻结及真实STA失败仍保留"})
    manifest["files"].append({"path":initial.relative_to(ROOT).as_posix(),"sha256":sha(initial),"role":"artifact"})
    final=FORMAL/"delivery_manifest_r02.json"
    save(final,manifest)
    print(json.dumps({"status":"ARCHIVED_REVIEWED_S7_FAILURE_ONLY","raw_count":len(rows),"raw_bytes":total,
        "bindings":len(manifest["files"]),"manifest_sha256":sha(final)},ensure_ascii=False))

if __name__=="__main__":
    main()
