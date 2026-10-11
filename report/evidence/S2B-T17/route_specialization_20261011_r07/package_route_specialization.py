import sys,json,pathlib,subprocess,hashlib,difflib,datetime,psutil,shutil
sys.path.insert(0,"verification")
import check_s2b_inference_platform as c
root=pathlib.Path.cwd()
run_id="route_specialization_20261011_r07"
evidence=root/"report/evidence/S2B-T17"/run_id
work=root/"tmp/2B/S2B-T17"/run_id
if not evidence.parent.is_dir() or evidence.parent.is_symlink() or evidence.exists():raise RuntimeError("精确证据父目录或新RunId不合法")
evidence.mkdir()
if not work.is_dir() or work.is_symlink() or sorted(p.name for p in work.iterdir())!=["package_route_specialization.py"]:raise RuntimeError("包装缓存目录归属不符")
shutil.copyfile(work/"package_route_specialization.py",evidence/"package_route_specialization.py")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,data):
 path=evidence/name
 if path.exists():raise RuntimeError("禁止覆盖")
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
base="5a676b700af4c27297977379417b1694dd64840e"
head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
runs=["route_specialization_20261011_r08","route_specialization_20261011_r05","route_specialization_20261011_r06"]
reports=[json.loads((root/"report/evidence/S2B-T17"/run/"validation.json").read_text(encoding="utf-8")) for run in runs]
bindings=c.check_static(root)
for name in ("verification/test_s2b_route_specialization_rtl.py","verification/test_s2b_backend_coordinates_rtl.py","verification/test_s2b_geometry_specialization_rtl.py"):bindings[name]=sha(root/name)
for run,r in zip(runs,reports):
 if not r["status"].startswith("PASS_"):raise RuntimeError("结果未通过")
 for path,digest in r["source_sha256_pre"].items():
  if sha(root/path)!=digest:raise RuntimeError("测后源漂移"+path)
 if r["source_sha256_pre"]!=r["source_sha256_post"] or r["frozen14_sha256_pre"]!=r["frozen14_sha256_post"]:raise RuntimeError("测中源漂移")
old_path=root/"report/evidence/S2B-T17/coordinates_20261011_r04/validation.json"
old=json.loads(old_path.read_text(encoding="utf-8"))
if old["trace_summaries"]!=reports[1]["trace_summaries"]:raise RuntimeError("15层S2/S3实际trace不同")
git_sources=[]
for path in ("src/int8_route_query.sv","src/s2a_route_engine.sv","src/s2b_network_backend.sv"):
 raw=subprocess.check_output(["git","show",base+":"+path])
 artifact=evidence/("git_5a_"+pathlib.Path(path).name)
 artifact.write_bytes(raw)
 actual=(root/path).read_bytes()
 relation="RAW_IDENTICAL" if actual==raw else "ONLY_CRLF_TO_LF" if actual.replace(b"\r\n",b"\n")==raw.replace(b"\r\n",b"\n") else "S3_EXACT_AUTHORIZED_DERIVATION"
 git_sources.append({"path":path,"git_commit":base,"git_blob_sha256":hashlib.sha256(raw).hexdigest(),"actual_raw_sha256":sha(root/path),"relation":relation,"artifact":artifact.relative_to(root).as_posix()})
changed=["src/s2b_route_query.sv","src/s2b_route_engine.sv","src/s2b_network_backend.sv","board/s2b_inference_platform.json","board/s2b_inference_platform.md","vivado/s2b_inference_platform.tcl","verification/check_s2b_inference_platform.py","verification/test_s2b_backend_coordinates_rtl.py","verification/test_s2b_geometry_specialization_rtl.py","verification/test_s2b_route_specialization_rtl.py"]
diff=subprocess.check_output(["git","diff","--binary","--",*changed]).decode("utf-8")
for path in ("src/s2b_route_query.sv","src/s2b_route_engine.sv","verification/test_s2b_route_specialization_rtl.py"):
 diff+="".join(difflib.unified_diff([], (root/path).read_text(encoding="utf-8").splitlines(keepends=True),fromfile="/dev/null",tofile="b/"+path))
(evidence/"source_changes.patch").write_text(diff,encoding="utf-8",newline="\n")
checks=[]
for label,args in (("static_checker",[sys.executable,"-X","utf8","-B","verification/check_s2b_inference_platform.py"]),("diff_check",["git","diff","--check"])):
 p=subprocess.run(args,capture_output=True)
 (evidence/(label+".log")).write_bytes(p.stdout+p.stderr)
 if p.returncode!=0:raise RuntimeError("原生静态核验失败")
 checks.append({"name":label,"status":"PASS","command":subprocess.list2cmdline(args),"exit_code":p.returncode,"reason":"真实原生退出码，原日志保留。"})
for run,r in zip(runs,reports):
 for item in r["runs"]:
  checks.append({"name":run+"_"+item["name"],"status":"PASS","command":subprocess.list2cmdline(item["command"]),"exit_code":item["exit_code"],"reason":"各实际Run验证报告绑定命令、原日志、耗时、进程树RSS。"})
