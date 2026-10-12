"""S14隔离功能审查：原件核验、干净仿真与独立手算。"""
from pathlib import Path
import sys, os, json, hashlib, subprocess, re, time, random, math, zlib
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_s14_arithmetic_rtl as s14
import test_s2b_conv_validation_rtl as validation
import test_s2b_conv_tile_origin_rtl as previous
import test_s2b_geometry_specialization_rtl as geometry
import test_s2b_route_specialization_rtl as route
import test_s2b_backend_coordinates_rtl as support
import psutil
BASE='5a674888acdedaa41127c4ea354231e10140eea5'
FORMAL=ROOT/'report/evidence/S2B-T17/s14_arithmetic_fix_20261012_r01'
SEED=0x1412B0C
def digest(path):
    """读取真实字节SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
    """仅在本次独占目录新建UTF8原件。"""
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def read(path):
    """严格UTF8读取JSON。"""
    return json.loads(path.read_text(encoding='utf-8'))
receipt={'schema_version':1,'status':'CHANGES_REQUIRED','source_commit':BASE,'seed':SEED,'tests':[],
 'limitations':['仅S14功能G2；STA、PNR、G3、G4、G5未执行或批准。','未重复完整layer0仿真；核验真实G1完整输出与停顿记录，并独立手算64个黄金坐标。','复用已读审查的bench生成器，新增独立刺激和算术手算；不复用G1编译缓存。','RSS为100ms进程树采样值，瞬时峰未测；工具调用总量未测。']}
started=time.monotonic()
try:
    checker=support.load_checker()
    assert previous.git('rev-parse','HEAD').decode().strip()==BASE
    dev=read(FORMAL/'final_receipt.json')
    assert digest(FORMAL/'final_receipt.json')=='4f392af31bb02c785ae8f966dd2f3426980e522fd9137dcf515d4cbd370d7086'
    receipt['source_sha256_pre']={p:digest(checker.exact_file(ROOT/p)) for p in dev['source_sha256']}
    assert receipt['source_sha256_pre']==dev['source_sha256']
    static=checker.check_static(ROOT)
    assert len(static)==33
    receipt['contract']=s14.contract(checker)
    profile=read(ROOT/'board/s2b_inference_platform.json')
    assert profile['vivado_part']=='xc7z020clg400-2' and profile['clock_hz']==50000000
    assert profile['visibility_default']==0 and len(profile['rtl_sources'])==18
    manifest=read(FORMAL/'delivery_manifest_r02.json')
    assert digest(FORMAL/'delivery_manifest_r02.json')=='7317c290a38aeaef6ca952090ab39c695deea6e310802aa6246cff6ebc7c3ac3'
    checks=[]
    for item in manifest['files']:
        path=checker.exact_file(ROOT/item['path'])
        assert digest(path)==item['sha256'],item['path']
        checks.append({'path':item['path'],'sha256':item['sha256'],'status':'MATCH'})
    save('manifest_file_hash_audit.json',checks)
    assert len(checks)==206
    g1=read(FORMAL/'all_r01/validation.json')
    assert g1['status']=='PASS_S14_ALL_G1_ONLY'
    assert g1['source_sha256_pre']==g1['source_sha256_post']
    for p,h in g1['source_sha256_pre'].items():
        assert digest(ROOT/p)==h
        assert digest(FORMAL/'all_r01/source_snapshot'/p)==h
    assert g1['frozen14_sha256']==checker.FROZEN_CORE_SHA256
    for p,h in checker.FROZEN_CORE_SHA256.items(): assert digest(ROOT/p)==h
    ended=[]
    for test in g1['tests']:
        for row in test['runs']:
            assert row['native_exit_code']==row['direct_wait_exit_code']==0
            assert row['terminal_state']=='EXITED_DIRECT_CHILD_WAIT' and row['failure'] is None
            assert read(FORMAL/'all_r01'/test['name']/(row['name']+'.native.json'))==row
            for stream in ('stdout','stderr'):
                assert digest(ROOT/row[stream]['path'])==row[stream]['sha256']
            if psutil.pid_exists(row['pid']):
                assert abs(psutil.Process(row['pid']).create_time()-row['create_time_unix'])>.01,'仍有G1原进程'
            ended.append({'test':test['name'],'phase':row['name'],'pid':row['pid'],'native_exit_code':0})
    assert len(ended)==14
    save('g1_child_terminal_audit.json',ended)
    layerlog=(FORMAL/'all_r01/layer0/simulation.stdout.log').read_text(encoding='utf-8')
    assert 'full tensor matched T25; bytes=1384448 mismatches=0' in layerlog
    layer=next(t for t in g1['tests'] if t['name']=='layer0')['coverage']
    assert layer['bytes']==layer['output_writes']==1384448 and layer['requests']==layer['responses']==2551955
    assert layer['request_stalls']==layer['response_stalls']==6635073
    boundarylog=(FORMAL/'all_r01/boundary/simulation.stdout.log').read_text(encoding='utf-8')
    assert boundarylog.count('S13_PUBLIC_TRACE')==2 and 'PASS S14_START_CACHE' in boundarylog
    frozen=(FORMAL/'all_r01/route_frozen/tb_s2b_route_specialization.sv').read_text(encoding='utf-8')
    assert frozen.count('#(.FROZEN_ROUTE_SHAPES(1))')==4
    assert read(FORMAL/'static_r01/validation.json')['status']=='FAIL'
    assert read(FORMAL/'packaging_failure_replay.native.json')['native_exit_code']==2
    receipt['g1_audit']={'manifest_sha256':digest(FORMAL/'delivery_manifest_r02.json'),'file_hashes':len(checks),
        'source_bindings':len(g1['source_sha256_pre']),'frozen14':14,'direct_children_ended':len(ended),
        'layer0_coverage':layer,'old_failures_preserved':True,'static_sources':len(static)}
    model=read(ROOT/support.MODEL);assert digest(ROOT/support.MODEL)==support.MODEL_SHA
    receipt['route_frozen_reachability']=route.route_math(model,(ROOT/'src/s2a_network_descriptor_pkg.sv').read_text(encoding='utf-8'))
    for name,(size,h) in validation.FIXED.items():
        p=checker.exact_file(validation.FIXTURE/name);assert p.stat().st_size==size and digest(p)==h
    input_bytes=(validation.FIXTURE/'sample0_input_chw_int8.bin').read_bytes()
    weights=(validation.FIXTURE/'sample0_layer0_gf8_weights.bin').read_bytes()
    golden=(validation.FIXTURE/'sample0_layer0_expected_nchw_int8.bin').read_bytes()
    cpu=FORMAL/'all_r01/cpu_layer0/cpu_layer0_expected.bin';assert cpu.read_bytes()==golden
    shard=checker.exact_file(Path('D:/FPGA_Competition/report/evidence/S2A-T25/tensors/sample_000.zlib'))
    assert digest(shard)=='49488538ced503bad996e284a3593d4fc7a1cf3b605d90221b3ca09875c4966e'
    restored=zlib.decompress(shard.read_bytes())
    assert hashlib.sha256(restored).hexdigest()=='090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80'
    assert restored[:len(golden)]==golden
    def signed(b):
        """将字节按二补码解释。"""
        return b-256 if b>127 else b
    rng=random.Random(SEED);row=model['layers'][0];samples=[]
    coords=[(0,0,0),(31,207,207),(15,0,207),(16,207,0)]+[(rng.randrange(32),rng.randrange(208),rng.randrange(208)) for _ in range(60)]
    for c,y,x in coords:
        acc=int(row['bias_accumulator_int32_per_output_channel'][c])
        for ic in range(3):
            for ky in range(3):
                for kx in range(3):
                    iy,ix=y*2+ky-1,x*2+kx-1
                    v=signed(input_bytes[(ic*416+iy)*416+ix]) if 0<=iy<416 and 0<=ix<416 else 0
                    acc+=v*signed(weights[c*27+ic*9+ky*3+kx])
        value=(acc*(float(row['input_scale'])*float(row['weight_scale_per_output_channel'][c])))/float(row['output_scale'])
        if value<0:value*=.1
        out=min(127,max(-127,(1 if value>=0 else -1)*math.floor(abs(value)+.5)))
        expected=signed(golden[(c*208+y)*208+x]);assert out==expected,(c,y,x,out,expected)
        samples.append({'channel':c,'y':y,'x':x,'accumulator':acc,'expected':expected,'actual':out})
    save('independent_scalar_golden64.json',samples)
    receipt['golden_audit']={'sample_count':64,'seed':SEED,'full_cpu_bytes_match':len(golden),'golden_sha256':digest(cpu),
       't25_shard_sha256':digest(shard),'restored_t25_slice_equal':True}
    math_rows=[];u32=(1<<32)-1;u64=(1<<64)-1
    for _ in range(2500):
        c,h,w,y,x,base=[rng.getrandbits(32) for _ in range(6)]
        assert c*h<=u64 and h*w<=u64
        assert ((base+((c*h+y)*w+x))&u64)==((base+c*(h*w)+y*w+x)&u64)
        assert (((c*h+y)*w+x)&u32)==((c*((h*w)&u32)+y*w+x)&u32)
    receipt['independent_math']={'random_vectors':2500,'seed':SEED,'unsigned64_cache_exact':True,'mod64_output_and_mod32_route_equivalent':True}
    save('audit_pre.json',receipt)
    tool=previous.exact_directory(Path('D:/FPGA_S2A_MSYS2_20261001/env'))
    bins=previous.exact_directory(tool/'mingw64/bin');make=previous.exact_directory(tool/'usr/bin')
    verilator=checker.exact_file(bins/'verilator_bin.exe')
    env=dict(os.environ,PATH=str(make)+os.pathsep+str(bins)+os.pathsep+os.environ.get('PATH',''),VERILATOR_ROOT=str(tool/'mingw64/share/verilator'),PYTHONUTF8='1')
    receipt['tool_versions']={'python':sys.version,'verilator':subprocess.check_output([str(verilator),'--version'],cwd=HERE,env=env,text=True,timeout=30).strip()}
    def run(name,top,rtl,bench,files,extras=None):
        """在全新目录串行编译，直接wait并保留原生退出码。"""
        wd=HERE/name;wd.mkdir();source=wd/'source';source.mkdir()
        record={'name':name,'runs':[],'preflight':previous.resource(checker,wd)};receipt['tests'].append(record)
        for p in rtl:(source/Path(p).name).write_bytes((ROOT/p).read_bytes())
        for p,text in (extras or {}).items():(source/p).write_text(text,encoding='utf-8',newline='\n')
        for p,text in files.items():(wd/p).write_text(text,encoding='utf-8',newline='\n')
        (wd/(top+'.sv')).write_text(bench,encoding='utf-8',newline='\n')
        command=[str(verilator),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1','--output-split','10000','--output-split-cfuncs','100','--top-module',top,'--Mdir','obj_dir','-MAKEFLAGS',"PYTHON3='\""+sys.executable+"\"'",'-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1',*['source/'+Path(p).name for p in rtl],*['source/'+p for p in (extras or {})],top+'.sv']
        previous.execute('compile',command,wd,wd,env,record,900)
        text=previous.execute('simulation',[str(checker.exact_file(wd/('obj_dir/V'+top+'.exe')))],wd,wd,env,record,180)
        record['pass_lines']=re.findall(r'(?:PASS|S13_PUBLIC_TRACE).*',text)
        return text
    names,data,small,proof=validation.vectors(model)
    bench=s14.boundary_bench(names,small)
    extra="""
