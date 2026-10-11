"""独立无限精度地址黄金与小规模原RTL逐字段/真实引擎逐周期审查。"""
import ast
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import time
import psutil

base = Path(__file__).absolute().parent
root = Path.cwd().resolve()
g1 = root / "report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r02"
trace = root / "report/evidence/S2B-T17/maxpool_geometry_factor_trace_20261012_r01"
checks = []; commands = []; inputs = {}; started = time.monotonic(); peak = 0
U32 = 2**32-1
def digest(path):
    obj = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""): obj.update(chunk)
    return obj.hexdigest()
def bind(path, role="input"):
    assert path.is_file(), str(path)
    relative = path.relative_to(root).as_posix()
    inputs[relative] = {"path": relative, "sha256": digest(path), "role": role}
    return path
def load(path, role="input"): return json.loads(bind(path, role).read_text(encoding="utf-8"))
def check(name, value):
    assert value, name
    checks.append(name)
def write(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream: json.dump(value, stream, ensure_ascii=False, indent=2); stream.write("\n")
def run(label, command, cwd=root, env=None, expected=0, budget=1073741824):
    global peak
    start = time.monotonic(); rss_peak = 0
    with (base / (label + ".stdout.log")).open("xb") as so, (base / (label + ".stderr.log")).open("xb") as se:
        child = subprocess.Popen(command, cwd=cwd, env=env, stdout=so, stderr=se)
        while child.poll() is None:
            try:
                process = psutil.Process(child.pid)
                rss = psutil.Process().memory_info().rss + process.memory_info().rss
                for owned in process.children(recursive=True):
                    try: rss += owned.memory_info().rss
                    except psutil.NoSuchProcess: pass
                rss_peak = max(rss_peak, rss); peak = max(peak, rss)
                if rss > budget: raise RuntimeError("独立单组超RSS预算，停止派发")
            except psutil.NoSuchProcess: pass
            assert time.monotonic()-start < 180, "独立命令时间上限"
            time.sleep(0.1)
    row = {"command": command, "cwd": str(cwd), "native_exit_code": child.returncode, "elapsed_seconds": time.monotonic()-start, "sampled_owned_tree_with_reviewer_peak_bytes": rss_peak}
    write(base / (label + ".native.json"), row); commands.append(row)
    check(label + "原生码", child.returncode == expected)
    return (base / (label + ".stdout.log")).read_bytes()

for path, expected in ((g1 / "delivery_manifest.json", "be999362a06f7a85571e847b494869cc2a5b6bb1b54ecaa2cfc38234234f1b67"), (trace / "delivery_manifest.json", "7e7f1053a5f933461fd1ea79f013a7c81618e4519b8d4258298b5c093d85f979")):
    manifest = load(path)
    check(path.parent.name + " manifest SHA", digest(path) == expected)
    for item in manifest["files"]:
        p = root / item["path"]
        check("绑定 " + item["path"], p.is_file() and digest(p) == item["sha256"])
    check("manifest六role三字段", all(set(x) == {"path", "sha256", "role"} and x["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"} for x in manifest["files"]))
freeze = load(g1 / "source_freeze.json")
check("source_freeze SHA", digest(g1 / "source_freeze.json") == "54fdd3e18d6e897bfb8c9df9ccd30699bb15e52ad807a327cf1ea37ad27093dc")
for item in freeze["source_files"]:
    check("当前源及快照 " + item["path"], digest(bind(root / item["path"], "source")) == item["sha256"] == digest(bind(root / item["snapshot"], "source")))
check("43源18RTL8修改", len(freeze["source_files"]) == 43 and len(freeze["active_rtl_sources"]) == 18 and len(freeze["modified_files"]) == 8)
for path, value in freeze["frozen14"].items(): check("原14 " + path, digest(root/path) == value)
check("engine原字节未变", digest(root / "src/s2b_maxpool_engine.sv") == "8908ec272fa47db816f110ccf7483d359733bf0e4f1dbea4b29d2b543af18f70")
check("冻结8source diff SHA", digest(bind(g1 / "source_diff.patch")) == "7071b8dbf53e0d4e0c4cefa1cc307a71d06fd9031a4d3a2ba6580e6adf90f9e9")
for path, value in freeze["modified_files"].items(): check("待审修改SHA " + path, digest(root/path) == value)
head = run("head", ["git", "rev-parse", "HEAD"])
check("HEAD固定", head.decode().strip() == "4288795b1e8c75b98cbbeb69ac33709172e97c66")
diff = run("source_diff", ["git", "-c", "core.autocrlf=false", "diff", "--", *freeze["modified_files"]])
check("实际八文件diff与冻结一致", hashlib.sha256(diff).hexdigest() == freeze["source_diff_sha256"])
summary = load(g1 / "g1_summary.json", "result")
check("G1摘要SHA", digest(g1 / "g1_summary.json") == "646db5e44767a7ee22aa6c7f667dcfeb02c1176edf5fc28f94e8a9064a297d4e")
check("G1 profile及闭包", summary["profile"] == "s2b-inference-platform/0.1.11" and summary["source_closure_count"] == 43 and summary["static_source_count"] == 33 and summary["derived_rtl_count"] == 8)
check("地址82591/旧82586+5", summary["geometry_fullfield"]["vectors"] == 82591)
validation = load(g1 / "validation.json", "result")
load(trace / "validation.json", "result")
check("26静态及12自身SHA mutants", summary["semantic_mutants"] == 12 and len(validation["checker_public_negatives"]) == 26 and all(x["status"] == "REJECTED" for x in validation["checker_semantic_mutants"]))
diagnostic = load(g1 / "diagnostic_scope.json", "diagnostic")
inherited = diagnostic["backend_inherited"]
for name in ("prior_log", "actual_log"):
    item = inherited[name]
    headers = re.findall(r"^%Warning-MULTIDRIVEN:.*", bind(root / item["path"], "log").read_text(encoding="utf-8"), re.M)
    check("16继承TB告警 " + name, digest(root/item["path"]) == item["sha256"] and headers == inherited["headers"] and len(headers) == 16)
for name in ("geometry", "engine"):
    log = bind(g1 / (name + "_compile.log"), "log").read_text(encoding="utf-8")
    check(name + "无新增三类异常", not re.search(r"%Warning-(LATCH|UNOPTFLAT|MULTIDRIVEN)", log))
for name in ("geometry_simulation.log", "engine_simulation.log"): bind(g1 / name, "log")
bind(trace / "simulation.log", "log")
check("cache首轮失败保留", summary["r01_failure"]["native_exit_code"] == 1 and summary["r01_failure"]["cache_bytes_at_diagnosis"] > 314572800 and "640MiB" in summary["r01_failure"]["new_budget_authorization"])
for stage in summary["execution"]:
    check("G1实际stage native0 " + stage["stage"], stage["native_exit_code"] == 0 and all(x["exit_code"] == 0 and digest(bind(root/x["log"], "log")) == x["log_sha256"] for x in stage["runs"]))
check("trace实际202.235s/702812160B", summary["execution"][1]["seconds"] == 202.235 and summary["execution"][1]["peak_tree_rss_bytes"] == 702812160)
profile = load(root / "board/s2b_inference_platform.json", "source")
check("50MHz/visibility0保留", "50000000" in json.dumps(profile) and profile["profile"] == "s2b-inference-platform/0.1.11" if "profile" in profile else "50000000" in json.dumps(profile))
# 只导入无副作用的静态检查器，不调用生产runner main。
spec = importlib.util.spec_from_file_location("s11_static", root / "verification/check_s2b_inference_platform.py")
checker = importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)
static = checker.check_static(root)
check("独立静态33源", len(static) == 33)
write(base / "static_result.json", static)
old_runner = run("baseline_runner", ["git", "show", "HEAD:verification/test_s2b_maxpool_address_guard_rtl.py"])
new_runner = (root / "verification/test_s2b_maxpool_address_guard_rtl.py").read_text(encoding="utf-8")
def function(text, name):
    node = next(x for x in ast.parse(text).body if isinstance(x, ast.FunctionDef) and x.name == name)
    return "\n".join(text.splitlines()[node.lineno-1:node.end_lineno])
