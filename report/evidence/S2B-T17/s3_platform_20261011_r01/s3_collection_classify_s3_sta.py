"""独立解析已结束的 S3 综合报告，真实时序失败返回原生 2。"""
from pathlib import Path
import argparse,hashlib,json,re,math,time

def require(condition,message):
    """解析错误与 STA 失败使用不同结果。"""
    if not condition: raise ValueError(message)

def classify(path):
    """只读报告数值与约束，不加载任何工程源或 Vivado。"""
    require(path.is_file() and not path.is_symlink() and path.stat().st_size<=10*1024*1024,"报告路径/大小错误")
    raw=path.read_bytes();text=raw.decode("utf-8")
    parts=text.split("| Design Timing Summary",1)
    require(len(parts)==2 and "| Clock Summary" in parts[1],"汇总区缺失")
    numeric=parts[1].split("| Clock Summary",1)[0]
    lines=[s.split() for s in numeric.splitlines() if re.fullmatch(r"\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*",s)]
    require(len(lines)==1,"汇总数值不唯一")
    names=("wns_ns","tns_ns","setup_failing_endpoints","setup_total_endpoints","whs_ns","ths_ns","hold_failing_endpoints","hold_total_endpoints","wpws_ns","tpws_ns","pulse_failing_endpoints","pulse_total_endpoints")
    timing={k:float(v) if k.endswith("_ns") else int(v) for k,v in zip(names,lines[0])}
    require(all(math.isfinite(v) for v in timing.values()),"非有限值")
    require(all(timing[k]>=0 for k in names if not k.endswith("_ns")),"负端点数")
    clocks=re.findall(r"^clk_fpga_0\s+\{([\d.]+)\s+([\d.]+)\}\s+([\d.]+)\s+([\d.]+)\s*$",text,re.M)
    require(len(clocks)==1,"时钟摘要不唯一")
    rise,fall,period,frequency=map(float,clocks[0]);require(period==20 and frequency==50,"不是实际 50MHz 报告")
    checks={}
    for key in ("no_clock","constant_clock","pulse_width_clock","unconstrained_internal_endpoints","no_input_delay","no_output_delay","multiple_clock","generated_clocks","loops","partial_input_delay","partial_output_delay","latch_loops"):
        values=set(re.findall(r"checking "+key+r" \((\d+)\)",text));require(len(values)==1,"约束检查缺失或冲突："+key);checks[key]=int(next(iter(values)))
    state=re.findall(r"^\| Design State\s*:\s*(.+)$",text,re.M);require([s.strip() for s in state]==["Synthesized"],"不能混作实现态")
    failing=any(timing[k]<0 for k in names if k.endswith("_ns")) or any(timing[k]>0 for k in ("setup_failing_endpoints","hold_failing_endpoints","pulse_failing_endpoints")) or any(checks.values())
    require(("Timing constraints are not met." in text)==failing,"报告文字与数值冲突")
    return {"status":"FAIL_TIMING" if failing else "PASS_TIMING","timing":timing,"clock":{"name":"clk_fpga_0","period_ns":period,"frequency_mhz":frequency,"rise_ns":rise,"fall_ns":fall},"check_timing":checks,"report":{"path":str(path.absolute()),"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)},"design_state":"Synthesized","report_command":re.findall(r"^\| Command\s*:\s*(.+)$",text,re.M)[0],"postroute":"NOT_RUN","hardware":"NOT_RUN"}

def main():
    """原生 2 是时序失败，原生 3 是分类器输入失败。"""
    parser=argparse.ArgumentParser();parser.add_argument("--report",required=True);parser.add_argument("--result",required=True);a=parser.parse_args()
    output=Path(a.result);require(output.parent.is_dir() and not output.exists(),"新结果名称错误")
    started=time.monotonic()
    try: result=classify(Path(a.report));code=2 if result["status"]=="FAIL_TIMING" else 0
    except (ValueError,UnicodeError,OSError,IndexError) as error: result={"status":"FAIL_CLASSIFIER_INPUT","error":repr(error)};code=3
    result.update(native_exit_code=code,elapsed_seconds=time.monotonic()-started,classifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    with output.open("x",encoding="utf-8",newline="\n") as out:json.dump(result,out,ensure_ascii=False,indent=2);out.write("\n")
    print(json.dumps(result,ensure_ascii=False));return code

if __name__=="__main__":raise SystemExit(main())
