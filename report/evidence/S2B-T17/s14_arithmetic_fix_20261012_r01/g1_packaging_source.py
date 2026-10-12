"""核验本次真实G1终态与源码绑定；只新增证据，不改动生产或清理缓存。"""
from pathlib import Path
import sys,json,hashlib,datetime,subprocess,psutil

repo=Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
run='s14_arithmetic_fix_20261012_r01'
evidence=repo/'report/evidence/S2B-T17'/run
cache=repo/'tmp/2B/S2B-T17'/run
source_files=['src/s2b_conv_tile_engine.sv','src/s2b_route_query.sv','board/s2b_inference_platform.json','verification/check_s2b_inference_platform.py','verification/test_s2b_conv_output_address_rtl.py','verification/test_s2b_s14_arithmetic_rtl.py']
sys.path.insert(0,str(repo/'verification'))
import test_s2b_s14_arithmetic_rtl as s14
import test_s2b_backend_coordinates_rtl as support

def sha(path):
    """真实文件原始字节SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,data):
    """拒绝覆盖任何既有报告。"""
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    """只对指定Run执行终态检查和证据清单生成。"""
    argv=sys.argv[1:]
    if len(argv)!=1 or argv[0] not in ['all_r01','all_r02','all_r03']:raise ValueError('必须给出精确最终all attempt')
    final=evidence/argv[0]
    packaging_source=evidence/'g1_packaging_source.py'
    if packaging_source.exists():raise ValueError('证据包装源码已存在，不覆盖')
    shutil_source=Path(__file__)
    packaging_source.write_bytes(shutil_source.read_bytes())
    result=json.loads((final/'validation.json').read_text(encoding='utf-8'))
    assert result['status']=='PASS_S14_ALL_G1_ONLY'
    assert result['source_sha256_pre']==result['source_sha256_post']
    checker=support.load_checker();bindings=checker.check_static(repo)
    assert all(sha(repo/p)==h for p,h in result['source_sha256_post'].items())
    assert len(bindings)==33
    expected=['feature','output','boundary','geometry','route_generic','route_frozen','layer0']
    assert [t['name'] for t in result['tests']]==expected
    for test in result['tests']:
        assert [r['name'] for r in test['runs']]==['compile','simulation']
        for row in test['runs']:
            assert row['native_exit_code']==row['direct_wait_exit_code']==0 and row['terminal_state']=='EXITED_DIRECT_CHILD_WAIT' and row['failure'] is None
    heavy=[]
    for process in psutil.process_iter(['name']):
        name=process.info.get('name') or ''
        if name.lower() in ['verilator_bin.exe','cc1plus.exe'] or name.startswith('Vtb_'):
            heavy.append(dict(pid=process.pid,name=name,birth=process.create_time()))
    assert not heavy
    gch=[]
    for path in cache.rglob('*.gch'):
        assert path.parent.name=='obj_dir' and path.is_file() and not path.is_symlink()
        gch.append(dict(path=str(path),size=path.stat().st_size,sha256=sha(path),status='REBUILDABLE_PCH_ENDED_RUN_ONLY_NOT_DELETED'))
    receipt=dict(schema_version=1,status='PASS_S14_G1_ONLY_STOP_SOURCE_WRITES',source_commit=result['source_commit'],observed_head=s14.previous.git('rev-parse','HEAD').decode().strip(),source_sha256={p:sha(repo/p) for p in source_files},final_attempt=argv[0],final_validation_sha256=sha(final/'validation.json'),static_sources=len(bindings),frozen14=result['frozen14_sha256'],tests={t['name']:dict(coverage=t.get('coverage'),pass_fields=t.get('actual_pass_fields'),runs=t['runs']) for t in result['tests']},math_proof=result['math_proof'],all_elapsed_seconds=result['elapsed_seconds'],peak_tree_rss_bytes=max(r['peak_tree_rss_bytes'] for t in result['tests'] for r in t['runs']),checks=dict(G1='PASS',G2='NOT_RUN',STA='NOT_RUN',PNR='NOT_RUN',G3='NOT_RUN',G4='NOT_RUN',G5='NOT_RUN'),failures_preserved=[p.relative_to(repo).as_posix() for p in evidence.glob('*/validation.json') if json.loads(p.read_text(encoding='utf-8'))['status']=='FAIL'],gch_rebuildable_ended_runs=gch,gch_total_bytes=sum(x['size'] for x in gch),heavy_processes=heavy,disk_free_bytes=psutil.disk_usage(str(repo)).free,created_at_utc8=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),limitations=['S14功能G1未完成独立G2或时序闭合；S13真实STA FAIL/监护BLOCKED未关闭。','整个G1没有启动Vivado、PNR或实物操作；下一次综合唯一由总控执行。','组合feature/output夹具仅登记等式条件域，公开START/PRE/owner/error/reset/abort由boundary及layer0另行实测。','子进程峰为100ms采样树RSS，瞬时峰可能未捕获；未知全部工具调用量未伪造。','子代理不提交；本轮源码保持STOP待Reviewer及总控提交。'])
    save(evidence/'final_receipt.json',receipt)
    manifest=dict(schema_version=1,stage='2B',task_id='S2B-T17-S14',run_id=run,source_commit=result['source_commit'],evidence_dir=evidence.relative_to(repo).as_posix(),interfaces=[],interfaces_not_applicable_reason='此次候选时序算术修改仅复用源码profile和既有tiny416黄金；不新冻结PS/PL物理接口，也不宣称阶段输入freeze。既有模型哈希与14冻结源码绑定在最终验证记录，正式语义审批仍由G0/G2确认。',files=[],checks=[dict(name='S14全部受影响功能G1',status='PASS',command=subprocess.list2cmdline([sys.executable,'-X','utf8','-B','verification/test_s2b_s14_arithmetic_rtl.py','--mode','all','--attempt',argv[0].split('_')[-1]]),exit_code=0,reason='实际七项单jobRTL编译及仿真原生0/直接child.wait0；pre/post源码逐字节一致。'),dict(name='S14独立Reviewer',status='NOT_RUN',command=None,exit_code=None,reason='总控后续独立G2；开发STOP。'),dict(name='S14最后一次综合时序',status='NOT_RUN',command=None,exit_code=None,reason='用户边界：总控在G1/G2完成后唯一执行；本Developer未启动。'),dict(name='实物与阶段验收',status='NOT_RUN',command=None,exit_code=None,reason='尚无S14时序或硬件验收。')],limitations=receipt['limitations'],tool_versions=result['tool_versions'])
    for path in sorted(evidence.rglob('*')):
        if not path.is_file():continue
        assert not path.is_symlink()
        role='source' if 'source_snapshot' in path.parts or path.suffix=='.py' else 'log' if path.suffix=='.log' else 'input' if path.suffix in ['.txt','.dat','.sv'] else 'result'
        manifest['files'].append(dict(path=path.relative_to(repo).as_posix(),sha256=sha(path),role=role))
    for p in source_files:manifest['files'].append(dict(path=p,sha256=sha(repo/p),role='source'))
    save(evidence/'delivery_manifest.json',manifest)
    print(json.dumps(dict(status=receipt['status'],receipt_sha256=sha(evidence/'final_receipt.json'),manifest_sha256=sha(evidence/'delivery_manifest.json'),files=len(manifest['files']),gch_files=len(gch),gch_bytes=receipt['gch_total_bytes'],disk_free_bytes=receipt['disk_free_bytes']),ensure_ascii=False))

if __name__=='__main__':main()
