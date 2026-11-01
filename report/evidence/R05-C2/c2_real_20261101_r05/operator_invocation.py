from pathlib import Path
import sys,os,threading,subprocess,time,uuid,json,re,hashlib,datetime
b=Path('D:/codex-worktrees/w6/legacy_codex_20261031');r=b.parent/'report/evidence/R05-C2/c2_real_20261101_r05';old=r.with_name('c2_real_20261101_r04')
assert not r.exists();r.mkdir();(r/'artifacts').mkdir()
for n in ['init','program','start','readback','close']:
 (r/n).mkdir();s=(old/n/(n+'.tcl')).read_text(encoding='utf-8').replace(old.as_posix(),r.as_posix())
 with (r/n/(n+'.tcl')).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
with (r/'artifacts/c2_real_chainb_display.elf').open('xb') as f:f.write((old/'artifacts/c2_real_chainb_display.elf').read_bytes())
sys.path[:0]=[str(b/'m3_w02'),str(b/'r03'),str(b/'c2_board'),'D:/tmp/lead/p3b_smoke_20261030_r01']
import owner_guard as g,hold_hw_server as h,job_launcher as j,m3_pair as m,board_state as bs
from uart_native import Uart
assert Path(h.__file__).resolve()==(b/'m3_w02/hold_hw_server.py').resolve()
assert bs.por_precondition()=='satisfied'
g.assert_port_free(3121);a=None;t=None;u=None;sr={};events=[];raw=bytearray();ok=False;touched=False;end=datetime.datetime(2026,11,1,1,0,tzinfo=g.UTC8)
def save(n,v):
 with (r/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def own():
 p=a.pids(a.job);q=g.query_listener_pids(3121)
 if not t.is_alive() or not q or not set(q)<=set(p):raise RuntimeError('owner failed')
 return {'job':a.job_name,'pids':p,'listeners':q}
def step(n,mark,timeout):
 pre=own();v=m._run_xsdb([str(m.OFFICIAL_XSDB),'-no-ini',str(r/n/(n+'.tcl'))],timeout);s=(v.stdout+v.stderr).decode('utf-8','replace');passed=v.returncode==0 and mark.encode() in v.stdout and not m.ERROR_RE.search(s);e={'step':n,'process_exit_code':v.returncode,'semantic_exit_code':0 if passed else 2,'pre':pre,'post':own(),'at':datetime.datetime.now(g.UTC8).isoformat()};save(n+'/result.json',e);events.append(e);print(n,passed,flush=True)
 if not passed:raise RuntimeError(s)
 return s
try:
 u=Uart();(r/'server').mkdir();a=h.OwnedJob('Local\\M3_OWNER_'+uuid.uuid4().hex);cmd=Path(os.environ.get('SystemRoot','C:/Windows'))/'System32/cmd.exe';bat=Path('D:/Xilinx/2026.1/Vivado/bin/hw_server.bat');line=subprocess.list2cmdline([str(cmd),'/d','/q','/v:off','/s','/c'])+' '+f'""{bat}" -p tcp::3121"';budget=min(300,int((end-datetime.datetime.now(g.UTC8)).total_seconds())-20)
 def worker():
  try:sr.update(j.run_job(str(cmd),line,r/'server',j.offline_environment(r/'server'),r/'server/job',budget,api=a))
  except Exception as e:sr.update(error=repr(e),cleanup_confirmed=False)
 t=threading.Thread(target=worker);t.start();assert a.ready.wait(10)
 for k in range(30):
  try:own();break
  except RuntimeError:time.sleep(.1)
 else:raise RuntimeError('server not ready')
 save('server_start.json',{'owner':own(),'budget':budget,'deadline':end.isoformat()});touched=True
 step('init','M3_SINGLE_INIT_COMPLETED',45)
 print(step('program','C2_PROGRAMMED_APP_NOT_STARTED',120),flush=True)
 wb=(r/'weights_readback.bin').read_bytes();wh=hashlib.sha256(wb).hexdigest();assert len(wb)==5903100 and wh=='f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39';save('weights_verified.json',{'bytes':len(wb),'sha256':wh,'status':'PASS','before_con':True})
 if (end-datetime.datetime.now(g.UTC8)).total_seconds()<105:raise RuntimeError('deadline insufficient')
 step('start','C2_APP_STARTED',15);print('REAL_INFERENCE_RUNNING',flush=True);clock=time.monotonic()
 while time.monotonic()-clock<95 and (end-datetime.datetime.now(g.UTC8)).total_seconds()>30:
  chunk=u.read();raw.extend(chunk)
  if b'CHAINB STEP=' in chunk or b'C2 PUBLISH' in chunk or b'C2 DISPLAY' in chunk:print(chunk.decode('utf-8','replace')[-1200:],flush=True)
  if re.search(rb'CHAINB RESULT=(\{[^\r\n]+\})\r*\n',raw):break
 else:raise RuntimeError('inference/deadline timeout')
 print(raw.decode('utf-8','replace')[-9000:],flush=True);u.close();u=None
 finals=re.findall(rb'CHAINB RESULT=(\{[^\r\n]+\})',raw)
 if not finals or json.loads(finals[-1]).get('pass')!=1:raise RuntimeError('CHAINB pass!=1')
 print(step('readback','C2_READBACK_OK',25),flush=True);ok=True
except Exception as e:events.append({'error':repr(e)});print('C2_FAILED',repr(e),flush=True)
finally:
 if u is not None:
  try:u.close()
  except Exception as e:events.append({'uart_close_error':repr(e)})
 with (r/'uart.bin').open('xb') as f:f.write(raw)
 if a is not None and t is not None and t.is_alive():
  try:step('close','C2_CORES_STOPPED',20)
  except Exception as e:events.append({'close_error':repr(e)});ok=False
  a.terminate_job(a.job);t.join(8)
 clean=bool(sr.get('cleanup_confirmed') and (t is None or not t.is_alive()));save('server_close.json',{'native':sr,'normal_stop_requested':True,'cleanup_confirmed':clean})
 if touched:
  if ok and clean:bs.note_clean(r.name)
  else:bs.mark_abnormal(r.name,'actual C2 failure; normal cleanup attempted')
 save('orchestration_result.json',{'status':'PASS' if ok and clean else 'FAIL','events':events,'cleanup_confirmed':clean,'hardware_touched':touched,'board_state':json.loads(Path(bs.STATE_FILE).read_text(encoding='utf-8'))})
raise SystemExit(0 if ok and clean else 2)
