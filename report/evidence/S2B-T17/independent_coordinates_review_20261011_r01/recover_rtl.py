"""保留首轮误判原件，精确排除仅MCP服务器后执行已准备的独立刺激。"""
from pathlib import Path
import hashlib, importlib.util, json, os, re, shutil, subprocess, sys, time
import psutil
sys.stdout.reconfigure(encoding='utf-8')
WORK=Path(__file__).resolve().parent; ROOT=WORK.parents[3]; started=time.monotonic()
s=importlib.util.spec_from_file_location('r',ROOT/'verification/test_s2b_backend_coordinates_rtl.py'); r=importlib.util.module_from_spec(s); s.loader.exec_module(r)
report=json.loads((WORK/'rtl_receipt.json').read_text(encoding='utf-8')); report['first_attempt_receipt_sha256']=r.sha(WORK/'rtl_receipt.json'); report['status']='FAIL'; report['runs']=[]
try:
    report['recovery_preflight']={'available_ram_bytes':psutil.virtual_memory().available,'disk_free_bytes':shutil.disk_usage(WORK).free,
      'actual_heavy_processes':[{'pid':p.pid,'name':p.info['name']} for p in psutil.process_iter(['name']) if p.info['name'] and (p.info['name'].lower() in ('vivado.exe','verilator_bin.exe','g++.exe','cc1plus.exe') or p.info['name'].lower().startswith('vtb_'))],
      'first_failure_reason':'首轮模糊vivado子串误把vivado-mcp-server进程当作重型任务；未启动编译。'}
    assert not report['recovery_preflight']['actual_heavy_processes']
    assert report['recovery_preflight']['available_ram_bytes']>=2147483648 and report['recovery_preflight']['disk_free_bytes']>=1073741824
    env=os.environ.copy(); tool=Path(r'D:\FPGA_S2A_MSYS2_20261001\env'); bins=tool/'mingw64/bin'; make=tool/'usr/bin'
    env['PATH']=str(make)+os.pathsep+str(bins)+os.pathsep+env.get('PATH',''); env['VERILATOR_ROOT']=str(tool/'mingw64/share/verilator'); env['PYTHONUTF8']='1'
    report['tool_versions']={'python':sys.version,'verilator':subprocess.check_output([str(bins/'verilator_bin.exe'),'--version'],env=env,cwd=WORK,text=True).strip()}
    command=[str(bins/'verilator_bin.exe'),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1',
      '--output-split','10000','--output-split-cfuncs','100','--top-module','tb_s2b_backend_coordinates','--Mdir','obj_dir',
      '-MAKEFLAGS',"PYTHON3='\""+sys.executable+"\"'",'-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1',
      *['source/'+Path(p).name for p in r.RTL],'source/s1_network_backend.sv','convolution_stub.sv','tb_s2b_backend_coordinates.sv']
    r.execute('compile_r02',command,WORK,WORK,env,report,600)
    r.execute('simulation_r02',[str(WORK/'obj_dir/Vtb_s2b_backend_coordinates.exe')],WORK,WORK,env,report,1200)
    log=(WORK/'simulation_r02.log').read_text(encoding='utf-8'); found=re.findall(r'PASS BACKEND_COORDINATES boundary=(\d+) layers=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) owner_drop_results=(\d+)',log); assert len(found)==1
    counts=dict(zip(('boundary_cases','nonconv_layers','nonconv_outputs','nonconv_requests','cycles','owner_drop_results'),map(int,found[0])))
    assert counts['boundary_cases']==4980736 and counts['nonconv_layers']==15 and counts['nonconv_outputs']==5234944 and counts['nonconv_requests']==12286976 and counts['owner_drop_results']>0
    report['simulation_counts']=counts; report['trace_summaries']=re.findall(r'TRACE layer=(\d+) op=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) digest=([0-9a-fA-F]+)',log)
    report['source_sha256_post']={p:r.sha(ROOT/p) for p in report['source_sha256_pre']}; assert report['source_sha256_post']==report['source_sha256_pre']
    report['frozen14_post']={p:r.sha(ROOT/p) for p in report['frozen14_pre']}; assert report['frozen14_post']==report['frozen14_pre']
    report['status']='PASS_INDEPENDENT_RTL_EXPERIMENT'; report.pop('failure',None)
except Exception as exc: report['failure']=repr(exc)
report['recovery_seconds']=round(time.monotonic()-started,6)
report['files_r02']=[{'path':p.relative_to(ROOT).as_posix(),'sha256':r.sha(p),'bytes':p.stat().st_size} for p in WORK.iterdir() if p.is_file()]
(WORK/'rtl_receipt_r02.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'seconds':report['recovery_seconds'],'counts':report.get('simulation_counts'),'failure':report.get('failure')},ensure_ascii=False),flush=True)
raise SystemExit(0 if report['status']=='PASS_INDEPENDENT_RTL_EXPERIMENT' else 1)
