"""独立S1来源核查及单job差分；只写本隔离目录。"""
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
import psutil

OUT = Path(__file__).absolute().parent
ROOT = Path(__file__).absolute().parents[4]
sys.path.insert(0, str(ROOT))
from verification import test_s2b_geometry_specialization_rtl as r
from verification import check_s2b_inference_platform as c
from verification import check_stage_delivery as d
from verification.s2b_board_acceptance import save, binding

BASE = "b8d5e5238fd01c460aa3155144785d65e06fc16e"
EVIDENCE = ROOT / "report/evidence/S2B-T17/specialization_20261011_r04"
TOOLS = Path(r"D:\FPGA_S2A_MSYS2_20261001\env")

def prepare():
    """核查证据、源关系及新增测试刺激，暂不启动编译。"""
    started = time.monotonic()
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == BASE
    validation = json.loads((EVIDENCE/"validation.json").read_text(encoding="utf-8"))
    provenance = json.loads((EVIDENCE/"provenance.json").read_text(encoding="utf-8"))
    sources = c.check_static(ROOT)
    for path, sha in validation["source_sha256_post"].items():
        assert r.sha(ROOT/path) == sha
    frozen = []
    for path, sha in c.FROZEN_CORE_SHA256.items():
        raw = (ROOT/path).read_bytes()
        blob = subprocess.check_output(["git", "show", "671f9cf494b92ce182b3f1542fefd0cfd4b209f5:"+path], cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest() == sha
        assert raw.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n")
        frozen.append({"path": path, "raw_sha256": sha, "git_blob_sha256": hashlib.sha256(blob).hexdigest(), "crlf_lines": raw.count(b"\r\n")})
    rules = {
      "src/s2a_maxpool_engine.sv": ("src/s2b_maxpool_engine.sv", [("module s2a_maxpool_engine (","module s2b_maxpool_engine ("), *[("."+name+"("+name+")", "."+name+"(32'd"+str(value)+")") for name,value in (("kernel_height",2),("kernel_width",2),("stride_y",2),("stride_x",2),("darknet_padding_parameter",1))]]),
      "src/s2a_upsample_engine.sv": ("src/s2b_upsample_engine.sv", [("module s2a_upsample_engine (","module s2b_upsample_engine ("),(".stride(stride)",".stride(32'd2)")]),
      "src/s2a_network_backend.sv": ("src/s2b_network_backend.sv", [("module s2a_network_backend (","module s2b_network_backend ("),("s2a_maxpool_engine u_maxpool_engine","s2b_maxpool_engine u_maxpool_engine"),("s2a_upsample_engine u_upsample_engine","s2b_upsample_engine u_upsample_engine")]),
      "src/s2a_stage2a_core_ooc.sv": ("src/s2b_stage2b_core.sv", [("module s2a_stage2a_core_ooc #(","module s2b_stage2b_core #("),("s2a_network_backend u_network_backend","s2b_network_backend u_network_backend")])}
    derived = []
    for old, (new, replacements) in rules.items():
        raw = (ROOT/old).read_bytes()
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for before, after in replacements:
            assert text.count(before) == 1
            text = text.replace(before, after)
        assert text.encode("utf-8") == (ROOT/new).read_bytes()
        derived.append({"source": old,"path":new,"sha256":r.sha(ROOT/new),"upstream_crlf_lines":raw.count(b"\r\n"),"derived_crlf_lines":(ROOT/new).read_bytes().count(b"\r\n")})
    negatives = r.checker_negatives(c, OUT, sources)
    assert len(negatives) == 26
    model = json.loads((ROOT/r.MODEL).read_text(encoding="utf-8"))
    assert r.sha(ROOT/r.MODEL) == r.MODEL_SHA
    declarations = {"pool":r.ports(ROOT/"src/s2a_maxpool_engine.sv"),"upsample":r.ports(ROOT/"src/s2a_upsample_engine.sv")}
    coverage = {}
    for kind, declarations_here in declarations.items():
        text, stats = r.vector_data(kind, declarations_here, model)
        names = stats["parameter_order"]
        rows = text.splitlines()
        rng = random.Random(0x2B1719 + (kind == "upsample"))
        extras = []
        for layer_id in ((9,17,25) if kind == "pool" else (33,)):
            if kind == "pool":
                basis = next(line for line in rows if int(line.split()[0],16) == layer_id)
            else: basis = rows[0]
            values = {name: int(value,16) for name,value in zip(names,basis.split())}
            def append_case(changes, expected):
                mutated = {**values,**changes}
                extras.append(" ".join(f"{mutated[name]:x}" for name in names)+" "+" ".join(f"{v:x}" for v in (expected,0,0,0,255,1)))
            for _ in range(20):
                append_case({"input_height":rng.choice((0,3,0x80000000,0xFFFFFFFF)),"input_length_bytes":0,"input_base_address":0xFFFFFFFF,"output_y":0xFFFFFFFF},1)
                append_case({"input_length_bytes":0,"input_base_address":0xFFFFFFFF},3)
                append_case({"output_base_address":0xFFFFFFFF},2)
            # 末边界合法坐标在更长等待下仍比较全部公开输出及独立地址/数值。
            source = model["layers"][layer_id]["output_shape_nchw"]
            append_case({"output_channel":source[1]-1,"output_y":source[2]-1,"output_x":source[3]-1},0)
        (OUT/(kind+"_vectors.dat")).write_text(text+"\n".join(extras)+"\n",encoding="utf-8",newline="\n")
        coverage[kind] = {"base_vectors":stats["vectors"],"independent_added":len(extras),"total":stats["vectors"]+len(extras),"seed":0x2B1719+(kind=="upsample")}
    tb = r.generate_tb(declarations)
    # 独立扩展请求背压与响应等待，保留相同事务/取消语义。
    tb = tb.replace("(cycles % 5) != 0", "(cycles % 11) >= 7")
    tb = tb.replace("? 0 : cycles % 4", "? 0 : 7 + cycles % 4")
    (OUT/"tb_s2b_geometry_specialization.sv").write_text(tb,encoding="utf-8",newline="\n")
    (OUT/"source").mkdir()
    for path in r.RTL: shutil.copyfile(ROOT/path,OUT/"source"/Path(path).name)
    result = {"schema_version":1,"status":"PASS_PRECOMPILE_CHECKS","baseline_commit":BASE,"frozen14":frozen,"derived":derived,"checker_negatives":negatives,"coverage":coverage,"source_bindings":validation["source_sha256_post"],"evidence":{name:binding(EVIDENCE/name) for name in ("delivery_manifest.json","validation.json","provenance.json")},"seconds":time.monotonic()-started,"limitations":["仅来源与26反例检查；尚未独立运行RTL。"]}
    for mode in ("evidence","inputs"): result["packaging_"+mode] = d.check_manifest(mode,str(EVIDENCE/"delivery_manifest.json"),str(ROOT))
    save(OUT/"precompile_result.json",result)
    print(json.dumps({"status":result["status"],"coverage":coverage,"seconds":result["seconds"]}))

def run():
    """在总控已分配重型槽运行受限单job编译与差分。"""
    report = {"runs":[],"hardware_execution":"NOT_RUN"}
    pre = json.loads((OUT/"precompile_result.json").read_text(encoding="utf-8"))
    for path,sha in pre["source_bindings"].items(): assert r.sha(ROOT/path)==sha
    available = psutil.virtual_memory().available
    free = shutil.disk_usage(OUT).free
    report["resources"]={"available_bytes":available,"disk_free":free,"processes":[{"pid":p.pid,"name":p.info["name"],"rss":p.memory_info().rss} for p in psutil.process_iter(["name"]) if p.info["name"] and any(x in p.info["name"].lower() for x in ("vivado","verilator","cc1plus"))],"slot_authorization":"root明确分配唯一重型槽，Vivado保持idle"}
    assert available > 2*1024**3 and free > 1024**3
    env=os.environ.copy()
    env["PATH"]=str(TOOLS/"usr/bin")+os.pathsep+str(TOOLS/"mingw64/bin")+os.pathsep+env.get("PATH","")
    env["VERILATOR_ROOT"]=str(TOOLS/"mingw64/share/verilator")
    env["PYTHONUTF8"]="1"
    cmd=[str(TOOLS/"mingw64/bin/verilator_bin.exe"),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","--top-module","tb_s2b_geometry_specialization","--Mdir","obj_dir","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O0",*["source/"+Path(path).name for path in r.RTL],"tb_s2b_geometry_specialization.sv"]
    for path in (Path(cmd[0]),TOOLS/"mingw64/bin/g++.exe",TOOLS/"usr/bin/make.exe"): c.exact_file(path)
    try:
        r.execute("compile",cmd,OUT,OUT,env,report,600)
        r.execute("simulation",[str(OUT/"obj_dir/Vtb_s2b_geometry_specialization.exe")],OUT,OUT,env,report,600)
        text=(OUT/"simulation.log").read_text(encoding="utf-8")
        match=re.findall(r"PASS GEOMETRY_SPECIALIZATION pool=(\d+) upsample=(\d+) cycles=(\d+) pool_abort=(\d+) upsample_abort=(\d+)",text)
        assert len(match)==1
        counts=list(map(int,match[0]))
        assert counts[:2]==[pre["coverage"][k]["total"] for k in ("pool","upsample")] and counts[3:]==[127,63]
        report["simulation_counts"]=dict(zip(("pool","upsample","cycles","pool_abort","upsample_abort"),counts))
        for path,sha in pre["source_bindings"].items(): assert r.sha(ROOT/path)==sha
        report["status"]="PASS_INDEPENDENT_G2_S1"
    except BaseException as error:
        report.update(status="FAIL_INDEPENDENT",error=repr(error))
        raise
    finally:
        save(OUT/"rtl_result.json",report)
    print(json.dumps({"status":report["status"],"counts":report["simulation_counts"],"runs":report["runs"]}))

if __name__=="__main__":
    (prepare if sys.argv[1]=="prepare" else run)()
