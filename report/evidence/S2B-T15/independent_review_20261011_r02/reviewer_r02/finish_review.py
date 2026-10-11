"""完整XSA构建绑定与独立G2复审收据；不操作任何实物。"""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,re,subprocess
目录=pathlib.Path(__file__).absolute().parent
根目录=目录.parents[3]
sys.path.insert(0,str(根目录/'vitis'));sys.path.insert(0,str(根目录))
from build_s2b_inference import verify_app_elf,xsa_contract
from check_s2b_ps_smoke_layout import verify_cache_contract,parse_elf
from verification import s2b_board_transport as 运输
from verification import test_s2b_board_transport as 测试
def 摘要(路径):return hashlib.sha256(路径.read_bytes()).hexdigest()
固定={'vitis/s2b_inference_app.c':'9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39',
 'vitis/build_s2b_inference.py':'0259af39128d003c5548ca04c8c51c1652e27c546b5ae2bb709bc92efd879b97',
 'verification/s2b_board_transport.py':'355721403848a4e28afffa06c1dc442b6d52c94859a6ee167d58db10fcdd26c8',
 'verification/test_s2b_board_transport.py':'a9ac5392d08499778af05b06cdcdf080ae122ebcc3f14fb16fad7617f7e8059b',
 'docs/obsidian-project/02-方案设计/s2b_board_transport.md':'8239191df5938e1d8c02c55a55bbf23ebe20c40fc53c9ae6b46641fc6254d1e5'}
assert all(摘要(根目录/名)==值 for 名,值 in 固定.items())
构建目录=根目录/'report/evidence/S2B-T15/full_build_20261011_r01'
构建=json.loads((构建目录/'build_details.json').read_text(encoding='utf-8'))
assert 摘要(构建目录/'build_details.json')=='932ac348d4e05268968b745bf45298fda36895aed4b143abb7c1abe1a477db64'
assert 构建['status']=='PASS_OFFLINE_FULL_XSA_BUILD' and 构建['hardware_mode']=='FULL_PLATFORM_BOUND'
for 名,绑定 in 构建['files'].items():assert 摘要(pathlib.Path(绑定['path']))==绑定['sha256'],名
for 命令 in 构建['commands']:assert 命令['exit_code']==0 and 摘要(pathlib.Path(命令['log']))==命令['log_sha256']
for 名 in ['elf','initializer_elf']:assert 摘要(pathlib.Path(构建[名]['path']))==构建[名]['sha256']
for 名,值 in 构建['source_sha256'].items():assert 摘要(根目录/名)==值,名
for 名 in ['xsa','platform_manifest']:assert 摘要(pathlib.Path(构建['config'][名]))==构建['config'][名+'_sha256']
元数据=xsa_contract(pathlib.Path(构建['config']['xsa']),'FULL_PLATFORM_BOUND')
布局=verify_app_elf(构建目录/'infer.elf')
初始化=parse_elf((构建目录/'init.elf').read_bytes())
for 节 in 初始化['sections']:
 if 节['flags']&2 and 节['size']:
  assert (0<=节['address'] and 节['address']+节['size']<=0x30000) or (0xffff0000<=节['address'] and 节['address']+节['size']<=0xfffffe00)
