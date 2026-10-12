"""S15独立功能审查，仅写当前隔离目录并保存真实原件。"""
from pathlib import Path
import sys, os, json, hashlib, subprocess, re, time, random, math
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent/'attempt_r02'
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_s15_arithmetic_rtl as s15
import test_s2b_conv_validation_rtl as validation
import test_s2b_conv_tile_origin_rtl as previous
import test_s2b_backend_coordinates_rtl as support
import psutil
BASE='0700c33e6faba8861cc2e7646a8981e424a69c45'
FORMAL=ROOT/'report/evidence/S2B-T17/s15_arithmetic_fix_20261012_r01'
SEED=0x1512B0C
def digest(path):
    """读取真实原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
    """仅创建新证据，不覆盖既有原件。"""
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def read(path):
    """严格UTF8读取原始JSON。"""
    return json.loads(path.read_text(encoding='utf-8'))
receipt=dict(schema_version=1,status='CHANGES_REQUIRED',source_commit=BASE,seed=SEED,tests=[],
 limitations=['仅S15功能G2；不是STA、PNR或G3/G4/G5。','完整layer0 RTL未重复；审计实际G1日志和绑定，独立重算CPU整层及64个标量坐标。','公开boundary使用已核读的旧RTL逐周期差分生成器，并添加独立刺激；不复用编译缓存。','ROUTE与其它几何消费者生产字节不变，审计G1实际回归原件而未重复重型ROUTE。','内存峰值为100ms进程树采样，瞬时峰及工具调用总量未测。'])
started=time.monotonic()
try:
    checker=support.load_checker();previous.exact_directory(HERE)
    assert previous.git('rev-parse','HEAD').decode().strip()==BASE
    dev=read(FORMAL/'final_receipt.json')
    assert digest(FORMAL/'final_receipt.json')=='92ed2230a768450bd750cc22ba6b21007f1e6e4bef15d7cfcee37b2abd31c72b'
    receipt['source_sha256_pre']={p:digest(checker.exact_file(ROOT/p)) for p in dev['source_sha256']}
    assert receipt['source_sha256_pre']==dev['source_sha256']
    snapshot=HERE/'source_snapshot';snapshot.mkdir()
    for p in receipt['source_sha256_pre']:
        target=snapshot/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/p).read_bytes())
    static=checker.check_static(ROOT);receipt['contract']=s15.contract(checker)
    receipt['frozen14_sha256']={p:digest(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
    assert receipt['frozen14_sha256']==checker.FROZEN_CORE_SHA256 and len(receipt['frozen14_sha256'])==14
    profile=read(ROOT/'board/s2b_inference_platform.json')
    assert profile['version']=='s2b-inference-platform/0.1.15' and profile['clock_hz']==50000000
    assert profile['vivado_part']=='xc7z020clg400-2' and profile['visibility_default']==0 and len(profile['rtl_sources'])==18
    assert 'variable version 0.1.12' in (ROOT/'vivado/s2b_inference_platform.tcl').read_text(encoding='utf-8')
    for p in profile['rtl_sources']:
        # 冻结原件已按真实SHA核对；Git文本转换另按内容检查不误当生产漂移。
        if p!=s15.ENGINE:assert previous.git('show',BASE+':'+p).decode('utf-8').replace('\r\n','\n')==(ROOT/p).read_text(encoding='utf-8'),p
    manifest=read(FORMAL/'delivery_manifest_r02.json')
    assert digest(FORMAL/'delivery_manifest_r02.json')=='d6f678d5d95869228fbc75348f4b56942ba15efaa3785b25511257bc5a4b5cc9'
    audits=[]
    for item in manifest['files']:
        path=checker.exact_file(ROOT/item['path']);assert digest(path)==item['sha256'],item['path']
        audits.append(dict(path=item['path'],sha256=item['sha256'],status='MATCH'))
    assert len(audits)==491
    save('manifest_file_hash_audit.json',audits)
    ended=[];summaries={}
    for mode,attempt in dev['final_attempts'].items():
        g1=read(FORMAL/attempt/'validation.json')
        assert g1['status']=='PASS_S15_'+mode.upper()+'_G1_ONLY'
        assert g1['source_sha256_pre']==g1['source_sha256_post']==dev['source_sha256']
        assert digest(FORMAL/attempt/'validation.json')==dev['results_sha256'][mode]
        for p,h in g1['source_sha256_pre'].items():assert digest(FORMAL/attempt/'source_snapshot'/p)==h
        for test in g1.get('tests',[]):
            for row in test['runs']:
                assert row['native_exit_code']==row['direct_wait_exit_code']==0 and row['failure'] is None
                assert row['terminal_state']=='EXITED_DIRECT_CHILD_WAIT'
                assert read(FORMAL/attempt/test['name']/(row['name']+'.native.json'))==row
                for stream in ('stdout','stderr'):assert digest(ROOT/row[stream]['path'])==row[stream]['sha256']
                if psutil.pid_exists(row['pid']):assert abs(psutil.Process(row['pid']).create_time()-row['create_time_unix'])>.01
                ended.append(dict(test=test['name'],phase=row['name'],pid=row['pid'],native_exit_code=0,log_sha256=row['stdout']['sha256']))
            summaries[test['name']]=dict(coverage=test.get('coverage'),pass_lines=test.get('pass_lines'),actual_pass_fields=test.get('actual_pass_fields'))
    assert len(ended)==14
    save('g1_child_terminal_audit.json',ended)
    layer=summaries['layer0']['coverage']
    assert layer['bytes']==layer['output_writes']==1384448 and layer['requests']==layer['responses']==2551955
    assert layer['cycles']==27235743 and layer['request_stalls']==layer['response_stalls']==6635073
    assert 'full tensor matched T25; bytes=1384448 mismatches=0' in (FORMAL/'layer0_r01/layer0/simulation.stdout.log').read_text(encoding='utf-8')
    assert summaries['feature']['coverage']['vectors']==summaries['output']['coverage']['vectors']==120361
    for name in ('route_generic','route_frozen'):
        assert summaries[name]['actual_pass_fields']['cases']==15816 and summaries[name]['actual_pass_fields']['queries']==4592720
    frozen=(FORMAL/'frozen_r01/route_frozen/tb_s2b_route_specialization.sv').read_text(encoding='utf-8')
    assert frozen.count('#(.FROZEN_ROUTE_SHAPES(1))')==4
    receipt['g1_audit']=dict(manifest_files=len(audits),direct_children_ended=len(ended),summaries=summaries,static_sources=len(static))
    receipt['checker_negatives']=s15.checker_negatives(checker,HERE,static)
    model=read(ROOT/support.MODEL);assert digest(ROOT/support.MODEL)==support.MODEL_SHA
    for name,(size,h) in validation.FIXED.items():
        p=checker.exact_file(validation.FIXTURE/name);assert p.stat().st_size==size and digest(p)==h
    cpu=HERE/'cpu_layer0';cpu.mkdir();receipt['cpu_layer0']=validation.cpu_layer0(model,cpu,checker)
    golden=(validation.FIXTURE/'sample0_layer0_expected_nchw_int8.bin').read_bytes()
    assert (cpu/'cpu_layer0_expected.bin').read_bytes()==golden
    assert (FORMAL/'layer0_r01/cpu_layer0/cpu_layer0_expected.bin').read_bytes()==golden
    inputs=(validation.FIXTURE/'sample0_input_chw_int8.bin').read_bytes();weights=(validation.FIXTURE/'sample0_layer0_gf8_weights.bin').read_bytes()
    def signed(value):
        """INT8按二补码转换。"""
        return value-256 if value>127 else value
    rng=random.Random(SEED);row=model['layers'][0];samples=[]
    coords=[(0,0,0),(31,207,207),(15,0,207),(16,207,0)]+[(rng.randrange(32),rng.randrange(208),rng.randrange(208)) for _ in range(60)]
    for c,y,x in coords:
        acc=int(row['bias_accumulator_int32_per_output_channel'][c])
        for ic in range(3):
            for ky in range(3):
                for kx in range(3):
                    iy,ix=y*2+ky-1,x*2+kx-1
                    v=signed(inputs[(ic*416+iy)*416+ix]) if 0<=iy<416 and 0<=ix<416 else 0
                    acc+=v*signed(weights[c*27+ic*9+ky*3+kx])
        value=acc*(float(row['input_scale'])*float(row['weight_scale_per_output_channel'][c]))/float(row['output_scale'])
        if value<0:value*=.1
        actual=min(127,max(-127,(1 if value>=0 else -1)*math.floor(abs(value)+.5)))
        expected=signed(golden[(c*208+y)*208+x]);assert actual==expected,(c,y,x,actual,expected)
        samples.append(dict(channel=c,y=y,x=x,accumulator=acc,expected=expected,actual=actual))
    save('independent_scalar_golden64.json',samples)
    u32=(1<<32)-1;u64=(1<<64)-1
    edge=(0,1,65535,65536,1<<31,u32)
    math_rows=[]
    for _ in range(10000):
        c,h,w,y,x,base=[rng.getrandbits(32) for _ in range(6)]
        plane=h*w;assert 0<=plane<=u64
        assert ((base+((c*h+y)*w+x))&u64)==((base+c*plane+y*w+x)&u64)
    for h in edge:
        for w in edge:math_rows.append(dict(h=h,w=w,expected_full64=h*w))
    save('independent_math_edges.json',math_rows)
    receipt['independent_math']=dict(random_vectors=10000,edge_pairs=len(math_rows),seed=SEED,unsigned64_product_exact=True,original_mod64_preserved=True)
    save('audit_pre.json',receipt)
    tool=previous.exact_directory(Path('D:/FPGA_S2A_MSYS2_20261001/env'))
    bins=previous.exact_directory(tool/'mingw64/bin');make=previous.exact_directory(tool/'usr/bin');verilator=checker.exact_file(bins/'verilator_bin.exe')
    env=dict(os.environ,PATH=str(make)+os.pathsep+str(bins)+os.pathsep+os.environ.get('PATH',''),VERILATOR_ROOT=str(tool/'mingw64/share/verilator'),PYTHONUTF8='1')
    receipt['tool_versions']=dict(python=sys.version,verilator=subprocess.check_output([str(verilator),'--version'],cwd=HERE,env=env,text=True,timeout=30).strip())
    wd=HERE/'boundary';wd.mkdir();source=wd/'source';source.mkdir()
    record=dict(name='boundary',runs=[],preflight=previous.resource(checker,wd));receipt['tests'].append(record)
    assert record['preflight']['disk_free_bytes']>=8*1024**3 and record['preflight']['available_ram_bytes']>=512*1024**2
    for p in validation.RTL:(source/Path(p).name).write_bytes((ROOT/p).read_bytes())
    names,data,small,proof=validation.vectors(model);bench=s15.boundary_bench(names,small)
    extra="""
