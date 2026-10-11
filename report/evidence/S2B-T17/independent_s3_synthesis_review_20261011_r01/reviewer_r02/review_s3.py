"""独立只读核查 S3 原始失败证据，输出只限当前隔离目录。"""
import hashlib
import json
import re
import subprocess
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path.cwd().resolve()
OUT = ROOT / 'tmp/2B/S2B-T17/independent_s3_synthesis_review_20261011_r02'
E = ROOT / 'report/evidence/S2B-T17/s3_platform_20261011_r01'
P = ROOT / 'report/evidence/S2B-T17/s3_source_preflight_20261011_r01'
BASE = 'f3a0b0514c90983c41c8729b93f18d627bfc1bb5'
MANIFEST_SHA = '86d9aff8dcda7161bc5027b5906824a59748e1439ed6e87e76637d086409bcd0'
checks = []
commands = []
started = time.monotonic()

def sha(raw):
    """按原始字节计算哈希。"""
    return hashlib.sha256(raw).hexdigest()

def rel(path):
    """仅自产索引用仓库相对名称；输入路径原样读取。"""
    return Path(path).resolve().relative_to(ROOT).as_posix()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def save(name, data):
    """隔离目录中的新文件不覆盖。"""
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def check(name, condition, evidence, detail=None):
    """记录独立判断及具体原件引用，不把开发摘要视为验证结果。"""
    checks.append(dict(name=name, status='PASS' if condition else 'FAIL', evidence=evidence, detail=detail))
    if not condition:
        print('FAIL', name)

def binding(record, key='path', prefix='绑定'):
    path = Path(record[key])
    check(prefix + '目标类型:' + str(path), path.is_file() and not path.is_symlink(), str(path))
    if not path.is_file():
        return
    raw = path.read_bytes()
    check(prefix + 'RAW_SHA:' + str(path), sha(raw) == record['sha256'], str(path), dict(actual_sha256=sha(raw), bytes=len(raw)))
    if 'bytes' in record:
        check(prefix + '长度:' + str(path), len(raw) == record['bytes'], str(path), len(raw))

def run(command, stem):
    """保留精确参数、关闭后的 stdout/stderr 和实际原生退出码。"""
    tick = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True)
    (OUT / (stem + '.stdout.log')).write_bytes(result.stdout)
    (OUT / (stem + '.stderr.log')).write_bytes(result.stderr)
    meta = dict(command=command, cwd=str(ROOT), native_exit_code=result.returncode, elapsed_seconds=time.monotonic()-tick,
                stdout=rel(OUT/(stem+'.stdout.log')), stderr=rel(OUT/(stem+'.stderr.log')))
    save(stem+'.native.json', meta)
    commands.append(meta)
    return result

