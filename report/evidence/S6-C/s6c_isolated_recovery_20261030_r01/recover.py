"""从固定 Git 对象恢复输入，隔离重跑并保留证据。"""
from pathlib import Path
import hashlib, importlib.util, json, os, subprocess, sys, time
SOURCE=Path(r'D:\codex-worktrees\w6')
COMMIT='44615bd3aad2a1f423af996b9af2b68cb8d20e57'
RUN='s6c_isolated_recovery_20261030_r01'
REL=f'report/evidence/S6-C/{RUN}'
OUT=SOURCE/REL
TEMP=SOURCE/'tmp/stage6/S6-C'/RUN
CLONE=TEMP/'clone'
ORIG_REL='report/evidence/S6-C/s6c_deterministic_matrix_20261030_r07'
HISTORY='report/evidence/S6-A/s6a_u6_02_recovery_20261029_r04'
PY=sys.executable
RECORD=[]
RESTORED=[]
START=time.monotonic()
ENV=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1')
ENV.pop('PYTHONPATH',None)
ENV.pop('PYTHONHOME',None)
def sha(b): return hashlib.sha256(b).hexdigest()
def save(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(data if isinstance(data,bytes) else (json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def command(name,args,cwd=SOURCE):
    begin=time.monotonic()
    p=subprocess.run([str(x) for x in args],cwd=cwd,capture_output=True,env=ENV)
    save(OUT/'raw'/f'{name}.stdout',p.stdout)
    save(OUT/'raw'/f'{name}.stderr',p.stderr)
    RECORD.append(dict(name=name,command=[str(x) for x in args],cwd=str(cwd),exit_code=p.returncode,elapsed_s=time.monotonic()-begin))
    save(OUT/'execution_record.json',RECORD)
    if p.returncode: raise RuntimeError(f'{name}: exit {p.returncode}')
    return p.stdout
def blob(path,expected=None,commit=COMMIT,repo=SOURCE):
    p=subprocess.run(['git','-c','core.longpaths=true','-C',str(repo),'cat-file','blob',f'{commit}:{path}'],capture_output=True)
    if p.returncode: raise RuntimeError(f'固定 blob 不存在: {commit}:{path}')
    if expected is not None and expected!=sha(p.stdout): raise RuntimeError(f'归档哈希不符: {path}')
    return p.stdout
def overlay(source_path,target,expected=None,layer=''):
    data=blob(source_path,expected)
    save(target,data)
    RESTORED.append(dict(source_path=source_path,target=str(target.relative_to(CLONE)),sha256=sha(data),hash_basis='commit_blob',commit=COMMIT,layer=layer))
def main():
    if CLONE.exists(): raise RuntimeError('隔离 clone 已存在，拒绝复用')
    command('clone',['git','clone','--shared','--no-checkout',SOURCE,CLONE])
    command('longpaths',['git','-C',CLONE,'config','core.longpaths','true'])
    command('checkout',['git','-C',CLONE,'checkout','--detach',COMMIT])
    if command('clean_checkout_status',['git','-C',CLONE,'status','--porcelain']): raise RuntimeError('初始 checkout 非干净')
    size=sum(p.stat().st_size for p in CLONE.rglob('*') if p.is_file())
    if size>1024**3: raise RuntimeError('超过1GiB预算')
    # 恢复次序固定为历史归档、本轮规范、运行时 STATE。
    history=json.loads(blob(f'{HISTORY}/source_bindings.json'))
    for row in history['files']: overlay(row['path'],CLONE/row['source_path'],row['sha256'],'historical_archive')
    original=CLONE/ORIG_REL
    blob(f'{ORIG_REL}/delivery_manifest.json','460060de6fa4276ddfe2759e4895783c9b1cf8a70997e8e52eb7353d86aa92d7')
    bindings=json.loads(blob(f'{ORIG_REL}/source_bindings.json'))
    for row in bindings['files']:
        blob(f"{ORIG_REL}/{row['snapshot_path']}",row['worktree_disk_sha256'])
        if row['snapshot_path'].startswith('inputs/src/'):
            overlay(f"{ORIG_REL}/{row['snapshot_path']}",CLONE/row['origin_path'],row['worktree_disk_sha256'],'r07_canonical')
    overlay(f'{ORIG_REL}/inputs/state_at_run.md',CLONE/'.codex/STATE.md',layer='r07_state')
    save(OUT/'restoration.json',dict(commit=COMMIT,checkout_bytes=size,shared_object_store=True,self_contained_git_archive=False,overlay_order=['完整固定提交','历史归档130项','r07 canonical 10项','r07 STATE'],restored=RESTORED))
    upstream=read(original/'inputs/upstream.json')
    mappings=[]
    for item in upstream['bindings']:
        if item.get('git_repo'):
            before={k:item[k] for k in ['path','git_repo','git_commit','git_relpath','sha256']}
            target=CLONE/'tmp/recovery_upstream'/item['id']/Path(item['git_relpath']).name
            save(target,blob(item['git_relpath'],item['sha256'],item['git_commit'],CLONE))
            item['path'],item['git_repo']=str(target),str(CLONE)
            mappings.append(dict(id=item['id'],before=before,after={k:item[k] for k in before}))
    save(OUT/'execution_upstream.json',upstream)
    save(OUT/'upstream_relocation.json',dict(allowed_fields=['path','git_repo'],mappings=mappings))
    checker=original/'inputs/checkers/check_stage_delivery.py'
    hashchecker=original/'inputs/checkers/check_manifest_hash_basis.py'
    for mode,manifest in [('inputs','inputs_manifest.json'),('evidence','delivery_manifest.json')]:
        command('original_'+mode,[PY,'-B',checker,'--mode',mode,'--project-root',CLONE,'--manifest',original/manifest],CLONE)
    command('original_strict',[PY,'-B',hashchecker,'--repo',CLONE,'--paths',f'{ORIG_REL}/inputs_manifest.json','--paths',f'{ORIG_REL}/delivery_manifest.json','--mode','strict','--json'],CLONE)
    command('s6b_unittest',[PY,'-B','-m','unittest','discover','-s','verification','-p','test_s6b_*.py','-v'],CLONE)
    command('s6c_unittest',[PY,'-B','-m','unittest','verification.test_s6c_receipt_boundary','-v'],CLONE)
    dest=CLONE/REL/'outputs'
    for name,cases in [('base_matrix','case_matrix.json'),('c11_matrix','c11_case.json')]:
        save(dest/name/'expected_freeze.json',(original/'outputs'/name/'expected_freeze.json').read_bytes())
        command(name,[PY,'-B',CLONE/'verification/s6b_run_cases.py','--project-root',CLONE,'--run-dir',dest/name,'--cases',original/'inputs/ref'/cases],CLONE)
    # 模块入口不运行；探针函数仅引用下方隔离路径。
    spec=importlib.util.spec_from_file_location('isolated_closeout',original/'scripts/closeout.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT,module.RUN_DIR,module.INPUTS,module.OUTPUTS=CLONE,CLONE/REL,original/'inputs',dest
    module.RUN_ID,module.HEAD='s6c_deterministic_matrix_20261030_r07','e13c5532abde97771c9e8ce3776e837f0c6816df'
    probe=module.run_boundary_probe()
    if probe['status']!='PASS': raise RuntimeError('序号探针失败')
    save(OUT/'probe_isolation.json',dict(called_function='run_boundary_probe',main_called=False,ROOT=str(module.ROOT),RUN_DIR=str(module.RUN_DIR),INPUTS=str(module.INPUTS),OUTPUTS=str(module.OUTPUTS),expected_unchanged=True))
    command('s6a_selfcheck',[PY,'-B',original/'inputs/selfcheck.py','--json',CLONE/'docs/stage6/s6a_stage6_g0_behavior_v1.json','--doc',CLONE/'docs/stage6/S6A_stage6_g0_behavior_spec_v1.md','--cases',original/'inputs/hand_cases.json','--upstream',OUT/'execution_upstream.json','--out',dest/'s6a_selfcheck.json','--project-root',CLONE,'--evidence-dir',original,'--manifest',original/'delivery_manifest.json','--state',original/'inputs/state_at_run.md'],CLONE)
    for p in dest.rglob('*'):
        if p.is_file(): save(OUT/'outputs'/p.relative_to(dest),p.read_bytes())
    save(OUT/'comparison_pending.json',dict(status='READY_FOR_COMPARISON',elapsed_s=time.monotonic()-START,subprocess_commands=len(RECORD),peak_memory='未测'))
if __name__=='__main__':
    try: main()
    except Exception as exc:
        save(OUT/'failure.json',dict(error=repr(exc),elapsed_s=time.monotonic()-START,commands=len(RECORD)))
        raise
