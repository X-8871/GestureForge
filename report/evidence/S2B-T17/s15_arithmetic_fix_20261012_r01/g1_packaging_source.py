"""只对S15指定运行生成G1源码绑定与证据清单，不提交或清理。"""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import psutil
from datetime import datetime, timedelta, timezone

root=Path.cwd()
sys.path.insert(0,str(root/'verification'))
import test_s2b_conv_tile_origin_rtl as support
import test_s2b_backend_coordinates_rtl as backend

def sha(path):
    """原始字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def copy_exact_new(source, target):
    """精确核对源文件与目标父目录，新文件拒绝覆盖。"""
    source=backend.load_checker().exact_file(source)
    support.exact_directory(target.parent)
    with target.open('xb') as stream:stream.write(source.read_bytes())

def main():
    """允许失败attempt保留，只消费明确成功的每mode最终attempt。"""
    evidence=support.exact_directory(root/'report/evidence/S2B-T17/s15_arithmetic_fix_20261012_r01')
    selected={}
    for value in sys.argv[1:]:
        mode,attempt=value.rsplit('_',1)
        if mode in selected:raise ValueError('mode重复')
        selected[mode]=value
    assert set(selected)=={'static','feature','output','boundary','regressions','frozen','layer0'}
    results={}
    for mode,folder in selected.items():
        path=support.exact_directory(evidence/folder)/'validation.json'
        result=json.loads(path.read_text(encoding='utf-8'))
        assert result['status']=='PASS_S15_'+mode.upper()+'_G1_ONLY'
        assert result['source_commit']=='0700c33e6faba8861cc2e7646a8981e424a69c45'
        assert result['source_sha256_pre']==result['source_sha256_post']
        assert all(sha(root/p)==h for p,h in result['source_sha256_post'].items())
        for test in result.get('tests',[]):
            assert [row['name'] for row in test['runs']]==['compile','simulation']
            for row in test['runs']:
                assert row['native_exit_code']==row['direct_wait_exit_code']==0 and row['failure'] is None
        results[mode]=result
    bindings=backend.load_checker().check_static(root)
    assert len(bindings)==33
    tests=[test for result in results.values() for test in result.get('tests',[])]
    assert {test['name'] for test in tests}=={'feature','output','boundary','geometry','route_generic','route_frozen','layer0'}
    assert next(test for test in tests if test['name']=='feature')['coverage']['vectors']==120361
    assert next(test for test in tests if test['name']=='layer0')['coverage']['bytes']==1384448
    assert len({json.dumps(result['frozen14_sha256'],sort_keys=True) for result in results.values()})==1
    assert len({json.dumps(result['source_sha256_post'],sort_keys=True) for result in results.values()})==1
    source=results['static']['source_sha256_post']
    heavy=[{'pid':p.pid,'name':p.info['name']} for p in psutil.process_iter(['name']) if p.info['name'] and (p.info['name'].lower() in ['vivado.exe','verilator_bin.exe','cc1plus.exe'] or p.info['name'].startswith('Vtb_'))]
    assert not heavy
    diagnostic=root/'tmp/2B/S2B-T17/s15_timing_g0_20261012_r01/analysis.json'
    assert sha(diagnostic)=='8b846f0bc845bb29599b74b9900d886d8dd66d7bf7234f647847ec81562e72f7'
    copy_exact_new(diagnostic,evidence/'g0_analysis.json')
    copy_exact_new(Path(__file__),evidence/'g1_packaging_source.py')
    copy_exact_new(Path(__file__).with_name('run_native.py'),evidence/'g1_native_capture_source.py')
    copy_exact_new(Path(__file__).with_name('layer0_resource_admission.json'),evidence/'layer0_resource_admission.json')
    limitations=['仅S15功能G1；独立G2、实际50MHz综合STA、PNR、109整网、实板与G4/G5未执行。','组合fixture只注入cache=H*W关系；真实START、reset/abort、owner与公开周期由boundary和layer0验证。','内层峰值为100ms采样进程树RSS；瞬时峰及外层峰未测。','未启动Vivado/MCP/JTAG；未清理、修改冻结14或提交。']
    receipt=dict(schema_version=1,status='PASS_S15_G1_ONLY_STOP_SOURCE_WRITES',source_commit=results['static']['source_commit'],source_sha256=source,final_attempts=selected,results_sha256={mode:sha(evidence/folder/'validation.json') for mode,folder in selected.items()},tests={test['name']:test for test in tests},math_proof=results['static']['math_proof'],frozen14=results['static']['frozen14_sha256'],peak_tree_rss_bytes=max(row['peak_tree_rss_bytes'] for test in tests for row in test['runs']),elapsed_seconds=sum(result['elapsed_seconds'] for result in results.values()),heavy_processes=heavy,disk_free_bytes=shutil.disk_usage(root).free,created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),limitations=limitations)
    support.save(evidence/'final_receipt.json',receipt)
    checks=[dict(name='S15 '+mode+' 功能G1',status='PASS',command='见'+folder+'/validation.json实际command数组与native直接wait码',exit_code=0,reason='源码pre/post一致；实际检查与RTL编译/仿真原生返回码0') for mode,folder in selected.items()]
    checks.extend(dict(name=name,status='NOT_RUN',command=None,exit_code=None,reason=reason) for name,reason in [('独立Reviewer','Developer STOP等待总控独立G2'),('50MHz STA','未启动Vivado，用户3次综合预算未由Developer消费'),('实物与阶段验收','本任务为离线功能G1')])
    manifest=dict(schema_version=1,stage='2B',task_id='S2B-T17-S15',run_id=evidence.name,source_commit=receipt['source_commit'],evidence_dir=evidence.relative_to(root).as_posix(),interfaces=[],interfaces_not_applicable_reason='本次是已批准候选算术实现的严格等价改写，复用现有profile、冻结14源码与tiny416黄金；不新增或冻结物理接口。具体接口语义与freeze前提仍由G0及独立G2核对。',files=[],checks=checks,limitations=limitations,tool_versions=results['feature']['tool_versions'])
    for path in sorted(evidence.rglob('*')):
        if not path.is_file():continue
        assert not path.is_symlink()
        role='source' if 'source_snapshot' in path.parts or path.suffix=='.py' else 'log' if path.suffix in ['.log','.bin'] and path.name!='cpu_layer0_expected.bin' else 'input' if path.suffix in ['.txt','.dat','.sv'] else 'result'
        manifest['files'].append(dict(path=path.relative_to(root).as_posix(),sha256=sha(path),role=role))
    for p,h in source.items():manifest['files'].append(dict(path=p,sha256=h,role='source'))
    support.save(evidence/'delivery_manifest.json',manifest)
    print(json.dumps(dict(status=receipt['status'],receipt_sha256=sha(evidence/'final_receipt.json'),manifest_sha256=sha(evidence/'delivery_manifest.json'),files=len(manifest['files'])),ensure_ascii=False),flush=True)

if __name__=='__main__':main()
