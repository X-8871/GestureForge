#!/usr/bin/env python3
"""S5独立只读审查：原整数黄金、真实源码绑定及小规模公开端口RTL。"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import zlib
import psutil

ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
WORK = Path(__file__).resolve().parent
G1 = ROOT / "report/evidence/S2B-T17/patch_guard_20261011_r07"
ENV = os.environ.copy()
ENV.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
os.environ.update(ENV)
START = time.monotonic()
REPORT = {"task_id":"S2B-T17-S5", "status":"FAIL", "runs":[], "source_commit_at_freeze":"140e5f6b7c4511b0a0699fab3a91b87de2faf381"}

def exact(path):
    """先核验精确完整目标，再读真实文件。"""
    if not path.is_file(): raise ValueError("精确文件缺失："+str(path))
    return path

def sha(path):
    """流式计算原字节，避免载入模型副本。"""
    h=hashlib.sha256()
    with exact(path).open("rb") as f:
        while chunk:=f.read(1048576): h.update(chunk)
    return h.hexdigest()

def read(path):
    return json.loads(exact(path).read_text(encoding="utf-8"))

def save(name,data):
    p=WORK/name
    if p.exists(): raise ValueError("不覆盖已存在原件："+str(p))
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,exact(path)); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def execute(name,command,expected=0,timeout=240):
    """只监视本次进程树，单任务、预算和超时超限立即停止。"""
    out=WORK/(name+".stdout.log"); err=WORK/(name+".stderr.log")
    started=time.monotonic(); peak=0; violation=None
    with out.open("xb") as a, err.open("xb") as b:
        p=subprocess.Popen(command,cwd=WORK,env=ENV,stdout=a,stderr=b)
        while p.poll() is None:
            try:
                tree=psutil.Process(p.pid); children=[tree]+tree.children(recursive=True)
                peak=max(peak,sum(c.memory_info().rss for c in children if c.is_running()))
            except psutil.Error: pass
            if peak>1610612736 or time.monotonic()-started>timeout:
                violation="内存或时间预算超限"
                subprocess.run(["taskkill","/PID",str(p.pid),"/T","/F"],capture_output=True,timeout=30); p.wait(timeout=30); break
            time.sleep(.1)
    row={"name":name,"command":command,"native_exit_code":p.returncode,"expected_exit_code":expected,"seconds":round(time.monotonic()-started,3),"peak_tree_rss_bytes_sampled_0_1s":peak,"budget_failure":violation,"stdout_sha256":sha(out),"stderr_sha256":sha(err)}
    REPORT["runs"].append(row);save(name+".native.json",row)
    print(json.dumps({"command":name,"native_exit_code":p.returncode,"seconds":row["seconds"],"peak_tree_rss_bytes":peak}),flush=True)
    if violation or (expected=="nonzero" and p.returncode==0) or (isinstance(expected,int) and p.returncode!=expected): raise ValueError("原生命令退出不符："+name)

def metadata(name):
    text=exact(ROOT/"src/s2a_network_descriptor_pkg.sv").read_text(encoding="utf-8")
    match=re.search(r"\b"+name+r"\s+\[0:37\]\s*=\s*'\{(.*?)\};",text,re.S)
    if not match: raise ValueError("冻结描述符元数据缺失")
    values=[int(v,16) for v in re.findall(r"\d+'h([0-9a-fA-F]+)",match[1])]
    assert len(values)==38
    return values

MQ=metadata("S2A_T23_MQ_CHANNEL_COUNT"); MB=metadata("S2A_T23_MQ_BASE"); OP=metadata("S2A_OP")

def original_error(v):
    """以未化简RTL的完整整数和首错顺序独立建黄金，不调用开发oracle。"""
    lid=v["layer_index"]; c=v["input_channels"]; kh=v["kernel_height"]; kw=v["kernel_width"]
    r=c*kh*kw
    zero=any(v[n]==0 for n in ("input_channels","input_height","input_width","output_channels","output_height","output_width","kernel_height","kernel_width","stride_y","stride_x"))
    bad=(not v["buffer_owner_pl"] or v["activation_mode"]>1 or v["input_batch_count"]!=1 or v["output_batch_count"]!=1 or v["output_batch"]!=0 or zero or v["groups"]!=1 or v["padding_value_int8"]!=0 or not r or r>4608 or lid>=38 or (lid<38 and OP[lid]!=0) or lid!=v["weight_layer_index"])
    if bad: return 2 if lid>=38 or lid!=v["weight_layer_index"] else 1
    counts=((c*v["input_height"]*v["input_width"],v["input_length_bytes"]),(v["output_channels"]*v["output_height"]*v["output_width"],v["output_length_bytes"]),(v["output_channels"]*r,v["quantized_weight_bytes"]))
    if any(n>0xffffffff or n!=length for n,length in counts): return 3
    h=(min(v["output_height"],8)-1)*v["stride_y"]+kh; w=(min(v["output_width"],8)-1)*v["stride_x"]+kw
    ends=any(v[a]+v[b]>2**32 for a,b in (("input_base_address","input_length_bytes"),("output_base_address","output_length_bytes"),("weight_package_base_address","weight_package_length_bytes")))
    if ends or not v["weight_package_length_bytes"] or v["quantized_weight_offset"]+v["quantized_weight_bytes"]>v["weight_package_length_bytes"] or MQ[lid]!=v["output_channels"] or MB[lid]+v["output_channels"]>3164 or h*w*c>51200 or min(v["output_channels"],8)*r>36864: return 2
    for axis,first,last,stride in (("height","pad_top","pad_bottom","stride_y"),("width","pad_left","pad_right","stride_x")):
        n=v["input_"+axis]+v[first]+v[last]; k=v["kernel_"+axis]; s=v[stride]; span=(n-k)&((1<<64)-1); product=v["output_"+axis]*s
        if n<k or product<=span or product>((span+s)&((1<<64)-1)): return 1
    return 0

def narrowed(c,kh,kw,oh,ow,sy,sx):
    """独立模拟显式无符号位宽以寻找截断反例。"""
    dy=min(oh,8)-1; dx=min(ow,8)-1
    h=dy*(sy&65535)+(kh&8191); w=dx*(sx&65535)+(kw&8191)
    hb=(dy!=0 and sy>>16!=0) or h>>16!=0 or (h&65535)>51200
    wb=(dx!=0 and sx>>16!=0) or w>>16!=0 or (w&65535)>51200
    p=(h&65535)*(w&65535); q=(p&65535)*(c&8191)
    assert h<2**19 and w<2**19 and p<2**32 and q<2**29
    return bool(hb or wb or p>>16!=0 or q>51200)

def audit():
    assert ROOT.is_dir() and WORK.parent.is_dir()
    assert sha(G1/"delivery_manifest_r04.json")=="9f6bf727745f28e363cf8877a0ec35216f01ea9e2a6fcdc59b7b5dba0c6d8a42"
    assert sha(G1/"source_freeze.json")=="4d9540a77c9c15e796609ba54040090556b577f3a9851434166859aba19090f6"
    freeze=read(G1/"source_freeze.json");manifest=read(G1/"delivery_manifest_r04.json")
    assert len(freeze["source_sha256"])==38 and len(manifest["files"])==344
    for item in manifest["files"]: assert sha(ROOT/item["path"])==item["sha256"],item["path"]
    for path,digest in freeze["source_sha256"].items(): assert sha(ROOT/path)==digest,path
    assert all(sha(ROOT/p)==s for p,s in freeze["frozen14_sha256"].items())
    checker=module(ROOT/"verification/check_s2b_inference_platform.py","review_checker")
    static=checker.check_static(ROOT);assert len(static)==31
    profile=read(ROOT/"board/s2b_inference_platform.json")
    assert profile["version"]=="s2b-inference-platform/0.1.5" and profile["clock_hz"]==50000000 and profile["visibility_default"]==0
    before=exact(G1/"raw/patch_guard_20261011_r01/source_before/src/s2b_conv_tile_engine.sv").read_text(encoding="utf-8")
    after=exact(ROOT/"src/s2b_conv_tile_engine.sv").read_text(encoding="utf-8")
    assert sha(G1/"raw/patch_guard_20261011_r01/source_before/src/s2b_conv_tile_engine.sv")=="58310baf69021502e6629fe80e16929d2de285fed96cce0640c18b9f5c9f0b4e"
    assert before.split(");",1)[0]==after.split(");",1)[0]
    assert before[before.index("    always_ff"):]==after[after.index("    always_ff"):]
    assert before.count("always_ff")==after.count("always_ff")==2
    assert sha(G1/"source_changes.diff")==freeze["source_diff_sha256"]
    changed=re.findall(r"^diff --git a/(.*?) b/",(G1/"source_changes.diff").read_text(encoding="utf-8"),re.M)
    assert set(changed)==set(freeze["changed_paths"]) and len(changed)==9
    utf={p:exact(ROOT/p).read_text(encoding="utf-8").count("\ufffd") for p in changed}
    assert not any(utf.values())
    validation=[]
    for run in range(2,7):
        p=G1/("raw/patch_guard_20261011_r"+str(run).zfill(2));data=read(p/"validation.json")
        assert data["status"].startswith("PASS") and all(item["exit_code"]==0 for item in data["runs"])
        for item in data["runs"]: assert sha(ROOT/item["log"])==item["log_sha256"]
        validation.append({"run":run,"status":data["status"],"coverage":data["actual_coverage"] if "actual_coverage" in data else data["simulation_counts"]})
    source_g1=(G1/"raw/patch_guard_20261011_r02/validation_vectors.txt").read_text(encoding="utf-8").splitlines()
    prior_path=ROOT/"report/evidence/S2B-T17/conv_validation_20261011_r06/validation_vectors.txt"
    assert sha(prior_path)=="e7db7751e31fbdf23daa2e32bfa57e44dfb7a73404c47463b566242e24151d22"
    prior=exact(prior_path).read_text(encoding="utf-8").splitlines();assert len(prior)==2871 and source_g1[:2871]==prior
    golden=G1/"raw/patch_guard_20261011_r03/cpu_layer0_expected.bin"
    assert golden.stat().st_size==1384448 and sha(golden)=="220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8"
    shard=Path(r"D:\FPGA_Competition\report\evidence\S2A-T25\tensors\sample_000.zlib")
    assert sha(shard)=="49488538ced503bad996e284a3593d4fc7a1cf3b605d90221b3ca09875c4966e"
    tensor=zlib.decompress(shard.read_bytes());assert hashlib.sha256(tensor).hexdigest()=="090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80"
    assert tensor[:1384448]==golden.read_bytes()
    s4cpu=read(ROOT/"report/evidence/S2B-T17/independent_conv_validation_review_20261011_r01/raw/independent_conv_validation_review_20261011_r03/independent_cpu_result.json")
    REPORT["source_sha256"]=freeze["source_sha256"]
    REPORT["audit"]={"bindings_streamed":344,"sources":38,"static_sources":31,"extra_sources":7,"changed_paths":changed,"frozen14_unchanged":True,"header_identical":True,"always_ff_before_after":[2,2],"sequential_suffix_identical":True,"replacement_character_counts":utf,"g1":validation,"g1_vectors_preserved_from_s4":2871,"layer0_bytes":1384448,"layer0_gold_sha256":sha(golden),"layer0_equals_t25_slice":True,"prior_independent_cpu_result":s4cpu,"scope":"原G1完整layer0数值与独立S4/T25黄金同源且原字节相同；本轮不重跑109或整layer0。"}
    save("audit_result.json",REPORT["audit"])

def vectors():
    sys.path.insert(0,str(ROOT/"verification"))
    generator=module(ROOT/"verification/test_s2b_conv_validation_rtl.py","review_harness")
    names=[n for d,w,n in generator.ports() if d=="input" and n not in generator.SKIP]
    rows=[];labels=[]
    base={n:0 for n in names};base.update(input_batch_count=1,output_batch_count=1,input_channels=1,input_height=1,input_width=1,output_channels=32,output_height=1,output_width=1,kernel_height=1,kernel_width=1,stride_y=1,stride_x=1,groups=1,weight_package_base_address=0x100000,weight_package_length_bytes=5903100,quantized_weight_offset=316,activation_mode=1,output_base_address=0x1000000,buffer_owner_pl=1)
    def add(label,expected=None,**changes):
        v=dict(base);v.update(changes)
        for field,number in (("input_length_bytes",v["input_channels"]*v["input_height"]*v["input_width"]),("output_length_bytes",v["output_channels"]*v["output_height"]*v["output_width"]),("quantized_weight_bytes",v["output_channels"]*v["input_channels"]*v["kernel_height"]*v["kernel_width"])):
            if field not in changes:v[field]=number&0xffffffff
        e=original_error(v)
        if expected is not None: assert e==expected,(label,e,expected)
        rows.append((v,e));labels.append({"label":label,"inputs":v,"expected_error":e})
    add("R4609首错",1,input_channels=4609)
    add("R4608可达",0,input_channels=4608)
    add("P51200等号",0,input_height=200,input_width=256,output_height=2,output_width=4,stride_y=199,stride_x=85)
    add("Q51201",2,input_channels=3,input_height=3,input_width=5690,output_width=2,kernel_height=3,kernel_width=3,stride_x=5686)
    add("P65536高位",2,input_height=256,input_width=256,output_height=4,output_width=4,stride_y=85,stride_x=85)
    add("D0双32位最大stride合法",0,stride_y=0xffffffff,stride_x=0xffffffff)
    add("H2^32加1",2,input_height=0xffffffff,output_height=2,kernel_height=2,stride_y=0xffffffff,pad_top=1,pad_bottom=1)
    add("非1/3核合法",0,kernel_height=2,kernel_width=5,input_height=2,input_width=5)
    add("2^32长度首错",3,input_height=65536,input_width=65536,input_length_bytes=0)
    for end in (-1,0,1):add("地址端点偏差"+str(end),2 if end==1 else 0,input_base_address=(1<<32)-4+end,input_height=4,output_height=4)
    for field in ("input_channels","kernel_height","kernel_width"):
        add("13位混叠"+field,1,**{field:8193})
    add("长度压patch范围",3,input_height=256,input_width=256,output_height=4,output_width=4,stride_y=85,stride_x=85,input_length_bytes=0)
    add("batch压MQ与长度",1,input_batch_count=2,output_channels=31,input_length_bytes=0)
    add("层索引压batch",2,layer_index=38,input_batch_count=2)
    add("零维压长度",1,input_height=0,input_length_bytes=1)
    add("MQ错误仍拒绝",2,output_channels=31)
    for line in (G1/"raw/patch_guard_20261011_r02/validation_vectors.txt").read_text(encoding="utf-8").splitlines():
        values=[int(x,16) for x in line.split()];assert len(values)==len(names)+2
        v=dict(zip(names+["buffer_owner_pl"],values));assert original_error(v)==values[-1]
        rows.append((v,values[-1]))
    rng=random.Random(0x5A171011);math_count=0
    for index in range(40000):
        c=rng.randint(1,4608);kh=rng.randint(1,4608//c);kw=rng.randint(1,4608//(c*kh));oh=rng.randint(1,16);ow=rng.randint(1,16)
        sy=rng.choice((1,51199,51200,65535,65536,0xffffffff,rng.getrandbits(32)));sx=rng.choice((1,51199,51200,65535,65536,0xffffffff,rng.getrandbits(32)))
        full=((min(oh,8)-1)*sy+kh)*((min(ow,8)-1)*sx+kw)*c>51200
        assert full==narrowed(c,kh,kw,oh,ow,sy,sx)
        math_count+=1
        if index<1024:
            ih=(oh-1)*sy+kh;iw=(ow-1)*sx+kw
            if ih>0xffffffff or iw>0xffffffff:oh=ow=1;ih=kh;iw=kw
            add("独立定向随机"+str(index),input_channels=c,kernel_height=kh,kernel_width=kw,input_height=ih,input_width=iw,output_height=oh,output_width=ow,stride_y=sy,stride_x=sx)
    save("independent_vectors.json",{"seed":0x5A171011,"math_cases":math_count,"rtl_vectors":len(rows),"manual_and_additional":labels,"method":"完整无界整数原RTL首错顺序；开发新增oracle完全未调用。"})
    (WORK/"validation_vectors.txt").write_text("\n".join(" ".join(f"{v[n]&0xffffffff:x}" for n in names+["buffer_owner_pl"])+f" {e:x}" for v,e in rows)+"\n",encoding="utf-8",newline="\n")
    small=dict(base);small.update(input_channels=3,input_height=4,input_width=4,input_length_bytes=48,output_height=2,output_width=2,output_length_bytes=128,kernel_height=3,kernel_width=3,quantized_weight_bytes=864)
    bench=generator.boundary_tb(names,small)
    bench=bench.replace("  start_dut; tick;","  if ($test$plusargs(\"INJECT_EXPECTATION\") && cases==0) expected_error=expected_error^1;\n  start_dut; tick;",1)
    bench=bench.replace("(result_error_code !== candidate_result_error_code)","(result_error_code !== (candidate_result_error_code ^ ($test$plusargs(\"INJECT_PUBLIC\") ? 3'd1 : 3'd0)))")
    assert "INJECT_EXPECTATION" in bench and "INJECT_PUBLIC" in bench
    (WORK/"tb_s2b_conv_validation.sv").write_text(bench,encoding="utf-8",newline="\n")
    REPORT["independent_math"]={"seed":0x5A171011,"cases":math_count,"rtl_vectors":len(rows),"bound_H":7*65535+4608,"bound_Q":65535*4608,"minimum_C_KH_KW":1,"weight_group_bound":8*4608,"D0_stride_high_bits":"合法不拒绝","kernel_scope":"通用正KH/KW，不限1和3"}

def rtl():
    pre={"available_ram":psutil.virtual_memory().available,"disk_free":shutil.disk_usage(WORK).free,"tools":[{"pid":p.pid,"name":p.info["name"]} for p in psutil.process_iter(["name"]) if p.info["name"] and re.search(r"^(vivado|verilator_bin|cc1plus|xsim|Vtb).*\.exe$",p.info["name"],re.I)]}
    assert pre["available_ram"]>=2147483648
    assert all(p["pid"]==23188 and p["name"].lower()=="vivado.exe" for p in pre["tools"])
    save("resource_preflight.json",pre)
    tools=Path(r"D:\FPGA_S2A_MSYS2_20261001\env");compiler=exact(tools/"mingw64/bin/verilator_bin.exe")
    ENV["PATH"]=str(tools/"usr/bin")+os.pathsep+str(tools/"mingw64/bin")+os.pathsep+ENV.get("PATH","");ENV["VERILATOR_ROOT"]=str(tools/"mingw64/share/verilator")
    execute("tool_version",[str(compiler),"--version"])
    source=WORK/"source";source.mkdir()
    names=("s2a_network_descriptor_pkg.sv","s2a_conv_tile_engine.sv","s2b_conv_tile_engine.sv")
    for n in names:shutil.copyfile(exact(ROOT/"src"/n),source/n)
    cmd=[str(compiler),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","--top-module","tb_s2b_conv_validation","--Mdir","obj_dir","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1",*["source/"+n for n in names],"tb_s2b_conv_validation.sv"]
    execute("independent_compile",cmd)
    cache=sum(p.stat().st_size for p in (WORK/"obj_dir").rglob("*") if p.is_file());assert cache<=314572800
    sim=[str(exact(WORK/"obj_dir/Vtb_s2b_conv_validation.exe"))]
    execute("independent_simulation",sim)
    log=(WORK/"independent_simulation.stdout.log").read_text(encoding="utf-8")
    match=re.search(r"PASS CONV_VALIDATION vectors=(\d+) cycles=(\d+) abort_mask=([0-9a-fA-F]+) reset_mask=([0-9a-fA-F]+) response_cases=24 raw80=1",log)
    assert match and int(match[1])==REPORT["independent_math"]["rtl_vectors"] and int(match[3],16)==int(match[4],16)==0xfffff
    execute("expected_gold_mismatch",sim+["+INJECT_EXPECTATION"],"nonzero")
    execute("expected_public_mismatch",sim+["+INJECT_PUBLIC"],"nonzero")
    REPORT["rtl"]={"coverage":match.group(0),"cache_bytes":cache,"compile_jobs":1,"simulation_threads":1,"harness_origin":"逐行审过开发公开口夹具，独立生成黄金；双向注入真实fatal验证比较器敏感性。","numeric_scope":"该独立小RTL覆盖合法状态/响应错误/非法raw80；非零完整数值取G1及先前独审T25完整layer0，不伪称本小RTL使用非零真实模型。"}

try:
    audit();vectors();rtl()
    for path,digest in REPORT["source_sha256"].items():assert sha(ROOT/path)==digest,path
    REPORT["remaining_heavy"]=[{"pid":p.pid,"name":p.info["name"]} for p in psutil.process_iter(["name"]) if p.info["name"] and re.search(r"^(verilator_bin|cc1plus|xsim|Vtb).*\.exe$",p.info["name"],re.I)]
    assert not REPORT["remaining_heavy"]
    REPORT["status"]="PASS_G2_ONLY"
except Exception as exc:
    REPORT["error"]=repr(exc)
finally:
    REPORT["seconds"]=round(time.monotonic()-START,3)
    REPORT["peak_self_working_set_bytes"]=getattr(psutil.Process().memory_info(),"peak_wset",None)
    REPORT["limitations"]=["仅S5组合判据等价、G1绑定、源冻结G2；无新STA、109整网、板上G3/G4/G5。","当前clock50MHz、visibility0与18源闭包不变，旧S4时序仍失败，不继承旧时序记录。","无Git、ROSS、SDK、串口、板卡或生产源写入；总控拥有后续提交。","采样内存仅本次子进程树0.1s及Python自身OS峰；系统峰与全代理工具调用量未测。"]
    save("review_receipt.json",REPORT)
    names=[p for p in WORK.iterdir() if p.is_file()]
    names+=list((WORK/"source").iterdir()) if (WORK/"source").is_dir() else []
    entries=[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"role":"independent_review_raw"} for p in names]
    raw={"schema_version":1,"task_id":"S2B-T17-S5","status":REPORT["status"],"files":entries,"bytes_by_path":{p.relative_to(ROOT).as_posix():p.stat().st_size for p in names},"manifest_self":"自身SHA与字节数由总控接收时另算；不递归扫描obj_dir缓存。"}
    save("raw_delivery_manifest.json",raw)
    print(json.dumps({"status":REPORT["status"],"error":REPORT.get("error"),"receipt_sha256":sha(WORK/"review_receipt.json"),"raw_delivery_manifest_sha256":sha(WORK/"raw_delivery_manifest.json"),"raw_files":len(entries),"seconds":REPORT["seconds"]},ensure_ascii=False),flush=True)
sys.exit(0 if REPORT["status"]=="PASS_G2_ONLY" else 2)