reset_dut;defaults;
// START拍owner低，VALIDATE拍恢复高应合法；随后撤销不改变已接受校验。
buffer_owner_pl=0;start_dut;buffer_owner_pl=1;tick;
if(result_valid)$fatal(1,"独立owner恢复到VALIDATE失败");
abort=1;tick;abort=0;tick;
// reset/abort与START同沿必须优先清零，不能登记新任务。
for(integer k=0;k<8;k++)begin
 defaults;input_channels=32'hffffffff;input_height=32'hffffffff;
 output_height=32'hffffffff;output_width=32'hffffffff;
 start_valid=1;if(k%2==0)hard_reset=1;else abort=1;
 tick;start_valid=0;hard_reset=0;abort=0;tick;
 if(!start_ready || busy || result_valid)$fatal(1,"独立reset/abort START优先失败");
 if(u_candidate.input_element_plane!==0 || u_candidate.output_element_plane!==0 || u_candidate.output_geometry_plane!==0)$fatal(1,"独立clear优先失败");
end
// 连续任务无需reset，raw与上轮latched各异；第三因子改变不能污染缓存。
for(integer k=0;k<64;k++)begin
 defaults;input_batch_count=2;input_channels=32'h80000000+32'(k);input_height=32'hffffffff-32'(k);
 output_channels=32'hffffffff-32'(k);output_height=32'h80000000+32'(k);output_width=32'hffffffff;
 start_dut;input_channels=1;input_height=1;output_height=1;output_width=1;tick;
 if(!result_valid || result_error_code!==1)$fatal(1,"独立raw/latched与参数优先失败");
 repeat(3)tick;result_ready=1;tick;result_ready=0;
