"""ROOT亲自运行的新隔离source-after；真实HEAD与被测源码提交分列。"""
import argparse,hashlib,importlib.util,json,re,subprocess,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
import compat_pins
ROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent
COMMIT=compat_pins.SOURCE_COMMIT
CACHE=compat_pins.PNR_CACHE
COMMON=WORK/'collector.py'
COMMON_SHA='5e58d32551fa3baf8f73e755defde178fc0a5f13cb03b8c018c619bbb4e1bc43'
def compare_raw(blob,raw):
 """只接受全文件RAW相同或精确LF到RAWCRLF变换，其他差异拒绝。"""
 if blob==raw: return 'RAW_IDENTICAL'
 if b'\r\n' not in blob and blob.replace(b'\n',b'\r\n')==raw: return 'GIT_LF_TO_RAW_CRLF'
 raise ValueError('Git blob与RAW既不相同也不是精确LF到RAWCRLF')
def main():
 """缺少明确实际HEAD或新输出目录时拒绝，绝不覆盖旧PRE。"""
 parser=argparse.ArgumentParser(); parser.add_argument('--expected-head',required=True); parser.add_argument('--output-dir',required=True,type=Path)
 args=parser.parse_args(); compat_pins.require_ready(pnr=True); assert re.fullmatch('[0-9a-f]{40}',args.expected_head)
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
  command=['git','-c','core.longpaths=true','-c','maintenance.auto=false','-C',str(ROOT),*arguments]; proc=subprocess.run(command,capture_output=True,timeout=30)
  index=len(commands); prefix=native/('git_'+str(index).zfill(2))
  for suffix,data in (('stdout.log',proc.stdout),('stderr.log',proc.stderr)):
   with prefix.with_suffix('.'+suffix).open('xb') as f: f.write(data)
  commands.append(dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=proc.returncode,stdout=c.binding(prefix.with_suffix('.stdout.log')),stderr=c.binding(prefix.with_suffix('.stderr.log'))))
  save(prefix.with_suffix('.native.json'),commands[-1])
  c.require(proc.returncode==0,'真实Git命令失败，原字节保留'); return proc.stdout
 head=git('rev-parse','HEAD').decode('ascii').strip(); c.require(head==args.expected_head==COMMIT,'实际HEAD/CLI/SOURCE不同，不能伪造或跳过')
 freeze,hashes,static,profile=c.load_freeze()
 c.require(len(profile['rtl_sources'])==18 and len(profile['source_derivation']['derived_sources'])==8,'实际18/8闭包不同')
 before_path=compat_pins.SOURCE_PRE/'source_before.json'; before=c.read(before_path)
 c.require(before['source_commit']==COMMIT and {r['path']:r['sha256'] for r in before['source_files']}==hashes and before['frozen14_sha256']==freeze['frozen14'],'继承本轮before/commit/43/原14不符')
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
 record=dict(schema_version=1,status='PASS_SOURCE_AFTER_ONLY',created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),source_commit=COMMIT,actual_head_at_check=head,actual_head_after_check=end_head,source_freeze=c.rel(c.FREEZE),source_freeze_sha256=c.FREEZE_SHA,source_files=files,source_count=len(hashes),platform_static_source_count=len(static),source_sha256=hashes,static_source_sha256=static,frozen14_sha256=freeze['frozen14'],profile_version=profile['version'],clock_hz=50000000,visibility_parameter=0,inherited_before=c.binding(before_path),before_scope='已归档综合before，另由ROOT绑定PNR运行中/launch前真实源码检查；不伪称本脚本生成新before。',project_dir=str(compat_pins.PROJECT),evidence_dir=str(compat_pins.PNR_REPORT),limitations=['只有ROOT于适用关闭时点运行才是该时点source-after；源码核验不证明PNR、时序、预算或实板通过。','HEAD读取两次实际Git命令，本轮全部Git blob逐项按本轮COMMIT核对；证据HEAD不代替源码基线。'])
 record.update(source_count=len(hashes),platform_static_source_count=len(static),runtime_config=compat_pins.runtime_config_binding())
 save(out/'source_after.json',record)
 print(json.dumps(dict(status=record['status'],source_count=len(hashes),static_count=len(static),source_commit=COMMIT,actual_head_at_check=head,git_native_calls=len(commands),source_record=c.binding(out/'source_after.json')),ensure_ascii=False))
if __name__=='__main__': main()
