"""新 tile 所选完整 tile 的真实 memory 定向回归；不替代整网。"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time
import numpy as np
import test_s2a_conv_engine_rtl as oracle

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('src/s2a_network_descriptor_pkg.sv', 'src/s2a_conv_tile_engine.sv', 'sim/tb_s2a_conv_tile_memory.sv')
HEADER = struct.Struct('<13I')

def sha(path: Path) -> str:
    """计算精确字节摘要。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def case_fixture(layer: dict, vector: dict, weights: bytes, ordinal: int) -> tuple[bytes, dict]:
    """把规范查询 tap 映射成一致稀疏 NCHW patch；相邻输出独立计算。"""
    _, channel, y, x = map(int, vector['target_output_nchw'])
    _, ci, hi, wi = map(int, layer['input_shape_nchw'])
    _, co, ho, wo = map(int, layer['output_shape_nchw'])
    kh, kw = map(int, layer['kernel_hw']); sy, sx = map(int, layer['stride_hw'])
    pl, _, pt, _ = map(int, layer['padding_lrtb'])
    ty, tx, group = y//8*8, x//8*8, channel//8*8
    th, tw, lanes = min(8, ho-ty), min(8, wo-tx), min(8, co-group)
    ph, pw, k = (th-1)*sy+kh, (tw-1)*sx+kw, ci*kh*kw
    patch = np.zeros((ci, ph, pw), dtype=np.int64)
    acts = list(map(int, vector['input_reduction_int8']))
    expected_weights = bytes(v & 255 for v in vector['weight_reduction_int8'])
    if len(acts) != k or expected_weights != weights[channel*k:(channel+1)*k]:
        raise ValueError('定向向量与冻结 GF8 不符')
    for index, value in enumerate(acts):
        ic, rem = divmod(index, kh*kw); ky, kx = divmod(rem, kw)
        iy, ix = y*sy+ky-pt, x*sx+kx-pl
        if 0 <= iy < hi and 0 <= ix < wi:
            patch[ic, (y-ty)*sy+ky, (x-tx)*sx+kx] = value
    wg = weights[group*k:(group+lanes)*k]
    weight_array = np.frombuffer(wg, dtype=np.int8).astype(np.int64).reshape(lanes, k)
    golden = bytearray(); target_checked = False
    for lane in range(lanes):
        oc = group+lane
        for py in range(th):
            for px in range(tw):
                values = patch[:, py*sy:py*sy+kh, px*sx:px*sx+kw].reshape(k)
                sums = np.cumsum(values * weight_array[lane], dtype=np.int64) + int(layer['bias_accumulator_int32_per_output_channel'][oc])
                if np.any(sums < -(1<<31)) or np.any(sums > (1<<31)-1):
                    raise ValueError('相邻输出发生 INT32 溢出')
                acc = int(sums[-1])
                result = oracle._d2_quantize(acc, float(layer['input_scale']), float(layer['weight_scale_per_output_channel'][oc]), float(layer['output_scale']), layer['activation'])
                golden.append(result & 255)
                if oc == channel and ty+py == y and tx+px == x:
                    if acc != int(vector['expected_int32_result']):
                        raise ValueError('规范目标累加值不一致')
                    target_checked = True
    if not target_checked:
        raise ValueError('未覆盖规范目标')
    header = HEADER.pack(layer['layer_index'], ordinal, ty, tx, group, th, tw, ph, pw, ci, k, lanes, len(golden))
    payload = header + patch.astype(np.int8).tobytes() + wg + golden
    return payload, {'layer': layer['layer_index'], 'case': ordinal, 'target': [channel,y,x], 'tile': [ty,tx,th,tw], 'group': [group,lanes], 'patch_bytes': patch.size, 'weight_bytes':len(wg), 'output_bytes':len(golden), 'sha256':hashlib.sha256(payload).hexdigest()}

def prepare(work: Path, mode: str) -> dict:
    """生成固定模型定向数据，pilot 选择不同规模的三个真实层。"""
    manifest, _, weights, package = oracle._load_bound_inputs()
    rows = []; cases = 0
    with (work/'cases.bin').open('xb') as stream:
        for layer in manifest['layers']:
            if layer['op'] != 'convolutional': continue
            lid = int(layer['layer_index'])
            vectors = manifest['operator_test_plan']['directed_case_vectors']['convolutional'][str(lid)]
            if len(vectors) != 16: raise ValueError('每层必须16定向')
            for ordinal, vector in enumerate(vectors):
                if mode == 'pilot' and (lid,ordinal) not in ((0,0),(26,0),(36,15)): continue
                data, row = case_fixture(layer, vector, weights[lid], ordinal)
                stream.write(data); rows.append(row); cases += 1
    if cases != (3 if mode == 'pilot' else 336): raise ValueError('用例计数不完整')
    (work/'source').mkdir()
    sources = []
    for rel in SOURCES:
        source = ROOT/rel
        if not source.is_file() or source.is_symlink(): raise ValueError('源路径类型错误')
        target = work/'source'/source.name
        shutil.copyfile(source,target); sources.append({'path':rel,'sha256':sha(target)})
    return {'schema':'s2a_tile_selected_memory_v1','status':'PREPARED_NOT_RTL_PASS','mode':mode,'cases':cases,'output_bytes':sum(r['output_bytes'] for r in rows), 'scope':'真实 descriptor 验证后白盒选择起始 tile/group，完整 patch/GF8组经过生产memory加载、全部tile输出比较后abort；不证明cache遍历/整层/异常/G4G5','not_covered':['blackbox cache traversal','invalid descriptor','-128','overflow','G4/G5'],'sources':sources,'runner_sha256':sha(Path(__file__)),'oracle_sha256':sha(Path(oracle.__file__)),'manifest_sha256':sha(oracle._MANIFEST),'gf8_path':str(package),'gf8_sha256':sha(package),'fixture_sha256':sha(work/'cases.bin'),'fixture_bytes':(work/'cases.bin').stat().st_size,'rows':rows}

