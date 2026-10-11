"""本轮修复G1纯模拟与真实轻量入口捕获，不执行实际source-after或PNR整理。"""
import ast,difflib,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
import psutil
WORK=Path(__file__).parent; ROOT=WORK.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):
 assert p.parent==WORK and not p.exists()
 with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
def capture(name,script,args):
 command=[sys.executable,'-X','utf8','-B',str(WORK/script),*args]; start=time.monotonic(); peak=0
 with (WORK/(name+'.stdout.log')).open('xb') as out,(WORK/(name+'.stderr.log')).open('xb') as err:
  child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'))
  while child.poll() is None:
   try: peak=max(peak,psutil.Process(child.pid).memory_info().rss)
   except psutil.Error: pass
   assert time.monotonic()-start<60 and peak<134217728; time.sleep(.02)
 record=dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=child.returncode,elapsed_seconds=time.monotonic()-start,sampled_owned_child_rss_peak_bytes=peak,absolute_peak_bytes=None,stdout_sha256=sha(WORK/(name+'.stdout.log')),stderr_sha256=sha(WORK/(name+'.stderr.log')))
 save(WORK/(name+'.native.json'),record); return record
for name in ('collector.py','source_after_check.py','native_source_after.py','history_tests_r03.py'): ast.parse((WORK/name).read_text(encoding='utf-8'))
tests={}
for name,script,args,expected in [('history_r03','history_tests_r03.py',[],0),('collector_help_r03','collector.py',['--help'],0),('collector_missing_gate_r03','collector.py',['collect'],1),('adapter_help_r03','source_after_check.py',['--help'],0),('native_adapter_help_r03','native_source_after.py',['--help'],0),('native_adapter_outside_refusal_r03','native_source_after.py',['--expected-head','0'*40,'--output-dir',str(WORK/'mock_forbidden_output')],1),('adapter_missing_head_r03','source_after_check.py',['--output-dir',str(WORK/'mock_forbidden_output')],2),('prepare_r03','collector.py',['prepare'],0),('prepare_overwrite_r03','collector.py',['prepare'],1)]:
 tests[name]=capture(name,script,args); assert tests[name]['native_exit_code']==expected,(name,tests[name])
assert not (WORK/'mock_forbidden_output').exists()
spec=importlib.util.spec_from_file_location('adapter',WORK/'source_after_check.py'); adapter=importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
compare_cases=[]
for label,blob,raw,expected in [('RAW',b'a\nb\n',b'a\nb\n','RAW_IDENTICAL'),('LF_CRLF',b'a\nb\n',b'a\r\nb\r\n','GIT_LF_TO_RAW_CRLF'),('already_CRLF',b'a\r\nb\r\n',b'a\r\nb\r\n','RAW_IDENTICAL'),('mixed_EOL',b'a\r\nb\n',b'a\r\nb\r\n',None),('semantic_diff',b'a\n',b'b\n',None),('missing_final_newline',b'a\n',b'a',None)]:
 try: actual=adapter.compare_raw(blob,raw)
 except ValueError: actual=None
 assert actual==expected; compare_cases.append(dict(case=label,expected=expected,actual=actual,simulated_not_git=True))
old=(WORK/'collector_before_r03.py').read_text(encoding='utf-8').splitlines(keepends=True); new=(WORK/'collector.py').read_text(encoding='utf-8').splitlines(keepends=True)
with (WORK/'source_diff_r03.patch').open('x',encoding='utf-8',newline='\n') as f: f.writelines(difflib.unified_diff(old,new,fromfile='collector_before_r03.py',tofile='collector.py'))
review=ROOT/'tmp/2B/S2B-T17/independent_s11_impl_collector_review_20261012_r01/final_review_receipt.json'; raw=review.with_name('raw_manifest.jsonl')
assert sha(review)=='f2bd6de5cd2cfdaf285d0a4142b510ff3bafff8e57d8b189150f9349200b2fb7' and sha(raw)=='31ac3fa82da3fdcf575ae1ace80ea398c13971416d730a6d13d0f1d96947b17b'
receipt=dict(status='PASS_G1_REPAIR_AND_SOURCE_AFTER_PREPARATION_ONLY',developer_stop=True,review_input=dict(receipt_sha256=sha(review),raw_manifest_sha256=sha(raw)),history_test=json.loads((WORK/'history_test_result_r03.json').read_text(encoding='utf-8')),source_adapter_compare_cases=compare_cases,commands=tests,source_after_actual_executed=False,git_head_queried_or_mocked=False,live_pnr_or_external_process_access=False,source_commit='a710ec431474841a81912a6055f861e811a151e3',source_hashes={n:sha(WORK/n) for n in ('collector.py','source_after_check.py','native_source_after.py')},prepared_receipt_sha256=sha(WORK/'prepared_receipt_r03.json'),source_diff_sha256=sha(WORK/'source_diff_r03.patch'),limitations=['本轮history为纯mock，mock code不是实际PNR原生码；真实Python原生码及stderr逐项保留。','作者未运行Git HEAD/source-after实际检查，也未monkeypatch Git/HEAD；源码adapter只有6个字节比较样例和真实help/参数/越界拒绝。','实际source-after由ROOT用新输出目录亲自运行，逐项核a710 Git blob/当前RAW、真实HEAD前后与43/33/18/原14；证据HEAD与源码基线分列。','准备G1不等于独立G2、PNR时序/预算/整树闭合或G3批准；旧r02及Reviewer CHANGES_REQUIRED原件保留。'])
save(WORK/'tool_receipt_r03.json',receipt)
rows=[]
for p in sorted(WORK.iterdir()):
 if p.is_file() and p.name!='raw_manifest_r03.jsonl': rows.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role='source' if p.suffix=='.py' else 'log' if p.suffix=='.log' else 'result'))
for p in (review,raw): rows.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role='input'))
with (WORK/'raw_manifest_r03.jsonl').open('x',encoding='utf-8',newline='\n') as f:
 for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print(json.dumps(dict(STOP=True,collector_sha256=receipt['source_hashes']['collector.py'],adapter_sha256=receipt['source_hashes']['source_after_check.py'],native_adapter_sha256=receipt['source_hashes']['native_source_after.py'],receipt_sha256=sha(WORK/'tool_receipt_r03.json'),prepared_sha256=receipt['prepared_receipt_sha256'],raw_manifest_sha256=sha(WORK/'raw_manifest_r03.jsonl'),raw_rows=len(rows),history_cases=receipt['history_test']['count'],actual_commands=len(tests),peak_sampled_owned_child_rss_bytes=max(r['sampled_owned_child_rss_peak_bytes'] for r in tests.values())),ensure_ascii=False))