def main():
    """按冻结清单、原件及固定 Git blob 形成独立证据。"""
    manifest_path = E / 's3_collection_delivery_manifest_r03.json'
    check('冻结清单SHA', sha(manifest_path.read_bytes()) == MANIFEST_SHA, rel(manifest_path))
    manifest = load(manifest_path)
    check('固定源码基线', manifest['source_commit'] == BASE, rel(manifest_path))
    check('清单224项+2接口', len(manifest['files']) == 224 and len(manifest['interfaces']) == 2, rel(manifest_path))
    check('清单路径唯一', len({v['path'] for v in manifest['files']}) == 224, rel(manifest_path))
    for item in manifest['files'] + manifest['interfaces']:
        binding(item)
    originals = load(E/'s3_collection_original_inventory.json')['files']
    closed = load(E/'s3_collection_closed_inventory.json')['files']
    check('原始126项', len(originals) == 126, rel(E/'s3_collection_original_inventory.json'))
    for item in originals:
        binding(item, prefix='原126不变')
    for item in closed:
        binding(item, prefix='关闭inventory')
    actual = {rel(f) for f in E.rglob('*') if f.is_file()}
    report_bound = {v['path'] for v in manifest['files'] if v['path'].startswith(rel(E)+'/')}
    check('主证据目录150文件闭包', len(actual)==150 and actual == report_bound | {rel(manifest_path)}, rel(manifest_path),
          dict(count=len(actual), bytes=sum((ROOT/f).stat().st_size for f in actual), missing=sorted(actual-report_bound-{rel(manifest_path)})))
    check('主证据5480190字节', sum((ROOT/f).stat().st_size for f in actual)==5480190, rel(E))
    sb = load(E/'s3_collection_source_binding.json')
    check('33快照闭包', len(sb['sources'])==33, rel(E/'s3_collection_source_binding.json'))
    before = {v['path']:v for v in load(P/'source_before.json')['source_files']}
    after = {v['path']:v for v in load(P/'source_after.json')['source_files']}
    rawsame = 0
    eolsame = 0
    original14 = []
    for i, source in enumerate(sb['sources']):
        a = (ROOT/source['snapshot']).read_bytes()
        b = (ROOT/source['snapshot_after']).read_bytes()
        check('前后字节不变:'+source['path'], a==b and sha(a)==source['sha256'], [source['snapshot'], source['snapshot_after']])
        check('preflight来源绑定:'+source['path'], before[source['path']]['sha256']==sha(a)==after[source['path']]['sha256'], [rel(P/'source_before.json'),rel(P/'source_after.json')])
        command = ['git','show',BASE+':'+source['path']]
        result = run(command, 'git_source_%02d'%i)
        same = result.stdout == a
        exact_eol = not same and b'\r' not in result.stdout and result.stdout.replace(b'\n', b'\r\n')==a
        rawsame += same
        eolsame += exact_eol
        check('Git固定源:'+source['path'], result.returncode==0 and (same or exact_eol) and sha(result.stdout)==source['git_blob_sha256'], source['snapshot'], dict(command=command, native_exit_code=result.returncode, relation='RAW_IDENTICAL' if same else 'EXACT_LF_TO_CRLF'))
        if source['path'].startswith('src/s2a_') or source['path'].startswith('src/int8_'):
            prior = run(['git','show','999238284157bed77cdb3a37e3e6eea52daeefc4:'+source['path']], 'git_frozen14_%02d'%len(original14))
            check('原2A冻结源不变:'+source['path'], prior.returncode==0 and prior.stdout==result.stdout, source['snapshot'], dict(native_exit_code=prior.returncode, baseline='999238284157bed77cdb3a37e3e6eea52daeefc4'))
            original14.append(source['path'])
    check('29RAW+4精确EOL', rawsame==29 and eolsame==4, rel(E/'s3_collection_source_binding.json'), dict(rawsame=rawsame, eolsame=eolsame))
    check('原14项冻结源完整', len(original14)==14, rel(E/'s3_collection_source_binding.json'), original14)
    native = load(E/'s3_collection_native_mapping.json')
    check('44副本5jobs', len(native['files'])==44 and len(native['jobs'])==5, rel(E/'s3_collection_native_mapping.json'))
    for item in native['files']:
        binding(item, 'saved_path', '44副本')
        binding(dict(path=item['original_path'],sha256=item['sha256'],bytes=item['bytes']), prefix='44源映射')
    job_results = []
    for job in native['jobs']:
        d=ROOT/job['saved_directory']
        text=(d/'runme.log').read_text(encoding='utf-8')
        pid=int(re.search(r'^# Process ID\s*:\s*(\d+)', text,re.M).group(1))
        begin_pid=int(re.search(r'Pid="(\d+)"',(d/'.vivado.begin.rst').read_text(encoding='utf-8')).group(1))
        timing=re.search(r'synth_design: Time \(s\): cpu = [\d:]+ ; elapsed = (\d+):(\d+):(\d+) . Memory \(MB\): peak = ([\d.]+)',text)
        elapsed=int(timing[1])*3600+int(timing[2])*60+int(timing[3]); peak=float(timing[4])
        diag=re.findall(r'(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered\.',text)[-1]
        diag=dict(zip(['infos','warnings','critical_warnings','errors'], map(int,diag)))
        check('job真实完成:'+job['run'], 'synth_design completed successfully' in text and (d/'.vivado.end.rst').is_file() and (d/'__synthesis_is_complete__').is_file() and not (d/'.vivado.error.rst').exists(), rel(d/'runme.log'))
        check('job原生PID/耗时/峰/诊断:'+job['run'], pid==job['pid'] and elapsed==job['synth_design_elapsed_seconds'] and peak==job['reported_single_process_peak_mb'] and diag==job['final_diagnostics'] and job['session_start'] in text and job['session_end'] in text and job['raw_process_exit_code'] is None, rel(d/'runme.log'), dict(pid=pid, launcher_marker_pid=begin_pid, elapsed_seconds=elapsed, peak_mb=peak, diagnostics=diag, raw_os_exit_code=None))
        job_results.append(dict(run=job['run'],actual_vivado_pid=pid,launcher_marker_pid=begin_pid,synth_seconds=elapsed,single_process_peak_mb=peak,diagnostics=diag,raw_os_exit_code=None))
    infer=ROOT/native['jobs'][1]['saved_directory']/'s2b_inference_infer_0.tcl'
    script=infer.read_text(encoding='utf-8')
    rtl=re.findall(r'\s([^\s{}]+/src/[^\s{}]+\.sv)',script)
    paths=['src/'+v.split('/src/',1)[1] for v in rtl]
    check('实际18RTL唯一且快照闭包相同', len(paths)==18 and len(set(paths))==18 and set(paths)==set(native['actual_compiled_rtl_sources']) and set(paths)<=set(before), rel(infer), paths)
    wrapper=ROOT/native['jobs'][-1]['saved_directory']/'s2b_inference_wrapper.tcl'
    imported=re.findall(r'^read_verilog[^\n]+s2b_inference_wrapper\.v',wrapper.read_text(encoding='utf-8'),re.M)
    check('唯一importwrapper',len(imported)==1 and '/imports/hdl/' in imported[0],rel(wrapper),imported)
    profile=load(ROOT/before['board/s2b_inference_platform.json']['snapshot'])
    profile_text=json.dumps(profile,ensure_ascii=False)
    readback=(E/'platform_readback.tcldict').read_text(encoding='utf-8')
    check('实际profile0.1.3/visibility0/50MHz/XC-2', '0.1.3' in profile_text and 'visibility_parameter 0' in readback and 'part xc7z020clg400-2' in readback and 'CONFIG.FREQ_HZ 50000000' in readback, [before['board/s2b_inference_platform.json']['snapshot'],rel(E/'platform_readback.tcldict')])
    history_raw=load(P/'root_mcp_calls_closed.json')
    history=json.loads(history_raw['history']['content'][0]['text'])['history']
    h={item['id']:item for item in history}
    pairs=load(E/'s3_collection_mcp_history_binding.json')['paired_calls']
    check('真实history77..85九项匹配',len(pairs)==9 and [v['native_history']['id'] for v in pairs]==list(range(77,86)) and all(v['native_history']==h[v['native_history']['id']] for v in pairs),rel(P/'root_mcp_calls_closed.json'))
    for i,pair in enumerate(pairs):
        check('客户端原件绑定:'+str(77+i),pair['client_result']==history_raw['calls'][i]['result'],rel(P/'root_mcp_calls_closed.json'))
    check('builder真实1/24.498s',h[78]['code']==1 and h[78]['elapsed']==24.498,rel(P/'root_mcp_calls_closed.json'))
    client_wait=history_raw['calls'][4]['result']
    check('wait客户端timeout/原生0/351.6s',h[81]['code']==0 and h[81]['elapsed']==351.6 and client_wait.get('isError') is True and 'timed out awaiting tools/call after 300s' in client_wait['content'][0]['text'],rel(P/'root_mcp_calls_closed.json'),dict(client_native_exit_code=None,client_error_text=client_wait['content'][0]['text'],wait_native_exit_code=h[81]['code'],wait_elapsed_seconds=h[81]['elapsed']))
    check('reports真实0/31.089s',h[83]['code']==0 and h[83]['elapsed']==31.089,rel(P/'root_mcp_calls_closed.json'))
    check('五综合Complete/实现Notstarted',h[84]['output'].count('synth_design Complete!')==5 and h[84]['output'].count('Not started')==5,rel(P/'root_mcp_calls_closed.json'))
    products=(E/'products.tcldict').read_text(encoding='utf-8')
    check('products实际0/capture1/WARNING逆减保留','code 0' in products and 'status FAIL' in products and 'WARNING 9' in products and 'WARNING 1' in products,rel(E/'products.tcldict'))
    root_snap=load(E/'s3_collection_root_session_snapshot.json')
    binding(root_snap['mapping'],'saved_path','root累积封存')
    check('root395086B固定SHA仅副本','65350b2a07572f3071ce95f7eca79cfd8b13a5fa4de692415a9f3e0909a6e0f9'==root_snap['mapping']['sha256'] and root_snap['mapping']['bytes']==395086 and root_snap['source_immutable_binding'] is False,rel(E/'s3_collection_root_session_snapshot.json'))
    root_log=(ROOT/root_snap['mapping']['saved_path']).read_bytes().decode('utf-8',errors='replace')
    check('root累计峰非run tree峰','peak = 2677.445' in root_log and root_snap['process_tree_peak_memory']=='NOT_MEASURED',rel(E/'s3_collection_root_session_snapshot.json'))
    preflight=load(P/'source_before.json')['prior_attempt']
    check('预检SyntaxError记录不伪造脚本',preflight['status']=='FAILED_BEFORE_EXECUTION' and preflight['native_exit_code']==1 and 'SyntaxError' in preflight['reason'],rel(P/'source_before.json'), '原完整inline脚本未捕获；仅核对记录，未执行事实来自Python编译阶段失败语义，不能独立恢复该次完整命令。')
    timing=(E/'timing_summary_synth.rpt').read_text(encoding='utf-8')
    section=timing.split('| Design Timing Summary',1)[1].split('| Clock Summary',1)[0]
    numbers=[line.split() for line in section.splitlines() if re.fullmatch(r'\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*',line)]
    expect=['-18.745','-6349.595','806','14653','0.037','0.000','0','14653','8.870','0.000','0','4181']
    check('独立STA数值/真实FAIL_TIMING',numbers==[expect] and 'Timing constraints are not met.' in timing and '| Design State : Synthesized' in timing,rel(E/'timing_summary_synth.rpt'),numbers)
    timing_checks={key:int(value) for key,value in re.findall(r'checking (\w+) \((\d+)\)',timing)}
    check('十二时钟/约束检查零漏项',len(timing_checks)==12 and not any(timing_checks.values()),rel(E/'timing_summary_synth.rpt'),timing_checks)
    xdc=(E/'constraints_synth.xdc').read_text(encoding='utf-8')
    active=[v.strip() for v in xdc.splitlines() if v.strip() and not v.strip().startswith('#')]
    exceptions=(E/'exceptions_synth.rpt').read_text(encoding='utf-8')
    check('时钟20ns与例外范围', 'create_clock -period 20.000 -name clk_fpga_0' in xdc and len(re.findall(r'^set_false_path',xdc,re.M))==2 and 'u_conv_engine' not in xdc and 'set_multicycle_path' not in xdc and 'No valid timing exceptions found.' in exceptions,[rel(E/'constraints_synth.xdc'),rel(E/'exceptions_synth.rpt')],active)
    worst=(E/'timing_worst_synth.rpt').read_text(encoding='utf-8').split('Slack (VIOLATED)',2)[1]
    check('最差路径起止与67层39CARRY4', 'input_batch_count_latched_reg[0]/C' in worst and 'request_address_latched_reg[10]/CE' in worst and 'Logic Levels:           67  (CARRY4=39' in worst and 'Data Path Delay:        38.133ns  (logic 20.141ns' in worst and 'route 17.992ns' in worst,rel(E/'timing_worst_synth.rpt'))
    util=(E/'utilization_flat_synth.rpt').read_text(encoding='utf-8')
    resource_labels={'lut':'Slice LUTs*','ff':'Slice Registers','bram':'Block RAM Tile','dsp':'DSPs'}
    resources={key:int(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)',util,re.M).group(1)) for key,label in resource_labels.items()}
    check('综合资源32790/4017/32/160',resources==dict(lut=32790,ff=4017,bram=32,dsp=160),rel(E/'utilization_flat_synth.rpt'),resources)
    checker=E/'s3_collection_stage_checker_snapshot.py'
    checker_blob=run(['git','show',BASE+':verification/check_stage_delivery.py'],'git_stage_checker')
    check('checker固定cf640快照与Git相同',checker_blob.returncode==0 and checker_blob.stdout==checker.read_bytes() and sha(checker.read_bytes())=='cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf',rel(checker))
    for mode,expected in [('evidence',0),('inputs',2)]:
        result=run([sys.executable,'-B',str(checker),'--mode',mode,'--manifest',str(manifest_path),'--project-root',str(ROOT)],'stage_'+mode)
        check('固定checker:'+mode,result.returncode==expected,rel(OUT/('stage_'+mode+'.native.json')),dict(actual_native_exit_code=result.returncode,expected=expected, meaning='包装检查；inputs候选依赖未冻结/FAIL_TIMING阻断，不批准G2/G3/G5'))
    result=run([sys.executable,'-B',str(E/'s3_collection_classify_s3_sta.py'),'--report',str(E/'timing_summary_synth.rpt'),'--result',str(OUT/'classifier_result.json')],'sta_classifier')
    check('classifier真实原生2/FAIL_TIMING',result.returncode==2 and load(OUT/'classifier_result.json')['status']=='FAIL_TIMING',rel(OUT/'sta_classifier.native.json'))
    for name,expected in [('collector',1),('evidence_r01',2),('seal',0),('evidence_r02',0),('inputs_r02',2),('sta',2)]:
        record=load(E/('s3_collection_'+name+'.native.json'))
        code=record.get('native_exit_code',record.get('exit_code'))
        check('原失败/修复码保留:'+name,code==expected,rel(E/('s3_collection_'+name+'.native.json')),dict(code=code))
    r01=load(E/'s3_collection_delivery_manifest_r01.json')
    check('首schema未知bytes事实',any('bytes' in v for v in r01['files']) and all(set(v)<= {'path','sha256','role'} for v in manifest['files']),[rel(E/'s3_collection_delivery_manifest_r01.json'),rel(manifest_path)])
    xsas=[E/'s2b_inference_no_bit.xsa', ROOT/'report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa']
    members=[]
    for xsa in xsas:
        with zipfile.ZipFile(xsa) as z:
            members.append({name:sha(z.read(name)) for name in z.namelist()})
    psinit=[name for name in members[0] if re.search(r'ps7_init\.(?:c|h|tcl|html)$|ps7_init_gpl\.(?:c|h)$',name)]
    check('XSA六PSinit相同但HWH改变',len(psinit)==6 and all(members[0][n]==members[1].get(n) for n in psinit) and any(members[0][n]!=members[1].get(n) for n in members[0] if n.endswith('.hwh')),[rel(v) for v in xsas],psinit)
    summary=load(E/'s3_collection_summary_final.json')
    check('业务失败与未执行保留',summary['status']=='COLLECTED_FAIL_TIMING_PENDING_EVIDENCE_REVIEW' and load(E/'s3_collection_sta_result.json')['status']=='FAIL_TIMING' and all(v['status']=='NOT_RUN' for v in manifest['checks'] if v['name'] in ['postroute实现','bitstream生成','板上缓存probe','板上模型推理','109样本回归','G3实物验收']),rel(manifest_path))
    return dict(job_results=job_results,resources=resources,timing_numbers=numbers[0],timing_checks=timing_checks,source_raw_same=rawsame,source_exact_eol=eolsame,compiled_sources=paths,active_constraints=active)

try:
    findings=main()
except Exception as error:
    checks.append(dict(name='独立审查脚本异常',status='FAIL',evidence=rel(Path(__file__)),detail=repr(error)))
    traceback.print_exc()
    findings={}
failed=[v for v in checks if v['status']!='PASS']
save('independent_checks.json',dict(checks=checks,commands=commands,findings=findings))
receipt=dict(schema_version=1,role='INDEPENDENT_REVIEWER',task_id='S2B-T17-S3-SYNTH-INTEGRITY',
             status='CHANGES_REQUIRED' if failed else 'PASS_EVIDENCE_INTEGRITY',business_status='FAIL_TIMING',
             source_commit=BASE,manifest=dict(path=rel(E/'s3_collection_delivery_manifest_r03.json'),sha256=MANIFEST_SHA),
             time_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),check_count=len(checks),failed_checks=failed,
             independent_evidence=rel(OUT/'independent_checks.json'),commands=commands,findings=findings,
             gate_scope='仅S3真实失败证据完整性；不授予设计G2、STA通过、部署、G3/G4/G5。',
             restrictions=dict(source_modified=False,evidence_modified=False,git_modified=False,hardware_used=False,ross_used=False,synthesis_rerun=False),
             performance=dict(elapsed_seconds=time.monotonic()-started,reviewer_peak_memory_bytes=None,reviewer_peak_memory_status='NOT_MEASURED',reviewer_runs=2),
             prior_reviewer_attempt=dict(directory='tmp/2B/S2B-T17/independent_s3_synthesis_review_20261011_r01',native_exit_code=1,reason='Reviewer错误将timed out文本期待成TIMEOUT；1713项通过，唯一断言已按真实原件精确匹配修复，原失败不改。'),
             limitations=['当前S4工作源码未用于S3判断；33前后快照与固定Git f3使用。','原生OS子进程退出码未直接观测保持null，成功依据原生日志/markers/wait0。','root session源文件可继续追加，核查仅395086B副本SHA，不依赖源未来字节。','总wall/treepeak/Collector峰未测；9次MCP历史不是本Reviewer的新调用。','初次inlinePython完整命令未捕获，未伪造rawscript；只核对既有SyntaxError预检记录。','原有编译产生的两条reset CDC false_path原样列明；report_exceptions无有效例外，核心内部路径未漏约束。','六PSinit成员相同不批准旧BSP/ELF runtime兼容；visibility1/实现/bit/下载/G3未执行。','审查角色仅写隔离目录不提交；总控负责归档和相关提交。'])
save('receipt.json',receipt)
print(json.dumps(dict(status=receipt['status'],business_status=receipt['business_status'],checks=len(checks),failed=len(failed)),ensure_ascii=False))
raise SystemExit(0 if not failed else 1)
