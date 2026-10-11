"""从已冻结r01原件生成r02最小P2修复，旧源码和独审证据只读。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re

WORK=Path(__file__).parent;ROOT=WORK.parents[3]
OLD=ROOT/'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r01'
REVIEW=ROOT/'tmp/2B/S2B-T17/independent_s12_physical_compat_review_20261012_r01'

def exact(path):
 """核验每个精确路径组件及文件类型，不接受链接。"""
 current=Path(path.anchor)
 for name in path.parts[1:]:
  assert name in {item.name for item in current.iterdir()},str(path)
  current=current/name;assert not current.is_symlink() and not current.is_junction()
 assert current.is_file();return current

def read(path,digest):
 """先核原SHA再读取，不以最终草稿SHA追认历史。"""
 raw=exact(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest,str(path);return raw

def save(name,text):
 """只创建新的UTF-8草稿或绑定，不覆盖已有产物。"""
 with (WORK/name).open('x',encoding='utf-8',newline='') as stream:stream.write(text)

def once(text,old,new):
 """精确匹配唯一来源位置，结构改变即拒绝。"""
 assert text.count(old)==1,old;return text.replace(old,new)

def add_commit_checks(text):
 """每个综合写入入口均先检查CLI与ROOT pin，再读取任何输出输入。"""
 tree=ast.parse(text);lines=text.splitlines(True)
 for node in sorted((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('source','closed_gate','collect','seal')),key=lambda n:n.lineno,reverse=True):
  ready=next(n for n in node.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='compat_pins.require_ready')
  lines.insert(ready.end_lineno,' '*ready.col_offset+'require_pinned_commit(commit)\n')
 return ''.join(lines)

def main():
 """实现仅关闭两个P2，不改变CLI、STA或预算批准条件。"""
 raw_index=read(OLD/'raw_manifest.jsonl','448666a160722be83767ba53a775695e515f3df918cef490141c6a47545d1166')
 index={row['path']:row for row in map(json.loads,raw_index.decode('utf-8').splitlines())}
 read(OLD/'compatibility_delivery_receipt.json','8985ce7655a95a48faabb273e502aa91131c1985163f6ba98e8aee336ebe779e')
 read(REVIEW/'final_review_receipt.json','ab56b991d4f9eb6563c7d06444ac35f9de57d07b8f26051b7f32af8dd9ad7d76')
 read(REVIEW/'raw_manifest.jsonl','5dfd60ebf6c7a37eff2ec2538ac3000e89b3f94abc57e04f2fd12a685bc7d727')
 names=['collector.py','impl_collector.py','source_after_check.py','native_source_after.py','native.py','compat_pins.py','compatibility_tests.py','source_after_harness_tests.py','native_checks.py']
 original={name:read(OLD/name,index[name]['sha256']).decode('utf-8') for name in names}
 new=dict(original)
 helper='''def require_pinned_commit(commit):
    """综合实际源码提交必须严格等于本轮ROOT冻结pin，不能仅比较HEAD或RAW。"""
    require(type(commit) is str and re.fullmatch(r"[0-9a-f]{40}",commit) and commit==compat_pins.SOURCE_COMMIT,"源码提交与ROOT冻结SOURCE_COMMIT不同")


'''
 new['collector.py']=once(new['collector.py'],'def load_freeze():',helper+'def load_freeze():')
 new['collector.py']=add_commit_checks(new['collector.py'])
 new['collector.py']=once(new['collector.py'],'freeze=read(FREEZE); rows=freeze["source_files"]','freeze=read(FREEZE); require_pinned_commit(freeze.get("source_commit")); rows=freeze["source_files"]')
 new['collector.py']=once(new['collector.py'],'    require([r["label"] for r in gate["design_mcp_records"]]==list(LABELS),"实际九design命令声明不同")','    require(sha(FREEZE)==FREEZE_SHA,"freeze漂移")\n    require_pinned_commit(read(FREEZE).get("source_commit"))\n    for key in ("source_before","source_after"):\n        require_pinned_commit(read(ROOT/gate[key]["path"]).get("source_commit"))\n    require([r["label"] for r in gate["design_mcp_records"]]==list(LABELS),"实际九design命令声明不同")')
 new['collector.py']=once(new['collector.py'],'    hashes={r["path"]:r["sha256"] for r in freeze["source_files"]}','    require_pinned_commit(freeze.get("source_commit"))\n    hashes={r["path"]:r["sha256"] for r in freeze["source_files"]}')
 new['impl_collector.py']=once(new['impl_collector.py'],"  c.require(timeout or client_code==item['code'],'客户端/原生返回码不同')","  c.require(timeout or (type(client_code) is type(item['code']) and client_code==item['code']),'客户端/原生返回码类型或值不同')")
 new['impl_collector.py']=once(new['impl_collector.py']," tags={r['label']:r['history'] for r in paired}"," tags={r['label']:r['history'] for r in paired}\n c.require(all(type(tags[label]['code']) is int and tags[label]['code']==0 for label in ('launch','wait','open_run','reports','close')),'五必需PNR命令原生码必须严格int0')")
 new['impl_collector.py']=once(new['impl_collector.py'],"isinstance(invalid['code'],int) and not isinstance(invalid['code'],bool)","type(invalid['code']) is int")
 new['impl_collector.py']=once(new['impl_collector.py'],"r['command'].startswith('launch_runs impl_1') and r['code']==0","r['command'].startswith('launch_runs impl_1') and type(r['code']) is int and r['code']==0")
 old_common=index['collector.py']['sha256'];new_common=hashlib.sha256(new['collector.py'].encode('utf-8')).hexdigest()
 for name in ('impl_collector.py','source_after_check.py'):new[name]=once(new[name],old_common,new_common)
 new['compatibility_tests.py']=once(new['compatibility_tests.py'],"original_ready=p.require_ready\np.require_ready=lambda pnr=False:None","original_ready=p.require_ready\noriginal_pin=p.SOURCE_COMMIT;p.SOURCE_COMMIT='0'*40\np.require_ready=lambda pnr=False:None")
 new['compatibility_tests.py']=once(new['compatibility_tests.py'],"freeze=dict(profile='s2b-inference-platform/0.1.12',source_files=","freeze=dict(source_commit='0'*40,profile='s2b-inference-platform/0.1.12',source_files=")
 new['compatibility_tests.py']=once(new['compatibility_tests.py'],"save(log,dict(fixture_test=True,not_real_result=True))","save(log,dict(fixture_test=True,not_real_result=True,source_commit=commit))")
 new['compatibility_tests.py']=once(new['compatibility_tests.py'],"old_commit=impl.COMMIT; impl.COMMIT=commit","old_commit=impl.COMMIT; impl.COMMIT=commit\n  old_freeze,old_freeze_sha=c.FREEZE,c.FREEZE_SHA\n  if not pnr:\n   c.FREEZE=base/'freeze.json';save(c.FREEZE,dict(source_commit=commit,fixture_test=True));c.FREEZE_SHA=hashlib.sha256(c.FREEZE.read_bytes()).hexdigest()")
 new['compatibility_tests.py']=once(new['compatibility_tests.py'],"finally: impl.COMMIT=old_commit","finally: impl.COMMIT=old_commit;c.FREEZE,c.FREEZE_SHA=old_freeze,old_freeze_sha")
 new['compatibility_tests.py']=once(new['compatibility_tests.py'],"expected='工程关闭失败'","expected='五必需PNR命令原生码'")
 new['compatibility_tests.py']=once(new['compatibility_tests.py'],"p.require_ready=original_ready\n\ndef recovery_negative","p.require_ready=original_ready;p.SOURCE_COMMIT=original_pin\n\ndef recovery_negative")
 new['source_after_harness_tests.py']=once(new['source_after_harness_tests.py'],"freeze=dict(profile='s2b-inference-platform/0.1.12',source_files=","freeze=dict(source_commit='0'*40,profile='s2b-inference-platform/0.1.12',source_files=")
 new['native_checks.py']=new['native_checks.py'].replace('256*1024**2','128*1024**2')
 for name,text in new.items():
  ast.parse(text);save(name,text)
  save(name+'.diff',''.join(difflib.unified_diff(original[name].splitlines(True),text.splitlines(True),fromfile='冻结r01:'+name,tofile='S12-PH-COMPAT2-R2:'+name)))
 bindings=[dict(path=str(OLD/name),sha256=index[name]['sha256'],bytes=index[name]['bytes']) for name in names]
 bindings+= [dict(path=str(path),sha256=sha) for path,sha in ((OLD/'raw_manifest.jsonl','448666a160722be83767ba53a775695e515f3df918cef490141c6a47545d1166'),(OLD/'compatibility_delivery_receipt.json','8985ce7655a95a48faabb273e502aa91131c1985163f6ba98e8aee336ebe779e'),(REVIEW/'final_review_receipt.json','ab56b991d4f9eb6563c7d06444ac35f9de57d07b8f26051b7f32af8dd9ad7d76'),(REVIEW/'raw_manifest.jsonl','5dfd60ebf6c7a37eff2ec2538ac3000e89b3f94abc57e04f2fd12a685bc7d727'))]
 save('input_bindings.json',json.dumps(bindings,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(dict(status='R02_MINIMAL_PATCH_GENERATED_BLOCKED',drafts=5,helper_unchanged=True,common_sha256=new_common),ensure_ascii=False))

if __name__=='__main__':main()
