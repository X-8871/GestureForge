"""S8实际综合失败证据独立轻量核验，不启动Vivado或设备。"""
from pathlib import Path
import json,hashlib,sys,subprocess,time,re,zipfile,traceback,importlib.util
from collections import Counter
import psutil
ROOT=Path.cwd(); WORK=Path(__file__).resolve().parent
BASE=ROOT/'report/evidence/S2B-T17/s8_platform_20261011_r01'
HEAD='c9f423cddc74ea45071fdbb6a68e4505316babb1'
INPUTS=set(); report={'status':'RUNNING','native_runs':[],'findings':[]}
def raw(p):
    """记录直接输入及真实字节。"""
    p=ROOT/p if isinstance(p,str) else p; assert p.is_file(),str(p); INPUTS.add(p); return p.read_bytes()
def text(p): return raw(p).decode('utf-8')
def read(p): return json.loads(text(p))
def digest(data): return hashlib.sha256(data).hexdigest()
def bind(p): return digest(raw(p))
def check_row(row,key='path'):
    """独立核对每项实际文件绑定。"""
    data=raw(row[key]); assert digest(data)==row['sha256'],row[key]
    if 'bytes' in row: assert len(data)==row['bytes'],row[key]
def unpack(obj): return json.loads(obj['result']['content'][0]['text'])
def native(label,args,expected=0):
    """保留真实原生退出码、命令字符串和输出。"""
    started=time.monotonic(); done=subprocess.run(args,cwd=ROOT,capture_output=True)
    (WORK/(label+'_r02.stdout.log')).write_bytes(done.stdout); (WORK/(label+'_r02.stderr.log')).write_bytes(done.stderr)
    report['native_runs'].append({'name':label,'command':subprocess.list2cmdline(args),'native_exit_code':done.returncode,'expected_exit_code':expected,'elapsed_seconds':round(time.monotonic()-started,3)})
    assert done.returncode==expected,(label,done.returncode,done.stderr)
    return done.stdout
def all_dicts(obj):
    """递归找原始history记录，无摘要替代。"""
    if isinstance(obj,dict):
        yield obj
        for v in obj.values(): yield from all_dicts(v)
    elif isinstance(obj,list):
        for v in obj: yield from all_dicts(v)
