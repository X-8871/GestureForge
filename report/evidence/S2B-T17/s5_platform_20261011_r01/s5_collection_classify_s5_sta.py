"""只读解析 S5 已结束的综合 STA，时序失败真实返回 2。"""
from pathlib import Path
import argparse,hashlib,json,re,math,time

def require(condition,message):
    """输入错误与 STA 失败分开记录。"""
    if not condition:raise ValueError(message)

def classify(path):
    """只读原报告，不加载工程或修改约束。"""
    require(path.is_file() and not path.is_symlink() and path.stat().st_size<=10*1024*1024,"报告路径错误")
    raw=path.read_bytes();text=raw.decode("utf-8")
    parts=text.split("| Design Timing Summary",1)
    require(len(parts)==2 and "| Clock Summary" in parts[1],"汇总区缺失")
    lines=[s.split() for s in parts[1].split("| Clock Summary",1)[0].splitlines() if re.fullmatch(r"\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*",s)]
    require(len(lines)==1,"数值不唯一")
    names=("wns_ns","tns_ns","setup_failing_endpoints","setup_total_endpoints","whs_ns","ths_ns","hold_failing_endpoints","hold_total_endpoints","wpws_ns","tpws_ns","pulse_failing_endpoints","pulse_total_endpoints")
    timing={k:float(v) if k.endswith("_ns") else int(v) for k,v in zip(names,lines[0])}
    require(all(math.isfinite(v) for v in timing.values()) and all(timing[k]>=0 for k in names if not k.endswith("_ns")),"非有限值或负计数")
    clocks=re.findall(r"^clk_fpga_0\s+\{([\d.]+)\s+([\d.]+)\}\s+([\d.]+)\s+([\d.]+)\s*$",text,re.M)
    require(len(clocks)==1,"时钟摘要不唯一")
    rise,fall,period,frequency=map(float,clocks[0]);require(period==20 and frequency==50,"不是实际 50MHz")
    checks={}
    for key in ("no_clock","constant_clock","pulse_width_clock","unconstrained_internal_endpoints","no_input_delay","no_output_delay","multiple_clock","generated_clocks","loops","partial_input_delay","partial_output_delay","latch_loops"):
        values=set(re.findall(r"checking "+key+r" \((\d+)\)",text));require(len(values)==1,"检查缺失或冲突："+key);checks[key]=int(next(iter(values)))
    state=re.findall(r"^\| Design State\s*:\s*(.+)$",text,re.M);require([s.strip() for s in state]==["Synthesized"],"不是综合态")
    failing=any(timing[k]<0 for k in names if k.endswith("_ns")) or any(timing[k]>0 for k in ("setup_failing_endpoints","hold_failing_endpoints","pulse_failing_endpoints")) or any(checks.values())
    require(("Timing constraints are not met." in text)==failing,"文字与数值冲突")
    return {"status":"FAIL_TIMING" if failing else "PASS_TIMING","timing":timing,"clock":{"name":"clk_fpga_0","period_ns":period,"frequency_mhz":frequency,"rise_ns":rise,"fall_ns":fall},"check_timing":checks,"report":{"path":str(path.absolute()),"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)},"design_state":"Synthesized","report_command":re.findall(r"^\| Command\s*:\s*(.+)$",text,re.M)[0],"implementation":"NOT_RUN","postroute":"NOT_RUN","hardware":"NOT_RUN"}

def main():
    """原生 2 为时序失败，原生 3 为解析输入失败。"""
    parser=argparse.ArgumentParser();parser.add_argument("--report",required=True);parser.add_argument("--result",required=True);args=parser.parse_args()
    output=Path(args.result);require(output.parent.is_dir() and not output.exists(),"输出不是新目标")
    started=time.monotonic()
    try:result=classify(Path(args.report));code=2 if result["status"]=="FAIL_TIMING" else 0
    except (ValueError,UnicodeError,OSError,IndexError) as error:result={"status":"FAIL_CLASSIFIER_INPUT","error":repr(error)};code=3
    result.update(native_exit_code=code,elapsed_seconds=time.monotonic()-started,classifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    with output.open("x",encoding="utf-8",newline="\n") as out:json.dump(result,out,ensure_ascii=False,indent=2);out.write("\n")
    print(json.dumps(result,ensure_ascii=False));return code

if __name__=="__main__":raise SystemExit(main())
