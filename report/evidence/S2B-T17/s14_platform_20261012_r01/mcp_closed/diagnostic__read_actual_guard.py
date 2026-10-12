"""只读两次实际监护终态，不执行进程查询或重启，不改变冻结工具G2。"""
import hashlib
import json
from pathlib import Path
import sys

W=Path(__file__).resolve().parent
ROOT=W.parents[4]
RUN=ROOT/'tmp/2B/S2B-T17/s14_physical_launch_root_20261012_r01'
KEYS=('pid','create_time','exe','cwd','cmdline','ppid')
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def lines(path):return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]
def binding(path):return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def member(row):return {key:row.get(key) for key in (*KEYS,'lineage_mode','stoppable','rss_bytes')}
result=[]; files=[]
for label in ('r01','r02'):
    guard=RUN/('supervision_'+label)/'guard'
    paths=[guard/'guard_receipt.json',guard/'samples.jsonl',guard/'events.jsonl',RUN/('supervision_'+label)/'supervisor_receipt.json',RUN/('supervision_'+label)/'supervision.jsonl',RUN/('native_consumer_'+label)/'consumer_receipt.json',RUN/('native_consumer_'+label)/'consumption.jsonl']
    files.extend(binding(path) for path in paths)
    receipt=load(paths[0]);samples=lines(paths[1]);events=lines(paths[2]);supervisor=load(paths[3]);consumer=load(paths[5]);consumption=lines(paths[6])
    assert receipt['binding']['pid']==19192 and receipt['binding']['create_time']==1791777476.053502
    assert receipt['guard_sha256']=='1dd9a678776d92d6042fff7c326582ebb360348732f35a6dc1939410dc867b3b'
    final=samples[-1]
    entry=dict(label=label,guard_receipt={key:receipt.get(key) for key in ['status','reason','at_utc8','guard_stop','samples','sampled_peak_tree_rss_bytes','minimum_sampled_available_ram_bytes','minimum_sampled_c_disk_free_bytes','limits','stopped','retained','known_members_count','known_lineage_count']},
        last_samples=[dict(line=i+1,fields={key:value for key,value in sample.items() if key not in ['members','root_identity','binding']},members=[member(row) for row in sample.get('members',[])]) for i,sample in list(enumerate(samples))[-3:]],
        final_sample_keys=list(final),
        final_events=[dict(line=i+1,event=row if row['kind']!='LINEAGE_FIRST_VERIFIED' else dict(at_utc8=row['at_utc8'],elapsed_seconds=row['elapsed_seconds'],kind=row['kind'],first_verified_sample=row['first_verified_sample'],leaf=member(row['ancestor_chain'][0]),chain=[(m['pid'],m['create_time']) for m in row['ancestor_chain']])) for i,row in list(enumerate(events))[-12:]],
        supervisor={key:supervisor.get(key) for key in ['reason','ready','child_native_exit_code','supervisor_exit_code','elapsed_seconds','guard_identity']},
        consumer={key:consumer.get(key) for key in ['status','native_exit_code','consumer_native_exit_code','blocked_latched','elapsed_seconds','samples']},
        last_consumption=[dict(line=i+1,row=row) for i,row in list(enumerate(consumption))[-2:]])
    result.append(entry)
output=dict(status='READONLY_DIAGNOSTIC_CAPTURE_ONLY',scope='非新的G2；不审实际最终交付，未执行进程/硬件/Vivado查询',files=files,runs=result)
with (W/'actual_guard_extract.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(output,stream,ensure_ascii=False,indent=2);stream.write('\n')
for entry in result:
    print(json.dumps(entry,ensure_ascii=False))
