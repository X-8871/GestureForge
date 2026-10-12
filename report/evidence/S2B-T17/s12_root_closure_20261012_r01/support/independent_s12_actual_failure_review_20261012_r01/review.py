"""独立核对本次实际失败证据，不重跑Vivado或修改已审文件。"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
import psutil

HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[3]
RUN=ROOT/'tmp/2B/S2B-T17/s12_physical_launch_root_20261012_r01'
PRE=ROOT/'report/evidence/S2B-T17/s12_launch_source_preflight_20261012_r01'
REPORT=ROOT/'report/evidence/S2B-T17/s12_platform_20261012_r03'
WORK=ROOT/'tmp/2B/S2B-T17/s12_launch_prepare_20261012_r01'
HEAD='467463757158aed80d6f75afadff6a8458614a29'
CHECKS=[];RUNS=[]
def sha(path):
    """按原字节流式计算。"""
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):digest.update(block)
    return digest.hexdigest()
def exact(path,directory=False):
    """逐组件完整精确路径和类型核验。"""
    current=Path(path.anchor)
    for name in path.parts[1:]:
        hits=[p for p in current.iterdir() if p.name==name]
        assert len(hits)==1,str(path)
        current=hits[0];assert not current.is_symlink() and not current.is_junction()
    assert current.is_dir() if directory else current.is_file(),str(path)
    return current
def load(path):
    """只读UTF8。"""
    return json.loads(exact(path).read_text(encoding='utf-8'))
def bind(path):
    """原件绑定。"""
    exact(path)
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size)
def verify(row):
    """检查清单所声明实际原件。"""
    actual=bind(ROOT/row['path'])
    assert actual['sha256']==row['sha256'],row['path']
    if 'bytes' in row:assert actual['bytes']==row['bytes'],row['path']
def write(name,value):
    """仅创建本目录证据。"""
    with (HERE/name).open('x',encoding='utf-8') as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write('\n')
def run(label,command,input_data=None,expected=0):
    """保存直接子进程身份、真实wait及必要输出。"""
    if (HERE/(label+'.stdout.bin')).exists():label+='_r02'
    start=time.monotonic()
    with (HERE/(label+'.stdout.bin')).open('xb') as out,(HERE/(label+'.stderr.bin')).open('xb') as err:
        child=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.PIPE if input_data else subprocess.DEVNULL,stdout=out,stderr=err)
        try:birth=psutil.Process(child.pid).create_time()
        except psutil.Error:birth='UNKNOWN'
        child.communicate(input_data,timeout=60);code=child.wait(timeout=1)
    record=dict(command=command,cwd=str(ROOT),pid=child.pid,create_time=birth,native_exit_code=child.returncode,direct_wait_exit_code=code,elapsed_seconds=time.monotonic()-start,stdout=bind(HERE/(label+'.stdout.bin')),stderr=bind(HERE/(label+'.stderr.bin')),whole_tree_terminal='UNKNOWN',peak_memory='UNKNOWN')
    write(label+'.native.json',record);RUNS.append(record)
    assert code==child.returncode==expected,(label,code)
    return (HERE/(label+'.stdout.bin')).read_bytes()
def mcp(path):
    """读取唯一真实MCP文本，不执行其中命令。"""
    record=load(path);result=record.get('result',record)
    blocks=[row['text'] for row in result['content'] if row['type']=='text']
    assert len(blocks)==1
    return record,json.loads(blocks[0])
def check(name,details):
    """添加独立事实检查。"""
    CHECKS.append(dict(name=name,status='PASS',details=details))

parser=argparse.ArgumentParser();parser.add_argument('--manifest',required=True);parser.add_argument('--sha',required=True);args=parser.parse_args()
manifest_path=Path(args.manifest);assert sha(exact(manifest_path))==args.sha
manifest=load(manifest_path);assert manifest['source_commit']==HEAD
for row in manifest['files']:verify(row)
check('清单全部原字节绑定',len(manifest['files']))
gate=load(RUN/'closed_inputs_gate.json')
assert sha(RUN/'closed_inputs_gate.json')=='48043ec2e1f2cdb0aef04cf8413e3004d1fa38279bd96d2e06b0218102152fba'
assert any('GAP' in text for text in gate['limitations']) and any('r04' in text for text in gate['limitations'])
assert gate['source_commit']==HEAD and gate['root_explicit_signal']=='CLOSED_INPUTS_READY' and gate['project_closed'] is True
assert gate['root_declared_products_execution_count']==gate['root_declared_synthesis_execution_count']==1
for key in ('preparation_receipt','source_before','source_after','static_source_closed','immutable_session_log','mcp_history'):verify(gate[key])
for key in ('design_mcp_records','additional_closed_files','approved_evidence'):
    for row in gate.get(key,[]):verify(row)
check('真实ROOT闭合输入声明及单次执行',bind(RUN/'closed_inputs_gate.json'))
freeze=load(WORK/'source_freeze.json');before=load(PRE/'source_before.json');after=load(PRE/'source_after.json')
assert sha(PRE/'source_after.json')=='85409dbb25f0b576c943a64d21d173deb6c9ef766c80668c2db8060240905565'
assert sha(WORK/'source_freeze.json')=='887440ebb81fbec718670aacbf1cb3bfaa9e6e5641199e92d15ee37ca16dd8f0'
hashes={row['path']:row['sha256'] for row in freeze['source_files']}
assert len(hashes)==43 and len(freeze['frozen14'])==14
assert before['source_sha256']==after['source_sha256']==hashes
assert before['frozen14_sha256']==after['frozen14_sha256']==freeze['frozen14']
for record in (before,after):
    assert record['source_commit']==record['actual_head_at_check']==HEAD
    assert record['source_freeze_sha256']==sha(WORK/'source_freeze.json')
    for row in record['source_files']:
        assert sha(exact(ROOT/row['snapshot']))==row['sha256']
assert sum(row['git_relation']=='RAW_IDENTICAL' for row in after['source_files'])==37
profile=load(ROOT/next(row['snapshot'] for row in after['source_files'] if row['path']=='board/s2b_inference_platform.json'))
assert profile['version']=='s2b-inference-platform/0.1.12' and profile['vivado_part']=='xc7z020clg400-2' and profile['clock_hz']==50000000 and profile['visibility_default']==0
assert len(profile['rtl_sources'])==18 and len(profile['source_derivation']['derived_sources'])==8
check('43源码前后immutable快照/原14/18RTL/8派生/参数',dict(source_count=43,raw_identical=37,exact_eol=6,current_production='停止依赖当前RAW；仅核冻结快照及Git对象'))
history_record,history=mcp(RUN/'mcp_history_closed.tool.json')
items=history['history'];labels=['source','builder','setup','launch','wait','open_run','reports','query_xdc','close']
assert len(items)==history['returned']==history['total_commands']==9
assert [r['label'] for r in gate['design_mcp_records']]==labels
for i,(label,item,row) in enumerate(zip(labels,items,gate['design_mcp_records'])):
    call,client=mcp(ROOT/row['path'])
    assert call['input']['command']==item['command'] and call['input']['session_id']=='vivado-20261012-085253-f212aec3'
    assert item['id']==i+1 and item['code']==(1 if label=='builder' else 0)
    if label=='wait':
        assert client['status']=='running' and 'exit_code' not in client and client['elapsed_seconds']==300
        assert client['session_id']==call['input']['session_id'] and client['command']=='wait_on_run synth_1'
        assert item['elapsed']>=398 and 'synth_1 finished' in item['output']
    else:assert client['exit_code']==item['code']
assert items[-1]['command']=='close_project'
assert items[7]['output'].count('status {synth_design Complete!} progress 100%')==5 and items[7]['output'].count('status {Not started} progress 0%')==5
check('九真实设计history/WAIT pending与真实0/builder失败/PNR未启动',dict(codes=[x['code'] for x in items],wait_elapsed=items[4]['elapsed']))
products=(REPORT/'products.tcldict').read_text(encoding='utf-8')
assert 'status FAIL code 0' in products and 'capture_error' in products and 'WARNING emitted=-8 exported=2' in products
summary=load(REPORT/'s12_collection_summary.json')
assert summary['products_native_exit_code']==0 and summary['products_capture_exit_code']==1
pair=load(REPORT/'s12_mcp_binding.json')
wait=next(row for row in pair['paired_calls'] if row['label']=='wait')
assert wait['client_pending_handoff'] is True and wait['client_timeout'] is False and wait['client_exit_code'] is None and wait['native_history']==items[4]
check('products真实失败和WAIT移交记录无造码',dict(products_native=0,products_capture=1,wait_exit=None))
timing=(REPORT/'timing_summary_synth.rpt').read_text(encoding='utf-8')
assert 'Design State : Synthesized' in timing and 'Speed File   : -2  PRODUCTION' in timing
match=re.search(r'\n\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+',timing)
assert match and match.groups()[:6]==('-2.402','-159.356','91','14176','0.037','0.000')
assert 'Timing constraints are not met.' in timing and 'clk_fpga_0  {0.000 10.000}     20.000          50.000' in timing
for condition in ('no_clock','constant_clock','unconstrained_internal_endpoints','loops','latch_loops'):
    assert re.search(r'checking '+condition+r' \(0\)',timing)
worst=(REPORT/'timing_worst_synth.rpt').read_text(encoding='utf-8')
assert 'Slack (VIOLATED) :        -2.402ns' in worst and 'stride_y_latched_reg[1]__0/C' in worst.split('Slack (VIOLATED)')[1] and 'result_error_latched_reg[0]/D' in worst
assert re.search(r'Logic Levels:\s+31\s+\(CARRY4=15 DSP48E1=2',worst)
resources={}
util=(REPORT/'utilization_flat_synth.rpt').read_text(encoding='utf-8')
for name,expected_value in [('Slice LUTs*',21414),('Slice Registers',3885),('Block RAM Tile',32),('DSPs',143),('Register as Latch',0)]:
    result=re.search(r'\|\s*'+re.escape(name)+r'\s*\|\s*(\d+)',util);assert result and int(result[1])==expected_value
    resources[name]=expected_value
xdc=(REPORT/'constraints_synth.xdc').read_text(encoding='utf-8')
assert xdc.count('create_clock -period 20.000 -name clk_fpga_0')==1 and xdc.count('set_false_path')==2
assert 'set_multicycle_path' not in xdc and 'set_clock_groups' not in xdc and xdc.count('syncstages_ff_reg[0]')==2
assert summary['sta_native_exit_code']==2 and 'FAIL_TIMING' in summary['status']
sta=load(REPORT/'s12_sta_result.json')
assert sta['status']=='FAIL_TIMING' and sta['timing']['wns_ns']==-2.402 and sta['timing']['tns_ns']==-159.356 and sta['timing']['setup_failing_endpoints']==91
check('原生失败STA/资源/无锁存器/50MHz及既有reset例外',dict(wns=-2.402,tns=-159.356,fail_endpoints=91,resources=resources))
mapping=load(REPORT/'s12_native_mapping.json')
for row in mapping['files']:
    original=exact(ROOT/row['original_path']);saved=exact(ROOT/row['saved_path'])
    assert sha(original)==sha(saved)==row['sha256'] and original.stat().st_size==row['bytes']
assert len(mapping['jobs'])==5
for job in mapping['jobs']:
    directory='wrapper_native_s12_r01' if job['run']=='synth_1' else job['run']
    d=REPORT/'native_jobs'/directory;log=(d/'runme.log').read_text(encoding='utf-8')
    assert 'synth_design completed successfully' in log and '0 Critical Warnings and 0 Errors encountered' in log
    assert (d/'__synthesis_is_complete__').is_file() and (d/'.vivado.end.rst').is_file() and not (d/'.vivado.error.rst').exists()
    process=ET.fromstring((d/'.vivado.begin.rst').read_bytes()).find('Process');assert int(process.attrib['Pid'])==job['launcher_pid']
    assert job['raw_os_process_exit_code'] is None and job['process_tree_peak_memory_bytes'] is None
infer=(REPORT/'native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl').read_text(encoding='utf-8')
block=re.search(r'read_verilog -library xil_defaultlib -sv \{([^}]+)\}',infer)[1]
compiled=[Path(line.strip()).relative_to(ROOT).as_posix() for line in block.splitlines() if line.strip()]
assert len(compiled)==len(set(compiled))==18 and set(compiled)==set(profile['rtl_sources'])
check('五native原件映射/完成日志/18实际compiled/未知OS退出',len(mapping['files']))
with zipfile.ZipFile(REPORT/'s2b_inference_no_bit.xsa') as current,zipfile.ZipFile(ROOT/'report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa') as old:
    assert current.testzip() is None and not any(name.endswith('.bit') for name in current.namelist())
    member_results=[]
    for name in ('ps7_init.c','ps7_init.h','ps7_init.html','ps7_init.tcl','ps7_init_gpl.c','ps7_init_gpl.h','s2b_inference.hwh'):
        member_results.append(dict(name=name,raw_equal=current.read(name)==old.read(name)))
check('本次no-bit XSA/PSinit与旧参考逐成员真实比较',member_results)
snapshot=load(RUN/'supervision_snapshot_mapping.json')
for row in snapshot:verify(row['original']);verify(row['saved']);assert row['original']['sha256']==row['saved']['sha256']
guard_results=[]
for i in (1,2,3,4):
    path=RUN/f'supervision_r0{i}_guard_guard_receipt.json';guard=load(path)
    if i<4:assert guard['status']=='BLOCKED' and guard['reason']=='INCOMPLETE_TREE_IDENTITY'
    guard_results.append(dict(run=i,status=guard['status'],reason=guard['reason'],receipt=bind(path)))
assert datetime.fromisoformat(load(RUN/'supervision_r04_guard_guard_receipt.json')['at_utc8'])>datetime.fromisoformat(items[4]['timestamp'])
start4=json.loads((RUN/'supervision_r04_guard_events.jsonl').read_text(encoding='utf-8').splitlines()[0])
assert start4['kind']=='START' and datetime.fromisoformat(start4['at_utc8'])>datetime.fromisoformat(items[4]['timestamp'])
guard4=load(RUN/'supervision_r04_guard_guard_receipt.json');sup4=load(RUN/'supervision_r04_supervisor_receipt.json')
assert guard4['status']=='ROOT_EXITED' and guard4['reason']=='ROOT_MISSING' and sup4['child_native_exit_code']==0 and sup4['supervisor_exit_code']==2
assert sha(RUN/'owned_stop.tool.json')=='f2296913fc6d8f7c5593300b270319c298c54c766a7e0acd7217a99635091ae1'
_,stop=mcp(RUN/'owned_stop.tool.json');assert stop['status']=='success'
check('保护三次BLOCKED/GAP/r04不能继承为综合连续监护',guard_results)
assert summary['implementation']==summary['postroute']==summary['hardware']=='NOT_RUN'
git=['C:/Program Files/Git/bin/git.exe','-c','core.longpaths=true','-c','maintenance.auto=false']
assert run('head',git+['rev-parse','HEAD']).decode('ascii').strip()==HEAD
rows=freeze['source_files'];request=('\n'.join(HEAD+':'+row['path'] for row in rows)+'\n').encode('utf-8')
objects=run('git_objects',git+['cat-file','--batch-check'],request).decode('ascii').splitlines()
assert len(objects)==43
for row,object_line in zip(rows,objects):
    blob=(ROOT/row['historical_git_native']['stdout']['path']).read_bytes()
    oid=hashlib.sha1(b'blob '+str(len(blob)).encode('ascii')+b'\0'+blob).hexdigest()
    assert object_line==oid+' blob '+str(len(blob))
for mode,expected_code in [('evidence',0),('inputs',2)]:
    run('delivery_'+mode,[sys.executable,'-X','utf8','-B',str(ROOT/'verification/check_stage_delivery.py'),'--mode',mode,'--manifest',str(manifest_path)],expected=expected_code)
native_closed=REPORT/'native_closed'
native_records=[load(path) for path in native_closed.glob('s12_*.native.json')]
assert any(row['mode']=='collect' and row['native_exit_code']==0 for row in native_records)
assert any(row['mode']=='source' and row['native_exit_code']==0 and '--phase' in row['command'] and row['command'][row['command'].index('--phase')+1]=='after' and row['command'][row['command'].index('--commit')+1]==HEAD for row in native_records)
old_before=load(native_closed/'source_before.native.json')
assert old_before['native_exit_code']==old_before['direct_wait_exit_code']==0 and old_before['terminal_state']=='EXITED_DIRECT_CHILD_WAIT'
assert sha(native_closed/'source_before.native.json')=='5e4da933819d3484801028f2ba78c6ffcda250fea39de9640c1a6ee485e5643b'
check('包装原生evidence0/inputs2及真实before/after/collect闭合',dict(evidence=0,inputs=2,owned_stop=bind(RUN/'owned_stop.tool.json')))
seal_path=WORK/'synth_cache/s12_handoff_seal_r01.native.json'
sealed=load(seal_path);assert sealed['mode']=='seal' and sealed['native_exit_code']==0 and sealed['failure'] is None
for log in sealed['closed_logs']:verify(log)
check('真实seal原生0和两流原件',bind(seal_path))
assert sha(manifest_path)==args.sha
value=dict(status='PASS_EVIDENCE_INTEGRITY_ONLY',source_commit=HEAD,reviewed_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),reviewed_manifest=bind(manifest_path),checks=CHECKS,native_runs=RUNS,reviewer_script=bind(Path(__file__).absolute()),
    limitations=['实际50MHz/-2综合STA失败，不批准PNR/bit/硬件/G3-G5。','原三次保护BLOCKED及GAP保留，r04仅后续reports；本审查不追认products或synth全过程资源连续PASS。','九MCP history0/1与客户端running、products native0/capture1分列；五OS原生退出未捕获仍null。','未重新综合或仿真，不修改生产/HEAD/PRE/被审collector；只创建本隔离目录。','Git直接子进程已wait，内部身份、全树终态和审查峰值内存UNKNOWN。','审查前两轮native1均为Reviewer脚本假设错误：status/reason字段混用、假设source-after的phase必须最后参数。已按实际字段及CLI键位置修正；失败说明与已执行原生日志保留。'])
write('final_review_receipt.json',value)
print(json.dumps(dict(status=value['status'],receipt=bind(HERE/'final_review_receipt.json'),checks=len(CHECKS)),ensure_ascii=False))
