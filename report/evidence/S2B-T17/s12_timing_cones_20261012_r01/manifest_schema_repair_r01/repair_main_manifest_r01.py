"""仅修复主清单工具版本字段类型，新增绑定并保存原失败字节。"""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
MAIN=ROOT/"report/evidence/S2B-T17/s12_timing_cones_20261012_r01"
OLD=MAIN/"delivery_manifest.json";NEW=MAIN/"delivery_manifest_r02.json"
RAW=MAIN/"manifest_schema_repair_r01";CAPTURE=HERE/"delivery_finalize_capture_r05"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert MAIN.is_dir() and OLD.is_file() and CAPTURE.is_dir() and not RAW.exists() and not NEW.exists()
assert sha(OLD)=="e9a32360e12c2f80aa91189d2b353e6b4dd2e58a3efee864e0eecfd34488103d"
fixed={"source_freeze.json":"eadf373c59420aa234a5e6394c9ca08066b480bdde6263f91600cf21bbbe02c7","g1_summary.json":"0674603c86f92762d172085323fdd0328d7a364735a87b45e389f0ede9d19549","source_diff.patch":"6be9a040c20520403532aec5a2626292f93b8b91845b21d883b69dae2ceb0a5d"}
assert all(sha(MAIN/p)==h for p,h in fixed.items())
freeze=json.loads((MAIN/"source_freeze.json").read_text(encoding="utf-8"))
expected=freeze["modified_files"];assert len(expected)==16 and {p:sha(ROOT/p) for p in expected}==expected
ast.parse(Path(__file__).read_text(encoding="utf-8"))
started=time.monotonic();original=json.loads(OLD.read_text(encoding="utf-8"));new=json.loads(OLD.read_text(encoding="utf-8"))
versions=original["tool_versions"];assert len(versions)==9 and all(isinstance(v,dict) and v for v in versions.values())
new["tool_versions"]={k:json.dumps(v,ensure_ascii=False,sort_keys=True) for k,v in versions.items()}
assert all(json.loads(new["tool_versions"][k])==v for k,v in versions.items())
RAW.mkdir();mapping=[]
def write(path,value):
    """创建新UTF-8原件，不覆盖历史文件。"""
    with path.open("x",encoding="utf-8",newline="\n") as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")
def copy(source,target):
    """逐RAW复制并核SHA；不重编码已有日志或receipt。"""
    assert source.is_file() and not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target);assert sha(source)==sha(target)
    mapping.append({"original_path":source.relative_to(ROOT).as_posix(),"restored_path":target.relative_to(ROOT).as_posix(),"sha256":sha(target),"bytes":target.stat().st_size})
for path in sorted(CAPTURE.iterdir()):
    assert path.is_file();copy(path,RAW/"finalize_failed_raw"/path.name)
copy(HERE/"delivery_finalize_native_r05.py",RAW/"finalize_failed_raw/delivery_finalize_native_r05.py")
copy(Path(__file__),RAW/Path(__file__).name)
receipt=json.loads((CAPTURE/"native_receipt.json").read_text(encoding="utf-8"))
assert [r["native_returncode"] for r in receipt["runs"]]==[0,2] and receipt["status"]=="FAILED_OR_BLOCKED_PARTIAL_PRESERVED"
state={"finalize_native_returncode":0,"evidence_native_returncode":2,"wrapper_outer_native_returncode":1,"wrapper_outer_native_basis":"实际exec session22132完成exit_code1，ROOT收到并授权修复；原receipt FAILED_OR_BLOCKED_PARTIAL_PRESERVED和原始stdout保留，不篡改内部码。","inputs":"NOT_RUN","source16_unchanged_before_repair":expected,"raw_samples":"原r05没有生成逐样本文件；真实20ms采样计数与离散峰保存在receipt.runs，不补造历史samples。"}
write(RAW/"failed_execution_state.json",state)
write(RAW/"tool_versions_schema_diff.json",{"old_manifest_sha256":sha(OLD),"operation":"各真实对象仅json.dumps(ensure_ascii=False,sort_keys=True)编码为非空字符串。","roundtrip_semantics_equal":True,"original":versions,"proposed":new["tool_versions"]})
write(RAW/"repair_note.json",{"status":"SCHEMA_REPAIR_ONLY","source_commit_role":freeze["source_commit_role"],"repair_command":__import__("subprocess").list2cmdline([sys.executable,"-X","utf8","-B",str(Path(__file__).resolve())]),"repair_script_sha256":sha(Path(__file__)),"unchanged_main":fixed,"prior_failure":state,"limits":"不重finalize/RTL；原manifest/源码43/freeze/summary/diff/nativecode不变。九项G1与包装分别判断，整体G2/STA/G3/G5未执行。后续r02 evidence/inputs实际结果只写新scratch，避免循环SHA。"})
write(RAW/"raw_restore_mapping.json",mapping)
files={r["path"]:r for r in new["files"]}
files[OLD.relative_to(ROOT).as_posix()]={"path":OLD.relative_to(ROOT).as_posix(),"sha256":sha(OLD),"role":"diagnostic"}
for path in sorted(RAW.rglob("*")):
    if path.is_file():
        role="source" if path.suffix==".py" else "log" if path.suffix in (".log",".jsonl") else "diagnostic" if path.name=="tool_versions_schema_diff.json" else "result"
        relative=path.relative_to(ROOT).as_posix();files[relative]={"path":relative,"sha256":sha(path),"role":role}
new["files"]=list(files.values())
new["checks"].extend([{"name":"首次finalize真实native","status":"PASS","command":receipt["runs"][0]["command"],"exit_code":0,"reason":"实际源码封存完成，旧清单schema包装失败另列。"},{"name":"旧清单evidence schema失败","status":"FAIL","command":receipt["runs"][1]["command"],"exit_code":2,"reason":"9个tool_versions对象不满足非空字符串schema；原始失败日志/code保留。"},{"name":"首次包装wrapper真实native","status":"FAIL","command":__import__("subprocess").list2cmdline([sys.executable,"-X","utf8","-B",str(HERE/"delivery_finalize_native_r05.py")]),"exit_code":1,"reason":"实际exec session22132 native1，因evidence2停止；inputs当时NOT_RUN。"}])
new["limitations"].append("r02仅工具版本schema最小修复与新增原失败绑定；旧manifest/freeze/summary/diff不改。r05无逐样本文件，真实聚合计数/峰RAW保留，不补造历史采样。首次finalize0/evidence2/wrapper1/inputsNOT_RUN不能被r02包装结果追认。")
write(NEW,new)
assert sha(OLD)=="e9a32360e12c2f80aa91189d2b353e6b4dd2e58a3efee864e0eecfd34488103d"
assert all(sha(MAIN/p)==h for p,h in fixed.items()) and {p:sha(ROOT/p) for p in expected}==expected
print(json.dumps({"status":"REPAIRED_SCHEMA_CHECKS_PENDING","manifest_r02_sha256":sha(NEW),"files":len(new["files"]),"raw_restored":len(mapping),"unchanged_main":fixed,"source16_unchanged":True,"seconds":time.monotonic()-started},ensure_ascii=False),flush=True)
