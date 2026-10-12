#!/usr/bin/env python3
"""复核最终生成bench、实际编译源和完整layer0独立黄金绑定。"""
from pathlib import Path
import hashlib, json, subprocess, sys

WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[3]
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_conv_tile_origin_rtl as origin
import test_s2b_conv_validation_rtl as validation
import test_s2b_conv_feature_address_rtl as feature
import test_s2b_geometry_specialization_rtl as geometry
import test_s2b_route_specialization_rtl as route

def sha(p):
    """原字节SHA。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    """只读生产及开发证据，输出独立单一新目标。"""
    evidence=ROOT/'report/evidence/S2B-T17/s13_tile_origin_20261012_r01'
    cached=ROOT/'tmp/2B/S2B-T17/s13_tile_origin_20261012_r01'
    model=json.loads((ROOT/origin.support.MODEL).read_text(encoding='utf-8'));result={}
    bench=feature.bench()
    inputs='\n'.join('u_dut.tile_origin_'+axis+' = $signed(64\'(v_tile_start_'+axis+') * 64\'(v_stride_'+axis+'_latched) - 64\'(v_'+pad+'_latched));' for axis,pad in (('y','pad_top'),('x','pad_left')))
    bench=bench.replace('#1;\n',inputs+'\n#1;\n')
    generated={'feature':('tb_s2b_conv_feature_address.sv',bench)}
    declarations={kind:geometry.ports(ROOT/path) for kind,path in (('pool','src/s2a_maxpool_engine.sv'),('upsample','src/s2a_upsample_engine.sv'))}
    generated['geometry']=('tb_s2b_geometry_specialization.sv',geometry.generate_tb(declarations))
    ports=geometry.ports(ROOT/'src/s2a_route_engine.sv')
    generated['route']=('tb_s2b_route_specialization.sv',route.testbench(model,ports))
    names,vectors,small,proof=validation.vectors(model)
    generated['boundary']=('tb_s2b_conv_validation.sv',origin.boundary_bench(names,small))
    for group,(name,text) in generated.items():
        target=evidence/'all_r03'/group/name;assert target.read_text(encoding='utf-8')==text
        assert (cached/'all_r03'/group/name).read_bytes()==target.read_bytes()
        result[group]=dict(bench_sha256=sha(target),final_generator_exact=True,compiled_source={})
        for path in (cached/'all_r03'/group/'source').iterdir():
            if path.name=='s9_conv_tile_engine_original.sv':
                raw=subprocess.check_output(['git','show',feature.BASELINE+':'+origin.ENGINE],cwd=ROOT).decode('utf-8').replace('\r\n','\n').replace('module s2b_conv_tile_engine (','module s2b_conv_tile_engine_original (')
                assert raw==path.read_text(encoding='utf-8')
                result[group]['compiled_source'][path.name]=sha(path)
            else:
                assert path.read_bytes()==(ROOT/'src'/path.name).read_bytes();result[group]['compiled_source'][path.name]=sha(path)
    name='tb_s2b_conv_layer0.sv';target=evidence/'layer0_r01/layer0'/name
    assert target.read_text(encoding='utf-8')==validation.layer0_tb()
    assert (cached/'layer0_r01/layer0'/name).read_bytes()==target.read_bytes()
    for path in (cached/'layer0_r01/layer0/source').iterdir():assert path.read_bytes()==(ROOT/'src'/path.name).read_bytes()
    golden=validation.FIXTURE/'sample0_layer0_expected_nchw_int8.bin';cpu=evidence/'layer0_r01/cpu_layer0/cpu_layer0_expected.bin'
    assert sha(golden)==sha(cpu)=='220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8'
    report=json.loads((evidence/'layer0_r01/validation.json').read_text(encoding='utf-8'))
    assert report['cpu_layer0']['status']=='PASS' and report['cpu_layer0']['mismatches']==0
    for binding in report['cpu_layer0']['bindings']:assert sha(Path(binding['path']))==binding['sha256']
    for filename,(size,digest) in validation.FIXED.items():
        path=validation.FIXTURE/filename;assert path.is_file() and path.stat().st_size==size and sha(path)==digest
    result['layer0']=dict(bench_sha256=sha(target),golden_sha256=sha(golden),cpu_sha256=sha(cpu),source_bindings='实际编译复制源与当前原件逐字节相等',
      independent_basis='T25冻结完整slice、GF8冻结权重切片、manifest fused bias；CPU INT64点积及D2量化，无读取生产MQROM或候选内部算法',
      limitation='本Reviewer核查已有真实CPU/RTL结果与输入绑定，未重复layer0重型仿真')
    with (WORK/'artifact_audit_receipt.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