checks.extend([{"name":"G2独立审查","status":"NOT_RUN","command":None,"exit_code":None,"reason":"Developer已停止写入，由总控串行创建独立Reviewer。"},{"name":"新闭包50MHz综合/实现","status":"NOT_RUN","command":None,"exit_code":None,"reason":"S2失败未关闭；需新派生源通过G2、提交后干净重建，不能继承旧STA。"},{"name":"109真实整网/bit/G3","status":"NOT_RUN","command":None,"exit_code":None,"reason":"当前卷积为共享控制stub；没有新实际完整模型或实物验证。"},{"name":"通用合法groups>=3","status":"NOT_APPLICABLE","command":None,"exit_code":None,"reason":"原通用合法3/4/0x80000000/0xffffffff与派生拒绝明确不等价，非固定ROM可达域。"}])
limits=["G1只覆盖固定tiny416/N1/38层实际可达ROUTE1/2组，原14字节完整保留；生产18闭包为8原2A+6派生+4outer，不混用原/派生route。","完整15nonconv逐请求黄金采用固定地址字节模型，CONV只共享控制stub；不声称真实CONV数值或109新闭包回归。","公共START实际完整38层与12类外部输入扰动覆盖11ROUTE组数来源，未注入内部状态；其他边界与每层trace采用明确relational初态。","CSR/runtime/memory源码不变，全周期request/response/owner/abort等价支持deadline消耗不变；本轮未重跑实际CSR计时器整core联调。","原S2的50MHzSTA失败不改判，新闭包综合/实现/bit/G3均NOT_RUN；physical0.1.1仍NOT_FROZEN，inputs预期原生2。","r01/r02/r04已通过但为较早runner来源，最终direct为r08；r03基线切换后的夹具cursor初态缺失导致native1已修，失败原件保留。","工具调用量未测；3个最终验证Run各单job/thread，峰RSS来自0.1秒进程树采样，非全系统峰值。"]
freeze={"schema_version":1,"status":"PASS_S3_DEVELOPER_G1_STOP","created_utc8":datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),"task_baseline_commit":base,"current_head":head,"source_sha256":bindings,"frozen14_sha256":{p:sha(root/p) for p in c.FROZEN_CORE_SHA256},"changed_files":changed,"original_git_sources":git_sources,"verification_runs":[{"run_id":run,"path":("report/evidence/S2B-T17/"+run+"/validation.json"),"sha256":sha(root/"report/evidence/S2B-T17"/run/"validation.json"),"status":r["status"],"counts":r["simulation_counts"],"seconds":r["seconds"],"peak_tree_rss_bytes":max(x["peak_tree_rss_bytes"] for x in r["runs"])} for run,r in zip(runs,reports)],"trace_equivalence":{"status":"PASS","reference":old_path.relative_to(root).as_posix(),"reference_sha256":sha(old_path),"all_15_counts_cycles_digests_equal":True},"source_derivation":json.loads((root/"board/s2b_inference_platform.json").read_text(encoding="utf-8"))["source_derivation"],"outside_profile_witnesses":reports[0]["outside_profile_witnesses"],"math_proof":reports[0]["math_proof"],"public_entries":reports[1]["public_entries"],"limitations":limits,"resource_status":{"available_ram_bytes":psutil.virtual_memory().available,"free_disk_bytes":shutil.disk_usage(work).free,"running_verilator_or_compiler":[{"pid":p.pid,"name":p.info["name"]} for p in psutil.process_iter(["name"]) if p.info["name"] and (p.info["name"].lower() in ("verilator_bin.exe","cc1plus.exe") or p.info["name"].startswith("Vtb_s2b_"))]}}
if freeze["resource_status"]["running_verilator_or_compiler"]:raise RuntimeError("重型进程尚未退出")
write("source_freeze.json",freeze)
interfaces=json.loads((root/"report/evidence/S2B-T17/coordinates_20261011_r04/delivery_manifest.json").read_text(encoding="utf-8"))["interfaces"]
for item in interfaces:
 if sha(root/item["path"])!=item["sha256"]:raise RuntimeError("正式接口文档SHA变化")
input_paths={old_path.relative_to(root).as_posix(), "report/evidence/S2A-T01/tiny416_model_manifest.json"}
for run in runs:
 for path in (root/"report/evidence/S2B-T17"/run).rglob("*"):
  if path.is_file():input_paths.add(path.relative_to(root).as_posix())
for run in ("route_specialization_20261011_r01","route_specialization_20261011_r02","route_specialization_20261011_r03","route_specialization_20261011_r04"):
 for name in ("validation.json","simulation.log"):
  path=root/"report/evidence/S2B-T17"/run/name
  if path.is_file():input_paths.add(path.relative_to(root).as_posix())
manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":run_id,"source_commit":head,"evidence_dir":evidence.relative_to(root).as_posix(),"interfaces":interfaces,"files":[{"path":p,"sha256":h,"role":"source"} for p,h in bindings.items()]+[{"path":p,"sha256":sha(root/p),"role":"input"} for p in sorted(input_paths)]+[{"path":p.relative_to(root).as_posix(),"sha256":sha(p),"role":"log" if p.suffix==".log" else "result" if p.suffix==".json" else "artifact"} for p in evidence.iterdir() if p.is_file()],"checks":checks,"tool_versions":reports[0]["tool_versions"],"limitations":limits}
write("delivery_manifest.json",manifest)
print(json.dumps({"status":freeze["status"],"head":head,"manifest_sha256":sha(evidence/"delivery_manifest.json"),"source_freeze_sha256":sha(evidence/"source_freeze.json"),"files":len(manifest["files"]),"runs":freeze["verification_runs"]},ensure_ascii=False))
