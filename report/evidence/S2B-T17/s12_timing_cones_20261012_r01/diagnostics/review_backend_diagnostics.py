"""只读核验backend实际诊断与继承夹具；证据写入独占新目录。"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import time
import psutil

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
RUN="s12_backend_timing_20261012_r01"
EVIDENCE=ROOT/"report/evidence/S2B-T17"/RUN
PRIOR=ROOT/"report/evidence/S2B-T17/maxpool_geometry_factor_trace_20261012_r01"
WORK=ROOT/"tmp/2B/S2B-T17"/RUN
OUT=HERE/(RUN+"_diagnostics")
assert HERE.is_dir() and EVIDENCE.is_dir() and PRIOR.is_dir() and WORK.is_dir()
assert not OUT.exists()
TB="tb_s2b_backend_coordinates.sv"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for directory in (EVIDENCE,PRIOR):
    assert (directory/TB).is_file() and (directory/"compile.log").is_file()
assert sha(EVIDENCE/TB)==sha(PRIOR/TB)
text=(EVIDENCE/TB).read_text(encoding="utf-8");lines=text.splitlines()
assert "reset_all; boundary; invalid_layer; actual_errors; full_traces; public_entries;" in text
public=text.split("task automatic public_entries;",1)[1].split("end endtask",1)[0]
assert not re.search(r"\b(?:seed|force|release)\b",public)
assert "backend_start=1; tick; backend_start=0" in public
assert "release old.alias_valid; release dut_new.alias_valid;" in text

def parse(directory):
    """将诊断归属到实际实例、变量和TB写入行；不使用全局豁免。"""
    log=(directory/"compile.log").read_text(encoding="utf-8")
    assert not re.search(r"%Warning-(?:LATCH|UNOPTFLAT)\b",log)
    records=[]
    for block in re.findall(r"%Warning-MULTIDRIVEN:[\s\S]*?(?=%Warning-|%Error|make(?:\[|:)|\Z)",log):
        header=block.splitlines()[0]
        symbol=re.search(r": '(\w+)'",header)[1]
        instance=re.search(r"In instance 'tb_s2b_backend_coordinates\.(\w+)'",block)[1]
        assert instance in ("old","dut_new")
        source,line=re.search(r"source[\\/](\w+\.sv):(\d+):",header).groups()
        locations=sorted(set(int(n) for n in re.findall(re.escape(TB)+r":(\d+):",block)))
        assert locations
        for n in locations:
            assert re.search(re.escape(instance)+r"\."+re.escape(symbol)+r"(?:\s*=|\s*;)",lines[n-1])
        writes=[n for n,s in enumerate(lines,1) if re.search(r"(?:force|release)\s+"+re.escape(instance)+r"\."+re.escape(symbol)+r"\b",s)]
        if symbol.startswith("output_"):
            assert locations==[140 if instance=="old" else 141]
            scope="seed内部边界/数值trace夹具写入cursor；public_entries不调用seed。"
        else:
            assert len(writes)==2 and writes[0] in range(147,152) and writes[1] in range(168,173)
            scope="boundary的force及release；后续full_traces/public_entries前已release。"
        records.append({"raw_header":header,"instance":instance,"signal":symbol,"source_name":source,"source_line":int(line),"tb_diagnostic_lines":locations,"tb_force_release_lines":writes,"scope":scope})
    assert len(records)==16 and Counter(x["instance"] for x in records)=={"old":8,"dut_new":8}
    return records

started=time.monotonic();current=parse(EVIDENCE);prior=parse(PRIOR)
key=lambda r:(r["instance"],r["signal"],tuple(r["tb_diagnostic_lines"]),tuple(r["tb_force_release_lines"]))
assert sorted(map(key,current))==sorted(map(key,prior))
bindings={}
for r in current:
    path=WORK/"source"/r["source_name"];assert path.is_file()
    assert re.search(r"\b"+r["signal"]+r"\b",path.read_text(encoding="utf-8").splitlines()[r["source_line"]-1])
    bindings[path.relative_to(ROOT).as_posix()]=sha(path)
receipt={"status":"PASS_BACKEND_TB_DIAGNOSTIC_SCOPE_ONLY","script_sha256":sha(Path(__file__)),"source_commit":"891f750045ce141a8152c96025da559ff1d3a321","tb_sha256":sha(EVIDENCE/TB),"prior_tb_sha256":sha(PRIOR/TB),"compile_log_sha256":sha(EVIDENCE/"compile.log"),"prior_compile_log_sha256":sha(PRIOR/"compile.log"),"controlled_multidriven":current,"count":16,"prior_instance_signal_tb_locations_identical":True,"compiled_source_sha256":bindings,"LATCH_UNOPTFLAT":[],"owned_runner_pid":30024,"owned_runner_currently_absent":not psutil.pid_exists(30024),"final_evidence_bytes":sum(p.stat().st_size for p in EVIDENCE.rglob("*") if p.is_file()),"seconds":time.monotonic()-started,"limits":"逐条诊断来源核验；没有运行RTL/更改编译flags，不代表所有warning为零，不替代功能G1/整体G2/STA。boundary/full_traces内部seed与public_entries真实START分别判断。"}
assert receipt["owned_runner_currently_absent"]
OUT.mkdir()
with (OUT/"receipt.json").open("x",encoding="utf-8",newline="\n") as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write("\n")
print(json.dumps({"status":receipt["status"],"count":16,"owned_runner_absent":True,"final_evidence_bytes":receipt["final_evidence_bytes"],"receipt_sha256":sha(OUT/"receipt.json")},ensure_ascii=False))
