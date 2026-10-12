#!/usr/bin/env python3
"""S13独立功能审查：隔离数学、反例、证据与公开顺序仿真。"""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, itertools, json, os, random, shutil, subprocess, sys, time
import psutil

ROOT=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
import check_s2b_inference_platform as checker
import test_s2b_conv_validation_rtl as validation
import test_s2b_conv_tile_origin_rtl as origin
EVIDENCE=ROOT/'report/evidence/S2B-T17/s13_tile_origin_20261012_r01'
FROZEN={
 'src/s2b_conv_tile_engine.sv':'5e02dbc77b5dcab0142275ffc358af231748d05cd25137d8f9385cf23c975da1',
 'board/s2b_inference_platform.json':'b340d858a6659d05036cb584ef6ad7f44ad8f1d3ba1d46a53ef4e265e53ad056',
 'verification/check_s2b_inference_platform.py':'f94bf529529b095442a53df86574fc10df258f95e5259357ab51433b036201c3',
 'verification/test_s2b_conv_tile_origin_rtl.py':'5b61f808e17c5559de45ab30de94c41525320aabf6e757ef905584f0c1364147'}

def sha(path):
    """读取真实原字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name,value):
    """输出仅新建；已有证据不能覆盖。"""
    with (WORK/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

def run(name,command,cwd=ROOT,env=None,timeout=60):
    """记录直接子进程两原生流和退出码。"""
    start=time.monotonic();peak=0
    with (WORK/(name+'.stdout.bin')).open('xb') as out,(WORK/(name+'.stderr.bin')).open('xb') as err:
        child=subprocess.Popen(command,cwd=cwd,env=env,stdout=out,stderr=err)
        while child.poll() is None:
            try:
                members=[psutil.Process(child.pid)]+psutil.Process(child.pid).children(recursive=True)
                peak=max(peak,sum(p.memory_info().rss for p in members))
            except psutil.Error:pass
            if time.monotonic()-start>timeout or peak>1073741824:
                subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=30)
                raise RuntimeError('隔离任务超时或超过1GiB预算')
            time.sleep(.1)
        code=child.wait()
    row=dict(command=command,cwd=str(cwd),native_exit_code=code,elapsed_seconds=round(time.monotonic()-start,3),peak_tree_rss_sampled_bytes=peak,
        stdout=dict(path=str(WORK/(name+'.stdout.bin')),sha256=sha(WORK/(name+'.stdout.bin'))),stderr=dict(path=str(WORK/(name+'.stderr.bin')),sha256=sha(WORK/(name+'.stderr.bin'))))
    save(name+'.native.json',row)
    return row

def static():
    """完整模域及允许派生的独立补充反例；不以包装检查充当行为通过。"""
    assert {p:sha(ROOT/p) for p in FROZEN}==FROZEN
    bindings=checker.check_static(ROOT)
    result=dict(frozen_sha256=FROZEN,rtl_sources=18,frozen_sources=len(checker.FROZEN_CORE_SHA256),static='PASS')
    old=subprocess.check_output(['git','-c','core.longpaths=true','show','467463757158aed80d6f75afadff6a8458614a29:src/s2b_conv_tile_engine.sv'],cwd=ROOT).decode('utf-8').replace('\r\n','\n')
    expected=old
    for before,after in checker.S13_TILE_ORIGIN_REPLACEMENTS:
        assert expected.count(before)==1;expected=expected.replace(before,after)
    assert len(checker.S13_TILE_ORIGIN_REPLACEMENTS)==6 and expected==(ROOT/'src/s2b_conv_tile_engine.sv').read_text(encoding='utf-8')
    result['exact_delta']='仅固定六项新增；原状态转移与公开端口相等'
    # 独立signed解释覆盖bit63、上界乘积、负padding及回绕。
    def signed(v):return v-(1<<64) if v&(1<<63) else v
    mask=(1<<64)-1;seed=0x2B131012;rng=random.Random(seed)
    edges=(0,1,2,7,8,65535,65536,0x7fffffff,0x80000000,0xfffffffe,0xffffffff)
    rows=itertools.chain(itertools.product(edges,repeat=4),(tuple(rng.getrandbits(32) for _ in range(4)) for _ in range(100000)))
    count=0;negative=0;wrapped=0
    for tile,stride,scan,pad in rows:
        a=signed((tile*stride+scan-pad)&mask);b=signed(((tile*stride-pad)&mask)+scan&mask)
        assert a==b;negative+=a<0;wrapped+=tile*stride+scan-pad>mask;count+=1
    result['algebra']=dict(seed=seed,vectors=count,negative=negative,above_u64=wrapped,
        manual=[{'tile':0,'stride':0xffffffff,'scan':0,'pad':1,'signed':-1},
          {'tile':0xffffffff,'stride':0xffffffff,'scan':0xffffffff,'pad':0,'signed':-4294967296},
          {'tile':0x80000000,'stride':0xffffffff,'scan':0,'pad':0,'signed':9223372034707292160}])
    fixture=WORK/'checker_fixture';fixture.mkdir()
    for path in bindings:
        target=fixture/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/path).read_bytes())
    original=json.loads((ROOT/'board/s2b_inference_platform.json').read_text(encoding='utf-8'))
    engine=fixture/'src/s2b_conv_tile_engine.sv';profile=fixture/'board/s2b_inference_platform.json'
    mutations=[
      ('origin窄化','logic signed [63:0] tile_origin_y;','logic signed [31:0] tile_origin_y;'),
      ('SCAN加1','tile_origin_y + $signed({32\'d0, feature_scan_y})','tile_origin_y + $signed({32\'d0, feature_scan_y}) + 64\'sd1'),
      ('PRE乘积窄化','$signed({32\'d0, tile_start_x} * {32\'d0, stride_x_latched}) -','$signed(tile_start_x * stride_x_latched) -'),
      ('abort保留原点','        end else if (abort) begin\n            state <= ST_IDLE;\n            tile_origin_y <= 64\'sd0;','        end else if (abort) begin\n            state <= ST_IDLE;'),
      ('原点登记延迟','                ST_TILE_PREP: begin\n','                ST_FEATURE_REQUEST: begin\n')]
    rejected=[]
    for name,before,after in mutations:
        raw=(ROOT/'src/s2b_conv_tile_engine.sv').read_text(encoding='utf-8');assert raw.count(before)==1
        engine.write_text(raw.replace(before,after),encoding='utf-8',newline='\n')
        obj=copy.deepcopy(original)
        for item in obj['source_derivation']['derived_sources']:
            if item['path']=='src/s2b_conv_tile_engine.sv':
                item['sha256']=sha(engine);item['replacements'].append([before,after])
        profile.write_text(json.dumps(obj,ensure_ascii=False),encoding='utf-8')
        try:checker.check_static(fixture)
        except (ValueError,KeyError,TypeError,OSError) as error:rejected.append(dict(name=name,status='REJECTED',reason=str(error)))
        else:raise AssertionError('未拒绝自报规则反例'+name)
    engine.write_bytes((ROOT/'src/s2b_conv_tile_engine.sv').read_bytes());profile.write_bytes((ROOT/'board/s2b_inference_platform.json').read_bytes())
    result['counterexamples']=rejected
    for mode,want in [('evidence',0),('inputs',2)]:
        receipt=run('delivery_'+mode,[sys.executable,'-X','utf8','-B',str(ROOT/'verification/check_stage_delivery.py'),'--mode',mode,'--manifest',str(EVIDENCE/'delivery_manifest.json')]);assert receipt['native_exit_code']==want
    records={}
    for attempt in ('all_r01','all_r02','all_r03','layer0_r01'):
        obj=json.loads((EVIDENCE/attempt/'validation.json').read_text(encoding='utf-8'))
        bound=obj['source_sha256_pre']
        assert all(sha(EVIDENCE/attempt/'source_snapshot'/p)==digest for p,digest in bound.items())
        assert bound['src/s2b_conv_tile_engine.sv']==FROZEN['src/s2b_conv_tile_engine.sv']
        records[attempt]=dict(status=obj['status'],error=obj.get('error'),engine_sha256=bound['src/s2b_conv_tile_engine.sv'],runner_sha256=bound['verification/test_s2b_conv_tile_origin_rtl.py'],tests=[])
        for test in obj.get('tests',[]):
            item=dict(name=test['name'],coverage=test.get('coverage'),codes=[])
            for action in test['runs']:
                for stream in ('stdout','stderr'):
                    assert sha(ROOT/action[stream]['path'])==action[stream]['sha256']
                item['codes'].append(action['native_exit_code'])
            records[attempt]['tests'].append(item)
    a=json.loads((EVIDENCE/'all_r03/validation.json').read_text(encoding='utf-8'));b=json.loads((EVIDENCE/'layer0_r01/validation.json').read_text(encoding='utf-8'))
    ap=dict(a['source_sha256_pre']);bp=dict(b['source_sha256_pre']);ap.pop(origin.RUNNER);bp.pop(origin.RUNNER)
    assert ap==bp and b['source_sha256_pre']==b['source_sha256_post'] and 'source_sha256_post' not in a
    old_runner=(EVIDENCE/'all_r03/source_snapshot'/origin.RUNNER).read_text(encoding='utf-8')
    change_before='            bench=validation.layer0_tb().replace("endmodule",origin_monitor()+"\\nendmodule")\n'
    change_after='            # PRE登记不变量由boundary真实顺序域单独核验；这里保持冻结完整数值bench。\n            bench=validation.layer0_tb()\n'
    assert old_runner.count(change_before)==1 and old_runner.replace(change_before,change_after)==(ROOT/origin.RUNNER).read_text(encoding='utf-8')
    model=json.loads((ROOT/origin.support.MODEL).read_text(encoding='utf-8'))
    names,vectors,small,proof=validation.vectors(model)
    assert origin.boundary_bench(names,small)==(EVIDENCE/'all_r03/boundary/tb_s2b_conv_validation.sv').read_text(encoding='utf-8')
    assert validation.layer0_tb()==(EVIDENCE/'layer0_r01/layer0/tb_s2b_conv_layer0.sv').read_text(encoding='utf-8')
    result['attempts']=records
    result['cross_attempt_final_sources']='all_r03及layer0_r01除runner完全相同；runner唯一差异移除layer0附加monitor，boundary与layer0最终生成bench逐字节一致；all_r03没有post，不能伪称有'
    result['head']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    save('static_receipt.json',result);print(json.dumps(result,ensure_ascii=False))

def rtl():
    """另种子、非对称padding和变换顺序，不写生产源。"""
    heavy=[]
    for p in psutil.process_iter(['name']):
        n=p.info['name'] or ''
        if n.lower() in ('vivado.exe','verilator_bin.exe','cc1plus.exe') or n.startswith('Vtb_'):heavy.append(dict(pid=p.pid,name=n))
    assert not heavy,str(heavy)
    assert psutil.virtual_memory().available>2147483648
    wd=WORK/'rtl';wd.mkdir();source=wd/'source';source.mkdir()
    for path in validation.RTL:(source/Path(path).name).write_bytes((ROOT/path).read_bytes())
    model=json.loads((ROOT/origin.support.MODEL).read_text(encoding='utf-8'))
    names,vectors,small,proof=validation.vectors(model)
    # 这里重跑既有全部门禁、20状态、24响应；新增32个实际公开完整任务。
    (wd/'validation_vectors.txt').write_text(vectors,encoding='utf-8',newline='\n')
    text=validation.boundary_tb(names,small)
    seed=0x1310A25;rng=random.Random(seed);cases=[];jobs=[]
    mq,mb,ops=(validation.rom(name) for name in ('S2A_T23_MQ_CHANNEL_COUNT','S2A_T23_MQ_BASE','S2A_OP'))
    for j in range(32):
        sy,sx=rng.randint(1,3),rng.randint(1,3);top,bottom,left,right=(rng.randint(0,2) for _ in range(4))
        oh,ow=rng.randint(8,12),rng.randint(8,12)
        ih=(oh-1)*sy+1-top-bottom;iw=(ow-1)*sx+1-left-right
        v=dict(small,input_channels=1,input_height=ih,input_width=iw,input_length_bytes=ih*iw,output_channels=32,
            output_height=oh,output_width=ow,output_length_bytes=32*oh*ow,kernel_height=1,kernel_width=1,
            stride_y=sy,stride_x=sx,pad_top=top,pad_bottom=bottom,pad_left=left,pad_right=right,quantized_weight_bytes=32)
        assert validation.oracle(v,mq,mb,ops)==0
        assignment=' '.join(f'{name}=32\'h{v[name]&0xffffffff:x};' for name in names)+' buffer_owner_pl=1;'
        jobs.append(f'''defaults;requests=0;error_code=0;error_request=0;pending=0;backend_rsp_valid=0;
 {assignment}
 start_dut;timeout_count=0;
 while(!result_valid && timeout_count<120000)begin service;timeout_count++;end
 if(!result_valid || result_error_code!=0)$fatal(1,"独立origin公开任务失败case={j}");
 $display("INDEPENDENT_JOB case={j} requests=%0d cycles=%0d",requests,timeout_count);
 result_ready=1;service;result_ready=0;''')
        cases.append(v)
    addition='raw_invalid=0;result_ready=1;service;result_ready=0;\n'+ '\n'.join(jobs)+'\n $display("PASS INDEPENDENT_ORIGIN jobs=32 preps=%0d xtiles=%0d ytiles=%0d clears=%0d",origin_preps,origin_x_tiles,origin_y_tiles,origin_clears);\n'
    marker=' $display("PASS CONV_VALIDATION';assert text.count(marker)==1
    text=text.replace(marker,addition+marker).replace('endmodule',origin.origin_monitor()+'\nendmodule')
    # 改变服务顺序和背压周期，保持单次请求配对语义。
    text=text.replace('(cycles%5)!=0','(cycles%7)!=1 && (cycles%7)!=4').replace('delay_count=cycles%4','delay_count=(cycles*3+1)%5')
    (wd/'tb_s2b_conv_validation.sv').write_text(text,encoding='utf-8',newline='\n')
    save('independent_cases.json',dict(seed=seed,cases=cases,oracle='H=(OH-1)*SY+KH-PT-PB；W=(OW-1)*SX+KW-PL-PR；冻结MQ=32'))
    tools=Path('D:/FPGA_S2A_MSYS2_20261001/env/mingw64/bin');make=Path('D:/FPGA_S2A_MSYS2_20261001/env/usr/bin')
    assert tools.is_dir() and make.is_dir()
    env=dict(os.environ,PATH=str(make)+os.pathsep+str(tools)+os.pathsep+os.environ.get('PATH',''),VERILATOR_ROOT='D:/FPGA_S2A_MSYS2_20261001/env/mingw64/share/verilator')
    command=[str(tools/'verilator_bin.exe'),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1','--output-split','10000','--output-split-cfuncs','100','--top-module','tb_s2b_conv_validation','--Mdir','obj_dir','-MAKEFLAGS','PYTHON3=\'"'+sys.executable+'"\'','-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1',*[f'source/{Path(p).name}' for p in validation.RTL],'tb_s2b_conv_validation.sv']
    c=run('independent_compile',command,wd,env,900);assert c['native_exit_code']==0
    s=run('independent_simulation',[str(wd/'obj_dir/Vtb_s2b_conv_validation.exe')],wd,env,180);assert s['native_exit_code']==0
    log=(WORK/'independent_simulation.stdout.bin').read_text(encoding='utf-8');assert 'PASS INDEPENDENT_ORIGIN jobs=32' in log and 'abort_mask=000fffff reset_mask=000fffff response_cases=24 raw80=1' in log
    assert {p:sha(ROOT/p) for p in FROZEN}==FROZEN
    save('rtl_receipt.json',dict(status='PASS',seed=seed,bench_sha256=sha(wd/'tb_s2b_conv_validation.sv'),vector_sha256=sha(wd/'validation_vectors.txt'),compile=c,simulation=s,stdout=log,frozen_sha256=FROZEN))
    print(log)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['static','rtl']);parser.add_argument('--attempt');args=parser.parse_args()
    if args.attempt:
        assert args.attempt=='r02';WORK=WORK/(args.mode+'_'+args.attempt);WORK.mkdir()
    static() if args.mode=='static' else rtl()
