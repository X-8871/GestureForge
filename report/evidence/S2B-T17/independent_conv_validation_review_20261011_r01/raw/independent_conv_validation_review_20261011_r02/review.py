"""S4独立审查：冻结绑定、独立数值复算及小型公开端口双RTL验证。"""
from __future__ import annotations
import argparse, ast, hashlib, importlib.util, json, math, os, pathlib, re, shutil, subprocess, sys, time, zlib
import psutil
os.environ.update({k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')})
R=pathlib.Path(__file__).resolve().parents[4]
W=pathlib.Path(__file__).resolve().parent
E=R/'report/evidence/S2B-T17'
BASE='6d3fd8567b579a51d4042667d47af7d94f2f5a97'
FROZEN='671f9cf494b92ce182b3f1542fefd0cfd4b209f5'
checks=[]
def sha(p):
    """原始字节SHA。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    """严格UTF8文本读取。"""
    assert p.is_file(),str(p)
    return p.read_text(encoding='utf-8')
def js(p):return json.loads(read(p))
def save(name,v):
    """所有产物仅写入已验证的隔离目录。"""
    p=W/name
    assert p.parent==W and not p.exists(),str(p)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def check(label,cond,detail=None):
    """保留可追溯断言。"""
    checks.append({'name':label,'pass':bool(cond),'detail':detail})
    if not cond:raise AssertionError(label)
def gitblob(commit,p):return subprocess.check_output(['git','show',commit+':'+p],cwd=R)
def load_module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def native(name,cmd,cwd,timeout=120,env=None):
    """采样实际进程树并限定资源；不读取或终止无关进程。"""
    log=W/(name+'.log');assert not log.exists()
    start=time.monotonic();peak=0;cache=0;reason=None
    with log.open('wb') as out:
        p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT,env=env)
        proc=psutil.Process(p.pid)
        while p.poll() is None:
            try:tree=[proc]+proc.children(recursive=True)
            except psutil.Error:tree=[]
            rss=0
            for q in tree:
                try:rss+=q.memory_info().rss
                except psutil.Error:pass
            peak=max(peak,rss)
            cache=sum(f.stat().st_size for f in (W/'obj_dir').rglob('*') if f.is_file()) if (W/'obj_dir').exists() else 0
            if rss>1610612736 or cache>314572800 or time.monotonic()-start>timeout:
                reason='资源或超时停止'
                for q in reversed(tree):
                    try:q.kill()
                    except psutil.Error:pass
                break
            time.sleep(.1)
        rc=p.wait()
    row={'command':cmd,'cwd':str(cwd),'exit_code':rc,'seconds':round(time.monotonic()-start,3),'peak_tree_rss_bytes':peak,'cache_bytes':cache,'stop_reason':reason,'log':log.name,'log_sha256':sha(log)}
    save(name+'_native.json',row)
    return row
def audit():
    """独立读取全部绑定、原始测试源码和黄金文件，不执行开发验证入口。"""
    freeze=E/'conv_validation_20261011_r15/source_freeze.json';man=E/'conv_validation_20261011_r15/delivery_manifest_r02.json'
    check('freeze入口SHA',sha(freeze)=='d8f2af3f6ac243267c12d9a8ca1b8559b0ff1e69054492b4eab50dcdee62a846')
    check('delivery入口SHA',sha(man)=='0fcec217510cccca8e79ce9ff312ccfea60f8cf5'+'20c4fcd647857cae5080ed06')
    f=js(freeze);m=js(man)
    check('37源及197产物数量',len(f['source_sha256'])==37 and len(m['files'])==197)
    for path,digest in f['source_sha256'].items():check('source:'+path,sha(R/path)==digest)
    for row in m['files']:check('delivery:'+row['path'],sha(R/row['path'])==row['sha256'])
    for path,digest in f['frozen14_sha256'].items():
        raw=(R/path).read_bytes();blob=gitblob(FROZEN,path)
        check('最终2A原件:'+path,sha(R/path)==digest and (raw==blob or raw.replace(b'\r\n',b'\n')==blob))
    committed=subprocess.check_output(['git','diff','--name-only',BASE,'HEAD','--',*f['source_sha256']],cwd=R,text=True)
    check('S3基线至HEAD无已提交业务差异',not committed.strip())
    old=read(R/'src/s2a_conv_tile_engine.sv');new=read(R/'src/s2b_conv_tile_engine.sv')
    transforms=[('module s2a_conv_tile_engine (','module s2b_conv_tile_engine ('),
        ("input_elements_wide = {96'd0, input_batch_count_latched} *\n                              {96'd0, input_channels_latched} *","input_elements_wide = {96'd0, input_channels_latched} *"),
        ("output_elements_wide = {96'd0, output_batch_count_latched} *\n                               {96'd0, output_channels_latched} *","output_elements_wide = {96'd0, output_channels_latched} *")]
    derived=old
    for a,b in transforms:check('替换唯一:'+a.splitlines()[0],derived.count(a)==1);derived=derived.replace(a,b)
    check('CONV独立固定三替换后全文相同',derived==new)
    backend=gitblob(BASE,'src/s2b_network_backend.sv').decode('utf-8').replace('\r\n','\n')
    check('backend只更换CONV引用',backend.replace('s2a_conv_tile_engine u_conv_engine','s2b_conv_tile_engine u_conv_engine')==read(R/'src/s2b_network_backend.sv'))
    # 独立确定宽度、先行拒绝和仅有的读写位置，为全二进制API归纳证明提供语法边界。
    for stem,count in (('input_elements_wide',4),('output_elements_wide',5)):
        check('宽乘积使用点:'+stem,len(re.findall(r'\b'+stem+r'\b',old))==count)
        check('128位保留:'+stem,'logic [127:0] '+stem+';' in new)
    for field in ('input_batch_count_latched','output_batch_count_latched'):
        check('batch只在reset及START赋值:'+field,len(re.findall(field+r'\s*<=',old))==2)
        check('batch前置拒绝:'+field,old.index('('+field+" != 32'd1)")<old.index('end else if ((input_elements_wide'))
    check('OUTPUT_SCAN仅有既有状态入口',old.count('state <= ST_OUTPUT_SCAN;')==2)
    check('最大4因子不溢出128',((1<<32)-1)**4<(1<<128))
    check('batch1乘法全值恒等',all(1*a*b*c==a*b*c for a in (0,1,2,2**32-1) for b in (0,1,2**32-1) for c in (0,1,2**32-1)))
    check('32位截断会错误放行的反例',65536*65536>2**32-1 and ((65536*65536)&(2**32-1))==0)
    sys.path.insert(0,str(R/'verification'))
    current=load_module('s4_current',R/'verification/test_s2b_conv_validation_rtl.py')
    prior=read(E/'conv_validation_20261011_r07/runner_source_used.py');now=read(R/'verification/test_s2b_conv_validation_rtl.py')
    prior_ast=ast.parse(prior);now_ast=ast.parse(now)
    for name in ('ports','rom','oracle','vectors','pair','boundary_tb','layer0_tb'):
        a=next(n for n in prior_ast.body if isinstance(n,ast.FunctionDef) and n.name==name)
        b=next(n for n in now_ast.body if isinstance(n,ast.FunctionDef) and n.name==name)
        check('r06保留函数全文:'+name,ast.get_source_segment(prior,a)==ast.get_source_segment(now,b))
    model=js(R/'report/evidence/S2A-T01/tiny416_model_manifest.json')
    names,vectors,small,_=current.vectors(model)
    r06=E/'conv_validation_20261011_r06';r10=E/'conv_validation_20261011_r10'
    check('r06与r10向量raw一致',(r06/'validation_vectors.txt').read_bytes()==(r10/'validation_vectors.txt').read_bytes())
    check('当前生成向量与r06逐字符一致',vectors==read(r06/'validation_vectors.txt'))
    check('当前生成边界TB与r06逐字符一致',current.boundary_tb(names,small)==read(r06/'tb_s2b_conv_validation.sv'))
    check('当前生成layer0TB与r10逐字符一致',current.layer0_tb()==read(r10/'tb_s2b_conv_layer0.sv'))
    runs=[]
    for n in (6,10,11,12,13):
        p=E/f'conv_validation_20261011_r{n:02d}/validation.json';j=js(p)
        expected_status={6:'PASS',10:'PASS',11:'PASS_GEOMETRY_SPECIALIZATION_G1',12:'PASS_ROUTE_SPECIALIZATION_DIRECT_G1',13:'PASS_BACKEND_COORDINATES_G1'}[n]
        check('验证状态'+str(n),j['status']==expected_status)
        for q in j['runs']:
            check('实际日志绑定'+str(n)+q['name'],q['exit_code']==0 and sha(R/q['log'])==q['log_sha256'])
        for path,digest in j['source_sha256_pre'].items():
            if path in f['source_sha256'] and 'test_s2b_conv_validation' not in path:
                check('实际源映射'+str(n)+path,digest==f['source_sha256'][path])
        runs.append({'run':n,'status':j['status'],'coverage':j.get('actual_coverage'),'runs':j['runs']})
    old_traces=re.findall(r'TRACE layer=(\d+) op=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) digest=([0-9a-f]+)',read(E/'route_specialization_20261011_r05/simulation.log'))
    new_traces=re.findall(r'TRACE layer=(\d+) op=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) digest=([0-9a-f]+)',read(E/'conv_validation_20261011_r13/simulation.log'))
    check('15nonconv原始trace完全相同',len(new_traces)==15 and old_traces==new_traces)
    # 每个历史失败均保留且其非零状态不由包装通过覆盖。
    failures=[]
    for n in (2,3,4,8,9):
        j=js(E/f'conv_validation_20261011_r{n:02d}/validation.json')
        check('原失败保留'+str(n),j['status']=='FAIL');failures.append({'run':n,'error':j.get('error'),'runs':j['runs']})
    tb=read(r10/'tb_s2b_conv_layer0.sv')
    check('真实全输出逐byte比较存在','expected_bytes[' in tb and 'output_seen[' in tb and 'missing_count' in tb and 'OUTPUT_BYTES' in tb)
    check('原新全部公开端口比较存在',all('candidate_'+n in tb for d,w,n in current.ports() if d=='output'))
    # 独立CPU通过27个tap的切片累加复算全张量，不调用开发CPU矩阵代码或生产MQROM。
    import numpy as np
    fixture=pathlib.Path('D:/FPGA_Competition/report/evidence/S2A-T66/tile01/fixture')
    shard=pathlib.Path('D:/FPGA_Competition/report/evidence/S2A-T25/tensors/sample_000.zlib')
    gf8=pathlib.Path('D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t02_d2_tiny416_int8_weight_r2/gesture_yolov4_tiny_416_int8_weights.gf8')
    for p,d in ((shard,'49488538ced503bad996e284a3593d4fc7a1cf3b605d90221b3ca09875c4966e'),(gf8,'f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39')):check('黄金外部原件'+str(p),p.is_file() and sha(p)==d)
    raw=zlib.decompress(shard.read_bytes());check('T25恢复全网SHA',hashlib.sha256(raw).hexdigest()=='090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80')
    image=(fixture/'sample0_input_chw_int8.bin').read_bytes();weight=(fixture/'sample0_layer0_gf8_weights.bin').read_bytes();gold=(fixture/'sample0_layer0_expected_nchw_int8.bin').read_bytes()
    for name,data in [('sample0_input_chw_int8.bin',image),('sample0_layer0_gf8_weights.bin',weight),('sample0_layer0_expected_nchw_int8.bin',gold)]:
        size,d=current.FIXED[name];check('独立夹具绑定'+name,len(data)==size and hashlib.sha256(data).hexdigest()==d)
    check('GF8权重实际切片',gf8.read_bytes()[316:1180]==weight)
    check('T25完整layer0实际切片',len(raw)==11382150 and raw[:1384448]==gold)
    start=time.monotonic();row=model['layers'][0]
    feature=np.pad(np.frombuffer(image,np.int8).astype(np.int64).reshape(3,416,416),((0,0),(1,1),(1,1)))
    kernel=np.frombuffer(weight,np.int8).astype(np.int64).reshape(32,3,3,3)
    output=[]
    for oc in range(32):
        acc=np.full((208,208),row['bias_accumulator_int32_per_output_channel'][oc],dtype=np.int64)
        for ic in range(3):
            for ky in range(3):
                for kx in range(3):acc+=feature[ic,ky:ky+416:2,kx:kx+416:2]*kernel[oc,ic,ky,kx]
        f64=acc.astype(np.float64)*(float(row['input_scale'])*float(row['weight_scale_per_output_channel'][oc]))/float(row['output_scale'])
        f64=np.where(f64<0,f64*.1,f64)
        quant=np.clip(np.copysign(np.floor(np.abs(f64)+.5),f64),-127,127).astype(np.int8)
        output.append(quant.tobytes())
    actual=b''.join(output)
    check('独立CPU全1384448byte等T25',actual==gold,{'bytes':len(actual),'mismatches':sum(a!=b for a,b in zip(actual,gold))})
    check('开发CPU实物文件等独立CPU',(r10/'cpu_layer0_expected.bin').read_bytes()==actual)
    save('independent_cpu_result.json',{'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest(),'mismatches':0,'seconds':time.monotonic()-start,'method':'逐输出通道、逐27tap的INT64切片累加；D2 binary64两步scale/除法、负值0.1、半远离零、[-127,127]；不读取生产MQROM','peak_self_bytes':getattr(psutil.Process().memory_info(),'peak_wset',None),'bindings':[{'path':str(p),'sha256':sha(p)} for p in (shard,gf8,R/'verification/s1_t02_d2_int8_forward.py',r10/'cpu_layer0_expected.bin')]})
    for mode,expected in [('evidence',0),('inputs',2)]:
        result=native('delivery_'+mode,[sys.executable,'-B','-X','utf8',str(R/'verification/check_stage_delivery.py'),'--mode',mode,'--manifest',str(man)],R)
        check('stage checker '+mode,result['exit_code']==expected)
    result=native('platform_checker',[sys.executable,'-B','-X','utf8',str(R/'verification/check_s2b_inference_platform.py')],R)
    check('平台静态核验',result['exit_code']==0)
    save('audit_result.json',{'status':'PASS','source_sha256':f['source_sha256'],'checks':checks,'verification_runs':runs,'preserved_failures':failures,'manifest_replacement_characters':read(man).count('\ufffd'),'source_freeze_sha256':sha(freeze),'delivery_sha256':sha(man),'baseline':BASE,'observed_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()})
    print('PASS_INDEPENDENT_AUDIT',len(checks))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['audit']);args=parser.parse_args()
    try:audit()
    except Exception as exc:
        save('audit_failure.json',{'status':'FAIL','exception':repr(exc),'checks':checks});raise
