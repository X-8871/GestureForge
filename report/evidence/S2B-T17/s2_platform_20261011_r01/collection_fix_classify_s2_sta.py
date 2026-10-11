"""从已结束综合STA报告独立分类；报告生成成功不等于时序满足。"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import math
import sys
import time

def require(condition,message):
    """分类输入损坏与真实时序失败分开。"""
    if not condition:raise ValueError(message)
def classify(path):
    """只读原始timing_summary，不读取当前候选RTL或调用Vivado。"""
    require(path.is_file() and path.stat().st_size<=10*1024*1024,"STA报告路径/类型/大小错误")
    raw=path.read_bytes();text=raw.decode("utf-8")
    section=text.split("| Design Timing Summary",1)
    require(len(section)==2 and "| Clock Summary" in section[1],"STA汇总区缺失")
    numeric=section[1].split("| Clock Summary",1)[0]
    lines=[line.split() for line in numeric.splitlines() if re.fullmatch(r"\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*",line)]
    require(len(lines)==1,"STA汇总数值区歧义或缺失")
    names=("wns_ns","tns_ns","setup_failing_endpoints","setup_total_endpoints","whs_ns","ths_ns","hold_failing_endpoints","hold_total_endpoints","wpws_ns","tpws_ns","pulse_failing_endpoints","pulse_total_endpoints")
    timing={name:float(value) if name.endswith("_ns") else int(value) for name,value in zip(names,lines[0])}
    require(all(math.isfinite(value) for value in timing.values()),"STA含非有限数")
    require(all(timing[name]>=0 for name in names if not name.endswith("_ns")),"STA端点数为负")
    clocks=re.findall(r"^clk_fpga_0\s+\{([\d.]+)\s+([\d.]+)\}\s+([\d.]+)\s+([\d.]+)\s*$",text,re.M)
    require(len(clocks)==1,"实际50MHz时钟摘要缺失或歧义")
    rise,fall,period,frequency=map(float,clocks[0])
    require(period==20.0 and frequency==50.0,"报告不是要求的50MHz综合STA")
    checks={}
    for name in ("no_clock","constant_clock","pulse_width_clock","unconstrained_internal_endpoints","no_input_delay","no_output_delay","multiple_clock","generated_clocks","loops","partial_input_delay","partial_output_delay","latch_loops"):
        values=set(re.findall(r"checking "+name+r" \((\d+)\)",text))
        require(len(values)==1,"check_timing项缺失或不同："+name);checks[name]=int(next(iter(values)))
    state=re.findall(r"^\| Design State\s*:\s*(.+)$",text,re.M)
    require(state==["Synthesized"],"仅允许综合态报告，不能误称实现态")
    failing=any(timing[k]<0 for k in ("wns_ns","tns_ns","whs_ns","ths_ns","wpws_ns","tpws_ns")) or any(timing[k]>0 for k in ("setup_failing_endpoints","hold_failing_endpoints","pulse_failing_endpoints")) or any(checks.values())
    require(("Timing constraints are not met." in text)==failing,"报告语句与数字分类不符")
    return {"status":"FAIL_TIMING" if failing else "PASS_TIMING","timing":timing,"clock":{"name":"clk_fpga_0","period_ns":period,"frequency_mhz":frequency,"rise_ns":rise,"fall_ns":fall},"check_timing":checks,"report":{"path":str(path.absolute()),"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)},"design_state":state[0],"report_command":re.findall(r"^\| Command\s*:\s*(.+)$",text,re.M)[0],"postroute":"NOT_RUN","hardware":"NOT_RUN"}

def main():
    """原生2明确表示STA FAIL，输入错误另用3。"""
    parser=argparse.ArgumentParser();parser.add_argument("--report",required=True);parser.add_argument("--result",required=True);args=parser.parse_args()
    result=Path(args.result);require(result.parent.is_dir() and not result.exists(),"分类结果必须新名称")
    started=time.monotonic()
    try:record=classify(Path(args.report));code=2 if record["status"]=="FAIL_TIMING" else 0
    except (ValueError,UnicodeError,OSError,IndexError) as error:record={"status":"FAIL_CLASSIFIER_INPUT","error":repr(error)};code=3
    record.update(native_exit_code=code,elapsed_seconds=time.monotonic()-started,classifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    with result.open("x",encoding="utf-8",newline="\n") as out:json.dump(record,out,ensure_ascii=False,indent=2);out.write("\n")
    print(json.dumps(record,ensure_ascii=False));return code

if __name__=="__main__":raise SystemExit(main())