new_cases = function(new_runner, "cases")
new_cases = "\n".join(line for line in new_cases.splitlines() if not any('("'+name+'"' in line for name in ("c0_high_plane", "c1_plane_m", "c2_plane_half_m", "channel_row_carry", "row_x_carry")))
check("旧82586循环/种子原样仅加5手算", new_cases == function(old_runner.decode("utf-8"), "cases") and "SEED = 0x581011" in new_runner)
old_geo = (root / "src/int8_maxpool_geometry.sv").read_text(encoding="utf-8")
new_geo = (root / "src/s2b_maxpool_geometry.sv").read_text(encoding="utf-8")
check("端口和组合电路不引入FF", old_geo.split(");",1)[0].replace("int8_maxpool_geometry", "s2b_maxpool_geometry") == new_geo.split(");",1)[0] and "always_ff" not in new_geo)
write(base / "audit_intermediate.json", {"checks": checks, "commands": commands})

def oracle(v):
    # 定义直接使用无限精度NCHW，不借用候选或Developer oracle。
    b,c,h,w,kh,kw,sy,sx,p,ch,y,x = v
    zero = (0,)*40
    if (kh,kw) not in ((2,2),(3,3)) or min(c,h,w,sy,sx)==0 or h+p<kh or w+p<kw: return (1,*zero)
    oh,ow = (h+p-kh)//sy+1,(w+p-kw)//sx+1
    if ch>=c or y>=oh or x>=ow: return (1,*zero)
    rows = []; mask = 0; failed = False
    for tap in range(9):
        if tap >= kh*kw: rows.extend((0,0,0,0)); continue
        dy,dx = divmod(tap,kw); ty=y*sy-p//2+dy; tx=x*sx-p//2+dx
        addr = 0
        if 0<=ty<h and 0<=tx<w:
            mask |= 1<<tap
            exact = b+ch*h*w+ty*w+tx
            failed |= exact>U32
            addr = exact if exact<=U32 else 0
        rows.extend((addr,ch,ty%(2**64),tx%(2**64)))
    return (2,*zero) if failed else (0,oh,ow,kh*kw,mask,*rows)