end
reset_dut;defaults;
$display("PASS INDEPENDENT_S14_EXTRA owner_restore=1 clear_start_priority=8 consecutive_start_raw_mutation=64");
"""
    marker=' $display("PASS CONV_VALIDATION';assert bench.count(marker)==1
    bench=bench.replace(marker,extra+marker)
    text=run('boundary','tb_s2b_conv_validation',validation.RTL,bench,{'validation_vectors.txt':data})
    assert 'PASS INDEPENDENT_S14_EXTRA' in text and 'abort_mask=000fffff reset_mask=000fffff' in text
    receipt['tests'][-1]['vector_seed']=proof['seed'];receipt['tests'][-1]['vectors']=proof['vectors']
    ports=geometry.ports(ROOT/'src/s2a_route_engine.sv');data,proof=s14.frozen_vectors(model,ports)
    extras={}
    for p,module in ((s14.QUERY,'s2b_route_query'),('src/s2b_route_engine.sv','s2b_route_engine')):
        old=previous.git('show',BASE+':'+p).decode('utf-8').replace('\r\n','\n').replace('module '+module,'module '+module+'_s13',1)
        if module=='s2b_route_engine':old=old.replace('s2b_route_query #','s2b_route_query_s13 #',1)
        extras[module+'_s13.sv']=old
    bench=s14.frozen_bench(model,ports);assert bench.count('#(.FROZEN_ROUTE_SHAPES(1))')==4
    text=run('route_frozen','tb_s2b_route_specialization',(s14.QUERY,'src/s2b_route_engine.sv'),bench,{'route_vectors.dat':data},extras)
    match=re.search(r'PASS ROUTE_SPECIALIZATION cases=(\d+) queries=(\d+) cycles=(\d+) abort=(\d+) reset=(\d+)',text)
    assert match and int(match[1])==proof['vectors'] and int(match[4])==int(match[5])==255
    receipt['tests'][-1]['actual_pass_fields']=dict(zip(('cases','queries','cycles','abort','reset'),map(int,match.groups())))
    receipt['tests'][-1]['vector_seed']=proof['seed'];receipt['tests'][-1]['explicit_frozen1_instances']=4
    receipt['source_sha256_post']={p:digest(ROOT/p) for p in receipt['source_sha256_pre']}
    assert receipt['source_sha256_pre']==receipt['source_sha256_post']
    assert previous.git('rev-parse','HEAD').decode().strip()==BASE
    receipt['status']='PASS_G2_FUNCTIONAL_ONLY'
except Exception as error:
    receipt['error']=repr(error)
finally:
    receipt['elapsed_seconds']=round(time.monotonic()-started,3)
    receipt['created_at_utc8']=datetime.now(timezone(timedelta(hours=8))).isoformat()
    receipt['reviewer_source_sha256']=digest(Path(__file__))
    save('final_review_receipt.json',receipt)
    print(json.dumps({'status':receipt['status'],'error':receipt.get('error'),'seconds':receipt['elapsed_seconds'],'receipt':str(HERE/'final_review_receipt.json')},ensure_ascii=True),flush=True)
sys.exit(0 if receipt['status']=='PASS_G2_FUNCTIONAL_ONLY' else 1)
