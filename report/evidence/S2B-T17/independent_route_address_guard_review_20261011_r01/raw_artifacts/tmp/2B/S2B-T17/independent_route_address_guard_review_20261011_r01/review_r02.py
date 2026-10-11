#!/usr/bin/env python3
"""独立复核S7固定源码、无限精度数学和额外公开口逐周期验证。"""
import collections
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone, timedelta
import psutil

W = Path(__file__).resolve().parent
R = W.parents[3]
BASE = 'f53e067ba91abc02ed60cf7f9063884d9ddb79f1'
SEED = 0x7A110C61
U = 2**32-1
FORMAL = R/'report/evidence/S2B-T17/route_address_guard_20261011_r04'
RESULT = {'status':'CHANGES_REQUIRED','reviewed_source_commit':BASE,
          'reviewed_manifest_sha256':'fe96ff60ecf84bdc7f592c1cbd9a30374105b2f9a6efa51a9d982482c252f0ad',
          'runs':[], 'seed':SEED, 'scope':'S7 ROUTE地址守卫数学、固定源码、独立公开口RTL和G1证据；不授予STA/G3/G4/G5',
          'started_at':datetime.now(timezone(timedelta(hours=8))).isoformat()}

def digest(p):
    """计算精确文件原字节。"""
    assert p.is_file() and not p.is_symlink(), str(p)
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def save(name, value):
    p=W/name
    assert not p.exists(), str(p)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def native(name, command, cwd=R, env=None, expect=0, timeout=600):
    """记录真实returncode及采样进程树RSS；失败原件保留。"""
    log=W/(name+'.log'); assert not log.exists()
    began=time.monotonic(); peak=0; samples=0
    with log.open('xb') as stream:
        p=subprocess.Popen(command,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
        while p.poll() is None:
            try:
                members=[psutil.Process(p.pid)]+psutil.Process(p.pid).children(recursive=True)
                rss=sum(x.memory_info().rss for x in members if x.is_running())
                peak=max(peak,rss); samples+=1
            except psutil.Error:
                pass
            if time.monotonic()-began>timeout or peak>1610612736:
                subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],stdout=stream,stderr=subprocess.STDOUT)
                p.wait(timeout=30)
                raise RuntimeError('独立运行触发时限或RSS停止条件')
            time.sleep(.05)
    rec={'name':name,'command':command,'native_exit_code':int(p.returncode),
         'seconds':round(time.monotonic()-began,3),'peak_tree_rss_bytes':peak if samples else None,
         'rss_sampling_interval_seconds':.05,'rss_samples':samples,'log':log.relative_to(R).as_posix(),'log_sha256':digest(log)}
    RESULT['runs'].append(rec); save(name+'_capture.json',rec)
    assert p.returncode==expect, rec
    return log.read_text(encoding='utf-8')

def git(*args):
    return subprocess.check_output(['git','-c','core.longpaths=true',*args],cwd=R)

