"""只读补充作者初始基线、当前HEAD与精确工具字节来源，不改旧PASS或索引。"""
import hashlib,json,subprocess,sys,time
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).parents[4];W=Path(__file__).parent;D=ROOT/'tmp/2B/S2B-T17/s12_resource_guard_20261012_r02';OLD=ROOT/'tmp/2B/S2B-T17/independent_s12_resource_guard_r04_review_20261012_r01';GIT=Path(r'C:\Program Files\Git\ucrt64\bin\git.exe');started=time.monotonic()
assert GIT.is_file() and not GIT.is_symlink()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
old=read(OLD/'final_review_receipt.json');author=read(D/'tool_receipt_r04_r02.json')
assert sha(OLD/'final_review_receipt.json')=='f528d50934d7e5c4c4cadbc0ae6db2d9708806d992cc222499de06e3ad83d350'
assert sha(OLD/'raw_manifest.jsonl')=='9bf798f9a8eb72cff4b32ec9b3ffe6bddc44ea4f87d0dd2d9647f43e2e3cdf34'
assert sha(D/'tool_receipt_r04_r02.json')=='36aec3823a06e410782e39d6dec7619431c85a7b1502fa21f0a57e98c4f5d1de'
commands=[]
def git(name,args):
    command=[str(GIT),'-C',str(ROOT),*args];t=time.monotonic();p=subprocess.run(command,capture_output=True,cwd=ROOT)
    for suffix,data in [('stdout.log',p.stdout),('stderr.log',p.stderr)]:
        with (W/(name+'.'+suffix)).open('xb') as f:f.write(data)
    native=dict(command=command,native_exit_code=p.returncode,elapsed_seconds=time.monotonic()-t)
    with (W/(name+'.native.json')).open('x',encoding='utf-8') as f:json.dump(native,f,ensure_ascii=False,indent=2)
    commands.append(native);assert p.returncode==0
    return p.stdout.decode('utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat();head=git('head_before',['rev-parse','HEAD']).strip()
root_commit='891f750045ce141a8152c96025da559ff1d3a321';baseline=author['source_commit_at_initial']
commit=git('root_commit_details',['show','--format=fuller','--name-status','--no-renames',root_commit])
names=git('initial_to_root_paths',['diff','--name-only',baseline,root_commit,'--']).splitlines()
relative_tools=[(D/n).relative_to(ROOT).as_posix() for n in ('guard.py','supervisor.py')]
tracked=git('tools_tracked_at_root',['ls-tree','-r','--name-only',root_commit,'--',*relative_tools]).splitlines()
head_after=git('head_after',['rev-parse','HEAD']).strip();assert head==head_after
hashes={p:sha(ROOT/p) for p in relative_tools};assert hashes==old['reviewed_source_hashes']
assert baseline==old['source_commit']=='932051cdacdf02f729d6a7554b07118d05e96aa4'
assert not tracked
assert not any(p.startswith(('src/','ip/','verification/','scripts/')) for p in names)
supplement=dict(status='PROVENANCE_CORRECTED_TOOL_PASS_SCOPE_UNCHANGED',reviewer_stop='STOP_NO_FURTHER_WRITES',original_receipt=dict(path=(OLD/'final_review_receipt.json').relative_to(ROOT).as_posix(),sha256=sha(OLD/'final_review_receipt.json')),original_raw=dict(path=(OLD/'raw_manifest.jsonl').relative_to(ROOT).as_posix(),sha256=sha(OLD/'raw_manifest.jsonl'),rows=35),original_source_commit_field=old['source_commit'],author_initial_git_baseline=baseline,author_field_origin='tool_receipt_r04_r02.json.source_commit_at_initial；独审将该初始值转录为未限定的source_commit字段。',accuracy_correction='原source_commit不是实际审查HEAD的独立观测记录；若按实际审查HEAD解读则不准确。现补充分列作者初始基线与当前观测，并保留原记录。',current_head_observed=head,current_head_observation_at_utc8=at,current_head_after_readonly_checks=head_after,historical_review_head_captured_at_time=None,historical_review_head_claimed_by_root=root_commit,historical_review_head_evidence='ROOT本次消息称工具审查前已提交到891f750；本补充未在过去实时捕获HEAD，当前rev-parse不能补造过去观测。',root_reported_commit_verified_as_git_object=root_commit,initial_to_root_changed_paths=names,tools_tracked_in_root_commit=tracked,reviewed_source_hashes=hashes,diff_does_not_change_tool_basis=['候选guard/supervisor不在891f750的Git树；它们由实际文件SHA冻结，而非source_commit隐式绑定。','932051→891f750的实际Git差异未修改src/ip/verification/scripts或被审tmp工具路径；正式证据/STATE/attrs变化单列原生命令日志。','当前被审两文件SHA与原PASS的reviewed_source_hashes逐项相同，原PASS与35行原清单SHA保持。'],readonly_git_commands=commands,elapsed_seconds=time.monotonic()-started,peak_memory_bytes=None,limitations=['不把当前HEAD观测冒充过去实时审查HEAD。','仅补正provenance字段的含义，未重复mock/canary，不修改候选/正式证据/Git/STATE。','工具G2范围仍有效；真实heavy监督/预算/STA/G3/G5仍须另判。'])
with (W/'provenance_supplement.json').open('x',encoding='utf-8') as f:json.dump(supplement,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(status=supplement['status'],current_head=head,author_initial_git_baseline=baseline,git_native_codes=[x['native_exit_code'] for x in commands],elapsed_seconds=supplement['elapsed_seconds']),ensure_ascii=False))
