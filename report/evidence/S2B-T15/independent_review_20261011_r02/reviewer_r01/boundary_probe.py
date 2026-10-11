"""独立注入ABORT提交前终态交错，保留真实应用的读后写路径。"""
import sys
sys.dont_write_bytecode = True
import pathlib
import os
import subprocess
import json
import struct
import hashlib

目录 = pathlib.Path(__file__).absolute().parent
根目录 = 目录.parents[3]
sys.path.insert(0, str(根目录))
from verification import test_s2b_board_transport as 测试
from verification import s2b_board_transport as 运输

源码 = 测试.MOCK_HARNESS
# 注入RTL允许的交错：CSR读返回RUN，此后在ABORT提交前变为ERROR_SAFE。
源码 = 源码.replace('if (pending > 0) { --pending; return OWNER_PL | 2U; }',
    'if (pending > 0) { --pending; if(getenv("S2B_REVIEW_RACE")) { physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=9U; } return OWNER_PL | 2U; }')
源码 = 源码.replace('} else if (value == 2U) { physical_status=',
    '} else if (value == 2U) { if((physical_status&7U)!=1U && (physical_status&7U)!=2U) { fprintf(stderr,"SLVERR_ABORT_AFTER_TERMINAL state=%x\\n",physical_status); exit(86); } physical_status=')
源码 = 源码.replace('count=atoi(argv[1]);', 'count=atoi(argv[1]); if(getenv("S2B_REVIEW_RACE")) { weights_loaded=1; input_loaded=1; }')
with (目录/'abort_boundary.c').open('x', encoding='utf-8', newline='\n') as 流:
    流.write(源码)
with (目录/'s2b_host_mock.h').open('x', encoding='utf-8', newline='\n') as 流:
    流.write(测试.MOCK_HEADER)
命令 = [str(测试.GCC), '-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(目录),
        '-I'+str(根目录/'vitis'),'-I'+str(根目录/'verification'),str(目录/'abort_boundary.c'),
        str(根目录/'verification/s2a_ps_decode_nms_reference.c'),'-o',str(目录/'abort_boundary.exe'),'-lm']
环境 = dict(os.environ, PATH=str(测试.GCC.parent)+os.pathsep+os.environ.get('PATH',''))
编译 = subprocess.run(命令, capture_output=True, env=环境)
assert 编译.returncode == 0, 编译.stderr
数据 = struct.pack('<III',2,1,1)
请求, 头 = 运输.make_request(3,1,7,数据)
运行 = subprocess.run([str(目录/'abort_boundary.exe'),'1'], input=头+数据,capture_output=True,
    env=dict(环境, S2B_REVIEW_RACE='1'),timeout=15)
with (目录/'abort_boundary_stderr.log').open('xb') as 流:
    流.write(运行.stderr)
with (目录/'abort_boundary_stdout.bin').open('xb') as 流:
    流.write(运行.stdout)
记录 = {'compile_command':命令, 'compile_exit_code':编译.returncode,'run_exit_code':运行.returncode,
        'reproduced':运行.returncode==86 and b'SLVERR_ABORT_AFTER_TERMINAL' in 运行.stderr,
        'stderr':运行.stderr.decode('utf-8'),'stdout_bytes':len(运行.stdout),
        'stderr_sha256':hashlib.sha256(运行.stderr).hexdigest(),
        'limitations':'此为软件边界注入，SLVERR状态规则来自RTL；不证明实物DataAbort已执行。'}
with (目录/'abort_boundary_result.json').open('x',encoding='utf-8') as 流:
    json.dump(记录,流,ensure_ascii=False,indent=2)
print(json.dumps(记录,ensure_ascii=False))
assert 记录['reproduced']
