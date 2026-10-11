"""冻结本次真实测试来源、差异及交付包装，不替代独立审查。"""
import ast,datetime,difflib,hashlib,json,pathlib,psutil,shutil,subprocess,sys
sys.path.insert(0,"verification")
import check_s2b_inference_platform as checker
import test_s2b_conv_validation_rtl as conv
root=pathlib.Path.cwd();run="conv_validation_20261011_r15";base=conv.BASELINE
work=root/"tmp/2B/S2B-T17"/run;evidence=root/"report/evidence/S2B-T17"/run
if not evidence.parent.is_dir() or evidence.exists():raise RuntimeError("父目录不符或Run已存在")
evidence.mkdir();shutil.copyfile(pathlib.Path(__file__),evidence/pathlib.Path(__file__).name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 p=evidence/name
 if p.exists():raise RuntimeError("不能覆盖")
 p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
changed=["src/s2b_conv_tile_engine.sv","src/s2b_network_backend.sv","board/s2b_inference_platform.json","board/s2b_inference_platform.md","vivado/s2b_inference_platform.tcl","verification/check_s2b_inference_platform.py","verification/test_s2b_conv_validation_rtl.py","verification/test_s2b_backend_coordinates_rtl.py","verification/test_s2b_geometry_specialization_rtl.py","verification/test_s2b_route_specialization_rtl.py"]
bindings=checker.check_static(root)
for p in changed+["sim/tb_s2a_t66_candidate_blackbox.sv","verification/s1_t02_d2_int8_forward.py"]:bindings[p]=sha(root/p)
runs=["conv_validation_20261011_r06","conv_validation_20261011_r10","conv_validation_20261011_r11","conv_validation_20261011_r12","conv_validation_20261011_r13"]
reports=[json.loads((root/"report/evidence/S2B-T17"/r/"validation.json").read_text(encoding="utf-8")) for r in runs]
for r,v in zip(runs,reports):
 if not v["status"].startswith("PASS"):raise RuntimeError("最终run未通过"+r)
 if v["source_sha256_pre"]!=v["source_sha256_post"]:raise RuntimeError("测中源漂移"+r)
 for p,d in v["source_sha256_pre"].items():
  if r==runs[0] and p==conv.RUNNER:continue
  if sha(root/p)!=d:raise RuntimeError("测后源漂移"+r+":"+p)
oldsource=root/"report/evidence/S2B-T17/conv_validation_20261011_r07/runner_source_used.py"
old=oldsource.read_text(encoding="utf-8");new=(root/conv.RUNNER).read_text(encoding="utf-8")
if sha(oldsource)!=reports[0]["source_sha256_pre"][conv.RUNNER]:raise RuntimeError("r06旧runner来源不符")
def functions(text):return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
a,b=functions(old),functions(new);names=("ports","rom","oracle","vectors","pair","boundary_tb","layer0_tb")
if any(a[n]!=b[n] for n in names):raise RuntimeError("边界生成/黄金/执行TB函数已变化")
model=json.loads((root/conv.support.MODEL).read_text(encoding="utf-8"));params,vectors,small,math_report=conv.vectors(model)
refdir=root/"report/evidence/S2B-T17"/runs[0]
if vectors.encode()!= (refdir/"validation_vectors.txt").read_bytes().replace(b"\r\n",b"\n") or conv.boundary_tb(params,small).encode()!=(refdir/"tb_s2b_conv_validation.sv").read_bytes():raise RuntimeError("最终边界TB/向量与r06不同")
if (root/"report/evidence/S2B-T17/conv_validation_20261011_r10/validation_vectors.txt").read_bytes()!=(refdir/"validation_vectors.txt").read_bytes():raise RuntimeError("最终已写入向量raw与r06不同")
mapping={"status":"PASS_EXACT_BOUNDARY_SOURCE_MAPPING","old_runner":str(oldsource.relative_to(root)).replace("\\","/"),"old_sha256":sha(oldsource),"current_runner":conv.RUNNER,"current_sha256":sha(root/conv.RUNNER),"identical_functions":{n:hashlib.sha256(a[n].encode()).hexdigest() for n in names},"vectors_sha256":sha(refdir/"validation_vectors.txt"),"vector_newline_policy":"r06与最终r10的已写向量raw逐字节相同；生成器LF只与实文件CRLF转LF后的文本比。","tb_sha256":sha(refdir/"tb_s2b_conv_validation.sv"),"changes":"只新增CPU库线程环境、实际getter/资源记录、冻结manifest与D2换行关系门禁及报告字段。上述函数/生成边界TB/向量、RTL和原执行命令不变；root已按影响范围授权复用r06。"}
write("boundary_source_mapping.json",mapping)
git_sources=[]
for p in ("src/s2a_conv_tile_engine.sv","src/s2b_network_backend.sv","verification/s1_t02_d2_int8_forward.py"):
 raw=subprocess.check_output(["git","show",base+":"+p]);dest=evidence/("git_baseline_"+pathlib.Path(p).name);dest.write_bytes(raw)
 actual=(root/p).read_bytes();relation="RAW_IDENTICAL" if raw==actual else "ONLY_CRLF_TO_LF" if raw.replace(b"\r\n",b"\n")==actual.replace(b"\r\n",b"\n") else "S4_CONV_REFERENCE_ONLY_AUTHORIZED"
 git_sources.append({"path":p,"commit":base,"git_blob_sha256":hashlib.sha256(raw).hexdigest(),"actual_raw_sha256":sha(root/p),"relation":relation})
diff=subprocess.check_output(["git","diff","--binary","--",*changed]).decode("utf-8")
for p in ("src/s2b_conv_tile_engine.sv",conv.RUNNER):diff+="".join(difflib.unified_diff([], (root/p).read_text(encoding="utf-8").splitlines(keepends=True),fromfile="/dev/null",tofile="b/"+p))
(evidence/"source_changes.patch").write_text(diff,encoding="utf-8",newline="\n")
summary=[];checks=[]
for r,v in zip(runs,reports):
 summary.append({"run_id":r,"status":v["status"],"validation_sha256":sha(root/"report/evidence/S2B-T17"/r/"validation.json"),"seconds":v.get("elapsed_seconds",v.get("seconds")),"coverage":v.get("actual_coverage",v.get("simulation_counts")),"peak_tree_rss_bytes":max(t["peak_tree_rss_bytes"] for t in v["runs"])})
 for t in v["runs"]:checks.append({"name":r+"_"+t["name"],"status":"PASS","command":subprocess.list2cmdline(t["command"]),"exit_code":t["exit_code"],"reason":"真实原生退出码/日志SHA/耗时/进程树RSS见该run。"})
old=json.loads((root/"report/evidence/S2B-T17/route_specialization_20261011_r05/validation.json").read_text(encoding="utf-8"))
if old["trace_summaries"]!=reports[-1]["trace_summaries"]:raise RuntimeError("S3/S4全部15nonconv trace不同")
write("nonconv_trace_comparison.json",{"status":"PASS","reference":"report/evidence/S2B-T17/route_specialization_20261011_r05/validation.json","reference_sha256":sha(root/"report/evidence/S2B-T17/route_specialization_20261011_r05/validation.json"),"all_15_counts_cycles_digests_identical":True,"actual":reports[-1]["trace_summaries"]})
for name,cmd in (("static_checker",[sys.executable,"-X","utf8","verification/check_s2b_inference_platform.py"]),("diff_check",["git","diff","--check","--",*changed])):
 p=subprocess.run(cmd,capture_output=True);(evidence/(name+".log")).write_bytes(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError("便宜终检失败")
 checks.append({"name":name,"status":"PASS","command":subprocess.list2cmdline(cmd),"exit_code":p.returncode,"reason":"精确本轮文件范围，原日志保留。"})
limits=["r14包装的生成器LF/实向量CRLF比较口径失败保留；本包用实际r06/r10 raw相同及文本换行关系核验。首次collector stdout仅在原工具返回，诊断明确未伪造文件日志。","CONV对已定义二进制公开API保持原语义：原首分支已拒绝batch非1；输入元素数仅后续长度判断使用，输出元素数另在校验成功(batch均1)轨迹的OUTPUT_SCAN使用；端口变化不改变锁存，abort/reset/default分支保持。","原14rawSHA完整保全；profile0.1.4/生产18=7原2A+7派生+4outer，physical0.1.1未冻结且50MHz不变。","最终真实CONV仅完整sample000 layer0及小层/21层合法配置校验；非conv全15层真实引擎golden/trace，backend卷积仅控制stub；不声明109新闭包整网。","不重跑实际CSR/runtime计时器整core联调或实板timeout；冻结源码与每周期请求/响应/owner/abort等价支持deadline消耗不变，实板恢复另任务。","ROUTE合法通用groups>=3仍非等价、固定tiny416不可达，不扩展既有S3覆盖。","r02预算、r03端口宽度oracle、r04单点不可达夹具、r08D2换行门禁及r09宿主线程数门禁失败原件完整保留；r07功能PASS但CPU线程活动未测，最终CPU资源由r10实际getter/各thread CPU delta/OS峰限定。","r06边界runner只CPU环境/报告/前置门禁不同；精确函数/TB/向量/RTL映射复用，原证据不改写。","G2/S4综合STA/postroute/bit/G3 NOT_RUN；旧S3时序失败不改判。工具调用量未测，进程树RSS为0.1秒采样，CPU OS峰为宿主进程生命周期上界。"]
checks += [{"name":name,"status":"NOT_RUN","command":None,"exit_code":None,"reason":reason} for name,reason in (("G2独立审查","Developer停止写入，由root串行独立审查后提交。"),("S4_50MHz_STA_postroute_bit","G2及提交后再由root干净综合；未改时钟或例外。"),("109新闭包及G3","仅本次真实layer0；未下载或操作实物。"))]
checks.append({"name":"ROUTE通用合法groups>=3","status":"NOT_APPLICABLE","command":None,"exit_code":None,"reason":"保持S3明确固定ROM不可达范围；不宣称通用等价。"})
running=[{"pid":p.pid,"name":p.info["name"]} for p in psutil.process_iter(["name"]) if p.info["name"] and (p.info["name"].lower() in ("verilator_bin.exe","cc1plus.exe") or p.info["name"].startswith("Vtb_s2b_"))]
if running:raise RuntimeError("验证重型进程未退出")
freeze={"schema_version":1,"status":"PASS_S4_DEVELOPER_G1_STOP","created_utc8":datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),"task_baseline_commit":base,"current_head":head,"source_sha256":bindings,"frozen14_sha256":{p:sha(root/p) for p in checker.FROZEN_CORE_SHA256},"changed_files":changed,"original_git_sources":git_sources,"verification_runs":summary,"boundary_source_mapping":mapping,"independent_cpu":reports[1]["independent_cpu_layer0"],"source_derivation":json.loads((root/"board/s2b_inference_platform.json").read_text(encoding="utf-8"))["source_derivation"],"limitations":limits,"resource_status":{"available_ram_bytes":psutil.virtual_memory().available,"disk_free_bytes":shutil.disk_usage(work).free,"running_validation_heavy":running}}
write("source_freeze.json",freeze)
interfaces=json.loads((root/"report/evidence/S2B-T17/route_specialization_20261011_r07/delivery_manifest.json").read_text(encoding="utf-8"))["interfaces"]
for x in interfaces:
 if sha(root/x["path"])!=x["sha256"]:raise RuntimeError("正式接口原件变化")
inputs={"report/evidence/S2A-T01/tiny416_model_manifest.json","report/evidence/S2B-T17/route_specialization_20261011_r05/validation.json"}
for n in range(1,15):
 directory=root/"report/evidence/S2B-T17"/f"conv_validation_20261011_r{n:02}"
 for p in directory.rglob("*"):
  if p.is_file():inputs.add(p.relative_to(root).as_posix())
manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":run,"source_commit":head,"evidence_dir":evidence.relative_to(root).as_posix(),"interfaces":interfaces,"files":[{"path":p,"sha256":d,"role":"source"} for p,d in bindings.items()]+[{"path":p,"sha256":sha(root/p),"role":"input"} for p in sorted(inputs)]+[{"path":p.relative_to(root).as_posix(),"sha256":sha(p),"role":"log" if p.suffix==".log" else "result" if p.suffix==".json" else "artifact"} for p in evidence.iterdir() if p.is_file()],"checks":checks,"tool_versions":reports[1]["tool_versions"],"limitations":limits}
write("delivery_manifest.json",manifest)
print(json.dumps({"status":freeze["status"],"manifest_sha256":sha(evidence/"delivery_manifest.json"),"source_freeze_sha256":sha(evidence/"source_freeze.json"),"files":len(manifest["files"]),"runs":summary},ensure_ascii=False))
