"""补核实际执行镜像与编译闭包，然后封存独立审查原件。"""
from pathlib import Path
import json,hashlib,subprocess,sys,time,re
ROOT=Path.cwd();WORK=Path(__file__).resolve().parent;BASE=ROOT/'report/evidence/S2B-T17/conv_output_address_20261011_r03'
CACHE=ROOT/'tmp/2B/S2B-T17/s9_conv_g1_20261011_r01'; ATTEMPT=WORK/'attempt_r02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def norm(p):return p.read_text(encoding='utf-8')
started=time.monotonic();extras=[];closure=[];raw_inputs=set()
for stage in ['direct_r03','boundary','layer0','backend','geometry']:
    adapter=BASE/'execution_raw'/f'{stage}_adapter.json';a=load(adapter);runtime=BASE/'execution_raw'/f'{stage}_runtime.py';native=BASE/'execution_raw'/f'{stage}_native.json';n=load(native)
    original=ROOT/a['source'];value=original.read_bytes().decode('utf-8');assert sha(original)==a['source_sha256']
    for change in a['unique_substitutions']:
        assert value.count(change['before'])==1
        assert change['after']==change['before'].replace('tmp/2B/S2B-T17','tmp/2B/S2B-T17/s9_conv_g1_20261011_r01')
        value=value.replace(change['before'],change['after'])
    assert runtime.read_bytes()==value.encode('utf-8') and sha(runtime)==a['transformed_sha256']
    assert n['native_exit_code']==0 and n['command'] and n['host_shell_exit_code'] is None
    run=load(ROOT/'report/evidence/S2B-T17'/a['run_id']/'validation.json');cmd=run['runs'][0]['command'];current=CACHE/a['run_id'];assert current.is_dir()
    files=[p for p in cmd if p.endswith('.sv')]
    for relative in files:
        actual=current/relative;assert actual.is_file(),actual
        if relative.startswith('source/'):
            upstream=ROOT/'src'/actual.name
            if actual.name=='s8_conv_tile_engine_original.sv':
                expected=subprocess.check_output(['git','show','5ea54b441bd885e10eac4794cbad5ad48c510a49:src/s2b_conv_tile_engine.sv']).decode('utf-8').replace('\r\n','\n').replace('module s2b_conv_tile_engine (','module s2b_conv_tile_engine_original (')
                assert norm(actual)==expected
            else: assert actual.read_bytes()==upstream.read_bytes(),relative
        else:assert actual.read_bytes()==(ROOT/'report/evidence/S2B-T17'/a['run_id']/actual.name).read_bytes()
        closure.append({'stage':stage,'path':actual.relative_to(ROOT).as_posix(),'sha256':sha(actual)})
        raw_inputs.add(actual)
    extras.append({'stage':stage,'adapter_sha256':sha(adapter),'runtime_sha256':sha(runtime),'native_command':n['command'],'native_exit_code':n['native_exit_code']})
    raw_inputs.update([adapter,runtime,native])
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='5ea54b441bd885e10eac4794cbad5ad48c510a49'
freeze=load(BASE/'source_freeze.json')
for row in freeze['source_files']:assert sha(ROOT/row['path'])==row['sha256'];raw_inputs.add(ROOT/row['path'])
supplement={'status':'PASS','adapters':extras,'actual_compile_closure':closure,'elapsed_seconds':round(time.monotonic()-started,3)}
(WORK/'closure_validation.json').write_text(json.dumps(supplement,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=load(ATTEMPT/'validation.json');assert r['status']=='PASS_S9_FUNCTIONAL_G2_ONLY'
review_command=subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/'review.py')]);seal_command=subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/'seal.py')])
receipt={'schema_version':1,'task_id':'S2B-T17-S9-G2','decision':'PASS','reviewer_stop':True,'scope':'S9候选组合地址优化功能G2；不批准STA/实现/上板/G3–G5。','source_commit':'5ea54b441bd885e10eac4794cbad5ad48c510a49','profile':'s2b-inference-platform/0.1.9','reviewed_manifest_sha256':sha(BASE/'delivery_manifest_r02.json'),'source_freeze_sha256':sha(BASE/'source_freeze.json'),'source_diff_sha256':sha(BASE/'source_diff.patch'),'modified_source_sha256':freeze['modified_files'],'source_sha256':r['source_sha256'],'ff_sha256':r['ff_sha256'],'findings':[],
 'math_proof':'C/Y/X保持32位赋值截断；64位无符号环中乘法对加法分配，故((C*H+Y)*W+X)模2^64等于C*(H*W)+Y*W+X模2^64。H*W精确64，base仍原64位加法，未消费分支及原范围判据不改。',
 'independent_validation':r['independent_math'],'public_start':{'vectors':5996,'cycles':100697,'abort_mask':'000fffff','reset_mask':'000fffff','response_cases':24,'raw80':1},'g1_counts_reviewed':r['g1_evidence_counts'],'mutants':r['mutants'],'negative_checks':r['negative_checks'],
 'commands':[{'name':'review_r01_failed','command':review_command,'native_exit_code':1,'seconds':None,'reason':'原日志CRLF与JSON诊断LF文本比较失败；原脚本/报告未覆盖。'},{'name':'review_r02','command':review_command,'native_exit_code':0,'seconds':r['elapsed_seconds']},{'name':'actual_closure_and_seal','command':seal_command,'native_exit_code':0,'seconds':supplement['elapsed_seconds']}]+r['runs'],
 'resource':{'peak_child_process_tree_rss_bytes':max(x['peak_tree_rss_bytes'] for x in r['runs']),'observed_attempt_directory_bytes':max(x['observed_review_directory_bytes'] for x in r['runs']),'rss_sampling_seconds':0.1,'disk_sampling_seconds':3,'rss_limit_bytes':1610612736,'review_budget_bytes':1073741824,'jobs':1,'threads':1,'scope':'采样子进程树峰，不含Python审查宿主；磁盘采样attempt_r02，外层旧失败原件另保留。'},
 'diagnostic_scope':{'direct':'只限恒0时钟、FF未执行、13寄存器×旧新两个实例的26 MULTIDRIVEN；逐条信号、代码和原日志核对，CRLF→LF仅用于字符串比较。','backend':'16条继承S8同一TB，警告header原文相等；PUBLIC_ENTRY/38层trace释放注入。','public':'公共boundary/layer0/geometry没有MULTIDRIVEN/LATCH/UNOPTFLAT；本次公共重建同样无这三类诊断。','production_zero_warning_claim':False},
 'limitations':['既有长layer0/非CONV/38层控制与geometry按冻结源码、实际原生日志及镜像审阅；本次未重复整网或长层仿真。','direct组合受控赋值包含公开START不可达值，只有组合锥/原边界判据对照含义；公共START单独实际重建。','inputs真实native2，物理接口未冻结、旧失败记录及未执行STA/板上项阻断依赖；不改判为通过。','S8真实STA失败仍存在，不能由候选功能G2推定50MHz闭合或继承109/1000板上验收。','未修改生产/正式证据/STATE/Git，子代理不提交；实际模型参数由总控配置，本receipt不伪造UI配置证明。']}
