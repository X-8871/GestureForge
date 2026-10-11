"""核对固定源码及原始构建绑定，记录独立G2结论。"""
import sys
sys.dont_write_bytecode = True
import pathlib
import json
import hashlib
import subprocess

目录 = pathlib.Path(__file__).absolute().parent
根目录 = 目录.parents[3]
sys.path.insert(0,str(根目录/'vitis'))
from build_s2b_inference import verify_app_elf
from check_s2b_ps_smoke_layout import verify_cache_contract

def 摘要(路径):
    return hashlib.sha256(路径.read_bytes()).hexdigest()

固定 = {'vitis/s2b_inference_app.c':'3b2579d1bc7a956aa35adeb515f9e67d1cc0d2ae99b71f693f4d8a6f855387c9',
        'vitis/build_s2b_inference.py':'4d77a0295ece69100d703872f4cb8976c6dd115df0b121e0188033ebbc02be2b',
        'verification/s2b_board_transport.py':'6e14861b7ba83b7d4f4299293602a38e5b39ed402357db345f738601c03337d4',
        'verification/test_s2b_board_transport.py':'963eb5f53086c9dc3606b8baa795ee31957662fdf79c6aca989427b2c8f82b68',
        'docs/obsidian-project/02-方案设计/s2b_board_transport.md':'a20a03a965fe2fadd5da619b2665f322da630f92ccc92aa401c2bb17869ed208'}
assert all(摘要(根目录/名)==值 for 名,值 in 固定.items())
构建目录 = 根目录/'report/evidence/S2B-T15/unit_build_20261011_r03'
构建 = json.loads((构建目录/'build_details.json').read_text(encoding='utf-8'))
assert 摘要(构建目录/'build_details.json')=='cbd684442ae5efaa73fd2756ba487ddb030b4df85cf1af3cb295de5bc573a912'
for 名,绑定 in 构建['files'].items():
    assert 摘要(pathlib.Path(绑定['path']))==绑定['sha256'],名
for 命令 in 构建['commands']:
    assert 命令['exit_code']==0 and 摘要(pathlib.Path(命令['log']))==命令['log_sha256']
for 名 in ['elf','initializer_elf']:
    assert 摘要(pathlib.Path(构建[名]['path']))==构建[名]['sha256']
for 名,值 in 构建['source_sha256'].items():
    assert 摘要(根目录/名)==值,名
构建调用 = [项 for 项 in 构建['api_calls'] if 项['name'] in ['platform.build','app.build','init.build']]
assert len(构建调用)==3 and all(项['return_type']=='int' and 项['return_repr']=='0' for 项 in 构建调用)
布局 = verify_app_elf(构建目录/'infer.elf')
verify_cache_contract((构建目录/'xil_cache.c').read_text(encoding='utf-8'))
终端 = (构建目录/'vitis_console.log').read_text(encoding='utf-8', errors='replace')
assert 'Shutting down Vitis server' in 终端 and 'PASS_UNIT_ONLY_PS_XSA_BUILD' in 终端
测试 = json.loads((目录/'test_result.json').read_text(encoding='utf-8'))
边界 = json.loads((目录/'abort_boundary_result.json').read_text(encoding='utf-8'))
记录 = {'status':'CHANGES_REQUIRED','scope':'S2B-T15 G2 software review; no G3/G4/G5',
        'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=根目录,text=True).strip(),
        'fixed_source_sha256':固定,'independent_tests':测试,'abort_boundary':边界,
        'original_build_verified':{'status':构建['status'],'build_details_sha256':摘要(构建目录/'build_details.json'),
            'file_bindings_verified':len(构建['files']),'commands_verified':len(构建['commands']),
            'build_api_results':构建调用,'elf_sha256':构建['elf']['sha256'],
            'raw_console_sha256':摘要(构建目录/'vitis_console.log'),'independent_elf_layout_check':'PASS',
            'actual_bsp_cache_contract_check':'PASS'},
        'findings':[{'id':'T15-R1-01','priority':'P1','file':'vitis/s2b_inference_app.c','lines':[341,344],
            'description':'诊断mode2状态读与ABORT提交存在终态交错；RTL在终态拒绝ABORT并返回SLVERR，CPU未安装恢复处理，可能DataAbort且没有二进制响应。',
            'basis':'src/s2b_control_csr.sv:112-114,259,344-347；public mode2接受任意非零core/drain，包括1；原hostmock csr_write(value2)无准入检查。',
            'closure':'防止或受控处理状态读后终态变化导致的SLVERR，保留所有权与原始错误；补mode2成功/终态交错/短deadline回归，禁止把额外状态重读作为原子性证明。'}],
        'commands':[{'command':'python run_independent.py','exit_code':0},
                    {'command':'python boundary_probe.py','exit_code':0},
                    {'command':'python make_receipt.py','exit_code':0}],
        'artifact_sha256':{项.name:摘要(项) for 项 in 目录.iterdir() if 项.is_file() and 项.suffix not in ['.exe']},
        'limits':['未运行Vitis server或硬件；复用实际ARM构建原件并独立检查绑定/ELF/BSP。',
                  '边界注入遵守RTL终态拒绝语义，但不代表真实DataAbort已经发生。',
                  'CPU1停核、同ELF cacheprobe、HP可见性、100样本、1000连续和完整50MHz timing仍须真实独立证据。',
                  '本代理不提交；待审五文件未修改；工具调用量与峰值内存未测。']}
with (目录/'review_receipt.json').open('x',encoding='utf-8',newline='\n') as 流:
    json.dump(记录,流,ensure_ascii=False,indent=2)
print(json.dumps({'status':记录['status'],'receipt_sha256':摘要(目录/'review_receipt.json'),
                  'verified_file_bindings':len(构建['files'])},ensure_ascii=False))