def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def reference_audit(checker):
    """自行重算全部闭包，核对头部及唯一时序差异。"""
    manifest=read(FORMAL/'delivery_manifest_r03.json'); freeze=read(FORMAL/'source_freeze.json')
    assert digest(FORMAL/'delivery_manifest_r03.json')==RESULT['reviewed_manifest_sha256']
    assert digest(FORMAL/'source_freeze.json')=='a4cc9d6696bc73545c231cf236b5f82d0845423196acacd44c66851904124df7'
    assert digest(FORMAL/'source_diff.patch')=='01bab0c0065570239260da52e238a243b830214df9070abac589e815e470d3da'
    assert git('rev-parse','HEAD').decode().strip()==BASE
    assert not git('diff','--cached','--name-only')
    paths=set(); counts=collections.Counter(); total=0
    for f in manifest['files']:
        assert set(f)=={'path','sha256','role'}
        assert f['path'] not in paths and f['path']!= (FORMAL/'delivery_manifest_r03.json').relative_to(R).as_posix()
        assert not any(x in f['path'].split('/') for x in ['obj_dir','__pycache__']) and not f['path'].lower().endswith('.exe')
        paths.add(f['path']); counts[f['role']]+=1
        assert digest(R/f['path'])==f['sha256'],f
        total+=(R/f['path']).stat().st_size
    assert len(paths)==136
    bindings=checker.check_static(R)
    assert len(bindings)==31 and len(freeze['source_sha256'])==39
    assert set(freeze['source_sha256'])==set(bindings)|set(freeze['extra_bindings_beyond_static'])
    assert {p:digest(R/p) for p in freeze['source_sha256']}==freeze['source_sha256']
    assert freeze['frozen14_sha256']==checker.FROZEN_CORE_SHA256
    for p,h in checker.FROZEN_CORE_SHA256.items():
        assert digest(R/p)==h
        actual=(R/p).read_bytes();blob=git('show',BASE+':'+p)
        assert actual==blob or actual.replace(b'\r\n',b'\n')==blob,(p,'仅授权精确CRLF到LF映射')
        RESULT.setdefault('frozen14_git_classes',{})[p]='RAW' if actual==blob else 'EXACT_CRLF_TO_LF'
    conv='src/s2b_conv_tile_engine.sv'
    assert digest(R/conv)=='e8231b045b4b94565cb7b54c1e127878ad1850e88c70298c86af6d74009eebf8'
    assert (R/conv).read_bytes()==git('show',BASE+':'+conv)
    changed=set(git('diff','--name-only').decode('utf-8').splitlines())|{'verification/test_s2b_route_address_guard_rtl.py'}
    assert changed==set(freeze['changed_paths']),changed
    profile=read(R/'board/s2b_inference_platform.json')
    assert profile['clock_hz']==50000000 and profile['visibility_default']==0 and len(profile['rtl_sources'])==18
    branch="                    end else if ((output_offset_work >= {33'd0, output_length_latched}) ||\n                                 (output_base_latched + output_offset_work[31:0] < output_base_latched)) begin\n                        result_error_latched <= BAD_RANGE;\n                        state <= RESULT;\n"
    before={}; structures={}
    for p in ['src/s2b_route_query.sv','src/s2b_route_engine.sv']:
        raw=git('show',BASE+':'+p);before[p]=hashlib.sha256(raw).hexdigest()
        old=raw.decode('utf-8').replace('\r\n','\n'); new=(R/p).read_text(encoding='utf-8')
        assert old.split(');',1)[0]==new.split(');',1)[0]
        if 'engine' in p:
            ffold=old[old.index('    always_ff'):];ffnew=new[new.index('    always_ff'):]
            assert ffold.count(branch)==1 and ffold.replace(branch,'')==ffnew
            structures[p]={'header_equal':True,'ff_only_removed_four_lines':True,'remaining_ff_sha256':hashlib.sha256(ffnew.encode()).hexdigest()}
        else:
            assert new.count('always_ff')==0
            structures[p]={'header_equal':True,'combinational_only':True}
    assert before=={'src/s2b_route_query.sv':'b7a36db57f27a6d32ae6616b569fb51a4b81a08e171621d495a7f54af602e89c','src/s2b_route_engine.sv':'c8b774b053179f40bb431290880710b46f51d589c2eeb4608a5914ecb6f60f36'}
    RESULT['source_sha256_before']=freeze['source_sha256'];RESULT['changed_source_sha256']={p:freeze['source_sha256'][p] for p in freeze['changed_paths']}
    RESULT['source_closure']={'static':31,'extra':8,'total':39,'active_rtl':18,'frozen14':14,'conv_unchanged':True,'s6_baseline_sha256':before,'structure':structures}
    RESULT['formal_closure']={'files':len(paths),'bytes':total,'role_counts':dict(counts),'all_raw_hashes_equal':True,'self_reference':False}
    return freeze,profile

