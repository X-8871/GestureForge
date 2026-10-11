#!/usr/bin/env python3
"""仅修复独审清单角色，保留所有已闭合证据和原G2结论。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

W=Path(__file__).resolve().parent
R=W.parents[3]
ALLOWED={'source','input','result','log','diagnostic','artifact'}
RECEIPT_SHA='6915839643e8644c89ec4fe88287c5b4c83fce27e717de2d1ed47212b0050e7b'
OLD_RAW_SHA='27c4203454c6718fa39736271d1829ddbb45b19cfc52cc66a5a719c6aca4e3d7'

def sha(path):
    """只计算原字节，不做换行或解码规范化。"""
    assert path.is_file() and not path.is_symlink(),str(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(name):
    return json.loads((W/name).read_text(encoding='utf-8'))

def save(name,obj):
    """精确新名称必须不存在，禁止覆盖已闭合文件。"""
    path=W/name;assert not path.exists(),name
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def mapped_role(item):
    """报告字段按真实语义映射到标准结果或诊断。"""
    if item['role']!='report':return item['role']
    name=Path(item['path']).name
    if name.startswith('mutation_') or name=='independent_rtl_receipt.json':return 'diagnostic'
    return 'result'

def validate_old():
    """独立核对旧绑定，确保此次只涉及元数据。"""
    assert sha(W/'receipt.json')==RECEIPT_SHA
    assert sha(W/'raw_manifest.json')==OLD_RAW_SHA
    raw=load('raw_manifest.json');receipt=load('receipt.json')
    for key in ['status','reviewed_source_commit','reviewed_manifest_sha256']:assert raw[key]==receipt[key]
    assert raw['status']=='PASS_G2_ONLY'
    assert len(raw['files'])==raw['file_count']==51
    assert len({x['path'] for x in raw['files']})==51
    for item in raw['files']:
        assert set(item)=={'path','sha256','role'}
        path=R/item['path'];assert sha(path)==item['sha256']
        assert path.stat().st_size==raw['file_bytes'][item['path']]
        assert mapped_role(item) in ALLOWED
    assert sum(raw['file_bytes'].values())==raw['total_bytes']==2983021
    return raw,receipt

def main():
    """先实际子进程核验并捕获原生码，再封闭新清单。"""
    if '--validate' in sys.argv:
        raw,receipt=validate_old()
        print(json.dumps({'status':'METADATA_BINDINGS_VALID','old_files':len(raw['files']),'changed_roles':sum(x['role']=='report' for x in raw['files']),
            'g2_unchanged':True,'rtl_rerun':False},ensure_ascii=False),flush=True)
        return 0
    for name in ['metadata_repair_stdout.log','metadata_repair_native_capture.json','raw_manifest_r02.json']:assert not (W/name).exists(),name
    command=[sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--validate']
    began=time.monotonic()
    with (W/'metadata_repair_stdout.log').open('xb') as stream:
        child=subprocess.run(command,cwd=R,stdout=stream,stderr=subprocess.STDOUT)
    cap={'command':command,'native_exit_code':int(child.returncode),'seconds':round(time.monotonic()-began,3),
        'peak_tree_rss_bytes':None,'capture_method':'subprocess.run.returncode','scope':'仅验证已有绑定并修正角色分类；不复跑RTL，不改receipt或旧原件'}
    save('metadata_repair_native_capture.json',cap)
    assert child.returncode==0,cap
    old,receipt=validate_old()
    files=[];sizes=dict(old['file_bytes']);changes=[]
    for item in old['files']:
        new=dict(item);new['role']=mapped_role(item);files.append(new)
        if new['role']!=item['role']:changes.append({'path':item['path'],'old_role':item['role'],'new_role':new['role']})
    for name,role in [('raw_manifest.json','artifact'),('metadata_repair.py','source'),('metadata_repair_stdout.log','log'),('metadata_repair_native_capture.json','result')]:
        path=W/name;rel=path.relative_to(R).as_posix()
        files.append({'path':rel,'sha256':sha(path),'role':role});sizes[rel]=path.stat().st_size
    newraw={key:receipt[key] for key in ['status','reviewed_source_commit','reviewed_manifest_sha256']}
    newraw.update({'files':files,'file_bytes':sizes,'file_count':len(files),'total_bytes':sum(sizes.values()),'self_reference':False,
        'metadata_repair_only':True,'g2_unchanged':True,'rtl_rerun':False,'role_changes':changes,
        'preserved_receipt_sha256':RECEIPT_SHA,'preserved_old_raw_sha256':OLD_RAW_SHA,
        'exclusions':old['exclusions'],'reference_scope':old['reference_scope']})
    assert len(files)==len({x['path'] for x in files})==55
    newpath=(W/'raw_manifest_r02.json').relative_to(R).as_posix()
    for item in files:
        assert set(item)=={'path','sha256','role'} and item['role'] in ALLOWED and item['path']!=newpath
        assert not any(x in item['path'].split('/') for x in ['obj_dir','checker_fixture','__pycache__'])
        assert not item['path'].lower().endswith(('.exe','.dll','.o','.a','.pyc'))
        assert sha(R/item['path'])==item['sha256'] and (R/item['path']).stat().st_size==sizes[item['path']]
    save('raw_manifest_r02.json',newraw)
    assert sha(W/'receipt.json')==RECEIPT_SHA and sha(W/'raw_manifest.json')==OLD_RAW_SHA
    print(json.dumps({'status':'PASS_G2_ONLY','raw_manifest_r02_sha256':sha(W/'raw_manifest_r02.json'),'files':len(files),
        'bytes':sum(sizes.values()),'role_changes':len(changes),'native_exit_code':cap['native_exit_code'],'STOP':True},ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