rng = random.Random(0xA11729)
for _ in range(100000):
    ch,h,w = (rng.getrandbits(32) for _ in range(3))
    q,r = divmod(h*w, 2**32)
    check_value = (ch != 0 and q != 0) or ch*r >= 2**32
    assert check_value == (ch*h*w >= 2**32)
    if h and w:
        y,x = rng.randrange(h),rng.randrange(w); b = rng.getrandbits(32)
        co = ch*r; row = y*w; s1=(co&U32)+(row&U32); s2=(s1&U32)+x; s3=(s2&U32)+b
        flags = check_value or row>=2**32 or s1>=2**32 or s2>=2**32 or s3>=2**32
        assert flags == (b+ch*h*w+y*w+x>U32)
check("100000独立分配恒等与三33位carry", True)
vectors = [
 (0,1,3,0x80000000,2,2,2,2,1,0,0,0),
 (0,2,2,0x80000000,2,2,2,2,1,1,0,0),
 (0,3,1,0x80000000,2,2,1,1,1,2,0,0),
 (0,2,3,0x55555555,2,2,1,1,1,1,1,0),
 (0,1,2,U32,2,2,1,1,1,0,1,1),
 (U32,U32,U32,U32,3,3,1,1,U32,U32-1,0,0),
 (0,1,U32,U32,3,3,1,1,U32,0,U32,U32),
 (U32,1,1,1,3,3,1,1,U32,0,0,0),
 (U32,1,2,2,2,2,1,1,0,0,0,0),
]
for _ in range(3500):
    c,h,w = [rng.choice([1,2,3,7,65536,2**31,U32,rng.getrandbits(32)]) for _ in range(3)]
    k=rng.choice([2,3]); p=rng.choice([0,1,2,3,8,U32]); sy,sx=[rng.choice([1,2,3,U32]) for _ in range(2)]
    oh=max(0,(h+p-k)//sy+1); ow=max(0,(w+p-k)//sx+1)
    y=rng.choice([0,min(U32,max(0,oh-1)),min(U32,oh),rng.getrandbits(32)])
    x=rng.choice([0,min(U32,max(0,ow-1)),min(U32,ow),rng.getrandbits(32)])
    ch=rng.choice([0,max(0,c-1),c,rng.getrandbits(32)])
    vectors.append((rng.choice([0,U32,rng.getrandbits(32)]),c,h,w,k,k,sy,sx,p,ch,y,x))
for h in (1,2,3,5):
    for w in (1,2,3,5):
        for k in (2,3):
            for p in (0,1,2,3,9):
                for y in (0,1,2):
                    for x in (0,1,2): vectors.append((0,2,h,w,k,k,1,1,p,1,y,x))
work = base / "rtl"; work.mkdir(); source=work/"source"; source.mkdir()
with (work / "independent_vectors.dat").open("x", encoding="utf-8", newline="\n") as stream:
    for v in vectors:
        expected=oracle(v); assert len(expected)==41
        stream.write(" ".join(format(z,"x") for z in (*v,*expected))+"\n")
write(base / "oracle_summary.json", {"seed": "0xA11729", "identity_random_samples":100000,"rtl_vectors":len(vectors),"expected_errors":dict(Counter(oracle(v)[0] for v in vectors)), "manual_first_nine_expected_errors":[oracle(v)[0] for v in vectors[:9]], "peak_math_self_rss_bytes":psutil.Process().memory_info().rss})
check("纯Python数学RSS小于128MiB", psutil.Process().memory_info().rss<=134217728)
files = ["src/int8_maxpool_geometry.sv", "src/s2b_maxpool_geometry.sv", "src/int8_maxpool_window.sv", "src/int8_upsample_query.sv", "src/s2a_maxpool_engine.sv", "src/s2a_upsample_engine.sv", "src/s2b_maxpool_engine.sv", "src/s2b_upsample_engine.sv"]
for file in files: (source/Path(file).name).write_bytes(bind(root/file,"source").read_bytes())
(work / "tb_s8_geometry.sv").write_bytes(bind(g1 / "tb_s8_geometry.sv", "source").read_bytes())
(work / "tb_s2b_geometry_specialization.sv").write_bytes(bind(g1 / "tb_s2b_geometry_specialization.sv", "source").read_bytes())
check("VECTOR_PATH必要且指向独立向量", "$value$plusargs(\"VECTOR_PATH=%s\"" in (work/"tb_s8_geometry.sv").read_text(encoding="utf-8"))
# 小矩阵使用公开START，改变合法坐标/背压并覆盖状态abort；不运行全模型。
engine_spec = importlib.util.spec_from_file_location("engine_shapes", root/"verification/test_s2b_geometry_specialization_rtl.py")
engine = importlib.util.module_from_spec(engine_spec); engine_spec.loader.exec_module(engine)
matrix_counts={}
for kind,file in (("pool","src/s2a_maxpool_engine.sv"),("upsample","src/s2a_upsample_engine.sv")):
    names=[name for direction,width,name in engine.ports(root/file) if direction=="input" and name not in engine.PORT_SKIP]
    first = (g1/(kind+"_vectors.dat")).read_text(encoding="utf-8").splitlines()[0]
    fields=[int(s,16) for s in first.split()]; legal=dict(zip(names,fields[:len(names)])); rows=[]
    def add(values, expected=0, abort=255, stall=1): rows.append([values[n] for n in names]+[expected,0,0,0,abort,stall])
    for ch,y,x in ((0,0,0),(legal["output_channels"]-1,legal["output_height"]-1,legal["output_width"]-1),(1,2,3)):
        for stall in (0,1,3): add(dict(legal,output_channel=ch,output_y=y,output_x=x),stall=stall)
    add(dict(legal,input_height=0),1); add(dict(legal,input_length_bytes=0),3); add(dict(legal,input_base_address=U32),2)
    for state in range(7 if kind=="pool" else 6): add(legal,abort=state)
    with (work/(kind+"_vectors.dat")).open("x",encoding="utf-8",newline="\n") as stream:
        for row in rows: stream.write(" ".join(format(x,"x") for x in row)+"\n")
    matrix_counts[kind]=len(rows)
toolchain=Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
bin_dir=toolchain/"mingw64/bin"; msys=toolchain/"usr/bin"; verilator=bin_dir/"verilator_bin.exe"
for file in (verilator,bin_dir/"g++.exe",msys/"make.exe"): assert file.is_file() and not file.is_symlink()
env=os.environ.copy(); env["PATH"]=str(msys)+os.pathsep+str(bin_dir)+os.pathsep+env.get("PATH",""); env["VERILATOR_ROOT"]=str(toolchain/"mingw64/share/verilator"); env["PYTHONUTF8"]="1"
common=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1"]
for label,top,selected in (("geometry","tb_s8_geometry",files[:2]),("public_engine","tb_s2b_geometry_specialization",files)):
    run(label+"_compile",common+["--top-module",top,"--Mdir","obj_"+label,*["source/"+Path(x).name for x in selected],top+".sv"],work,env)
    logs=(base/(label+"_compile.stdout.log")).read_text(encoding="utf-8")+(base/(label+"_compile.stderr.log")).read_text(encoding="utf-8")
    check("独立"+label+"无三类异常",not re.search(r"%Warning-(LATCH|UNOPTFLAT|MULTIDRIVEN)",logs))
    command=[str(work/("obj_"+label)/("V"+top+".exe"))]
    if label=="geometry": command.append("+VECTOR_PATH="+str(work/"independent_vectors.dat"))
    output=run(label+"_simulation",command,work,env)
    check("独立"+label+"真实PASS正文",b"PASS" in output)
write(base/"review_inputs.json",list(inputs.values()))
write(base/"review_result.json",{"status":"PASS","scope":"S11 maxpool geometry通道/行分配功能等价、公开周期、静态来源与G1恢复性；不批准STA/实际资源预算/硬件/G3-G5","source_commit":freeze["source_commit"],"reviewed_source_hashes":freeze["modified_files"],"reviewed_manifest_hash":digest(g1/"delivery_manifest.json"),"reviewed_trace_manifest_hash":digest(trace/"delivery_manifest.json"),"reviewer_stop":"STOP_READONLY_S11_GEO_REVIEW","checks":checks,"findings":[],"commands":commands,"elapsed_seconds":time.monotonic()-started,"sampled_owned_tree_with_reviewer_peak_bytes":peak,"absolute_peak_bytes":None,"independent_geometry_vectors":len(vectors),"identity_random_samples":100000,"public_start_matrix":matrix_counts,"limitations":["原始RTL、无限精度独立oracle及候选逐字段比较；随机有限样本不是任意U32组合穷举","独立公开POOL/UP START小矩阵逐周期比较并含abort/backpressure；不重跑15层/CONV109/整模型","G1原82586循环和种子不改、加5手算；首轮cache失败与 inherited16TB告警保留，未抬正式功能/STA指标","编译仅单job/线程且两组串行；RSS1GiB/数学128MiB工具预算，仅自有树离散读回非绝对峰","未执行Vivado/ROSS/JTAG/端口/真实进程操作，未改生产/正式原件/Git/STATE"]})
print(json.dumps({"status":"PASS","checks":len(checks),"geometry_vectors":len(vectors),"public_start_matrix":matrix_counts,"sampled_peak":peak},ensure_ascii=False))