def configuration(c=1,h=1,w=1,c1=0,g=1,gid=0,base=0):
    """独立生成合法公开配置，source1未启用时仍保留公开参数。"""
    oc=c+c1 if g==1 else c//2
    v=dict(source_count=2 if c1 else 1,groups=g,group_id=gid,output_channel=oc-1,output_y=h-1,output_x=w-1,
           output_base_address=base,output_length_bytes=oc*h*w,output_channels=oc,output_height=h,output_width=w)
    for s,cs in enumerate((c,c1)):
        vals=dict(base_address=base if s==0 else 0,length_bytes=cs*h*w,channels=cs,height=h,width=w,
                  channel_start=(gid*(c//2) if s==0 and g==2 else 0),
                  channel_end=((gid+1)*(c//2) if s==0 and g==2 else cs),multiplier_q31=2**31,value=37 if s==0 else -53)
        v.update({f'source{s}_{k}':x for k,x in vals.items()})
    return v

def golden(v):
    """重新按无界整数谓词和线性索引定义黄金结果；不调用Developer oracle。"""
    n,g,gid=[v[k] for k in ('source_count','groups','group_id')]
    s=[{k.removeprefix(f'source{i}_'):val for k,val in v.items() if k.startswith(f'source{i}_')} for i in (0,1)]
    considered=[s[0]]+([s[1]] if n==2 else [])
    selections=[(a['channel_end']-a['channel_start'])%(U+1) for a in considered]
    oc=sum(selections);slot=0 if v['output_channel']<selections[0] else 1 if n==2 else 0
    chosen=s[slot];raw=chosen['value'] if v['output_channel']<selections[0] or n==2 else 0
    args=[n not in (1,2),g not in (1,2),gid>=g,v['output_channel']>=oc,v['output_y']>=s[0]['height'],v['output_x']>=s[0]['width'],raw==-128]
    ranges=[oc>U]
    for i,a in enumerate(considered):
        c,h,w,begin,end,mul=[a[k] for k in ('channels','height','width','channel_start','channel_end','multiplier_q31')]
        args.extend([min(c,h,w)==0,begin>=end,end>c,not 1<=mul<=2**31])
        if i==0:
            if g==1:args.append((begin,end)!=(0,c))
            if g==2:args.extend([n!=1,c%2!=0,(begin,end)!=(gid*(c//2),(gid+1)*(c//2))])
        else:args.extend([g!=1,(begin,end)!=(0,c),(h,w)!=(s[0]['height'],s[0]['width'])])
        ranges.extend([c*h>U,c*h*w>U,a['length_bytes']==0,c*h*w>a['length_bytes'],a['base_address']+a['length_bytes']>U+1])
    if any(args):return (0,0,0,0,0,0,0,1)
    if any(ranges):return (0,0,0,0,0,0,0,2)
    ch=chosen['channel_start']+v['output_channel']-(selections[0] if slot else 0)
    # 用NCHW线性展开而非候选连乘语句建立结果。
    off=ch*s[0]['height']*s[0]['width']+v['output_y']*s[0]['width']+v['output_x']
    addr=chosen['base_address']+off
    prefix=ch*s[0]['height']+v['output_y']
    assert 0<=ch<chosen['channels'] and prefix<=U and 0<=off<chosen['channels']*chosen['height']*chosen['width']<=chosen['length_bytes']<=U and addr<=U
    rounded=(abs(raw)*chosen['multiplier_q31']+2**30)//2**31
    value=min(127,rounded)*(-1 if raw<0 else 1)
    return (oc,s[0]['height'],s[0]['width'],slot,ch,addr,value%256,0)

def independent_vectors(ports,qports):
    """手算端点、不同种子的有效大域及有意非法域，独立生成两类向量。"""
    rng=random.Random(SEED);qrows=[];categories=collections.Counter();eng=[];ecats=collections.Counter()
    names=[n for d,w,n in ports if d=='input' and n not in {'clk','hard_reset','abort','start_valid','backend_req_ready','backend_rsp_valid','backend_rsp_rdata','backend_rsp_error','result_ready'}]
    def query(cat,v):
        v={k:(x if k.endswith('value') else x&U) for k,x in v.items()};qrows.append((v,golden(v)));categories[cat]+=1;return v
    def engine(cat,v,raw=23,error=0,target=0,control=0,state=255,stall=1):
        q=golden(dict(v,source0_value=0,source1_value=0));err=q[-1]
        if err==0:
            product=v['output_channels']*v['output_height']*v['output_width']
            if q[:3]!=(v['output_channels'],v['output_height'],v['output_width']) or min(v['output_channels'],v['output_height'],v['output_width'],v['output_length_bytes'])==0 or product>v['output_length_bytes']:err=3
            elif v['output_base_address']+v['output_length_bytes']>U+1:err=2
            else:
                offset=v['output_channel']*v['output_height']*v['output_width']+v['output_y']*v['output_width']+v['output_x']
                assert offset<product<=U and v['output_base_address']+offset<=U
        requests=0 if err else 1 if raw==-128 or error and target==1 else 2
        final=err if err else (error if error in (1,2,6) else 6) if error and target in (1,2) else 1 if raw==-128 else 0
        val=golden(dict(v,source0_value=raw,source1_value=raw))[6]
        outaddr=(v['output_base_address']+v['output_channel']*v['output_height']*v['output_width']+v['output_y']*v['output_width']+v['output_x'])&U
        extras=[raw&255,error,target,control,state,stall,final,q[3],q[5],outaddr,val,requests]
        eng.append(' '.join(f'{v[n]&U:x}' for n in names)+' '+' '.join(f'{x:x}' for x in extras));ecats[cat]+=1
    manual=[configuration(base=U),configuration(c=U,base=1),configuration(h=U,base=1),configuration(w=U,base=1),
            configuration(c=0x80000000),configuration(c=2,h=65535,w=32768),configuration(c=U-1,g=2,gid=0),configuration(c=U-1,g=2,gid=1),
            configuration(c=0x80000000,c1=0x7fffffff),configuration(c=U,c1=U),configuration(c=65536,h=65536,w=1),
            configuration(c=2,h=65536,w=32768),configuration(c=U,h=U,w=U)]
    for v in manual:
        v=query('hand_u32_end_product',v);engine('hand_u32_end_product',v)
    assert qrows[0][1]==(1,1,1,0,0,U,37,0)
    assert qrows[1][1][5]==U and qrows[8][1][0]==U
    assert qrows[9][1][-1]==2 and qrows[10][1][-1]==2 and qrows[11][1][-1]==2 and qrows[12][1][-1]==2
    for i in range(2500):
        group=2 if i%3==0 else 1
        h=rng.choice([1,2,3,7,257,65535]); w=rng.choice([1,2,13,127])
        cap=U//(h*w); total=rng.choice([max(2,cap-2),max(2,cap//2),rng.randint(2,min(cap,9999))])
        if group==2:total &=~1
        c1=rng.randint(1,total-1) if group==1 and i%2 else 0
        v=configuration(total-c1,h,w,c1,group,(i//3)%2 if group==2 else 0)
        for slot in range(v['source_count']):
            p=f'source{slot}_';size=v[p+'length_bytes'];v[p+'length_bytes']=size+rng.randint(0,min(31,U-size))
            v[p+'base_address']=U+1-v[p+'length_bytes'] if i%2 else rng.randint(0,U+1-v[p+'length_bytes'])
            v[p+'multiplier_q31']=rng.choice([1,3,0x3fffffff,0x40000000,0x7fffffff,0x80000000]);v[p+'value']=rng.randrange(-127,128)
        v['output_base_address']=U+1-v['output_length_bytes']
        v['output_channel']=rng.choice([0,v['output_channels']-1,rng.randrange(v['output_channels'])])
        v['output_y']=rng.randrange(h);v['output_x']=rng.randrange(w)
        if v['source_count']==1:
            for k in list(v):
                if k.startswith('source1_'):v[k]=rng.randrange(-128,128) if k.endswith('value') else rng.getrandbits(32)
        query('seeded_valid_large',v);engine('seeded_valid_large',v,raw=v['source0_value'] if v['source_count']==1 else 23,stall=i%2)
        if i<250:
            for cat,key,x in [('coord_and_range','output_x',w),('argument_and_range','groups',0),('short_source','source0_length_bytes',max(0,v['source0_channels']*h*w-1)),('source_end_overflow','source0_base_address',U)]:
                a=dict(v,**{key:x})
                if 'and_range' in cat:a['source0_length_bytes']=0
                query(cat,a);engine(cat,a)
            for cat,key,x in [('output_length','output_length_bytes',v['output_channels']*h*w-1),('output_end','output_base_address',U),('output_shape_and_end','output_channels',U)]:
                a=dict(v,**{key:x});a['output_base_address']=U;engine(cat,a)
    for raw in range(-128,128):
        for mul in [0,1,0x40000000,0x80000000,0x80000001,U]:
            v=dict(configuration(),source0_value=raw,source0_multiplier_q31=mul);query('int8_all_multiplier_bounds',v)
    for group in [0,1,2,3,4,0x80000000,U]:
        for gid in [0,1,2,U]:
            v=dict(configuration(c=4),groups=group,group_id=gid);query('groups_all_domain_rejection',v);engine('groups_all_domain_rejection',v)
    qnames=[n for d,w,n in qports if d=='input']
    for i in range(4000):
        v=configuration()
        for n in qnames:v[n]=rng.randrange(-128,128) if n.endswith('value') else rng.getrandbits(32)
        query('seeded_full_u32',v)
        if i<500:engine('seeded_full_u32',v)
    for slot,target in [(0,1),(0,2),(1,1)]:
        v=configuration(c1=1) if slot else configuration()
        for error in range(8):engine('response24',v,error=error,target=target)
    for raw in range(-40,40):engine('raw80',configuration(base=U),raw=raw)
    for control in [1,2]:
        for state in range(8):engine('abort8' if control==1 else 'reset8',configuration(c=4,h=3,w=5,c1=2),control=control,state=state)
    engine('infinite_backpressure_abort',configuration(),control=3,stall=2)
    qdata='\n'.join(' '.join(f'{v[n]&U:x}' for n in qnames)+' '+' '.join(f'{x:x}' for x in expected) for v,expected in qrows)+'\n'
    (W/'query_vectors.dat').write_text(qdata,encoding='utf-8',newline='\n')
    (W/'route_vectors.dat').write_text('\n'.join(eng)+'\n',encoding='utf-8',newline='\n')
    RESULT['independent_coverage']={'seed':SEED,'query_vectors':len(qrows),'query_categories':dict(categories),'query_errors':dict(collections.Counter(q[-1] for v,q in qrows)),
        'engine_vectors':len(eng),'engine_categories':dict(ecats),'query_outputs':8,'engine_outputs_compared':len([n for d,w,n in ports if d=='output']),
        'reuse':'只复用公开口驱动与逐周期比较框架；黄金函数、种子和全部向量独立新建；未调用G1 oracle/cases/vectors'}
    return qnames,qports

def mutations(checker,profile,freeze):
    """故意同步声明SHA，必须仍被精确派生关系拒绝。"""
    fixture=W/'checker_fixture'; fixture.mkdir()
    for p in freeze['source_sha256']:
        if p.startswith(('src/','board/','vivado/')) or p=='verification/check_s2b_inference_platform.py':
            dst=fixture/p;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((R/p).read_bytes())
    base=copy.deepcopy(profile);check=checker.check_static(fixture);assert len(check)==31
    tests=[('query_31bit','src/s2b_route_query.sv','logic [31:0] selected_offset;','logic [30:0] selected_offset;'),
           ('engine_31bit','src/s2b_route_engine.sv','logic [31:0] output_offset_work;','logic [30:0] output_offset_work;'),
           ('wrong_priority','src/s2b_route_query.sv','        if (bad_argument) begin','        if (bad_argument && !bad_range) begin'),
           ('result_gating','src/s2b_route_engine.sv','result_valid = (state == RESULT);','result_valid = (state == RESULT) && !abort;'),
           ('pre_shape','src/s2b_route_query.sv',"if (source0_plane_elements > 64'h0000_0000_FFFF_FFFF)","if (source0_plane_elements > 64'h0000_0001_FFFF_FFFF)"),
           ('output_endpoint','src/s2b_route_engine.sv',"output_end_work > 65'h0000_0001_0000_0000","output_end_work > 65'h0000_0001_0000_0001"),
           ('recovery_state','src/s2b_route_engine.sv',"state <= IDLE;\n                        result_error_latched <= NONE;","state <= VALIDATE;\n                        result_error_latched <= NONE;")]
    records=[]
    for label,p,before,after in tests:
        original=(R/p).read_text(encoding='utf-8');assert original.count(before)==1,(label,original.count(before))
        mutant=original.replace(before,after);(fixture/p).write_text(mutant,encoding='utf-8',newline='\n')
        claimed=copy.deepcopy(base); sha=digest(fixture/p)
        for item in claimed['source_derivation']['derived_sources']:
            if item['path']==p:item['sha256']=sha
        (fixture/'board/s2b_inference_platform.json').write_text(json.dumps(claimed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        try:checker.check_static(fixture)
        except ValueError as exc:
            reason=str(exc);assert '未授权的额外差异' in reason,reason
            rec={'name':label,'path':p,'before':before,'after':after,'self_reported_sha256':sha,'self_hash_updated':True,'accepted':False,'rejection':reason}
            records.append(rec);save('mutation_'+label+'.json',rec)
        else:raise AssertionError('检查器接受篡改：'+label)
        (fixture/p).write_bytes((R/p).read_bytes())
    (fixture/'board/s2b_inference_platform.json').write_bytes((R/'board/s2b_inference_platform.json').read_bytes())
    assert checker.check_static(fixture)==check
    RESULT['checker_mutations']=records

def simulation_framework(route,geometry,qnames,qports):
    """框架保留全部公开口比较、八态取消和结果保持，替换为独立向量读入。"""
    ports=geometry.ports(R/'src/s2b_route_engine.sv')
    tb=route.testbench({'layers':[]},ports).replace('s2a_route_engine dut_old','s6_route_engine dut_old').replace('int8_route_query q_qo','s6_route_query q_qo')
    qouts=[n for d,w,n in qports if d=='output']
    declarations='integer qf,qs; '+' '.join('logic [31:0] expect_'+n+';' for n in qouts)+'\n'
    fmt=' '.join('%h' for _ in qnames+qouts)+'\\n'
    run='qf=$fopen("query_vectors.dat","r");if(!qf)$fatal(1,"缺独立向量");while(!$feof(qf))begin qs=$fscanf(qf,"'+fmt+'",'+','.join(qnames+['expect_'+n for n in qouts])+');if(qs=='+str(len(qnames)+len(qouts))+')begin query_compare;'
    for n in qouts:
        bits=8 if n=='output_value' else 3 if n=='error_code' else 32
        run+=f'if($unsigned(qo_{n})!=={bits}\'(expect_{n}))$fatal(1,"独立黄金 {n} case=%0d",query_cases);'
    run+='end else if(qs!=-1)$fatal(1,"独立列数");end $fclose(qf);\n'
    begin=tb.index('$fclose(fh);clear;')+len('$fclose(fh);clear;');end=tb.index('if(abort_mask!=255',begin)
    tb=tb[:begin]+'\n'+run+tb[end:]
    tb=tb.replace('integer fh,scanned',declarations+'integer fh,scanned')
    # 结果保持的公开值额外快照，验证背压期间三周期不改变；abort RESULT单独保留原语义。
    tb=tb.replace('integer fh,scanned','logic [31:0] held_source_index,held_source_address,held_output_address; logic [7:0] held_value; logic [2:0] held_error;\ninteger fh,scanned')
    tb=tb.replace('    repeat(3) service;', '    if(old_result_valid) begin held_source_index=old_result_source_index;held_source_address=old_result_source_address;held_output_address=old_result_output_address;held_value=old_result_value;held_error=old_result_error_code;repeat(3) begin service;if(!old_result_valid||old_result_source_index!==held_source_index||old_result_source_address!==held_source_address||old_result_output_address!==held_output_address||old_result_value!==held_value||old_result_error_code!==held_error)$fatal(1,"结果背压保持失败");end end else repeat(3) service;')
    (W/'tb_s2b_route_specialization.sv').write_text(tb,encoding='utf-8',newline='\n')
    source=W/'source';source.mkdir()
    for p in ('src/s2b_route_query.sv','src/s2b_route_engine.sv'):
        raw=git('show',BASE+':'+p)
        (source/('s6_raw_'+Path(p).name)).write_bytes(raw)
        renamed=raw.decode('utf-8').replace('s2b_route_engine','s6_route_engine').replace('s2b_route_query','s6_route_query')
        (source/('s6_'+Path(p).name)).write_text(renamed,encoding='utf-8',newline='\n')
        (source/Path(p).name).write_bytes((R/p).read_bytes())
    return source

def main():
    began=time.monotonic()
    assert R==Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
    sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'verification'))
    checker=imported('independent_checker',R/'verification/check_s2b_inference_platform.py')
    freeze,profile=reference_audit(checker)
    mutations(checker,profile,freeze)
    geometry=imported('geometry_frame',R/'verification/test_s2b_geometry_specialization_rtl.py')
    route=imported('route_frame',R/'verification/test_s2b_route_specialization_rtl.py')
    qhead=(R/'src/s2b_route_query.sv').read_text(encoding='utf-8').split(');',1)[0]
    qports=re.findall(r'^\s*(input|output)\s+logic\s*(?:signed\s*)?(\[[^\]]+\])?\s*(\w+)',qhead,re.M)
    ports=geometry.ports(R/'src/s2b_route_engine.sv')
    qnames,qports=independent_vectors(ports,qports)
    source=simulation_framework(route,geometry,qnames,qports)
    save('precompile_audit.json',RESULT)
    RESULT['resource_preflight']={'available_ram_bytes':psutil.virtual_memory().available,'disk_free_bytes':shutil.disk_usage(W).free,
        'running_heavy':[{'pid':p.pid,'name':p.info['name']} for p in psutil.process_iter(['name']) if p.info['name'] and p.info['name'].lower() in ['vivado.exe','verilator_bin.exe','cc1plus.exe']],
        'jobs':1,'threads':1,'rss_limit_bytes':1610612736,'timeout_seconds':600}
    assert not RESULT['resource_preflight']['running_heavy']
    assert RESULT['resource_preflight']['available_ram_bytes']>=2147483648 and RESULT['resource_preflight']['disk_free_bytes']>=1073741824
    save('resource_preflight.json',RESULT['resource_preflight'])
    tool=Path(r'D:\FPGA_S2A_MSYS2_20261001\env');bd=tool/'mingw64/bin';md=tool/'usr/bin'
    for p in [bd/'verilator_bin.exe',bd/'g++.exe',md/'make.exe']:assert p.is_file()
    env=os.environ.copy();env['PATH']=str(md)+os.pathsep+str(bd)+os.pathsep+env['PATH'];env['VERILATOR_ROOT']=str(tool/'mingw64/share/verilator');env['PYTHONUTF8']='1'
    native('verilator_version',[str(bd/'verilator_bin.exe'),'--version'],env=env)
    sources=['source/s2b_route_engine.sv','source/s2b_route_query.sv','source/s6_s2b_route_engine.sv','source/s6_s2b_route_query.sv']
    command=[str(bd/'verilator_bin.exe'),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1','--output-split','10000','--output-split-cfuncs','100','--top-module','tb_s2b_route_specialization','--Mdir','obj_dir','-MAKEFLAGS',"PYTHON3='\""+sys.executable+"\"'",'-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1',*sources,'tb_s2b_route_specialization.sv']
    clog=native('compile',command,cwd=W,env=env)
    assert not re.findall(r'%Warning-(LATCH|UNOPTFLAT|MULTIDRIVEN)\b',clog)
    slog=native('simulation',[str(W/'obj_dir/Vtb_s2b_route_specialization.exe')],cwd=W,env=env)
    matches=re.findall(r'PASS ROUTE_SPECIALIZATION cases=(\d+) queries=(\d+) cycles=(\d+) abort=(\d+) reset=(\d+)',slog)
    assert len(matches)==1
    RESULT['simulation_counts']=dict(zip(['engine','query','cycles','abort_mask','reset_mask'],map(int,matches[0])))
    assert RESULT['simulation_counts']['engine']==RESULT['independent_coverage']['engine_vectors']
    assert RESULT['simulation_counts']['query']==RESULT['independent_coverage']['query_vectors']
    assert RESULT['simulation_counts']['abort_mask']==RESULT['simulation_counts']['reset_mask']==255
    RESULT['source_sha256_after']={p:digest(R/p) for p in freeze['source_sha256']}
    assert RESULT['source_sha256_before']==RESULT['source_sha256_after']
    RESULT['status']='INDEPENDENT_RTL_PASS_PENDING_G1_AUDIT'
    RESULT['seconds']=round(time.monotonic()-began,3)

if __name__=='__main__':
    try:main()
    except Exception as exc:RESULT['failure']=repr(exc);RESULT['traceback']=traceback.format_exc()
    save('independent_rtl_receipt_r02.json',RESULT)
    print(json.dumps({k:RESULT.get(k) for k in ['status','failure','simulation_counts','independent_coverage']},ensure_ascii=False),flush=True)
    raise SystemExit(0 if RESULT['status']=='INDEPENDENT_RTL_PASS_PENDING_G1_AUDIT' else 2)