verify_cache_contract((构建目录/'xil_cache.c').read_text(encoding='utf-8'))
调用=[项 for 项 in 构建['api_calls'] if 项['name'] in ['platform.build','app.build','init.build']]
assert len(调用)==3 and all(项['return_type']=='int' and 项['return_repr']=='0' for 项 in 调用)
终端=(构建目录/'vitis_console.log').read_text(encoding='utf-8',errors='replace')
assert 'Shutting down Vitis server' in 终端 and 'PASS_OFFLINE_FULL_XSA_BUILD' in 终端
应用=(根目录/'vitis/s2b_inference_app.c').read_text(encoding='utf-8')
控制写=re.findall(r'csr_write\(0x008U,\s*([^)]*)\)',应用)
assert sorted(控制写)==['1U','4U']
向量=(构建目录/'asm_vectors.S').read_text(encoding='utf-8')
assert 'DataAbortInterrupt' in 向量 and re.search(r'subs\s+pc,\s*lr,\s*#8',向量)
定时器=(构建目录/'globaltimer_sleep_zynq.c').read_text(encoding='utf-8')
assert 'XGlobalTimer_Start(InstancePtr)' in 定时器 and 'CpuFreq/2' in 定时器
for 项 in json.loads((构建目录/'app_compile_commands.json').read_text(encoding='utf-8')):
 if pathlib.Path(项['file']).name in ['s2b_inference_app.c','s2a_ps_decode_nms_reference.c']:
  assert all(标志 in 项['command'] for 标志 in ['-DSDT','-Wall','-Wextra','-Werror']) and '-DUSE_AMP' not in 项['command']
# 独立验证无pending的ACK和CRC错误不能触发硬件ACK。
额外=[]
for 标签,序列,损坏 in [('no_pending',1,False),('corrupt_crc',1,True)]:
 载荷=__import__('struct').pack('<III',3,0,0)
 _,头=运输.make_request(3,序列,77,载荷)
 if 损坏: 头=头[:-1]+bytes([头[-1]^1])
 运行=subprocess.run([str(目录/'independent_boundary.exe'),'6','1'],input=头+载荷,capture_output=True,timeout=15)
 assert 运行.returncode==2 and b'ack=0 pending=0' in 运行.stderr
 (目录/f'ack_{标签}.log').write_bytes(运行.stderr);(目录/f'ack_{标签}.bin').write_bytes(运行.stdout)
 额外.append({'case':标签,'exit_code':运行.returncode,'stderr_sha256':运输.digest(运行.stderr),'stdout_sha256':运输.digest(运行.stdout)})
记录={'status':'PASS','scope':'S2B-T15 independent G2 software R2','source_commit':'3700b9a61de41375138ad8c9633788fd73b3960f',
 'review_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=根目录,text=True).strip(),'fixed_source_sha256':固定,
 'closed_findings':['T15-R1-01: CPU不再执行ABORT STR；六种终态交错失败锁存、原错误与所有权保留且无ACK；DAP后显式ACK另行核验。'],
 'test_result':json.loads((目录/'test_result.json').read_text(encoding='utf-8')),'additional_ack_cases':额外,
 'actual_build_checks':{'build_details_sha256':摘要(构建目录/'build_details.json'),'files_verified':len(构建['files']),
   'commands_verified':len(构建['commands']),'build_api_results':调用,'full_xsa_contract':元数据,
   'app_elf_sha256':构建['elf']['sha256'],'init_elf_sha256':构建['initializer_elf']['sha256'],
   'elf_layout_check':'PASS','bsp_cache_contract':'PASS','actual_timer_enable':'PASS','CPU_command_values':控制写,
   'raw_console_sha256':摘要(构建目录/'vitis_console.log')},
 'commands':[{'command':'python run_review.py','exit_code':0},{'command':'python finish_review.py','exit_code':0}],
 'artifact_sha256':{项.name:摘要(项) for 项 in 目录.iterdir() if 项.is_file() and 项.suffix!='.exe'},
 'limits':['未启动Vitis server、硬件或MCP；真实ARM构建来自原件并独立核对。','独立模型不代表RTL或真实DAP操作通过；T16外部协同需独立审查。',
  'CPU1停核、cacheprobe、HP可见性、100样本、1000连续和50MHz完整timing仍须真实证据，G2不等于G3/G4/G5。',
  '固定待审五文件未修改；无提交；峰值内存及工具调用总量未测。']}
with (目录/'review_receipt.json').open('x',encoding='utf-8',newline='\n') as 流:json.dump(记录,流,ensure_ascii=False,indent=2)
print(json.dumps({'status':'PASS','receipt_sha256':摘要(目录/'review_receipt.json'),'files_verified':len(构建['files'])},ensure_ascii=False))
