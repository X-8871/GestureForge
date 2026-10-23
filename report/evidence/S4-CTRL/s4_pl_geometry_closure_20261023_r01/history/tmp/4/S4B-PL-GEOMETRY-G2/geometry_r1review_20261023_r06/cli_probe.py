import hashlib, json, os, subprocess, sys, zlib
from pathlib import Path
root=Path(r'D:\codex-worktrees\w4'); run=Path(os.environ['REVIEW_RUN']); tmp=Path(os.environ['TEMP'])
manifest=root/'report/evidence/S4-B/s4b_pl_geometry_g2_20261023_r02/frozen_sources.json'
gen=root/'scripts/stage4_s4b/build_s4b_preproc_geometry.py'; test=root/'verification/test_s4b_preproc_geometry.py'; d2=root/'verification/s1_t02_d2_numeric_reference.py'
expected={manifest:'28479466f6d2613e10a9820639daaf825536d0532b04ff918f9c74a06d7a00dc',gen:'8b0d1692b3609c9da255133169bc74c2d141c3b34a37e82549e771bebfde70ef',test:'383bbae3d716a7288f2acd3e6f57b89858d918150d616d0d155e02fe6fdc9211',d2:'6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in expected}; assert before=={str(k):v for k,v in expected.items()}
assert tmp.is_dir() and tmp.is_absolute() and run in tmp.parents
child=os.environ.copy(); child['TEMP']=str(tmp); child['TMP']=str(tmp)
cli=run/'valid_geometry.json'
args=[sys.executable,'-B',str(gen),'--src-width','202','--src-height','329','--dst-width','416','--dst-height','416','--output',str(cli)]
valid=subprocess.run(args,env=child,cwd=str(root),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
assert valid.returncode==0,(valid.returncode,valid.stdout,valid.stderr)
raw=cli.read_bytes(); meta=json.loads(raw.decode('utf-8'))
payload={k:v for k,v in meta.items() if k!='integrity'}
canonical=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
assert hashlib.sha256(canonical).hexdigest()==meta['integrity']['canonical_sha256']
assert f'0x{zlib.crc32(canonical)&0xffffffff:08x}'==meta['integrity']['canonical_crc32']
assert meta['status']=='DRAFT_GEOMETRY_ONLY_NOT_FOR_HARDWARE'
assert meta['provenance']['generator_sha256']==expected[gen]
assert meta['provenance']['reference_sha256']==expected[d2]
trailing=run/'new_target.json.'
trailing_run=subprocess.run(args[:-2]+['--output',str(trailing)],env=child,cwd=str(root),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
assert trailing_run.returncode==2 and not (run/'new_target.json').exists()
before_existing=cli.read_bytes()
ads=str(cli)+':review_probe'
ads_run=subprocess.run(args[:-2]+['--output',ads],env=child,cwd=str(root),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
assert ads_run.returncode==2 and cli.read_bytes()==before_existing and not os.path.lexists(ads)
after={str(p):sha(p) for p in expected}; assert after==before
result={'run_id':run.name,'TEMP':str(tmp),'TMP':str(tmp),'python':sys.executable,'frozen_hashes_before':before,'frozen_hashes_after':after,'valid_cli_exit':valid.returncode,'valid_cli_stdout':valid.stdout.strip().splitlines(),'valid_output_sha256':sha(cli),'valid_status':meta['status'],'valid_integrity':'PASS','trailing_dot_cli_exit':trailing_run.returncode,'trailing_dot_stderr':trailing_run.stderr.strip().splitlines(),'trailing_target_created':(run/'new_target.json').exists(),'existing_ads_cli_exit':ads_run.returncode,'existing_ads_stderr':ads_run.stderr.strip().splitlines(),'existing_output_unchanged':cli.read_bytes()==before_existing,'ads_created':os.path.lexists(ads)}
(run/'cli_results.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
print(f'VALID_CLI_EXIT={valid.returncode}; TRAILING_DOT_CLI_EXIT={trailing_run.returncode}; ADS_CLI_EXIT={ads_run.returncode}')