reset_dut;defaults;
// START时owner低而VALIDATE时恢复高，继承原实时owner语义。
buffer_owner_pl=0;start_dut;buffer_owner_pl=1;tick;
if(result_valid)$fatal(1,"独立owner恢复失败");
abort=1;tick;abort=0;tick;
// 同沿reset/abort与START必须优先清零完整64位缓存。
for(integer k=0;k<8;k++)begin
 defaults;input_height=32'hffffffff;input_width=32'hffffffff;start_valid=1;
 if(k%2==0)hard_reset=1;else abort=1;
 tick;start_valid=0;hard_reset=0;abort=0;tick;
 if(!start_ready || busy || result_valid || u_candidate.input_geometry_plane!==64'd0)$fatal(1,"独立clear与START优先失败");
end
// 连续START覆盖旧H/W；之后raw变化与结果反压都不能改缓存。
for(integer k=0;k<64;k++)begin
 defaults;input_batch_count=2;input_height=32'h80000000+32'(k);input_width=32'hffffffff-32'(k);
 start_dut;input_height=1;input_width=3;tick;
 if(!result_valid || result_error_code!==1)$fatal(1,"独立参数首错优先失败");
 repeat(3)tick;result_ready=1;tick;result_ready=0;
end
reset_dut;defaults;
$display("PASS INDEPENDENT_S15_EXTRA owner_restore=1 clear_start_priority=8 consecutive_start_raw_mutation=64");
"""
    marker=' $display("PASS CONV_VALIDATION';assert bench.count(marker)==1;bench=bench.replace(marker,extra+marker)
    (wd/'validation_vectors.txt').write_text(data,encoding='utf-8',newline='\n')
    (wd/'tb_s2b_conv_validation.sv').write_text(bench,encoding='utf-8',newline='\n')
    command=[str(verilator),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1','--output-split','10000','--output-split-cfuncs','100','--top-module','tb_s2b_conv_validation','--Mdir','obj_dir','-MAKEFLAGS',"PYTHON3='\""+sys.executable+"\"'",'-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1',*['source/'+Path(p).name for p in validation.RTL],'tb_s2b_conv_validation.sv']
    previous.execute('compile',command,wd,wd,env,record,900)
    text=previous.execute('simulation',[str(checker.exact_file(wd/'obj_dir/Vtb_s2b_conv_validation.exe'))],wd,wd,env,record,180)
    assert 'PASS INDEPENDENT_S15_EXTRA' in text and 'abort_mask=000fffff reset_mask=000fffff' in text
    record['pass_lines']=re.findall(r'(?:PASS|S13_PUBLIC_TRACE).*',text);record['vector_seed']=proof['seed'];record['vectors']=proof['vectors']
    receipt['source_sha256_post']={p:digest(ROOT/p) for p in receipt['source_sha256_pre']}
    assert receipt['source_sha256_pre']==receipt['source_sha256_post']
    assert previous.git('rev-parse','HEAD').decode().strip()==BASE
    receipt['status']='PASS_G2_FUNCTIONAL_ONLY'
except Exception as error:receipt['error']=repr(error)
finally:
    receipt['elapsed_seconds']=round(time.monotonic()-started,3)
    receipt['created_at_utc8']=datetime.now(timezone(timedelta(hours=8))).isoformat()
    receipt['reviewer_source_sha256']=digest(Path(__file__))
    save('final_review_receipt.json',receipt)
    print(json.dumps(dict(status=receipt['status'],error=receipt.get('error'),seconds=receipt['elapsed_seconds'],receipt=str(HERE/'final_review_receipt.json')),ensure_ascii=True),flush=True)
sys.exit(0 if receipt['status']=='PASS_G2_FUNCTIONAL_ONLY' else 1)
