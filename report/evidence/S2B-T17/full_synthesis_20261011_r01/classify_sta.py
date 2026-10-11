"""只读解析本次综合STA原报告，时序失败以真实原生码2退出。"""
import hashlib
import json
from pathlib import Path
import re
import sys

def digest(path):
    """流式绑定原报告字节。"""
    h=hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda:src.read(1048576),b""):h.update(block)
    return h.hexdigest()

directory=Path(sys.argv[1]); destination=Path(sys.argv[2])
assert directory.is_dir() and destination.parent.is_dir() and not destination.exists()
record={"schema_version":1,"status":"FAIL_PARSE","hardware_execution":"NOT_RUN","post_route":"NOT_RUN"}
try:
    timing_path=directory/"timing_synth.rpt"; utilization_path=directory/"utilization_full_synth.rpt"
    assert timing_path.is_file() and utilization_path.is_file()
    timing=timing_path.read_text(encoding="utf-8"); utilization=utilization_path.read_text(encoding="utf-8")
    line=re.search(r"^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s*$",timing,re.M)
    assert line is not None
    keys=["wns_ns","tns_ns","setup_failing_endpoints","setup_total_endpoints","whs_ns","ths_ns","hold_failing_endpoints","hold_total_endpoints","wpws_ns","tpws_ns","pulse_failing_endpoints","pulse_total_endpoints"]
    record["timing"]={k:int(line[i+1]) if "endpoints" in k else float(line[i+1]) for i,k in enumerate(keys)}
    clock=re.search(r"^clk_fpga_0\s+\{[^}]+\}\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$",timing,re.M)
    assert clock is not None and "Design State : Synthesized" in timing
    record["clock"]={"name":"clk_fpga_0","period_ns":float(clock[1]),"frequency_mhz":float(clock[2])}
    checks=dict(re.findall(r"checking ([a-z_]+) \((\d+)\)",timing))
    assert len(checks)==12
    record["check_timing"]={k:int(v) for k,v in checks.items()}
    record["worst_setup_path"]={"logic_levels":int(re.search(r"Logic Levels:\s+(\d+)",timing)[1]),
                                "source":re.search(r"Source:\s+([^\r\n]+)",timing)[1].strip(),
                                "destination":re.search(r"Destination:\s+([^\r\n]+)",timing)[1].strip(),
                                "data_path_delay_ns":float(re.search(r"Data Path Delay:\s+(\d+\.\d+)ns",timing)[1])}
    record["resources"]={}
    for label,name in [("Slice LUTs*","lut"),("Slice Registers","ff"),("Block RAM Tile","bram_tiles"),("DSPs","dsp")]:
        row=re.search(r"\|\s*"+re.escape(label)+r"\s*\|\s*(\d+)\s*\|",utilization)
        assert row is not None;record["resources"][name]=int(row[1])
    record["inputs"]=[{"path":str(p),"sha256":digest(p)} for p in (timing_path,utilization_path)]
    record["design_state"]="Synthesized"
    failed=record["timing"]["wns_ns"]<0 or record["timing"]["tns_ns"]<0 or record["timing"]["setup_failing_endpoints"]>0
    record["status"]="FAIL_TIMING" if failed else "PASS_SYNTH_STA_ONLY"
    record["native_exit_code"]=2 if failed else 0
except BaseException as error:
    record["error"]=repr(error);record["native_exit_code"]=3
finally:
    with destination.open("x",encoding="utf-8",newline="\n") as out:json.dump(record,out,ensure_ascii=False,indent=2);out.write("\n")
print(json.dumps(record,ensure_ascii=False))
sys.exit(record["native_exit_code"])
