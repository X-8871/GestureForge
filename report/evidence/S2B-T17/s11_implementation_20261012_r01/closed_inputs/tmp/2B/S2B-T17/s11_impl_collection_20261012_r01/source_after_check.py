"""ROOT亲自运行的新隔离source-after；真实HEAD与被测源码提交分列。"""
import argparse,hashlib,importlib.util,json,re,subprocess,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
ROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent
COMMIT='a710ec431474841a81912a6055f861e811a151e3'
CACHE=ROOT/'tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01'
COMMON=ROOT/'tmp/2B/S2B-T17/s11_collection_20261012_r01/collector.py'
COMMON_SHA='8bb59a7485a2f03adb6d71d5923913d724952077a961af208fff18f76b8c6cc9'
def compare_raw(blob,raw):
 """只接受全文件RAW相同或精确LF到RAWCRLF变换，其他差异拒绝。"""
 if blob==raw: return 'RAW_IDENTICAL'
 if b'\r\n' not in blob and blob.replace(b'\n',b'\r\n')==raw: return 'GIT_LF_TO_RAW_CRLF'
 raise ValueError('Git blob与RAW既不相同也不是精确LF到RAWCRLF')
def main():
 """缺少明确实际HEAD或新输出目录时拒绝，绝不覆盖旧PRE。"""
 parser=argparse.ArgumentParser(); parser.add_argument('--expected-head',required=True); parser.add_argument('--output-dir',required=True,type=Path)
 args=parser.parse_args(); assert re.fullmatch('[0-9a-f]{40}',args.expected_head)
 assert hashlib.sha256(COMMON.read_bytes()).hexdigest()==COMMON_SHA
 spec=importlib.util.spec_from_file_location('common',COMMON); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
 out=args.output_dir; c.require(out.is_absolute() and out.parent.parts==CACHE.parts and re.fullmatch('source_after_check_r[0-9]+',out.name),'输出必须为本PNR ROOTcache的新source-after目录')
 c.exact(out.parent,'directory')
 if out.exists():
  c.exact(out,'directory'); c.require({p.name for p in out.iterdir()}<= {'stdout.log','stderr.log'},'输出已存在或非原生包装新目录')
 else: out.mkdir()
 def save(path,obj):
  c.require(path.is_relative_to(out) and not path.exists(),'source-after不覆盖输出')
  with path.open('x',encoding='utf-8',newline='\n') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
 native=out/'git_native'; native.mkdir(); commands=[]
 def git(*arguments):
  command=['git','-C',str(ROOT),*arguments]; proc=subprocess.run(command,capture_output=True,timeout=30)
  index=len(commands); prefix=native/('git_'+str(index).zfill(2))
  for suffix,data in (('stdout.log',proc.stdout),('stderr.log',proc.stderr)):
   with prefix.with_suffix('.'+suffix).open('xb') as f: f.write(data)
  commands.append(dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=proc.returncode,stdout=c.binding(prefix.with_suffix('.stdout.log')),stderr=c.binding(prefix.with_suffix('.stderr.log'))))
  save(prefix.with_suffix('.native.json'),commands[-1])
  c.require(proc.returncode==0,'真实Git命令失败，原字节保留'); return proc.stdout
 head=git('rev-parse','HEAD').decode('ascii').strip(); c.require(head==args.expected_head,'实际HEAD不同，不能伪造或跳过')
 freeze,hashes,static,profile=c.load_freeze()
 c.require(len(hashes)==43 and len(static)==33 and len(profile['rtl_sources'])==18 and len(profile['source_derivation']['derived_sources'])==8,'实际43/33/18/8闭包不同')
 before_path=ROOT/'report/evidence/S2B-T17/s11_source_preflight_20261012_r01/source_before.json'; before=c.read(before_path)
 c.require(before['source_commit']==COMMIT and {r['path']:r['sha256'] for r in before['source_files']}==hashes and before['frozen14_sha256']==freeze['frozen14'],'继承before/a710/43/原14不符')
 snapshots=out/'source_snapshot_after'; snapshots.mkdir(); files=[]
 for name,expected in hashes.items():
  raw=c.exact(ROOT/name).read_bytes(); c.require(hashlib.sha256(raw).hexdigest()==expected,'本轮RAW漂移：'+name)
  blob=git('show',COMMIT+':'+name); relation=compare_raw(blob,raw)
  dest=snapshots/name; dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as f: f.write(raw)
  files.append(dict(path=name,sha256=expected,bytes=len(raw),snapshot=c.rel(dest),git_blob_sha256=hashlib.sha256(blob).hexdigest(),git_relation=relation,git_native_command=commands[-1]['command'],git_native_exit_code=commands[-1]['native_exit_code']))
 for name,expected in hashes.items(): c.require(c.sha(ROOT/name)==expected,'核验期间RAW变化：'+name)
 end_head=git('rev-parse','HEAD').decode('ascii').strip(); c.require(end_head==head,'核验期间真实HEAD变化')
 save(out/'git_commands.json',dict(commands=commands))
 record=dict(schema_version=1,status='PASS_SOURCE_AFTER_ONLY',created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),source_commit=COMMIT,actual_head_at_check=head,actual_head_after_check=end_head,source_freeze=c.rel(c.FREEZE),source_freeze_sha256=c.FREEZE_SHA,source_files=files,source_count=43,platform_static_source_count=33,source_sha256=hashes,static_source_sha256=static,frozen14_sha256=freeze['frozen14'],profile_version=profile['version'],clock_hz=50000000,visibility_parameter=0,inherited_before=c.binding(before_path),before_scope='已归档综合before，另由ROOT绑定PNR运行中/launch前真实源码检查；不伪称本脚本生成新before。',project_dir=str(ROOT/'tmp/2B/S2B-T17/s11p1'),evidence_dir=str(ROOT/'report/evidence/S2B-T17/s11_implementation_20261012_r01'),limitations=['只有ROOT于适用关闭时点运行才是该时点source-after；源码核验不证明PNR、时序、预算或实板通过。','HEAD读取两次实际Git命令，43份Git blob逐项按a710核对；证据HEAD不代替源码基线。'])
 save(out/'source_after.json',record)
 print(json.dumps(dict(status=record['status'],source_count=43,static_count=33,source_commit=COMMIT,actual_head_at_check=head,git_native_calls=len(commands),source_record=c.binding(out/'source_after.json')),ensure_ascii=False))
if __name__=='__main__': main()