(WORK/'final_review_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# 只绑定直接审查输入及自有输出；旧清单负责其证据树闭包，不重复列旧源码快照。
direct=load(ATTEMPT/'direct_inputs.json')
for relative in direct:
    p=ROOT/relative
    if p.suffix in ['.log','.json','.patch'] and 'source_snapshot' not in relative and 'final_source_snapshot' not in relative:raw_inputs.add(p)
for name in ['delivery_manifest_r02.json','source_freeze.json','g1_summary.json','source_diff.patch']:raw_inputs.add(BASE/name)
items={p:{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'input'} for p in raw_inputs}
for p in WORK.rglob('*'):
    if not p.is_file() or p.name=='raw_manifest.jsonl' or any(part in ['build_direct','build_public','checker_fixture','offset_mutants'] for part in p.relative_to(WORK).parts):continue
    assert p.suffix.lower() not in ['.exe','.o','.dcp','.bit','.gch']
    role='log' if p.suffix=='.log' else 'source' if p.suffix in ['.py','.sv'] else 'input' if p.name.endswith('vectors.txt') else 'result'
    items[p]={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':role}
rows=sorted(items.values(),key=lambda x:x['path']);assert all(set(x)=={'path','sha256','role'} and x['role'] in ['source','input','result','log','diagnostic','artifact'] for x in rows)
(WORK/'raw_manifest.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
print(json.dumps({'status':'PASS','reviewer_stop':True,'receipt_sha256':sha(WORK/'final_review_receipt.json'),'raw_manifest_sha256':sha(WORK/'raw_manifest.jsonl'),'bindings':len(rows),'closure_files':len(closure),'seconds':supplement['elapsed_seconds']},ensure_ascii=False))
