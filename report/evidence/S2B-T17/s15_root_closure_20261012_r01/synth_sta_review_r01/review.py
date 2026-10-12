"""S15综合STA独立只读机器审查，保持历史失败和预算受阻原语义。"""
from pathlib import Path
import sys, json, hashlib, re, subprocess, time, collections
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent/'attempt_r03'
F=ROOT/'report/evidence/S2B-T17/s15_platform_20261012_r01'
BASE='926c2fd382069e68e6c5ec533b7d3b6a87fbb363'
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_conv_tile_origin_rtl as previous
import test_s2b_backend_coordinates_rtl as support
def sha(path):
    """绑定完整真实原字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    """读取UTF8 JSON。"""
    return json.loads(path.read_text(encoding='utf-8'))
def text(name):
    """读取声明报告原文。"""
    return (F/name).read_text(encoding='utf-8')
def save(name,value):
    """只在本次隔离目录创建新证据。"""
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def unwrap(value):
    """两种真实MCP封装明确选择，不改字段。"""
    return json.loads(value.get('result',value)['content'][0]['text'])
receipt=dict(schema_version=1,status='CHANGES_REQUIRED',stop=False,source_commit=BASE,production_commit='5492928349e5e5c0b72dab10c136dab8c549cea2',findings=[],native_checks=[],limitations=['仅综合与Synthesized STA，不证明PNR、postroute、实板或G3/G4/G5。','SOURCE wrapper与连续资源预算身份仍BLOCKED，不能以包装CHECKS_OK或独立源码字节核验升级。','五Vivado作业OS进程原生退出码未知；保留日志/marker与真实MCP wait_on_run0，不伪造五child0。','先前details只读结构脚本误选result封装native1在宿主工具结果中，非STA失败；失败源码保存，实际独立机器审查另有直接wait日志。'])
started=time.monotonic()
try:
    checker=support.load_checker();previous.exact_directory(HERE)
    assert previous.git('rev-parse','HEAD').decode().strip()==BASE
    r01=F/'s15_root_delivery_manifest_r01.json';r02=F/'s15_root_delivery_manifest_r02.json'
    assert sha(r01)=='e45ba1c837d600b387fe7067c81dd442685dc1832457153bb21cb85f8c1f163f'
    assert sha(r02)=='b730f13e3447717287815de1977a4b72007d55eb58ff660062a6e89e032f5aec'
    r03=F/'s15_root_delivery_manifest_r03.json';assert sha(r03)=='02e5d0d6da4ac331e0c0686d710c58d27944fe60dcd8b474296cbb6a31e88824'
    m1=read(r01);m2=read(r02);m3=read(r03);assert len(m1['files'])==424 and len(m2['files'])==434 and len(m3['files'])==438
    audits=[]
    for manifest in (m1,m2,m3):
        for row in manifest['files']:
            p=checker.exact_file(ROOT/row['path']);assert sha(p)==row['sha256'],row['path']
            audits.append(dict(path=row['path'],sha256=row['sha256']))
    save('bound_original_file_hashes.json',audits)
    receipt['manifest']=dict(r01_sha256=sha(r01),r01_bindings=424,r02_sha256=sha(r02),r02_bindings=434,r03_sha256=sha(r03),r03_bindings=438)
    pack1=read(F/'packaging_check_r01.native.json');pack2=read(F/'packaging_check_r02.native.json')
    assert pack1['native_exit_code']==2 and pack2['native_exit_code']==0
    assert 'CHECKS_OK' in text('packaging_check_r02.stdout.bin')
    record=dict(runs=[])
    previous.execute('independent_evidence',[sys.executable,'-X','utf8','-B',str(ROOT/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(r03)],ROOT,HERE,dict(__import__('os').environ),record,90)
    receipt['native_checks'].extend(record['runs'])
    receipt['packaging_current']='r03438绑定独立重建0；r02当时0及随后新增三日志造成独立2均保留，不计综合或STA失败。'
    before=read(F/'mcp_closed/source_before.json');after=read(F/'mcp_closed/source_after.json');freeze=read(F/'native_capture_closed/source_freeze_r01.json')
    assert before['source_sha256']==after['source_sha256']
    assert before['source_count']==after['source_count']==len(freeze['source_files'])==46
    assert before['platform_static_source_count']==after['platform_static_source_count']==33
    static=checker.check_static(ROOT);assert len(static)==33 and dict(static)==freeze['static_source_sha256']==before['static_source_sha256']==after['static_source_sha256']
    assert len(checker.FROZEN_CORE_SHA256)==14 and before['frozen14_sha256']==after['frozen14_sha256']==freeze['frozen14']==checker.FROZEN_CORE_SHA256
    sources=[];relations=collections.Counter()
    gitdir=HERE/'git';gitdir.mkdir()
    for i,row in enumerate(before['source_files']):
        p=checker.exact_file(ROOT/row['path']);raw=p.read_bytes();assert sha(p)==row['sha256']==after['source_sha256'][row['path']]
        snap=checker.exact_file(ROOT/row['snapshot']);assert snap.read_bytes()==raw
        command=['git','-c','core.longpaths=true','-c','maintenance.auto=false','show',BASE+':'+row['path']]
        child=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE);blob,err=child.communicate(timeout=30);code=child.wait(timeout=30);assert code==0
        (gitdir/(str(i)+'.stdout.bin')).write_bytes(blob);(gitdir/(str(i)+'.stderr.bin')).write_bytes(err)
        if blob==raw:relation='RAW_IDENTICAL'
        else:
            assert b'\r\n' not in blob and blob.replace(b'\n',b'\r\n')==raw,row['path']
            relation='EXACT_LF_TO_CRLF'
        relations[relation]+=1
        sources.append(dict(path=row['path'],sha256=sha(p),snapshot=row['snapshot'],snapshot_sha256=sha(snap),git_relation=relation,git_blob_sha256=hashlib.sha256(blob).hexdigest(),git_command=command,git_native_exit_code=code,direct_wait_returned=True))
    assert relations==dict(RAW_IDENTICAL=40,EXACT_LF_TO_CRLF=6)
    save('independent_source_binding.json',dict(sources=sources,relations=dict(relations),frozen14=checker.FROZEN_CORE_SHA256))
    profile=read(ROOT/'board/s2b_inference_platform.json');assert profile['version']=='s2b-inference-platform/0.1.15' and profile['visibility_default']==0 and profile['clock_hz']==50000000 and profile['vivado_part']=='xc7z020clg400-2'
    assert before['visibility_parameter']==after['visibility_parameter']==0 and len(profile['rtl_sources'])==18
    setup=text('setup_synthesis.tcldict');registered=re.findall(r'\{(src/[^ ]+\.sv) C:/[^}]+\}',setup)
    assert registered==profile['rtl_sources'] and len(set(registered))==18
    assert 'top s2b_inference_wrapper part xc7z020clg400-2 threads 1 jobs 1 profile 0.1.12 visibility 0 clock_hz 50000000' in setup
    infer_tcl=text('native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl')
    readblock=re.search(r'read_verilog -library xil_defaultlib -sv \{(.*?)\}',infer_tcl,re.S)[1]
    actual=re.findall(r'C:/Users/22061/\.codex/worktrees/96a3/FPGA_Competition/(src/[^\s]+\.sv)',readblock)
    assert len(actual)==18 and set(actual)==set(registered)
    wrapper=text('generated_inputs/s2b_inference_wrapper.v');assert wrapper.count('module s2b_inference_wrapper')==1
    wrapper_tcl=text('native_jobs/wrapper_native_s15_r01/s2b_inference_wrapper.tcl')
    assert len(re.findall(r'(?m)^read_verilog [^\r\n]*s2b_inference_wrapper\.v\s*$',wrapper_tcl))==1
    assert '.PROFILE_VISIBILITY_PROVEN(1\'D0)' in text('generated_inputs/s2b_inference_infer_0.sv')
    receipt['platform']=dict(part=profile['vivado_part'],visibility=0,clock_hz=50000000,registered18=registered,unique_wrapper=True,namespace='0.1.12',static_count=33,source_count=46)
    timing=text('timing_summary_synth.rpt');assert '| Design State : Synthesized' in timing and '| Speed File   : -2' in timing
    assert 'report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose' in timing
    match=re.search(r'(?m)^\s*(0\.194)\s+(0\.000)\s+(0)\s+(15126)\s+(0\.037)\s+(0\.000)\s+(0)\s+(15126)\s+(8\.870)\s+(0\.000)\s+(0)\s+(4369)\s*$',timing);assert match
    checkpairs=re.findall(r'(?m)^\d+\. checking (\w+) \((\d+)\)',timing);checks=dict(checkpairs)
    expected=('no_clock','constant_clock','pulse_width_clock','unconstrained_internal_endpoints','no_input_delay','no_output_delay','multiple_clock','generated_clocks','loops','partial_input_delay','partial_output_delay','latch_loops')
    assert set(checks)==set(expected) and all(int(n)==0 for _,n in checkpairs) and len(checkpairs)==24
    assert re.search(r'clk_fpga_0\s+\{0\.000 10\.000\}\s+20\.000\s+50\.000',timing)
    assert 'All user specified timing constraints are met.' in timing
    worst=text('timing_worst_synth.rpt');slacks=[float(n) for n in re.findall(r'Slack \(MET\)\s*:\s*([-+\d.]+)ns',worst)]
    assert slacks and min(slacks)==.194 and all(n>=0 for n in slacks)
    methodology=text('methodology_synth.rpt');assert re.search(r'Checks found:\s+0',methodology) and '| Design State : Synthesized' in methodology
    xdc=text('constraints_synth.xdc');commands=[line.strip() for line in xdc.splitlines() if line.strip() and not line.lstrip().startswith('#')]
    assert sum(line.startswith('create_clock ') for line in commands)==1
    assert 'create_clock -period 20.000 -name clk_fpga_0 [get_pins {PS7_i/FCLKCLK[0]}]' in commands
    assert 'set_input_jitter clk_fpga_0 0.600' in commands
    allowed=('current_instance','create_clock','set_input_jitter','set_false_path');assert all(line.split()[0] in allowed for line in commands)
    assert commands.count('set_false_path -to [get_cells {syncstages_ff_reg[0]}]')==2
    assert sum('ACTIVE_HIGH_AUX.ACT_HI_AUX' in line for line in commands)==1 and sum('ACTIVE_LOW_EXT.ACT_LO_EXT' in line for line in commands)==1
    assert 'No valid timing exceptions found.' in text('exceptions_synth.rpt')
    assert re.search(r'clk_fpga_0\s+20\.000\s+\{0\.000 10\.000\}',text('clocks_synth.rpt'))
    receipt['independent_sta']=dict(wns_ns=.194,tns_ns=0,setup_failing=0,setup_endpoints=15126,whs_ns=.037,ths_ns=0,hold_failing=0,hold_endpoints=15126,wpws_ns=8.870,pulse_failing=0,pulse_endpoints=4369,clock_period_ns=20,clock_frequency_mhz=50,check_timing=checks,methodology_checks=0,worst_paths=len(slacks),exported_false_paths=2,exception_report='No valid timing exceptions found; exported reset CDC directives remain explicit.',report_sha256=sha(F/'timing_summary_synth.rpt'))
    flat=text('utilization_flat_synth.rpt');resource={}
    for name,want,capacity in (('Slice LUTs*',21505,53200),('Slice Registers',4203,106400),('Block RAM Tile',32,140),('DSPs',143,220),('Register as Latch',0,106400)):
        row=re.search(r'\|\s*'+re.escape(name)+r'\s*\|\s*(\d+)\s*\|\s*0\s*\|\s*0\s*\|\s*(\d+)\s*\|',flat);assert row and tuple(map(int,row.groups()))==(want,capacity)
        resource[name]=dict(used=want,available=capacity)
    drc=text('drc_synth.rpt');assert re.search(r'Checks found:\s+395',drc)
    warnings=re.findall(r'(?m)^(DPIP-1|DPOP-1|DPOP-2)#\d+ Warning\s*$',drc);assert dict(collections.Counter(warnings))=={'DPIP-1':116,'DPOP-1':139,'DPOP-2':140}
    assert not re.search(r'(?m)^\w[\w-]*#\d+ (?:Error|Critical Warning)\s*$',drc)
    receipt['resources']=resource;receipt['drc']=dict(warnings=395,classes=dict(collections.Counter(warnings)),scope='DSP流水线建议Warning仍保留，不计时序失败或资源预算PASS。')
    full=unwrap(read(F/'mcp_closed/history_full.tool.json'));design=unwrap(read(F/'mcp_closed/history_design.tool.json'))
    assert full['returned']==full['total_commands']==len(full['history'])==14 and len(design['history'])==9
    mapping=read(F/'s15_mcp_binding.json');assert mapping['design_execute_calls']==9
    fullby={h['id']:h for h in full['history']};paired=[]
    for row in mapping['paired_calls']:
        native=row['native_history'];assert native==fullby[native['id']]
        client=read(ROOT/row['client_record']['path']);assert client['input']['command']==native['command']
        result=unwrap(client);assert result['exit_code']==row['client_exit_code']
        assert native in design['history'];paired.append(dict(label=row['label'],id=native['id'],command=native['command'],native_history_code=native['code'],client_exit_code=result['exit_code']))
    assert fullby[2]['code']==1 and 'PATH_ALREADY_EXISTS:' in fullby[2]['output'] and 'ATTEMPT:' not in fullby[2]['output']
    assert fullby[3]['code']==1 and mapping['products_native_exit_code']==0 and mapping['products_capture_exit_code']==1 and not mapping['products_repeated']
    assert re.search(r'\bstatus FAIL code 0\b',text('products.tcldict'))
    assert sum(h['command']=='launch_runs synth_1 -jobs 1' for h in full['history'])==1
    assert fullby[10]['command']=='wait_on_run synth_1' and fullby[10]['code']==0
    assert fullby[14]['command']=='close_project' and fullby[14]['code']==0
    save('independent_mcp_binding.json',dict(full_calls=14,paired9=paired,products_native=0,products_capture=1,firstbuilder='PATH_ALREADY_EXISTS before products',actual_products_count=1,actual_synthesis_launches=1,close_project=0))
    native_map=read(F/'s15_native_mapping.json');assert native_map['native_job_count']==5 and native_map['native_vds_count']==5
    jobs=[]
    for job in native_map['jobs']:
        mapped=[row for row in native_map['files'] if row['original_path'].endswith('/'+job['run']+'/runme.log')];assert len(mapped)==1
        folder=(ROOT/mapped[0]['saved_path']).parent;previous.exact_directory(folder)
        assert (folder/'.vivado.begin.rst').is_file() and (folder/'.vivado.end.rst').is_file() and not (folder/'.vivado.error.rst').exists()
        log=(folder/'runme.log').read_text(encoding='utf-8');assert 'synth_design completed successfully' in log and '0 Critical Warnings and 0 Errors encountered.' in log
        assert job['raw_os_process_exit_code'] is None
        jobs.append(dict(run=job['run'],begin_sha256=sha(folder/'.vivado.begin.rst'),end_sha256=sha(folder/'.vivado.end.rst'),log_sha256=sha(folder/'runme.log'),log_success=True,os_exit_code=None))
    save('independent_native_jobs.json',jobs)
    collector=read(F/'native_capture_closed/s15_runtime_collect_r1.native.json');launcher=read(F/'native_capture_closed/root_collect_launch_r01.native.json')
    assert collector['native_exit_code']==collector['wrapper_exit_code']==0 and collector['direct_child_wait_returned'] and collector['unknown_count']==0 and collector['capture_status']=='CLOSED_NATIVE_SUCCESS'
    assert launcher['native_exit_code']==0
    receipt['collector']=dict(child=0,wrapper=0,unknown_count=0,direct_child_wait_returned=True,launcher_native=0)
    sourcecaptures=[]
    for phase,wantunknown in (('before',27),('after',26)):
        item=read(F/('native_capture_closed/s15_runtime_source_'+phase+'_r1.native.json'))
        assert item['native_exit_code']==0 and item['wrapper_exit_code']==2 and item['unknown_count']==wantunknown
        sourcecaptures.append(dict(phase=phase,actual_child=0,wrapper=2,unknown_count=wantunknown,status=item['capture_status']))
    obs=read(F/'mcp_closed/closed_runtime_observation.json')
    assert obs['continuous_budget_status']=='NOT_PROVEN_CONTINUOUS_FROM_DISCRETE_SAMPLES'
    assert len(obs['known_identity_observations'])==38 and all(row['status']=='ABSENT' for row in obs['known_identity_observations'])
    for row in obs['monitor_rounds']:assert row['guard_native_exit_code']==3 and row['supervisor_exit_code']==2 and row['consumer_native_exit_code']==2
    receipt['preserved_blocks']=dict(sourcecaptures=sourcecaptures,monitor_rounds=obs['monitor_rounds'],continuous_budget=obs['continuous_budget_status'],known_old_identities=38,known_old_identity_observation='ABSENT',entire_os_tree_terminal=obs['entire_os_tree_terminal'])
    for row in sources:assert sha(ROOT/row['path'])==row['sha256']
    for row in m1['files']:assert sha(ROOT/row['path'])==row['sha256']
    receipt['source_bindings']=sources;receipt['git_relations']=dict(relations)
    receipt['status']='PASS_SYNTHESIS_STA_ONLY';receipt['allowed_next']='允许消费本次固定综合与源码证据进入独立PNR；PNR必须另行遵守资源准入与监护，当前连续资源预算不批准。'
except Exception as error:
    receipt['error']=repr(error);receipt['diagnostic_traceback']=__import__('traceback').format_exc()
finally:
    receipt['stop']=True;receipt['elapsed_seconds']=round(time.monotonic()-started,3);receipt['reviewer_sha256']=sha(Path(__file__))
    receipt['created_at_utc8']=datetime.now(timezone(timedelta(hours=8))).isoformat();save('final_review_receipt.json',receipt)
    print(json.dumps(dict(status=receipt['status'],error=receipt.get('error'),stop=True,seconds=receipt['elapsed_seconds'],receipt_sha256=sha(HERE/'final_review_receipt.json')),ensure_ascii=True),flush=True)
sys.exit(0 if receipt['status']=='PASS_SYNTHESIS_STA_ONLY' else 1)
