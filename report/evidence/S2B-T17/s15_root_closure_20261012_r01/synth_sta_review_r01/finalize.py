"""最终冻结源码冻结表一致性、实际直接wait以及独立原件索引。"""
from pathlib import Path
import json,hashlib,sys,subprocess,time
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
F=ROOT/'report/evidence/S2B-T17/s15_platform_20261012_r01'
def sha(path):
    """计算真实原件SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    """读取UTF8 JSON。"""
    return json.loads(path.read_text(encoding='utf-8'))
def save(name,value):
    """独占目录创建新原件。"""
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
receipt=read(HERE/'attempt_r03/final_review_receipt.json');assert receipt['status']=='PASS_SYNTHESIS_STA_ONLY'
assert receipt['stop'] and sha(HERE/'review.py')==receipt['reviewer_sha256']
native=read(HERE/'review_driver_r03.native.json')
assert native['native_exit_code']==native['direct_wait_exit_code']==0 and native['terminal_state']=='EXITED_DIRECT_CHILD_WAIT'
for phase in ('stdout','stderr'):assert sha(ROOT/native[phase]['path'])==native[phase]['sha256']
before=read(F/'mcp_closed/source_before.json');after=read(F/'mcp_closed/source_after.json');freeze=read(F/'native_capture_closed/source_freeze_r01.json')
expected={row['path']:row['sha256'] for row in freeze['source_files']}
assert len(expected)==46 and expected==before['source_sha256']==after['source_sha256']
for path,digest in expected.items():assert sha(ROOT/path)==digest
r01=read(F/'s15_root_delivery_manifest_r01.json');r03=read(F/'s15_root_delivery_manifest_r03.json')
old={row['path']:row['sha256'] for row in r01['files']};new={row['path']:row['sha256'] for row in r03['files']}
assert len(old)==424 and len(new)==438 and all(new[path]==digest for path,digest in old.items())
assert sha(F/'s15_root_delivery_manifest_r03.json')=='02e5d0d6da4ac331e0c0686d710c58d27944fe60dcd8b474296cbb6a31e88824'
for path,digest in new.items():assert sha(ROOT/path)==digest
command=['git','-c','core.longpaths=true','-c','maintenance.auto=false','rev-parse','HEAD']
child=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=child.communicate(timeout=30);code=child.wait(timeout=30)
assert code==0 and out.decode().strip()==receipt['source_commit']
(HERE/'final_git.stdout.bin').write_bytes(out);(HERE/'final_git.stderr.bin').write_bytes(err)
save('final_git.native.json',dict(command=command,native_exit_code=code,direct_wait_returned=True,stdout_sha256=sha(HERE/'final_git.stdout.bin'),stderr_sha256=sha(HERE/'final_git.stderr.bin')))
save('diagnostic_failures.json',dict(facts=[
 dict(tool_chunk_id='bbf986',exit_code=0,scope='只读结构诊断；大型输出截断不构成原报告缺失'),
 dict(tool_chunk_id='7ba84c',exit_code=1,reason='诊断details误选历史result封装，已按两种真实封装修复，保存失败源码'),
 dict(tool_chunk_id='d09ab0',exit_code=1,reason='本隔离inspect.py遮蔽stdlib inspect，NumPy导入失败；未启动审查child，改名保留源码'),
 dict(native='review_driver.native.json',exit_code=1,reason='独立包装r02发现随后写回三检查日志未登记，r03固定补齐438且独立CHECKS_OK0'),
 dict(native='review_driver_r02.native.json',exit_code=1,reason='审查driver错把run标签synth_1当已归档目录名；原mapping已明确wrapper_native_s15_r01，r03按精确saved_path读取通过')],
 limitations=['早期只读诊断宿主输出未在本目录另存原生两流；记录实际tool chunk与host码，不能称已捕获直接childwait。','三次实际审查driver直接wait及两流已完整保存；失败审查driver真实源码保留。']))
receipt['final_source_freeze_all46_equal']=True;receipt['r01_original424_preserved_in_r03']=True
receipt['direct_review_driver_native']=native;receipt['reviewed5source']=[dict(path=path,sha256=expected[path]) for path in ('src/s2b_conv_tile_engine.sv','board/s2b_inference_platform.json','verification/check_s2b_inference_platform.py','verification/test_s2b_conv_feature_address_rtl.py','verification/test_s2b_s15_arithmetic_rtl.py')]
receipt['failure_history']='原包装r01=2/r02当时0后再核2均保留，r03隔离输出实际0；审查自身结构、导入、归档目录假设错误原件保留，未改变被审报告。'
receipt['stop']=True;receipt['created_at_utc8']=datetime.now(timezone(timedelta(hours=8))).isoformat()
save('final_stop_receipt.json',receipt)
files=[]
for path in sorted(HERE.rglob('*')):
    if path.is_file():files.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),size_bytes=path.stat().st_size))
index=dict(schema_version=1,status=receipt['status'],stop=True,source_commit=receipt['source_commit'],production_commit=receipt['production_commit'],
 final_stop_receipt=dict(path=(HERE/'final_stop_receipt.json').relative_to(ROOT).as_posix(),sha256=sha(HERE/'final_stop_receipt.json')),files=files,
 reviewed_manifest=dict(path=(F/'s15_root_delivery_manifest_r03.json').relative_to(ROOT).as_posix(),sha256=sha(F/'s15_root_delivery_manifest_r03.json'),binding_count=438),
 limitations=receipt['limitations']+['索引只列本次独立审查目录真原件；被审438原件按固定标准清单引用，未复制或改变。','本目录无重型编译缓存，所有文件列入索引；索引自身用外部SHA绑定。','源码、快照、Git原始stdout及两种明确字节关系已核验；未调用尚在修补的SOURCE fallback工具。'])
save('original_file_index.json',index)
print(json.dumps(dict(status=index['status'],stop=True,files=len(files),bytes=sum(row['size_bytes'] for row in files),receipt_sha256=sha(HERE/'final_stop_receipt.json'),index_sha256=sha(HERE/'original_file_index.json')),ensure_ascii=True),flush=True)