def run(work: Path, report: dict, timeout: int) -> None:
    """只编译运行本隔离任务，单job与单thread，不产生波形。"""
    toolroot = Path(r'D:\FPGA_S2A_MSYS2_20261001\env')
    toolbin = toolroot/'mingw64/bin'; makebin = toolroot/'usr/bin'
    tools = [toolbin/'verilator_bin.exe',toolbin/'g++.exe',makebin/'make.exe',Path(sys.executable)]
    for p in tools:
        if not p.is_file(): raise ValueError(f'工具不存在：{p}')
    report['tools'] = [{'path':str(p),'sha256':sha(p)} for p in tools]
    env = os.environ.copy(); env['PATH'] = str(makebin)+os.pathsep+str(toolbin)+os.pathsep+env.get('PATH',''); env['VERILATOR_ROOT']=str(toolroot/'mingw64/share/verilator')
    report['verilator_version'] = subprocess.run([str(tools[0]),'--version'],capture_output=True,text=True,env=env,check=True,timeout=30).stdout.strip()
    if sha(work/'cases.bin') != report['fixture_sha256']: raise ValueError('fixture准备后改变')
    for row in report['sources']:
        if sha(work/'source'/Path(row['path']).name) != row['sha256']: raise ValueError('隔离编译源改变')
    command = [str(tools[0]),'--binary','--timing','-Wno-fatal','-j','1','--threads','1','--top-module','tb_s2a_conv_tile_memory','--Mdir','obj_dir','-MAKEFLAGS', 'PYTHON3=\'"'+sys.executable+'"\'','-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0']+[str(Path('source')/Path(rel).name) for rel in SOURCES]
    for label,cmd in (('compile',command),('simulation',[str(work/'obj_dir/Vtb_s2a_conv_tile_memory.exe'),f'+CASES={report["cases"]}'])):
        started=time.monotonic()
        with (work/f'{label}.log').open('x',encoding='utf-8') as log:
            result=subprocess.run(cmd,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout,check=False)
        report[label]={'command':cmd,'exit_code':result.returncode,'seconds':round(time.monotonic()-started,3)}
        report[label]['log_sha256']=sha(work/f'{label}.log')
        if result.returncode: raise ValueError(f'{label}失败：{work/f"{label}.log"}')
    text=(work/'simulation.log').read_text(encoding='utf-8')
    marker=f'PASS TILE_MEMORY cases={report["cases"]} outputs={report["output_bytes"]}'
    if text.count(marker)!=1: raise ValueError('缺完整唯一marker')
    checkpoints=re.findall(r'CHECKPOINT TILE_MEMORY layer=(\d+) case=(\d+) cycles=(\d+) feature=(\d+) weight=(\d+) output=(\d+) stalls=(\d+)/(\d+)/(\d+)',text)
    if len(checkpoints)!=report['cases'] or [(int(c[0]),int(c[1])) for c in checkpoints]!=[(r['layer'],r['case']) for r in report['rows']]: raise ValueError('checkpoint次序/计数不符')
    report['cycle_count']=sum(int(c[2]) for c in checkpoints)
    report['binary_sha256']=sha(work/'obj_dir/Vtb_s2a_conv_tile_memory.exe')
    report['status']='PASS_SELECTED_TILE_MEMORY_ONLY'

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=('pilot','full'),default='pilot'); parser.add_argument('--work-dir',type=Path,required=True); parser.add_argument('--timeout-seconds',type=int,default=1200)
    args=parser.parse_args(); work=args.work_dir
    if not work.is_absolute() or work.exists() or not work.parent.is_dir() or work.parent.is_symlink() or args.timeout_seconds<=0: parser.error('须给普通父目录内的新绝对目录及正timeout')
    work.mkdir(); report={'status':'FAILED'}
    try:
        report=prepare(work,args.mode); run(work,report,args.timeout_seconds)
    except Exception as exc:
        report['status']='FAILED'; report['error']=str(exc); raise
    finally:
        (work/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(report['status']); return 0

if __name__=='__main__': raise SystemExit(main())
