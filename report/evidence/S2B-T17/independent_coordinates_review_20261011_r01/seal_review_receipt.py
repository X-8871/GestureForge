"""封存独立G2审查范围、实测计数与失败原件，不授予STA或硬件验收。"""
from pathlib import Path
import hashlib,json,subprocess,re,time,sys
sys.stdout.reconfigure(encoding='utf-8')
W=Path(__file__).resolve().parent;R=W.parents[3]
def sha(p):
    """返回原始SHA。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    """读取UTF8记录。"""
    return json.loads(p.read_text(encoding='utf-8'))
fixed={'src/s2b_network_backend.sv':'32cf883d40abe94a0bb2287586eb52dff1c305a48da21d3762db775679b0422a',
'board/s2b_inference_platform.json':'ad93a6e9947f7f0a5962eada74e6456bd71de9699925188c032b48466ff71228',
'board/s2b_inference_platform.md':'6c5c4221deb3729e8afc20b0f839a58c277da7d1f94f6c9a8bd1d4f7be44b74c',
'vivado/s2b_inference_platform.tcl':'bef430284805a7a760784835ed47cadae86ffc54ab75abe48014b45df5aead4a',
'verification/check_s2b_inference_platform.py':'1f8d4d4d099f32713ceec04ad4661e110b331394761f83f6efe02d1098f39901',
'verification/test_s2b_backend_coordinates_rtl.py':'db26414348ea08b0f142b9e0322d2de84b4ce0dfabaa5058eb5ef51a982f4f9b'}
for p,h in fixed.items(): assert sha(R/p)==h
rtl=read(W/'rtl_receipt_r04.json');audit=read(W/'delivery_audit.json');native=read(W/'checker_native_receipt.json')
assert rtl['status']=='PASS_INDEPENDENT_RTL_EXPERIMENT' and audit['status']=='PASS_DELIVERY_BINDINGS'
assert len(rtl['checker_negatives'])==15 and all(row['status']=='REJECTED' for row in rtl['checker_negatives'])
assert [x['native_exit_code'] for x in native]==[0,0,2]
old=(W/'s1_backend_raw.sv').read_text(encoding='utf-8');new=(R/'src/s2b_network_backend.sv').read_text(encoding='utf-8')
assert len(re.findall(r'output_element_index\s*<=',old))==6 and len(re.findall(r'output_element_index\s*<=',new))==6
dev=read(R/'report/evidence/S2B-T17/coordinates_20261011_r04/validation.json')
assert len(rtl['trace_summaries'])==15 and all(a[:4]==b[:4] and a[5]!=b[5] for a,b in zip(rtl['trace_summaries'],dev['trace_summaries']))
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
diff=subprocess.check_output(['git','diff','--name-only','1f2f9b964135ae6b92ccf557fd3f1de9639c3f46',head,'--',*rtl['source_sha256_pre']],cwd=R,text=True)
assert not diff.strip()
cache_bytes=sum(p.stat().st_size for p in W.rglob('*') if p.is_file())
evidence=[p for p in W.rglob('*') if p.is_file() and 'obj_dir' not in p.relative_to(W).parts and 'checker_fixture' not in p.relative_to(W).parts]
assert cache_bytes<314572800 and sum(p.stat().st_size for p in evidence)<104857600
receipt={'status':'PASS','role':'INDEPENDENT_REVIEWER','task':'S2B-T17-S2 G2 源码审查','review_baseline_commit':'1f2f9b964135ae6b92ccf557fd3f1de9639c3f46',
 'actual_head_after_independent_T19_commit':head,'source_closure_committed_diff_since_review_baseline':[],
 's1_comparison_commit':'6d00ff2d05e92fa6cff05243fb620f8a0232b9f1','original_backend_raw_sha256':sha(W/'s1_backend_raw.sv'),
 'reviewed_six_raw_sha256':fixed,'frozen14':audit['frozen14'],'profile':'s2b-inference-platform/0.1.2','policy':'s2b-constant-geometry-and-coordinates/1.0.0',
 'physical_interface':'s2b-physical-candidate/0.1.1 未冻结','clock_hz':50000000,
 'findings':[],
 'source_findings':['原32bit index与64bit count不变；冻结38层N=1、C<=512、H/W<=208；9/8/8位足以表示全部合法坐标。',
 '在原五个index清零分支同沿清零，在唯一非conv成功且index+1<count沿按X/Y/C进位；末元素原count门禁排除C溢出。',
 'WAIT selected_result_valid成功沿保留owner=0时推进；错误优先、未知state、descriptor错误、alias、abort/reset/start门禁和请求响应状态保持。',
 '实际派生源与最终冻结14源及独立固定字符替换完全一致，检查器拒绝自报SHA额外差异、旧版本/policy、宽度/carry漂移及新增owner门禁。'],
 'oracle_audit':{'source_manifest':'report/evidence/S2A-T01/tiny416_model_manifest.json','sha256':rtl['model_sha256'],
 'basis':'独立manifest给出shape、tensor_address、输入引用、route通道范围与scale；golden不读取query候选输出，独立求地址/字节lane、pool四tap、route Q31舍入饱和及upsample除2。实际所有请求检查读写、地址、wdata、rstrb、wstrb。',
 'independence_limit':'复用已逐行审阅的Developer TB生成器；审查自身逐索引计数证明和15项反例实际重跑，并独立改变地址数据模式与mem/owner周期。',
 'stimulus_changes':rtl['independent_stimulus_changes'],'all_15_trace_digests_differ_from_developer':True},
 'independent_coordinate_checks':rtl['independent_coordinate_proof']['checks'],'independent_simulation_counts':rtl['simulation_counts'],
 'checker_negative_count':15,'delivery_binding_checks':len(audit['checks']),'manifest_file_binding_count':77,
 'commands':{'rtl':rtl['runs'],'checkers':native,
 'audit_delivery':{'command':[sys.executable,'-B',str(W/'audit_delivery.py')],'native_exit_code':0,'seconds':audit['seconds'],'peak_memory':'NOT_MEASURED'},
 'independent_recovery_program':{'command':[sys.executable,'-B',str(W/'recover_rtl_r04.py')],'native_exit_code':0,'seconds':rtl['recovery_seconds']}},
 'failed_attempts':[{'receipt':'rtl_receipt.json','native_program_exit_code':1,'reason':'预检模糊子串误分类MCP server，未编译'},
 {'receipt':'rtl_receipt_r02.json','native_program_exit_code':1,'reason':'现有Vivado会话待确认，未编译'},
 {'receipt':'rtl_receipt_r03.json','native_program_exit_code':1,'compile_native_exit_code':1,'reason':'共用cache/evidence目录造成100MiB证据预算误分类；中止编译，原件保留'}],
 'resource_metrics':{'successful_compile_peak_tree_rss_bytes':rtl['runs'][0]['peak_tree_rss_bytes'],'simulation_peak_tree_rss_bytes':rtl['runs'][1]['peak_tree_rss_bytes'],
 'cache_bytes_at_seal_including_all_preserved_attempts':cache_bytes,'evidence_bytes_at_seal_excluding_cache_and_fixture':sum(p.stat().st_size for p in evidence),
 'whole_machine_peak':'NOT_MEASURED','whole_review_tree_peak':'NOT_MEASURED','whole_review_walltime':'NOT_MEASURED','peak_metric':'0.1秒采样本次编译/仿真子进程树RSS求和最大值'},
 'limits':rtl['limitations']+['Verilator二态实验不是形式证明；边界寄存器初态满足坐标关系，内部注入只用于边界分支。',
 '既有S1直接异常证据仅按真实source不变复用pool/upsample；route原源码字节不变不冒充直接参数拒绝覆盖。',
 '新综合/STA、实现/bit、完整实际CONV数值/109整网、runtime兼容性和G3均NOT_RUN；不批准缓存可见性启用、G4或G5。'],
 'not_run':['STA','implementation','bitstream','full_convolution_numerics','full_109_network_golden','hardware_G3','runtime_compatibility'],
 'files':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(evidence)]}
assert not (W/'receipt.json').exists()
(W/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','receipt_sha256':sha(W/'receipt.json'),'rtl_runs':rtl['runs'],'counts':rtl['simulation_counts'],'cache_bytes':cache_bytes,'evidence_bytes':sum(p.stat().st_size for p in evidence)},ensure_ascii=False))
