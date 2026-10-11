"""只捕获ROOT授权运行的新source-after子进程，不查询live Vivado身份。"""
import argparse,hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
import psutil
ROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent; CACHE=ROOT/'tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01'
parser=argparse.ArgumentParser(); parser.add_argument('--expected-head',required=True); parser.add_argument('--output-dir',required=True,type=Path)
args=parser.parse_args(); out=args.output_dir
assert out.is_absolute() and out.parent.parts==CACHE.parts and CACHE.is_dir() and not out.exists() and re.fullmatch('source_after_check_r[0-9]+',out.name)
assert re.fullmatch('[0-9a-f]{40}',args.expected_head)
out.mkdir()
command=[sys.executable,'-X','utf8','-B',str(WORK/'source_after_check.py'),'--expected-head',args.expected_head,'--output-dir',str(out)]
start=time.monotonic(); peak=0; failure=None
with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
 child=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'))
 while child.poll() is None:
  try:
   process=psutil.Process(child.pid); peak=max(peak,sum(p.memory_info().rss for p in [process]+process.children(recursive=True)))
  except psutil.Error: pass
  if time.monotonic()-start>90 or peak>134217728:
   failure='TIMEOUT' if time.monotonic()-start>90 else 'OWNED_TEST_RSS_LIMIT'
   child.terminate(); child.wait(timeout=15); break
  time.sleep(.03)
def binding(p): return dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
record=dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=child.returncode,wrapper_exit_code=child.returncode if failure is None else 3,host_shell_exit_code=None,elapsed_seconds=time.monotonic()-start,sampled_owned_tree_rss_peak_bytes=peak,absolute_peak_bytes=None,failure=failure,closed_logs=[binding(out/'stdout.log'),binding(out/'stderr.log')],actual_vivado_or_hardware_started=False)
with (out/'native_receipt.json').open('x',encoding='utf-8',newline='\n') as f: json.dump(record,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps(record,ensure_ascii=False)); raise SystemExit(record['wrapper_exit_code'])
