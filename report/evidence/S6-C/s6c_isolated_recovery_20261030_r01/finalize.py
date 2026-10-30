"""逐字段对照恢复运行与原包，并封装检查结果。"""
import recover as r
import json, subprocess, sys, time
from pathlib import Path

def diff(a,b,path=''):
    if type(a)!=type(b): return [dict(path=path,before=a,after=b)]
    if isinstance(a,dict):
        return sum((diff(a.get(k),b.get(k),path+'/'+k) for k in sorted(a.keys()|b.keys())),[])
    if isinstance(a,list):
        if len(a)!=len(b): return [dict(path=path,before=a,after=b)]
        return sum((diff(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    return [] if a==b else [dict(path=path,before=a,after=b)]

original=r.CLONE/r.ORIG_REL
r.RECORD[:]=r.read(r.OUT/'execution_record.json')
comparisons=[]
for name in ['base_matrix/run_report.json','c11_matrix/run_report.json','sequence_boundary_probe.json','s6a_selfcheck.json']:
    differences=diff(r.read(original/'outputs'/name),r.read(r.OUT/'outputs'/name))
    comparisons.append(dict(file=name,differences=differences))
r.save(r.OUT/'comparison_draft.json',comparisons)
code="""import json, pathlib, sys
from src.stage6 import s6_core,s6_actions,s6_params,s6_receipts
from verification import s6b_run_cases
root=pathlib.Path.cwd().resolve()
mods=[s6_core,s6_actions,s6_params,s6_receipts,s6b_run_cases]
rows=[dict(module=m.__name__,file=m.__file__,inside_clone=pathlib.Path(m.__file__).resolve().is_relative_to(root)) for m in mods]
assert all(x['inside_clone'] for x in rows)
print(json.dumps(dict(modules=rows,sys_path=sys.path,pythonpath_removed=True,pythonhome_removed=True),ensure_ascii=False,indent=2))
"""
if not any(x['name']=='module_provenance' for x in r.RECORD):
    r.command('module_provenance',[sys.executable,'-B','-c',code],r.CLONE)
# 差异白名单精确到文件及 JSON 指针；不删除其他语义字段。
allowed_inputs={'/inputs/'+x for x in ['behavior_json_path','evidence_dir','hand_cases_path','human_doc_path','manifest_path','state_path']}
for row in comparisons:
    for d in row['differences']:
        p=d['path']
        if row['file'] in ['base_matrix/run_report.json','c11_matrix/run_report.json']:
            assert p=='/expected_frozen_sha256'
            assert d['after']==d['before'].replace(r.ORIG_REL,r.REL)
            d['reason']='字段实际存相对路径；只迁移输出目录，expected_freeze 原始字节哈希相同'
        elif row['file']=='s6a_selfcheck.json' and p in allowed_inputs:
            assert d['after']==d['before'].replace(str(r.SOURCE),str(r.CLONE),1)
            d['reason']='绝对输入路径按源根到隔离根的一对一映射；输入字节不变'
        elif row['file']=='s6a_selfcheck.json' and p=='/checks/7/detail':
            assert d['after']=='11 个上游绑定哈希一致（外部树按提交版本复算）'
            assert d['before']==d['after']+'；工作副本漂移（非失败，已在上游绑定中记录）：s4a_stage4_g0_fields(657ea2fb), s4a_stage4_g0_doc(75278f8d), s5a_stage5_display_g0_fields(af51a4bf)'
            d['reason']='C8 绑定提交/相对路径/SHA 未改；执行路径使用同一固定blob，不访问外部live漂移副本'
        else: raise RuntimeError(f'未批准结果差异: {row["file"]}:{p}')
log_results=[]
for name in ['base_matrix','c11_matrix']:
    for p in sorted((r.OUT/'outputs'/name/'logs').glob('*.jsonl')):
        old=original/'outputs'/name/'logs'/p.name
        assert p.read_bytes()==old.read_bytes()
        log_results.append(dict(file=str(p.relative_to(r.OUT)),sha256=r.sha(p.read_bytes()),hash_basis='worktree_disk',byte_identical=True))
summary=dict(status='PASS',scope='replay_only/software isolated filesystem recovery',comparisons=comparisons,
             raw_log_comparisons=log_results,raw_log_count=len(log_results),ignored_semantic_fields=[],
             semantic_result='全部业务结果、断言、状态、计数、17项自检结果一致；仅逐项列出的路径及C8外部漂移说明变化',
             tests=dict(s6b=44,s6b_core=34,receipt=17,base=26,duplicate_ack=1,sequence_steps=6,selfcheck=17,original_strict_entries=114,original_strict_mismatched=0),
             packaging_preflight_failures=[dict(output='raw/packaging_preflight_failed.stdout',exit_code=2,reason='首次输入清单缺input角色、循环检查NOT_RUN缺exit_code'),
                dict(output='raw/packaging_preflight_source_failed.stdout',exit_code=2,reason='首次证据清单缺source角色')],
             elapsed_s=r.read(r.OUT/'comparison_pending.json')['elapsed_s'],verification_subprocess_count=len(r.RECORD),peak_memory='未测',
             pythonpath_initial=None,pythonhome_initial=None,environment_note='首次执行时未设置PYTHONPATH；脚本现显式删除PYTHONPATH/PYTHONHOME，后续provenance使用删除后的环境',
             limitations=['共享只读源Git对象，不是自包含Git归档；业务与fixtures均从固定对象恢复',
               '本轮只证明独立文件系统恢复固定r07运行输入，孤立HEAD不是完整运行规格',
               '6-D真实集成BLOCKED；P/T6-A03 NOT_RUN；6-E实物/G3及阶段G4/G5未通过',
               '未调用硬件/Vivado/FPS流程；独立Reviewer未执行，不声明G2 PASS',
               'Git Bash启动E_ACCESSDENIED，改用PowerShell启动UTF-8 Python；恢复脚本失败保留clone且不自动删除'])
r.save(r.OUT/'comparison.json',summary)
# 先创建最终文件集合，再用快照检查器依次刷新哈希并检查，禁止伪造 stdout。
checker=original/'inputs/checkers/check_stage_delivery.py'
hashchecker=original/'inputs/checkers/check_manifest_hash_basis.py'
commands=[('new_inputs',[sys.executable,'-B',checker,'--mode','inputs','--project-root',r.SOURCE,'--manifest',r.OUT/'inputs_manifest.json']),
          ('new_evidence',[sys.executable,'-B',checker,'--mode','evidence','--project-root',r.SOURCE,'--manifest',r.OUT/'delivery_manifest.json']),
          ('new_strict',[sys.executable,'-B',hashchecker,'--repo',r.SOURCE,'--paths',r.REL+'/inputs_manifest.json','--paths',r.REL+'/delivery_manifest.json','--mode','strict','--json'])]
for name,args in commands:
    for ext in ['stdout','stderr']:
        p=r.OUT/'raw'/f'{name}.{ext}'
        if not p.exists(): r.save(p,b'')
checks=[dict(name=x['name'],status='PASS',command=subprocess.list2cmdline(x['command']),exit_code=x['exit_code']) for x in r.RECORD]
checks += [dict(name='序号边界探针',status='PASS',command='recover.py: isolated run_boundary_probe()',exit_code=0),
           dict(name='逐字段与27日志比较',status='PASS',command='finalize.py: exact JSON pointer comparison and byte comparison',exit_code=0)]
newchecks=[dict(name=n,status='NOT_RUN',command=None,exit_code=None,reason='尚未执行本轮包装检查') for n,a in commands]
def refresh():
    files=[]
    for p in sorted(r.OUT.rglob('*')):
        if p.is_file() and p.name not in ['delivery_manifest.json','inputs_manifest.json'] and '__pycache__' not in p.parts:
            files.append(dict(path=p.relative_to(r.SOURCE).as_posix(),sha256=r.sha(p.read_bytes()),role='source' if p.suffix=='.py' else 'result',keep_reason='隔离恢复运行与对照的可复核证据',hash_basis='worktree_disk'))
    header=dict(schema_version=1,stage='6',task_id='S6-C',run_id=r.RUN,source_commit=r.COMMIT,evidence_dir=r.REL,
                interfaces=[],interfaces_not_applicable_reason='软件隔离恢复r07，不改变上游接口且不执行真实集成',hash_basis='worktree_disk',
                checks=checks+newchecks,limitations=summary['limitations'])
    inputfiles=[dict(x,role='input') for x in files if x['path'].endswith(('recover.py','finalize.py','execution_upstream.json','upstream_relocation.json','restoration.json'))]
    r.save(r.OUT/'inputs_manifest.json',dict(header,checks=checks,files=inputfiles))
    files.append(dict(path=(r.OUT/'inputs_manifest.json').relative_to(r.SOURCE).as_posix(),sha256=r.sha((r.OUT/'inputs_manifest.json').read_bytes()),role='input',keep_reason='恢复输入索引',hash_basis='worktree_disk'))
    r.save(r.OUT/'delivery_manifest.json',dict(header,files=files,tool_versions=dict(python=sys.version,checker_sha256=r.sha(checker.read_bytes()),hashchecker_sha256=r.sha(hashchecker.read_bytes()))))
for iteration in range(1,5):
    stable=True
    for index,(name,args) in enumerate(commands):
        refresh()
        before=[(r.OUT/'raw'/f'{name}.{ext}').read_bytes() for ext in ['stdout','stderr']]
        p=subprocess.run([str(x) for x in args],cwd=r.SOURCE,capture_output=True,env=r.ENV)
        after=[p.stdout,p.stderr]
        for ext,data in zip(['stdout','stderr'],after): r.save(r.OUT/'raw'/f'{name}.{ext}',data)
        newchecks[index]=dict(name=name,status='PASS' if p.returncode==0 else 'FAIL',command=subprocess.list2cmdline([str(x) for x in args]),exit_code=p.returncode)
        if p.returncode: raise RuntimeError(f'{name}: {p.returncode}: {p.stdout.decode("utf-8","replace")}')
        stable=stable and before==after
    if stable: break
else: raise RuntimeError('包装检查输出四轮内未收敛')
print(json.dumps(dict(status='PASS',package_rounds=iteration,verification_subprocesses=len(r.RECORD),packaging_subprocesses=iteration*3,manifest_sha256=r.sha((r.OUT/'delivery_manifest.json').read_bytes()),file_count=len(list(r.OUT.rglob('*'))))),flush=True)