def main():
    """对源、MCP、STA、XSA及关闭记录执行断言。"""
    started=time.monotonic(); peak=psutil.Process().memory_info().rss
    assert native('head',['git','rev-parse','HEAD']).decode().strip()==HEAD
    manifest_path=BASE/'s8_delivery_manifest_r02.json'; manifest=read(manifest_path)
    assert bind(manifest_path)=='a63839ea6e82b71fa28c6f9bd37223123ffeda3df5f122978b9b420c8c962e0e'
    assert manifest['source_commit']==HEAD and len(manifest['files'])==318
    for row in manifest['files']: check_row(row)
    for row in manifest['checks']:
        if row['status']=='PASS': assert isinstance(row['command'],str) and row['command'].strip() and row['exit_code']==0,row
    native('evidence',[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','evidence','--manifest',str(manifest_path)])
    native('inputs',[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','inputs','--manifest',str(manifest_path)],2)
    before=read('report/evidence/S2B-T17/s8_source_preflight_20261011_r01/source_before.json')
    after=read('report/evidence/S2B-T17/s8_source_preflight_20261011_r01/source_after.json')
    assert before['source_sha256']==after['source_sha256'] and len(before['source_files'])==len(after['source_files'])==41
    assert before['static_source_sha256']==after['static_source_sha256'] and len(before['static_source_sha256'])==32
    relations=Counter()
    for record in [before,after]:
        assert record['source_commit']==record['actual_head_at_check']==HEAD
        assert record['profile_version']=='s2b-inference-platform/0.1.8' and record['clock_hz']==50000000 and record['visibility_parameter']==0
        for row in record['source_files']:
            data=raw(row['path']); assert digest(data)==row['sha256'] and len(data)==row['bytes']
            assert raw(row['snapshot'])==data
            if record is before:
                blob=native('git_'+Path(row['path']).name,['git','-c','core.longpaths=true','-c','maintenance.auto=false','show',HEAD+':'+row['path']])
                assert digest(blob)==row['git_blob_sha256'] and row['git_native_exit_code']==0
                if row['git_relation']=='RAW_IDENTICAL': assert blob==data
                else: assert row['git_relation']=='GIT_LF_TO_RAW_CRLF' and b'\r' not in blob and blob.replace(b'\n',b'\r\n')==data
                relations[row['git_relation']]+=1
    assert dict(relations)=={'RAW_IDENTICAL':35,'GIT_LF_TO_RAW_CRLF':6}
    spec=importlib.util.spec_from_file_location('checker',ROOT/'verification/check_s2b_inference_platform.py'); checker=importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)
    static=checker.check_static(ROOT); assert static==before['static_source_sha256']
    freeze=read(before['source_freeze']); assert bind(before['source_freeze'])==before['source_freeze_sha256']
    for p,d in freeze['frozen14'].items(): assert bind(p)==d
    profile=read('board/s2b_inference_platform.json'); assert len(profile['rtl_sources'])==18 and len(profile['source_derivation']['derived_sources'])==8
    assert profile['vivado_part']=='xc7z020clg400-2'
    mapping=read(BASE/'s8_native_mapping.json')
    assert mapping['native_job_count']==mapping['native_vds_count']==5 and mapping['generated_xdc_count']==7
    for row in mapping['files']:
        check_row(row,'saved_path'); assert raw(row['saved_path'])==raw(row['original_path'])
    infer_path=BASE/'native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl'; infer=text(infer_path)
    block=re.search(r'read_verilog -library xil_defaultlib -sv \{(.*?)\n\}',infer,re.S).group(1)
    compiled=[p.strip().removeprefix(ROOT.as_posix()+'/') for p in block.splitlines() if p.strip()]
    assert compiled==mapping['compiled_rtl'] and set(compiled)==set(profile['rtl_sources'])
    assert 'create_project -in_memory -part xc7z020clg400-2' in infer and 'set_param general.maxThreads 1' in infer
    for job in mapping['jobs']:
        assert job['raw_os_process_exit_code'] is None and job['process_tree_peak_memory_bytes'] is None
        name='wrapper_native_s8_r01' if job['run']=='synth_1' else job['run']; directory=BASE/'native_jobs'/name
        assert (directory/'.vivado.end.rst').is_file() and (directory/'__synthesis_is_complete__').is_file()
        log=text(directory/'runme.log'); assert 'synth_design completed successfully' in log
        summary=re.findall(r'(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered',log)[-1]
        assert dict(zip(['infos','warnings','critical_warnings','errors'],map(int,summary)))==job['final_diagnostics']
        elapsed=re.findall(r'synth_design: Time \(s\): cpu = [^;]+; elapsed = (\d\d):(\d\d):(\d\d) \. Memory \(MB\): peak = ([\d.]+)',log)[-1]
        h,m,s,mem=elapsed; assert int(h)*3600+int(m)*60+int(s)==job['synth_elapsed_seconds'] and float(mem)==job['reported_single_process_peak_mb']
    mcp=read(BASE/'s8_mcp_binding.json'); history=unpack(read(BASE/'mcp_closed/mcp_history.json'))
    historical={r['id']:r for r in all_dicts(history) if set(['id','command','code','elapsed','output'])<=set(r)}
    assert len(historical)==mcp['design_execute_calls']==9
    assert [r['label'] for r in mcp['paired_calls']]==['source','builder','setup','launch','wait','open_run','reports','query_xdc','close']
    for row in mcp['paired_calls']:
        assert row['native_history']==historical[row['native_history']['id']]
        check_row(row['client_record']); saved=read(BASE/'mcp_closed'/('mcp_'+row['label']+'.json'))
        assert saved['input']['command']==row['native_history']['command'] and not row['client_timeout']
        assert unpack(saved)['exit_code']==row['client_exit_code']==row['native_history']['code']
    assert mcp['products_native_exit_code']==0 and mcp['products_capture_exit_code']==1 and not mcp['products_repeated']
    products=text(BASE/'products.tcldict'); assert 'status FAIL code 0' in products and 'native_counts_before {WARNING 9' in products and 'native_counts_after {WARNING 1' in products
    assert 'PLATFORM_CAPTURE_FAIL:products' in historical[2]['output']
    assert historical[5]['command']=='wait_on_run synth_1' and historical[5]['code']==0 and historical[5]['elapsed']==251.126
    query=historical[8]['output']; assert query.count('100%')==5 and query.count('Not started')+query.count('NotStarted')>=5,query
    session=raw(BASE/'mcp_closed/immutable_session_log.log'); assert len(session)==65140 and digest(session)=='c8e5c5660203206a8df3421b0aaf4f96bd22ea91594b7d86e8d1887bb6b76a08'
    sta=read(BASE/'s8_sta_result.json'); timing=text(BASE/'timing_summary_synth.rpt'); worst=text(BASE/'timing_worst_synth.rpt')
    assert sta['status']=='FAIL_TIMING' and sta['native_exit_code']==2 and sta['design_state']=='Synthesized'
    summary=re.search(r'^\s*(-6\.749)\s+(-2135\.540)\s+(754)\s+(14886)\s+(0\.037)\s+(0\.000)\s+(0)\s+(14886)',timing,re.M); assert summary
    assert 'clk_fpga_0  {0.000 10.000}     20.000          50.000' in timing
    assert all(re.search(r'checking '+key+r' \(0\)',timing) for key in sta['check_timing'])
    assert 'Design State : Synthesized' in timing and 'Timing constraints are not met.' in timing
    for needle in ['output_group_base_reg[4]/C','result_error_latched_reg[0]/D','26.345ns  (logic 18.635ns','route 7.710ns','32  (CARRY4=16 DSP48E1=5']:
        assert needle in worst
    flat=text(BASE/'utilization_flat_synth.rpt')
    for name,value in [('Slice LUTs',17502),('Slice Registers',3972),('Block RAM Tile',32),('DSPs',146),('Register as Latch',0)]:
        assert re.search(r'\|\s*'+name+r'\*?\s*\|\s*'+str(value)+r'(?:\.0+)?\s*\|',flat),name
    xdc=text(BASE/'constraints_synth.xdc'); assert xdc.count('set_false_path')==2 and 'set_multicycle_path' not in xdc and 'set_max_delay' not in xdc
    assert 'create_clock -period 20.000 -name clk_fpga_0' in xdc and 'ACTIVE_HIGH_AUX.ACT_HI_AUX' in xdc and 'ACTIVE_LOW_EXT.ACT_LO_EXT' in xdc
    assert 'No valid timing exceptions found.' in text(BASE/'exceptions_synth.rpt')
    drc=text(BASE/'drc_synth.rpt'); methodology=text(BASE/'methodology_synth.rpt')
    assert 'Checks found: 397' in drc and 'Checks found: 712' in methodology
    report['drc_summary']=drc.split('2. REPORT DETAILS')[0][-1100:]; report['methodology_summary']=methodology.split('2. REPORT DETAILS')[0][-1200:]
    xsa=read(BASE/'s8_xsa_comparison.json')
    for k in ['old_xsa','new_xsa']: check_row(xsa[k])
    with zipfile.ZipFile(ROOT/xsa['old_xsa']['path']) as old, zipfile.ZipFile(ROOT/xsa['new_xsa']['path']) as new:
        assert old.testzip() is None and new.testzip() is None and not any(n.lower().endswith('.bit') for n in new.namelist())
        for row in xsa['members']:
            a=old.read(row['member']); b=new.read(row['member']); assert digest(a)==row['old_sha256'] and digest(b)==row['new_sha256']
            assert (a==b)==row['raw_equal'] and new.getinfo(row['member']).CRC==row['crc32']
            if 'generated_original' in row: check_row(row['generated_original']); assert raw(row['generated_original']['path'])==b
        assert [r['raw_equal'] for r in xsa['members']]==[True]*6+[False] and xsa['runtime_elf_bsp_compatibility']=='NOT_APPROVED'
    closed=read(BASE/'root_closed/owned_process_closed.json'); assert closed['exit_code']==0
    observed=json.loads(closed['output']); assert observed['expected_pid']==5236 and observed['owned_process_absent'] is True
    assert unpack(read(BASE/'root_closed/mcp_stop.json'))['status']=='success'
    for p,code in [('native_closed/s8_collection_r01.native.json',0),('root_closed/s8_seal_r01.native.json',0),('root_closed/evidence.native.json',2),('root_closed_r02/closure_r02_evidence.native.json',0),('root_closed_r02/closure_r02_inputs.native.json',2)]:
        obj=read(BASE/p); assert obj['native_exit_code']==code,(p,obj)
    classifier=read(BASE/'s8_sta_classifier.native.json'); check_row(classifier['classifier'])
    args=classifier['command'][:]; args[args.index('--result')+1]=str(WORK/'independent_sta_result.json')
    native('sta_classifier',args,2)
    own=read(WORK/'independent_sta_result.json'); assert own['timing']==sta['timing'] and own['check_timing']==sta['check_timing'] and own['status']==sta['status']
    report.update(status='PASS_FAILED_EVIDENCE_ACCURACY_ONLY',reviewed_manifest_sha256=bind(manifest_path),source_sha256=before['source_sha256'],source_relations=dict(relations),timing=sta['timing'],resources=read(BASE/'s8_collection_summary.json')['resources'],clock=sta['clock'],mcp_design_calls=9,wait_seconds=251.126,native_jobs=mapping['jobs'],elapsed_seconds=round(time.monotonic()-started,3),sampled_self_rss_bytes=max(peak,psutil.Process().memory_info().rss),peak_process_tree_rss_bytes=None)
try: main()
except Exception: report['status']='FAIL_AUDIT'; report['traceback']=traceback.format_exc()
(WORK/'audit_result_r02.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(WORK/'direct_inputs_r02.json').write_text(json.dumps(sorted(p.relative_to(ROOT).as_posix() for p in INPUTS),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'seconds':report.get('elapsed_seconds'),'error':report.get('traceback')},ensure_ascii=False))
raise SystemExit(0 if report['status'].startswith('PASS') else 1)
